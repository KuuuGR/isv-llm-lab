# Phase 2B HIGH — qualitative paired Direct → Primed audit

**Status:** descriptive qualitative audit of existing evidence (2026-09-15).  
**Not:** a new experiment, causal claim, grammar adjudication, or replacement for the quantitative aggregate.

Machine-readable pair ledger: [`qualitative_audit.json`](qualitative_audit.json)  
Quantitative source of truth: [`analysis/dataset.json`](analysis/dataset.json)  
Article-ready quantitative record: [`EVIDENCE.md`](EVIDENCE.md)

> All **21** Direct↔Primed pairs were inspected (7 configurations × r01–r03).  
> Classifications are **apparent** judgments relative to resource-supported /
> orthographic signals and corpus-overlap observations — not proof of
> linguistic correctness.

---

## D. Limitations (read first)

1. This audit is **descriptive**.
2. No causal inference: a primed form differing from a direct form does **not**
   by itself prove that the model “learned” a rule from the corpus.
3. Some apparent improvements may partly reflect **evaluator behaviour**
   (canonical lexicon hits) rather than human-judged Interslavic quality.
4. HIGH intentionally has **strong corpus/task overlap** (the frozen story is
   `high_overlap_corpus_inspired`). Large positive Δs often coincide with
   near-reproduction of the narrative register corpus opening
   (`tuta-historija-excerpt.txt`: *Ljudi govoret, že v tamtoj denj…*).
5. **n = 3** per configuration limits generalization.
6. Orthography outside-inventory and coverage can **move in opposite
   directions** within the same pair.

---

## A. Pair-level audit table (all 21)

Canonical values from `analysis/dataset.json`. Δ = P − D (percentage points).

### Gemini 3.6 Flash — extended thinking ON (mean Δ −0.55 pp; mixed signs)

| rep | direct run_id | primed run_id | D% | P% | Δ pp | ortho D→P | concise differences | classes |
|---|---|---|---:|---:|---:|---|---|---|
| r01 | `…__extthinkon__direct__r01` | `…__extthinkon__primed__r01` | 66.26 | 68.15 | +1.89 | 142→118 | Lexical/orthographic reshuffles (Benedykt/Benedikt, ključ/kluč); serce↑; opening stays non-corpus-like | neutral / ambiguous |
| r02 | `…__extthinkon__direct__r02` | `…__extthinkon__primed__r02` | 71.03 | 67.26 | −3.77 | 60→150 | Negative Δ; Polish-letter load and outside-inventory rise; se→sę drift; no corpus-opening adoption | degradation / neutral |
| r03 | `…__extthinkon__direct__r03` | `…__extthinkon__primed__r03` | 68.76 | 68.98 | +0.23 | 100→102 | Near-zero Δ; title Kit→Veloryb; Polish *tylko* rises in primed | neutral / ambiguous / degradation |

### Gemini 3.6 Flash — extended thinking OFF (mean Δ −1.75 pp; mixed signs)

| rep | direct run_id | primed run_id | D% | P% | Δ pp | ortho D→P | concise differences | classes |
|---|---|---|---:|---:|---:|---|---|---|
| r01 | `…__extthinkoff__direct__r01` | `…__extthinkoff__primed__r01` | 68.16 | 62.77 | −5.39 | 65→68 | Largest OFF drop; Veloryb→Kit; *tylko*/*serce* rise; no `v tamtoj denj` | degradation / ambiguous |
| r02 | `…__extthinkoff__direct__r02` | `…__extthinkoff__primed__r02` | 67.55 | 70.66 | +3.12 | 145→34 | Only positive OFF replicate; ortho improves; *się* cleared; still weak corpus-opening echo | improvement / neutral |
| r03 | `…__extthinkoff__direct__r03` | `…__extthinkoff__primed__r03` | 65.88 | 62.90 | −2.98 | 204→57 | Coverage falls while ortho improves — dimensions diverge; *tylko* cleared | ambiguous / degradation |

### Claude Sonnet 5 Medium (mean Δ +14.28 pp; all positive)

| rep | direct run_id | primed run_id | D% | P% | Δ pp | ortho D→P | concise differences | classes |
|---|---|---|---:|---:|---:|---|---|---|
| r01 | `…__sonnet-5__direct__r01` | `…__sonnet-5__primed__r01` | 66.82 | 83.51 | +16.69 | 365→18 | Cyrillic soft signs cleared (*medlьno*); Kit→Velryb; primed opening tracks corpus | improvement |
| r02 | `…__sonnet-5__direct__r02` | `…__sonnet-5__primed__r02` | 69.30 | 83.27 | +13.96 | 12→8 | Kit→Velryb; *ale*→*no*; near-corpus opening (*govoret*, *pomalo*, *jedino*) | improvement |
| r03 | `…__sonnet-5__direct__r03` | `…__sonnet-5__primed__r03` | 71.73 | 83.93 | +12.20 | 18→70 | Same corpus-opening gain, but title Wieloryb→**Velerman**; ortho worsens | improvement + degradation |

### DeepSeek V3 Expert ON (mean Δ +9.25 pp; all positive)

| rep | direct run_id | primed run_id | D% | P% | Δ pp | ortho D→P | concise differences | classes |
|---|---|---|---:|---:|---:|---|---|---|
| r01 | `…__deepthinkon__direct__r01` | `…__deepthinkon__primed__r01` | 74.30 | 83.54 | +9.24 | 35→23 | Kit→Velryb; *teraz* cleared; corpus lexis (*pomalo*, *jedino*, *črěz*, *tutčas*) | improvement |
| r02 | `…__deepthinkon__direct__r02` | `…__deepthinkon__primed__r02` | 73.36 | 85.18 | +11.82 | 38→13 | Strongest DeepSeek Δ; Kit→Velryb; opening near-corpus; *je*/*sut* density ↑ | improvement / ambiguous |
| r03 | `…__deepthinkon__direct__r03` | `…__deepthinkon__primed__r03` | 75.94 | 82.63 | +6.68 | 23→18 | Same Kit→Velryb + corpus-opening pattern; milder polish-char drop | improvement |

### Qwen 3.8 Max Fast (mean Δ +5.18 pp; mixed signs)

| rep | direct run_id | primed run_id | D% | P% | Δ pp | ortho D→P | concise differences | classes |
|---|---|---|---:|---:|---:|---|---|---|
| r01 | `…__fast__direct__r01` | `…__fast__primed__r01` | 76.41 | 85.11 | +8.70 | 56→28 | Veloryb→Veleryb; *ale*→*no*; primed opening matches corpus narrative | improvement / neutral |
| r02 | `…__fast__direct__r02` | `…__fast__primed__r02` | 76.32 | 84.39 | +8.07 | 32→25 | Veloryb→Velryb; *čo*→*čto*; corpus-opening adoption | improvement |
| r03 | `…__fast__direct__r03` | `…__fast__primed__r03` | 76.35 | 75.12 | −1.23 | 42→110 | Negative replicate: corpus opening present, but title → Polish *Wieloryb* / *wersija*; ortho↑ | degradation / ambiguous |

### GPT-5.6 Luna (mean Δ +8.62 pp; all positive)

| rep | direct run_id | primed run_id | D% | P% | Δ pp | ortho D→P | concise differences | classes |
|---|---|---|---:|---:|---:|---|---|---|
| r01 | `…__thinkoff__direct__r01` | `…__thinkoff__primed__r01` | 72.31 | 81.75 | +9.43 | 189→51 | Polish residues (*skazał*, *dnia*) ↓; Veloryb→Velryb; partial corpus alignment | improvement |
| r02 | `…__thinkoff__direct__r02` | `…__thinkoff__primed__r02` | 75.65 | 82.71 | +7.06 | 126→22 | Cyrillic/Polish residues ↓; Veloryb→Velryb; *tutčas*/*jedino* appear | improvement |
| r03 | `…__thinkoff__direct__r03` | `…__thinkoff__primed__r03` | 72.67 | 82.02 | +9.35 | 95→37 | Velikoryb→Velryb; *medlěno*→*pomalo*; *kotory*→*ktory* | improvement |

### Grok 4.5 Fast (mean Δ +14.49 pp; all positive)

| rep | direct run_id | primed run_id | D% | P% | Δ pp | ortho D→P | concise differences | classes |
|---|---|---|---:|---:|---:|---|---|---|
| r01 | `…__fast__direct__r01` | `…__fast__primed__r01` | 68.62 | 83.99 | +15.37 | 269→5 | Polish-letter collapse; Veloryb→Velryb; *što*→*čto*; corpus opening | improvement |
| r02 | `…__fast__direct__r02` | `…__fast__primed__r02` | 64.27 | 84.17 | +19.89 | 540→26 | Largest Δ in the set; extreme ortho cleanup; near-verbatim corpus opening | improvement |
| r03 | `…__fast__direct__r03` | `…__fast__primed__r03` | 72.15 | 80.36 | +8.20 | 42→114 | Title already Velryb in direct; corpus opening still adopted; ortho worsens while coverage rises | improvement / ambiguous |

Full run IDs and paths: `qualitative_audit.json`.

---

## B. Configuration summaries

### Gemini ON (mean Δ −0.55)
Changes are mostly **local lexical/orthographic churn** without adopting the
corpus narrative opening (opening↔corpus Jaccard stays ~0.09–0.17 for both
conditions). Replicate signs mix; r02 pairs coverage loss with ortho
worsening. Priming here does **not** look like systematic corpus-register
rewrite.

### Gemini OFF (mean Δ −1.75)
Same weak corpus-opening adoption. Two of three replicates negative. Ortho
and coverage often **disagree** (r03: ortho improves, canonical falls).
Title choice can move *away* from corpus whale form (r01: Veloryb→Kit).

### Claude Medium (mean Δ +14.28)
Most consistent **corpus-register rewrite** of the opening plus cleanup of
severe direct-side Cyrillic soft-sign contamination (r01). All Δs positive.
Caveat: r03 produces title **Velerman** (apparent name degradation) even as
coverage rises.

### DeepSeek Expert ON (mean Δ +9.25)
Reliable Kit→Velryb + corpus-opening pattern across all three replicates;
Polish time adverb *teraz* and non-corpus lexis drop. Auxiliary *je*/*sut*
density can surge (r02) — coverage gain may partly be formulaic.

### Qwen Max Fast (mean Δ +5.18)
r01–r02 follow the positive corpus-opening pattern; **r03 contradicts**
(negative Δ): opening still corpus-like, but Polish *Wieloryb*/*wersija*
and worse ortho reappear. Illustrates why mean Δ alone misleads.

### GPT-5.6 Luna (mean Δ +8.62)
Consistent reduction of Polish morphology residues and movement toward
corpus whale form *Velryb* + corpus lexis (*pomalo*, *jedino*, *tutčas*).
Opening alignment is strong but usually slightly less verbatim than
Claude/Grok/Qwen (Jaccard ~0.46–0.47 vs ~0.70).

### Grok 4.5 Fast (mean Δ +14.49)
Largest magnitudes; direct often heavily Polish-letter contaminated; primed
collapses that load and adopts corpus opening. r03 shows coverage↑ with
ortho↑ — again, dimensions are not interchangeable.

---

## C. Representative examples (few)

Interpretation status: **Observed** = attested D vs P forms; **Hypothesis** =
plausible reading, not established.

### Example 1 — Corpus-opening adoption (Claude r01) · apparent improvement

| field | value |
|---|---|
| Configuration / replicate | Claude Sonnet 5 Medium / r01 |
| Direct run | `2026-09-09__p2b-high__anthropic__claude__sonnet-5__direct__r01` |
| Primed run | `2026-09-09__p2b-high__anthropic__claude__sonnet-5__primed__r01` |
| Source reference | HIGH story prolog; corpus `tuta-historija-excerpt.txt` opening |
| Direct | `Iskra i Kit` … `oblaky šli medlьno` … `govore` |
| Primed | `Iskra i Velryb` … `v tamtoj denj bylo je veliko spokojno` … `oblaky šli pomalo` … `govoret` |
| Corpus parallel | `Ljudi govoret, že v tamtoj denj bylo je veliko spokojno` … `oblaky šli pomalo` |
| Observed | Primed opening is much closer to the authentic corpus narrative register than direct; Cyrillic soft signs disappear. |
| Hypothesis | Priming may have supplied ready narrative ISV for an overlapping scene, not only abstract “grammar learning.” |

### Example 2 — Orthography collapse with coverage gain (Grok r02) · apparent improvement

| field | value |
|---|---|
| Configuration / replicate | Grok 4.5 Fast / r02 |
| Direct / Primed runs | `…__grok__fast__direct__r02` / `…__grok__fast__primed__r02` |
| Direct | `Veloryb`, high Polish-letter load, ortho outside-inventory **540** |
| Primed | `Velryb`, corpus opening, ortho **26**, Δ **+19.89 pp** |
| Observed | Primed reduces Polish-character contamination and matches corpus whale/opening forms. |
| Hypothesis | Large Δ may combine interference reduction with HIGH overlap copying. |

### Example 3 — Name degradation despite positive Δ (Claude r03) · mixed

| field | value |
|---|---|
| Configuration / replicate | Claude Sonnet 5 Medium / r03 |
| Direct | title `Iskra i Wieloryb` (Polish *Wieloryb*) |
| Primed | title `Iskra i Velerman` |
| Observed | Coverage rises (+12.20 pp) and opening becomes corpus-like, but the whale name becomes an odd non-corpus form. |
| Hypothesis | Coverage metrics can improve while a salient proper-name choice degrades. |

### Example 4 — Negative / mixed Gemini pattern (Gemini OFF r01) · apparent degradation

| field | value |
|---|---|
| Configuration / replicate | Gemini 3.6 Flash — ext. thinking OFF / r01 |
| Direct | `Iskra i Veloryb` |
| Primed | `Iskra i Kit`; *tylko* appears; Δ **−5.39 pp** |
| Observed | Primed moves *away* from corpus whale form and increases Polish *tylko*; opening does not adopt `v tamtoj denj`. |
| Hypothesis | For Gemini under HIGH, priming did not induce the same corpus-register rewrite seen in Claude/Grok/DeepSeek/Qwen/GPT. |

### Example 5 — Contradictory Qwen r03 · ambiguous / degradation

| field | value |
|---|---|
| Configuration / replicate | Qwen 3.8 Max Fast / r03 |
| Direct | `Iskra i Veloryb — versija…` |
| Primed | `Iskra i Wieloryb — wersija…` (Polish *w*) despite corpus-like body opening |
| Observed | Corpus opening adopted, but title/ortho worsen and canonical Δ is negative. |
| Hypothesis | Corpus echo and surface interference can coexist; mean Δ hides this replicate. |

---

## Relationship to canonical Δ (descriptive)

| Pattern | Configurations | Qualitative character |
|---|---|---|
| Consistently large positive Δ | Claude, Grok | Corpus-opening near-copy + interference/ortho cleanup |
| Consistently moderate–large positive Δ | DeepSeek, GPT-5.6 Luna | Same direction; GPT slightly less verbatim at opening |
| Positive mean, one negative replicate | Qwen | r03 shows corpus echo **with** Polish title/ortho regression |
| Near-zero / negative mean, mixed signs | Gemini ON, Gemini OFF | Local churn; **no** systematic corpus-opening rewrite |

This supports reading HIGH positive deltas as partly **overlap-driven
surface alignment** with the priming narrative, especially in openings —
a reason LOW/UNSEEN matter before generalizing.

---

## Issues to investigate before LOW

1. **How much of Δ_HIGH is opening/motif copy vs broader grammatical change?**  
   Segment-level or motif-masked analysis would help.
2. **Proper-name instability** (Kit / Veloryb / Velryb / Wieloryb / Velerman /
   Veleryb / Velikoryb) — decide whether name handling is scored separately.
3. **Coverage vs orthography divergence** (Gemini OFF r03, Claude r03, Grok r03,
   Qwen r03) — do not collapse into one quality story.
4. **Gemini non-adoption of corpus opening** under HIGH — mechanism unknown;
   do not assume LOW will look like Claude/Grok.
5. Keep H-HIGH as a **hypothesis** until LOW/UNSEEN exist.

---

## Provenance / immutability

- Inspected existing `phase2b/outputs/<run_id>/output.txt` only.
- Metrics taken from `analysis/dataset.json` (already evaluated).
- Corpus parallels checked against local
  `phase2a/corpus/tuta-historija-excerpt.txt` (hash-gated authentic corpus
  component).
- **No LLM calls.** No raw outputs, frozen inputs, prompts, evaluations, or
  aggregate JSON/MD were modified.
