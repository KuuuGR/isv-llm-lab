"""Text and word normalization for evaluation lookups.

Lookup policy (documented in DESIGN.md / report):
- Surface forms are never modified; normalization only builds a lookup key.
- The primary lookup key is NFC + lowercase.
- A secondary "folded" key maps etymological-only ISV characters (å ę ų ȯ ė ć
  đ ď ĺ ľ ń ŕ ś ť ź) onto their base letters, so an LLM output that spells an
  etymological vowel with its base letter (e.g. ``ženoju`` for ``ženojų``) can
  still be matched. A folded match is reported as such so review can confirm
  it. Standard letters (č š ž ě) are deliberately NOT folded: they are
  meaningful in both orthographies.
- Cyrillic tokens are transliterated to ISV Latin by the morphology backend
  before lookup (kept in ``Token.translit``).
"""

from __future__ import annotations

import re
import unicodedata

# 1:1 etymological-character folding (lower- and uppercase). Same-length
# source/target so str.translate applies cleanly. Standard Interslavic
# letters (č š ž ě) are NOT folded — only the etymological-only characters
# that an LLM output may plausibly spell with their base letters.
_ETYM_SRC = "åęųȯėćđďĺľńŕśťźÅĘŲȮĖĆĐĎĹĽŃŔŚŤŹ"
_ETYM_DST = "aeuoecddllnrstzAEUOECDDLLNRSTZ"
_ETYMOLOGICAL = str.maketrans(_ETYM_SRC, _ETYM_DST)

_CYRILLIC_RE = re.compile(r"[\u0400-\u04FF]")
_LETTER_RE = re.compile(r"[^\W\d_]", re.UNICODE)


def nfc(text: str) -> str:
    return unicodedata.normalize("NFC", text)


def normalize_word(word: str) -> str:
    """Primary lookup key: NFC + lowercase, trimmed. Diacritics are kept."""
    return nfc(word).strip().lower()


def fold_etymological(word: str) -> str:
    """Secondary lookup key: base-letter folding of etymological characters."""
    return nfc(word.translate(_ETYMOLOGICAL)).lower()


def lookup_keys(word: str) -> list[str]:
    """The ordered keys to try for a lexical lookup (primary, then folded)."""
    norm = normalize_word(word)
    folded = fold_etymological(norm)
    return [norm] if norm == folded else [norm, folded]


def is_cyrillic(text: str) -> bool:
    return bool(_CYRILLIC_RE.search(text))


def is_lexical(token: str) -> bool:
    """True when the token contains at least one Unicode letter (word-like)."""
    return bool(_LETTER_RE.search(token))
