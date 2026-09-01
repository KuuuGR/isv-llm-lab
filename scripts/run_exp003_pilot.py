#!/usr/bin/env python3
"""EXP-003 — run orchestrator (prepare / collect / evaluate / status).

Reuses the EXP-002 execution pattern: the LLM is executed EXTERNALLY (the
project has no LLM API client, D-007); this script only prepares runs,
registers externally produced outputs byte-for-byte, evaluates them with the
Task 008 evaluator, and reports status.

Commands:

    prepare  --date YYYY-MM-DD
             write outputs/plan.json — the 12 planned (model x condition)
             runs with run ids, prompt/source/scaffold hashes and model
             metadata, derived from the packaged operator prompts. This is
             the reproducible "preparing a run" step; it never calls an LLM.
    collect  --run <run_id> --output <path>
             register an externally generated raw output. The file is copied
             byte-for-byte, never modified, never overwritten; meta.json
             records prompt hash, source hash, condition, model, provider,
             model version, generation date, evaluator commit, resource
             versions, and the SHA-256 of the collected file.
    evaluate --run <run_id> [--all]
             run the Task 008 evaluator (isv-eval, unmodified) on a collected
             output and write outputs/<run_id>/evaluation.json + .md.
    status
             show which planned runs have collected outputs / evaluations.

Run id: <date>__<provider>__<model>__<model_version>__<condition> (lowercase
condition), per the EXP-003 design §19. Failures are preserved: a collected
file is stored regardless of content, and its meta.json records status.

No LLM call anywhere. No fabricated outputs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from isv_eval.cli import git_commit  # noqa: E402

EXP = ROOT / "experiments" / "exp003-scaffold"
OPERATOR_PROMPTS = EXP / "operator-prompts"
OUTPUTS_DIR = EXP / "outputs"
SCAFFOLD_DIR = EXP / "scaffolds" / "op-pl"
CURATION_DIR = EXP / "curation" / "op-pl"
DEFAULT_MANIFEST = ROOT / "data" / "dictionary" / "manifest.json"
DEFAULT_LEXICON = ROOT / "data" / "dictionary" / "lexicon.tsv"

MODELS = {
    "chatgpt": {"provider": "openai", "model": "chatgpt", "version": "unknown"},
    "claude": {"provider": "anthropic", "model": "claude", "version": "unknown"},
    "bielik": {"provider": "unknown", "model": "bielik", "version": "unknown"},
}
CONDITIONS = ("A", "B", "C", "D")

# Mapping run-id components back to a model+condition (order matters: the run
# id is <date>__<provider>__<model>__<version>__<condition>; model is the 3rd
# component, condition the 5th).
RUN_ID_FIELDS = ("date", "provider", "model", "model_version", "condition")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def run_id_for(date: str, model: str, condition: str) -> str:
    meta = MODELS[model]
    return (f"{date}__{meta['provider']}__{meta['model']}__"
            f"{meta['version']}__{condition.lower()}")


def parse_run_id(run_id: str) -> dict:
    parts = run_id.split("__")
    if len(parts) != 5:
        raise ValueError(
            f"run id must be <date>__<provider>__<model>__<model_version>__"
            f"<condition>, got: {run_id!r}")
    return dict(zip(RUN_ID_FIELDS, parts))


def prompt_file_for(model: str, condition: str) -> Path | None:
    number = CONDITIONS.index(condition) + 1 + len(CONDITIONS) * (
        list(MODELS).index(model))
    path = OPERATOR_PROMPTS / f"{number:02d}-{model}-{condition}.md"
    return path if path.is_file() else None


def load_plan() -> dict:
    plan = OUTPUTS_DIR / "plan.json"
    if not plan.is_file():
        return {}
    return json.loads(plan.read_text(encoding="utf-8"))


def resource_versions() -> dict:
    """Deterministic resource pins recorded in every collected run's meta."""
    versions: dict = {
        "evaluator_commit": git_commit(),
        "dictionary_manifest": (json.loads(
            DEFAULT_MANIFEST.read_text(encoding="utf-8"))
            if DEFAULT_MANIFEST.is_file() else None),
        "dictionary_lexicon": {
            "path": str(DEFAULT_LEXICON),
            "bytes": DEFAULT_LEXICON.stat().st_size if DEFAULT_LEXICON.is_file() else 0,
            "sha256": sha256_file(DEFAULT_LEXICON) if DEFAULT_LEXICON.is_file() else None,
        },
        "scaffold_generator": {
            "script": "scripts/build_exp003_scaffold.py",
            "commit": git_commit(),
        },
    }
    curation = {}
    for name in ("names.tsv", "multiword.tsv", "residual.tsv"):
        path = CURATION_DIR / name
        if path.is_file():
            curation[name] = sha256_file(path)
    versions["curation"] = curation
    return versions


def run_prepare(date: str, force: bool = False) -> int:
    if not date:
        print("error: --date YYYY-MM-DD is required (run ids carry the "
              "planned generation date)", file=sys.stderr)
        return 2
    plan = OUTPUTS_DIR / "plan.json"
    if plan.is_file() and not force:
        print(f"error: {plan} already exists; use --force to rewrite "
              "(changing the plan invalidates collected runs)", file=sys.stderr)
        return 2

    runs = []
    for model in MODELS:
        for condition in CONDITIONS:
            pf = prompt_file_for(model, condition)
            if pf is None:
                print(f"error: operator prompt missing for {model} {condition}; "
                      "run scripts/package_exp003_prompts.py first",
                      file=sys.stderr)
                return 2
            prompt_text = pf.read_text(encoding="utf-8")
            source_sha = sha256_file(EXP / "input" / "source.txt")
            scaffold_sha = None
            if condition in ("B", "C", "D"):
                scaffold_sha = sha256_file(
                    SCAFFOLD_DIR / f"scaffold_{condition}.txt")
            runs.append({
                "run_id": run_id_for(date, model, condition),
                "model": model,
                "provider": MODELS[model]["provider"],
                "model_version": MODELS[model]["version"],
                "condition": condition,
                "prompt_file": str(pf.relative_to(ROOT)),
                "prompt_sha256": sha256_bytes(prompt_text.encode("utf-8")),
                "source_sha256": source_sha,
                "scaffold_sha256": scaffold_sha,
            })

    plan_payload = {
        "experiment_id": "exp003",
        "artifact": "run-plan",
        "date": date,
        "generator": "scripts/run_exp003_pilot.py prepare",
        "generator_commit": git_commit(),
        "note": "Planned (model x condition) runs. LLM execution is external; "
                "this plan never calls an LLM.",
        "runs": runs,
    }
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    plan.write_text(json.dumps(plan_payload, ensure_ascii=False, indent=2),
                    encoding="utf-8")
    print(f"[prepare] {plan.relative_to(ROOT)}")
    for r in runs:
        print(f"  {r['run_id']:58s} prompt {r['prompt_sha256'][:12]}")
    print(f"{len(runs)} planned run(s).")
    return 0


def run_collect(run_id: str, output: Path, generation_date: str,
                model: str, provider: str, model_version: str) -> int:
    try:
        parts = parse_run_id(run_id)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    condition = parts["condition"].upper()
    if condition not in CONDITIONS:
        print(f"error: unknown condition {parts['condition']!r}", file=sys.stderr)
        return 2
    plan = load_plan()
    plan_entry = next(
        (r for r in plan.get("runs", [])
         if r["model"] == parts["model"]
         and r["condition"].lower() == condition.lower()),
        None)
    if plan_entry is None:
        print("error: run not in the plan; run "
              "`scripts/run_exp003_pilot.py prepare --date <date>` first",
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

    meta = {
        "run_id": run_id,
        "experiment_id": "exp003",
        "condition": condition,
        "model": model if model != "unknown" else parts["model"],
        "provider": provider if provider != "unknown" else parts["provider"],
        "model_version": (model_version if model_version != "unknown"
                          else parts["model_version"]),
        "generation_date": generation_date if generation_date != "unknown"
                           else parts["date"],
        "status": "collected_external_output",
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "collected_by": "scripts/run_exp003_pilot.py collect",
        "prompt": {
            "file": plan_entry["prompt_file"],
            "sha256": plan_entry["prompt_sha256"],
        },
        "source": {"sha256": plan_entry["source_sha256"]},
        "scaffold": {"sha256": plan_entry["scaffold_sha256"]},
        "output": {
            "file": str(dst),
            "sha256": sha256_bytes(data),
            "bytes": len(data),
        },
        "resources": resource_versions(),
        "note": "Raw LLM output stored byte-for-byte; never modified. "
                "Empty or failed runs are preserved and documented, not "
                "deleted.",
    }
    (out_dir / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[collect] {run_id}")
    print(f"  output sha256: {meta['output']['sha256']}")
    print(f"  prompt sha256: {meta['prompt']['sha256']}")
    print(f"  condition/model/provider/version/date: "
          f"{condition}/{meta['model']}/{meta['provider']}/"
          f"{meta['model_version']}/{meta['generation_date']}")
    return 0


def run_evaluate(run_id: str) -> int:
    out_dir = OUTPUTS_DIR / run_id
    text = out_dir / "output.txt"
    if not text.is_file():
        print(f"error: no output.txt for {run_id}; collect it first",
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
    report = json.loads((eval_dir / "report.json").read_text(encoding="utf-8"))
    meta = json.loads((out_dir / "meta.json").read_text(encoding="utf-8"))
    m = report["metrics"]
    summary = {
        "run_id": run_id,
        "evaluator": report["evaluator"],
        "condition": meta["condition"],
        "metrics": m,
        "output_files": report["output_files"],
    }
    (out_dir / "evaluation.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = [
        f"# EXP-003 — evaluation — {run_id}",
        "",
        f"condition {meta['condition']} · model {meta['model']} "
        f"({meta['provider']}, version {meta['model_version']}) · "
        f"generated {meta['generation_date']}",
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
        "No linguistic quality score is assigned; coverage is evidence, not "
        "correctness.",
        "",
    ]
    (out_dir / "evaluation.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"[evaluate] {run_id}")
    print(f"  canonical coverage: {_pct(m['canonical_coverage'])}  "
          f"broader: {_pct(m['broader_resource_supported_coverage'])}  "
          f"unresolved: {_pct(m['unresolved_rate'])}")
    return 0


def _pct(v: float | None) -> str:
    return f"{v * 100:.2f}%" if v is not None else "n/a"


def run_status() -> int:
    plan = load_plan()
    rows = []
    for r in plan.get("runs", []):
        rid = r["run_id"]
        out = OUTPUTS_DIR / rid
        has_output = (out / "output.txt").is_file()
        has_meta = (out / "meta.json").is_file()
        has_eval = (out / "evaluation.json").is_file()
        rows.append((rid, r["model"], r["condition"], has_output, has_eval))
    if not rows:
        print("no plan; run `scripts/run_exp003_pilot.py prepare "
              "--date YYYY-MM-DD` first")
        return 0
    print(f"{'run_id':<58} {'model':<9} {'cond':<5} {'output':<7} {'eval':<5}")
    for rid, model, condition, has_output, has_eval in rows:
        print(f"{rid:<58} {model:<9} {condition:<5} "
              f"{'yes' if has_output else 'no':<7} {'yes' if has_eval else 'no':<5}")
    print(f"\n{len(rows)} planned run(s); "
          f"{sum(1 for r in rows if r[3])} with collected output(s); "
          f"{sum(1 for r in rows if r[4])} evaluated.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p_prep = sub.add_parser("prepare", help="write the run plan")
    p_prep.add_argument("--date", required=True, help="YYYY-MM-DD")
    p_prep.add_argument("--force", action="store_true")

    p_col = sub.add_parser("collect", help="register an external raw output")
    p_col.add_argument("--run", required=True, dest="run_id")
    p_col.add_argument("--output", required=True, type=Path)
    p_col.add_argument("--generation-date", default="unknown")
    p_col.add_argument("--model", default="unknown")
    p_col.add_argument("--provider", default="unknown")
    p_col.add_argument("--model-version", default="unknown")

    p_ev = sub.add_parser("evaluate", help="evaluate a collected output")
    p_ev.add_argument("--run", required=True, dest="run_id")

    sub.add_parser("status", help="show run progress")
    args = parser.parse_args(argv)

    if args.command == "prepare":
        return run_prepare(args.date, args.force)
    if args.command == "collect":
        return run_collect(args.run_id, args.output, args.generation_date,
                           args.model, args.provider, args.model_version)
    if args.command == "evaluate":
        return run_evaluate(args.run_id)
    if args.command == "status":
        return run_status()
    return 2


if __name__ == "__main__":
    sys.exit(main())
