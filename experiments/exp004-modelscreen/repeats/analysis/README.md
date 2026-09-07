# Phase-repeat analysis (EXP-004, SODA Task 025)

Derived artifacts in this directory are **gitignored** (deterministic
outputs of `scripts/analyze_exp004_repeats.py`, derived from raw outputs
that stay local); this README is committed.

## Current state (2026-09-07): no results scaffold

The repeat kit is prepared but **no LLM generation has been collected yet**,
so this directory holds an explicit no-results scaffold written by the
analysis script:

| file | content |
|---|---|
| `dataset.json` | per-configuration observation + stats dataset — empty until usable observations exist |
| `analysis.json` | machine-readable analysis — `status: no_results` |
| `analysis.md` | narrative report — "NO RESULTS YET", design/stats method + interpretation rules |
| `figures/figure_a..e.svg` | placeholder files ("figure not generated: no usable repeat observations yet") |

No empty or fabricated charts are produced. After the research lead
collects and the pipeline evaluates usable replicates
(`run_exp004_repeats.py collect-msg2/collect-session` → `verify` →
`evaluate` → `roster`), re-running
`scripts/analyze_exp004_repeats.py` writes the real results here:
per-(configuration, condition) n=3 small-sample descriptive statistics,
`mean(primed) − mean(direct)` deltas (explicitly distinct from the
Task-024 single-run deltas), figures A–E, three research-facing selection
views (absolute quality / stability / priming responsiveness) plus the
orthography dimension, candidate reproducibility answers and
supported/suggestive/not-established conclusions. No composite score, no
winner.

## Method (deterministic, standard library only)

- n=3 descriptive statistics per (configuration, condition): n, mean,
  median, sd, min, max, range for canonical + broader coverage; mean
  unresolved; orthography anomaly mean/min/max.
- Primary priming quantity:
  `mean(primed replicates) − mean(direct replicates)`; old single deltas
  joined from the Phase-1/Phase-2A rosters for Figure D.
- Replicate blocks r01/r02/r03 are not matched samples; block differences
  appear only as a secondary descriptive view.
- Baseline dependence revisited descriptively (Spearman, repeated direct
  mean vs repeated delta) and compared with the Task-024 ρ ≈ −0.86.
- Interpretation rules: supported / suggestive / not-established; never
  causality, "priming generally improves ISV", a "best" model, coverage =
  naturalness, reasoning-mode superiority, or a Dola learning ability.
