# Phase 2B combined — EVIDENCE (HIGH / LOW / UNSEEN)

Layered article-ready evidence pack. Reconstruct every claim from cited regime artifacts.

**Claim classes:** Measured · Observed · Methodological interpretation · Uncertainty · Limitation.

---

## Layer A — Measured quantitative results

### A1. Integrity

| Regime | Planned | Collected | Primary valid paired configs | Valid pairs | Invalid |
|---|---:|---:|---:|---:|---|
| HIGH | 42 | 42 | 7 | 21 | 0 |
| LOW | 42 | 42 retained | 6 | 18 | 1 (Qwen mismatch) |
| UNSEEN | 42 | 42 | 7 | 21 | 0 |

Sources: `analysis/analysis.json`, `analysis/low/analysis.json`, `analysis/unseen/analysis.json`.

### A2. Configuration mean Δ (canonical coverage, pp)

| Configuration | HIGH Δ | LOW Δ | UNSEEN Δ |
|---|---:|---:|---:|
| Gemini ON | −0.55 | +13.23 | +5.68 |
| Gemini OFF | −1.75 | +10.40 | +6.09 |
| Claude Sonnet 5 | +14.28 | +12.11 | +6.42 |
| DeepSeek Expert ON | +9.25 | +6.19 | +3.83 |
| Qwen 3.8 Max Fast | +5.18 | INVALID | +3.52 |
| GPT-5.6 Luna | +8.62 | +5.31 | +5.52 |
| Grok 4.5 Fast | +14.49 | +3.95 | +7.12 |

Full Direct/Primed means: [`cross_regime_table.csv`](cross_regime_table.csv).

### A3. Summary means

| Summary | Value |
|---|---:|
| HIGH mean of 7 config Δ | +7.07 pp |
| LOW mean of 6 valid config Δ | +8.53 pp |
| UNSEEN mean of 7 config Δ | +5.45 pp |
| Matched-six HIGH | +7.39 pp |
| Matched-six LOW | +8.53 pp |
| Matched-six UNSEEN | +5.78 pp |

Matched six omit Qwen (LOW invalid). **Measured**, not inferential.

### A4. Replicate direction (valid cells)

- HIGH: 2/7 configs mixed-sign mean cells (Gemini ON/OFF; also Qwen mixed); 5/7 all-positive mean direction with mixed only where noted in HIGH analysis.
- LOW primary-valid: 5/6 all-positive; Grok mixed (one negative replicate).
- UNSEEN: **21/21** replicate Δ > 0.

---

## Layer B — Observed textual behavior

Condensed from regime qualitative audits (see [`QUALITATIVE_SYNTHESIS.md`](QUALITATIVE_SYNTHESIS.md)).

| Pattern | Where observed | Example class |
|---|---|---|
| Corpus-opening / winter motif near-copy | HIGH large-Δ (Claude, DeepSeek, Grok, some GPT) | Primed openings align with corpus winter/boat motifs |
| Lexical borrowing without opening copy | LOW positives; many UNSEEN | Shared ISV/corpus lexis without narrative transplant |
| Orthographic / Polish-residue reduction | All regimes, uneven by config | Spelling cleanup co-occurring with Δ |
| Proper-name / term shifts | HIGH/LOW narrative; UNSEEN technical terms | Name/term substitutions |
| Positive Δ with little obvious corpus copying | LOW Gemini (large Δ); several UNSEEN cells | Metric gain without motif transplant |
| Metric–text misalignment risk | Cross-regime | Lexical/orthographic change may move coverage without clear “quality” judgment |

---

## Layer C — Methodological interpretation

1. **Descriptive design:** n=3; report means/SD/sign consistency; no p-values.
2. **Paired within configuration:** Δ always same model config + replicate.
3. **Qwen LOW:** invalid for same-model effect; exclude from LOW means and from matched-six.
4. **Matched-six:** enables same-config cross-regime descriptive comparison; not a statistical test.
5. **Regime confounds:** overlap, length, and genre differ jointly — interpret magnitude differences as **descriptive**, not causal.
6. **Gemini protocol:** multi-message Primed is a recorded interface constraint across regimes.
7. **Stale docs:** `EXP-004_PHASE2B_CHECKPOINT.md` and `analysis/high_low/` predate or omit full UNSEEN; **combined/** is the final synthesis.

---

## Layer D — Uncertainty

- Whether corpus priming **caused** Δ (vs session/order/other factors).
- Whether HIGH Gemini negatives would replicate under different interface packaging.
- How much UNSEEN magnitude attenuation reflects length/genre vs domain.
- Whether positive Δ without copying reflects genuine ISV improvement or metric sensitivity.
- Population generalization beyond these seven vendor configurations.

---

## Layer E — Limitations

See [`analysis.md`](analysis.md) §8. Minimum set:

- n=3; descriptive only  
- Qwen LOW invalid cell  
- Gemini multi-message Primed  
- Source length/genre confounds  
- UNSEEN bibliography unknown  
- Metric may track orthography/lexis  
- No causal identification  
- Historical checkpoint can mislead if used as current state  

---

## Traceability

| Claim | Source |
|---|---|
| HIGH numbers | `analysis/analysis.json`, `analysis/EVIDENCE.md` |
| LOW numbers + Qwen | `analysis/low/analysis.json`, `analysis/low/EVIDENCE.md`, `QWEN_INCIDENT.md` |
| UNSEEN numbers | `analysis/unseen/analysis.json`, `analysis/unseen/EVIDENCE.md` |
| Combined tables | `cross_regime_table.json`, `analysis.json` |
