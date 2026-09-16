"""Phase 2B HIGH aggregate analysis — integrity + pairing (hermetic)."""
import importlib.util
import json
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
ROOT = SCRIPTS.parent


def _load():
    spec = importlib.util.spec_from_file_location(
        "analyze_exp004_phase2b", SCRIPTS / "analyze_exp004_phase2b.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def ana():
    return _load()


def _synth_obs(label, provider, model, version, condition, replicate,
               canonical, broader, unresolved, ortho):
    return {
        "run_id": (f"2099-01-01__p2b-high__{provider}__{model}__{version}"
                   f"__{condition}__{replicate}"),
        "label": label,
        "provider": provider,
        "model": model,
        "model_version": version,
        "condition": condition,
        "replicate": replicate,
        "phase2b_role": "test",
        "intake_verdict": "complete",
        "usable": True,
        "metrics": {
            "canonical_coverage": canonical,
            "broader_resource_supported_coverage": broader,
            "unresolved_rate": unresolved,
            "outside_inventory": ortho,
        },
        "orthography": {"outside_inventory": ortho},
        "artifact_paths": {},
    }


def test_integrity_and_paired_delta(ana):
    # One configuration, 3 D + 3 P with known deltas
    label = "Test Config"
    key = ("google", "gemini-3.6-flash", "extthinkon")
    # direct: 0.60, 0.62, 0.64 ; primed: 0.70, 0.66, 0.68
    # deltas: +0.10, +0.04, +0.04 ; mean Δ = +0.06
    d_can = [0.60, 0.62, 0.64]
    p_can = [0.70, 0.66, 0.68]
    obs = []
    for i, rep in enumerate(("r01", "r02", "r03")):
        obs.append(_synth_obs(label, *key, "direct", rep,
                              d_can[i], 0.8, 0.4 - d_can[i] + 0.4, 10 + i))
        # unresolved dummy; broader/ortho not under test here
        obs.append(_synth_obs(label, *key, "primed", rep,
                              p_can[i], 0.85, 0.3, 8 + i))

    # Pad to 7 configs × 6 = 42 with flat zeros so integrity passes
    for provider, model, version in ana.SHORTLIST_ORDER:
        if (provider, model, version) == key:
            continue
        lab = f"{model}-{version}"
        for rep in ("r01", "r02", "r03"):
            for cond in ("direct", "primed"):
                obs.append(_synth_obs(lab, provider, model, version, cond,
                                      rep, 0.5, 0.6, 0.5, 20))

    plan = {"runs": [{"run_id": o["run_id"]} for o in obs],
            "source": {"sha256": "s"}, "corpus": {"sha256": "c"}}
    integrity = ana.integrity_checks(obs, plan)
    assert integrity["ok"]
    dataset = ana.build_dataset(obs, integrity, plan)
    cfg = next(c for c in dataset["configurations"]
               if tuple(c["config"]) == key)
    assert cfg["direct"]["canonical"]["n"] == 3
    assert abs(cfg["direct"]["canonical"]["mean"] - 0.62) < 1e-12
    deltas = cfg["paired_deltas"]["canonical"]
    assert abs(deltas["values"]["r01"] - 0.10) < 1e-12
    assert abs(deltas["values"]["r02"] - 0.04) < 1e-12
    assert abs(deltas["values"]["r03"] - 0.04) < 1e-12
    assert abs(deltas["mean"] - 0.06) < 1e-12
    # pairs carry run ids for traceability
    assert all("direct_run_id" in p and "primed_run_id" in p
               for p in deltas["pairs"])


def test_integrity_fails_on_missing_pair(ana):
    obs = []
    for provider, model, version in ana.SHORTLIST_ORDER:
        for rep in ("r01", "r02", "r03"):
            for cond in ("direct", "primed"):
                if (provider, model, version) == ana.SHORTLIST_ORDER[0] \
                        and cond == "primed" and rep == "r03":
                    continue  # missing one primed
                obs.append(_synth_obs("L", provider, model, version, cond,
                                      rep, 0.5, 0.6, 0.5, 1))
    plan = {"runs": [{"run_id": o["run_id"]} for o in obs]}
    # also need planned count mismatch — construct matching plan of incomplete set
    with pytest.raises(RuntimeError, match="integrity check FAILED"):
        ana.integrity_checks(obs, plan)


@pytest.mark.skipif(
    not (ROOT / "experiments/exp004-modelscreen/phase2b/outputs"
         / "2026-09-09__p2b-high__google__gemini-3.6-flash__extthinkon__direct__r01"
         / "evaluation.json").is_file(),
    reason="Phase-2B HIGH evaluated outputs not present locally")
def test_real_phase2b_integrity_passes(ana):
    plan = ana.p2b.load_plan()
    obs = ana.load_observations()
    integrity = ana.integrity_checks(obs, plan)
    assert integrity["ok"]
    assert integrity["n_observations"] == 42


def test_low_qwen_excluded_from_primary_mean(ana):
    """LOW Qwen config is retained but excluded from primary mean Δ."""
    key_q = ("alibaba", "qwen-3.8-max", "fast")
    assert key_q in ana.INVALID_LOW_PAIRED_CONFIGS
    assert not ana._cfg_is_primary_valid("low", key_q)
    assert ana._cfg_is_primary_valid("high", key_q)

    obs = []
    for provider, model, version in ana.SHORTLIST_ORDER:
        lab = f"{model}-{version}"
        for rep in ("r01", "r02", "r03"):
            if (provider, model, version) == key_q:
                d_c, p_c = 0.70, 0.40  # Δ = -0.30
            else:
                d_c, p_c = 0.60, 0.70  # Δ = +0.10
            d = _synth_obs(lab, provider, model, version, "direct",
                           rep, d_c, 0.8, 0.4, 10)
            d["run_id"] = (
                f"2099-01-01__p2b-low__{provider}__{model}__{version}"
                f"__direct__{rep}")
            p = _synth_obs(lab, provider, model, version, "primed",
                           rep, p_c, 0.85, 0.3, 8)
            p["run_id"] = (
                f"2099-01-01__p2b-low__{provider}__{model}__{version}"
                f"__primed__{rep}")
            obs.extend([d, p])

    plan = {"runs": [{"run_id": o["run_id"]} for o in obs],
            "source": {"sha256": "s"}, "corpus": {"sha256": "c"}}
    integrity = ana.integrity_checks(obs, plan, regime="low")
    assert integrity["ok"]
    dataset = ana.build_dataset(obs, integrity, plan, regime="low")
    assert dataset["n_configurations_primary_valid"] == 6
    assert dataset["n_configurations_invalid_pairing"] == 1
    analysis = ana.build_analysis(dataset)
    assert len(analysis["tables"]["canonical"]["rows"]) == 6
    assert all("qwen" not in r["config"][1]
               for r in analysis["tables"]["canonical"]["rows"])
    mean_d = analysis["distribution_notes"][
        "canonical_delta_mean_across_configs"]
    assert abs(mean_d - 0.10) < 1e-12
    assert analysis["distribution_notes"][
        "canonical_delta_mean_across_configs_n"] == 6
    assert analysis["distribution_notes"][
        "qwen_low_priming_effect_estimated"] is False
    inv = analysis["invalid_pairing_tables"]["canonical"]["rows"]
    assert len(inv) == 1
    assert abs(inv[0]["delta_mean"] - (-0.30)) < 1e-12
