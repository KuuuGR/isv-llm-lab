#!/usr/bin/env python3
"""EXP-002 pilot — reproducible run orchestrator.

Wraps the three deterministic stages of the pilot around the EXP-001 outputs
and the Task-005 cross-resource audit:

    prepare   →  scripts/prepare_exp002_pilot.py  (input packages)
    collect   →  register an externally produced revised.txt + run metadata
    compare   →  scripts/compare_exp002.py        (before/after evaluation)
    status    →  show which pilot runs have inputs / revisions / comparisons

The LLM is executed EXTERNALLY (the project has no LLM API client, D-007).
`collect` therefore never fabricates a revision: it copies the operator's
revised.txt byte-for-byte, records the run metadata (model/provider/version/
generation date default to `unknown`), refuses to overwrite an existing
revision, and verifies the SHA-256 of the copied file.

Example (single model):

    python scripts/run_exp002_pilot.py prepare --source-run 2026-08-31__openai__chatgpt__unknown
    python scripts/run_exp002_pilot.py collect \\
        --pilot-run exp002__2026-08-31__openai__chatgpt__unknown \\
        --revised /path/to/llm_reply.txt --model chatgpt --provider openai
    python scripts/run_exp002_pilot.py compare

Example (all seven source runs):

    python scripts/run_exp002_pilot.py prepare --all
    python scripts/run_exp002_pilot.py status
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

EXP002 = ROOT / "experiments" / "exp002-pilot"
INPUT_DIR = EXP002 / "input"
OUTPUTS_DIR = EXP002 / "outputs"
COMPARISON_DIR = EXP002 / "comparison"
OUTPUTS001 = ROOT / "experiments" / "exp001-baseline" / "outputs"

PREPARE = ROOT / "scripts" / "prepare_exp002_pilot.py"
COMPARE = ROOT / "scripts" / "compare_exp002.py"

METADATA_FIELDS = ("model", "model_version", "provider", "generation_date")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_runs() -> list[str]:
    return sorted(p.name for p in OUTPUTS001.iterdir() if p.is_dir()
                  and not p.name.startswith(("comparison", ".")))


def pilot_input_dirs() -> list[Path]:
    if not INPUT_DIR.is_dir():
        return []
    return sorted(p for p in INPUT_DIR.iterdir() if p.is_dir())


def existing_pilot_ids() -> list[str]:
    return [p.name for p in pilot_input_dirs()]


def run_prepare(all_: bool, source_run: str | None) -> int:
    if all_:
        ids = source_runs()
    elif source_run:
        ids = [source_run]
    else:
        print("error: --all or --source-run required", file=sys.stderr)
        return 2
    existing = existing_pilot_ids()
    rc = 0
    for run_id in ids:
        pilot_id = f"exp002__{run_id}"
        if pilot_id in existing:
            print(f"[skip] {pilot_id}: input package already exists")
            continue
        proc = subprocess.run([sys.executable, str(PREPARE), "--source-run", run_id],
                              cwd=ROOT)
        rc |= proc.returncode
    return rc


def run_collect(pilot_run: str, revised: Path,
                model: str, provider: str, version: str,
                generation_date: str) -> int:
    out_dir = OUTPUTS_DIR / pilot_run
    revised_dst = out_dir / "revised.txt"
    if revised_dst.exists():
        print(f"error: {revised_dst} already exists; refusing to overwrite "
              "(never overwrite an existing run)", file=sys.stderr)
        return 2
    if not Path(revised).is_file():
        print(f"error: revised file not found: {revised}", file=sys.stderr)
        return 2
    if Path(revised).read_bytes().strip() == b"":
        print("error: revised file is empty", file=sys.stderr)
        return 2

    out_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(revised, revised_dst)  # byte-for-byte, never modified

    # Revision metadata lives next to the raw output; the input package meta.json
    # stays immutable (it documents the prepared condition, not the execution).
    out_meta = {
        "pilot_run_id": pilot_run,
        "experiment_id": "exp002-pilot",
        "source": {
            "exp001_run_id": pilot_run.removeprefix("exp002__"),
            "exp001_output_sha256": json.loads(
                (INPUT_DIR / pilot_run / "meta.json").read_text(
                    encoding="utf-8"))["source"]["exp001_output_sha256"],
        },
        "revision": {
            "model": model, "model_version": version, "provider": provider,
            "generation_date": generation_date,
            "status": "collected_external_output",
            "collected_at": datetime.now(timezone.utc).isoformat(),
            "collected_by": "scripts/run_exp002_pilot.py collect",
        },
        "revised": {
            "file": str(revised_dst),
            "sha256": _sha256(revised_dst),
            "bytes": revised_dst.stat().st_size,
        },
        "note": "Raw LLM output stored byte-for-byte; never modified.",
    }
    (out_dir / "meta.json").write_text(
        json.dumps(out_meta, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[collect] {pilot_run}")
    print(f"  revised sha256: {out_meta['revised']['sha256']}")
    print(f"  revision model/provider/version/date: "
          f"{model}/{provider}/{version}/{generation_date}")
    print("  Raw output stored byte-for-byte; not modified.")
    return 0


def run_compare(pilot_run: str | None) -> int:
    cmd = [sys.executable, str(COMPARE)]
    if pilot_run:
        cmd += ["--pilot-run", pilot_run]
    return subprocess.run(cmd, cwd=ROOT).returncode


def run_status() -> int:
    rows = []
    for pilot_id in existing_pilot_ids():
        src = pilot_id.removeprefix("exp002__")
        has_input = True
        has_revision = (OUTPUTS_DIR / pilot_id / "revised.txt").is_file()
        has_comparison = (COMPARISON_DIR / pilot_id / "comparison.json").is_file()
        out_meta_path = OUTPUTS_DIR / pilot_id / "meta.json"
        model = "unknown"
        if out_meta_path.is_file():
            model = json.loads(out_meta_path.read_text(encoding="utf-8"))\
                .get("revision", {}).get("model", "unknown")
        rows.append((pilot_id, src, has_revision, has_comparison, model))
    print(f"{'pilot run':<44} {'source run':<38} {'revised':<8} {'compared':<9} model")
    for pilot_id, src, has_revision, has_comparison, model in rows:
        print(f"{pilot_id:<44} {src:<38} "
              f"{'yes' if has_revision else 'no':<8} "
              f"{'yes' if has_comparison else 'no':<9} {model}")
    print(f"\n{len(rows)} input package(s); "
          f"{sum(1 for r in rows if r[2])} with revised output(s).")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p_prep = sub.add_parser("prepare", help="build input packages")
    p_prep.add_argument("--source-run", default=None)
    p_prep.add_argument("--all", action="store_true",
                        help="prepare for every EXP-001 source run")

    p_col = sub.add_parser("collect", help="register an external revised output")
    p_col.add_argument("--pilot-run", required=True)
    p_col.add_argument("--revised", required=True,
                       help="path to the raw LLM reply (copied byte-for-byte)")
    for field in METADATA_FIELDS:
        p_col.add_argument(f"--{field}", default="unknown")
    p_col.set_defaults(provider="unknown", model_version="unknown",
                       generation_date="unknown")

    p_cmp = sub.add_parser("compare", help="run before/after evaluation")
    p_cmp.add_argument("--pilot-run", default=None)

    p_st = sub.add_parser("status", help="show pilot progress")
    args = parser.parse_args(argv)

    if args.command == "prepare":
        return run_prepare(args.all, args.source_run)
    if args.command == "collect":
        return run_collect(args.pilot_run, Path(args.revised),
                           args.model, args.provider, args.model_version,
                           args.generation_date)
    if args.command == "compare":
        return run_compare(args.pilot_run)
    if args.command == "status":
        return run_status()
    return 2


if __name__ == "__main__":
    sys.exit(main())
