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
- `human_review.md` — the DESIGN §11 blinded holistic review of the complete
  runs (ChatGPT A–D, Claude A–D). **SUPERSEDED (2026-09-05, SODA Task 014)**
  as the primary human-evaluation method: comparing four complete long
  translations was too cognitively demanding for the Project Owner. It is
  preserved only as a historical/provisional review design and carries a
  superseded banner; **no holistic human result was obtained and none is
  recorded anywhere**. Do not perform this review.
- `human_review_key.json` — the mapping for the superseded holistic artifact
  (set label → model → condition → Version label → run id). Kept only for
  the historical record.
- `sentence_review.md` — the PRIMARY EXP-003 human-evaluation instrument
  (SODA Task 014): a sentence-level forced-choice preference test prepared
  by `scripts/prepare_exp003_sentence_review.py`. ~100 questions; each shows
  one Polish source sentence and the corresponding sentence from each of the
  four conditions (A/B/C/D) of the same model, randomized per question into
  neutral "Version 1..4" labels (fixed recorded seed, never alphabetical).
  The Project Owner ticks the version that sounds most natural as
  Medžuslovjansky (best-choice only). The document contains no model names,
  no A/B/C/D condition labels, no automatic metrics, and no hints; the
  instructions explicitly ask for a holistic sentence impression, not
  word-level dictionary verification.
- `sentence_review_key.json` — private answer key for `sentence_review.md`:
  source sentence identity and text, story section, dialogue flag, the model,
  run ids, the per-question randomized display order (Version label →
  A/B/C/D), the version texts, the randomization seed, and sampling
  metadata. Kept separate from the participant document and opened only
  after the answers are recorded.

Incomplete runs (e.g. all four Bielik runs, Task 011) are preserved under
`<run_id>/excluded.json` and never enter the human review.

No composite quality score is ever assigned. All files embed raw model
outputs and are **gitignored** — they stay local.
