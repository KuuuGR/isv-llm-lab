"""Lexical reference: dictionary headwords plus generated full-form paradigms.

The lexicon is a generated, gitignored artifact (``data/dictionary/lexicon.tsv``)
produced by ``scripts/generate_lexicon.py`` from the dictionary snapshot plus
the morphology backend. Format (TSV):

    form \\t lemma \\t xpos \\t upos \\t feats(JSON or empty) \\t entry_type

``entry_type`` is ``headword`` (from the dictionary word list) or ``paradigm``
(from morphology generation).

Lookups try the normalized key first and the etymological-folded key second
(see ``normalize.lookup_keys``). Multiple entries for one surface form are
preserved — a form that belongs to several lemmas reports all of them.
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path

from .normalize import lookup_keys, normalize_word

HEADWORD = "headword"
PARADIGM = "paradigm"


@dataclass(frozen=True)
class LexiconEntry:
    form: str
    lemma: str
    xpos: str
    upos: str
    feats: dict | None
    entry_type: str

    def as_dict(self) -> dict:
        return {
            "form": self.form,
            "lemma": self.lemma,
            "xpos": self.xpos,
            "upos": self.upos,
            "feats": self.feats,
            "entry_type": self.entry_type,
        }


class Lexicon:
    def __init__(self, entries: list[LexiconEntry]):
        self.entries = entries
        self._by_key: dict[str, list[LexiconEntry]] = {}
        self._lemmas_by_prefix: dict[str, set[str]] = {}
        for entry in entries:
            for key in lookup_keys(entry.form):
                self._by_key.setdefault(key, []).append(entry)
            lemma = entry.lemma
            if lemma and " " not in lemma and "," not in lemma:
                for length in (3, 4):
                    self._lemmas_by_prefix.setdefault(lemma[:length], set()).add(lemma)

    @classmethod
    def load_tsv(cls, path: str | Path) -> "Lexicon":
        entries: list[LexiconEntry] = []
        with open(path, newline="", encoding="utf-8") as fh:
            for row in csv.reader(fh, delimiter="\t"):
                if not row or not row[0]:
                    continue
                form, lemma = row[0], row[1]
                xpos = row[2] if len(row) > 2 else ""
                upos = row[3] if len(row) > 3 else ""
                feats = json.loads(row[4]) if len(row) > 4 and row[4] else None
                entry_type = row[5] if len(row) > 5 else PARADIGM
                entries.append(
                    LexiconEntry(form, lemma, xpos, upos, feats, entry_type)
                )
        return cls(entries)

    def __len__(self) -> int:
        return len(self.entries)

    def lookup(self, word: str) -> list[LexiconEntry]:
        """Exact lexical lookup. Returns all matching entries (any may match
        multiple lemmas). Empty when the form is not in the lexical data.

        A hit may be an orthographic (etymological-folded) match: the caller
        can detect it because ``normalize_word(entry.form)`` differs from the
        query's normalized form."""
        norm = normalize_word(word)
        keys = lookup_keys(norm)
        hits = self._by_key.get(keys[0])
        if hits:
            return hits
        if len(keys) > 1:
            folded = self._by_key.get(keys[1])
            if folded:
                return folded
        return []

    def candidate_lemmas(self, word: str, limit: int = 150) -> list[str]:
        """Lemma candidates for the morphological fallback (bucket B): the
        dictionary lemmas sharing the first 3–4 characters with the word.
        Bounded and deduplicated; single-token lemmas only."""
        norm = normalize_word(word)
        if len(norm) < 3:
            return []
        candidates: set[str] = set()
        candidates.update(self._lemmas_by_prefix.get(norm[:3], ()))
        candidates.update(self._lemmas_by_prefix.get(norm[:4], ()))
        return sorted(candidates)[:limit]

    def lemma_xpos(self, lemma: str) -> str | None:
        """The dictionary POS tag of a lemma (from a headword entry), used to
        guide the morphology engine in the fallback."""
        norm = normalize_word(lemma)
        for key in lookup_keys(norm):
            for entry in self._by_key.get(key, ()):
                if entry.entry_type == HEADWORD and entry.xpos:
                    return entry.xpos
        return None
