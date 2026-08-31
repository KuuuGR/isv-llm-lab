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
- The fallback is batched: all unresolved tokens share one morphology call
  per chunk of distinct candidate lemmas (no per-token subprocess).
"""

from __future__ import annotations

from .lexicon import Lexicon
from .morphology import MorphologyBackend
from .normalize import is_cyrillic, lookup_keys, normalize_word

# Distinct candidate lemmas per morphology backend call. Keeps a single
# response line bounded while still collapsing most tokens into few calls.
_FALLBACK_CHUNK = 2000


def classify(tokens: list, lexicon: Lexicon, backend: MorphologyBackend,
             use_fallback: bool = True) -> list:
    """Classify every token in place and return the same list.

    ``use_fallback=False`` disables the morphological fallback (bucket B is
    then never assigned; tests can exercise the A/C split in isolation).
    """
    fallback_tokens = []
    for token in tokens:
        if not token.is_lexical:
            token.classification = "non_lexical"
            continue
        status = _classify_a_or_defer(token, lexicon, backend, use_fallback)
        if status == "defer":
            fallback_tokens.append(token)

    if fallback_tokens:
        _run_batched_fallback(fallback_tokens, lexicon, backend)
    return tokens


def _classify_a_or_defer(token, lexicon: Lexicon, backend: MorphologyBackend,
                         use_fallback: bool) -> str:
    """Bucket A check; returns 'defer' when the token needs the fallback."""
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
        token.classification = "A"
        return "done"

    if not use_fallback:
        token.review = True
        token.classification = "C"
        return "done"

    candidates = lexicon.candidate_lemmas(lookup)
    token.candidates = candidates
    if not candidates:
        token.review = True
        token.classification = "C"
        return "done"
    return "defer"


def _run_batched_fallback(fallback_tokens, lexicon: Lexicon,
                          backend: MorphologyBackend) -> None:
    # Distinct lemmas across all tokens, one inflection each.
    distinct = sorted({c for t in fallback_tokens for c in t.candidates})
    results: dict[str, list[list]] = {}
    for start in range(0, len(distinct), _FALLBACK_CHUNK):
        chunk = distinct[start:start + _FALLBACK_CHUNK]
        batch = backend.inflect([
            {"id": c, "form": c, "xpos": lexicon.lemma_xpos(c),
             "addition": None}
            for c in chunk
        ])
        results.update(batch)

    for token in fallback_tokens:
        per_lemma = {c: results.get(c, []) for c in token.candidates}
        token.matches = _match_in_paradigms(per_lemma, token.normalized)
        if token.matches:
            token.classification = "B"
        else:
            token.review = True
            token.classification = "C"


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
