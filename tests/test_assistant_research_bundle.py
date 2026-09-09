"""Tests for scripts/build_assistant_research_bundle.py (SODA Task 027).

Two layers:

A. Hermetic — a small synthetic kit is built through the real generator
   and the standalone verifier must prove the bundle is internally
   consistent (counts, statuses, per-condition statistics recomputed from
   the run records, repeated deltas, aggregates) and deterministic
   (two fresh builds are byte-identical).

B. Standalone data-package test against the real committed bundle
   (experiments/exp004-modelscreen/assistant-research-bundle/) — the key
   Task-026 conclusions must be reconstructible from results.json +
   summary.json + audit.json alone, without the ~500 MB raw experiment
   directory. Skipped if the bundle is not present.
"""

import importlib.util
import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
BUNDLE = ROOT / "experiments" / "exp004-modelscreen" / \
    "assistant-research-bundle"

SHA = "0" * 64


def load_script(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def bundle_mod():
    return load_script("build_assistant_research_bundle",
                       SCRIPTS / "build_assistant_research_bundle.py")


# ---------------------------------------------------------------------------
# synthetic kit
# ---------------------------------------------------------------------------

def _plan_run(rid: str, condition: str, replicate: str, provider: str,
              model: str, version: str, label: str, primary: bool,
              corpus: str | None = None):
    return {
        "run_id": rid, "phase": "repeat", "condition": condition,
        "replicate": replicate, "primary": primary,
        "exploratory": not primary, "provider": provider, "model": model,
        "model_version": version, "label": label,
        "interface": "test-interface", "generation_parameters": "test",
        "custom_gpt": False, "identity_note": None,
        "prompt_files": [f"{condition}-{replicate}.md"],
        "translation_prompt_sha256": SHA,
        "source_sha256": SHA,
        "corpus_sha256": corpus,
        "phase1_baseline_run_id": "baseline", "phase2a_primed_run_id": None,
        "phase1_number": 1, "run_number": None, "status": "planned",
    }


def _roster_row(rid: str, condition: str, replicate: str, primary: bool,
                collected: bool, verdict: str | None = None,
                usable: bool = False, canonical: float | None = None,
                broader: float | None = None,
                unresolved: float | None = None,
                ortho_out: int | None = None):
    base = {
        "run_id": rid, "condition": condition, "replicate": replicate,
        "primary": primary, "exploratory": not primary,
        "label": "L", "model": "m", "provider": "p",
        "model_version": "v", "generation_parameters": "test",
    }
    if not collected:
        base.update({"status": None, "generation_date": None,
                     "interface_settings": None, "intake": None,
                     "usable": False, "metrics": None, "orthography": None})
        return base
    base.update({
        "status": "collected_external_output",
        "generation_date": "2026-09-08",
        "interface_settings": "not exposed",
        "intake": {"verdict": verdict, "reasons": [],
                   "checks": {"non_empty": True, "size_bytes": 100,
                              "size_floor": 50, "head_sane": True,
                              "end_marker": verdict == "complete",
                              "names_present": 3, "names_required": 3}},
        "usable": usable,
        "metrics": None if canonical is None else {
            "canonical_coverage": canonical,
            "broader_resource_supported_coverage": broader,
            "unresolved_rate": unresolved,
            "total_tokens": 100, "tokens_total": 110,
            "non_lexical_tokens": 10, "exact_dictionary_matches": 60,
            "morphologically_valid_forms": 1,
            "unresolved_forms": 40},
        "orthography": None if ortho_out is None else {
            "outside_inventory": ortho_out, "cyrillic": 0,
            "polish_specific": 0, "other_latin": 0, "other_script": 0,
            "unexpected_nonletters": 0, "total_chars": 1000,
            "allowed_letters": 900, "accepted_nonletters": 100},
    })
    return base


def _write_synthetic_kit(tmp: Path) -> None:
    """One primary config (a/b/c) with direct r01 usable, primed r01
    partial, primed r02 usable, primed r03 missing + one exploratory
    config (d/e/f) with direct r01 usable. planned 5 = 4 primary + 1
    exploratory; usable 3, partial 1, missing 1."""
    def rid(p, m, v, cond, rep):
        return f"2026-09-08__{p}__{m}__{v}__{cond}__{rep}"

    def make_run(prov, model, ver, cond, rep, primary):
        return _plan_run(rid(prov, model, ver, cond, rep), cond, rep,
                         prov, model, ver,
                         "Primary Cfg" if primary else "Expl Cfg",
                         primary,
                         corpus=SHA if cond == "primed" else None)

    p_runs = [
        make_run("a", "b", "c", "direct", "r01", True),
        make_run("a", "b", "c", "primed", "r01", True),
        make_run("a", "b", "c", "primed", "r02", True),
        make_run("a", "b", "c", "primed", "r03", True),
        make_run("d", "e", "f", "direct", "r01", False),
    ]
    plan = {
        "experiment_id": "exp004", "artifact": "repeat_plan",
        "phase": "repeat", "date": "2026-09-08",
        "generator": "test", "generator_commit": "abc1234",
        "source": {"file": "src.txt", "sha256": SHA, "bytes": 10},
        "corpus": {"id": "corpus", "version": "v1",
                   "file": "corpus.txt", "sha256": SHA, "bytes": 10},
        "counts": {"primary_runs": 4, "exploratory_runs": 1,
                   "total_runs": 5}, "runs": p_runs,
    }
    rows = [
        _roster_row(rid("a", "b", "c", "direct", "r01"), "direct", "r01",
                    True, True, verdict="complete", usable=True,
                    canonical=0.60, broader=0.70, unresolved=0.40,
                    ortho_out=10),
        _roster_row(rid("a", "b", "c", "primed", "r01"), "primed", "r01",
                    True, True, verdict="partial", usable=False,
                    canonical=0.999, broader=0.999, unresolved=0.001,
                    ortho_out=999),
        _roster_row(rid("a", "b", "c", "primed", "r02"), "primed", "r02",
                    True, True, verdict="complete", usable=True,
                    canonical=0.65, broader=0.72, unresolved=0.35,
                    ortho_out=12),
        _roster_row(rid("a", "b", "c", "primed", "r03"), "primed", "r03",
                    True, False),
        _roster_row(rid("d", "e", "f", "direct", "r01"), "direct", "r01",
                    False, True, verdict="complete", usable=True,
                    canonical=0.50, broader=0.60, unresolved=0.50,
                    ortho_out=5),
    ]
    roster = {"experiment_id": "exp004", "artifact": "repeat_roster",
              "phase": "repeat", "date": "2026-09-08", "generator": "test",
              "counts": {"planned": 5, "collected": 4,
                         "intake_complete": 3, "usable": 3},
              "rows": rows}
    audit_runs = []
    for r in p_runs:
        collected = not (r["condition"] == "primed"
                         and r["replicate"] == "r03")
        audit_runs.append({
            "run_id": r["run_id"], "condition": r["condition"],
            "replicate": r["replicate"], "primary": r["primary"],
            "exploratory": not r["primary"],
            "collection_status": "collected" if collected else "missing",
            "roster_status": ("collected_external_output" if collected
                              else None),
            "plan_status": "planned", "file_prompt_ok": collected,
            "end_marker_ok": collected, "size_floor_ok": collected,
            "reply_bytes": 100 if collected else None,
            "reply_nonempty": collected, "last_line": "KONIEC",
        })
    audit = {
        "artifact": "exp004-repeats-collection-audit",
        "experiment_id": "exp004", "phase": "repeat",
        "audit_date": "2026-09-09", "plan": {}, "manifest": {},
        "hash_gates": {"source": SHA, "corpus": SHA},
        "collection": {"collected": 4, "missing": 1, "primary": {},
                       "exploratory": {}},
        "fresh_session_proof": "unavailable", "runs": audit_runs,
        "deviations": [],
    }
    manifest = {"artifact": "repeat_prompt_manifest", "experiment_id":
                "exp004", "counts": {"total_runs": 5}, "files": []}
    dataset = {
        "primary": [{"config": ["a", "b", "c"], "label": "Primary Cfg",
                     "primary": True, "exploratory": False,
                     "old_single": None, "direct": {}, "primed": {}}],
        "exploratory": [{"config": ["d", "e", "f"], "label": "Expl Cfg",
                         "primary": False, "exploratory": True,
                         "old_single": None, "direct": {}, "primed": {}}],
    }
    analysis = {"status": "results", "baseline_dependence_revisited": {}}
    kit = tmp
    (kit / "figures").mkdir(parents=True)
    (kit / "outputs").mkdir(parents=True)
    (kit / "operator-prompts").mkdir(parents=True)
    (kit / "analysis").mkdir(parents=True)
    (kit / "outputs" / "plan.json").write_text(json.dumps(plan))
    (kit / "outputs" / "roster.json").write_text(json.dumps(roster))
    (kit / "outputs" / "audit.json").write_text(json.dumps(audit))
    (kit / "operator-prompts" / "manifest.json").write_text(
        json.dumps(manifest))
    (kit / "analysis" / "dataset.json").write_text(json.dumps(dataset))
    (kit / "analysis" / "analysis.json").write_text(json.dumps(analysis))


def _build(bundle_mod, kit: Path, out: Path):
    assert bundle_mod.main(["build",
                            "--plan", str(kit / "outputs" / "plan.json"),
                            "--roster", str(kit / "outputs"
                                            / "roster.json"),
                            "--audit", str(kit / "outputs" / "audit.json"),
                            "--manifest", str(kit / "operator-prompts"
                                             / "manifest.json"),
                            "--dataset", str(kit / "analysis"
                                             / "dataset.json"),
                            "--analysis", str(kit / "analysis"
                                              / "analysis.json"),
                            "--figures", str(kit / "figures"),
                            "--out", str(out)]) == 0


# ---------------------------------------------------------------------------
# A. hermetic
# ---------------------------------------------------------------------------

def test_bundle_generator_hermetic_consistency(tmp_path, bundle_mod):
    kit = tmp_path / "kit"
    _write_synthetic_kit(kit)
    out = tmp_path / "bundle"
    _build(bundle_mod, kit, out)

    results = json.loads((out / "results.json").read_text())
    recs = results["records"]
    assert len(recs) == 5
    by_id = {r["run_id"]: r for r in recs}
    primed = [r for r in recs if r["condition"] == "primed"]
    assert sorted(r["status"] for r in primed) == \
        ["missing", "partial", "usable"]
    assert by_id[[k for k in by_id if k.endswith("primed__r03")][0]]["metrics"] \
        is None

    # verify: internal consistency only (no real-count assumptions)
    report = bundle_mod.verify_bundle(out)
    failed = [c for c in report["checks"] if not c["ok"]]
    assert not failed, [c for c in report["checks"] if not c["ok"]]
    comp = report["computed"]
    assert comp["usable"] == 3 and comp["partial"] == 1
    assert comp["missing"] == 1
    # repeated delta = primed r02 (0.65) - direct r01 (0.60)
    assert comp["mean_repeated_delta_canonical_pp"] == pytest.approx(5.0)
    assert comp["positive_canonical_delta"] == 1

    # partial run's metrics never enter summary statistics
    summary = json.loads((out / "summary.json").read_text())
    pcfg = summary["configurations"]["primary"][0]
    assert pcfg["primed"]["usable_n"] == 1
    assert pcfg["primed"]["canonical"]["mean"] == pytest.approx(0.65)
    assert pcfg["repeated"]["delta_mean_canonical"] == pytest.approx(0.05)
    # exploratory config has no primed runs -> repeated delta is null
    ecfg = summary["configurations"]["exploratory"][0]
    assert ecfg["direct"]["usable_n"] == 1
    assert ecfg["repeated"]["delta_mean_canonical"] is None

    # CSV has one header + five rows, and a missing row has blank metrics
    csv_text = (out / "results.csv").read_text(encoding="utf-8")
    assert csv_text.count("\n") == 6
    assert "primary" in csv_text


def test_bundle_generator_deterministic(tmp_path, bundle_mod):
    kit = tmp_path / "kit"
    _write_synthetic_kit(kit)
    b1 = tmp_path / "b1"
    b2 = tmp_path / "b2"
    _build(bundle_mod, kit, b1)
    _build(bundle_mod, kit, b2)
    f1 = sorted(p.relative_to(b1) for p in b1.rglob("*") if p.is_file())
    f2 = sorted(p.relative_to(b2) for p in b2.rglob("*") if p.is_file())
    assert [str(p) for p in f1] == [str(p) for p in f2]
    for rel in f1:
        assert (b1 / rel).read_bytes() == (b2 / rel).read_bytes(), rel


# ---------------------------------------------------------------------------
# B. standalone reconstruction of the real Task-026 conclusions
# ---------------------------------------------------------------------------

REAL = pytest.mark.skipif(not BUNDLE.is_dir(),
                          reason="assistant-research-bundle not present")


def test_manifest_hashes_and_no_bloat():
    if not BUNDLE.is_dir():
        pytest.skip("assistant-research-bundle not present")
    manifest = json.loads((BUNDLE / "manifest.json").read_text())
    # manifest lists every bundle file except itself (self-hash impossible)
    files = sorted(p.relative_to(BUNDLE).as_posix()
                   for p in BUNDLE.rglob("*")
                   if p.is_file() and p.name != "manifest.json")
    assert files == sorted(e["file"] for e in manifest["files"])
    import hashlib
    for e in manifest["files"]:
        data = (BUNDLE / e["file"]).read_bytes()
        assert hashlib.sha256(data).hexdigest() == e["sha256"], e["file"]
        assert len(data) < 2_000_000, f"unexpectedly large file {e['file']}"
    total = sum(e["bytes"] for e in manifest["files"])
    assert total < 10_000_000, "bundle should stay compact"


# Credential-looking assignments ("api_key = …", "secret: abc…", …).
# Plain prose such as the provenance "no secrets" policy note and metric
# key names ("tokens_total") must NOT match.
SECRET_RE = re.compile(
    r"\b(api[_-]?key|secret|password|passwd|bearer[ _-]?token|"
    r"session[_-]?token|session[_-]?id|cookie|authorization|"
    r"private[_-]?key|access[_-]?token|auth[_-]?token)\b\s*[=:]\s*"
    r"['\"]?[A-Za-z0-9_\-./+]{6,}", re.IGNORECASE)


def test_no_secrets_in_bundle():
    if not BUNDLE.is_dir():
        pytest.skip("assistant-research-bundle not present")
    for p in BUNDLE.rglob("*"):
        if not p.is_file() or p.suffix not in (".json", ".md", ".csv"):
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        hits = [m for m in SECRET_RE.finditer(text)]
        assert not [m.group(0) for m in hits], f"{p}: {hits[:3]}"


@REAL
def test_standalone_reconstruction(bundle_mod):
    report = bundle_mod.verify_bundle(BUNDLE)
    failed = [c for c in report["checks"] if not c["ok"]]
    assert not failed, [c["id"] for c in failed]
    comp = report["computed"]

    # planned / collected / usable / partial / missing
    assert comp["planned"] == 120
    assert comp["collected"] == 114
    assert comp["usable"] == 106
    assert comp["partial"] == 8
    assert comp["missing"] == 6
    assert comp["primary_planned"] == 108
    assert comp["exploratory_planned"] == 12

    # key repeated statistics from Task 026 (recomputed from run records)
    assert comp["assessable_primary"] == 16
    assert comp["positive_canonical_delta"] == 16
    assert comp["mean_repeated_delta_canonical_pp"] == pytest.approx(
        6.93, abs=0.02)
    assert comp["mean_repeated_delta_broader_pp"] == pytest.approx(
        3.88, abs=0.02)
    assert comp["old_vs_new_rows"] == 15
    assert comp["same_direction_rows"] == 15
    assert comp["mean_old_delta_pp"] == pytest.approx(6.33, abs=0.02)
    assert comp["mean_new_delta_pp_oldrows"] == pytest.approx(6.73,
                                                              abs=0.02)
    assert comp["median_direct_sd_pp"] == pytest.approx(1.49, abs=0.02)
    assert comp["median_primed_sd_pp"] == pytest.approx(0.87, abs=0.02)

    # Qwen 3.8 Max Fast: primed SD exceeds its own repeated delta
    assert comp["primed_sd_exceeds_delta_configs"] == \
        ["alibaba__qwen-3.8-max__fast"]

    # the two never-collected primed conditions stay missing (no fill)
    assert sorted(comp["missing_configurations"]) == [
        "alibaba__qwen-3.8-max__thinking",
        "google__gemini-3.1-pro__extthinkon"]


@REAL
def test_dola_kept_out_of_primary(bundle_mod):
    results = json.loads((BUNDLE / "results.json").read_text())
    summary = json.loads((BUNDLE / "summary.json").read_text())
    recs = results["records"]
    primary_ids = {r["configuration_id"] for r in recs
                   if r["in_primary_statistics"]}
    expl_ids = {r["configuration_id"] for r in recs
                if not r["in_primary_statistics"]}
    assert primary_ids.isdisjoint(expl_ids)
    dola_ids = {c["configuration_id"] for c in
                summary["configurations"]["exploratory"]}
    assert all("dola" in cid for cid in dola_ids)
    assert not ({c["configuration_id"] for c in
                 summary["configurations"]["primary"]} & dola_ids)
    # Dola Fast direct condition is intake-partial -> 0 usable direct runs
    dola_fast = next(c for c in summary["configurations"]["exploratory"]
                     if c["configuration_id"] == "bytedance__dola-3.8__fast")
    assert dola_fast["direct"]["usable_n"] == 0
    assert dola_fast["repeated"]["delta_mean_canonical"] is None
