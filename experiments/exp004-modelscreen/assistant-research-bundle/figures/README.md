# figures/

Deterministic figures from `scripts/analyze_exp004_repeats.py`
(Task-026 repeated-generation analysis). SVG is the canonical
deterministic form; PNG is a render for direct inspection.

- `figure_a.svg` / `figure_a.png` — A — direct vs primed replicate distributions (all primary configurations)
- `figure_b.svg` / `figure_b.png` — B — repeated mean delta canonical, sorted
- `figure_c.svg` / `figure_c.png` — C — within-condition stochastic spread (SD + range)
- `figure_d.svg` / `figure_d.png` — D — Task-024 single-run delta vs Task-026 repeated mean delta
- `figure_e.svg` / `figure_e.png` — E — baseline mean vs repeated priming delta

Notes:
- Primary statistics are shown for the 18 primary configurations;
  **Dola is exploratory** and is kept out of these primary figures —
  its numbers are in `summary.json` under `configurations.exploratory`
  and in `results.json` (population `exploratory`).
- Dot/range plots, not bar charts; individual replicate observations are
  shown and outliers are not hidden.
- No winner/composite score is introduced anywhere.
