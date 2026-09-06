"""EXP-004 Phase 1 — screening run orchestration tests (SODA Tasks 017/018).

Covers the clean-baseline preparation and the byte-for-byte / completeness
discipline:
- prepare packages one self-contained operator prompt per roster row from a
  synthetic source, with an IDENTICAL instruction body across all rows (no
  guidance content anywhere), deterministic regeneration (byte-identical
  prompts, manifest, plan), a prompt manifest of hashes, and a fixed 19-row
  executed-roster plan with `direct` condition run ids (Task 018: the
  planned 11-row roster expanded during collection into the reconciled
  executed set);
- collect registers an external output byte-for-byte, refuses to overwrite,
  rejects unknown runs, and records status + the practical free-access
  verdict; collect-session extracts the raw reply embedded in an author
  session file (prompt + reply in one markdown file) after validating the
  instruction body against the canonical prompt;
- verify runs the structural completeness gate (size floor, end marker
  KONIEC/KONEC/KONĖC, ISV-tolerant story-name stems, head sanity) and
  classifies outputs as complete / partial / failed, never deleting or
  repairing them;
- evaluate refuses a 'failed' intake without --force and writes the Task 008
  summary plus the orthographic audit (subprocess faked);
- no fabricated outputs: nothing is evaluated without a collected file.
"""
import importlib.util
import json
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
ROOT = SCRIPTS.parent

RUN_ID = "2099-01-01__openai__gpt-5.6-luna__thinkoff__direct"
RUN2_ID = "2099-01-01__openai__gpt-5.6-luna__thinkon__direct"
RUN3_ID = "2099-01-01__openai__gpt-isv-teacher__unknown__direct"
RUN4_ID = "2099-01-01__anthropic__claude__sonnet-5__direct"
RUN5_ID = ("2099-01-01__deepseek__deepseek-v3-expert__deepthinkoff__direct")

_SOURCE = (
    "Opowieść o Słów, Które Były Jak Siostry\n"
    "Prolog\n\n"
    "Bronisława, Teofil i Julianna živili v Międzyrzeczu. Przemysława prišla. "
    "Antoni molčal.\n" * 8 +
    "\nKONIEC\n"
)

_COMPLETE = (
    "Povědka o slovah, ktore byle kako sestry\n"
    "Prolog\n\n"
    + ("Bronisława, Teofil i Julianna živili v Medžurečju. Przemysława "
       "prišla k nih. Antoni molčal.\n") * 400
    + "\nKONIEC\n"
)


@pytest.fixture(scope="module")
def run_mod():
    spec = importlib.util.spec_from_file_location(
        "run_exp004_phase1", SCRIPTS / "run_exp004_phase1.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture()
def setup(run_mod, tmp_path, monkeypatch):
    """Temp EXP-004: synthetic source + real committed base instruction."""
    exp = tmp_path
    inp = exp / "input"
    prompts = exp / "operator-prompts"
    outputs = exp / "outputs"
    inp.mkdir()
    prompts.mkdir()
    outputs.mkdir()
    src = inp / "source.txt"
    src.write_text(_SOURCE, encoding="utf-8")
    monkeypatch.setattr(run_mod, "EXP", exp)
    monkeypatch.setattr(run_mod, "INPUT_DIR", inp)
    monkeypatch.setattr(run_mod, "OPERATOR_PROMPTS", prompts)
    monkeypatch.setattr(run_mod, "OUTPUTS_DIR", outputs)
    monkeypatch.setattr(run_mod, "EXP003_SOURCE", src)
    monkeypatch.setattr(
        run_mod, "EXP003_SOURCE_SHA256",
        run_mod.sha256_bytes(_SOURCE.encode("utf-8")))
    # real committed template: contains {STORY}, no copyrighted content
    monkeypatch.setattr(
        run_mod, "BASE_INSTRUCTION",
        ROOT / "experiments" / "exp004-modelscreen" / "base_instruction.txt")
    return exp


def prepare(run_mod, setup, date="2099-01-01", force=False):
    rc = run_mod.run_prepare(date, force)
    assert rc == 0
    return setup / "outputs" / "plan.json"


# ---------------------------------------------------------------------------
# prepare
# ---------------------------------------------------------------------------

def test_prepare_packages_19_rows_with_identical_instruction(run_mod, setup):
    plan = json.loads(prepare(run_mod, setup).read_text(encoding="utf-8"))
    assert len(plan["runs"]) == 19
    assert {r["model"] for r in plan["runs"]} == {
        "gpt-5.6-luna", "gpt-isv-teacher", "claude", "gemini-3.1-pro",
        "gemini-3.6-flash", "deepseek-v3-instant", "deepseek-v3-expert",
        "grok", "kimi", "qwen-3.8-max", "qwen-3.7-plus", "glm"}
    bodies = []
    for r in plan["runs"]:
        pf = setup / "operator-prompts" / Path(r["prompt_file"]).name
        text = pf.read_text(encoding="utf-8")
        assert "Translate the Polish story below into Interslavic" in text
        rules = text.split("## Rules")[1].split("## Source text")[0].lower()
        assert "scaffold" not in rules and "candidate" not in rules
        assert "morphology" not in rules and "grammar" not in rules
        assert r["condition"] == "direct"
        # instruction + story body = everything after the 2nd '---'
        body = "\n---\n".join(text.split("\n---\n")[2:])
        bodies.append(body)
    # every row: identical instruction+source body (headers differ only)
    assert all(b == bodies[0] for b in bodies)


def test_prepare_deterministic_and_plan_run_ids(run_mod, setup):
    prepare(run_mod, setup)
    def snap():
        d = {}
        for name in ("plan.json", "manifest.json"):
            p = setup / "outputs" / name if name == "plan.json" else \
                setup / "operator-prompts" / name
            d[name] = p.read_bytes()
        for pf in sorted((setup / "operator-prompts").glob("*.md")):
            d[pf.name] = pf.read_bytes()
        return d
    first = snap()
    prepare(run_mod, setup, force=True)
    assert snap() == first
    plan = json.loads((setup / "outputs" / "plan.json").read_text(
        encoding="utf-8"))
    assert plan["runs"][0]["run_id"] == RUN_ID
    assert all(r["run_id"].endswith("__direct") for r in plan["runs"])
    manifest = json.loads((setup / "operator-prompts" / "manifest.json")
                          .read_text(encoding="utf-8"))
    assert len(manifest["files"]) == 19
    for f in manifest["files"]:
        pf = setup / "operator-prompts" / f["file"]
        assert run_mod.sha256_bytes(pf.read_bytes()) == f["prompt_sha256"]


def test_prepare_records_conditional_rows_and_exclusions_in_plan(
        run_mod, setup):
    plan = json.loads(prepare(run_mod, setup).read_text(encoding="utf-8"))
    gemini = next(r for r in plan["runs"]
                  if r["model"] == "gemini-3.1-pro")
    glm = next(r for r in plan["runs"] if r["model"] == "glm")
    assert "conditional" in gemini and "conditional" in glm
    assert gemini["conditional"] and glm["conditional"]
    # variant rows carry variant_of and same provider/model
    off = next(r for r in plan["runs"]
               if r["model"] == "gpt-5.6-luna" and r["model_version"] == "thinkoff")
    on = next(r for r in plan["runs"]
              if r["model"] == "gpt-5.6-luna" and r["model_version"] == "thinkon")
    assert on["variant_of"] == off["model_version"]
    assert off["provider"] == on["provider"] == "openai"


def test_prepare_never_overwrites_plan_without_force(run_mod, setup):
    prepare(run_mod, setup)
    rc = run_mod.run_prepare("2099-01-01")
    assert rc == 2  # plan exists -> refuses


# ---------------------------------------------------------------------------
# collect
# ---------------------------------------------------------------------------

def test_collect_byte_for_byte_and_meta(run_mod, setup):
    prepare(run_mod, setup)
    reply = setup / "reply.txt"
    data = _COMPLETE.encode("utf-8")
    reply.write_bytes(data)
    rc = run_mod.run_collect(
        RUN_ID, reply, "2099-01-01", "gpt-5.6-luna", "openai", "thinkoff",
        "thinking OFF", "collected_external_output", "pass",
        "complete in one free session")
    assert rc == 0
    out_dir = setup / "outputs" / RUN_ID
    assert (out_dir / "output.txt").read_bytes() == data
    meta = json.loads((out_dir / "meta.json").read_text(encoding="utf-8"))
    assert meta["status"] == "collected_external_output"
    assert meta["access"]["filter_verdict"] == "pass"
    assert meta["access"]["quota_observed"] == "complete in one free session"
    assert meta["output"]["sha256"] == run_mod.sha256_bytes(data)
    assert meta["condition"] == "direct"
    assert meta["model"] == "gpt-5.6-luna"
    assert "resources" in meta


def test_collect_refuses_overwrite_and_unknown_run(run_mod, setup):
    prepare(run_mod, setup)
    reply = setup / "reply.txt"
    reply.write_bytes(_COMPLETE.encode("utf-8"))
    assert run_mod.run_collect(RUN_ID, reply, "2099-01-01", "unknown",
                               "unknown", "unknown") == 0
    reply2 = setup / "reply2.txt"
    reply2.write_bytes(b"other")
    assert run_mod.run_collect(RUN_ID, reply2, "2099-01-01", "unknown",
                               "unknown", "unknown") == 2  # no overwrite
    assert run_mod.run_collect("2099-01-01__openai__nope__x__direct",
                               reply2, "2099-01-01", "unknown", "unknown",
                               "unknown") == 2  # unknown roster row


# ---------------------------------------------------------------------------
# collect-session (Task 018: raw reply embedded in an author session file)
# ---------------------------------------------------------------------------

def _author_session(run_mod, setup, row_prompt_file, reply_text):
    """Simulate the author's save: canonical prompt with its final two lines
    ('Return the complete Interslavic translation ...') replaced by the raw
    model reply."""
    pf = setup / "operator-prompts" / row_prompt_file
    text = pf.read_text(encoding="utf-8")
    assert text.endswith("else.\n")
    cut = text.rfind("Return the complete")
    return text[:cut].encode("utf-8") + reply_text.encode("utf-8")


def test_collect_session_extracts_reply_byte_for_byte(run_mod, setup):
    prepare(run_mod, setup)
    session = setup / "session.md"
    session.write_bytes(_author_session(run_mod, setup,
                                        "01-gpt-5.6-luna-thinkoff.md",
                                        _COMPLETE))
    rc = run_mod.run_collect_session(
        RUN_ID, session, "2099-01-01", "unknown", "unknown", "unknown",
        "unknown", "collected_external_output", "pass",
        "complete in one free session", "")
    assert rc == 0
    out_dir = setup / "outputs" / RUN_ID
    assert (out_dir / "output.txt").read_text(
        encoding="utf-8") == _COMPLETE
    meta = json.loads((out_dir / "meta.json").read_text(encoding="utf-8"))
    assert meta["session"]["name"] == "session.md"
    assert meta["output"]["sha256"] == run_mod.sha256_bytes(
        _COMPLETE.encode("utf-8"))
    assert meta["access"]["filter_verdict"] == "pass"
    # session file itself untouched
    assert session.read_bytes().startswith(b"# EXP-004")


def test_collect_session_refuses_overwrite_and_unknown_run(run_mod, setup):
    prepare(run_mod, setup)
    session = setup / "session.md"
    session.write_bytes(_author_session(run_mod, setup,
                                        "01-gpt-5.6-luna-thinkoff.md",
                                        _COMPLETE))
    assert run_mod.run_collect_session(
        RUN_ID, session, "2099-01-01", "unknown", "unknown", "unknown") == 0
    assert run_mod.run_collect_session(
        RUN_ID, session, "2099-01-01", "unknown", "unknown", "unknown") == 2
    assert run_mod.run_collect_session(
        "2099-01-01__openai__nope__x__direct", session, "2099-01-01",
        "unknown", "unknown", "unknown") == 2


def test_collect_session_rejects_altered_instruction_body(run_mod, setup):
    prepare(run_mod, setup)
    raw = _author_session(run_mod, setup, "01-gpt-5.6-luna-thinkoff.md",
                          _COMPLETE)
    # tamper with the instruction text (would break the clean-baseline
    # invariant if the author had modified the instruction)
    raw = raw.replace(b"Translate the Polish story below into Interslavic",
                      b"Translate the Polish fable below into Interslavic")
    session = setup / "session.md"
    session.write_bytes(raw)
    assert run_mod.run_collect_session(
        RUN_ID, session, "2099-01-01", "unknown", "unknown", "unknown") == 2
    assert not (setup / "outputs" / RUN_ID / "output.txt").exists()


# ---------------------------------------------------------------------------
# verify (completeness gate)
# ---------------------------------------------------------------------------

def test_verify_complete_partial_failed(run_mod, setup):
    prepare(run_mod, setup)

    def register(rid, text, status, access="pass"):
        reply = setup / f"reply-{rid.split('__')[2]}.txt"
        reply.write_text(text, encoding="utf-8")
        assert run_mod.run_collect(rid, reply, "2099-01-01", "unknown",
                                   "unknown", "unknown", "unknown", status,
                                   access) == 0
        out_dir = setup / "outputs" / rid
        assert run_mod.run_verify(rid) == 0
        return json.loads((out_dir / "intake.json").read_text(
            encoding="utf-8"))

    # complete: size >= floor(0.6 * source bytes), end marker, names
    intake = register(RUN_ID, _COMPLETE, "collected_external_output")
    assert intake["verdict"] == "complete"

    # partial: real translation but no end marker
    intake = register(RUN2_ID, _COMPLETE.replace("\nKONIEC\n", "\n...\n"),
                      "collected_partial_output")
    assert intake["verdict"] == "partial"

    # failed: not a translation (short service-error page)
    intake = register(RUN3_ID, "Przepraszamy, wystąpił błąd serwisu.",
                      "failed_external_output")
    assert intake["verdict"] == "failed"

    # empty output preserved and classified failed, never deleted
    out_dir = setup / "outputs" / RUN4_ID
    intake = register(RUN4_ID, "", "failed_external_output")
    assert intake["verdict"] == "failed"
    assert (out_dir / "output.txt").read_bytes() == b""


def test_gate_accepts_transliterated_names_and_konce_end_marker(
        run_mod, setup):
    """EXP-004 Phase 1 models transliterate Polish proper names
    (Bronisława -> Bronislava, Przemysław -> Przemyslava, Antoni -> Antonij,
    Julianna -> Julijana) and close with 'KONEC'. The gate must still pass
    such a complete translation (Task 018 calibration)."""
    prepare(run_mod, setup)
    reply = setup / "reply-isv.txt"
    text = (_COMPLETE
            .replace("Bronisława", "Bronislava")
            .replace("Przemysława", "Przemyslava")
            .replace("Antoni", "Antonij")
            .replace("Julianna", "Julijana")
            .replace("\nKONIEC\n", "\nKONEC\n"))
    reply.write_text(text, encoding="utf-8")
    assert run_mod.run_collect(RUN_ID, reply, "2099-01-01", "unknown",
                               "unknown", "unknown") == 0
    assert run_mod.run_verify(RUN_ID) == 0
    intake = json.loads((setup / "outputs" / RUN_ID / "intake.json")
                        .read_text(encoding="utf-8"))
    assert intake["verdict"] == "complete"
    assert intake["checks"]["names_present"] == 5
    assert intake["checks"]["end_marker"] is True


def test_verify_detects_tamper(run_mod, setup):
    prepare(run_mod, setup)
    out_dir = setup / "outputs" / RUN5_ID
    reply = setup / "reply.txt"
    reply.write_bytes(_COMPLETE.encode("utf-8"))
    assert run_mod.run_collect(RUN5_ID, reply, "2099-01-01", "unknown",
                               "unknown", "unknown") == 0
    # tamper with the collected raw output after collect
    (out_dir / "output.txt").write_bytes(_COMPLETE.encode("utf-8") + b"X")
    rc = run_mod.run_verify(RUN5_ID)
    assert rc == 1  # sha mismatch reported
    intake = json.loads((out_dir / "intake.json").read_text(
        encoding="utf-8"))
    assert intake["integrity_errors"]


# ---------------------------------------------------------------------------
# evaluate
# ---------------------------------------------------------------------------

def test_evaluate_refuses_failed_without_force_and_writes_summary(
        run_mod, setup, monkeypatch):
    prepare(run_mod, setup)
    out_dir = setup / "outputs" / RUN_ID
    reply = setup / "reply.txt"
    reply.write_bytes(_COMPLETE.encode("utf-8"))
    assert run_mod.run_collect(RUN_ID, reply, "2099-01-01", "unknown",
                               "unknown", "unknown", "unknown",
                               "collected_external_output", "pass") == 0
    # run the gate first -> complete
    assert run_mod.run_verify(RUN_ID) == 0

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

    assert run_mod.run_evaluate(RUN_ID) == 0
    ev = json.loads((out_dir / "evaluation.json").read_text(
        encoding="utf-8"))
    assert ev["usable"] is True
    assert ev["metrics"]["canonical_coverage"] == 0.8
    assert (out_dir / "orthography.json").is_file()
    assert (out_dir / "evaluation.md").is_file()

    # failed intake refuses evaluation
    (out_dir / "output.txt").write_text("Blad serwisu.", encoding="utf-8")
    meta = json.loads((out_dir / "meta.json").read_text(encoding="utf-8"))
    meta["output"]["sha256"] = run_mod.sha256_bytes(b"Blad serwisu.")
    meta["status"] = "failed_external_output"
    (out_dir / "meta.json").write_text(json.dumps(meta), encoding="utf-8")
    assert run_mod.run_verify(RUN_ID) == 0
    assert run_mod.run_evaluate(RUN_ID) == 2
    assert run_mod.run_evaluate(RUN_ID, force=True) == 0


# ---------------------------------------------------------------------------
# status / roster
# ---------------------------------------------------------------------------

def test_status_and_roster_empty_and_with_run(run_mod, setup):
    prepare(run_mod, setup)
    assert run_mod.run_status() == 0
    assert run_mod.run_roster() == 0
    roster = json.loads((setup / "outputs" / "roster.json").read_text(
        encoding="utf-8"))
    assert len(roster["rows"]) == 19
    assert roster["rows"][0]["collected"] is False
