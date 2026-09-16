# Phase 2B LOW — article-ready evidence record

**Status:** descriptive aggregate results preserved (2026-09-16);
**corrected 2026-09-16** after Qwen model-mismatch incident.
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
| Design (planned) | 7 configurations × direct/primed × r01–r03 = 42 runs |
| **Primary paired analysis** | **6 valid same-model configurations** (18 Direct + 18 Primed = 18 pairs) |
| Invalid pairing | **1** — Qwen: `INVALID — MODEL MISMATCH` (retained; excluded) |
| Pairing | `Δᵢ = Pᵢ − Dᵢ` by configuration + replicate ID (**valid cells only**) |
| Metrics | `canonical_coverage`, `broader_resource_supported_coverage`, `unresolved_rate`, orthography `outside_inventory` (same definitions as HIGH) |
| Computational results | `analysis/low/dataset.json`, `analysis/low/analysis.json`, `analysis/low/analysis.md` |
| Incident record | [`QWEN_INCIDENT.md`](QWEN_INCIDENT.md) + [`invalid_cells.json`](invalid_cells.json) |
| Regenerator | `scripts/analyze_exp004_phase2b.py --regime low` (deterministic; no LLM) |
| Integrity | PASS — 42 evaluated, unique run IDs; primary valid = 6 |

Every mean, SD, and Δ traces to `phase2b/outputs/<run_id>/evaluation.json`
and `orthography.json` via paths listed in `analysis/low/dataset.json`.

## Methodological incident (fact — not a linguistic result)

See [`QWEN_INCIDENT.md`](QWEN_INCIDENT.md) for the full record.

| Item | Value |
|---|---|
| Intended model | Qwen 3.8 Max — Fast |
| Actual Direct | Qwen 3.8 Max — Fast |
| Actual Primed | **Qwen3.7-Plus** (default-selected) |
| Status | **INVALID — MODEL MISMATCH** |
| Qwen3.8-Max Primed service error | `Oops! There was an issue connecting to Qwen3.8-Max.` / `Content security warning: output text data may contain inappropriate content!` |
| Workaround attempted | **NO** |
| Data disposition | retained (not deleted); excluded from primary aggregates |
| Qwen 3.8 Max LOW priming effect | **not estimated** |

Do **not** cite any historical **−12.08 pp** Qwen LOW figure as a
Qwen 3.8 Max priming effect.

## Experimental status (fact)

- Collection: **42/42** retained (including invalid Qwen cell)
- Verification: **42/42**
- Evaluation: **42/42**
- Primary paired analysis: **6/7 configurations valid**
- Aggregate analysis: **complete** (integrity PASS; Qwen excluded from primary)
- Qualitative paired D→P audit: **18 valid pairs** (+ separate Qwen incident note)
  — [`QUALITATIVE_AUDIT.md`](QUALITATIVE_AUDIT.md) +
  [`qualitative_audit.json`](qualitative_audit.json)
- No LLM calls during intake, aggregate analysis, qualitative audit, or
  this correction
- Raw `output.txt`, frozen LOW story, frozen corpus, prompts, and evaluator
  definitions were not modified by the analysis/documentation tasks
- HIGH artifacts under `analysis/` (not `analysis/low/`) were not overwritten
- Gemini LOW data were not modified or reinterpreted
- Gemini primed sessions used the established multi-message corpus
  delivery protocol (context-window / interface constraint); that
  protocol and its results are preserved as executed — not redesigned
  in this correction

## Canonical coverage — observed facts (primary: n=6 valid configs)

Primary paired quantity: mean of three replicate Δᵢ values per
**valid** configuration (`Δᵢ = primedᵢ − directᵢ`). Values below are
**descriptive** (n = 3 per cell).

| Configuration | Direct mean | Primed mean | Mean Δ | SD(Δ) | Δ range (pp) |
|---|---:|---:|---:|---:|---|
| Gemini 3.6 Flash — extended thinking ON | 64.33% | 77.56% | +13.23 pp | 2.33 | [+11.37, +15.84] |
| Gemini 3.6 Flash — extended thinking OFF | 64.51% | 74.91% | +10.40 pp | 4.04 | [+5.91, +13.74] |
| Claude Sonnet 5 Medium | 65.72% | 77.83% | +12.11 pp | 2.50 | [+9.24, +13.82] |
| DeepSeek V3 Expert ON | 68.93% | 75.12% | +6.19 pp | 1.50 | [+5.22, +7.92] |
| GPT-5.6 Luna | 70.75% | 76.06% | +5.31 pp | 0.91 | [+4.73, +6.37] |
| Grok 4.5 Fast | 69.32% | 73.27% | +3.95 pp | 4.96 | [−1.50, +8.21] |

**Qwen 3.8 Max Fast** — excluded from this table (`INVALID — MODEL MISMATCH`).

### Direction consistency (canonical Δ, r01/r02/r03) — valid cells

| Configuration | Δ r01 / r02 / r03 (pp) | Direction |
|---|---|---|
| Gemini ON | +15.84 / +11.37 / +12.48 | all positive |
| Gemini OFF | +13.74 / +11.55 / +5.91 | all positive |
| Claude Sonnet 5 | +13.82 / +9.24 / +13.27 | all positive |
| DeepSeek V3 Expert ON | +5.43 / +7.92 / +5.22 | all positive |
| GPT-5.6 Luna | +4.85 / +6.37 / +4.73 | all positive |
| Grok 4.5 Fast | +8.21 / +5.13 / −1.50 | mixed |

### Overall LOW mean Δ (explicit n)

Descriptive mean of the **six valid** configuration mean-Δ values:
**+8.53 pp** (`n=6 configurations`; all six positive at the mean level;
Grok has one negative replicate).

This **must not** be compared silently to HIGH’s published **7-config**
mean Δ (+7.07 pp). See matched sensitivity below.

### Observed facts (examples suitable for paper Methods/Results)

- Across the **six valid** configurations, all six showed a positive mean
  canonical Δ (Grok mixed at the replicate level).
- Gemini ON/OFF under LOW: all six replicate Δs positive (contrast with
  HIGH, where both Gemini means were near-zero/negative with mixed signs).
- Grok under LOW: mixed signs (+8.21 / +5.13 / −1.50 pp).
- Qwen 3.8 Max LOW priming is **not estimated** (model mismatch + later
  service block on true Qwen3.8-Max Primed).
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
- Orthography outside-inventory is a separate character-level diagnostic.

### Hypotheses / future investigation (not findings)

- Positive LOW Δ **without** corpus-opening near-copy (see qualitative
  audit) is compatible with a reading that HIGH large positive Δs were
  partly overlap/opening-driven — but this remains a **hypothesis**, not
  a causal proof.
- Gemini’s LOW vs HIGH sign flip is compatible with configuration ×
  regime interaction; mechanism unknown.
- Qwen LOW is an **infrastructure/execution incident**, not evidence of
  anti-priming.

## HIGH vs LOW (descriptive only)

### Unequal configuration sets (do not conflate)

| Aggregate | n configs | Mean Δ (canonical) | Note |
|---|---:|---:|---|
| HIGH published | **7** | +7.07 pp | includes valid HIGH Qwen |
| LOW primary (this record) | **6** | +8.53 pp | Qwen excluded as invalid |

### Matched-configuration sensitivity (identical 6 configs)

Qwen excluded on **both** sides so the configuration sets match.
Descriptive only — not a replacement for HIGH’s full 7-config record.

| Configuration | HIGH mean Δ | LOW mean Δ | HIGH dir. | LOW dir. |
|---|---:|---:|---|---|
| Gemini ON | −0.55 pp | +13.23 pp | mixed | all+ |
| Gemini OFF | −1.75 pp | +10.40 pp | mixed | all+ |
| Claude Sonnet 5 | +14.28 pp | +12.11 pp | all+ | all+ |
| DeepSeek V3 Expert ON | +9.25 pp | +6.19 pp | all+ | all+ |
| GPT-5.6 Luna | +8.62 pp | +5.31 pp | all+ | all+ |
| Grok 4.5 Fast | +14.49 pp | +3.95 pp | all+ | mixed |

| Aggregate (matched 6) | Mean Δ |
|---|---:|
| HIGH (matched) | **+7.39 pp** |
| LOW (matched) | **+8.53 pp** |

| Qualitative contrast | HIGH | LOW (valid cells) |
|---|---|---|
| Corpus-opening near-copy in primed | common in large+ configs | **not observed** (openings stay Podkłady-shaped) |
| Lexical borrowing without opening rewrite | often with opening rewrite | present without opening rewrite |

Do **not** rank models. Do **not** treat the HIGH−LOW contrast as a
causal test of H-HIGH by itself. UNSEEN remains unexecuted.

## What this record deliberately does not claim

- Statistical significance (n = 3; no significance tests)
- Causal effect of corpus priming in general
- Model ranking or “best translator”
- A Qwen 3.8 Max LOW priming effect (not estimated)
- That LOW results generalize to UNSEEN
- Final scientific conclusions of Phase 2B

## Related project documents

- Computational report: `analysis/low/analysis.md`
- Qwen incident: `analysis/low/QWEN_INCIDENT.md`
- Qualitative D→P audit: `analysis/low/QUALITATIVE_AUDIT.md`
- HIGH evidence (unchanged): `phase2b/EVIDENCE.md`
- Protocol + kit: `phase2b/README.md`
- Research notes: `docs/RESEARCH_NOTES.md`
- Roadmap status: `docs/research-roadmap.md` §11.2b
