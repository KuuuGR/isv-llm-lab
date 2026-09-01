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
- `human_review.md` — the DESIGN §11 blinded holistic review for the Project
  Owner. Contains ONLY the 8 complete runs (ChatGPT A–D, Claude A–D),
  grouped into two neutral sets ("Set 1", "Set 2") with per-set randomized
  "Version 1..4" labels (deterministic seed, reproducible). Includes the four
  holistic questions, a preference-ordering template, a clearly separated
  post-unblinding section (scaffold-constraint question for B/C/D), and a
  recording checklist. No automatic metric and no model identity appears in
  the document.
- `human_review_key.json` — the mapping (set label → model → condition →
  Version label → run id), kept separate and opened only after the initial
  holistic judgment is recorded. Answers are recorded verbatim in
  `human_review.md`; no score is computed from them.

Incomplete runs (e.g. all four Bielik runs, Task 011) are preserved under
`<run_id>/excluded.json` and never enter the human review.

No composite quality score is ever assigned. All files embed raw model
outputs and are **gitignored** — they stay local.
