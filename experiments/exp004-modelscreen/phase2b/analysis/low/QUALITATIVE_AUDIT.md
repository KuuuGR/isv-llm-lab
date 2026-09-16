# Phase 2B LOW — qualitative paired Direct → Primed audit

**Status:** descriptive qualitative audit of existing evidence (2026-09-16).  
**Not:** a new experiment, causal claim, grammar adjudication, or replacement for the quantitative aggregate.

Machine-readable pair ledger: [`qualitative_audit.json`](qualitative_audit.json)  
Quantitative source of truth: [`dataset.json`](dataset.json)  
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
4. LOW deliberately has **low thematic overlap** with the priming corpus
   (`Podkłady` urban/archive plot). Unlike HIGH, primed openings here do
   **not** systematically near-copy the corpus winter narrative
   (`Ljudi govoret, že v tamtoj denj…`).
5. **n = 3** per configuration limits generalization.
6. Orthography outside-inventory and coverage can **move in opposite
   directions** within the same pair (extreme: Qwen r03).

---

## A. Pair-level audit table (all 21)

Canonical values from `dataset.json`. Δ = P − D (percentage points).
Opening Jaccard is vs the authentic corpus narrative excerpt
(`tuta-historija-excerpt.txt`) — a HIGH-style corpus-opening detector.

### Gemini 3.6 Flash — extended thinking ON (mean Δ +13.23 pp; all positive)

| rep | D% | P% | Δ pp | ortho D→P | concise differences | classes |
|---|---:|---:|---:|---|---|---|
| r01 | 62.35 | 78.19 | +15.84 | 61→12 | Podkłady opening retained; Polish-char / ortho drop; corpus lexis (črěz, govoret) without winter-opening rewrite | improvement / lexical borrowing |
| r02 | 65.86 | 77.23 | +11.37 | 42→41 | Same pattern: urban plot kept; coverage↑ without corpus-opening adoption | improvement / lexical borrowing |
| r03 | 64.79 | 77.26 | +12.48 | 25→37 | Positive Δ; local lexical/ortho churn; opening Jaccard vs corpus stays low | improvement / lexical borrowing |

### Gemini 3.6 Flash — extended thinking OFF (mean Δ +10.40 pp; all positive)

| rep | D% | P% | Δ pp | ortho D→P | concise differences | classes |
|---|---:|---:|---:|---|---|---|
| r01 | 63.55 | 77.29 | +13.74 | 38→18 | Title-like “Zemja pametaje” in primed; still Podkłady body; no `v tamtoj denj` rewrite | improvement / lexical borrowing |
| r02 | 62.69 | 74.25 | +11.55 | 55→28 | Coverage↑; Polish residue↓; corpus markers without opening copy | improvement / lexical borrowing |
| r03 | 67.30 | 73.21 | +5.91 | 36→43 | Mildest OFF gain; dimensions partly diverge | improvement / lexical borrowing |

### Claude Sonnet 5 Medium (mean Δ +12.11 pp; all positive)

| rep | D% | P% | Δ pp | ortho D→P | concise differences | classes |
|---|---:|---:|---:|---|---|---|
| r01 | 64.18 | 78.00 | +13.82 | 301→11 | Large ortho cleanup; Katarina→Katarzyna; corpus lexis↑; plot remains archive/podkłady | improvement / lexical borrowing |
| r02 | 66.34 | 75.58 | +9.24 | 142→10 | Same direction; milder Δ | improvement / lexical borrowing |
| r03 | 66.65 | 79.92 | +13.27 | 104→18 | Katarina naming retained; Andžej; positive Δ without corpus-opening near-copy | improvement / lexical borrowing |

### DeepSeek V3 Expert ON (mean Δ +6.19 pp; all positive)

| rep | D% | P% | Δ pp | ortho D→P | concise differences | classes |
|---|---:|---:|---:|---|---|---|
| r01 | 69.25 | 74.67 | +5.43 | 18→14 | Moderate gain; lexical borrowing; Podkłady structure kept | improvement / lexical borrowing |
| r02 | 67.80 | 75.72 | +7.92 | 16→15 | Strongest DeepSeek LOW Δ | improvement / lexical borrowing |
| r03 | 69.75 | 74.97 | +5.22 | 12→9 | Consistent mild positive | improvement / lexical borrowing |

### Qwen 3.8 Max Fast (mean Δ −12.08 pp; all negative)

| rep | D% | P% | Δ pp | ortho D→P | concise differences | classes |
|---|---:|---:|---:|---|---|---|
| r01 | 72.48 | 66.70 | −5.78 | 32→28 | Negative Δ despite some corpus markers; opening stays Podkłady | degradation / ambiguous |
| r02 | 71.96 | 68.27 | −3.68 | 30→25 | Milder negative; same qualitative character | degradation / ambiguous |
| r03 | 72.11 | 45.34 | −26.77 | 18→1066 | **Polish collapse:** primed largely restores Polish source prose (`się`, `który`, …); extreme outside-inventory | degradation / Polish collapse |

### GPT-5.6 Luna (mean Δ +5.31 pp; all positive)

| rep | D% | P% | Δ pp | ortho D→P | concise differences | classes |
|---|---:|---:|---:|---|---|---|
| r01 | 70.12 | 74.97 | +4.85 | 14→12 | Katarina/Andrej naming; podkład→pragy synonym; mild positive | improvement / neutral |
| r02 | 71.04 | 77.41 | +6.37 | 10→14 | Strongest Luna LOW Δ; still no corpus-opening rewrite | improvement / lexical borrowing |
| r03 | 71.08 | 75.81 | +4.73 | 11→19 | Katarina; podložky synonym; mild positive | improvement / neutral |

### Grok 4.5 Fast (mean Δ +3.95 pp; mixed signs)

| rep | D% | P% | Δ pp | ortho D→P | concise differences | classes |
|---|---:|---:|---:|---|---|---|
| r01 | 69.34 | 77.55 | +8.21 | 22→28 | Positive; Podkłady retained | improvement / lexical borrowing |
| r02 | 69.26 | 74.39 | +5.13 | 25→41 | Positive; ortho rises while coverage rises | improvement / ambiguous |
| r03 | 69.36 | 67.86 | −1.50 | 26→145 | Small negative; light winter-motif bleed signal without opening rewrite | ambiguous / degradation |

---

## B. Recurring D→P patterns (observations)

1. **No systematic corpus-opening near-copy.** Primed openings remain
   recognizably `Podkłady` (Katarzyna/Katarina + archive). Opening Jaccard
   vs `tuta-historija` stays low (max ≈ 0.09 across all primed runs).
2. **Lexical borrowing without opening rewrite.** Primed texts more often
   contain corpus-register items such as `črěz`, `govoret`, `tutčas`,
   `jedino` while keeping the urban plot.
3. **Orthographic / Polish-residue cleanup** often co-occurs with positive Δ
   (especially Claude, Gemini), but is not universal (Grok r02/r03 ortho↑).
4. **Name/title variation:** Katarzyna↔Katarina, Andrzej↔Andžej/Andrej;
   occasional title lines (`Katarzyna`, `Zemja pametaje`, `Katarzyna Pametaje Zemja`).
5. **Structural continuity:** archive / Fabryczna / podkłady plot usually
   preserved (≠ HIGH’s frequent winter-narrative opening swap).

### Counterexamples

- **Δ↑ with little obvious corpus influence:** Gemini positives with low
  opening Jaccard — improvement may be local ISV/ortho cleanup rather than
  motif copy.
- **Δ↓ despite visible corpus markers:** Qwen r01/r02 show some
  `govoret`/`črěz`/`jedino` yet negative canonical Δ.
- **Δ↓ with catastrophic Polish reversion:** Qwen r03 — primed ≈ Polish
  source; coverage and orthography both collapse.

---

## C. Relationship to canonical Δ (descriptive)

| Pattern | Configurations | Qualitative character |
|---|---|---|
| Consistently large positive Δ | Gemini ON/OFF, Claude | Lexical borrowing + ortho cleanup; **no** corpus-opening near-copy |
| Consistently moderate positive Δ | DeepSeek, GPT-5.6 Luna | Same direction; milder magnitude |
| Positive mean, one negative replicate | Grok | r03 small negative; no opening rewrite |
| Consistently negative Δ | Qwen | Interference / Polish collapse (r03 extreme) |

This is **compatible with** (not proof of) the hypothesis that large HIGH
positive Δs partly reflected overlap with corpus-like openings/motifs:
LOW can still show positive Δ, but without that opening-copy signature —
and some HIGH-strong configs (Grok) show smaller / mixed LOW Δ.

---

## HIGH vs LOW qualitative contrast (descriptive)

| Observation | HIGH | LOW |
|---|---|---|
| Primed opening ≈ corpus winter narrative | Frequent in large+ configs | Not observed |
| Gemini priming direction | Mixed / mean≈0 or negative | Strongly positive, all+ |
| Qwen priming direction | Mostly positive (1 negative rep) | All negative |
| Polish collapse under priming | Rare | Qwen r03 extreme case |

---

## Provenance / immutability

- Inspected existing `phase2b/outputs/<run_id>/output.txt` only.
- Metrics taken from `analysis/low/dataset.json` (already evaluated).
- Corpus parallels checked against local
  `phase2a/corpus/tuta-historija-excerpt.txt` (hash-gated authentic corpus
  component).
- **No LLM calls.** No raw outputs, frozen inputs, prompts, evaluations, or
  HIGH aggregate artifacts were modified.
