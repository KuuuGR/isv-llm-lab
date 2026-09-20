# EXP-004 Phase 2B — Research documentation hub

**Project:** `isv-llm-lab`  
**Experiment:** `EXP-004`  
**Phase:** `Phase 2B` (source-regime corpus-priming tests)

> **`experiments/exp004-modelscreen/phase2b/` is the canonical source of truth.**  
> The `docs/research/exp004-phase2b/` tree is a **curated documentation mirror** for human access and manuscript preparation. Copied files are byte-identical snapshots of canonical artifacts; they are **not** independently authoritative. Prefer the experiment tree when regenerating analysis or resolving conflicts.

Canonical root: [`../../../experiments/exp004-modelscreen/phase2b/`](../../../experiments/exp004-modelscreen/phase2b/)

Copy provenance ledger: [`COPY_LEDGER.json`](COPY_LEDGER.json)

---

## Experimental design

Phase 2B asks whether authentic ISV corpus priming generalizes across source-text regimes.

| Regime | Definition | Frozen source |
|---|---|---|
| **HIGH** | Polish story strongly inspired by the priming corpus | `Iskra i Wieloryb — wersja z oryginalnymi nazwami` |
| **LOW** | Polish story with weak thematic/fabular overlap | `Podkłady` |
| **UNSEEN** | Polish scientific/educational text from a domain absent from the corpus | `Ćwiczenie 2.2 — Biofizyka głosu ludzkiego` |

| Factor | Design |
|---|---|
| Conditions | **Direct** (no corpus) vs **Primed** (authentic ISV corpus first, then translate) |
| Configurations | **7** representative Phase 2B model configurations (identical across regimes) |
| Repeats | **3** independent fresh sessions per (configuration × condition) |
| Planned runs | **42** per regime (21 Direct + 21 Primed) |
| Pairing | Same-model Direct↔Primed pairs; Δᵢ = Pᵢ − Dᵢ |
| Inference | **n = 3** → **descriptive only**; no significance tests; no causal claims |

Priming corpus (all regimes): authentic three-register `phase2a-authentic-isv` v1  
SHA-256 `aaad28e43935a40313585d77a33bfc788d97e8d69b081f9486af74d52ca1a857`  
(never shortened for any model).

---

## Current status

| Item | Status |
|---|---|
| **HIGH** | executed + analysed (42/42; descriptive Δ_HIGH; 2026-09-15) |
| **LOW** | executed + analysed (42/42 retained; **6 valid** paired configs; Qwen `INVALID — MODEL MISMATCH`; descriptive Δ_LOW; 2026-09-16) |
| **UNSEEN** | executed + analysed (42/42; **7/7 valid**; descriptive Δ_UNSEEN; 2026-09-18) |
| **Final cross-regime synthesis** | **Complete** — [`analysis/combined/`](analysis/combined/) (HIGH / LOW / UNSEEN; 2026-09-18) |
| Manuscript (Paper 1) | **Working draft** — [`manuscript/`](manuscript/); map: [`docs/research/PAPERS.md`](../PAPERS.md) |

**Authoritative combined synthesis:** [`analysis/combined/analysis.md`](analysis/combined/analysis.md) · [`analysis/combined/EVIDENCE.md`](analysis/combined/EVIDENCE.md)

Historical notes (do **not** treat as current final state):

- [`checkpoint/EXP-004_PHASE2B_CHECKPOINT.md`](checkpoint/EXP-004_PHASE2B_CHECKPOINT.md) — state **after HIGH+LOW, before UNSEEN**
- Canonical `analysis/high_low/` — exploratory **HIGH↔LOW-only** synthesis (superseded for three-regime questions by `analysis/combined/`)

---

## Important methodological notes

Preserve these as documented; do not strengthen into causal claims.

- **Gemini Primed protocol:** multi-message structure (corpus in msg1, translation in msg2) because of interface/context-window limits. The corpus is **not** shortened for Gemini; the split is a recorded deviation, not a corpus edit.
- **Qwen LOW incident:** one LOW configuration cell is `INVALID — MODEL MISMATCH` (Direct vs Primed model identity mismatch). Retained as evidence; **excluded from primary paired priming analysis** and from matched-six cross-regime means. See [`analysis/low/QWEN_INCIDENT.md`](analysis/low/QWEN_INCIDENT.md).
- **Valid vs invalid pairing:** LOW primary paired analysis uses **6 valid** same-model configuration cells. HIGH and UNSEEN use full **7** configurations. Matched-six comparison uses the six configs valid in all three regimes.
- **UNSEEN source character:** shorter and more expository/domain-specific than HIGH/LOW narratives; treated as a design characteristic / confound to disclose, not silently “corrected.”

---

## Quick navigation

| Area | Hub path | Canonical path |
|---|---|---|
| **Final combined synthesis** | [`analysis/combined/`](analysis/combined/) | `experiments/exp004-modelscreen/phase2b/analysis/combined/` |
| Checkpoint (historical) | [`checkpoint/`](checkpoint/) | `experiments/exp004-modelscreen/phase2b/EXP-004_PHASE2B_CHECKPOINT.md` |
| Frozen source metadata | [`source-material/`](source-material/) | `experiments/exp004-modelscreen/phase2b/input/*.meta.json` |
| HIGH analysis | [`analysis/high/`](analysis/high/) | `experiments/exp004-modelscreen/phase2b/analysis/` (+ root EVIDENCE/QUALITATIVE) |
| LOW analysis | [`analysis/low/`](analysis/low/) | `experiments/exp004-modelscreen/phase2b/analysis/low/` |
| UNSEEN validation + analysis | [`analysis/unseen/`](analysis/unseen/) | `experiments/exp004-modelscreen/phase2b/analysis/unseen/` |
| Readable results | [`results/`](results/) | mirrors of EVIDENCE / analysis.md per regime + combined |
| Manuscript (Paper 1) | [`manuscript/`](manuscript/) | Working draft + [`SUBMISSION_CHECKLIST.md`](manuscript/SUBMISSION_CHECKLIST.md) |

Historical HIGH↔LOW-only pack remains only under the experiment tree:  
`experiments/exp004-modelscreen/phase2b/analysis/high_low/` (not duplicated as the hub “combined” target).

---

## Directory map

```text
docs/research/exp004-phase2b/
├── README.md                 ← this file
├── COPY_LEDGER.json          ← hub↔canonical SHA map
├── checkpoint/
├── source-material/
├── results/{high,low,unseen,combined}/
├── analysis/{high,low,unseen,combined}/
└── manuscript/
```

This hub does **not** duplicate raw LLM session outputs. Those remain under `experiments/exp004-modelscreen/phase2b/outputs/`.
