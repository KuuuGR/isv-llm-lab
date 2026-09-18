# Phase 2B UNSEEN — article-ready evidence record

**Status:** descriptive aggregate results preserved (2026-09-18).
**Not:** final scientific conclusions, paper Discussion/Conclusion, or
HIGH/LOW/UNSEEN synthesis.

This document separates **observed facts**, **bounded interpretations**, and
**hypotheses for future investigation**. Aggregate numbers reconstruct from
the machine-readable analysis; do not treat this file as an independent
data source.

## Provenance (reconstruct every aggregate)

| Item | Value |
|---|---|
| Regime | UNSEEN-domain (`unseen_domain`) |
| Source | `Ćwiczenie 2.2 — Biofizyka głosu ludzkiego` v1 |
| Source SHA-256 | `cd3bfb9a819b415e3cfb382e0737ba22540ccb679d0d34983c40dfbf89a9f7f4` |
| Source size | 5 676 B / 51 lines / 675 whitespace tokens |
| Corpus | `phase2a-authentic-isv` v1 |
| Corpus SHA-256 | `aaad28e43935a40313585d77a33bfc788d97e8d69b081f9486af74d52ca1a857` |
| Design | 7 configurations × direct/primed × r01–r03 = 42 runs |
| Pairing | `Δᵢ = Pᵢ − Dᵢ` by configuration + replicate ID |
| Metrics | identical to HIGH/LOW: `canonical_coverage`, `broader_resource_supported_coverage`, `unresolved_rate`, orthography `outside_inventory` |
| Computational results | `analysis/unseen/dataset.json`, `analysis/unseen/analysis.json`, `analysis/unseen/analysis.md` |
| Regenerator | `scripts/analyze_exp004_phase2b.py --regime unseen` (deterministic; no LLM) |
| Integrity | PASS — 42 evaluated, unique run IDs, complete D↔P pairing, **0 invalid pairings** |

Every mean, SD, and Δ traces to `phase2b/outputs/<run_id>/evaluation.json`
and `orthography.json` via paths listed in `analysis/unseen/dataset.json`.

## Experimental status (fact)

- Collection: **42/42**
- Verification: **42/42**
- Evaluation: **42/42**
- Aggregate analysis: **complete** (integrity PASS; 7/7 primary-valid)
- Qualitative paired D→P audit: **complete** (all 21 pairs)
- No LLM calls during intake, aggregate analysis, or qualitative audit
- Raw `output.txt`, frozen UNSEEN source, frozen corpus, HIGH, and LOW
  artifacts were not modified by this analysis task
- LOW Qwen model-mismatch / Polish-collapse pattern: **not observed** on
  UNSEEN Qwen (inspected; primed remains Interslavic voice-biophysics prose)

## Canonical coverage — observed facts

Primary paired quantity: mean of three replicate Δᵢ values per configuration
(`Δᵢ = primedᵢ − directᵢ`). Values below are **descriptive** (n = 3).

| Configuration | Direct mean | Primed mean | Mean Δ | SD(Δ) | Δ range (pp) |
|---|---:|---:|---:|---:|---|
| Gemini 3.6 Flash — extended thinking ON | 65.77% | 71.45% | +5.68 pp | 3.38 | [+2.12, +8.84] |
| Gemini 3.6 Flash — extended thinking OFF | 63.85% | 69.95% | +6.09 pp | 2.02 | [+3.96, +7.97] |
| Claude Sonnet 5 Medium | 66.07% | 72.48% | +6.42 pp | 1.11 | [+5.14, +7.14] |
| DeepSeek V3 Expert ON | 67.97% | 71.80% | +3.83 pp | 1.06 | [+2.91, +5.00] |
| Qwen 3.8 Max Fast | 67.65% | 71.17% | +3.52 pp | 2.18 | [+1.27, +5.62] |
| GPT-5.6 Luna | 68.53% | 74.05% | +5.52 pp | 2.73 | [+2.43, +7.58] |
| Grok 4.5 Fast | 65.90% | 73.02% | +7.12 pp | 2.17 | [+5.70, +9.62] |

### Direction consistency (canonical Δ, r01/r02/r03)

| Configuration | Δ r01 / r02 / r03 (pp) | Direction |
|---|---|---|
| Gemini ON | +2.12 / +6.08 / +8.84 | all positive |
| Gemini OFF | +7.97 / +3.96 / +6.35 | all positive |
| Claude Sonnet 5 | +7.14 / +5.14 / +6.96 | all positive |
| DeepSeek V3 Expert ON | +2.91 / +5.00 / +3.58 | all positive |
| Qwen 3.8 Max Fast | +3.67 / +1.27 / +5.62 | all positive |
| GPT-5.6 Luna | +6.56 / +7.58 / +2.43 | all positive |
| Grok 4.5 Fast | +6.02 / +9.62 / +5.70 | all positive |

### Observed facts

- **7/7** configurations show a positive mean canonical Δ.
- Descriptive mean of the seven configuration mean-Δ values: **+5.45 pp**.
- **All 21** individual replicate Δs are positive (no mixed-sign configs).
- Mean Δ magnitudes are moderate (about +3.5 to +7.1 pp); SD(Δ) is
  generally smaller than |mean Δ| except Gemini ON (SD 3.38 vs mean 5.68).
- No configuration excluded from the paired aggregate.
- Broader / unresolved / ortho tracks: see `analysis/unseen/analysis.md`.

### Bounded interpretation (not a finding beyond the data)

- Within this UNSEEN cell, the within-sample direction of paired Δ is
  uniformly positive across configurations and replicates.
- Uniform positivity does **not** establish a causal priming effect or
  statistical significance (n = 3).
- Orthography outside-inventory remains a separate diagnostic and does not
  always move with coverage.

## Source-length / genre characteristic (design note)

UNSEEN is substantially **shorter** than HIGH/LOW and is
**expository/educational** (voice biophysics) rather than narrative fiction.
This is a **design characteristic / possible confound**, not a defect and
not corrected for in the metrics. Shorter texts can compress variance and
change how opening-copy / motif-copy behaviours appear relative to HIGH.

## Operational incidents

- **None** that invalidate pairing.
- Minor observation: GPT-5.6 Luna primed r03 wraps the title line in
  markdown bold (`**## Vježba 2.2**`); run remains usable/complete; Δ still
  positive (+2.43 pp).
- Explicit check vs LOW Qwen incident: UNSEEN Qwen Direct and Primed both
  remain Interslavic translations of the biophysics source (no Polish
  collapse; no evidence of Qwen3.7-Plus substitution in prompt headers /
  output character).

## What this record deliberately does not claim

- Statistical significance
- Causal effect of corpus priming
- Model ranking
- HIGH/LOW/UNSEEN synthesis or paper conclusions
- That shorter expository Δs are directly comparable in magnitude to
  narrative HIGH/LOW Δs without caveats

## Related project documents

- Computational report: `analysis.md`
- Qualitative D→P audit: `QUALITATIVE_AUDIT.md`
- Pre-execution source validation: `VALIDATION.md`
- HIGH evidence: `../../EVIDENCE.md`
- LOW evidence: `../low/EVIDENCE.md`
