# Phase 2B HIGH vs LOW — article-ready evidence record

**Status:** exploratory descriptive synthesis preserved (2026-09-16).  
**Not:** final scientific conclusions, causal claim, significance test, or model ranking.

This document separates **observed facts**, **bounded interpretations**, and
**hypotheses**. Numbers reconstruct from [`analysis.json`](analysis.json)
and the frozen HIGH/LOW aggregates.

## Provenance

| Item | Value |
|---|---|
| HIGH story | `Iskra i Wieloryb` v1 (`ab8a0dcf…792f63`) |
| LOW story | `Podkłady` v1 (`ce1c4fca…5271b`) |
| Corpus | `phase2a-authentic-isv` v1 (`aaad28e4…a857`) |
| HIGH sample | 7 configs × 42 runs (Qwen included) |
| LOW primary | **6 valid** configs / 18 pairs (Qwen excluded) |
| Matched set | same 6 configs in HIGH and LOW |
| Computational companion | [`analysis.json`](analysis.json), [`analysis.md`](analysis.md) |
| HIGH primary | `phase2b/analysis/`, `phase2b/EVIDENCE.md` (unchanged) |
| LOW primary | `phase2b/analysis/low/` (unchanged by this synthesis write) |

## Observed facts (supported)

### Matched aggregate

| Set | n | Mean canonical Δ |
|---|---:|---:|
| HIGH matched | 6 | +7.39 pp |
| LOW matched | 6 | +8.53 pp |
| Difference (LOW − HIGH) | 6 | +1.14 pp |

The 1.14 pp difference is **not** interpretable as a meaningful effect size
on its own.

### Configuration table (canonical mean Δ)

| Configuration | HIGH | LOW | LOW − HIGH | Classes |
|---|---:|---:|---:|---|
| Gemini ON | −0.55 | +13.23 | +13.78 | direction reversal; large magnitude change |
| Gemini OFF | −1.75 | +10.40 | +12.15 | direction reversal; large magnitude change |
| Claude Sonnet 5 | +14.28 | +12.11 | −2.17 | same direction; similar magnitude |
| DeepSeek Expert ON | +9.25 | +6.19 | −3.05 | same direction; similar magnitude |
| GPT-5.6 Luna | +8.62 | +5.31 | −3.30 | same direction; similar magnitude |
| Grok 4.5 Fast | +14.49 | +3.95 | −10.54 | same-sign means; large magnitude change; LOW mixed reps |

### Qualitative (fact-level)

- HIGH: large positive Δs often co-occur with corpus-opening / motif near-copy.
- LOW (valid): no systematic corpus-opening near-copy; lexical borrowing and
  orthography/Polish-residue cleanup recur with Podkłady structure retained.
- LOW can show large positive Δ without HIGH-style opening rewrite.

### Infrastructure (fact-level, not linguistic)

- Qwen LOW: `INVALID — MODEL MISMATCH`; Qwen3.8-Max Primed later blocked by
  content-security warning; **no workaround**; priming **not estimated**.
- Gemini LOW: multi-message protocol for context constraint; results valid
  as executed.

## Bounded interpretations (compatible, not demonstrated)

- Overlap with corpus-like openings/motifs may contribute to some HIGH gains.
- Priming response appears substantially configuration-associated (Gemini
  reversal; Grok drop; Claude-like stability).
- LOW gains may reflect local lexical/ortho conditioning without narrative
  reuse.
- Coverage metrics may be sensitive to orthography/lexis independently of
  human-judged quality.

## Not established

- Causal corpus priming; proof of H-HIGH; a law that HIGH Δ > LOW Δ;
  configuration as sole cause; significance; rankings; UNSEEN behavior;
  Qwen3.8-Max LOW priming.

## Article-ready paragraph

Across two Phase 2B source regimes, authentic-corpus priming is associated
with configuration-specific shifts in resource-supported Interslavic
coverage rather than with a single, uniform HIGH>LOW pattern. On a matched
six-configuration set, mean canonical Δ was descriptively similar across
regimes (HIGH +7.39 pp; LOW +8.53 pp), while Gemini reversed from near-zero
or negative HIGH effects to large positive LOW effects, and several other
configurations remained positive in both regimes with smaller magnitude
changes. Qualitative inspection suggests that large HIGH gains often
coincide with corpus-opening reuse, whereas LOW gains more often occur
without that signature. These observations are compatible with both
overlap-sensitive and configuration-sensitive accounts; they do not
establish either mechanism, nor do they license causal or ranking claims.
UNSEEN-domain evidence remains absent.

## Related

- Full narrative: [`analysis.md`](analysis.md)
- HIGH evidence: [`../../EVIDENCE.md`](../../EVIDENCE.md)
- LOW evidence: [`../low/EVIDENCE.md`](../low/EVIDENCE.md)
- Qwen incident: [`../low/QWEN_INCIDENT.md`](../low/QWEN_INCIDENT.md)
