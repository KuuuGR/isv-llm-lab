"""EXP-004 Phase 1 — collection-audit / reconciliation logic tests (Task 018).

Covers the read-only reconciliation evidence machinery:
- split_reply finds the prompt/reply boundary at the prompt's closing
  '## Output' marker;
- instruction_body isolates the clean-baseline invariant region;
- header_lines parses the author-typed declared identity;
- audit() scans a session directory, verifies every session file carries the
  canonical instruction body, counts replies/end markers, and detects
  duplicate replies (raw session files are never modified).
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
    "Bronisława, Teofil i Julianna živili v Międzyrzeczu. Przemysława prišla. "
    "Antoni molčal.\n" * 4 +
    "\nKONIEC\n"
)

_REPLY = (
    "Povědka o slovah, ktore byle kako sestry\n"
    "Prolog\n\n"
    + ("Bronisława, Teofil i Julianna živili v Medžurečju. Przemysława "
       "prišla k nih. Antoni molčal.\n") * 40
    + "\nKONEC\n"
)


@pytest.fixture(scope="module")
def audit_mod():
    spec = importlib.util.spec_from_file_location(
        "audit_exp004_collected", SCRIPTS / "audit_exp004_collected.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_split_reply_and_instruction_body(audit_mod):
    text = ("# header\n---\n"
            "Translate the Polish story below into Interslavic.\n"
            "## Source text (Polish)\n\nstorý text\n"
            "## Output\n\n")
    prefix, marker, reply = audit_mod.split_reply(text + "RAW REPLY TEXT\n")
    assert reply == "RAW REPLY TEXT\n"
    assert "## Output" in marker
    assert prefix.endswith("storý text\n")
    body = audit_mod.instruction_body(text)
    assert body.endswith("## Output")
    assert body.startswith("Translate the Polish story below")
    # a reply that itself contains '## Output' still splits at the last one
    prefix2, _, reply2 = audit_mod.split_reply(text + "head\n## Output\nx")
    assert reply2 == "x"


def test_header_lines(audit_mod):
    text = ("# title\n> copy\n---\n"
            "Experiment ID: EXP-004\n"
            "Target model: Claude Sonnet 5 (max)\n"
            "Model version / settings: sonnet-5 max\n"
            "Provider / interface: anthropic / Claude (web)\n"
            "conditional filter: only if practical web access\n"
            "---\nbody")
    hdr = audit_mod.header_lines(text)
    assert hdr["Experiment ID"] == "EXP-004"
    assert hdr["Target model"] == "Claude Sonnet 5 (max)"
    assert hdr["Model version"] == "sonnet-5 max"
    assert hdr["Provider"].startswith("anthropic")
    assert "conditional filter" in hdr


def test_audit_scans_sessions_and_detects_duplicates(audit_mod, tmp_path,
                                                     monkeypatch):
    """End-to-end audit on a temp exp dir: canonical package generated into
    the temp operator-prompts, session files assembled like the author's,
    audit() must verify canonical bodies and flag a duplicate reply."""
    exp = tmp_path / "exp"
    inp = exp / "input"
    prompts = exp / "operator-prompts"
    sessions = exp / "collected-sessions"
    (inp).mkdir(parents=True)
    prompts.mkdir()
    sessions.mkdir()
    src = inp / "source.txt"
    src.write_text(_SOURCE, encoding="utf-8")
    monkeypatch.setattr(audit_mod, "EXP", exp)
    monkeypatch.setattr(audit_mod, "SESSION_DIR", sessions)
    # regenerate canonical prompts inside the temp package
    text = audit_mod.canonical_prompts()  # uses ROSTER + tmp EXP source
    canon = next(iter(text.values()))
    cut = canon.rfind("Return the complete")
    head = canon[:cut]
    # two distinct sessions + one duplicate reply
    (sessions / "01-model-a.md").write_bytes(
        head.encode("utf-8") + _REPLY.encode("utf-8"))
    (sessions / "02-model-b.md").write_bytes(
        head.encode("utf-8") + _REPLY.replace("Prolog", "Prolog II")
        .encode("utf-8"))
    (sessions / "03-model-c.md").write_bytes(
        head.encode("utf-8") + _REPLY.encode("utf-8"))
    result = audit_mod.audit()
    assert result["summary"]["files_scanned"] == 3
    assert result["summary"]["files_with_reply"] == 3
    assert result["summary"]["files_with_end_marker"] == 3
    assert result["summary"]["files_with_noncanonical_body"] == []
    # duplicate groups: 01 and 03 carry the same reply bytes
    dup = result["duplicate_replies"]
    assert len(dup) == 1
    files = next(iter(dup.values()))
    assert set(files) == {"01-model-a.md", "03-model-c.md"}
    # raw session files untouched
    assert (sessions / "01-model-a.md").read_bytes().startswith(b"# EXP")
    # audit artifacts written next to the sessions
    assert (sessions / "collection_audit.json").is_file()
    assert (sessions / "collection_audit.md").is_file()


def test_audit_flags_noncanonical_body(audit_mod, tmp_path, monkeypatch):
    exp = tmp_path / "exp"
    inp = exp / "input"
    prompts = exp / "operator-prompts"
    sessions = exp / "collected-sessions"
    inp.mkdir(parents=True)
    prompts.mkdir()
    sessions.mkdir()
    (inp / "source.txt").write_text(_SOURCE, encoding="utf-8")
    monkeypatch.setattr(audit_mod, "EXP", exp)
    monkeypatch.setattr(audit_mod, "SESSION_DIR", sessions)
    text = audit_mod.canonical_prompts()
    canon = next(iter(text.values()))
    cut = canon.rfind("Return the complete")
    # author-edited instruction (should never happen; must be flagged)
    bad = (canon[:cut].replace(
        "Translate the Polish story below into Interslavic",
        "Translate the Polish story below into Interslavic, using the "
        "candidate list") + _REPLY)
    (sessions / "01-x.md").write_text(bad, encoding="utf-8")
    result = audit_mod.audit()
    assert result["summary"]["files_with_noncanonical_body"] == ["01-x.md"]
