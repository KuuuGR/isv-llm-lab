"""Metrics for Experiment 001 evaluation.

Denominator policy (documented in DESIGN.md §6 and in every report):

- ``total_tokens`` is the number of *lexical* tokens (word-like tokens).
  Punctuation, numbers and other non-lexical tokens are excluded from the
  vocabulary-coverage denominators.
- ``tokens_total`` reports every token the tokenizer produced (lexical +
  non-lexical) for completeness.
- ``exact_dictionary_coverage``     = A / total_tokens
- ``morphologically_valid_coverage`` = (A + B) / total_tokens
    ("justifiable by the available ISV lexical/morphological resources" —
    the important metric; reconciliation of DESIGN.md §6 wording: the
    "headword-or-justified" reading is A + B.)
- ``unresolved_rate``              = C / total_tokens
"""

from __future__ import annotations

from collections import Counter

A = "A"
B = "B"
C = "C"
NON_LEXICAL = "non_lexical"


def compute_metrics(classifications: list) -> dict:
    counts = Counter(c.classification for c in classifications)
    a = counts[A]
    b = counts[B]
    c = counts[C]
    lexical = a + b + c
    total = len(classifications)
    non_lexical = total - lexical

    def rate(numerator: int) -> float | None:
        return round(numerator / lexical, 6) if lexical else None

    return {
        # The metric names required by the task, with explicit denominators.
        "total_tokens": lexical,
        "tokens_total": total,
        "non_lexical_tokens": non_lexical,
        "exact_dictionary_matches": a,
        "morphologically_valid_forms": b,
        "unresolved_forms": c,
        "exact_dictionary_coverage": rate(a),
        "morphologically_valid_coverage": rate(a + b),
        "unresolved_rate": rate(c),
        "denominator_policy": (
            "coverage denominators are lexical tokens (word-like tokens); "
            "punctuation and numbers are excluded; "
            "morphologically_valid_coverage = (A + B) / lexical_tokens"
        ),
        "bucket_counts": {"A": a, "B": b, "C": c, "non_lexical": non_lexical},
    }
