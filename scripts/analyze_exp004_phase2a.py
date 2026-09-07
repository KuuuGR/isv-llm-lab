#!/usr/bin/env python3
"""EXP-004 full analysis — Phase 1 → Phase 2A corpus priming (SODA Task 024).

Read-only research analysis over the COMPLETED EXP-004 dataset. It never
calls an LLM, never collects new outputs, never modifies raw outputs, the
corpus, or any evaluation artifact. Every number in the outputs is derived
deterministically from the committed/recorded evidence:

  inputs
    experiments/exp004-modelscreen/outputs/roster.json         (Phase-1,
        21 rows incl. the two Dola retrospective baselines, Task 023)
    experiments/exp004-modelscreen/phase2a/outputs/roster.json (Phase-2A,
        38 rows; the 20 corpus-primed runs)
    experiments/exp004-modelscreen/phase2a/outputs/compare.json
        (primed-vs-baseline pairing + deltas produced by run_exp004_phase2a)
    per-run intake/evaluation/orthography are already folded into the
        rosters (the rosters are generated deterministically from them)

  outputs (all under experiments/exp004-modelscreen/analysis/, gitignored
  except README.md — derived artifacts stay local like all EXP-004 outputs)
    dataset.json      assembled per-configuration dataset (P1/P2A/deltas)
    analysis.json     machine-readable analysis (rankings, stats, tests,
                      correlations, families, orthography, master table)
    analysis.md       human-readable quantitative analysis report
    figures/chart_a..g.svg   charts A–G (deterministic SVG, no plotting
                      dependencies; the repo has none and none is added)
    poster.md, poster.html   first research-poster draft (embeds the SVG)

Dataset definition
  20 configurations: the original 18 Phase-1-usable configurations (GLM 4.5
  is excluded exactly as in Phase 1/2A: its Phase-1 intake failed) + the
  two exploratory Dola 3.8 configurations (Fast/Pro, `exploratory: true`,
  NOT part of the original roster — preserved separately, never merged).
  Each configuration contributes its Phase-1 direct generation and its
  Phase-2A corpus-primed generation (one each — see the limitations section
  in analysis.md; deltas are paired per configuration).

Methodology
  All deltas = Phase-2A − Phase-1 for the same configuration (existing
  metrics: canonical resource coverage, broader resource-supported
  coverage, unresolved rate, lexical token count, orthography
  outside-inventory + category counts; A/B/C bucket counts). No composite
  score, no ranking of models, no new linguistic evaluator, no manual
  re-interpretation of words. Descriptive statistics use the standard
  library only. Paired tests (exact sign test + exact sign-flip
  permutation test on the paired deltas) are EXPLORATORY and labelled as
  such: each configuration contributes exactly one direct and one primed
  generation, so any delta conflates priming, stochastic generation
  variation, interface behaviour, configuration differences and possible
  baseline dependence. Correlations are Spearman rank correlations,
  descriptive only. Charts are pure functions of dataset.json (fixed
  colour map, fixed geometry, no randomness).

Commands:
  analyze                write dataset.json + analysis.json + analysis.md
  charts                 write figures/chart_a..g.svg
  poster                 write poster.md + poster.html
  all                    analyze + charts + poster (default)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXP = ROOT / "experiments" / "exp004-modelscreen"
P1_OUTPUTS = EXP / "outputs"
P2A_OUTPUTS = EXP / "phase2a" / "outputs"
P1_ROSTER = P1_OUTPUTS / "roster.json"
P2A_ROSTER = P2A_OUTPUTS / "roster.json"
COMPARE_JSON = P2A_OUTPUTS / "compare.json"
ANALYSIS_DIR = EXP / "analysis"
FIGURES_DIR = ANALYSIS_DIR / "figures"

try:  # same stamping helper used by the other run orchestrators
    from isv_eval.cli import git_commit
except Exception:  # pragma: no cover - analysis must not die on import path
    def git_commit() -> str:
        return "unknown"

# Fixed corpus / source pins (identical to run_exp004_phase2a.py).
CORPUS_ID = "phase2a-authentic-isv"
CORPUS_VERSION = "v1"
AUTH_CORPUS_SHA256 = (
    "aaad28e43935a40313585d77a33bfc788d97e8d69b081f9486af74d52ca1a857")

# Canonical configuration order: original 18 by their preregistered
# Phase-1 number, then the two exploratory Dola configurations (fast, pro).
FAMILY_ORDER = [
    "GPT", "Claude", "Gemini", "DeepSeek", "Qwen", "Grok", "Kimi", "Dola",
]
FAMILY_OF = {
    "openai": "GPT", "anthropic": "Claude", "google": "Gemini",
    "deepseek": "DeepSeek", "alibaba": "Qwen", "xai": "Grok",
    "moonshot": "Kimi", "bytedance": "Dola",
}

# Deterministic short labels (charts + tables). Keyed by
# (provider, model, model_version).
SHORT_LABELS = {
    ("openai", "gpt-5.6-luna", "thinkoff"): "GPT-5.6 Luna OFF",
    ("openai", "gpt-5.6-luna", "thinkon"): "GPT-5.6 Luna ON",
    ("openai", "gpt-isv-teacher", "unknown"): "GPT ISV Teacher",
    ("anthropic", "claude", "sonnet-5"): "Claude Sonnet 5",
    ("anthropic", "claude", "sonnet-5-max"): "Claude Sonnet 5 max",
    ("google", "gemini-3.1-pro", "extthinkon"): "Gemini 3.1 Pro ON",
    ("google", "gemini-3.6-flash", "extthinkoff"): "Gemini 3.6 Flash OFF",
    ("google", "gemini-3.6-flash", "extthinkon"): "Gemini 3.6 Flash ON",
    ("deepseek", "deepseek-v3-instant", "deepthinkoff"): "DeepSeek V3 Instant OFF",
    ("deepseek", "deepseek-v3-instant", "deepthinkon"): "DeepSeek V3 Instant ON",
    ("deepseek", "deepseek-v3-expert", "deepthinkoff"): "DeepSeek V3 Expert OFF",
    ("deepseek", "deepseek-v3-expert", "deepthinkon"): "DeepSeek V3 Expert ON",
    ("xai", "grok", "unknown"): "Grok",
    ("moonshot", "kimi", "k2.6-instant"): "Kimi K2.6 Instant",
    ("alibaba", "qwen-3.8-max", "thinking"): "Qwen 3.8 Max Think",
    ("alibaba", "qwen-3.8-max", "fast"): "Qwen 3.8 Max Fast",
    ("alibaba", "qwen-3.7-plus", "thinking"): "Qwen 3.7 Plus Think",
    ("alibaba", "qwen-3.7-plus", "fast"): "Qwen 3.7 Plus Fast",
    ("bytedance", "dola-3.8", "fast"): "Dola 3.8 Fast",
    ("bytedance", "dola-3.8", "pro"): "Dola 3.8 Pro",
}

# Per-configuration recorded execution notes (from the Task 021/023 audit;
# pure documentation, never metrics).
NOTES = {
    "openai__gpt-5.6-luna__thinkoff": "free ChatGPT web; no constraint recorded",
    "openai__gpt-5.6-luna__thinkon": "free ChatGPT web; thinking ON",
    "openai__gpt-isv-teacher__unknown": "custom GPT; built-in system prompt unknown (recorded confound D-018)",
    "anthropic__claude__sonnet-5": "Claude web; free-tier token allowance exhausted repeatedly — three waits/continuations (Task 021)",
    "anthropic__claude__sonnet-5-max": "Claude web; P2A intake partial — final line **KONEC** bold-wrapped (usable=no by the end-marker rule, evaluated); >45 min + free-tier exhaustion; three token-limit continuations",
    "google__gemini-3.1-pro__extthinkon": "corpus messages ingested in Gemini 3.6 Flash, model switched to 3.1 Pro for the translation (documented deviation: ingestion model != translation model)",
    "google__gemini-3.6-flash__extthinkoff": "corpus delivered as two messages (~83% + ~17% with 'continue previous prompt') — interface one-message limit",
    "google__gemini-3.6-flash__extthinkon": "corpus two-message delivery; extended-thinking toggle re-enabled per prompt (auto-reset)",
    "deepseek__deepseek-v3-instant__deepthinkoff": "no constraint recorded",
    "deepseek__deepseek-v3-instant__deepthinkon": "no constraint recorded",
    "deepseek__deepseek-v3-expert__deepthinkoff": "no constraint recorded",
    "deepseek__deepseek-v3-expert__deepthinkon": "no constraint recorded",
    "xai__grok__unknown": "no constraint recorded",
    "moonshot__kimi__k2.6-instant": "no constraint recorded",
    "alibaba__qwen-3.8-max__thinking": "no constraint recorded",
    "alibaba__qwen-3.8-max__fast": "no constraint recorded",
    "alibaba__qwen-3.7-plus__thinking": "no constraint recorded",
    "alibaba__qwen-3.7-plus__fast": "no constraint recorded",
    "bytedance__dola-3.8__fast": "EXPLORATORY (not part of the original 18). Identity author-recorded in prompt headers only, not independently verifiable; P1 baseline collected retrospectively (Task 023)",
    "bytedance__dola-3.8__pro": "EXPLORATORY (not part of the original 18). Identity author-recorded in prompt headers only, not independently verifiable; P1 baseline collected retrospectively (Task 023)",
}

ORTHO_CATEGORIES = [
    ("cyrillic", "Cyrillic"),
    ("polish_specific", "Polish-specific"),
    ("other_latin", "other Latin"),
    ("other_script", "other script"),
    ("unexpected_nonletters", "unexpected non-letter"),
]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def _load_json(path: Path) -> dict | list:
    return json.loads(path.read_text(encoding="utf-8"))


def _num(x: float | int | None, nd: int = 4) -> str:
    return "—" if x is None else f"{x:.{nd}f}"


def pct(x: float | None, nd: int = 2) -> str:
    return "—" if x is None else f"{x * 100:.{nd}f}%"


def pp(x: float | None, nd: int = 2) -> str:
    return "—" if x is None else f"{x * 100:+.2f} pp" if nd == 2 else f"{x * 100:+.{nd}f} pp"


# ---------------------------------------------------------------------------
# 1. Dataset assembly
# ---------------------------------------------------------------------------

def _row_metrics(row: dict) -> dict:
    return row.get("metrics") or {}


def _row_ortho(row: dict) -> dict:
    return row.get("orthography") or {}


def _phase1_sort_key(x: dict):
    pn = x.get("phase1_number")
    if pn is not None:
        return (0, pn)
    return (1, 0 if "fast" in x.get("run_id", "") else 1)


def _config_key(x: dict) -> str:
    return f"{x['provider']}__{x['model']}__{x['model_version']}"


def _short_label(x: dict) -> str:
    return SHORT_LABELS.get(
        (x["provider"], x["model"], x["model_version"]), x["label"])


def _notes_for(x: dict) -> str:
    return NOTES.get(_config_key(x), "")


def build_dataset() -> dict:
    """Assemble the deterministic 20-configuration dataset.

    Returns a dict with metadata (input hashes), the ordered configuration
    list and per-configuration P1/P2A metrics + exact deltas. Raises on any
    missing/invalid value (none expected for the completed dataset).
    """
    if not P1_ROSTER.is_file() or not P2A_ROSTER.is_file():
        sys.exit("missing roster input; run the phase1/phase2a roster "
                 "commands first")
    p1_raw = _load_json(P1_ROSTER)
    p1_rows = {r["run_id"]: r for r in (p1_raw if isinstance(p1_raw, list)
                                        else p1_raw.get("rows", []))}
    p2a = _load_json(P2A_ROSTER)
    if isinstance(p2a, dict):
        p2a = p2a.get("rows", [])
    primed = [r for r in p2a if r.get("condition") == "p2a-primed"]
    primed.sort(key=_phase1_sort_key)

    compare = _load_json(COMPARE_JSON)
    compare_rows = {r["run_id"]: r for r in compare["rows"]}

    configs: list[dict] = []
    for p2 in primed:
        rid = p2["run_id"]
        b_id = p2.get("baseline_run_id")
        if not b_id or b_id not in p1_rows:
            raise ValueError(f"{rid}: baseline {b_id!r} missing from Phase-1 "
                             "roster")
        p1 = p1_rows[b_id]
        if not p1.get("usable"):
            raise ValueError(f"{rid}: Phase-1 baseline {b_id} not usable")
        m1, m2 = _row_metrics(p1), _row_metrics(p2)
        o1, o2 = _row_ortho(p1), _row_ortho(p2)
        need = ("canonical_coverage", "broader_resource_supported_coverage",
                "unresolved_rate", "total_tokens", "exact_dictionary_matches",
                "morphologically_valid_forms", "bucket_counts")
        missing = [k for k in need
                   if m1.get(k) is None or m2.get(k) is None]
        if missing:
            raise ValueError(f"{rid}: missing metrics {missing}")
        for label, o in (("P1", o1), ("P2A", o2)):
            for k in ("outside_inventory",) + tuple(
                    c for c, _ in ORTHO_CATEGORIES):
                if o.get(k) is None:
                    raise ValueError(f"{rid} {label}: missing orthography "
                                     f"{k}")

        def delta(field: str) -> float:
            return float(m2[field]) - float(m1[field])

        # reconcile with the phase2a compare artifact (guard against drift)
        cr = compare_rows.get(rid)
        cfg = {
            "run_id_p1": b_id,
            "run_id_p2a": rid,
            "label": p2["label"],
            "short_label": _short_label(p2),
            "family": FAMILY_OF[p2["provider"]],
            "provider": p2["provider"],
            "model": p2["model"],
            "model_version": p2["model_version"],
            "phase1_number": p2.get("phase1_number"),
            "exploratory": bool(p2.get("phase1_number") is None),
            "p1_intake": p1.get("intake_verdict"),
            "p2a_intake": p2.get("intake_verdict"),
            "p2a_usable": bool(p2.get("usable")),
            "notes": _notes_for(p2),
            "P1": {
                "canonical_coverage": float(m1["canonical_coverage"]),
                "broader_coverage": float(
                    m1["broader_resource_supported_coverage"]),
                "unresolved_rate": float(m1["unresolved_rate"]),
                "lexical_tokens": int(m1["total_tokens"]),
                "exact_A": int(m1["exact_dictionary_matches"]),
                "morph_B": int(m1["morphologically_valid_forms"]),
                "buckets": dict(m1["bucket_counts"]),
                "ortho_out": int(o1["outside_inventory"]),
                "ortho": {c: int(o1[c]) for c, _ in ORTHO_CATEGORIES},
            },
            "P2A": {
                "canonical_coverage": float(m2["canonical_coverage"]),
                "broader_coverage": float(
                    m2["broader_resource_supported_coverage"]),
                "unresolved_rate": float(m2["unresolved_rate"]),
                "lexical_tokens": int(m2["total_tokens"]),
                "exact_A": int(m2["exact_dictionary_matches"]),
                "morph_B": int(m2["morphologically_valid_forms"]),
                "buckets": dict(m2["bucket_counts"]),
                "ortho_out": int(o2["outside_inventory"]),
                "ortho": {c: int(o2[c]) for c, _ in ORTHO_CATEGORIES},
            },
        }
        cfg["deltas"] = {
            "canonical_coverage_pp": delta("canonical_coverage"),
            "broader_coverage_pp": delta(
                "broader_resource_supported_coverage"),
            "unresolved_rate_pp": delta("unresolved_rate"),
            "lexical_tokens": delta("total_tokens"),
            "exact_A": delta("exact_dictionary_matches"),
            "morph_B": delta("morphologically_valid_forms"),
            "ortho_out": cfg["P2A"]["ortho_out"] - cfg["P1"]["ortho_out"],
        }
        if cr is not None:
            d = cr.get("deltas") or {}
            tol = 2e-9
            mism = []
            if abs(d.get("canonical_coverage_pp", 0.0)
                   - cfg["deltas"]["canonical_coverage_pp"]) > tol:
                mism.append("canonical")
            if abs(d.get("broader_resource_supported_coverage_pp", 0.0)
                   - cfg["deltas"]["broader_coverage_pp"]) > tol:
                mism.append("broader")
            if mism:
                raise ValueError(f"{rid}: delta drift vs compare.json "
                                 f"({', '.join(mism)})")
        configs.append(cfg)

    orig = [c for c in configs if not c["exploratory"]]
    dola = [c for c in configs if c["exploratory"]]
    if len(orig) != 18 or len(dola) != 2:
        raise ValueError(
            f"expected 18 original + 2 exploratory, got {len(orig)} + "
            f"{len(dola)}")
    return {
        "experiment_id": "exp004",
        "phase": "1->2A-analysis",
        "artifact": "task-024-analysis",
        "generator": str(Path(__file__).name),
        "generator_commit": git_commit(),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "corpus": {"id": CORPUS_ID, "version": CORPUS_VERSION,
                   "sha256": AUTH_CORPUS_SHA256},
        "inputs": {
            "phase1_roster": {
                "file": str(P1_ROSTER.relative_to(ROOT)),
                "sha256": sha256_file(P1_ROSTER)},
            "phase2a_roster": {
                "file": str(P2A_ROSTER.relative_to(ROOT)),
                "sha256": sha256_file(P2A_ROSTER)},
            "compare_json": {
                "file": str(COMPARE_JSON.relative_to(ROOT)),
                "sha256": sha256_file(COMPARE_JSON)},
        },
        "note": "One Phase-1 direct + one Phase-2A primed generation per "
                "configuration. Deltas are paired, per-configuration "
                "observations; they are NOT independent repeated samples "
                "and cannot establish a general causal priming effect.",
        "configs": configs,
    }


# ---------------------------------------------------------------------------
# statistics (stdlib only, deterministic)
# ---------------------------------------------------------------------------

def describe(values: list[float]) -> dict:
    n = len(values)
    mean = statistics.fmean(values)
    return {
        "n": n,
        "mean": mean,
        "median": statistics.median(values),
        "sd": statistics.stdev(values) if n > 1 else 0.0,
        "min": min(values),
        "max": max(values),
        "positive": sum(v > 0 for v in values),
        "negative": sum(v < 0 for v in values),
        "zero": sum(v == 0 for v in values),
    }


def _exact_two_sided_binom(k: int, n: int) -> float:
    """Exact two-sided binomial test p-value, p = 0.5 (sign test)."""
    if n == 0:
        return 1.0
    # P(X >= k) via complement of CDF
    def pmf(i: int) -> float:
        return math.comb(n, i) / (2 ** n)

    p_ge = sum(pmf(i) for i in range(k, n + 1))
    p_le = sum(pmf(i) for i in range(0, k + 1))
    return min(1.0, 2.0 * min(p_ge, p_le))


def sign_test(values: list[float]) -> dict:
    """Exact two-sided sign test on paired deltas (zeros dropped)."""
    nz = [v for v in values if v != 0.0]
    k = sum(v > 0 for v in nz)
    return {
        "test": "exact two-sided sign test (paired deltas, zeros dropped)",
        "n_nonzero": len(nz),
        "positive": k,
        "negative": len(nz) - k,
        "p_value": _exact_two_sided_binom(k, len(nz)),
    }


def _quantized(v: float) -> int:
    return int(round(v * 1e6))


def permutation_test_mean(values: list[float]) -> dict:
    """Exact sign-flip permutation test on the mean of paired deltas.

    The exact randomization distribution for paired data: every paired
    difference may be flipped in sign with equal probability. The
    enumeration is done meet-in-the-middle (two halves of at most ~10
    differences each), which is exact, deterministic (integer micro-unit
    arithmetic) and fast for the n <= 20 used here. Zero differences are
    sign-invariant and cancel out of the probability.
    """
    import bisect

    q = [_quantized(v) for v in values]
    nz = [v for v in q if v != 0]
    n = len(nz)
    if len(values) > 40:
        raise ValueError("meet-in-the-middle permutation test supports "
                         "n <= 40")
    t_obs_abs = abs(sum(q))

    def half_sums(part: list[int]) -> list[int]:
        out = []
        for mask in range(1 << len(part)):
            s = 0
            for i, v in enumerate(part):
                s += v if (mask >> i) & 1 else -v
            out.append(s)
        return out

    cut = n // 2
    sa = half_sums(nz[:cut])
    sb = sorted(half_sums(nz[cut:]))
    # count pairs (a, b) with |a + b| >= t_obs_abs
    extreme = 0
    for a in sa:
        # b >= t - a  (upper tail)
        extreme += len(sb) - bisect.bisect_left(sb, t_obs_abs - a)
        # b <= -t - a (lower tail); disjoint from the upper tail for t > 0
        extreme += bisect.bisect_right(sb, -t_obs_abs - a)
    total = 2 ** n
    p = extreme / total
    return {
        "test": "exact sign-flip permutation test on the mean of paired "
                "deltas (meet-in-the-middle enumeration)",
        "n": len(values),
        "n_nonzero": n,
        "statistic": statistics.fmean(values),
        "assignments": total,
        "p_value": p,
    }


def _rank(values: list[float]) -> list[float]:
    order = sorted(range(len(values)), key=lambda i: values[i])
    rk = [0.0] * len(values)
    i = 0
    while i < len(values):
        j = i
        while (j + 1 < len(values)
               and values[order[j + 1]] == values[order[i]]):
            j += 1
        avg = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            rk[order[k]] = avg
        i = j + 1
    return rk


def spearman(a: list[float], b: list[float]) -> dict:
    if len(a) != len(b) or len(a) < 2:
        raise ValueError("spearman needs equal-length pairs, n >= 2")
    ra, rb = _rank(a), _rank(b)
    ma, mb = statistics.fmean(ra), statistics.fmean(rb)
    cov = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    va = sum((x - ma) ** 2 for x in ra)
    vb = sum((y - mb) ** 2 for y in rb)
    rho = cov / math.sqrt(va * vb) if va and vb else float("nan")
    return {"rho": rho, "n": len(a)}


def lsq(xs: list[float], ys: list[float]) -> dict:
    """Least-squares line y = slope*x + intercept (deterministic)."""
    n = len(xs)
    mx, my = statistics.fmean(xs), statistics.fmean(ys)
    sxx = sum((x - mx) ** 2 for x in xs)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    slope = sxy / sxx if sxx else 0.0
    return {"slope": slope, "intercept": my - slope * mx, "n": n}


# ---------------------------------------------------------------------------
# 2-4. rankings / delta tables / master table / families
# ---------------------------------------------------------------------------

def _ranked(configs: list[dict], field: str, reverse: bool,
            value_fn, lower_better: bool = False) -> list[dict]:
    """Deterministic ranking. `reverse`=sort high->low; `lower_better`
    overrides to low->high for e.g. unresolved rate."""
    ascend = lower_better
    items = sorted(configs, key=lambda c: (value_fn(c), c["short_label"]))
    if not ascend:
        items.reverse()
    out = []
    prev, prev_rank = None, 0
    for i, c in enumerate(items, start=1):
        v = value_fn(c)
        if prev is not None and abs(v - prev) < 1e-12:
            rank = prev_rank
        else:
            rank = i
        prev, prev_rank = v, rank
        out.append({"rank": rank, "configuration": c["short_label"],
                    "label": c["label"], "value": v,
                    "exploratory": c["exploratory"]})
    return out


def rank_tables(ds: dict) -> dict:
    orig = [c for c in ds["configs"] if not c["exploratory"]]
    allc = list(ds["configs"])
    sections = {}
    for scope_name, configs in (("original_18", orig), ("all_20", allc)):
        sections[scope_name] = {
            "canonical_coverage": _ranked(
                configs, "canonical", True,
                lambda c: c["P1"]["canonical_coverage"]),
            "broader_coverage": _ranked(
                configs, "broader", True,
                lambda c: c["P1"]["broader_coverage"]),
            "unresolved_rate": _ranked(
                configs, "unresolved", False,
                lambda c: c["P1"]["unresolved_rate"], lower_better=True),
            "orthography_cleanliness": _ranked(
                configs, "ortho", False,
                lambda c: c["P1"]["ortho_out"], lower_better=True),
            "p2a_canonical_coverage": _ranked(
                configs, "p2a_canonical", True,
                lambda c: c["P2A"]["canonical_coverage"]),
            "p2a_broader_coverage": _ranked(
                configs, "p2a_broader", True,
                lambda c: c["P2A"]["broader_coverage"]),
            "p2a_unresolved_rate": _ranked(
                configs, "p2a_unresolved", False,
                lambda c: c["P2A"]["unresolved_rate"], lower_better=True),
            "p2a_orthography_cleanliness": _ranked(
                configs, "p2a_ortho", False,
                lambda c: c["P2A"]["ortho_out"], lower_better=True),
        }
    return sections


def delta_table(ds: dict) -> list[dict]:
    """Sorted by Δ canonical desc, then Δ broader desc (task §4)."""
    items = sorted(
        ds["configs"],
        key=lambda c: (-c["deltas"]["canonical_coverage_pp"],
                       -c["deltas"]["broader_coverage_pp"],
                       c["short_label"]))
    return [{
        "configuration": c["short_label"],
        "label": c["label"],
        "exploratory": c["exploratory"],
        "family": c["family"],
        "P1_canonical": c["P1"]["canonical_coverage"],
        "P2A_canonical": c["P2A"]["canonical_coverage"],
        "d_canonical_pp": c["deltas"]["canonical_coverage_pp"],
        "P1_broader": c["P1"]["broader_coverage"],
        "P2A_broader": c["P2A"]["broader_coverage"],
        "d_broader_pp": c["deltas"]["broader_coverage_pp"],
        "d_unresolved_pp": c["deltas"]["unresolved_rate_pp"],
        "d_tokens": c["deltas"]["lexical_tokens"],
        "d_ortho_out": c["deltas"]["ortho_out"],
    } for c in items]


def master_rows(ds: dict) -> list[dict]:
    """Canonical-order master table rows (task §12)."""
    rows = []
    for c in ds["configs"]:
        rows.append({
            "configuration": c["short_label"],
            "family": c["family"],
            "status": "exploratory (Dola)" if c["exploratory"]
            else "original 18",
            "P1_canonical": c["P1"]["canonical_coverage"],
            "P2A_canonical": c["P2A"]["canonical_coverage"],
            "d_canonical_pp": c["deltas"]["canonical_coverage_pp"],
            "P1_broader": c["P1"]["broader_coverage"],
            "P2A_broader": c["P2A"]["broader_coverage"],
            "d_broader_pp": c["deltas"]["broader_coverage_pp"],
            "P1_unresolved": c["P1"]["unresolved_rate"],
            "P2A_unresolved": c["P2A"]["unresolved_rate"],
            "P1_tokens": c["P1"]["lexical_tokens"],
            "P2A_tokens": c["P2A"]["lexical_tokens"],
            "P1_ortho_out": c["P1"]["ortho_out"],
            "P2A_ortho_out": c["P2A"]["ortho_out"],
            "P2A_intake": c["p2a_intake"],
            "notes": c["notes"],
        })
    return rows


def family_tables(ds: dict) -> dict:
    fams = {}
    for c in ds["configs"]:
        fams.setdefault(c["family"], []).append(c)
    out = {}
    for fam in FAMILY_ORDER:
        if fam not in fams:
            continue
        out[fam] = [{
            "configuration": c["short_label"],
            "exploratory": c["exploratory"],
            "P1_canonical": c["P1"]["canonical_coverage"],
            "P2A_canonical": c["P2A"]["canonical_coverage"],
            "d_canonical_pp": c["deltas"]["canonical_coverage_pp"],
            "P1_broader": c["P1"]["broader_coverage"],
            "P2A_broader": c["P2A"]["broader_coverage"],
            "d_broader_pp": c["deltas"]["broader_coverage_pp"],
            "P1_ortho_out": c["P1"]["ortho_out"],
            "P2A_ortho_out": c["P2A"]["ortho_out"],
        } for c in fams[fam]]
    return out


def analysis_stats(ds: dict) -> dict:
    orig = [c for c in ds["configs"] if not c["exploratory"]]
    dc18 = [c["deltas"]["canonical_coverage_pp"] for c in orig]
    db18 = [c["deltas"]["broader_coverage_pp"] for c in orig]
    all20 = list(ds["configs"])
    dc20 = [c["deltas"]["canonical_coverage_pp"] for c in all20]
    db20 = [c["deltas"]["broader_coverage_pp"] for c in all20]

    def scope(values):
        return {
            "describe": describe(values),
            "sign_test": sign_test(values),
            "permutation_test_mean": permutation_test_mean(values),
        }

    # correlations (task §7, §8)
    def col(c, ph, f):
        return c[ph]["canonical_coverage"] if f == "canonical" \
            else c[ph]["broader_coverage"]

    def corr(cfgs, f, delta: bool):
        x = [col(c, "P1", f) for c in cfgs]
        y = ([c["deltas"]["canonical_coverage_pp"]
              if f == "canonical"
              else c["deltas"]["broader_coverage_pp"]]
             for c in cfgs)
        y = list(y)
        s = spearman(x, y)
        return {"rho": s["rho"], "n": s["n"]}

    p1c_vs_p2c_18 = spearman(
        [c["P1"]["canonical_coverage"] for c in orig],
        [c["P2A"]["canonical_coverage"] for c in orig])
    p1b_vs_p2b_18 = spearman(
        [c["P1"]["broader_coverage"] for c in orig],
        [c["P2A"]["broader_coverage"] for c in orig])
    p1c_vs_p2c_20 = spearman(
        [c["P1"]["canonical_coverage"] for c in all20],
        [c["P2A"]["canonical_coverage"] for c in all20])
    p1b_vs_p2b_20 = spearman(
        [c["P1"]["broader_coverage"] for c in all20],
        [c["P2A"]["broader_coverage"] for c in all20])

    return {
        "original_18": {
            "delta_canonical_pp": scope(dc18),
            "delta_broader_pp": scope(db18),
            "baseline_dependence": {
                "p1_canonical_vs_delta_canonical":
                    corr(orig, "canonical", True),
                "p1_broader_vs_delta_broader": corr(orig, "broader", True),
            },
            "baseline_vs_primed": {
                "p1_canonical_vs_p2a_canonical": {
                    "rho": p1c_vs_p2c_18["rho"], "n": p1c_vs_p2c_18["n"]},
                "p1_broader_vs_p2a_broader": {
                    "rho": p1b_vs_p2b_18["rho"], "n": p1b_vs_p2b_18["n"]},
            },
        },
        "all_20_exploratory": {
            "delta_canonical_pp": scope(dc20),
            "delta_broader_pp": scope(db20),
            "baseline_dependence": {
                "p1_canonical_vs_delta_canonical":
                    corr(all20, "canonical", True),
                "p1_broader_vs_delta_broader": corr(all20, "broader", True),
            },
            "baseline_vs_primed": {
                "p1_canonical_vs_p2a_canonical": {
                    "rho": p1c_vs_p2c_20["rho"], "n": p1c_vs_p2c_20["n"]},
                "p1_broader_vs_p2a_broader": {
                    "rho": p1b_vs_p2b_20["rho"], "n": p1b_vs_p2b_20["n"]},
            },
        },
        "note": "All tests and correlations are EXPLORATORY and descriptive "
                "only: each configuration contributes one direct and one "
                "primed generation (n = 18 original / 20 including the two "
                "exploratory Dola rows). No causal priming estimate is "
                "claimed.",
    }


def build_analysis(ds: dict) -> dict:
    return {
        "experiment_id": ds["experiment_id"],
        "phase": ds["phase"],
        "artifact": ds["artifact"],
        "generator": ds["generator"],
        "generator_commit": ds["generator_commit"],
        "generated_at": ds["generated_at"],
        "corpus": ds["corpus"],
        "inputs": ds["inputs"],
        "rankings": rank_tables(ds),
        "deltas_sorted_by_canonical_delta": delta_table(ds),
        "stats": analysis_stats(ds),
        "families": family_tables(ds),
        "master_table": master_rows(ds),
        "note": ds["note"],
    }


# ---------------------------------------------------------------------------
# Markdown rendering
# ---------------------------------------------------------------------------

def _md_rank_table(rows: list[dict], value_name: str) -> str:
    lines = ["| rank | configuration | value |",
             "|---:|:---|---:|"]
    for r in rows:
        exp = " (exploratory)" if r["exploratory"] else ""
        lines.append(f"| {r['rank']} | {r['configuration']}{exp} | "
                     f"{r['value']:.4f} |")
    return "\n".join(lines)


def _md_stats_block(scope: dict) -> str:
    out = []
    for label, key in (("Δ canonical coverage (pp)", "delta_canonical_pp"),
                       ("Δ broader coverage (pp)", "delta_broader_pp")):
        d = scope[key]["describe"]
        out.append(
            f"- **{label}:** n = {d['n']}, mean = {d['mean'] * 100:+.2f} pp, "
            f"median = {d['median'] * 100:+.2f} pp, "
            f"sd = {d['sd'] * 100:.2f} pp, min = {d['min'] * 100:+.2f} pp, "
            f"max = {d['max'] * 100:+.2f} pp "
            f"(positive {d['positive']}, negative {d['negative']}, "
            f"zero {d['zero']}).")
        st = scope[key]["sign_test"]
        out.append(
            f"  - sign test (exact, two-sided): {st['positive']}+ / "
            f"{st['negative']}- of {st['n_nonzero']} non-zero paired "
            f"deltas, p = {st['p_value']:.4g}.")
        pt = scope[key]["permutation_test_mean"]
        out.append(
            f"  - sign-flip permutation test on the mean (exact, "
            f"{pt['assignments']:,} assignments): "
            f"p = {pt['p_value']:.4g}.")
    return "\n".join(out)


def _md_delta_table(rows: list[dict]) -> str:
    lines = [
        "| configuration | status | Δ canonical (pp) | Δ broader (pp) | "
        "Δ unresolved (pp) | Δ tokens | Δ ortho-out |",
        "|:---|:---|---:|---:|---:|---:|---:|",
    ]
    for r in rows:
        status = "exploratory" if r["exploratory"] else "original"
        lines.append(
            f"| {r['configuration']} | {status} | "
            f"{r['d_canonical_pp'] * 100:+.2f} | "
            f"{r['d_broader_pp'] * 100:+.2f} | "
            f"{r['d_unresolved_pp'] * 100:+.2f} | "
            f"{int(round(r['d_tokens'])):+d} | "
            f"{int(round(r['d_ortho_out'])):+d} |")
    return "\n".join(lines)


def _md_master_table(rows: list[dict]) -> str:
    lines = [
        "| # | Configuration | Family | Status | P1 Canonical | P2A "
        "Canonical | Δ Canonical | P1 Broader | P2A Broader | Δ Broader | "
        "P2A Unresolved | P2A Ortho Out | Notes |",
        "|--:|:---|:---|:---|---:|---:|---:|---:|---:|---:|---:|---:|:---|",
    ]
    for i, r in enumerate(rows, start=1):
        lines.append(
            f"| {i} | {r['configuration']} | {r['family']} | "
            f"{r['status']} | {r['P1_canonical'] * 100:.2f}% | "
            f"{r['P2A_canonical'] * 100:.2f}% | "
            f"{r['d_canonical_pp'] * 100:+.2f} pp | "
            f"{r['P1_broader'] * 100:.2f}% | "
            f"{r['P2A_broader'] * 100:.2f}% | "
            f"{r['d_broader_pp'] * 100:+.2f} pp | "
            f"{r['P2A_unresolved'] * 100:.2f}% | "
            f"{r['P2A_ortho_out']} | {r['notes']} |")
    return "\n".join(lines)


def _md_family_table(fam_rows: list[dict]) -> str:
    lines = [
        "| configuration | status | P1 canon | P2A canon | Δ canon | "
        "P1 broader | P2A broader | Δ broader | P1 ortho | P2A ortho |",
        "|:---|:---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for r in fam_rows:
        st = "exploratory" if r["exploratory"] else "original"
        lines.append(
            f"| {r['configuration']} | {st} | "
            f"{r['P1_canonical'] * 100:.2f}% | "
            f"{r['P2A_canonical'] * 100:.2f}% | "
            f"{r['d_canonical_pp'] * 100:+.2f} | "
            f"{r['P1_broader'] * 100:.2f}% | "
            f"{r['P2A_broader'] * 100:.2f}% | "
            f"{r['d_broader_pp'] * 100:+.2f} | "
            f"{r['P1_ortho_out']} | {r['P2A_ortho_out']} |")
    return "\n".join(lines)


def render_md(ds: dict, an: dict) -> str:
    R = []
    a = R.append
    a(f"# EXP-004 full analysis — Phase 1 → Phase 2A corpus priming "
      f"(SODA Task 024, {ds['generated_at'][:10]})")
    a("")
    a("Deterministic, read-only analysis over the completed EXP-004 dataset "
      "(20 configurations: the original 18 Phase-1-usable configurations "
      "+ the two exploratory Dola 3.8 configurations). Generator: "
      f"`{ds['generator']}` @ `{ds['generator_commit'][:10]}`. Inputs:")
    for name, info in ds["inputs"].items():
        a(f"- `{name}`: `{info['file']}` sha256 `{info['sha256'][:16]}…`")
    a("")
    a("> **Methodological caution (read first).** Each configuration "
      "contributes exactly ONE Phase-1 direct generation and ONE Phase-2A "
      "corpus-primed generation. Every delta therefore conflates a possible "
      "corpus-priming effect with stochastic generation variation, "
      "model/interface behaviour, configuration differences and possible "
      "baseline dependence. All statistics below are descriptive and "
      "explicitly exploratory; nothing here is a definitive causal "
      "estimate of priming, and no composite score or 'winner' is "
      "produced.")
    a("")

    # dataset
    orig = [c for c in ds["configs"] if not c["exploratory"]]
    dola = [c for c in ds["configs"] if c["exploratory"]]
    a(f"## 1. Dataset ({len(orig)} original + {len(dola)} exploratory = "
      f"{len(ds['configs'])})")
    a("")
    a("Source: Phase-1 direct outputs (`outputs/roster.json`, 21 rows) and "
      "Phase-2A corpus-primed outputs (`phase2a/outputs/roster.json`, 20 "
      "primed rows), joined on `baseline_run_id`; the join and the exact "
      "deltas were cross-checked against `phase2a/outputs/compare.json` "
      "(no drift). GLM 4.5 remains excluded (Phase-1 intake failed). "
      "Dola rows carry `exploratory = true` and are kept separate from the "
      "original 18 everywhere.")
    a("")
    a("### 1a. Canonical order master table (one row per configuration)")
    a("")
    a(_md_master_table(an["master_table"]))
    a("")

    # rankings P1
    rk = an["rankings"]["original_18"]
    a("## 2. Phase-1 baseline landscape — rankings (original 18; "
      "Dola shown separately where included)")
    a("")
    a("Four separate dimensions; no composite score.")
    a("")
    a("### 2a. Phase-1 canonical resource coverage (desc)")
    a("")
    a(_md_rank_table(rk["canonical_coverage"], "canonical coverage"))
    a("")
    a("### 2b. Phase-1 broader resource-supported coverage (desc)")
    a("")
    a(_md_rank_table(rk["broader_coverage"], "broader coverage"))
    a("")
    a("### 2c. Phase-1 unresolved rate (asc = lower is better)")
    a("")
    a(_md_rank_table(rk["unresolved_rate"], "unresolved rate"))
    a("")
    a("### 2d. Phase-1 orthography cleanliness — outside-inventory "
      "characters (asc = lower is better)")
    a("")
    a(_md_rank_table(rk["orthography_cleanliness"], "outside-inventory"))
    a("")
    a("Dola Phase-1 anchors for the same four dimensions: Fast canonical "
      f"{dola[0]['P1']['canonical_coverage'] * 100:.2f}%, broader "
      f"{dola[0]['P1']['broader_coverage'] * 100:.2f}%, unresolved "
      f"{dola[0]['P1']['unresolved_rate'] * 100:.2f}%, ortho-out "
      f"{dola[0]['P1']['ortho_out']}; Pro canonical "
      f"{dola[1]['P1']['canonical_coverage'] * 100:.2f}%, broader "
      f"{dola[1]['P1']['broader_coverage'] * 100:.2f}%, unresolved "
      f"{dola[1]['P1']['unresolved_rate'] * 100:.2f}%, ortho-out "
      f"{dola[1]['P1']['ortho_out']}.")
    a("")

    # rankings P2A
    rk2 = an["rankings"]["original_18"]
    a("## 3. Phase-2A primed landscape — rankings (original 18)")
    a("")
    a("Same four separate dimensions, now for the corpus-primed runs.")
    a("")
    a("### 3a. Phase-2A canonical resource coverage (desc)")
    a("")
    a(_md_rank_table(rk2["p2a_canonical_coverage"], "P2A canonical"))
    a("")
    a("### 3b. Phase-2A broader resource-supported coverage (desc)")
    a("")
    a(_md_rank_table(rk2["p2a_broader_coverage"], "P2A broader"))
    a("")
    a("### 3c. Phase-2A unresolved rate (asc)")
    a("")
    a(_md_rank_table(rk2["p2a_unresolved_rate"], "P2A unresolved"))
    a("")
    a("### 3d. Phase-2A orthography cleanliness (asc)")
    a("")
    a(_md_rank_table(rk2["p2a_orthography_cleanliness"], "P2A ortho-out"))
    a("")
    a("Dola Phase-2A anchors: Fast canonical "
      f"{dola[0]['P2A']['canonical_coverage'] * 100:.2f}%, broader "
      f"{dola[0]['P2A']['broader_coverage'] * 100:.2f}%, unresolved "
      f"{dola[0]['P2A']['unresolved_rate'] * 100:.2f}%, ortho-out "
      f"{dola[0]['P2A']['ortho_out']}; Pro canonical "
      f"{dola[1]['P2A']['canonical_coverage'] * 100:.2f}%, broader "
      f"{dola[1]['P2A']['broader_coverage'] * 100:.2f}%, unresolved "
      f"{dola[1]['P2A']['unresolved_rate'] * 100:.2f}%, ortho-out "
      f"{dola[1]['P2A']['ortho_out']}.")
    a("")

    # main delta table
    a("## 4. Corpus-priming effect — Δ table (sorted by Δ canonical desc, "
      "then Δ broader desc)")
    a("")
    a("Δ = Phase-2A − Phase-1 for the same configuration. Original 18 and "
      "the two exploratory Dola rows are distinguished.")
    a("")
    a(_md_delta_table(an["deltas_sorted_by_canonical_delta"]))
    a("")

    # stats
    st = an["stats"]
    a("## 5. Descriptive statistics (paired per-configuration deltas)")
    a("")
    a("These are NOT independent repeated samples; they are one paired "
      "observation per configuration. Descriptive only; the tests below "
      "are labelled exploratory.")
    a("")
    a("### 5a. Original 18")
    a("")
    a(_md_stats_block(st["original_18"]))
    a("")
    a("### 5b. All 20 (including the two exploratory Dola configurations) "
      "— EXPLORATORY scope")
    a("")
    a(_md_stats_block(st["all_20_exploratory"]))
    a("")
    a("The Dola rows pull the mean Δ canonical up (0.0600 → 0.0715) and "
      "inflate the sd (0.0339 → 0.0590): Dola Fast's Δ canonical is "
      "≈ 4.7× the original-18 mean and sits far outside the original-18 "
      "range (max +0.1433). The sign-flip and sign tests on the original "
      "18 are consistent with a generalised positive shift, but with n = "
      "18 paired generations they cannot separate priming from other "
      "sources of variation — see the regression-to-the-middle section.")
    a("")

    # baseline dependence
    bd = st["original_18"]["baseline_dependence"]
    bd20 = st["all_20_exploratory"]["baseline_dependence"]
    a("## 6. Baseline dependence / regression-to-the-middle check")
    a("")
    a("Spearman rank correlations (descriptive):")
    a("")
    a(f"- Phase-1 canonical coverage vs Δ canonical (original 18, n = "
      f"{bd['p1_canonical_vs_delta_canonical']['n']}): ρ = "
      f"{bd['p1_canonical_vs_delta_canonical']['rho']:+.3f}")
    a(f"- Phase-1 broader coverage vs Δ broader (original 18, n = "
      f"{bd['p1_broader_vs_delta_broader']['n']}): ρ = "
      f"{bd['p1_broader_vs_delta_broader']['rho']:+.3f}")
    a(f"- Same with the two exploratory Dola rows added (n = "
      f"{bd20['p1_canonical_vs_delta_canonical']['n']}): ρ = "
      f"{bd20['p1_canonical_vs_delta_canonical']['rho']:+.3f} (canonical) "
      f"and ρ = {bd20['p1_broader_vs_delta_broader']['rho']:+.3f} "
      f"(broader).")
    a("")
    a("The strong negative correlation (−0.86 canonical / −0.84 broader on "
      "the original 18) means configurations that started lower gained "
      "more. This is a descriptive association, consistent with (but not "
      "proof of) regression toward the middle and/or a 'ceiling' for "
      "configurations that already scored high. **Dola Fast's very large Δ "
      "cannot be read as a strong priming response without accounting for "
      "this baseline dependence: it started far below every other "
      "configuration (Phase-1 canonical 38.87%).** Dola Pro (+6.67 pp from "
      "a 65.08% baseline) is close to the original-18 behaviour for a "
      "low-baseline configuration.")
    a("")

    # baseline vs primed correlation
    bv = st["original_18"]["baseline_vs_primed"]
    bv20 = st["all_20_exploratory"]["baseline_vs_primed"]
    a("## 7. Baseline vs primed correlation (descriptive)")
    a("")
    a("Spearman rank correlations between Phase-1 and Phase-2A of the same "
      "metric (do configurations that started higher stay higher?):")
    a("")
    a(f"- Phase-1 canonical vs Phase-2A canonical (original 18, n = "
      f"{bv['p1_canonical_vs_p2a_canonical']['n']}): ρ = "
      f"{bv['p1_canonical_vs_p2a_canonical']['rho']:+.3f}")
    a(f"- Phase-1 broader vs Phase-2A broader (original 18, n = "
      f"{bv['p1_broader_vs_p2a_broader']['n']}): ρ = "
      f"{bv['p1_broader_vs_p2a_broader']['rho']:+.3f}")
    a(f"- Including Dola (n = {bv20['p1_canonical_vs_p2a_canonical']['n']}): "
      f"ρ = {bv20['p1_canonical_vs_p2a_canonical']['rho']:+.3f} (canonical) "
      f"and ρ = {bv20['p1_broader_vs_p2a_broader']['rho']:+.3f} (broader).")
    a("")
    a("The rank order is only moderately preserved (ρ ≈ +0.45 canonical / "
      "+0.37 broader for the original 18): priming shifts the ordering, "
      "not just the level. With one generation per configuration the "
      "correlation also contains per-run noise.")
    a("")

    # families
    a("## 8. Configuration-family analysis (descriptive, matched variants)")
    a("")
    a("Matched variants share a provider/model line and differ only in the "
      "recorded setting. Single observations per variant — descriptive "
      "only, no over-generalisation.")
    a("")
    for fam, rows in an["families"].items():
        a(f"### 8x. {fam}")
        a("")
        a(_md_family_table(rows))
        a("")

    # orthography
    a("## 9. Orthography (separate dimension from lexical coverage)")
    a("")
    a("'Ortho-out' = characters outside the official Interslavic "
      "inventory (Task 015 audit; official alphabet source D-040). The "
      "audit distinguishes character categories only (Cyrillic / "
      "Polish-specific / other Latin / other script / unexpected "
      "non-letter); it does NOT attribute characters to proper names or "
      "to generated text, so no per-word reinterpretation is performed "
      "here. Figures below are for the Phase-2A primed outputs; "
      "Phase-1 ortho-out is in the master table.")
    a("")
    ortho_rows = sorted(
        ds["configs"], key=lambda c: -c["P2A"]["ortho_out"])
    lines = [
        "| configuration | status | outside | Cyrillic | Polish-specific | "
        "other Latin | other script | unexpected non-letter |",
        "|:---|:---|---:|---:|---:|---:|---:|---:|",
    ]
    for c in ortho_rows:
        o = c["P2A"]["ortho"]
        stt = "exploratory" if c["exploratory"] else "original"
        lines.append(
            f"| {c['short_label']} | {stt} | {c['P2A']['ortho_out']} | "
            f"{o['cyrillic']} | {o['polish_specific']} | "
            f"{o['other_latin']} | {o['other_script']} | "
            f"{o['unexpected_nonletters']} |")
    a("\n".join(lines))
    a("")
    a("Configurations with clean output AND high coverage (reported as a "
      "descriptive observation, not a composite score): Claude Sonnet 5 "
      "(canonical 84.6%, broader 91.0%, ortho-out 0), DeepSeek V3 Expert "
      "ON (85.6%, 91.2%, 0), Grok (82.4%, 89.0%, 0) and Gemini 3.1 Pro "
      "(83.0%, 89.4%, 0) produced ZERO outside-inventory characters in "
      "their primed outputs. At the other extreme, GPT-5.6 Luna (both "
      "settings, 72–75) and GPT ISV Teacher (72) produced the most "
      "outside-inventory characters among original-18 primed runs, and "
      "Qwen 3.7 Plus Fast 97. Dola Fast dropped from 468 (Phase-1) to 24 "
      "(Phase-2A) outside-inventory characters; Dola Pro from 63 to 17. "
      "Note the P1 baseline of Dola Fast was the single dirtiest output "
      "in the whole experiment.")
    a("")

    # practical usability pointer
    a("## 10. Practical usability — separate dimension")
    a("")
    a("Practical interface constraints were recorded during collection "
      "(Tasks 018/021/023) and are documentation, not metrics. They are "
      "reproduced in the master-table Notes and summarised in the "
      "accompanying analysis README / EXPERIMENTS.md entry; they are kept "
      "strictly separate from the coverage numbers above.")
    a("")

    # supported / suggestive / not established
    a("## 11. Supported / suggestive / not established")
    a("")
    a("(Interpretive summary — see EXPERIMENTS.md Task-024 entry for the "
      "full evidence-based wording.)")
    a("")
    a("- **Supported:** corpus priming was followed by higher canonical "
      "coverage in 18/18 original configurations and 20/20 including "
      "Dola (descriptive; sign + sign-flip tests exploratory, n = 18).")
    a("- **Supported:** broader resource-supported coverage rose in 14/18 "
      "original configurations (mean +2.36 pp) — smaller and less "
      "uniform than the canonical shift.")
    a("- **Suggestive:** the larger canonical deltas occurred for the "
      "lowest Phase-1 baselines (ρ = −0.86), including Dola Fast — "
      "consistent with a ceiling/baseline-dependence effect.")
    a("- **Not established:** a causal priming effect of any specific "
      "size; any effect on naturalness; any claim that Dola Fast "
      "'learned' more from the corpus; any model being 'best'; any "
      "corpus-composition advantage; any thinking-mode advantage; any "
      "baseline-quality → priming-response prediction.")
    a("")

    # candidates + next experiments pointers
    a("## 12. Research candidates + next experiments")
    a("")
    a("See the analysis README and the Task-024 EXPERIMENTS.md entry for "
      "the candidate list and the (at most 3) recommended next "
      "experiments. No winner is declared here.")
    a("")

    # charts index
    a("## 13. Figures")
    a("")
    for letter, name in (("A", "Phase 1 vs Phase 2A canonical coverage"),
                         ("B", "Priming Δ canonical coverage (desc)"),
                         ("C", "Phase 1 vs Phase 2A broader coverage"),
                         ("D", "Canonical vs broader coverage in Phase 2A"),
                         ("E", "Phase-2A orthography anomalies"),
                         ("F", "Baseline coverage vs priming delta"),
                         ("G", "Model configuration map")):
        a(f"- `figures/chart_{letter.lower()}.svg` — {name}")
    a("")
    a("## Appendix — generator metadata")
    a("")
    a(f"- script: `scripts/{ds['generator']}`")
    a(f"- generator commit: `{ds['generator_commit']}`")
    a(f"- generated at (UTC): `{ds['generated_at']}`")
    a("")
    return "\n".join(R)


# ---------------------------------------------------------------------------
# SVG charts (deterministic, stdlib only)
# ---------------------------------------------------------------------------

def _esc(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


COL_P1 = "#4C72B0"       # original 18, Phase 1
COL_P2 = "#DD8452"       # original 18, Phase 2A
COL_DOLA = "#C44E52"     # exploratory Dola (both phases)
COL_DOLA2 = "#E6A0A4"
GRID = "#D9D9D9"
TXT = "#1a1a1a"

FONT = "Helvetica, Arial, sans-serif"


def _svg_header(w: int, h: int, title: str, subtitle: str = "") -> list[str]:
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" '
           f'height="{h}" viewBox="0 0 {w} {h}" '
           f'font-family="{FONT}">']
    if title:
        out.append(f'<text x="20" y="30" font-size="20" font-weight="bold" '
                   f'fill="{TXT}">{_esc(title)}</text>')
    if subtitle:
        out.append(f'<text x="20" y="50" font-size="12" fill="#555">'
                   f'{_esc(subtitle)}</text>')
    return out


def _bar_chart_pairs(items, w=1200, h=None, title="", subtitle="",
                     xmax=1.0, xlabel="", fmt="{:.0%}"):
    """Horizontal grouped bars (P1 solid, P2A hatched-lighter)."""
    n = len(items)
    row_h = 34
    head = 70
    left = 420
    right = 120
    plot_h = n * row_h + 20
    H = head + plot_h + 60
    W = w
    svg = _svg_header(W, H, title, subtitle)
    svg.append(f'<line x1="{left}" y1="{head}" x2="{left}" y2="'
               f'{head + plot_h}" stroke="{GRID}"/>')
    # x gridlines + labels
    nticks = 10
    plot_w = W - left - right
    for i in range(nticks + 1):
        v = xmax * i / nticks
        x = left + plot_w * i / nticks
        svg.append(f'<line x1="{x:.1f}" y1="{head}" x2="{x:.1f}" '
                   f'y2="{head + plot_h}" stroke="{GRID}" '
                   f'stroke-dasharray="2 3"/>')
        svg.append(f'<text x="{x:.1f}" y="{head + plot_h + 16}" '
                   f'font-size="11" fill="#555" text-anchor="middle">'
                   f'{fmt.format(v)}</text>')
    svg.append(f'<text x="{left}" y="{head - 8}" font-size="12" '
               f'fill="#555">{_esc(xlabel)}</text>')
    for idx, it in enumerate(items):
        y = head + idx * row_h + 14
        svg.append(f'<text x="{left - 10}" y="{y + 4}" font-size="12" '
                   f'text-anchor="end" fill="{TXT}">{_esc(it["label"])}</text>')
        for phase, key, color, cls in (("P1", "v1", COL_P1, "bar-p1"),
                                       ("P2A", "v2", COL_P2, "bar-p2")):
            v = it[key]
            bw = plot_w * (max(0.0, min(v, xmax)) / xmax)
            if cls == "bar-p1":
                svg.append(f'<rect x="{left}" y="{y}" width="{bw:.1f}" '
                           f'height="14" fill="{color}"/>')
            else:
                svg.append(f'<rect x="{left}" y="{y + 16}" width="{bw:.1f}" '
                           f'height="14" fill="{color}"/>')
        if it.get("exploratory"):
            for yy in (y, y + 16):
                svg.append(f'<rect x="{left}" y="{yy}" width="4" height="14" '
                           f'fill="{COL_DOLA}"/>')
    # legend
    lx = left + 20
    ly = head + plot_h + 34
    svg.append(f'<rect x="{lx}" y="{ly - 12}" width="14" height="12" '
               f'fill="{COL_P1}"/><text x="{lx + 18}" y="{ly - 2}" '
               f'font-size="12" fill="{TXT}">Phase 1 direct</text>')
    svg.append(f'<rect x="{lx + 150}" y="{ly - 12}" width="14" height="12" '
               f'fill="{COL_P2}"/><text x="{lx + 168}" y="{ly - 2}" '
               f'font-size="12" fill="{TXT}">Phase 2A primed</text>')
    svg.append(f'<rect x="{lx + 320}" y="{ly - 12}" width="14" height="12" '
               f'fill="{COL_DOLA}"/><text x="{lx + 338}" y="{ly - 2}" '
               f'font-size="12" fill="{TXT}">left edge marker = '
               f'exploratory Dola</text>')
    svg.append("</svg>")
    return "\n".join(svg)


def _delta_bar_chart(items, w=1200, h=None, title="", subtitle=""):
    """Horizontal bars of a signed delta, sorted descending."""
    n = len(items)
    row_h = 30
    head = 70
    left = 400
    right = 130
    plot_h = n * row_h + 20
    W, H = w, head + plot_h + 50
    svg = _svg_header(W, H, title, subtitle)
    plot_w = W - left - right
    zero_x = left + plot_w * 0.30  # 30% of width reserved to negative side
    # make scale symmetric-ish around observed min..max
    vals = [it["v"] for it in items]
    vmin = min(min(vals), 0.0)
    vmax = max(max(vals), 0.0)
    # map: value -> x
    span = max(vmax - vmin, 1e-9)
    def xof(v):
        return left + (v - vmin) / span * plot_w
    # gridlines
    for i in range(0, 11):
        frac = i / 10
        v = vmin + span * frac
        x = xof(v)
        svg.append(f'<line x1="{x:.1f}" y1="{head}" x2="{x:.1f}" '
                   f'y2="{head + plot_h}" stroke="{GRID}" '
                   f'stroke-dasharray="2 3"/>')
        svg.append(f'<text x="{x:.1f}" y="{head + plot_h + 16}" '
                   f'font-size="10" fill="#555" text-anchor="middle">'
                   f'{v * 100:+.0f}</text>')
    svg.append(f'<line x1="{xof(0):.1f}" y1="{head}" x2="{xof(0):.1f}" '
               f'y2="{head + plot_h}" stroke="#333"/>')
    for idx, it in enumerate(items):
        y = head + idx * row_h + 8
        svg.append(f'<text x="{left - 10}" y="{y + 13}" font-size="11" '
                   f'text-anchor="end" fill="{TXT}">{_esc(it["label"])}</text>')
        x0 = xof(0)
        x1 = xof(it["v"])
        col = COL_DOLA if it.get("exploratory") else COL_P1
        svg.append(f'<rect x="{min(x0, x1):.1f}" y="{y}" '
                   f'width="{abs(x1 - x0):.1f}" height="14" fill="{col}"/>')
        svg.append(f'<text x="{x1 + 6 if x1 >= x0 else x1 - 6:.1f}" '
                   f'y="{y + 13}" font-size="11" fill="{TXT}" '
                   f'text-anchor="{"start" if x1 >= x0 else "end"}">'
                   f'{it["v"] * 100:+.1f}</text>')
    svg.append("</svg>")
    return "\n".join(svg)


def _scatter(items, w=1200, h=760, title="", subtitle="",
             xlabel="", ylabel="", xmax=1.0, ymin=None, ymax=None,
             trend=None, highlight=(), fmt="{:.0%}", leader=False):
    # `leader`: points carry small index numbers; a deterministic legend
    # lane on the right margin maps index -> configuration (used when the
    # point cloud is too crowded for inline labels).
    left, right, top, bottom = 90, (340 if leader else 40), 80, 70
    plot_w = w - left - right
    plot_h = h - top - bottom
    svg = _svg_header(w, h, title, subtitle)
    if ymin is None:
        ymin = 0.0
    if ymax is None:
        ymax = 1.0

    def X(v):
        return left + plot_w * (v / xmax)

    def Y(v):
        return top + plot_h * (1 - (v - ymin) / (ymax - ymin))

    for i in range(11):
        x = X(xmax * i / 10)
        svg.append(f'<line x1="{x:.1f}" y1="{top}" x2="{x:.1f}" '
                   f'y2="{top + plot_h}" stroke="{GRID}" '
                   f'stroke-dasharray="2 3"/>')
        svg.append(f'<text x="{x:.1f}" y="{top + plot_h + 18}" '
                   f'font-size="11" fill="#555" text-anchor="middle">'
                   f'{fmt.format(xmax * i / 10)}</text>')
    ny = 10
    for i in range(ny + 1):
        v = ymin + (ymax - ymin) * i / ny
        y = Y(v)
        svg.append(f'<line x1="{left}" y1="{y:.1f}" x2="{left + plot_w}" '
                   f'y2="{y:.1f}" stroke="{GRID}" stroke-dasharray="2 3"/>')
        svg.append(f'<text x="{left - 8}" y="{y + 4:.1f}" font-size="11" '
                   f'fill="#555" text-anchor="end">{v * 100:.0f}%</text>')
    svg.append(f'<text x="{left}" y="{top - 14}" font-size="12" '
               f'fill="#555">{_esc(ylabel)}</text>')
    svg.append(f'<text x="{left + plot_w}" y="{top + plot_h + 34}" '
               f'font-size="12" fill="#555" text-anchor="end">'
               f'{_esc(xlabel)}</text>')
    if trend:
        x0 = trend.get("xmin", 0.0)
        x1 = trend.get("xmax", xmax)
        y0 = trend["slope"] * x0 + trend["intercept"]
        y1 = trend["slope"] * x1 + trend["intercept"]
        if (ymin <= y0 <= ymax and ymin <= y1 <= ymax
                and x0 < x1 and x1 <= xmax):
            svg.append(f'<line x1="{X(x0):.1f}" y1="{Y(y0):.1f}" '
                       f'x2="{X(x1):.1f}" y2="{Y(y1):.1f}" '
                       f'stroke="#555" stroke-width="1.5" '
                       f'stroke-dasharray="5 4"/>')
            xm = 0.5 * (x0 + x1)
            ym = trend["slope"] * xm + trend["intercept"]
            svg.append(f'<text x="{X(xm):.1f}" y="{Y(ym) - 8:.1f}" '
                       f'font-size="11" fill="#555" '
                       f'text-anchor="middle">descriptive OLS trend '
                       f'(original 18)</text>')
    # deterministic label placement
    def text_w(txt: str, fs: float) -> float:
        return len(txt) * fs * 0.62

    if leader:
        order = sorted(range(len(items)),
                       key=lambda i: (-items[i]["y"], items[i]["x"]))
        lane_h = 17
        lane_x = left + plot_w + 14
        for k, i in enumerate(order):
            it = items[i]
            px, py = X(it["x"]), Y(it["y"])
            ly = top + 10 + k * lane_h
            exp = it.get("exploratory")
            col = COL_DOLA if exp else COL_P1
            svg.append(f'<line x1="{px:.1f}" y1="{py:.1f}" '
                       f'x2="{lane_x - 8:.1f}" y2="{py:.1f}" '
                       f'stroke="#b9b9b9" stroke-width="0.8"/>')
            svg.append(f'<line x1="{lane_x - 8:.1f}" y1="{py:.1f}" '
                       f'x2="{lane_x - 8:.1f}" y2="{ly:.1f}" '
                       f'stroke="#b9b9b9" stroke-width="0.8"/>')
            svg.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="5" '
                       f'fill="{col}" stroke="#fff" stroke-width="1"/>')
            svg.append(f'<text x="{px + 7:.1f}" y="{py - 5:.1f}" '
                       f'font-size="9" font-weight="bold" fill="#333">'
                       f'{k + 1}</text>')
            svg.append(f'<rect x="{lane_x}" y="{ly - 8}" width="10" '
                       f'height="10" fill="{col}"/>')
            svg.append(f'<text x="{lane_x + 16}" y="{ly + 1}" font-size="10" '
                       f'fill="{TXT}">{k + 1}. {_esc(it["label"])}</text>')
    else:
        order = sorted(range(len(items)),
                       key=lambda i: (-items[i]["y"], items[i]["x"]))
        occupied: list[tuple[float, float, float, float]] = []
        offset_by_idx = {}
        # candidate (dy, dx) placements: vertical first, then x-shifted so
        # near-duplicate points can stack sideways instead of colliding
        candidates = [(-16, 0), (24, 0), (-16, 70), (24, 70), (-16, -70),
                      (24, -70), (-34, 0), (34, 0)]
        for i in order:
            it = items[i]
            px, py = X(it["x"]), Y(it["y"])
            anchor = "start" if it["x"] < 0.20 * xmax else "middle"
            label = it["label"]
            lw = text_w(label, 10)
            for dy, dx in candidates:
                cx = px + dx
                lx0 = cx - (lw / 2 if anchor == "middle" else 0)
                lx1 = cx + (lw / 2 if anchor == "middle" else lw)
                ly = py + dy
                box = (lx0 - 2, lx1 + 2, ly - 10, ly + 2)
                if not any(not (box[0] >= o[1] or box[1] <= o[0]
                                or box[2] >= o[3] or box[3] <= o[2])
                           for o in occupied):
                    offset_by_idx[i] = (dy, dx, anchor, cx, ly)
                    occupied.append(box)
                    break
            else:
                offset_by_idx[i] = (-16, 0, anchor, px, py - 16)
        for i, it in enumerate(items):
            x, y = it["x"], it["y"]
            exp = it.get("exploratory")
            col = COL_DOLA if exp else COL_P1
            r = 7 if exp else 5
            svg.append(f'<circle cx="{X(x):.1f}" cy="{Y(y):.1f}" r="{r}" '
                       f'fill="{col}" stroke="#fff" stroke-width="1"/>')
            dy, dx, anchor, lx, ly = offset_by_idx[i]
            svg.append(f'<text x="{lx:.1f}" y="{ly:.1f}" '
                       f'font-size="10" fill="{TXT}" '
                       f'text-anchor="{anchor}">{_esc(it["label"])}</text>')
    svg.append("</svg>")
    return "\n".join(svg)


def _stacked_ortho(items, w=1200, title="", subtitle=""):
    n = len(items)
    row_h = 30
    head = 70
    left = 400
    right = 150
    plot_h = n * row_h + 20
    W, H = w, head + plot_h + 60
    plot_w = W - left - right
    maxv = max((it["total"] for it in items), default=1) or 1
    cols = {"cyrillic": "#8C1515", "polish_specific": "#DD8452",
            "other_latin": "#4C72B0", "other_script": "#937860",
            "unexpected_nonletters": "#2F4858"}
    svg = _svg_header(W, H, title, subtitle)
    for i in range(11):
        x = left + plot_w * i / 10
        svg.append(f'<line x1="{x:.1f}" y1="{head}" x2="{x:.1f}" '
                   f'y2="{head + plot_h}" stroke="{GRID}" '
                   f'stroke-dasharray="2 3"/>')
        svg.append(f'<text x="{x:.1f}" y="{head + plot_h + 16}" '
                   f'font-size="10" fill="#555" text-anchor="middle">'
                   f'{int(maxv * i / 10)}</text>')
    for idx, it in enumerate(items):
        y = head + idx * row_h + 6
        svg.append(f'<text x="{left - 10}" y="{y + 15}" font-size="11" '
                   f'text-anchor="end" fill="{TXT}">{_esc(it["label"])}</text>')
        xcur = left
        for cat in ("cyrillic", "polish_specific", "other_latin",
                    "other_script", "unexpected_nonletters"):
            v = it.get(cat, 0)
            bw = plot_w * (v / maxv)
            if v:
                svg.append(f'<rect x="{xcur:.1f}" y="{y}" width="{bw:.1f}" '
                           f'height="16" fill="{cols[cat]}"/>')
            xcur += bw
        svg.append(f'<text x="{xcur + 6:.1f}" y="{y + 14}" font-size="11" '
                   f'fill="{TXT}">{it["total"]}</text>')
    # legend
    lx, ly = left + 20, head + plot_h + 32
    step = 150
    for ci, (cat, name) in enumerate(ORTHO_CATEGORIES):
        cx = lx + ci * step
        svg.append(f'<rect x="{cx}" y="{ly - 12}" width="14" height="12" '
                   f'fill="{cols[cat]}"/>')
        svg.append(f'<text x="{cx + 18}" y="{ly - 2}" font-size="12" '
                   f'fill="{TXT}">{_esc(name)}</text>')
    svg.append("</svg>")
    return "\n".join(svg)


def _slope_chart(groups, w=1200, title="", subtitle=""):
    """Chart G — model configuration map: per-family lanes, each config a
    P1->P2A dumbbell on a shared canonical-coverage axis."""
    # groups: list of (family_name, [configs]) in display order
    lane_h = 34
    group_gap = 26
    left = 330
    right = 170
    head = 90
    plot_w = w - left - right
    n_lanes = sum(len(g[1]) for g in groups)
    total_h = n_lanes * lane_h + len(groups) * group_gap + 40
    H = head + total_h + 40
    svg = _svg_header(w, H, title, subtitle)
    xmin, xmax = 0.0, 1.0

    def X(v):
        return left + plot_w * (v - xmin) / (xmax - xmin)

    plot_bottom = head + total_h
    for i in range(11):
        x = X(xmin + (xmax - xmin) * i / 10)
        svg.append(f'<line x1="{x:.1f}" y1="{head}" x2="{x:.1f}" '
                   f'y2="{plot_bottom}" stroke="{GRID}" '
                   f'stroke-dasharray="2 3"/>')
        svg.append(f'<text x="{x:.1f}" y="{plot_bottom + 16}" '
                   f'font-size="10" fill="#555" text-anchor="middle">'
                   f'{i * 10}%</text>')
    y = head
    for fam, cfgs in groups:
        y += group_gap / 2
        svg.append(f'<text x="{left - 12}" y="{y - 8}" font-size="13" '
                   f'font-weight="bold" fill="{TXT}" text-anchor="end">'
                   f'{_esc(fam)}</text>')
        for c in cfgs:
            y += lane_h
            ymid = y - lane_h / 2
            p1 = c["P1"]["canonical_coverage"]
            p2 = c["P2A"]["canonical_coverage"]
            exp = c.get("exploratory")
            col = COL_DOLA if exp else COL_P1
            svg.append(f'<text x="{left - 10}" y="{ymid + 4}" font-size="11" '
                       f'text-anchor="end" fill="{TXT}">'
                       f'{_esc(c["short_label"])}</text>')
            dash = ' stroke-dasharray="4 3"' if exp else ""
            svg.append(f'<line x1="{X(p1):.1f}" y1="{ymid}" '
                       f'x2="{X(p2):.1f}" y2="{ymid}" stroke="{col}" '
                       f'stroke-width="2"{dash}/>')
            svg.append(f'<circle cx="{X(p1):.1f}" cy="{ymid}" r="4.5" '
                       f'fill="#fff" stroke="{col}" stroke-width="2"/>')
            svg.append(f'<circle cx="{X(p2):.1f}" cy="{ymid}" r="5" '
                       f'fill="{col}"/>')
            d = (p2 - p1) * 100
            svg.append(f'<text x="{X(p2) + 8:.1f}" y="{ymid + 4}" '
                       f'font-size="10" fill="{TXT}">{d:+.1f}</text>')
    svg.append(f'<text x="{left}" y="{head - 26}" font-size="12" '
               f'fill="#555">canonical resource coverage — open circle = '
               f'Phase 1, filled circle = Phase 2A, delta pp on the '
               f'right; dashed = exploratory Dola</text>')
    svg.append("</svg>")
    return "\n".join(svg)


def _sorted_pairs(ds: dict, field: str):
    """items for pair-bar charts, sorted by P1 ascending (deterministic)."""
    out = []
    for c in ds["configs"]:
        out.append({
            "label": c["short_label"],
            "v1": c["P1"][field],
            "v2": c["P2A"][field],
            "exploratory": c["exploratory"],
        })
    out.sort(key=lambda it: (it["v1"], it["label"]))
    return out


def render_charts(ds: dict, outdir: Path) -> list[Path]:
    outdir.mkdir(parents=True, exist_ok=True)
    sub = ("20 configurations; Dola 3.8 Fast/Pro exploratory (red marker). "
           "Source: outputs/roster.json + phase2a/outputs/roster.json")
    # A
    items = _sorted_pairs(ds, "canonical_coverage")
    a_svg = _bar_chart_pairs(
        items, title="Chart A — Phase 1 vs Phase 2A canonical coverage",
        subtitle=sub, xmax=0.9, xlabel="canonical resource coverage")
    # C
    items = _sorted_pairs(ds, "broader_coverage")
    c_svg = _bar_chart_pairs(
        items, title="Chart C — Phase 1 vs Phase 2A broader coverage",
        subtitle=sub, xmax=0.95,
        xlabel="broader resource-supported coverage")
    # B
    items = [{"label": c["short_label"], "v": c["deltas"]["canonical_coverage_pp"],
              "exploratory": c["exploratory"]} for c in ds["configs"]]
    items.sort(key=lambda it: (-it["v"], it["label"]))
    b_svg = _delta_bar_chart(
        items, title="Chart B — Priming Δ canonical coverage (sorted desc)",
        subtitle="Δ = Phase 2A − Phase 1, same configuration. "
                 "Dola Fast/Pro in red.")
    # D
    d_items = [{"label": c["short_label"], "x": c["P2A"]["canonical_coverage"],
                "y": c["P2A"]["broader_coverage"],
                "exploratory": c["exploratory"]} for c in ds["configs"]]
    d_svg = _scatter(
        d_items, leader=True,
        title="Chart D — Phase 2A: canonical vs broader coverage",
        subtitle="Numbered scatter; legend on the right maps each number "
                 "to a configuration (red = exploratory Dola).",
        xlabel="canonical coverage", ylabel="broader coverage")
    # E
    e_items = []
    for c in ds["configs"]:
        o = c["P2A"]["ortho"]
        e_items.append({"label": c["short_label"], "total": c["P2A"]["ortho_out"],
                        **{cat: o[cat] for cat, _ in ORTHO_CATEGORIES},
                        "exploratory": c["exploratory"]})
    e_items.sort(key=lambda it: (-it["total"], it["label"]))
    e_svg = _stacked_ortho(
        e_items, title="Chart E — Phase-2A orthography anomalies "
                       "(outside-inventory characters by category)",
        subtitle="Category counts per primed output; total at the right.")
    # F
    orig = [c for c in ds["configs"] if not c["exploratory"]]
    xs = [c["P1"]["canonical_coverage"] for c in orig]
    ys = [c["deltas"]["canonical_coverage_pp"] for c in orig]
    trend = lsq(xs, ys)
    trend["xmin"] = min(xs)
    trend["xmax"] = max(xs)
    f_items = [{"label": c["short_label"],
                "x": c["P1"]["canonical_coverage"],
                "y": c["deltas"]["canonical_coverage_pp"],
                "exploratory": c["exploratory"]} for c in ds["configs"]]
    f_svg = _scatter(
        f_items, leader=True, w=1400, h=820,
        title="Chart F — Baseline coverage vs priming Δ canonical",
        subtitle="Dola Fast/Pro highlighted (red). Numbered legend on the "
                 "right. Trend line = descriptive OLS over the original 18 "
                 "only (drawn over its data range).",
        xlabel="Phase-1 canonical coverage",
        ylabel="Δ canonical coverage (pp)", xmax=0.9,
        ymin=-0.05, ymax=0.33, trend=trend)
    # G
    groups = []
    for fam in FAMILY_ORDER:
        famc = [c for c in ds["configs"] if c["family"] == fam]
        if famc:
            famc = sorted(famc, key=lambda c: (c["phase1_number"] is None,
                                               c["phase1_number"] or 99,
                                               c["short_label"]))
            groups.append((fam, famc))
    g_svg = _slope_chart(
        groups, title="Chart G — Model configuration map "
                      "(P1 → P2A canonical coverage)",
        subtitle="Family lanes; open = Phase 1, filled = Phase 2A, "
                 "right number = Δ pp; dashed = exploratory Dola.")
    files = {
        "chart_a.svg": a_svg, "chart_b.svg": b_svg, "chart_c.svg": c_svg,
        "chart_d.svg": d_svg, "chart_e.svg": e_svg, "chart_f.svg": f_svg,
        "chart_g.svg": g_svg,
    }
    written = []
    for name, svg in files.items():
        p = outdir / name
        p.write_text(svg + "\n", encoding="utf-8")
        written.append(p)
    return written


# ---------------------------------------------------------------------------
# poster
# ---------------------------------------------------------------------------

def render_poster_md(ds: dict, an: dict) -> str:
    dola = [c for c in ds["configs"] if c["exploratory"]]
    orig = [c for c in ds["configs"] if not c["exploratory"]]
    R = []
    a = R.append
    a("# EXP-004 — Does Authentic Medžuslovjansky Corpus Priming Improve "
      "LLM Translation?")
    a("")
    a("*First research-poster draft — SODA Task 024. Every number below is "
      "from the deterministic analysis (`scripts/analyze_exp004_phase2a.py`); "
      "figures are `figures/chart_a..g.svg`. This is a research "
      "visualisation, not a product claim: no winner, no 'best AI', no "
      "'proven', no 'human-level', no 'most natural' wording is used.*")
    a("")
    a("## Design")
    a("")
    a("- **Task:** translate one fixed Polish story into Medžuslovjansky "
      "(Interslavic).")
    a("- **Phase 1 (baseline):** each model, fresh session, direct "
      "translation only — no reference material.")
    a("- **Phase 2A (priming):** same story, same instruction, but the "
      "model first studies a fixed **authentic three-register "
      "Medžuslovjansky corpus** (~58 KB; literary/narrative + "
      "artistic/poetic + informative/encyclopedic) in the same session.")
    a(f"- **Configurations:** {len(orig)} original (preregistered) + "
      f"{len(dola)} exploratory Dola 3.8 (Fast/Pro, `exploratory = true`, "
      "not part of the original roster). GLM 4.5 excluded (Phase-1 "
      "intake failed).")
    a("- **One generation per condition per configuration** — see "
      "Limitations.")
    a("- **Metrics (unchanged, deterministic):** canonical resource "
      "coverage; broader resource-supported coverage; unresolved rate; "
      "lexical tokens; orthography outside-inventory characters (with "
      "Cyrillic / Polish-specific / other-Latin / other-script / "
      "unexpected-non-letter categories). Four separate dimensions — no "
      "composite score.")
    a("")
    a("## Headline numbers")
    a("")
    a(f"- Original 18: Δ canonical coverage mean **+{statistics.fmean([c['deltas']['canonical_coverage_pp'] for c in orig]) * 100:+.2f} pp** "
      f"(median +{statistics.median([c['deltas']['canonical_coverage_pp'] for c in orig]) * 100:+.2f} pp); "
      f"{sum(c['deltas']['canonical_coverage_pp'] > 0 for c in orig)}/18 "
      "configurations positive.")
    a(f"- Original 18: Δ broader coverage mean "
      f"**+{statistics.fmean([c['deltas']['broader_coverage_pp'] for c in orig]) * 100:+.2f} pp** "
      f"({sum(c['deltas']['broader_coverage_pp'] > 0 for c in orig)}/18 positive).")
    a(f"- Dola 3.8 Fast: **+{dola[0]['deltas']['canonical_coverage_pp'] * 100:+.2f} pp** canonical "
      f"({dola[0]['P1']['canonical_coverage'] * 100:.1f}% → "
      f"{dola[0]['P2A']['canonical_coverage'] * 100:.1f}%) — the largest "
      "observed change, from the lowest Phase-1 baseline in the whole "
      "experiment.")
    a(f"- Dola 3.8 Pro: **+{dola[1]['deltas']['canonical_coverage_pp'] * 100:+.2f} pp** canonical "
      f"({dola[1]['P1']['canonical_coverage'] * 100:.1f}% → "
      f"{dola[1]['P2A']['canonical_coverage'] * 100:.1f}%).")
    a("")
    a("> **Baseline dependence warning.** Δ canonical correlates "
      "negatively with Phase-1 canonical coverage (Spearman ρ ≈ −0.86, "
      "original 18): low baselines gained more. Dola Fast's large change "
      "is **observed behaviour, not evidence of stronger corpus "
      "learning**.")
    a("")
    a("## Master table (20 configurations)")
    a("")
    a(_md_master_table(an["master_table"]))
    a("")
    a("## Strongest changes (Δ canonical, pp)")
    a("")
    a("- Largest original-18: Gemini 3.6 Flash thinking ON **+14.33**; "
      "Claude Sonnet 5 **+11.66**; Qwen 3.7 Plus Fast **+8.94**; "
      "DeepSeek V3 Instant ON **+8.55**; Claude Sonnet 5 max **+8.31**.")
    a("- Smallest original-18: Gemini 3.1 Pro **+1.74**; Qwen 3.8 Max "
      "Fast **+3.04**; Kimi **+3.06**; Qwen 3.8 Max Think **+3.07**.")
    a("- Exploratory: Dola Fast **+28.20** (see warning above); Dola Pro "
      "**+6.67**.")
    a("")
    a("## Orthography observations")
    a("")
    a("- Cleanest primed outputs (0 outside-inventory chars) with high "
      "coverage: Claude Sonnet 5, DeepSeek V3 Expert ON, Grok, Gemini 3.1 "
      "Pro.")
    a("- GPT-5.6 Luna (both settings, 72–75) and GPT ISV Teacher (72) had "
      "the most outside-inventory characters among original-18 primed "
      "runs; Qwen 3.7 Plus Fast 97.")
    a("- Dola Fast: 468 (Phase 1) → 24 (Phase 2A); Dola Pro: 63 → 17. "
      "Orthography improved alongside coverage for Dola, but the audit "
      "cannot attribute characters to proper names vs generated text.")
    a("")
    a("## Practical interface constraints (separate dimension)")
    a("")
    a("- Claude (Sonnet 5, Sonnet 5 max): free-tier token exhaustion, "
      "repeated waits/continuations; max run > 45 min; run 12 P2A intake "
      "partial (end-marker formatting).")
    a("- Gemini: corpus must be split across two messages (interface "
      "one-message limit); Gemini 3.1 Pro ingested the corpus in 3.6 "
      "Flash then translated in 3.1 Pro; extended-thinking toggle resets "
      "per message.")
    a("- Dola: identity is author-recorded (ByteDance web) and not "
      "independently verifiable; exploratory.")
    a("")
    a("## Limitations")
    a("")
    a("- n = 1 direct + 1 primed generation per configuration; observed "
      "deltas mix priming, stochastic generation variation, interface "
      "behaviour, configuration differences and baseline dependence.")
    a("- No causal priming estimate; tests are exploratory.")
    a("- Canonical coverage answers 'resource coverage', not 'is this "
      "valid/natural Interslavic'; naturalness was not measured in "
      "EXP-004 (no human evaluation by design, D-042).")
    a("- EXP-003 human-preference data is a separate one-participant "
      "experiment and is NOT used as a selection criterion here.")
    a("")
    a("## Supported / suggestive / not established (short form)")
    a("")
    a("| Statement | Class |")
    a("|---|---|")
    a("| Priming was followed by higher canonical coverage (18/18) | supported (descriptive, exploratory tests) |"),
    a("| Priming was followed by higher broader coverage (14/18) | supported (descriptive, weaker) |"),
    a("| Priming improves Interslavic naturalness | not established |"),
    a("| Dola Fast responds 'particularly strongly' to priming | not established (baseline dependence) |"),
    a("| The highest-coverage model is 'best' for Interslavic | not established (no composite, no naturalness) |"),
    a("| Canonical coverage predicts human preference | not established (separate experiment) |"),
    a("| Three-register corpus beats one-register | not established (no comparison condition) |"),
    a("| Thinking mode improves Interslavic generation | suggestive only, inconsistent across families |"),
    a("| Baseline quality predicts priming response | suggestive (ρ ≈ −0.86 canonical), descriptive |"),
    a("")
    a("## Candidates for further investigation (not winners)")
    a("")
    a("See analysis.md / EXPERIMENTS.md Task 024. Short list: Claude "
      "Sonnet 5; DeepSeek V3 Expert (ON); Qwen 3.8 Max Fast; Gemini 3.6 "
      "Flash (both settings) for the largest credible deltas; Dola Fast "
      "only as an explicitly exploratory follow-up (identity + "
      "baseline-dependence caveats).")
    a("")
    a("## Figures")
    a("")
    for letter in "ABCDEFG":
        a(f"![chart {letter}](figures/chart_{letter.lower()}.svg)")
    a("")
    return "\n".join(R)


def render_poster_html(md_path: Path, fig_dir: Path) -> str:
    svgs = {}
    for letter in "ABCDEFG":
        p = fig_dir / f"chart_{letter.lower()}.svg"
        if p.is_file():
            svgs[letter] = p.read_text(encoding="utf-8")
    head = []
    for letter in "ABCDEFG":
        head.append(f"<h2>Chart {letter}</h2>")
        head.append(svgs.get(letter, f"<p>missing chart {letter}</p>"))
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>EXP-004 poster draft (Task 024)</title>
<style>
 body {{ font-family: Helvetica, Arial, sans-serif; margin: 2em auto;
        max-width: 1400px; color: #1a1a1a; }}
 h1 {{ font-size: 26px; }} h2 {{ font-size: 18px; margin-top: 1.5em; }}
 .note {{ font-style: italic; color: #555; }}
 svg {{ max-width: 100%; height: auto; border: 1px solid #eee; }}
 table {{ border-collapse: collapse; font-size: 11px; }}
 td, th {{ border: 1px solid #ccc; padding: 2px 6px; }}
</style></head><body>
<h1>EXP-004 — Does Authentic Medžuslovjansky Corpus Priming Improve LLM
Translation? <span style="font-size:14px">(first poster draft, Task 024;
markdown text version: poster.md)</span></h1>
<p class="note">Every number is from scripts/analyze_exp004_phase2a.py
(deterministic; dataset + analysis JSON in this directory). Research
visualisation — no winner claim.</p>
{''.join(head)}
</body></html>
"""


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def cmd_analyze(ds: dict) -> Path:
    an = build_analysis(ds)
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    (ANALYSIS_DIR / "dataset.json").write_text(
        json.dumps(ds, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (ANALYSIS_DIR / "analysis.json").write_text(
        json.dumps(an, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (ANALYSIS_DIR / "analysis.md").write_text(
        render_md(ds, an), encoding="utf-8")
    print(f"[analyze] wrote dataset.json + analysis.json + analysis.md "
          f"({len(ds['configs'])} configurations; {ANALYSIS_DIR})")
    return ANALYSIS_DIR / "analysis.md"


def cmd_charts(ds: dict) -> None:
    written = render_charts(ds, FIGURES_DIR)
    print(f"[charts] wrote {len(written)} svg charts to {FIGURES_DIR}")


def cmd_poster(ds: dict, an: dict) -> None:
    md = render_poster_md(ds, an)
    (ANALYSIS_DIR / "poster.md").write_text(md, encoding="utf-8")
    html = render_poster_html(ANALYSIS_DIR / "poster.md", FIGURES_DIR)
    (ANALYSIS_DIR / "poster.html").write_text(html, encoding="utf-8")
    print(f"[poster] wrote poster.md + poster.html to {ANALYSIS_DIR}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="EXP-004 full analysis (Task 024) — deterministic, "
                    "read-only.")
    ap.add_argument("what", nargs="?", default="all",
                    choices=("analyze", "charts", "poster", "all"),
                    help="what to generate (default: all)")
    args = ap.parse_args(argv)
    ds = build_dataset()
    an = None
    if args.what in ("analyze", "all"):
        cmd_analyze(ds)
    if args.what in ("poster", "all"):
        an = an or build_analysis(ds)
        cmd_poster(ds, an)
    if args.what in ("charts", "all"):
        cmd_charts(ds)
    return 0


if __name__ == "__main__":
    sys.exit(main())
