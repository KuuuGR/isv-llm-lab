"""EXP-004 Phase 2A — full-roster corpus priming: orchestration tests
(SODA Task 019 preparation).

Covers the corpus-priming discipline:
- Phase-2A roster = the reconciled 18 usable Phase-1 configurations (GLM
  excluded), derived from run_exp004_phase1.ROSTER, never from filenames;
- run identity: <date>__<provider>__<model>__<model_version>__p2a-ctl /
  p2a-primed — never confused with Phase-1 '__direct' baselines; every
  primed run carries its Phase-1 baseline run id;
- condition separation: control prompts (fresh session, direct translation)
  contain the Polish story but NO corpus material; primed msg1 contains the
  corpus but NO story; primed msg2 contains the story but NO corpus; the
  translation instruction+story body is byte-identical across all control
  and msg2 prompts;
- hash consistency: corpus file == plan == manifest == pinned constant;
  Polish source == plan == pinned constant;
- contamination controls in collect-session: primed sessions must contain
  the corpus BEFORE the translation instruction (same-session proof);
  control sessions containing corpus material are rejected;
- roster coverage: 18 configurations × 2 conditions = 36 planned runs,
  complete pairs, deterministic regeneration;
- no fabricated outputs: nothing is collected/evaluated without an author
  session or external output file.
"""
import importlib.util
import json
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

_COMPLETE = (
    "Povědka o slovah, ktore byle kako sestry\n"
    "Prolog\n\n"
    + ("Bronisława, Teofil i Julianna živili v Medžurečju. Przemysława "
       "prišla k nih. Antoni molčal.\n") * 400
    + "\nKONIEC\n"
)

# Synthetic corpus: short authentic-ISV-looking three-register text that
# carries the three per-register fingerprint anchors used by the
# contamination checks (register 1 narrative, 2 artistic, 3 encyclopedic).
_CORPUS = (
    "=== REGISTER 1: LITERARY / NARRATIVE ===\n\n"
    "Prolog\n"
    "Ljudi govoret, že v tamtoj denj bylo je veliko spokojno. Čisto "
    "nebo bylo jasno, a větr je byl silny, kako v zimě. V tamtoj denj "
    "prišla Črvena Iskra.\n\n"
    "Razděl 1. Věčna Zima\n"
    "- Pytanje zvuči v krčmě. Seljani sut silni, no dolgo tako ne "
    "smožemo žiti.\n"
    "Seljani načeli sut organizovati jedanje i vsako dobro, ktoro jest "
    "potrěbno, da by prěžiti v tutoj težkoj době.\n\n"
    "=== REGISTER 2: ARTISTIC / POETIC ===\n\n"
    "Velerman\n\n"
    "Toj korab znajut ljudi vsi\n"
    "A jego ime jest Billy of Tea\n\n"
    "Morske Opověsti\n\n"
    "Hej ho, nalijte vino\n"
    "Hej ho, prineste čaše\n\n"
    "=== REGISTER 3: INFORMATIVE / ENCYCLOPEDIC ===\n\n"
    "Sadovničstvo jest proces raščenja rastlin zaradi jih zeleniny, "
    "ovočev, cvětov i zelěnosti. Odomašnjenje rastlin sčitaje se "
    "narodženjem zemjeděljstva.\n"
)

# One fingerprint phrase per corpus register (mirrors run_mod.CORPUS_ANCHORS)
ANCHORS = (
    "Ljudi govoret, že v tamtoj denj bylo je veliko spokojno",
    "Toj korab znajut ljudi vsi",
    "Sadovničstvo jest proces raščenja rastlin",
)
STORY_START = "Translate the Polish story below into Interslavic"
STORY_TITLE = "Opowieść o Słów, Które Były Jak Siostry"

DATE = "2099-01-01"
BASE_CTL = f"{DATE}__openai__gpt-5.6-luna__thinkoff__p2a-ctl"
BASE_PRI = f"{DATE}__openai__gpt-5.6-luna__thinkoff__p2a-primed"


@pytest.fixture(scope="module")
def run_mod():
    spec = importlib.util.spec_from_file_location(
        "run_exp004_phase2a", SCRIPTS / "run_exp004_phase2a.py")
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
    # empty phase-1 outputs -> baseline ids fall back to the documented
    # Phase-1 plan date (deterministic for tests)
    p1_outputs = tmp_path / "phase1-outputs"
    p1_outputs.mkdir()
    monkeypatch.setattr(run_mod.p1, "OUTPUTS_DIR", p1_outputs)
    return {"tmp": tmp_path, "p1_outputs": p1_outputs}


def prepare(run_mod, setup, date=DATE, force=False):
    rc = run_mod.run_prepare(date, force)
    assert rc == 0
    return setup["tmp"] / "outputs" / "plan.json"


def row_for(run_mod, provider, model, version):
    return next(r for r in run_mod.ROSTER
                if r["provider"] == provider and r["model"] == model
                and r["model_version"] == version)


def _prompt_text(run_mod, setup, name) -> str:
    return (setup["tmp"] / "operator-prompts" / name).read_text(
        encoding="utf-8")


def _plan_run(plan, run_id):
    return next(r for r in plan["runs"] if r["run_id"] == run_id)


# ---------------------------------------------------------------------------
# roster
# ---------------------------------------------------------------------------

def test_roster_is_the_18_usable_phase1_configs(run_mod):
    assert len(run_mod.ROSTER) == 18
    assert all(r["provider"] != "zhipu" for r in run_mod.ROSTER)
    p1_rows = [(r["provider"], r["model"], r["model_version"])
               for r in run_mod.p1.ROSTER if r["provider"] != "zhipu"]
    assert len(p1_rows) == 18
    assert {tuple(r[k] for k in ("provider", "model", "model_version"))
            for r in run_mod.ROSTER} == set(p1_rows)


def test_run_id_identity_and_condition_separation(run_mod, setup):
    plan = json.loads(prepare(run_mod, setup).read_text(encoding="utf-8"))
    ids = [r["run_id"] for r in plan["runs"]]
    assert len(ids) == 36
    assert len(set(ids)) == 36  # unique
    assert all(i.endswith("__p2a-ctl") or i.endswith("__p2a-primed")
               for i in ids)
    assert not any(i.endswith("__direct") for i in ids)  # not Phase 1
    # every primed run has exactly one ctl twin and vice versa
    ctl = {r["run_id"] for r in plan["runs"] if r["condition"] == "p2a-ctl"}
    pri = {r["run_id"] for r in plan["runs"] if r["condition"] == "p2a-primed"}
    assert len(ctl) == len(pri) == 18
    stem = lambda i: "__".join(i.split("__")[:4])  # noqa: E731
    assert {stem(i) for i in ctl} == {stem(i) for i in pri}
    # each run parses back and carries its Phase-1 baseline id
    for r in plan["runs"]:
        parts = run_mod.parse_run_id(r["run_id"])
        assert parts["condition"] in run_mod.P2A_CONDITIONS
        assert parts["provider"] == r["provider"]
        assert parts["model"] == r["model"]
        assert r["baseline_run_id"].endswith("__direct")
        assert r["baseline_run_id"].split("__")[1:4] == [
            r["provider"], r["model"], r["model_version"]]
    # ctl and primed share the same baseline for the same configuration
    def find(cond):
        return {stem(i) for i in ids if i.endswith(f"__{cond}")}
    for i in sorted(stem(x) for x in ctl):
        c = _plan_run(plan, f"{i}__p2a-ctl")
        p = _plan_run(plan, f"{i}__p2a-primed")
        assert c["baseline_run_id"] == p["baseline_run_id"]


def test_parse_run_id_rejects_phase1_and_garbage(run_mod):
    with pytest.raises(ValueError):
        run_mod.parse_run_id(f"{DATE}__openai__gpt-5.6-luna__thinkoff"
                             "__direct")  # Phase-1 id, not a 2A condition
    with pytest.raises(ValueError):
        run_mod.parse_run_id("garbage")
    assert run_mod.roster_entry("garbage") is None


# ---------------------------------------------------------------------------
# prepare
# ---------------------------------------------------------------------------

def test_prepare_packages_36_runs_and_54_prompt_files(run_mod, setup):
    plan = json.loads(prepare(run_mod, setup).read_text(encoding="utf-8"))
    assert len(plan["runs"]) == 36
    assert plan["phase"] == "2a"
    assert plan["source"]["sha256"] == run_mod.SOURCE_SHA256
    assert plan["corpus"]["id"] == "phase2a-authentic-isv"
    assert plan["corpus"]["sha256"] == run_mod.AUTH_CORPUS_SHA256
    assert [r["n"] for r in plan["corpus"]["registers"]] == [1, 2, 3]
    files = sorted(p.name for p in
                   (setup["tmp"] / "operator-prompts").glob("*.md"))
    assert len(files) == 54
    # ctl files: 18; primed msg1/msg2: 36
    assert len([f for f in files if f.startswith("ctl-")]) == 18
    assert len([f for f in files if f.startswith("primed-")
                and f.endswith("-msg1.md")]) == 18
    assert len([f for f in files if f.startswith("primed-")
                and f.endswith("-msg2.md")]) == 18


def test_prompt_separation_and_identical_translation_bodies(run_mod, setup):
    """Control + msg2 prompts carry the same instruction+story body and no
    corpus; msg1 carries the full corpus and no story."""
    prepare(run_mod, setup)
    op = setup["tmp"] / "operator-prompts"
    bodies = []
    for f in sorted(op.glob("*.md")):
        text = f.read_text(encoding="utf-8")
        has_corpus = any(a in text for a in ANCHORS)
        has_story_start = STORY_START in text
        has_title = STORY_TITLE in text
        if f.name.startswith("ctl-") or f.name.endswith("-msg2.md"):
            # translation prompts: story present, corpus absent
            assert has_story_start and has_title
            assert not has_corpus, f"{f.name} must not contain corpus"
            bodies.append(run_mod._translation_body(text))
        else:
            # msg1: corpus present, story absent
            assert has_corpus and not has_story_start and not has_title
            # Prompt 1 describes the three registers and the poetic note
            assert "three different registers" in text
            assert "artistic / poetic" in text
            assert not text.rstrip("\n").endswith(
                "Return the complete Interslavic translation")
    # the invariant translation instruction+story body is IDENTICAL across
    # all 36 control/msg2 prompts (headers and the msg2 lead differ only)
    assert len(bodies) == 36
    assert all(b == bodies[0] for b in bodies)
    assert bodies[0].startswith(STORY_START)


def test_prepare_deterministic_and_hash_consistency(run_mod, setup):
    prepare(run_mod, setup)

    def snap():
        d = {}
        for name in ("plan.json",):
            d[name] = (setup["tmp"] / "outputs" / name).read_bytes()
        d["manifest.json"] = (setup["tmp"] / "operator-prompts"
                              / "manifest.json").read_bytes()
        for pf in sorted((setup["tmp"] / "operator-prompts").glob("*.md")):
            d[pf.name] = pf.read_bytes()
        return d

    first = snap()
    prepare(run_mod, setup, force=True)
    assert snap() == first  # byte-identical regeneration

    plan = json.loads((setup["tmp"] / "outputs" / "plan.json").read_text(
        encoding="utf-8"))
    manifest = json.loads((setup["tmp"] / "operator-prompts"
                           / "manifest.json").read_text(encoding="utf-8"))
    # corpus hash consistency: file == manifest == plan == pinned constant
    corpus_sha = run_mod.sha256_bytes(_CORPUS.encode("utf-8"))
    assert manifest["corpus"]["sha256"] == corpus_sha
    assert plan["corpus"]["sha256"] == corpus_sha
    assert corpus_sha == run_mod.AUTH_CORPUS_SHA256
    assert manifest["corpus"]["id"] == "phase2a-authentic-isv"
    # source hash consistency: file == plan == pinned constant
    source_sha = run_mod.sha256_bytes(_SOURCE.encode("utf-8"))
    assert plan["source"]["sha256"] == source_sha
    assert source_sha == run_mod.SOURCE_SHA256
    # manifest prompt hashes match the prompt files
    assert len(manifest["files"]) == 54
    for f in manifest["files"]:
        pf = setup["tmp"] / "operator-prompts" / f["file"]
        assert run_mod.sha256_bytes(pf.read_bytes()) == f["prompt_sha256"]
        # prompt manifest rows carry run id / condition / message
        assert f["run_id"].endswith("__" + f["condition"])
        if f["condition"] == "p2a-ctl":
            assert f["message"] is None
        else:
            assert f["message"] in (1, 2)


def test_prepare_never_overwrites_plan_without_force(run_mod, setup):
    prepare(run_mod, setup)
    assert run_mod.run_prepare(DATE) == 2


def test_prepare_refuses_tampered_corpus(run_mod, setup):
    """A corpus file whose hash does not match the pinned constant must be
    refused (an accidental edit would break the fixed-corpus invariant)."""
    prepare(run_mod, setup)
    # mutate the corpus file (the test fixture monkeypatched the constant
    # to the ORIGINAL synthetic corpus hash, so a mutation is detectable)
    corpus = setup["tmp"] / "corpus.txt"
    corpus.write_text(_CORPUS.replace(
        "veliko spokojno", "VELIKO SPOKOJNO"), encoding="utf-8")
    (setup["tmp"] / "outputs" / "plan.json").unlink()
    for f in (setup["tmp"] / "operator-prompts").glob("*.md"):
        f.unlink()
    with pytest.raises(RuntimeError):
        run_mod.run_prepare(DATE)


# ---------------------------------------------------------------------------
# collect
# ---------------------------------------------------------------------------

def test_collect_byte_for_byte_and_meta(run_mod, setup):
    plan = json.loads(prepare(run_mod, setup).read_text(encoding="utf-8"))
    reply = setup["tmp"] / "reply.txt"
    data = _COMPLETE.encode("utf-8")
    reply.write_bytes(data)
    for run_id in (BASE_CTL, BASE_PRI):
        assert run_mod.run_collect(run_id, reply, DATE) == 0
        out_dir = setup["tmp"] / "outputs" / run_id
        assert (out_dir / "output.txt").read_bytes() == data
        meta = json.loads((out_dir / "meta.json").read_text(
            encoding="utf-8"))
        assert meta["condition"] == run_id.split("__")[4]
        assert meta["baseline_run_id"].endswith("__direct")
        assert meta["output"]["sha256"] == run_mod.sha256_bytes(data)
        assert meta["corpus"]["sha256"] == run_mod.AUTH_CORPUS_SHA256
        assert meta["source"]["sha256"] == run_mod.SOURCE_SHA256
        p = _plan_run(plan, run_id)
        assert meta["prompt"]["translation_prompt_sha256"] == \
            p["translation_prompt_sha256"]


def test_collect_refuses_overwrite_and_unknown_run(run_mod, setup):
    prepare(run_mod, setup)
    reply = setup["tmp"] / "reply.txt"
    reply.write_bytes(_COMPLETE.encode("utf-8"))
    assert run_mod.run_collect(BASE_CTL, reply, DATE) == 0
    assert run_mod.run_collect(BASE_CTL, reply, DATE) == 2  # no overwrite
    assert run_mod.run_collect(f"{DATE}__openai__nope__x__p2a-ctl",
                               reply, DATE) == 2  # unknown row
    assert run_mod.run_collect(f"{DATE}__openai__gpt-5.6-luna__thinkoff"
                               "__direct", reply, DATE) == 2  # phase-1 id


# ---------------------------------------------------------------------------
# collect-session (contamination-controlled)
# ---------------------------------------------------------------------------

def _session(run_mod, setup, prompt_name, reply_text):
    pf = setup["tmp"] / "operator-prompts" / prompt_name
    text = pf.read_text(encoding="utf-8")
    cut = text.rfind("Return the complete")
    return text[:cut].encode("utf-8") + reply_text.encode("utf-8")


def _primed_session(run_mod, setup, msg1_name, msg2_name, reply1,
                    reply2):
    m1 = (setup["tmp"] / "operator-prompts" / msg1_name).read_text(
        encoding="utf-8").encode("utf-8")
    m2 = (setup["tmp"] / "operator-prompts" / msg2_name).read_text(
        encoding="utf-8").encode("utf-8")
    cut = m2.rfind(b"Return the complete")
    return m1 + b"\n\n" + reply1.encode("utf-8") + b"\n\n" + \
        m2[:cut] + reply2.encode("utf-8")


def _file_names_for(run_mod, run_id):
    row = run_mod.roster_entry(run_id)
    return run_mod._prompt_names(row)


def test_collect_session_control_extracts_and_rejects_corpus(
        run_mod, setup):
    prepare(run_mod, setup)
    ctl, m1, m2 = _file_names_for(run_mod, BASE_CTL)
    session = setup["tmp"] / "session.md"
    session.write_bytes(_session(run_mod, setup, ctl, _COMPLETE))
    assert run_mod.run_collect_session(BASE_CTL, session, DATE) == 0
    out_dir = setup["tmp"] / "outputs" / BASE_CTL
    assert (out_dir / "output.txt").read_text(encoding="utf-8") == _COMPLETE
    meta = json.loads((out_dir / "meta.json").read_text(encoding="utf-8"))
    assert meta["session"]["contamination_checks"]["corpus_in_control"] \
        is False

    # second configuration (same model, thinking ON) for the rejection
    # checks — its ctl run is still uncollected
    row_on = row_for(run_mod, "openai", "gpt-5.6-luna", "thinkon")
    ctl_on = run_mod.run_id_for(DATE, row_on, "p2a-ctl")

    # control session that ALSO contains the reference corpus = contamination
    bad = setup["tmp"] / "bad-ctl.md"
    bad.write_bytes(_session(run_mod, setup, ctl, _COMPLETE) + b"\n" +
                    _CORPUS.encode("utf-8"))
    assert run_mod.run_collect_session(ctl_on, bad, DATE) == 2
    # corpus placed before the prompt body also counts as contamination
    bad2 = setup["tmp"] / "bad-ctl2.md"
    bad2.write_bytes(_CORPUS.encode("utf-8") + b"\n\n" +
                     _session(run_mod, setup, ctl, _COMPLETE))
    assert run_mod.run_collect_session(ctl_on, bad2, DATE) == 2
    assert not (setup["tmp"] / "outputs" / ctl_on / "output.txt").exists()


def test_collect_session_primed_requires_corpus_in_session(
        run_mod, setup):
    prepare(run_mod, setup)
    ctl, m1, m2 = _file_names_for(run_mod, BASE_PRI)
    good = setup["tmp"] / "primed-session.md"
    good.write_bytes(_primed_session(run_mod, setup, m1, m2,
                                     "Ponjal. Gotov.",
                                     _COMPLETE))
    assert run_mod.run_collect_session(BASE_PRI, good, DATE) == 0
    out_dir = setup["tmp"] / "outputs" / BASE_PRI
    assert (out_dir / "output.txt").read_text(encoding="utf-8") == _COMPLETE
    meta = json.loads((out_dir / "meta.json").read_text(encoding="utf-8"))
    assert meta["session"]["contamination_checks"][
        "corpus_before_translation"] is True
    assert meta["condition"] == "p2a-primed"
    # session file untouched
    assert good.read_bytes().startswith(b"# EXP-004")

    # a primed session WITHOUT the corpus (msg1 skipped) must be rejected:
    # Prompt 2 alone is not the priming condition
    no_corpus = setup["tmp"] / "no-corpus-primed.md"
    m2_only = (setup["tmp"] / "operator-prompts" / m2).read_text(
        encoding="utf-8")
    cut = m2_only.rfind("Return the complete")
    no_corpus.write_bytes((m2_only[:cut] + _COMPLETE).encode("utf-8"))
    row_on = row_for(run_mod, "openai", "gpt-5.6-luna", "thinkon")
    pri_on = run_mod.run_id_for(DATE, row_on, "p2a-primed")
    assert run_mod.run_collect_session(pri_on, no_corpus, DATE) == 2


def test_collect_session_primed_rejects_partial_corpus(run_mod, setup):
    """msg1 that lost one register (e.g. a truncated corpus) must not pass
    the priming check: all three register anchors must precede msg2."""
    prepare(run_mod, setup)
    ctl, m1, m2 = _file_names_for(run_mod, BASE_PRI)
    m1_text = (setup["tmp"] / "operator-prompts" / m1).read_text(
        encoding="utf-8")
    # remove register-3 material (drop everything from its register header)
    cut = m1_text.find("=== REGISTER 3: INFORMATIVE / ENCYCLOPEDIC ===")
    assert cut > 0
    truncated = m1_text[:cut]
    assert any(a in truncated for a in ANCHORS[:2])
    assert not any(a in truncated for a in ANCHORS[2:])
    m2b = (setup["tmp"] / "operator-prompts" / m2).read_text(
        encoding="utf-8")
    cut2 = m2b.rfind("Return the complete")
    raw = (truncated.encode("utf-8") + b"\n\nPonjal.\n\n"
           + m2b[:cut2].encode("utf-8") + _COMPLETE.encode("utf-8"))
    bad = setup["tmp"] / "partial-corpus-primed.md"
    bad.write_bytes(raw)
    row_on = row_for(run_mod, "openai", "gpt-5.6-luna", "thinkon")
    pri_on = run_mod.run_id_for(DATE, row_on, "p2a-primed")
    assert run_mod.run_collect_session(pri_on, bad, DATE) == 2
    assert not (setup["tmp"] / "outputs" / pri_on / "output.txt").exists()


def test_collect_session_rejects_altered_translation_instruction(
        run_mod, setup):
    prepare(run_mod, setup)
    ctl, m1, m2 = _file_names_for(run_mod, BASE_PRI)
    good = setup["tmp"] / "primed-session.md"
    raw = _primed_session(run_mod, setup, m1, m2, "Ponjal.", _COMPLETE)
    raw = raw.replace(b"Translate the Polish story below into Interslavic",
                      b"Translate the Polish fable below into Interslavic")
    good.write_bytes(raw)
    assert run_mod.run_collect_session(BASE_PRI, good, DATE) == 2
    assert not (setup["tmp"] / "outputs" / BASE_PRI /
                "output.txt").exists()


def test_split_primed_reply_ignores_reply1_marker(run_mod):
    """If the model's reply to msg1 happens to contain '## Output', the
    primed split must still find msg2's real marker."""
    raw = (b"msg1 header + corpus\n\n"
           b"Ponjal: '## Output example' in reply1\n\n"
           b"msg2 header\n"
           b"Translate the Polish story below into Interslavic\n"
           b"## Output\nfinal translation\n")
    prefix, reply = run_mod._split_primed_reply(raw)
    assert reply == b"final translation\n"


# ---------------------------------------------------------------------------
# verify / evaluate
# ---------------------------------------------------------------------------

def _register(run_mod, setup, run_id, text, status="collected_external_output"):
    reply = setup["tmp"] / f"reply-{run_id.split('__')[4]}.txt"
    reply.write_text(text, encoding="utf-8")
    assert run_mod.run_collect(run_id, reply, DATE, status=status) == 0
    assert run_mod.run_verify(run_id) == 0
    out_dir = setup["tmp"] / "outputs" / run_id
    return json.loads((out_dir / "intake.json").read_text(encoding="utf-8"))


def test_verify_complete_partial_failed(run_mod, setup):
    prepare(run_mod, setup)
    intake = _register(run_mod, setup, BASE_PRI, _COMPLETE)
    assert intake["verdict"] == "complete"

    row = row_for(run_mod, "openai", "gpt-5.6-luna", "thinkon")
    pri2 = run_mod.run_id_for(DATE, row, "p2a-primed")
    intake = _register(run_mod, setup, pri2,
                       _COMPLETE.replace("\nKONIEC\n", "\n...\n"),
                       status="collected_partial_output")
    assert intake["verdict"] == "partial"

    row = row_for(run_mod, "openai", "gpt-isv-teacher", "unknown")
    pri3 = run_mod.run_id_for(DATE, row, "p2a-primed")
    intake = _register(run_mod, setup, pri3,
                       "Przepraszamy, wystąpił błąd serwisu.",
                       status="failed_external_output")
    assert intake["verdict"] == "failed"


def test_evaluate_writes_summary_and_refuses_failed(run_mod, setup,
                                                    monkeypatch):
    prepare(run_mod, setup)
    out_dir = setup["tmp"] / "outputs" / BASE_PRI
    reply = setup["tmp"] / "reply.txt"
    reply.write_bytes(_COMPLETE.encode("utf-8"))
    assert run_mod.run_collect(BASE_PRI, reply, DATE, status="collected_external_output") == 0
    assert run_mod.run_verify(BASE_PRI) == 0

    def fake_eval(cmd, **kw):
        import subprocess
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

    assert run_mod.run_evaluate(BASE_PRI) == 0
    ev = json.loads((out_dir / "evaluation.json").read_text(
        encoding="utf-8"))
    assert ev["usable"] is True
    assert ev["condition"] == "p2a-primed"
    assert ev["baseline_run_id"].endswith("__direct")
    assert ev["metrics"]["canonical_coverage"] == 0.8
    assert (out_dir / "orthography.json").is_file()
    assert (out_dir / "evaluation.md").is_file()

    # failed intake refuses evaluation
    (out_dir / "output.txt").write_text("Blad serwisu.", encoding="utf-8")
    meta = json.loads((out_dir / "meta.json").read_text(encoding="utf-8"))
    meta["output"]["sha256"] = run_mod.sha256_bytes(b"Blad serwisu.")
    meta["status"] = "failed_external_output"
    (out_dir / "meta.json").write_text(json.dumps(meta), encoding="utf-8")
    assert run_mod.run_verify(BASE_PRI) == 0
    assert run_mod.run_evaluate(BASE_PRI) == 2
    assert run_mod.run_evaluate(BASE_PRI, force=True) == 0


# ---------------------------------------------------------------------------
# status / roster / compare
# ---------------------------------------------------------------------------

def test_status_and_roster_empty_and_with_run(run_mod, setup):
    prepare(run_mod, setup)
    assert run_mod.run_status() == 0
    assert run_mod.run_roster() == 0
    roster = json.loads((setup["tmp"] / "outputs" / "roster.json")
                        .read_text(encoding="utf-8"))
    assert len(roster["rows"]) == 36
    assert roster["rows"][0]["collected"] is False


def _fake_isv_eval(monkeypatch, run_mod, metrics):
    """Monkeypatch isv_eval subprocess to write canned metrics and to pass
    through unrelated subprocess calls (e.g. git_commit's rev-parse)."""
    def fake_eval(cmd, **kw):
        import subprocess
        if "--out" not in cmd:  # e.g. git rev-parse inside git_commit()
            return subprocess.CompletedProcess(cmd, 0, "fake-commit", "")
        out_dir_arg = Path(cmd[cmd.index("--out") + 1])
        out_dir_arg.mkdir(parents=True, exist_ok=True)
        (out_dir_arg / "report.json").write_text(json.dumps({
            "evaluator": {"name": "isv-eval", "version": "0.0.0"},
            "metrics": metrics, "output_files": {}},
            ensure_ascii=False), encoding="utf-8")
        return subprocess.CompletedProcess(cmd, 0, "", "")
    monkeypatch.setattr(run_mod.subprocess, "run", fake_eval)


def _eval_metrics(run_mod, setup, run_id, monkeypatch, metrics=None):
    """Collect + verify + evaluate an already-prepared run with canned
    isv-eval metrics (prepare must already have run once)."""
    out_dir = setup["tmp"] / "outputs" / run_id
    reply = setup["tmp"] / "reply.txt"
    reply.write_bytes(_COMPLETE.encode("utf-8"))
    assert run_mod.run_collect(run_id, reply, DATE,
                               status="collected_external_output") == 0
    assert run_mod.run_verify(run_id) == 0
    m = metrics or {"total_tokens": 100, "canonical_supported_tokens": 80,
                    "canonical_coverage": 0.8,
                    "broader_resource_supported_tokens": 90,
                    "broader_resource_supported_coverage": 0.9,
                    "unresolved_tokens": 10, "unresolved_rate": 0.1,
                    "exact_dictionary_matches": 70,
                    "morphologically_valid_forms": 10}
    _fake_isv_eval(monkeypatch, run_mod, m)
    assert run_mod.run_evaluate(run_id) == 0
    return m


def test_compare_primed_vs_phase1_baseline(run_mod, setup, monkeypatch):
    prepare(run_mod, setup)
    plan = json.loads((setup["tmp"] / "outputs" / "plan.json").read_text(
        encoding="utf-8"))
    pri_row = _plan_run(plan, BASE_PRI)
    baseline_id = pri_row["baseline_run_id"]

    primed_m = _eval_metrics(run_mod, setup, BASE_PRI, monkeypatch, metrics={
        "total_tokens": 120, "canonical_supported_tokens": 90,
        "canonical_coverage": 0.9,
        "broader_resource_supported_tokens": 100,
        "broader_resource_supported_coverage": 0.95,
        "unresolved_tokens": 8, "unresolved_rate": 0.067,
        "exact_dictionary_matches": 75, "morphologically_valid_forms": 15})

    # Phase-1 baseline output for the same configuration (under the Phase-1
    # outputs dir): baseline id must match what prepare recorded
    base_dir = setup["p1_outputs"] / baseline_id
    base_dir.mkdir(parents=True)
    (base_dir / "evaluation.json").write_text(json.dumps({
        "run_id": baseline_id, "phase": "1", "condition": "direct",
        "usable": True,
        "metrics": {"total_tokens": 100,
                    "canonical_supported_tokens": 80,
                    "canonical_coverage": 0.8,
                    "broader_resource_supported_tokens": 90,
                    "broader_resource_supported_coverage": 0.9,
                    "unresolved_tokens": 10, "unresolved_rate": 0.1,
                    "exact_dictionary_matches": 70,
                    "morphologically_valid_forms": 10}},
        ensure_ascii=False), encoding="utf-8")

    assert run_mod.run_compare() == 0
    out = json.loads((setup["tmp"] / "outputs" / "compare.json").read_text(
        encoding="utf-8"))
    rows = out["rows"]
    assert len(rows) == 18  # all primed configs listed
    row = next(r for r in rows if r["run_id"] == BASE_PRI)
    assert row["baseline_source"] == "phase1-baseline"
    d = row["deltas"]
    assert d["canonical_coverage_pp"] == 0.1
    assert d["broader_resource_supported_coverage_pp"] == 0.05
    assert d["unresolved_rate_pp"] == pytest.approx(-0.033, abs=1e-6)
    assert d["lexical_tokens"] == 20
    # other rows: primed not evaluated -> listed with an error, not skipped
    others = [r for r in rows if "error" in r]
    assert len(others) == 17
    assert (setup["tmp"] / "outputs" / "compare.md").is_file()


def test_compare_prefers_fresh_control_over_phase1(run_mod, setup,
                                                   monkeypatch):
    prepare(run_mod, setup)
    # fresh Phase-2A control run with different metrics than phase-1
    ctl_m = _eval_metrics(run_mod, setup, BASE_CTL, monkeypatch, metrics={
        "total_tokens": 90, "canonical_supported_tokens": 60,
        "canonical_coverage": 0.6,
        "broader_resource_supported_tokens": 70,
        "broader_resource_supported_coverage": 0.7,
        "unresolved_tokens": 20, "unresolved_rate": 0.22,
        "exact_dictionary_matches": 50, "morphologically_valid_forms": 10})
    pri_m = _eval_metrics(run_mod, setup, BASE_PRI, monkeypatch, metrics={
        "total_tokens": 120, "canonical_supported_tokens": 90,
        "canonical_coverage": 0.9,
        "broader_resource_supported_tokens": 100,
        "broader_resource_supported_coverage": 0.95,
        "unresolved_tokens": 8, "unresolved_rate": 0.067,
        "exact_dictionary_matches": 75, "morphologically_valid_forms": 15})

    assert run_mod.run_compare() == 0
    out = json.loads((setup["tmp"] / "outputs" / "compare.json").read_text(
        encoding="utf-8"))
    row = next(r for r in out["rows"] if r["run_id"] == BASE_PRI)
    assert row["baseline_source"] == "p2a-ctl"
    # deltas now computed against the fresh control (0.6 -> 0.9)
    assert row["deltas"]["canonical_coverage_pp"] == 0.3
