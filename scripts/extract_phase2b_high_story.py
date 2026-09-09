#!/usr/bin/env python3
"""EXP-004 Phase 2B — HIGH-overlap story extraction from the author's
story bank (SODA Task 030, 2026-09-09).

The research lead supplied `InterslavicTesty.md` — a *source bank*
containing several Polish stories in one Markdown file. This module
extracts exactly ONE story section for the HIGH-overlap Phase-2B-A
experiment:

  section 3: "# 3. Iskra i Wieloryb — wersja z oryginalnymi nazwami"

and writes a plain-text story-only artifact (the same shape as the
canonical EXP-003/EXP-004 source stories: title line, heading lines,
paragraphs, no Markdown syntax tokens). It NEVER touches the bank file
(only reads it), never edits the story's Polish, and never includes the
other sections (1 "Opowieść o Faktach...", 2 "Opowieść o sygnale" —
retained in the bank, not used now — or 4 "Podkłady" — the LOW-overlap
source reserved for the NEXT stage).

Extraction + normalization rules (deterministic; documented so a future
researcher can reconstruct the frozen bytes exactly):

  1. section = the lines from the section H1 (exclusive) up to (but
     excluding) the next H1 line ("# 4. Podkłady");
  2. story title = the H1 line minus its Markdown "# " prefix and the
     bank's section number ("3. "), i.e.
     "Iskra i Wieloryb — wersja z oryginalnymi nazwami";
  3. leading blank line(s) right after the H1 and trailing blank line(s)
     at the section end are removed;
  4. per body line, ONLY Markdown structural markers are removed, all
     story text is preserved byte-for-byte:
       - "## " heading prefix  -> removed (headings stay as plain lines,
         matching the canonical source-story shape);
       - "> " blockquote prefix -> removed (song lyrics);
       - "*" emphasis markers   -> removed (paired inline emphasis;
         no asterisk is part of a word in this story);
       - a lone "---" line      -> removed (Markdown horizontal rule);
  5. runs of 2+ blank lines are collapsed to one blank line (a removed
     "---" always sat between two blank lines, so this restores the
     canonical single-blank paragraph layout);
  6. output = title line, one blank line, normalized body, one trailing
     newline.

The module never calls an LLM. It is a pure text transformation; run it
once to produce the `--src` input for
`scripts/run_exp004_phase2b.py freeze-story` (which records the
authoritative SHA-256/bytes and stores the immutable frozen copy).
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Story bank section boundaries (author's file, kept untouched)
# ---------------------------------------------------------------------------

#: the exact H1 line of the HIGH-overlap story in the author's bank.
HIGH_HEADING = "# 3. Iskra i Wieloryb — wersja z oryginalnymi nazwami"
#: the H1 that begins the next (LOW-overlap) section — extraction stops there.
NEXT_HEADING_PREFIX = "# 4. "

TITLE = "Iskra i Wieloryb — wersja z oryginalnymi nazwami"
STORY_ID = "iskra-wieloryb-original-names"
CLASSIFICATION = "high_overlap_corpus_inspired"


def _strip_title(h1_line: str) -> str:
    """H1 '  # 3. <Title>' -> '<Title>' (drop Markdown '#' + the bank's
    section number)."""
    m = re.match(r"^#\s*(?:\d+\.\s*)?(.*)$", h1_line)
    title = m.group(1) if m else h1_line.lstrip("# ").strip()
    return title.strip()


def _normalize_line(line: str) -> str:
    """Strip Markdown structural markers; keep all text characters."""
    if line.startswith("## "):
        line = line[3:]
    elif line.startswith("> "):
        line = line[2:]
    return line.replace("*", "")


def extract_story(bank_text: str) -> str:
    """Extract the HIGH-overlap story section from the bank text and
    return the normalized story-only text (deterministic)."""
    lines = bank_text.splitlines()
    # locate the HIGH H1 and the next H1 (end of the section)
    start = end = None
    for i, line in enumerate(lines):
        if line == HIGH_HEADING or re.match(
                r"^#\s*3\.\s*Iskra i Wieloryb", line):
            start = i
            break
    if start is None:
        raise ValueError(
            f"HIGH-overlap section heading {HIGH_HEADING!r} not found in "
            "the story bank")
    for i in range(start + 1, len(lines)):
        if lines[i].startswith("# "):
            end = i
            break
    if end is None:
        end = len(lines)

    body = lines[start + 1:end]
    # drop the blank line(s) right after the H1
    while body and not body[0].strip():
        body.pop(0)
    # drop trailing blank line(s)
    while body and not body[-1].strip():
        body.pop()

    out: list[str] = []
    prev_blank = True  # a blank already separates the title from the body
    for line in body:
        if line.strip() == "":
            if prev_blank:
                continue  # collapse runs of blank lines
            out.append("")
            prev_blank = True
            continue
        if line.strip() == "---":
            continue  # Markdown horizontal rule (never story text)
        out.append(_normalize_line(line))
        prev_blank = False

    # ensure a single blank line between the title and the first heading
    text = "\n".join([TITLE, ""] + out).rstrip() + "\n"
    return text


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Extract the Phase-2B HIGH-overlap story from the "
                    "author's story bank (deterministic; read-only on the "
                    "bank; never calls an LLM)")
    parser.add_argument("--bank", required=True,
                        help="author's story bank file (read-only), e.g. "
                             "InterslavicTesty.md")
    parser.add_argument("--out", required=True,
                        help="output path for the story-only plain-text "
                             "artifact (fed to freeze-story --src)")
    args = parser.parse_args(argv)

    bank = Path(args.bank).expanduser()
    if not bank.is_file():
        print(f"error: story bank not found: {bank}", file=sys.stderr)
        return 2
    out = Path(args.out).expanduser()
    out.parent.mkdir(parents=True, exist_ok=True)

    text = extract_story(bank.read_text(encoding="utf-8"))
    data = text.encode("utf-8")
    out.write_bytes(data)
    n_lines = len(text.splitlines())
    print(f"[extract] {TITLE!r} extracted from {bank} "
          f"(sha256 of bank file {sha256_bytes(bank.read_bytes())})")
    print(f"  wrote {out}  sha256 {sha256_bytes(data)}  "
          f"bytes {len(data)}  lines {n_lines}")
    print("  other bank sections (1, 2, 4) were not included; the bank "
          "file was not modified")
    return 0


if __name__ == "__main__":
    sys.exit(main())
