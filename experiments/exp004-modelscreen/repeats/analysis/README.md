# Phase-repeat analysis (EXP-004, SODA Task 025)

Derived artifacts in this directory are **gitignored** (deterministic
outputs of `scripts/analyze_exp004_repeats.py`, derived from raw outputs
that stay local); this README is committed.

## Current state (2026-09-09): results written (Task 026)

The repeated-generation collection was completed, audited (Task 026:
114/120 collected, 106 usable) and evaluated with the unmodified
pipeline. `scripts/analyze_exp004_repeats.py` was re-run and wrote the
full deterministic result set here:

| file | content |
|---|---|
| `dataset.json` | per-configuration observation + stats dataset (usable replicates only; per-observation rows, direct/primed, primary/exploratory, orthography, replicate blocks) |
| `analysis.json` | machine-readable analysis — `status: results`; counts, stats, repeated Δ canonical + broader, old-vs-new rows, figure data |
| `analysis.md` | narrative report — collection summary, stats tables, candidate re-evaluation, figures |
| `figures/figure_a..e.svg` | Figure A replicate distributions; B repeated mean Δ (sorted); C within-condition spread; D Task-024 single vs repeated Δ; E baseline vs repeated Δ — Dola kept visually distinct + labelled exploratory |

Key numbers (see `analysis.md`, `REPORT.md`): repeated Δ canonical mean
**+6.93 pp** over 16 primary configurations with both conditions usable
(16/16 positive); Task-024 direction reproduced in 15/15 rows with an
old delta; mean old Δ +6.33 pp vs mean repeated Δ +6.73 pp on the same
rows. 6 runs were never collected (Gemini 3.1 Pro and Qwen 3.8 Max
Thinking primed → repeated Δ n/a) and 8 collected runs are intake
partial (end-marker soft failures) and excluded from usable stats. Dola
Fast's old +28.20 pp cannot be re-estimated (direct condition unusable);
Dola Pro repeated Δ +12.41 pp.

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
