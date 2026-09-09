# EXP-004 methodology — as packaged for independent analysis

Reference commits: Task 024 `bc06858`, Task 025 `2db827d`, Task 026
`048c026` (bundle version 1.0.0). This text is the method
description needed to interpret `results.json` / `summary.json`.

## 1. Phase 1 — direct translation (baseline)

One Polish source story (SHA-256 `5de968a6…`, byte-identical across the
whole project) translated directly to Medžuslovjansky (Interslavic) by
each roster model through its ordinary web/chat interface, with a single
equivalent base instruction and NO guidance (no scaffold, no dictionary,
no grammar notes, no examples). 19 runs were executed; 18 passed the
intake gate (GLM 4.5 failed with a service-error page and is excluded).
Each configuration = provider × model × variant (e.g. thinking toggle).

## 2. Phase 2A — corpus priming

The same Polish translation task, but in ONE fresh session the model
first receives the authoritative **`phase2a-authentic-isv` v1 corpus**
(SHA-256 `aaad28e4…`, ~58 KB) with an explicit *study-as-language-
reference* instruction, then the exact same Polish source + translation
instruction. The corpus has three authentic Medžuslovjansky registers:

- **literary/narrative** — excerpt of *Tuta historija*;
- **artistic/poetic** — the Latin-script *Ahoj, Slovjani!* album
  (poetic forms deliberately not normalized);
- **informative/encyclopedic** — the existing ISV Wikipedia article
  *Sadovničstvo*.

Phase 2A measured one primed generation per configuration; Task 024
analysed `P2A_single − P1_single` per configuration.

## 3. Task 025/026 — controlled repeated generation

To separate the priming shift from run-to-run stochastic variation, every
configuration was generated **3 times per condition** in independent
fresh sessions:

- `direct` r01/r02/r03 — the Phase-1 direct task;
- `primed` r01/r02/r03 — the Phase-2A protocol (corpus → translation).

r01/r02/r03 are **replication blocks, not matched samples**. Prompt bytes
are identical within (configuration, condition); only stochastic
generation and recorded interface/server variation differ. No lexical
scaffolding, no dictionary guidance, no human linguistic classification,
no repair, no re-runs (unusable runs are preserved with status and
excluded). 120 runs planned (108 primary + 12 exploratory Dola Fast/Pro);
114 collected; 106 usable; 8 partial; 6 missing (never fabricated).
Dola is **exploratory** — separate tables/figures only, never in the
primary n=18 statistics.

## 4. Metrics (definitions unchanged from the project evaluator)

Evaluated with **isv-eval v0.1.0** (Task-008 two-tier evaluator,
unmodified) on the raw model reply:

- **canonical coverage** — fraction of lexical tokens (non-name,
  non-multiword-excluded) that match the canonical dictionary exactly (A)
  or are morphologically valid against the generated full-form lexicon
  (B): `(exact + morph_valid) / lexical_tokens`;
- **broader resource-supported coverage** — same denominator, but
  tokens are also credited when they are attested by the audited
  alternative resource layer (exact surfaces in `isv.dic`,
  `interslavicfreq`, `slovnik`). Broader never promotes an A/B change;
  it is a separate, wider tier;
- **unresolved rate** — `unresolved_forms / lexical_tokens` (the C tier:
  neither canonical nor alternative-attested);
- **orthography audit** (Task 015) — character-level check against the
  official ISV Latin alphabet; reported as **outside-inventory** counts
  split by category (cyrillic / polish_specific / other_latin /
  other_script / unexpected non-letters). Orthography is a separate
  quality dimension, never merged into coverage.

Coverage values are stored as fractions in `results.json`/`results.csv`
(multiply by 100 for percentage points). `tokens_total` is the raw
whitespace token count; `lexical_tokens` (`total_tokens`) is the
evaluator denominator.

## 5. Repeated estimate (the primary Task-026 quantity)

For each configuration:

```
repeated Δ = mean(primed r01..r03 usable) − mean(direct r01..r03 usable)
```

This is deliberately different from the old Task-024 quantity:

```
old single Δ = (one primed generation) − (one direct generation)
```

`summary.json` carries both, with the old values marked
`historical_task024`; they are never mixed into the replicate
distributions (Figure D compares them only as a point-vs-distribution
view).

## 6. Statistical caution

- n = 3 usable replicates per condition (smaller where runs are
  missing/partial — see the `n`/`usable_n` fields).
- All statistics are **descriptive**; SD is a sample SD and is NOT a
  precise estimate of population variance at n = 3.
- No causal effect estimate is claimed anywhere; wording stays
  observational ("observed", "consistent with", "replicated / not
  replicated", "not established").
- No winner/composite score: performance, stability, priming response,
  orthographic cleanliness and practical usability stay separate
  dimensions.
- Coverage measures resource grounding, not linguistic correctness or
  naturalness.

## 7. Known interface deviations (full detail in `deviations.json`)

- **Claude Sonnet 5 — max:** thinking/reasoning OFF during the repeats
  (operationally impractical when enabled). Configuration name preserved;
  results not comparable with its Task-024 record without this caveat.
- **Grok:** model identity operator-reported as "Grok 4.5, built by xAI
  (fast)" (files originally said `unknown`); not independently verified;
  prompt bodies unchanged.
- **Gemini:** primed corpus delivered in two messages (interface limit,
  `continue last prompt:` continuation); stored records verify the full
  corpus was delivered — usable with recorded deviation.
- **Dola:** exploratory; identity recorded from the interface, not
  independently verified.
- **Fresh-session provenance:** `fresh_session_proof: unavailable` for
  all runs (msg2-style records carry no machine-visible session
  provenance).

## 8. What cannot be concluded from this bundle

- Causality of corpus priming, generality beyond this story/corpus,
  model superiority ("best model"), naturalness (not measured here).
- Repeated estimates for the two configurations whose primed condition
  was never collected: **Gemini 3.1 Pro (extended thinking ON)** and
  **Qwen 3.8 Max — Thinking** (`status: missing` in results.json).
- Dola Fast's Task-024 +28.20 pp is **not re-estimable** (its repeated
  direct condition is intake-partial → no usable direct replicate).
