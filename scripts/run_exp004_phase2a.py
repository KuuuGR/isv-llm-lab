#!/usr/bin/env python3
"""EXP-004 Phase 2A (full-roster corpus priming) — run orchestrator.

Phase 2A tests the project's core corpus-grounding hypothesis:

> Does exposing an LLM to authentic Medžuslovjansky text immediately before
> translation cause it to generate Medžuslovjansky that is more consistent
> with the real language than the same model translating without that
> exposure?

This is NOT another model screening. Phase 1 (scripts/run_exp004_phase1.py)
already established the clean direct-translation baseline for the 18 usable
configurations; Phase 2A asks how much authentic ISV corpus exposure changes
each model's generation.

Two conditions per Phase-1-usable configuration (the reconciled 18-row
Phase-1 roster minus the single failed GLM run — the authoritative roster is
imported from run_exp004_phase1.ROSTER, never reconstructed from filenames):

  Condition A — control (condition token 'p2a-ctl')
      the SAME clean direct-translation task as Phase 1 (same base
      instruction, same Polish source story, fresh session, NO corpus).
      The Phase-1 baseline outputs satisfy this condition; a fresh control
      may be re-executed with the provided control prompt, and the compare
      step prefers a freshly collected control when one exists.

  Condition B — corpus primed (condition token 'p2a-primed')
      TWO sequential prompts in ONE fresh conversation/session:
        Prompt 1 (msg1): the fixed authentic Medžuslovjansky reference text
            ("Tuta historija" excerpt, corpus id tuta-historija v1) with an
            explicit study-as-language-reference instruction. The model is
            told NOT to translate/summarize/reproduce/modify/continue the
            text, NOT to imitate its sentences, and NOT to answer questions
            about it; it should retain the language information for the next
            task. NO translation is requested in Prompt 1.
        Prompt 2 (msg2): the SAME Polish source story as Phase 1 with the
            standard direct-translation instruction, asking the model to
            translate using the preceding authentic text as a language
            reference. The Polish story bytes are unchanged; no lexical
            scaffolding, no candidate lists, no dictionary injection, no
            morphology annotations, no repair instructions (Phase 2A must
            remain a genuine corpus-priming experiment).

Terminology is fixed: in-context learning / corpus priming / contextual
grounding / reference-text conditioning. The corpus is NEVER described as
training and model weights are never changed.

Conversation-contamination control:
- primed runs must keep Prompt 1 and Prompt 2 in the SAME session (the
  hypothesis concerns information retained in context);
- control runs must never contain prior ISV reference material (fresh
  session; collect-session REJECTS a control session whose content contains
  the corpus fingerprint);
- collect-session for a primed run REQUIRES the corpus fingerprint to be
  present before the translation instruction (proof that the reference text
  was actually in the session) and rejects altered translation instructions.

Run ids: <date>__<provider>__<model>__<model_version>__<condition> where
<condition> is 'p2a-ctl' or 'p2a-primed'. Phase-1 baseline run ids end in
'__direct', so the three identities (Phase 1 baseline / Phase 2A control /
Phase 2A corpus-primed) can never be confused. Each Phase-2A run is unique;
every plan row records its Phase-1 baseline run id.

LLM execution is EXTERNAL (D-007): the operator executes the prompts in the
model's web/chat interface and returns the raw reply. This script only
prepares runs, registers externally produced outputs byte-for-byte (D-035),
verifies them (Phase-1 completeness gate, L-027), evaluates them with the
Task 008 evaluator (unmodified) plus the Task 015 orthographic audit, and
reports status/roster and the primed-vs-baseline delta table. It never
calls an LLM and never fabricates outputs.

Commands:

  prepare  --date YYYY-MM-DD [--force]
           write the run plan (outputs/plan.json), render the operator
           prompts (operator-prompts/*.md: 18 control files + 18 primed
           msg1 files + 18 primed msg2 files), and write the prompt
           manifest (operator-prompts/manifest.json, hashes only).
           Deterministic: regenerating with the same --date yields
           byte-identical prompts, manifest, and plan. The Polish source
           story and the corpus file must exist locally with their recorded
           SHA-256 (never fetched).

  collect  --run <run_id> --output <path>
           register an externally generated raw output byte-for-byte
           (never modified, never overwritten). meta.json records the
           condition, corpus + source hashes, the Phase-1 baseline run id,
           status (D-035), the practical free-access verdict, and resource
           pins.

  collect-session  --run <run_id> --session <path>
           register the raw reply embedded in an author session file with
           contamination controls:
             control runs:   session must carry the canonical control prompt
                             body and must NOT contain the corpus
                             fingerprint (rejected otherwise);
             primed runs:    session must contain Prompt 1 (corpus
                             fingerprint before the translation instruction)
                             AND the canonical Prompt-2 body; the reply is
                             extracted after Prompt 2's closing '## Output'
                             line.
           The session file is never modified; its SHA-256 is recorded.

  verify   [--run <run_id> | --all]
           integrity checks (output hash vs meta, plan consistency) plus the
           structural completeness gate (L-027): non-empty, size floor
           (0.60 x Polish source bytes), head sanity, ISV-tolerant story
           name stems, end marker KONIEC/KONEC/KONĖC. Verdict
           complete/partial/failed preserved as data (D-035).

  evaluate --run <run_id> [--force]
           run the gate if no intake.json exists, refuse for verdict
           'failed' (unless --force), then the Task 008 evaluator (isv-eval,
           unmodified) and the orthographic audit; write evaluation.json
           (+ evaluation/ detail) and orthography.json. No composite score.

  status   show planned / collected / verified / evaluated / usable per run.

  roster   join plan + meta + intake + evaluation + orthography into
           outputs/roster.json and outputs/roster.md (per-dimension only).

  compare  [--run <run_id>]
           the Phase 2A result table: for each of the 18 configurations,
           pair the corpus-primed run against its baseline. Baseline
           preference: a freshly collected Phase-2A control output (intake
           complete), else the Phase-1 baseline output (same config).
           Reports per-dimension deltas (canonical coverage, broader
           resource-supported coverage, unresolved rate, lexical tokens,
           A/B/C counts, orthography-out) with NO composite score and NO
           ranking. The main question is "how much does authentic ISV corpus
           exposure change each model's output?", not "which model wins?".

Phase 2B (authentic ISV Wikipedia article + an independently written Polish
story inspired by its subject) is documented as future work and is NOT
implemented here. Phase 2 must not execute any external LLM call from this
repository.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(ROOT / "src"))

import run_exp004_phase1 as p1  # noqa: E402  (ROSTER, gate, hashes, ...)

from isv_eval.cli import git_commit  # noqa: E402
from isv_eval.orthography import scan_file  # noqa: E402

EXP = ROOT / "experiments" / "exp004-modelscreen"
P2A = EXP / "phase2a"
CORPUS_DIR = P2A / "corpus"
OPERATOR_PROMPTS = P2A / "operator-prompts"
OUTPUTS_DIR = P2A / "outputs"
SESSION_DIR = P2A / "collected-sessions"
CORPUS_FILE = CORPUS_DIR / "tuta-historija-excerpt.txt"
SOURCE_FILE = EXP / "input" / "source.txt"

# Fixed author-supplied reference corpus (SODA Task 019, 2026-09-06).
CORPUS_ID = "tuta-historija"
CORPUS_VERSION = "v1"
TUTA_EXCERPT_SHA256 = (
    "413830fa4ff6aaa8833895a22e7ef1fa5fa3807e5a5a105b7e4050cf7b67a29c")

# Canonical Polish source story (EXP-001..EXP-004 Phase 1 lineage).
SOURCE_SHA256 = p1.EXP003_SOURCE_SHA256

P2A_CONDITIONS = ("p2a-ctl", "p2a-primed")
CTL, PRIMED = P2A_CONDITIONS

# Fingerprints used for prompt-separation and contamination checks.
CORPUS_FP_START = ("Ljudi govoret, že v tamtoj denj bylo je veliko spokojno")
CORPUS_FP_END = "da by prěžiti v tutoj težkoj době"
# The story markers used to locate the translation prompt inside a session.
STORY_TITLE = "Opowieść o Słów, Które Były Jak Siostry"
TRANSLATION_START = "Translate the Polish story below into Interslavic"

PHASE1_PLAN_DATE = "2026-09-06"  # fallback for baseline ids if Phase-1 plan
                                 # is unavailable (the plan carries it)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


# ---------------------------------------------------------------------------
# Phase-2A roster = reconciled Phase-1 usable roster (18), GLM excluded
# ---------------------------------------------------------------------------

def phase2a_roster() -> list[dict]:
    """The authoritative Phase-2A roster: every Phase-1 row that was
    reconciled as usable, i.e. all of run_exp004_phase1.ROSTER except the
    single failed run (GLM 4.5, provider 'zhipu'). Never reconstructed from
    filenames."""
    rows = [row for row in p1.ROSTER if row["provider"] != "zhipu"]
    if len(rows) != 18:
        raise RuntimeError(
            f"expected 18 Phase-1-usable roster rows, found {len(rows)} "
            "(Phase-1 roster changed; reconcile before Phase 2A)")
    return rows


ROSTER = phase2a_roster()


def phase1_number(row: dict) -> int:
    """Row's number in the Phase-1 roster (1..19, GLM=11 skipped here)."""
    return p1.ROSTER.index(row) + 1


def run_id_for(date: str, row: dict, condition: str) -> str:
    if condition not in P2A_CONDITIONS:
        raise ValueError(f"unknown Phase-2A condition {condition!r}")
    return (f"{date}__{row['provider']}__{row['model']}__"
            f"{row['model_version']}__{condition}")


def parse_run_id(run_id: str) -> dict:
    parts = run_id.split("__")
    if len(parts) != 5 or parts[4] not in P2A_CONDITIONS:
        raise ValueError(
            f"run id must be <date>__<provider>__<model>__<model_version>__"
            f"p2a-ctl|p2a-primed, got: {run_id!r}")
    return {"date": parts[0], "provider": parts[1], "model": parts[2],
            "model_version": parts[3], "condition": parts[4]}


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


def baseline_run_id_for(date: str, row: dict) -> str:
    """The Phase-1 baseline run id for this configuration. Prefers the real
    Phase-1 plan (outputs/plan.json) when present; otherwise falls back to
    the documented Phase-1 plan date."""
    p1_plan = p1.load_plan()  # reads p1.OUTPUTS_DIR/plan.json
    for r in p1_plan.get("runs", []):
        if (r["provider"] == row["provider"]
                and r["model"] == row["model"]
                and r["model_version"] == row["model_version"]):
            return r["run_id"]
    return (f"{PHASE1_PLAN_DATE}__{row['provider']}__{row['model']}__"
            f"{row['model_version']}__direct")


def _base_instruction_text(source_text: str) -> str:
    return p1.BASE_INSTRUCTION.read_text(encoding="utf-8").replace(
        "{STORY}", source_text).rstrip() + "\n"


# ---------------------------------------------------------------------------
# prompt rendering
# ---------------------------------------------------------------------------

def _prompt_names(row: dict) -> tuple[str, str, str]:
    nn = phase1_number(row)
    base = (f"{nn:02d}-{row['model']}-{row['model_version']}")
    return (f"ctl-{base}.md",
            f"primed-{base}-msg1.md",
            f"primed-{base}-msg2.md")


def _render_ctl_prompt(row: dict, source_text: str) -> str:
    setting = row["generation_parameters"]
    return "\n".join([
        f"# EXP-004 — Phase 2A — control (clean direct baseline) — "
        f"{row['label']}",
        "",
        "> COPY THIS ENTIRE FILE INTO " + row["interface"]
        + " in a NEW, FRESH session.",
        "> Do not modify anything. Run this single message ONLY — no",
        "> reference text, no preceding corpus. Save the model's complete",
        "> reply byte-for-byte and hand it to the collect step.",
        "",
        "---",
        "",
        "Experiment ID: EXP-004",
        "Phase: 2A — control condition (clean direct translation; no corpus)",
        "Condition: control — the identical task to the Phase-1 baseline "
        "(same instruction, same Polish source story, fresh session, no ISV "
        "reference material)",
        f"Target model: {row['label']}",
        f"Provider / interface: {row['provider']} / {row['interface']}",
        f"Model version / settings: {row['model_version']} ({setting})",
        "",
        "---",
        "",
        _base_instruction_text(source_text),
    ])


def _render_primed_msg1(row: dict, corpus_text: str) -> str:
    setting = row["generation_parameters"]
    return "\n".join([
        f"# EXP-004 — Phase 2A — corpus priming — {row['label']} — "
        "message 1 of 2",
        "",
        "> COPY THIS ENTIRE FILE INTO " + row["interface"]
        + " as the FIRST message of a NEW, FRESH session.",
        "> Do not modify anything. Send message 1, WAIT for the model's",
        "> short confirmation, THEN send message 2 (the file ending",
        "> \"-msg2\") in the SAME session.",
        "",
        "---",
        "",
        "Experiment ID: EXP-004",
        "Phase: 2A — corpus priming (in-context language reference)",
        "Condition: primed — message 1 of 2 (reference text only; no "
        "translation in this message)",
        f"Target model: {row['label']}",
        f"Provider / interface: {row['provider']} / {row['interface']}",
        f"Model version / settings: {row['model_version']} ({setting})",
        "",
        "---",
        "",
        "Below is an authentic text written in Medžuslovjansky "
        "(Interslavic). Treat it as REFERENCE MATERIAL ONLY.",
        "",
        "Study this text carefully as a language reference. Pay attention "
        "to:",
        "- vocabulary and word formation;",
        "- morphology (noun and adjective endings, verb forms, pronouns, "
        "cases);",
        "- syntax and word order;",
        "- orthography and spelling conventions;",
        "- stylistic and narrative patterns.",
        "",
        "Do NOT translate, summarize, reproduce, modify or continue this "
        "text.",
        "Do NOT imitate its particular sentences. Do NOT answer questions "
        "about its story or content. Do NOT produce any Medžuslovjansky "
        "text in this message.",
        "",
        "Retain the useful language information — vocabulary, morphology, "
        "syntax, orthography and style — for the translation task in the "
        "next message of this same conversation. If you have understood "
        "and are ready, reply with a short confirmation only (one or two "
        "sentences). No translation.",
        "",
        "## Reference text (authentic Medžuslovjansky)",
        "",
        corpus_text.rstrip("\n"),
    ]) + "\n"


def _render_primed_msg2(row: dict, source_text: str) -> str:
    setting = row["generation_parameters"]
    return "\n".join([
        f"# EXP-004 — Phase 2A — corpus priming — {row['label']} — "
        "message 2 of 2",
        "",
        "> COPY THIS ENTIRE FILE INTO " + row["interface"]
        + " as the SECOND message of the SAME session as message 1 (send "
        "it after the model's short confirmation).",
        "> Do not modify anything. Save the model's complete reply (the "
        "translation) byte-for-byte.",
        "",
        "---",
        "",
        "Experiment ID: EXP-004",
        "Phase: 2A — corpus priming (in-context language reference)",
        "Condition: primed — message 2 of 2 (translation task)",
        f"Target model: {row['label']}",
        f"Provider / interface: {row['provider']} / {row['interface']}",
        f"Model version / settings: {row['model_version']} ({setting})",
        "",
        "---",
        "",
        "Using the authentic Medžuslovjansky text from the previous message "
        "of this conversation as a language reference, translate the Polish "
        "text below into Medžuslovjansky.",
        "",
        _base_instruction_text(source_text),
    ])


# ---------------------------------------------------------------------------
# prepare
# ---------------------------------------------------------------------------

def _ensure_source() -> Path:
    if not SOURCE_FILE.is_file():
        raise RuntimeError(
            f"Polish source story missing at {SOURCE_FILE}; run "
            "scripts/run_exp004_phase1.py prepare --date YYYY-MM-DD first")
    actual = sha256_file(SOURCE_FILE)
    if actual != SOURCE_SHA256:
        raise RuntimeError(
            f"{SOURCE_FILE} sha256 {actual[:16]}... does not match the "
            f"canonical source {SOURCE_SHA256[:16]}...; refusing to use a "
            "different story")
    return SOURCE_FILE


def _ensure_corpus() -> Path:
    if not CORPUS_FILE.is_file():
        raise RuntimeError(
            f"reference corpus missing at {CORPUS_FILE}; it is the "
            "author-supplied Phase-2A text (SODA Task 019)")
    actual = sha256_file(CORPUS_FILE)
    if actual != TUTA_EXCERPT_SHA256:
        raise RuntimeError(
            f"{CORPUS_FILE} sha256 {actual[:16]}... does not match the "
            f"recorded corpus {TUTA_EXCERPT_SHA256[:16]}...; an accidental "
            "edit would break the fixed-corpus fairness invariant")
    return CORPUS_FILE


def run_prepare(date: str, force: bool = False) -> int:
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date or ""):
        print("error: --date YYYY-MM-DD is required (run ids carry the "
              "planned generation date)", file=sys.stderr)
        return 2
    source = _ensure_source()
    corpus = _ensure_corpus()
    source_text = source.read_text(encoding="utf-8")
    corpus_text = corpus.read_text(encoding="utf-8")
    source_sha = sha256_bytes(source_text.encode("utf-8"))
    corpus_sha = sha256_bytes(corpus_text.encode("utf-8"))

    plan_path = OUTPUTS_DIR / "plan.json"
    if plan_path.is_file() and not force:
        print(f"error: {plan_path} already exists; use --force to rewrite "
              "(changing the plan invalidates collected runs)",
              file=sys.stderr)
        return 2

    OPERATOR_PROMPTS.mkdir(parents=True, exist_ok=True)
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    files: list[dict] = []
    runs: list[dict] = []

    for row in ROSTER:
        ctl_name, msg1_name, msg2_name = _prompt_names(row)
        rendered = {
            ctl_name: _render_ctl_prompt(row, source_text),
            msg1_name: _render_primed_msg1(row, corpus_text),
            msg2_name: _render_primed_msg2(row, source_text),
        }
        # primed prompt pair hashes: msg2 carries the translation task
        for fname, text in rendered.items():
            path = OPERATOR_PROMPTS / fname
            prompt_sha = sha256_bytes(text.encode("utf-8"))
            if path.is_file() and not force:
                if sha256_bytes(path.read_bytes()) != prompt_sha:
                    print(f"error: {path} exists with different content; "
                          "--force to overwrite", file=sys.stderr)
                    return 2
            path.write_text(text, encoding="utf-8")
            condition = CTL if fname.startswith("ctl-") else PRIMED
            message = None if condition == CTL else (
                1 if fname.endswith("-msg1.md") else 2)
            run_id = run_id_for(date, row, condition)
            files.append({"file": fname, "run_id": run_id,
                          "condition": condition, "message": message,
                          "prompt_sha256": prompt_sha,
                          "bytes": len(text.encode("utf-8"))})

        ctl_id = run_id_for(date, row, CTL)
        primed_id = run_id_for(date, row, PRIMED)
        ctl_prompt_sha = sha256_bytes(
            rendered[ctl_name].encode("utf-8"))
        msg2_prompt_sha = sha256_bytes(
            rendered[msg2_name].encode("utf-8"))
        runs.append({
            "run_id": ctl_id,
            "phase": "2a", "condition": CTL, "phase1_number": phase1_number(row),
            "provider": row["provider"], "model": row["model"],
            "model_version": row["model_version"], "label": row["label"],
            "interface": row["interface"],
            "generation_parameters": row["generation_parameters"],
            "custom_gpt": row["custom_gpt"],
            "prompt_files": [ctl_name],
            "translation_prompt_sha256": ctl_prompt_sha,
            "baseline_run_id": baseline_run_id_for(date, row),
        })
        runs.append({
            "run_id": primed_id,
            "phase": "2a", "condition": PRIMED, "phase1_number": phase1_number(row),
            "provider": row["provider"], "model": row["model"],
            "model_version": row["model_version"], "label": row["label"],
            "interface": row["interface"],
            "generation_parameters": row["generation_parameters"],
            "custom_gpt": row["custom_gpt"],
            "prompt_files": [msg1_name, msg2_name],
            "translation_prompt_sha256": msg2_prompt_sha,
            "baseline_run_id": baseline_run_id_for(date, row),
        })

    plan = {
        "experiment_id": "exp004",
        "artifact": "run-plan",
        "phase": "2a",
        "date": date,
        "generator": "scripts/run_exp004_phase2a.py prepare",
        "generator_commit": git_commit(),
        "hypothesis": "exposing an LLM to authentic Medžuslovjansky text "
                      "immediately before translation changes its generated "
                      "Medžuslovjansky (in-context learning / corpus "
                      "priming / contextual grounding / reference-text "
                      "conditioning; NOT training)",
        "source": {"file": (str(source.relative_to(ROOT))
                            if source.is_relative_to(ROOT)
                            else str(source)),
                   "sha256": source_sha,
                   "bytes": source.stat().st_size},
        "corpus": {"id": CORPUS_ID, "version": CORPUS_VERSION,
                   "file": (str(corpus.relative_to(ROOT))
                            if corpus.is_relative_to(ROOT)
                            else str(corpus)),
                   "sha256": corpus_sha,
                   "bytes": corpus.stat().st_size,
                   "note": "Fixed authentic Medžuslovjansky reference text "
                           "supplied by the project author (Task 019); "
                           "identical for every model in the primed "
                           "condition"},
        "conditions": {
            CTL: "control — same clean direct-translation task as Phase 1, "
                 "fresh session, no corpus (Phase-1 outputs satisfy it; a "
                 "fresh control may be re-executed)",
            PRIMED: "corpus primed — msg1 authentic ISV reference text "
                    "(study only) + msg2 translation of the same Polish "
                    "story, in ONE session",
        },
        "note": "Phase 2A keeps the full reconciled 18-model Phase-1 roster "
                "(the author decided NOT to narrow to 3-5 models yet). "
                "GLM 4.5 is excluded (Phase-1 intake failed). LLM execution "
                "is external; this plan never calls an LLM.",
        "runs": runs,
    }
    plan_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2),
                         encoding="utf-8")

    manifest = {
        "artifact": "operator-prompt-manifest",
        "experiment_id": "exp004",
        "phase": "2a",
        "date": date,
        "generator": "scripts/run_exp004_phase2a.py prepare",
        "generator_commit": git_commit(),
        "corpus": {"id": CORPUS_ID, "version": CORPUS_VERSION,
                   "file": plan["corpus"]["file"],
                   "sha256": corpus_sha, "bytes": corpus.stat().st_size},
        "source": {"file": plan["source"]["file"], "sha256": source_sha},
        "note": "Prompt files embed the copyrighted Polish story and the "
                "author-supplied corpus and stay local (gitignored); this "
                "manifest records prompt hashes only.",
        "files": sorted(files, key=lambda f: f["file"]),
    }
    (OPERATOR_PROMPTS / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[prepare] prompts -> {OPERATOR_PROMPTS}/")
    print(f"[prepare] plan     -> {plan_path}")
    for r in runs:
        print(f"  {r['run_id']:70s} prompt {r['translation_prompt_sha256'][:12]}")
    print(f"{len(runs)} planned run(s) ({len(runs)//2} configurations × "
          f"{CTL}/{PRIMED}); source sha256 {source_sha[:16]}...; corpus "
          f"sha256 {corpus_sha[:16]}...")
    return 0


# ---------------------------------------------------------------------------
# collect
# ---------------------------------------------------------------------------

def _plan_entry(run_id: str) -> dict | None:
    return next((r for r in load_plan().get("runs", [])
                 if r["run_id"] == run_id), None)


def _meta_base(run_id: str, plan_entry: dict, row: dict,
               generation_date: str) -> dict:
    parts = parse_run_id(run_id)
    return {
        "run_id": run_id,
        "experiment_id": "exp004",
        "phase": "2a",
        "condition": plan_entry["condition"],
        "label": row["label"],
        "interface": row["interface"],
        "model": row["model"],
        "provider": row["provider"],
        "model_version": row["model_version"],
        "generation_parameters": row["generation_parameters"],
        "generation_date": (generation_date if generation_date != "unknown"
                            else parts["date"]),
        "baseline_run_id": plan_entry["baseline_run_id"],
        "source": {"sha256": load_plan()["source"]["sha256"]},
        "corpus": dict(load_plan()["corpus"]),
        "resources": p1.resource_versions(),
    }


def run_collect(run_id: str, output: Path, generation_date: str,
                status: str = "collected_external_output",
                access_verdict: str = "unknown",
                access_note: str = "",
                note: str = "") -> int:
    row = roster_entry(run_id)
    if row is None:
        print(f"error: unknown run id {run_id!r} (not a Phase-2A roster row)",
              file=sys.stderr)
        return 2
    if status not in p1.STATUSES:
        print(f"error: unknown status {status!r}", file=sys.stderr)
        return 2
    if access_verdict not in p1.ACCESS_VERDICTS:
        print(f"error: unknown access verdict {access_verdict!r}",
              file=sys.stderr)
        return 2
    plan_entry = _plan_entry(run_id)
    if plan_entry is None:
        print("error: run not in the Phase-2A plan; run "
              "`scripts/run_exp004_phase2a.py prepare --date <date>` first",
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

    meta = _meta_base(run_id, plan_entry, row, generation_date)
    meta.update({
        "status": status,
        "access": {
            "filter_verdict": access_verdict,
            "quota_observed": access_note,
            "criteria": "D-036/§5.1 (as recorded in Phase 1); observed by "
                        "the operator at execution time.",
        },
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "collected_by": "scripts/run_exp004_phase2a.py collect",
        "prompt": {"files": plan_entry["prompt_files"],
                   "translation_prompt_sha256":
                       plan_entry["translation_prompt_sha256"]},
        "output": {"file": str(dst), "sha256": sha256_bytes(data),
                   "bytes": len(data)},
        "note": ("Raw LLM output stored byte-for-byte; never modified. "
                 "Empty or failed runs are preserved and documented, not "
                 "deleted." + (f" {note}" if note else "")),
    })
    (out_dir / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[collect] {run_id}")
    print(f"  label/interface: {row['label']} / {row['interface']}")
    print(f"  condition: {meta['condition']}; baseline: "
          f"{meta['baseline_run_id']}")
    print(f"  output sha256: {meta['output']['sha256']}")
    print(f"  status: {meta['status']}; access filter: "
          f"{meta['access']['filter_verdict']}")
    return 0


# ---------------------------------------------------------------------------
# collect-session (contamination-controlled extraction)
# ---------------------------------------------------------------------------

def _corpus_fingerprints() -> tuple[bytes, bytes]:
    text = CORPUS_FILE.read_text(encoding="utf-8")
    return (CORPUS_FP_START.encode("utf-8"),
            CORPUS_FP_END.encode("utf-8"))


def _translation_body(text: str) -> str:
    """The invariant region of a translation prompt (control or primed
    msg2): from the standard instruction start through the prompt's closing
    '## Output' line."""
    start = text.find(TRANSLATION_START)
    if start < 0:
        return ""
    end = text.rfind("## Output")
    if end < 0:
        return text[start:]
    return text[start:end + len("## Output")]


def _strip_trailing_prompt_boilerplate(reply: bytes) -> bytes:
    """Some author session files include the prompt's final instruction
    sentence(s) after the '## Output' marker (the base instruction ends
    '## Output\\n\\nReturn the complete Interslavic translation of the
    source text, and nothing\\nelse.\\n'). The reply boundary is the
    marker, so drop that known boilerplate prefix when present. The phrase
    is distinctive enough that a genuine reply starting with it is not a
    realistic risk."""
    boilerplate = (b"Return the complete Interslavic translation of the "
                   b"source text, and nothing\nelse.\n")
    if reply.startswith(boilerplate):
        return reply[len(boilerplate):]
    return reply


def _split_primed_reply(raw: bytes) -> tuple[bytes, bytes]:
    """Split a 2-message primed session file (msg1 + reply1 + msg2 + reply2)
    at msg2's closing '## Output' marker. The marker that matters is the
    first '## Output' occurring AFTER the translation instruction starts
    (reply1 sits before it and is irrelevant). Returns (prefix, reply)."""
    text = raw.decode("utf-8", errors="replace")
    start = text.find(TRANSLATION_START)
    if start < 0:
        return raw, b""
    marker = b"## Output\n"
    idx = raw.find(marker, start)
    if idx < 0:
        return raw, b""
    pos = idx + len(marker)
    while pos < len(raw) and raw[pos:pos + 1] in (b"\n", b"\r"):
        pos += 1
    return raw[:idx], _strip_trailing_prompt_boilerplate(raw[pos:])


def run_collect_session(run_id: str, session: Path, generation_date: str,
                        status: str = "collected_external_output",
                        access_verdict: str = "unknown",
                        access_note: str = "",
                        note: str = "") -> int:
    """Register the model reply embedded in an author session file, with
    condition-specific contamination controls (see module docstring)."""
    row = roster_entry(run_id)
    if row is None:
        print(f"error: unknown run id {run_id!r} (not a Phase-2A roster row)",
              file=sys.stderr)
        return 2
    if status not in p1.STATUSES:
        print(f"error: unknown status {status!r}", file=sys.stderr)
        return 2
    if access_verdict not in p1.ACCESS_VERDICTS:
        print(f"error: unknown access verdict {access_verdict!r}",
              file=sys.stderr)
        return 2
    plan_entry = _plan_entry(run_id)
    if plan_entry is None:
        print("error: run not in the Phase-2A plan; prepare first",
              file=sys.stderr)
        return 2
    if not session.is_file():
        print(f"error: session file not found: {session}", file=sys.stderr)
        return 2
    out_dir = OUTPUTS_DIR / run_id
    dst = out_dir / "output.txt"
    if dst.exists():
        print(f"error: {dst} already exists; refusing to overwrite "
              "(never overwrite an existing run)", file=sys.stderr)
        return 2

    session_bytes = session.read_bytes()
    session_text = session_bytes.decode("utf-8", errors="replace")
    condition = plan_entry["condition"]
    fp_start, fp_end = _corpus_fingerprints()

    # canonical translation prompt (the file whose reply is the output)
    trans_file = (OPERATOR_PROMPTS / plan_entry["prompt_files"][-1])
    canonical_text = trans_file.read_text(encoding="utf-8")
    canonical_body = _translation_body(canonical_text)
    if not canonical_body:
        print(f"error: cannot locate the canonical translation body in "
              f"{trans_file.name}", file=sys.stderr)
        return 2

    if condition == CTL:
        # control: the translation prompt is the ONLY message; the session
        # must match its body and must NOT contain the reference corpus.
        if _translation_body(session_text) != canonical_body:
            print(f"error: session file's translation instruction body does "
                  f"not match the canonical control prompt for {run_id}; "
                  "refusing to collect", file=sys.stderr)
            return 2
        if (fp_start in session_bytes or fp_end in session_bytes):
            print(f"error: control session for {run_id} CONTAINS the "
                  "reference corpus (or its fingerprint) — the control "
                  "condition must never include ISV reference material; "
                  "refusing to collect (conversation contamination)",
                  file=sys.stderr)
            return 2
        prefix, reply = p1.split_session_reply(session_bytes)
        reply = _strip_trailing_prompt_boilerplate(reply)
    else:
        # primed: msg1 (corpus) must precede the translation instruction;
        # msg2 body must match the canonical msg2 prompt.
        body_start = session_text.find(TRANSLATION_START)
        before = session_bytes[:body_start] if body_start >= 0 else b""
        if not (fp_start in before and fp_end in before):
            print(f"error: primed session for {run_id} does not contain the "
                  "reference corpus BEFORE the translation instruction — "
                  "the priming condition requires msg1 (corpus) and msg2 "
                  "(translation) in the same session; refusing to collect",
                  file=sys.stderr)
            return 2
        if _translation_body(session_text) != canonical_body:
            print(f"error: session file's translation instruction body does "
                  f"not match the canonical Prompt-2 for {run_id}; refusing "
                  "to collect", file=sys.stderr)
            return 2
        prefix, reply = _split_primed_reply(session_bytes)

    if not reply.strip():
        print(f"error: no model reply found after the '## Output' marker "
              f"in {session.name}", file=sys.stderr)
        return 2

    out_dir.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(reply)  # byte-for-byte raw reply, never modified

    meta = _meta_base(run_id, plan_entry, row, generation_date)
    meta.update({
        "status": status,
        "access": {
            "filter_verdict": access_verdict,
            "quota_observed": access_note,
            "criteria": "D-036/§5.1; observed by the operator at execution "
                        "time.",
        },
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "collected_by": "scripts/run_exp004_phase2a.py collect-session",
        "prompt": {"files": plan_entry["prompt_files"],
                   "translation_prompt_sha256":
                       plan_entry["translation_prompt_sha256"]},
        "session": {
            "file": str(session),
            "name": session.name,
            "sha256": sha256_bytes(session_bytes),
            "condition": condition,
            "contamination_checks": {
                "corpus_before_translation":
                    condition == PRIMED and
                    (fp_start in session_bytes and fp_end in session_bytes),
                "corpus_in_control": condition == CTL and (
                    fp_start in session_bytes or fp_end in session_bytes),
            },
        },
        "output": {"file": str(dst), "sha256": sha256_bytes(reply),
                   "bytes": len(reply)},
        "note": ("Raw model reply extracted from the author's session file "
                 "and stored byte-for-byte; never modified. The session "
                 "file itself is preserved unmodified under "
                 "collected-sessions/." + (f" {note}" if note else "")),
    })
    (out_dir / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[collect-session] {run_id}")
    print(f"  condition: {condition}; session: {session.name} -> output.txt "
          f"({len(reply)} B)")
    print(f"  output sha256: {meta['output']['sha256']}")
    print(f"  status: {meta['status']}; access filter: "
          f"{meta['access']['filter_verdict']}")
    return 0


# ---------------------------------------------------------------------------
# verify (integrity + Phase-1 completeness gate)
# ---------------------------------------------------------------------------

def _verify_integrity(run_id: str, plan_entry: dict) -> list[str]:
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
    if meta and plan_entry is not None:
        if meta["prompt"]["translation_prompt_sha256"] != \
                plan_entry["translation_prompt_sha256"]:
            errors.append("translation prompt hash differs from plan")
        if meta.get("condition") != plan_entry["condition"]:
            errors.append("condition mismatch meta vs plan")
        if meta["source"]["sha256"] != load_plan()["source"]["sha256"]:
            errors.append("source hash differs from plan")
        if meta["corpus"]["sha256"] != load_plan()["corpus"]["sha256"]:
            errors.append("corpus hash differs from plan")
        for fname in plan_entry["prompt_files"]:
            pf = OPERATOR_PROMPTS / fname
            if not pf.is_file():
                errors.append(f"prompt file missing: {pf}")
    return errors


def run_verify(run_id: str | None = None,
               size_floor: int | None = None) -> int:
    plan = load_plan()
    runs: list[tuple[str, dict | None]] = []
    if run_id:
        runs.append((run_id, _plan_entry(run_id)))
    else:
        for r in plan.get("runs", []):
            runs.append((r["run_id"], r))
    if not runs:
        print("nothing to verify; prepare a plan first", file=sys.stderr)
        return 2
    src = plan.get("source") or {}
    sp = (Path(src["file"]) if src.get("file")
          and Path(src["file"]).is_absolute() else ROOT / (src["file"] or ""))
    source_bytes = sp.stat().st_size if sp.is_file() else 0

    problems = 0
    for rid, plan_entry in runs:
        out_dir = OUTPUTS_DIR / rid
        if not (out_dir / "output.txt").is_file():
            print(f"[skip] {rid}: no collected output")
            continue
        integrity = _verify_integrity(rid, plan_entry)
        floor = size_floor if size_floor is not None else int(
            0.60 * source_bytes)
        gate = p1._gate_checks(out_dir, source_bytes, floor)
        verdict = p1._intake_verdict(gate)
        meta = load_meta(rid)
        intake = {
            "run_id": rid,
            "condition": meta.get("condition"),
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
    print(f"\n{len(runs)} planned run(s) checked.")
    return 1 if problems else 0


# ---------------------------------------------------------------------------
# evaluate
# ---------------------------------------------------------------------------

def _pct(v: float | None) -> str:
    return f"{v * 100:.2f}%" if v is not None else "n/a"


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
        print("[evaluate] no intake.json; running the completeness gate "
              "first")
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
        "phase": "2a",
        "condition": meta.get("condition"),
        "label": meta.get("label"),
        "model": meta.get("model"),
        "provider": meta.get("provider"),
        "model_version": meta.get("model_version"),
        "generation_parameters": meta.get("generation_parameters"),
        "baseline_run_id": meta.get("baseline_run_id"),
        "intake_verdict": intake["verdict"],
        "usable": intake["verdict"] == "complete",
        "metrics": m,
        "output_files": report["output_files"],
    }
    (out_dir / "evaluation.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8")

    ortho = scan_file(text)
    od = ortho.as_dict()
    (out_dir / "orthography.json").write_text(json.dumps({
        "run_id": run_id,
        "condition": meta.get("condition"),
        "inventory": "official Interslavic alphabet "
                     "(src/isv_eval/orthography.py, D-040)",
        "metrics": od,
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        f"# EXP-004 Phase 2A — evaluation — {run_id}",
        "",
        f"{meta.get('label', '?')} ({meta.get('provider')}, version "
        f"{meta.get('model_version')}) · condition "
        f"{meta.get('condition')} · generated {meta.get('generation_date')} "
        f"· intake {intake['verdict']} · usable {summary['usable']}",
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
    print(f"  orthography outside-inventory: {od['outside_inventory']}")
    return 0


# ---------------------------------------------------------------------------
# status / roster
# ---------------------------------------------------------------------------

def run_status() -> int:
    plan = load_plan()
    if not plan.get("runs"):
        print("no plan; run `scripts/run_exp004_phase2a.py prepare "
              "--date YYYY-MM-DD` first")
        return 0
    print(f"{'run_id':<70} {'output':<7} {'intake':<10} {'eval':<5} "
          f"{'usable':<7}")
    n_out = n_int = n_ev = n_us = 0
    for r in plan["runs"]:
        rid = r["run_id"]
        out_dir = OUTPUTS_DIR / rid
        has_out = (out_dir / "output.txt").is_file()
        intake = out_dir / "intake.json"
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
        print(f"{rid:<70} {'yes' if has_out else 'no':<7} "
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
        intake = (json.loads(intake_p.read_text(encoding="utf-8"))
                  if intake_p.is_file() else {})
        ev = (json.loads(ev_p.read_text(encoding="utf-8"))
              if ev_p.is_file() else {})
        rows.append({
            "run_id": rid,
            "condition": r["condition"],
            "phase1_number": r["phase1_number"],
            "label": r["label"],
            "provider": r["provider"],
            "model": r["model"],
            "model_version": r["model_version"],
            "generation_parameters": r["generation_parameters"],
            "interface": r["interface"],
            "baseline_run_id": r["baseline_run_id"],
            "collected": (out_dir / "output.txt").is_file(),
            "status": meta.get("status", None),
            "access": meta.get("access", {}),
            "intake_verdict": intake.get("verdict", None),
            "intake_reasons": intake.get("reasons", []),
            "metrics": ev.get("metrics"),
            "usable": ev.get("usable"),
            "orthography": (json.loads(ortho_p.read_text(
                encoding="utf-8")).get("metrics")
                if ortho_p.is_file() else None),
        })
    out = {"experiment_id": "exp004", "phase": "2a",
           "generator": "scripts/run_exp004_phase2a.py roster",
           "note": "Metrics are separate evidence dimensions; no ranking "
                   "and no composite score.",
           "rows": rows}
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUTS_DIR / "roster.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = [
        "# EXP-004 Phase 2A — roster (corpus priming)",
        "",
        "| run | condition | label | access | intake | usable | canon. | "
        "broader | unres. | tok | ortho out |",
        "|---|---|---|---|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        m = row["metrics"] or {}
        o = row["orthography"] or {}
        access = (row["access"] or {}).get("filter_verdict", "—")
        lines.append(
            f"| {row['run_id']} | {row['condition']} | {row['label']} | "
            f"{access} | {row['intake_verdict'] or '—'} | "
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
# compare (primed vs baseline; per-dimension deltas only)
# ---------------------------------------------------------------------------

def _run_metrics(run_id: str) -> dict | None:
    """Metrics of an evaluated run inside this phase-2A outputs dir."""
    ev_p = OUTPUTS_DIR / run_id / "evaluation.json"
    if not ev_p.is_file():
        return None
    ev = json.loads(ev_p.read_text(encoding="utf-8"))
    return ev.get("metrics")


def _phase1_metrics(phase1_run_id: str) -> dict | None:
    ev_p = p1.OUTPUTS_DIR / phase1_run_id / "evaluation.json"
    if not ev_p.is_file():
        return None
    ev = json.loads(ev_p.read_text(encoding="utf-8"))
    if ev.get("usable") is not True:
        return None
    return ev.get("metrics")


def _baseline_metrics(plan_entry: dict) -> tuple[dict | None, str]:
    """(metrics, source) of the baseline for a primed run. Preference:
    1) a freshly collected Phase-2A control (p2a-ctl) of the same
    configuration (same run date as the primed run); 2) the Phase-1 direct
    baseline output."""
    primed_parts = plan_entry["run_id"].split("__")
    p2a_ctl_id = "__".join(primed_parts[:4] + [CTL])
    m = _run_metrics(p2a_ctl_id)
    if m is not None:
        return m, CTL
    return _phase1_metrics(plan_entry["baseline_run_id"]), \
        "phase1-baseline"


def _ortho_out(run_dir: Path) -> int | None:
    ortho_p = run_dir / "orthography.json"
    if not ortho_p.is_file():
        return None
    od = json.loads(ortho_p.read_text(encoding="utf-8"))
    return od.get("metrics", {}).get("outside_inventory")


def _delta(a: float | None, b: float | None) -> float | None:
    return (round((a or 0.0) - (b or 0.0), 6)
            if a is not None and b is not None else None)


def _signed(v: float | None, digits: int = 2) -> str:
    if v is None:
        return "—"
    sign = "+" if v >= 0 else ""
    return f"{sign}{v:.{digits}f}"


def run_compare(run_id: str | None = None) -> int:
    plan = load_plan()
    if not plan.get("runs"):
        print("no plan; prepare first", file=sys.stderr)
        return 2
    primed_runs = [r for r in plan["runs"] if r["condition"] == PRIMED]
    rows: list[dict] = []
    for r in primed_runs:
        if run_id and r["run_id"] != run_id:
            continue
        rid = r["run_id"]
        out_dir = OUTPUTS_DIR / rid
        intake_p = out_dir / "intake.json"
        intake = (json.loads(intake_p.read_text(encoding="utf-8"))
                  if intake_p.is_file() else {})
        pm = _run_metrics(rid)
        bm, base_source = _baseline_metrics(r)
        if pm is None:
            rows.append({"run_id": rid, "label": r["label"],
                         "primed_intake": intake.get("verdict"),
                         "baseline_run_id": r["baseline_run_id"],
                         "error": "primed run not evaluated yet"})
            continue
        if bm is None:
            rows.append({"run_id": rid, "label": r["label"],
                         "primed_intake": intake.get("verdict"),
                         "baseline_run_id": r["baseline_run_id"],
                         "baseline_source": "missing",
                         "error": "no baseline metrics (fresh p2a-ctl or "
                                  "Phase-1 baseline) available"})
            continue
        row = {
            "run_id": rid,
            "label": r["label"],
            "provider": r["provider"],
            "model": r["model"],
            "model_version": r["model_version"],
            "primed_intake": intake.get("verdict"),
            "baseline_run_id": r["baseline_run_id"],
            "baseline_source": base_source,
            "deltas": {
                "canonical_coverage_pp": _delta(
                    pm.get("canonical_coverage"),
                    bm.get("canonical_coverage")),
                "broader_resource_supported_coverage_pp": _delta(
                    pm.get("broader_resource_supported_coverage"),
                    bm.get("broader_resource_supported_coverage")),
                "unresolved_rate_pp": _delta(
                    pm.get("unresolved_rate"), bm.get("unresolved_rate")),
                "lexical_tokens": _delta(
                    pm.get("total_tokens"), bm.get("total_tokens")),
                "exact_dictionary_matches": _delta(
                    pm.get("exact_dictionary_matches"),
                    bm.get("exact_dictionary_matches")),
                "morphologically_valid_forms": _delta(
                    pm.get("morphologically_valid_forms"),
                    bm.get("morphologically_valid_forms")),
            },
            "primed": {"canonical_coverage": pm.get("canonical_coverage"),
                       "broader": pm.get("broader_resource_supported_coverage"),
                       "unresolved_rate": pm.get("unresolved_rate"),
                       "tokens": pm.get("total_tokens"),
                       "ortho_out": _ortho_out(out_dir)},
            "baseline": {"canonical_coverage": bm.get("canonical_coverage"),
                         "broader": bm.get("broader_resource_supported_coverage"),
                         "unresolved_rate": bm.get("unresolved_rate"),
                         "tokens": bm.get("total_tokens"),
                         "ortho_out": None},
        }
        rows.append(row)

    out = {
        "experiment_id": "exp004",
        "phase": "2a",
        "artifact": "priming-comparison",
        "generator": "scripts/run_exp004_phase2a.py compare",
        "generator_commit": git_commit(),
        "hypothesis": "authentic ISV corpus exposure changes generation "
                      "(in-context learning / corpus priming / contextual "
                      "grounding / reference-text conditioning)",
        "note": "Per-dimension deltas only: canonical coverage, broader "
                "resource-supported coverage, unresolved rate, lexical "
                "tokens, A/B/C counts. NO composite score, NO ranking. A "
                "positive canonical-coverage delta is evidence, not a "
                "quality verdict (L-033).",
        "corpus": plan.get("corpus"),
        "rows": rows,
    }
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUTS_DIR / "compare.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# EXP-004 Phase 2A — corpus-primed vs baseline (per-dimension "
        "deltas)",
        "",
        f"Corpus: {plan.get('corpus', {}).get('id')} "
        f"{plan.get('corpus', {}).get('version')} "
        f"(sha256 {str(plan.get('corpus', {}).get('sha256', ''))[:16]}...). "
        "Baseline = freshly collected Phase-2A control when present, else "
        "the Phase-1 direct baseline of the same configuration.",
        "",
        "Δ = primed − baseline (coverage/unresolved in percentage points). "
        "Evidence dimensions are NOT merged and are NOT a composite score.",
        "",
        "| configuration | base | canon Δ | broader Δ | unres Δ | tok Δ | "
        "A Δ | B Δ | primed ortho out |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        if "error" in row:
            lines.append(
                f"| {row['label']} | {row.get('baseline_source', '?')} | "
                f"— (no comparison: {row['error']}) |")
            continue
        d = row["deltas"]
        lines.append(
            f"| {row['label']} | {row['baseline_source']} | "
            f"{_signed(d['canonical_coverage_pp'])} | "
            f"{_signed(d['broader_resource_supported_coverage_pp'])} | "
            f"{_signed(d['unresolved_rate_pp'])} | "
            f"{_signed(d['lexical_tokens'], 0)} | "
            f"{_signed(d['exact_dictionary_matches'], 0)} | "
            f"{_signed(d['morphologically_valid_forms'], 0)} | "
            f"{row['primed']['ortho_out'] if row['primed']['ortho_out'] is not None else '—'} |")
    (OUTPUTS_DIR / "compare.md").write_text("\n".join(lines) + "\n",
                                            encoding="utf-8")
    compared = [x for x in rows if "error" not in x]
    print(f"[compare] {len(compared)}/{len(primed_runs)} configurations "
          f"compared -> outputs/compare.json + compare.md")
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
    p_col.add_argument("--status", default="collected_external_output",
                       choices=p1.STATUSES)
    p_col.add_argument("--access-verdict", default="unknown",
                       choices=p1.ACCESS_VERDICTS)
    p_col.add_argument("--access-note", default="")
    p_col.add_argument("--note", default="")

    p_sec = sub.add_parser(
        "collect-session",
        help="register the raw reply embedded in an author session file "
             "(contamination-controlled, Phase 2A)")
    p_sec.add_argument("--run", required=True, dest="run_id")
    p_sec.add_argument("--session", required=True, type=Path)
    p_sec.add_argument("--generation-date", default="unknown")
    p_sec.add_argument("--status", default="collected_external_output",
                       choices=p1.STATUSES)
    p_sec.add_argument("--access-verdict", default="unknown",
                       choices=p1.ACCESS_VERDICTS)
    p_sec.add_argument("--access-note", default="")
    p_sec.add_argument("--note", default="")

    p_ver = sub.add_parser("verify", help="integrity + completeness gate")
    p_ver.add_argument("--run", default=None, dest="run_id")
    p_ver.add_argument("--size-floor", type=int, default=None)

    p_ev = sub.add_parser("evaluate", help="evaluate a collected output")
    p_ev.add_argument("--run", required=True, dest="run_id")
    p_ev.add_argument("--force", action="store_true")

    sub.add_parser("status", help="show run progress")
    sub.add_parser("roster", help="write the Phase-2A roster summary")
    p_cmp = sub.add_parser(
        "compare",
        help="primed vs baseline per-dimension delta table")
    p_cmp.add_argument("--run", default=None, dest="run_id")

    args = parser.parse_args(argv)
    if args.command == "prepare":
        return run_prepare(args.date, args.force)
    if args.command == "collect":
        return run_collect(args.run_id, args.output, args.generation_date,
                           args.status, args.access_verdict,
                           args.access_note, args.note)
    if args.command == "collect-session":
        return run_collect_session(args.run_id, args.session,
                                   args.generation_date, args.status,
                                   args.access_verdict, args.access_note,
                                   args.note)
    if args.command == "verify":
        return run_verify(args.run_id, args.size_floor)
    if args.command == "evaluate":
        return run_evaluate(args.run_id, args.force)
    if args.command == "status":
        return run_status()
    if args.command == "roster":
        return run_roster()
    if args.command == "compare":
        return run_compare(args.run_id)
    return 2


if __name__ == "__main__":
    sys.exit(main())
