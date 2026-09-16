# EXP-004 Phase 2B — Checkpoint

**Document type:** authoritative project checkpoint  
**Scope:** state **after** HIGH and LOW completion, **before** UNSEEN  
**Date:** 2026-09-16  
**Nature:** documentation only — no new LLM sessions, translations, evaluations, or kit preparation  
**Sources of truth:** frozen Phase 2B plans, intake/aggregate artifacts, qualitative audits, Qwen incident ledger, HIGH↔LOW synthesis (paths below)

> Reconstruct every figure from the cited artifacts. Do not treat this file as an independent data source if aggregates are regenerated.

---

## 1. Experimental state

| Item | Status |
|---|---|
| Experiment | **EXP-004 Phase 2B** (source-regime corpus-priming tests) |
| **HIGH-overlap** | **complete** (collected, verified, evaluated, aggregated, qualitative audit) |
| **LOW-overlap** | **complete** with one invalid configuration cell retained and excluded from primary priming analysis |
| **UNSEEN DOMAIN** | **not frozen / not prepared / not executed** |

Regime root: `experiments/exp004-modelscreen/phase2b/`

---

## 2. HIGH

| Field | Value (from artifacts) |
|---|---|
| Story | **`Iskra i Wieloryb — wersja z oryginalnymi nazwami`** v1 |
| Classification | `high_overlap_corpus_inspired` |
| Story SHA-256 | `ab8a0dcf7352789c09c4aca132c086999c861407e4cd682ee9414aab5b792f63` |
| Design | 7 configurations × Direct/Primed × 3 replicates (r01–r03) |
| Observations | **42** planned / collected / verified / evaluated / usable |
| Aggregate analysis | complete — `phase2b/analysis/` (`dataset.json`, `analysis.json`, `analysis.md`) |
| Qualitative audit | complete — `phase2b/QUALITATIVE_AUDIT.md` + `phase2b/qualitative_audit.json` |
| Article-ready evidence | `phase2b/EVIDENCE.md` |
| Integrity | PASS (`exactly_42_evaluated`, 7 configs, unique run IDs, complete D↔P pairing) |

**Canonical mean Δ (n=3 per cell; descriptive; all 7 configurations):**

| Configuration | Mean Δ |
|---|---:|
| Gemini 3.6 Flash — extended thinking ON | −0.55 pp |
| Gemini 3.6 Flash — extended thinking OFF | −1.75 pp |
| Claude Sonnet 5 — Medium (default) | +14.28 pp |
| DeepSeek V3 Expert — DeepThink ON | +9.25 pp |
| Qwen 3.8 Max — Fast | +5.18 pp |
| GPT-5.6 Luna — thinking OFF | +8.62 pp |
| Grok 4.5 Fast | +14.49 pp |

Descriptive mean of the seven configuration mean-Δ values: **+7.07 pp**  
Source: `phase2b/analysis/analysis.json`.

---

## 3. LOW

| Field | Value (from artifacts) |
|---|---|
| Story | **`Podkłady`** v1 (clean prose; casting/API preamble excluded) |
| Classification | `low_overlap` |
| Story SHA-256 | `ce1c4fca03fe9cb2c5f8181ab45c91767759a0c785f0a066543d95bc32f5271b` |
| Design (planned) | 7 configurations × Direct/Primed × 3 replicates |
| Runs retained | **42/42** |
| Primary paired analysis | **6 valid** same-model configuration cells |
| Invalid configuration cells | **1** — Qwen (`INVALID — MODEL MISMATCH`) |
| Valid observations | **36** (18 Direct + 18 Primed) |
| Valid Direct↔Primed pairs | **18** |
| Aggregate analysis | complete — `phase2b/analysis/low/` |
| Qualitative audit | complete for **18 valid pairs** — `phase2b/analysis/low/QUALITATIVE_AUDIT.md` |
| Article-ready evidence | `phase2b/analysis/low/EVIDENCE.md` |

**Canonical mean Δ — primary valid configurations only (n=3 per cell; descriptive):**

| Configuration | Mean Δ |
|---|---:|
| Gemini 3.6 Flash — extended thinking ON | +13.23 pp |
| Gemini 3.6 Flash — extended thinking OFF | +10.40 pp |
| Claude Sonnet 5 — Medium (default) | +12.11 pp |
| DeepSeek V3 Expert — DeepThink ON | +6.19 pp |
| GPT-5.6 Luna — thinking OFF | +5.31 pp |
| Grok 4.5 Fast | +3.95 pp |

Descriptive mean of the **six valid** configuration mean-Δ values: **+8.53 pp** (`n=6 configurations`)  
Source: `phase2b/analysis/low/analysis.json`.

**Matched six-configuration HIGH vs LOW aggregate** (identical config set; Qwen excluded on both sides):

| Aggregate | Mean canonical Δ |
|---|---:|
| HIGH matched (n=6) | **+7.39 pp** |
| LOW matched / primary (n=6) | **+8.53 pp** |

Source: `phase2b/analysis/low/analysis.json` → `matched_high_sensitivity` and `phase2b/analysis/high_low/analysis.json`.

> Do **not** silently compare LOW `n=6` to HIGH’s published full `n=7` aggregate (+7.07 pp) without stating unequal configuration sets.  
> Do **not** present any historical Qwen LOW −12.08 pp figure as a Qwen 3.8 Max priming effect.

---

## 4. Qwen incident

| Item | Record |
|---|---|
| Intended model | **Qwen 3.8 Max — Fast** (Direct and Primed) |
| Actual Direct | Qwen 3.8 Max — Fast |
| Actual Primed | **Qwen3.7-Plus** (default-selected in Qwen Chat) |
| Pairing status | **`INVALID — MODEL MISMATCH`** |
| Subsequent Qwen3.8-Max Primed attempt | service error (verbatim): `Oops! There was an issue connecting to Qwen3.8-Max.` / `Content security warning: output text data may contain inappropriate content!` |
| Workaround attempted | **NO** |
| Raw evidence | preserved (outputs + metadata hashes; not deleted) |
| Qwen 3.8 Max LOW priming effect | **not estimated** |

Authoritative records: `phase2b/analysis/low/QWEN_INCIDENT.md`, `phase2b/analysis/low/invalid_cells.json`.  
Classification: **execution / infrastructure incident**, not a linguistic priming result.

---

## 5. Gemini constraint

| Item | Record |
|---|---|
| Protocol | LOW Primed used the **established multi-message** corpus delivery structure |
| Reason | interface / **context-window** constraint |
| Data status | retained as **valid under the executed protocol** |
| Redesign | **none** — no retroactive redesign of the Gemini experiment |

This is an infrastructure/protocol observation, not a reason to reinterpret Gemini Δ values as invalid.

---

## 6. HIGH vs LOW synthesis (descriptive only)

Verified descriptive findings from `phase2b/analysis/high_low/`:

- Matched HIGH mean Δ = **+7.39 pp**; LOW valid six-configuration mean Δ = **+8.53 pp**.
- Do **not** treat the **+1.14 pp** difference as meaningful by itself.
- **Gemini** shows **direction reversal** between regimes (HIGH near-zero/negative → LOW strongly positive).
- **Claude / DeepSeek / GPT** remain positive in both regimes (modest mean shifts).
- **Grok** shows a large reduction (HIGH +14.49 → LOW +3.95) and **mixed** LOW replicate signs.
- HIGH large positive effects often **coincide with** corpus-opening / motif copying.
- LOW positive effects often occur **without** systematic opening copying (lexical borrowing / orthography cleanup with Podkłady structure retained).

**Hypotheses (not established mechanisms):** overlap with corpus-like openings/motifs may contribute to some HIGH gains; priming response appears substantially configuration-associated; LOW gains may reflect local lexical/orthographic conditioning without narrative reuse.

---

## 7. What is established / not established

### Supported observations

- HIGH 42/42 complete; LOW 42/42 retained with 6 valid paired cells and 1 invalid Qwen cell.
- Matched 6-config means: HIGH +7.39 pp, LOW +8.53 pp.
- Gemini regime direction reversal; Claude/DeepSeek/GPT both-regime positives; Grok magnitude drop with LOW mixed replicates.
- Qualitative contrast: HIGH opening-copy common in large+; LOW opening-copy not systematic.
- Qwen3.8-Max LOW priming is not estimated; Gemini multi-message protocol preserved as executed.

### Compatible hypotheses

- Part of HIGH Δ may reflect overlap with corpus-like openings/motifs.
- Priming response is substantially configuration-dependent.
- LOW positive Δ without opening-copy may reflect local lexical/ortho conditioning.
- Coverage metrics may amplify some changes independently of human-judged quality.

### Not established

- Causal effect of corpus priming in general.
- Confirmation of H-HIGH as a causal claim.
- A law that HIGH-overlap produces larger Δ than LOW-overlap.
- Statistical significance (n=3; no tests).
- Model ranking or inherent model superiority.
- UNSEEN-domain behavior.
- Qwen 3.8 Max LOW priming effect.

---

## 8. Frozen inputs and integrity

| Input | Path | SHA-256 |
|---|---|---|
| HIGH story v1 | `phase2b/input/versions/iskra-wieloryb-original-names-v1.txt` | `ab8a0dcf7352789c09c4aca132c086999c861407e4cd682ee9414aab5b792f63` |
| LOW story v1 | `phase2b/input/versions/podklady-v1.txt` | `ce1c4fca03fe9cb2c5f8181ab45c91767759a0c785f0a066543d95bc32f5271b` |
| Authentic corpus v1 | `phase2a/corpus/phase2a-authentic-isv-corpus.txt` | `aaad28e43935a40313585d77a33bfc788d97e8d69b081f9486af74d52ca1a857` |

**Confirmation:** HIGH story, LOW story, and authentic corpus are **frozen** and were **not modified** by analysis, synthesis, or this checkpoint. HIGH and LOW raw `output.txt` files are retention-protected evidence (not rewritten by this checkpoint).

---

## 9. UNSEEN status

- UNSEEN has **not** been frozen.
- No UNSEEN story has been selected as authoritative.
- No UNSEEN kit exists.
- No UNSEEN LLM sessions have been run.
- No UNSEEN results exist.

This checkpoint does **not** choose an UNSEEN story.

---

## 10. Known infrastructure / execution constraints

Separated from linguistic results:

| Constraint | Nature | Consequence |
|---|---|---|
| **Qwen LOW model mismatch + later content-security block** | execution / infrastructure | invalid paired cell; priming not estimated; evidence retained; no workaround |
| **Gemini multi-message corpus delivery** | interface / context-window protocol | data valid as executed; no retroactive redesign |

---

## 11. Next decision point

> The next experimental decision is selection and validation of the UNSEEN source text and confirmation of the execution protocol before any UNSEEN kit is prepared.

This checkpoint does **not** make that decision.

---

## Known documentation discrepancies

Historical task snapshots (e.g. Task 030 rows stating `Podkłady` “not prepared”) are intentionally left as historical and are **not** conflicts with this checkpoint.

One mild presentational risk:

- `docs/EXPERIMENTS.md` — the **HIGH** experiment status cell still includes the phrase “LOW/UNSEEN not started,” which was accurate at HIGH preservation time (2026-09-15) but can be misread as the **current** Phase 2B state. The separate LOW section and this checkpoint supersede that reading. Not rewritten here (historical HIGH entry).

No conflict was found between current machine-readable HIGH/LOW aggregates, the Qwen incident ledger, and the HIGH↔LOW synthesis figures cited above.

---

## Artifact index (compact)

| Role | Path |
|---|---|
| HIGH aggregates | `phase2b/analysis/` |
| HIGH evidence / qualitative | `phase2b/EVIDENCE.md`, `phase2b/QUALITATIVE_AUDIT.md` |
| LOW aggregates | `phase2b/analysis/low/` |
| LOW evidence / qualitative / incident | `phase2b/analysis/low/EVIDENCE.md`, `QUALITATIVE_AUDIT.md`, `QWEN_INCIDENT.md` |
| HIGH↔LOW synthesis | `phase2b/analysis/high_low/` |
| This checkpoint | `phase2b/EXP-004_PHASE2B_CHECKPOINT.md` |
