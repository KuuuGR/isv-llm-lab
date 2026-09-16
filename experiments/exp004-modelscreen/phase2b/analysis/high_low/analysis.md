# Phase 2B HIGH vs LOW — cross-regime synthesis (descriptive)

**Status:** exploratory descriptive synthesis (2026-09-16).  
**Not:** a causal test, significance analysis, model ranking, or UNSEEN claim.  
**Generator:** synthesis from frozen HIGH/LOW aggregates + qualitative audits; **no LLM sessions**.

Machine-readable companion: [`analysis.json`](analysis.json)  
Article-ready layered record: [`EVIDENCE.md`](EVIDENCE.md)

## Research question

> Across HIGH-overlap and LOW-overlap source texts, does the observed
> priming effect show a pattern more consistent with source/corpus
> overlap, or does it appear primarily configuration/model-dependent?

This document explores that question **descriptively**. It does **not**
claim the data prove either explanation.

## Data scope

| Regime | What is used |
|---|---|
| **HIGH** | 7 planned configs, 42 observations (includes valid HIGH Qwen) |
| **LOW primary** | **6 valid** same-model configs, 18 pairs (Qwen excluded) |
| **Matched comparison** | identical 6 configs in HIGH and LOW (Qwen out on both sides) |

Qwen LOW is `INVALID — MODEL MISMATCH` (Direct=Qwen3.8-Max;
Primed=Qwen3.7-Plus). It is retained as infrastructure evidence only;
**Qwen3.8-Max LOW priming is not estimated.** See
[`../low/QWEN_INCIDENT.md`](../low/QWEN_INCIDENT.md).

Gemini LOW used the established multi-message corpus protocol
(context-window constraint). Those results remain **valid under the
executed protocol** and are not reinterpreted here.

---

## 1. Cross-regime configuration stability (matched 6)

Canonical mean Δ = mean of three replicate Δᵢ = Pᵢ − Dᵢ.  
**LOW − HIGH** = difference of configuration mean-Δ values (pp).

| Configuration | HIGH Δ | LOW Δ | LOW − HIGH | HIGH dir. | LOW dir. | Descriptive class |
|---|---:|---:|---:|---|---|---|
| Gemini ON | −0.55 | +13.23 | **+13.78** | mixed | all+ | direction reversal; magnitude substantially changed |
| Gemini OFF | −1.75 | +10.40 | **+12.15** | mixed | all+ | direction reversal; magnitude substantially changed |
| Claude Sonnet 5 | +14.28 | +12.11 | −2.17 | all+ | all+ | same direction; magnitude similar (<5 pp) |
| DeepSeek Expert ON | +9.25 | +6.19 | −3.05 | all+ | all+ | same direction; magnitude similar (<5 pp) |
| GPT-5.6 Luna | +8.62 | +5.31 | −3.30 | all+ | all+ | same direction; magnitude similar (<5 pp) |
| Grok 4.5 Fast | +14.49 | +3.95 | **−10.54** | all+ | mixed | same direction (means); magnitude substantially changed |

### Replicate-level detail (canonical Δ, pp)

| Configuration | HIGH r01 / r02 / r03 | LOW r01 / r02 / r03 |
|---|---|---|
| Gemini ON | +1.89 / −3.77 / +0.23 | +15.84 / +11.37 / +12.48 |
| Gemini OFF | −5.39 / +3.12 / −2.98 | +13.74 / +11.55 / +5.91 |
| Claude | +16.69 / +13.96 / +12.20 | +13.82 / +9.24 / +13.27 |
| DeepSeek ON | +9.24 / +11.82 / +6.68 | +5.43 / +7.92 / +5.22 |
| GPT-5.6 Luna | +9.43 / +7.06 / +9.35 | +4.85 / +6.37 / +4.73 |
| Grok | +15.37 / +19.89 / +8.20 | +8.21 / +5.13 / −1.50 |

### Explicitly identified instabilities

- **Gemini direction reversals:** both ON and OFF flip from HIGH
  near-zero/negative (mixed) to LOW strongly positive (all+).
- **Both-regime positives:** Claude, DeepSeek, GPT, Grok (means).
- **Grok LOW mixed replicate direction:** one negative replicate
  (−1.50 pp) despite positive mean.
- **Grok magnitude drop:** HIGH +14.49 → LOW +3.95 (−10.54 pp) while
  remaining positive at the mean — notable instability without a
  direction reversal of the mean.

These classes are **descriptive labels only**, not scores or rankings.

---

## 2. Matched HIGH vs LOW descriptive comparison

| Aggregate | n configs | Mean canonical Δ |
|---|---:|---:|
| HIGH published (full) | 7 | +7.07 pp |
| HIGH matched | **6** | **+7.39 pp** |
| LOW primary / matched | **6** | **+8.53 pp** |
| LOW − HIGH (matched) | 6 | **+1.14 pp** |

Do **not** interpret the 1.14 pp aggregate difference as meaningful by
itself. Do **not** silently compare LOW n=6 to HIGH’s published n=7
without stating unequal configuration sets.

---

## 3. Does overlap track with Δ?

### What supports a simple “HIGH-overlap → larger Δ” story

- HIGH large positive Δs (Claude, DeepSeek, Grok, often GPT/Qwen) commonly
  co-occur with **corpus-opening / motif near-copy** in the qualitative
  audit.
- LOW lacks that systematic opening rewrite, so HIGH’s largest effects
  are **compatible with** overlap-driven narrative reuse.

### What contradicts a simple overlap story

- Matched aggregate means are **not** HIGH ≫ LOW; LOW +8.53 vs HIGH +7.39.
- Gemini shows **larger** positive Δ under LOW than under HIGH, despite
  LOW’s weaker thematic overlap and **without** HIGH-style opening copy.
- Several LOW configs remain clearly positive with Podkłady openings
  retained (lexical borrowing / ortho cleanup without motif swap).
- Configuration-level direction and magnitude vary more than a single
  overlap scalar would predict (Gemini reversal; Grok drop).

**Bounded reading:** overlap with corpus-like material is a **plausible
contributor** to some HIGH gains, especially where opening-copy is
visible; it is **not** a sufficient account of Δ across regimes.

---

## 4. Does model/configuration appear important?

Observed configuration patterns (descriptive, not causal):

| Configuration | HIGH → LOW (mean Δ) | Pattern note |
|---|---|---|
| Gemini ON | −0.55 → +13.23 | large reversal |
| Gemini OFF | −1.75 → +10.40 | large reversal |
| Claude | +14.28 → +12.11 | stable positive, mild drop |
| DeepSeek ON | +9.25 → +6.19 | stable positive, mild drop |
| GPT | +8.62 → +5.31 | stable positive, mild drop |
| Grok | +14.49 → +3.95 | same-sign mean, large magnitude drop; LOW mixed reps |

**Observation:** the response to priming is **highly
configuration-associated** in this sample — Gemini’s regime flip and
Grok’s magnitude change are as salient as any regime-level mean. This
does **not** prove a model-level causal mechanism; n=3 and two stories
only.

---

## 5. Qualitative mechanism comparison

| Phenomenon | HIGH | LOW (valid pairs) |
|---|---|---|
| 1. Corpus-opening / motif copying | Recurrent in large+ configs | **Not systematic**; openings stay Podkłady-shaped |
| 2. Lexical borrowing from corpus | Common, often with opening rewrite | Common **without** opening rewrite |
| 3. Orthographic normalization | Often with positive Δ; can diverge | Often (Gemini/Claude); not universal |
| 4. Polish-residue reduction | Often with improvement | Often with improvement |
| 5. Structural changes | Frequent winter-opening / world swap | Usually plot continuity |
| 6. Other local lexical effects | Kit/Velryb, local substitutions | Katarzyna/Katarina, local synonyms |

**Score vs visible borrowing:** higher canonical Δ sometimes coincides
with opening-copy (HIGH large+), but LOW shows substantial Δ↑ with little
obvious motif copy (especially Gemini). Visible corpus borrowing is
therefore **neither necessary nor proven beneficial/harmful** as a
universal mechanism.

---

## 6. Alternative explanations (not ranked)

Plausible accounts consistent with the data include:

1. source/corpus lexical & motif overlap;
2. model/configuration differences;
3. stochastic variation between repeats (n=3);
4. prompt/context handling differences;
5. context-window / multi-message delivery (Gemini protocol);
6. service/infrastructure constraints (Qwen filter incident);
7. scoring sensitivity to orthography and lexical choices.

No single explanation is established as fact.

---

## 7. Infrastructure notes (not linguistic findings)

### Qwen

- LOW Qwen Direct/Primed pair invalid (3.8-Max vs 3.7-Plus).
- Later Qwen3.8-Max Primed produced a content-security / connection
  warning; **no workaround**.
- Qwen3.8-Max LOW priming effect: **not estimated**.

### Gemini

- LOW priming used the established multi-message protocol for the
  context constraint.
- Gemini data remain valid under that executed protocol.
- This is an infrastructure/protocol observation, not a reason to
  reinterpret Δ as invalid.

---

## 8. What HIGH + LOW can actually tell us

### Supported observations

- Matched 6-config means: HIGH +7.39 pp, LOW +8.53 pp (descriptive).
- Gemini reverses from HIGH≈0/− to LOW large+.
- Claude / DeepSeek / GPT stay positive with modest mean shifts.
- Grok stays positive at the mean but drops substantially; LOW mixed.
- HIGH large+ often co-occurs with opening-copy; LOW large+ often does not.
- Positive LOW Δ occurs without systematic corpus-opening near-copy.

### Compatible hypotheses

- Part of HIGH Δ may reflect overlap with corpus-like openings/motifs.
- Priming response is substantially configuration-dependent.
- LOW gains may reflect local lexical/ortho conditioning without narrative
  reuse.
- Coverage metrics may amplify some changes independently of human quality.

### Not established

- Causal priming in general; H-HIGH as proven; HIGH≻LOW overlap law;
  configuration as sole cause; significance; rankings; UNSEEN behavior;
  Qwen3.8-Max LOW priming.

---

## Suggested article-ready framing (Results/Discussion draft)

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

---

## Provenance / immutability

- Sources: `phase2b/analysis/{dataset,analysis}.{json,md}`,
  `phase2b/analysis/low/{dataset,analysis}.{json,md}`,
  `phase2b/QUALITATIVE_AUDIT.md`,
  `phase2b/analysis/low/QUALITATIVE_AUDIT.md`,
  `phase2b/analysis/low/QWEN_INCIDENT.md`.
- Does **not** overwrite HIGH or LOW primary aggregates.
- Does **not** modify frozen stories or corpus.
- No LLM sessions.
