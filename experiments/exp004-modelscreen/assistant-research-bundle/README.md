# EXP-004 — Assistant Research Bundle (Tasks 024 / 025 / 026)

**Generated research-export interface** for an independent analysis of
EXP-004 (practical LLM model screening for Polish → Medžuslovjansky) —
Phase 1 (direct baselines), Phase 2A (authentic-corpus priming) and the
Task-025/026 controlled repeated-generation experiment.

**What this bundle is.** A compact, self-contained, deterministic
machine-readable export of the authoritative quantitative results, the
Task-026 collection audit, provenance/hashes, methodology and figures. It
is the file set the research lead can upload to an analysis assistant
without uploading the full experiment directory (~500 MB, dominated by
raw outputs which are intentionally excluded — see `raw/README.md`).

## What it represents

- Experiment: **EXP-004** (repository `isv-llm-lab`).
- Tasks included: **024** (full Phase-1 → Phase-2A analysis),
  **025** (controlled repeated generation kit) and **026** (collection
  audit + repeated-generation analysis, commit `048c026`).
- Reference commits: Task 024 `bc06858`; Task 025 `2db827d`;
  Task 026 `048c026` (see `provenance.json`).
- Version of this bundle: **1.0.0** (`manifest.json` pins every
  file's SHA-256).

## Authoritative data (exact counts from the files)

| population | planned | collected | usable | partial | invalid | missing |
|---|---:|---:|---:|---:|---:|---:|
| Primary (18 configurations) | 108 | 102 | 99 | 3 | 0 | 6 |
| Exploratory (Dola Fast/Pro) | 12 | 12 | 7 | 5 | 0 | 0 |
| **Total** | **120** | **114** | **106** | **8** | **0** | **6** |

Headline (descriptive; every number below is reconstructed in the
`verify` step from `results.json` alone): repeated mean Δ canonical
`mean(primed) − mean(direct)` is positive for **16/16** primary
configurations with both conditions usable (mean ≈ **+6.93 pp**; broader
≈ **+3.88 pp**); the Task-024 single-run direction is reproduced in
**15/15** rows that have an old delta; stochastic spread (median SD ≈
1.49 pp direct / ≈ 0.87 pp primed) is typically smaller than the shift.
Dola is exploratory and never enters primary statistics.

## Files: full data vs summaries

| file | role |
|---|---|
| `results.json` | **FULL per-run data** — one object per planned run (120 = 108 primary + 12 exploratory), with per-replicate r01/r02/r03 metrics, intake verdicts, hashes, orthography counts, deviation flags. Missing runs are present with `status: missing` and `metrics: null`. |
| `results.csv` | flat tabular form of `results.json` (one row per planned run) |
| `summary.json` | per-configuration descriptive statistics over the usable replicates (n/mean/median/SD/min/max/range for canonical + broader + unresolved + orthography), repeated deltas, Task-024 old singles (marked `historical_task024`), aggregates, missing/partial lists |
| `audit.json` | run-level Task-026 audit projection (counts, hash gates, manifest consistency, mechanical checks, per-run structural flags) |
| `deviations.json` | structured registry of every protocol/interface deviation (Claude Max thinking OFF, Grok identity, Gemini split corpus, Dola Pro blank line, fresh-session provenance, intake-partial) |
| `provenance.json` | source/corpus/kit hashes, evaluator + audit + analysis references, commits, runtime |
| `manifest.json` | bundle file list with SHA-256 for every file (deterministic) |
| `methodology.md` | complete method description (design, metrics, repeated estimate, statistical caution) |
| `figures/` | figures A–E (SVG + PNG) |
| `raw/README.md` | explains raw-output exclusion and how to request specific files |

## Generation

Deterministic, standard-library generator:
`scripts/build_assistant_research_bundle.py build`
(run `… verify` to re-run the standalone reconstruction check). Sources:
`repeats/outputs/plan.json`, `outputs/roster.json`, `outputs/audit.json`,
`operator-prompts/manifest.json`, `analysis/dataset.json`,
`analysis/analysis.json`, `analysis/figures/`. No timestamp is embedded —
regeneration is byte-identical (manifest included).

## What is deliberately excluded

- Raw model replies and operator prompt files (copyrighted source +
  corpus, ~500 MB, gitignored in the repo) — metadata + metrics are here
  instead.
- The full corpus and full prompt text (hashes are sufficient for
  provenance; both are pinned in `provenance.json`).
- Per-character orthography line details (per-run counts are included;
  full breakdowns stay in the repo's orthography reports).
- Secrets/credentials (none are read or written).
- Historical Task-024 raw outputs (their per-run metrics are included
  only as `historical_task024` markers in `summary.json`).
