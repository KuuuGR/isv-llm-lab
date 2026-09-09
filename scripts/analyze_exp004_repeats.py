#!/usr/bin/env python3
"""EXP-004 Phase repeat — deterministic repeated-generation analysis
(SODA Task 025).

Run AFTER the research lead collects and evaluates the replicate outputs
(scripts/run_exp004_repeats.py collect-session/collect-msg2 → verify →
evaluate → roster). This script never calls an LLM and never fabricates
data: with no usable collected observations it writes an explicit
'no results yet' analysis and exits 0.

Central scientific purpose: transform the single-run Phase-1 → Phase-2A
delta into a DISTRIBUTION-SHIFT vs STOCHASTIC-VARIATION statement:

  mean(primed replicates) − mean(direct replicates)   (new estimate)
  vs
  P2A_single − P1_single                               (old Task-024 delta)

Scope:
- primary statistics use exactly the original 18 usable configurations
  (repeated rows flagged primary in the repeat roster);
- the exploratory Dola 3.8 configurations are analysed in a separate,
  clearly labelled section and never merged into the primary n=18
  statistics;
- per (configuration, condition) with n <= 3 usable replicates the report
  gives small-sample descriptive statistics (n, mean, median, sd, min,
  max, range) and explicitly avoids fragile claims from normality
  assumptions; r01/r02/r03 are replication blocks, NOT matched linguistic
  samples (block differences may be shown as a secondary descriptive
  view only).

Outputs (repeats/analysis/, stdlib only):
  analysis.json    machine-readable results + figure metadata
  dataset.json     per-configuration observation + stats dataset
  analysis.md      narrative report (deterministic)
  figures/         figure_a..figure_e.svg (deterministic)

Figure set:
  A — replicate distributions (direct vs primed dots + mean + range)
  B — priming deltas (mean primed − mean direct, sorted; faint replicate
      differences)
  C — stochastic spread (within-condition SD + range, canonical)
  D — old single-run delta vs repeated mean delta (Task-024 comparison)
  E — baseline dependence revisited (repeated direct mean vs repeated
      priming delta; Spearman vs Task-024 ρ ≈ −0.86)
"""
from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

EXP = ROOT / "experiments" / "exp004-modelscreen"
REPEATS = EXP / "repeats"
DEFAULT_ROSTER = REPEATS / "outputs" / "roster.json"
DEFAULT_P1_ROSTER = EXP / "outputs" / "roster.json"
DEFAULT_P2A_ROSTER = EXP / "phase2a" / "outputs" / "roster.json"
DEFAULT_ANALYSIS_DIR = REPEATS / "analysis"

TASK024_RHO_NOTE = "Task-024 baseline-dependence ρ ≈ −0.86 (single-run, n=18)"
TASK024_DELTA_SOURCE = ("Task-024 single-run delta = Phase-2A primed single "
                        "generation − Phase-1 direct single generation "
                        "(same definitions as analyze_exp004_phase2a.py)")

KEYS = ("provider", "model", "model_version")


def _cfg_key(o: dict) -> tuple:
    return tuple(o[k] for k in KEYS)


def _label(o: dict) -> str:
    return o.get("label", " ".join(str(k) for k in _cfg_key(o)))


def _canonical(o: dict) -> float | None:
    return (o.get("metrics") or {}).get("canonical_coverage")


def _broader(o: dict) -> float | None:
    return (o.get("metrics") or {}).get(
        "broader_resource_supported_coverage")


def _unresolved(o: dict) -> float | None:
    return (o.get("metrics") or {}).get("unresolved_rate")


def _ortho_out(o: dict) -> int | None:
    return (o.get("orthography") or {}).get("outside_inventory")


# ---------------------------------------------------------------------------
# loading
# ---------------------------------------------------------------------------

def load_repeat_observations(roster_path: Path) -> list[dict]:
    """Load usable repeat observations from a repeat roster.json. A row is
    an observation if it has metrics (evaluated). Unusable rows are carried
    in the returned list with usable=False so the ledger is preserved."""
    if not roster_path.is_file():
        raise FileNotFoundError(
            f"repeat roster not found: {roster_path} — collect + evaluate "
            "the replicate runs first (run_exp004_repeats.py status)")
    roster = json.loads(roster_path.read_text(encoding="utf-8"))
    obs = []
    for r in roster.get("rows", []):
        if r.get("metrics") is None:
            continue
        obs.append({
            "run_id": r["run_id"],
            "condition": r["condition"],
            "replicate": r["replicate"],
            "primary": r["primary"],
            "exploratory": r["exploratory"],
            "label": r["label"],
            "provider": r["provider"],
            "model": r["model"],
            "model_version": r["model_version"],
            "usable": bool(r["usable"]),
            "metrics": r["metrics"],
            "orthography": r["orthography"] or {},
            "intake_verdict": (r["intake"] or {}).get("verdict"),
        })
    return obs


def load_legacy_singles(p1_roster_path: Path,
                        p2a_roster_path: Path) -> list[dict]:
    """Task-024 old single-run observations: for every primary Phase-2A
    primed row, its Phase-1 baseline direct row (baseline_run_id)."""
    if not p1_roster_path.is_file() or not p2a_roster_path.is_file():
        raise FileNotFoundError(
            "Phase-1/Phase-2A rosters not found — needed for the Task-024 "
            "single-run delta comparison (Figure D)")
    p1 = {r["run_id"]: r
          for r in json.loads(p1_roster_path.read_text(encoding="utf-8"))
          .get("rows", [])}
    p2a = json.loads(p2a_roster_path.read_text(encoding="utf-8")) \
        .get("rows", [])
    out = []
    for r in p2a:
        if r.get("condition") != "p2a-primed" or r.get("exploratory"):
            continue
        if not r.get("usable") or r.get("metrics") is None:
            continue
        base = p1.get(r.get("baseline_run_id"))
        if base is None or not base.get("usable") \
                or base.get("metrics") is None:
            continue
        out.append({
            "run_id": r["run_id"],
            "baseline_run_id": base["run_id"],
            "label": r["label"],
            "provider": r["provider"],
            "model": r["model"],
            "model_version": r["model_version"],
            "p1_metrics": base["metrics"],
            "p1_ortho_out": (base.get("orthography") or {}).get(
                "outside_inventory"),
            "p2a_metrics": r["metrics"],
            "p2a_ortho_out": (r.get("orthography") or {}).get(
                "outside_inventory"),
        })
    return out


# ---------------------------------------------------------------------------
# small-sample descriptive statistics (n <= 3, stdlib)
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


def group_observations(obs: list[dict]) -> dict:
    """Group usable observations by configuration key → condition lists
    (usable only; unusable rows are not dropped silently — they appear in
    the ledger passed separately)."""
    groups: dict[tuple, dict] = {}
    for o in obs:
        key = _cfg_key(o)
        g = groups.setdefault(key, {"label": _label(o),
                                    "provider": o["provider"],
                                    "model": o["model"],
                                    "model_version": o["model_version"],
                                    "direct": [], "primed": [],
                                    "unusable": []})
        if o.get("usable"):
            g[o["condition"]].append(o)
        else:
            g["unusable"].append(o)
    return groups


def build_dataset(repeat_obs: list[dict],
                  legacy: list[dict] | None = None) -> dict:
    """Deterministic dataset: primary config stats + deltas + old singles.

    repeat_obs: loaded repeat observations (usable rows carry metrics).
    legacy:     Task-024 single-run rows (load_legacy_singles).
    """
    groups = group_observations(repeat_obs)

    def metric_lists(cond_obs: list[dict], metric: str) -> list[float]:
        vals = []
        for o in cond_obs:
            m = (o.get("metrics") or {}).get(metric)
            if m is not None:
                vals.append(float(m))
        return vals

    legacy_by_key = {}
    for s in legacy or []:
        legacy_by_key[(_cfg_key(s))] = s

    primary_rows = []
    exploratory_rows = []
    for key in sorted(groups, key=lambda k: (k[0], k[1], k[2])):
        g = groups[key]
        rec = {
            "config": list(key),
            "label": g["label"],
            "primary": _is_primary(key, repeat_obs),
            "exploratory": _is_exploratory(key, repeat_obs),
            "condition_n": {"direct": len(g["direct"]),
                            "primed": len(g["primed"])},
            "direct": {
                "canonical": stats(metric_lists(g["direct"],
                                                "canonical_coverage")),
                "broader": stats(metric_lists(
                    g["direct"], "broader_resource_supported_coverage")),
                "unresolved": stats(metric_lists(g["direct"],
                                                 "unresolved_rate")),
                "ortho_out": stats([_ortho_out(o) for o in g["direct"]
                                    if _ortho_out(o) is not None]),
                "observations": [_obs_meta(o) for o in
                                 sorted(g["direct"],
                                        key=lambda o: o["replicate"])],
            },
            "primed": {
                "canonical": stats(metric_lists(g["primed"],
                                                "canonical_coverage")),
                "broader": stats(metric_lists(
                    g["primed"], "broader_resource_supported_coverage")),
                "unresolved": stats(metric_lists(g["primed"],
                                                 "unresolved_rate")),
                "ortho_out": stats([_ortho_out(o) for o in g["primed"]
                                    if _ortho_out(o) is not None]),
                "observations": [_obs_meta(o) for o in
                                 sorted(g["primed"],
                                        key=lambda o: o["replicate"])],
            },
            "unusable": [_obs_meta(o) for o in g["unusable"]],
        }
        rec["deltas"] = {
            "mean_canonical": _delta(rec["direct"]["canonical"],
                                     rec["primed"]["canonical"]),
            "mean_broader": _delta(rec["direct"]["broader"],
                                   rec["primed"]["broader"]),
            "block_differences_canonical": _block_diffs(
                g["direct"], g["primed"], "canonical_coverage"),
        }
        leg = legacy_by_key.get(key)
        if leg:
            rec["old_single"] = {
                "run_id": leg["run_id"],
                "baseline_run_id": leg["baseline_run_id"],
                "p1_canonical": leg["p1_metrics"]["canonical_coverage"],
                "p2a_canonical": leg["p2a_metrics"]["canonical_coverage"],
                "old_delta_canonical": (
                    leg["p2a_metrics"]["canonical_coverage"]
                    - leg["p1_metrics"]["canonical_coverage"]),
                "p1_broader": leg["p1_metrics"][
                    "broader_resource_supported_coverage"],
                "p2a_broader": leg["p2a_metrics"][
                    "broader_resource_supported_coverage"],
                "old_delta_broader": (
                    leg["p2a_metrics"][
                        "broader_resource_supported_coverage"]
                    - leg["p1_metrics"][
                        "broader_resource_supported_coverage"]),
                "p1_ortho_out": leg["p1_ortho_out"],
                "p2a_ortho_out": leg["p2a_ortho_out"],
            }
        (primary_rows if rec["primary"] else exploratory_rows).append(rec)

    return {
        "primary": _order_configs(primary_rows),
        "exploratory": _order_configs(exploratory_rows),
    }


def _is_primary(key: tuple, obs: list[dict]) -> bool:
    return any(_cfg_key(o) == key and o.get("primary") for o in obs)


def _is_exploratory(key: tuple, obs: list[dict]) -> bool:
    return any(_cfg_key(o) == key and o.get("exploratory") for o in obs)


def _order_configs(rows: list[dict]) -> list[dict]:
    """Deterministic order: by phase-1 roster number when derivable from
    the config key, else appended at the end by (provider, model, version)
    — i.e., never filename/roster-order dependent."""
    return sorted(rows, key=lambda r: (r["config"][0], r["config"][1],
                                       r["config"][2]))


def _delta(a: dict, b: dict) -> dict | None:
    if a["mean"] is None or b["mean"] is None:
        return None
    return {
        "direct_mean": a["mean"],
        "primed_mean": b["mean"],
        "delta_mean": b["mean"] - a["mean"],
        "direct_sd": a["sd"],
        "primed_sd": b["sd"],
        "direct_range": a["range"],
        "primed_range": b["range"],
        "direct_n": a["n"],
        "primed_n": b["n"],
    }


def _block_diffs(direct: list[dict], primed: list[dict],
                 metric: str) -> list[dict]:
    """r01/r02/r03 block differences b_i − a_i — SECONDARY descriptive
    view only (replication blocks, not matched linguistic samples)."""
    by = {}
    for o in direct:
        by[o["replicate"]] = (o.get("metrics") or {}).get(metric)
    out = []
    for o in sorted(primed, key=lambda x: x["replicate"]):
        a = by.get(o["replicate"])
        b = (o.get("metrics") or {}).get(metric)
        if a is not None and b is not None:
            out.append({"replicate": o["replicate"], "diff": b - a})
    return out


def _obs_meta(o: dict) -> dict:
    return {"run_id": o.get("run_id"),
            "condition": o.get("condition"),
            "replicate": o.get("replicate"),
            "usable": o.get("usable"),
            "intake_verdict": o.get("intake_verdict"),
            "canonical_coverage": (o.get("metrics") or {}).get(
                "canonical_coverage")}


# ---------------------------------------------------------------------------
# correlations (Spearman, stdlib)
# ---------------------------------------------------------------------------

def spearman(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) < 2 or len(xs) != len(ys):
        return None

    def ranks(vals: list[float]) -> list[float]:
        order = sorted(range(len(vals)), key=lambda i: vals[i])
        r = [0.0] * len(vals)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and vals[order[j + 1]] == vals[order[i]]:
                j += 1
            avg = (i + j) / 2 + 1
            for k in range(i, j + 1):
                r[order[k]] = avg
            i = j + 1
        return r

    rx, ry = ranks(xs), ranks(ys)
    n = len(xs)
    d2 = sum((rx[i] - ry[i]) ** 2 for i in range(n))
    denom = n * (n * n - 1) / 6
    if denom == 0:
        return None
    return 1 - d2 / denom


def ols_slope_intercept(xs: list[float], ys: list[float]) -> tuple | None:
    if len(xs) < 2:
        return None
    mx, my = statistics.fmean(xs), statistics.fmean(ys)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sxx = sum((x - mx) ** 2 for x in xs)
    if sxx == 0:
        return None
    slope = sxy / sxx
    return slope, my - slope * mx


def _fmt_pct(v: float | None) -> str:
    return f"{v * 100:.2f}%" if v is not None else "n/a"


def _fmt_pp(v: float | None) -> str:
    return f"{v * 100:+.2f} pp" if v is not None else "n/a"


# ---------------------------------------------------------------------------
# deterministic SVG figures (stdlib only)
# ---------------------------------------------------------------------------

C_DIRECT = "#1f77b4"
C_PRIMED = "#d62728"
C_OLD = "#7f7f7f"
C_NEW = "#2ca02c"
C_AXIS = "#555555"
FIG_W, MARG_L, MARG_R, MARG_T = 1240, 70, 30, 46


def _esc(t: str) -> str:
    return (t.replace("&", "&amp;").replace("<", "&lt;")
             .replace(">", "&gt;").replace('"', "&quot;"))


def _svg_head(title: str, height: int) -> list[str]:
    return [f'<svg xmlns="http://www.w3.org/2000/svg" width="{FIG_W}" '
            f'height="{height}" viewBox="0 0 {FIG_W} {height}">',
            f'<text x="{MARG_L}" y="24" font-family="Helvetica,Arial" '
            f'font-size="15" font-weight="bold" fill="#111">{_esc(title)}'
            "</text>"]


def _y_axis(lo: float, hi: float, plot_top: float, plot_h: float,
            left: float, n_ticks: int = 6) -> tuple[list[str], float]:
    """Return (svg lines, y_of(value) callable)."""
    out: list[str] = []
    pad = (hi - lo) * 0.05 if hi > lo else 1.0
    lo2, hi2 = lo - pad, hi + pad

    def y_of(v: float) -> float:
        if hi2 == lo2:
            return plot_top + plot_h / 2
        return plot_top + (1 - (v - lo2) / (hi2 - lo2)) * plot_h

    step = (hi2 - lo2) / n_ticks
    for i in range(n_ticks + 1):
        v = lo2 + i * step
        y = y_of(v)
        out.append(f'<line x1="{left}" y1="{y:.1f}" x2="{left + 8}" '
                   f'y2="{y:.1f}" stroke="{C_AXIS}"/>')
        out.append(f'<text x="{left - 8}" y="{y + 4:.1f}" text-anchor="end" '
                   f'font-family="Helvetica,Arial" font-size="10" '
                   f'fill="{C_AXIS}">{_fmt_pct(v)}</text>')
    return out, y_of


def _config_codes(recs: list[dict]) -> dict:
    """Config label -> deterministic short code (1-based index over the
    dataset's deterministic ordering)."""
    return {r["config"][0] + "__" + r["config"][1] + "__" + r["config"][2]:
            str(i + 1) for i, r in enumerate(recs)}


def _caption_block(codes: dict, recs: list[dict], y_start: int,
                   width: int) -> list[str]:
    """Two-column legend under the chart: code = label. `codes` maps
    '__'.join(config) -> code."""
    pairs = [(codes["__".join(r["config"])], r["label"]) for r in recs]
    return _caption_pairs(pairs, y_start, width)


def _caption_pairs(pairs: list[tuple[str, str]], y_start: int,
                   width: int) -> list[str]:
    """Two-column legend under the chart: code = label (explicit pairs)."""
    out: list[str] = []
    n_cols = 2
    per = math.ceil(len(pairs) / n_cols)
    col_w = width // n_cols
    for col in range(n_cols):
        x = MARG_L + col * col_w
        for i, (code, label) in enumerate(pairs[col * per:(col + 1) * per]):
            y = y_start + i * 14
            out.append(f'<text x="{x}" y="{y}" font-family="Helvetica,Arial" '
                       f'font-size="9.5" fill="#333">{code} = '
                       f"{_esc(label)}</text>")
    return out


def _range_bar(x: float, lo_v: float | None, hi_v: float | None,
               y_of, color: str) -> list[str]:
    if lo_v is None or hi_v is None:
        return []
    y1, y2 = y_of(lo_v), y_of(hi_v)
    if y1 == y2:
        y1, y2 = y1 - 2, y2 + 2
    return [f'<line x1="{x:.1f}" y1="{y1:.1f}" x2="{x:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="1.2"/>']


def _dots_and_mean(x: float, vals: list[float], y_of, color: str,
                   radius: float = 3.2) -> list[str]:
    out = []
    for v in vals:
        y = y_of(v)
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{radius}" '
                   f'fill="{color}" opacity="0.85"/>')
    if vals:
        y = y_of(statistics.fmean(vals))
        out.append(f'<line x1="{x - 6:.1f}" y1="{y:.1f}" x2="{x + 6:.1f}" '
                   f'y2="{y:.1f}" stroke="#111" stroke-width="2.6"/>')
    return out


def figure_a(recs: list[dict], out: Path) -> None:
    """Replicate distributions: per config direct/primed dots + range +
    mean + connector between means (canonical coverage)."""
    allv = []
    for r in recs:
        for cond in ("direct", "primed"):
            st = r[cond]["canonical"]
            if st["n"]:
                allv += [st["min"], st["max"], st["mean"]]
    lo, hi = min(allv), max(allv)
    n = len(recs)
    plot_top, plot_h = MARG_T + 14, 330
    bot = plot_top + plot_h
    xstep = (FIG_W - MARG_L - MARG_R) / (n + 1)
    left = MARG_L
    lines = _svg_head(
        "Figure A — Replicate distributions (canonical coverage; 3 direct + 3 primed "
        "independent generations per configuration)", bot + 190)
    ax, y_of = _y_axis(lo, hi, plot_top, plot_h, left)
    lines += ax
    codes = _config_codes(recs)
    for i, r in enumerate(recs):
        xc = left + xstep * (i + 1)
        xd, xp = xc - xstep * 0.16, xc + xstep * 0.16
        d, p = r["direct"]["canonical"], r["primed"]["canonical"]
        if d["mean"] is not None and p["mean"] is not None:
            lines.append(f'<line x1="{xd + 7:.1f}" y1="{y_of(d["mean"]):.1f}" '
                         f'x2="{xp - 7:.1f}" y2="{y_of(p["mean"]):.1f}" '
                         f'stroke="#999" stroke-width="0.8" '
                         f'stroke-dasharray="3 2"/>')
        lines += _range_bar(xd, d["min"], d["max"], y_of, C_DIRECT)
        lines += _range_bar(xp, p["min"], p["max"], y_of, C_PRIMED)
        dv = [o["canonical_coverage"] for o in r["direct"]["observations"]
              if o["canonical_coverage"] is not None]
        pv = [o["canonical_coverage"] for o in r["primed"]["observations"]
              if o["canonical_coverage"] is not None]
        lines += _dots_and_mean(xd, dv, y_of, C_DIRECT)
        lines += _dots_and_mean(xp, pv, y_of, C_PRIMED)
        code = codes["__".join(r["config"])]
        lines.append(f'<text x="{xc:.1f}" y="{bot + 16}" text-anchor="middle" '
                     f'font-family="Helvetica,Arial" font-size="10" '
                     f'fill="#111">{code}</text>')
        if d["mean"] is not None:
            lines.append(f'<text x="{xd:.1f}" y="{y_of(d["mean"]) - 6:.1f}" '
                         f'text-anchor="middle" font-family="Helvetica,Arial" '
                         f'font-size="7.5" fill="{C_DIRECT}">'
                         f'{_fmt_pct(d["mean"])}</text>')
        if p["mean"] is not None:
            lines.append(f'<text x="{xp:.1f}" y="{y_of(p["mean"]) - 6:.1f}" '
                         f'text-anchor="middle" font-family="Helvetica,Arial" '
                         f'font-size="7.5" fill="{C_PRIMED}">'
                         f'{_fmt_pct(p["mean"])}</text>')
    lines += _caption_block(codes, recs, bot + 40, FIG_W - MARG_L - MARG_R)
    lines += [f'<text x="{MARG_L}" y="{bot + 40 + 14 * (math.ceil(len(recs) / 2) + 1)}" '
              f'font-family="Helvetica,Arial" font-size="9.5" fill="#555">'
              f"Direct (blue) = independent fresh-session translations without corpus; "
              f"primed (red) = corpus-primed fresh sessions. Vertical bar = replicate "
              f"min–max range; circles = the 3 replicate observations; bold tick = "
              f"replicate mean; dashed line connects the two means.</text>"]
    lines.append("</svg>")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")


def figure_b(recs: list[dict], out: Path) -> None:
    """Priming deltas sorted: mean primed − mean direct (canonical)."""
    rows = []
    for r in recs:
        d = r["deltas"]["mean_canonical"]
        rows.append({"label": r["label"], "code": None, "delta": d,
                     "blocks": r["deltas"]["block_differences_canonical"]})
    rows = [x for x in rows if x["delta"] is not None]
    rows.sort(key=lambda x: x["delta"]["delta_mean"])
    for i, x in enumerate(rows):
        x["code"] = str(i + 1)
    allv = [x["delta"]["delta_mean"] for x in rows]
    for x in rows:
        allv += [b["diff"] for b in x["blocks"]]
    lo, hi = min(allv), max(allv)
    n = len(rows)
    plot_top, plot_h = MARG_T + 14, 300
    bot = plot_top + plot_h
    left = MARG_L
    lines = _svg_head(
        "Figure B — Priming deltas (mean primed − mean direct, canonical coverage; "
        "sorted; small ticks = r01/r02/r03 block differences)", bot + 190)
    ax, y_of = _y_axis(lo, hi, plot_top, plot_h, left)
    lines += ax
    zero_y = y_of(0.0) if lo <= 0 <= hi else None
    if zero_y is not None:
        lines.append(f'<line x1="{left}" y1="{zero_y:.1f}" x2="'
                     f'{FIG_W - MARG_R}" y2="{zero_y:.1f}" stroke="#999" '
                     f'stroke-width="1" stroke-dasharray="4 3"/>')
    bw = (FIG_W - MARG_L - MARG_R) / (n + 1)
    for i, x in enumerate(rows):
        xc = left + bw * (i + 1)
        d = x["delta"]
        y1, y2 = y_of(0.0), y_of(d["delta_mean"])
        color = C_PRIMED if d["delta_mean"] >= 0 else "#9467bd"
        lines.append(f'<rect x="{xc - bw * 0.22:.1f}" y="{min(y1, y2):.1f}" '
                     f'width="{bw * 0.44:.1f}" '
                     f'height="{abs(y2 - y1):.1f}" fill="{color}" '
                     f'opacity="0.75"/>')
        for b in x["blocks"]:
            yb = y_of(b["diff"])
            lines.append(f'<line x1="{xc - bw * 0.3:.1f}" y1="{yb:.1f}" '
                         f'x2="{xc + bw * 0.3:.1f}" y2="{yb:.1f}" '
                         f'stroke="#333" stroke-width="0.8" '
                         f'stroke-dasharray="1.5 2" opacity="0.7"/>')
        lines.append(f'<text x="{xc:.1f}" y="{bot + 16}" text-anchor="middle" '
                     f'font-family="Helvetica,Arial" font-size="10" '
                     f'fill="#111">{x["code"]}</text>')
        lines.append(f'<text x="{xc:.1f}" y="{min(y1, y2) - 5:.1f}" '
                     f'text-anchor="middle" font-family="Helvetica,Arial" '
                     f'font-size="7.5" fill="#333">'
                     f'{_fmt_pp(d["delta_mean"])}</text>')
    pairs = [(x["code"], x["label"]) for x in rows]
    lines += _caption_pairs(pairs, bot + 40, FIG_W - MARG_L - MARG_R)
    lines += [f'<text x="{MARG_L}" y="{bot + 40 + 14 * (math.ceil(len(rows) / 2) + 1)}" '
              f'font-family="Helvetica,Arial" font-size="9.5" fill="#555">'
              f"Bar = mean(primed) − mean(direct); faint dashed ticks = "
              f"r01/r02/r03 block differences (secondary descriptive view).</text>"]
    lines.append("</svg>")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")


def _sd_range_bars(xc: float, st: dict, y_of, color: str) -> list[str]:
    """SD as a bar from 0 and range as a thin whisker line."""
    out = []
    sd = st.get("sd") or 0.0
    rng = st.get("range")
    y0 = y_of(0.0)
    y_sd = y_of(sd)
    out.append(f'<rect x="{xc - 8:.1f}" y="{min(y0, y_sd):.1f}" '
               f'width="16" height="{abs(y_sd - y0):.1f}" fill="{color}" '
               f'opacity="0.8"/>')
    if rng is not None:
        yr0, yr1 = y_of(0.0), y_of(rng)
        out.append(f'<line x1="{xc:.1f}" y1="{min(yr0, yr1):.1f}" x2="{xc:.1f}" '
                   f'y2="{max(yr0, yr1):.1f}" stroke="#333" stroke-width="1"/>')
    return out


def figure_c(recs: list[dict], out: Path) -> None:
    """Stochastic spread: within-condition replicate SD (bars) + range
    (whisker), canonical coverage, per configuration."""
    allv = []
    for r in recs:
        for cond in ("direct", "primed"):
            st = r[cond]["canonical"]
            if st["n"]:
                allv += [st["sd"] or 0.0,
                         st["range"] if st["range"] is not None else 0.0]
    lo, hi = 0.0, max(allv) if allv else 1.0
    n = len(recs)
    plot_top, plot_h = MARG_T + 14, 300
    bot = plot_top + plot_h
    left = MARG_L
    lines = _svg_head(
        "Figure C — Stochastic spread (within-condition replicate SD, bars, and "
        "min–max range, whisker; canonical coverage) — how random is each model?",
        bot + 190)
    ax, y_of = _y_axis(lo, hi, plot_top, plot_h, left)
    lines += ax
    codes = _config_codes(recs)
    xstep = (FIG_W - MARG_L - MARG_R) / (n + 1)
    for i, r in enumerate(recs):
        xc = left + xstep * (i + 1)
        xd, xp = xc - xstep * 0.13, xc + xstep * 0.13
        lines += _sd_range_bars(xd, r["direct"]["canonical"], y_of, C_DIRECT)
        lines += _sd_range_bars(xp, r["primed"]["canonical"], y_of, C_PRIMED)
        code = codes["__".join(r["config"])]
        lines.append(f'<text x="{xc:.1f}" y="{bot + 16}" text-anchor="middle" '
                     f'font-family="Helvetica,Arial" font-size="10" '
                     f'fill="#111">{code}</text>')
    lines += _caption_block(codes, recs, bot + 40, FIG_W - MARG_L - MARG_R)
    lines.append("</svg>")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")


def figure_d(recs: list[dict], out: Path) -> None:
    """Old single-run delta vs repeated mean delta (canonical)."""
    rows = []
    for r in recs:
        old = r.get("old_single")
        new = r["deltas"]["mean_canonical"]
        if old is None or new is None:
            continue
        rows.append((r, old["old_delta_canonical"], new["delta_mean"]))
    if not rows:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(
            f"<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"{FIG_W}\" "
            f"height=\"120\"><text x=\"20\" y=\"30\" font-size=\"12\" "
            f"fill=\"#555\">Figure D: Task-024 legacy single-run data not "
            f"available (no collected/evaluated Phase-1/Phase-2A rosters)."
            f"</text></svg>", encoding="utf-8")
        return
    allv = [x[1] for x in rows] + [x[2] for x in rows]
    lo, hi = min(allv), max(allv)
    n = len(rows)
    plot_top, plot_h = MARG_T + 14, 300
    bot = plot_top + plot_h
    left = MARG_L
    lines = _svg_head(
        "Figure D — Old Task-024 single-run delta (grey) vs repeated mean delta "
        "(green): which previous conclusions were stable?", bot + 190)
    ax, y_of = _y_axis(lo, hi, plot_top, plot_h, left)
    lines += ax
    zero_y = y_of(0.0) if lo <= 0 <= hi else None
    if zero_y is not None:
        lines.append(f'<line x1="{left}" y1="{zero_y:.1f}" x2="{FIG_W - MARG_R}" '
                     f'y2="{zero_y:.1f}" stroke="#999" stroke-width="1" '
                     f'stroke-dasharray="4 3"/>')
    codes = _config_codes(recs)
    ystep = (bot - plot_top) / (n + 1)
    for i, (r, old, new) in enumerate(rows):
        yc = plot_top + ystep * (i + 1)
        yo, yn = y_of(old), y_of(new)
        lines.append(f'<line x1="{yo:.1f}" y1="{yc:.1f}" x2="{yn:.1f}" '
                     f'y2="{yc:.1f}" stroke="#aaa" stroke-width="0.8"/>')
        lines.append(f'<rect x="{yo - 5:.1f}" y="{yc - 5:.1f}" width="10" '
                     f'height="10" fill="{C_OLD}" opacity="0.9"/>')
        lines.append(f'<circle cx="{yn:.1f}" cy="{yc:.1f}" r="5" '
                     f'fill="{C_NEW}"/>')
        code = codes["__".join(r["config"])]
        lines.append(f'<text x="{left - 8}" y="{yc + 4:.1f}" text-anchor="end" '
                     f'font-family="Helvetica,Arial" font-size="10" '
                     f'fill="#111">{code}</text>')
        lines.append(f'<text x="{FIG_W - MARG_R}" y="{yc + 4:.1f}" '
                     f'text-anchor="end" font-family="Helvetica,Arial" '
                     f'font-size="7.5" fill="#333">old {_fmt_pp(old)} / '
                     f"new {_fmt_pp(new)}</text>")
    lines += _caption_block(codes, recs, bot + 40, FIG_W - MARG_L - MARG_R)
    lines += [f'<text x="{MARG_L}" y="{bot + 40 + 14 * (math.ceil(n / 2) + 1)}" '
              f'font-family="Helvetica,Arial" font-size="9.5" fill="#555">'
              f"Grey square = Task-024 single delta (P2A_single − P1_single); "
              f"green circle = repeated estimate mean(primed) − mean(direct); "
              f"n=3 per condition. {TASK024_DELTA_SOURCE}.</text>"]
    lines.append("</svg>")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")


def figure_e(recs: list[dict], out: Path) -> None:
    """Baseline dependence revisited: repeated direct mean (x) vs repeated
    priming delta (y), canonical; OLS trend + new Spearman rho."""
    pts = []
    for r in recs:
        d = r["direct"]["canonical"]
        dd = r["deltas"]["mean_canonical"]
        if d["mean"] is not None and dd is not None:
            pts.append((d["mean"], dd["delta_mean"], r))
    if not pts:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(
            f"<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"{FIG_W}\" "
            f"height=\"120\"><text x=\"20\" y=\"30\" font-size=\"12\" "
            f"fill=\"#555\">Figure E: no repeated data yet.</text></svg>",
            encoding="utf-8")
        return
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    lo_x, hi_x = min(xs), max(xs)
    lo_y, hi_y = min(ys), max(ys)
    pad_y = (hi_y - lo_y) * 0.15 if hi_y > lo_y else 0.02
    lo_y, hi_y = lo_y - pad_y, hi_y + pad_y
    pad_x = (hi_x - lo_x) * 0.08 if hi_x > lo_x else 0.02
    lo_x, hi_x = lo_x - pad_x, hi_x + pad_x
    plot_top, plot_h = MARG_T + 14, 300
    bot = plot_top + plot_h
    left = MARG_L
    lines = _svg_head(
        "Figure E — Baseline dependence revisited (repeated direct mean vs repeated "
        "priming delta; Task-024 follow-up)", bot + 190)
    # x axis
    for i in range(6):
        v = lo_x + (hi_x - lo_x) * i / 5
        x = left + (v - lo_x) / (hi_x - lo_x) * (FIG_W - MARG_R - left)
        y0 = bot
        lines.append(f'<line x1="{x:.1f}" y1="{y0}" x2="{x:.1f}" y2="{y0 + 5}" '
                     f'stroke="{C_AXIS}"/>')
        lines.append(f'<text x="{x:.1f}" y="{y0 + 16}" text-anchor="middle" '
                     f'font-family="Helvetica,Arial" font-size="9" '
                     f'fill="{C_AXIS}">{_fmt_pct(v)}</text>')
    ax, y_of = _y_axis(lo_y, hi_y, plot_top, plot_h, left)
    lines += ax
    ols = ols_slope_intercept(xs, ys)
    if ols:
        x0, x1 = lo_x, hi_x
        y0, y1 = ols[0] * x0 + ols[1], ols[0] * x1 + ols[1]
        yy0, yy1 = y_of(y0), y_of(y1)
        lines.append(f'<line x1="{left:.1f}" y1="{yy0:.1f}" x2="'
                     f'{FIG_W - MARG_R:.1f}" y2="{yy1:.1f}" stroke="#999" '
                     f'stroke-width="1" stroke-dasharray="4 3"/>')
    codes = _config_codes(recs)
    for (x, y, r) in pts:
        px = left + (x - lo_x) / (hi_x - lo_x) * (FIG_W - MARG_R - left)
        py = y_of(y)
        code = codes["__".join(r["config"])]
        lines.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="4.5" '
                     f'fill="{C_NEW}" opacity="0.9"/>')
        lines.append(f'<text x="{px + 6:.1f}" y="{py - 5:.1f}" '
                     f'font-family="Helvetica,Arial" font-size="8.5" '
                     f'fill="#333">{code}</text>')
    rho = spearman(xs, ys)
    lines.append(f'<text x="{FIG_W - MARG_R}" y="{plot_top}" '
                 f'text-anchor="end" font-family="Helvetica,Arial" '
                 f'font-size="11" fill="#111">new Spearman ρ = '
                 f'{rho if rho is None else f"{rho:.2f}"}  ·  '
                 f"{TASK024_RHO_NOTE}</text>")
    lines += _caption_block(codes, recs, bot + 40, FIG_W - MARG_L - MARG_R)
    lines.append("</svg>")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")


# ---------------------------------------------------------------------------
# selection views + narrative
# ---------------------------------------------------------------------------

CANDIDATES = {
    ("deepseek", "deepseek-v3-expert", "deepthinkon"):
        ("High primed performance — is it stable?",
         "Previous: 79.92/80.49 baseline family → 84.62/85.63 primed."),
    ("deepseek", "deepseek-v3-expert", "deepthinkoff"):
        ("High primed performance — is it stable?",
         "Previous: 79.92/80.49 baseline family → 84.62/85.63 primed."),
    ("anthropic", "claude", "sonnet-5"):
        ("Does a large priming improvement recur?",
         "Previous: 72.97 → 84.63 (+11.66 pp)."),
    ("alibaba", "qwen-3.8-max", "fast"):
        ("Does a high-baseline model remain high and stable?",
         "Previous: 82.35 → 85.38 (+3.04 pp)."),
    ("google", "gemini-3.6-flash", "extthinkon"):
        ("Was the large shift reproducible?",
         "Previous: 69.86 → 84.19 (+14.33 pp)."),
    ("google", "gemini-3.6-flash", "extthinkoff"):
        ("Gemini Flash OFF companion of the ON row.",
         "Previous: OFF sibling of the ON row."),
    ("bytedance", "dola-3.8", "fast"):
        ("Does anything remotely similar to +28.20 pp happen again? "
         "(exploratory)",
         "Previous: 38.87 → 67.07 (+28.20 pp)."),
    ("bytedance", "dola-3.8", "pro"):
        ("Dola Pro companion (exploratory).",
         "Previous: exploratory Dola primed run without Phase-1 baseline at "
         "Task 021; Phase-1 baseline prepared retrospectively (Task 023)."),
}


def _row(r: dict) -> dict:
    """Compact per-configuration selection-view row."""
    d_c = r["direct"]["canonical"]
    p_c = r["primed"]["canonical"]
    d_b = r["direct"]["broader"]
    p_b = r["primed"]["broader"]
    delta = r["deltas"]["mean_canonical"]
    old = r.get("old_single")
    return {
        "config": r["config"], "label": r["label"],
        "canonical_direct_mean": d_c["mean"],
        "canonical_direct_sd": d_c["sd"],
        "canonical_direct_range": d_c["range"],
        "canonical_primed_mean": p_c["mean"],
        "canonical_primed_sd": p_c["sd"],
        "canonical_primed_range": p_c["range"],
        "broader_direct_mean": d_b["mean"],
        "broader_primed_mean": p_b["mean"],
        "unresolved_direct_mean": r["direct"]["unresolved"]["mean"],
        "unresolved_primed_mean": r["primed"]["unresolved"]["mean"],
        "ortho_direct_mean": r["direct"]["ortho_out"]["mean"],
        "ortho_primed_mean": r["primed"]["ortho_out"]["mean"],
        "delta_mean_canonical": (delta or {}).get("delta_mean"),
        "old_delta_canonical": (old or {}).get("old_delta_canonical"),
    }


def _selection_table_md(rows: list[dict]) -> str:
    def pp(v):
        return _fmt_pp(v)

    def diff_pp(a, b):
        """a - b in pp when both present, else n/a (never fabricate)."""
        if a is None or b is None:
            return "n/a"
        return f"{(a - b) * 100:+.2f} pp"

    def diff_count(a, b):
        """a - b as a plain count (orthography anomalies), else n/a."""
        if a is None or b is None:
            return "n/a"
        return f"{a - b:+.1f}"

    out = [
        "| config | dir mean | dir SD | dir range | primed mean | primed SD | "
        "primed range | Δ mean | old Δ | broader Δ | unres Δ | ortho Δ |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for r in rows:
        out.append(
            f"| {r['label']} | {_fmt_pct(r['canonical_direct_mean'])} | "
            f"{pp(r['canonical_direct_sd'])} | "
            f"{pp(r['canonical_direct_range'])} | "
            f"{_fmt_pct(r['canonical_primed_mean'])} | "
            f"{pp(r['canonical_primed_sd'])} | "
            f"{pp(r['canonical_primed_range'])} | "
            f"{pp(r['delta_mean_canonical'])} | "
            f"{pp(r['old_delta_canonical'])} | "
            f"{diff_pp(r['broader_primed_mean'], r['broader_direct_mean'])} | "
            f"{diff_pp(r['unresolved_primed_mean'], r['unresolved_direct_mean'])} | "
            f"{diff_count(r['ortho_primed_mean'], r['ortho_direct_mean'])} |")
    return "\n".join(out)


def _fmt_cell(v: float | None, pp: bool = False) -> str:
    if v is None:
        return "n/a"
    return f"{v * 100:+.2f} pp" if pp else f"{v * 100:.2f}%"


def _candidate_md(dataset: dict) -> str:
    by_key = {tuple(r["config"]): r for r in dataset["primary"]}
    for r in dataset["exploratory"]:
        by_key[tuple(r["config"])] = r
    lines = [
        "## Candidate configurations (Task-024 follow-up, descriptive)",
        "",
        "n=3 per condition — small-sample descriptive statistics. No claim "
        "of population-level behaviour follows from three repetitions.",
        "",
    ]
    for key, (question, previous) in sorted(CANDIDATES.items()):
        r = by_key.get(key)
        lines.append(f"### {' / '.join(str(k) for k in key)}")
        lines.append("")
        lines.append(f"- Task-024 question: {question}")
        lines.append(f"- Task-024 single-run record: {previous}")
        if r is None:
            lines.append("- Repeated data: not available (not collected or "
                         "not usable).")
        else:
            d, p = r["direct"]["canonical"], r["primed"]["canonical"]
            delta = r["deltas"]["mean_canonical"]
            old = r.get("old_single")
            lines.append(
                f"- Repeated direct: mean {_fmt_cell(d['mean'])} "
                f"(sd {_fmt_pp(d['sd'])}, range {_fmt_pp(d['range'])}), "
                f"n={d['n']}.")
            lines.append(
                f"- Repeated primed: mean {_fmt_cell(p['mean'])} "
                f"(sd {_fmt_pp(p['sd'])}, range {_fmt_pp(p['range'])}), "
                f"n={p['n']}.")
            lines.append(
                f"- Repeated Δ mean canonical: {_fmt_cell((delta or {}).get('delta_mean'), pp=True)}"
                f"{'  (old single Δ: ' + _fmt_cell(old['old_delta_canonical'], pp=True) + ')' if old else ''}.")
        lines.append("")
    return "\n".join(lines)


def _stats_table_md(recs: list[dict]) -> str:
    lines = [
        "| config | cond | n | canonical mean | canonical median | canonical "
        "SD | min | max | range | broader mean | unresolved mean | ortho "
        "min/mean/max |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for r in recs:
        for cond in ("direct", "primed"):
            c = r[cond]["canonical"]
            b = r[cond]["broader"]
            u = r[cond]["unresolved"]
            o = r[cond]["ortho_out"]
            ortho = ("—" if o["n"] == 0 else
                     f"{o['min']}/{o['mean']:.1f}/{o['max']}")
            lines.append(
                f"| {r['label']} | {cond} | {c['n']} | "
                f"{_fmt_cell(c['mean'])} | {_fmt_cell(c['median'])} | "
                f"{_fmt_pp(c['sd'])} | {_fmt_cell(c['min'])} | "
                f"{_fmt_cell(c['max'])} | {_fmt_pp(c['range'])} | "
                f"{_fmt_cell(b['mean'])} | {_fmt_cell(u['mean'])} | "
                f"{ortho} |")
    return "\n".join(lines)


def build_analysis(primary: list[dict], exploratory: list[dict]) -> dict:
    """Deterministic analysis.json body (machine-readable facts)."""
    prim_rows = [_row(r) for r in primary]
    expl_rows = [_row(r) for r in exploratory]
    # baseline dependence revisited (primary only, descriptive)
    pts = []
    for r in primary:
        d = r["direct"]["canonical"]
        dd = r["deltas"]["mean_canonical"]
        if d["mean"] is not None and dd is not None:
            pts.append({"config": r["config"], "label": r["label"],
                        "repeated_direct_mean": d["mean"],
                        "repeated_delta_mean": dd["delta_mean"]})
    xs = [p["repeated_direct_mean"] for p in pts]
    ys = [p["repeated_delta_mean"] for p in pts]
    new_rho = spearman(xs, ys) if len(xs) >= 2 else None
    old_pts = []
    for r in primary:
        old = r.get("old_single")
        dd = r["deltas"]["mean_canonical"]
        if old is not None and dd is not None:
            old_pts.append({"config": r["config"], "label": r["label"],
                            "old_delta": old["old_delta_canonical"],
                            "new_delta": dd["delta_mean"]})
    return {
        "status": ("results" if primary else "no_results"),
        "primary": prim_rows,
        "exploratory": expl_rows,
        "counts": {
            "primary_configs_with_data": len(primary),
            "exploratory_configs_with_data": len(exploratory),
            "primary_repeated_deltas": len(pts),
            "primary_old_single_deltas": len(old_pts),
        },
        "baseline_dependence_revisited": {
            "n": len(pts),
            "new_spearman_rho": new_rho,
            "task024_rho": -0.86,
            "task024_rho_note": TASK024_RHO_NOTE,
            "note": "Descriptive follow-up, n=18 primary configurations; "
                    "not a causal test.",
        },
        "old_vs_new_deltas": old_pts,
        "interpretation_rules": [
            "Directly supported: observed run-to-run variation; observed "
            "mean/SD/range; observed repeated direct-vs-primed differences; "
            "reproducibility (or not) of Task-024 patterns.",
            "Suggestive: candidates whose priming effect appears robust; "
            "candidates with unusually low variance; possible baseline "
            "dependence.",
            "Not established: causality; that corpus priming generally "
            "improves ISV; that a model is 'best'; that coverage equals "
            "naturalness; that reasoning mode is superior; that Dola Fast "
            "has a special learning ability; that three repetitions "
            "establish population-level model behaviour.",
        ],
    }


def build_markdown(dataset: dict, analysis: dict) -> str:
    primary, exploratory = dataset["primary"], dataset["exploratory"]
    lines = [
        "# EXP-004 Phase repeat — repeated-generation analysis",
        "",
        "Deterministic analysis of the controlled repeated-generation "
        "dataset (SODA Task 025). Primary statistics use exactly the "
        "original 18 usable configurations; exploratory Dola rows are "
        "reported separately and never merged into primary statistics.",
        "",
        ("Status: results — repeated observations analysed."
         if primary else
         "Status: NO RESULTS YET — no usable repeat observations found "
         "(collect + evaluate first)."),
        "",
        "## 1. Research question",
        "",
        "For the same model/configuration and the same translation task, "
        "how much does measured Interslavic resource coverage vary between "
        "independent generations, and is the observed Phase-2A "
        "corpus-priming shift larger than that variation?",
        "",
        "## 2. Design and sample",
        "",
        "- Primary population: 18 configurations × direct/primed × 3 "
        "independent fresh-session replicates (108 planned runs).",
        "- Exploratory: Dola 3.8 Fast/Pro × direct/primed × 3 (12 planned "
        "runs) — never merged into the primary statistics.",
        "- Replicate labels r01/r02/r03 are replication blocks, NOT matched "
        "linguistic samples; the primary comparison is distribution/mean-"
        "based: mean(primed replicates) − mean(direct replicates).",
        "- n=3 per condition: small-sample descriptive statistics only; no "
        "normality-based claims.",
        "",
        "## 3. Per-configuration statistics (n<=3 descriptive)",
        "",
        _stats_table_md(primary),
        "",
    ]
    if exploratory:
        lines += [
            "### 3b. Exploratory Dola configurations (separate, never "
            "primary)",
            "",
            _stats_table_md(exploratory),
            "",
        ]
    lines += [
        "## 4. Priming comparison under repetition (canonical coverage)",
        "",
        _selection_table_md([_row(r) for r in primary]),
        "",
        "The most important quantity is the repeated estimate "
        "mean(primed replicates) − mean(direct replicates); the old "
        "Task-024 single delta (P2A_single − P1_single) is shown for "
        "comparison (Figure D).",
        "",
        "## 5. Baseline dependence revisited",
        "",
    ]
    bd = analysis.get("baseline_dependence_revisited") or {}
    lines += [
        f"- New Spearman ρ = "
        f"{bd.get('new_spearman_rho') if bd.get('new_spearman_rho') is None else round(bd['new_spearman_rho'], 2)} "
        f"(n = {bd.get('n')}) vs Task-024 ρ ≈ −0.86. Descriptive "
        f"follow-up only.",
        "",
        "## 6. Figures",
        "",
        "- Figure A — replicate distributions: "
        "`analysis/figures/figure_a.svg`",
        "- Figure B — priming deltas sorted: "
        "`analysis/figures/figure_b.svg`",
        "- Figure C — stochastic spread: "
        "`analysis/figures/figure_c.svg`",
        "- Figure D — old single-run delta vs repeated mean delta: "
        "`analysis/figures/figure_d.svg`",
        "- Figure E — baseline dependence revisited: "
        "`analysis/figures/figure_e.svg`",
        "",
        "## 7. Candidate configurations (Task-024 follow-up)",
        "",
        _candidate_md(dataset),
        "## 8. Interpretation",
        "",
    ]
    lines += [f"- {rule}" for rule in
              (analysis.get("interpretation_rules") or [])]
    lines += [
        "",
        "## 9. Limitations",
        "",
        "- n=3 per condition: descriptive only; SDs are noisy estimates.",
        "- Replicates are not matched samples; block differences are "
        "secondary descriptive views.",
        "- Interface/server variation is unavoidable and recorded as "
        "metadata, not removed.",
        "- Coverage is evidence, not linguistic correctness or naturalness.",
        "- Three repetitions do not establish population-level model "
        "behaviour.",
        "",
    ]
    return "\n".join(lines)


def write_analysis(out_dir: Path, repeat_obs: list[dict],
                   legacy: list[dict] | None = None) -> dict:
    dataset = build_dataset(repeat_obs, legacy)
    analysis = build_analysis(dataset["primary"], dataset["exploratory"])
    out_dir.mkdir(parents=True, exist_ok=True)
    figures = out_dir / "figures"
    figures.mkdir(parents=True, exist_ok=True)
    # Figures are only meaningful once usable replicates exist; with no
    # results the analysis.md states the plan explicitly and no empty
    # charts are fabricated.
    if dataset["primary"]:
        figure_a(dataset["primary"], figures / "figure_a.svg")
        figure_b(dataset["primary"], figures / "figure_b.svg")
        figure_c(dataset["primary"], figures / "figure_c.svg")
        figure_d(dataset["primary"], figures / "figure_d.svg")
        figure_e(dataset["primary"], figures / "figure_e.svg")
    else:
        for name in ("figure_a.svg", "figure_b.svg", "figure_c.svg",
                     "figure_d.svg", "figure_e.svg"):
            (figures / name).write_text(
                "<!-- figure not generated: no usable repeat "
                "observations yet -->\n", encoding="utf-8")
    (out_dir / "dataset.json").write_text(
        json.dumps(dataset, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "analysis.json").write_text(
        json.dumps(analysis, ensure_ascii=False, indent=2),
        encoding="utf-8")
    md = build_markdown(dataset, analysis)
    (out_dir / "analysis.md").write_text(md, encoding="utf-8")
    return analysis


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="EXP-004 Phase repeat — deterministic repeated-"
                    "generation analysis (SODA Task 025).")
    ap.add_argument("--roster", type=Path, default=DEFAULT_ROSTER)
    ap.add_argument("--p1-roster", type=Path, default=DEFAULT_P1_ROSTER)
    ap.add_argument("--p2a-roster", type=Path, default=DEFAULT_P2A_ROSTER)
    ap.add_argument("--out", type=Path, default=DEFAULT_ANALYSIS_DIR)
    args = ap.parse_args(argv)

    try:
        obs = load_repeat_observations(args.roster)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    usable = [o for o in obs if o["usable"]]
    legacy = None
    if usable:
        try:
            legacy = load_legacy_singles(args.p1_roster, args.p2a_roster)
        except FileNotFoundError as exc:
            print(f"warning: {exc} — Figure D / old-delta columns will be "
                  "empty", file=sys.stderr)
            legacy = []
    analysis = write_analysis(args.out, usable, legacy)
    print(f"[analyze] wrote {args.out} (status: {analysis['status']})")
    if not usable:
        print("  no usable repeat observations yet — run the collection "
              "pipeline first (run_exp004_repeats.py)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
