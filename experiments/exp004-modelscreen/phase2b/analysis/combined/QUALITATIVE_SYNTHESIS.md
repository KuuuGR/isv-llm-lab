# Phase 2B — qualitative synthesis across HIGH / LOW / UNSEEN

**Status:** descriptive qualitative synthesis (2026-09-18).  
**Not:** causal proof; not grammar adjudication; not a model ranking.

Sources (primary):

- HIGH: `analysis/QUALITATIVE_AUDIT.md` (+ `qualitative_audit.json`)
- LOW: `analysis/low/QUALITATIVE_AUDIT.md` (+ `qualitative_audit.json`)
- UNSEEN: `analysis/unseen/QUALITATIVE_AUDIT.md` (+ `qualitative_audit.json`)

Quantitative companion: [`analysis.md`](analysis.md) · [`EVIDENCE.md`](EVIDENCE.md)

For every major claim below: **Observation** cites configuration/regime/examples; **Interpretation** is labeled separately.

---

## 1. Corpus-opening / motif copying

**Observation (HIGH):** Large positive Δ cells often co-occur with primed openings that track the authentic corpus winter narrative (`Ljudi govoret, že v tamtoj denj…`). Examples:

- Claude HIGH r01–r03: corpus-opening gain; mean Δ +14.28 pp
- DeepSeek HIGH r01–r03: Kit→Velryb + corpus lexis (`pomalo`, `jedino`, `črěz`); mean Δ +9.25 pp
- Qwen HIGH r01–r02: corpus-opening adoption with positive Δ; r03 negative despite opening present

**Observation (LOW):** Primed openings remain recognizably `Podkłady` (Katarzyna/Katarina + archive). Opening Jaccard vs `tuta-historija` stays low (max ≈ 0.09). No systematic winter-opening near-copy. Gemini LOW nonetheless shows large positive mean Δ (+13.23 / +10.40 pp).

**Observation (UNSEEN):** Primed texts open with exercise/biophysics titles (`Ćvičenje` / `Vježba` / `Upražnenje` + *Biofizika … glasa*), not the winter story. Opening Jaccard vs corpus stays low for all 21 pairs.

**Interpretation:** Corpus-opening near-copy is a **HIGH-overlap narrative signature**, not a universal accompaniment of positive Δ. Positive Δ on LOW and UNSEEN frequently occurs **without** that signature.

---

## 2. Lexical borrowing

**Observation:** Across regimes, primed outputs often show corpus-register items (`črěz`, `jedino`, `govoret`, `pomalo`, `no` for *ale*) while retaining source plot/structure.

- LOW Gemini ON r01: `črěz`, `govoret` without winter-opening rewrite; Δ +15.84 pp
- UNSEEN Gemini OFF / Claude / DeepSeek: `jedino` / `črěz` with expository outline retained
- HIGH DeepSeek / Claude: denser corpus lexis alongside opening alignment

**Interpretation:** Lexical borrowing is a recurring **apparent** D→P pattern. It does not by itself prove rule learning from the corpus.

---

## 3. Orthographic normalization / Polish-residue reduction

**Observation:** Many positive-Δ pairs show Polish-letter / outside-inventory drops.

- LOW Claude r01: ortho 301→11 with Δ +13.82 pp
- UNSEEN Gemini OFF r02: Polish 99→2 with coverage↑
- HIGH Claude r01: Cyrillic soft signs cleared; ortho 365→18

**Counterexamples (dimensions diverge):**

- HIGH Gemini OFF r03: coverage↓ while ortho improves
- UNSEEN Claude r03 / GPT r03 / Grok r03: coverage↑ with ortho↑
- LOW Grok r02: ortho rises while coverage rises

**Interpretation:** Orthographic cleanup often **co-occurs** with positive coverage Δ but is neither necessary nor sufficient. Metric and ortho can disagree within a pair.

---

## 4. Proper-name and term changes

**Observation:**

- HIGH: Kit / Veloryb / Velryb / Wieloryb / Velerman title churn; Benedykt/Benedikt
- LOW: Katarina↔Katarzyna; Andrej/Andžej; podkład→pragy / podložky synonyms
- UNSEEN: title variants (`Vježa`→`Ukvěžba`; Ćvičenje / Čvičenje / Upražnenje) without changing the biophysics task

**Interpretation:** Name/title variation is common surface behavior. Do not equate a preferred name with priming success.

---

## 5. Technical-domain terminology (UNSEEN)

**Observation:** Domain continuity: `formant*` / `rezonan*` / `biofizik*` remain in both Direct and Primed (expected for voice-biophysics source). Priming does not appear to rewrite the educational outline into the winter narrative.

**Interpretation:** UNSEEN positives look more like register/lexis/ortho shifts within an expository frame than genre transplant.

---

## 6. Structural preservation

**Observation:**

- HIGH large-Δ cells: narrative structure often preserved while opening/lexis shift toward corpus register
- LOW: urban/archive plot retained under priming
- UNSEEN: sectioned educational structure retained

**Interpretation:** Across regimes, priming more often reshapes **surface register** than source **task structure** — with HIGH as the exception where opening near-copy is frequent.

---

## 7. Positive Δ with little obvious corpus copying

**Observation (concrete cases):**

| Case | Δ | Note |
|---|---:|---|
| LOW Gemini ON (cell mean) | +13.23 | Large gain; openings stay Podkłady; no winter near-copy |
| LOW Gemini OFF (cell mean) | +10.40 | Same pattern |
| UNSEEN Gemini ON r03 | +8.84 | Metric↑ with little obvious `jedino`/`črěz` echo |
| UNSEEN Qwen r02 | +1.27 | Markers present but small Δ (inverse case) |

**Interpretation:** Large positive Δ is **compatible with** little motif copying. Conversely, markers/opening copy do not guarantee large Δ (HIGH Qwen r03: opening present, Δ −1.23).

---

## 8. Metric–text misalignment

**Observation:** Cases where coverage moves one way and human-readable quality signals another:

- Ortho worsens while Δ positive (HIGH Claude r03; UNSEEN GPT r03 markdown-bold title)
- Ortho improves while Δ negative (HIGH Gemini OFF r03)
- LOW Grok r03: small negative Δ with light winter-motif bleed signal

**Interpretation:** Canonical coverage is a **useful screening metric**, not a complete communicative-quality judgment. Article claims should keep metric and qualitative layers separate.

---

## 9. Qwen LOW vs UNSEEN (execution vs language)

**Observation:** LOW Qwen Primed used a different model identity (`Qwen3.7-Plus`) → invalid for priming inference. UNSEEN Qwen remains same-model valid; primed outputs stay Interslavic biophysics prose with low Polish-letter counts; mean Δ +3.52 pp (all+).

**Interpretation:** The LOW incident is primarily an **execution / model-identity** failure mode for that cell, not evidence about Qwen 3.8 Max priming on LOW. UNSEEN does not “fix” LOW Qwen; it only shows a later valid Qwen cell elsewhere.

---

## 10. Cross-regime qualitative summary

| Theme | HIGH | LOW | UNSEEN |
|---|---|---|---|
| Winter-opening near-copy | Common in large+ cells | Rare / absent | Absent |
| Lexical borrowing | Strong with opening | Present without opening | Present within exposition |
| Ortho / Polish cleanup | Frequent, uneven | Frequent, uneven | Frequent, uneven |
| Positive Δ without copying | Less typical for largest gains | Common (esp. Gemini) | Common |
| Genre | Narrative fiction | Narrative fiction | Expository technical |

Do **not** over-generalize from one model or one repeat. Heterogeneity across configurations remains first-order.
