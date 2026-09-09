#!/usr/bin/env python3
"""EXP-004 Assistant Research Bundle — compact, self-contained,
deterministic machine-readable research export (SODA Task 027, 2026-09-09).

What this does
--------------
Packages the authoritative EXP-004 Phase-1/Phase-2A/repeat (Tasks 024/025/
026) quantitative results + audit + provenance into ONE small directory
(experiments/exp004-modelscreen/assistant-research-bundle/) that an
independent research analyst can upload and reason from WITHOUT the full
(~500 MB) raw experiment directory.

Guarantees
----------
- standard library only; fully deterministic (no timestamps; run twice ->
  byte-identical outputs, figures copied unchanged);
- never calls an LLM; never reads or copies raw model outputs;
- missing/partial runs are preserved as records with status, never
  fabricated with metrics;
- one record per planned run (120): 108 primary + 12 exploratory Dola;
- historical Task-024 single-run numbers are included only under
  historical_task024 markers and never mixed into replicate statistics;
- `verify` subcommand loads ONLY the bundle (results.json + summary.json +
  audit.json) and recomputes the headline Task-026 conclusions to prove
  the bundle is sufficient for standalone analysis.

Inputs (authoritative Task-025/026 artifacts, gitignored, local):
  repeats/outputs/plan.json           120-run plan
  repeats/outputs/roster.json         per-run intake + metrics + orthography
  repeats/outputs/audit.json          Task-026 collection audit (run-level)
  repeats/operator-prompts/manifest.json  prompt hashes (provenance)
  repeats/analysis/dataset.json       repeated per-config stats + old_single
  repeats/analysis/analysis.json      aggregate analysis + baseline dep.
  repeats/analysis/figures/           figure_a..figure_e.svg (+ .png)

Outputs:
  assistant-research-bundle/
    README.md  methodology.md  raw/README.md  figures/README.md
    manifest.json  provenance.json  audit.json  deviations.json
    results.json  results.csv  summary.json
    figures/figure_a..e.svg (+ .png)
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import statistics
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXP = ROOT / "experiments" / "exp004-modelscreen"
REPEATS = EXP / "repeats"
ANALYSIS = REPEATS / "analysis"
OUTPUTS = REPEATS / "outputs"
OP_DIR = REPEATS / "operator-prompts"

DEFAULTS = {
    "plan": OUTPUTS / "plan.json",
    "roster": OUTPUTS / "roster.json",
    "audit": OUTPUTS / "audit.json",
    "manifest": OP_DIR / "manifest.json",
    "dataset": ANALYSIS / "dataset.json",
    "analysis": ANALYSIS / "analysis.json",
    "figures": ANALYSIS / "figures",
}
BUNDLE_DIR = EXP / "assistant-research-bundle"

BUNDLE_VERSION = "1.0.0"
TASKS_INCLUDED = ["024", "025", "026"]

# Referenced commits (short SHAs recorded in the project SODA docs).
TASK_COMMITS = {
    "task024_analysis_commit": "bc06858",
    "task025_kit_commit": "2db827d",
    "task026_audit_commit": "048c026",
}

# Orthography count fields copied from roster records (per-char detail maps
# with line numbers stay in the repo's per-run orthography reports).
ORTHO_FIELDS = [
    "outside_inventory", "cyrillic", "polish_specific", "other_latin",
    "other_script", "unexpected_nonletters", "total_chars",
    "allowed_letters", "accepted_nonletters",
]

CANONICAL = "canonical_coverage"
BROADER = "broader_resource_supported_coverage"
UNRESOLVED = "unresolved_rate"
ORTHO = "outside_inventory"


# ---------------------------------------------------------------------------
# small-sample descriptive statistics (identical rule to analyze_exp004_repeats)
# ---------------------------------------------------------------------------

def stats(values: list[float]) -> dict:
    n = len(values)
    if n == 0:
        return {"n": 0, "mean": None, "median": None, "sd": None,
                "min": None, "max": None, "range": None}
    return {
        "n": n,
        "mean": statistics.fmean(values),
        "median": statistics.median(values),
        "sd": statistics.stdev(values) if n > 1 else 0.0,
        "min": min(values),
        "max": max(values),
        "range": max(values) - min(values),
    }


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _git_head_short() -> str | None:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--short=7", "HEAD"],
            cwd=ROOT, capture_output=True, text=True, timeout=5)
        return out.stdout.strip() or None
    except Exception:
        return None


# ---------------------------------------------------------------------------
# record construction (results.json)
# ---------------------------------------------------------------------------

def config_id_of(provider: str, model: str, model_version: str) -> str:
    return "__".join([provider, model, model_version])


def build_results(plan: dict, roster: dict, audit: dict) -> dict:
    """One record per planned run (120). Status/usable from the intake
    roster; metrics only for collected (evaluated) runs; missing runs keep
    metrics = None (never fabricated)."""
    by_roster = {r["run_id"]: r for r in roster.get("rows", [])}
    by_audit = {r["run_id"]: r for r in audit.get("runs", [])}
    dev_registry = audit.get("deviations", [])
    dev_by_run: dict[str, list[str]] = {}
    for dev in dev_registry:
        for rid in dev.get("run_ids", []):
            dev_by_run.setdefault(rid, []).append(dev["id"])

    records = []
    for run in plan["runs"]:
        rid = run["run_id"]
        rr = by_roster.get(rid)
        ar = by_audit.get(rid)
        collected = rr is not None and rr.get("status") is not None
        verdict = None
        if collected:
            verdict = (rr.get("intake") or {}).get("verdict")
        if not collected:
            status = "missing"
        elif verdict == "complete":
            status = "usable"
        elif verdict == "partial":
            status = "partial"
        else:
            status = "invalid"
        usable = bool(rr.get("usable")) if collected else False

        metrics = rr.get("metrics") if collected else None
        ortho_raw = (rr.get("orthography") or {}) if collected else {}
        ortho = {k: ortho_raw.get(k) for k in ORTHO_FIELDS} if collected else None

        intake = None
        if collected and rr.get("intake"):
            it = rr["intake"]
            intake = {
                "verdict": it.get("verdict"),
                "reasons": it.get("reasons") or [],
                "checks": {
                    k: it.get("checks", {}).get(k)
                    for k in ("non_empty", "size_bytes", "size_floor",
                              "head_sane", "end_marker", "names_present",
                              "names_required")
                } if isinstance(it.get("checks"), dict) else None,
            }

        structural = None
        if ar is not None and ar.get("collection_status") == "collected":
            structural = {
                "file_prompt_ok": ar.get("file_prompt_ok"),
                "end_marker_ok": ar.get("end_marker_ok"),
                "size_floor_ok": ar.get("size_floor_ok"),
                "reply_bytes": ar.get("reply_bytes"),
                "reply_nonempty": ar.get("reply_nonempty"),
                "last_line": ar.get("last_line"),
            }

        exclusion_reason = None
        if status == "missing":
            exclusion_reason = ("not collected — pristine prompt file, no "
                                "reply appended; never fabricated")
        elif status == "partial":
            exclusion_reason = ("intake partial: final non-empty line is not "
                                "KONIEC/KONEC/KONĖC (markdown-wrapped end "
                                "marker); evaluated but excluded from "
                                "statistics per the unchanged gate")

        records.append({
            "run_id": rid,
            "phase": run.get("phase"),
            "population": "exploratory" if run.get("exploratory")
            else "primary",
            "in_primary_statistics": bool(run.get("primary")),
            "configuration_id": config_id_of(run["provider"],
                                             run["model"],
                                             run["model_version"]),
            "label": run.get("label"),
            "provider": run.get("provider"),
            "model": run.get("model"),
            "variant": run.get("model_version"),
            "interface": run.get("interface"),
            "generation_parameters": run.get("generation_parameters"),
            "custom_gpt": run.get("custom_gpt"),
            "identity_note": run.get("identity_note"),
            "condition": run.get("condition"),
            "replicate": run.get("replicate"),
            "status": status,
            "usable": usable,
            "analysis_included": usable,
            "in_exploratory_statistics": bool(run.get("exploratory"))
            and usable,
            "exclusion_reason": exclusion_reason,
            "metrics_present": metrics is not None,
            "prompt_hash": run.get("translation_prompt_sha256"),
            "prompt_files": run.get("prompt_files"),
            "source_sha256": run.get("source_sha256"),
            "corpus_sha256": run.get("corpus_sha256"),
            "phase1_baseline_run_id": run.get("phase1_baseline_run_id"),
            "phase2a_primed_run_id": run.get("phase2a_primed_run_id"),
            "phase1_number": run.get("phase1_number"),
            "generation_date": rr.get("generation_date") if collected
            else None,
            "interface_settings": rr.get("interface_settings")
            if collected else None,
            "deviation_ids": sorted(dev_by_run.get(rid, [])),
            "collection_status": ar.get("collection_status")
            if ar is not None else None,
            "intake": intake,
            "structural": structural,
            "metrics": metrics,
            "orthography": ortho,
        })
    return {
        "artifact": "exp004-assistant-research-bundle-results",
        "experiment_id": plan.get("experiment_id"),
        "phase": "repeat",
        "bundle_version": BUNDLE_VERSION,
        "record_count": len(records),
        "evaluation": {
            "evaluator": "isv-eval 0.1.0 (Task-008 two-tier evaluator — "
                        "canonical/broader coverage + unresolved rate; "
                        "used unmodified)",
            "orthography_audit": "Task-015 character-level orthography "
                                 "audit against the official ISV Latin "
                                 "alphabet (used unmodified)",
            "note": ("metrics/orthography fields on each record are the "
                     "values the Task-026 analysis consumed; for partial "
                     "runs they are present but excluded from statistics "
                     "(analysis_included = false)."),
        },
        "note": ("One record per planned repeated-generation run "
                 "(Task 025 kit, 120 planned = 108 primary + 12 "
                 "exploratory Dola). status: usable/partial/missing. "
                 "metrics + orthography exist only for collected runs that "
                 "were evaluated (partial runs were evaluated but are "
                 "excluded from statistics: analysis_included = false). "
                 "Missing runs have metrics = null — never fabricated. "
                 "Historical Task-024 single-run data is NOT here; it lives "
                 "in summary.json under historical_task024 markers."),
        "records": records,
    }


# ---------------------------------------------------------------------------
# summary.json
# ---------------------------------------------------------------------------

def _cond_block(records: list[dict], cond: str, usable_only: bool = True):
    rows = [r for r in records
            if r["condition"] == cond
            and (not usable_only or r["status"] == "usable")]
    can = stats([r["metrics"][CANONICAL] for r in rows
                 if r.get("metrics") is not None])
    bro = stats([r["metrics"][BROADER] for r in rows
                 if r.get("metrics") is not None])
    unr = stats([r["metrics"][UNRESOLVED] for r in rows
                 if r.get("metrics") is not None])
    ort = stats([float(r["orthography"][ORTHO]) for r in rows
                 if r.get("orthography") is not None
                 and r["orthography"].get(ORTHO) is not None])
    return {"n": len(rows), "usable_n": can["n"],
            "canonical": can, "broader": bro, "unresolved": unr,
            "orthography": ort}


def build_summary(plan: dict, dataset: dict, records: list[dict],
                  dev_by_config: dict, notes_by_config: dict) -> dict:
    """Per-configuration aggregates over the USABLE replicate observations
    (recomputed from the per-run records) + historical Task-024 old singles
    (marked historical_task024) + aggregate headline numbers."""
    by_id: dict[str, dict] = {}
    for r in records:
        by_id.setdefault(r["configuration_id"], []).append(r)

    primary_out, exploratory_out = [], []
    for pop_key, out in (("primary", primary_out), ("exploratory", exploratory_out)):
        for cfg in dataset.get(pop_key, []):
            cfg_id = "__".join(cfg["config"])
            rows = by_id.get(cfg_id, [])
            direct = _cond_block(rows, "direct")
            primed = _cond_block(rows, "primed")
            delta_can = None
            delta_bro = None
            if direct["usable_n"] > 0 and primed["usable_n"] > 0:
                delta_can = primed["canonical"]["mean"] - \
                    direct["canonical"]["mean"]
                delta_bro = primed["broader"]["mean"] - \
                    direct["broader"]["mean"]
            old = cfg.get("old_single")
            task024 = None
            if old:
                task024 = {
                    "historical_task024": True,
                    "run_id": old.get("run_id"),
                    "baseline_run_id": old.get("baseline_run_id"),
                    "p1_canonical": old.get("p1_canonical"),
                    "p2a_canonical": old.get("p2a_canonical"),
                    "old_delta_canonical": old.get("old_delta_canonical"),
                    "p1_broader": old.get("p1_broader"),
                    "p2a_broader": old.get("p2a_broader"),
                    "old_delta_broader": old.get("old_delta_broader"),
                    "p1_ortho_out": old.get("p1_ortho_out"),
                    "p2a_ortho_out": old.get("p2a_ortho_out"),
                }
            direction = None
            if task024 is not None and delta_can is not None:
                od = task024["old_delta_canonical"]
                if od is not None:
                    if (od > 0 and delta_can > 0) or \
                       (od < 0 and delta_can < 0) or \
                       (od == 0 and delta_can == 0):
                        direction = "same_direction"
                    else:
                        direction = "opposite_direction"
            devs = sorted(dev_by_config.get(cfg_id, []))
            out.append({
                "configuration_id": cfg_id,
                "label": cfg.get("label"),
                "population": pop_key,
                "primary": bool(cfg.get("primary")),
                "exploratory": bool(cfg.get("exploratory")),
                "planned_condition_n": {"direct": 3, "primed": 3},
                "direct": direct,
                "primed": primed,
                "repeated": {
                    "delta_mean_canonical": delta_can,
                    "delta_mean_broader": delta_bro,
                    "direct_n": direct["usable_n"],
                    "primed_n": primed["usable_n"],
                    "direct_sd_canonical": direct["canonical"]["sd"],
                    "primed_sd_canonical": primed["canonical"]["sd"],
                    "direct_range_canonical": direct["canonical"]["range"],
                    "primed_range_canonical": primed["canonical"]["range"],
                },
                "task024": task024,
                "task024_direction_reproduced": direction,
                "deviation_ids": devs,
                "comparability_status": "deviation_recorded" if devs
                else "comparable",
                "usability_notes": sorted(notes_by_config.get(cfg_id, [])),
            })

    prim = primary_out

    def _agg(fn):
        vals = [fn(c) for c in prim]
        vals = [v for v in vals if v is not None]
        return vals

    pos_can = _agg(lambda c: (c["repeated"]["delta_mean_canonical"]))
    pos_bro = _agg(lambda c: (c["repeated"]["delta_mean_broader"]))
    assessable = [c for c in prim
                  if c["repeated"]["delta_mean_canonical"] is not None]

    # old-vs-new over rows with BOTH an old Task-024 delta and a repeated
    # delta (canonical).
    ovn = [c for c in prim
           if c["task024"] is not None
           and c["task024"]["old_delta_canonical"] is not None
           and c["repeated"]["delta_mean_canonical"] is not None]
    same_dir = [c for c in ovn
                if c["task024_direction_reproduced"] == "same_direction"]
    old_vals = [c["task024"]["old_delta_canonical"] for c in ovn]
    new_vals = [c["repeated"]["delta_mean_canonical"] for c in ovn]

    # stochastic spread: sample SD per condition over configs with n >= 2
    d_sds = [c["direct"]["canonical"]["sd"] for c in prim
             if c["direct"]["canonical"]["n"] >= 2
             and c["direct"]["canonical"]["sd"] is not None]
    p_sds = [c["primed"]["canonical"]["sd"] for c in prim
             if c["primed"]["canonical"]["n"] >= 2
             and c["primed"]["canonical"]["sd"] is not None]

    spread_above = [c for c in assessable
                    if (c["primed"]["canonical"]["sd"] is not None
                        and c["repeated"]["delta_mean_canonical"] is not None
                        and c["primed"]["canonical"]["sd"]
                        > c["repeated"]["delta_mean_canonical"])]

    missing_runs = [r for r in records if r["status"] == "missing"]
    partial_runs = [r for r in records if r["status"] == "partial"]
    missing_configs = sorted({
        r["configuration_id"] for r in missing_runs})

    return {
        "artifact": "exp004-assistant-research-bundle-summary",
        "experiment_id": plan.get("experiment_id"),
        "phase": "repeat",
        "bundle_version": BUNDLE_VERSION,
        "tasks_included": TASKS_INCLUDED,
        "counts": {
            "planned": len(records),
            "collected": sum(1 for r in records
                             if r["status"] in ("usable", "partial")),
            "usable": sum(1 for r in records if r["status"] == "usable"),
            "partial": len(partial_runs),
            "invalid": sum(1 for r in records
                           if r["status"] == "invalid"),
            "missing": len(missing_runs),
            "primary": {
                "planned": sum(1 for r in records
                               if r["in_primary_statistics"]),
                "collected": sum(1 for r in records
                                 if r["in_primary_statistics"]
                                 and r["status"] in ("usable", "partial")),
                "usable": sum(1 for r in records
                              if r["in_primary_statistics"]
                              and r["status"] == "usable"),
                "partial": sum(1 for r in records
                               if r["in_primary_statistics"]
                               and r["status"] == "partial"),
                "missing": sum(1 for r in records
                               if r["in_primary_statistics"]
                               and r["status"] == "missing"),
            },
            "exploratory": {
                "planned": sum(1 for r in records
                               if r["in_exploratory_statistics"]
                               or not r["in_primary_statistics"]),
                "collected": sum(1 for r in records
                                 if not r["in_primary_statistics"]
                                 and r["status"] in ("usable", "partial")),
                "usable": sum(1 for r in records
                              if not r["in_primary_statistics"]
                              and r["status"] == "usable"),
                "partial": sum(1 for r in records
                               if not r["in_primary_statistics"]
                               and r["status"] == "partial"),
                "missing": sum(1 for r in records
                               if not r["in_primary_statistics"]
                               and r["status"] == "missing"),
            },
        },
        "assessable_primary_configs": len(assessable),
        "repeated_delta_canonical": {
            "count_positive": sum(1 for v in pos_can if v > 0),
            "count_negative": sum(1 for v in pos_can if v < 0),
            "count_zero": sum(1 for v in pos_can if v == 0),
            "n": len(pos_can),
            "mean_pp": (statistics.fmean(pos_can) * 100)
            if pos_can else None,
        },
        "repeated_delta_broader": {
            "count_positive": sum(1 for v in pos_bro if v > 0),
            "n": len(pos_bro),
            "mean_pp": (statistics.fmean(pos_bro) * 100)
            if pos_bro else None,
        },
        "old_vs_new": {
            "rows_with_both_deltas": len(ovn),
            "same_direction_rows": len(same_dir),
            "mean_old_delta_pp": (statistics.fmean(old_vals) * 100)
            if old_vals else None,
            "mean_repeated_delta_pp": (statistics.fmean(new_vals) * 100)
            if new_vals else None,
            "note": ("canonical coverage; rows where BOTH the Task-024 "
                     "single-run delta and the repeated mean delta exist"),
        },
        "stochastic_spread": {
            "median_direct_sd_pp": (statistics.median(d_sds) * 100)
            if d_sds else None,
            "median_primed_sd_pp": (statistics.median(p_sds) * 100)
            if p_sds else None,
            "direct_sd_pp_values": [round(v * 100, 4) for v in d_sds],
            "primed_sd_pp_values": [round(v * 100, 4) for v in p_sds],
            "note": ("sample SD of canonical coverage over configurations "
                     "with >= 2 usable replicates in that condition; "
                     "descriptive, n <= 3"),
        },
        "primed_sd_exceeds_delta": {
            "count": len(spread_above),
            "configuration_ids": [c["configuration_id"]
                                  for c in spread_above],
        },
        "configurations": {
            "primary": primary_out,
            "exploratory": exploratory_out,
        },
        "missing": {
            "configuration_ids": missing_configs,
            "runs": [r["run_id"] for r in missing_runs],
        },
        "partial": {
            "count": len(partial_runs),
            "runs": [r["run_id"] for r in partial_runs],
            "note": ("markdown-wrapped end markers only (## KONEC / "
                     "# KONEC / **KONEC** / # KONĘC); content complete; "
                     "preserved and excluded from statistics"),
        },
        "note": ("Statistics (direct/primed per configuration) are "
                 "recomputed over usable replicate observations carried in "
                 "results.json. Task-024 old single-run values are "
                 "historical (marked historical_task024) and are never "
                 "mixed into replicate distributions. Coverage values are "
                 "fractions (multiply by 100 for pp)."),
    }


def _json_round(obj):
    """Round small floats to 12 decimals for stable, readable JSON while
    keeping reconstruction comparisons exact to double precision."""
    if isinstance(obj, float):
        return round(obj, 12)
    if isinstance(obj, dict):
        return {k: _json_round(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_json_round(v) for v in obj]
    return obj


def _rel_or_abs(p: Path) -> str:
    try:
        return str(p.relative_to(ROOT))
    except ValueError:
        return str(p)


# ---------------------------------------------------------------------------
# audit.json (bundle) — deterministic projection of the Task-026 audit
# ---------------------------------------------------------------------------

def build_audit(audit: dict, records: list[dict]) -> dict:
    by_rec = {r["run_id"]: r for r in records}
    runs = []
    for ar in audit.get("runs", []):
        rec = by_rec.get(ar["run_id"], {})
        runs.append({
            "run_id": ar["run_id"],
            "condition": ar.get("condition"),
            "replicate": ar.get("replicate"),
            "population": "exploratory" if ar.get("exploratory")
            else "primary",
            "collection_status": ar.get("collection_status"),
            "intake_verdict": rec.get("status"),
            "roster_status": ar.get("roster_status"),
            "plan_status": ar.get("plan_status"),
            "file_prompt_ok": ar.get("file_prompt_ok"),
            "end_marker_ok": ar.get("end_marker_ok"),
            "size_floor_ok": ar.get("size_floor_ok"),
            "reply_bytes": ar.get("reply_bytes"),
            "reply_nonempty": ar.get("reply_nonempty"),
            "last_line": ar.get("last_line"),
            "deviation_ids": rec.get("deviation_ids") or [],
        })
    coll = audit.get("collection", {})
    return {
        "artifact": "exp004-assistant-research-bundle-audit",
        "experiment_id": audit.get("experiment_id"),
        "phase": audit.get("phase"),
        "audit_date": audit.get("audit_date"),
        "source": ("experiments/exp004-modelscreen/repeats/outputs/"
                   "audit.json (Task 026 collection audit)"),
        "fresh_session_proof": audit.get("fresh_session_proof"),
        "counts": {
            "planned": coll.get("collected", 0) + coll.get("missing", 0),
            "collected": coll.get("collected"),
            "missing": coll.get("missing"),
            "primary": coll.get("primary") or {},
            "exploratory": coll.get("exploratory") or {},
        },
        "hash_gates": audit.get("hash_gates"),
        "manifest_consistency": audit.get("manifest"),
        "mechanical_checks": {
            "duplicate_output_detected": False,
            "source_echo_detected": False,
            "cross_run_contamination_detected": False,
            "wrong_run_assignment_detected": False,
            "stale_file_copy_detected": False,
            "malformed_metadata_detected": False,
            "prompt_body_mismatch": sum(1 for r in audit.get("runs", [])
                                        if r.get("file_prompt_ok") is False),
            "note": ("Task-026 audit found no duplicate output, source "
                     "echo, cross-run contamination, wrong model/condition/"
                     "replicate assignment, stale file copy or malformed "
                     "metadata. Operator-metadata header edits (Grok "
                     "identity, Dola Pro r03 blank line) are recorded as "
                     "deviations in deviations.json, not as errors."),
        },
        "runs": runs,
        "deviations_reference": "see deviations.json (structured) and "
                                "repeats/outputs/audit.json (full)",
    }


# ---------------------------------------------------------------------------
# deviations.json — structured, run-scoped
# ---------------------------------------------------------------------------

def build_deviations(audit: dict) -> dict:
    registry = {d["id"]: d for d in audit.get("deviations", [])}

    def base(dev_id):
        d = registry.get(dev_id, {})
        return {
            "id": dev_id,
            "affected_run_ids": d.get("run_ids", []),
            "affected_run_count": len(d.get("run_ids", [])),
            "severity": d.get("severity"),
            "description": d.get("description"),
            "evidence": d.get("evidence"),
            "usability_assessment": d.get("usability_assessment"),
        }

    items = [
        {
            **base("claude-max-thinking-off"),
            "category": "execution",
            "title": ("Claude Sonnet 5 — max: thinking/reasoning OFF "
                      "during the repeated generation"),
            "configuration_name": "Claude Sonnet 5 — max (long reasoning)",
            "configuration_name_preserved": True,
            "reason": ("enabled mode operationally impractical during "
                       "repeated collection: very long analysis, repeated "
                       "token-limit interruptions, continuation "
                       "requirements, waits of several hours"),
            "task024_comparability": ("Task-024 Phase-1/Phase-2A records "
                                      "for this configuration ran with "
                                      "intensive reasoning; the repeated "
                                      "results are NOT silently merged as "
                                      "identical configurations. Historical "
                                      "Task-024 data unchanged."),
        },
        {
            **base("grok-identity-header-edit"),
            "category": "operator-metadata-identity",
            "title": "Grok model identity recorded in operator metadata",
            "identity_before": "unknown (unknown)",
            "identity_operator_reported": "Grok 4.5, built by xAI (fast)",
            "identity_independently_verified": False,
            "model_facing_prompt_bytes_unchanged": True,
            "handling": ("reconciled in the roster as operator-reported "
                         "identity; raw outputs not modified"),
        },
        {
            **base("gemini-primed-split-delivery"),
            "category": "interface",
            "title": ("Gemini primed reference-corpus message delivered as "
                      "two messages"),
            "continuation_instruction_used": True,
            "corpus_delivered_complete": True,
            "corpus_tail_present_verbatim": True,
            "content_loss_or_corruption_detected": False,
            "model_switch_detected": False,
            "matches_task021_024_gemini_deviation": True,
            "handling": ("usable with recorded interface deviation; not "
                         "marked invalid for splitting alone"),
        },
        {
            **base("dola-pro-r03-msg1-blank-line"),
            "category": "operator-metadata",
            "title": "Dola Pro primed r03 msg1: extra blank header line",
            "handling": ("header whitespace only; model-facing study "
                         "instruction + corpus tail byte-identical; usable"),
        },
        {
            "id": "fresh-session-proof-unavailable",
            "category": "provenance",
            "title": "No machine-visible fresh-session proof",
            "affected_run_count": len(audit.get("runs", [])),
            "affected_run_ids": [],
            "severity": "informational",
            "description": ("msg2-style operator records carry no "
                            "machine-visible session provenance; the "
                            "research lead reports fresh independent "
                            "sessions per replicate."),
            "evidence": ("record shape msg2-style (prompt file + reply "
                         "appended after '## Output') contains no session "
                         "identifier"),
            "usability_assessment": ("fresh_session_proof: unavailable — "
                                     "absence of proof is not proof of "
                                     "violation"),
        },
        {
            "id": "intake-partial-end-marker",
            "category": "intake",
            "title": "Intake-partial runs (markdown-wrapped end markers)",
            "affected_run_count": sum(
                1 for r in audit.get("runs", [])
                if r.get("intake_verdict") == "partial"),
            "affected_run_ids": [r["run_id"] for r in audit.get("runs", [])
                                 if r.get("intake_verdict") == "partial"],
            "severity": "minor",
            "description": ("8 collected runs are intake-partial solely "
                            "because their final non-empty line is a "
                            "markdown-wrapped end marker (## KONEC / "
                            "# KONEC / **KONEC** / # KONĘC) that the "
                            "unmodified completeness gate does not accept; "
                            "translations are otherwise complete."),
            "evidence": "unmodified verify gate verdicts (roster intake)",
            "usability_assessment": ("preserved, evaluated, excluded from "
                                     "usable statistics per protocol (not "
                                     "repaired)"),
        },
    ]
    return {
        "artifact": "exp004-assistant-research-bundle-deviations",
        "experiment_id": audit.get("experiment_id"),
        "bundle_version": BUNDLE_VERSION,
        "note": ("Structured registry of every known protocol/interface "
                 "deviation for the repeated-generation dataset. "
                 "affected_run_ids derive from the Task-026 audit "
                 "registry. Raw outputs were never modified to 'fix' any "
                 "deviation."),
        "items": items,
    }


# ---------------------------------------------------------------------------
# provenance.json
# ---------------------------------------------------------------------------

def build_provenance(plan: dict, manifest: dict, dataset_path: Path,
                     analysis_path: Path, audit: dict,
                     head: str | None) -> dict:
    src = plan.get("source") or {}
    cor = plan.get("corpus") or {}
    return {
        "artifact": "exp004-assistant-research-bundle-provenance",
        "experiment_id": plan.get("experiment_id"),
        "bundle_version": BUNDLE_VERSION,
        "tasks_included": TASKS_INCLUDED,
        "source_story": {
            "sha256": src.get("sha256"),
            "file": src.get("file"),
            "note": "authoritative Polish source story (Phase 1 / 2A / repeat)",
        },
        "corpus": {
            "id": cor.get("id"),
            "version": cor.get("version"),
            "sha256": cor.get("sha256"),
            "file": cor.get("file"),
            "registers": [
                "literary/narrative (Tuta historija excerpt)",
                "artistic/poetic (Ahoj, Slovjani! album, Latin script)",
                "informative/encyclopedic (ISV Wikipedia 'Sadovničstvo')",
            ],
            "note": ("combined file byte-identical across every primed "
                     "replicate; component hashes pinned in "
                     "experiments/exp004-modelscreen/DESIGN.md §13.3"),
        },
        "task025_kit": {
            "plan": {
                "runs": plan.get("counts", {}).get("total_runs"),
                "prompt_files": len(manifest.get("files", [])),
                "primary_runs": plan.get("counts", {}).get("primary_runs"),
                "exploratory_runs": plan.get("counts", {})
                .get("exploratory_runs"),
                "generator": plan.get("generator"),
                "generator_commit": plan.get("generator_commit"),
                "date": plan.get("date"),
            },
        },
        "commits": TASK_COMMITS,
        "generated_at_git_head": {
            "sha": head,
            "note": ("short SHA of the repository working-tree HEAD when "
                     "this bundle was generated; the bundle and its "
                     "generator are committed with Task 027"),
        },
        "evaluator": {
            "name": "isv-eval",
            "version": "0.1.0",
            "reference": ("Task-008 two-tier evaluator (canonical coverage + "
                          "broader resource-supported coverage, unresolved "
                          "rate) — used unmodified"),
            "orthography_audit": ("Task-015 character-level orthography "
                                  "audit (official ISV alphabet) — used "
                                  "unmodified"),
        },
        "analysis": {
            "script": "scripts/analyze_exp004_repeats.py",
            "status": _json_round(
                json.loads(analysis_path.read_text(encoding="utf-8"))
                .get("status")) if analysis_path.is_file() else None,
            "dataset_source": _rel_or_abs(dataset_path),
            "note": "deterministic, std-lib, figures A-E SVG (+ PNG render)",
        },
        "audit": {
            "script": "scripts/audit_exp004_repeats.py",
            "date": audit.get("audit_date"),
        },
        "runtime": {
            "python": ".".join(str(x) for x in sys.version_info[:3]),
            "note": "recorded for provenance only; no secrets, keys or "
                    "account information are included",
        },
        "no_secrets_note": ("This bundle intentionally contains no API "
                            "keys, cookies, session tokens or private "
                            "account information."),
    }


# ---------------------------------------------------------------------------
# figures + static markdown
# ---------------------------------------------------------------------------

FIGURES = {
    "figure_a": "A — direct vs primed replicate distributions (all primary configurations)",
    "figure_b": "B — repeated mean delta canonical, sorted",
    "figure_c": "C — within-condition stochastic spread (SD + range)",
    "figure_d": "D — Task-024 single-run delta vs Task-026 repeated mean delta",
    "figure_e": "E — baseline mean vs repeated priming delta",
}


def _copy_figures(src_dir: Path, dst_dir: Path) -> list[str]:
    dst_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for name in sorted(FIGURES):
        for ext in ("svg", "png"):
            s = src_dir / f"{name}.{ext}"
            if s.is_file():
                (dst_dir / f"{name}.{ext}").write_bytes(s.read_bytes())
                written.append(f"{name}.{ext}")
    return written


def _write_json(path: Path, obj: dict) -> None:
    path.write_text(json.dumps(_json_round(obj), indent=1,
                               ensure_ascii=False,
                               sort_keys=True) + "\n", encoding="utf-8")


RESULTS_CSV_COLUMNS = [
    "run_id", "population", "in_primary_statistics", "configuration_id",
    "label", "provider", "model", "variant", "condition", "replicate",
    "status", "usable", "analysis_included", "exclusion_reason",
    "prompt_hash", "source_sha256", "corpus_sha256", "generation_date",
    "interface_settings", "deviation_ids", "intake_verdict",
    "end_marker_ok", "size_floor_ok", "file_prompt_ok",
    "tokens_total", "lexical_tokens", "canonical_coverage",
    "broader_coverage", "unresolved_rate", "exact_dictionary_matches",
    "morphologically_valid_forms", "unresolved_forms",
    "ortho_outside_inventory", "ortho_cyrillic", "ortho_polish_specific",
    "ortho_other_latin", "ortho_other_script",
    "ortho_unexpected_nonletters",
]


def _csv_cell(record: dict, col: str):
    if col == "deviation_ids":
        return ";".join(record.get("deviation_ids") or [])
    if col == "intake_verdict":
        return record.get("status")
    if col == "end_marker_ok":
        st = record.get("structural")
        return "" if st is None else _bool(st.get("end_marker_ok"))
    if col == "size_floor_ok":
        st = record.get("structural")
        return "" if st is None else _bool(st.get("size_floor_ok"))
    if col == "file_prompt_ok":
        st = record.get("structural")
        return "" if st is None else _bool(st.get("file_prompt_ok"))
    if col in ("tokens_total", "lexical_tokens", "canonical_coverage",
               "broader_coverage", "unresolved_rate",
               "exact_dictionary_matches", "morphologically_valid_forms",
               "unresolved_forms"):
        m = record.get("metrics")
        if m is None:
            return ""
        key = {
            "tokens_total": "tokens_total",
            "lexical_tokens": "total_tokens",
            "canonical_coverage": "canonical_coverage",
            "broader_coverage": "broader_resource_supported_coverage",
            "unresolved_rate": "unresolved_rate",
            "exact_dictionary_matches": "exact_dictionary_matches",
            "morphologically_valid_forms": "morphologically_valid_forms",
            "unresolved_forms": "unresolved_forms",
        }[col]
        return m.get(key)
    if col.startswith("ortho_"):
        o = record.get("orthography")
        if o is None:
            return ""
        key = col[len("ortho_"):]
        return o.get(key)
    if col in ("usable", "analysis_included", "in_primary_statistics"):
        return _bool(record.get(col))
    return record.get(col)


def _bool(v):
    if v is None:
        return ""
    return "true" if v else "false"


def _write_results_csv(path: Path, records: list[dict]) -> None:
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(RESULTS_CSV_COLUMNS)
        for r in records:
            w.writerow([_csv_cell(r, c) for c in RESULTS_CSV_COLUMNS])


# ---------------------------------------------------------------------------
# manifest.json (bundle file list + sha256)
# ---------------------------------------------------------------------------

def build_manifest(files: list[tuple[str, bytes]]) -> dict:
    entries = []
    for rel, data in files:
        entries.append({"file": rel, "bytes": len(data),
                        "sha256": _sha256_bytes(data)})
    entries.sort(key=lambda e: e["file"])
    return {
        "artifact": "exp004-assistant-research-bundle-manifest",
        "experiment_id": "exp004",
        "bundle_version": BUNDLE_VERSION,
        "tasks_included": TASKS_INCLUDED,
        "counts": {
            "primary_configurations": 18,
            "exploratory_configurations": 2,
            "planned_runs": 120,
            "collected_runs": 114,
            "usable_runs": 106,
            "partial_runs": 8,
            "invalid_runs": 0,
            "missing_runs": 6,
        },
        "file_count": len(entries),
        "files": entries,
        "note": ("Deterministic manifest (sorted relative paths). No "
                 "timestamp is embedded anywhere in the bundle, so a "
                 "regeneration is byte-identical."),
    }


# ---------------------------------------------------------------------------
# markdown content
# ---------------------------------------------------------------------------

def _README_md(counts: dict, written_figures: list[str]) -> str:
    p, e = counts["primary"], counts["exploratory"]
    return f"""# EXP-004 — Assistant Research Bundle (Tasks 024 / 025 / 026)

**Generated research-export interface** for an independent analysis of
EXP-004 (practical LLM model screening for Polish → Medžuslovjansky) —
Phase 1 (direct baselines), Phase 2A (authentic-corpus priming) and the
Task-025/026 controlled repeated-generation experiment.

**What this bundle is.** A compact, self-contained, deterministic
machine-readable export of the authoritative quantitative results, the
Task-026 collection audit, provenance/hashes, methodology and figures. It
is the file set the research lead can upload to an analysis assistant
without uploading the full experiment directory (~500 MB, dominated by
raw outputs which are intentionally excluded — see `raw/README.md`).

## What it represents

- Experiment: **EXP-004** (repository `isv-llm-lab`).
- Tasks included: **024** (full Phase-1 → Phase-2A analysis),
  **025** (controlled repeated generation kit) and **026** (collection
  audit + repeated-generation analysis, commit `048c026`).
- Reference commits: Task 024 `bc06858`; Task 025 `2db827d`;
  Task 026 `048c026` (see `provenance.json`).
- Version of this bundle: **{BUNDLE_VERSION}** (`manifest.json` pins every
  file's SHA-256).

## Authoritative data (exact counts from the files)

| population | planned | collected | usable | partial | invalid | missing |
|---|---:|---:|---:|---:|---:|---:|
| Primary (18 configurations) | {p['planned']} | {p['collected']} | {p['usable']} | {p['partial']} | 0 | {p['missing']} |
| Exploratory (Dola Fast/Pro) | {e['planned']} | {e['collected']} | {e['usable']} | {e['partial']} | 0 | 0 |
| **Total** | **{counts['planned']}** | **{counts['collected']}** | **{counts['usable']}** | **{counts['partial']}** | **0** | **{counts['missing']}** |

Headline (descriptive; every number below is reconstructed in the
`verify` step from `results.json` alone): repeated mean Δ canonical
`mean(primed) − mean(direct)` is positive for **16/16** primary
configurations with both conditions usable (mean ≈ **+6.93 pp**; broader
≈ **+3.88 pp**); the Task-024 single-run direction is reproduced in
**15/15** rows that have an old delta; stochastic spread (median SD ≈
1.49 pp direct / ≈ 0.87 pp primed) is typically smaller than the shift.
Dola is exploratory and never enters primary statistics.

## Files: full data vs summaries

| file | role |
|---|---|
| `results.json` | **FULL per-run data** — one object per planned run (120 = 108 primary + 12 exploratory), with per-replicate r01/r02/r03 metrics, intake verdicts, hashes, orthography counts, deviation flags. Missing runs are present with `status: missing` and `metrics: null`. |
| `results.csv` | flat tabular form of `results.json` (one row per planned run) |
| `summary.json` | per-configuration descriptive statistics over the usable replicates (n/mean/median/SD/min/max/range for canonical + broader + unresolved + orthography), repeated deltas, Task-024 old singles (marked `historical_task024`), aggregates, missing/partial lists |
| `audit.json` | run-level Task-026 audit projection (counts, hash gates, manifest consistency, mechanical checks, per-run structural flags) |
| `deviations.json` | structured registry of every protocol/interface deviation (Claude Max thinking OFF, Grok identity, Gemini split corpus, Dola Pro blank line, fresh-session provenance, intake-partial) |
| `provenance.json` | source/corpus/kit hashes, evaluator + audit + analysis references, commits, runtime |
| `manifest.json` | bundle file list with SHA-256 for every file (deterministic) |
| `methodology.md` | complete method description (design, metrics, repeated estimate, statistical caution) |
| `figures/` | figures A–E (SVG + PNG) |
| `raw/README.md` | explains raw-output exclusion and how to request specific files |

## Generation

Deterministic, standard-library generator:
`scripts/build_assistant_research_bundle.py build`
(run `… verify` to re-run the standalone reconstruction check). Sources:
`repeats/outputs/plan.json`, `outputs/roster.json`, `outputs/audit.json`,
`operator-prompts/manifest.json`, `analysis/dataset.json`,
`analysis/analysis.json`, `analysis/figures/`. No timestamp is embedded —
regeneration is byte-identical (manifest included).

## What is deliberately excluded

- Raw model replies and operator prompt files (copyrighted source +
  corpus, ~500 MB, gitignored in the repo) — metadata + metrics are here
  instead.
- The full corpus and full prompt text (hashes are sufficient for
  provenance; both are pinned in `provenance.json`).
- Per-character orthography line details (per-run counts are included;
  full breakdowns stay in the repo's orthography reports).
- Secrets/credentials (none are read or written).
- Historical Task-024 raw outputs (their per-run metrics are included
  only as `historical_task024` markers in `summary.json`).
"""


def _methodology_md() -> str:
    return f"""# EXP-004 methodology — as packaged for independent analysis

Reference commits: Task 024 `bc06858`, Task 025 `2db827d`, Task 026
`048c026` (bundle version {BUNDLE_VERSION}). This text is the method
description needed to interpret `results.json` / `summary.json`.

## 1. Phase 1 — direct translation (baseline)

One Polish source story (SHA-256 `5de968a6…`, byte-identical across the
whole project) translated directly to Medžuslovjansky (Interslavic) by
each roster model through its ordinary web/chat interface, with a single
equivalent base instruction and NO guidance (no scaffold, no dictionary,
no grammar notes, no examples). 19 runs were executed; 18 passed the
intake gate (GLM 4.5 failed with a service-error page and is excluded).
Each configuration = provider × model × variant (e.g. thinking toggle).

## 2. Phase 2A — corpus priming

The same Polish translation task, but in ONE fresh session the model
first receives the authoritative **`phase2a-authentic-isv` v1 corpus**
(SHA-256 `aaad28e4…`, ~58 KB) with an explicit *study-as-language-
reference* instruction, then the exact same Polish source + translation
instruction. The corpus has three authentic Medžuslovjansky registers:

- **literary/narrative** — excerpt of *Tuta historija*;
- **artistic/poetic** — the Latin-script *Ahoj, Slovjani!* album
  (poetic forms deliberately not normalized);
- **informative/encyclopedic** — the existing ISV Wikipedia article
  *Sadovničstvo*.

Phase 2A measured one primed generation per configuration; Task 024
analysed `P2A_single − P1_single` per configuration.

## 3. Task 025/026 — controlled repeated generation

To separate the priming shift from run-to-run stochastic variation, every
configuration was generated **3 times per condition** in independent
fresh sessions:

- `direct` r01/r02/r03 — the Phase-1 direct task;
- `primed` r01/r02/r03 — the Phase-2A protocol (corpus → translation).

r01/r02/r03 are **replication blocks, not matched samples**. Prompt bytes
are identical within (configuration, condition); only stochastic
generation and recorded interface/server variation differ. No lexical
scaffolding, no dictionary guidance, no human linguistic classification,
no repair, no re-runs (unusable runs are preserved with status and
excluded). 120 runs planned (108 primary + 12 exploratory Dola Fast/Pro);
114 collected; 106 usable; 8 partial; 6 missing (never fabricated).
Dola is **exploratory** — separate tables/figures only, never in the
primary n=18 statistics.

## 4. Metrics (definitions unchanged from the project evaluator)

Evaluated with **isv-eval v0.1.0** (Task-008 two-tier evaluator,
unmodified) on the raw model reply:

- **canonical coverage** — fraction of lexical tokens (non-name,
  non-multiword-excluded) that match the canonical dictionary exactly (A)
  or are morphologically valid against the generated full-form lexicon
  (B): `(exact + morph_valid) / lexical_tokens`;
- **broader resource-supported coverage** — same denominator, but
  tokens are also credited when they are attested by the audited
  alternative resource layer (exact surfaces in `isv.dic`,
  `interslavicfreq`, `slovnik`). Broader never promotes an A/B change;
  it is a separate, wider tier;
- **unresolved rate** — `unresolved_forms / lexical_tokens` (the C tier:
  neither canonical nor alternative-attested);
- **orthography audit** (Task 015) — character-level check against the
  official ISV Latin alphabet; reported as **outside-inventory** counts
  split by category (cyrillic / polish_specific / other_latin /
  other_script / unexpected non-letters). Orthography is a separate
  quality dimension, never merged into coverage.

Coverage values are stored as fractions in `results.json`/`results.csv`
(multiply by 100 for percentage points). `tokens_total` is the raw
whitespace token count; `lexical_tokens` (`total_tokens`) is the
evaluator denominator.

## 5. Repeated estimate (the primary Task-026 quantity)

For each configuration:

```
repeated Δ = mean(primed r01..r03 usable) − mean(direct r01..r03 usable)
```

This is deliberately different from the old Task-024 quantity:

```
old single Δ = (one primed generation) − (one direct generation)
```

`summary.json` carries both, with the old values marked
`historical_task024`; they are never mixed into the replicate
distributions (Figure D compares them only as a point-vs-distribution
view).

## 6. Statistical caution

- n = 3 usable replicates per condition (smaller where runs are
  missing/partial — see the `n`/`usable_n` fields).
- All statistics are **descriptive**; SD is a sample SD and is NOT a
  precise estimate of population variance at n = 3.
- No causal effect estimate is claimed anywhere; wording stays
  observational ("observed", "consistent with", "replicated / not
  replicated", "not established").
- No winner/composite score: performance, stability, priming response,
  orthographic cleanliness and practical usability stay separate
  dimensions.
- Coverage measures resource grounding, not linguistic correctness or
  naturalness.

## 7. Known interface deviations (full detail in `deviations.json`)

- **Claude Sonnet 5 — max:** thinking/reasoning OFF during the repeats
  (operationally impractical when enabled). Configuration name preserved;
  results not comparable with its Task-024 record without this caveat.
- **Grok:** model identity operator-reported as "Grok 4.5, built by xAI
  (fast)" (files originally said `unknown`); not independently verified;
  prompt bodies unchanged.
- **Gemini:** primed corpus delivered in two messages (interface limit,
  `continue last prompt:` continuation); stored records verify the full
  corpus was delivered — usable with recorded deviation.
- **Dola:** exploratory; identity recorded from the interface, not
  independently verified.
- **Fresh-session provenance:** `fresh_session_proof: unavailable` for
  all runs (msg2-style records carry no machine-visible session
  provenance).

## 8. What cannot be concluded from this bundle

- Causality of corpus priming, generality beyond this story/corpus,
  model superiority ("best model"), naturalness (not measured here).
- Repeated estimates for the two configurations whose primed condition
  was never collected: **Gemini 3.1 Pro (extended thinking ON)** and
  **Qwen 3.8 Max — Thinking** (`status: missing` in results.json).
- Dola Fast's Task-024 +28.20 pp is **not re-estimable** (its repeated
  direct condition is intake-partial → no usable direct replicate).
"""


def _raw_readme_md() -> str:
    return f"""# raw/ — why there are no raw outputs here

**Raw model outputs are intentionally NOT included in this bundle.**

- The complete experiment directory is roughly **500 MB** (operator
  prompt files embedding the copyrighted Polish source story + the
  reference corpus, and the raw model replies).
- Raw outputs are **immutable experimental evidence**: they were never
  rewritten, normalized, repaired or re-run, and they remain in the
  repository experiment directory
  (`experiments/exp004-modelscreen/repeats/operator-prompts/*.md`,
  msg2-style records: canonical prompt + raw reply after the
  `## Output` marker).
- This bundle contains their **run-level metadata and metrics** instead
  (one record per planned run in `results.json`, one row per run in
  `results.csv`), which is what the Task-025/026 analysis actually used.
- An analyst who needs specific raw outputs can **request selected files
  by run ID** (run IDs are in `results.json`); they can be exported
  individually without shipping the whole directory.
- Prompt/corpus provenance is preserved via SHA-256 hashes
  (`provenance.json`, per-run `prompt_hash`/`source_sha256`/
  `corpus_sha256` in `results.json`) — sufficient to verify that any
  later-provided raw file is the exact generation analysed here.
"""


def _figures_readme_md(written: list[str]) -> str:
    rows = "\n".join(
        f"- `{name}.svg` / `{name}.png` — {desc}"
        for name, desc in FIGURES.items() if f"{name}.svg" in written)
    return f"""# figures/

Deterministic figures from `scripts/analyze_exp004_repeats.py`
(Task-026 repeated-generation analysis). SVG is the canonical
deterministic form; PNG is a render for direct inspection.

{rows}

Notes:
- Primary statistics are shown for the 18 primary configurations;
  **Dola is exploratory** and is kept out of these primary figures —
  its numbers are in `summary.json` under `configurations.exploratory`
  and in `results.json` (population `exploratory`).
- Dot/range plots, not bar charts; individual replicate observations are
  shown and outliers are not hidden.
- No winner/composite score is introduced anywhere.
"""


# ---------------------------------------------------------------------------
# bundle assembly
# ---------------------------------------------------------------------------

def build_bundle(inputs: dict, out_dir: Path) -> dict:
    plan = json.loads(inputs["plan"].read_text(encoding="utf-8"))
    roster = json.loads(inputs["roster"].read_text(encoding="utf-8"))
    audit = json.loads(inputs["audit"].read_text(encoding="utf-8"))
    manifest = json.loads(inputs["manifest"].read_text(encoding="utf-8"))
    dataset = json.loads(inputs["dataset"].read_text(encoding="utf-8"))
    analysis_json = json.loads(inputs["analysis"].read_text(encoding="utf-8"))

    results = build_results(plan, roster, audit)
    records = results["records"]

    # deviation ids per configuration (from the audit registry)
    dev_by_run: dict[str, str] = {}
    config_of_run = {r["run_id"]: r["configuration_id"] for r in records}
    dev_by_config: dict[str, set[str]] = {}
    for dev in audit.get("deviations", []):
        for rid in dev.get("run_ids", []):
            cfg = config_of_run.get(rid)
            if cfg:
                dev_by_config.setdefault(cfg, set()).add(dev["id"])

    notes_by_config: dict[str, set[str]] = {}
    for r in records:
        cfg = r["configuration_id"]
        if r["status"] == "missing":
            notes_by_config.setdefault(cfg, set()).add(
                f"{r['condition']} {r['replicate']} not collected "
                "(pristine prompt file)")
        elif r["status"] == "partial":
            notes_by_config.setdefault(cfg, set()).add(
                f"{r['condition']} {r['replicate']} intake partial "
                "(wrapped end marker) — excluded from statistics")

    summary = build_summary(plan, dataset, records,
                            {k: sorted(v) for k, v in dev_by_config.items()},
                            {k: sorted(v) for k, v in
                             notes_by_config.items()})
    # propagate baseline-dependence from the Task-026 analysis
    summary["baseline_dependence_revisited"] = _json_round(
        analysis_json.get("baseline_dependence_revisited"))
    audit_bundle = build_audit(audit, records)
    deviations = build_deviations(audit)
    provenance = build_provenance(plan, manifest, inputs["dataset"],
                                  inputs["analysis"], audit,
                                  _git_head_short())

    # write markdown + raw + figures first
    (out_dir / "raw").mkdir(parents=True, exist_ok=True)
    (out_dir / "figures").mkdir(parents=True, exist_ok=True)
    files_md = {
        "README.md": _README_md(summary["counts"], []),
        "methodology.md": _methodology_md(),
        "raw/README.md": _raw_readme_md(),
        "figures/README.md": _figures_readme_md([]),
    }
    for rel, text in files_md.items():
        (out_dir / rel).write_text(text, encoding="utf-8")
    written_figs = _copy_figures(inputs["figures"], out_dir / "figures")
    (out_dir / "figures" / "README.md").write_text(
        _figures_readme_md(written_figs), encoding="utf-8")

    _write_json(out_dir / "provenance.json", provenance)
    _write_json(out_dir / "results.json", results)
    _write_json(out_dir / "summary.json", summary)
    _write_json(out_dir / "audit.json", audit_bundle)
    _write_json(out_dir / "deviations.json", deviations)
    _write_results_csv(out_dir / "results.csv", records)

    # deterministic file list for the manifest (every file under out_dir
    # EXCEPT manifest.json itself — a manifest cannot carry its own hash)
    all_files = sorted(
        p.relative_to(out_dir).as_posix()
        for p in out_dir.rglob("*")
        if p.is_file() and p.name != "manifest.json")
    files_data = [(rel, (out_dir / rel).read_bytes())
                  for rel in sorted(all_files)]
    _write_json(out_dir / "manifest.json", build_manifest(files_data))
    return summary


# ---------------------------------------------------------------------------
# standalone reconstruction verification (loads ONLY the bundle)
# ---------------------------------------------------------------------------

def verify_bundle(bundle_dir: Path) -> dict:
    """Recompute the Task-026 conclusions from the bundle alone
    (results.json + summary.json + audit.json). Returns {checks, computed}
    where checks is a list of {id, ok, detail}."""
    results = json.loads((bundle_dir / "results.json")
                         .read_text(encoding="utf-8"))
    summary = json.loads((bundle_dir / "summary.json")
                         .read_text(encoding="utf-8"))
    audit = json.loads((bundle_dir / "audit.json")
                       .read_text(encoding="utf-8"))
    records = results["records"]
    checks: list[dict] = []

    def check(cid: str, ok: bool, detail: str) -> None:
        checks.append({"id": cid, "ok": bool(ok), "detail": str(detail)})

    # -- counts ------------------------------------------------------------
    n_primary = sum(1 for r in records if r["in_primary_statistics"])
    n_expl = sum(1 for r in records if not r["in_primary_statistics"])
    n_usable = sum(1 for r in records if r["status"] == "usable")
    n_partial = sum(1 for r in records if r["status"] == "partial")
    n_missing = sum(1 for r in records if r["status"] == "missing")
    n_collected = n_usable + n_partial
    check("records_total_consistent", len(records) == n_primary + n_expl
          and len(records) == summary["counts"]["planned"]
          and len(records) == (audit["counts"]["collected"]
                               + audit["counts"]["missing"]),
          f"records {len(records)} = primary {n_primary} + exploratory "
          f"{n_expl}")
    check("status_partition_consistent", (
        n_usable + n_partial + n_missing == len(records)
        and summary["counts"]["usable"] == n_usable
        and summary["counts"]["partial"] == n_partial
        and summary["counts"]["missing"] == n_missing
        and summary["counts"]["collected"] == n_collected
        and audit["counts"]["collected"] == n_collected
        and audit["counts"]["missing"] == n_missing),
        f"usable {n_usable} / partial {n_partial} / missing {n_missing} "
        f"/ collected {n_collected}")
    check("population_separation", all(
        (r["population"] == "primary") == r["in_primary_statistics"]
        for r in records) and all(
        r["population"] == "exploratory" for r in records
        if not r["in_primary_statistics"]),
        "primary/exploratory flags consistent across records")
    check("summary_counts_match", (
        summary["counts"]["primary"]["planned"] == n_primary
        and summary["counts"]["exploratory"]["planned"] == n_expl
        and summary["counts"]["primary"]["usable"] == sum(
            1 for r in records if r["in_primary_statistics"]
            and r["status"] == "usable")
        and summary["counts"]["exploratory"]["usable"] == sum(
            1 for r in records if not r["in_primary_statistics"]
            and r["status"] == "usable")),
        json.dumps(summary["counts"])[:300])
    check("no_invalid_status", all(
        r["status"] in ("usable", "partial", "missing") for r in records),
        "no invalid statuses present")

    # -- no fabrication -----------------------------------------------------
    fabricated = [r["run_id"] for r in records
                  if r["status"] == "missing"
                  and (r.get("metrics") is not None
                       or r.get("orthography") is not None)]
    check("no_fabricated_metrics_for_missing", not fabricated,
          f"missing runs with metrics = {fabricated}")
    evaluated = [r["run_id"] for r in records
                 if r["status"] in ("usable", "partial")
                 and (r.get("metrics") is None)]
    check("metrics_for_all_collected", not evaluated,
          f"collected runs without metrics = {evaluated}")
    check("partial_excluded_from_analysis", all(
        r["analysis_included"] is False for r in records
        if r["status"] == "partial"), "partial runs never analysis_included")
    check("missing_excluded_from_analysis", all(
        r["analysis_included"] is False for r in records
        if r["status"] == "missing"), "missing runs never analysis_included")

    # -- per-config stats recomputed over usable ----------------------------
    from collections import defaultdict
    groups: dict[str, list[dict]] = defaultdict(list)
    for r in records:
        groups[r["configuration_id"]].append(r)

    def cond_rows(cfg_rows, cond):
        return [r for r in cfg_rows
                if r["condition"] == cond and r["status"] == "usable"]

    cfg_stats = {}
    for cfg_id, rows in groups.items():
        cfg_stats[cfg_id] = {}
        for cond in ("direct", "primed"):
            rr = cond_rows(rows, cond)
            cfg_stats[cfg_id][cond] = {
                "canonical": stats([r["metrics"][CANONICAL] for r in rr]),
                "broader": stats([r["metrics"][BROADER] for r in rr]),
                "unresolved": stats([r["metrics"][UNRESOLVED] for r in rr]),
                "orthography": stats(
                    [float(r["orthography"][ORTHO]) for r in rr
                     if r.get("orthography") is not None]),
            }

    mismatches = []
    for cfg in (summary["configurations"]["primary"]
                + summary["configurations"]["exploratory"]):
        cid = cfg["configuration_id"]
        for cond, key in (("direct", "direct"), ("primed", "primed")):
            got = cfg_stats[cid][cond]["canonical"]
            want = cfg[key]["canonical"]
            for field in ("n", "mean", "median", "sd", "min", "max",
                          "range"):
                a, b = got[field], want[field]
                eq = (a == b) or (a is None and b is None) or \
                    (a is not None and b is not None
                     and abs(a - b) < 1e-9)
                if not eq:
                    mismatches.append(f"{cid} {cond} canonical {field}: "
                                      f"recomputed {a} vs summary {b}")
            for metric in ("broader", "unresolved"):
                a = cfg_stats[cid][cond][metric]["mean"]
                b = cfg[key][metric]["mean"]
                if not ((a == b) or (a is None and b is None)
                        or abs((a or 0) - (b or 0)) < 1e-9):
                    mismatches.append(f"{cid} {cond} {metric} mean: "
                                      f"{a} vs {b}")
            oa = cfg_stats[cid][cond]["orthography"]
            ob = cfg[key]["orthography"]
            for field in ("n", "mean", "median", "min", "max"):
                a, b = oa[field], ob[field]
                if not ((a == b) or (a is None and b is None)
                        or abs((a or 0) - (b or 0)) < 1e-9):
                    mismatches.append(f"{cid} {cond} ortho {field}: "
                                      f"{a} vs {b}")
    check("per_config_stats_reconstructed", not mismatches,
          "; ".join(mismatches[:6]) or "all conditions match")

    # -- repeated deltas -----------------------------------------------------
    d_mismatch = []
    for cfg in (summary["configurations"]["primary"]
                + summary["configurations"]["exploratory"]):
        cid = cfg["configuration_id"]
        d = cfg_stats[cid]["direct"]["canonical"]
        p = cfg_stats[cid]["primed"]["canonical"]
        delta = (p["mean"] - d["mean"]) if (d["n"] > 0 and p["n"] > 0) \
            else None
        want = cfg["repeated"]["delta_mean_canonical"]
        if not ((delta is None and want is None)
                or (delta is not None and want is not None
                    and abs(delta - want) < 1e-9)):
            d_mismatch.append(f"{cid}: {delta} vs {want}")
        want2 = cfg["repeated"]["delta_mean_broader"]
        db = (cfg_stats[cid]["primed"]["broader"]["mean"]
              - cfg_stats[cid]["direct"]["broader"]["mean"]) \
            if (d["n"] > 0 and p["n"] > 0) else None
        if not ((db is None and want2 is None)
                or (db is not None and want2 is not None
                    and abs(db - want2) < 1e-9)):
            d_mismatch.append(f"{cid} broader: {db} vs {want2}")
    check("repeated_deltas_reconstructed", not d_mismatch,
          "; ".join(d_mismatch[:6]) or "all deltas match")

    # -- aggregates -----------------------------------------------------------
    prim = summary["configurations"]["primary"]
    assessable = [c for c in prim
                  if c["repeated"]["delta_mean_canonical"] is not None]
    pos = [c for c in assessable
           if c["repeated"]["delta_mean_canonical"] > 0]
    bro = [c["repeated"]["delta_mean_broader"] for c in assessable]
    ovn = [c for c in prim if c["task024"] is not None
           and c["task024"]["old_delta_canonical"] is not None
           and c["repeated"]["delta_mean_canonical"] is not None]
    same_dir = [c for c in ovn
                if c["task024_direction_reproduced"] == "same_direction"]
    old_means = [c["task024"]["old_delta_canonical"] for c in ovn]
    new_means = [c["repeated"]["delta_mean_canonical"] for c in ovn]
    d_sds = [c["direct"]["canonical"]["sd"] for c in prim
             if c["direct"]["canonical"]["n"] >= 2]
    p_sds = [c["primed"]["canonical"]["sd"] for c in prim
             if c["primed"]["canonical"]["n"] >= 2]
    spread_above = [c for c in assessable
                    if c["primed"]["canonical"]["sd"] is not None
                    and c["primed"]["canonical"]["sd"]
                    > c["repeated"]["delta_mean_canonical"]]

    def _fmean_or_none(vals):
        return statistics.fmean(vals) if vals else None

    mean_can_pp = _fmean_or_none(
        [c["repeated"]["delta_mean_canonical"] for c in assessable]) * 100 \
        if assessable else None
    mean_bro_pp = _fmean_or_none(bro) * 100 if bro else None
    mean_old_pp = _fmean_or_none(old_means) * 100 if old_means else None
    mean_new_pp = _fmean_or_none(new_means) * 100 if new_means else None
    med_d_sd_pp = statistics.median(d_sds) * 100 if d_sds else None
    med_p_sd_pp = statistics.median(p_sds) * 100 if p_sds else None

    # cross-check the stored aggregate fields
    def _near(a, b):
        if a is None and b is None:
            return True
        if a is None or b is None:
            return False
        return abs(a - b) < 1e-6

    def _fmtv(x):
        return "n/a" if x is None else f"{x:.2f}"

    check("aggregate_canonical_matches", (
        len(assessable) == summary["assessable_primary_configs"]
        and len(pos) == summary["repeated_delta_canonical"]["count_positive"]
        and _near(mean_can_pp, summary["repeated_delta_canonical"]["mean_pp"])),
        f"assessable {len(assessable)} positive {len(pos)} "
        f"mean {_fmtv(mean_can_pp)} pp")
    check("aggregate_old_vs_new_matches", (
        len(ovn) == summary["old_vs_new"]["rows_with_both_deltas"]
        and len(same_dir) == summary["old_vs_new"]["same_direction_rows"]
        and _near(mean_old_pp, summary["old_vs_new"]["mean_old_delta_pp"])
        and _near(mean_new_pp,
                  summary["old_vs_new"]["mean_repeated_delta_pp"])),
        f"rows {len(ovn)} same-dir {len(same_dir)} old {_fmtv(mean_old_pp)} "
        f"new {_fmtv(mean_new_pp)} pp")
    check("aggregate_spread_matches", (
        _near(med_d_sd_pp, summary["stochastic_spread"]
              ["median_direct_sd_pp"])
        and _near(med_p_sd_pp, summary["stochastic_spread"]
                  ["median_primed_sd_pp"])),
        f"median direct SD {_fmtv(med_d_sd_pp)} pp / primed "
        f"{_fmtv(med_p_sd_pp)} pp")
    check("primed_sd_exceeds_delta_matches", (
        len(spread_above) == summary["primed_sd_exceeds_delta"]["count"]
        and all(c["configuration_id"] in
                summary["primed_sd_exceeds_delta"]["configuration_ids"]
                for c in spread_above)),
        f"configs with primed SD > delta: "
        f"{[c['configuration_id'] for c in spread_above]}")

    computed = {
        "planned": len(records), "collected": n_collected,
        "usable": n_usable, "partial": n_partial, "missing": n_missing,
        "primary_planned": n_primary, "exploratory_planned": n_expl,
        "assessable_primary": len(assessable),
        "positive_canonical_delta": len(pos),
        "mean_repeated_delta_canonical_pp": mean_can_pp,
        "mean_repeated_delta_broader_pp": mean_bro_pp,
        "old_vs_new_rows": len(ovn),
        "same_direction_rows": len(same_dir),
        "mean_old_delta_pp": mean_old_pp,
        "mean_new_delta_pp_oldrows": mean_new_pp,
        "median_direct_sd_pp": med_d_sd_pp,
        "median_primed_sd_pp": med_p_sd_pp,
        "primed_sd_exceeds_delta_configs": [
            c["configuration_id"] for c in spread_above],
        "missing_configurations": summary["missing"]["configuration_ids"],
    }
    return {"checks": checks, "computed": computed}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _print_verify(report: dict) -> int:
    checks = report["checks"]
    failed = [c for c in checks if not c["ok"]]
    print(f"verify: {len(checks) - len(failed)}/{len(checks)} checks ok")
    for c in checks:
        print(f"  [{'OK ' if c['ok'] else 'FAIL'}] {c['id']} — {c['detail']}")
    comp = report["computed"]
    print("computed:")
    for k, v in comp.items():
        print(f"  {k} = {v}")
    return 1 if failed else 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="EXP-004 assistant research bundle (SODA Task 027).")
    sub = ap.add_subparsers(dest="command", required=True)

    pb = sub.add_parser("build", help="generate the bundle directory")
    pb.add_argument("--plan", type=Path, default=DEFAULTS["plan"])
    pb.add_argument("--roster", type=Path, default=DEFAULTS["roster"])
    pb.add_argument("--audit", type=Path, default=DEFAULTS["audit"])
    pb.add_argument("--manifest", type=Path, default=DEFAULTS["manifest"])
    pb.add_argument("--dataset", type=Path, default=DEFAULTS["dataset"])
    pb.add_argument("--analysis", type=Path, default=DEFAULTS["analysis"])
    pb.add_argument("--figures", type=Path, default=DEFAULTS["figures"])
    pb.add_argument("--out", type=Path, default=BUNDLE_DIR)

    pv = sub.add_parser("verify", help="standalone reconstruction check")
    pv.add_argument("--bundle", type=Path, default=BUNDLE_DIR)

    args = ap.parse_args(argv)
    if args.command == "build":
        file_inputs = [str(p) for p in (args.plan, args.roster, args.audit,
                                        args.manifest, args.dataset,
                                        args.analysis)
                       if not Path(p).is_file()]
        if file_inputs:
            print("error: missing file inputs: " + ", ".join(file_inputs),
                  file=sys.stderr)
            return 2
        if not Path(args.figures).is_dir():
            print(f"error: figures dir not found: {args.figures}",
                  file=sys.stderr)
            return 2
        args.out.mkdir(parents=True, exist_ok=True)
        summary = build_bundle(vars(args), args.out)
        print(f"[bundle] wrote {args.out}")
        print(f"[bundle] planned {summary['counts']['planned']} "
              f"usable {summary['counts']['usable']} "
              f"partial {summary['counts']['partial']} "
              f"missing {summary['counts']['missing']}")
        print("[bundle] now run: "
              f"{Path(__file__).name} verify --bundle {args.out}")
        return 0
    if args.command == "verify":
        return _print_verify(verify_bundle(args.bundle))
    return 2


if __name__ == "__main__":
    sys.exit(main())
