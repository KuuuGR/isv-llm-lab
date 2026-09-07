"""EXP-004 — exploratory Dola 3.8 Phase-1 DIRECT baseline tests (SODA Task
022, 2026-09-07).

Covers the retrospective preparation of Phase-1 direct baselines for the
two author-added exploratory Dola 3.8 configurations (run 20 = Fast,
run 21 = Pro) whose Phase-2A primed runs were integrated in Task 021:

- the exploratory direct rows exist on the Phase-1 side, are NOT part of
  the reconciled 19-row ROSTER, and are consistent with the Phase-2A
  EXPLORATORY_ROWS (same provider/model/version/label/identity note);
- extend-direct renders two operator prompts with the canonical Phase-1
  direct structure: exact Polish source story + the established
  direct-translation instruction, distinct Dola configuration metadata,
  NO corpus / no scaffold / no dictionary / no morphology content, and no
  linkage to the Phase-2A primed prompts;
- extend-direct marks the rows pending_manual_collection in plan + manifest
  (idempotent) and never creates a false completed baseline (no output
  dir, no meta.json, no metrics);
- once the author executes a baseline, the existing Phase-1
  collect-session / verify pipeline registers and gates it;
- link-baselines pairs each Dola p2a-primed plan row's baseline_run_id
  with its direct run id (idempotent, requires the Phase-1 rows), and
  compare reports the baseline as pending until collected; after
  collection + evaluation the same deterministic pipeline reports the
  within-Dola Phase 1 → Phase 2A deltas;
- the original 18 Phase-1 baselines and the preregistered protocol are
  untouched.
"""
import importlib.util
import json
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
ROOT = SCRIPTS.parent

_SOURCE = (
    "Opowieść o Słów, Które Były Jak Siostry\n"
    "Prolog\n\n"
    "Bronisława, Teofil i Julianna živili v Międzyrzeczu. Przemysława "
    "prišla. Antoni molčal.\n" * 12 +
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

_REPLY = (
    "Povědka o slovah, ktore byle kako sestry\n"
    "Prolog\n\n"
    + ("Bronisława, Teofil i Julianna živili v Medžurečju. Przemysława "
       "prišla k nih. Antoni molčal.\n") * 200
    + "\nKONIEC\n"
)

ANCHORS = (
    "Ljudi govoret, že v tamtoj denj bylo je veliko spokojno",
    "Toj korab znajut ljudi vsi",
    "Sadovničstvo jest proces raščenja rastlin",
)
TRANSLATION_START = "Translate the Polish story below into Interslavic"
DATE = "2099-01-01"
DOLA_FAST_DIRECT = f"{DATE}__bytedance__dola-3.8__fast__direct"
DOLA_PRO_DIRECT = f"{DATE}__bytedance__dola-3.8__pro__direct"
DOLA_FAST_PRIMED = f"{DATE}__bytedance__dola-3.8__fast__p2a-primed"
DOLA_PRO_PRIMED = f"{DATE}__bytedance__dola-3.8__pro__p2a-primed"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def p2a_mod():
    """Phase-2A module. Its internal `import run_exp004_phase1 as p1` binds
    the canonical sys.modules instance, which is the object we patch for the
    Phase-1 side too (single shared instance)."""
    mod = _load("run_exp004_phase2a_t022", SCRIPTS / "run_exp004_phase2a.py")
    # the plain import inside the module must resolve to the same object
    # that later code manipulates via mod.p1
    assert mod.p1.__name__ == "run_exp004_phase1"
    sys.modules.setdefault("run_exp004_phase1", mod.p1)
    return mod


@pytest.fixture()
def kit(p2a_mod, tmp_path, monkeypatch):
    """Temp Phase-1 + Phase-2A kits with synthetic source + synthetic
    three-register corpus; both modules point into tmp_path."""
    p1 = p2a_mod.p1
    exp1 = tmp_path / "phase1"
    inp1 = exp1 / "input"
    pr1 = exp1 / "operator-prompts"
    out1 = exp1 / "outputs"
    for d in (inp1, pr1, out1):
        d.mkdir(parents=True)
    src1 = inp1 / "source.txt"
    src1.write_text(_SOURCE, encoding="utf-8")
    monkeypatch.setattr(p1, "EXP", exp1)
    monkeypatch.setattr(p1, "INPUT_DIR", inp1)
    monkeypatch.setattr(p1, "OPERATOR_PROMPTS", pr1)
    monkeypatch.setattr(p1, "OUTPUTS_DIR", out1)
    monkeypatch.setattr(p1, "EXP003_SOURCE", src1)
    monkeypatch.setattr(
        p1, "EXP003_SOURCE_SHA256",
        p1.sha256_bytes(_SOURCE.encode("utf-8")))
    monkeypatch.setattr(
        p1, "BASE_INSTRUCTION",
        ROOT / "experiments" / "exp004-modelscreen" / "base_instruction.txt")

    pr2 = tmp_path / "p2a-prompts"
    out2 = tmp_path / "p2a-outputs"
    pr2.mkdir()
    out2.mkdir()
    src2 = tmp_path / "p2a-source.txt"
    src2.write_text(_SOURCE, encoding="utf-8")
    corpus = tmp_path / "corpus.txt"
    corpus.write_text(_CORPUS, encoding="utf-8")
    monkeypatch.setattr(p2a_mod, "SOURCE_FILE", src2)
    monkeypatch.setattr(
        p2a_mod, "SOURCE_SHA256",
        p2a_mod.sha256_bytes(_SOURCE.encode("utf-8")))
    monkeypatch.setattr(p2a_mod, "CORPUS_FILE", corpus)
    monkeypatch.setattr(
        p2a_mod, "AUTH_CORPUS_SHA256",
        p2a_mod.sha256_bytes(_CORPUS.encode("utf-8")))
    monkeypatch.setattr(p2a_mod, "OPERATOR_PROMPTS", pr2)
    monkeypatch.setattr(p2a_mod, "OUTPUTS_DIR", out2)
    return {"p1": p1, "p2a": p2a_mod, "phase1_prompts": pr1,
            "phase1_outputs": out1, "p2a_prompts": pr2, "p2a_outputs": out2}


def phase1_prepare(kit, date=DATE):
    assert kit["p1"].run_prepare(date) == 0
    return kit["phase1_outputs"] / "plan.json"


def phase2a_prepare_and_extend(kit, date=DATE):
    """Phase-2A prepare (36 rows) + author Dola msg1/msg2 prompt files +
    extend-exploratory (38 rows)."""
    p2a = kit["p2a"]
    assert p2a.run_prepare(date) == 0
    for run_id, version, nn in ((DOLA_FAST_PRIMED, "Fast", 20),
                                (DOLA_PRO_PRIMED, "Pro", 21)):
        p = kit["p2a_prompts"]
        (p / f"primed-{nn}-dola-3.8-{version}-msg1.md").write_text(
            "# header\n\nCondition: primed — message 1 of 2\n\n"
            + _CORPUS, encoding="utf-8")
        (p / f"primed-{nn}-dola-3.8-{version}-msg2.md").write_text(
            "# header\n\n" + TRANSLATION_START + ".\n\n" + _SOURCE
            + f"\n## Output\n\n{_REPLY}", encoding="utf-8")
    assert p2a.run_extend_exploratory(date) == 0


def body_after_header(prompt_text: str) -> str:
    """Instruction+source body of a Phase-1 direct prompt: everything after
    the second '---' separator (mirrors tests/test_exp004_phase1.py)."""
    return "\n---\n".join(prompt_text.split("\n---\n")[2:])


# ---------------------------------------------------------------------------
# exploratory direct rows are separate + consistent across modules
# ---------------------------------------------------------------------------

def test_direct_exploratory_rows_separate_and_consistent(kit):
    p1 = kit["p1"]
    p2a = kit["p2a"]
    assert len(p1.ROSTER) == 19  # reconciled executed roster untouched
    assert len(p1.DIRECT_EXPLORATORY_ROWS) == 2
    assert len(p2a.ROSTER) == 18
    assert len(p2a.EXPLORATORY_ROWS) == 2
    assert all(r["exploratory"] is True
               for r in p1.DIRECT_EXPLORATORY_ROWS)
    assert [r["model_version"] for r in p1.DIRECT_EXPLORATORY_ROWS] == \
        ["fast", "pro"]
    assert [r["run_number"] for r in p1.DIRECT_EXPLORATORY_ROWS] == [20, 21]
    # never merged into the reconciled Phase-1 roster
    base = {tuple(r[k] for k in ("provider", "model", "model_version"))
            for r in p1.ROSTER}
    assert not ({tuple(r[k] for k in ("provider", "model", "model_version"))
                 for r in p1.DIRECT_EXPLORATORY_ROWS} & base)
    # consistent with the Phase-2A exploratory primed rows
    for drow, prow in zip(p1.DIRECT_EXPLORATORY_ROWS,
                          p2a.EXPLORATORY_ROWS):
        for key in ("provider", "model", "model_version", "label",
                    "interface", "generation_parameters"):
            assert drow[key] == prow[key]
        assert drow["identity_note"] == prow["identity_note"]
    # roster_entry resolves the direct ids (Phase-1 machinery)
    fast = p1.roster_entry(DOLA_FAST_DIRECT)
    assert fast is not None and fast["exploratory"] is True
    assert fast["label"] == "Dola 3.8 — Fast"
    assert "not independently verifiable" in fast["identity_note"].lower()
    assert p1.roster_entry(DOLA_PRO_DIRECT)["label"] == "Dola 3.8 — Pro"


# ---------------------------------------------------------------------------
# extend-direct: clean canonical direct prompts, pending rows
# ---------------------------------------------------------------------------

def test_extend_direct_renders_two_clean_canonical_prompts(kit):
    p1 = kit["p1"]
    plan = json.loads(phase1_prepare(kit).read_text(encoding="utf-8"))
    # canonical bodies of the original prepared rows
    orig_body = None
    for r in plan["runs"]:
        pf = kit["phase1_prompts"] / Path(r["prompt_file"]).name
        body = body_after_header(pf.read_text(encoding="utf-8"))
        orig_body = body if orig_body is None else orig_body
        assert body == orig_body  # all 19 identical instruction+source
    assert p1.run_extend_direct(DATE) == 0
    p1_prompts = kit["phase1_prompts"]
    for row, fname in ((p1.DIRECT_EXPLORATORY_ROWS[0],
                        "20-dola-3.8-fast.md"),
                       (p1.DIRECT_EXPLORATORY_ROWS[1],
                        "21-dola-3.8-pro.md")):
        path = p1_prompts / fname
        assert path.is_file()
        text = path.read_text(encoding="utf-8")
        # established direct-translation instruction + exact Polish source
        assert TRANSLATION_START in text
        story = text.split("## Source text (Polish)", 1)[1]
        story = story.split("## Output", 1)[0].strip("\n")
        assert story == _SOURCE.strip("\n")
        # canonical Phase-1 body is byte-identical to the original rows
        assert body_after_header(text) == orig_body
        # distinct Dola configuration metadata in the header
        assert f"Target model: {row['label']}" in text
        assert row["model_version"] in text
        assert "Condition: direct" in text
        # NO corpus / priming / msg2 content anywhere
        for anchor in ANCHORS:
            assert anchor not in text
        assert "REGISTER 1" not in text and "REGISTER 2" not in text
        assert "REGISTER 3" not in text
        assert "msg1" not in text and "msg2" not in text
        assert "Using the authentic Medžuslovjansky text" not in text
        assert text.count("## Output") == 1  # only the prompt's own marker
        # direct-only wording (no corpus scaffolding, no lexicon) in body
        rules = text.split("## Rules")[1].split("## Source text")[0].lower()
        assert "scaffold" not in rules and "candidate" not in rules
        assert "dictionary" not in rules and "morphology" not in rules
        # manifest entry hash matches the file bytes
        manifest = json.loads(
            (kit["phase1_prompts"] / "manifest.json").read_text(
                encoding="utf-8"))
        entry = next(f for f in manifest["files"] if f["file"] == fname)
        assert entry["exploratory"] is True
        assert entry["prompt_sha256"] == p1.sha256_bytes(
            text.encode("utf-8"))


def test_extend_direct_marks_pending_and_never_fabricates(kit):
    p1 = kit["p1"]
    plan_path = phase1_prepare(kit)
    plan_before = json.loads(plan_path.read_text(encoding="utf-8"))
    assert len(plan_before["runs"]) == 19
    assert p1.run_extend_direct(DATE) == 0
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    assert len(plan["runs"]) == 21
    # original 19 rows byte-identical (unchanged)
    assert plan["runs"][:19] == plan_before["runs"]
    dola = [r for r in plan["runs"] if r.get("exploratory")]
    assert {r["run_id"] for r in dola} == {DOLA_FAST_DIRECT, DOLA_PRO_DIRECT}
    for r in dola:
        assert r["condition"] == "direct"
        assert r["status"] == "pending_manual_collection"
        assert r["prompt_sha256"]
        # no false completed baseline: nothing collected/evaluated
        out_dir = kit["phase1_outputs"] / r["run_id"]
        assert not (out_dir / "output.txt").exists()
        assert not (out_dir / "meta.json").exists()
        assert not (out_dir / "evaluation.json").exists()
    manifest = json.loads((kit["phase1_prompts"] / "manifest.json")
                          .read_text(encoding="utf-8"))
    assert len(manifest["files"]) == 21
    dola_files = [f for f in manifest["files"] if f.get("exploratory")]
    assert {f["file"] for f in dola_files} == \
        {"20-dola-3.8-fast.md", "21-dola-3.8-pro.md"}
    # roster shows the two rows as not collected
    assert p1.run_roster() == 0
    roster = json.loads((kit["phase1_outputs"] / "roster.json")
                        .read_text(encoding="utf-8"))
    assert len(roster["rows"]) == 21
    for row in roster["rows"]:
        if row["run_id"] in (DOLA_FAST_DIRECT, DOLA_PRO_DIRECT):
            assert row["collected"] is False
            assert row["intake_verdict"] is None
            assert row["metrics"] is None
    # idempotent second call: no growth, files unchanged
    snap = {p.name: p.read_bytes()
            for p in kit["phase1_prompts"].glob("*.md")}
    assert p1.run_extend_direct(DATE) == 0
    plan2 = json.loads(plan_path.read_text(encoding="utf-8"))
    manifest2 = json.loads((kit["phase1_prompts"] / "manifest.json")
                           .read_text(encoding="utf-8"))
    assert len(plan2["runs"]) == 21 and len(manifest2["files"]) == 21
    assert {p.name: p.read_bytes()
            for p in kit["phase1_prompts"].glob("*.md")} == snap


def test_extend_direct_requires_existing_phase1_plan(kit):
    p1 = kit["p1"]
    assert p1.run_extend_direct(DATE) == 2  # no plan yet
    assert not (kit["phase1_prompts"] / "20-dola-3.8-fast.md").exists()


# ---------------------------------------------------------------------------
# after author execution: the existing Phase-1 pipeline collects the runs
# ---------------------------------------------------------------------------

def test_phase1_collect_session_registers_dola_direct_baseline(kit):
    p1 = kit["p1"]
    phase1_prepare(kit)
    assert p1.run_extend_direct(DATE) == 0
    # simulate the author's session file: canonical prompt (final two lines
    # replaced) + raw reply appended after '## Output'
    pf = kit["phase1_prompts"] / "20-dola-3.8-fast.md"
    canon = pf.read_text(encoding="utf-8")
    cut = canon.rfind("Return the complete")
    session = kit["phase1_prompts"] / "20-dola-3.8-Fast-session.md"
    session.write_bytes(canon[:cut].encode("utf-8") + _REPLY.encode("utf-8"))
    rc = p1.run_collect_session(
        DOLA_FAST_DIRECT, session, DATE, "unknown", "unknown", "unknown",
        "unknown", "collected_external_output", "pass",
        "complete in one free session", "")
    assert rc == 0
    out_dir = kit["phase1_outputs"] / DOLA_FAST_DIRECT
    assert (out_dir / "output.txt").read_text(encoding="utf-8") == _REPLY
    meta = json.loads((out_dir / "meta.json").read_text(encoding="utf-8"))
    assert meta["condition"] == "direct"
    assert meta["label"] == "Dola 3.8 — Fast"
    assert meta["provider"] == "bytedance"
    # verify runs the completeness gate -> complete
    assert p1.run_verify(DOLA_FAST_DIRECT) == 0
    intake = json.loads((out_dir / "intake.json").read_text(
        encoding="utf-8"))
    assert intake["verdict"] == "complete"
    # tampered instruction body refused (clean-baseline invariant)
    bad = canon[:cut].encode("utf-8").replace(
        TRANSLATION_START.encode("utf-8"),
        b"Translate the Polish fable below into Interslavic") \
        + _REPLY.encode("utf-8")
    (kit["phase1_prompts"] / "20-dola-3.8-Fast-bad.md").write_bytes(bad)
    assert p1.run_collect_session(
        DOLA_FAST_DIRECT,
        kit["phase1_prompts"] / "20-dola-3.8-Fast-bad.md",
        DATE, "unknown", "unknown", "unknown") == 2


# ---------------------------------------------------------------------------
# link-baselines: unambiguous pairing with the Dola Phase-2A runs 20/21
# ---------------------------------------------------------------------------

def test_link_baselines_pairs_direct_ids_with_primed_rows(kit):
    p1 = kit["p1"]
    p2a = kit["p2a"]
    phase2a_prepare_and_extend(kit)
    # refuses before the Phase-1 direct rows exist
    assert p2a.run_link_baselines(DATE) == 2
    phase1_prepare(kit)
    assert p1.run_extend_direct(DATE) == 0
    assert p2a.run_link_baselines(DATE) == 0
    plan = json.loads((kit["p2a_outputs"] / "plan.json").read_text(
        encoding="utf-8"))
    dola = {r["run_id"]: r for r in plan["runs"] if r.get("exploratory")}
    assert dola[DOLA_FAST_PRIMED]["baseline_run_id"] == DOLA_FAST_DIRECT
    assert dola[DOLA_PRO_PRIMED]["baseline_run_id"] == DOLA_PRO_DIRECT
    assert dola[DOLA_FAST_PRIMED]["baseline_status"] == "pending_collection"
    assert dola[DOLA_FAST_PRIMED]["baseline_task"] == "022"
    # the 18 preregistered configurations' baselines are untouched
    for r in plan["runs"]:
        if not r.get("exploratory"):
            assert r["baseline_run_id"] and \
                r["baseline_run_id"].endswith("__direct")
    # collected Phase-2A outputs/meta of Task 021 are untouched
    for rid in (DOLA_FAST_PRIMED, DOLA_PRO_PRIMED):
        assert not (kit["p2a_outputs"] / rid / "meta.json").exists()
    # idempotent second call: no growth, no relink
    assert p2a.run_link_baselines(DATE) == 0
    plan2 = json.loads((kit["p2a_outputs"] / "plan.json").read_text(
        encoding="utf-8"))
    assert len(plan2["runs"]) == len(plan["runs"])
    assert {r["run_id"]: r["baseline_run_id"] for r in plan2["runs"]} == \
        {r["run_id"]: r["baseline_run_id"] for r in plan["runs"]}


# ---------------------------------------------------------------------------
# compare: pending until collected, real deltas afterwards
# ---------------------------------------------------------------------------

_METRICS = {
    "total_tokens": 1000,
    "canonical_supported_tokens": 800,
    "canonical_coverage": 0.7,
    "broader_resource_supported_tokens": 900,
    "broader_resource_supported_coverage": 0.8,
    "unresolved_tokens": 200,
    "unresolved_rate": 0.2,
    "exact_dictionary_matches": 700,
    "morphologically_valid_forms": 100,
}
_PRIMED_METRICS = dict(_METRICS, canonical_coverage=0.9,
                       broader_resource_supported_coverage=0.95,
                       unresolved_rate=0.1, total_tokens=1100,
                       exact_dictionary_matches=800,
                       morphologically_valid_forms=150)


def _fake_eval(monkeypatch, mod):
    """Fake the isv-eval subprocess for p1.run_evaluate; every other
    subprocess call (e.g. git_commit) falls through to the real runner."""
    import subprocess as sp
    real_run = sp.run

    def fake(cmd, **kw):
        if "--out" not in cmd:
            return real_run(cmd, **kw)
        out_dir_arg = Path(cmd[cmd.index("--out") + 1])
        out_dir_arg.mkdir(parents=True, exist_ok=True)
        (out_dir_arg / "report.json").write_text(json.dumps({
            "evaluator": {"name": "isv-eval", "version": "0.0.0"},
            "metrics": _METRICS,
            "output_files": {}}, ensure_ascii=False), encoding="utf-8")
        return sp.CompletedProcess(cmd, 0, "", "")
    monkeypatch.setattr(sp, "run", fake)


def test_compare_reports_pending_then_delta_after_collection(
        kit, monkeypatch):
    p1 = kit["p1"]
    p2a = kit["p2a"]
    phase1_prepare(kit)
    assert p1.run_extend_direct(DATE) == 0
    phase2a_prepare_and_extend(kit)
    assert p2a.run_link_baselines(DATE) == 0
    # the Task-021 Dola primed runs are already collected + evaluated in the
    # real kit; simulate that here so compare reaches its baseline handling
    for rid in (DOLA_FAST_PRIMED, DOLA_PRO_PRIMED):
        fast_dir = kit["p2a_outputs"] / rid
        fast_dir.mkdir(parents=True, exist_ok=True)
        (fast_dir / "intake.json").write_text(json.dumps(
            {"verdict": "complete"}, ensure_ascii=False, indent=2),
            encoding="utf-8")
        (fast_dir / "evaluation.json").write_text(json.dumps({
            "run_id": rid, "usable": True,
            "metrics": _PRIMED_METRICS}, ensure_ascii=False, indent=2),
            encoding="utf-8")
    # compare: Dola rows carry their direct baseline ids and are reported as
    # pending — no fabricated deltas
    assert p2a.run_compare() == 0
    cmp_data = json.loads((kit["p2a_outputs"] / "compare.json").read_text(
        encoding="utf-8"))
    rows = {r["run_id"]: r for r in cmp_data["rows"]}
    for rid in (DOLA_FAST_PRIMED, DOLA_PRO_PRIMED):
        row = rows[rid]
        assert row["baseline_run_id"] == (DOLA_FAST_DIRECT if "fast" in rid
                                          else DOLA_PRO_DIRECT)
        assert "error" in row and "deltas" not in row
        assert "pending" in row["error"]
        assert DOLA_FAST_DIRECT in row["error"] or \
            DOLA_PRO_DIRECT in row["error"]
    # simulate the author execution + collection + evaluation of the Fast
    # direct baseline through the existing Phase-1 pipeline
    pf = kit["phase1_prompts"] / "20-dola-3.8-fast.md"
    canon = pf.read_text(encoding="utf-8")
    cut = canon.rfind("Return the complete")
    session = kit["phase1_prompts"] / "20-dola-3.8-Fast-session.md"
    session.write_bytes(canon[:cut].encode("utf-8") + _REPLY.encode("utf-8"))
    assert p1.run_collect_session(
        DOLA_FAST_DIRECT, session, DATE, "unknown", "unknown", "unknown",
        "unknown", "collected_external_output", "pass",
        "complete in one free session", "") == 0
    assert p1.run_verify(DOLA_FAST_DIRECT) == 0
    _fake_eval(monkeypatch, p1)
    assert p1.run_evaluate(DOLA_FAST_DIRECT) == 0
    # compare now reports the within-Dola Phase 1 → Phase 2A deltas
    assert p2a.run_compare() == 0
    cmp2 = json.loads((kit["p2a_outputs"] / "compare.json").read_text(
        encoding="utf-8"))
    rows2 = {r["run_id"]: r for r in cmp2["rows"]}
    fast = rows2[DOLA_FAST_PRIMED]
    assert "deltas" in fast and "error" not in fast
    assert fast["baseline_source"] == "phase1-baseline"
    assert fast["baseline_run_id"] == DOLA_FAST_DIRECT
    assert abs(fast["deltas"]["canonical_coverage_pp"] - 0.2) < 1e-9
    assert abs(fast["deltas"]["unresolved_rate_pp"] + 0.1) < 1e-9
    assert fast["deltas"]["lexical_tokens"] == 100
    # Pro baseline still pending (not collected) — nothing fabricated
    pro = rows2[DOLA_PRO_PRIMED]
    assert "error" in pro and "pending" in pro["error"]
    assert pro["baseline_run_id"] == DOLA_PRO_DIRECT
