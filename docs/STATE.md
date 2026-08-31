# Project State

Updated: 2026-08-31 (SODA Task 006.2 — EXP-002 pilot finalized and analyzed)

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

## Current status (end of Task 006.2)

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
| **Manual audit sample (Task 004)** | ✅ **PREPARED** — stratified ~100-form sample of unresolved forms + statistics under `experiments/exp001-baseline/manual-audit/` (local, gitignored) for human review; no linguistic classification performed |
| **Cross-resource audit (Task 005)** | ✅ **COMPLETE** — all 1,050 unresolved forms re-checked against hunspell `isv.dic`, `interslavicfreq` wordlists, and the `slovnik` snapshot (evidence only; no resource modified); report under `experiments/exp001-baseline/manual-audit/` (local, gitignored) |
| **EXP-002 pilot (Task 006/006.1)** | ✅ **EXECUTED** — all seven conditions run externally (via `operator-prompts/` copy/paste), collected byte-for-byte, compared with the same evaluator |
| **EXP-002 finalization (Task 006.2)** | ✅ **COMPLETE** — 7/7 runs verified (SHA-256); token-aligned transition matrix (C→A=90, A→C=12, B→C=0); per-form candidate usage; `interslavicfreq` discrepancy explained; Bielik no-change case verified; 5 human-review pairs; final report + recommendation in `experiments/exp002-pilot/REPORT.md` |
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
  sample_exp001_audit.py     — build the manual-audit sample of unresolved forms
  audit_exp001_resources.py  — cross-resource audit of all unresolved forms (Task 005)
  prepare_exp002_pilot.py    — EXP-002 candidate generation + prompt packages
  compare_exp002.py          — EXP-002 before/after evaluation + transition matrix + human-review pairs
  run_exp002_pilot.py        — EXP-002 orchestrator (prepare / collect / compare / status)
  package_operator_prompts.py — EXP-002 operator-facing single-file Markdown prompts
  verify_exp002_runs.py      — EXP-002 completeness + SHA-256 integrity check (Task 006.2)
data/
  dictionary/README.md       — how to regenerate the (gitignored) data
  dictionary/audit/          — downloaded audit inputs (hunspell, frequency, slovnik), gitignored
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
    manual-audit/README.md   — manual audit sample of unresolved forms + cross-resource audit index (data is gitignored)
  exp002-pilot/
    DESIGN.md                — EXP-002 pilot design (candidate generation, prompt, evaluation)
    README.md                — operator instructions (prepare / execute externally / evaluate)
    REPORT.md                — final report: results, regressions, `interslavicfreq` discrepancy, recommendation
    prompt_template.txt      — revision prompt template (shared)
    operator-prompts/        — ONE self-contained Markdown prompt per condition (generated, .md gitignored)
    input/  outputs/  comparison/  — run artifacts (all gitignored; all 7 runs executed and compared)
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
