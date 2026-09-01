"""EXP-003 — scaffold generator tests (self-contained; no repo data needed).

Covers the deterministic alignment pipeline: exact reverse-index hits,
dictionary-verified lemma recovery, multiword expressions, proper-name
precedence over the dictionary (D-031), curated residual entries, unmapped
[?], orthographic-variant splitting, headword-note cleaning, candidate
provenance shape and ordering, and deterministic regeneration.
"""
import importlib.util
import json
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"

# basic.json-shaped fixture. Fields: id, isv, pl, partOfSpeech, type.
_FIXTURE_HEADER = ["id", "isv", "pl", "partOfSpeech", "type"]
_FIXTURE_ROWS = [
    ["1", "dom", "dom", "m.", "1"],
    ["2", "sestra", "siostra", "f.", "1"],
    ["3", "byti", "być", "v.", "1"],
    ["4", "bojati sę", "bać się", "v.refl. ipf.", "1"],
    ["5", "veliky", "wielki", "adj.", "1"],
    ["6", "někȯgda, někȯgdy", "kiedyś, czasem", "adv.", "1"],
    ["7", "međurěčje", "międzyrzecze", "n.", "2"],
    ["8", "pozirati (na)", "patrzeć", "v.intr. ipf.", "1"],
]


@pytest.fixture(scope="module")
def scaffold_mod():
    spec = importlib.util.spec_from_file_location(
        "build_exp003_scaffold", SCRIPTS / "build_exp003_scaffold.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture()
def fixture_index(tmp_path, scaffold_mod):
    data = {"wordList": [_FIXTURE_HEADER] + _FIXTURE_ROWS}
    path = tmp_path / "basic.json"
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return scaffold_mod.PolishReverseIndex.load(path)


@pytest.fixture()
def curation(tmp_path, scaffold_mod):
    base = tmp_path / "curation" / "op-pl"
    base.mkdir(parents=True)
    (base / "names.tsv").write_text(
        "Międzyrzecze\tkeep\tstory town name\n", encoding="utf-8")
    (base / "multiword.tsv").write_text(
        "po prostu\tprosto\tidiomatic\n", encoding="utf-8")
    (base / "residual.tsv").write_text(
        "bał\tbojati sę\tlemma 'bać się' (pl)\n", encoding="utf-8")
    scaffold_mod.CURATION_DIR = tmp_path / "curation"
    return scaffold_mod.load_curation()


def align_story(scaffold_mod, idx, curation, text):
    return scaffold_mod.align_story(text, idx, curation, None, None)


def _tokens_by_surface(aligned):
    out = {}
    for sent in aligned["sentences"]:
        for tok in sent["tokens"]:
            out[tok["pl_surface"]] = tok
    return out


# ---------------------------------------------------------------------------
# Reverse index + alignment pipeline
# ---------------------------------------------------------------------------


def test_reverse_index_lookup_and_provenance(scaffold_mod, fixture_index):
    hits = fixture_index.lookup("siostra")
    assert [h["isv"] for h in hits] == ["sestra"]
    assert hits[0]["pl_gloss"] == "siostra"
    assert fixture_index.headword_pos["sestra"] == ("f.", "1")


def test_exact_match(scaffold_mod, fixture_index, curation):
    aligned = align_story(scaffold_mod, fixture_index, curation, "Dom i siostra.")
    toks = _tokens_by_surface(aligned)
    assert toks["Dom"]["kind"] == "exact"
    assert toks["Dom"]["isv_candidates"][0]["surface"] == "dom"
    assert toks["Dom"]["isv_candidates"][0]["layer"] == "canonical"
    assert toks["Dom"]["isv_candidates"][0]["kind"] == "pl_gloss_exact"
    assert toks["Dom"]["isv_candidates"][0]["source"] == "basic.json"


def test_lemma_recovery_verified_by_index(scaffold_mod, fixture_index,
                                          curation):
    # 'wielkiego' → strip 'ego' → 'wielki' → must re-look-up → veliky.
    aligned = align_story(scaffold_mod, fixture_index, curation,
                          "wielkiego")
    toks = _tokens_by_surface(aligned)
    assert toks["wielkiego"]["kind"] == "recovery"
    assert toks["wielkiego"]["isv_candidates"][0]["surface"] == "veliky"
    assert toks["wielkiego"]["isv_candidates"][0]["kind"] == "lemma_recovery"
    # 'bał' has no dict entry but is curated, so no recovery attempted.
    assert toks["wielkiego"]["note"] == "recovered lemma 'wielki'"


def test_recovery_is_dictionary_filtered(scaffold_mod, fixture_index,
                                         curation):
    # 'blalwkgj' strips to a stem that does NOT re-look-up → unmapped, not a
    # guessed candidate.
    aligned = align_story(scaffold_mod, fixture_index, curation, "blalwkgj")
    toks = _tokens_by_surface(aligned)
    assert toks["blalwkgj"]["kind"] == "unmapped"
    assert toks["blalwkgj"]["isv_candidates"] == []


def test_multiword_expression(scaffold_mod, fixture_index, curation):
    aligned = align_story(scaffold_mod, fixture_index, curation,
                          "po prostu")
    toks = _tokens_by_surface(aligned)
    assert toks["po prostu"]["kind"] == "multiword"
    assert toks["po prostu"]["isv_candidates"][0]["surface"] == "prosto"
    assert toks["po prostu"]["isv_candidates"][0]["layer"] == "curated"


def test_curated_residual(scaffold_mod, fixture_index, curation):
    aligned = align_story(scaffold_mod, fixture_index, curation, "bał się")
    toks = _tokens_by_surface(aligned)
    assert toks["bał"]["kind"] == "curated"
    assert toks["bał"]["isv_candidates"][0]["surface"] == "bojati sę"
    assert "bać się" in toks["bał"]["isv_candidates"][0]["detail"]


def test_unmapped_renders_question_mark(scaffold_mod, fixture_index,
                                        curation):
    aligned = align_story(scaffold_mod, fixture_index, curation, "xyzzy")
    toks = _tokens_by_surface(aligned)
    assert toks["xyzzy"]["kind"] == "unmapped"
    payload = {"sentences": aligned["sentences"]}
    rendered = scaffold_mod.render_scaffold(payload, "B")
    assert "xyzzy" in rendered and "[?]" in rendered


def test_name_takes_precedence_over_dictionary(scaffold_mod, fixture_index,
                                               curation):
    # D-031: 'Międzyrzecze' is in the names table although 'międzyrzecze' is
    # a real basic.json pl gloss; the name must win.
    aligned = align_story(scaffold_mod, fixture_index, curation,
                          "Międzyrzecze")
    toks = _tokens_by_surface(aligned)
    assert toks["Międzyrzecze"]["kind"] == "name"
    assert toks["Międzyrzecze"]["isv_candidates"] == []
    payload = {"sentences": aligned["sentences"]}
    rendered = scaffold_mod.render_scaffold(payload, "B")
    assert "[Międzyrzecze]" in rendered
    assert "proper name — keep as-is" in rendered


def test_orthographic_variant_split(scaffold_mod, fixture_index):
    hits = fixture_index.lookup("kiedyś")
    cands = scaffold_mod.candidates_from_hits(
        hits, "pl_gloss_exact", "pl gloss '{gloss}' (basic.json row {id})",
        None, None)
    surfaces = [c["surface"] for c in cands]
    assert surfaces == ["někȯgda", "někȯgdy"]
    assert cands[0]["layer"] == "canonical"
    assert cands[1]["layer"] == "orthographic_variant"
    assert cands[1]["kind"] == "orthographic_variant"
    assert "orthographic variant of 'někȯgda'" in cands[1]["detail"]


def test_headword_note_stripped_from_surface(scaffold_mod, fixture_index):
    hits = fixture_index.lookup("patrzeć")
    cands = scaffold_mod.candidates_from_hits(
        hits, "pl_gloss_exact", "pl gloss '{gloss}' (basic.json row {id})",
        None, None)
    assert cands[0]["surface"] == "pozirati"
    assert "headword note: (na)" in cands[0]["detail"]
    # In the aligned story the rendered scaffold shows the clean surface.
    curated = {"multiword": {}, "names": {}, "residual": {}}
    aligned = scaffold_mod.align_story(
        "patrzeć", fixture_index, curated, None, None)
    cand = _tokens_by_surface(aligned)["patrzeć"]["isv_candidates"][0]
    assert cand["surface"] == "pozirati"


def test_candidate_provenance_shape(scaffold_mod, fixture_index, curation):
    aligned = align_story(scaffold_mod, fixture_index, curation,
                          "Dom siostra po prostu bał xyzzy.")
    for sent in aligned["sentences"]:
        for tok in sent["tokens"]:
            for cand in tok["isv_candidates"]:
                for key in ("surface", "layer", "source", "kind", "detail",
                            "annotations"):
                    assert key in cand, f"missing {key} in {cand}"


def test_candidate_order_hierarchy(scaffold_mod, fixture_index):
    # type ascending then lexicographic; deterministic.
    hits = [{"isv": "veliky", "pos": "adj.", "type": "1", "id": "5",
             "pl_gloss": "wielki"},
            {"isv": "međurěčje", "pos": "n.", "type": "2", "id": "7",
             "pl_gloss": "międzyrzecze"}]
    cands = scaffold_mod.candidates_from_hits(
        hits, "pl_gloss_exact", "pl gloss '{gloss}' (basic.json row {id})",
        None, None)
    assert [c["surface"] for c in cands] == ["veliky", "međurěčje"]


def test_grammar_pos_lookup_for_curated(scaffold_mod, fixture_index):
    # curated candidates that are canonical headwords get their dictionary POS.
    cands = scaffold_mod.curated_candidates(
        ["bojati sę"], "curation/residual.tsv", "basis", None, {},
        fixture_index.headword_pos)
    anns = cands[0]["annotations"]
    grammar = [a for a in anns if a["kind"] == "grammar"]
    assert grammar and grammar[0]["pos"] == "v.refl. ipf."


def test_alignment_is_deterministic(scaffold_mod, fixture_index, curation):
    story = "Dom i siostra po prostu byli. Międzyrzecze bał się kiedyś wielkiego."
    a1 = align_story(scaffold_mod, fixture_index, curation, story)
    a2 = align_story(scaffold_mod, fixture_index, curation, story)
    assert json.dumps(a1, ensure_ascii=False, sort_keys=True) == \
        json.dumps(a2, ensure_ascii=False, sort_keys=True)
    # rendered scaffolds are byte-identical too
    p1 = {"sentences": a1["sentences"]}
    r1 = scaffold_mod.render_scaffold(p1, "D")
    p2 = {"sentences": a2["sentences"]}
    r2 = scaffold_mod.render_scaffold(p2, "D")
    assert r1 == r2


def test_condition_B_uses_single_first_candidate(scaffold_mod, fixture_index,
                                                 curation):
    story = "Dom i siostra."
    aligned = align_story(scaffold_mod, fixture_index, curation, story)
    payload = {"sentences": aligned["sentences"]}
    b = scaffold_mod.render_scaffold(payload, "B")
    c = scaffold_mod.render_scaffold(payload, "C")
    assert "siostra" in b and "sestra" in b
    # B shows exactly one candidate per token line.
    assert "→ [sestra]" in b
    # C shows the same single candidate here (only one hit) but the line
    # format allows multiple.
    assert "→ [sestra]" in c
