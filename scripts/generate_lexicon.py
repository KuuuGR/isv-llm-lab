"""Generate the full-form lexicon from the dictionary snapshot + morphology.

Usage:
    python scripts/generate_lexicon.py [--dict data/dictionary/basic.json]
        [--out data/dictionary/lexicon.tsv] [--chunk 500]

For every dictionary row, the morphology backend (``@interslavic/morphology``)
expands the lemma into its full paradigm; comma-separated variant lemmas
(``den, denj``) are expanded separately and dictionary annotations such as
``(+2)`` are filtered out (see the backend docstring). The output TSV contains:

- ``headword`` entries for every dictionary lemma, and
- ``paradigm`` entries for every generated inflected form.

The lexicon is a generated artifact derived from the dictionary snapshot,
whose license is UNRESOLVED: the file stays local, out of git.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from isv_eval.morphology import (DEFAULT_BACKEND, MorphologyBackend,
                                 morphology_version)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DICT = PROJECT_ROOT / "data" / "dictionary" / "basic.json"
DEFAULT_OUT = PROJECT_ROOT / "data" / "dictionary" / "lexicon.tsv"

ANNOTATION_RE = r"\s*\([^)]*\)"


def clean_lemma(form: str) -> str:
    return re.sub(ANNOTATION_RE, "", form).strip()


def split_lemmas(form: str) -> list[str]:
    return [p.strip() for p in clean_lemma(form).split(",") if p.strip()]


def write_rows(path: Path, rows: list[tuple], chunk: int = 50_000) -> None:
    with open(path, "w", encoding="utf-8", newline="") as fh:
        for i in range(0, len(rows), chunk):
            block = rows[i:i + chunk]
            lines = ["\t".join(cell) for cell in block]
            fh.write("\n".join(lines))
            if i + chunk < len(rows):
                fh.write("\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dict", default=str(DEFAULT_DICT))
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    parser.add_argument("--chunk", type=int, default=500)
    parser.add_argument("--backend", default=str(DEFAULT_BACKEND))
    args = parser.parse_args(argv)

    dict_path = Path(args.dict)
    out_path = Path(args.out)
    if not dict_path.is_file():
        print(f"error: dictionary snapshot not found: {dict_path}\n"
              "Run `python scripts/fetch_dictionary.py` first.",
              file=sys.stderr)
        return 2

    data = json.loads(dict_path.read_text(encoding="utf-8"))
    word_list = data["wordList"]
    header, rows = word_list[0], word_list[1:]
    print(f"dictionary: {dict_path} ({len(rows)} rows)")

    backend = MorphologyBackend(args.backend)
    started = time.time()

    out_rows: list[tuple] = []
    items = []
    seen = set()

    def add_entry(form: str, lemma: str, xpos: str, upos: str, feats: dict | None,
                  entry_type: str) -> None:
        key = (form, lemma, json.dumps(feats or {}, sort_keys=True), entry_type)
        if key not in seen:
            seen.add(key)
            out_rows.append((form, lemma, xpos, upos,
                             json.dumps(feats, ensure_ascii=False) if feats else "",
                             entry_type))

    for idx, row in enumerate(rows):
        isv = row[1]
        xpos = row[3]
        addition = row[2] if len(row) > 2 else ""
        for piece in split_lemmas(isv):
            add_entry(piece, piece, xpos, "", None, "headword")
        items.append({"id": str(idx), "form": isv, "xpos": xpos,
                      "addition": addition})

        if len(items) >= args.chunk:
            _inflect_batch(backend, items, add_entry)
            items = []
    if items:
        _inflect_batch(backend, items, add_entry)

    write_rows(out_path, out_rows)
    elapsed = time.time() - started

    raw = out_path.read_bytes()
    lexicon_manifest = {
        "source": "generated full-form lexicon",
        "derived_from": {
            "dictionary": dict_path.name,
            "dictionary_sha256": _sha256(dict_path),
        },
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "size_bytes": len(raw),
        "entry_count": len(out_rows),
        "morphology_package": "@interslavic/morphology",
        "morphology_version": morphology_version(),
        "elapsed_seconds": round(elapsed, 1),
        "license_status": "UNRESOLVED — derived from dictionary data; do not redistribute",
    }
    (out_path.with_name("lexicon.manifest.json")).write_text(
        json.dumps(lexicon_manifest, ensure_ascii=False, indent=2),
        encoding="utf-8")

    print(f"lexicon:  {out_path} ({len(out_rows)} entries, {len(raw)} bytes)")
    print(f"sha256    {lexicon_manifest['sha256']}")
    print(f"morphology @interslavic/morphology@{lexicon_manifest['morphology_version']}")
    print(f"elapsed   {elapsed:.1f}s")
    return 0


def _inflect_batch(backend: MorphologyBackend, items: list[dict],
                   add_entry) -> None:
    results = backend.inflect(items)
    for item in items:
        lemma = clean_lemma(item["form"])
        for form, llemma, upos, xpos, feats in results[item["id"]]:
            add_entry(form, llemma or lemma, xpos or item["xpos"], upos or "",
                      feats, "paradigm")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


if __name__ == "__main__":
    sys.exit(main())
