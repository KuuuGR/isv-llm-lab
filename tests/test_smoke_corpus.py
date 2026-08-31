"""End-to-end evaluation of the synthetic smoke corpus against the real
lexicon artifact. Skipped when the generated lexicon is not present (it is
gitignored); regenerate with:

    python scripts/generate_lexicon.py
"""

from pathlib import Path

import pytest

from isv_eval.classifier import classify
from isv_eval.lexicon import Lexicon
from isv_eval.metrics import compute_metrics
from isv_eval.morphology import MorphologyBackend
from isv_eval.tokenizer import tokenize

PROJECT_ROOT = Path(__file__).resolve().parents[1]
LEXICON = PROJECT_ROOT / "data" / "dictionary" / "lexicon.tsv"
CORPUS = Path(__file__).parent / "fixtures" / "smoke_corpus.txt"

pytestmark = pytest.mark.skipif(
    not LEXICON.is_file(),
    reason="lexicon artifact missing; run scripts/generate_lexicon.py first",
)


@pytest.fixture(scope="module")
def result():
    lex = Lexicon.load_tsv(LEXICON)
    tokens = classify(
        tokenize(CORPUS.read_text(encoding="utf-8")),
        lex, MorphologyBackend(),
    )
    return lex, tokens


def classify_map(tokens):
    return {t.surface: t for t in tokens}


def test_exact_headwords_are_A(result):
    _, tokens = result
    by_surface = classify_map(tokens)
    for word in ("Brat", "i", "žena", "veliky", "dom", "čaj", "morje",
                 "jest", "to", "do", "v", "a", "ne"):
        assert by_surface[word].classification == "A", word


def test_inflected_forms_are_A_not_unknown(result):
    _, tokens = result
    by_surface = classify_map(tokens)
    # These are inflected forms present in the generated full-form lexicon;
    # they are bucket A, demonstrating that "not a headword" is not "unknown".
    for word, lemma in (("knigy", "kniga"), ("morja", "morje"),
                        ("prišla", "prijdti"), ("žili", "žiti"),
                        ("jehali", "jehati"), ("čita", "čitati"),
                        ("pije", "piti"), ("veliko", "veliky")):
        tok = by_surface[word]
        assert tok.classification == "A", word
        assert {m["lemma"] for m in tok.matches} == {lemma}, word


def test_folded_etymological_match(result):
    _, tokens = result
    tok = classify_map(tokens)["imajut"]
    assert tok.classification == "A"
    assert all(m.get("folded_match") for m in tok.matches)
    assert {m["dictionary_form"] for m in tok.matches} == {"imajųt"}


def test_intentional_unresolved_tokens(result):
    _, tokens = result
    by_surface = classify_map(tokens)
    for word in ("Po-mojemu", "wspaniale", "domě"):
        tok = by_surface[word]
        assert tok.classification == "C", word
        assert tok.review is True, word
        assert tok.sentence, word  # context retained


def test_numbers_and_punctuation_excluded(result):
    _, tokens = result
    by_surface = classify_map(tokens)
    assert by_surface["2024"].classification == "non_lexical"
    assert all(
        t.classification == "non_lexical"
        for t in tokens if not t.is_lexical
    )


def test_metrics_consistent(result):
    _, tokens = result
    m = compute_metrics(tokens)
    a = m["bucket_counts"]["A"]
    b = m["bucket_counts"]["B"]
    c = m["bucket_counts"]["C"]
    lexical = m["total_tokens"]
    assert a + b + c == lexical
    assert m["exact_dictionary_matches"] == a
    assert m["morphologically_valid_forms"] == b
    assert m["unresolved_forms"] == c
    assert m["exact_dictionary_coverage"] == round(a / lexical, 6)
    assert m["morphologically_valid_coverage"] == round((a + b) / lexical, 6)
    assert m["unresolved_rate"] == round(c / lexical, 6)
    # Expected values for the committed fixture corpus.
    assert lexical == 34
    assert a == 31
    assert b == 0
    assert c == 3
