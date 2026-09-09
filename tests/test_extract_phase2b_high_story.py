"""EXP-004 Phase 2B — HIGH-overlap story-bank extraction tests (SODA Task
030).

scripts/extract_phase2b_high_story.py:
- the correct HIGH-overlap story section (`# 3. Iskra i Wieloryb — wersja
  z oryginalnymi nazwami`) is extracted from a multi-story Markdown bank;
- sections 1, 2 and 4 (LOW `Podkłady`) never leak into the extraction;
- only Markdown structural markers are removed (`# <n>.` section number,
  `## ` heading prefixes, `> ` song prefixes, `*` emphasis, `---` rules) —
  all story text lines are preserved exactly; title line added;
- blank runs are collapsed; output is deterministic (byte-identical on
  regeneration);
- the frozen/recorded story hash is stable; the extractor output feeds
  freeze-story → prepare (42-run HIGH kit) unchanged.
"""
import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
ROOT = SCRIPTS.parent

TITLE = "Iskra i Wieloryb — wersja z oryginalnymi nazwami"
STORY_ID = "iskra-wieloryb-original-names"
CLASSIFICATION = "high_overlap_corpus_inspired"
DATE = "2099-03-03"

# Real-author bank (local, outside the repo). Tests skip cleanly when the
# file is absent on a machine without the author's material.
BANK_FILE = Path(
    "/Users/admin/Developer/MiscellaneousNotes/AwesomeVault/!Apps/App "
    "Ideas/alephBits/Books/InterslavicTesty.md")
# Pinned 2026-09-09 extraction of section 3 (30 061 bytes, 440 lines).
EXPECTED_STORY_SHA = \
    "ab8a0dcf7352789c09c4aca132c086999c861407e4cd682ee9414aab5b792f63"

# Synthetic bank mirroring the real file's structure (4 H1 sections,
# `##` headings, `---` rules, `> *song*` blockquotes, markdown title).
_BANK = """# 1. Opowieść o Faktach, Które Były Jak Klucze

## Prolog

W miasteczku mieszkała trójka dzieci – **Anastazja**, **Władysław** i **Zofia**.

---

## Akt Pierwszy

Zegarmistrz Hieronim uczył dzieci słuchać tykania.

#  2. Opowieść o sygnale

## Rozdział pierwszy

Anna słuchała sygnału nadajnika i nagrywała go na stary rejestrator.

# 3. Iskra i Wieloryb — wersja z oryginalnymi nazwami

## Prolog: O tym, co mówią ludzie

Ludzie mówią, że tamtego dnia było bardzo spokojnie. Przyszła Szkarłatna Iskra, a związał nas śnieg.

Moja Iskra, a związał nas śnieg.

---

## Akt I: Lodowa Klątwa

— To już półtora roku? — zapytał Benedykt.

Danek bawił się kluczem po dziadku. Zimorodzice czekały na serce ziemi.

Na kamieniu wyryte były słowa: *„Tu leży serce. Obudź je, jeśli masz Iskrę."*

---

## Akt II: Pieśń, która prowadzi

Mężczyzna uderzył w struny i izba ucichła:

> *Ten okręt znają wszyscy ludzie,*
> *a jego imię brzmi Herbata.*
> *On idzie po morzu, wieje wiatr,*
> *och, płyniemy brać w świat!*

Ludzie odwrócili się w jego stronę.

---

## Epilog: Ciepło

Ludzie idą na Mogiłę Szronu i kładą dłonie na kamieniu. A moja? Moja dopiero się zaczyna.

# 4. Podkłady

Katarzyna odłożyła teczkę z aktami osobowymi i przeciągnęła się.

Dziadek był kolejarzem i mówił, że ziemia pamięta.
"""


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


@pytest.fixture(scope="module")
def ex_mod():
    spec = importlib.util.spec_from_file_location(
        "extract_phase2b_high_story", SCRIPTS / "extract_phase2b_high_story.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_extracts_high_story_only(ex_mod):
    out = ex_mod.extract_story(_BANK)
    assert out.startswith(TITLE + "\n")
    # section 3 content present
    for marker in ("Prolog: O tym, co mówią ludzie",
                   "Szkarłatna Iskra", "Mogiłę Szronu",
                   "Akt II: Pieśń, która prowadzi",
                   "Epilog: Ciepło", "A moja? Moja dopiero się zaczyna."):
        assert marker in out
    # sections 1, 2, 4 never leak
    for forbidden in ("Opowieść o Faktach", "Anastazja", "Hieronim",
                      "Opowieść o sygnale", "rejestrator", "Podkłady",
                      "Katarzyna", "kolejarzem"):
        assert forbidden not in out
    assert out.strip().endswith("A moja? Moja dopiero się zaczyna.")


def test_strips_markdown_markers_only(ex_mod):
    out = ex_mod.extract_story(_BANK)
    # no markdown structural markers remain
    for line in out.splitlines():
        assert not line.startswith("# ")
        assert not line.startswith("## ")
        assert not line.startswith("> ")
        assert line.strip() != "---"
        assert "*" not in line
    # song text survived as plain lines
    assert "\nTen okręt znają wszyscy ludzie,\na jego imię brzmi Herbata.\n" \
        in out
    # heading text preserved without the '## ' prefix
    assert "\nProlog: O tym, co mówią ludzie\n\n" in out
    assert "\nAkt I: Lodowa Klątwa\n\n" in out
    # inline italic content preserved without '*'
    assert "słowa: „Tu leży serce. Obudź je, jeśli masz Iskrę.\"" in out


def test_content_lines_preserved_exactly(ex_mod):
    """Every non-blank non-rule content line of section 3 survives
    byte-for-byte (only structural markers removed)."""
    lines = _BANK.splitlines()
    start = next(i for i, l in enumerate(lines)
                 if l.startswith("# 3. ") or "# 3. " in l and "Iskra" in l
                 or (l.startswith("# ") and "Iskra i Wieloryb" in l))
    end = next(i for i in range(start + 1, len(lines))
               if lines[i].startswith("# 4. "))
    raw_body = lines[start + 1:end]
    content = []
    for ln in raw_body:
        s = ln.strip()
        if not s or s == "---":
            continue
        if s.startswith("## "):
            s = s[3:]
        elif s.startswith("> "):
            s = s[2:]
        s = s.replace("*", "")
        content.append(s)
    out_lines = [l for l in ex_mod.extract_story(_BANK).splitlines()
                 if l.strip()]
    assert out_lines[0] == TITLE
    assert content == out_lines[1:], "content lines drifted"


def test_blank_runs_collapsed_and_trailing_newline(ex_mod):
    out = ex_mod.extract_story(_BANK)
    prev_blank = False
    for line in out.splitlines():
        if line.strip() == "":
            assert not prev_blank, "run of blank lines survived"
            prev_blank = True
        else:
            prev_blank = False
    assert out.endswith("\n") and not out.endswith("\n\n")


def test_extraction_deterministic(ex_mod):
    assert ex_mod.extract_story(_BANK) == ex_mod.extract_story(_BANK)


def test_title_constant(ex_mod):
    assert ex_mod.TITLE == TITLE
    assert ex_mod.STORY_ID == STORY_ID
    assert ex_mod.CLASSIFICATION == CLASSIFICATION


def test_cli_writes_deterministic_artifact(ex_mod, tmp_path, monkeypatch,
                                           capsys):
    bank = tmp_path / "bank.md"
    bank.write_text(_BANK, encoding="utf-8")
    out = tmp_path / "story.txt"
    monkeypatch.setattr("sys.argv", ["extract_phase2b_high_story",
                                     "--bank", str(bank), "--out", str(out)])
    rc = ex_mod.main()
    assert rc == 0
    data = out.read_bytes()
    assert _sha(data.decode("utf-8")) == _sha(ex_mod.extract_story(_BANK))
    # deterministic regeneration
    ex_mod.main()
    assert out.read_bytes() == data


def _p2b():
    spec = importlib.util.spec_from_file_location(
        "run_exp004_phase2b", SCRIPTS / "run_exp004_phase2b.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_extract_freeze_prepare_end_to_end(ex_mod, tmp_path, monkeypatch):
    """Extractor output → freeze-story → prepare: 42-run HIGH kit with the
    extracted story hash pinned in the plan (no LOW/unseen sections)."""
    p2b = _p2b()
    exp = tmp_path / "exp004"
    phase2b = exp / "phase2b"
    inp = phase2b / "input"
    versions = inp / "versions"
    prompts = phase2b / "operator-prompts"
    outputs = phase2b / "outputs"
    for d in (versions, prompts, outputs):
        d.mkdir(parents=True)
    corpus = tmp_path / "corpus.txt"
    corpus.write_text("=== REGISTER 1 ===\n\nLjudi govoret.\n",
                      encoding="utf-8")
    monkeypatch.setattr(p2b, "EXP", exp)
    monkeypatch.setattr(p2b, "PHASE2B", phase2b)
    monkeypatch.setattr(p2b, "INPUT_DIR", inp)
    monkeypatch.setattr(p2b, "VERSIONS_DIR", versions)
    monkeypatch.setattr(p2b, "OPERATOR_PROMPTS", prompts)
    monkeypatch.setattr(p2b, "OUTPUTS_DIR", outputs)
    monkeypatch.setattr(p2b.rep.p2a, "CORPUS_FILE", corpus)
    monkeypatch.setattr(
        p2b.rep, "AUTH_CORPUS_SHA256",
        p2b.rep.sha256_bytes(corpus.read_bytes()))

    bank = tmp_path / "bank.md"
    bank.write_text(_BANK, encoding="utf-8")
    extracted = tmp_path / "extracted-story.txt"
    extracted.write_text(ex_mod.extract_story(_BANK), encoding="utf-8")
    assert p2b.run_freeze_story(str(extracted), "v1",
                                "extracted from synthetic bank") == 0
    assert p2b.run_prepare(DATE) == 0
    plan = json.loads((outputs / "plan.json").read_text(encoding="utf-8"))
    assert plan["source"]["classification"] == CLASSIFICATION
    assert plan["source"]["sha256"] == _sha(extracted.read_text("utf-8"))
    assert plan["source"]["version"] == "v1"
    assert plan["counts"]["total_runs"] == 42
    assert all(r["regime"] == "high" for r in plan["runs"])


# ---------------------------------------------------------------------------
# real-author-bank check (skips cleanly when the local bank is absent)
# ---------------------------------------------------------------------------

@pytest.mark.skipif(not BANK_FILE.is_file(),
                    reason="author's story bank is local/outside the repo")
def test_real_bank_high_story_sha_pinned(ex_mod):
    """The frozen HIGH-overlap story (Task 030, 2026-09-09) extracted from
    the real author's bank has a pinned SHA-256 (30 061 bytes, 440 lines,
    section 3 only)."""
    text = ex_mod.extract_story(BANK_FILE.read_text(encoding="utf-8"))
    assert _sha(text) == EXPECTED_STORY_SHA
    assert len(text.encode("utf-8")) == 30_061
    assert len(text.splitlines()) == 440


@pytest.mark.skipif(not BANK_FILE.is_file(),
                    reason="author's story bank is local/outside the repo")
def test_real_bank_excludes_other_sections(ex_mod):
    text = ex_mod.extract_story(BANK_FILE.read_text(encoding="utf-8"))
    for forbidden in ("Opowieść o Faktach", "Opowieść o sygnale",
                      "Podkłady", "Katarzyna"):
        assert forbidden not in text
