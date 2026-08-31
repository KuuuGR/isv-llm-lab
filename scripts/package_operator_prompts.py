#!/usr/bin/env python3
"""EXP-002 pilot — package operator-facing single-file prompts.

The input packages (experiments/exp002-pilot/input/<run>/) already contain a
complete self-contained revision prompt per run: prompt.txt holds the revision
instructions, the candidate table with provenance, and the COMPLETE original
translation. This script packages that prompt into one clearly named Markdown
file per condition so the Project Owner only has to copy/paste a single file.

For each EXP-001 condition it writes:

    experiments/exp002-pilot/operator-prompts/<NN>-<slug>.md
        # EXP-002 Pilot — <Display Name>
        > COPY THIS ENTIRE FILE INTO <LLM>.
        <complete prompt.txt content>

plus a deterministic manifest.json recording the generator, the commit, and
per-file SHA-256s.

Properties:

- Purely packaging: reads only the generated input packages; never changes
  candidate selection, candidate-generation rules, the selected 30 forms,
  EXP-001 outputs, metrics, the dictionary, or the evaluator.
- Deterministic: no timestamps; regenerating produces byte-identical files.
- The operator Markdown files embed the complete original EXP-001 translation
  (model output) and are therefore gitignored; only this script, the manifest
  and the README are committed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXP002 = ROOT / "experiments" / "exp002-pilot"
INPUT_DIR = EXP002 / "input"
OUTPUT_DIR = EXP002 / "operator-prompts"

# Canonical operator order, filename slug, LLM to paste into.
# Matches the seven EXP-001 conditions; source run ids recorded in meta.json.
CONDITIONS = [
    ("01", "chatgpt", "ChatGPT", "ChatGPT",
     "exp002__2026-08-31__openai__chatgpt__unknown"),
    ("02", "gpt-isv-teacher", "GPTs — ISV Teacher", "the GPTs "
     "'Interslavic — Medžuslovjansky Language Teacher' chat",
     "exp002__2026-08-31__openai__gpt-isvt__unknown"),
    ("03", "gemini", "Gemini", "Google Gemini",
     "exp002__2026-08-31__google__gemini__unknown"),
    ("04", "claude", "Claude", "Anthropic Claude",
     "exp002__2026-08-31__anthropic__claude__unknown"),
    ("05", "deepseek", "DeepSeek", "DeepSeek",
     "exp002__2026-08-31__deepseek__deepseek__unknown"),
    ("06", "bielik", "Bielik", "Bielik",
     "exp002__2026-08-31__unknown__bielik__unknown"),
    ("07", "grok", "Grok", "xAI Grok",
     "exp002__2026-08-31__unknown__grok__unknown"),
]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_commit() -> str:
    try:
        proc = subprocess.run(
            ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=10)
        return proc.stdout.strip() if proc.returncode == 0 else "unknown"
    except (OSError, subprocess.SubprocessError):
        return "unknown"


def render_operator_file(number: str, display: str, llm_name: str,
                         prompt_text: str) -> str:
    header = (
        f"# EXP-002 Pilot — {display}\n"
        "\n"
        f"> COPY THIS ENTIRE FILE INTO {llm_name}.\n"
        "> Do not modify anything. Save the model's complete reply\n"
        "> byte-for-byte and hand it to the collect step.\n"
        "\n"
        "---\n"
        "\n"
    )
    return header + prompt_text


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default=str(OUTPUT_DIR),
                        help="output directory (default: operator-prompts/)")
    args = parser.parse_args(argv)

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest = {
        "experiment_id": "exp002-pilot",
        "artifact": "operator-prompts",
        "generator": "scripts/package_operator_prompts.py",
        "generator_commit": git_commit(),
        "source": "experiments/exp002-pilot/input/<pilot_run_id>/prompt.txt "
                  "(complete revision prompt per run)",
        "note": "Deterministic packaging; no timestamps. The Markdown files "
                "embed the complete original EXP-001 translation (model "
                "output) and are gitignored; manifest + README are committed.",
        "files": {},
    }

    missing = []
    for number, slug, display, llm_name, pilot_run in CONDITIONS:
        prompt_path = INPUT_DIR / pilot_run / "prompt.txt"
        if not prompt_path.is_file():
            missing.append(pilot_run)
            print(f"[missing] {pilot_run}: {prompt_path.name}")
            continue
        prompt_text = prompt_path.read_text(encoding="utf-8")
        body = render_operator_file(number, display, llm_name, prompt_text)
        out_path = out_dir / f"{number}-{slug}.md"
        out_path.write_text(body, encoding="utf-8")
        manifest["files"][out_path.name] = {
            "pilot_run": pilot_run,
            "source_prompt_sha256": sha256_bytes(
                prompt_text.encode("utf-8")),
            "output_sha256": sha256_bytes(body.encode("utf-8")),
        }
        print(f"[write] {out_path.relative_to(ROOT)} ({len(body.encode())} B)")

    if missing:
        print(f"error: missing input packages for {len(missing)} run(s); "
              "run scripts/run_exp002_pilot.py prepare --all first",
              file=sys.stderr)
        return 2

    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[write] {out_dir.relative_to(ROOT)}/manifest.json")
    print(f"\n{len(CONDITIONS)} operator prompt(s) packaged. The Project "
          "Owner only needs to copy/paste one Markdown file per condition.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
