from isv_eval.classifier import classify
from isv_eval.lexicon import HEADWORD, PARADIGM, Lexicon, LexiconEntry
from isv_eval.morphology import MorphologyBackend
from isv_eval.tokenizer import tokenize


def make_lexicon(entries):
    return Lexicon([LexiconEntry(*e) for e in entries])


def classify_text(text, lexicon, use_fallback=True):
    tokens = tokenize(text)
    classify(tokens, lexicon, MorphologyBackend(), use_fallback=use_fallback)
    return {t.surface: t for t in tokens}


def test_exact_headword_match():
    lex = make_lexicon([
        ("brat", "brat", "m.anim.", "NOUN", None, HEADWORD),
        ("žena", "žena", "f.", "NOUN", None, HEADWORD),
    ])
    toks = classify_text("brat žena", lex)
    assert toks["brat"].classification == "A"
    assert toks["žena"].classification == "A"
    assert toks["brat"].matches[0]["lemma"] == "brat"


def test_inflected_form_is_exact_match_not_unknown():
    # The key linguistic requirement: a valid inflected form present in the
    # full-form lexicon is bucket A — never "not a headword = unknown".
    lex = make_lexicon([
        ("brat", "brat", "m.anim.", "NOUN", None, HEADWORD),
        ("brata", "brat", "m.anim.", "NOUN",
         {"Case": "Gen", "Number": "Sing"}, PARADIGM),
    ])
    toks = classify_text("brat brata", lex)
    assert toks["brata"].classification == "A"
    assert toks["brata"].matches[0]["lemma"] == "brat"


def test_capitalized_word_matches():
    lex = make_lexicon([("brat", "brat", "m.anim.", "NOUN", None, HEADWORD)])
    toks = classify_text("Brat", lex)
    assert toks["Brat"].classification == "A"
    assert toks["Brat"].normalized == "brat"


def test_folded_etymological_match():
    lex = make_lexicon([
        ("ženojų", "žena", "f.", "NOUN",
         {"Case": "Ins", "Number": "Sing"}, PARADIGM),
    ])
    toks = classify_text("ženoju", lex)
    assert toks["ženoju"].classification == "A"
    match = toks["ženoju"].matches[0]
    assert match["folded_match"] is True
    assert match["dictionary_form"] == "ženojų"


def test_multiple_lemma_associations_preserved():
    lex = make_lexicon([
        ("piše", "pisati", "v.tr. ipf.", "VERB", None, PARADIGM),
        ("piše", "piti", "v.tr. ipf.", "VERB", None, PARADIGM),
    ])
    toks = classify_text("piše", lex)
    assert toks["piše"].classification == "A"
    assert {m["lemma"] for m in toks["piše"].matches} == {"pisati", "piti"}


def test_unresolved_token_is_flagged_for_review():
    lex = make_lexicon([("brat", "brat", "m.anim.", "NOUN", None, HEADWORD)])
    toks = classify_text("wspaniale", lex)
    assert toks["wspaniale"].classification == "C"
    assert toks["wspaniale"].review is True
    # Context is retained for later manual review.
    assert toks["wspaniale"].sentence == "wspaniale"


def test_morphological_fallback_classifies_valid_form_as_B():
    # A valid inflected form that is missing from the precomputed lexicon is
    # rescued by re-inflecting candidate dictionary lemmas (bucket B) — the
    # DESIGN.md procedure, exercised against the real morphology backend.
    lex = make_lexicon([
        ("brat", "brat", "m.anim.", "NOUN", None, HEADWORD),
    ])
    toks = classify_text("brata", lex)
    assert toks["brata"].classification == "B"
    assert toks["brata"].matches[0]["lemma"] == "brat"
    assert toks["brata"].matches[0]["source"] == "morphological_fallback"


def test_fallback_disabled_gives_C():
    lex = make_lexicon([("brat", "brat", "m.anim.", "NOUN", None, HEADWORD)])
    toks = classify_text("brata", lex, use_fallback=False)
    assert toks["brata"].classification == "C"


def test_non_lexical_tokens_never_enter_coverage():
    lex = make_lexicon([("brat", "brat", "m.anim.", "NOUN", None, HEADWORD)])
    toks = classify_text("brat, 2024!", lex)
    assert toks["brat"].classification == "A"
    assert toks[","].classification == "non_lexical"
    assert toks["2024"].classification == "non_lexical"
    assert toks["!"].classification == "non_lexical"
