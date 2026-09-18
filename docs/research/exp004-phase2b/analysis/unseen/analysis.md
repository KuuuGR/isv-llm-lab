# EXP-004 Phase 2B UNSEEN — aggregate analysis (descriptive)

**Status:** results written from 42 verified + evaluated runs.
**Generator:** `scripts/analyze_exp004_phase2b.py` (deterministic;
std-lib only; never calls an LLM).

> **n = 3** replicates per configuration/condition. This report is
> a **descriptive** paired summary of observed values. It does
> **not** establish statistical significance, does **not** claim
> causal corpus-priming effects, and does **not** rank models.

## 1. Data-integrity checks

Overall: **PASS** (42 observations collected, 7 planned configurations; primary valid pairs = 7).

| check | result |
|---|---|
| `exactly_42_evaluated` | yes |
| `exactly_7_configurations` | yes |
| `no_duplicate_run_ids` | yes |
| `three_direct_three_primed_per_config` | yes |
| `every_direct_has_matching_primed_replicate` | yes |
| `all_usable_complete` | yes |

Provenance pins (from plan):
- UNSEEN story SHA-256: `cd3bfb9a819b415e3cfb382e0737ba22540ccb679d0d34983c40dfbf89a9f7f4`
- corpus SHA-256: `aaad28e43935a40313585d77a33bfc788d97e8d69b081f9486af74d52ca1a857`

Every aggregate below traces to `phase2b/outputs/<run_id>/evaluation.json` and `orthography.json` (paths listed in `dataset.json`).

## 2. Cross-configuration summary (primary valid pairs only; n=7)

### canonical coverage

| configuration | direct mean (SD) | primed mean (SD) | mean Δ | SD(Δ) | Δ range |
|---|---:|---:|---:|---:|---:|
| Gemini 3.6 Flash — extended thinking ON | 65.77% (0.95) | 71.45% (2.86) | +5.68 pp | 3.38 pp | [+2.12, +8.84] pp |
| Gemini 3.6 Flash — extended thinking OFF | 63.85% (1.37) | 69.95% (1.02) | +6.09 pp | 2.02 pp | [+3.96, +7.97] pp |
| Claude Sonnet 5 — Medium (default) | 66.07% (0.19) | 72.48% (1.29) | +6.42 pp | 1.11 pp | [+5.14, +7.14] pp |
| DeepSeek V3 Expert — DeepThink ON | 67.97% (1.23) | 71.80% (1.64) | +3.83 pp | 1.06 pp | [+2.91, +5.00] pp |
| Qwen 3.8 Max — Fast | 67.65% (0.70) | 71.17% (1.54) | +3.52 pp | 2.18 pp | [+1.27, +5.62] pp |
| GPT-5.6 Luna — thinking OFF | 68.53% (2.85) | 74.05% (1.39) | +5.52 pp | 2.73 pp | [+2.43, +7.58] pp |
| Grok 4.5 Fast | 65.90% (1.44) | 73.02% (1.71) | +7.12 pp | 2.17 pp | [+5.70, +9.62] pp |

### broader resource-supported coverage

| configuration | direct mean (SD) | primed mean (SD) | mean Δ | SD(Δ) | Δ range |
|---|---:|---:|---:|---:|---:|
| Gemini 3.6 Flash — extended thinking ON | 76.38% (1.25) | 79.82% (3.48) | +3.44 pp | 2.55 pp | [+0.80, +5.89] pp |
| Gemini 3.6 Flash — extended thinking OFF | 73.03% (2.52) | 80.62% (1.27) | +7.59 pp | 2.97 pp | [+5.74, +11.02] pp |
| Claude Sonnet 5 — Medium (default) | 76.60% (1.17) | 83.12% (0.64) | +6.52 pp | 0.80 pp | [+5.65, +7.25] pp |
| DeepSeek V3 Expert — DeepThink ON | 80.13% (0.90) | 83.17% (1.47) | +3.04 pp | 0.61 pp | [+2.33, +3.46] pp |
| Qwen 3.8 Max — Fast | 79.25% (2.41) | 81.60% (1.87) | +2.35 pp | 4.08 pp | [-2.31, +5.27] pp |
| GPT-5.6 Luna — thinking OFF | 78.89% (4.32) | 82.49% (1.49) | +3.60 pp | 5.05 pp | [-2.20, +6.99] pp |
| Grok 4.5 Fast | 76.10% (0.98) | 80.93% (1.78) | +4.83 pp | 2.04 pp | [+3.55, +7.18] pp |

### unresolved rate

| configuration | direct mean (SD) | primed mean (SD) | mean Δ | SD(Δ) | Δ range |
|---|---:|---:|---:|---:|---:|
| Gemini 3.6 Flash — extended thinking ON | 34.23% (0.95) | 28.55% (2.86) | -5.68 pp | 3.38 pp | [-8.84, -2.12] pp |
| Gemini 3.6 Flash — extended thinking OFF | 36.15% (1.37) | 30.05% (1.02) | -6.09 pp | 2.02 pp | [-7.97, -3.96] pp |
| Claude Sonnet 5 — Medium (default) | 33.93% (0.19) | 27.52% (1.29) | -6.42 pp | 1.11 pp | [-7.14, -5.14] pp |
| DeepSeek V3 Expert — DeepThink ON | 32.03% (1.23) | 28.20% (1.64) | -3.83 pp | 1.06 pp | [-5.00, -2.91] pp |
| Qwen 3.8 Max — Fast | 32.35% (0.70) | 28.83% (1.54) | -3.52 pp | 2.18 pp | [-5.62, -1.27] pp |
| GPT-5.6 Luna — thinking OFF | 31.47% (2.85) | 25.95% (1.39) | -5.52 pp | 2.73 pp | [-7.58, -2.43] pp |
| Grok 4.5 Fast | 34.10% (1.44) | 26.98% (1.71) | -7.12 pp | 2.17 pp | [-9.62, -5.70] pp |

### orthography outside-inventory

| configuration | direct mean (SD) | primed mean (SD) | mean Δ | SD(Δ) | Δ range |
|---|---:|---:|---:|---:|---:|
| Gemini 3.6 Flash — extended thinking ON | 24.00 (8.00) | 22.00 (6.08) | -2.00 | 4.58 | [-6, +3] |
| Gemini 3.6 Flash — extended thinking OFF | 31.00 (15.10) | 18.67 (6.43) | -12.33 | 9.02 | [-21, -3] |
| Claude Sonnet 5 — Medium (default) | 24.00 (2.65) | 19.33 (8.62) | -4.67 | 10.50 | [-15, +6] |
| DeepSeek V3 Expert — DeepThink ON | 17.00 (4.36) | 14.33 (0.58) | -2.67 | 4.73 | [-8, +1] |
| Qwen 3.8 Max — Fast | 21.67 (0.58) | 21.00 (1.73) | -0.67 | 1.53 | [-2, +1] |
| GPT-5.6 Luna — thinking OFF | 28.00 (13.11) | 28.33 (21.36) | +0.33 | 13.58 | [-14, +13] |
| Grok 4.5 Fast | 15.00 (1.73) | 19.33 (6.11) | +4.33 | 4.93 | [+1, +10] |

**Overall descriptive mean Δ (canonical)** across **n=7 valid configurations**: +5.45 pp (7 positive / 0 negative).

## 3. Per-configuration detail (individual D / P / Δ)

Replicates are independent fresh sessions (r01–r03). Δᵢ = Pᵢ − Dᵢ for the same replicate tag.

### 3a. Primary valid configurations

### Gemini 3.6 Flash — extended thinking ON

Role (shortlist note): strong priming effect (large reproduced Δ)

**canonical coverage**

- Direct:  n=3  mean=65.77%  SD=0.95 pp  min=64.87%  max=66.77%
- Primed:  n=3  mean=71.45%  SD=2.86 pp  min=68.89%  max=74.53%
- Paired:  Δ r01/r02/r03 = +2.12 / +6.08 / +8.84 pp;  mean Δ=+5.68 pp  SD(Δ)=3.38 pp  range [+2.12, +8.84] pp

| rep | direct | primed | Δ | direct run_id | primed run_id |
|---|---:|---:|---:|---|---|
| r01 | 66.77% | 68.89% | +2.12 pp | `2026-09-16__p2b-unseen__google__gemini-3.6-flash__extthinkon__direct__r01` | `2026-09-16__p2b-unseen__google__gemini-3.6-flash__extthinkon__primed__r01` |
| r02 | 64.87% | 70.95% | +6.08 pp | `2026-09-16__p2b-unseen__google__gemini-3.6-flash__extthinkon__direct__r02` | `2026-09-16__p2b-unseen__google__gemini-3.6-flash__extthinkon__primed__r02` |
| r03 | 65.68% | 74.53% | +8.84 pp | `2026-09-16__p2b-unseen__google__gemini-3.6-flash__extthinkon__direct__r03` | `2026-09-16__p2b-unseen__google__gemini-3.6-flash__extthinkon__primed__r03` |

**broader resource-supported coverage**

- Direct:  n=3  mean=76.38%  SD=1.25 pp  min=75.34%  max=77.76%
- Primed:  n=3  mean=79.82%  SD=3.48 pp  min=76.85%  max=83.65%
- Paired:  Δ r01/r02/r03 = +0.80 / +3.64 / +5.89 pp;  mean Δ=+3.44 pp  SD(Δ)=2.55 pp  range [+0.80, +5.89] pp

| rep | direct | primed | Δ | direct run_id | primed run_id |
|---|---:|---:|---:|---|---|
| r01 | 76.05% | 76.85% | +0.80 pp | `2026-09-16__p2b-unseen__google__gemini-3.6-flash__extthinkon__direct__r01` | `2026-09-16__p2b-unseen__google__gemini-3.6-flash__extthinkon__primed__r01` |
| r02 | 75.34% | 78.98% | +3.64 pp | `2026-09-16__p2b-unseen__google__gemini-3.6-flash__extthinkon__direct__r02` | `2026-09-16__p2b-unseen__google__gemini-3.6-flash__extthinkon__primed__r02` |
| r03 | 77.76% | 83.65% | +5.89 pp | `2026-09-16__p2b-unseen__google__gemini-3.6-flash__extthinkon__direct__r03` | `2026-09-16__p2b-unseen__google__gemini-3.6-flash__extthinkon__primed__r03` |

**unresolved rate**

- Direct:  n=3  mean=34.23%  SD=0.95 pp  min=33.23%  max=35.13%
- Primed:  n=3  mean=28.55%  SD=2.86 pp  min=25.47%  max=31.11%
- Paired:  Δ r01/r02/r03 = -2.12 / -6.08 / -8.84 pp;  mean Δ=-5.68 pp  SD(Δ)=3.38 pp  range [-8.84, -2.12] pp

| rep | direct | primed | Δ | direct run_id | primed run_id |
|---|---:|---:|---:|---|---|
| r01 | 33.23% | 31.11% | -2.12 pp | `2026-09-16__p2b-unseen__google__gemini-3.6-flash__extthinkon__direct__r01` | `2026-09-16__p2b-unseen__google__gemini-3.6-flash__extthinkon__primed__r01` |
| r02 | 35.13% | 29.05% | -6.08 pp | `2026-09-16__p2b-unseen__google__gemini-3.6-flash__extthinkon__direct__r02` | `2026-09-16__p2b-unseen__google__gemini-3.6-flash__extthinkon__primed__r02` |
| r03 | 34.32% | 25.47% | -8.84 pp | `2026-09-16__p2b-unseen__google__gemini-3.6-flash__extthinkon__direct__r03` | `2026-09-16__p2b-unseen__google__gemini-3.6-flash__extthinkon__primed__r03` |

**orthography outside-inventory**

- Direct:  n=3  mean=24.00  SD=8.00  min=16  max=32
- Primed:  n=3  mean=22.00  SD=6.08  min=18  max=29
- Paired:  Δ r01/r02/r03 = +3 / -3 / -6;  mean Δ=-2.00  SD(Δ)=4.58  range [-6, +3]

| rep | direct | primed | Δ | direct run_id | primed run_id |
|---|---:|---:|---:|---|---|
| r01 | 16 | 19 | +3 | `2026-09-16__p2b-unseen__google__gemini-3.6-flash__extthinkon__direct__r01` | `2026-09-16__p2b-unseen__google__gemini-3.6-flash__extthinkon__primed__r01` |
| r02 | 32 | 29 | -3 | `2026-09-16__p2b-unseen__google__gemini-3.6-flash__extthinkon__direct__r02` | `2026-09-16__p2b-unseen__google__gemini-3.6-flash__extthinkon__primed__r02` |
| r03 | 24 | 18 | -6 | `2026-09-16__p2b-unseen__google__gemini-3.6-flash__extthinkon__direct__r03` | `2026-09-16__p2b-unseen__google__gemini-3.6-flash__extthinkon__primed__r03` |

### Gemini 3.6 Flash — extended thinking OFF

Role (shortlist note): strong priming effect (large reproduced Δ)

**canonical coverage**

- Direct:  n=3  mean=63.85%  SD=1.37 pp  min=62.30%  max=64.84%
- Primed:  n=3  mean=69.95%  SD=1.02 pp  min=68.80%  max=70.78%
- Paired:  Δ r01/r02/r03 = +7.97 / +3.96 / +6.35 pp;  mean Δ=+6.09 pp  SD(Δ)=2.02 pp  range [+3.96, +7.97] pp

| rep | direct | primed | Δ | direct run_id | primed run_id |
|---|---:|---:|---:|---|---|
| r01 | 62.30% | 70.27% | +7.97 pp | `2026-09-16__p2b-unseen__google__gemini-3.6-flash__extthinkoff__direct__r01` | `2026-09-16__p2b-unseen__google__gemini-3.6-flash__extthinkoff__primed__r01` |
| r02 | 64.84% | 68.80% | +3.96 pp | `2026-09-16__p2b-unseen__google__gemini-3.6-flash__extthinkoff__direct__r02` | `2026-09-16__p2b-unseen__google__gemini-3.6-flash__extthinkoff__primed__r02` |
| r03 | 64.42% | 70.78% | +6.35 pp | `2026-09-16__p2b-unseen__google__gemini-3.6-flash__extthinkoff__direct__r03` | `2026-09-16__p2b-unseen__google__gemini-3.6-flash__extthinkoff__primed__r03` |

**broader resource-supported coverage**

- Direct:  n=3  mean=73.03%  SD=2.52 pp  min=70.34%  max=75.34%
- Primed:  n=3  mean=80.62%  SD=1.27 pp  min=79.15%  max=81.36%
- Paired:  Δ r01/r02/r03 = +11.02 / +5.74 / +6.01 pp;  mean Δ=+7.59 pp  SD(Δ)=2.97 pp  range [+5.74, +11.02] pp

| rep | direct | primed | Δ | direct run_id | primed run_id |
|---|---:|---:|---:|---|---|
| r01 | 70.34% | 81.36% | +11.02 pp | `2026-09-16__p2b-unseen__google__gemini-3.6-flash__extthinkoff__direct__r01` | `2026-09-16__p2b-unseen__google__gemini-3.6-flash__extthinkoff__primed__r01` |
| r02 | 73.41% | 79.15% | +5.74 pp | `2026-09-16__p2b-unseen__google__gemini-3.6-flash__extthinkoff__direct__r02` | `2026-09-16__p2b-unseen__google__gemini-3.6-flash__extthinkoff__primed__r02` |
| r03 | 75.34% | 81.35% | +6.01 pp | `2026-09-16__p2b-unseen__google__gemini-3.6-flash__extthinkoff__direct__r03` | `2026-09-16__p2b-unseen__google__gemini-3.6-flash__extthinkoff__primed__r03` |

**unresolved rate**

- Direct:  n=3  mean=36.15%  SD=1.37 pp  min=35.16%  max=37.70%
- Primed:  n=3  mean=30.05%  SD=1.02 pp  min=29.22%  max=31.20%
- Paired:  Δ r01/r02/r03 = -7.97 / -3.96 / -6.35 pp;  mean Δ=-6.09 pp  SD(Δ)=2.02 pp  range [-7.97, -3.96] pp

| rep | direct | primed | Δ | direct run_id | primed run_id |
|---|---:|---:|---:|---|---|
| r01 | 37.70% | 29.73% | -7.97 pp | `2026-09-16__p2b-unseen__google__gemini-3.6-flash__extthinkoff__direct__r01` | `2026-09-16__p2b-unseen__google__gemini-3.6-flash__extthinkoff__primed__r01` |
| r02 | 35.16% | 31.20% | -3.96 pp | `2026-09-16__p2b-unseen__google__gemini-3.6-flash__extthinkoff__direct__r02` | `2026-09-16__p2b-unseen__google__gemini-3.6-flash__extthinkoff__primed__r02` |
| r03 | 35.58% | 29.22% | -6.35 pp | `2026-09-16__p2b-unseen__google__gemini-3.6-flash__extthinkoff__direct__r03` | `2026-09-16__p2b-unseen__google__gemini-3.6-flash__extthinkoff__primed__r03` |

**orthography outside-inventory**

- Direct:  n=3  mean=31.00  SD=15.10  min=17  max=47
- Primed:  n=3  mean=18.67  SD=6.43  min=14  max=26
- Paired:  Δ r01/r02/r03 = -3 / -21 / -13;  mean Δ=-12.33  SD(Δ)=9.02  range [-21, -3]

| rep | direct | primed | Δ | direct run_id | primed run_id |
|---|---:|---:|---:|---|---|
| r01 | 17 | 14 | -3 | `2026-09-16__p2b-unseen__google__gemini-3.6-flash__extthinkoff__direct__r01` | `2026-09-16__p2b-unseen__google__gemini-3.6-flash__extthinkoff__primed__r01` |
| r02 | 47 | 26 | -21 | `2026-09-16__p2b-unseen__google__gemini-3.6-flash__extthinkoff__direct__r02` | `2026-09-16__p2b-unseen__google__gemini-3.6-flash__extthinkoff__primed__r02` |
| r03 | 29 | 16 | -13 | `2026-09-16__p2b-unseen__google__gemini-3.6-flash__extthinkoff__direct__r03` | `2026-09-16__p2b-unseen__google__gemini-3.6-flash__extthinkoff__primed__r03` |

### Claude Sonnet 5 — Medium (default)

Role (shortlist note): stable high-performance configuration

**canonical coverage**

- Direct:  n=3  mean=66.07%  SD=0.19 pp  min=65.86%  max=66.22%
- Primed:  n=3  mean=72.48%  SD=1.29 pp  min=71.00%  max=73.36%
- Paired:  Δ r01/r02/r03 = +7.14 / +5.14 / +6.96 pp;  mean Δ=+6.42 pp  SD(Δ)=1.11 pp  range [+5.14, +7.14] pp

| rep | direct | primed | Δ | direct run_id | primed run_id |
|---|---:|---:|---:|---|---|
| r01 | 66.22% | 73.36% | +7.14 pp | `2026-09-16__p2b-unseen__anthropic__claude__sonnet-5__direct__r01` | `2026-09-16__p2b-unseen__anthropic__claude__sonnet-5__primed__r01` |
| r02 | 65.86% | 71.00% | +5.14 pp | `2026-09-16__p2b-unseen__anthropic__claude__sonnet-5__direct__r02` | `2026-09-16__p2b-unseen__anthropic__claude__sonnet-5__primed__r02` |
| r03 | 66.12% | 73.08% | +6.96 pp | `2026-09-16__p2b-unseen__anthropic__claude__sonnet-5__direct__r03` | `2026-09-16__p2b-unseen__anthropic__claude__sonnet-5__primed__r03` |

**broader resource-supported coverage**

- Direct:  n=3  mean=76.60%  SD=1.17 pp  min=75.27%  max=77.41%
- Primed:  n=3  mean=83.12%  SD=0.64 pp  min=82.51%  max=83.78%
- Paired:  Δ r01/r02/r03 = +6.65 / +7.25 / +5.65 pp;  mean Δ=+6.52 pp  SD(Δ)=0.80 pp  range [+5.65, +7.25] pp

| rep | direct | primed | Δ | direct run_id | primed run_id |
|---|---:|---:|---:|---|---|
| r01 | 77.13% | 83.78% | +6.65 pp | `2026-09-16__p2b-unseen__anthropic__claude__sonnet-5__direct__r01` | `2026-09-16__p2b-unseen__anthropic__claude__sonnet-5__primed__r01` |
| r02 | 75.27% | 82.51% | +7.25 pp | `2026-09-16__p2b-unseen__anthropic__claude__sonnet-5__direct__r02` | `2026-09-16__p2b-unseen__anthropic__claude__sonnet-5__primed__r02` |
| r03 | 77.41% | 83.07% | +5.65 pp | `2026-09-16__p2b-unseen__anthropic__claude__sonnet-5__direct__r03` | `2026-09-16__p2b-unseen__anthropic__claude__sonnet-5__primed__r03` |

**unresolved rate**

- Direct:  n=3  mean=33.93%  SD=0.19 pp  min=33.78%  max=34.14%
- Primed:  n=3  mean=27.52%  SD=1.29 pp  min=26.64%  max=29.00%
- Paired:  Δ r01/r02/r03 = -7.14 / -5.14 / -6.96 pp;  mean Δ=-6.42 pp  SD(Δ)=1.11 pp  range [-7.14, -5.14] pp

| rep | direct | primed | Δ | direct run_id | primed run_id |
|---|---:|---:|---:|---|---|
| r01 | 33.78% | 26.64% | -7.14 pp | `2026-09-16__p2b-unseen__anthropic__claude__sonnet-5__direct__r01` | `2026-09-16__p2b-unseen__anthropic__claude__sonnet-5__primed__r01` |
| r02 | 34.14% | 29.00% | -5.14 pp | `2026-09-16__p2b-unseen__anthropic__claude__sonnet-5__direct__r02` | `2026-09-16__p2b-unseen__anthropic__claude__sonnet-5__primed__r02` |
| r03 | 33.88% | 26.92% | -6.96 pp | `2026-09-16__p2b-unseen__anthropic__claude__sonnet-5__direct__r03` | `2026-09-16__p2b-unseen__anthropic__claude__sonnet-5__primed__r03` |

**orthography outside-inventory**

- Direct:  n=3  mean=24.00  SD=2.65  min=21  max=26
- Primed:  n=3  mean=19.33  SD=8.62  min=10  max=27
- Paired:  Δ r01/r02/r03 = -5 / -15 / +6;  mean Δ=-4.67  SD(Δ)=10.50  range [-15, +6]

| rep | direct | primed | Δ | direct run_id | primed run_id |
|---|---:|---:|---:|---|---|
| r01 | 26 | 21 | -5 | `2026-09-16__p2b-unseen__anthropic__claude__sonnet-5__direct__r01` | `2026-09-16__p2b-unseen__anthropic__claude__sonnet-5__primed__r01` |
| r02 | 25 | 10 | -15 | `2026-09-16__p2b-unseen__anthropic__claude__sonnet-5__direct__r02` | `2026-09-16__p2b-unseen__anthropic__claude__sonnet-5__primed__r02` |
| r03 | 21 | 27 | +6 | `2026-09-16__p2b-unseen__anthropic__claude__sonnet-5__direct__r03` | `2026-09-16__p2b-unseen__anthropic__claude__sonnet-5__primed__r03` |

### DeepSeek V3 Expert — DeepThink ON

Role (shortlist note): clean output, high baseline

**canonical coverage**

- Direct:  n=3  mean=67.97%  SD=1.23 pp  min=66.57%  max=68.90%
- Primed:  n=3  mean=71.80%  SD=1.64 pp  min=70.15%  max=73.43%
- Paired:  Δ r01/r02/r03 = +2.91 / +5.00 / +3.58 pp;  mean Δ=+3.83 pp  SD(Δ)=1.06 pp  range [+2.91, +5.00] pp

| rep | direct | primed | Δ | direct run_id | primed run_id |
|---|---:|---:|---:|---|---|
| r01 | 68.90% | 71.81% | +2.91 pp | `2026-09-16__p2b-unseen__deepseek__deepseek-v3-expert__deepthinkon__direct__r01` | `2026-09-16__p2b-unseen__deepseek__deepseek-v3-expert__deepthinkon__primed__r01` |
| r02 | 68.44% | 73.43% | +5.00 pp | `2026-09-16__p2b-unseen__deepseek__deepseek-v3-expert__deepthinkon__direct__r02` | `2026-09-16__p2b-unseen__deepseek__deepseek-v3-expert__deepthinkon__primed__r02` |
| r03 | 66.57% | 70.15% | +3.58 pp | `2026-09-16__p2b-unseen__deepseek__deepseek-v3-expert__deepthinkon__direct__r03` | `2026-09-16__p2b-unseen__deepseek__deepseek-v3-expert__deepthinkon__primed__r03` |

**broader resource-supported coverage**

- Direct:  n=3  mean=80.13%  SD=0.90 pp  min=79.16%  max=80.95%
- Primed:  n=3  mean=83.17%  SD=1.47 pp  min=81.49%  max=84.27%
- Paired:  Δ r01/r02/r03 = +3.32 / +3.46 / +2.33 pp;  mean Δ=+3.04 pp  SD(Δ)=0.61 pp  range [+2.33, +3.46] pp

| rep | direct | primed | Δ | direct run_id | primed run_id |
|---|---:|---:|---:|---|---|
| r01 | 80.95% | 84.27% | +3.32 pp | `2026-09-16__p2b-unseen__deepseek__deepseek-v3-expert__deepthinkon__direct__r01` | `2026-09-16__p2b-unseen__deepseek__deepseek-v3-expert__deepthinkon__primed__r01` |
| r02 | 80.27% | 83.73% | +3.46 pp | `2026-09-16__p2b-unseen__deepseek__deepseek-v3-expert__deepthinkon__direct__r02` | `2026-09-16__p2b-unseen__deepseek__deepseek-v3-expert__deepthinkon__primed__r02` |
| r03 | 79.16% | 81.49% | +2.33 pp | `2026-09-16__p2b-unseen__deepseek__deepseek-v3-expert__deepthinkon__direct__r03` | `2026-09-16__p2b-unseen__deepseek__deepseek-v3-expert__deepthinkon__primed__r03` |

**unresolved rate**

- Direct:  n=3  mean=32.03%  SD=1.23 pp  min=31.10%  max=33.43%
- Primed:  n=3  mean=28.20%  SD=1.64 pp  min=26.57%  max=29.85%
- Paired:  Δ r01/r02/r03 = -2.91 / -5.00 / -3.58 pp;  mean Δ=-3.83 pp  SD(Δ)=1.06 pp  range [-5.00, -2.91] pp

| rep | direct | primed | Δ | direct run_id | primed run_id |
|---|---:|---:|---:|---|---|
| r01 | 31.10% | 28.19% | -2.91 pp | `2026-09-16__p2b-unseen__deepseek__deepseek-v3-expert__deepthinkon__direct__r01` | `2026-09-16__p2b-unseen__deepseek__deepseek-v3-expert__deepthinkon__primed__r01` |
| r02 | 31.56% | 26.57% | -5.00 pp | `2026-09-16__p2b-unseen__deepseek__deepseek-v3-expert__deepthinkon__direct__r02` | `2026-09-16__p2b-unseen__deepseek__deepseek-v3-expert__deepthinkon__primed__r02` |
| r03 | 33.43% | 29.85% | -3.58 pp | `2026-09-16__p2b-unseen__deepseek__deepseek-v3-expert__deepthinkon__direct__r03` | `2026-09-16__p2b-unseen__deepseek__deepseek-v3-expert__deepthinkon__primed__r03` |

**orthography outside-inventory**

- Direct:  n=3  mean=17.00  SD=4.36  min=14  max=22
- Primed:  n=3  mean=14.33  SD=0.58  min=14  max=15
- Paired:  Δ r01/r02/r03 = -1 / +1 / -8;  mean Δ=-2.67  SD(Δ)=4.73  range [-8, +1]

| rep | direct | primed | Δ | direct run_id | primed run_id |
|---|---:|---:|---:|---|---|
| r01 | 15 | 14 | -1 | `2026-09-16__p2b-unseen__deepseek__deepseek-v3-expert__deepthinkon__direct__r01` | `2026-09-16__p2b-unseen__deepseek__deepseek-v3-expert__deepthinkon__primed__r01` |
| r02 | 14 | 15 | +1 | `2026-09-16__p2b-unseen__deepseek__deepseek-v3-expert__deepthinkon__direct__r02` | `2026-09-16__p2b-unseen__deepseek__deepseek-v3-expert__deepthinkon__primed__r02` |
| r03 | 22 | 14 | -8 | `2026-09-16__p2b-unseen__deepseek__deepseek-v3-expert__deepthinkon__direct__r03` | `2026-09-16__p2b-unseen__deepseek__deepseek-v3-expert__deepthinkon__primed__r03` |

### Qwen 3.8 Max — Fast

Role (shortlist note): small-effect/high-variance counterexample

**canonical coverage**

- Direct:  n=3  mean=67.65%  SD=0.70 pp  min=66.87%  max=68.22%
- Primed:  n=3  mean=71.17%  SD=1.54 pp  min=69.48%  max=72.49%
- Paired:  Δ r01/r02/r03 = +3.67 / +1.27 / +5.62 pp;  mean Δ=+3.52 pp  SD(Δ)=2.18 pp  range [+1.27, +5.62] pp

| rep | direct | primed | Δ | direct run_id | primed run_id |
|---|---:|---:|---:|---|---|
| r01 | 67.86% | 71.54% | +3.67 pp | `2026-09-16__p2b-unseen__alibaba__qwen-3.8-max__fast__direct__r01` | `2026-09-16__p2b-unseen__alibaba__qwen-3.8-max__fast__primed__r01` |
| r02 | 68.22% | 69.48% | +1.27 pp | `2026-09-16__p2b-unseen__alibaba__qwen-3.8-max__fast__direct__r02` | `2026-09-16__p2b-unseen__alibaba__qwen-3.8-max__fast__primed__r02` |
| r03 | 66.87% | 72.49% | +5.62 pp | `2026-09-16__p2b-unseen__alibaba__qwen-3.8-max__fast__direct__r03` | `2026-09-16__p2b-unseen__alibaba__qwen-3.8-max__fast__primed__r03` |

**broader resource-supported coverage**

- Direct:  n=3  mean=79.25%  SD=2.41 pp  min=77.58%  max=82.01%
- Primed:  n=3  mean=81.60%  SD=1.87 pp  min=79.70%  max=83.43%
- Paired:  Δ r01/r02/r03 = +4.09 / -2.31 / +5.27 pp;  mean Δ=+2.35 pp  SD(Δ)=4.08 pp  range [-2.31, +5.27] pp

| rep | direct | primed | Δ | direct run_id | primed run_id |
|---|---:|---:|---:|---|---|
| r01 | 77.58% | 81.67% | +4.09 pp | `2026-09-16__p2b-unseen__alibaba__qwen-3.8-max__fast__direct__r01` | `2026-09-16__p2b-unseen__alibaba__qwen-3.8-max__fast__primed__r01` |
| r02 | 82.01% | 79.70% | -2.31 pp | `2026-09-16__p2b-unseen__alibaba__qwen-3.8-max__fast__direct__r02` | `2026-09-16__p2b-unseen__alibaba__qwen-3.8-max__fast__primed__r02` |
| r03 | 78.16% | 83.43% | +5.27 pp | `2026-09-16__p2b-unseen__alibaba__qwen-3.8-max__fast__direct__r03` | `2026-09-16__p2b-unseen__alibaba__qwen-3.8-max__fast__primed__r03` |

**unresolved rate**

- Direct:  n=3  mean=32.35%  SD=0.70 pp  min=31.78%  max=33.13%
- Primed:  n=3  mean=28.83%  SD=1.54 pp  min=27.51%  max=30.52%
- Paired:  Δ r01/r02/r03 = -3.67 / -1.27 / -5.62 pp;  mean Δ=-3.52 pp  SD(Δ)=2.18 pp  range [-5.62, -1.27] pp

| rep | direct | primed | Δ | direct run_id | primed run_id |
|---|---:|---:|---:|---|---|
| r01 | 32.14% | 28.46% | -3.67 pp | `2026-09-16__p2b-unseen__alibaba__qwen-3.8-max__fast__direct__r01` | `2026-09-16__p2b-unseen__alibaba__qwen-3.8-max__fast__primed__r01` |
| r02 | 31.78% | 30.52% | -1.27 pp | `2026-09-16__p2b-unseen__alibaba__qwen-3.8-max__fast__direct__r02` | `2026-09-16__p2b-unseen__alibaba__qwen-3.8-max__fast__primed__r02` |
| r03 | 33.13% | 27.51% | -5.62 pp | `2026-09-16__p2b-unseen__alibaba__qwen-3.8-max__fast__direct__r03` | `2026-09-16__p2b-unseen__alibaba__qwen-3.8-max__fast__primed__r03` |

**orthography outside-inventory**

- Direct:  n=3  mean=21.67  SD=0.58  min=21  max=22
- Primed:  n=3  mean=21.00  SD=1.73  min=20  max=23
- Paired:  Δ r01/r02/r03 = -2 / +1 / -1;  mean Δ=-0.67  SD(Δ)=1.53  range [-2, +1]

| rep | direct | primed | Δ | direct run_id | primed run_id |
|---|---:|---:|---:|---|---|
| r01 | 22 | 20 | -2 | `2026-09-16__p2b-unseen__alibaba__qwen-3.8-max__fast__direct__r01` | `2026-09-16__p2b-unseen__alibaba__qwen-3.8-max__fast__primed__r01` |
| r02 | 22 | 23 | +1 | `2026-09-16__p2b-unseen__alibaba__qwen-3.8-max__fast__direct__r02` | `2026-09-16__p2b-unseen__alibaba__qwen-3.8-max__fast__primed__r02` |
| r03 | 21 | 20 | -1 | `2026-09-16__p2b-unseen__alibaba__qwen-3.8-max__fast__direct__r03` | `2026-09-16__p2b-unseen__alibaba__qwen-3.8-max__fast__primed__r03` |

### GPT-5.6 Luna — thinking OFF

Role (shortlist note): neutral general-purpose reference

**canonical coverage**

- Direct:  n=3  mean=68.53%  SD=2.85 pp  min=65.45%  max=71.06%
- Primed:  n=3  mean=74.05%  SD=1.39 pp  min=73.03%  max=75.64%
- Paired:  Δ r01/r02/r03 = +6.56 / +7.58 / +2.43 pp;  mean Δ=+5.52 pp  SD(Δ)=2.73 pp  range [+2.43, +7.58] pp

| rep | direct | primed | Δ | direct run_id | primed run_id |
|---|---:|---:|---:|---|---|
| r01 | 69.08% | 75.64% | +6.56 pp | `2026-09-16__p2b-unseen__openai__gpt-5.6-luna__thinkoff__direct__r01` | `2026-09-16__p2b-unseen__openai__gpt-5.6-luna__thinkoff__primed__r01` |
| r02 | 65.45% | 73.03% | +7.58 pp | `2026-09-16__p2b-unseen__openai__gpt-5.6-luna__thinkoff__direct__r02` | `2026-09-16__p2b-unseen__openai__gpt-5.6-luna__thinkoff__primed__r02` |
| r03 | 71.06% | 73.49% | +2.43 pp | `2026-09-16__p2b-unseen__openai__gpt-5.6-luna__thinkoff__direct__r03` | `2026-09-16__p2b-unseen__openai__gpt-5.6-luna__thinkoff__primed__r03` |

**broader resource-supported coverage**

- Direct:  n=3  mean=78.89%  SD=4.32 pp  min=75.65%  max=83.79%
- Primed:  n=3  mean=82.49%  SD=1.49 pp  min=81.59%  max=84.21%
- Paired:  Δ r01/r02/r03 = +6.99 / +6.02 / -2.20 pp;  mean Δ=+3.60 pp  SD(Δ)=5.05 pp  range [-2.20, +6.99] pp

| rep | direct | primed | Δ | direct run_id | primed run_id |
|---|---:|---:|---:|---|---|
| r01 | 77.22% | 84.21% | +6.99 pp | `2026-09-16__p2b-unseen__openai__gpt-5.6-luna__thinkoff__direct__r01` | `2026-09-16__p2b-unseen__openai__gpt-5.6-luna__thinkoff__primed__r01` |
| r02 | 75.65% | 81.67% | +6.02 pp | `2026-09-16__p2b-unseen__openai__gpt-5.6-luna__thinkoff__direct__r02` | `2026-09-16__p2b-unseen__openai__gpt-5.6-luna__thinkoff__primed__r02` |
| r03 | 83.79% | 81.59% | -2.20 pp | `2026-09-16__p2b-unseen__openai__gpt-5.6-luna__thinkoff__direct__r03` | `2026-09-16__p2b-unseen__openai__gpt-5.6-luna__thinkoff__primed__r03` |

**unresolved rate**

- Direct:  n=3  mean=31.47%  SD=2.85 pp  min=28.94%  max=34.55%
- Primed:  n=3  mean=25.95%  SD=1.39 pp  min=24.36%  max=26.97%
- Paired:  Δ r01/r02/r03 = -6.56 / -7.58 / -2.43 pp;  mean Δ=-5.52 pp  SD(Δ)=2.73 pp  range [-7.58, -2.43] pp

| rep | direct | primed | Δ | direct run_id | primed run_id |
|---|---:|---:|---:|---|---|
| r01 | 30.92% | 24.36% | -6.56 pp | `2026-09-16__p2b-unseen__openai__gpt-5.6-luna__thinkoff__direct__r01` | `2026-09-16__p2b-unseen__openai__gpt-5.6-luna__thinkoff__primed__r01` |
| r02 | 34.55% | 26.97% | -7.58 pp | `2026-09-16__p2b-unseen__openai__gpt-5.6-luna__thinkoff__direct__r02` | `2026-09-16__p2b-unseen__openai__gpt-5.6-luna__thinkoff__primed__r02` |
| r03 | 28.94% | 26.51% | -2.43 pp | `2026-09-16__p2b-unseen__openai__gpt-5.6-luna__thinkoff__direct__r03` | `2026-09-16__p2b-unseen__openai__gpt-5.6-luna__thinkoff__primed__r03` |

**orthography outside-inventory**

- Direct:  n=3  mean=28.00  SD=13.11  min=14  max=40
- Primed:  n=3  mean=28.33  SD=21.36  min=16  max=53
- Paired:  Δ r01/r02/r03 = -14 / +2 / +13;  mean Δ=+0.33  SD(Δ)=13.58  range [-14, +13]

| rep | direct | primed | Δ | direct run_id | primed run_id |
|---|---:|---:|---:|---|---|
| r01 | 30 | 16 | -14 | `2026-09-16__p2b-unseen__openai__gpt-5.6-luna__thinkoff__direct__r01` | `2026-09-16__p2b-unseen__openai__gpt-5.6-luna__thinkoff__primed__r01` |
| r02 | 14 | 16 | +2 | `2026-09-16__p2b-unseen__openai__gpt-5.6-luna__thinkoff__direct__r02` | `2026-09-16__p2b-unseen__openai__gpt-5.6-luna__thinkoff__primed__r02` |
| r03 | 40 | 53 | +13 | `2026-09-16__p2b-unseen__openai__gpt-5.6-luna__thinkoff__direct__r03` | `2026-09-16__p2b-unseen__openai__gpt-5.6-luna__thinkoff__primed__r03` |

### Grok 4.5 Fast

Role (shortlist note): independent model-family reference; operator-reported identity

**canonical coverage**

- Direct:  n=3  mean=65.90%  SD=1.44 pp  min=64.78%  max=67.53%
- Primed:  n=3  mean=73.02%  SD=1.71 pp  min=71.10%  max=74.40%
- Paired:  Δ r01/r02/r03 = +6.02 / +9.62 / +5.70 pp;  mean Δ=+7.12 pp  SD(Δ)=2.17 pp  range [+5.70, +9.62] pp

| rep | direct | primed | Δ | direct run_id | primed run_id |
|---|---:|---:|---:|---|---|
| r01 | 67.53% | 73.55% | +6.02 pp | `2026-09-16__p2b-unseen__xai__grok__fast__direct__r01` | `2026-09-16__p2b-unseen__xai__grok__fast__primed__r01` |
| r02 | 64.78% | 74.40% | +9.62 pp | `2026-09-16__p2b-unseen__xai__grok__fast__direct__r02` | `2026-09-16__p2b-unseen__xai__grok__fast__primed__r02` |
| r03 | 65.40% | 71.10% | +5.70 pp | `2026-09-16__p2b-unseen__xai__grok__fast__direct__r03` | `2026-09-16__p2b-unseen__xai__grok__fast__primed__r03` |

**broader resource-supported coverage**

- Direct:  n=3  mean=76.10%  SD=0.98 pp  min=75.50%  max=77.24%
- Primed:  n=3  mean=80.93%  SD=1.78 pp  min=79.12%  max=82.68%
- Paired:  Δ r01/r02/r03 = +3.74 / +7.18 / +3.55 pp;  mean Δ=+4.83 pp  SD(Δ)=2.04 pp  range [+3.55, +7.18] pp

| rep | direct | primed | Δ | direct run_id | primed run_id |
|---|---:|---:|---:|---|---|
| r01 | 77.24% | 80.98% | +3.74 pp | `2026-09-16__p2b-unseen__xai__grok__fast__direct__r01` | `2026-09-16__p2b-unseen__xai__grok__fast__primed__r01` |
| r02 | 75.50% | 82.68% | +7.18 pp | `2026-09-16__p2b-unseen__xai__grok__fast__direct__r02` | `2026-09-16__p2b-unseen__xai__grok__fast__primed__r02` |
| r03 | 75.57% | 79.12% | +3.55 pp | `2026-09-16__p2b-unseen__xai__grok__fast__direct__r03` | `2026-09-16__p2b-unseen__xai__grok__fast__primed__r03` |

**unresolved rate**

- Direct:  n=3  mean=34.10%  SD=1.44 pp  min=32.47%  max=35.22%
- Primed:  n=3  mean=26.98%  SD=1.71 pp  min=25.60%  max=28.90%
- Paired:  Δ r01/r02/r03 = -6.02 / -9.62 / -5.70 pp;  mean Δ=-7.12 pp  SD(Δ)=2.17 pp  range [-9.62, -5.70] pp

| rep | direct | primed | Δ | direct run_id | primed run_id |
|---|---:|---:|---:|---|---|
| r01 | 32.47% | 26.45% | -6.02 pp | `2026-09-16__p2b-unseen__xai__grok__fast__direct__r01` | `2026-09-16__p2b-unseen__xai__grok__fast__primed__r01` |
| r02 | 35.22% | 25.60% | -9.62 pp | `2026-09-16__p2b-unseen__xai__grok__fast__direct__r02` | `2026-09-16__p2b-unseen__xai__grok__fast__primed__r02` |
| r03 | 34.60% | 28.90% | -5.70 pp | `2026-09-16__p2b-unseen__xai__grok__fast__direct__r03` | `2026-09-16__p2b-unseen__xai__grok__fast__primed__r03` |

**orthography outside-inventory**

- Direct:  n=3  mean=15.00  SD=1.73  min=13  max=16
- Primed:  n=3  mean=19.33  SD=6.11  min=14  max=26
- Paired:  Δ r01/r02/r03 = +2 / +1 / +10;  mean Δ=+4.33  SD(Δ)=4.93  range [+1, +10]

| rep | direct | primed | Δ | direct run_id | primed run_id |
|---|---:|---:|---:|---|---|
| r01 | 16 | 18 | +2 | `2026-09-16__p2b-unseen__xai__grok__fast__direct__r01` | `2026-09-16__p2b-unseen__xai__grok__fast__primed__r01` |
| r02 | 13 | 14 | +1 | `2026-09-16__p2b-unseen__xai__grok__fast__direct__r02` | `2026-09-16__p2b-unseen__xai__grok__fast__primed__r02` |
| r03 | 16 | 26 | +10 | `2026-09-16__p2b-unseen__xai__grok__fast__direct__r03` | `2026-09-16__p2b-unseen__xai__grok__fast__primed__r03` |

## 4. Observations about distribution and variance

- Each cell has **n = 3**. Means and SDs are small-sample descriptive characterizations, not population estimates.
- Primary overall mean Δ uses **n=7 valid configurations**.
- Do not compare a 6-config LOW aggregate directly to the published 7-config HIGH aggregate without stating the unequal configuration sets; see matched sensitivity below when present.

- Gemini 3.6 Flash — extended thinking ON: Δ +2.12 / +6.08 / +8.84 pp → **all positive**
- Gemini 3.6 Flash — extended thinking OFF: Δ +7.97 / +3.96 / +6.35 pp → **all positive**
- Claude Sonnet 5 — Medium (default): Δ +7.14 / +5.14 / +6.96 pp → **all positive**
- DeepSeek V3 Expert — DeepThink ON: Δ +2.91 / +5.00 / +3.58 pp → **all positive**
- Qwen 3.8 Max — Fast: Δ +3.67 / +1.27 / +5.62 pp → **all positive**
- GPT-5.6 Luna — thinking OFF: Δ +6.56 / +7.58 / +2.43 pp → **all positive**
- Grok 4.5 Fast: Δ +6.02 / +9.62 / +5.70 pp → **all positive**

## 6. Constraints

- No significance tests.
- No causal corpus-priming claims.
- No model ranking.
- Orthography outside-inventory is a separate diagnostic.
- Unresolved rate is structurally related to canonical coverage.

