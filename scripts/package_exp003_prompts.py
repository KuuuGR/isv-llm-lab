#!/usr/bin/env python3
"""EXP-003 — package self-contained operator prompts (4 conditions x 3 models).

Writes experiments/exp003-scaffold/operator-prompts/<NN>-<model>-<COND>.md
from the committed prompt template (prompt_template.txt) + the cleaned story
source + the rendered scaffold blocks (scaffold_B/C/D.txt). One file per
(model, condition): the Project Owner copies the whole file into the target
model and pastes the reply back byte-for-byte.

Conditions:
    A  direct baseline (no scaffold block)
    B  generation-time lexical scaffold
    C  scaffold + alternatives
    D  scaffold + alternatives + grammatical annotations

Guarantees (design SS8/SS13):

- Deterministic: no timestamps; regenerating produces byte-identical files.
- Attribution discipline: the four prompts for one model are byte-identical
  except the condition block (the scaffold block). The scaffold intro for
  B/C/D is the same text; C/D add one sentence each about alternatives /
  grammar, and the embedded block differs (scaffold_C.txt / scaffold_D.txt).
- Purely packaging: reads only the prepared source + scaffolds; never changes
  alignment, candidates, curation, the dictionary, or the evaluator.
- The .md files embed the copyrighted story and are gitignored; only
  README.md + manifest.json are committed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXP = ROOT / "experiments" / "exp003-scaffold"
INPUT_DIR = EXP / "input"
SCAFFOLD_DIR = EXP / "scaffolds" / "op-pl"
OUTPUT_DIR = EXP / "operator-prompts"

EXPERIMENT_ID = "EXP-003"

# Filename order, display name, provider, model name, model version.
# Provider/version are 'unknown' where not confirmed (task: never invent
# metadata). Bielik is 'unknown' provider per EXP-001/EXP-002 conventions.
MODELS = [
    ("chatgpt", "ChatGPT", "openai", "chatgpt", "unknown"),
    ("claude", "Claude", "anthropic", "claude", "unknown"),
    ("bielik", "Bielik", "unknown", "bielik", "unknown"),
]

# Condition order: (label, name, scaffold file). A has no scaffold block.
CONDITIONS = [
    ("A", "A — direct baseline (no scaffold)", None),
    ("B", "B — lexical scaffold", "scaffold_B.txt"),
    ("C", "C — lexical scaffold + alternatives", "scaffold_C.txt"),
    ("D", "D — lexical scaffold + alternatives + grammar", "scaffold_D.txt"),
]

_SCAFFOLD_INTRO_COMMON = (
    "## Lexical scaffold (dictionary guidance)\n"
    "\n"
    "Below is a word-by-word lexical scaffold of the story: each Polish\n"
    "surface form is paired with suggested Interslavic headwords from a\n"
    "canonical dictionary.\n"
    "\n"
    "The scaffold is **lexical guidance, not a finished translation**. You\n"
    "are still responsible for producing natural Interslavic:\n"
    "\n"
    "- You may change word order freely and choose any grammatical\n"
    "  construction.\n"
    "- Inflect the supplied candidates (case, number, gender, tense, person,\n"
    "  aspect) as the context requires.\n"
    "- `[?]` marks a Polish form for which no reliable mapping was found —\n"
    "  use your best judgment there.\n"
    "- Proper names are marked \u201c(proper name \u2014 keep as-is)\u201d; keep them\n"
    "  unchanged.\n"
    "- Do not copy the scaffold mechanically. Where no supplied candidate\n"
    "  fits the context, use natural Interslavic vocabulary.\n"
)

_SCAFFOLD_INTRO_ALTERNATIVES = (
    "- Where several alternatives are listed, choose the one that best fits\n"
    "  the context; all listed alternatives are supported by the project's\n"
    "  resources.\n"
)

_SCAFFOLD_INTRO_GRAMMAR = (
    "- Parenthesised annotations give the part of speech, verb aspect, and \u2014\n"
    "  where the resources generate them \u2014 a few example forms. They are\n"
    "  hints, not mandates: you remain responsible for the final surface\n"
    "  forms and agreement.\n"
)


def scaffold_block(condition: str) -> str:
    """The condition content: intro + rendered scaffold (B/C/D)."""
    label, _name, scaffold_file = next(
        c for c in CONDITIONS if c[0] == condition)
    if label == "A":
        return ""
    lines = [_SCAFFOLD_INTRO_COMMON]
    if label in ("C", "D"):
        lines.append(_SCAFFOLD_INTRO_ALTERNATIVES)
    if label == "D":
        lines.append(_SCAFFOLD_INTRO_GRAMMAR)
    body = (SCAFFOLD_DIR / scaffold_file).read_text(encoding="utf-8")
    return "".join(lines) + "\n" + body + "\n"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _display(path: Path, root: Path) -> str:
    """Path shown relative to the repo root when possible (absolute in tmp)."""
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def git_commit() -> str:
    try:
        proc = subprocess.run(
            ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=10)
        return proc.stdout.strip() if proc.returncode == 0 else "unknown"
    except (OSError, subprocess.SubprocessError):
        return "unknown"


def render_prompt(model_slug: str, model_name: str, condition: str) -> str:
    template = (EXP / "prompt_template.txt").read_text(encoding="utf-8")
    label, cond_name, _ = next(c for c in CONDITIONS if c[0] == condition)
    story = (INPUT_DIR / "source.txt").read_text(encoding="utf-8").rstrip("\n")
    block = scaffold_block(condition)
    if block:
        block = block.rstrip("\n") + "\n\n"
    return template.format(
        EXPERIMENT_ID=EXPERIMENT_ID,
        CONDITION_NAME=cond_name,
        CONDITION_LABEL=label,
        MODEL_NAME=model_name,
        STORY=story,
        SCAFFOLD_BLOCK=block,
    )


def render_operator_file(model_name: str, condition: str,
                         prompt_text: str) -> str:
    header = (
        f"# EXP-003 \u2014 Condition {condition} \u2014 {model_name}\n"
        "\n"
        f"> COPY THIS ENTIRE FILE INTO {model_name}.\n"
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

    for required in (EXP / "prompt_template.txt", INPUT_DIR / "source.txt"):
        if not required.is_file():
            print(f"error: missing {required}; run the scaffold prep first",
                  file=sys.stderr)
            return 2
    for _label, _name, scaffold_file in CONDITIONS:
        if scaffold_file and not (SCAFFOLD_DIR / scaffold_file).is_file():
            print(f"error: missing {SCAFFOLD_DIR / scaffold_file}; "
                  "build the scaffold first", file=sys.stderr)
            return 2

    source_sha = sha256_bytes(
        (INPUT_DIR / "source.txt").read_bytes())
    scaffold_sha = {
        label: sha256_bytes((SCAFFOLD_DIR / file).read_bytes())
        for label, _name, file in CONDITIONS if file
    }

    manifest = {
        "experiment_id": "exp003",
        "artifact": "operator-prompts",
        "generator": "scripts/package_exp003_prompts.py",
        "generator_commit": git_commit(),
        "template": "experiments/exp003-scaffold/prompt_template.txt",
        "source": {
            "file": "experiments/exp003-scaffold/input/source.txt",
            "sha256": source_sha,
        },
        "scaffold_blocks": scaffold_sha,
        "note": "Deterministic packaging; no timestamps. The Markdown files "
                "embed the copyrighted story and are gitignored; README + "
                "manifest are committed. Prompts for one model differ only "
                "in the condition block.",
        "files": {},
    }

    number = 0
    for model_slug, model_name, provider, model, version in MODELS:
        for label, _cond_name, _file in CONDITIONS:
            number += 1
            prompt_text = render_prompt(model_slug, model_name, label)
            body = render_operator_file(model_name, label, prompt_text)
            out_path = out_dir / f"{number:02d}-{model_slug}-{label}.md"
            out_path.write_text(body, encoding="utf-8")
            manifest["files"][out_path.name] = {
                "model": model_slug,
                "provider": provider,
                "model_version": version,
                "condition": label,
                "prompt_text_sha256": sha256_bytes(
                    prompt_text.encode("utf-8")),
                "output_sha256": sha256_bytes(body.encode("utf-8")),
            }
            print(f"[write] {_display(out_path, ROOT)} "
                  f"({len(body.encode())} B)")

    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[write] {_display(out_dir / 'manifest.json', ROOT)}")
    print(f"\n{len(MODELS) * len(CONDITIONS)} operator prompt(s) packaged. "
          "The Project Owner only needs to copy/paste one Markdown file per "
          "(model, condition).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
