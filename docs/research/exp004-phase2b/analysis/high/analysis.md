# EXP-004 Phase 2B HIGH — aggregate analysis (descriptive)

**Status:** results written from 42 verified + evaluated runs.
**Generator:** `scripts/analyze_exp004_phase2b.py` (deterministic;
std-lib only; never calls an LLM).

> **n = 3** replicates per configuration/condition. This report is
> a **descriptive** paired summary of observed values. It does
> **not** establish statistical significance, does **not** claim
> causal corpus-priming effects, and does **not** rank models.

## 1. Data-integrity checks

Overall: **PASS** (42 observations, 7 configurations).

| check | result |
|---|---|
| `exactly_42_evaluated` | yes |
| `exactly_7_configurations` | yes |
| `no_duplicate_run_ids` | yes |
| `three_direct_three_primed_per_config` | yes |
| `every_direct_has_matching_primed_replicate` | yes |
| `all_usable_complete` | yes |

Provenance pins (from plan):
- HIGH story SHA-256: `ab8a0dcf7352789c09c4aca132c086999c861407e4cd682ee9414aab5b792f63`
- corpus SHA-256: `aaad28e43935a40313585d77a33bfc788d97e8d69b081f9486af74d52ca1a857`

Every aggregate below traces to `phase2b/outputs/<run_id>/evaluation.json` and `orthography.json` (paths listed in `dataset.json`).

## 2. Cross-configuration summary (direct vs primed vs mean Δ)

### canonical coverage

| configuration | direct mean (SD) | primed mean (SD) | mean Δ | SD(Δ) | Δ range |
|---|---:|---:|---:|---:|---:|
| Gemini 3.6 Flash — extended thinking ON | 68.68% (2.38) | 68.13% (0.86) | -0.55 pp | 2.91 pp | [-3.77, +1.89] pp |
| Gemini 3.6 Flash — extended thinking OFF | 67.20% (1.18) | 65.45% (4.52) | -1.75 pp | 4.38 pp | [-5.39, +3.12] pp |
| Claude Sonnet 5 — Medium (default) | 69.29% (2.46) | 83.57% (0.34) | +14.28 pp | 2.26 pp | [+12.20, +16.69] pp |
| DeepSeek V3 Expert — DeepThink ON | 74.53% (1.31) | 83.78% (1.29) | +9.25 pp | 2.57 pp | [+6.68, +11.82] pp |
| Qwen 3.8 Max — Fast | 76.36% (0.05) | 81.54% (5.57) | +5.18 pp | 5.56 pp | [-1.23, +8.70] pp |
| GPT-5.6 Luna — thinking OFF | 73.54% (1.83) | 82.16% (0.50) | +8.62 pp | 1.34 pp | [+7.06, +9.43] pp |
| Grok 4.5 Fast | 68.35% (3.95) | 82.84% (2.15) | +14.49 pp | 5.90 pp | [+8.20, +19.89] pp |

### broader resource-supported coverage

| configuration | direct mean (SD) | primed mean (SD) | mean Δ | SD(Δ) | Δ range |
|---|---:|---:|---:|---:|---:|
| Gemini 3.6 Flash — extended thinking ON | 78.05% (2.47) | 77.67% (0.63) | -0.38 pp | 2.57 pp | [-3.06, +2.06] pp |
| Gemini 3.6 Flash — extended thinking OFF | 77.24% (1.10) | 74.32% (5.05) | -2.92 pp | 4.23 pp | [-5.82, +1.93] pp |
| Claude Sonnet 5 — Medium (default) | 82.48% (1.43) | 90.11% (0.61) | +7.62 pp | 2.00 pp | [+5.88, +9.81] pp |
| DeepSeek V3 Expert — DeepThink ON | 86.17% (1.45) | 90.16% (0.94) | +4.00 pp | 2.33 pp | [+2.09, +6.60] pp |
| Qwen 3.8 Max — Fast | 84.35% (0.31) | 87.98% (3.14) | +3.63 pp | 3.17 pp | [-0.01, +5.80] pp |
| GPT-5.6 Luna — thinking OFF | 83.93% (0.70) | 89.70% (0.05) | +5.77 pp | 0.71 pp | [+5.02, +6.42] pp |
| Grok 4.5 Fast | 78.03% (3.51) | 88.63% (1.14) | +10.59 pp | 4.49 pp | [+6.00, +14.98] pp |

### unresolved rate

| configuration | direct mean (SD) | primed mean (SD) | mean Δ | SD(Δ) | Δ range |
|---|---:|---:|---:|---:|---:|
| Gemini 3.6 Flash — extended thinking ON | 31.32% (2.38) | 31.87% (0.86) | +0.55 pp | 2.91 pp | [-1.89, +3.77] pp |
| Gemini 3.6 Flash — extended thinking OFF | 32.80% (1.18) | 34.55% (4.52) | +1.75 pp | 4.38 pp | [-3.12, +5.39] pp |
| Claude Sonnet 5 — Medium (default) | 30.71% (2.46) | 16.43% (0.34) | -14.28 pp | 2.26 pp | [-16.69, -12.20] pp |
| DeepSeek V3 Expert — DeepThink ON | 25.47% (1.31) | 16.22% (1.29) | -9.25 pp | 2.57 pp | [-11.82, -6.68] pp |
| Qwen 3.8 Max — Fast | 23.64% (0.05) | 18.46% (5.57) | -5.18 pp | 5.56 pp | [-8.70, +1.23] pp |
| GPT-5.6 Luna — thinking OFF | 26.46% (1.83) | 17.84% (0.50) | -8.62 pp | 1.34 pp | [-9.43, -7.06] pp |
| Grok 4.5 Fast | 31.65% (3.95) | 17.16% (2.15) | -14.49 pp | 5.90 pp | [-19.89, -8.20] pp |

### orthography outside-inventory

| configuration | direct mean (SD) | primed mean (SD) | mean Δ | SD(Δ) | Δ range |
|---|---:|---:|---:|---:|---:|
| Gemini 3.6 Flash — extended thinking ON | 100.67 (41.00) | 123.33 (24.44) | +22.67 | 59.74 | [-24, +90] |
| Gemini 3.6 Flash — extended thinking OFF | 138.00 (69.76) | 53.00 (17.35) | -85.00 | 78.31 | [-147, +3] |
| Claude Sonnet 5 — Medium (default) | 131.67 (202.09) | 32.00 (33.29) | -99.67 | 216.02 | [-347, +52] |
| DeepSeek V3 Expert — DeepThink ON | 32.00 (7.94) | 18.00 (5.00) | -14.00 | 10.15 | [-25, -5] |
| Qwen 3.8 Max — Fast | 43.33 (12.06) | 54.33 (48.23) | +11.00 | 50.47 | [-28, +68] |
| GPT-5.6 Luna — thinking OFF | 136.67 (47.90) | 36.67 (14.50) | -100.00 | 40.15 | [-138, -58] |
| Grok 4.5 Fast | 283.67 (249.32) | 48.33 (57.83) | -235.33 | 294.05 | [-514, +72] |

## 3. Per-configuration detail (individual D / P / Δ)

Replicates are independent fresh sessions (r01–r03). Δᵢ = Pᵢ − Dᵢ for the same replicate tag.

### Gemini 3.6 Flash — extended thinking ON

Role (shortlist note): strong priming effect (large reproduced Δ)

**canonical coverage**

- Direct:  n=3  mean=68.68%  SD=2.38 pp  min=66.26%  max=71.03%
- Primed:  n=3  mean=68.13%  SD=0.86 pp  min=67.26%  max=68.98%
- Paired:  Δ r01/r02/r03 = +1.89 / -3.77 / +0.23 pp;  mean Δ=-0.55 pp  SD(Δ)=2.91 pp  range [-3.77, +1.89] pp

| rep | direct | primed | Δ | direct run_id | primed run_id |
|---|---:|---:|---:|---|---|
| r01 | 66.26% | 68.15% | +1.89 pp | `2026-09-09__p2b-high__google__gemini-3.6-flash__extthinkon__direct__r01` | `2026-09-09__p2b-high__google__gemini-3.6-flash__extthinkon__primed__r01` |
| r02 | 71.03% | 67.26% | -3.77 pp | `2026-09-09__p2b-high__google__gemini-3.6-flash__extthinkon__direct__r02` | `2026-09-09__p2b-high__google__gemini-3.6-flash__extthinkon__primed__r02` |
| r03 | 68.76% | 68.98% | +0.23 pp | `2026-09-09__p2b-high__google__gemini-3.6-flash__extthinkon__direct__r03` | `2026-09-09__p2b-high__google__gemini-3.6-flash__extthinkon__primed__r03` |

**broader resource-supported coverage**

- Direct:  n=3  mean=78.05%  SD=2.47 pp  min=75.38%  max=80.25%
- Primed:  n=3  mean=77.67%  SD=0.63 pp  min=77.19%  max=78.39%
- Paired:  Δ r01/r02/r03 = +2.06 / -3.06 / -0.14 pp;  mean Δ=-0.38 pp  SD(Δ)=2.57 pp  range [-3.06, +2.06] pp

| rep | direct | primed | Δ | direct run_id | primed run_id |
|---|---:|---:|---:|---|---|
| r01 | 75.38% | 77.44% | +2.06 pp | `2026-09-09__p2b-high__google__gemini-3.6-flash__extthinkon__direct__r01` | `2026-09-09__p2b-high__google__gemini-3.6-flash__extthinkon__primed__r01` |
| r02 | 80.25% | 77.19% | -3.06 pp | `2026-09-09__p2b-high__google__gemini-3.6-flash__extthinkon__direct__r02` | `2026-09-09__p2b-high__google__gemini-3.6-flash__extthinkon__primed__r02` |
| r03 | 78.52% | 78.39% | -0.14 pp | `2026-09-09__p2b-high__google__gemini-3.6-flash__extthinkon__direct__r03` | `2026-09-09__p2b-high__google__gemini-3.6-flash__extthinkon__primed__r03` |

**unresolved rate**

- Direct:  n=3  mean=31.32%  SD=2.38 pp  min=28.97%  max=33.74%
- Primed:  n=3  mean=31.87%  SD=0.86 pp  min=31.02%  max=32.74%
- Paired:  Δ r01/r02/r03 = -1.89 / +3.77 / -0.23 pp;  mean Δ=+0.55 pp  SD(Δ)=2.91 pp  range [-1.89, +3.77] pp

| rep | direct | primed | Δ | direct run_id | primed run_id |
|---|---:|---:|---:|---|---|
| r01 | 33.74% | 31.85% | -1.89 pp | `2026-09-09__p2b-high__google__gemini-3.6-flash__extthinkon__direct__r01` | `2026-09-09__p2b-high__google__gemini-3.6-flash__extthinkon__primed__r01` |
| r02 | 28.97% | 32.74% | +3.77 pp | `2026-09-09__p2b-high__google__gemini-3.6-flash__extthinkon__direct__r02` | `2026-09-09__p2b-high__google__gemini-3.6-flash__extthinkon__primed__r02` |
| r03 | 31.24% | 31.02% | -0.23 pp | `2026-09-09__p2b-high__google__gemini-3.6-flash__extthinkon__direct__r03` | `2026-09-09__p2b-high__google__gemini-3.6-flash__extthinkon__primed__r03` |

**orthography outside-inventory**

- Direct:  n=3  mean=100.67  SD=41.00  min=60  max=142
- Primed:  n=3  mean=123.33  SD=24.44  min=102  max=150
- Paired:  Δ r01/r02/r03 = -24 / +90 / +2;  mean Δ=+22.67  SD(Δ)=59.74  range [-24, +90]

| rep | direct | primed | Δ | direct run_id | primed run_id |
|---|---:|---:|---:|---|---|
| r01 | 142 | 118 | -24 | `2026-09-09__p2b-high__google__gemini-3.6-flash__extthinkon__direct__r01` | `2026-09-09__p2b-high__google__gemini-3.6-flash__extthinkon__primed__r01` |
| r02 | 60 | 150 | +90 | `2026-09-09__p2b-high__google__gemini-3.6-flash__extthinkon__direct__r02` | `2026-09-09__p2b-high__google__gemini-3.6-flash__extthinkon__primed__r02` |
| r03 | 100 | 102 | +2 | `2026-09-09__p2b-high__google__gemini-3.6-flash__extthinkon__direct__r03` | `2026-09-09__p2b-high__google__gemini-3.6-flash__extthinkon__primed__r03` |

### Gemini 3.6 Flash — extended thinking OFF

Role (shortlist note): strong priming effect (large reproduced Δ)

**canonical coverage**

- Direct:  n=3  mean=67.20%  SD=1.18 pp  min=65.88%  max=68.16%
- Primed:  n=3  mean=65.45%  SD=4.52 pp  min=62.77%  max=70.66%
- Paired:  Δ r01/r02/r03 = -5.39 / +3.12 / -2.98 pp;  mean Δ=-1.75 pp  SD(Δ)=4.38 pp  range [-5.39, +3.12] pp

| rep | direct | primed | Δ | direct run_id | primed run_id |
|---|---:|---:|---:|---|---|
| r01 | 68.16% | 62.77% | -5.39 pp | `2026-09-09__p2b-high__google__gemini-3.6-flash__extthinkoff__direct__r01` | `2026-09-09__p2b-high__google__gemini-3.6-flash__extthinkoff__primed__r01` |
| r02 | 67.55% | 70.66% | +3.12 pp | `2026-09-09__p2b-high__google__gemini-3.6-flash__extthinkoff__direct__r02` | `2026-09-09__p2b-high__google__gemini-3.6-flash__extthinkoff__primed__r02` |
| r03 | 65.88% | 62.90% | -2.98 pp | `2026-09-09__p2b-high__google__gemini-3.6-flash__extthinkoff__direct__r03` | `2026-09-09__p2b-high__google__gemini-3.6-flash__extthinkoff__primed__r03` |

**broader resource-supported coverage**

- Direct:  n=3  mean=77.24%  SD=1.10 pp  min=76.05%  max=78.22%
- Primed:  n=3  mean=74.32%  SD=5.05 pp  min=71.18%  max=80.15%
- Paired:  Δ r01/r02/r03 = -5.82 / +1.93 / -4.87 pp;  mean Δ=-2.92 pp  SD(Δ)=4.23 pp  range [-5.82, +1.93] pp

| rep | direct | primed | Δ | direct run_id | primed run_id |
|---|---:|---:|---:|---|---|
| r01 | 77.45% | 71.63% | -5.82 pp | `2026-09-09__p2b-high__google__gemini-3.6-flash__extthinkoff__direct__r01` | `2026-09-09__p2b-high__google__gemini-3.6-flash__extthinkoff__primed__r01` |
| r02 | 78.22% | 80.15% | +1.93 pp | `2026-09-09__p2b-high__google__gemini-3.6-flash__extthinkoff__direct__r02` | `2026-09-09__p2b-high__google__gemini-3.6-flash__extthinkoff__primed__r02` |
| r03 | 76.05% | 71.18% | -4.87 pp | `2026-09-09__p2b-high__google__gemini-3.6-flash__extthinkoff__direct__r03` | `2026-09-09__p2b-high__google__gemini-3.6-flash__extthinkoff__primed__r03` |

**unresolved rate**

- Direct:  n=3  mean=32.80%  SD=1.18 pp  min=31.84%  max=34.12%
- Primed:  n=3  mean=34.55%  SD=4.52 pp  min=29.34%  max=37.23%
- Paired:  Δ r01/r02/r03 = +5.39 / -3.12 / +2.98 pp;  mean Δ=+1.75 pp  SD(Δ)=4.38 pp  range [-3.12, +5.39] pp

| rep | direct | primed | Δ | direct run_id | primed run_id |
|---|---:|---:|---:|---|---|
| r01 | 31.84% | 37.23% | +5.39 pp | `2026-09-09__p2b-high__google__gemini-3.6-flash__extthinkoff__direct__r01` | `2026-09-09__p2b-high__google__gemini-3.6-flash__extthinkoff__primed__r01` |
| r02 | 32.45% | 29.34% | -3.12 pp | `2026-09-09__p2b-high__google__gemini-3.6-flash__extthinkoff__direct__r02` | `2026-09-09__p2b-high__google__gemini-3.6-flash__extthinkoff__primed__r02` |
| r03 | 34.12% | 37.10% | +2.98 pp | `2026-09-09__p2b-high__google__gemini-3.6-flash__extthinkoff__direct__r03` | `2026-09-09__p2b-high__google__gemini-3.6-flash__extthinkoff__primed__r03` |

**orthography outside-inventory**

- Direct:  n=3  mean=138.00  SD=69.76  min=65  max=204
- Primed:  n=3  mean=53.00  SD=17.35  min=34  max=68
- Paired:  Δ r01/r02/r03 = +3 / -111 / -147;  mean Δ=-85.00  SD(Δ)=78.31  range [-147, +3]

| rep | direct | primed | Δ | direct run_id | primed run_id |
|---|---:|---:|---:|---|---|
| r01 | 65 | 68 | +3 | `2026-09-09__p2b-high__google__gemini-3.6-flash__extthinkoff__direct__r01` | `2026-09-09__p2b-high__google__gemini-3.6-flash__extthinkoff__primed__r01` |
| r02 | 145 | 34 | -111 | `2026-09-09__p2b-high__google__gemini-3.6-flash__extthinkoff__direct__r02` | `2026-09-09__p2b-high__google__gemini-3.6-flash__extthinkoff__primed__r02` |
| r03 | 204 | 57 | -147 | `2026-09-09__p2b-high__google__gemini-3.6-flash__extthinkoff__direct__r03` | `2026-09-09__p2b-high__google__gemini-3.6-flash__extthinkoff__primed__r03` |

### Claude Sonnet 5 — Medium (default)

Role (shortlist note): stable high-performance configuration

**canonical coverage**

- Direct:  n=3  mean=69.29%  SD=2.46 pp  min=66.82%  max=71.73%
- Primed:  n=3  mean=83.57%  SD=0.34 pp  min=83.27%  max=83.93%
- Paired:  Δ r01/r02/r03 = +16.69 / +13.96 / +12.20 pp;  mean Δ=+14.28 pp  SD(Δ)=2.26 pp  range [+12.20, +16.69] pp

| rep | direct | primed | Δ | direct run_id | primed run_id |
|---|---:|---:|---:|---|---|
| r01 | 66.82% | 83.51% | +16.69 pp | `2026-09-09__p2b-high__anthropic__claude__sonnet-5__direct__r01` | `2026-09-09__p2b-high__anthropic__claude__sonnet-5__primed__r01` |
| r02 | 69.30% | 83.27% | +13.96 pp | `2026-09-09__p2b-high__anthropic__claude__sonnet-5__direct__r02` | `2026-09-09__p2b-high__anthropic__claude__sonnet-5__primed__r02` |
| r03 | 71.73% | 83.93% | +12.20 pp | `2026-09-09__p2b-high__anthropic__claude__sonnet-5__direct__r03` | `2026-09-09__p2b-high__anthropic__claude__sonnet-5__primed__r03` |

**broader resource-supported coverage**

- Direct:  n=3  mean=82.48%  SD=1.43 pp  min=80.87%  max=83.58%
- Primed:  n=3  mean=90.11%  SD=0.61 pp  min=89.46%  max=90.68%
- Paired:  Δ r01/r02/r03 = +9.81 / +5.88 / +7.19 pp;  mean Δ=+7.62 pp  SD(Δ)=2.00 pp  range [+5.88, +9.81] pp

| rep | direct | primed | Δ | direct run_id | primed run_id |
|---|---:|---:|---:|---|---|
| r01 | 80.87% | 90.68% | +9.81 pp | `2026-09-09__p2b-high__anthropic__claude__sonnet-5__direct__r01` | `2026-09-09__p2b-high__anthropic__claude__sonnet-5__primed__r01` |
| r02 | 83.58% | 89.46% | +5.88 pp | `2026-09-09__p2b-high__anthropic__claude__sonnet-5__direct__r02` | `2026-09-09__p2b-high__anthropic__claude__sonnet-5__primed__r02` |
| r03 | 82.99% | 90.18% | +7.19 pp | `2026-09-09__p2b-high__anthropic__claude__sonnet-5__direct__r03` | `2026-09-09__p2b-high__anthropic__claude__sonnet-5__primed__r03` |

**unresolved rate**

- Direct:  n=3  mean=30.71%  SD=2.46 pp  min=28.27%  max=33.18%
- Primed:  n=3  mean=16.43%  SD=0.34 pp  min=16.07%  max=16.73%
- Paired:  Δ r01/r02/r03 = -16.69 / -13.96 / -12.20 pp;  mean Δ=-14.28 pp  SD(Δ)=2.26 pp  range [-16.69, -12.20] pp

| rep | direct | primed | Δ | direct run_id | primed run_id |
|---|---:|---:|---:|---|---|
| r01 | 33.18% | 16.49% | -16.69 pp | `2026-09-09__p2b-high__anthropic__claude__sonnet-5__direct__r01` | `2026-09-09__p2b-high__anthropic__claude__sonnet-5__primed__r01` |
| r02 | 30.70% | 16.73% | -13.96 pp | `2026-09-09__p2b-high__anthropic__claude__sonnet-5__direct__r02` | `2026-09-09__p2b-high__anthropic__claude__sonnet-5__primed__r02` |
| r03 | 28.27% | 16.07% | -12.20 pp | `2026-09-09__p2b-high__anthropic__claude__sonnet-5__direct__r03` | `2026-09-09__p2b-high__anthropic__claude__sonnet-5__primed__r03` |

**orthography outside-inventory**

- Direct:  n=3  mean=131.67  SD=202.09  min=12  max=365
- Primed:  n=3  mean=32.00  SD=33.29  min=8  max=70
- Paired:  Δ r01/r02/r03 = -347 / -4 / +52;  mean Δ=-99.67  SD(Δ)=216.02  range [-347, +52]

| rep | direct | primed | Δ | direct run_id | primed run_id |
|---|---:|---:|---:|---|---|
| r01 | 365 | 18 | -347 | `2026-09-09__p2b-high__anthropic__claude__sonnet-5__direct__r01` | `2026-09-09__p2b-high__anthropic__claude__sonnet-5__primed__r01` |
| r02 | 12 | 8 | -4 | `2026-09-09__p2b-high__anthropic__claude__sonnet-5__direct__r02` | `2026-09-09__p2b-high__anthropic__claude__sonnet-5__primed__r02` |
| r03 | 18 | 70 | +52 | `2026-09-09__p2b-high__anthropic__claude__sonnet-5__direct__r03` | `2026-09-09__p2b-high__anthropic__claude__sonnet-5__primed__r03` |

### DeepSeek V3 Expert — DeepThink ON

Role (shortlist note): clean output, high baseline

**canonical coverage**

- Direct:  n=3  mean=74.53%  SD=1.31 pp  min=73.36%  max=75.94%
- Primed:  n=3  mean=83.78%  SD=1.29 pp  min=82.63%  max=85.18%
- Paired:  Δ r01/r02/r03 = +9.24 / +11.82 / +6.68 pp;  mean Δ=+9.25 pp  SD(Δ)=2.57 pp  range [+6.68, +11.82] pp

| rep | direct | primed | Δ | direct run_id | primed run_id |
|---|---:|---:|---:|---|---|
| r01 | 74.30% | 83.54% | +9.24 pp | `2026-09-09__p2b-high__deepseek__deepseek-v3-expert__deepthinkon__direct__r01` | `2026-09-09__p2b-high__deepseek__deepseek-v3-expert__deepthinkon__primed__r01` |
| r02 | 73.36% | 85.18% | +11.82 pp | `2026-09-09__p2b-high__deepseek__deepseek-v3-expert__deepthinkon__direct__r02` | `2026-09-09__p2b-high__deepseek__deepseek-v3-expert__deepthinkon__primed__r02` |
| r03 | 75.94% | 82.63% | +6.68 pp | `2026-09-09__p2b-high__deepseek__deepseek-v3-expert__deepthinkon__direct__r03` | `2026-09-09__p2b-high__deepseek__deepseek-v3-expert__deepthinkon__primed__r03` |

**broader resource-supported coverage**

- Direct:  n=3  mean=86.17%  SD=1.45 pp  min=84.65%  max=87.53%
- Primed:  n=3  mean=90.16%  SD=0.94 pp  min=89.62%  max=91.25%
- Paired:  Δ r01/r02/r03 = +3.30 / +6.60 / +2.09 pp;  mean Δ=+4.00 pp  SD(Δ)=2.33 pp  range [+2.09, +6.60] pp

| rep | direct | primed | Δ | direct run_id | primed run_id |
|---|---:|---:|---:|---|---|
| r01 | 86.31% | 89.62% | +3.30 pp | `2026-09-09__p2b-high__deepseek__deepseek-v3-expert__deepthinkon__direct__r01` | `2026-09-09__p2b-high__deepseek__deepseek-v3-expert__deepthinkon__primed__r01` |
| r02 | 84.65% | 91.25% | +6.60 pp | `2026-09-09__p2b-high__deepseek__deepseek-v3-expert__deepthinkon__direct__r02` | `2026-09-09__p2b-high__deepseek__deepseek-v3-expert__deepthinkon__primed__r02` |
| r03 | 87.53% | 89.62% | +2.09 pp | `2026-09-09__p2b-high__deepseek__deepseek-v3-expert__deepthinkon__direct__r03` | `2026-09-09__p2b-high__deepseek__deepseek-v3-expert__deepthinkon__primed__r03` |

**unresolved rate**

- Direct:  n=3  mean=25.47%  SD=1.31 pp  min=24.06%  max=26.64%
- Primed:  n=3  mean=16.22%  SD=1.29 pp  min=14.82%  max=17.37%
- Paired:  Δ r01/r02/r03 = -9.24 / -11.82 / -6.68 pp;  mean Δ=-9.25 pp  SD(Δ)=2.57 pp  range [-11.82, -6.68] pp

| rep | direct | primed | Δ | direct run_id | primed run_id |
|---|---:|---:|---:|---|---|
| r01 | 25.70% | 16.46% | -9.24 pp | `2026-09-09__p2b-high__deepseek__deepseek-v3-expert__deepthinkon__direct__r01` | `2026-09-09__p2b-high__deepseek__deepseek-v3-expert__deepthinkon__primed__r01` |
| r02 | 26.64% | 14.82% | -11.82 pp | `2026-09-09__p2b-high__deepseek__deepseek-v3-expert__deepthinkon__direct__r02` | `2026-09-09__p2b-high__deepseek__deepseek-v3-expert__deepthinkon__primed__r02` |
| r03 | 24.06% | 17.37% | -6.68 pp | `2026-09-09__p2b-high__deepseek__deepseek-v3-expert__deepthinkon__direct__r03` | `2026-09-09__p2b-high__deepseek__deepseek-v3-expert__deepthinkon__primed__r03` |

**orthography outside-inventory**

- Direct:  n=3  mean=32.00  SD=7.94  min=23  max=38
- Primed:  n=3  mean=18.00  SD=5.00  min=13  max=23
- Paired:  Δ r01/r02/r03 = -12 / -25 / -5;  mean Δ=-14.00  SD(Δ)=10.15  range [-25, -5]

| rep | direct | primed | Δ | direct run_id | primed run_id |
|---|---:|---:|---:|---|---|
| r01 | 35 | 23 | -12 | `2026-09-09__p2b-high__deepseek__deepseek-v3-expert__deepthinkon__direct__r01` | `2026-09-09__p2b-high__deepseek__deepseek-v3-expert__deepthinkon__primed__r01` |
| r02 | 38 | 13 | -25 | `2026-09-09__p2b-high__deepseek__deepseek-v3-expert__deepthinkon__direct__r02` | `2026-09-09__p2b-high__deepseek__deepseek-v3-expert__deepthinkon__primed__r02` |
| r03 | 23 | 18 | -5 | `2026-09-09__p2b-high__deepseek__deepseek-v3-expert__deepthinkon__direct__r03` | `2026-09-09__p2b-high__deepseek__deepseek-v3-expert__deepthinkon__primed__r03` |

### Qwen 3.8 Max — Fast

Role (shortlist note): small-effect/high-variance counterexample

**canonical coverage**

- Direct:  n=3  mean=76.36%  SD=0.05 pp  min=76.32%  max=76.41%
- Primed:  n=3  mean=81.54%  SD=5.57 pp  min=75.12%  max=85.11%
- Paired:  Δ r01/r02/r03 = +8.70 / +8.07 / -1.23 pp;  mean Δ=+5.18 pp  SD(Δ)=5.56 pp  range [-1.23, +8.70] pp

| rep | direct | primed | Δ | direct run_id | primed run_id |
|---|---:|---:|---:|---|---|
| r01 | 76.41% | 85.11% | +8.70 pp | `2026-09-09__p2b-high__alibaba__qwen-3.8-max__fast__direct__r01` | `2026-09-09__p2b-high__alibaba__qwen-3.8-max__fast__primed__r01` |
| r02 | 76.32% | 84.39% | +8.07 pp | `2026-09-09__p2b-high__alibaba__qwen-3.8-max__fast__direct__r02` | `2026-09-09__p2b-high__alibaba__qwen-3.8-max__fast__primed__r02` |
| r03 | 76.35% | 75.12% | -1.23 pp | `2026-09-09__p2b-high__alibaba__qwen-3.8-max__fast__direct__r03` | `2026-09-09__p2b-high__alibaba__qwen-3.8-max__fast__primed__r03` |

**broader resource-supported coverage**

- Direct:  n=3  mean=84.35%  SD=0.31 pp  min=84.04%  max=84.67%
- Primed:  n=3  mean=87.98%  SD=3.14 pp  min=84.35%  max=89.85%
- Paired:  Δ r01/r02/r03 = +5.80 / +5.08 / -0.01 pp;  mean Δ=+3.63 pp  SD(Δ)=3.17 pp  range [-0.01, +5.80] pp

| rep | direct | primed | Δ | direct run_id | primed run_id |
|---|---:|---:|---:|---|---|
| r01 | 84.04% | 89.85% | +5.80 pp | `2026-09-09__p2b-high__alibaba__qwen-3.8-max__fast__direct__r01` | `2026-09-09__p2b-high__alibaba__qwen-3.8-max__fast__primed__r01` |
| r02 | 84.67% | 89.74% | +5.08 pp | `2026-09-09__p2b-high__alibaba__qwen-3.8-max__fast__direct__r02` | `2026-09-09__p2b-high__alibaba__qwen-3.8-max__fast__primed__r02` |
| r03 | 84.36% | 84.35% | -0.01 pp | `2026-09-09__p2b-high__alibaba__qwen-3.8-max__fast__direct__r03` | `2026-09-09__p2b-high__alibaba__qwen-3.8-max__fast__primed__r03` |

**unresolved rate**

- Direct:  n=3  mean=23.64%  SD=0.05 pp  min=23.59%  max=23.68%
- Primed:  n=3  mean=18.46%  SD=5.57 pp  min=14.89%  max=24.88%
- Paired:  Δ r01/r02/r03 = -8.70 / -8.07 / +1.23 pp;  mean Δ=-5.18 pp  SD(Δ)=5.56 pp  range [-8.70, +1.23] pp

| rep | direct | primed | Δ | direct run_id | primed run_id |
|---|---:|---:|---:|---|---|
| r01 | 23.59% | 14.89% | -8.70 pp | `2026-09-09__p2b-high__alibaba__qwen-3.8-max__fast__direct__r01` | `2026-09-09__p2b-high__alibaba__qwen-3.8-max__fast__primed__r01` |
| r02 | 23.68% | 15.61% | -8.07 pp | `2026-09-09__p2b-high__alibaba__qwen-3.8-max__fast__direct__r02` | `2026-09-09__p2b-high__alibaba__qwen-3.8-max__fast__primed__r02` |
| r03 | 23.65% | 24.88% | +1.23 pp | `2026-09-09__p2b-high__alibaba__qwen-3.8-max__fast__direct__r03` | `2026-09-09__p2b-high__alibaba__qwen-3.8-max__fast__primed__r03` |

**orthography outside-inventory**

- Direct:  n=3  mean=43.33  SD=12.06  min=32  max=56
- Primed:  n=3  mean=54.33  SD=48.23  min=25  max=110
- Paired:  Δ r01/r02/r03 = -28 / -7 / +68;  mean Δ=+11.00  SD(Δ)=50.47  range [-28, +68]

| rep | direct | primed | Δ | direct run_id | primed run_id |
|---|---:|---:|---:|---|---|
| r01 | 56 | 28 | -28 | `2026-09-09__p2b-high__alibaba__qwen-3.8-max__fast__direct__r01` | `2026-09-09__p2b-high__alibaba__qwen-3.8-max__fast__primed__r01` |
| r02 | 32 | 25 | -7 | `2026-09-09__p2b-high__alibaba__qwen-3.8-max__fast__direct__r02` | `2026-09-09__p2b-high__alibaba__qwen-3.8-max__fast__primed__r02` |
| r03 | 42 | 110 | +68 | `2026-09-09__p2b-high__alibaba__qwen-3.8-max__fast__direct__r03` | `2026-09-09__p2b-high__alibaba__qwen-3.8-max__fast__primed__r03` |

### GPT-5.6 Luna — thinking OFF

Role (shortlist note): neutral general-purpose reference

**canonical coverage**

- Direct:  n=3  mean=73.54%  SD=1.83 pp  min=72.31%  max=75.65%
- Primed:  n=3  mean=82.16%  SD=0.50 pp  min=81.75%  max=82.71%
- Paired:  Δ r01/r02/r03 = +9.43 / +7.06 / +9.35 pp;  mean Δ=+8.62 pp  SD(Δ)=1.34 pp  range [+7.06, +9.43] pp

| rep | direct | primed | Δ | direct run_id | primed run_id |
|---|---:|---:|---:|---|---|
| r01 | 72.31% | 81.75% | +9.43 pp | `2026-09-09__p2b-high__openai__gpt-5.6-luna__thinkoff__direct__r01` | `2026-09-09__p2b-high__openai__gpt-5.6-luna__thinkoff__primed__r01` |
| r02 | 75.65% | 82.71% | +7.06 pp | `2026-09-09__p2b-high__openai__gpt-5.6-luna__thinkoff__direct__r02` | `2026-09-09__p2b-high__openai__gpt-5.6-luna__thinkoff__primed__r02` |
| r03 | 72.67% | 82.02% | +9.35 pp | `2026-09-09__p2b-high__openai__gpt-5.6-luna__thinkoff__direct__r03` | `2026-09-09__p2b-high__openai__gpt-5.6-luna__thinkoff__primed__r03` |

**broader resource-supported coverage**

- Direct:  n=3  mean=83.93%  SD=0.70 pp  min=83.25%  max=84.65%
- Primed:  n=3  mean=89.70%  SD=0.05 pp  min=89.67%  max=89.76%
- Paired:  Δ r01/r02/r03 = +6.42 / +5.02 / +5.87 pp;  mean Δ=+5.77 pp  SD(Δ)=0.71 pp  range [+5.02, +6.42] pp

| rep | direct | primed | Δ | direct run_id | primed run_id |
|---|---:|---:|---:|---|---|
| r01 | 83.25% | 89.67% | +6.42 pp | `2026-09-09__p2b-high__openai__gpt-5.6-luna__thinkoff__direct__r01` | `2026-09-09__p2b-high__openai__gpt-5.6-luna__thinkoff__primed__r01` |
| r02 | 84.65% | 89.67% | +5.02 pp | `2026-09-09__p2b-high__openai__gpt-5.6-luna__thinkoff__direct__r02` | `2026-09-09__p2b-high__openai__gpt-5.6-luna__thinkoff__primed__r02` |
| r03 | 83.89% | 89.76% | +5.87 pp | `2026-09-09__p2b-high__openai__gpt-5.6-luna__thinkoff__direct__r03` | `2026-09-09__p2b-high__openai__gpt-5.6-luna__thinkoff__primed__r03` |

**unresolved rate**

- Direct:  n=3  mean=26.46%  SD=1.83 pp  min=24.35%  max=27.69%
- Primed:  n=3  mean=17.84%  SD=0.50 pp  min=17.29%  max=18.25%
- Paired:  Δ r01/r02/r03 = -9.43 / -7.06 / -9.35 pp;  mean Δ=-8.62 pp  SD(Δ)=1.34 pp  range [-9.43, -7.06] pp

| rep | direct | primed | Δ | direct run_id | primed run_id |
|---|---:|---:|---:|---|---|
| r01 | 27.69% | 18.25% | -9.43 pp | `2026-09-09__p2b-high__openai__gpt-5.6-luna__thinkoff__direct__r01` | `2026-09-09__p2b-high__openai__gpt-5.6-luna__thinkoff__primed__r01` |
| r02 | 24.35% | 17.29% | -7.06 pp | `2026-09-09__p2b-high__openai__gpt-5.6-luna__thinkoff__direct__r02` | `2026-09-09__p2b-high__openai__gpt-5.6-luna__thinkoff__primed__r02` |
| r03 | 27.33% | 17.98% | -9.35 pp | `2026-09-09__p2b-high__openai__gpt-5.6-luna__thinkoff__direct__r03` | `2026-09-09__p2b-high__openai__gpt-5.6-luna__thinkoff__primed__r03` |

**orthography outside-inventory**

- Direct:  n=3  mean=136.67  SD=47.90  min=95  max=189
- Primed:  n=3  mean=36.67  SD=14.50  min=22  max=51
- Paired:  Δ r01/r02/r03 = -138 / -104 / -58;  mean Δ=-100.00  SD(Δ)=40.15  range [-138, -58]

| rep | direct | primed | Δ | direct run_id | primed run_id |
|---|---:|---:|---:|---|---|
| r01 | 189 | 51 | -138 | `2026-09-09__p2b-high__openai__gpt-5.6-luna__thinkoff__direct__r01` | `2026-09-09__p2b-high__openai__gpt-5.6-luna__thinkoff__primed__r01` |
| r02 | 126 | 22 | -104 | `2026-09-09__p2b-high__openai__gpt-5.6-luna__thinkoff__direct__r02` | `2026-09-09__p2b-high__openai__gpt-5.6-luna__thinkoff__primed__r02` |
| r03 | 95 | 37 | -58 | `2026-09-09__p2b-high__openai__gpt-5.6-luna__thinkoff__direct__r03` | `2026-09-09__p2b-high__openai__gpt-5.6-luna__thinkoff__primed__r03` |

### Grok 4.5 Fast

Role (shortlist note): independent model-family reference; operator-reported identity

**canonical coverage**

- Direct:  n=3  mean=68.35%  SD=3.95 pp  min=64.27%  max=72.15%
- Primed:  n=3  mean=82.84%  SD=2.15 pp  min=80.36%  max=84.17%
- Paired:  Δ r01/r02/r03 = +15.37 / +19.89 / +8.20 pp;  mean Δ=+14.49 pp  SD(Δ)=5.90 pp  range [+8.20, +19.89] pp

| rep | direct | primed | Δ | direct run_id | primed run_id |
|---|---:|---:|---:|---|---|
| r01 | 68.62% | 83.99% | +15.37 pp | `2026-09-09__p2b-high__xai__grok__fast__direct__r01` | `2026-09-09__p2b-high__xai__grok__fast__primed__r01` |
| r02 | 64.27% | 84.17% | +19.89 pp | `2026-09-09__p2b-high__xai__grok__fast__direct__r02` | `2026-09-09__p2b-high__xai__grok__fast__primed__r02` |
| r03 | 72.15% | 80.36% | +8.20 pp | `2026-09-09__p2b-high__xai__grok__fast__direct__r03` | `2026-09-09__p2b-high__xai__grok__fast__primed__r03` |

**broader resource-supported coverage**

- Direct:  n=3  mean=78.03%  SD=3.51 pp  min=74.32%  max=81.30%
- Primed:  n=3  mean=88.63%  SD=1.14 pp  min=87.31%  max=89.29%
- Paired:  Δ r01/r02/r03 = +10.81 / +14.98 / +6.00 pp;  mean Δ=+10.59 pp  SD(Δ)=4.49 pp  range [+6.00, +14.98] pp

| rep | direct | primed | Δ | direct run_id | primed run_id |
|---|---:|---:|---:|---|---|
| r01 | 78.48% | 89.28% | +10.81 pp | `2026-09-09__p2b-high__xai__grok__fast__direct__r01` | `2026-09-09__p2b-high__xai__grok__fast__primed__r01` |
| r02 | 74.32% | 89.29% | +14.98 pp | `2026-09-09__p2b-high__xai__grok__fast__direct__r02` | `2026-09-09__p2b-high__xai__grok__fast__primed__r02` |
| r03 | 81.30% | 87.31% | +6.00 pp | `2026-09-09__p2b-high__xai__grok__fast__direct__r03` | `2026-09-09__p2b-high__xai__grok__fast__primed__r03` |

**unresolved rate**

- Direct:  n=3  mean=31.65%  SD=3.95 pp  min=27.85%  max=35.73%
- Primed:  n=3  mean=17.16%  SD=2.15 pp  min=15.83%  max=19.64%
- Paired:  Δ r01/r02/r03 = -15.37 / -19.89 / -8.20 pp;  mean Δ=-14.49 pp  SD(Δ)=5.90 pp  range [-19.89, -8.20] pp

| rep | direct | primed | Δ | direct run_id | primed run_id |
|---|---:|---:|---:|---|---|
| r01 | 31.38% | 16.01% | -15.37 pp | `2026-09-09__p2b-high__xai__grok__fast__direct__r01` | `2026-09-09__p2b-high__xai__grok__fast__primed__r01` |
| r02 | 35.73% | 15.83% | -19.89 pp | `2026-09-09__p2b-high__xai__grok__fast__direct__r02` | `2026-09-09__p2b-high__xai__grok__fast__primed__r02` |
| r03 | 27.85% | 19.64% | -8.20 pp | `2026-09-09__p2b-high__xai__grok__fast__direct__r03` | `2026-09-09__p2b-high__xai__grok__fast__primed__r03` |

**orthography outside-inventory**

- Direct:  n=3  mean=283.67  SD=249.32  min=42  max=540
- Primed:  n=3  mean=48.33  SD=57.83  min=5  max=114
- Paired:  Δ r01/r02/r03 = -264 / -514 / +72;  mean Δ=-235.33  SD(Δ)=294.05  range [-514, +72]

| rep | direct | primed | Δ | direct run_id | primed run_id |
|---|---:|---:|---:|---|---|
| r01 | 269 | 5 | -264 | `2026-09-09__p2b-high__xai__grok__fast__direct__r01` | `2026-09-09__p2b-high__xai__grok__fast__primed__r01` |
| r02 | 540 | 26 | -514 | `2026-09-09__p2b-high__xai__grok__fast__direct__r02` | `2026-09-09__p2b-high__xai__grok__fast__primed__r02` |
| r03 | 42 | 114 | +72 | `2026-09-09__p2b-high__xai__grok__fast__direct__r03` | `2026-09-09__p2b-high__xai__grok__fast__primed__r03` |

## 4. Observations about distribution and variance

- Each cell has **n = 3**. Means and SDs are small-sample descriptive quantities; ranges of the three replicates are the clearest variance signal.
- Individual replicate Δ values are reported above so that a large mean Δ driven by a single replicate remains visible.
- Across the 7 configurations, mean canonical Δ is **+7.07 pp** (positive in 5/7, negative in 2/7). This is a descriptive cross-config summary only.
- Orthography outside-inventory is a character-level count (not a coverage rate); interpret separately from canonical/broader/unresolved.
- Unresolved rate moves inversely with coverage by construction of the evaluator (unresolved ≈ 1 − canonical under the lexical-token denominator); report both, do not invent a composite.

## 5. Clear statement on n = 3

n = 3 replicates per configuration/condition. Results are descriptive replication/variance characterizations. Do not treat mean Δ as a statistically established effect.

No significance tests were run. No causal claim about corpus priming is made in this artifact. A later bounded task may interpret these descriptive results against Phase-2A / repeats.

## 6. Anomalies worth investigating

- Gemini 3.6 Flash — extended thinking ON: canonical replicate Δs have mixed signs (+1.89, -3.77, +0.23 pp) — mean Δ alone is misleading.
- Gemini 3.6 Flash — extended thinking ON: direct canonical SD (2.38 pp) exceeds |mean Δ| (0.55 pp).
- Gemini 3.6 Flash — extended thinking ON: primed canonical SD (0.86 pp) exceeds |mean Δ| (0.55 pp).
- Gemini 3.6 Flash — extended thinking OFF: canonical replicate Δs have mixed signs (-5.39, +3.12, -2.98 pp) — mean Δ alone is misleading.
- Gemini 3.6 Flash — extended thinking OFF: primed canonical SD (4.52 pp) exceeds |mean Δ| (1.75 pp).
- Qwen 3.8 Max — Fast: canonical replicate Δs have mixed signs (+8.70, +8.07, -1.23 pp) — mean Δ alone is misleading.
- Qwen 3.8 Max — Fast: primed canonical SD (5.57 pp) exceeds |mean Δ| (5.18 pp).

## 7. Files

| file | role |
|---|---|
| `dataset.json` | machine-readable observations + per-config stats + paired Δ (traceable to run artifacts) |
| `analysis.json` | summary tables + distribution notes |
| `analysis.md` | this report |

