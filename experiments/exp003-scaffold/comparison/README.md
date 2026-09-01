# EXP-003 — comparison

Analysis produced by `scripts/compare_exp003.py` after runs are collected:

- `<run_id>/comparison.json` + `comparison.md` — per-run two-tier metrics,
  NEW name-excluded diagnostics, supplied-candidate usage (surface-level
  proxy), and non-supplied/invented vocabulary breakdown.
- `within_model/<model>.json` — pairwise condition comparisons for one model
  (A vs B/C/D, B vs C, B vs D, C vs D): token-aligned evaluator-state
  transitions, A→C / B→C regressions, C→A / C→B resolutions, metric deltas,
  output-length and structural changes.
- `within_condition/<condition>.json` — pairwise model comparisons within one
  condition.
- `summary.md` — run summary plus all pairwise transition tables.
- `human_review.md` — blinded complete-text pairs for holistic Project-Owner
  judgment (automatic metrics hidden).
- `human_review_key.json` — the blinded-label → (model, condition, run)
  mapping, kept separate and unblinded only after the holistic judgment.

No composite quality score is ever assigned. All files embed raw model
outputs and are **gitignored** — they stay local.
