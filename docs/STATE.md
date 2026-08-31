# Project State

Updated: 2026-08-31 (SODA Task 003 complete — Experiment 001 baseline run)

## What this project is

**Interslavic LLM Lab** (`isv-llm-lab`) — a research lab for improving
LLM-generated Interslavic by constraining generation with existing lexical and
morphological resources. This is an open-source, non-profit, community research
project. **It is not an official Interslavic project.**

Research hypothesis:
> Modern LLMs can generate plausible-looking Interslavic while introducing
> vocabulary or forms actually borrowed from individual Slavic languages.
> Constraining generation with existing Interslavic resources may reduce this.

This is a hypothesis. The first experiment must establish a baseline before
any constrained system is judged against it.

## Current status (end of Task 003)

| Area | Status |
|---|---|
| Repository initialized | ✅ README + SODA docs + source inventory |
| Dictionary resources audited | ✅ `sonic16x/interslavic` + generated `basic.json` |
| Morphology engines audited | ✅ JS (`@interslavic/morphology`, tested live) and Rust (`gold-silver-copper/interslavic`, static) |
| Frequency/synonym resources audited | ✅ `medzuslovjansky/interslavicfreq` |
| Grammar consistency audit | ✅ `docs/GRAMMAR_AUDIT.md` |
| Ecosystem survey | ✅ `SOURCES.md` ("Not used" section) |
| Dictionary snapshot | ✅ `data/dictionary/basic.json` (19,100 rows, local, gitignored) + `manifest.json` (SHA-256, URL, retrieval time, schema, license status) |
| Full-form lexicon | ✅ `data/dictionary/lexicon.tsv` (320,824 entries) generated from `@interslavic/morphology@0.1.2` |
| Evaluation harness | ✅ `isv-eval` CLI: tokenizer, lexical lookup, morphological validation, A/B/C classification, metrics, serialization |
| Smoke tests | ✅ 31 tests (tokenizer, normalization, classifier, B-fallback, end-to-end corpus) |
| **Experiment 001 (baseline)** | ✅ **RUN COMPLETED** — 7 model conditions evaluated on the complete Polish story; comparison in `experiments/exp001-baseline/outputs/comparison.md` |
| Translator / LLM integration | ❌ Not implemented (out of scope) |

### Experiment 001 headline numbers

Seven whole-story translations were evaluated against the snapshot dictionary
+ generated full-form lexicon (denominators = lexical tokens):

| Condition | Lexical Tokens | Exact (A) | Morph. Valid (B) | Unresolved (C) | Valid Coverage |
|---|---:|---:|---:|---:|---:|
| ChatGPT | 1522 | 1153 | 3 | 366 | 75.95% |
| GPTs — ISV Teacher | 1522 | 1213 | 2 | 307 | 79.83% |
| Gemini | 1471 | 1054 | 1 | 416 | 71.72% |
| Claude | 1486 | 1092 | 1 | 393 | 73.55% |
| DeepSeek | 1431 | 1064 | 1 | 366 | 74.42% |
| Bielik | 1561 | 862 | 4 | 695 | 55.48% |
| Grok | 1472 | 1127 | 0 | 345 | 76.56% |

Order is not a ranking. Full table, per-model unresolved vocabularies,
pairwise overlaps and shared-form statistics are in
`experiments/exp001-baseline/outputs/comparison.{md,json}` (gitignored) and
summarized in `docs/EXPERIMENTS.md` § EXP-001.

## Repository layout

```
README.md                    — project intro + index
SOURCES.md                   — source/dependency inventory
pyproject.toml               — Python package (`isv-eval`), console script
src/
  isv_eval/                  — tokenizer, lexicon, morphology client,
  |                            classifier, metrics, CLI
  morphology_backend/        — Node stdio backend (inflect + translit),
                               pinned deps + committed package-lock.json
scripts/
  fetch_dictionary.py        — snapshot basic.json + write manifest
  generate_lexicon.py        — build full-form lexicon TSV + manifest
data/
  dictionary/README.md       — how to regenerate the (gitignored) data
tests/
  fixtures/smoke_corpus.txt  — synthetic smoke corpus
  test_*.py                  — normalize/tokenizer/classifier/smoke tests
docs/
  STATE.md                   — this file
  ROADMAP.md                 — roadmap + future ideas
  DECISIONS.md               — decision log
  EXPERIMENTS.md             — experiment log
  GRAMMAR_AUDIT.md           — grammar consistency audit (Task 001 deliverable)
  LESSONS.md                 — lessons learned (SODA mechanism)
experiments/
  exp001-baseline/
    DESIGN.md                — Experiment 001 design (input/storage/metrics/reproducibility)
```

## Working agreements

- Python is the default language for the evaluation pipeline unless an existing
  Interslavic component requires another runtime (the JS morphology engine is
  the expected primary backend; Node is therefore also an accepted runtime).
- Reuse existing resources; do not reimplement morphology or synonym ranking.
- Keep experiments small and reproducible; never overwrite previous results.
- Do not build production infrastructure.

## To run the evaluator

```bash
python3 -m venv .venv && .venv/bin/pip install -e ".[dev]"   # once
npm ci                                                       # once, in src/morphology_backend/
python3 scripts/fetch_dictionary.py                          # once (network)
python3 scripts/generate_lexicon.py                          # once (~90 s)
.venv/bin/isv-eval path/to/text.txt --out results/           # evaluate
```

Generated data (`data/dictionary/basic.json`, `lexicon.tsv`, manifests) is
local and gitignored because the dictionary data license is unresolved
(SOURCES.md).
