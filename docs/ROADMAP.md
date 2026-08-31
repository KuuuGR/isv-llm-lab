# Roadmap

Status: updated 2026-08-31 (end of Task 005). This is a plan, not a
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
- [x] **Task 004 — Manual audit sample prepared** (follow-up analysis of
  EXP-001, not a new experiment):
  - [x] Dataset statistics (1,050 unique unresolved forms / 2,888 occurrences;
        831 in exactly one model, 8 in all seven).
  - [x] Stratified ~100-form sample (`scripts/sample_exp001_audit.py`):
        A 25 high-frequency, B 25 shared (2–6 models), C 25 model-specific,
        D 15 diverse/edge-case, E 10 story-name representatives, plus the
        8 shared-by-all forms as a diagnostic appendix.
  - [x] Worksheet with blank human-review columns
        (`experiments/exp001-baseline/manual-audit/`), no automatic
        linguistic classification.
- [x] **Task 005 — Cross-resource audit of unresolved forms** (post-hoc
  evidence audit of EXP-001, not a new experiment):
  - [x] All **1,050** unresolved forms re-checked against every documented
        Interslavic resource (`scripts/audit_exp001_resources.py`): `basic.json`,
        generated lexicon, `slovnik` snapshot, hunspell `isv.dic`, and
        `interslavicfreq` wordlists; JS morphology (deterministic via lexicon),
        Rust morphology recorded NOT_TESTABLE (no toolchain).
  - [x] Per-form evidence matrix + report
        (`experiments/exp001-baseline/manual-audit/cross-resource-audit.{json,csv}`,
        `cross-resource-summary.md`); evidence categories, no linguistic
        judgments, no resource modification.
  - [x] Audit inputs downloaded at documented pins and stored locally
        (`data/dictionary/audit/`, gitignored).
  - [x] Key finding: 403 forms (38.4%) are attested verbatim in an alternative
        resource; 450 have candidate lemmas but no resource evidence; 116 have
        neither; 45 orthographic-variant candidates; 36 names/special only.

## Next recommended task (single)

- [ ] **Manual linguistic review of the Experiment 001 unresolved sample** —
  annotate `experiments/exp001-baseline/manual-audit/sample.csv`
  (100 stratified forms + 8 shared-by-all diagnostic forms, prepared in Task
  004; full contexts in `sample.json`). The Task 005 cross-resource evidence
  (`cross-resource-audit.csv`) is available as an input to the review.
  Human classification only — no automatic language-origin detection.

## Later

- [ ] **Experiment 002 — constrained generation** (compare against the
  baseline; see `experiments/exp001-baseline/DESIGN.md` § Future experiment)
  after the manual audit informs what the unresolved forms actually are.
- [ ] Investigate dictionary **data licensing** (Steen source data / Google
  Spreadsheet) before any redistribution of derived data.
- [ ] Decide primary morphology backend for constrained generation
  (JS `@interslavic/morphology` vs Rust `interslavic`) based on integration cost
  and Experiment 001 validation results.
- [ ] Verify whether `interslavicfreq` is published on PyPI; pin accordingly
  (planned signal for suspicious-form ranking, not yet integrated).
- [ ] Precomputed lexicon index (e.g. serialized dict) to cut lexicon load time
  if full-story runs get slow.

## Future ideas (recorded, not implemented)

- Translation-length metrics for future experiments (do NOT compare raw file
  sizes across source vs outputs — the source may carry prompt/formatting
  content, Task 003.1): character count excluding formatting, lexical token
  count, average word length, output/source length ratio.
- `@interslavic/levenshtein` as an approximate-intelligibility signal for
  ranking candidate lexemes in the constrained system.
- `@interslavic/stemmer`/`@interslavic/lunr` for cross-script search over the
  generated lexicon.
- Hunspell `isv.dic` as an independent surface-form validity signal and/or a
  spellcheck-style fuzzy fallback for unresolved forms (Task 005 confirmed it
  covers 54 of the 1,050 unresolved forms with full-form morphological tags;
  integration decision still open).
- Dictionary `type` and `intelligibility` columns as provenance-aware features
  in the candidate ranking (e.g. down-weight neologisms/doubtful entries).
- A lightweight manual-review workflow for "suspicious forms" with sentence
  context preserved (no language-origin classifier in Task 001).
- Corpus building: collected raw model outputs + validated analysis as a seed
  evaluation set for later experiments.
