# Phase 2B UNSEEN — aggregate analysis

Derived artifacts in this directory are **gitignored** (deterministic
outputs of `scripts/analyze_exp004_phase2b.py --regime unseen`, derived from
evaluated runs that stay local); this README is committed.

## Contents

| file | content |
|---|---|
| `dataset.json` | integrity ledger + 42 observations + per-config direct/primed stats + paired Δᵢ = Pᵢ − Dᵢ |
| `analysis.json` | machine-readable summary tables + distribution notes |
| `analysis.md` | human-readable descriptive report |
| `EVIDENCE.md` | article-ready evidence record |
| `QUALITATIVE_AUDIT.md` | descriptive D→P audit of all 21 pairs |
| `qualitative_audit.json` | machine-readable pair ledger |
| `VALIDATION.md` / `validation.json` | pre-execution source validation (committed earlier) |

## Method

```bash
.venv/bin/python scripts/analyze_exp004_phase2b.py --regime unseen
```

- Reads `phase2b/outputs/unseen/plan.json` and each run's `evaluation.json` +
  `orthography.json` (already produced by intake).
- Hard integrity gate: 42 runs, 7 configs × 3 direct × 3 primed, unique
  run ids, every D/P pair share replicate tags, all usable/complete.
- **n = 3** → descriptive only; no significance tests; no causal claims.
- Never calls an LLM; never modifies raw outputs / story / corpus.
- Does **not** overwrite HIGH or LOW analysis artifacts.
- UNSEEN source is shorter/expository (design characteristic).
