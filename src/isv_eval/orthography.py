"""Deterministic character-level orthographic sanity check (SODA Task 015).

The Interslavic letter inventory is taken verbatim from the authoritative
definition on the official Interslavic website — NOT derived from this
project's dictionaries, lexicons, Hunspell resources, or model outputs:

    https://steen.free.fr/interslavic/orthography.html
    (Orthography / Pravopisanje; fetched 2026-09-05)

Inventory accepted here (Latin script; this project's experiment outputs are
all Latin-script Medžuslovjansky):

1. Standard Latin alphabet (27 letters; all of a–z except q, w, x, plus
   č, š, ž and ě):  a b c č d e ě f g h i j k l m n o p r s š t u v y z ž
   (+ uppercase). Digraphs dž/lj/nj are combinations of these letters and
   add no extra characters.
2. Etymological alphabet (optional letters, same source):  ę ų å ė ȯ ć đ
   ĺ ń ŕ ś ź (+ uppercase).
3. Sanctioned alternative graphemes listed on the same page (overview table
   and "Etymological alphabet" section): t́/d́ written with a haček as ť/ď,
   ĺ as ľ, ń as ň, ŕ as ř, ė as è, ȯ as ò (+ uppercase); t́/d́ may also be
   written as t/d + U+0301 (combining acute), which this module accepts as
   a two-code-unit spelling of the letter t́/d́.

Everything else is reported by category and is NEVER repaired or normalized:

- CYRILLIC            any Unicode Cyrillic letter (all outputs were requested
                      in Latin script, so any Cyrillic letter is unexpected);
- POLISH_SPECIFIC     Polish letters that are NOT in the Interslavic
                      inventory: ą ł ó ż (+ uppercase).  NB ć ę ń ś ź ARE
                      valid etymological Interslavic letters, so they are
                      ALLOWED here, never flagged as Polish-specific;
- OTHER_LATIN         other Latin letters outside the inventory (e.g. q w x,
                      á é í ý, ă ē ū, ǫ …);
- OTHER_SCRIPT        letters of other scripts (Greek, Hebrew, …);
- UNEXPECTED          non-letter characters outside the accepted non-letter
                      set (control chars, emoji, math/markdown/formatting
                      glyphs such as # * → ‡ …).

Non-letter policy (letters are the only thing the alphabet check governs):
whitespace (any Unicode space incl. newlines), ASCII digits 0–9, and the
explicit prose-punctuation set are ACCEPTED and never count as errors.
The accepted punctuation set is the typography this corpus legitimately uses
(period, comma, semicolon, colon, question/exclamation, ellipsis, hyphen/
en/em dash, parentheses, guillemets, German/English quotes, apostrophes);
it was cross-checked against the actual source and output documents so that
no legitimate corpus glyph is misclassified as an alphabet violation. Any
other non-letter is counted as UNEXPECTED (a formatting/symbol note, never
an "alphabet error").

This check is an AUDIT ONLY. It never modifies, transliterates, or repairs
text, and it never touches lexical/resource coverage numbers: a word absent
from the canonical dictionary and a stray character are two independent
signals, deliberately kept separate.
"""
from __future__ import annotations

import unicodedata
from collections import Counter
from dataclasses import dataclass, field

ALPHABET_SOURCE_URL = "https://steen.free.fr/interslavic/orthography.html"
ALPHABET_SOURCE_NOTE = (
    "Official Interslavic website, 'Orthography (Pravopisanje)' — standard "
    "Latin alphabet (27 letters) + etymological alphabet extensions + "
    "sanctioned alternative graphemes; fetched 2026-09-05."
)

_STANDARD = "abcdefghijklmnoprstuvyzčěšž"
_ETYMOLOGICAL = "ęųåėȯćđĺńŕśź"
_ALTERNATIVES = "ťďľňřèò"

ALLOWED_LETTERS = frozenset(
    _STANDARD + _ETYMOLOGICAL + _ALTERNATIVES
    + (_STANDARD + _ETYMOLOGICAL + _ALTERNATIVES).upper()
)
"""Latin letters accepted in Interslavic output (lower + upper)."""

# Polish letters the task calls out that are NOT in the accepted inventory.
# ć ę ń ś ź are valid etymological ISV letters -> allowed, not listed here.
POLISH_ONLY_LETTERS = frozenset("ąłóż" + "ĄŁÓŻ")
"""Polish-specific letters that are violations (ą ł ó ż; lower + upper)."""

# Accepted non-letter characters: prose punctuation only (see module doc).
ACCEPTED_PUNCTUATION = frozenset(
    ".,;:!?…‥-–—()«»‹›„“”\"'‘’"
)
"""Prose punctuation accepted in the corpus (never an error)."""

# accepted ASCII digits + any Unicode whitespace are handled separately.

# Unicode Cyrillic blocks (all of them; covers old/new Cyrillic incl. і ї ѣ).
_CYRILLIC_RANGES = (
    (0x0400, 0x04FF), (0x0500, 0x052F), (0x1C80, 0x1C8F),
    (0x2DE0, 0x2DFF), (0xA640, 0xA69F), (0x1E030, 0x1E08F),
)
COMBINING_ACUTE = "\u0301"  # allowed only right after t / d (spelling of t́/d́)


def _is_cyrillic(ch: str) -> bool:
    o = ord(ch)
    return any(lo <= o <= hi for lo, hi in _CYRILLIC_RANGES)


def _is_other_script_letter(ch: str) -> bool:
    """A letter that is neither Cyrillic nor Latin."""
    try:
        name = unicodedata.name(ch, "")
    except ValueError:
        return False
    return (ch.isalpha() and not name.startswith("LATIN")
            and not _is_cyrillic(ch))


def char_category(ch: str, prev: str = "") -> str:
    """Category of one character (letter buckets + accepted non-letters).

    ``prev`` is the previous character, used only for the combining-acute
    spelling of t́ / d́. Returns one of: allowed_letter, cyrillic_letter,
    polish_specific_letter, other_latin_letter, other_script_letter,
    whitespace, digit, punctuation, t/d_combining_acute, unexpected.
    """
    if ch in ALLOWED_LETTERS:
        return "allowed_letter"
    if ch == COMBINING_ACUTE and prev in ("t", "d", "T", "D"):
        return "t/d_combining_acute"
    if _is_cyrillic(ch):
        return "cyrillic_letter"
    if ch in POLISH_ONLY_LETTERS:
        return "polish_specific_letter"
    if ch.isalpha():
        if ch.isascii() or (unicodedata.name(ch, "").startswith("LATIN")
                            or 0x0080 <= ord(ch) <= 0x024F
                            or 0x1E00 <= ord(ch) <= 0x1EFF
                            or 0x2C60 <= ord(ch) <= 0x2C7F
                            or 0xA720 <= ord(ch) <= 0xA7FF
                            or 0xAB30 <= ord(ch) <= 0xAB6F):
            return "other_latin_letter"
        return "other_script_letter"
    if ch.isspace():
        return "whitespace"
    if ch in "0123456789":
        return "digit"
    if ch in ACCEPTED_PUNCTUATION:
        return "punctuation"
    return "unexpected"


LETTER_CATEGORIES = ("allowed_letter", "cyrillic_letter",
                     "polish_specific_letter", "other_latin_letter",
                     "other_script_letter")


@dataclass
class CharReport:
    """Deterministic per-text character audit (see module docstring)."""

    text: str = ""
    counts: dict[str, int] = field(default_factory=dict)
    unexpected: dict[str, dict] = field(default_factory=dict)

    def _add(self, cat: str, ch: str, line: int) -> None:
        self.counts[cat] = self.counts.get(cat, 0) + 1
        if cat not in ("allowed_letter", "whitespace", "digit",
                       "punctuation", "t/d_combining_acute"):
            d = self.unexpected.setdefault(ch, {"category": cat,
                                                "count": 0,
                                                "lines": []})
            d["count"] += 1
            if line not in d["lines"]:
                d["lines"].append(line)

    @property
    def total_chars(self) -> int:
        return sum(self.counts.values())

    @property
    def allowed_letters(self) -> int:
        return self.counts.get("allowed_letter", 0) \
            + self.counts.get("t/d_combining_acute", 0)

    @property
    def cyrillic(self) -> int:
        return self.counts.get("cyrillic_letter", 0)

    @property
    def polish_specific(self) -> int:
        return self.counts.get("polish_specific_letter", 0)

    @property
    def other_latin(self) -> int:
        return self.counts.get("other_latin_letter", 0)

    @property
    def other_script(self) -> int:
        return self.counts.get("other_script_letter", 0)

    @property
    def accepted_nonletters(self) -> int:
        return (self.counts.get("whitespace", 0)
                + self.counts.get("digit", 0)
                + self.counts.get("punctuation", 0))

    @property
    def unexpected_nonletters(self) -> int:
        return self.counts.get("unexpected", 0)

    @property
    def outside_inventory(self) -> int:
        """Everything that is neither an allowed letter nor an accepted
        non-letter (whitespace/digit/prose punctuation)."""
        return self.total_chars - self.allowed_letters - self.accepted_nonletters

    def as_dict(self) -> dict:
        return {
            "total_chars": self.total_chars,
            "allowed_letters": self.allowed_letters,
            "accepted_nonletters": self.accepted_nonletters,
            "outside_inventory": self.outside_inventory,
            "cyrillic": self.cyrillic,
            "polish_specific": self.polish_specific,
            "other_latin": self.other_latin,
            "other_script": self.other_script,
            "unexpected_nonletters": self.unexpected_nonletters,
            "unexpected": {
                ch: {"char": ch, "name": unicodedata.name(ch, "?"),
                     "category": d["category"], "count": d["count"],
                     "lines": d["lines"]}
                for ch, d in sorted(self.unexpected.items())
            },
        }


def scan_text(text: str) -> CharReport:
    """Deterministically audit one text; never modifies it."""
    report = CharReport(text=text)
    line = 1
    prev = ""
    for ch in text:
        if ch == "\n":
            report._add("whitespace", ch, line)
            line += 1
            prev = ch
            continue
        cat = char_category(ch, prev)
        report._add(cat, ch, line)
        prev = ch
    return report


def scan_file(path) -> CharReport:
    return scan_text(path.read_text(encoding="utf-8"))
