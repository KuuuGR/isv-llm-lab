#!/usr/bin/env python3
"""EXP-003 — verify run completeness and raw-output integrity.

Checks every planned (or specified) run:

- the operator prompt file exists and its SHA-256 matches the plan;
- a collected output exists and its SHA-256 matches the recorded meta.json
  (byte-for-byte integrity: the raw output has not changed since collect);
- meta.json is present and self-consistent (condition, model, provider,
  model version, generation date, prompt/source/scaffold hashes, resource
  pins);
- evaluation.json is present when the run was evaluated;
- failed runs (e.g. empty or truncated outputs) are present and documented in
  meta.json, never silently deleted.

Exit code 0 when everything passes; 1 with a per-run report otherwise.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXP = ROOT / "experiments" / "exp003-scaffold"
OUTPUTS_DIR = EXP / "outputs"
OPERATOR_PROMPTS = EXP / "operator-prompts"

CONDITIONS = ("A", "B", "C", "D")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_plan() -> dict:
    plan = OUTPUTS_DIR / "plan.json"
    if not plan.is_file():
        return {}
    return json.loads(plan.read_text(encoding="utf-8"))


def verify_run(run_id: str, plan_entry: dict) -> list[str]:
    errors: list[str] = []
    out_dir = OUTPUTS_DIR / run_id
    meta_path = out_dir / "meta.json"
    output_path = out_dir / "output.txt"

    meta = None
    if meta_path.is_file():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
    else:
        errors.append("meta.json missing")

    # plan consistency
    if plan_entry is not None:
        if meta is None:
            errors.append("cannot check plan consistency: meta.json missing")
        else:
            if meta.get("condition") != plan_entry["condition"]:
                errors.append(f"condition mismatch: meta={meta.get('condition')} "
                              f"plan={plan_entry['condition']}")
            if meta["prompt"].get("sha256") != plan_entry["prompt_sha256"]:
                errors.append("prompt hash differs from plan")
            if meta["source"].get("sha256") != plan_entry["source_sha256"]:
                errors.append("source hash differs from plan")
            if meta["scaffold"].get("sha256") != plan_entry.get("scaffold_sha256"):
                errors.append("scaffold hash differs from plan")

    # raw output integrity (byte-for-byte)
    if not output_path.is_file():
        errors.append("output.txt missing")
    elif meta is None:
        errors.append("cannot check output sha256: meta.json missing")
    else:
        recorded = meta.get("output", {}).get("sha256")
        actual = sha256_bytes(output_path.read_bytes())
        if recorded is None:
            errors.append("meta.json has no output sha256")
        elif recorded != actual:
            errors.append(f"output sha256 mismatch: meta={recorded} "
                          f"actual={actual}")

    # required metadata fields present
    if meta is not None:
        for field in ("condition", "model", "provider", "model_version",
                      "generation_date", "status", "prompt", "source",
                      "resources"):
            if field not in meta:
                errors.append(f"meta.json missing field: {field}")

        # prompt file still matches its hash
        pf = OPERATOR_PROMPTS / Path(meta.get("prompt", {}).get("file", "")).name
        if not pf.is_file():
            errors.append(f"prompt file missing: {pf}")
        elif sha256_bytes(pf.read_bytes()) != meta.get("prompt", {}).get("sha256"):
            errors.append("prompt file content no longer matches recorded hash")

        # evaluation, if expected
        if (out_dir / "evaluation.json").is_file():
            ev = json.loads((out_dir / "evaluation.json").read_text(
                encoding="utf-8"))
            if ev.get("condition") != meta.get("condition"):
                errors.append("evaluation condition mismatch")

        # failed runs must be preserved and documented
        if output_path.is_file() and output_path.stat().st_size == 0:
            if meta.get("status") == "collected_external_output":
                errors.append("empty output collected but status not marked "
                              "as a documented failure")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", default=None,
                        help="single run id; default: all planned runs")
    parser.add_argument("--no-plan", action="store_true",
                        help="verify collected run directories only "
                             "(skip plan-consistency checks)")
    args = parser.parse_args(argv)

    plan = load_plan()
    runs: list[tuple[str, dict | None]] = []
    if args.run:
        runs.append((args.run, next(
            (r for r in plan.get("runs", []) if r["run_id"] == args.run), None)))
    else:
        if plan.get("runs"):
            runs = [(r["run_id"], r) for r in plan["runs"]]
        else:
            runs = [(p.name, None) for p in OUTPUTS_DIR.iterdir()
                    if p.is_dir() and (p / "output.txt").is_file()]
    if not runs:
        print("nothing to verify; prepare a plan or collect runs first",
              file=sys.stderr)
        return 2

    failures = 0
    for run_id, plan_entry in runs:
        errors = verify_run(run_id, None if args.no_plan else plan_entry)
        status = "OK" if not errors else "FAIL"
        if errors:
            failures += 1
        print(f"[{status}] {run_id}")
        for err in errors:
            print(f"    - {err}")

    print(f"\n{len(runs)} run(s) checked; {failures} with problems.")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
