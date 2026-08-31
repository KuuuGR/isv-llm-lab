#!/usr/bin/env python3
"""Task 006.2 — verify all seven EXP-002 pilot runs are complete and intact.

Checks, per pilot run:
  - input package: meta.json, original.txt, prompt.txt, candidates.json exist;
  - input original sha256 matches input meta.json source sha256;
  - prompt sha256 matches input meta.json prompt sha256;
  - output package: meta.json, revised.txt exist;
  - revised sha256 matches output meta.json;
  - comparison: comparison.json + comparison.md + before/after evaluator dirs exist.

Read-only: never writes, never reconstructs anything.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXP002 = ROOT / "experiments" / "exp002-pilot"
INPUT = EXP002 / "input"
OUTPUTS = EXP002 / "outputs"
COMPARISON = EXP002 / "comparison"

EXPECTED_RUNS = [
    "exp002__2026-08-31__anthropic__claude__unknown",
    "exp002__2026-08-31__deepseek__deepseek__unknown",
    "exp002__2026-08-31__google__gemini__unknown",
    "exp002__2026-08-31__openai__chatgpt__unknown",
    "exp002__2026-08-31__openai__gpt-isvt__unknown",
    "exp002__2026-08-31__unknown__bielik__unknown",
    "exp002__2026-08-31__unknown__grok__unknown",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    problems: list[str] = []
    ok = 0
    for run_id in EXPECTED_RUNS:
        print(f"== {run_id}")
        p_in = INPUT / run_id
        p_out = OUTPUTS / run_id
        p_cmp = COMPARISON / run_id
        run_problems: list[str] = []

        # 1. input package
        for fname in ("meta.json", "original.txt", "prompt.txt", "candidates.json"):
            if not (p_in / fname).is_file():
                run_problems.append(f"input/{fname} missing")
        if not p_in.is_dir():
            problems += [f"{run_id}: input dir missing"]
            continue

        try:
            in_meta = json.loads((p_in / "meta.json").read_text(encoding="utf-8"))
        except Exception as exc:
            run_problems.append(f"input/meta.json unreadable: {exc}")
            in_meta = {}

        if (p_in / "original.txt").is_file():
            orig_sha = sha256(p_in / "original.txt")
            expected_orig = in_meta.get("source", {}).get("exp001_output_sha256")
            if expected_orig and orig_sha != expected_orig:
                run_problems.append(
                    f"original.txt sha mismatch: {orig_sha} != meta {expected_orig}")
        if (p_in / "prompt.txt").is_file():
            prompt_sha = sha256(p_in / "prompt.txt")
            expected_prompt = in_meta.get("prompt", {}).get("sha256")
            if expected_prompt and prompt_sha != expected_prompt:
                run_problems.append(
                    f"prompt.txt sha mismatch: {prompt_sha} != meta {expected_prompt}")

        # 2. output package
        for fname in ("meta.json", "revised.txt"):
            if not (p_out / fname).is_file():
                run_problems.append(f"outputs/{fname} missing")
        if (p_out / "meta.json").is_file() and (p_out / "revised.txt").is_file():
            try:
                out_meta = json.loads((p_out / "meta.json").read_text(encoding="utf-8"))
                rev_sha = sha256(p_out / "revised.txt")
                expected_rev = out_meta.get("revised", {}).get("sha256")
                if expected_rev and rev_sha != expected_rev:
                    run_problems.append(
                        f"revised.txt sha mismatch: {rev_sha} != meta {expected_rev}")
            except Exception as exc:
                run_problems.append(f"outputs/meta.json unreadable: {exc}")

        # 3. comparison
        for fname in ("comparison.json", "comparison.md"):
            if not (p_cmp / fname).is_file():
                run_problems.append(f"comparison/{fname} missing")
        for sub in ("before", "after"):
            for fname in ("report.json", "unresolved.json", "tokens.json"):
                if not (p_cmp / sub / fname).is_file():
                    run_problems.append(f"comparison/{sub}/{fname} missing")

        if run_problems:
            problems += [f"{run_id}: " + "; ".join(run_problems)]
        else:
            ok += 1
            print("  OK")

    print(f"\n{ok}/7 runs complete and intact.")
    if problems:
        print("PROBLEMS:")
        for p in problems:
            print(" -", p)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
