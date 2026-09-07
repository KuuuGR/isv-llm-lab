#!/usr/bin/env python3
"""EXP-004 Phase 2A — deterministic three-register corpus builder (SODA
Task 020).

Rebuilds the Phase-2A reference corpus from its local sources:

  Register 1 (literary / narrative): corpus/tuta-historija-excerpt.txt
      — author-supplied "Tuta historija" excerpt (SODA Task 019),
        byte-for-byte as supplied; NEVER regenerated, only read + verified.
  Register 2 (artistic / poetic):     corpus/album-ahoj-slovjani-artistic-isv.txt
      — complete unique Latin-script song material of the album "Ahoj,
        Slovjani!" (MELAC PIŠE), extracted from the author-copied webpage
        saved at corpus/sources/album-ahoj-slovjani-teksty-pesnej.html.
        Only structural/webpage cleanup + exact textual deduplication are
        applied; no linguistic normalization.
  Register 3 (informative / encyclopedic):
                                      corpus/wiki-sadovnistvo-encyclopedic-isv.txt
      — running encyclopedic prose (body paragraphs + section headings) of
        the existing Medžuslovjansky Wikipedia article "Sadovničstvo",
        cleaned deterministically from the saved article wikitext at
        corpus/sources/sadovnistvo.wikitext (retrieved via the Wikimedia
        action=raw interface). The text is an EXISTING ISV article — this
        project never translates anything into ISV.

The authoritative Phase-2A corpus consumed by the operator Prompt-1 files
is the combined file corpus/phase2a-authentic-isv-corpus.txt, assembled
from the three components under fixed plain-text section headers:

  === REGISTER 1: LITERARY / NARRATIVE ===
  === REGISTER 2: ARTISTIC / POETIC ===
  === REGISTER 3: INFORMATIVE / ENCYCLOPEDIC ===

The headers are metadata for the LLM (English register labels), not part of
the linguistic source texts.

Fairness invariant: every primed configuration receives byte-identical
corpus bytes. The combined file's SHA-256 is pinned in
scripts/run_exp004_phase2a.py and asserted by the test suite.

Extraction policy (album):
- only Latin-script song material; the Cyrillic duplicate versions and all
  webpage material (iframe/YouTube embeds, navigation, columns/wordpress
  markup, footers) are removed;
- Latin-script wording is preserved exactly (no spellcheck, no evaluator,
  no dictionary substitution, no rewriting of poetic forms);
- repeated musical material is removed when the SAME stanza/refrain
  recurs verbatim within one song (first occurrence kept); similar-but-
  different stanzas, repeated words, and short phrases are kept;
- the 11 songs appear in their original page order with song boundaries
  (Latin song titles as plain headers; the Cyrillic title halves are
  dropped with the Cyrillic material).

Extraction policy (Wikipedia):
- input: article wikitext from the leading image up to (excluding) the
  "Gledite takože" / "Iztočniky" sections;
- figure markup lines ([[Fajl:...]]) incl. their captions are excluded;
- <ref> citation markup is removed; inline {{LatCyr|A|B|C}} name-gloss
  templates are replaced by their Latin parameter (A) so the running
  prose stays clean Latin-script ISV; [[link]] markup is unwrapped to its
  displayed text; '''bold'''/''italic'' and HTML entities are resolved;
- section headings are kept as plain lines; paragraphs keep the article's
  own wording and orthography (no rewriting, no normalization, no
  evaluator filtering).

This script never calls an LLM and never fetches anything from the
network; the two sources must already exist locally under
corpus/sources/ (see corpus/README.md for the retrieval record).
"""
from __future__ import annotations

import argparse
import hashlib
import html as html_mod
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORPUS_DIR = ROOT / "experiments" / "exp004-modelscreen" / "phase2a" / "corpus"
SOURCES = CORPUS_DIR / "sources"

TUTA_FILE = CORPUS_DIR / "tuta-historija-excerpt.txt"
ALBUM_HTML = SOURCES / "album-ahoj-slovjani-teksty-pesnej.html"
WIKI_WIKITEXT = SOURCES / "sadovnistvo.wikitext"

ARTISTIC_FILE = CORPUS_DIR / "album-ahoj-slovjani-artistic-isv.txt"
WIKI_FILE = CORPUS_DIR / "wiki-sadovnistvo-encyclopedic-isv.txt"
COMBINED_FILE = CORPUS_DIR / "phase2a-authentic-isv-corpus.txt"

TUTA_SHA256 = ("413830fa4ff6aaa8833895a22e7ef1fa5fa3807e5a5a105b7e4050cf7b67a29c")

# Exact song order on the album page (Latin titles as shown on the page).
ALBUM_SONGS = [
    "Velerman", "Santiana", "Nikogda Vyše", "Rěka Essekibo",
    "Slovjanske Děvčiny", "Idi, Džoni, Idi", "Ješče Raz!",
    "Primorje Barbari", "Stara Maui", "Morske Opověsti", "Bude Dobro",
]

REGISTER_HEADERS = (
    "=== REGISTER 1: LITERARY / NARRATIVE ===",
    "=== REGISTER 2: ARTISTIC / POETIC ===",
    "=== REGISTER 3: INFORMATIVE / ENCYCLOPEDIC ===",
)

# Anchor phrases pinned by the run orchestrator's contamination checks
# (one per register; see run_exp004_phase2a.py CORPUS_ANCHORS).
REGISTER_ANCHORS = {
    "register1": "Ljudi govoret, že v tamtoj denj bylo je veliko spokojno",
    "register2": "Toj korab znajut ljudi vsi",
    "register3": "Sadovničstvo jest proces raščenja rastlin",
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


# ---------------------------------------------------------------------------
# album extraction
# ---------------------------------------------------------------------------

def _entry_content(html_text: str) -> str:
    m = re.search(
        r'<div[^>]*class="[^"]*entry-content[^"]*"[^>]*>(.*?)'
        r'</div>\s*<!--\s*\.entry-content', html_text, re.S)
    if not m:
        raise RuntimeError("cannot locate the WordPress .entry-content block")
    return m.group(1)


def _paragraph_texts(html_text: str) -> list[str]:
    """Ordered <p> contents of the entry content, with <br> mapped to '\n'
    and all other tags removed (html entities resolved)."""
    inner = _entry_content(html_text)
    out = []
    for p in re.findall(r"<p\b[^>]*>(.*?)</p>", inner, re.S):
        body = re.sub(r"<br\s*/?>", "\n", p)
        body = re.sub(r"<[^>]+>", "", body)
        body = html_mod.unescape(body)
        # collapse horizontal whitespace but KEEP blank lines (stanza
        # breaks come from <br><br>, i.e. "\n\n")
        body = re.sub(r"[ \t]+", " ", body)
        body = "\n".join(ln.strip() for ln in body.split("\n"))
        body = body.strip("\n")
        out.append(body)
    return out


def _is_latin(text: str) -> bool:
    cyr = sum(1 for c in text if 0x0400 <= ord(c) <= 0x04FF)
    return cyr == 0


def _stanzas(text: str) -> list[list[str]]:
    """Split one paragraph's text (lines joined by '\n') into stanzas:
    stanza boundaries are blank lines (double <br> in the source)."""
    stanzas = []
    for block in text.split("\n\n"):
        lines = [ln.strip() for ln in block.split("\n")]
        lines = [ln for ln in lines if ln]
        if lines:
            stanzas.append(lines)
    return stanzas


def extract_album(html_text: str) -> tuple[list[dict], int]:
    """Returns (per-song records, number of dropped duplicate stanzas)."""
    paras = _paragraph_texts(html_text)
    songs: list[dict] = []
    current = None
    dropped = 0
    for p in paras:
        if not p:
            continue
        title_m = re.match(r"^([^|\n]+?)\s*\|", p)
        lat_title = title_m.group(1).strip() if title_m else None
        if lat_title in ALBUM_SONGS:
            if current is not None:
                songs.append(current)
            current = {"title": lat_title, "stanzas": [], "dropped": 0}
            continue
        if current is None:
            continue  # pre-album page text (page header etc.)
        if not _is_latin(p):
            continue  # Cyrillic duplicate version
        for stanza in _stanzas(p):
            key = tuple(stanza)
            if key in {tuple(s) for s in current["stanzas"]}:
                current["dropped"] += 1
                dropped += 1
                continue
            current["stanzas"].append(list(stanza))
    if current is not None:
        songs.append(current)
    titles = [s["title"] for s in songs]
    if titles != ALBUM_SONGS:
        raise RuntimeError(
            f"album song order mismatch: found {titles}")
    return songs, dropped


def render_album(songs: list[dict]) -> str:
    parts: list[str] = []
    for s in songs:
        parts.append(s["title"])
        for stanza in s["stanzas"]:
            parts.append("")
            parts.extend(stanza)
    return "\n".join(parts) + "\n"


# ---------------------------------------------------------------------------
# wikipedia (article prose) extraction
# ---------------------------------------------------------------------------

def _clean_wikitext_prose(wt: str) -> str:
    # keep everything before the see-also/references tail
    cut = wt.find("\n== Gledite takože ==")
    if cut < 0:
        raise RuntimeError("cannot find the 'Gledite takože' section end")
    body = wt[:cut]
    # drop figure lines incl. captions
    lines = [ln for ln in body.split("\n")
             if not ln.lstrip().startswith("[[Fajl")
             and not ln.lstrip().startswith("[[File")
             and not ln.lstrip().startswith("[[Файл")]
    text = "\n".join(lines)
    # inline citation markup
    text = re.sub(r"<ref[^>/]*/>", "", text)
    text = re.sub(r"<ref[^>]*>.*?</ref>", "", text, flags=re.S)
    text = re.sub(r"<br\s*/?>", " ", text)
    # {{LatCyr|A|B|C}} -> A (Latin spelling; Cyrillic + translit removed)
    def _latcyr_simple(m: re.Match) -> str:
        inner = m.group(1)
        # first top-level parameter
        depth = 0
        for i, ch in enumerate(inner):
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
            elif ch == "|" and depth == 0:
                return inner[:i]
        return inner

    text = re.sub(r"\{\{\s*LatCyr\s*\|(.*?)\}\}", _latcyr_simple, text,
                  flags=re.S)
    # unwrap [[target|display]] and [[target]] links to their text
    text = re.sub(r"\[\[([^\]|]*)\|([^\]]*)\]\]", r"\2", text)
    text = re.sub(r"\[\[([^\]]*)\]\]", r"\1", text)
    # bold/italic markup
    text = re.sub(r"''+", "", text)
    # any residual html tags / templates -> empty (should be none)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\{\{.*?\}\}", "", text, flags=re.S)
    text = html_mod.unescape(text)
    # headings keep their title text as a plain line
    text = re.sub(r"^=+\s*(.*?)\s*=+\s*$", r"\1", text, flags=re.M)
    # collapse empty lines runs to single blank lines; trim each line
    paras = [re.sub(r"[ \t]+", " ", ln).strip()
             for ln in text.split("\n")]
    out: list[str] = []
    blank = False
    for ln in paras:
        if not ln:
            if blank:
                continue
            blank = True
            out.append("")
            continue
        blank = False
        out.append(ln)
    while out and not out[-1]:
        out.pop()
    while out and not out[0]:
        out.pop(0)
    return "\n".join(out) + "\n"


# ---------------------------------------------------------------------------
# combined corpus
# ---------------------------------------------------------------------------

def assemble(register_texts: list[str]) -> str:
    parts = []
    for header, body in zip(REGISTER_HEADERS, register_texts):
        parts.append(header + "\n\n" + body.rstrip("\n") + "\n")
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# validation helpers (used by the test suite as well)
# ---------------------------------------------------------------------------

def cyrillic_count(text: str) -> int:
    return sum(1 for c in text if 0x0400 <= ord(c) <= 0x04FF)


def has_html_markup(text: str) -> bool:
    return bool(re.search(r"<[a-zA-Z/!]", text))


# ---------------------------------------------------------------------------
# run
# ---------------------------------------------------------------------------

def _stats(path: Path) -> dict:
    data = path.read_bytes()
    text = data.decode("utf-8")
    return {
        "file": str(path.relative_to(ROOT)),
        "bytes": len(data),
        "chars": len(text),
        "words": len(re.findall(r"\S+", text)),
        "lines": text.count("\n"),
        "sha256": sha256_bytes(data),
    }


def run(force: bool = False) -> int:
    if not TUTA_FILE.is_file():
        print(f"error: missing {TUTA_FILE}", file=sys.stderr)
        return 2
    if sha256_file(TUTA_FILE) != TUTA_SHA256:
        raise RuntimeError(
            f"{TUTA_FILE.name} sha256 changed vs the pinned Task-019 "
            "excerpt; refusing to assemble a corpus on top of an edited "
            "register-1 source")
    for f in (ALBUM_HTML, WIKI_WIKITEXT):
        if not f.is_file():
            print(f"error: missing source {f}", file=sys.stderr)
            return 2

    # register 1 — verbatim author-supplied excerpt
    register1 = TUTA_FILE.read_text(encoding="utf-8")
    if not register1.endswith("\n"):
        register1 += "\n"

    # register 2 — album
    songs, dropped = extract_album(ALBUM_HTML.read_text(
        encoding="utf-8", errors="replace"))
    album_text = render_album(songs)
    if cyrillic_count(album_text) or has_html_markup(album_text):
        raise RuntimeError("album extraction produced Cyrillic or HTML "
                           "markup; refusing to write a contaminated corpus")

    # register 3 — wikipedia prose
    wiki_text = _clean_wikitext_prose(WIKI_WIKITEXT.read_text(
        encoding="utf-8"))
    if cyrillic_count(wiki_text) or has_html_markup(wiki_text):
        raise RuntimeError("wiki extraction produced Cyrillic or HTML "
                           "markup; refusing to write a contaminated corpus")
    for bad in ("[[", "{{", "<ref", "Gledite takože", "Iztočniky",
                "Fajl:"):
        if bad in wiki_text:
            raise RuntimeError(f"wiki prose still contains {bad!r}")

    combined = assemble([register1, album_text, wiki_text])
    for anchor in REGISTER_ANCHORS.values():
        if anchor not in combined:
            raise RuntimeError(f"missing corpus anchor {anchor!r}")

    targets = [
        (ARTISTIC_FILE, album_text),
        (WIKI_FILE, wiki_text),
        (COMBINED_FILE, combined),
    ]
    for path, text in targets:
        if path.is_file() and not force:
            print(f"error: {path} exists; use --force to rebuild",
                  file=sys.stderr)
            return 2
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    print("album: 11 songs; unique stanzas per song:")
    total_stanzas = 0
    total_lines = 0
    for s in songs:
        n = len(s["stanzas"])
        ls = sum(len(st) for st in s["stanzas"])
        total_stanzas += n
        total_lines += ls
        print(f"  {s['title']:<22} {n:>2} stanzas / {ls:>3} lines "
              f"(dropped {s['dropped']} verbatim repeats)")
    print(f"  total {total_stanzas} stanzas / {total_lines} lines; "
          f"{dropped} duplicate stanzas removed")
    for path, _text in targets:
        st = _stats(path)
        print(f"[write] {st['file']}  {st['bytes']} B  "
              f"sha256 {st['sha256']}")
    st = _stats(COMBINED_FILE)
    print(f"\ncombined corpus (authoritative): {st['bytes']} bytes, "
          f"~{st['words']} whitespace tokens, sha256 {st['sha256']}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true",
                        help="overwrite existing corpus component files")
    args = parser.parse_args(argv)
    try:
        return run(args.force)
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
