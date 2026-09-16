# Phase 2B LOW — article-ready evidence record

**Status:** descriptive aggregate results preserved (2026-09-16).
**Not:** final scientific conclusions, polished paper draft, or causal claim.

This document separates **observed facts**, **bounded interpretations**, and
**hypotheses for future investigation**. Aggregate numbers reconstruct from
the machine-readable analysis; do not treat this file as an independent
data source.

## Provenance (reconstruct every aggregate)

| Item | Value |
|---|---|
| Regime | LOW-overlap (`low_overlap`) |
| Story | `Podkłady` v1 (approved clean prose; casting/API preamble excluded) |
| Story SHA-256 | `ce1c4fca03fe9cb2c5f8181ab45c91767759a0c785f0a066543d95bc32f5271b` |
| Corpus | `phase2a-authentic-isv` v1 |
| Corpus SHA-256 | `aaad28e43935a40313585d77a33bfc788d97e8d69b081f9486af74d52ca1a857` |
| Design | 7 configurations × direct/primed × r01–r03 = 42 runs |
| Pairing | `Δᵢ = Pᵢ − Dᵢ` by configuration + replicate ID |
| Metrics | `canonical_coverage`, `broader_resource_supported_coverage`, `unresolved_rate`, orthography `outside_inventory` (same definitions as HIGH) |
| Computational results | `analysis/low/dataset.json`, `analysis/low/analysis.json`, `analysis/low/analysis.md` |
| Regenerator | `scripts/analyze_exp004_phase2b.py --regime low` (deterministic; no LLM) |
| Integrity | PASS — 42 evaluated, unique run IDs, complete D↔P pairing |

Every mean, SD, and Δ traces to `phase2b/outputs/<run_id>/evaluation.json`
and `orthography.json` via paths listed in `analysis/low/dataset.json`.

## Experimental status (fact)

- Collection: **42/42**
- Verification: **42/42**
- Evaluation: **42/42**
- Aggregate analysis: **complete** (integrity PASS)
- Qualitative paired D→P audit: **complete** (all 21 pairs; descriptive)
  — [`QUALITATIVE_AUDIT.md`](QUALITATIVE_AUDIT.md) +
  [`qualitative_audit.json`](qualitative_audit.json)
- No LLM calls during intake, aggregate analysis, or qualitative audit
- Raw `output.txt`, frozen LOW story, frozen corpus, prompts, and evaluator
  definitions were not modified by the analysis/documentation tasks
- HIGH artifacts under `analysis/` (not `analysis/low/`) were not overwritten

## Canonical coverage — observed facts

Primary paired quantity: mean of three replicate Δᵢ values per configuration
(`Δᵢ = primedᵢ − directᵢ`). Values below are **descriptive** (n = 3).

| Configuration | Direct mean | Primed mean | Mean Δ | SD(Δ) | Δ range (pp) |
|---|---:|---:|---:|---:|---|
| Gemini 3.6 Flash — extended thinking ON | 64.33% | 77.56% | +13.23 pp | 2.33 | [+11.37, +15.84] |
| Gemini 3.6 Flash — extended thinking OFF | 64.51% | 74.91% | +10.40 pp | 4.04 | [+5.91, +13.74] |
| Claude Sonnet 5 Medium | 65.72% | 77.83% | +12.11 pp | 2.50 | [+9.24, +13.82] |
| DeepSeek V3 Expert ON | 68.93% | 75.12% | +6.19 pp | 1.50 | [+5.22, +7.92] |
| Qwen 3.8 Max Fast | 72.18% | 60.11% | −12.08 pp | 12.76 | [−26.77, −3.68] |
| GPT-5.6 Luna | 70.75% | 76.06% | +5.31 pp | 0.91 | [+4.73, +6.37] |
| Grok 4.5 Fast | 69.32% | 73.27% | +3.95 pp | 4.96 | [−1.50, +8.21] |

### Direction consistency (canonical Δ, r01/r02/r03)

| Configuration | Δ r01 / r02 / r03 (pp) | Direction |
|---|---|---|
| Gemini ON | +15.84 / +11.37 / +12.48 | all positive |
| Gemini OFF | +13.74 / +11.55 / +5.91 | all positive |
| Claude Sonnet 5 | +13.82 / +9.24 / +13.27 | all positive |
| DeepSeek V3 Expert ON | +5.43 / +7.92 / +5.22 | all positive |
| Qwen 3.8 Max Fast | −5.78 / −3.68 / −26.77 | all negative |
| GPT-5.6 Luna | +4.85 / +6.37 / +4.73 | all positive |
| Grok 4.5 Fast | +8.21 / +5.13 / −1.50 | mixed |

### Observed facts (examples suitable for paper Methods/Results)

- Across the seven configurations, **six** showed a positive mean
  canonical Δ and **one** (Qwen 3.8 Max Fast) showed a negative mean
  canonical Δ.
- Descriptive mean of the seven configuration mean-Δ values:
  **+5.59 pp**.
- Gemini ON/OFF under LOW: all six replicate Δs positive (contrast with
  HIGH, where both Gemini means were near-zero/negative with mixed signs).
- Qwen under LOW: all three replicate Δs negative; r03 is an extreme
  orthography/Polish-collapse case (outside-inventory 18→1066).
- Grok under LOW: mixed signs (+8.21 / +5.13 / −1.50 pp).
- Individual D/P/Δ values and the other three metrics are in
  `analysis/low/analysis.md` §2–3 and `analysis/low/dataset.json`.

### Bounded interpretation (not a finding beyond the data)

- For configurations whose three replicate Δs share the same sign, the
  mean Δ summarizes a consistent within-sample direction on this LOW
  story under the measured metrics.
- For Grok, **mean Δ alone is incomplete**: one replicate moved opposite
  the positive mean.
- Unresolved rate moves inversely with canonical coverage under the
  existing evaluator construction; report both, do not invent a composite.
- Orthography outside-inventory is a separate character-level diagnostic;
  Qwen r03 shows that coverage and orthography can diverge violently.

### Hypotheses / future investigation (not findings)

- Positive LOW Δ **without** corpus-opening near-copy (see qualitative
  audit) is compatible with a reading that HIGH large positive Δs were
  partly overlap/opening-driven — but this remains a **hypothesis**, not
  a causal proof.
- Gemini’s LOW vs HIGH sign flip is compatible with configuration ×
  regime interaction; mechanism unknown.
- Qwen’s LOW collapse (especially r03) may reflect interference /
  register failure under priming rather than “anti-priming” as a stable
  effect; n = 3.

## HIGH vs LOW (descriptive only)

| Question | HIGH (frozen) | LOW (this record) |
|---|---|---|
| Mean Δ across 7 configs (canonical) | +7.07 pp | +5.59 pp |
| Positive mean-Δ configs | 5/7 | 6/7 |
| Gemini mean Δ | negative / near-zero, mixed reps | strongly positive, all+ |
| Qwen mean Δ | +5.18 pp (mixed) | −12.08 pp (all−) |
| Corpus-opening near-copy in primed | common in large+ configs | **not observed** (openings stay Podkłady-shaped) |
| Lexical borrowing (črěz / govoret / tutčas / jedino) | often with opening rewrite | present without opening rewrite |

Do **not** rank models. Do **not** treat the HIGH−LOW contrast as a
causal test of H-HIGH by itself. UNSEEN remains unexecuted.

## What this record deliberately does not claim

- Statistical significance (n = 3; no significance tests)
- Causal effect of corpus priming in general
- Model ranking or “best translator”
- That LOW results generalize to UNSEEN
- Final scientific conclusions of Phase 2B

## Related project documents

- Computational report: `analysis/low/analysis.md`
- Qualitative D→P audit: `analysis/low/QUALITATIVE_AUDIT.md`
- HIGH evidence (unchanged): `../EVIDENCE.md` / `../../EVIDENCE.md` → `phase2b/EVIDENCE.md`
- Protocol + kit: `../../README.md`
- Research notes: `docs/RESEARCH_NOTES.md`
- Roadmap status: `docs/research-roadmap.md` §11.2
