# Phase 2B HIGH — article-ready evidence record

**Status:** descriptive aggregate results preserved (2026-09-15).
**Not:** final scientific conclusions, polished paper draft, or causal claim.

This document separates **observed facts**, **bounded interpretations**, and
**hypotheses for future investigation**. Aggregate numbers reconstruct from
the machine-readable analysis; do not treat this file as an independent
data source.

## Provenance (reconstruct every aggregate)

| Item | Value |
|---|---|
| Regime | HIGH-overlap (`high_overlap_corpus_inspired`) |
| Story | `Iskra i Wieloryb — wersja z oryginalnymi nazwami` v1 |
| Story SHA-256 | `ab8a0dcf7352789c09c4aca132c086999c861407e4cd682ee9414aab5b792f63` |
| Corpus | `phase2a-authentic-isv` v1 |
| Corpus SHA-256 | `aaad28e43935a40313585d77a33bfc788d97e8d69b081f9486af74d52ca1a857` |
| Design | 7 configurations × direct/primed × r01–r03 = 42 runs |
| Pairing | `Δᵢ = Pᵢ − Dᵢ` by configuration + replicate ID |
| Metrics | `canonical_coverage`, `broader_resource_supported_coverage`, `unresolved_rate`, orthography `outside_inventory` |
| Computational results | `analysis/dataset.json`, `analysis/analysis.json`, `analysis/analysis.md` |
| Regenerator | `scripts/analyze_exp004_phase2b.py` (deterministic; no LLM) |
| Integrity | PASS — 42 evaluated, unique run IDs, complete D↔P pairing |

Every mean, SD, and Δ traces to `phase2b/outputs/<run_id>/evaluation.json`
and `orthography.json` via paths listed in `analysis/dataset.json`.

## Experimental status (fact)

- Collection: **42/42**
- Verification: **42/42**
- Evaluation: **42/42**
- Aggregate analysis: **complete** (integrity PASS)
- Qualitative paired D→P audit: **complete** (all 21 pairs; descriptive)
  — [`QUALITATIVE_AUDIT.md`](QUALITATIVE_AUDIT.md) +
  [`qualitative_audit.json`](qualitative_audit.json)
- No LLM calls during intake, aggregate analysis, or qualitative audit
- Raw `output.txt`, frozen story, frozen corpus, prompts, and evaluator
  definitions were not modified by the analysis/documentation tasks

## Canonical coverage — observed facts

Primary paired quantity: mean of three replicate Δᵢ values per configuration
(`Δᵢ = primedᵢ − directᵢ`). Values below are **descriptive** (n = 3).

| Configuration | Direct mean | Primed mean | Mean Δ | SD(Δ) | Δ range (pp) |
|---|---:|---:|---:|---:|---|
| Gemini 3.6 Flash — extended thinking ON | 68.68% | 68.13% | −0.55 pp | 2.91 | [−3.77, +1.89] |
| Gemini 3.6 Flash — extended thinking OFF | 67.20% | 65.45% | −1.75 pp | 4.38 | [−5.39, +3.12] |
| Claude Sonnet 5 Medium | 69.29% | 83.57% | +14.28 pp | 2.26 | [+12.20, +16.69] |
| DeepSeek V3 Expert ON | 74.53% | 83.78% | +9.25 pp | 2.57 | [+6.68, +11.82] |
| Qwen 3.8 Max Fast | 76.36% | 81.54% | +5.18 pp | 5.56 | [−1.23, +8.70] |
| GPT-5.6 Luna | 73.54% | 82.16% | +8.62 pp | 1.34 | [+7.06, +9.43] |
| Grok 4.5 Fast | 68.35% | 82.84% | +14.49 pp | 5.90 | [+8.20, +19.89] |

### Observed facts (examples suitable for paper Methods/Results)

- Across the seven configurations, **five** showed a positive mean
  canonical Δ and **two** (both Gemini 3.6 Flash conditions) showed a
  negative mean canonical Δ.
- Claude Sonnet 5 Medium: mean canonical Δ = **+14.28 pp** across three
  paired repeats; all three replicate Δs were positive
  ([+12.20, +16.69] pp).
- Grok 4.5 Fast: mean canonical Δ = **+14.49 pp**; all three replicate
  Δs were positive ([+8.20, +19.89] pp).
- Gemini 3.6 Flash — extended thinking ON: replicate Δs were
  **+1.89 / −3.77 / +0.23 pp** (mixed signs); mean Δ = −0.55 pp.
- Gemini 3.6 Flash — extended thinking OFF: replicate Δs were
  **−5.39 / +3.12 / −2.98 pp** (mixed signs); mean Δ = −1.75 pp.
- Qwen 3.8 Max Fast: replicate Δs were **+8.70 / +8.07 / −1.23 pp**
  (mixed signs); mean Δ = +5.18 pp.
- Individual D/P/Δ values, run IDs, and the other three metrics are in
  `analysis/analysis.md` §2–3 and `analysis/dataset.json`.

### Bounded interpretation (not a finding beyond the data)

- For configurations whose three replicate Δs share the same sign, the
  mean Δ summarizes a consistent within-sample direction on this HIGH
  story under the measured metrics.
- For Gemini ON, Gemini OFF, and Qwen, **mean Δ alone is misleading**:
  at least one replicate moved opposite the mean.
- Unresolved rate moves inversely with canonical coverage under the
  existing evaluator construction; report both, do not invent a composite.
- Orthography outside-inventory is a separate character-level diagnostic;
  it must not be collapsed into canonical/broader coverage.

### Hypotheses / future investigation (not findings)

- Configuration-dependent differences in mean Δ **may** reflect
  model-specific sensitivity to target-language contextual grounding on
  HIGH-overlap material; this is untested against LOW and UNSEEN regimes.
- H-HIGH (larger priming improvement under high thematic overlap) remains
  a **hypothesis** until Δ_HIGH can be compared with Δ_LOW and Δ_UNSEEN.
- Mixed-sign Gemini/Qwen replicate patterns **may** warrant closer
  inspection of within-condition variance versus shift magnitude; no
  mechanistic explanation is asserted here.
- Qualitative audit observation (hypothesis-level): large positive HIGH
  deltas often co-occur with near-reproduction of the overlapping corpus
  narrative opening; Gemini configs largely lack that pattern — see
  `QUALITATIVE_AUDIT.md`.

## What this record deliberately does not claim

- Statistical significance (n = 3; no significance tests run for Phase 2B HIGH)
- Causal effect of corpus priming in general
- Model ranking or “best translator”
- That HIGH-overlap results generalize to LOW or UNSEEN
- Final scientific conclusions of Phase 2B

## Related project documents

- Computational report: `analysis/analysis.md`
- Qualitative D→P audit: `QUALITATIVE_AUDIT.md` (+ `qualitative_audit.json`)
- Protocol + kit: `README.md`
- Research notes: `docs/RESEARCH_NOTES.md` §4.25
- Roadmap status: `docs/research-roadmap.md` §11.2
- Experiment log: `docs/EXPERIMENTS.md` (Phase 2B HIGH entry)
