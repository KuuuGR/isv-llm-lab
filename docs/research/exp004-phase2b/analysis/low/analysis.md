# EXP-004 Phase 2B LOW — aggregate analysis (descriptive)

**Status:** results written from 42 verified + evaluated runs; **primary priming analysis uses 6 valid paired configurations** (1 invalid pairing retained, excluded).
**Generator:** `scripts/analyze_exp004_phase2b.py` (deterministic;
std-lib only; never calls an LLM).

> **n = 3** replicates per configuration/condition. This report is
> a **descriptive** paired summary of observed values. It does
> **not** establish statistical significance, does **not** claim
> causal corpus-priming effects, and does **not** rank models.

## 0. Validity (LOW)

| set | n |
|---|---:|
| planned configurations | 7 |
| **valid paired configurations (primary)** | **6** |
| invalid pairing (retained, excluded from primary) | 1 |

**Qwen 3.8 Max — Fast** — `INVALID — MODEL MISMATCH`

- Intended model: Qwen 3.8 Max — Fast
- Actual Direct model: Qwen 3.8 Max — Fast
- Actual Primed model: Qwen3.7-Plus (default-selected in Qwen Chat)
- Why invalid: Primed sessions were accidentally run on Qwen3.7-Plus rather than the intended Qwen3.8-Max; Direct/Primed are not a same-model pair.
- Observed Qwen3.8-Max Primed service error (verbatim; not worked around):

```
Oops! There was an issue connecting to Qwen3.8-Max.
Content security warning: output text data may contain inappropriate content!
```

- Workaround attempted: **NO**
- Qwen 3.8 Max LOW priming effect: **not estimated**
- Raw outputs / metadata retained for audit (see `experiments/exp004-modelscreen/phase2b/analysis/low/QWEN_INCIDENT.md`).

Do **not** cite any historical −12.08 pp Qwen LOW figure as a Qwen 3.8 Max priming effect.

## 1. Data-integrity checks

Overall: **PASS** (42 observations collected, 7 planned configurations; primary valid pairs = 6).

| check | result |
|---|---|
| `exactly_42_evaluated` | yes |
| `exactly_7_configurations` | yes |
| `no_duplicate_run_ids` | yes |
| `three_direct_three_primed_per_config` | yes |
| `every_direct_has_matching_primed_replicate` | yes |
| `all_usable_complete` | yes |

Provenance pins (from plan):
- LOW story SHA-256: `ce1c4fca03fe9cb2c5f8181ab45c91767759a0c785f0a066543d95bc32f5271b`
- corpus SHA-256: `aaad28e43935a40313585d77a33bfc788d97e8d69b081f9486af74d52ca1a857`

Every aggregate below traces to `phase2b/outputs/<run_id>/evaluation.json` and `orthography.json` (paths listed in `dataset.json`).

## 2. Cross-configuration summary (primary valid pairs only; n=6)

### canonical coverage

| configuration | direct mean (SD) | primed mean (SD) | mean Δ | SD(Δ) | Δ range |
|---|---:|---:|---:|---:|---:|
| Gemini 3.6 Flash — extended thinking ON | 64.33% (1.80) | 77.56% (0.54) | +13.23 pp | 2.33 pp | [+11.37, +15.84] pp |
| Gemini 3.6 Flash — extended thinking OFF | 64.51% (2.45) | 74.91% (2.12) | +10.40 pp | 4.04 pp | [+5.91, +13.74] pp |
| Claude Sonnet 5 — Medium (default) | 65.72% (1.35) | 77.83% (2.18) | +12.11 pp | 2.50 pp | [+9.24, +13.82] pp |
| DeepSeek V3 Expert — DeepThink ON | 68.93% (1.02) | 75.12% (0.54) | +6.19 pp | 1.50 pp | [+5.22, +7.92] pp |
| GPT-5.6 Luna — thinking OFF | 70.75% (0.88) | 76.06% (0.78) | +5.31 pp | 0.91 pp | [+4.73, +6.37] pp |
| Grok 4.5 Fast | 69.32% (0.05) | 73.27% (4.94) | +3.95 pp | 4.96 pp | [-1.50, +8.21] pp |

### broader resource-supported coverage

| configuration | direct mean (SD) | primed mean (SD) | mean Δ | SD(Δ) | Δ range |
|---|---:|---:|---:|---:|---:|
| Gemini 3.6 Flash — extended thinking ON | 76.84% (2.91) | 84.12% (0.97) | +7.28 pp | 3.76 pp | [+4.66, +11.59] pp |
| Gemini 3.6 Flash — extended thinking OFF | 76.17% (1.80) | 82.44% (2.25) | +6.27 pp | 3.98 pp | [+1.96, +9.80] pp |
| Claude Sonnet 5 — Medium (default) | 77.46% (2.58) | 85.97% (0.87) | +8.51 pp | 2.82 pp | [+5.34, +10.76] pp |
| DeepSeek V3 Expert — DeepThink ON | 81.71% (0.98) | 85.32% (0.76) | +3.61 pp | 0.93 pp | [+2.82, +4.64] pp |
| GPT-5.6 Luna — thinking OFF | 83.15% (0.75) | 86.05% (0.20) | +2.91 pp | 0.59 pp | [+2.22, +3.32] pp |
| Grok 4.5 Fast | 81.64% (0.53) | 81.47% (4.45) | -0.16 pp | 4.36 pp | [-4.74, +3.95] pp |

### unresolved rate

| configuration | direct mean (SD) | primed mean (SD) | mean Δ | SD(Δ) | Δ range |
|---|---:|---:|---:|---:|---:|
| Gemini 3.6 Flash — extended thinking ON | 35.67% (1.80) | 22.44% (0.54) | -13.23 pp | 2.33 pp | [-15.84, -11.37] pp |
| Gemini 3.6 Flash — extended thinking OFF | 35.49% (2.45) | 25.09% (2.12) | -10.40 pp | 4.04 pp | [-13.74, -5.91] pp |
| Claude Sonnet 5 — Medium (default) | 34.28% (1.35) | 22.17% (2.18) | -12.11 pp | 2.50 pp | [-13.82, -9.24] pp |
| DeepSeek V3 Expert — DeepThink ON | 31.07% (1.02) | 24.88% (0.54) | -6.19 pp | 1.50 pp | [-7.92, -5.22] pp |
| GPT-5.6 Luna — thinking OFF | 29.25% (0.88) | 23.94% (0.78) | -5.31 pp | 0.91 pp | [-6.37, -4.73] pp |
| Grok 4.5 Fast | 30.68% (0.05) | 26.73% (4.94) | -3.95 pp | 4.96 pp | [-8.21, +1.50] pp |

### orthography outside-inventory

| configuration | direct mean (SD) | primed mean (SD) | mean Δ | SD(Δ) | Δ range |
|---|---:|---:|---:|---:|---:|
| Gemini 3.6 Flash — extended thinking ON | 42.67 (17.16) | 30.00 (15.72) | -12.67 | 32.59 | [-49, +14] |
| Gemini 3.6 Flash — extended thinking OFF | 43.00 (26.29) | 29.67 (17.95) | -13.33 | 41.67 | [-57, +26] |
| Claude Sonnet 5 — Medium (default) | 182.33 (116.42) | 13.00 (14.93) | -169.33 | 102.65 | [-284, -86] |
| DeepSeek V3 Expert — DeepThink ON | 15.33 (3.79) | 12.67 (4.62) | -2.67 | 3.79 | [-7, +0] |
| GPT-5.6 Luna — thinking OFF | 11.67 (4.93) | 15.00 (7.21) | +3.33 | 4.51 | [-1, +8] |
| Grok 4.5 Fast | 24.33 (4.93) | 71.33 (71.65) | +47.00 | 73.08 | [-2, +131] |

**Overall descriptive mean Δ (canonical)** across **n=6 valid configurations**: +8.53 pp (6 positive / 0 negative).

## 3. Per-configuration detail (individual D / P / Δ)

Replicates are independent fresh sessions (r01–r03). Δᵢ = Pᵢ − Dᵢ for the same replicate tag.

### 3a. Primary valid configurations

### Gemini 3.6 Flash — extended thinking ON

Role (shortlist note): strong priming effect (large reproduced Δ)

**canonical coverage**

- Direct:  n=3  mean=64.33%  SD=1.80 pp  min=62.35%  max=65.86%
- Primed:  n=3  mean=77.56%  SD=0.54 pp  min=77.23%  max=78.19%
- Paired:  Δ r01/r02/r03 = +15.84 / +11.37 / +12.48 pp;  mean Δ=+13.23 pp  SD(Δ)=2.33 pp  range [+11.37, +15.84] pp

| rep | direct | primed | Δ | direct run_id | primed run_id |
|---|---:|---:|---:|---|---|
| r01 | 62.35% | 78.19% | +15.84 pp | `2026-09-15__p2b-low__google__gemini-3.6-flash__extthinkon__direct__r01` | `2026-09-15__p2b-low__google__gemini-3.6-flash__extthinkon__primed__r01` |
| r02 | 65.86% | 77.23% | +11.37 pp | `2026-09-15__p2b-low__google__gemini-3.6-flash__extthinkon__direct__r02` | `2026-09-15__p2b-low__google__gemini-3.6-flash__extthinkon__primed__r02` |
| r03 | 64.79% | 77.26% | +12.48 pp | `2026-09-15__p2b-low__google__gemini-3.6-flash__extthinkon__direct__r03` | `2026-09-15__p2b-low__google__gemini-3.6-flash__extthinkon__primed__r03` |

**broader resource-supported coverage**

- Direct:  n=3  mean=76.84%  SD=2.91 pp  min=73.60%  max=79.23%
- Primed:  n=3  mean=84.12%  SD=0.97 pp  min=83.28%  max=85.19%
- Paired:  Δ r01/r02/r03 = +11.59 / +5.59 / +4.66 pp;  mean Δ=+7.28 pp  SD(Δ)=3.76 pp  range [+4.66, +11.59] pp

| rep | direct | primed | Δ | direct run_id | primed run_id |
|---|---:|---:|---:|---|---|
| r01 | 73.60% | 85.19% | +11.59 pp | `2026-09-15__p2b-low__google__gemini-3.6-flash__extthinkon__direct__r01` | `2026-09-15__p2b-low__google__gemini-3.6-flash__extthinkon__primed__r01` |
| r02 | 77.69% | 83.28% | +5.59 pp | `2026-09-15__p2b-low__google__gemini-3.6-flash__extthinkon__direct__r02` | `2026-09-15__p2b-low__google__gemini-3.6-flash__extthinkon__primed__r02` |
| r03 | 79.23% | 83.89% | +4.66 pp | `2026-09-15__p2b-low__google__gemini-3.6-flash__extthinkon__direct__r03` | `2026-09-15__p2b-low__google__gemini-3.6-flash__extthinkon__primed__r03` |

**unresolved rate**

- Direct:  n=3  mean=35.67%  SD=1.80 pp  min=34.14%  max=37.65%
- Primed:  n=3  mean=22.44%  SD=0.54 pp  min=21.81%  max=22.77%
- Paired:  Δ r01/r02/r03 = -15.84 / -11.37 / -12.48 pp;  mean Δ=-13.23 pp  SD(Δ)=2.33 pp  range [-15.84, -11.37] pp

| rep | direct | primed | Δ | direct run_id | primed run_id |
|---|---:|---:|---:|---|---|
| r01 | 37.65% | 21.81% | -15.84 pp | `2026-09-15__p2b-low__google__gemini-3.6-flash__extthinkon__direct__r01` | `2026-09-15__p2b-low__google__gemini-3.6-flash__extthinkon__primed__r01` |
| r02 | 34.14% | 22.77% | -11.37 pp | `2026-09-15__p2b-low__google__gemini-3.6-flash__extthinkon__direct__r02` | `2026-09-15__p2b-low__google__gemini-3.6-flash__extthinkon__primed__r02` |
| r03 | 35.21% | 22.74% | -12.48 pp | `2026-09-15__p2b-low__google__gemini-3.6-flash__extthinkon__direct__r03` | `2026-09-15__p2b-low__google__gemini-3.6-flash__extthinkon__primed__r03` |

**orthography outside-inventory**

- Direct:  n=3  mean=42.67  SD=17.16  min=27  max=61
- Primed:  n=3  mean=30.00  SD=15.72  min=12  max=41
- Paired:  Δ r01/r02/r03 = -49 / +14 / -3;  mean Δ=-12.67  SD(Δ)=32.59  range [-49, +14]

| rep | direct | primed | Δ | direct run_id | primed run_id |
|---|---:|---:|---:|---|---|
| r01 | 61 | 12 | -49 | `2026-09-15__p2b-low__google__gemini-3.6-flash__extthinkon__direct__r01` | `2026-09-15__p2b-low__google__gemini-3.6-flash__extthinkon__primed__r01` |
| r02 | 27 | 41 | +14 | `2026-09-15__p2b-low__google__gemini-3.6-flash__extthinkon__direct__r02` | `2026-09-15__p2b-low__google__gemini-3.6-flash__extthinkon__primed__r02` |
| r03 | 40 | 37 | -3 | `2026-09-15__p2b-low__google__gemini-3.6-flash__extthinkon__direct__r03` | `2026-09-15__p2b-low__google__gemini-3.6-flash__extthinkon__primed__r03` |

### Gemini 3.6 Flash — extended thinking OFF

Role (shortlist note): strong priming effect (large reproduced Δ)

**canonical coverage**

- Direct:  n=3  mean=64.51%  SD=2.45 pp  min=62.69%  max=67.30%
- Primed:  n=3  mean=74.91%  SD=2.12 pp  min=73.21%  max=77.29%
- Paired:  Δ r01/r02/r03 = +13.74 / +11.55 / +5.91 pp;  mean Δ=+10.40 pp  SD(Δ)=4.04 pp  range [+5.91, +13.74] pp

| rep | direct | primed | Δ | direct run_id | primed run_id |
|---|---:|---:|---:|---|---|
| r01 | 63.55% | 77.29% | +13.74 pp | `2026-09-15__p2b-low__google__gemini-3.6-flash__extthinkoff__direct__r01` | `2026-09-15__p2b-low__google__gemini-3.6-flash__extthinkoff__primed__r01` |
| r02 | 62.69% | 74.25% | +11.55 pp | `2026-09-15__p2b-low__google__gemini-3.6-flash__extthinkoff__direct__r02` | `2026-09-15__p2b-low__google__gemini-3.6-flash__extthinkoff__primed__r02` |
| r03 | 67.30% | 73.21% | +5.91 pp | `2026-09-15__p2b-low__google__gemini-3.6-flash__extthinkoff__direct__r03` | `2026-09-15__p2b-low__google__gemini-3.6-flash__extthinkoff__primed__r03` |

**broader resource-supported coverage**

- Direct:  n=3  mean=76.17%  SD=1.80 pp  min=74.89%  max=78.23%
- Primed:  n=3  mean=82.44%  SD=2.25 pp  min=80.19%  max=84.69%
- Paired:  Δ r01/r02/r03 = +9.80 / +7.06 / +1.96 pp;  mean Δ=+6.27 pp  SD(Δ)=3.98 pp  range [+1.96, +9.80] pp

| rep | direct | primed | Δ | direct run_id | primed run_id |
|---|---:|---:|---:|---|---|
| r01 | 74.89% | 84.69% | +9.80 pp | `2026-09-15__p2b-low__google__gemini-3.6-flash__extthinkoff__direct__r01` | `2026-09-15__p2b-low__google__gemini-3.6-flash__extthinkoff__primed__r01` |
| r02 | 75.39% | 82.45% | +7.06 pp | `2026-09-15__p2b-low__google__gemini-3.6-flash__extthinkoff__direct__r02` | `2026-09-15__p2b-low__google__gemini-3.6-flash__extthinkoff__primed__r02` |
| r03 | 78.23% | 80.19% | +1.96 pp | `2026-09-15__p2b-low__google__gemini-3.6-flash__extthinkoff__direct__r03` | `2026-09-15__p2b-low__google__gemini-3.6-flash__extthinkoff__primed__r03` |

**unresolved rate**

- Direct:  n=3  mean=35.49%  SD=2.45 pp  min=32.70%  max=37.31%
- Primed:  n=3  mean=25.09%  SD=2.12 pp  min=22.71%  max=26.79%
- Paired:  Δ r01/r02/r03 = -13.74 / -11.55 / -5.91 pp;  mean Δ=-10.40 pp  SD(Δ)=4.04 pp  range [-13.74, -5.91] pp

| rep | direct | primed | Δ | direct run_id | primed run_id |
|---|---:|---:|---:|---|---|
| r01 | 36.45% | 22.71% | -13.74 pp | `2026-09-15__p2b-low__google__gemini-3.6-flash__extthinkoff__direct__r01` | `2026-09-15__p2b-low__google__gemini-3.6-flash__extthinkoff__primed__r01` |
| r02 | 37.31% | 25.75% | -11.55 pp | `2026-09-15__p2b-low__google__gemini-3.6-flash__extthinkoff__direct__r02` | `2026-09-15__p2b-low__google__gemini-3.6-flash__extthinkoff__primed__r02` |
| r03 | 32.70% | 26.79% | -5.91 pp | `2026-09-15__p2b-low__google__gemini-3.6-flash__extthinkoff__direct__r03` | `2026-09-15__p2b-low__google__gemini-3.6-flash__extthinkoff__primed__r03` |

**orthography outside-inventory**

- Direct:  n=3  mean=43.00  SD=26.29  min=24  max=73
- Primed:  n=3  mean=29.67  SD=17.95  min=16  max=50
- Paired:  Δ r01/r02/r03 = -57 / -9 / +26;  mean Δ=-13.33  SD(Δ)=41.67  range [-57, +26]

| rep | direct | primed | Δ | direct run_id | primed run_id |
|---|---:|---:|---:|---|---|
| r01 | 73 | 16 | -57 | `2026-09-15__p2b-low__google__gemini-3.6-flash__extthinkoff__direct__r01` | `2026-09-15__p2b-low__google__gemini-3.6-flash__extthinkoff__primed__r01` |
| r02 | 32 | 23 | -9 | `2026-09-15__p2b-low__google__gemini-3.6-flash__extthinkoff__direct__r02` | `2026-09-15__p2b-low__google__gemini-3.6-flash__extthinkoff__primed__r02` |
| r03 | 24 | 50 | +26 | `2026-09-15__p2b-low__google__gemini-3.6-flash__extthinkoff__direct__r03` | `2026-09-15__p2b-low__google__gemini-3.6-flash__extthinkoff__primed__r03` |

### Claude Sonnet 5 — Medium (default)

Role (shortlist note): stable high-performance configuration

**canonical coverage**

- Direct:  n=3  mean=65.72%  SD=1.35 pp  min=64.18%  max=66.65%
- Primed:  n=3  mean=77.83%  SD=2.18 pp  min=75.58%  max=79.92%
- Paired:  Δ r01/r02/r03 = +13.82 / +9.24 / +13.27 pp;  mean Δ=+12.11 pp  SD(Δ)=2.50 pp  range [+9.24, +13.82] pp

| rep | direct | primed | Δ | direct run_id | primed run_id |
|---|---:|---:|---:|---|---|
| r01 | 64.18% | 78.00% | +13.82 pp | `2026-09-15__p2b-low__anthropic__claude__sonnet-5__direct__r01` | `2026-09-15__p2b-low__anthropic__claude__sonnet-5__primed__r01` |
| r02 | 66.34% | 75.58% | +9.24 pp | `2026-09-15__p2b-low__anthropic__claude__sonnet-5__direct__r02` | `2026-09-15__p2b-low__anthropic__claude__sonnet-5__primed__r02` |
| r03 | 66.65% | 79.92% | +13.27 pp | `2026-09-15__p2b-low__anthropic__claude__sonnet-5__direct__r03` | `2026-09-15__p2b-low__anthropic__claude__sonnet-5__primed__r03` |

**broader resource-supported coverage**

- Direct:  n=3  mean=77.46%  SD=2.58 pp  min=74.84%  max=80.00%
- Primed:  n=3  mean=85.97%  SD=0.87 pp  min=85.34%  max=86.96%
- Paired:  Δ r01/r02/r03 = +10.76 / +5.34 / +9.43 pp;  mean Δ=+8.51 pp  SD(Δ)=2.82 pp  range [+5.34, +10.76] pp

| rep | direct | primed | Δ | direct run_id | primed run_id |
|---|---:|---:|---:|---|---|
| r01 | 74.84% | 85.60% | +10.76 pp | `2026-09-15__p2b-low__anthropic__claude__sonnet-5__direct__r01` | `2026-09-15__p2b-low__anthropic__claude__sonnet-5__primed__r01` |
| r02 | 80.00% | 85.34% | +5.34 pp | `2026-09-15__p2b-low__anthropic__claude__sonnet-5__direct__r02` | `2026-09-15__p2b-low__anthropic__claude__sonnet-5__primed__r02` |
| r03 | 77.53% | 86.96% | +9.43 pp | `2026-09-15__p2b-low__anthropic__claude__sonnet-5__direct__r03` | `2026-09-15__p2b-low__anthropic__claude__sonnet-5__primed__r03` |

**unresolved rate**

- Direct:  n=3  mean=34.28%  SD=1.35 pp  min=33.35%  max=35.82%
- Primed:  n=3  mean=22.17%  SD=2.18 pp  min=20.08%  max=24.42%
- Paired:  Δ r01/r02/r03 = -13.82 / -9.24 / -13.27 pp;  mean Δ=-12.11 pp  SD(Δ)=2.50 pp  range [-13.82, -9.24] pp

| rep | direct | primed | Δ | direct run_id | primed run_id |
|---|---:|---:|---:|---|---|
| r01 | 35.82% | 22.00% | -13.82 pp | `2026-09-15__p2b-low__anthropic__claude__sonnet-5__direct__r01` | `2026-09-15__p2b-low__anthropic__claude__sonnet-5__primed__r01` |
| r02 | 33.66% | 24.42% | -9.24 pp | `2026-09-15__p2b-low__anthropic__claude__sonnet-5__direct__r02` | `2026-09-15__p2b-low__anthropic__claude__sonnet-5__primed__r02` |
| r03 | 33.35% | 20.08% | -13.27 pp | `2026-09-15__p2b-low__anthropic__claude__sonnet-5__direct__r03` | `2026-09-15__p2b-low__anthropic__claude__sonnet-5__primed__r03` |

**orthography outside-inventory**

- Direct:  n=3  mean=182.33  SD=116.42  min=93  max=314
- Primed:  n=3  mean=13.00  SD=14.93  min=2  max=30
- Paired:  Δ r01/r02/r03 = -284 / -86 / -138;  mean Δ=-169.33  SD(Δ)=102.65  range [-284, -86]

| rep | direct | primed | Δ | direct run_id | primed run_id |
|---|---:|---:|---:|---|---|
| r01 | 314 | 30 | -284 | `2026-09-15__p2b-low__anthropic__claude__sonnet-5__direct__r01` | `2026-09-15__p2b-low__anthropic__claude__sonnet-5__primed__r01` |
| r02 | 93 | 7 | -86 | `2026-09-15__p2b-low__anthropic__claude__sonnet-5__direct__r02` | `2026-09-15__p2b-low__anthropic__claude__sonnet-5__primed__r02` |
| r03 | 140 | 2 | -138 | `2026-09-15__p2b-low__anthropic__claude__sonnet-5__direct__r03` | `2026-09-15__p2b-low__anthropic__claude__sonnet-5__primed__r03` |

### DeepSeek V3 Expert — DeepThink ON

Role (shortlist note): clean output, high baseline

**canonical coverage**

- Direct:  n=3  mean=68.93%  SD=1.02 pp  min=67.80%  max=69.75%
- Primed:  n=3  mean=75.12%  SD=0.54 pp  min=74.67%  max=75.72%
- Paired:  Δ r01/r02/r03 = +5.43 / +7.92 / +5.22 pp;  mean Δ=+6.19 pp  SD(Δ)=1.50 pp  range [+5.22, +7.92] pp

| rep | direct | primed | Δ | direct run_id | primed run_id |
|---|---:|---:|---:|---|---|
| r01 | 69.25% | 74.67% | +5.43 pp | `2026-09-15__p2b-low__deepseek__deepseek-v3-expert__deepthinkon__direct__r01` | `2026-09-15__p2b-low__deepseek__deepseek-v3-expert__deepthinkon__primed__r01` |
| r02 | 67.80% | 75.72% | +7.92 pp | `2026-09-15__p2b-low__deepseek__deepseek-v3-expert__deepthinkon__direct__r02` | `2026-09-15__p2b-low__deepseek__deepseek-v3-expert__deepthinkon__primed__r02` |
| r03 | 69.75% | 74.98% | +5.22 pp | `2026-09-15__p2b-low__deepseek__deepseek-v3-expert__deepthinkon__direct__r03` | `2026-09-15__p2b-low__deepseek__deepseek-v3-expert__deepthinkon__primed__r03` |

**broader resource-supported coverage**

- Direct:  n=3  mean=81.71%  SD=0.98 pp  min=80.73%  max=82.69%
- Primed:  n=3  mean=85.32%  SD=0.76 pp  min=84.53%  max=86.06%
- Paired:  Δ r01/r02/r03 = +3.37 / +4.64 / +2.82 pp;  mean Δ=+3.61 pp  SD(Δ)=0.93 pp  range [+2.82, +4.64] pp

| rep | direct | primed | Δ | direct run_id | primed run_id |
|---|---:|---:|---:|---|---|
| r01 | 82.69% | 86.06% | +3.37 pp | `2026-09-15__p2b-low__deepseek__deepseek-v3-expert__deepthinkon__direct__r01` | `2026-09-15__p2b-low__deepseek__deepseek-v3-expert__deepthinkon__primed__r01` |
| r02 | 80.73% | 85.36% | +4.64 pp | `2026-09-15__p2b-low__deepseek__deepseek-v3-expert__deepthinkon__direct__r02` | `2026-09-15__p2b-low__deepseek__deepseek-v3-expert__deepthinkon__primed__r02` |
| r03 | 81.72% | 84.53% | +2.82 pp | `2026-09-15__p2b-low__deepseek__deepseek-v3-expert__deepthinkon__direct__r03` | `2026-09-15__p2b-low__deepseek__deepseek-v3-expert__deepthinkon__primed__r03` |

**unresolved rate**

- Direct:  n=3  mean=31.07%  SD=1.02 pp  min=30.25%  max=32.20%
- Primed:  n=3  mean=24.88%  SD=0.54 pp  min=24.28%  max=25.33%
- Paired:  Δ r01/r02/r03 = -5.43 / -7.92 / -5.22 pp;  mean Δ=-6.19 pp  SD(Δ)=1.50 pp  range [-7.92, -5.22] pp

| rep | direct | primed | Δ | direct run_id | primed run_id |
|---|---:|---:|---:|---|---|
| r01 | 30.75% | 25.33% | -5.43 pp | `2026-09-15__p2b-low__deepseek__deepseek-v3-expert__deepthinkon__direct__r01` | `2026-09-15__p2b-low__deepseek__deepseek-v3-expert__deepthinkon__primed__r01` |
| r02 | 32.20% | 24.28% | -7.92 pp | `2026-09-15__p2b-low__deepseek__deepseek-v3-expert__deepthinkon__direct__r02` | `2026-09-15__p2b-low__deepseek__deepseek-v3-expert__deepthinkon__primed__r02` |
| r03 | 30.25% | 25.02% | -5.22 pp | `2026-09-15__p2b-low__deepseek__deepseek-v3-expert__deepthinkon__direct__r03` | `2026-09-15__p2b-low__deepseek__deepseek-v3-expert__deepthinkon__primed__r03` |

**orthography outside-inventory**

- Direct:  n=3  mean=15.33  SD=3.79  min=11  max=18
- Primed:  n=3  mean=12.67  SD=4.62  min=10  max=18
- Paired:  Δ r01/r02/r03 = -1 / -7 / +0;  mean Δ=-2.67  SD(Δ)=3.79  range [-7, +0]

| rep | direct | primed | Δ | direct run_id | primed run_id |
|---|---:|---:|---:|---|---|
| r01 | 11 | 10 | -1 | `2026-09-15__p2b-low__deepseek__deepseek-v3-expert__deepthinkon__direct__r01` | `2026-09-15__p2b-low__deepseek__deepseek-v3-expert__deepthinkon__primed__r01` |
| r02 | 17 | 10 | -7 | `2026-09-15__p2b-low__deepseek__deepseek-v3-expert__deepthinkon__direct__r02` | `2026-09-15__p2b-low__deepseek__deepseek-v3-expert__deepthinkon__primed__r02` |
| r03 | 18 | 18 | +0 | `2026-09-15__p2b-low__deepseek__deepseek-v3-expert__deepthinkon__direct__r03` | `2026-09-15__p2b-low__deepseek__deepseek-v3-expert__deepthinkon__primed__r03` |

### GPT-5.6 Luna — thinking OFF

Role (shortlist note): neutral general-purpose reference

**canonical coverage**

- Direct:  n=3  mean=70.75%  SD=0.88 pp  min=70.07%  max=71.74%
- Primed:  n=3  mean=76.06%  SD=0.78 pp  min=75.17%  max=76.58%
- Paired:  Δ r01/r02/r03 = +4.85 / +6.37 / +4.73 pp;  mean Δ=+5.31 pp  SD(Δ)=0.91 pp  range [+4.73, +6.37] pp

| rep | direct | primed | Δ | direct run_id | primed run_id |
|---|---:|---:|---:|---|---|
| r01 | 71.74% | 76.58% | +4.85 pp | `2026-09-15__p2b-low__openai__gpt-5.6-luna__thinkoff__direct__r01` | `2026-09-15__p2b-low__openai__gpt-5.6-luna__thinkoff__primed__r01` |
| r02 | 70.07% | 76.43% | +6.37 pp | `2026-09-15__p2b-low__openai__gpt-5.6-luna__thinkoff__direct__r02` | `2026-09-15__p2b-low__openai__gpt-5.6-luna__thinkoff__primed__r02` |
| r03 | 70.44% | 75.17% | +4.73 pp | `2026-09-15__p2b-low__openai__gpt-5.6-luna__thinkoff__direct__r03` | `2026-09-15__p2b-low__openai__gpt-5.6-luna__thinkoff__primed__r03` |

**broader resource-supported coverage**

- Direct:  n=3  mean=83.15%  SD=0.75 pp  min=82.68%  max=84.01%
- Primed:  n=3  mean=86.05%  SD=0.20 pp  min=85.84%  max=86.23%
- Paired:  Δ r01/r02/r03 = +2.22 / +3.17 / +3.32 pp;  mean Δ=+2.91 pp  SD(Δ)=0.59 pp  range [+2.22, +3.32] pp

| rep | direct | primed | Δ | direct run_id | primed run_id |
|---|---:|---:|---:|---|---|
| r01 | 84.01% | 86.23% | +2.22 pp | `2026-09-15__p2b-low__openai__gpt-5.6-luna__thinkoff__direct__r01` | `2026-09-15__p2b-low__openai__gpt-5.6-luna__thinkoff__primed__r01` |
| r02 | 82.68% | 85.84% | +3.17 pp | `2026-09-15__p2b-low__openai__gpt-5.6-luna__thinkoff__direct__r02` | `2026-09-15__p2b-low__openai__gpt-5.6-luna__thinkoff__primed__r02` |
| r03 | 82.76% | 86.09% | +3.32 pp | `2026-09-15__p2b-low__openai__gpt-5.6-luna__thinkoff__direct__r03` | `2026-09-15__p2b-low__openai__gpt-5.6-luna__thinkoff__primed__r03` |

**unresolved rate**

- Direct:  n=3  mean=29.25%  SD=0.88 pp  min=28.26%  max=29.93%
- Primed:  n=3  mean=23.94%  SD=0.78 pp  min=23.42%  max=24.83%
- Paired:  Δ r01/r02/r03 = -4.85 / -6.37 / -4.73 pp;  mean Δ=-5.31 pp  SD(Δ)=0.91 pp  range [-6.37, -4.73] pp

| rep | direct | primed | Δ | direct run_id | primed run_id |
|---|---:|---:|---:|---|---|
| r01 | 28.26% | 23.42% | -4.85 pp | `2026-09-15__p2b-low__openai__gpt-5.6-luna__thinkoff__direct__r01` | `2026-09-15__p2b-low__openai__gpt-5.6-luna__thinkoff__primed__r01` |
| r02 | 29.93% | 23.57% | -6.37 pp | `2026-09-15__p2b-low__openai__gpt-5.6-luna__thinkoff__direct__r02` | `2026-09-15__p2b-low__openai__gpt-5.6-luna__thinkoff__primed__r02` |
| r03 | 29.56% | 24.83% | -4.73 pp | `2026-09-15__p2b-low__openai__gpt-5.6-luna__thinkoff__direct__r03` | `2026-09-15__p2b-low__openai__gpt-5.6-luna__thinkoff__primed__r03` |

**orthography outside-inventory**

- Direct:  n=3  mean=11.67  SD=4.93  min=6  max=15
- Primed:  n=3  mean=15.00  SD=7.21  min=9  max=23
- Paired:  Δ r01/r02/r03 = +3 / -1 / +8;  mean Δ=+3.33  SD(Δ)=4.51  range [-1, +8]

| rep | direct | primed | Δ | direct run_id | primed run_id |
|---|---:|---:|---:|---|---|
| r01 | 6 | 9 | +3 | `2026-09-15__p2b-low__openai__gpt-5.6-luna__thinkoff__direct__r01` | `2026-09-15__p2b-low__openai__gpt-5.6-luna__thinkoff__primed__r01` |
| r02 | 14 | 13 | -1 | `2026-09-15__p2b-low__openai__gpt-5.6-luna__thinkoff__direct__r02` | `2026-09-15__p2b-low__openai__gpt-5.6-luna__thinkoff__primed__r02` |
| r03 | 15 | 23 | +8 | `2026-09-15__p2b-low__openai__gpt-5.6-luna__thinkoff__direct__r03` | `2026-09-15__p2b-low__openai__gpt-5.6-luna__thinkoff__primed__r03` |

### Grok 4.5 Fast

Role (shortlist note): independent model-family reference; operator-reported identity

**canonical coverage**

- Direct:  n=3  mean=69.32%  SD=0.05 pp  min=69.26%  max=69.36%
- Primed:  n=3  mean=73.27%  SD=4.94 pp  min=67.86%  max=77.55%
- Paired:  Δ r01/r02/r03 = +8.21 / +5.13 / -1.50 pp;  mean Δ=+3.95 pp  SD(Δ)=4.96 pp  range [-1.50, +8.21] pp

| rep | direct | primed | Δ | direct run_id | primed run_id |
|---|---:|---:|---:|---|---|
| r01 | 69.34% | 77.55% | +8.21 pp | `2026-09-15__p2b-low__xai__grok__fast__direct__r01` | `2026-09-15__p2b-low__xai__grok__fast__primed__r01` |
| r02 | 69.26% | 74.39% | +5.13 pp | `2026-09-15__p2b-low__xai__grok__fast__direct__r02` | `2026-09-15__p2b-low__xai__grok__fast__primed__r02` |
| r03 | 69.36% | 67.86% | -1.50 pp | `2026-09-15__p2b-low__xai__grok__fast__direct__r03` | `2026-09-15__p2b-low__xai__grok__fast__primed__r03` |

**broader resource-supported coverage**

- Direct:  n=3  mean=81.64%  SD=0.53 pp  min=81.32%  max=82.25%
- Primed:  n=3  mean=81.47%  SD=4.45 pp  min=76.59%  max=85.29%
- Paired:  Δ r01/r02/r03 = +3.95 / +0.29 / -4.74 pp;  mean Δ=-0.16 pp  SD(Δ)=4.36 pp  range [-4.74, +3.95] pp

| rep | direct | primed | Δ | direct run_id | primed run_id |
|---|---:|---:|---:|---|---|
| r01 | 81.34% | 85.29% | +3.95 pp | `2026-09-15__p2b-low__xai__grok__fast__direct__r01` | `2026-09-15__p2b-low__xai__grok__fast__primed__r01` |
| r02 | 82.25% | 82.54% | +0.29 pp | `2026-09-15__p2b-low__xai__grok__fast__direct__r02` | `2026-09-15__p2b-low__xai__grok__fast__primed__r02` |
| r03 | 81.32% | 76.59% | -4.74 pp | `2026-09-15__p2b-low__xai__grok__fast__direct__r03` | `2026-09-15__p2b-low__xai__grok__fast__primed__r03` |

**unresolved rate**

- Direct:  n=3  mean=30.68%  SD=0.05 pp  min=30.64%  max=30.74%
- Primed:  n=3  mean=26.73%  SD=4.94 pp  min=22.45%  max=32.14%
- Paired:  Δ r01/r02/r03 = -8.21 / -5.13 / +1.50 pp;  mean Δ=-3.95 pp  SD(Δ)=4.96 pp  range [-8.21, +1.50] pp

| rep | direct | primed | Δ | direct run_id | primed run_id |
|---|---:|---:|---:|---|---|
| r01 | 30.66% | 22.45% | -8.21 pp | `2026-09-15__p2b-low__xai__grok__fast__direct__r01` | `2026-09-15__p2b-low__xai__grok__fast__primed__r01` |
| r02 | 30.74% | 25.61% | -5.13 pp | `2026-09-15__p2b-low__xai__grok__fast__direct__r02` | `2026-09-15__p2b-low__xai__grok__fast__primed__r02` |
| r03 | 30.64% | 32.14% | +1.50 pp | `2026-09-15__p2b-low__xai__grok__fast__direct__r03` | `2026-09-15__p2b-low__xai__grok__fast__primed__r03` |

**orthography outside-inventory**

- Direct:  n=3  mean=24.33  SD=4.93  min=21  max=30
- Primed:  n=3  mean=71.33  SD=71.65  min=19  max=153
- Paired:  Δ r01/r02/r03 = -2 / +12 / +131;  mean Δ=+47.00  SD(Δ)=73.08  range [-2, +131]

| rep | direct | primed | Δ | direct run_id | primed run_id |
|---|---:|---:|---:|---|---|
| r01 | 21 | 19 | -2 | `2026-09-15__p2b-low__xai__grok__fast__direct__r01` | `2026-09-15__p2b-low__xai__grok__fast__primed__r01` |
| r02 | 30 | 42 | +12 | `2026-09-15__p2b-low__xai__grok__fast__direct__r02` | `2026-09-15__p2b-low__xai__grok__fast__primed__r02` |
| r03 | 22 | 153 | +131 | `2026-09-15__p2b-low__xai__grok__fast__direct__r03` | `2026-09-15__p2b-low__xai__grok__fast__primed__r03` |

### 3b. Invalid pairing (retained; not primary)

Metrics below are retained for audit completeness only. **They are not same-model priming effects.**

#### Qwen 3.8 Max — Fast — INVALID — MODEL MISMATCH

- Canonical Δ r01/r02/r03 (audit only): -5.78 / -3.68 / -26.77 pp; mean=-12.08 pp — **do not interpret as Qwen 3.8 Max priming**.

- `direct` `r01`: `2026-09-15__p2b-low__alibaba__qwen-3.8-max__fast__direct__r01`
- `direct` `r02`: `2026-09-15__p2b-low__alibaba__qwen-3.8-max__fast__direct__r02`
- `direct` `r03`: `2026-09-15__p2b-low__alibaba__qwen-3.8-max__fast__direct__r03`
- `primed` `r01`: `2026-09-15__p2b-low__alibaba__qwen-3.8-max__fast__primed__r01`
- `primed` `r02`: `2026-09-15__p2b-low__alibaba__qwen-3.8-max__fast__primed__r02`
- `primed` `r03`: `2026-09-15__p2b-low__alibaba__qwen-3.8-max__fast__primed__r03`

## 4. Observations about distribution and variance

- Each cell has **n = 3**. Means and SDs are small-sample descriptive characterizations, not population estimates.
- Primary overall mean Δ uses **n=6 valid configurations** (not the 7 planned cells).
- Do not compare a 6-config LOW aggregate directly to the published 7-config HIGH aggregate without stating the unequal configuration sets; see matched sensitivity below when present.

- Gemini 3.6 Flash — extended thinking ON: Δ +15.84 / +11.37 / +12.48 pp → **all positive**
- Gemini 3.6 Flash — extended thinking OFF: Δ +13.74 / +11.55 / +5.91 pp → **all positive**
- Claude Sonnet 5 — Medium (default): Δ +13.82 / +9.24 / +13.27 pp → **all positive**
- DeepSeek V3 Expert — DeepThink ON: Δ +5.43 / +7.92 / +5.22 pp → **all positive**
- GPT-5.6 Luna — thinking OFF: Δ +4.85 / +6.37 / +4.73 pp → **all positive**
- Grok 4.5 Fast: Δ +8.21 / +5.13 / -1.50 pp → **mixed**

## 5. Matched-configuration HIGH↔LOW sensitivity (n=6)

Descriptive only. Unequal to the published HIGH 7-config aggregate; do not treat as a replacement for HIGH's full record. Qwen is excluded on both sides so the configuration sets match.

- HIGH mean Δ (matched 6): +7.39 pp
- LOW mean Δ (matched 6): +8.53 pp

| configuration | HIGH mean Δ | LOW mean Δ | HIGH direction | LOW direction |
|---|---:|---:|---|---|
| Gemini 3.6 Flash — extended thinking ON | -0.55 pp | +13.23 pp | mixed | all positive |
| Gemini 3.6 Flash — extended thinking OFF | -1.75 pp | +10.40 pp | mixed | all positive |
| Claude Sonnet 5 — Medium (default) | +14.28 pp | +12.11 pp | all positive | all positive |
| DeepSeek V3 Expert — DeepThink ON | +9.25 pp | +6.19 pp | all positive | all positive |
| GPT-5.6 Luna — thinking OFF | +8.62 pp | +5.31 pp | all positive | all positive |
| Grok 4.5 Fast | +14.49 pp | +3.95 pp | all positive | mixed |

## 6. Constraints

- No significance tests.
- No causal corpus-priming claims.
- No model ranking.
- Orthography outside-inventory is a separate diagnostic.
- Unresolved rate is structurally related to canonical coverage.

