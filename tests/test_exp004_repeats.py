"""EXP-004 Phase repeat — controlled repeated generation tests (SODA Task
025).

Covers the deterministic repeats kit:
- prepare: exactly 18 primary configurations × direct/primed × r01..r03 =
  108 primary planned runs, plus 12 exploratory Dola runs (2 × 2 × 3);
  unique deterministic run ids (6-field scheme), 180 prompt files, prompt
  manifest hashes matching on-disk bytes, source/corpus SHA-256 gating
  (fail loudly on byte drift), byte-identical regenerate;
- replicate discipline: the three replicate prompt files of a
  (configuration, condition) are byte-identical BY DESIGN (the model must
  not be able to tell replicates apart); run ids differ only in the
  replicate field;
- prompt fidelity: direct prompt body == Phase-1 direct instruction body;
  primed msg1 body == Phase-2A study instruction + corpus verbatim; msg2
  body == Phase-2A translation task (through the '## Output' marker);
- collection: collect-session (standalone session / msg2-style prompt-file
  record) with direct contamination rejection and primed
  corpus-before-translation requirement; collect-msg2 (primed only);
  never overwrite; unknown runs rejected;
- verify/evaluate: completeness gate verdicts preserved as data; failed
  intake refuses evaluation (isv-eval subprocess faked);
- analysis: deterministic small-sample statistics, exact deltas, no Dola
  contamination of primary statistics, byte-identical chart regeneration.
"""
import importlib.util
import json
import subprocess
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
ROOT = SCRIPTS.parent

DATE = "2099-01-01"
RUN_DIR = f"{DATE}__anthropic__claude__sonnet-5__direct__r01"
RUN_P1 = f"{DATE}__anthropic__claude__sonnet-5__primed__r01"

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


@pytest.fixture(scope="module")
def run_mod():
    spec = importlib.util.spec_from_file_location(
        "run_exp004_repeats", SCRIPTS / "run_exp004_repeats.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def ana_mod():
    spec = importlib.util.spec_from_file_location(
        "analyze_exp004_repeats", SCRIPTS / "analyze_exp004_repeats.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture()
def setup(run_mod, tmp_path, monkeypatch):
    """Temp repeat kit: synthetic source + synthetic corpus, real roster."""
    exp = tmp_path / "exp004"
    repeats = exp / "repeats"
    prompts = repeats / "operator-prompts"
    outputs = repeats / "outputs"
    inp = exp / "input"
    inp.mkdir(parents=True)
    prompts.mkdir(parents=True)
    outputs.mkdir(parents=True)
    src = inp / "source.txt"
    src.write_text(_SOURCE, encoding="utf-8")
    corpus = tmp_path / "corpus.txt"
    corpus.write_text(_CORPUS, encoding="utf-8")

    monkeypatch.setattr(run_mod, "REPEATS", repeats)
    monkeypatch.setattr(run_mod, "OPERATOR_PROMPTS", prompts)
    monkeypatch.setattr(run_mod, "OUTPUTS_DIR", outputs)
    monkeypatch.setattr(run_mod, "EXP", exp)
    monkeypatch.setattr(
        run_mod, "SOURCE_SHA256",
        run_mod.sha256_bytes(_SOURCE.encode("utf-8")))
    monkeypatch.setattr(
        run_mod, "AUTH_CORPUS_SHA256",
        run_mod.sha256_bytes(_CORPUS.encode("utf-8")))
    # keep legacy lookups deterministic: empty p1/p2a plans
    p1_out = tmp_path / "p1-outputs"
    p1_out.mkdir()
    p2a_out = tmp_path / "p2a-outputs"
    p2a_out.mkdir()
    monkeypatch.setattr(run_mod.p1, "OUTPUTS_DIR", p1_out)
    monkeypatch.setattr(run_mod.p2a, "OUTPUTS_DIR", p2a_out)
    monkeypatch.setattr(run_mod.p2a, "CORPUS_FILE", corpus)
    return {"exp": exp, "repeats": repeats, "prompts": prompts,
            "outputs": outputs, "source": src, "corpus": corpus}


def prepare(run_mod, setup, force=False):
    rc = run_mod.run_prepare(DATE, force)
    assert rc == 0
    return setup["outputs"] / "plan.json"


# ---------------------------------------------------------------------------
# prepare
# ---------------------------------------------------------------------------

def test_prepare_108_primary_plus_12_exploratory(run_mod, setup):
    plan = json.loads(prepare(run_mod, setup).read_text(encoding="utf-8"))
    c = plan["counts"]
    assert c == {"primary_configurations": 18,
                 "exploratory_configurations": 2,
                 "runs_per_configuration_per_condition": 3,
                 "primary_runs": 108, "exploratory_runs": 12,
                 "total_runs": 120}
    runs = plan["runs"]
    assert len(runs) == 120
    assert len({r["run_id"] for r in runs}) == 120
    prim = [r for r in runs if r["primary"]]
    expl = [r for r in runs if not r["primary"]]
    assert len(prim) == 108 and len(expl) == 12
    assert {r["condition"] for r in runs} == {"direct", "primed"}
    assert {r["replicate"] for r in runs} == {"r01", "r02", "r03"}
    # block ordering: r01 direct+primed, r02, r03 per configuration
    claude = [r for r in prim
              if r["model"] == "claude"
              and r["model_version"] == "sonnet-5"]
    assert [(r["replicate"], r["condition"]) for r in claude] == [
        ("r01", "direct"), ("r01", "primed"), ("r02", "direct"),
        ("r02", "primed"), ("r03", "direct"), ("r03", "primed")]
    # exactly 18 primary configurations, GLM excluded
    assert len({(r["provider"], r["model"], r["model_version"])
                for r in prim}) == 18
    assert all(r["model"] != "glm" for r in prim)
    # Dola exploratory configs only
    assert {r["model_version"] for r in expl} == {"fast", "pro"}
    assert {r["model"] for r in expl} == {"dola-3.8"}
    assert all(r["exploratory"] and not r["primary"] for r in expl)
    # every primary run has exactly 1 direct / 2 primed prompt files
    for r in runs:
        if r["condition"] == "direct":
            assert len(r["prompt_files"]) == 1
        else:
            assert len(r["prompt_files"]) == 2
            assert all(f.endswith(("-msg1.md", "-msg2.md"))
                       for f in r["prompt_files"])


def test_run_ids_six_field_scheme_and_no_confusion(run_mod, setup):
    prepare(run_mod, setup)
    plan = json.loads((setup["outputs"] / "plan.json").read_text(
        encoding="utf-8"))
    for r in plan["runs"]:
        parts = run_mod.parse_run_id(r["run_id"])
        assert parts["date"] == DATE
        assert parts["condition"] in ("direct", "primed")
        assert parts["replicate"] in ("r01", "r02", "r03")
    # canonical 6-field ids must NOT parse under the Phase-1 (5-field)
    # or Phase-2A parsers — identities can never be confused.
    with pytest.raises(ValueError):
        run_mod.p1.parse_run_id(plan["runs"][0]["run_id"])
    with pytest.raises(ValueError):
        run_mod.p2a.parse_run_id(plan["runs"][0]["run_id"])
    # and repeat parser rejects Phase-1/2A ids
    with pytest.raises(ValueError):
        run_mod.parse_run_id(
            "2026-09-06__anthropic__claude__sonnet-5__direct")
    with pytest.raises(ValueError):
        run_mod.parse_run_id(
            "2026-09-07__anthropic__claude__sonnet-5__p2a-primed")


def test_prepare_prompt_manifest_and_hashes(run_mod, setup):
    prepare(run_mod, setup)
    man = json.loads((setup["prompts"] / "manifest.json").read_text(
        encoding="utf-8"))
    assert len(man["files"]) == 180
    plan = json.loads((setup["outputs"] / "plan.json").read_text(
        encoding="utf-8"))
    run_ids_in_plan = {r["run_id"] for r in plan["runs"]}
    run_ids_in_manifest = {f["run_id"] for f in man["files"]}
    assert run_ids_in_manifest == run_ids_in_plan
    assert {f["condition"] for f in man["files"]} == {"direct", "primed"}
    assert {f["replicate"] for f in man["files"]} == {"r01", "r02", "r03"}
    for f in man["files"]:
        p = setup["prompts"] / f["file"]
        assert p.is_file()
        assert run_mod.sha256_bytes(p.read_bytes()) == f["prompt_sha256"]
    # plan hashes match the on-disk translation prompts and pinned source
    for r in plan["runs"]:
        last = setup["prompts"] / r["prompt_files"][-1]
        assert run_mod.sha256_bytes(
            last.read_bytes()) == r["translation_prompt_sha256"]
        assert r["source_sha256"] == run_mod.SOURCE_SHA256
        if r["condition"] == "primed":
            assert r["corpus_sha256"] == run_mod.AUTH_CORPUS_SHA256
        else:
            assert r["corpus_sha256"] is None


def test_prepare_deterministic_regeneration(run_mod, setup):
    prepare(run_mod, setup)
    snap = {}
    for p in setup["prompts"].glob("*.md"):
        snap[p.name] = p.read_bytes()
    plan1 = (setup["outputs"] / "plan.json").read_bytes()
    checklist1 = (setup["outputs"] / "collection-checklist.md").read_bytes()
    prepare(run_mod, setup, force=True)
    for p in setup["prompts"].glob("*.md"):
        assert p.read_bytes() == snap[p.name]
    assert (setup["outputs"] / "plan.json").read_bytes() == plan1
    assert (setup["outputs"] / "collection-checklist.md").read_bytes() \
        == checklist1


def test_prepare_refuses_existing_plan_without_force(run_mod, setup):
    prepare(run_mod, setup)
    assert run_mod.run_prepare(DATE) == 2  # exists, no --force


def test_replicate_prompt_files_byte_identical_by_design(run_mod, setup):
    """The model must not be able to tell replicates apart: contents of
    r01/r02/r03 are byte-identical for every (config, condition, message)."""
    prepare(run_mod, setup)
    import re
    from collections import defaultdict
    groups = defaultdict(set)
    for p in setup["prompts"].glob("*.md"):
        m = re.match(r"^(direct|primed)-(\d+)-(.+?)-(r0[123])"
                     r"(?:-(msg[12]))?\.md$", p.name)
        assert m, p.name
        cond, nn, model, rep, msg = m.groups()
        groups[(cond, nn, model, msg)].add(p.read_bytes())
    assert len(groups) == 60
    assert all(len(v) == 1 for v in groups.values())
    # replicate tag never appears inside the prompt content
    for p in setup["prompts"].glob("*.md"):
        assert "r01" not in p.read_text(encoding="utf-8")
        assert "replicate" not in p.read_text(encoding="utf-8").lower()


def test_source_corpus_hash_gates_fail_loudly(run_mod, setup):
    prepare(run_mod, setup)
    # corrupt corpus bytes -> prepare --force must refuse
    setup["corpus"].write_text(_CORPUS + "tampering\n", encoding="utf-8")
    with pytest.raises(RuntimeError, match="corpus"):
        run_mod.run_prepare(DATE, force=True)
    setup["corpus"].write_text(_CORPUS, encoding="utf-8")
    # corrupt source bytes -> refuse
    setup["source"].write_text(_SOURCE + "tampering\n", encoding="utf-8")
    with pytest.raises(RuntimeError, match="source"):
        run_mod.run_prepare(DATE, force=True)


def test_prompt_body_fidelity_vs_phase1_phase2a(run_mod, setup):
    """Model-facing instruction regions are byte-identical to the
    authoritative Phase-1 direct body and Phase-2A msg1/msg2 bodies."""
    prepare(run_mod, setup)
    # direct body == base instruction rendered with the story
    base = run_mod.p1.BASE_INSTRUCTION.read_text(encoding="utf-8").replace(
        "{STORY}", _SOURCE).rstrip() + "\n"
    direct_file = setup["prompts"] / "direct-04-claude-sonnet-5-r01.md"
    dtext = direct_file.read_text(encoding="utf-8")
    assert dtext.endswith(base)
    assert base.startswith(TRANSLATION_START)
    assert "KONIEC" in base
    # msg1 carries the full study text + the corpus verbatim
    msg1 = (setup["prompts"] / "primed-04-claude-sonnet-5-r01-msg1.md"
            ).read_text(encoding="utf-8")
    assert run_mod.PRIMED_MSG1_STUDY_TEXT in msg1
    assert _CORPUS.rstrip("\n") in msg1
    for a in ANCHORS:
        assert a in msg1
    # msg2 == intro sentence + identical direct body
    msg2 = (setup["prompts"] / "primed-04-claude-sonnet-5-r01-msg2.md"
            ).read_text(encoding="utf-8")
    assert run_mod.PRIMED_MSG2_INTRO in msg2
    assert base in msg2
    # msg2 body through the '## Output' marker equals the Phase-2A msg2
    # prompt part rendered by the authoritative renderer
    p2_msg2 = run_mod.p2a._render_primed_msg2(
        {"provider": "anthropic", "model": "claude",
         "model_version": "sonnet-5",
         "label": "Claude Sonnet 5 — Medium (default)",
         "interface": "Claude (web)",
         "generation_parameters": "Sonnet 5 Medium (default)"}, _SOURCE)
    i = p2_msg2.rfind("## Output\n")
    assert run_mod._translation_body(
        msg2) == run_mod._translation_body(
            p2_msg2[:i + len("## Output\n")])


def test_prepare_writes_human_collection_checklist(run_mod, setup):
    prepare(run_mod, setup)
    cl = (setup["outputs"] / "collection-checklist.md").read_text(
        encoding="utf-8")
    assert cl.count("[ ]") == 120
    assert "EXPLORATORY (optional)" in cl
    assert RUN_DIR in cl


# ---------------------------------------------------------------------------
# collect-session / collect-msg2
# ---------------------------------------------------------------------------

def _args(run_mod, **kw):
    class A:
        pass
    a = A()
    a.run = kw.pop("run")
    a.generation_date = kw.pop("generation_date", DATE)
    a.status = kw.pop("status", "collected_external_output")
    a.access_verdict = kw.pop("access_verdict", "pass")
    a.access_note = kw.pop("access_note", "")
    a.interface_settings = kw.pop("interface_settings", "not exposed")
    a.note = kw.pop("note", "")
    for k, v in kw.items():
        setattr(a, k, v)
    return a


def test_collect_session_direct_standalone_session(run_mod, setup,
                                                   monkeypatch):
    prepare(run_mod, setup)
    pf = setup["prompts"] / "direct-04-claude-sonnet-5-r01.md"
    session = setup["repeats"] / "session-r01.md"
    session.write_bytes(pf.read_bytes() + _REPLY.encode("utf-8"))
    rc = run_mod.run_collect_session(
        _args(run_mod, run=RUN_DIR, session=str(session)))
    assert rc == 0
    out = setup["outputs"] / RUN_DIR / "output.txt"
    assert out.read_bytes() == _REPLY.encode("utf-8")
    meta = json.loads((setup["outputs"] / RUN_DIR / "meta.json").read_text(
        encoding="utf-8"))
    assert meta["phase"] == "repeat"
    assert meta["condition"] == "direct"
    assert meta["replicate"] == "r01"
    assert meta["primary"] is True and meta["exploratory"] is False
    assert meta["source"]["sha256"] == run_mod.SOURCE_SHA256
    assert meta["corpus"] is None
    assert meta["session"]["msg2_style_record"] is False
    assert meta["interface_settings"] == "not exposed"


def test_collect_session_never_overwrites(run_mod, setup):
    prepare(run_mod, setup)
    pf = setup["prompts"] / "direct-04-claude-sonnet-5-r01.md"
    session = setup["repeats"] / "session-r01.md"
    session.write_bytes(pf.read_bytes() + _REPLY.encode("utf-8"))
    assert run_mod.run_collect_session(
        _args(run_mod, run=RUN_DIR, session=str(session))) == 0
    assert run_mod.run_collect_session(
        _args(run_mod, run=RUN_DIR, session=str(session))) == 2
    assert run_mod.run_collect_session(
        _args(run_mod, run="2099-01-01__unknown__x__y__direct__r01",
              session=str(session))) == 2


def test_collect_session_direct_rejects_corpus_contamination(run_mod,
                                                             setup):
    prepare(run_mod, setup)
    pf = setup["prompts"] / "direct-04-claude-sonnet-5-r01.md"
    session = setup["repeats"] / "bad.md"
    contaminated = (pf.read_text(encoding="utf-8").split("## Source text")[0]
                    + _CORPUS + "\n## Source text (Polish)\n\n"
                    + pf.read_text(encoding="utf-8").split(
                        "## Source text (Polish)")[1].split("## Output")[0]
                    + "## Output\n\n" + _REPLY)
    session.write_text(contaminated, encoding="utf-8")
    assert run_mod.run_collect_session(
        _args(run_mod, run=RUN_DIR, session=str(session))) == 2


def test_collect_session_msg2_style_prompt_file_record(run_mod, setup):
    prepare(run_mod, setup)
    # author saves the reply INSIDE the canonical prompt file (msg2-style)
    pf = setup["prompts"] / "direct-04-claude-sonnet-5-r01.md"
    virgin = pf.read_text(encoding="utf-8")
    head, _marker, tail = virgin.rpartition("## Output\n")
    # keep prompt part through the marker; append the raw reply
    pf.write_text(head + "## Output\n\n" + _REPLY, encoding="utf-8")
    assert run_mod.run_collect_session(
        _args(run_mod, run=RUN_DIR, session=str(pf))) == 0
    out = setup["outputs"] / RUN_DIR / "output.txt"
    assert out.read_bytes() == _REPLY.encode("utf-8")
    meta = json.loads((setup["outputs"] / RUN_DIR / "meta.json").read_text(
        encoding="utf-8"))
    assert meta["session"]["msg2_style_record"] is True
    assert meta["session"]["sha256"] == run_mod.sha256_bytes(pf.read_bytes())
    # verify passes (session file == prompt file, hash-based immutability)
    assert run_mod.run_verify(RUN_DIR) == 0


def test_collect_session_primed_full_transcript(run_mod, setup):
    prepare(run_mod, setup)
    m1 = (setup["prompts"] / "primed-04-claude-sonnet-5-r01-msg1.md"
          ).read_text(encoding="utf-8")
    m2 = (setup["prompts"] / "primed-04-claude-sonnet-5-r01-msg2.md"
          ).read_text(encoding="utf-8")
    head2, _marker, _tail = m2.rpartition("## Output\n")
    transcript = (m1 + "\n\nUnderstood.\n\n" + head2 + "## Output\n\n"
                  + _REPLY)
    session = setup["repeats"] / "primed-transcript.md"
    session.write_text(transcript, encoding="utf-8")
    assert run_mod.run_collect_session(
        _args(run_mod, run=RUN_P1, session=str(session))) == 0
    assert (setup["outputs"] / RUN_P1 / "output.txt").read_bytes() \
        == _REPLY.encode("utf-8")
    meta = json.loads((setup["outputs"] / RUN_P1 / "meta.json").read_text(
        encoding="utf-8"))
    assert meta["condition"] == "primed"
    assert meta["corpus"]["sha256"] == run_mod.AUTH_CORPUS_SHA256
    assert meta["session"]["contamination_checks"]["corpus_before_translation"]


def test_collect_session_primed_requires_corpus_before_translation(
        run_mod, setup):
    prepare(run_mod, setup)
    m2 = (setup["prompts"] / "primed-04-claude-sonnet-5-r01-msg2.md"
          ).read_text(encoding="utf-8")
    head2, _marker, _tail = m2.rpartition("## Output\n")
    transcript = ("No corpus here.\n\n" + head2 + "## Output\n\n" + _REPLY)
    session = setup["repeats"] / "primed-bad.md"
    session.write_text(transcript, encoding="utf-8")
    assert run_mod.run_collect_session(
        _args(run_mod, run=RUN_P1, session=str(session))) == 2


def test_collect_msg2_primed_only(run_mod, setup):
    prepare(run_mod, setup)
    m2 = setup["prompts"] / "primed-04-claude-sonnet-5-r01-msg2.md"
    virgin = m2.read_text(encoding="utf-8")
    head, _marker, _tail = virgin.rpartition("## Output\n")
    m2.write_text(head + "## Output\n\n" + _REPLY, encoding="utf-8")
    assert run_mod.run_collect_msg2(
        _args(run_mod, run=RUN_P1)) == 0
    assert (setup["outputs"] / RUN_P1 / "output.txt").read_bytes() \
        == _REPLY.encode("utf-8")
    meta = json.loads((setup["outputs"] / RUN_P1 / "meta.json").read_text(
        encoding="utf-8"))
    assert meta["session"]["contamination_checks"]["record_shape"].startswith(
        "msg2-style")
    # collect-msg2 only applies to primed runs
    assert run_mod.run_collect_msg2(
        _args(run_mod, run=RUN_DIR)) == 2


def test_collect_msg2_empty_reply_rejected(run_mod, setup):
    prepare(run_mod, setup)
    m2 = setup["prompts"] / "primed-04-claude-sonnet-5-r01-msg2.md"
    virgin = m2.read_text(encoding="utf-8")
    m2.write_text(virgin, encoding="utf-8")  # no reply appended
    assert run_mod.run_collect_msg2(
        _args(run_mod, run=RUN_P1)) == 2


# ---------------------------------------------------------------------------
# verify / evaluate
# ---------------------------------------------------------------------------

def _collect_complete_direct(run_mod, setup, size_floor_note=True):
    prepare(run_mod, setup)
    pf = setup["prompts"] / "direct-04-claude-sonnet-5-r01.md"
    session = setup["repeats"] / "session-r01.md"
    big_reply = (_REPLY + "\n" + _REPLY) * 60  # well above the size floor
    session.write_bytes(pf.read_bytes()
                        + big_reply.encode("utf-8"))
    assert run_mod.run_collect_session(
        _args(run_mod, run=RUN_DIR, session=str(session))) == 0
    return big_reply


def test_verify_gate_verdicts_complete_partial_failed(run_mod, setup):
    big = _collect_complete_direct(run_mod, setup)
    assert run_mod.run_verify(RUN_DIR) == 0
    intake = json.loads((setup["outputs"] / RUN_DIR / "intake.json")
                        .read_text(encoding="utf-8"))
    assert intake["verdict"] == "complete"
    assert intake["integrity_errors"] == []
    # partial: truncate the reply (drop the end marker)
    out = setup["outputs"] / RUN_DIR / "output.txt"
    meta_path = setup["outputs"] / RUN_DIR / "meta.json"
    truncated = big.split("KONEC")[0]
    out.write_bytes(truncated.encode("utf-8"))
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    meta["output"]["sha256"] = run_mod.sha256_bytes(truncated.encode("utf-8"))
    meta_path.write_text(json.dumps(meta), encoding="utf-8")
    assert run_mod.run_verify(RUN_DIR) == 0
    intake = json.loads((setup["outputs"] / RUN_DIR / "intake.json")
                        .read_text(encoding="utf-8"))
    assert intake["verdict"] == "partial"
    # failed: non-translation content, never deleted
    out.write_bytes(b"Blad serwisu.")
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    meta["output"]["sha256"] = run_mod.sha256_bytes(b"Blad serwisu.")
    meta["status"] = "failed_external_output"
    meta_path.write_text(json.dumps(meta), encoding="utf-8")
    assert run_mod.run_verify(RUN_DIR) == 0
    intake = json.loads((setup["outputs"] / RUN_DIR / "intake.json")
                        .read_text(encoding="utf-8"))
    assert intake["verdict"] == "failed"
    assert (setup["outputs"] / RUN_DIR / "output.txt").is_file()  # preserved


def test_evaluate_writes_summary_and_refuses_failed(run_mod, setup,
                                                    monkeypatch):
    _collect_complete_direct(run_mod, setup)
    assert run_mod.run_verify(RUN_DIR) == 0

    def fake_eval(cmd, **kw):
        out_dir_arg = Path(cmd[cmd.index("--out") + 1])
        out_dir_arg.mkdir(parents=True, exist_ok=True)
        (out_dir_arg / "report.json").write_text(json.dumps({
            "evaluator": {"name": "isv-eval", "version": "0.0.0"},
            "metrics": {"total_tokens": 100,
                        "canonical_supported_tokens": 80,
                        "canonical_coverage": 0.8,
                        "broader_resource_supported_tokens": 90,
                        "broader_resource_supported_coverage": 0.9,
                        "unresolved_tokens": 10,
                        "unresolved_rate": 0.1,
                        "exact_dictionary_matches": 70,
                        "morphologically_valid_forms": 10},
            "output_files": {}}, ensure_ascii=False), encoding="utf-8")
        return subprocess.CompletedProcess(cmd, 0, "", "")
    monkeypatch.setattr(run_mod.subprocess, "run", fake_eval)
    assert run_mod.run_evaluate(RUN_DIR) == 0
    ev = json.loads((setup["outputs"] / RUN_DIR / "evaluation.json")
                    .read_text(encoding="utf-8"))
    assert ev["usable"] is True
    assert ev["condition"] == "direct" and ev["replicate"] == "r01"
    assert ev["metrics"]["canonical_coverage"] == 0.8
    assert (setup["outputs"] / RUN_DIR / "orthography.json").is_file()
    assert (setup["outputs"] / RUN_DIR / "evaluation.md").is_file()

    # failed intake refuses evaluation without --force
    out = setup["outputs"] / RUN_DIR / "output.txt"
    out.write_bytes(b"Blad serwisu.")
    meta = json.loads((setup["outputs"] / RUN_DIR / "meta.json").read_text(
        encoding="utf-8"))
    meta["output"]["sha256"] = run_mod.sha256_bytes(b"Blad serwisu.")
    meta["status"] = "failed_external_output"
    (setup["outputs"] / RUN_DIR / "meta.json").write_text(
        json.dumps(meta), encoding="utf-8")
    assert run_mod.run_verify(RUN_DIR) == 0
    assert run_mod.run_evaluate(RUN_DIR) == 2
    assert run_mod.run_evaluate(RUN_DIR, force=True) == 0


def test_status_and_roster(run_mod, setup):
    prepare(run_mod, setup)
    assert run_mod.run_status() == 0
    assert run_mod.run_roster() == 0
    roster = json.loads((setup["outputs"] / "roster.json").read_text(
        encoding="utf-8"))
    assert roster["counts"]["planned"] == 120
    assert len(roster["rows"]) == 120
    assert (setup["outputs"] / "roster.md").is_file()


# ---------------------------------------------------------------------------
# analysis (synthetic observations)
# ---------------------------------------------------------------------------

def _obs(run_id, condition, replicate, primary, canonical, broader,
         unresolved=0.1, ortho=0, provider="x", model="y", version="z"):
    return {
        "run_id": run_id, "condition": condition, "replicate": replicate,
        "primary": primary, "exploratory": not primary,
        "label": f"{provider} {model} {version}", "provider": provider,
        "model": model, "model_version": version, "usable": True,
        "metrics": {"canonical_coverage": canonical,
                    "broader_resource_supported_coverage": broader,
                    "unresolved_rate": unresolved},
        "orthography": {"outside_inventory": ortho},
        "intake_verdict": "complete",
    }


def test_analysis_stats_and_deltas_exact(ana_mod):
    obs = []
    for i, (can, bro) in enumerate([(0.1, 0.2), (0.2, 0.3), (0.3, 0.4)]):
        obs.append(_obs(f"r-d{i}", "direct", f"r0{i + 1}", True, can, bro))
    for i, (can, bro) in enumerate([(0.4, 0.5), (0.5, 0.6), (0.6, 0.7)]):
        obs.append(_obs(f"r-p{i}", "primed", f"r0{i + 1}", True, can, bro))
    ds = ana_mod.build_dataset(obs)
    prim = ds["primary"]
    assert len(prim) == 1 and not ds["exploratory"]
    rec = prim[0]
    d, p = rec["direct"]["canonical"], rec["primed"]["canonical"]
    assert d["mean"] == pytest.approx(0.2)
    assert d["median"] == pytest.approx(0.2)
    assert d["sd"] == pytest.approx(0.1)
    assert d["range"] == pytest.approx(0.2)
    assert p["mean"] == pytest.approx(0.5)
    delta = rec["deltas"]["mean_canonical"]
    assert delta["delta_mean"] == pytest.approx(0.3)
    assert delta["direct_sd"] == pytest.approx(0.1)
    # block differences secondary view
    assert [b["diff"] for b in rec["deltas"]["block_differences_canonical"]] \
        == pytest.approx([0.3, 0.3, 0.3])


def test_analysis_no_dola_contamination_of_primary(ana_mod):
    prim = [_obs(f"p-d{i}", "direct", f"r0{i + 1}", True, 0.2, 0.3)
            for i in range(3)]
    prim += [_obs(f"p-p{i}", "primed", f"r0{i + 1}", True, 0.4, 0.5)
             for i in range(3)]
    dola = [_obs(f"d-d{i}", "direct", f"r0{i + 1}", False, 0.1, 0.2,
                 provider="dola", model="fast", version="3.8")
            for i in range(3)]
    dola += [_obs(f"d-p{i}", "primed", f"r0{i + 1}", False, 0.7, 0.8,
                  provider="dola", model="fast", version="3.8")
             for i in range(3)]
    ds = ana_mod.build_dataset(prim + dola)
    assert len(ds["primary"]) == 1
    assert len(ds["exploratory"]) == 1
    # primary stats are untouched by the Dola rows
    assert ds["primary"][0]["primed"]["canonical"]["mean"] \
        == pytest.approx(0.4)
    assert ds["exploratory"][0]["primed"]["canonical"]["mean"] \
        == pytest.approx(0.7)
    assert ds["exploratory"][0]["primary"] is False


def test_analysis_legacy_single_delta_joins(ana_mod):
    obs = []
    for i, can in enumerate([0.2, 0.25, 0.3]):
        obs.append(_obs(f"r-d{i}", "direct", f"r0{i + 1}", True, can, 0.3))
    for i, can in enumerate([0.5, 0.55, 0.6]):
        obs.append(_obs(f"r-p{i}", "primed", f"r0{i + 1}", True, can, 0.6))
    legacy = [{
        "run_id": "p2a-id", "baseline_run_id": "p1-id",
        "label": "x y z", "provider": "x", "model": "y",
        "model_version": "z",
        "p1_metrics": {"canonical_coverage": 0.2,
                       "broader_resource_supported_coverage": 0.3},
        "p1_ortho_out": 1,
        "p2a_metrics": {"canonical_coverage": 0.65,
                        "broader_resource_supported_coverage": 0.7},
        "p2a_ortho_out": 0}]
    ds = ana_mod.build_dataset(obs, legacy)
    rec = ds["primary"][0]
    assert rec["old_single"]["old_delta_canonical"] == pytest.approx(0.45)
    assert rec["old_single"]["p1_ortho_out"] == 1
    # repeated delta is unaffected by the legacy record
    assert rec["deltas"]["mean_canonical"]["delta_mean"] \
        == pytest.approx(0.3)


def test_analysis_no_results_scaffold(ana_mod, tmp_path):
    # empty observation set -> explicit no-results scaffold, no fake charts
    out = tmp_path / "a"
    ana_mod.write_analysis(out, [], [])
    an = json.loads((out / "analysis.json").read_text(encoding="utf-8"))
    assert an["status"] == "no_results"
    assert an["counts"]["primary_configs_with_data"] == 0
    for f in ("figure_a.svg", "figure_b.svg", "figure_c.svg",
              "figure_d.svg", "figure_e.svg"):
        assert (out / "figures" / f).read_text(encoding="utf-8") \
            .startswith("<!-- figure not generated")


def test_analysis_spearman_and_figures_deterministic(ana_mod, tmp_path):
    xs = [0.1 * i for i in range(1, 7)]
    ys = [0.9 * x for x in xs]
    assert ana_mod.spearman(xs, ys) == pytest.approx(1.0)
    assert ana_mod.spearman(xs, [-v for v in ys]) == pytest.approx(-1.0)
    assert ana_mod.spearman([], []) is None

    obs = []
    for j in range(2):
        for i, can in enumerate([0.3, 0.4, 0.5]):
            obs.append(_obs(f"c{j}-d{i}", "direct", f"r0{i + 1}", True,
                            can, can + 0.1, version=f"v{j}"))
        for i, can in enumerate([0.35, 0.45, 0.55]):
            obs.append(_obs(f"c{j}-p{i}", "primed", f"r0{i + 1}", True,
                            can, can + 0.1, version=f"v{j}"))
    out1 = tmp_path / "a1"
    out2 = tmp_path / "a2"
    ana_mod.write_analysis(out1, obs, [])
    ana_mod.write_analysis(out2, obs, [])
    for name in ("analysis.json", "analysis.md", "dataset.json"):
        assert (out1 / name).read_bytes() == (out2 / name).read_bytes()
    for f in ("figure_a.svg", "figure_b.svg", "figure_c.svg",
              "figure_d.svg", "figure_e.svg"):
        assert (out1 / "figures" / f).read_bytes() \
            == (out2 / "figures" / f).read_bytes()
    an = json.loads((out1 / "analysis.json").read_text(encoding="utf-8"))
    assert an["status"] == "results"
    assert an["counts"]["primary_configs_with_data"] == 2
    assert (out1 / "analysis.md").read_text(encoding="utf-8").startswith(
        "# EXP-004 Phase repeat")
