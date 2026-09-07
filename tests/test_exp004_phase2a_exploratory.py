"""EXP-004 Phase 2A — exploratory Dola 3.8 integration tests (SODA Task
021, 2026-09-07).

Covers the Task-021 integration for the two author-added exploratory
primed runs recorded as "Dola 3.8 — Fast" (run 20) and "Dola 3.8 — Pro"
(run 21):

- EXPLORATORY_ROWS exist, resolve through roster_entry(), and are NOT part
  of the 18-configuration ROSTER: `prepare` still emits exactly 36 planned
  runs / 54 manifest prompt files — the original preregistered protocol is
  untouched;
- extend-exploratory appends the two exploratory plan rows (no Phase-1
  baseline) and their four manifest entries idempotently, without
  regenerating any prompt file;
- collect-msg2 registers the raw reply appended after the closing
  '## Output' marker of the author's operator-prompts *-msg2.md file,
  byte-for-byte, records message-2-only provenance (no machine same-session
  transcript proof), refuses to overwrite an existing run and rejects a
  reply-less msg2 file;
- exploratory rows carry baseline_run_id None and _baseline_metrics()
  returns no-baseline, so `compare` never fabricates a priming effect for
  Dola (the two runs stay two distinct observations, never collapsed).
"""
import importlib.util
import json
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"

_SOURCE = (
    "Opowieść o Słów, Które Były Jak Siostry\n"
    "Prolog\n\n"
    "Bronisława, Teofil i Julianna živili v Międzyrzeczu. Przemysława "
    "prišla. Antoni molčal.\n" * 12 +
    "\nKONIEC\n"
)

# Synthetic three-register corpus carrying the three fingerprint anchors.
_CORPUS = (
    "=== REGISTER 1: LITERARY / NARRATIVE ===\n\n"
    "Ljudi govoret, že v tamtoj denj bylo je veliko spokojno.\n\n"
    "=== REGISTER 2: ARTISTIC / POETIC ===\n\n"
    "Toj korab znajut ljudi vsi\n\n"
    "=== REGISTER 3: INFORMATIVE / ENCYCLOPEDIC ===\n\n"
    "Sadovničstvo jest proces raščenja rastlin.\n"
)

_REPLY = (
    "Povědka o slovah, ktore byle kako sestry\n"
    "Prolog\n\n"
    "Bronisława, Teofil i Julianna živili v Medžurečju. Przemysława "
    "prišla k nih. Antoni molčal.\n"
    "\nKONEC\n"
)

ANCHORS = (
    "Ljudi govoret, že v tamtoj denj bylo je veliko spokojno",
    "Toj korab znajut ljudi vsi",
    "Sadovničstvo jest proces raščenja rastlin",
)
TRANSLATION_START = "Translate the Polish story below into Interslavic"

DATE = "2099-01-01"
DOLA_FAST = f"{DATE}__bytedance__dola-3.8__fast__p2a-primed"
DOLA_PRO = f"{DATE}__bytedance__dola-3.8__pro__p2a-primed"


@pytest.fixture(scope="module")
def run_mod():
    spec = importlib.util.spec_from_file_location(
        "run_exp004_phase2a_exploratory",
        SCRIPTS / "run_exp004_phase2a.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture()
def setup(run_mod, tmp_path, monkeypatch):
    """Temp Phase-2A experiment: synthetic source + synthetic corpus."""
    prompts = tmp_path / "operator-prompts"
    outputs = tmp_path / "outputs"
    prompts.mkdir()
    outputs.mkdir()
    src = tmp_path / "source.txt"
    src.write_text(_SOURCE, encoding="utf-8")
    corpus = tmp_path / "corpus.txt"
    corpus.write_text(_CORPUS, encoding="utf-8")

    monkeypatch.setattr(run_mod, "SOURCE_FILE", src)
    monkeypatch.setattr(
        run_mod, "SOURCE_SHA256",
        run_mod.sha256_bytes(_SOURCE.encode("utf-8")))
    monkeypatch.setattr(run_mod, "CORPUS_FILE", corpus)
    monkeypatch.setattr(
        run_mod, "AUTH_CORPUS_SHA256",
        run_mod.sha256_bytes(_CORPUS.encode("utf-8")))
    monkeypatch.setattr(run_mod, "OPERATOR_PROMPTS", prompts)
    monkeypatch.setattr(run_mod, "OUTPUTS_DIR", outputs)
    p1_outputs = tmp_path / "phase1-outputs"
    p1_outputs.mkdir()
    monkeypatch.setattr(run_mod.p1, "OUTPUTS_DIR", p1_outputs)
    return {"tmp": tmp_path, "prompts": prompts, "outputs": outputs,
            "p1_outputs": p1_outputs}


def prepare(run_mod, setup):
    assert run_mod.run_prepare(DATE) == 0
    return setup["outputs"] / "plan.json"


def write_dola_prompts(run_mod, setup):
    """Author-created exploratory prompt files (Task 021 shape)."""
    p = setup["prompts"]
    for run, version, nn in ((DOLA_FAST, "Fast", 20), (DOLA_PRO, "Pro", 21)):
        msg1 = p / f"primed-{nn}-dola-3.8-{version}-msg1.md"
        msg2 = p / f"primed-{nn}-dola-3.8-{version}-msg2.md"
        msg1.write_text(
            "# header\n\nCondition: primed — message 1 of 2\n\n"
            + _CORPUS, encoding="utf-8")
        msg2.write_text(
            "# header\n\n"
            f"{TRANSLATION_START}.\n\n{_SOURCE}\n"
            f"## Output\n\n{_REPLY}", encoding="utf-8")


def _author_msg2(run_mod, setup, row, reply, keep_boilerplate):
    """Rewrite the prepared msg2 prompt file of a roster row into the
    author's collected shape: canonical prompt + raw reply after the
    closing '## Output' marker. When keep_boilerplate is True the reply is
    appended after the canonical trailing 'Return the complete …'
    boilerplate (the collector must strip it); otherwise the boilerplate is
    replaced by the reply, exactly as the author's files are."""
    nn = run_mod.phase1_number(row)
    name = f"primed-{nn:02d}-{row['model']}-{row['model_version']}-msg2.md"
    path = setup["prompts"] / name
    canon = path.read_text(encoding="utf-8")
    boiler = ("Return the complete Interslavic translation of the source "
              "text, and nothing\nelse.\n")
    if keep_boilerplate:
        path.write_text(canon + reply, encoding="utf-8")
    else:
        assert canon.endswith(boiler)
        path.write_text(
            canon[: -len(boiler)] + reply, encoding="utf-8")
    return path


def row_for(run_mod, provider, model, version):
    return next(r for r in run_mod.ROSTER
                if r["provider"] == provider and r["model"] == model
                and r["model_version"] == version)


# ---------------------------------------------------------------------------
# exploratory roster: separate from the preregistered 18
# ---------------------------------------------------------------------------

def test_exploratory_rows_are_distinct_from_the_18_roster(run_mod, setup):
    assert len(run_mod.ROSTER) == 18
    assert len(run_mod.EXPLORATORY_ROWS) == 2
    assert all(r["exploratory"] is True for r in run_mod.EXPLORATORY_ROWS)
    assert [r["model_version"] for r in run_mod.EXPLORATORY_ROWS] == \
        ["fast", "pro"]
    assert all(r["model"] == "dola-3.8" and r["provider"] == "bytedance"
               for r in run_mod.EXPLORATORY_ROWS)
    # never merged: the 18-roster tuple set has no exploratory member
    base = {tuple(r[k] for k in ("provider", "model", "model_version"))
            for r in run_mod.ROSTER}
    assert not ({tuple(r[k] for k in ("provider", "model", "model_version"))
                 for r in run_mod.EXPLORATORY_ROWS} & base)


def test_roster_entry_resolves_exploratory_dola_rows(run_mod):
    row = run_mod.roster_entry(DOLA_FAST)
    assert row is not None and row["exploratory"] is True
    assert row["label"] == "Dola 3.8 — Fast"
    assert "not independently verifiable" in row["identity_note"].lower()
    assert run_mod.roster_entry(DOLA_PRO)["label"] == "Dola 3.8 — Pro"
    assert run_mod.roster_entry(f"{DATE}__openai__gpt-5.6-luna__"
                                "thinkoff__p2a-primed").get("exploratory") \
        is not True


def test_prepare_protocol_untouched_by_exploratory_rows(run_mod, setup):
    """extend-exploratory is explicit: prepare still emits the original
    36 runs / 54 manifest entries."""
    plan = json.loads(prepare(run_mod, setup).read_text(encoding="utf-8"))
    assert len(plan["runs"]) == 36
    manifest = json.loads(
        (setup["prompts"] / "manifest.json").read_text(encoding="utf-8"))
    assert len(manifest["files"]) == 54
    assert not any(r.get("exploratory") for r in plan["runs"])


# ---------------------------------------------------------------------------
# extend-exploratory
# ---------------------------------------------------------------------------

def test_extend_exploratory_appends_rows_idempotently(run_mod, setup):
    prepare(run_mod, setup)
    write_dola_prompts(run_mod, setup)
    assert run_mod.run_extend_exploratory(DATE) == 0
    plan = json.loads((setup["outputs"] / "plan.json").read_text(
        encoding="utf-8"))
    assert len(plan["runs"]) == 38
    dola = [r for r in plan["runs"] if r.get("exploratory")]
    assert len(dola) == 2
    assert {r["run_id"] for r in dola} == {DOLA_FAST, DOLA_PRO}
    for r in dola:
        assert r["condition"] == "p2a-primed"
        assert r["phase1_number"] is None
        assert r["baseline_run_id"] is None
        assert len(r["prompt_files"]) == 2
        assert r["prompt_files"][-1].endswith("-msg2.md")
        assert r["translation_prompt_sha256"]
    manifest = json.loads((setup["prompts"] / "manifest.json").read_text(
        encoding="utf-8"))
    assert len(manifest["files"]) == 58
    dola_files = [f for f in manifest["files"] if f.get("exploratory")]
    assert len(dola_files) == 4
    assert {f["message"] for f in dola_files} == {1, 2}
    # msg2 manifest entry hashes the prompt part only (reply excluded)
    fast_row = next(r for r in dola if r["run_id"] == DOLA_FAST)
    m2_entry = next(f for f in dola_files
                    if f["file"] == "primed-20-dola-3.8-Fast-msg2.md")
    assert m2_entry["prompt_sha256"] == \
        fast_row["translation_prompt_sha256"]
    # idempotent second call: no growth
    assert run_mod.run_extend_exploratory(DATE) == 0
    plan2 = json.loads((setup["outputs"] / "plan.json").read_text(
        encoding="utf-8"))
    manifest2 = json.loads((setup["prompts"] / "manifest.json").read_text(
        encoding="utf-8"))
    assert len(plan2["runs"]) == 38 and len(manifest2["files"]) == 58


def test_extend_exploratory_requires_author_prompt_files(run_mod, setup):
    prepare(run_mod, setup)
    assert run_mod.run_extend_exploratory(DATE) == 2  # no dola files yet
    plan = json.loads((setup["outputs"] / "plan.json").read_text(
        encoding="utf-8"))
    assert len(plan["runs"]) == 36  # nothing was appended


# ---------------------------------------------------------------------------
# collect-msg2 (author msg2 prompt+reply files)
# ---------------------------------------------------------------------------

def test_collect_msg2_extracts_reply_for_exploratory_run(run_mod, setup):
    prepare(run_mod, setup)
    write_dola_prompts(run_mod, setup)
    run_mod.run_extend_exploratory(DATE)
    rc = run_mod.run_collect_msg2(DOLA_FAST, generation_date=DATE)
    assert rc == 0
    out_dir = setup["outputs"] / DOLA_FAST
    assert (out_dir / "output.txt").read_bytes() == _REPLY.encode("utf-8")
    meta = json.loads((out_dir / "meta.json").read_text(encoding="utf-8"))
    assert meta["collected_by"] == \
        "scripts/run_exp004_phase2a.py collect-msg2"
    assert meta["output"]["sha256"] == run_mod.sha256_bytes(
        _REPLY.encode("utf-8"))
    assert meta["session"]["contamination_checks"]["machine_same_session_proof"] \
        is False
    assert meta["session"]["contamination_checks"][
        "corpus_in_msg1_prompt_file"] is True
    assert "message-2 only" in meta["session"]["record"]
    # refusing to overwrite
    assert run_mod.run_collect_msg2(DOLA_FAST, generation_date=DATE) == 2


def test_collect_msg2_original_run_author_shape_without_boilerplate(
        run_mod, setup):
    """Author msg2 file = canonical prompt + reply after '## Output'
    (canonical trailing boilerplate replaced by the reply)."""
    prepare(run_mod, setup)
    row = row_for(run_mod, "openai", "gpt-5.6-luna", "thinkoff")
    rid = run_mod.run_id_for(DATE, row, "p2a-primed")
    _author_msg2(run_mod, setup, row, _REPLY, keep_boilerplate=False)
    assert run_mod.run_collect_msg2(rid, generation_date=DATE) == 0
    out = (setup["outputs"] / rid / "output.txt").read_text(
        encoding="utf-8")
    assert out == _REPLY


def test_collect_msg2_strips_trailing_prompt_boilerplate(run_mod, setup):
    """Author msg2 file = canonical prompt (boilerplate retained) with the
    reply appended after it — the collector must strip the boilerplate."""
    prepare(run_mod, setup)
    row = row_for(run_mod, "openai", "gpt-5.6-luna", "thinkon")
    rid = run_mod.run_id_for(DATE, row, "p2a-primed")
    _author_msg2(run_mod, setup, row, _REPLY, keep_boilerplate=True)
    assert run_mod.run_collect_msg2(rid, generation_date=DATE) == 0
    out = (setup["outputs"] / rid / "output.txt").read_text(
        encoding="utf-8")
    assert out == _REPLY


def test_collect_msg2_rejects_replyless_msg2_file(run_mod, setup):
    prepare(run_mod, setup)
    row = row_for(run_mod, "deepseek", "deepseek-v3-instant",
                  "deepthinkoff")
    rid = run_mod.run_id_for(DATE, row, "p2a-primed")
    path = _author_msg2(run_mod, setup, row, "", keep_boilerplate=True)
    assert run_mod.run_collect_msg2(rid, generation_date=DATE) == 2
    assert not (setup["outputs"] / rid / "output.txt").exists()


def test_collect_msg2_refuses_control_run(run_mod, setup):
    prepare(run_mod, setup)
    row = row_for(run_mod, "openai", "gpt-5.6-luna", "thinkoff")
    rid = run_mod.run_id_for(DATE, row, "p2a-ctl")
    assert run_mod.run_collect_msg2(rid, generation_date=DATE) == 2


# ---------------------------------------------------------------------------
# no Phase-1 baseline for exploratory rows -> no priming-effect comparison
# ---------------------------------------------------------------------------

def test_baseline_metrics_is_none_for_exploratory_rows(run_mod, setup):
    prepare(run_mod, setup)
    plan = json.loads((setup["outputs"] / "plan.json").read_text(
        encoding="utf-8"))
    row = {"run_id": DOLA_FAST, "baseline_run_id": None,
           "condition": "p2a-primed"}
    bm, source = run_mod._baseline_metrics(row)
    assert bm is None and source == "no-baseline"


def test_compare_does_not_crash_and_never_claims_baseline_for_dola(
        run_mod, setup):
    prepare(run_mod, setup)
    write_dola_prompts(run_mod, setup)
    run_mod.run_extend_exploratory(DATE)
    # no run evaluated, empty phase-1 outputs -> every primed row is an
    # error row, including Dola (no baseline fabricated)
    assert run_mod.run_compare() == 0
    cmp_data = json.loads((setup["outputs"] / "compare.json").read_text(
        encoding="utf-8"))
    ids = {r["run_id"] for r in cmp_data["rows"]}
    assert DOLA_FAST in ids and DOLA_PRO in ids
    for r in cmp_data["rows"]:
        if r["run_id"] == DOLA_FAST:
            assert r["baseline_run_id"] is None
            assert "baseline" in r["error"].lower() or \
                "evaluated" in r["error"].lower()
