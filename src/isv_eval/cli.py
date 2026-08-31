"""Command-line interface: ``isv-eval text.txt [options]``.

Reads an Interslavic text file, tokenizes, classifies every token (A/B/C),
computes coverage metrics, and writes three artifacts next to the input
(``--out DIR`` overrides):

- ``report.json``      summary metrics + provenance + denominator policy
- ``tokens.json``      every token with classification and context
- ``unresolved.json``  detailed bucket-C information for manual review
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

from . import __version__
from .classifier import classify
from .lexicon import Lexicon
from .metrics import compute_metrics
from .morphology import (MORPHOLOGY_PACKAGE, TRANSLIT_PACKAGE,
                         DEFAULT_BACKEND, MorphologyBackend,
                         morphology_version)
from .normalize import is_cyrillic
from .tokenizer import tokenize

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_LEXICON = PROJECT_ROOT / "data" / "dictionary" / "lexicon.tsv"
DEFAULT_MANIFEST = PROJECT_ROOT / "data" / "dictionary" / "manifest.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_commit() -> str:
    try:
        proc = subprocess.run(
            ["git", "-C", str(PROJECT_ROOT), "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=10,
        )
        return proc.stdout.strip() if proc.returncode == 0 else "unknown"
    except (OSError, subprocess.SubprocessError):
        return "unknown"


def load_manifest() -> dict | None:
    try:
        return json.loads(DEFAULT_MANIFEST.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def build_report(text_path: Path, out_dir: Path, metrics: dict,
                 lexicon: Lexicon, manifest: dict | None) -> dict:
    report = {
        "evaluator": {
            "name": "isv-eval",
            "version": __version__,
            "commit": git_commit(),
        },
        "input": {
            "path": str(text_path),
            "size": text_path.stat().st_size,
            "sha256": sha256(text_path),
        },
        "metrics": metrics,
        "classification_buckets": {"A": "exact lexical match",
                                   "B": "morphologically valid",
                                   "C": "unresolved"},
        "provenance": {
            "dictionary": manifest,
            "lexicon": {
                "path": str(DEFAULT_LEXICON),
                "entry_count": len(lexicon),
            },
            "morphology": {
                "package": MORPHOLOGY_PACKAGE,
                "version": morphology_version(),
                "translit_package": TRANSLIT_PACKAGE,
                "backend_script": str(DEFAULT_BACKEND),
            },
        },
        "output_files": {
            "report": str(out_dir / "report.json"),
            "tokens": str(out_dir / "tokens.json"),
            "unresolved": str(out_dir / "unresolved.json"),
        },
    }
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="isv-eval",
        description="Evaluate how much of an Interslavic text is justifiable "
                    "by existing lexical and morphological resources.",
    )
    parser.add_argument("text", help="path to the Interslavic text file")
    parser.add_argument("--out", default=None,
                        help="output directory (default: <text>.eval)")
    parser.add_argument("--lexicon", default=None,
                        help="lexicon TSV (default: data/dictionary/lexicon.tsv)")
    parser.add_argument("--backend", default=None,
                        help="path to the Node morphology backend script")
    parser.add_argument("--no-fallback", action="store_true",
                        help="disable the morphological fallback (bucket B)")
    args = parser.parse_args(argv)

    text_path = Path(args.text)
    if not text_path.is_file():
        print(f"error: input file not found: {text_path}", file=sys.stderr)
        return 2

    lexicon_path = Path(args.lexicon) if args.lexicon else DEFAULT_LEXICON
    if not lexicon_path.is_file():
        print(
            f"error: lexicon not found at {lexicon_path}\n"
            "Run `python scripts/generate_lexicon.py` to build it from the "
            "dictionary snapshot.",
            file=sys.stderr,
        )
        return 2

    out_dir = Path(args.out) if args.out else text_path.with_name(
        text_path.name + ".eval")
    out_dir.mkdir(parents=True, exist_ok=True)

    lexicon = Lexicon.load_tsv(lexicon_path)
    backend = MorphologyBackend(args.backend)
    tokens = classify(tokenize(text_path.read_text(encoding="utf-8")),
                      lexicon, backend, use_fallback=not args.no_fallback)
    metrics = compute_metrics(tokens)

    manifest = load_manifest()
    report = build_report(text_path, out_dir, metrics, lexicon, manifest)

    (out_dir / "report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "tokens.json").write_text(
        json.dumps([t.as_dict() for t in tokens], ensure_ascii=False, indent=2),
        encoding="utf-8")
    unresolved = [t.as_dict() for t in tokens if t.classification == "C"]
    (out_dir / "unresolved.json").write_text(
        json.dumps(unresolved, ensure_ascii=False, indent=2), encoding="utf-8")

    m = metrics
    print(f"input:      {text_path}")
    print(f"lexicon:    {lexicon_path} ({len(lexicon)} entries)")
    print(f"output:     {out_dir}/")
    print(f"lexical tokens: {m['total_tokens']}  "
          f"(all tokens: {m['tokens_total']}, non-lexical: {m['non_lexical_tokens']})")
    print(f"A exact dictionary matches:  {m['exact_dictionary_matches']}  "
          f"({_pct(m['exact_dictionary_coverage'])})")
    print(f"B morphologically valid:     {m['morphologically_valid_forms']}  "
          f"({_pct(_delta(m['morphologically_valid_coverage'], m['exact_dictionary_coverage']))})")
    print(f"C unresolved:                {m['unresolved_forms']}  "
          f"({_pct(m['unresolved_rate'])})")
    print(f"morphologically_valid_coverage: {_pct(m['morphologically_valid_coverage'])} "
          f"(= A+B over lexical tokens)")
    print(f"\nartifacts: report.json, tokens.json, unresolved.json")
    return 0


def _pct(value: float | None) -> str:
    return f"{value * 100:.2f}%" if value is not None else "n/a"


def _delta(total: float | None, part: float | None) -> float | None:
    if total is None or part is None:
        return None
    return total - part


if __name__ == "__main__":
    sys.exit(main())
