"""Experiment 001 — run ingestion: create an immutable run directory for a
raw model output and evaluate it with isv-eval.

The actual model requests are made OUTSIDE this script (by the Project Owner /
Architect / experiment operator) — this project has no LLM API clients by
design (D-007, Task 002 scope). This script takes the resulting raw output
text and turns it into a reproducible, evaluated run.

Usage:

    # 1. once: register the authoritative Polish source
    python3 scripts/run_exp001.py --ingest-source source_pl.txt

    # 2. per model output (one run per model condition)
    python3 scripts/run_exp001.py \
        --provider openai --model chatgpt --model-version gpt-4o-2024-08-06 \
        --output /path/to/raw/output.txt \
        [--notes "web UI, default system prompt"] \
        [--system-notes "could not remove the built-in system prompt"]

Run layout (per DESIGN.md §4):

    experiments/exp001-baseline/outputs/<YYYY-MM-DD>__<provider>__<model>__<model_version>/
        source.txt  prompt.txt  output.txt  meta.json
        report.json tokens.json unresolved.json   (produced by isv-eval)

Existing run directories are never overwritten: a `-2`, `-3`, … suffix is
appended for repeated conditions. `meta.json` records source/output SHA-256,
the evaluation code commit, the dictionary manifest and the morphology
version, so the run is reproducible.
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

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from isv_eval.morphology import (MORPHOLOGY_PACKAGE, morphology_version)
from isv_eval.cli import git_commit, load_manifest, sha256

PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXP = PROJECT_ROOT / "experiments" / "exp001-baseline"
INPUT_DIR = EXP / "input"
OUTPUTS_DIR = EXP / "outputs"
PROMPT_TEMPLATE = EXP / "prompt_template.txt"

EXPERIMENT_ID = "exp001"

# provider (task §3): exact names to avoid silent substitutions
PROVIDERS = ("openai", "google", "anthropic", "deepseek")


def run_id(date: str, provider: str, model: str, model_version: str) -> str:
    def clean(part: str) -> str:
        return re.sub(r"[^A-Za-z0-9._-]", "-", part)
    return f"{date}__{clean(provider)}__{clean(model)}__{clean(model_version)}"


def unique_run_dir(base_id: str) -> Path:
    candidate = OUTPUTS_DIR / base_id
    suffix = 2
    while candidate.exists():
        candidate = OUTPUTS_DIR / f"{base_id}-{suffix}"
        suffix += 1
    return candidate


def ingest_source(source_path: Path) -> None:
    """Register the authoritative Polish source (input/source.txt + meta)."""
    if not source_path.is_file():
        sys.exit(f"error: source file not found: {source_path}")
    raw = source_path.read_bytes()
    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    (INPUT_DIR / "source.txt").write_bytes(raw)
    meta = {
        "experiment_id": EXPERIMENT_ID,
        "filename": source_path.name,
        "sha256": hashlib.sha256(raw).hexdigest(),
        "size_bytes": len(raw),
        "ingested_at": datetime.now(timezone.utc).isoformat(),
        "title": None,          # fill in from Project Owner if known
        "author": None,
        "copyright_note": (
            "Project Owner owns the story and permits its use in this "
            "project; keep local, do not commit or redistribute."
        ),
    }
    (INPUT_DIR / "source.meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"source registered: {INPUT_DIR / 'source.txt'} ({meta['sha256']})")


def build_prompt() -> str:
    template = PROMPT_TEMPLATE.read_text(encoding="utf-8")
    source = (INPUT_DIR / "source.txt").read_text(encoding="utf-8")
    return template.replace("[FULL POLISH SOURCE TEXT]", source)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ingest-source", metavar="PATH",
                        help="register the authoritative Polish source and exit")
    parser.add_argument("--provider", choices=PROVIDERS,
                        help="provider (openai|google|anthropic|deepseek)")
    parser.add_argument("--model", help="model family label, e.g. chatgpt")
    parser.add_argument("--model-version",
                        help="exact model/version string given by the interface")
    parser.add_argument("--output", help="path to the RAW model output text file")
    parser.add_argument("--notes", default="",
                        help="free-form run notes (interface, parameters, …)")
    parser.add_argument("--system-notes", default="",
                        help="system-level instructions that could not be removed")
    args = parser.parse_args(argv)

    if args.ingest_source:
        ingest_source(Path(args.ingest_source))
        return 0

    missing = [flag for flag, value in (
        ("--provider", args.provider), ("--model", args.model),
        ("--model-version", args.model_version), ("--output", args.output),
    ) if not value]
    if missing:
        parser.error(f"missing required argument(s): {', '.join(missing)}")

    source_file = INPUT_DIR / "source.txt"
    if not source_file.is_file():
        sys.exit("error: no registered source; run --ingest-source first")
    source_sha = sha256(source_file)

    output_path = Path(args.output)
    if not output_path.is_file():
        sys.exit(f"error: output file not found: {output_path}")
    output_raw = output_path.read_bytes()
    output_sha = hashlib.sha256(output_raw).hexdigest()

    now = datetime.now(timezone.utc)
    date = now.strftime("%Y-%m-%d")
    run_dir = unique_run_dir(run_id(date, args.provider, args.model,
                                    args.model_version))
    run_dir.mkdir(parents=True, exist_ok=True)

    prompt = build_prompt()
    (run_dir / "prompt.txt").write_text(prompt, encoding="utf-8")
    (run_dir / "output.txt").write_bytes(output_raw)
    (run_dir / "source.txt").write_bytes(source_file.read_bytes())

    manifest = load_manifest() or {}
    meta = {
        "experiment_id": EXPERIMENT_ID,
        "date": date,
        "timestamp": now.isoformat(),
        "provider": args.provider,
        "model": args.model,
        "model_version": args.model_version,
        "prompt": str(run_dir / "prompt.txt"),
        "source_text": str(run_dir / "source.txt"),
        "output_text": str(run_dir / "output.txt"),
        "source_sha256": source_sha,
        "output_sha256": output_sha,
        "evaluation_code_commit": git_commit(),
        "dictionary_manifest": manifest,
        "morphology_package": MORPHOLOGY_PACKAGE,
        "morphology_version": morphology_version(),
        "parameters": {"temperature": None, "seed": None,
                       "notes": args.notes},
        "interface_notes": args.system_notes or None,
    }
    (run_dir / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    eval_cmd = [sys.executable, "-m", "isv_eval.cli",
                str(run_dir / "output.txt"), "--out", str(run_dir)]
    proc = subprocess.run(eval_cmd, cwd=PROJECT_ROOT)
    if proc.returncode != 0:
        sys.exit(f"error: isv-eval failed on {output_path.name}")

    print(f"run:    {run_dir.relative_to(PROJECT_ROOT)}")
    print(f"source: {source_sha}")
    print(f"output: {output_sha}")
    print("artifacts: report.json tokens.json unresolved.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
