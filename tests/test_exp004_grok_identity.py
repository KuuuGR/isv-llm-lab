"""EXP-004 Grok configuration-identity canonicalization tests (SODA Task
031).

Task 031 canonicalizes the *rendered* Grok configuration identity to
**"Grok 4.5 Fast"** (operator-reported identity "Grok 4.5, built by xAI
(fast)", evidence `operator_reported` — never upgraded to independently
verified) while preserving historical provenance:

- Phase-1 / Phase-2A / phase-repeat run ids and prompt filenames that
  were recorded with the `unknown` version token stay byte-identical
  (they are the record); the canonical mapping is exposed as an alias
  (`xai__grok__unknown` → `xai__grok__fast`) via
  `run_exp004_phase1.grok_run_id_alias`;
- forward-looking kits (Phase-2B HIGH and future regimes) are born
  canonical: `canonical_grok_row` applies the overlay so new run ids /
  prompt files / headers read `grok…fast` / "Grok 4.5 Fast";
- display/analysis layers (`analyze_exp004_repeats.py`,
  `build_assistant_research_bundle.py`) render the canonical label and
  expose canonical fields additively — recorded values are untouched;
- no Grok Build run exists in repository evidence; the EXP-001/002-era
  Grok condition (genuinely unannotated) stays `unknown`.

These tests never modify raw outputs and never recompute metrics.
"""
import importlib.util
import json
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
ROOT = SCRIPTS.parent

P2A_MANIFEST = ROOT / "experiments" / "exp004-modelscreen" / "phase2a" \
    / "operator-prompts" / "manifest.json"
P2B_MANIFEST = ROOT / "experiments" / "exp004-modelscreen" / "phase2b" \
    / "operator-prompts" / "manifest.json"
P2B_PLAN = ROOT / "experiments" / "exp004-modelscreen" / "phase2b" \
    / "outputs" / "plan.json"
BUNDLE_RESULTS = ROOT / "experiments" / "exp004-modelscreen" \
    / "assistant-research-bundle" / "results.json"


def _load(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def p1():
    return _load("run_exp004_phase1", "run_exp004_phase1.py")


@pytest.fixture(scope="module")
def analyze():
    return _load("analyze_exp004_repeats", "analyze_exp004_repeats.py")


@pytest.fixture(scope="module")
def bundle():
    return _load("build_assistant_research_bundle",
                 "build_assistant_research_bundle.py")


# ---------------------------------------------------------------------------
# canonical constants / helpers (scripts/run_exp004_phase1.py)
# ---------------------------------------------------------------------------

def test_canonical_constants(p1):
    assert p1.GROK_HISTORICAL_KEY == ("xai", "grok", "unknown")
    assert p1.GROK_CANONICAL_MODEL_VERSION == "fast"
    assert p1.GROK_CANONICAL_LABEL == "Grok 4.5 Fast"
    assert p1.GROK_CANONICAL_IDENTITY == "Grok 4.5, built by xAI (fast)"
    assert p1.GROK_IDENTITY_EVIDENCE == "operator_reported"
    assert p1.GROK_CANONICAL_ALIAS == "xai__grok__fast"


def test_phase1_historical_row_recognized_and_overlay_is_pure(p1):
    """Phase-1 current-line Grok roster row (recorded 'unknown') is
    detected; the canonical overlay is additive and never mutates the
    recorded row (provenance preserved)."""
    row = next(r for r in p1.ROSTER
               if (r["provider"], r["model"], r["model_version"])
               == p1.GROK_HISTORICAL_KEY)
    assert p1.is_grok_historical(row)
    assert row["model_version"] == "unknown"      # recorded, preserved
    assert row["label"] == "Grok"                 # recorded, preserved

    over = p1.canonical_grok_row(row)
    assert over is not row                       # copy, not mutation
    assert row["model_version"] == "unknown"     # original untouched
    assert over["model_version"] == "fast"
    assert over["label"] == "Grok 4.5 Fast"
    assert over["generation_parameters"] == "4.5 (fast)"
    # only the canonical overlay keys differ; everything else (evidence,
    # interface, session file, metrics if any) is identical
    diff = {k for k in row if row[k] != over.get(k)}
    assert diff <= {"model_version", "label", "generation_parameters"}

    # non-Grok rows are not touched by the overlay
    non_grok = next(r for r in p1.ROSTER
                    if (r["provider"], r["model"], r["model_version"])
                    != p1.GROK_HISTORICAL_KEY)
    assert p1.canonical_grok_row(non_grok) == non_grok


def test_run_id_alias_maps_only_historical_grok(p1):
    """Historical Grok run ids keep their recorded 'unknown' token; the
    canonical alias maps them to the 'fast' representation for
    lookup/rendering. Non-Grok run ids are never rewritten."""
    historical = [
        # Phase 1 (Task 018)
        "2026-09-06__xai__grok__unknown__direct",
        # Phase 2A (Task 021)
        "2026-09-07__xai__grok__unknown__p2a-ctl",
        "2026-09-07__xai__grok__unknown__p2a-primed",
        # Phase repeat (Task 025/026)
        "2026-09-08__xai__grok__unknown__direct__r01",
        "2026-09-08__xai__grok__unknown__direct__r03",
        "2026-09-08__xai__grok__unknown__primed__r02",
    ]
    for rid in historical:
        alias = p1.grok_run_id_alias(rid)
        assert "__xai__grok__unknown__" in rid          # recorded intact
        assert alias == rid.replace("__xai__grok__unknown__",
                                    "__xai__grok__fast__")
        assert "__xai__grok__fast__" in alias
        assert alias != rid

    other = [
        "2026-09-06__openai__gpt-5.6-luna__thinkoff__direct",
        "2026-09-07__anthropic__claude__sonnet-5__p2a-primed",
        "exp002__2026-08-31__unknown__grok__unknown",   # early era: format has no double underscore xai segment
    ]
    for rid in other:
        assert p1.grok_run_id_alias(rid) == rid          # never rewritten


# ---------------------------------------------------------------------------
# committed Phase-2A manifest: historical 'unknown' preserved with alias
# ---------------------------------------------------------------------------

def test_phase2a_committed_manifest_historical_unknown_preserved(p1):
    """The committed Phase-2A manifest records the Grok runs with the
    genuine 'unknown' version token (generation-time state). Task 031
    does not rewrite them: the recorded run ids and prompt filenames are
    intact and the canonical mapping is exposed only as an alias."""
    manifest = json.loads(P2A_MANIFEST.read_text(encoding="utf-8"))
    grok = [f for f in manifest["files"]
            if "__xai__grok__unknown__" in f["run_id"]]
    assert len(grok) == 3                      # ctl + primed msg1 + msg2
    for f in grok:
        assert "grok-unknown" in f["file"]           # filename preserved
        assert "__xai__grok__unknown__" in f["run_id"]
        # canonical alias exists for the recorded id
        alias = p1.grok_run_id_alias(f["run_id"])
        assert alias != f["run_id"]
        assert "__xai__grok__fast__" in alias
        assert alias.replace("__xai__grok__fast__",
                             "__xai__grok__unknown__") == f["run_id"]


# ---------------------------------------------------------------------------
# display layers: canonical label, recorded values untouched
# ---------------------------------------------------------------------------

def test_repeats_display_label_canonical(analyze):
    """The repeats-analysis display maps the historical Grok row to the
    canonical label; every other configuration renders its own label."""
    assert analyze._display_label("xai", "grok", "unknown",
                                  "Grok") == "Grok 4.5 Fast"
    assert analyze._display_label("xai", "grok", "unknown",
                                  "Grok (unknown (unknown))") \
        == "Grok 4.5 Fast"
    assert analyze._display_label("anthropic", "claude", "sonnet-5-medium",
                                  "Claude Sonnet 5 — Medium (default)") \
        == "Claude Sonnet 5 — Medium (default)"
    assert analyze.GROK_CANONICAL_LABEL == "Grok 4.5 Fast"
    assert analyze.GROK_HISTORICAL_KEY == ("xai", "grok", "unknown")


def test_bundle_helpers_canonical(bundle):
    assert bundle._is_grok_historical("xai", "grok", "unknown") is True
    assert bundle._is_grok_historical("xai", "grok", "fast") is False
    assert bundle._is_grok_historical("anthropic", "claude",
                                      "sonnet-5") is False
    assert bundle._canonical_label("xai", "grok", "unknown",
                                   "Grok") == "Grok 4.5 Fast"
    assert bundle._canonical_label("anthropic", "claude", "sonnet-5",
                                   "Claude Sonnet 5") == "Claude Sonnet 5"
    assert bundle.GROK_CANONICAL_ALIAS_ID == "xai__grok__fast"
    assert bundle.GROK_IDENTITY_EVIDENCE == "operator_reported"
    assert bundle.GROK_CANONICAL_LABEL == "Grok 4.5 Fast"


def test_bundle_committed_records_canonical_additive_only(bundle):
    """Committed bundle records: Grok rows carry the canonical label /
    alias / identity-evidence fields additively while the recorded run id
    keeps its historical 'unknown' token and the recorded model token
    stays 'grok' (no rewriting, no metric recomputation)."""
    results = json.loads(BUNDLE_RESULTS.read_text(encoding="utf-8"))
    records = results["records"]
    grok = [r for r in records if r["provider"] == "xai"
            and r["model"] == "grok"]
    assert len(grok) == 6                       # repeats, 6 Grok runs
    for r in grok:
        assert r["canonical_config_label"] == "Grok 4.5 Fast"
        assert r["canonical_configuration_id"] == "xai__grok__fast"
        assert r["identity_evidence"] == "operator_reported"
        assert r["operator_reported_identity"] \
            == "Grok 4.5, built by xAI (fast)"
        assert r["label"] == "Grok 4.5 Fast"          # rendered canonical
        assert "__xai__grok__unknown__" in r["run_id"]   # recorded intact
        assert r["model"] == "grok"
    # every canonicalization-relevant key is present on all 120 records
    for r in records:
        assert "canonical_config_label" in r
        assert "canonical_configuration_id" in r
        assert "identity_evidence" in r


# ---------------------------------------------------------------------------
# committed Phase-2B kit (regenerated, Task 031): born canonical
# ---------------------------------------------------------------------------

def test_phase2b_committed_kit_born_canonical(p1):
    """The never-collected Phase-2B HIGH kit was regenerated with the
    canonical Grok identity: manifest + plan contain only
    'grok…fast' run ids / files, and no historical 'unknown' Grok
    artifact remains in the committed kit records."""
    manifest = json.loads(P2B_MANIFEST.read_text(encoding="utf-8"))
    grok = [f for f in manifest["files"]
            if "__p2b-high__xai__grok__" in f["run_id"]]
    assert len(grok) == 9
    for f in grok:
        assert "grok-fast" in f["file"]
        assert "unknown" not in f["file"]
        assert "__xai__grok__fast__" in f["run_id"]
        assert "unknown" not in f["run_id"]
        assert p1.grok_run_id_alias(f["run_id"]) == f["run_id"]  # already canonical

    plan = json.loads(P2B_PLAN.read_text(encoding="utf-8"))
    blob = json.dumps(plan, ensure_ascii=False) + \
        json.dumps(manifest, ensure_ascii=False)
    assert "grok-unknown" not in blob
    assert "xai__grok__unknown" not in blob
    assert "__xai__grok__fast__" in blob
