# Phase 2B — final cross-regime synthesis (HIGH / LOW / UNSEEN)

**Status:** final **descriptive** evidence synthesis (2026-09-18)  
**Not:** manuscript Abstract/Introduction/Discussion/Conclusion; not a significance test; not a causal claim; not a model ranking.

**Metric:** canonical coverage.  
**Effect:** `Δᵢ = Primedᵢ − Directᵢ` (same configuration + replicate).  
**Configuration mean Δ:** mean of three replicate Δᵢ (n = 3; descriptive only).

Machine-readable: [`analysis.json`](analysis.json) · [`cross_regime_table.json`](cross_regime_table.json) · [`cross_regime_table.csv`](cross_regime_table.csv)  
Article-ready layered record: [`EVIDENCE.md`](EVIDENCE.md)  
Qualitative synthesis: [`QUALITATIVE_SYNTHESIS.md`](QUALITATIVE_SYNTHESIS.md)

> Reconstruct every figure from the cited HIGH / LOW / UNSEEN analysis artifacts.  
> This file is a synthesis layer, not an independent measurement source.

---

## 0. Authoritative state vs stale records

| Record | Role |
|---|---|
| `analysis/analysis.json` (+ `EVIDENCE.md`, `QUALITATIVE_AUDIT.md`) | **HIGH** authoritative |
| `analysis/low/analysis.json` (+ LOW EVIDENCE / qualitative / Qwen incident) | **LOW** authoritative |
| `analysis/unseen/analysis.json` (+ UNSEEN EVIDENCE / qualitative) | **UNSEEN** authoritative |
| **This directory (`analysis/combined/`)** | **Final three-regime synthesis** |
| `analysis/high_low/` | Historical **HIGH↔LOW-only** exploratory synthesis (2026-09-16). Keep; do not treat as final Phase 2B state |
| `EXP-004_PHASE2B_CHECKPOINT.md` | Historical checkpoint **after HIGH+LOW, before UNSEEN**. Stale for current UNSEEN-complete status |

Canonical experiment root: `experiments/exp004-modelscreen/phase2b/`.

---

## 1. Regime verification (facts)

| Regime | Planned | Collected / evaluated | Primary valid paired configs | Valid pairs | Invalid paired cells |
|---|---:|---:|---:|---:|---|
| **HIGH** | 42 | 42 / 42 | **7** | 21 | 0 |
| **LOW** | 42 | 42 / 42 retained | **6** | 18 | **1** (Qwen `INVALID — MODEL MISMATCH`) |
| **UNSEEN** | 42 | 42 / 42 | **7** | 21 | 0 |

Integrity gates PASS on all three datasets (`exactly_42_evaluated`, 7 configs, unique run IDs, complete D↔P pairing structure).

### Qwen LOW (preserved exactly)

- Intended: Qwen 3.8 Max — Fast Direct **and** Primed  
- Actual: Direct = Qwen 3.8 Max — Fast; Primed = **Qwen3.7-Plus**  
- Status: **INVALID — MODEL MISMATCH**  
- Priming effect for Qwen 3.8 Max on LOW: **not estimated**  
- Do **not** cite historical **−12.08 pp** as a Qwen 3.8 Max LOW priming effect  
- Record: `analysis/low/QWEN_INCIDENT.md`, `analysis/low/invalid_cells.json`

### Gemini protocol (all regimes)

Primed Gemini used the established **multi-message** corpus delivery (msg1 corpus / msg2 translation). Corpus bytes were **not** shortened. This is a recorded interface/context-window constraint, not a redesign.

---

## 2. Canonical cross-regime table (canonical coverage)

Means are percentages; Δ in percentage points (pp). LOW Qwen paired Δ = **N/A (invalid)**.

| Configuration | HIGH D | HIGH P | HIGH Δ | LOW D | LOW P | LOW Δ | UNSEEN D | UNSEEN P | UNSEEN Δ | Validity H/L/U |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Gemini 3.6 Flash — ext. thinking ON | 68.68 | 68.13 | **−0.55** | 64.33 | 77.56 | **+13.23** | 65.77 | 71.45 | **+5.68** | valid / valid / valid |
| Gemini 3.6 Flash — ext. thinking OFF | 67.20 | 65.45 | **−1.75** | 64.51 | 74.92 | **+10.40** | 63.85 | 69.95 | **+6.09** | valid / valid / valid |
| Claude Sonnet 5 — Medium | 69.29 | 83.57 | **+14.28** | 65.72 | 77.83 | **+12.11** | 66.07 | 72.48 | **+6.42** | valid / valid / valid |
| DeepSeek V3 Expert — DeepThink ON | 74.53 | 83.78 | **+9.25** | 68.93 | 75.12 | **+6.19** | 67.97 | 71.80 | **+3.83** | valid / valid / valid |
| Qwen 3.8 Max — Fast | 76.36 | 81.54 | **+5.18** | N/A | N/A | **INVALID** | 67.65 | 71.17 | **+3.52** | valid / **invalid** / valid |
| GPT-5.6 Luna — thinking OFF | 73.54 | 82.16 | **+8.62** | 70.75 | 76.06 | **+5.31** | 68.53 | 74.05 | **+5.52** | valid / valid / valid |
| Grok 4.5 Fast | 68.35 | 82.84 | **+14.49** | 69.32 | 73.27 | **+3.95** | 65.90 | 73.02 | **+7.12** | valid / valid / valid |

### Compact central table

| Configuration | HIGH Δ | LOW Δ | UNSEEN Δ |
|---|---:|---:|---:|
| Gemini ON | −0.55 | +13.23 | +5.68 |
| Gemini OFF | −1.75 | +10.40 | +6.09 |
| Claude Sonnet 5 | +14.28 | +12.11 | +6.42 |
| DeepSeek Expert ON | +9.25 | +6.19 | +3.83 |
| Qwen 3.8 Max Fast | +5.18 | **INVALID** | +3.52 |
| GPT-5.6 Luna | +8.62 | +5.31 | +5.52 |
| Grok 4.5 Fast | +14.49 | +3.95 | +7.12 |

---

## 3. All-configuration vs matched-six summaries

### All-configuration (not perfectly matched)

| Regime | n configs in mean | Mean of config mean-Δ | Positive / negative mean-Δ configs |
|---|---:|---:|---|
| HIGH | 7 | **+7.07 pp** | 5 / 2 |
| LOW | 6 | **+8.53 pp** | 6 / 0 |
| UNSEEN | 7 | **+5.45 pp** | 7 / 0 |

These means **must not** be read as a single matched three-regime average (LOW omits Qwen).

### Matched six (identical configs in HIGH, LOW, UNSEEN)

**Excluded:** Qwen 3.8 Max — Fast (LOW invalid pairing).  
**Included:** Gemini ON, Gemini OFF, Claude Sonnet 5, DeepSeek Expert ON, GPT-5.6 Luna, Grok 4.5 Fast.

| Regime | Matched-six mean Δ |
|---|---:|
| HIGH | **+7.39 pp** |
| LOW | **+8.53 pp** |
| UNSEEN | **+5.78 pp** |

Descriptive only. Not a statistical test. Not a causal attribution to overlap, length, or genre.

---

## 4. Replicate consistency

| Configuration | HIGH direction | LOW direction | UNSEEN direction |
|---|---|---|---|
| Gemini ON | mixed | all positive | all positive |
| Gemini OFF | mixed | all positive | all positive |
| Claude Sonnet 5 | all positive | all positive | all positive |
| DeepSeek Expert ON | all positive | all positive | all positive |
| Qwen 3.8 Max Fast | mixed | **invalid** | all positive |
| GPT-5.6 Luna | all positive | all positive | all positive |
| Grok 4.5 Fast | all positive | mixed | all positive |

**UNSEEN:** all **21** replicate Δs are positive (verified in UNSEEN distribution notes / EVIDENCE).

**Particularly variable (HIGH):** Grok SD(Δ) ≈ 5.90 pp; Qwen SD(Δ) ≈ 5.56 pp.  
**Particularly stable (examples):** GPT HIGH SD(Δ) ≈ 1.34 pp; Claude UNSEEN SD(Δ) ≈ 1.11 pp; DeepSeek UNSEEN SD(Δ) ≈ 1.06 pp.

---

## 5. Configuration-specific patterns (descriptive)

| Configuration | Pattern across HIGH → LOW → UNSEEN |
|---|---|
| **Gemini ON/OFF** | HIGH near-zero / **negative** mean Δ with **mixed** replicates → LOW **strongly positive** (all+) → UNSEEN **moderately positive** (all+). Clear **direction reversal** HIGH→LOW; UNSEEN stays positive. |
| **Claude** | Persistently positive mean Δ in all three regimes; HIGH/LOW large (~+12–14 pp), UNSEEN smaller (~+6.4 pp). |
| **DeepSeek** | Persistently positive; magnitude **attenuates** HIGH→LOW→UNSEEN (+9.25 → +6.19 → +3.83). |
| **Qwen** | HIGH mixed but positive mean; LOW **invalid**; UNSEEN all-positive moderate (+3.52). No valid three-regime Qwen series. |
| **GPT-5.6 Luna** | Persistently positive; similar moderate magnitude on LOW and UNSEEN (~+5.3–5.5); HIGH larger (+8.62). |
| **Grok** | HIGH large positive (all+); LOW much smaller mean with **one negative replicate**; UNSEEN moderate–strong positive (all+). **Magnitude instability** HIGH→LOW without mean-sign reversal. |

Heterogeneity across configurations is a primary observation. Do not collapse to a single “priming always helps / hurts” claim.

---

## 6. Source-regime comparison (design + observed Δ)

| Axis | HIGH | LOW | UNSEEN |
|---|---|---|---|
| Domain | Fantasy / maritime narrative | Contemporary municipal / archive narrative | Voice biophysics / speech acoustics |
| Genre | Narrative fiction | Narrative fiction | Expository educational theory |
| Length (bytes) | ~30 061 | ~15 249 | ~5 676 |
| Corpus overlap (design) | Intentionally high | Intentionally low | Domain unseen vs corpus registers |
| Primary valid mean Δ (unmatched) | +7.07 (n=7) | +8.53 (n=6) | +5.45 (n=7) |
| Matched-six mean Δ | +7.39 | +8.53 | +5.78 |

**Confounds (disclose, do not causalize):** length, genre (narrative vs expository), and overlap are **jointly** different across regimes. Overlap alone does **not** explain Gemini’s HIGH→LOW reversal (LOW is lower-overlap yet strongly positive for Gemini). Length/genre may affect magnitude comparability, especially UNSEEN vs HIGH/LOW.

---

## 7. Main findings (evidence-backed)

1. **Priming and the metric:** Primed − Direct is **not uniformly signed** across configurations on HIGH (2/7 negative mean Δ). On LOW primary-valid cells and on UNSEEN, mean Δ is positive for every valid configuration; UNSEEN also has all 21 replicate Δs positive.
2. **Configuration heterogeneity:** Direction and magnitude vary strongly by configuration (Gemini reversals; Claude/DeepSeek/GPT persistent positives; Grok magnitude drop on LOW).
3. **Regime differences:** HIGH shows both large positives and Gemini negatives; LOW (valid) is broadly positive with Gemini amplification; UNSEEN is uniformly positive at moderate magnitudes.
4. **Large overlap is not necessary for positive Δ:** LOW (low-overlap narrative) and UNSEEN (unseen-domain exposition) both show many positive paired Δs; Gemini’s largest positives appear on LOW, not HIGH.
5. **Corpus-like copying is not required for every positive Δ:** HIGH large positives often co-occur with corpus-opening / motif alignment; LOW/UNSEEN positives frequently show lexical borrowing / orthographic cleanup **without** winter-narrative opening near-copy (see qualitative synthesis).
6. **Qwen LOW incident:** Invalidates same-model LOW priming inference for that cell; demonstrates execution/identity risk; UNSEEN Qwen remained valid and positive (all+).
7. **What UNSEEN adds:** Shows positive paired Δ on a short technical/educational domain absent from the priming corpus, with uniform replicate positivity and **no** invalid pairing cells — extending beyond narrative HIGH/LOW.
8. **Robustly supported:** descriptive tables above; integrity counts; Qwen invalidation; UNSEEN all-positive replicate direction; matched-six construction excluding Qwen.
9. **Uncertain / not established:** causality of corpus priming; statistical significance; that overlap, length, or genre “caused” magnitude differences; model ranking; whether metric gains equal communicative quality.

---

## 8. Limitations

- n = 3 repeats per configuration (descriptive only).
- No inferential / significance testing by design.
- One invalid Qwen LOW paired cell (model mismatch).
- Gemini multi-message Primed protocol (context-window / interface constraint).
- Source length and genre differ across regimes (confound for magnitude comparison).
- UNSEEN provenance: operator-supplied teaching-derived text; exact bibliography unknown.
- Canonical coverage may be sensitive to orthographic/lexical changes that are not full “quality” gains.
- Design cannot isolate causal contribution of corpus priming vs other session factors.
- Historical checkpoint / HIGH↔LOW-only synthesis can confuse readers if mistaken for final three-regime state.

---

## 9. Provenance / immutability

- No LLM sessions during this synthesis.
- No modification of raw outputs, frozen sources, or the authentic corpus.
- Numbers traced to HIGH/LOW/UNSEEN `analysis.json` / EVIDENCE tables (see `analysis.json` in this directory).
