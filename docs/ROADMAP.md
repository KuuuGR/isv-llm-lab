# Roadmap

Status: updated 2026-08-31 (end of Task 002). This is a plan, not a
commitment; the Architect/Research Lead re-prioritizes as evidence arrives.

## Done

- [x] **Task 002 — Baseline experiment harness (implemented; full experiment not run)**
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
- [ ] Obtain one complete Polish short story from the Project Owner.
- [ ] **Experiment 001 (baseline)**: send the whole story independently to
  ChatGPT, Gemini, Claude, DeepSeek (one translation task per model); store raw
  outputs; analyze with `isv-eval`; report metrics.

## Later

- [ ] **Experiment 002 (constrained generation)** — compare baseline vs the
  constrained pipeline (lemma+features → dictionary → ranking → LLM contextual
  choice → deterministic morphology → validation). Design already documented in
  `experiments/exp001-baseline/DESIGN.md` (§ Future experiment), implementation pending.
- [ ] Investigate dictionary **data licensing** (Steen source data / Google
  Spreadsheet) before any redistribution of derived data.
- [ ] Decide primary morphology backend for constrained generation
  (JS `@interslavic/morphology` vs Rust `interslavic`) based on integration cost
  and Experiment 001 validation results.
- [ ] Verify whether `interslavicfreq` is published on PyPI; pin accordingly
  (planned signal for suspicious-form ranking, not yet integrated).
- [ ] Batch the bucket-B morphological fallback (one morphology call per text
  instead of per unresolved token) if unresolved counts grow.
- [ ] Precomputed lexicon index (e.g. serialized dict) to cut lexicon load time
  if full-story runs get slow.

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
