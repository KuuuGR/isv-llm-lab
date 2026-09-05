#!/usr/bin/env python3
"""EXP-004 Phase 1 (practical model screening) — run orchestrator.

Phase 1 asks one question: which practically accessible LLMs are worth
taking forward as candidate engines for Polish → Medžuslovjansky? It
establishes a CLEAN direct-translation baseline per roster row: same
byte-identical Polish source story, same direct-translation instruction,
NO lexical scaffolding, NO candidate word lists, NO morphology/POS or
grammar annotations, NO previous translations, NO evaluator feedback, NO
iterative repair (D-037, EXP-004 DESIGN §6.2).

LLM execution is EXTERNAL (the project has no LLM API client, D-007): the
operator executes one self-contained prompt per roster row in the model's
web/chat interface and returns the raw reply. This script only prepares
runs, registers externally produced outputs byte-for-byte, verifies them
(structural completeness gate, L-027), evaluates them with the Task 008
evaluator (unmodified) plus the Task 015 character-level orthographic
audit, and reports status. It never calls an LLM and never fabricates
outputs.

Commands:

  prepare  --date YYYY-MM-DD [--force]
           provision the local story source (byte-identical copy of the
           EXP-003 canonical source), render one self-contained operator
           prompt per roster row into operator-prompts/, write the prompt
           manifest (operator-prompts/manifest.json, prompt hashes only),
           and write outputs/plan.json (the fixed roster: run ids +
           provider/model/version/interface/access metadata + hashes).
           Deterministic: regenerating with the same --date yields
           byte-identical prompts, manifest, and plan.

  collect  --run <run_id> --output <path>
           [--generation-date YYYY-MM-DD] [--model M] [--provider P]
           [--model-version V] [--generation-parameters S]
           [--status {collected_external_output,collected_partial_output,
                      failed_external_output}]
           [--access-verdict {pass,fail,unknown}] [--access-note TEXT]
           [--note TEXT]
           register an externally generated raw output: copied byte-for-byte,
           never modified, never overwritten; meta.json records prompt/source
           hashes, provider/model/version, generation date + parameters,
           status (D-035), the practical free-access verdict (§5.1/D-036,
           observed by the operator at execution time), output SHA-256, and
           resource pins.

  verify   [--run <run_id> | --all] [--size-floor BYTES] [--no-plan]
           integrity checks (output hash vs meta, plan consistency) plus the
           structural completeness gate (L-027): non-empty output, byte size
           >= floor (default 0.60 x source bytes), head sanity, presence of
           the story's main character-name tokens, and the end marker
           (KONIEC/KONĖC) as the final non-empty line. Writes
           outputs/<run>/intake.json with a verdict:
             complete  — passes the gate (quantitatively usable)
             partial   — real translation but truncated / marker missing
             failed    — not a usable translation (echo, error page, empty)
           The verdict is recorded as data; partial/failed runs are NEVER
           silently deleted, repaired, or rerun (D-035, L-027).

  evaluate --run <run_id> [--force]
           run the completeness gate if no intake.json exists, refuse for
           verdict 'failed' (unless --force), then run the Task 008
           evaluator (isv-eval, unmodified) and the orthographic audit
           (isv_eval.orthography) on the collected output; write
           outputs/<run>/evaluation.json (+ evaluation/ detail),
           outputs/<run>/orthography.json, and evaluation.md. evaluation.json
           carries 'usable' = (intake verdict complete). Metrics are evidence
           dimensions, never merged and never a composite score.

  status   show planned / collected / verified / evaluated / usable per row.

  roster   join plan + meta + intake + evaluation + orthography for every
           collected run into outputs/roster.json and outputs/roster.md
           (coverage pair, unresolved rate, orthography counts, access
           verdict, usability per row — no ranking, no composite score).

Run id: <date>__<provider>__<model>__<model_version>__direct (condition
token 'direct'; variant settings such as thinkon/deepthinkoff are part of
the model_version token). Failures are preserved as data.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from isv_eval.cli import git_commit  # noqa: E402
from isv_eval.orthography import scan_file  # noqa: E402

EXP = ROOT / "experiments" / "exp004-modelscreen"
INPUT_DIR = EXP / "input"
OPERATOR_PROMPTS = EXP / "operator-prompts"
OUTPUTS_DIR = EXP / "outputs"
BASE_INSTRUCTION = EXP / "base_instruction.txt"
EXP003_SOURCE = (ROOT / "experiments" / "exp003-scaffold" / "input"
                 / "source.txt")
DEFAULT_MANIFEST = ROOT / "data" / "dictionary" / "manifest.json"
DEFAULT_LEXICON = ROOT / "data" / "dictionary" / "lexicon.tsv"
EXP003_SOURCE_SHA256 = (
    "5de968a6214d3d64bdb586b5121f494c4bb107e33546487a86bf8ecc57280723")

CONDITION = "direct"
END_MARKER_RE = re.compile(r"^\s*(KONIEC|KONĖC)\s*$")
# story's main character names (kept verbatim in every prior ISV run)
NAME_TOKENS = ("Bronisława", "Teofil", "Julianna", "Przemysław", "Antoni")

# ---------------------------------------------------------------------------
# Roster (EXP-004 DESIGN §5.2/§11.7; finalized Task 016/017)
# ---------------------------------------------------------------------------
# Every row: provider, model, model_version (variant/settings token),
# label, interface, generation_parameters (human text), custom_gpt (bool),
# variant_of (run-id model/version token of the sibling, or None),
# conditional (free-text filter condition or "").
ROSTER = [
    {
        "provider": "openai", "model": "gpt-5.6-luna", "model_version": "thinkoff",
        "label": "GPT-5.6 Luna — thinking OFF", "interface": "ChatGPT (web)",
        "generation_parameters": "thinking OFF", "custom_gpt": False,
        "variant_of": None, "conditional": "",
    },
    {
        "provider": "openai", "model": "gpt-5.6-luna", "model_version": "thinkon",
        "label": "GPT-5.6 Luna — thinking ON", "interface": "ChatGPT (web)",
        "generation_parameters": "thinking ON", "custom_gpt": False,
        "variant_of": "thinkoff", "conditional": "",
    },
    {
        "provider": "openai", "model": "gpt-isv-teacher", "model_version": "unknown",
        "label": "GPT Interslavic Teacher (custom GPT)", "interface": "ChatGPT (custom GPT)",
        "generation_parameters": "custom GPT; built-in system prompt unknown (D-018)",
        "custom_gpt": True, "variant_of": None, "conditional": "",
    },
    {
        "provider": "anthropic", "model": "claude", "model_version": "sonnet-5",
        "label": "Claude Sonnet 5", "interface": "Claude (web)",
        "generation_parameters": "Sonnet 5", "custom_gpt": False,
        "variant_of": None, "conditional": "",
    },
    {
        "provider": "google", "model": "gemini", "model_version": "unknown",
        "label": "Gemini", "interface": "Google Gemini (web)",
        "generation_parameters": "unknown",
        "custom_gpt": False, "variant_of": None,
        "conditional": "only if practical free access/quota satisfies §5.1 "
                       "(>= 1 full story per day or every other day)",
    },
    {
        "provider": "deepseek", "model": "deepseek-v4-pro",
        "model_version": "deepthinkoff",
        "label": "DeepSeek V4 Pro — DeepThink OFF", "interface": "DeepSeek chat (web)",
        "generation_parameters": "DeepThink OFF", "custom_gpt": False,
        "variant_of": None, "conditional": "",
    },
    {
        "provider": "deepseek", "model": "deepseek-v4-pro",
        "model_version": "deepthinkon",
        "label": "DeepSeek V4 Pro — DeepThink ON", "interface": "DeepSeek chat (web)",
        "generation_parameters": "DeepThink ON", "custom_gpt": False,
        "variant_of": "deepthinkoff", "conditional": "",
    },
    {
        "provider": "xai", "model": "grok", "model_version": "unknown",
        "label": "Grok", "interface": "Grok (web)",
        "generation_parameters": "unknown", "custom_gpt": False,
        "variant_of": None, "conditional": "",
    },
    {
        "provider": "moonshot", "model": "kimi", "model_version": "unknown",
        "label": "Kimi", "interface": "Kimi (web)",
        "generation_parameters": "unknown", "custom_gpt": False,
        "variant_of": None, "conditional": "",
    },
    {
        "provider": "alibaba", "model": "qwen", "model_version": "unknown",
        "label": "Qwen", "interface": "Qwen Chat (web)",
        "generation_parameters": "unknown", "custom_gpt": False,
        "variant_of": None, "conditional": "",
    },
    {
        "provider": "zhipu", "model": "glm", "model_version": "unknown",
        "label": "GLM", "interface": "Zhipu GLM (web)",
        "generation_parameters": "unknown", "custom_gpt": False,
        "variant_of": None,
        "conditional": "only if practical web access satisfies the project "
                       "filter (§5.1/D-036)",
    },
]

STATUSES = ("collected_external_output", "collected_partial_output",
            "failed_external_output")
ACCESS_VERDICTS = ("pass", "fail", "unknown")
RUN_ID_FIELDS = ("date", "provider", "model", "model_version", "condition")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def run_id_for(date: str, row: dict) -> str:
    return (f"{date}__{row['provider']}__{row['model']}__"
            f"{row['model_version']}__{CONDITION}")


def parse_run_id(run_id: str) -> dict:
    parts = run_id.split("__")
    if len(parts) != 5:
        raise ValueError(
            f"run id must be <date>__<provider>__<model>__<model_version>__"
            f"direct, got: {run_id!r}")
    return dict(zip(RUN_ID_FIELDS, parts))


def roster_entry(run_id: str) -> dict | None:
    try:
        parts = parse_run_id(run_id)
    except ValueError:
        return None
    for row in ROSTER:
        if (row["provider"] == parts["provider"]
                and row["model"] == parts["model"]
                and row["model_version"] == parts["model_version"]):
            return row
    return None


def load_plan() -> dict:
    plan = OUTPUTS_DIR / "plan.json"
    if not plan.is_file():
        return {}
    return json.loads(plan.read_text(encoding="utf-8"))


def load_meta(run_id: str) -> dict:
    meta_path = OUTPUTS_DIR / run_id / "meta.json"
    if not meta_path.is_file():
        return {}
    return json.loads(meta_path.read_text(encoding="utf-8"))


def resource_versions() -> dict:
    versions: dict = {
        "evaluator_commit": git_commit(),
        "dictionary_manifest": (json.loads(
            DEFAULT_MANIFEST.read_text(encoding="utf-8"))
            if DEFAULT_MANIFEST.is_file() else None),
        "dictionary_lexicon": {
            "path": str(DEFAULT_LEXICON),
            "bytes": (DEFAULT_LEXICON.stat().st_size
                      if DEFAULT_LEXICON.is_file() else 0),
            "sha256": (sha256_file(DEFAULT_LEXICON)
                       if DEFAULT_LEXICON.is_file() else None),
        },
        "orthography_inventory": "src/isv_eval/orthography.py (official "
                                 "Interslavic alphabet; D-040)",
        "base_instruction": {
            "file": "experiments/exp004-modelscreen/base_instruction.txt",
            "sha256": (sha256_file(BASE_INSTRUCTION)
                       if BASE_INSTRUCTION.is_file() else None),
        },
    }
    return versions


# ---------------------------------------------------------------------------
# prepare
# ---------------------------------------------------------------------------

def _ensure_source(date: str, force: bool = False) -> Path:
    """Provision the local story source (byte-identical EXP-003 copy)."""
    source = INPUT_DIR / "source.txt"
    meta = INPUT_DIR / "source.meta.json"
    if source.is_file():
        actual = sha256_file(source)
        if actual != EXP003_SOURCE_SHA256:
            raise RuntimeError(
                f"{source} exists but sha256 {actual[:16]}... does not match "
                f"the canonical EXP-003 source {EXP003_SOURCE_SHA256[:16]}...; "
                "refusing to proceed with a different source")
        return source
    if not EXP003_SOURCE.is_file():
        raise RuntimeError(
            f"canonical source missing at {EXP003_SOURCE}; provide it first")
    if sha256_file(EXP003_SOURCE) != EXP003_SOURCE_SHA256:
        raise RuntimeError("EXP-003 source does not match its recorded hash")
    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(EXP003_SOURCE, source)
    (INPUT_DIR / "source.meta.json").write_text(json.dumps({
        "experiment_id": "exp004",
        "story_id": "op-pl",
        "filename": "source.txt",
        "sha256": sha256_file(source),
        "size_bytes": source.stat().st_size,
        "derivation": {
            "from": str(EXP003_SOURCE),
            "from_sha256": EXP003_SOURCE_SHA256,
            "note": "Byte-identical copy of the EXP-003 canonical story-only "
                    "source (itself cleaned from "
                    "experiments/exp001-baseline/input/source.txt; see "
                    "exp003 input/source.meta.json). Story text only "
                    "(title, headings, body, KONIEC marker).",
        },
        "copyright_note": "Project Owner owns the story and permits its use "
                          "in this project; keep local, do not commit or "
                          "redistribute.",
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    return source


def _prompt_filename(row: dict) -> str:
    nn = ROSTER.index(row) + 1
    return f"{nn:02d}-{row['model']}-{row['model_version']}.md"


def _render_prompt(row: dict, source_text: str) -> str:
    setting = row["generation_parameters"]
    cond = f"conditional filter: {row['conditional']}" if row[
        "conditional"] else "no conditional filter"
    return "\n".join([
        f"# EXP-004 — Phase 1 — direct baseline — {row['label']}",
        "",
        "> COPY THIS ENTIRE FILE INTO " + row["interface"] + ".",
        "> Do not modify anything. Save the model's complete reply",
        "> byte-for-byte and hand it to the collect step.",
        "",
        "---",
        "",
        "Experiment ID: EXP-004",
        "Phase: 1 (practical model screening)",
        f"Target model: {row['label']}",
        f"Provider / interface: {row['provider']} / {row['interface']}",
        f"Model version / settings: {row['model_version']} ({setting})",
        f"Condition: {CONDITION} (no guidance — no scaffold, no candidates, "
        "no morphology/POS, no grammar notes, no evaluator feedback)",
        cond,
        "",
        "---",
        "",
        BASE_INSTRUCTION.read_text(encoding="utf-8").replace(
            "{STORY}", source_text).rstrip() + "\n",
    ])


def run_prepare(date: str, force: bool = False) -> int:
    if not date:
        print("error: --date YYYY-MM-DD is required (run ids carry the "
              "planned generation date)", file=sys.stderr)
        return 2
    if not BASE_INSTRUCTION.is_file():
        print(f"error: base instruction missing: {BASE_INSTRUCTION}",
              file=sys.stderr)
        return 2
    source = _ensure_source(date)
    source_text = source.read_text(encoding="utf-8")
    source_sha = sha256_bytes(source_text.encode("utf-8"))

    plan_path = OUTPUTS_DIR / "plan.json"
    if plan_path.is_file() and not force:
        print(f"error: {plan_path} already exists; use --force to rewrite "
              "(changing the plan invalidates collected runs)",
              file=sys.stderr)
        return 2

    OPERATOR_PROMPTS.mkdir(parents=True, exist_ok=True)
    files = []
    runs = []
    for row in ROSTER:
        fname = _prompt_filename(row)
        path = OPERATOR_PROMPTS / fname
        prompt_text = _render_prompt(row, source_text)
        prompt_sha = sha256_bytes(prompt_text.encode("utf-8"))
        if path.is_file() and not force:
            if sha256_bytes(path.read_bytes()) != prompt_sha:
                print(f"error: {path} exists with different content; "
                      "--force to overwrite", file=sys.stderr)
                return 2
        path.write_text(prompt_text, encoding="utf-8")
        run_id = run_id_for(date, row)
        files.append({"file": fname, "run_id": run_id,
                      "prompt_sha256": prompt_sha,
                      "bytes": len(prompt_text.encode("utf-8"))})
        runs.append({
            "run_id": run_id,
            "provider": row["provider"],
            "model": row["model"],
            "model_version": row["model_version"],
            "label": row["label"],
            "interface": row["interface"],
            "generation_parameters": row["generation_parameters"],
            "custom_gpt": row["custom_gpt"],
            "variant_of": row["variant_of"],
            "conditional": row["conditional"],
            "condition": CONDITION,
            "prompt_file": (str(path.relative_to(ROOT))
                            if path.is_relative_to(ROOT)
                            else str(path)),
            "prompt_sha256": prompt_sha,
            "source_sha256": source_sha,
        })

    manifest = {
        "artifact": "operator-prompt-manifest",
        "experiment_id": "exp004",
        "date": date,
        "generator": "scripts/run_exp004_phase1.py prepare",
        "generator_commit": git_commit(),
        "note": "Prompt files embed the copyrighted story and stay local "
                "(gitignored); this manifest records prompt hashes only.",
        "files": files,
    }
    (OPERATOR_PROMPTS / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    plan = {
        "experiment_id": "exp004",
        "artifact": "run-plan",
        "phase": "1",
        "date": date,
        "generator": "scripts/run_exp004_phase1.py prepare",
        "generator_commit": git_commit(),
        "source": {"file": (str(source.relative_to(ROOT))
                            if source.is_relative_to(ROOT)
                            else str(source)),
                   "sha256": source_sha,
                   "bytes": source.stat().st_size},
        "note": "Fixed Phase-1 roster (clean direct-translation baseline). "
                "LLM execution is external; this plan never calls an LLM.",
        "runs": runs,
    }
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    plan_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2),
                         encoding="utf-8")
    print(f"[prepare] prompts -> {OPERATOR_PROMPTS}/")
    print(f"[prepare] plan     -> {plan_path}")
    for r in runs:
        print(f"  {r['run_id']:64s} prompt {r['prompt_sha256'][:12]}")
    print(f"{len(runs)} planned run(s); source sha256 {source_sha[:16]}...")
    return 0


# ---------------------------------------------------------------------------
# collect
# ---------------------------------------------------------------------------

def run_collect(run_id: str, output: Path, generation_date: str,
                model: str, provider: str, model_version: str,
                generation_parameters: str = "unknown",
                status: str = "collected_external_output",
                access_verdict: str = "unknown",
                access_note: str = "",
                note: str = "") -> int:
    row = roster_entry(run_id)
    if row is None:
        print(f"error: unknown run id {run_id!r} (not a Phase-1 roster row)",
              file=sys.stderr)
        return 2
    if status not in STATUSES:
        print(f"error: unknown status {status!r}", file=sys.stderr)
        return 2
    if access_verdict not in ACCESS_VERDICTS:
        print(f"error: unknown access verdict {access_verdict!r}",
              file=sys.stderr)
        return 2
    plan = load_plan()
    plan_entry = next((r for r in plan.get("runs", [])
                       if r["run_id"] == run_id), None)
    if plan_entry is None:
        print("error: run not in the plan; run "
              "`scripts/run_exp004_phase1.py prepare --date <date>` first",
              file=sys.stderr)
        return 2

    out_dir = OUTPUTS_DIR / run_id
    dst = out_dir / "output.txt"
    if dst.exists():
        print(f"error: {dst} already exists; refusing to overwrite "
              "(never overwrite an existing run)", file=sys.stderr)
        return 2
    if not output.is_file():
        print(f"error: output file not found: {output}", file=sys.stderr)
        return 2

    data = output.read_bytes()
    out_dir.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(data)  # byte-for-byte, never modified

    parts = parse_run_id(run_id)
    meta = {
        "run_id": run_id,
        "experiment_id": "exp004",
        "phase": "1",
        "condition": CONDITION,
        "label": row["label"],
        "interface": row["interface"],
        "model": model if model != "unknown" else row["model"],
        "provider": (provider if provider != "unknown"
                     else row["provider"]),
        "model_version": (model_version if model_version != "unknown"
                          else row["model_version"]),
        "generation_parameters": (generation_parameters
                                  if generation_parameters != "unknown"
                                  else row["generation_parameters"]),
        "generation_date": generation_date if generation_date != "unknown"
                           else parts["date"],
        "status": status,
        "access": {
            "filter_verdict": access_verdict,
            "quota_observed": access_note,
            "criteria": "D-036/§5.1: web/chat interface; free access with "
                        "practical quota >= 1 full story/day or every other "
                        "day; not a one-time trial; usable by the project "
                        "author. Observed by the operator at execution time.",
        },
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "collected_by": "scripts/run_exp004_phase1.py collect",
        "prompt": {"file": plan_entry["prompt_file"],
                   "sha256": plan_entry["prompt_sha256"]},
        "source": {"sha256": plan_entry["source_sha256"]},
        "output": {"file": str(dst), "sha256": sha256_bytes(data),
                   "bytes": len(data)},
        "resources": resource_versions(),
        "note": ("Raw LLM output stored byte-for-byte; never modified. "
                 "Empty or failed runs are preserved and documented, not "
                 "deleted." + (f" {note}" if note else "")),
    }
    (out_dir / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[collect] {run_id}")
    print(f"  label/interface: {row['label']} / {row['interface']}")
    print(f"  output sha256: {meta['output']['sha256']}")
    print(f"  status: {meta['status']}; access filter: "
          f"{meta['access']['filter_verdict']}")
    return 0


# ---------------------------------------------------------------------------
# verify (integrity + structural completeness gate, L-027)
# ---------------------------------------------------------------------------

def _gate_checks(run_dir: Path, source_bytes: int,
                 size_floor: int) -> dict:
    output = run_dir / "output.txt"
    checks: dict = {}
    if not output.is_file():
        return {"verdict": "failed", "checks": {"file": False},
                "reasons": ["no output.txt"]}
    data = output.read_bytes()
    checks["non_empty"] = len(data) > 0
    checks["size_bytes"] = len(data)
    checks["size_floor"] = size_floor
    text = data.decode("utf-8", errors="replace")
    lines = text.splitlines()
    nonempty = [ln for ln in lines if ln.strip()]
    checks["head_sane"] = bool(nonempty) and len(nonempty[0].strip()) >= 10
    checks["end_marker"] = bool(nonempty) and bool(
        END_MARKER_RE.match(nonempty[-1]))
    found = [name for name in NAME_TOKENS
             if name.lower() in text.lower()]
    checks["names_present"] = len(found)
    checks["names_required"] = 3
    reasons: list[str] = []
    if not checks["non_empty"]:
        reasons.append("empty output")
    if checks["non_empty"] and checks["size_bytes"] < size_floor:
        reasons.append(f"size {checks['size_bytes']} < floor {size_floor}")
    if checks["non_empty"] and not checks["head_sane"]:
        reasons.append("first non-empty line implausibly short "
                       "(service-error page?)")
    if not checks["end_marker"]:
        reasons.append("final non-empty line is not KONIEC/KONĖC "
                       "(truncated?)")
    if checks["names_present"] < checks["names_required"]:
        reasons.append(f"only {checks['names_present']}/5 main story names "
                       "found (not a translation?)")
    return {"checks": checks, "reasons": reasons}


def _intake_verdict(gate: dict) -> str:
    reasons = gate.get("reasons", [])
    if not gate.get("checks", {}).get("non_empty", False):
        return "failed"
    # only hard failures that mean "not a usable translation"
    hard = [r for r in reasons if any(k in r for k in (
        "empty output", "implausibly short", "not a translation"))]
    if hard:
        return "failed"
    if any(r.startswith(("size", "final non-empty")) for r in reasons):
        return "partial"
    return "complete"


def _verify_integrity(run_id: str, plan_entry: dict | None) -> list[str]:
    errors: list[str] = []
    out_dir = OUTPUTS_DIR / run_id
    meta = load_meta(run_id)
    if not meta:
        errors.append("meta.json missing")
    output_path = out_dir / "output.txt"
    if not output_path.is_file():
        errors.append("output.txt missing")
    elif meta:
        recorded = meta.get("output", {}).get("sha256")
        actual = sha256_bytes(output_path.read_bytes())
        if recorded is None:
            errors.append("meta.json has no output sha256")
        elif recorded != actual:
            errors.append(f"output sha256 mismatch: meta={recorded} "
                          f"actual={actual}")
    if plan_entry is not None and meta:
        if meta.get("condition") != plan_entry["condition"]:
            errors.append("condition mismatch meta vs plan")
        if meta["prompt"].get("sha256") != plan_entry["prompt_sha256"]:
            errors.append("prompt hash differs from plan")
        if meta["source"].get("sha256") != plan_entry["source_sha256"]:
            errors.append("source hash differs from plan")
        pf = OPERATOR_PROMPTS / Path(meta["prompt"].get("file", "")).name
        if meta["prompt"].get("file") is None:
            errors.append("meta.json prompt has no file")
        elif not pf.is_file():
            errors.append(f"prompt file missing: {pf}")
        elif sha256_bytes(pf.read_bytes()) != meta["prompt"]["sha256"]:
            errors.append("prompt file content no longer matches recorded "
                          "hash")
    return errors


def run_verify(run_id: str | None = None, size_floor: int | None = None,
               no_plan: bool = False) -> int:
    plan = load_plan()
    runs: list[tuple[str, dict | None]] = []
    if run_id:
        runs.append((run_id, next((r for r in plan.get("runs", [])
                                   if r["run_id"] == run_id), None)))
    else:
        for r in plan.get("runs", []):
            runs.append((r["run_id"], r))
    if not runs:
        print("nothing to verify; prepare a plan first", file=sys.stderr)
        return 2

    source_bytes = 0
    src = plan.get("source")
    if src:
        sp = (Path(src["file"]) if Path(src["file"]).is_absolute()
              else ROOT / src["file"])
        source_bytes = sp.stat().st_size if sp.is_file() else 0
    problems = 0
    for rid, plan_entry in runs:
        out_dir = OUTPUTS_DIR / rid
        if not (out_dir / "output.txt").is_file():
            print(f"[skip] {rid}: no collected output")
            continue
        integrity = _verify_integrity(rid, None if no_plan else plan_entry)
        floor = size_floor if size_floor is not None else int(
            0.60 * source_bytes)
        gate = _gate_checks(out_dir, source_bytes, floor)
        verdict = _intake_verdict(gate)
        meta = load_meta(rid)
        intake = {
            "run_id": rid,
            "verdict": verdict,
            "checks": gate["checks"],
            "reasons": gate["reasons"],
            "floor_bytes": floor,
            "integrity_errors": integrity,
            "meta_status": meta.get("status", None),
        }
        (out_dir / "intake.json").write_text(
            json.dumps(intake, ensure_ascii=False, indent=2),
            encoding="utf-8")
        flag = "OK " if not integrity else "FAIL"
        if integrity:
            problems += 1
        print(f"[{flag}] {rid} -> {verdict.upper()}"
              f"{' (FAILS: ' + '; '.join(integrity) + ')' if integrity else ''}")
        if gate["reasons"]:
            print("    reasons: " + "; ".join(gate["reasons"]))
        # consistency between the recorded meta status and content verdict
        if verdict == "complete" and meta.get("status") == \
                "collected_partial_output":
            print("    note: content looks complete but meta.status says "
                  "collected_partial_output")
        if verdict == "partial" and meta.get("status") == \
                "collected_external_output":
            print("    note: content looks partial but meta.status says "
                  "collected_external_output")
    print(f"\n{len(runs)} planned run(s) checked.")
    return 1 if problems else 0


# ---------------------------------------------------------------------------
# evaluate
# ---------------------------------------------------------------------------

def run_evaluate(run_id: str, force: bool = False) -> int:
    out_dir = OUTPUTS_DIR / run_id
    text = out_dir / "output.txt"
    if not text.is_file():
        print(f"error: no output.txt for {run_id}; collect it first",
              file=sys.stderr)
        return 2
    meta = load_meta(run_id)
    if not meta:
        print(f"error: no meta.json for {run_id}; collect it first",
              file=sys.stderr)
        return 2
    intake_path = out_dir / "intake.json"
    if not intake_path.is_file():
        print(f"[evaluate] no intake.json; running the completeness gate "
              f"first")
        rc = run_verify(run_id)
        if rc == 2:
            return 2
    intake = json.loads(intake_path.read_text(encoding="utf-8"))
    if intake["verdict"] == "failed" and not force:
        print(f"error: intake verdict for {run_id} is 'failed' "
              f"({'; '.join(intake['reasons'])}); refusing to evaluate a "
              "non-translation output (--force to override)",
              file=sys.stderr)
        return 2

    eval_dir = out_dir / "evaluation"
    eval_dir.mkdir(parents=True, exist_ok=True)
    cmd = [sys.executable, "-m", "isv_eval.cli", str(text),
           "--out", str(eval_dir)]
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    if proc.returncode != 0:
        print(f"error: isv-eval failed on {text}: {proc.stderr[-500:]}",
              file=sys.stderr)
        return 2
    report = json.loads((eval_dir / "report.json").read_text(
        encoding="utf-8"))
    m = report["metrics"]
    summary = {
        "run_id": run_id,
        "evaluator": report["evaluator"],
        "phase": "1",
        "condition": meta.get("condition"),
        "label": meta.get("label"),
        "model": meta.get("model"),
        "provider": meta.get("provider"),
        "model_version": meta.get("model_version"),
        "generation_parameters": meta.get("generation_parameters"),
        "intake_verdict": intake["verdict"],
        "usable": intake["verdict"] == "complete",
        "metrics": m,
        "output_files": report["output_files"],
    }
    (out_dir / "evaluation.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8")

    # orthographic sanity audit (independent dimension, Task 015 inventory)
    ortho = scan_file(text)
    od = ortho.as_dict()
    (out_dir / "orthography.json").write_text(json.dumps({
        "run_id": run_id,
        "inventory": "official Interslavic alphabet "
                     "(src/isv_eval/orthography.py, D-040)",
        "metrics": od,
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        f"# EXP-004 Phase 1 — evaluation — {run_id}",
        "",
        f"{meta.get('label', '?')} ({meta.get('provider')}, version "
        f"{meta.get('model_version')}) · generated "
        f"{meta.get('generation_date')} · intake "
        f"{intake['verdict']} · usable {summary['usable']}",
        "",
        "| metric | value |",
        "|---|---:|",
        f"| lexical tokens | {m['total_tokens']} |",
        f"| canonical supported tokens (A+B) | {m['canonical_supported_tokens']} |",
        f"| canonical coverage | {_pct(m['canonical_coverage'])} |",
        f"| broader resource-supported tokens | {m['broader_resource_supported_tokens']} |",
        f"| broader resource-supported coverage | {_pct(m['broader_resource_supported_coverage'])} |",
        f"| unresolved tokens (C) | {m['unresolved_tokens']} |",
        f"| unresolved rate | {_pct(m['unresolved_rate'])} |",
        f"| exact dictionary matches (A) | {m['exact_dictionary_matches']} |",
        f"| morphologically valid (B) | {m['morphologically_valid_forms']} |",
        "",
        "Orthography (outside-inventory): "
        f"cyrillic {od['cyrillic']} · polish-specific {od['polish_specific']} "
        f"· other-latin {od['other_latin']} · other-script "
        f"{od['other_script']} · unexpected non-letter "
        f"{od['unexpected_nonletters']} (total {od['outside_inventory']})",
        "",
        "Coverage is evidence, not linguistic correctness; no composite "
        "quality score is assigned.",
        "",
    ]
    (out_dir / "evaluation.md").write_text("\n".join(lines),
                                          encoding="utf-8")
    print(f"[evaluate] {run_id} (intake {intake['verdict']}, "
          f"usable {summary['usable']})")
    print(f"  canonical: {_pct(m['canonical_coverage'])}  "
          f"broader: {_pct(m['broader_resource_supported_coverage'])}  "
          f"unresolved: {_pct(m['unresolved_rate'])}")
    print(f"  orthography outside-inventory: {od['outside_inventory']} "
          f"(cyr {od['cyrillic']}, pol {od['polish_specific']}, "
          f"lat {od['other_latin']})")
    return 0


def _pct(v: float | None) -> str:
    return f"{v * 100:.2f}%" if v is not None else "n/a"


# ---------------------------------------------------------------------------
# status / roster
# ---------------------------------------------------------------------------

def run_status() -> int:
    plan = load_plan()
    if not plan.get("runs"):
        print("no plan; run `scripts/run_exp004_phase1.py prepare "
              "--date YYYY-MM-DD` first")
        return 0
    print(f"{'run_id':<66} {'output':<7} {'intake':<10} {'eval':<5} "
          f"{'usable':<7}")
    n_out = n_int = n_ev = n_us = 0
    for r in plan["runs"]:
        rid = r["run_id"]
        out_dir = OUTPUTS_DIR / rid
        has_out = (out_dir / "output.txt").is_file()
        intake = (out_dir / "intake.json")
        has_intake = intake.is_file()
        verdict = (json.loads(intake.read_text(encoding="utf-8"))
                   .get("verdict", "") if has_intake else "")
        has_ev = (out_dir / "evaluation.json").is_file()
        usable = False
        if has_ev:
            usable = json.loads((out_dir / "evaluation.json").read_text(
                encoding="utf-8")).get("usable", False)
        n_out += has_out
        n_int += has_intake
        n_ev += has_ev
        n_us += usable
        print(f"{rid:<66} {'yes' if has_out else 'no':<7} "
              f"{verdict or '-':<10} {'yes' if has_ev else 'no':<5} "
              f"{'yes' if usable else 'no':<7}")
    print(f"\n{len(plan['runs'])} planned; {n_out} collected; {n_int} "
          f"verified; {n_ev} evaluated; {n_us} usable (complete).")
    return 0


def run_roster() -> int:
    plan = load_plan()
    runs = plan.get("runs", [])
    if not runs:
        print("no plan; prepare first", file=sys.stderr)
        return 2
    rows = []
    for r in runs:
        rid = r["run_id"]
        out_dir = OUTPUTS_DIR / rid
        meta = load_meta(rid)
        intake_p = out_dir / "intake.json"
        ev_p = out_dir / "evaluation.json"
        ortho_p = out_dir / "orthography.json"
        row = {
            "run_id": rid,
            "label": r["label"],
            "provider": r["provider"],
            "model": r["model"],
            "model_version": r["model_version"],
            "generation_parameters": r["generation_parameters"],
            "interface": r["interface"],
            "conditional": r["conditional"],
            "collected": (out_dir / "output.txt").is_file(),
            "status": meta.get("status", None),
            "access": meta.get("access", {}),
            "intake_verdict": (json.loads(intake_p.read_text(
                encoding="utf-8")).get("verdict")
                if intake_p.is_file() else None),
            "intake_reasons": (json.loads(intake_p.read_text(
                encoding="utf-8")).get("reasons", [])
                if intake_p.is_file() else []),
            "metrics": (json.loads(ev_p.read_text(encoding="utf-8"))
                        .get("metrics") if ev_p.is_file() else None),
            "usable": (json.loads(ev_p.read_text(encoding="utf-8"))
                       .get("usable") if ev_p.is_file() else None),
            "orthography": (json.loads(ortho_p.read_text(
                encoding="utf-8")).get("metrics")
                if ortho_p.is_file() else None),
        }
        rows.append(row)
    out = {"experiment_id": "exp004", "phase": "1",
           "generator": "scripts/run_exp004_phase1.py roster",
           "note": "Metrics are separate evidence dimensions; no ranking "
                   "and no composite score.",
           "rows": rows}
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUTS_DIR / "roster.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = [
        "# EXP-004 Phase 1 — screening roster (clean direct baseline)",
        "",
        "| run | label | access | intake | usable | canon. | broader | "
        "unres. | tok | ortho out |",
        "|---|---|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        m = row["metrics"] or {}
        o = row["orthography"] or {}
        access = (row["access"] or {}).get("filter_verdict", "—")
        lines.append(
            f"| {row['run_id']} | {row['label']} | {access} | "
            f"{row['intake_verdict'] or '—'} | "
            f"{'yes' if row['usable'] else 'no'} | "
            f"{_pct(m.get('canonical_coverage')) if m else '—'} | "
            f"{_pct(m.get('broader_resource_supported_coverage')) if m else '—'} | "
            f"{_pct(m.get('unresolved_rate')) if m else '—'} | "
            f"{m.get('total_tokens', '—') if m else '—'} | "
            f"{o.get('outside_inventory', '—')} |")
    (OUTPUTS_DIR / "roster.md").write_text("\n".join(lines) + "\n",
                                           encoding="utf-8")
    print(f"[roster] wrote outputs/roster.json + roster.md "
          f"({len(rows)} rows; "
          f"{sum(1 for x in rows if x['usable'])} usable)")
    return 0


# ---------------------------------------------------------------------------
# cli
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p_prep = sub.add_parser("prepare", help="package prompts + write plan")
    p_prep.add_argument("--date", required=True, help="YYYY-MM-DD")
    p_prep.add_argument("--force", action="store_true")

    p_col = sub.add_parser("collect", help="register an external raw output")
    p_col.add_argument("--run", required=True, dest="run_id")
    p_col.add_argument("--output", required=True, type=Path)
    p_col.add_argument("--generation-date", default="unknown")
    p_col.add_argument("--model", default="unknown")
    p_col.add_argument("--provider", default="unknown")
    p_col.add_argument("--model-version", default="unknown")
    p_col.add_argument("--generation-parameters", default="unknown")
    p_col.add_argument("--status", default="collected_external_output",
                       choices=STATUSES)
    p_col.add_argument("--access-verdict", default="unknown",
                       choices=ACCESS_VERDICTS,
                       help="operator's practical free-access verdict "
                            "(D-036 filter), observed at execution time")
    p_col.add_argument("--access-note", default="",
                       help="free-access/quota observation (e.g. 'complete "
                            "in one free session')")
    p_col.add_argument("--note", default="",
                       help="observed facts about the reply "
                            "(e.g. truncation)")

    p_ver = sub.add_parser("verify", help="integrity + completeness gate")
    p_ver.add_argument("--run", default=None, dest="run_id")
    p_ver.add_argument("--size-floor", type=int, default=None)
    p_ver.add_argument("--no-plan", action="store_true")

    p_ev = sub.add_parser("evaluate", help="evaluate a collected output")
    p_ev.add_argument("--run", required=True, dest="run_id")
    p_ev.add_argument("--force", action="store_true")

    sub.add_parser("status", help="show run progress")
    sub.add_parser("roster", help="write the screening roster summary")
    args = parser.parse_args(argv)

    if args.command == "prepare":
        return run_prepare(args.date, args.force)
    if args.command == "collect":
        return run_collect(args.run_id, args.output, args.generation_date,
                           args.model, args.provider, args.model_version,
                           args.generation_parameters, args.status,
                           args.access_verdict, args.access_note, args.note)
    if args.command == "verify":
        return run_verify(args.run_id, args.size_floor, args.no_plan)
    if args.command == "evaluate":
        return run_evaluate(args.run_id, args.force)
    if args.command == "status":
        return run_status()
    if args.command == "roster":
        return run_roster()
    return 2


if __name__ == "__main__":
    sys.exit(main())
