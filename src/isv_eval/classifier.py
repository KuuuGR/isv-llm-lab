"""A/B/C/D classification of tokens against the lexical and morphological data.

Buckets (see DESIGN.md §5):
- ``A``  Exact lexical match: the normalized form is directly present in the
         lexical reference (headwords or generated full-form paradigms).
- ``B``  Morphologically valid: not an exact lexical match, but generated as a
         valid form of a known dictionary lemma by the morphology engine.
- ``C``  Unresolved: cannot be associated with an accepted ISV lemma/form.
- ``D``  Not a separate linguistic judgment. Unresolved (C) tokens carry
         ``review=True`` plus sentence context, lemma candidates considered,
         and failure reasons, for later manual analysis.

Design constraints implemented here:
- Never classify "not a headword" as unknown: exact-match coverage comes from
  the full-form lexicon, and the fallback re-inflects candidate lemmas.
- Lemma-driven validity, not surface POS heuristics (D-005).
- The fallback is batched: all unresolved tokens are handled in one
  morphology call per unique form set (cheap, bounded candidates).
"""

from __future__ import annotations

from .lexicon import Lexicon
from .morphology import MorphologyBackend
from .normalize import is_cyrillic, lookup_keys, normalize_word


def classify(tokens: list, lexicon: Lexicon, backend: MorphologyBackend,
             use_fallback: bool = True) -> list:
    """Classify every token in place and return the same list.

    ``use_fallback=False`` disables the morphological fallback (bucket B is
    then never assigned; tests can exercise the A/C split in isolation).
    """
    for token in tokens:
        if not token.is_lexical:
            token.classification = "non_lexical"
            continue
        token.classification = _classify_lexical(token, lexicon, backend,
                                                 use_fallback)
    return tokens


def _classify_lexical(token, lexicon: Lexicon, backend: MorphologyBackend,
                      use_fallback: bool) -> str:
    lookup = token.normalized
    if is_cyrillic(lookup):
        token.translit = backend.translit(lookup)
        lookup = token.translit

    entries = lexicon.lookup(lookup)
    if entries:
        token.matches = []
        for entry in entries:
            record = entry.as_dict()
            if normalize_word(entry.form) != lookup:
                record["folded_match"] = True
                record["dictionary_form"] = entry.form
            token.matches.append(record)
        return "A"

    if not use_fallback:
        token.review = True
        return "C"

    candidates = lexicon.candidate_lemmas(lookup)
    if not candidates:
        token.review = True
        token.candidates = []
        return "C"

    results = backend.inflect([
        {"id": c, "form": c, "xpos": lexicon.lemma_xpos(c),
         "addition": None}
        for c in candidates
    ])
    token.candidates = candidates
    token.matches = _match_in_paradigms(results, lookup)
    if token.matches:
        return "B"
    token.review = True
    return "C"


def _match_in_paradigms(results: dict[str, list[list]], lookup: str) -> list[dict]:
    """Return every (lemma, form) whose paradigm contains the lookup form.

    Uses the same lookup keys as lexical matching (primary + folded), so a
    fallback hit is also orthography-tolerant.
    """
    keys = lookup_keys(lookup)
    found = []
    for lemma, tokens in results.items():
        for form, lemma_name, upos, xpos, feats in tokens:
            norm = normalize_word(form)
            if norm in keys:
                found.append({
                    "form": form,
                    "lemma": lemma_name or lemma,
                    "xpos": xpos,
                    "upos": upos,
                    "feats": feats,
                    "source": "morphological_fallback",
                })
    return found
