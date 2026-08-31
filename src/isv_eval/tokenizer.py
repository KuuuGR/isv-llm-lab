"""Conservative tokenizer for literary Interslavic text.

Design:
- Paragraphs are blank-line-separated blocks.
- Sentences are split after sentence-final punctuation (``. ! ? …``) followed
  by whitespace; the punctuation stays attached to the preceding sentence.
  Known limitations (kept simple deliberately): abbreviations such as
  ``dr.`` cause an over-split; a quote closing after sentence-final
  punctuation (``„Dobro." Oni``) is not split at the closing quote.
- Tokens within a sentence: words (letters, with internal apostrophes and
  hyphens kept — e.g. ``po-mojemu`` stays one token), numbers, and
  single-character punctuation. ``is_lexical`` is true only for word tokens.
- Both the surface form and normalized lookup keys are retained.

No non-standard dependencies (stdlib ``re`` only).
"""

from __future__ import annotations

import re

from .normalize import is_lexical, lookup_keys, nfc

_PARAGRAPH_RE = re.compile(r"\n[ \t]*\n")
_SENTENCE_RE = re.compile(r"(?<=[.!?…])\s+")
_TOKEN_RE = re.compile(
    r"""
    [^\W\d_]+(?:['\u2019-][^\W\d_]+)*   # word with internal apostrophe/hyphen
  | \d+(?:[.,]\d+)*                      # number (decimal or thousands)
  | [^\s\w]                              # punctuation character
    """,
    re.VERBOSE | re.UNICODE,
)

# Token kinds
WORD = "word"
NUMBER = "number"
PUNCT = "punct"


class Token:
    __slots__ = (
        "surface",
        "normalized",
        "folded",
        "kind",
        "is_lexical",
        "sentence_id",
        "sentence",
        "paragraph_id",
        "position",
        "translit",
        "classification",
        "matches",
        "candidates",
        "review",
        # Two-layer resource evidence (SODA Task 008). ``resource_evidence``
        # is a list of {"layer", "source", "kind", "detail"} records;
        # ``resource_evidence_status`` summarizes the strongest layer;
        # ``broader_supported`` marks tokens that count toward the broader
        # resource-supported coverage metric.
        "resource_evidence_status",
        "resource_evidence",
        "broader_supported",
    )

    def __init__(self, surface: str, kind: str, sentence_id: int,
                 sentence: str, paragraph_id: int, position: int):
        self.surface = surface
        keys = lookup_keys(surface)
        self.normalized = keys[0]
        self.folded = keys[-1] if len(keys) > 1 else keys[0]
        self.kind = kind
        self.is_lexical = kind == WORD
        self.sentence_id = sentence_id
        self.sentence = sentence
        self.paragraph_id = paragraph_id
        self.position = position
        self.translit = None
        self.classification = None
        self.matches = None
        self.candidates = None
        self.review = False
        self.resource_evidence_status = None
        self.resource_evidence = []
        self.broader_supported = False

    def as_dict(self) -> dict:
        return {
            "token": self.surface,
            "normalized": self.normalized,
            "folded": self.folded,
            "kind": self.kind,
            "is_lexical": self.is_lexical,
            "sentence_id": self.sentence_id,
            "sentence": self.sentence,
            "paragraph_id": self.paragraph_id,
            "position": self.position,
            "translit": self.translit,
            "classification": self.classification,
            "canonical_status": self.classification,
            "matches": self.matches,
            "candidates": self.candidates,
            "review": self.review,
            "broader_resource_supported": self.broader_supported,
            "resource_evidence_status": self.resource_evidence_status,
            "resource_evidence": self.resource_evidence,
        }

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"Token({self.surface!r}, {self.classification})"


def tokenize(text: str) -> list[Token]:
    """Tokenize a full text into a flat list of ``Token`` objects.

    ``sentence`` holds the full sentence text so unresolved tokens can be
    reviewed with their context.
    """
    text = nfc(text)
    tokens: list[Token] = []
    sentence_id = 0

    for paragraph_id, paragraph in enumerate(_PARAGRAPH_RE.split(text)):
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        for sentence in _SENTENCE_RE.split(paragraph):
            sentence = sentence.strip()
            if not sentence:
                continue
            for match in _TOKEN_RE.finditer(sentence):
                surface = match.group(0)
                kind = _kind(surface)
                tokens.append(
                    Token(surface, kind, sentence_id, sentence, paragraph_id,
                          len(tokens))
                )
            sentence_id += 1

    return tokens


def _kind(surface: str) -> str:
    if surface[0].isdigit():
        return NUMBER
    if is_lexical(surface):
        return WORD
    return PUNCT
