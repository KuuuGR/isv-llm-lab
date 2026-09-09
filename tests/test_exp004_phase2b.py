"""EXP-004 Phase 2B HIGH-overlap kit + authentic-corpus self-evaluation
tests (SODA Task 029).

Phase-2B HIGH-overlap kit (scripts/run_exp004_phase2b.py):
- freeze-story: author's original file is only read; frozen versions are
  immutable and preserved; the current version is pinned in provenance;
  prepare fails loudly (never fabricates) when no story is frozen;
- prepare: exactly 7 representative configurations x direct/primed x
  r01..r03 = 42 planned HIGH-overlap runs (21 direct + 21 primed), 63
  prompt files, unique 7-field run ids (…__p2b-high__…), prompt manifest
  hashes matching on-disk bytes, deterministic regeneration;
- prompt fidelity: direct prompts are corpus-free (no corpus anchors,
  no study text); primed msg1 embeds the complete corpus + the Phase-2A
  study instruction; msg2 is the Phase-2A translation task; the three
  replicate files of a (configuration, condition) are byte-identical;
- no LOW-overlap (`Opowieść o sygnale` / `Podkłady`) or biomedical/
  UNSEEN-domain run can enter the HIGH manifest; story classification is
  `high_overlap_corpus_inspired`, never an independent control;
- the authoritative corpus is never shortened (full bytes, SHA-256 gate).

Corpus self-evaluation (scripts/selfeval_exp004_corpus.py):
- register boundaries are preserved: the combined corpus is exactly
  assemble(register1, register2, register3) with the fixed headers;
- corpus metrics are reproducible (deterministic structure; hermetic
  tests fake only the slow isv-eval subprocess, never its definitions);
- the orthography audit is deterministic;
- committed corpus_selfeval.json hashes match the on-disk corpus files.
"""
import importlib.util
import json
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
ROOT = SCRIPTS.parent

DATE = "2099-02-02"

_STORY = (
    "Iskra i Wieloryb — wersja z oryginalnymi nazwami\n"
    "Prolog\n\n"
    "W krainie wiecznej zimy Iskra odziedziczyła klucz po dziadku. "
    "Zimorodzice śpiewały o Mogiły Szronu i o Sercu Ziemi. Wieloryb "
    "wynurzył się z burzy.\n"
    "\nKONIEC\n"
)
_STORY_V2 = (
    "Iskra i Wieloryb — wersja z oryginalnymi nazwami\n"
    "Prolog\n\n"
    "Wersja druga: wieczna zima, klucz po dziadku, Zimorodzice, Mogiła "
    "Szronu, Serce Ziemi i wieloryb.\n"
    "\nKONIEC\n"
)
_CORPUS = (
    "=== REGISTER 1: LITERARY / NARRATIVE ===\n\n"
    "Ljudi govoret, že v tamtoj denj bylo je veliko spokojno.\n\n"
    "=== REGISTER 2: ARTISTIC / POETIC ===\n\n"
    "Toj korab znajut ljudi vsi\n\n"
    "=== REGISTER 3: INFORMATIVE / ENCYCLOPEDIC ===\n\n"
    "Sadovničstvo jest proces raščenja rastlin.\n"
)
ANCHORS = (
    "Ljudi govoret, že v tamtoj denj bylo je veliko spokojno",
    "Toj korab znajut ljudi vsi",
    "Sadovničstvo jest proces raščenja rastlin",
)
TRANSLATION_START = "Translate the Polish story below into Interslavic"
STUDY_TEXT_FRAGMENT = "REGISTER 1 — literary / narrative"

CORPUS_SHA = "aaad28e43935a40313585d77a33bfc788d97e8d69b081f9486af74d52ca1a857"


def _load(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def p2b_mod():
    return _load("run_exp004_phase2b", "run_exp004_phase2b.py")


@pytest.fixture(scope="module")
def se_mod():
    return _load("selfeval_exp004_corpus", "selfeval_exp004_corpus.py")


@pytest.fixture()
def kit(p2b_mod, tmp_path, monkeypatch):
    """Temp Phase-2B HIGH kit: synthetic story + synthetic corpus. Roster
    rows are the real authoritative 18-configuration roster (like the
    repeats tests)."""
    exp = tmp_path / "exp004"
    phase2b = exp / "phase2b"
    inp = phase2b / "input"
    versions = inp / "versions"
    prompts = phase2b / "operator-prompts"
    outputs = phase2b / "outputs"
    versions.mkdir(parents=True)
    prompts.mkdir(parents=True)
    outputs.mkdir(parents=True)
    corpus = tmp_path / "corpus.txt"
    corpus.write_text(_CORPUS, encoding="utf-8")

    monkeypatch.setattr(p2b_mod, "EXP", exp)
    monkeypatch.setattr(p2b_mod, "PHASE2B", phase2b)
    monkeypatch.setattr(p2b_mod, "INPUT_DIR", inp)
    monkeypatch.setattr(p2b_mod, "VERSIONS_DIR", versions)
    monkeypatch.setattr(p2b_mod, "OPERATOR_PROMPTS", prompts)
    monkeypatch.setattr(p2b_mod, "OUTPUTS_DIR", outputs)
    # corpus accessed through the repeats module object at prepare time
    monkeypatch.setattr(p2b_mod.rep.p2a, "CORPUS_FILE", corpus)
    monkeypatch.setattr(
        p2b_mod.rep, "AUTH_CORPUS_SHA256",
        p2b_mod.rep.sha256_bytes(_CORPUS.encode("utf-8")))
    return {"phase2b": phase2b, "input": inp, "versions": versions,
            "prompts": prompts, "outputs": outputs, "corpus": corpus}


def _freeze(p2b_mod, kit, text, label="v1", note="synthetic"):
    src = kit["input"] / f"author-{label}.txt"
    src.write_text(text, encoding="utf-8")
    rc = p2b_mod.run_freeze_story(str(src), label, note)
    assert rc == 0
    return src


def _prepare(p2b_mod, kit, force=False):
    rc = p2b_mod.run_prepare(DATE, force)
    assert rc == 0
    return json.loads((kit["outputs"] / "plan.json").read_text(
        encoding="utf-8"))


# ---------------------------------------------------------------------------
# freeze-story
# ---------------------------------------------------------------------------

def test_freeze_story_preserves_author_file(p2b_mod, kit):
    src = _freeze(p2b_mod, kit, _STORY)
    assert src.read_text(encoding="utf-8") == _STORY  # untouched
    meta = json.loads((kit["input"] / "high-overlap-story.meta.json")
                      .read_text(encoding="utf-8"))
    assert meta["classification"] == "high_overlap_corpus_inspired"
    assert meta["story_id"] == "iskra-wieloryb-original-names"
    assert meta["title"].startswith("Iskra i Wieloryb")
    v = meta["versions"]["v1"]
    assert v["sha256"] == p2b_mod.sha256_bytes(_STORY.encode("utf-8"))
    frozen = kit["input"] / v["file"]
    assert frozen.read_text(encoding="utf-8") == _STORY


def test_freeze_story_versions_immutable_and_preserved(p2b_mod, kit):
    _freeze(p2b_mod, kit, _STORY, "v1")
    _freeze(p2b_mod, kit, _STORY_V2, "v2")
    v1_file = kit["versions"] / "iskra-wieloryb-original-names-v1.txt"
    v2_file = kit["versions"] / "iskra-wieloryb-original-names-v2.txt"
    assert v1_file.is_file() and v1_file.read_text() == _STORY  # preserved
    assert v2_file.read_text() == _STORY_V2
    meta = json.loads((kit["input"] / "high-overlap-story.meta.json")
                      .read_text(encoding="utf-8"))
    assert meta["current_version"] == "v2"
    # duplicate freeze refused
    assert p2b_mod.run_freeze_story(str(kit["input"] / "author-v2.txt"),
                                    "v2", "") == 2
    # prepare now gates on v2 bytes
    plan = _prepare(p2b_mod, kit)
    assert plan["source"]["version"] == "v2"
    assert plan["source"]["sha256"] == p2b_mod.sha256_bytes(
        _STORY_V2.encode("utf-8"))


def test_prepare_fails_loudly_without_frozen_story(p2b_mod, kit):
    with pytest.raises(RuntimeError, match="has not been frozen"):
        p2b_mod.run_prepare(DATE)


# ---------------------------------------------------------------------------
# prepare — counts, ids, manifest
# ---------------------------------------------------------------------------

def test_prepare_42_high_runs_only(p2b_mod, kit):
    _freeze(p2b_mod, kit, _STORY)
    plan = _prepare(p2b_mod, kit)
    counts = plan["counts"]
    assert counts["representative_configurations"] == 7
    assert counts["total_runs"] == 42
    assert counts["direct_runs"] == 21
    assert counts["primed_runs"] == 21
    assert counts["prompt_files"] == 63
    runs = plan["runs"]
    assert len(runs) == 42
    ids = [r["run_id"] for r in runs]
    assert len(set(ids)) == 42
    assert all(r["regime"] == "high" and r["phase"] == "p2b-high"
               for r in runs)
    # replicate blocks: 3 reps x (direct, primed) per configuration
    per_cfg = {}
    for r in runs:
        per_cfg.setdefault(r["label"], []).append(r["condition"])
    assert sorted(per_cfg) == sorted(
        ["Gemini 3.6 Flash — extended thinking ON",
         "Gemini 3.6 Flash — extended thinking OFF",
         "Claude Sonnet 5 — Medium (default)",
         "DeepSeek V3 Expert — DeepThink ON",
         "Qwen 3.8 Max — Fast",
         "GPT-5.6 Luna — thinking OFF",
         "Grok 4.5 Fast"])
    for label, conds in per_cfg.items():
        assert conds == ["direct", "primed"] * 3, label
    assert all(r["source_classification"]
               == "high_overlap_corpus_inspired" for r in runs)
    assert all(r["status"] == "pending_manual_collection" for r in runs)


def test_prepare_no_low_unseen_or_biomedical_runs(p2b_mod, kit):
    _freeze(p2b_mod, kit, _STORY)
    plan = _prepare(p2b_mod, kit)
    blob = json.dumps(plan, ensure_ascii=False)
    for forbidden in ("Opowieść o sygnale", "Podkłady", "biomed",
                      "electromedicine", "p2b-low", "p2b-unseen",
                      "independent_same_topic"):
        assert forbidden not in blob
    manifest = json.loads(
        (kit["prompts"] / "manifest.json").read_text(encoding="utf-8"))
    assert len(manifest["files"]) == 63
    assert all(f["regime"] == "high" for f in manifest["files"])


def test_prepare_manifest_hashes_match_disk(p2b_mod, kit):
    _freeze(p2b_mod, kit, _STORY)
    _prepare(p2b_mod, kit)
    manifest = json.loads(
        (kit["prompts"] / "manifest.json").read_text(encoding="utf-8"))
    for f in manifest["files"]:
        data = (kit["prompts"] / f["file"]).read_bytes()
        assert p2b_mod.sha256_bytes(data) == f["prompt_sha256"]
        assert len(data) == f["bytes"]
        assert f["run_id"].startswith(DATE)
        assert "__p2b-high__" in f["run_id"]
        p2b_mod.parse_run_id(f["run_id"])  # scheme valid


def test_prepare_direct_prompts_corpus_free(p2b_mod, kit):
    _freeze(p2b_mod, kit, _STORY)
    _prepare(p2b_mod, kit)
    direct_files = sorted((kit["prompts"] / f).name for f in
                          (kit["prompts"]).glob("high-direct-*.md"))
    assert len(direct_files) == 21
    for name in direct_files:
        text = (kit["prompts"] / name).read_text(encoding="utf-8")
        assert TRANSLATION_START in text
        assert "## Output" in text
        for anchor in ANCHORS:
            assert anchor not in text
        assert STUDY_TEXT_FRAGMENT not in text
        assert _STORY.split("Prolog")[0].strip() in text  # story present


def test_prepare_primed_prompts_corpus_gated(p2b_mod, kit):
    _freeze(p2b_mod, kit, _STORY)
    plan = _prepare(p2b_mod, kit)
    msg1_files = sorted((kit["prompts"]).glob("high-primed-*-msg1.md"))
    msg2_files = sorted((kit["prompts"]).glob("high-primed-*-msg2.md"))
    assert len(msg1_files) == len(msg2_files) == 21
    for f in msg1_files:
        text = f.read_text(encoding="utf-8")
        for anchor in ANCHORS:
            assert anchor in text
        assert STUDY_TEXT_FRAGMENT in text
        assert "Do NOT translate" in text
        assert _CORPUS.rstrip() in text or "Sadovničstvo jest proces" in text
    for f in msg2_files:
        text = f.read_text(encoding="utf-8")
        assert TRANSLATION_START in text
        assert "Using the authentic Medžuslovjansky text" in text
        for anchor in ANCHORS:
            assert anchor not in text  # msg2 never carries corpus bytes
    # every primed plan row pins the authoritative corpus sha
    for r in plan["runs"]:
        if r["condition"] == "primed":
            assert r["corpus_sha256"] == p2b_mod.rep.sha256_file(
                kit["corpus"])


def test_prepare_replicate_bytes_identical(p2b_mod, kit):
    _freeze(p2b_mod, kit, _STORY)
    _prepare(p2b_mod, kit)
    groups = {}
    for f in sorted((kit["prompts"]).glob("high-*.md")):
        stem = f.name
        # drop the replicate tag -> group key
        key = stem.replace("-r01", "").replace("-r02", "").replace("-r03", "")
        groups.setdefault(key, []).append(stem)
    for key, stems in groups.items():
        contents = {(kit["prompts"] / s).read_bytes() for s in stems}
        assert len(contents) == 1, f"replicates differ for {key}"


def test_prepare_deterministic_regeneration(p2b_mod, kit):
    _freeze(p2b_mod, kit, _STORY)
    _prepare(p2b_mod, kit)
    snap = {
        "plan": (kit["outputs"] / "plan.json").read_bytes(),
        "manifest": (kit["prompts"] / "manifest.json").read_bytes(),
        "checklist": (kit["outputs"] / "collection-checklist.md")
        .read_bytes(),
        "prompts": sorted((kit["prompts"] / f).read_bytes() for f in
                          (kit["prompts"]).glob("high-*.md")),
    }
    _prepare(p2b_mod, kit, force=True)
    assert snap["plan"] == (kit["outputs"] / "plan.json").read_bytes()
    assert snap["manifest"] == (kit["prompts"] / "manifest.json").read_bytes()
    assert snap["checklist"] == (kit["outputs"] / "collection-checklist.md") \
        .read_bytes()
    prompts2 = sorted((kit["prompts"] / f).read_bytes() for f in
                      (kit["prompts"]).glob("high-*.md"))
    assert snap["prompts"] == prompts2


def test_story_corpus_hashes_pinned_in_plan(p2b_mod, kit):
    _freeze(p2b_mod, kit, _STORY)
    plan = _prepare(p2b_mod, kit)
    assert plan["source"]["classification"] \
        == "high_overlap_corpus_inspired"
    assert plan["source"]["sha256"] \
        == p2b_mod.sha256_bytes(_STORY.encode("utf-8"))
    assert plan["corpus"]["sha256"] \
        == p2b_mod.sha256_bytes(_CORPUS.encode("utf-8"))


# ---------------------------------------------------------------------------
# canonical Grok 4.5 Fast identity (Task 031)
# ---------------------------------------------------------------------------

def _grok_runs(plan: dict) -> list[dict]:
    return [r for r in plan["runs"] if r["provider"] == "xai"]


def test_grok_shortlist_row_uses_canonical_fast_identity(p2b_mod, kit):
    _freeze(p2b_mod, kit, _STORY)
    plan = _prepare(p2b_mod, kit)
    grok = _grok_runs(plan)
    assert len(grok) == 6  # 3 direct + 3 primed
    for r in grok:
        assert r["model"] == "grok"
        assert r["model_version"] == "fast"          # canonical token
        assert r["label"] == "Grok 4.5 Fast"          # canonical label
        assert r["run_id"].startswith(
            f"{DATE}__p2b-high__xai__grok__fast__")
        assert "unknown" not in r["run_id"]
        assert "Grok 4.5, built by xAI (fast)" in r["identity_note"]
        assert "__xai__grok__fast__" in r["run_id"]


def test_grok_prompt_files_and_manifest_canonical(p2b_mod, kit):
    _freeze(p2b_mod, kit, _STORY)
    plan = _prepare(p2b_mod, kit)
    manifest = json.loads((kit["prompts"] / "manifest.json")
                          .read_text(encoding="utf-8"))
    grok_files = sorted(
        (kit["prompts"] / f).name for f in
        (kit["prompts"]).glob("high-*-07-grok-fast-*.md"))
    assert len(grok_files) == 9  # 3 direct + 3 msg1 + 3 msg2
    for f in manifest["files"]:
        if f["run_id"].startswith(f"{DATE}__p2b-high__xai__grok__"):
            assert f["run_id"].startswith(
                f"{DATE}__p2b-high__xai__grok__fast__")
            assert "grok-fast" in f["file"]
            assert "unknown" not in f["file"]
    # prompt headers render the canonical identity (filename/metadata agree)
    for name in grok_files:
        text = (kit["prompts"] / name).read_text(encoding="utf-8")
        assert "# EXP-004 Phase 2B — HIGH-overlap test — Grok 4.5 Fast" \
            in text
        assert "Target model: Grok 4.5 Fast" in text
        assert "Identity note: Operator-reported model identity:" in text
        assert "Grok 4.5, built by xAI (fast)" in text
        assert "unknown" not in text
    # no historical 'unknown' Grok artifact may enter the HIGH kit
    blob = json.dumps(plan, ensure_ascii=False)
    assert "xai__grok__unknown" not in blob
    assert "grok-unknown" not in blob


def test_historical_roster_row_keeps_recorded_unknown(p2b_mod):
    """Task 031 preserves the historical Phase-1 roster row: the recorded
    'unknown' identity token stays untouched (historical provenance); the
    canonical overlay exists for forward-looking kits only."""
    p1 = p2b_mod.p1
    row = next(r for r in p1.ROSTER
               if (r["provider"], r["model"], r["model_version"])
               == p1.GROK_HISTORICAL_KEY)
    assert row["model_version"] == "unknown"
    assert row["label"] == "Grok"
    assert p1.is_grok_historical(row)
    over = p1.canonical_grok_row(row)
    assert over["model_version"] == "fast"
    assert over["label"] == "Grok 4.5 Fast"
    # the historical row object itself is not mutated
    assert row["model_version"] == "unknown"
    alias = p1.grok_run_id_alias(
        "2026-09-06__xai__grok__unknown__direct")
    assert alias == "2026-09-06__xai__grok__fast__direct"
    assert p1.grok_run_id_alias(
        "2026-09-06__anthropic__claude__sonnet-5__direct") \
        == "2026-09-06__anthropic__claude__sonnet-5__direct"


# ---------------------------------------------------------------------------
# corpus self-evaluation (hermetic; the slow isv-eval subprocess is faked,
# its definitions are untouched — only the call is replaced)
# ---------------------------------------------------------------------------

_FAKE_METRICS = {
    "total_tokens": 100, "tokens_total": 120,
    "non_lexical_tokens": 20,
    "exact_dictionary_matches": 70, "morphologically_valid_forms": 5,
    "unresolved_forms": 25,
    "exact_dictionary_coverage": 0.7,
    "morphologically_valid_coverage": 0.75,
    "unresolved_rate": 0.25,
    "canonical_supported_tokens": 75, "canonical_coverage": 0.75,
    "broader_resource_supported_tokens": 90,
    "broader_resource_supported_coverage": 0.9,
    "unresolved_tokens": 25,
}

_FAKE_TOKENS = [
    {"token": "Ljudi", "normalized": "ljudi", "kind": "word",
     "is_lexical": True, "classification": "A"},
    {"token": "korab", "normalized": "korab", "kind": "word",
     "is_lexical": True, "classification": "A",
     "broader_resource_supported": True},
    {"token": "xyzabc", "normalized": "xyzabc", "kind": "word",
     "is_lexical": True, "classification": "C",
     "broader_resource_supported": False},
    {"token": ",", "normalized": ",", "kind": "punct",
     "is_lexical": False, "classification": "non_lexical"},
]


@pytest.fixture()
def fake_eval(se_mod, monkeypatch):
    def _fake_cli(text_path: Path, out_dir: Path) -> None:
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "report.json").write_text(json.dumps(
            {"evaluator": {"name": "isv-eval", "version": "test",
                           "commit": "fake"},
             "metrics": _FAKE_METRICS}), encoding="utf-8")
        (out_dir / "tokens.json").write_text(json.dumps(_FAKE_TOKENS),
                                             encoding="utf-8")
    monkeypatch.setattr(se_mod, "run_isv_eval_cli", _fake_cli)


def test_corpus_selfeval_evaluate_dataset_structure(se_mod, kit, fake_eval,
                                                    tmp_path):
    text = tmp_path / "reg.txt"
    text.write_text("Ljudi govoret, že v tamtoj denj bylo je veliko "
                    "spokojno.\n", encoding="utf-8")
    ds = {"id": "register1", "label": "Register 1", "register": 1,
          "file": text}
    rec = se_mod.evaluate_dataset(ds, tmp_path / "scratch")
    assert rec["metrics"]["canonical_coverage"] == 0.75
    assert rec["orthography"]["outside_inventory"] >= 0
    assert rec["sha256"] == se_mod.sha256_file(text)


def test_corpus_selfeval_hash_gate_fails_loudly(se_mod, kit, fake_eval,
                                                tmp_path):
    text = tmp_path / "reg.txt"
    text.write_text("x\n", encoding="utf-8")
    ds = {"id": "register1", "label": "R1", "register": 1, "file": text,
          "sha256": "0" * 64}
    with pytest.raises(RuntimeError, match="does not match"):
        se_mod.evaluate_dataset(ds, tmp_path / "scratch")


def test_cross_register_composition(se_mod):
    recs = [
        {"register": 1, "tokens": [
            {"token": "ljudi", "normalized": "ljudi", "is_lexical": True,
             "classification": "A"},
            {"token": "xyz", "normalized": "xyz", "is_lexical": True,
             "classification": "C", "broader_resource_supported": False}]},
        {"register": 2, "tokens": [
            {"token": "ljudi", "normalized": "ljudi", "is_lexical": True,
             "classification": "A"},
            {"token": "korab", "normalized": "korab", "is_lexical": True,
             "classification": "B"}]},
        {"register": 3, "tokens": [
            {"token": "rastlin", "normalized": "rastlin", "is_lexical": True,
             "classification": "A"}]},
    ]
    cross = se_mod.cross_register(recs)
    assert cross["per_register_unique_surfaces"]["1"] == 2
    assert cross["pairwise"]["1_x_2"]["shared_surfaces"] == 1
    assert cross["all_three_shared"] == 0
    assert cross["union_all_registers"] == 4
    assert "NOT a quality score" in cross["note"]


def test_orthography_audit_deterministic(se_mod, tmp_path):
    text = tmp_path / "t.txt"
    text.write_text("Ljudi govoret, že v tamtoj denj. Żółw Ćma ą ę — …",
                    encoding="utf-8")
    a = se_mod.scan_file(text).as_dict()
    b = se_mod.scan_file(text).as_dict()
    assert a == b
    assert a["outside_inventory"] == (a["cyrillic"] + a["polish_specific"]
                                      + a["other_latin"] + a["other_script"]
                                      + a["unexpected_nonletters"])


def test_model_comparison_groups_empty_without_rosters(se_mod, monkeypatch,
                                                       tmp_path):
    monkeypatch.setattr(se_mod, "EXP", tmp_path)
    assert se_mod.model_output_groups() == []


# ---------------------------------------------------------------------------
# real-corpus checks (skip cleanly when the gitignored corpus is absent)
# ---------------------------------------------------------------------------

CORPUS_FILE = ROOT / "experiments" / "exp004-modelscreen" / "phase2a" \
    / "corpus" / "phase2a-authentic-isv-corpus.txt"
REGISTER_FILES = {
    "register1": ROOT / "experiments" / "exp004-modelscreen" / "phase2a" \
        / "corpus" / "tuta-historija-excerpt.txt",
    "register2": ROOT / "experiments" / "exp004-modelscreen" / "phase2a" \
        / "corpus" / "album-ahoj-slovjani-artistic-isv.txt",
    "register3": ROOT / "experiments" / "exp004-modelscreen" / "phase2a" \
        / "corpus" / "wiki-sadovnistvo-encyclopedic-isv.txt",
}


def _real_corpus():
    return CORPUS_FILE.is_file() and all(p.is_file()
                                         for p in REGISTER_FILES.values())


@pytest.mark.skipif(not _real_corpus(), reason="authoritative corpus is "
                                               "gitignored/local-only")
def test_real_corpus_sha256_pinned():
    import hashlib
    assert hashlib.sha256(CORPUS_FILE.read_bytes()).hexdigest() == CORPUS_SHA


@pytest.mark.skipif(not _real_corpus(), reason="authoritative corpus is "
                                               "gitignored/local-only")
def test_real_corpus_register_boundaries_preserved():
    """The combined corpus must be byte-exactly the three register
    components assembled under the fixed plain-text headers (register
    boundaries preserved as established in Phase 2A)."""
    import sys
    sys.path.insert(0, str(SCRIPTS))
    import build_phase2a_corpus as builder
    register_texts = [p.read_text(encoding="utf-8")
                      for p in REGISTER_FILES.values()]
    combined = builder.assemble(register_texts)
    assert builder.sha256_bytes(combined.encode("utf-8")) == CORPUS_SHA


@pytest.mark.skipif(not _real_corpus(), reason="authoritative corpus is "
                                               "gitignored/local-only")
def test_real_corpus_selfeval_json_matches_disk():
    report_path = ROOT / "experiments" / "exp004-modelscreen" / "phase2a" \
        / "corpus-selfeval" / "corpus_selfeval.json"
    if not report_path.is_file():
        pytest.skip("corpus_selfeval.json not generated yet")
    import hashlib
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    by_id = {d["dataset_id"]: d for d in payload["datasets"]}
    assert by_id["combined"]["sha256"] == CORPUS_SHA
    for rid, path in REGISTER_FILES.items():
        assert by_id[rid]["sha256"] \
            == hashlib.sha256(path.read_bytes()).hexdigest()
    assert payload["corpus"]["sha256"] == CORPUS_SHA
