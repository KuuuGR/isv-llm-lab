# Evidence map — EXP-004 Phase 2B manuscript

Maps major manuscript claims/tables/figures to canonical experiment artifacts.
Canonical root: `experiments/exp004-modelscreen/phase2b/`.

## Design / regimes

| Manuscript item | Canonical source |
|---|---|
| HIGH/LOW/UNSEEN definitions, hashes, lengths | `input/*.meta.json` (mirrored under `docs/research/exp004-phase2b/source-material/`); `analysis/combined/analysis.md` §6 |
| Priming corpus SHA-256 `aaad28e4…a857` | `analysis/combined/analysis.json` (`corpus_sha256`); HIGH/LOW/UNSEEN EVIDENCE headers |
| Direct vs Primed; Δ definition; n=3; 7 configs × 42 runs | `README.md`; `analysis/combined/analysis.md` §1–3 |

## Quantitative tables / figures

| Manuscript item | Canonical source |
|---|---|
| Table 3 central Δ (HIGH/LOW/UNSEEN) | `analysis/combined/cross_regime_table.csv` (+ `analysis.json` `configurations`) |
| Table 4 matched-six (+7.39 / +8.53 / +5.78) | `analysis/combined/analysis.json` → `matched_six` |
| All-config means (+7.07 / +8.53 / +5.45) | `analysis/combined/analysis.json` → `regime_summaries` |
| Integrity counts 42/42; valid configs 7/6/7 | `analysis/combined/analysis.md` §1; regime `analysis.json` integrity |
| Figure 1 config mean Δ | derived from `cross_regime_table.csv` |
| Figure 2 UNSEEN 21 replicate Δ | `analysis/combined/analysis.json` `configurations[*].unseen.delta_values_pp`; UNSEEN EVIDENCE |
| HIGH Direct/Primed means & SD | `EVIDENCE.md` (HIGH root); `analysis/analysis.json` |
| LOW valid/invalid cells | `analysis/low/analysis.json`; `analysis/low/invalid_cells.json` |
| UNSEEN all-positive replicates | `analysis/unseen/analysis.json` / EVIDENCE; combined `all_21_replicate_deltas_positive` |

## Qualitative claims

| Manuscript item | Canonical source |
|---|---|
| Corpus-opening / lexical / ortho synthesis | `analysis/combined/QUALITATIVE_SYNTHESIS.md` |
| HIGH pair examples | `QUALITATIVE_AUDIT.md`, `qualitative_audit.json` |
| LOW pair examples; Jaccard note | `analysis/low/QUALITATIVE_AUDIT.md` |
| UNSEEN pair examples | `analysis/unseen/QUALITATIVE_AUDIT.md` |

## Operational incidents

| Manuscript item | Canonical source |
|---|---|
| Qwen LOW INVALID — MODEL MISMATCH | `analysis/low/QWEN_INCIDENT.md` |
| Gemini multi-message Primed protocol | `analysis/combined/analysis.md` §1; regime READMEs/EVIDENCE |
| UNSEEN validation / provenance limits | `analysis/unseen/VALIDATION.md`; `UNSEEN_VALIDATION.md` |

## Stale records (do not use as current state)

| Record | Note |
|---|---|
| `EXP-004_PHASE2B_CHECKPOINT.md` | Post-HIGH+LOW, before UNSEEN |
| `analysis/high_low/` | HIGH↔LOW-only exploratory synthesis |

## Metrics

| Manuscript item | Canonical source |
|---|---|
| Metric names (canonical/broader/unresolved/ortho) | `EVIDENCE.md` (HIGH); LOW/UNSEEN EVIDENCE |
| Evaluator regeneration | `scripts/analyze_exp004_phase2b.py` |
