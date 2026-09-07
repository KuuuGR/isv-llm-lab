"""EXP-004 full analysis — Phase 1 → Phase 2A corpus priming tests (SODA
Task 024, 2026-09-07).

Covers the deterministic read-only analysis script
(scripts/analyze_exp004_phase2a.py):

- the assembled dataset represents all 20 configurations (18 original +
  2 exploratory Dola rows) and the two groups are never merged;
- Dola Fast/Pro pair to their Phase-1 DIRECT baselines correctly;
- every Phase-1 → Phase-2A delta is exactly Phase-2A − Phase-1 of the
  SAME configuration and agrees with the recorded compare.json deltas;
- missing/invalid input values make build_dataset fail loudly (no
  fabricated metrics are ever produced);
- dataset values equal the roster source values (nothing invented);
- master-table ordering, statistics, tests and chart inputs are
  deterministic;
- the Dola exploratory status survives into every derived output
  (master table, Δ table, family table, rankings, poster).

The tests run against the real completed EXP-004 rosters; all expected
numbers are recomputed inside the test or taken from the recorded
compare.json artifact — nothing is hard-coded from memory.
"""
import json
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
ROOT = SCRIPTS.parent


def _load_analysis_module():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "analyze_exp004_phase2a", SCRIPTS / "analyze_exp004_phase2a.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


AN = _load_analysis_module()


@pytest.fixture(scope="module")
def ds():
    return AN.build_dataset()


@pytest.fixture(scope="module")
def an(ds):
    return AN.build_analysis(ds)


# ---------------------------------------------------------------------------
# 1. dataset composition
# ---------------------------------------------------------------------------

def test_dataset_has_all_20_configurations(ds):
    cfg = ds["configs"]
    assert len(cfg) == 20
    orig = [c for c in cfg if not c["exploratory"]]
    dola = [c for c in cfg if c["exploratory"]]
    assert len(orig) == 18
    assert len(dola) == 2
    assert {c["short_label"] for c in dola} == {
        "Dola 3.8 Fast", "Dola 3.8 Pro"}


def test_original_18_are_distinguished_from_dola(ds):
    orig = [c for c in ds["configs"] if not c["exploratory"]]
    dola = [c for c in ds["configs"] if c["exploratory"]]
    # originals carry their preregistered Phase-1 number; Dola rows do not
    assert all(c["phase1_number"] is not None for c in orig)
    assert all(c["phase1_number"] is None for c in dola)
    # ordering: Phase-1 numbers ascending, then the two Dola rows
    nums = [c["phase1_number"] for c in orig]
    assert nums == sorted(nums)
    assert [c["short_label"] for c in dola] == ["Dola 3.8 Fast",
                                                "Dola 3.8 Pro"]
    # Dola is its own family in every derived table
    assert {c["family"] for c in dola} == {"Dola"}


def test_dola_fast_and_pro_pair_to_their_direct_baselines(ds):
    dola = {c["short_label"]: c for c in ds["configs"]
            if c["exploratory"]}
    # P1 run ids resolve to the Dola __direct retrospective baselines
    assert "dola-3.8__fast__direct" in dola["Dola 3.8 Fast"]["run_id_p1"]
    assert "dola-3.8__pro__direct" in dola["Dola 3.8 Pro"]["run_id_p1"]
    # P2A run ids are the exploratory corpus-primed runs 20/21
    assert dola["Dola 3.8 Fast"]["run_id_p2a"].endswith("__p2a-primed")
    # intake was complete and the paired P1 baseline usable (Task 023)
    for c in dola.values():
        assert c["p2a_intake"] == "complete"
        assert c["p2a_usable"] is True
    # pairing agrees with the recorded compare.json artifact
    compare = json.loads(
        (ROOT / "experiments/exp004-modelscreen/phase2a/outputs"
               / "compare.json").read_text())
    for row in compare["rows"]:
        if "dola" not in row["run_id"]:
            continue
        fast = "fast" in row["run_id"]
        c = dola["Dola 3.8 Fast" if fast else "Dola 3.8 Pro"]
        assert row["baseline_run_id"] == c["run_id_p1"]
        assert row["baseline_source"] == "phase1-baseline"


# ---------------------------------------------------------------------------
# 2. deltas
# ---------------------------------------------------------------------------

def test_deltas_are_exact_p2a_minus_p1(ds):
    for c in ds["configs"]:
        d = c["deltas"]
        assert d["canonical_coverage_pp"] == pytest.approx(
            c["P2A"]["canonical_coverage"] - c["P1"]["canonical_coverage"],
            abs=1e-12)
        assert d["broader_coverage_pp"] == pytest.approx(
            c["P2A"]["broader_coverage"] - c["P1"]["broader_coverage"],
            abs=1e-12)
        assert d["unresolved_rate_pp"] == pytest.approx(
            c["P2A"]["unresolved_rate"] - c["P1"]["unresolved_rate"],
            abs=1e-12)
        assert d["lexical_tokens"] == pytest.approx(
            c["P2A"]["lexical_tokens"] - c["P1"]["lexical_tokens"],
            abs=1e-9)
        assert d["ortho_out"] == (
            c["P2A"]["ortho_out"] - c["P1"]["ortho_out"])


def test_deltas_agree_with_recorded_compare_json(ds):
    compare = json.loads(
        (ROOT / "experiments/exp004-modelscreen/phase2a/outputs"
               / "compare.json").read_text())
    by_run = {c["run_id_p2a"]: c for c in ds["configs"]}
    for row in compare["rows"]:
        c = by_run[row["run_id"]]
        rec = row["deltas"]
        assert c["deltas"]["canonical_coverage_pp"] == pytest.approx(
            rec["canonical_coverage_pp"], abs=1e-9)
        assert c["deltas"]["broader_coverage_pp"] == pytest.approx(
            rec["broader_resource_supported_coverage_pp"], abs=1e-9)


def test_known_dola_fast_delta_is_preserved(ds):
    fast = next(c for c in ds["configs"]
                if c["short_label"] == "Dola 3.8 Fast")
    # recomputed from the roster files directly, not from memory
    p1 = json.loads((ROOT / "experiments/exp004-modelscreen/outputs"
                     / "roster.json").read_text())
    p2 = json.loads((ROOT / "experiments/exp004-modelscreen/phase2a"
                     / "outputs" / "roster.json").read_text())
    r1 = {r["run_id"]: r for r in p1["rows"]}
    b = r1[fast["run_id_p1"]]["metrics"]
    a = next(r["metrics"] for r in p2["rows"]
             if r["run_id"] == fast["run_id_p2a"])
    assert fast["P1"]["canonical_coverage"] == pytest.approx(
        b["canonical_coverage"], abs=1e-12)
    assert fast["P2A"]["canonical_coverage"] == pytest.approx(
        a["canonical_coverage"], abs=1e-12)
    assert fast["deltas"]["canonical_coverage_pp"] == pytest.approx(
        a["canonical_coverage"] - b["canonical_coverage"], abs=1e-12)


# ---------------------------------------------------------------------------
# 3. no fabricated metrics / explicit failure on missing data
# ---------------------------------------------------------------------------

def test_no_fabricated_metrics_values_match_rosters(ds):
    p1 = json.loads((ROOT / "experiments/exp004-modelscreen/outputs"
                     / "roster.json").read_text())
    p2 = json.loads((ROOT / "experiments/exp004-modelscreen/phase2a"
                     / "outputs" / "roster.json").read_text())
    r1 = {r["run_id"]: r for r in p1["rows"]}
    r2 = {r["run_id"]: r for r in p2["rows"]}
    for c in ds["configs"]:
        m1, m2 = r1[c["run_id_p1"]]["metrics"], r2[c["run_id_p2a"]]["metrics"]
        o1, o2 = (r1[c["run_id_p1"]]["orthography"],
                  r2[c["run_id_p2a"]]["orthography"])
        assert c["P1"]["canonical_coverage"] == m1["canonical_coverage"]
        assert c["P2A"]["canonical_coverage"] == m2["canonical_coverage"]
        assert (c["P1"]["broader_coverage"]
                == m1["broader_resource_supported_coverage"])
        assert c["P2A"]["lexical_tokens"] == m2["total_tokens"]
        assert c["P1"]["ortho_out"] == o1["outside_inventory"]
        assert c["P2A"]["ortho_out"] == o2["outside_inventory"]
        assert c["P2A"]["ortho"]["other_latin"] == o2["other_latin"]
        assert c["P2A"]["buckets"] == m2["bucket_counts"]


def _copy_roster(src: Path) -> dict:
    return json.loads(src.read_text())


def test_missing_metrics_fail_loudly(ds, tmp_path, monkeypatch):
    p2 = _copy_roster(ROOT / "experiments/exp004-modelscreen/phase2a"
                      / "outputs" / "roster.json")
    p1 = _copy_roster(ROOT / "experiments/exp004-modelscreen/outputs"
                      / "roster.json")
    # break one primed row: metrics exist but canonical is missing
    target = next(r for r in p2["rows"]
                  if r.get("condition") == "p2a-primed")
    del target["metrics"]["canonical_coverage"]
    p1f, p2f, cf = (tmp_path / "p1.json"), (tmp_path / "p2.json"), \
                   (tmp_path / "cmp.json")
    p1f.write_text(json.dumps(p1))
    p2f.write_text(json.dumps(p2))
    cf.write_text(json.dumps({"rows": []}))
    monkeypatch.setattr(AN, "P1_ROSTER", p1f)
    monkeypatch.setattr(AN, "P2A_ROSTER", p2f)
    monkeypatch.setattr(AN, "COMPARE_JSON", cf)
    with pytest.raises(ValueError, match="missing metrics"):
        AN.build_dataset()


def test_missing_baseline_fails_loudly(ds, tmp_path, monkeypatch):
    p2 = _copy_roster(ROOT / "experiments/exp004-modelscreen/phase2a"
                      / "outputs" / "roster.json")
    p1 = _copy_roster(ROOT / "experiments/exp004-modelscreen/outputs"
                      / "roster.json")
    target = next(r for r in p2["rows"]
                  if r.get("condition") == "p2a-primed")
    target["baseline_run_id"] = "does-not-exist"
    p1f, p2f, cf = (tmp_path / "p1.json"), (tmp_path / "p2.json"), \
                   (tmp_path / "cmp.json")
    p1f.write_text(json.dumps(p1))
    p2f.write_text(json.dumps(p2))
    cf.write_text(json.dumps({"rows": []}))
    monkeypatch.setattr(AN, "P1_ROSTER", p1f)
    monkeypatch.setattr(AN, "P2A_ROSTER", p2f)
    monkeypatch.setattr(AN, "COMPARE_JSON", cf)
    with pytest.raises(ValueError, match="missing from Phase-1 roster"):
        AN.build_dataset()


# ---------------------------------------------------------------------------
# 4. deterministic ordering + derived tables
# ---------------------------------------------------------------------------

def test_master_table_ordering_is_deterministic(ds, an):
    rows = an["master_table"]
    assert len(rows) == 20
    again = AN.master_rows(ds)
    assert rows == again
    # canonical order: original 18 (Phase-1 number asc) then Dola fast/pro
    assert [r["configuration"] for r in rows[-2:]] == [
        "Dola 3.8 Fast", "Dola 3.8 Pro"]
    assert all(r["status"] == "original 18" for r in rows[:18])
    assert all(r["status"] == "exploratory (Dola)" for r in rows[-2:])


def test_delta_table_sorted_desc_then_broader(ds, an):
    rows = an["deltas_sorted_by_canonical_delta"]
    assert len(rows) == 20
    d = [r["d_canonical_pp"] for r in rows]
    assert d == sorted(d, reverse=True)
    # larger Δ canonical first; equal keys ordered by Δ broader desc
    for a, b in zip(rows, rows[1:]):
        assert (a["d_canonical_pp"], a["d_broader_pp"]) >= \
               (b["d_canonical_pp"], b["d_broader_pp"])
    assert rows[0]["configuration"] == "Dola 3.8 Fast"
    assert rows[0]["exploratory"] is True


def test_dola_exploratory_status_preserved_everywhere(ds, an):
    dola_labels = {"Dola 3.8 Fast", "Dola 3.8 Pro"}
    # master table
    for r in an["master_table"]:
        if r["configuration"] in dola_labels:
            assert r["status"] == "exploratory (Dola)"
    # delta table
    for r in an["deltas_sorted_by_canonical_delta"]:
        assert r["exploratory"] == (r["configuration"] in dola_labels)
    # family tables
    for fam_rows in an["families"].values():
        for r in fam_rows:
            assert r["exploratory"] == (r["configuration"] in dola_labels)
    # rankings scoped to all 20
    for scope in ("original_18", "all_20"):
        ranks = an["rankings"][scope]
        seen = {r["configuration"] for r in ranks["canonical_coverage"]}
        for r in ranks["canonical_coverage"]:
            assert r["exploratory"] == (r["configuration"] in dola_labels)
        if scope == "all_20":
            assert dola_labels <= seen
        else:
            assert not (dola_labels & seen)


def test_rankings_are_deterministic_and_use_existing_metrics(ds, an):
    rk = an["rankings"]["original_18"]
    # canonical ranking sorted desc by the recorded P1 metric
    vals = [r["value"] for r in rk["canonical_coverage"]]
    assert vals == sorted(vals, reverse=True)
    assert vals[0] == max(c["P1"]["canonical_coverage"]
                          for c in ds["configs"] if not c["exploratory"])
    # unresolved ranking is ascending (lower = better)
    uv = [r["value"] for r in rk["unresolved_rate"]]
    assert uv == sorted(uv)
    # orthography cleanliness ranking is ascending outside-inventory
    ov = [r["value"] for r in rk["orthography_cleanliness"]]
    assert ov == sorted(ov)
    assert len(rk["canonical_coverage"]) == 18


# ---------------------------------------------------------------------------
# 5. statistics + tests are deterministic and known
# ---------------------------------------------------------------------------

def test_descriptive_statistics_match_direct_computation(ds, an):
    import statistics as st
    orig = [c for c in ds["configs"] if not c["exploratory"]]
    dv = [c["deltas"]["canonical_coverage_pp"] for c in orig]
    desc = an["stats"]["original_18"]["delta_canonical_pp"]["describe"]
    assert desc["mean"] == pytest.approx(st.fmean(dv), abs=1e-12)
    assert desc["median"] == pytest.approx(st.median(dv), abs=1e-12)
    assert desc["sd"] == pytest.approx(st.stdev(dv), abs=1e-12)
    assert desc["min"] == min(dv) and desc["max"] == max(dv)
    assert desc["n"] == 18
    assert desc["positive"] == 18 and desc["negative"] == 0


def test_sign_and_permutation_p_values_known(ds, an):
    # all 18 original deltas are positive: two-sided sign-test p = 2/2^18
    o = an["stats"]["original_18"]["delta_canonical_pp"]
    assert o["sign_test"]["positive"] == 18
    assert o["sign_test"]["p_value"] == pytest.approx(2 / 2 ** 18,
                                                      abs=1e-12)
    # ... and the sign-flip permutation test can only be that extreme in
    # the all-plus / all-minus configurations: p = 2/2^18
    assert o["permutation_test_mean"]["p_value"] == pytest.approx(
        2 / 2 ** 18, abs=1e-12)
    assert o["permutation_test_mean"]["assignments"] == 2 ** 18
    # broader coverage: 14+/4- -> exact two-sided binomial p
    b = an["stats"]["original_18"]["delta_broader_pp"]["sign_test"]
    assert b["positive"] == 14 and b["negative"] == 4
    assert b["p_value"] == pytest.approx(
        AN._exact_two_sided_binom(14, 18), abs=1e-12)


def test_spearman_correlations_known(ds, an):
    o = an["stats"]["original_18"]
    bd = o["baseline_dependence"]
    assert bd["p1_canonical_vs_delta_canonical"]["n"] == 18
    assert bd["p1_canonical_vs_delta_canonical"]["rho"] == pytest.approx(
        -0.8575851393188855, abs=1e-9)
    assert bd["p1_broader_vs_delta_broader"]["rho"] == pytest.approx(
        -0.8390092879256966, abs=1e-9)
    bv = o["baseline_vs_primed"]
    assert bv["p1_canonical_vs_p2a_canonical"]["n"] == 18
    assert bv["p1_canonical_vs_p2a_canonical"]["rho"] == pytest.approx(
        0.44685242518059853, abs=1e-9)
    a20 = an["stats"]["all_20_exploratory"]
    assert a20["baseline_dependence"][
        "p1_canonical_vs_delta_canonical"]["n"] == 20


def test_stats_are_identical_on_recomputation(ds):
    s1 = AN.analysis_stats(ds)
    s2 = AN.analysis_stats(ds)
    assert s1 == s2


# ---------------------------------------------------------------------------
# 6. chart inputs deterministic
# ---------------------------------------------------------------------------

def test_chart_inputs_are_deterministic(ds):
    a1 = AN._sorted_pairs(ds, "canonical_coverage")
    a2 = AN._sorted_pairs(ds, "canonical_coverage")
    assert a1 == a2
    # sorted by Phase-1 value ascending (deterministic tie-break by label)
    p1 = [it["v1"] for it in a1]
    assert p1 == sorted(p1)


def test_charts_are_byte_identical_across_two_generations(ds, tmp_path):
    d1, d2 = tmp_path / "f1", tmp_path / "f2"
    AN.render_charts(ds, d1)
    AN.render_charts(ds, d2)
    f1 = {p.name: p.read_bytes() for p in d1.glob("*.svg")}
    f2 = {p.name: p.read_bytes() for p in d2.glob("*.svg")}
    assert set(f1) == set(f2) == {f"chart_{x}.svg" for x in "abcdefg"}
    for name in f1:
        assert f1[name] == f2[name]
