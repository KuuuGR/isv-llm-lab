"""Focused tests for the two-layer resource evaluation policy (SODA Task 008).

Specification: docs/RESOURCE_POLICY.md. Requirements tested:

1. canonical form        → canonical coverage
2. canonical inflection  → canonical coverage
3. alternative-only form → broader coverage but NOT canonical coverage
4. form in several alternative resources → counted once (no double counting)
5. orthographic candidate only → not automatically counted as exact
6. unresolved form → neither coverage
7. proper name / special case → existing policy preserved (no promotion)
8. historical-only evidence → does not become canonical coverage
9. existing A/B/C behavior unchanged
"""

from isv_eval.classifier import classify
from isv_eval.evidence import (ALTERNATIVE_ATTESTATION, CANONICAL,
                               CANONICAL_INFLECTION, HISTORICAL_EVIDENCE,
                               ORTHOGRAPHIC_VARIANT, UNRESOLVED,
                               ResourceEvidenceProvider, attach_evidence)
from isv_eval.lexicon import HEADWORD, PARADIGM, Lexicon, LexiconEntry
from isv_eval.metrics import compute_metrics
from isv_eval.morphology import MorphologyBackend
from isv_eval.tokenizer import tokenize


def make_lexicon(entries):
    return Lexicon([LexiconEntry(*e) for e in entries])


def eval_text(text, entries, provider=None, use_fallback=True):
    tokens = tokenize(text)
    classify(tokens, make_lexicon(entries), MorphologyBackend(),
             use_fallback=use_fallback)
    attach_evidence(tokens, provider)
    return tokens


def make_provider():
    return ResourceEvidenceProvider(
        # surface -> raw pipeline tags (distrusted as annotation; used only
        # as exact-surface attestation)
        hunspell_forms={
            "seli": "st:seliti po:v",
            "sěděli": "st:sěděti po:v",
            "clověk": "st:člověk po:n",
            "dalše": "st:daľši po:adj deg:cmp",
        },
        # surface -> cB (log-frequency); exact attestation signal only.
        # Note: `sěli` is deliberately ABSENT verbatim (matches the audited
        # data) so its diacritic-stripped near-miss `seli` is testable.
        freq_isv={
            "seli": -619, "sedeli": -619, "reci": -580, "rekl": -486,
            "dejstvitelno": -650, "sěděli": -508,
        },
        # second wordlist as another independent alternative resource
        freq_isvx={"seli": -100},
        # historical snapshot (same lineage as basic.json; no weight)
        slovnik_index={"starodavny": [{"isv": "starodavny",
                                       "partOfSpeech": "adj"}]},
    )


BASIC = [("brat", "brat", "m.anim.", "NOUN", None, HEADWORD)]


# -- 1. canonical form ---------------------------------------------------------
def test_canonical_form_counts_toward_both_tiers():
    tokens = eval_text("brat", BASIC, make_provider())
    tok = tokens[0]
    assert tok.classification == "A"
    assert tok.resource_evidence_status == CANONICAL
    assert tok.broader_supported is True
    assert tok.resource_evidence[0]["layer"] == CANONICAL
    assert tok.resource_evidence[0]["source"] == "basic.json"
    m = compute_metrics(tokens)
    assert m["canonical_supported_tokens"] == 1
    assert m["canonical_coverage"] == 1.0
    assert m["broader_resource_supported_tokens"] == 1
    assert m["broader_resource_supported_coverage"] == 1.0


# -- 2. canonical inflection ----------------------------------------------------
def test_lexicon_paradigm_form_is_canonical_inflection():
    lex_entries = BASIC + [
        ("brata", "brat", "m.anim.", "NOUN",
         {"Case": "Gen", "Number": "Sing"}, PARADIGM),
    ]
    tokens = eval_text("brata", lex_entries, make_provider())
    tok = tokens[0]
    assert tok.classification == "A"
    assert tok.resource_evidence_status == CANONICAL_INFLECTION
    assert tok.broader_supported is True
    assert tok.resource_evidence[0]["kind"] == "lexicon_paradigm_form"


def test_morphological_fallback_is_canonical_inflection():
    tokens = eval_text("brata", BASIC, make_provider())
    tok = tokens[0]
    assert tok.classification == "B"          # fallback rescued it
    assert tok.resource_evidence_status == CANONICAL_INFLECTION
    assert tok.resource_evidence[0]["kind"] == "morphological_fallback"
    assert tok.broader_supported is True
    m = compute_metrics(tokens)
    assert m["canonical_supported_tokens"] == 1
    assert m["canonical_coverage"] == 1.0


# -- 3. alternative-resource-only form -----------------------------------------
def test_alternative_only_form_is_broader_not_canonical():
    tokens = eval_text("dejstvitelno", BASIC, make_provider())
    tok = tokens[0]
    assert tok.classification == "C"          # canonical layer: unresolved
    assert tok.resource_evidence_status == ALTERNATIVE_ATTESTATION
    assert tok.broader_supported is True
    assert tok.resource_evidence[0]["source"] == "interslavicfreq.small_isv"
    assert tok.resource_evidence[0]["kind"] == "exact_surface_attestation"
    m = compute_metrics(tokens)
    assert m["canonical_supported_tokens"] == 0
    assert m["canonical_coverage"] == 0.0
    assert m["broader_resource_supported_tokens"] == 1
    assert m["broader_resource_supported_coverage"] == 1.0


# -- 4. multiple resources → counted once ---------------------------------------
def test_multi_resource_token_counted_once():
    # `seli` is attested in isv.dic AND both frequency wordlists.
    tokens = eval_text("brat seli", BASIC, make_provider())
    by_form = {t.surface: t for t in tokens}
    assert by_form["seli"].classification == "C"
    assert by_form["seli"].resource_evidence_status == ALTERNATIVE_ATTESTATION
    layers = [r["layer"] for r in by_form["seli"].resource_evidence]
    sources = [r["source"] for r in by_form["seli"].resource_evidence]
    assert layers == [ALTERNATIVE_ATTESTATION] * 3
    assert sources == ["isv.dic", "interslavicfreq.small_isv",
                       "interslavicfreq.small_isvx"]
    m = compute_metrics(tokens)
    assert m["total_tokens"] == 2
    assert m["canonical_supported_tokens"] == 1
    assert m["broader_resource_supported_tokens"] == 2   # counted once, not 4


# -- 5. orthographic candidate only → not counted --------------------------------
def test_diacritic_stripped_candidate_is_not_exact():
    # `sěli` is NOT in any wordlist verbatim; only its diacritic-stripped
    # form `seli` is. That is an orthographic candidate, never a match.
    tokens = eval_text("sěli", BASIC, make_provider())
    tok = tokens[0]
    assert tok.classification == "C"
    assert tok.resource_evidence_status == ORTHOGRAPHIC_VARIANT
    assert tok.broader_supported is False
    assert any(r["kind"] == "diacritic_stripped"
               for r in tok.resource_evidence)
    m = compute_metrics(tokens)
    assert m["broader_resource_supported_tokens"] == 0
    assert m["broader_resource_supported_coverage"] == 0.0


def test_folded_candidate_is_not_exact():
    # `ćlověk` is only attested in isv.dic through its folded spelling
    # `clověk` — a folded near-miss, not an exact attestation.
    tokens = eval_text("ćlověk", BASIC, make_provider())
    tok = tokens[0]
    assert tok.classification == "C"
    assert tok.resource_evidence_status == ORTHOGRAPHIC_VARIANT
    assert tok.broader_supported is False
    assert any(r["kind"] == "folded_etymological"
               for r in tok.resource_evidence)


# -- 6. unresolved → neither coverage --------------------------------------------
def test_unresolved_form_counts_nowhere():
    tokens = eval_text("wspaniale", BASIC, make_provider())
    tok = tokens[0]
    assert tok.classification == "C"
    assert tok.resource_evidence_status == UNRESOLVED
    assert tok.resource_evidence == []
    assert tok.broader_supported is False
    m = compute_metrics(tokens)
    assert m["canonical_supported_tokens"] == 0
    assert m["broader_resource_supported_tokens"] == 0
    assert m["unresolved_tokens"] == 1


# -- 7. proper name / special case → existing policy preserved --------------------
def test_proper_name_is_not_promoted():
    # Story names have no dictionary path today; the evidence layer must not
    # invent one. A name attested nowhere stays unresolved.
    tokens = eval_text("Wszesław", BASIC, make_provider())
    tok = tokens[0]
    assert tok.classification == "C"
    assert tok.resource_evidence_status == UNRESOLVED
    assert tok.broader_supported is False


def test_alternative_evidence_never_becomes_A():
    # The key invariant: an alternative-resource hit stays C; it is evidence
    # in the broader tier, never a canonical match.
    tokens = eval_text("dejstvitelno", BASIC, make_provider())
    assert tokens[0].classification == "C"
    assert tokens[0].broader_supported is True


# -- 8. historical-only evidence → not canonical -----------------------------------
def test_historical_only_evidence_does_not_count():
    tokens = eval_text("starodavny", BASIC, make_provider())
    tok = tokens[0]
    assert tok.classification == "C"
    assert tok.resource_evidence_status == HISTORICAL_EVIDENCE
    assert tok.broader_supported is False
    assert tok.resource_evidence[0]["source"] == "slovnik"
    m = compute_metrics(tokens)
    assert m["canonical_supported_tokens"] == 0
    assert m["broader_resource_supported_tokens"] == 0


# -- 9. existing A/B/C behavior unchanged ------------------------------------------
def test_mixed_text_metrics_and_a_b_c_unchanged():
    entries = BASIC + [
        ("brata", "brat", "m.anim.", "NOUN",
         {"Case": "Gen", "Number": "Sing"}, PARADIGM),
    ]
    text = "brat brata seli sěli wspaniale starodavny"
    tokens = eval_text(text, entries, make_provider())
    by_form = {t.surface: t for t in tokens}
    assert by_form["brat"].classification == "A"
    assert by_form["brata"].classification == "A"
    for word in ("seli", "sěli", "wspaniale", "starodavny"):
        assert by_form[word].classification == "C", word
    m = compute_metrics(tokens)
    assert m["total_tokens"] == 6
    assert m["exact_dictionary_matches"] == 2
    assert m["canonical_supported_tokens"] == 2
    assert m["canonical_coverage"] == round(2 / 6, 6)
    assert m["broader_resource_supported_tokens"] == 3  # brat, brata, seli
    assert m["broader_resource_supported_coverage"] == round(3 / 6, 6)
    assert m["unresolved_tokens"] == 4


def test_without_provider_broader_equals_canonical():
    tokens = eval_text("brat dejstvitelno", BASIC, provider=None)
    by_form = {t.surface: t for t in tokens}
    assert by_form["brat"].broader_supported is True
    assert by_form["dejstvitelno"].classification == "C"
    assert by_form["dejstvitelno"].resource_evidence_status == UNRESOLVED
    assert by_form["dejstvitelno"].broader_supported is False
    m = compute_metrics(tokens)
    assert m["broader_resource_supported_tokens"] == m["canonical_supported_tokens"]


def test_token_dict_exposes_evidence_fields():
    tokens = eval_text("brat", BASIC, make_provider())
    d = tokens[0].as_dict()
    assert d["canonical_status"] == "A"
    assert d["broader_resource_supported"] is True
    assert d["resource_evidence_status"] == CANONICAL
    assert isinstance(d["resource_evidence"], list)
