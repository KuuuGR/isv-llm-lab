# Phase 2B LOW — Qwen paired-cell incident

**Status:** `INVALID — MODEL MISMATCH`  
**Classification:** experimental execution / infrastructure incident  
**Not:** a linguistic result, priming effect, or model ranking signal  
**Recorded:** 2026-09-16  
**Incident ID:** `p2b-low-qwen-model-mismatch-2026-09-16`

## What was intended

| Field | Value |
|---|---|
| Configuration | **Qwen 3.8 Max — Fast** |
| Direct | Qwen 3.8 Max |
| Primed | Qwen 3.8 Max |
| Replicates | r01–r03 (fresh independent sessions) |
| Story | frozen LOW `Podkłady` v1 (`ce1c4fca…5271b`) |
| Corpus | frozen `phase2a-authentic-isv` v1 (`aaad28e4…a857`) |

## What actually happened

| Condition | Actual model used |
|---|---|
| Direct (r01–r03) | **Qwen 3.8 Max — Fast** (as intended) |
| Primed (r01–r03) | **Qwen3.7-Plus** (default-selected in Qwen Chat) — **not** Qwen3.8-Max |

Therefore the existing Direct/Primed pairs are **not a valid same-model
paired priming experiment**.

## Why the pair is invalid

Priming Δ requires the same configuration on both sides of each
replicate. Here Direct and Primed differ by model family/version
(3.8-Max vs 3.7-Plus). Any numerical Δ — including the historical
**−12.08 pp** figure — must **not** be cited as a Qwen 3.8 Max LOW
priming effect.

## Subsequent Qwen3.8-Max Primed service constraint

Attempting Qwen3.8-Max Primed with the frozen authentic corpus produced
the following service response (verbatim; treated as an observed
constraint, not worked around):

```
Oops! There was an issue connecting to Qwen3.8-Max.
Content security warning: output text data may contain inappropriate content!
```

### Workaround attempted

**NO.**

Forbidden / not performed:

- modifying, shortening, or paraphrasing the corpus;
- splitting the corpus differently to evade the filter;
- altering the experimental prompt to evade the warning;
- substituting Qwen3.7-Plus as the official Primed model;
- substituting another model;
- retrying calls merely to overcome the block;
- additional LLM sessions for this correction.

## Evidence retained (not deleted)

All six planned Qwen LOW run directories remain on disk with
byte-for-byte `output.txt` and unchanged original `meta.json` /
evaluation artifacts. Sidecar `pairing_validity.json` files annotate
validity without modifying raw outputs.

| Condition | Run IDs |
|---|---|
| Direct (Qwen3.8-Max) | `…__qwen-3.8-max__fast__direct__r01` … `r03` |
| Primed (actual Qwen3.7-Plus; planned id still says 3.8-max) | `…__qwen-3.8-max__fast__primed__r01` … `r03` |

Machine-readable ledger: [`invalid_cells.json`](invalid_cells.json).

## Analytical consequence

| Quantity | Status |
|---|---|
| Planned LOW configurations | 7 |
| Valid same-model paired LOW configurations | **6** |
| Invalid Qwen pairing | **1** |
| Qwen 3.8 Max LOW priming effect | **not estimated** |

Primary LOW aggregates and HIGH↔LOW priming comparisons exclude this
cell. Gemini LOW data are unaffected and were not reinterpreted.

## Related

- Primary LOW evidence: [`EVIDENCE.md`](EVIDENCE.md)
- Qualitative audit note: [`QUALITATIVE_AUDIT.md`](QUALITATIVE_AUDIT.md)
- Regenerator: `scripts/analyze_exp004_phase2b.py --regime low`
