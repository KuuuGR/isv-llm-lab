# Roadmap

Status: updated 2026-08-31 (end of Task 003). This is a plan, not a
commitment; the Architect/Research Lead re-prioritizes as evidence arrives.

## Done

- [x] **Task 002 — Baseline experiment harness**
  - [x] Snapshot `basic.json` into `data/dictionary/` with hash manifest
        (`scripts/fetch_dictionary.py` → `manifest.json`).
  - [x] Full-form lexicon from the dictionary via `@interslavic/morphology`
        (`scripts/generate_lexicon.py` → 320,824-entry TSV).
  - [x] Evaluation pipeline: tokenizer + exact-match lookup + morphological
        validation (Node stdio backend), A/B/C classification + review (D).
  - [x] Metrics: `exact_dictionary_coverage`, `morphologically_valid_coverage`,
        `unresolved_forms`, `total_tokens` (denominator policy documented).
  - [x] Smoke tests (31) incl. edge cases (`more → morem` corrected, folded
        etymological matching, hyphenation, Cyrillic).
- [x] **Experiment 001 (baseline) — RUN COMPLETED** (Task 003):
  - [x] Source registered (`opowiadania-set-isv/op-pl.txt`, SHA-256
        `e3164ffc…e643`; preprocessing artifact documented in `source.meta.json`).
  - [x] Seven independent whole-story conditions evaluated with `isv-eval`:
        ChatGPT, Gemini, Claude, DeepSeek, Bielik, Grok,
        GPTs "Interslavic — Medžuslovjansky Language Teacher"
        (`condition_type = specialized_custom_gpt`, kept separate from ChatGPT).
  - [x] Per-run reproducibility (source/output SHA-256, dict manifest,
        morphology version, evaluator commit `48f2523`).
  - [x] Cross-model comparison (`scripts/compare_exp001.py`): metrics table,
        per-model unresolved vocabularies + frequencies, pairwise overlaps,
        shared-form summary (1050 unique / 219 in 2+ / 83 in 3+ / 8 in all 7).
  - [x] B-bucket fallback batched (one morphology call per chunk of distinct
        candidate lemmas) — cut full-story runtime from minutes to seconds.
  - [x] Results: `experiments/exp001-baseline/outputs/comparison.md` + docs/EXPERIMENTS.md.

## Next recommended task (single)

- [ ] **Experiment 002 — constrained generation** (compare against this
  baseline; see `experiments/exp001-baseline/DESIGN.md` § Future experiment).

## Later

- [ ] Investigate dictionary **data licensing** (Steen source data / Google
  Spreadsheet) before any redistribution of derived data.
- [ ] Decide primary morphology backend for constrained generation
  (JS `@interslavic/morphology` vs Rust `interslavic`) based on integration cost
  and Experiment 001 validation results.
- [ ] Verify whether `interslavicfreq` is published on PyPI; pin accordingly
  (planned signal for suspicious-form ranking, not yet integrated).
- [ ] Precomputed lexicon index (e.g. serialized dict) to cut lexicon load time
  if full-story runs get slow.
- [ ] Manual linguistic review of the Experiment 001 unresolved vocabularies
  (sentence context + candidate lemmas already preserved in
  `outputs/*/unresolved.json`); no automatic language-origin classification.

## Future ideas (recorded, not implemented)

- `@interslavic/levenshtein` as an approximate-intelligibility signal for
  ranking candidate lexemes in the constrained system.
- `@interslavic/stemmer`/`@interslavic/lunr` for cross-script search over the
  generated lexicon.
- Hunspell `isv.dic` as an independent surface-form validity signal and/or a
  spellcheck-style fuzzy fallback for unresolved forms.
- Dictionary `type` and `intelligibility` columns as provenance-aware features
  in the candidate ranking (e.g. down-weight neologisms/doubtful entries).
- A lightweight manual-review workflow for "suspicious forms" with sentence
  context preserved (no language-origin classifier in Task 001).
- Corpus building: collected raw model outputs + validated analysis as a seed
  evaluation set for later experiments.
