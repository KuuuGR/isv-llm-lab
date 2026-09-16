# Phase 2B LOW — aggregate analysis

Derived artifacts in this directory are **gitignored** (deterministic
outputs of `scripts/analyze_exp004_phase2b.py --regime low`, derived from
evaluated runs that stay local); this README is committed.

## Contents

| file | content |
|---|---|
| `dataset.json` | integrity ledger + 42 observations + per-config direct/primed stats + paired Δᵢ = Pᵢ − Dᵢ for canonical / broader / unresolved / orthography-out |
| `analysis.json` | machine-readable summary tables + distribution notes |
| `analysis.md` | human-readable descriptive report |
| `EVIDENCE.md` | article-ready evidence record (fact / interpretation / hypothesis) |
| `QUALITATIVE_AUDIT.md` | descriptive D→P audit of **valid** pairs (Qwen mismatch excluded from primary) |
| `qualitative_audit.json` | machine-readable pair ledger for the qualitative audit |
| `QWEN_INCIDENT.md` | methodological incident: invalid Qwen LOW pairing + service error |
| `invalid_cells.json` | machine-readable invalid-cell ledger |

## Method

```bash
.venv/bin/python scripts/analyze_exp004_phase2b.py --regime low
```

- Reads `phase2b/outputs/low/plan.json` and each run's `evaluation.json` +
  `orthography.json` (already produced by intake).
- Hard integrity gate: 42 runs, 7 configs × 3 direct × 3 primed, unique
  run ids, every D/P pair share replicate tags, all usable/complete.
- **n = 3** → descriptive only; no significance tests; no causal claims.
- Never calls an LLM; never modifies raw outputs / story / corpus.
- Does **not** overwrite HIGH artifacts under `phase2b/analysis/` (parent).
- Primary priming aggregates use **6 valid** same-model paired configurations; Qwen is retained but marked `INVALID — MODEL MISMATCH`.
