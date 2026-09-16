# Phase 2B HIGH — aggregate analysis

Derived artifacts in this directory are **gitignored** (deterministic
outputs of `scripts/analyze_exp004_phase2b.py`, derived from evaluated
runs that stay local); this README is committed.

**Research status:** 42/42 collected, verified, evaluated; aggregate
integrity **PASS**. Article-ready evidence (fact vs interpretation vs
hypothesis): [`../EVIDENCE.md`](../EVIDENCE.md). Protocol:
[`../README.md`](../README.md).

## Contents

| file | content |
|---|---|
| `dataset.json` | integrity ledger + 42 observations + per-config direct/primed stats + paired Δᵢ = Pᵢ − Dᵢ for canonical / broader / unresolved / orthography-out (each row traces to run IDs + artifact paths) |
| `analysis.json` | machine-readable summary tables + distribution notes |
| `analysis.md` | human-readable descriptive report |

## Method

```bash
.venv/bin/python scripts/analyze_exp004_phase2b.py
```

- Reads `phase2b/outputs/plan.json` and each run's `evaluation.json` +
  `orthography.json` (already produced by intake).
- Hard integrity gate: 42 runs, 7 configs × 3 direct × 3 primed, unique
  run ids, every D/P pair share replicate tags, all usable/complete.
- **n = 3** → descriptive only; no significance tests; no causal claims.
- Never calls an LLM; never modifies raw outputs / story / corpus.
