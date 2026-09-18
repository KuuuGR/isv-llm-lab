# Phase 2B — final cross-regime synthesis (HIGH / LOW / UNSEEN)

**Status:** final descriptive evidence pack (2026-09-18).  
**Not:** manuscript prose; not a significance test; not a causal claim; not a model ranking.

Canonical experiment root: `experiments/exp004-modelscreen/phase2b/`  
This directory is the authoritative **three-regime** synthesis layer.

## Contents

| File | Role |
|---|---|
| [`analysis.md`](analysis.md) | Human-readable final synthesis |
| [`analysis.json`](analysis.json) | Machine-readable synthesis + per-config tables |
| [`EVIDENCE.md`](EVIDENCE.md) | Layered Measured / Observed / Interpretation / Uncertainty / Limitation |
| [`QUALITATIVE_SYNTHESIS.md`](QUALITATIVE_SYNTHESIS.md) | Cross-regime qualitative synthesis |
| [`cross_regime_table.csv`](cross_regime_table.csv) | Compact Δ table (HIGH / LOW / UNSEEN) |
| [`cross_regime_table_full.csv`](cross_regime_table_full.csv) | Full Direct / Primed / Δ / validity |
| [`cross_regime_table.json`](cross_regime_table.json) | Compact table (JSON) |
| [`README.md`](README.md) | This file |

## Scope

| Regime | Primary valid paired configs | Notes |
|---|---:|---|
| HIGH | 7 | 42/42 runs |
| LOW | 6 | Qwen `INVALID — MODEL MISMATCH` |
| UNSEEN | 7 | 42/42 runs; all 21 replicate Δ > 0 |

**Matched-six** comparison (same configs on all three regimes) excludes Qwen.

## Relation to other artifacts

| Artifact | Role |
|---|---|
| `analysis/` (HIGH root) | HIGH primary aggregate |
| `analysis/low/` | LOW primary aggregate + Qwen incident |
| `analysis/unseen/` | UNSEEN primary aggregate |
| `analysis/high_low/` | Historical **HIGH↔LOW-only** exploratory synthesis (keep; superseded for three-regime questions) |
| `EXP-004_PHASE2B_CHECKPOINT.md` | Historical post-HIGH+LOW checkpoint (stale for UNSEEN-complete status) |

## Method

Reconstructed from existing HIGH / LOW / UNSEEN `analysis.json`, EVIDENCE, and qualitative audits.  
No LLM sessions. No raw-output edits. No frozen-source or corpus edits. No methodology change.

## Key descriptive numbers (pp)

| Summary | HIGH | LOW | UNSEEN |
|---|---:|---:|---:|
| All-config mean Δ | +7.07 (n=7) | +8.53 (n=6) | +5.45 (n=7) |
| Matched-six mean Δ | +7.39 | +8.53 | +5.78 |

See [`analysis.md`](analysis.md) for the full configuration table and findings.
