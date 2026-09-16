#!/usr/bin/env python3
"""EXP-004 Phase 2B HIGH — aggregate paired analysis (descriptive, n=3).

Reads the already-collected / verified / evaluated Phase-2B HIGH runs
under experiments/exp004-modelscreen/phase2b/outputs/ and writes a
deterministic aggregate dataset + report under phase2b/analysis/.

Never calls an LLM. Never modifies raw outputs, frozen story, corpus,
prompts, or evaluation artifacts. Metrics are taken exactly from the
existing evaluation.json / orthography.json files.

Primary paired quantity (per configuration, per replicate):
    Δᵢ = Pᵢ − Dᵢ

With n = 3 replicates per condition this analysis is DESCRIPTIVE —
not inferential. No significance testing.

Outputs (deterministic; std-lib only):
  dataset.json   integrity ledger + per-run observations + per-config
                 direct/primed stats + paired Δ values for all four
                 metrics
  analysis.json  machine-readable summary tables
  analysis.md    human-readable report
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import run_exp004_phase2b as p2b  # noqa: E402

PHASE2B = p2b.PHASE2B
OUTPUTS = p2b.OUTPUTS_DIR
ANALYSIS_ROOT = PHASE2B / "analysis"


def analysis_dir(regime: str = "high") -> Path:
    if regime == "low":
        return ANALYSIS_ROOT / "low"
    if regime == "high":
        return ANALYSIS_ROOT
    raise ValueError(f"unknown regime {regime!r}")

METRICS = (
    ("canonical", "canonical_coverage", "canonical coverage"),
    ("broader", "broader_resource_supported_coverage",
     "broader resource-supported coverage"),
    ("unresolved", "unresolved_rate", "unresolved rate"),
    ("ortho_out", "outside_inventory", "orthography outside-inventory"),
)

# Shortlist order = plan order (behavioural sample, not a ranking).
SHORTLIST_ORDER = [
    ("google", "gemini-3.6-flash", "extthinkon"),
    ("google", "gemini-3.6-flash", "extthinkoff"),
    ("anthropic", "claude", "sonnet-5"),
    ("deepseek", "deepseek-v3-expert", "deepthinkon"),
    ("alibaba", "qwen-3.8-max", "fast"),
    ("openai", "gpt-5.6-luna", "thinkoff"),
    ("xai", "grok", "fast"),
]

# LOW paired cells excluded from primary priming aggregates.
# Collection ledger still retains all 42 runs; exclusion is analytical only.
INVALID_LOW_PAIRED_CONFIGS: dict[tuple[str, str, str], dict] = {
    ("alibaba", "qwen-3.8-max", "fast"): {
        "status": "INVALID — MODEL MISMATCH",
        "incident_id": "p2b-low-qwen-model-mismatch-2026-09-16",
        "intended_model": "Qwen 3.8 Max — Fast",
        "actual_direct_model": "Qwen 3.8 Max — Fast",
        "actual_primed_model": "Qwen3.7-Plus (default-selected in Qwen Chat)",
        "why_invalid": (
            "Primed sessions were accidentally run on Qwen3.7-Plus rather "
            "than the intended Qwen3.8-Max; Direct/Primed are not a "
            "same-model pair."
        ),
        "qwen38_primed_service_error": (
            "Oops! There was an issue connecting to Qwen3.8-Max.\n"
            "Content security warning: output text data may contain "
            "inappropriate content!"
        ),
        "workaround_attempted": False,
        "priming_effect_estimated": False,
        "do_not_interpret_delta_as": (
            "Qwen 3.8 Max LOW priming effect (including any −12.08 pp figure)"
        ),
        "retained": True,
        "incident_doc": (
            "experiments/exp004-modelscreen/phase2b/analysis/low/"
            "QWEN_INCIDENT.md"
        ),
    },
}


def _invalid_low_info(key: tuple[str, str, str]) -> dict | None:
    return INVALID_LOW_PAIRED_CONFIGS.get(key)


def _cfg_is_primary_valid(regime: str, key: tuple[str, str, str]) -> bool:
    if regime != "low":
        return True
    return key not in INVALID_LOW_PAIRED_CONFIGS


def _cfg_key(o: dict) -> tuple[str, str, str]:
    return (o["provider"], o["model"], o["model_version"])


def _pct(v: float | None, digits: int = 2) -> str:
    if v is None:
        return "—"
    return f"{v * 100:.{digits}f}"


def _num(v: float | None, digits: int = 2) -> str:
    if v is None:
        return "—"
    return f"{v:.{digits}f}"


def _pp(v: float | None, digits: int = 2) -> str:
    """Signed percentage-point delta (fraction → pp)."""
    if v is None:
        return "—"
    return f"{v * 100:+.{digits}f}"


def _signed(v: float | None, digits: int = 2) -> str:
    if v is None:
        return "—"
    return f"{v:+.{digits}f}"


def stats(values: list[float]) -> dict:
    n = len(values)
    if n == 0:
        return {"n": 0, "mean": None, "sd": None, "min": None, "max": None,
                "range": None}
    return {
        "n": n,
        "mean": statistics.fmean(values),
        "sd": statistics.stdev(values) if n > 1 else 0.0,
        "min": min(values),
        "max": max(values),
        "range": max(values) - min(values),
    }


def load_observations(regime: str = "high") -> list[dict]:
    """Load one observation per planned Phase-2B run from evaluation
    artifacts. Fails loudly if any planned run is missing evaluation."""
    plan = p2b.load_plan(regime)
    if not plan.get("runs"):
        raise RuntimeError(
            f"Phase-2B {regime.upper()} plan missing; cannot analyse")
    obs: list[dict] = []
    for pe in plan["runs"]:
        rid = pe["run_id"]
        out = OUTPUTS / rid
        ev_path = out / "evaluation.json"
        ortho_path = out / "orthography.json"
        intake_path = out / "intake.json"
        meta_path = out / "meta.json"
        if not ev_path.is_file():
            raise RuntimeError(f"missing evaluation.json for {rid}")
        if not ortho_path.is_file():
            raise RuntimeError(f"missing orthography.json for {rid}")
        if not intake_path.is_file():
            raise RuntimeError(f"missing intake.json for {rid}")
        ev = json.loads(ev_path.read_text(encoding="utf-8"))
        ortho = json.loads(ortho_path.read_text(encoding="utf-8"))
        intake = json.loads(intake_path.read_text(encoding="utf-8"))
        meta = (json.loads(meta_path.read_text(encoding="utf-8"))
                if meta_path.is_file() else {})
        m = ev["metrics"]
        od = ortho["metrics"]
        obs.append({
            "run_id": rid,
            "label": pe["label"],
            "provider": pe["provider"],
            "model": pe["model"],
            "model_version": pe["model_version"],
            "condition": pe["condition"],
            "replicate": pe["replicate"],
            "phase2b_role": pe.get("phase2b_role"),
            "intake_verdict": intake.get("verdict"),
            "usable": bool(ev.get("usable")),
            "metrics": {
                "canonical_coverage": float(m["canonical_coverage"]),
                "broader_resource_supported_coverage": float(
                    m["broader_resource_supported_coverage"]),
                "unresolved_rate": float(m["unresolved_rate"]),
                "outside_inventory": float(od["outside_inventory"]),
                "total_tokens": m.get("total_tokens"),
                "canonical_supported_tokens":
                    m.get("canonical_supported_tokens"),
                "unresolved_tokens": m.get("unresolved_tokens"),
            },
            "orthography": {
                "outside_inventory": od["outside_inventory"],
                "cyrillic": od.get("cyrillic"),
                "polish_specific": od.get("polish_specific"),
                "other_latin": od.get("other_latin"),
            },
            "output_sha256": (meta.get("output") or {}).get("sha256"),
            "source_sha256": pe.get("source_sha256"),
            "corpus_sha256": pe.get("corpus_sha256"),
            "artifact_paths": {
                "evaluation": str(ev_path.relative_to(ROOT)),
                "orthography": str(ortho_path.relative_to(ROOT)),
                "intake": str(intake_path.relative_to(ROOT)),
                "output": str((out / "output.txt").relative_to(ROOT)),
            },
        })
    return obs


def integrity_checks(obs: list[dict], plan: dict,
                     regime: str = "high") -> dict:
    """Hard integrity gate. Returns a report; raises RuntimeError on
    failure so aggregates are never produced from a broken ledger."""
    issues: list[str] = []
    planned = plan["runs"]
    if len(obs) != 42:
        issues.append(f"expected 42 evaluated runs, found {len(obs)}")
    if len(planned) != 42:
        issues.append(f"expected 42 planned runs, found {len(planned)}")

    ids = [o["run_id"] for o in obs]
    if len(ids) != len(set(ids)):
        dup = sorted({i for i in ids if ids.count(i) > 1})
        issues.append(f"duplicate run ids: {dup}")

    planned_ids = {r["run_id"] for r in planned}
    obs_ids = set(ids)
    missing = sorted(planned_ids - obs_ids)
    extra = sorted(obs_ids - planned_ids)
    if missing:
        issues.append(f"planned runs missing evaluation: {missing}")
    if extra:
        issues.append(f"extra evaluated runs not in plan: {extra}")

    # Group by configuration
    by_cfg: dict[tuple, dict[str, dict[str, dict]]] = {}
    for o in obs:
        key = _cfg_key(o)
        by_cfg.setdefault(key, {"direct": {}, "primed": {}})
        slot = by_cfg[key][o["condition"]]
        if o["replicate"] in slot:
            issues.append(
                f"duplicate {o['condition']} {o['replicate']} for {key}")
        slot[o["replicate"]] = o

    if len(by_cfg) != 7:
        issues.append(f"expected 7 configurations, found {len(by_cfg)}: "
                      f"{sorted(by_cfg)}")

    expected_keys = set(SHORTLIST_ORDER)
    if set(by_cfg) != expected_keys:
        issues.append(
            f"configuration key mismatch: "
            f"missing={sorted(expected_keys - set(by_cfg))} "
            f"extra={sorted(set(by_cfg) - expected_keys)}")

    for key, conds in by_cfg.items():
        for cond in ("direct", "primed"):
            reps = sorted(conds[cond])
            if reps != ["r01", "r02", "r03"]:
                issues.append(
                    f"{key} {cond}: expected r01..r03, got {reps}")
        for rep in ("r01", "r02", "r03"):
            d = conds["direct"].get(rep)
            p = conds["primed"].get(rep)
            if d is None or p is None:
                issues.append(f"{key} replicate {rep}: missing D or P pair")
                continue
            if d["label"] != p["label"]:
                issues.append(
                    f"{key} {rep}: label mismatch D={d['label']!r} "
                    f"P={p['label']!r}")

    # Metric presence / non-null
    for o in obs:
        for _k, field, _label in METRICS:
            if field == "outside_inventory":
                v = o["metrics"].get("outside_inventory")
            else:
                v = o["metrics"].get(field)
            if v is None:
                issues.append(f"{o['run_id']}: missing metric {field}")
        if not o.get("usable"):
            issues.append(f"{o['run_id']}: usable=False")
        if o.get("intake_verdict") != "complete":
            issues.append(
                f"{o['run_id']}: intake_verdict={o.get('intake_verdict')!r}")

    report = {
        "ok": not issues,
        "n_observations": len(obs),
        "n_configurations": len(by_cfg),
        "n_planned": len(planned),
        "issues": issues,
        "checks": {
            "exactly_42_evaluated": len(obs) == 42,
            "exactly_7_configurations": len(by_cfg) == 7,
            "no_duplicate_run_ids": len(ids) == len(set(ids)),
            "three_direct_three_primed_per_config": all(
                sorted(by_cfg[k]["direct"]) == ["r01", "r02", "r03"]
                and sorted(by_cfg[k]["primed"]) == ["r01", "r02", "r03"]
                for k in by_cfg),
            "every_direct_has_matching_primed_replicate": all(
                set(by_cfg[k]["direct"]) == set(by_cfg[k]["primed"])
                == {"r01", "r02", "r03"}
                for k in by_cfg),
            "all_usable_complete": all(
                o.get("usable") and o.get("intake_verdict") == "complete"
                for o in obs),
        },
    }
    if issues:
        raise RuntimeError(
            f"Phase-2B {regime.upper()} aggregate integrity check FAILED:\n"
            "  - " + "\n  - ".join(issues))
    return report


def _metric_value(o: dict, field: str) -> float:
    return float(o["metrics"][field])


def build_dataset(obs: list[dict], integrity: dict, plan: dict,
                  regime: str = "high") -> dict:
    by_cfg: dict[tuple, dict[str, dict[str, dict]]] = {}
    for o in obs:
        key = _cfg_key(o)
        by_cfg.setdefault(key, {"direct": {}, "primed": {},
                                "label": o["label"],
                                "role": o.get("phase2b_role")})
        by_cfg[key][o["condition"]][o["replicate"]] = o

    configurations = []
    for key in SHORTLIST_ORDER:
        g = by_cfg[key]
        invalid_info = _invalid_low_info(key) if regime == "low" else None
        primary_valid = _cfg_is_primary_valid(regime, key)
        cfg_rec: dict = {
            "config": list(key),
            "label": g["label"],
            "phase2b_role": g["role"],
            "paired_validity": (
                "valid" if primary_valid else "INVALID — MODEL MISMATCH"
            ),
            "primary_analysis_include": primary_valid,
            "invalid_pairing": invalid_info,
            "direct": {},
            "primed": {},
            "paired_deltas": {},
            "observations": {
                "direct": [],
                "primed": [],
            },
        }
        for cond in ("direct", "primed"):
            for rep in ("r01", "r02", "r03"):
                o = g[cond][rep]
                cfg_rec["observations"][cond].append({
                    "run_id": o["run_id"],
                    "replicate": rep,
                    "metrics": {
                        "canonical_coverage":
                            o["metrics"]["canonical_coverage"],
                        "broader_resource_supported_coverage":
                            o["metrics"][
                                "broader_resource_supported_coverage"],
                        "unresolved_rate":
                            o["metrics"]["unresolved_rate"],
                        "outside_inventory":
                            o["metrics"]["outside_inventory"],
                    },
                    "artifact_paths": o["artifact_paths"],
                })

        for short, field, _human in METRICS:
            d_vals = [_metric_value(g["direct"][r], field)
                      for r in ("r01", "r02", "r03")]
            p_vals = [_metric_value(g["primed"][r], field)
                      for r in ("r01", "r02", "r03")]
            deltas = [p_vals[i] - d_vals[i] for i in range(3)]
            cfg_rec["direct"][short] = {
                **stats(d_vals),
                "values": {
                    "r01": d_vals[0], "r02": d_vals[1], "r03": d_vals[2],
                },
            }
            cfg_rec["primed"][short] = {
                **stats(p_vals),
                "values": {
                    "r01": p_vals[0], "r02": p_vals[1], "r03": p_vals[2],
                },
            }
            cfg_rec["paired_deltas"][short] = {
                **stats(deltas),
                "values": {
                    "r01": deltas[0], "r02": deltas[1], "r03": deltas[2],
                },
                "pairs": [
                    {"replicate": "r01",
                     "direct_run_id": g["direct"]["r01"]["run_id"],
                     "primed_run_id": g["primed"]["r01"]["run_id"],
                     "direct": d_vals[0], "primed": p_vals[0],
                     "delta": deltas[0]},
                    {"replicate": "r02",
                     "direct_run_id": g["direct"]["r02"]["run_id"],
                     "primed_run_id": g["primed"]["r02"]["run_id"],
                     "direct": d_vals[1], "primed": p_vals[1],
                     "delta": deltas[1]},
                    {"replicate": "r03",
                     "direct_run_id": g["direct"]["r03"]["run_id"],
                     "primed_run_id": g["primed"]["r03"]["run_id"],
                     "direct": d_vals[2], "primed": p_vals[2],
                     "delta": deltas[2]},
                ],
                "usable_for_primary_priming_analysis": primary_valid,
            }
        configurations.append(cfg_rec)

    primary = [c for c in configurations if c["primary_analysis_include"]]
    invalid = [c for c in configurations if not c["primary_analysis_include"]]
    phase = "p2b-low" if regime == "low" else "p2b-high"
    note = (
        f"Descriptive aggregate of the 42 Phase-2B {regime.upper()} "
        "runs. Paired Δᵢ = Pᵢ − Dᵢ by configuration × replicate. "
        "n = 3 per cell — descriptive only, not inferential. "
        "Every aggregate traces to evaluation.json / "
        "orthography.json under phase2b/outputs/<run_id>/."
    )
    if regime == "low":
        note += (
            " PRIMARY priming aggregates use the "
            f"{len(primary)} valid same-model paired configurations only; "
            f"{len(invalid)} planned configuration(s) are retained but "
            "marked INVALID — MODEL MISMATCH and excluded from primary "
            "mean Δ / HIGH↔LOW priming comparison."
        )
    return {
        "artifact": f"phase2b_{regime}_aggregate_dataset",
        "experiment_id": "exp004",
        "phase": phase,
        "regime": regime,
        "generator": "scripts/analyze_exp004_phase2b.py",
        "note": note,
        "source": plan.get("source"),
        "corpus": plan.get("corpus"),
        "integrity": integrity,
        "metrics": [
            {"key": k, "field": f, "label": lab} for k, f, lab in METRICS
        ],
        "n_runs": len(obs),
        "n_configurations_planned": len(configurations),
        "n_configurations_primary_valid": len(primary),
        "n_configurations_invalid_pairing": len(invalid),
        "n_configurations": len(configurations),
        "configurations": configurations,
        "primary_valid_configurations": [
            c["label"] for c in primary
        ],
        "invalid_pairing_configurations": [
            {
                "label": c["label"],
                "config": c["config"],
                "status": c["paired_validity"],
                "invalid_pairing": c["invalid_pairing"],
            }
            for c in invalid
        ],
        "observations": obs,
    }


def _table_rows_for_cfgs(configurations: list[dict], short: str) -> list[dict]:
    rows = []
    for cfg in configurations:
        d = cfg["direct"][short]
        p = cfg["primed"][short]
        delta = cfg["paired_deltas"][short]
        rows.append({
            "label": cfg["label"],
            "config": cfg["config"],
            "paired_validity": cfg.get("paired_validity", "valid"),
            "primary_analysis_include": cfg.get(
                "primary_analysis_include", True),
            "direct_mean": d["mean"],
            "direct_sd": d["sd"],
            "direct_min": d["min"],
            "direct_max": d["max"],
            "primed_mean": p["mean"],
            "primed_sd": p["sd"],
            "primed_min": p["min"],
            "primed_max": p["max"],
            "delta_mean": delta["mean"],
            "delta_sd": delta["sd"],
            "delta_min": delta["min"],
            "delta_max": delta["max"],
            "delta_values": delta["values"],
        })
    return rows


def _direction_label(delta_values: dict) -> str:
    vals = [delta_values["r01"], delta_values["r02"], delta_values["r03"]]
    if all(v > 0 for v in vals):
        return "all positive"
    if all(v < 0 for v in vals):
        return "all negative"
    if all(v == 0 for v in vals):
        return "all zero"
    return "mixed"


def _matched_high_sensitivity(low_primary: list[dict]) -> dict | None:
    """Descriptive HIGH↔LOW comparison on the same 6 valid LOW configs.

    Reads the frozen HIGH analysis.json if present. Does not modify HIGH.
    """
    high_path = ANALYSIS_ROOT / "analysis.json"
    if not high_path.is_file():
        return None
    high = json.loads(high_path.read_text(encoding="utf-8"))
    high_rows = {
        tuple(r["config"]): r
        for r in high["tables"]["canonical"]["rows"]
    }
    pairs = []
    high_means = []
    low_means = []
    for cfg in low_primary:
        key = tuple(cfg["config"])
        h = high_rows.get(key)
        if h is None:
            continue
        low_d = cfg["paired_deltas"]["canonical"]["mean"]
        pairs.append({
            "label": cfg["label"],
            "config": list(key),
            "high_delta_mean": h["delta_mean"],
            "low_delta_mean": low_d,
            "high_delta_values": h["delta_values"],
            "low_delta_values": cfg["paired_deltas"]["canonical"]["values"],
            "high_direction": _direction_label(h["delta_values"]),
            "low_direction": _direction_label(
                cfg["paired_deltas"]["canonical"]["values"]),
        })
        high_means.append(h["delta_mean"])
        low_means.append(low_d)
    if not pairs:
        return None
    return {
        "label": (
            "matched-configuration sensitivity analysis "
            "(identical 6 configs in HIGH and LOW; Qwen excluded)"
        ),
        "n_configurations": len(pairs),
        "note": (
            "Descriptive only. Unequal to the published HIGH 7-config "
            "aggregate; do not treat as a replacement for HIGH's full "
            "record. Qwen is excluded on both sides so the configuration "
            "sets match."
        ),
        "high_canonical_delta_mean_across_configs":
            statistics.fmean(high_means),
        "low_canonical_delta_mean_across_configs":
            statistics.fmean(low_means),
        "rows": pairs,
    }


def build_analysis(dataset: dict) -> dict:
    regime = dataset.get("regime", "high")
    primary = [c for c in dataset["configurations"]
               if c.get("primary_analysis_include", True)]
    invalid = [c for c in dataset["configurations"]
               if not c.get("primary_analysis_include", True)]

    tables = {}
    for short, _field, human in METRICS:
        tables[short] = {
            "metric": human,
            "scope": "primary_valid_paired_configurations",
            "n_configurations": len(primary),
            "rows": _table_rows_for_cfgs(primary, short),
        }

    invalid_tables = {}
    for short, _field, human in METRICS:
        invalid_tables[short] = {
            "metric": human,
            "scope": "invalid_pairing_retained_not_primary",
            "n_configurations": len(invalid),
            "rows": _table_rows_for_cfgs(invalid, short),
            "warning": (
                "Do not interpret these Δ values as same-model priming "
                "effects."
            ),
        }

    canon_means = [r["delta_mean"] for r in tables["canonical"]["rows"]]
    n_cfg = len(canon_means)
    notes = {
        "n_per_cell": 3,
        "interpretation": "descriptive_only",
        "n_configurations_planned": dataset.get(
            "n_configurations_planned", len(dataset["configurations"])),
        "n_configurations_primary_valid": n_cfg,
        "n_configurations_invalid_pairing": len(invalid),
        "canonical_delta_mean_across_configs":
            statistics.fmean(canon_means) if canon_means else None,
        "canonical_delta_mean_across_configs_n": n_cfg,
        "canonical_delta_mean_label": (
            f"mean of {n_cfg} valid configuration mean-Δ values"
        ),
        "canonical_delta_positive_configs":
            sum(1 for v in canon_means if v > 0),
        "canonical_delta_negative_configs":
            sum(1 for v in canon_means if v < 0),
        "canonical_delta_zero_configs":
            sum(1 for v in canon_means if v == 0),
        "direction_consistency": [
            {
                "label": r["label"],
                "delta_values": r["delta_values"],
                "direction": _direction_label(r["delta_values"]),
            }
            for r in tables["canonical"]["rows"]
        ],
    }
    if regime == "low":
        notes["qwen_low_priming_effect_estimated"] = False
        notes["do_not_use_as_qwen38_low_priming"] = (
            "Any historical −12.08 pp Qwen LOW figure is from an invalid "
            "model-mismatched pair and must not be cited as a Qwen 3.8 Max "
            "priming effect."
        )

    analysis = {
        "artifact": f"phase2b_{regime}_aggregate_analysis",
        "status": "results",
        "generator": "scripts/analyze_exp004_phase2b.py",
        "integrity_ok": dataset["integrity"]["ok"],
        "tables": tables,
        "invalid_pairing_tables": invalid_tables,
        "distribution_notes": notes,
        "disclaimer": (
            "n = 3 replicates per configuration/condition. Results are "
            "descriptive replication/variance characterizations. Do not "
            "treat mean Δ as a statistically established effect."
            + (
                " LOW primary mean Δ uses valid same-model pairs only "
                f"(n={n_cfg} configurations)."
                if regime == "low" else ""
            )
        ),
    }
    if regime == "low":
        analysis["matched_high_sensitivity"] = _matched_high_sensitivity(
            primary)
    return analysis


def _fmt_rate_stats(s: dict) -> str:
    return (f"n={s['n']}  mean={_pct(s['mean'])}%  "
            f"SD={_pct(s['sd'])} pp  "
            f"min={_pct(s['min'])}%  max={_pct(s['max'])}%")


def _fmt_count_stats(s: dict) -> str:
    return (f"n={s['n']}  mean={_num(s['mean'])}  "
            f"SD={_num(s['sd'])}  "
            f"min={_num(s['min'], 0)}  max={_num(s['max'], 0)}")


def _fmt_delta_rate(s: dict) -> str:
    vals = s["values"]
    return (f"Δ r01/r02/r03 = {_pp(vals['r01'])} / {_pp(vals['r02'])} / "
            f"{_pp(vals['r03'])} pp;  mean Δ={_pp(s['mean'])} pp  "
            f"SD(Δ)={_pct(s['sd'])} pp  "
            f"range [{_pp(s['min'])}, {_pp(s['max'])}] pp")


def _fmt_delta_count(s: dict) -> str:
    vals = s["values"]
    return (f"Δ r01/r02/r03 = {_signed(vals['r01'], 0)} / "
            f"{_signed(vals['r02'], 0)} / {_signed(vals['r03'], 0)};  "
            f"mean Δ={_signed(s['mean'])}  SD(Δ)={_num(s['sd'])}  "
            f"range [{_signed(s['min'], 0)}, {_signed(s['max'], 0)}]")


def render_markdown(dataset: dict, analysis: dict) -> str:
    regime = dataset.get("regime", "high")
    regime_u = regime.upper()
    story_label = "LOW" if regime == "low" else "HIGH"
    primary_cfgs = [c for c in dataset["configurations"]
                    if c.get("primary_analysis_include", True)]
    invalid_cfgs = [c for c in dataset["configurations"]
                    if not c.get("primary_analysis_include", True)]
    n_primary = len(primary_cfgs)
    lines: list[str] = []
    status_line = (
        f"**Status:** results written from 42 verified + evaluated runs"
        + (
            f"; **primary priming analysis uses {n_primary} valid "
            f"paired configurations** "
            f"({len(invalid_cfgs)} invalid pairing retained, excluded)."
            if regime == "low" and invalid_cfgs else "."
        )
    )
    lines += [
        f"# EXP-004 Phase 2B {regime_u} — aggregate analysis (descriptive)",
        "",
        status_line,
        "**Generator:** `scripts/analyze_exp004_phase2b.py` (deterministic;",
        "std-lib only; never calls an LLM).",
        "",
        "> **n = 3** replicates per configuration/condition. This report is",
        "> a **descriptive** paired summary of observed values. It does",
        "> **not** establish statistical significance, does **not** claim",
        "> causal corpus-priming effects, and does **not** rank models.",
        "",
    ]
    if regime == "low" and invalid_cfgs:
        lines += [
            "## 0. Validity (LOW)",
            "",
            "| set | n |",
            "|---|---:|",
            "| planned configurations | "
            f"{dataset.get('n_configurations_planned', 7)} |",
            f"| **valid paired configurations (primary)** | "
            f"**{n_primary}** |",
            f"| invalid pairing (retained, excluded from primary) | "
            f"{len(invalid_cfgs)} |",
            "",
        ]
        for inv in invalid_cfgs:
            info = inv.get("invalid_pairing") or {}
            lines += [
                f"**{inv['label']}** — `{inv['paired_validity']}`",
                "",
                f"- Intended model: {info.get('intended_model', '—')}",
                f"- Actual Direct model: "
                f"{info.get('actual_direct_model', '—')}",
                f"- Actual Primed model: "
                f"{info.get('actual_primed_model', '—')}",
                f"- Why invalid: {info.get('why_invalid', '—')}",
                "- Observed Qwen3.8-Max Primed service error "
                "(verbatim; not worked around):",
                "",
                "```",
                info.get("qwen38_primed_service_error", "").rstrip(),
                "```",
                "",
                "- Workaround attempted: **NO**",
                "- Qwen 3.8 Max LOW priming effect: **not estimated**",
                "- Raw outputs / metadata retained for audit "
                f"(see `{info.get('incident_doc', 'QWEN_INCIDENT.md')}`).",
                "",
                "Do **not** cite any historical −12.08 pp Qwen LOW figure "
                "as a Qwen 3.8 Max priming effect.",
                "",
            ]

    lines += [
        "## 1. Data-integrity checks",
        "",
    ]
    integ = dataset["integrity"]
    lines.append(f"Overall: **{'PASS' if integ['ok'] else 'FAIL'}** "
                 f"({integ['n_observations']} observations collected, "
                 f"{integ['n_configurations']} planned configurations; "
                 f"primary valid pairs = {n_primary}).")
    lines.append("")
    lines.append("| check | result |")
    lines.append("|---|---|")
    for k, v in integ["checks"].items():
        lines.append(f"| `{k}` | {'yes' if v else 'NO'} |")
    lines.append("")
    if integ["issues"]:
        lines.append("Issues:")
        for issue in integ["issues"]:
            lines.append(f"- {issue}")
        lines.append("")

    lines += [
        "Provenance pins (from plan):",
        f"- {story_label} story SHA-256: `{dataset['source']['sha256']}`",
        f"- corpus SHA-256: `{dataset['corpus']['sha256']}`",
        "",
        "Every aggregate below traces to "
        "`phase2b/outputs/<run_id>/evaluation.json` and "
        "`orthography.json` (paths listed in `dataset.json`).",
        "",
        "## 2. Cross-configuration summary "
        f"(primary valid pairs only; n={n_primary})",
        "",
    ]

    # Four summary tables — primary only
    for short, _field, human in METRICS:
        is_rate = short != "ortho_out"
        lines.append(f"### {human}")
        lines.append("")
        if is_rate:
            lines.append(
                "| configuration | direct mean (SD) | primed mean (SD) | "
                "mean Δ | SD(Δ) | Δ range |")
            lines.append("|---|---:|---:|---:|---:|---:|")
            for row in analysis["tables"][short]["rows"]:
                lines.append(
                    f"| {row['label']} | "
                    f"{_pct(row['direct_mean'])}% ({_pct(row['direct_sd'])}) | "
                    f"{_pct(row['primed_mean'])}% ({_pct(row['primed_sd'])}) | "
                    f"{_pp(row['delta_mean'])} pp | "
                    f"{_pct(row['delta_sd'])} pp | "
                    f"[{_pp(row['delta_min'])}, {_pp(row['delta_max'])}] pp |"
                )
        else:
            lines.append(
                "| configuration | direct mean (SD) | primed mean (SD) | "
                "mean Δ | SD(Δ) | Δ range |")
            lines.append("|---|---:|---:|---:|---:|---:|")
            for row in analysis["tables"][short]["rows"]:
                lines.append(
                    f"| {row['label']} | "
                    f"{_num(row['direct_mean'])} ({_num(row['direct_sd'])}) | "
                    f"{_num(row['primed_mean'])} ({_num(row['primed_sd'])}) | "
                    f"{_signed(row['delta_mean'])} | "
                    f"{_num(row['delta_sd'])} | "
                    f"[{_signed(row['delta_min'], 0)}, "
                    f"{_signed(row['delta_max'], 0)}] |"
                )
        lines.append("")

    notes = analysis["distribution_notes"]
    if notes.get("canonical_delta_mean_across_configs") is not None:
        lines += [
            f"**Overall descriptive mean Δ (canonical)** across "
            f"**n={notes['canonical_delta_mean_across_configs_n']} "
            f"valid configurations**: "
            f"{_pp(notes['canonical_delta_mean_across_configs'])} pp "
            f"({notes['canonical_delta_positive_configs']} positive / "
            f"{notes['canonical_delta_negative_configs']} negative).",
            "",
        ]

    lines += [
        "## 3. Per-configuration detail (individual D / P / Δ)",
        "",
        "Replicates are independent fresh sessions (r01–r03). "
        "Δᵢ = Pᵢ − Dᵢ for the same replicate tag.",
        "",
        "### 3a. Primary valid configurations",
        "",
    ]
    for cfg in primary_cfgs:
        lines.append(f"### {cfg['label']}")
        lines.append("")
        if cfg.get("phase2b_role"):
            lines.append(f"Role (shortlist note): {cfg['phase2b_role']}")
            lines.append("")
        for short, _field, human in METRICS:
            lines.append(f"**{human}**")
            lines.append("")
            d = cfg["direct"][short]
            p = cfg["primed"][short]
            delta = cfg["paired_deltas"][short]
            if short == "ortho_out":
                lines.append(f"- Direct:  {_fmt_count_stats(d)}")
                lines.append(f"- Primed:  {_fmt_count_stats(p)}")
                lines.append(f"- Paired:  {_fmt_delta_count(delta)}")
            else:
                lines.append(f"- Direct:  {_fmt_rate_stats(d)}")
                lines.append(f"- Primed:  {_fmt_rate_stats(p)}")
                lines.append(f"- Paired:  {_fmt_delta_rate(delta)}")
            lines.append("")
            lines.append("| rep | direct | primed | Δ | direct run_id | "
                         "primed run_id |")
            lines.append("|---|---:|---:|---:|---|---|")
            for pair in delta["pairs"]:
                if short == "ortho_out":
                    lines.append(
                        f"| {pair['replicate']} | "
                        f"{_num(pair['direct'], 0)} | "
                        f"{_num(pair['primed'], 0)} | "
                        f"{_signed(pair['delta'], 0)} | "
                        f"`{pair['direct_run_id']}` | "
                        f"`{pair['primed_run_id']}` |"
                    )
                else:
                    lines.append(
                        f"| {pair['replicate']} | "
                        f"{_pct(pair['direct'])}% | "
                        f"{_pct(pair['primed'])}% | "
                        f"{_pp(pair['delta'])} pp | "
                        f"`{pair['direct_run_id']}` | "
                        f"`{pair['primed_run_id']}` |"
                    )
            lines.append("")

    if invalid_cfgs:
        lines += [
            "### 3b. Invalid pairing (retained; not primary)",
            "",
            "Metrics below are retained for audit completeness only. "
            "**They are not same-model priming effects.**",
            "",
        ]
        for cfg in invalid_cfgs:
            lines.append(f"#### {cfg['label']} — {cfg['paired_validity']}")
            lines.append("")
            delta = cfg["paired_deltas"]["canonical"]
            lines.append(
                f"- Canonical Δ r01/r02/r03 (audit only): "
                f"{_pp(delta['values']['r01'])} / "
                f"{_pp(delta['values']['r02'])} / "
                f"{_pp(delta['values']['r03'])} pp; "
                f"mean={_pp(delta['mean'])} pp — "
                "**do not interpret as Qwen 3.8 Max priming**."
            )
            lines.append("")
            for cond in ("direct", "primed"):
                for o in cfg["observations"][cond]:
                    lines.append(f"- `{cond}` `{o['replicate']}`: "
                                 f"`{o['run_id']}`")
            lines.append("")

    lines += [
        "## 4. Observations about distribution and variance",
        "",
        "- Each cell has **n = 3**. Means and SDs are small-sample "
        "descriptive characterizations, not population estimates.",
        f"- Primary overall mean Δ uses "
        f"**n={notes.get('canonical_delta_mean_across_configs_n', n_primary)} "
        f"valid configurations**"
        + (" (not the 7 planned cells)." if regime == "low" and invalid_cfgs
           else "."),
        "- Do not compare a 6-config LOW aggregate directly to the "
        "published 7-config HIGH aggregate without stating the unequal "
        "configuration sets; see matched sensitivity below when present.",
        "",
    ]
    for item in notes.get("direction_consistency", []):
        vals = item["delta_values"]
        lines.append(
            f"- {item['label']}: Δ "
            f"{_pp(vals['r01'])} / {_pp(vals['r02'])} / "
            f"{_pp(vals['r03'])} pp → **{item['direction']}**"
        )
    lines.append("")

    matched = analysis.get("matched_high_sensitivity")
    if matched:
        lines += [
            "## 5. Matched-configuration HIGH↔LOW sensitivity "
            f"(n={matched['n_configurations']})",
            "",
            matched["note"],
            "",
            f"- HIGH mean Δ (matched 6): "
            f"{_pp(matched['high_canonical_delta_mean_across_configs'])} pp",
            f"- LOW mean Δ (matched 6): "
            f"{_pp(matched['low_canonical_delta_mean_across_configs'])} pp",
            "",
            "| configuration | HIGH mean Δ | LOW mean Δ | "
            "HIGH direction | LOW direction |",
            "|---|---:|---:|---|---|",
        ]
        for row in matched["rows"]:
            lines.append(
                f"| {row['label']} | "
                f"{_pp(row['high_delta_mean'])} pp | "
                f"{_pp(row['low_delta_mean'])} pp | "
                f"{row['high_direction']} | {row['low_direction']} |"
            )
        lines.append("")

    lines += [
        "## 6. Constraints",
        "",
        "- No significance tests.",
        "- No causal corpus-priming claims.",
        "- No model ranking.",
        "- Orthography outside-inventory is a separate diagnostic.",
        "- Unresolved rate is structurally related to canonical coverage.",
        "",
    ]
    return "\n".join(lines) + "\n"


def _flag_anomalies(dataset: dict) -> list[str]:
    """Lightweight descriptive flags only (not scientific conclusions)."""
    flags: list[str] = []
    for cfg in dataset["configurations"]:
        if not cfg.get("primary_analysis_include", True):
            continue
        label = cfg["label"]
        # Sign inconsistency across the three replicate deltas (canonical)
        deltas = list(cfg["paired_deltas"]["canonical"]["values"].values())
        if any(d > 0 for d in deltas) and any(d < 0 for d in deltas):
            flags.append(
                f"{label}: canonical replicate Δs have mixed signs "
                f"({', '.join(f'{v*100:+.2f}' for v in deltas)} pp) — "
                "mean Δ alone is misleading.")
        # Very large within-condition SD relative to |mean Δ|
        d_sd = cfg["direct"]["canonical"]["sd"]
        p_sd = cfg["primed"]["canonical"]["sd"]
        mean_d = cfg["paired_deltas"]["canonical"]["mean"]
        if mean_d is not None and abs(mean_d) > 0:
            if d_sd is not None and d_sd > abs(mean_d):
                flags.append(
                    f"{label}: direct canonical SD "
                    f"({d_sd*100:.2f} pp) exceeds |mean Δ| "
                    f"({abs(mean_d)*100:.2f} pp).")
            if p_sd is not None and p_sd > abs(mean_d):
                flags.append(
                    f"{label}: primed canonical SD "
                    f"({p_sd*100:.2f} pp) exceeds |mean Δ| "
                    f"({abs(mean_d)*100:.2f} pp).")
    return flags


def write_readme(regime: str = "high") -> None:
    out = analysis_dir(regime)
    regime_u = regime.upper()
    plan_path = ("phase2b/outputs/low/plan.json" if regime == "low"
                 else "phase2b/outputs/plan.json")
    if regime == "low":
        cmd = (".venv/bin/python scripts/analyze_exp004_phase2b.py "
               "--regime low")
        generator_note = (
            "outputs of `scripts/analyze_exp004_phase2b.py --regime low`, "
            "derived from\nevaluated runs that stay local"
        )
        contents = (
            "| file | content |\n"
            "|---|---|\n"
            "| `dataset.json` | integrity ledger + 42 observations + "
            "per-config direct/primed stats + paired Δᵢ = Pᵢ − Dᵢ for "
            "canonical / broader / unresolved / orthography-out |\n"
            "| `analysis.json` | machine-readable summary tables + "
            "distribution notes |\n"
            "| `analysis.md` | human-readable descriptive report |\n"
            "| `EVIDENCE.md` | article-ready evidence record "
            "(fact / interpretation / hypothesis) |\n"
            "| `QUALITATIVE_AUDIT.md` | descriptive D→P audit of "
            "**valid** pairs (Qwen mismatch excluded from primary) |\n"
            "| `qualitative_audit.json` | machine-readable pair ledger "
            "for the qualitative audit |\n"
            "| `QWEN_INCIDENT.md` | methodological incident: invalid "
            "Qwen LOW pairing + service error |\n"
            "| `invalid_cells.json` | machine-readable invalid-cell "
            "ledger |"
        )
        extra = (
            "- Does **not** overwrite HIGH artifacts under "
            "`phase2b/analysis/` (parent).\n"
            "- Primary priming aggregates use **6 valid** same-model "
            "paired configurations; Qwen is retained but marked "
            "`INVALID — MODEL MISMATCH`.\n"
        )
    else:
        cmd = ".venv/bin/python scripts/analyze_exp004_phase2b.py"
        generator_note = (
            "outputs of `scripts/analyze_exp004_phase2b.py`, derived from "
            "evaluated\nruns that stay local"
        )
        contents = (
            "| file | content |\n"
            "|---|---|\n"
            "| `dataset.json` | integrity ledger + 42 observations + "
            "per-config direct/primed stats + paired Δᵢ = Pᵢ − Dᵢ for "
            "canonical / broader / unresolved / orthography-out "
            "(each row traces to run IDs + artifact paths) |\n"
            "| `analysis.json` | machine-readable summary tables + "
            "distribution notes |\n"
            "| `analysis.md` | human-readable descriptive report |"
        )
        extra = ""
    text = f"""# Phase 2B {regime_u} — aggregate analysis

Derived artifacts in this directory are **gitignored** (deterministic
{generator_note}); this README is committed.

## Contents

{contents}

## Method

```bash
{cmd}
```

- Reads `{plan_path}` and each run's `evaluation.json` +
  `orthography.json` (already produced by intake).
- Hard integrity gate: 42 runs, 7 configs × 3 direct × 3 primed, unique
  run ids, every D/P pair share replicate tags, all usable/complete.
- **n = 3** → descriptive only; no significance tests; no causal claims.
- Never calls an LLM; never modifies raw outputs / story / corpus.
{extra}"""
    out.mkdir(parents=True, exist_ok=True)
    (out / "README.md").write_text(text, encoding="utf-8")


def run_analyze(regime: str = "high") -> int:
    plan = p2b.load_plan(regime)
    obs = load_observations(regime)
    integrity = integrity_checks(obs, plan, regime)
    dataset = build_dataset(obs, integrity, plan, regime)
    analysis = build_analysis(dataset)
    md = render_markdown(dataset, analysis)

    out = analysis_dir(regime)
    out.mkdir(parents=True, exist_ok=True)
    (out / "dataset.json").write_text(
        json.dumps(dataset, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")
    (out / "analysis.json").write_text(
        json.dumps(analysis, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")
    (out / "analysis.md").write_text(md, encoding="utf-8")
    write_readme(regime)

    print(f"[analyze] Phase-2B {regime.upper()} aggregate written to {out}")
    print(f"  integrity: PASS ({integrity['n_observations']} runs, "
          f"{integrity['n_configurations']} planned configs; "
          f"primary valid="
          f"{dataset.get('n_configurations_primary_valid', 7)})")
    notes = analysis["distribution_notes"]
    n_mean = notes.get("canonical_delta_mean_across_configs_n", 7)
    mean_d = notes.get("canonical_delta_mean_across_configs")
    if mean_d is not None:
        print(f"  canonical mean Δ across {n_mean} valid configs: "
              f"{mean_d*100:+.2f} pp "
              f"(positive {notes['canonical_delta_positive_configs']}/"
              f"{n_mean})")
    if regime == "low" and dataset.get("n_configurations_invalid_pairing"):
        print("  Qwen LOW pairing: INVALID — MODEL MISMATCH "
              "(excluded from primary; priming effect not estimated)")
    print("  note: n=3 descriptive only — see analysis.md")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="EXP-004 Phase 2B HIGH/LOW aggregate analysis "
                    "(descriptive; never calls an LLM)")
    parser.add_argument("--regime", default="high",
                        choices=["high", "low"],
                        help="source-text regime (default: high)")
    parser.add_argument("--check-only", action="store_true",
                        help="run integrity checks only; write nothing")
    args = parser.parse_args(argv)
    if args.check_only:
        plan = p2b.load_plan(args.regime)
        obs = load_observations(args.regime)
        integrity = integrity_checks(obs, plan, args.regime)
        print(json.dumps(integrity, indent=2))
        return 0
    return run_analyze(args.regime)


if __name__ == "__main__":
    sys.exit(main())
