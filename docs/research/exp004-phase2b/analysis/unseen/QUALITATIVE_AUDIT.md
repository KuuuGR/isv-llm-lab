# Phase 2B UNSEEN — qualitative paired Direct → Primed audit

**Status:** descriptive qualitative audit of existing evidence (2026-09-18).  
**Not:** a new experiment, causal claim, grammar adjudication, or
HIGH/LOW/UNSEEN synthesis.

Machine-readable pair ledger: [`qualitative_audit.json`](qualitative_audit.json)  
Quantitative source of truth: [`dataset.json`](dataset.json)  
Article-ready quantitative record: [`EVIDENCE.md`](EVIDENCE.md)

> All **21** Direct↔Primed pairs were inspected (7 configurations × r01–r03).  
> Classifications are **apparent** judgments — not proof of linguistic
> correctness.

---

## D. Limitations (read first)

1. This audit is **descriptive**.
2. No causal inference from D→P differences alone.
3. Coverage gains may partly reflect evaluator lexicon hits.
4. UNSEEN source is **short** and **expository** (voice biophysics) —
   openings are section titles, not narrative hooks; corpus-opening
   near-copy of the winter story is a poor expected signature here.
5. **n = 3** per configuration.
6. Do not treat a higher score as broader language improvement.

---

## A. Pair-level audit table (all 21)

Canonical values from `dataset.json`. Δ = P − D (percentage points).

### Gemini 3.6 Flash — extended thinking ON (mean Δ +5.68 pp; all positive)

| rep | D% | P% | Δ pp | ortho D→P | concise differences | classes |
|---|---:|---:|---:|---|---|---|
| r01 | 66.77 | 68.89 | +2.12 | 16→19 | Mildest ON gain; Polish letters drop sharply; `črěz` appears in P; title stays exercise/biophysics | improvement / lexical borrowing / ortho cleanup |
| r02 | 64.87 | 70.95 | +6.08 | 32→29 | Larger gain; `jedino` in P; expository structure retained | improvement / lexical borrowing |
| r03 | 65.68 | 74.53 | +8.84 | 24→18 | Strongest ON replicate; little obvious corpus-marker echo | improvement / ortho cleanup |

### Gemini 3.6 Flash — extended thinking OFF (mean Δ +6.09 pp; all positive)

| rep | D% | P% | Δ pp | ortho D→P | concise differences | classes |
|---|---:|---:|---:|---|---|---|
| r01 | 62.30 | 70.27 | +7.97 | 17→14 | Large Polish-letter drop; `jedino`/`črěz` in P | improvement / lexical borrowing / ortho cleanup |
| r02 | 64.84 | 68.80 | +3.96 | 47→26 | Polish 99→2; coverage↑ with ortho cleanup | improvement / lexical borrowing / ortho cleanup |
| r03 | 64.42 | 70.78 | +6.35 | 29→16 | Same direction | improvement / lexical borrowing / ortho cleanup |

### Claude Sonnet 5 Medium (mean Δ +6.42 pp; all positive)

| rep | D% | P% | Δ pp | ortho D→P | concise differences | classes |
|---|---:|---:|---:|---|---|---|
| r01 | 66.22 | 73.36 | +7.14 | 26→21 | Title *Vježa*→*Ukvěžba*; body remains biophysics; `črěz` in P | improvement / lexical borrowing |
| r02 | 65.86 | 71.00 | +5.14 | 25→10 | Ortho cleanup; `jedino`/`črěz` | improvement / lexical borrowing / ortho cleanup |
| r03 | 66.12 | 73.08 | +6.96 | 21→27 | Coverage↑ while ortho rises slightly — dimensions diverge | improvement / lexical borrowing / ambiguous |

### DeepSeek V3 Expert ON (mean Δ +3.83 pp; all positive)

| rep | D% | P% | Δ pp | ortho D→P | concise differences | classes |
|---|---:|---:|---:|---|---|---|
| r01 | 68.90 | 71.81 | +2.91 | 15→14 | Mild gain; already low Polish load | improvement |
| r02 | 68.44 | 73.43 | +5.00 | 14→15 | Strongest DeepSeek UNSEEN Δ; `jedino`/`črěz` | improvement / lexical borrowing |
| r03 | 66.57 | 70.15 | +3.58 | 22→14 | Moderate | improvement / lexical borrowing |

### Qwen 3.8 Max Fast (mean Δ +3.52 pp; all positive)

| rep | D% | P% | Δ pp | ortho D→P | concise differences | classes |
|---|---:|---:|---:|---|---|---|
| r01 | 67.86 | 71.54 | +3.67 | 22→20 | Stable Interslavic; **no** LOW-style Polish collapse | improvement |
| r02 | 68.22 | 69.48 | +1.27 | 22→23 | Smallest cell Δ; markers present without large metric move | improvement / lexical borrowing |
| r03 | 66.87 | 72.49 | +5.62 | 21→20 | Largest Qwen UNSEEN Δ | improvement / lexical borrowing |

### GPT-5.6 Luna (mean Δ +5.52 pp; all positive)

| rep | D% | P% | Δ pp | ortho D→P | concise differences | classes |
|---|---:|---:|---:|---|---|---|
| r01 | 69.08 | 75.64 | +6.56 | 30→16 | Polish↓; markers present | improvement / lexical borrowing / ortho cleanup |
| r02 | 65.45 | 73.03 | +7.58 | 14→16 | Strong gain | improvement / lexical borrowing |
| r03 | 71.06 | 73.49 | +2.43 | 40→53 | Title wrapped in markdown bold; ortho worsens while Δ still + | improvement / ambiguous / neutral variation |

### Grok 4.5 Fast (mean Δ +7.12 pp; all positive)

| rep | D% | P% | Δ pp | ortho D→P | concise differences | classes |
|---|---:|---:|---:|---|---|---|
| r01 | 67.53 | 73.55 | +6.02 | 16→18 | Lexical borrowing without opening rewrite | improvement / lexical borrowing |
| r02 | 64.78 | 74.40 | +9.62 | 13→14 | Largest UNSEEN replicate Δ; openings both *Vježba 2.2* / Biofizika | improvement / lexical borrowing |
| r03 | 65.40 | 71.10 | +5.70 | 16→26 | Coverage↑, ortho↑ | improvement / lexical borrowing / ambiguous |

---

## B. Recurring D→P patterns (observations)

1. **No corpus winter-opening near-copy.** Primed texts open with exercise /
   biophysics titles (`Ćvičenje` / `Vježba` / `Upražnenje` + *Biofizika
   … glasa*), not `Ljudi govoret, že v tamtoj denj…`. Opening Jaccard vs
   `tuta-historija` stays low for all pairs.
2. **Lexical borrowing without opening rewrite.** Many primed outputs
   contain corpus-register items such as `črěz` and `jedino` while keeping
   the educational outline (formants, resonance, larynx, turbulence).
3. **Domain continuity.** `formant*` / `rezonan*` / `biofizik*` remain in
   both Direct and Primed (expected for this source).
4. **Polish-residue / ortho cleanup** often co-occurs with positive Δ
   (especially Gemini OFF, Claude, GPT r01), but not always (Claude r03,
   GPT r03, Grok r03: coverage↑ with ortho↑).
5. **Title variation** across repeats (Ćvičenje / Čvičenje / Vježba /
   Upražnenje / Ukvěžba) without changing the expository task.

### Counterexamples / notable cases

- **Δ↑ with little corpus-marker echo:** Gemini ON r03 (+8.84 pp) —
  metric improvement without obvious `jedino`/`črěz` adoption.
- **Markers present, small Δ:** Qwen r02 (+1.27 pp) — lexical echo without
  large coverage move.
- **Markdown pollution:** GPT primed r03 title `**## Vježba 2.2**` —
  surface formatting artifact; run still complete/usable.
- **LOW Qwen incident not replicated:** UNSEEN Qwen primed remains
  Interslavic biophysics prose (Polish-letter counts stay low).

---

## C. Relationship to canonical Δ (descriptive)

| Pattern | Configurations | Qualitative character |
|---|---|---|
| All-positive moderate Δ | All 7 | Expository structure retained; occasional corpus lexis; no winter-opening rewrite |
| Largest mean Δ | Grok (~+7.1 pp) | Lexical borrowing + local ISV shifts |
| Smallest mean Δ | Qwen (~+3.5 pp) | Same direction; milder magnitude; **valid** pairing |

Uniform positive Δ on a short educational source is **compatible with**
priming helping resource-supported coverage without narrative motif
copy — but this remains an association, not a causal claim.

---

## E. UNSEEN-specific methodological note

UNSEEN differs from HIGH/LOW by length and genre. That difference is a
**design characteristic / possible confound** for cross-regime magnitude
comparisons. This audit does not rescale or “correct” Δ for source length.

---

## Provenance / immutability

- Inspected existing `phase2b/outputs/<run_id>/output.txt` only.
- Metrics from `analysis/unseen/dataset.json`.
- Corpus parallels checked against `phase2a/corpus/tuta-historija-excerpt.txt`.
- **No LLM calls.** No raw outputs, frozen inputs, HIGH, or LOW artifacts
  modified.
