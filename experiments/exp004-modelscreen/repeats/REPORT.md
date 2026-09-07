# EXP-004 — Phase repeat: controlled repeated generation, stochastic variation (REPORT)

**Status: KIT PREPARED AND TESTED (2026-09-07) — NO RESULTS YET.**
Planned generation date `2026-09-08` (run-id prefix). This report is the
dedicated record for SODA Task 025. It will be completed with results
after the research lead executes the prepared prompts and the outputs pass
the deterministic pipeline (`collect` → `verify` → `evaluate` → `roster`
→ `analyze`). **Do not treat any planned number below as an experimental
result.**

## 1. Research question

For the same model/configuration and the same translation task, how much
does measured Interslavic resource coverage vary between independent
generations, and is the observed Phase-2A corpus-priming shift larger than
that variation?

This follows directly from the Task-024 analysis (`analysis/` at the
experiment root): every single Phase-1 → Phase-2A delta mixes any corpus
priming with the model's own stochastic generation variation,
model/interface behaviour, configuration differences and baseline
dependence (D-051, L-041). Task 025 replaces the single-run comparison
with replicate distributions:

> **old:** `P2A_single − P1_single` (one direct + one primed generation)
> **new:** `mean(primed replicates) − mean(direct replicates)` (3
> independent fresh-session generations per condition), reported against
> each model's own within-condition spread.

## 2. Design

- **Population:** the original **18 usable EXP-004 configurations**
  (Phase-1 roster numbers 01–10 and 12–19; GLM 4.5, number 11, excluded
  because Phase 1 failed; no new primary models).
- **Condition A — Direct:** 3 independent fresh-session generations with
  the authoritative Phase-1 direct prompt (same Polish source story; no
  ISV corpus, no dictionary, no examples, no scaffolding).
- **Condition B — Corpus-primed:** 3 independent fresh-session generations
  with the Phase-2A protocol — fresh session → authentic Medžuslovjansky
  corpus (`phase2a-authentic-isv` v1) → exact Polish source + translation
  instruction → translation collected after the corpus.
- **Replicates:** `r01`, `r02`, `r03` — replication blocks, NOT matched
  linguistic samples. Each replicate is a fresh independent session with
  the exact same prompt bytes; no session continuation, no previous
  translation fed back, no improvement requests, no evaluation results
  shown, no corpus-primed session reuse, no "repeat" cue, no wording
  change. Only stochastic generation and unavoidable interface/server
  variation may differ.
- **No lexical scaffolding, dictionary candidates, morphology hints,
  grammar annotations, post-hoc repair, evaluator feedback, or human
  guidance** anywhere.
- **Collection order:** replicate blocks per configuration (r01
  direct+primed → r02 direct+primed → r03 direct+primed) to reduce
  temporal/interface confounding; per-run timestamps, visible interface
  settings, continuations/retries and deviations recorded as metadata.
- **No human evaluation** (D-042) and **no Phase 2B** preparation in this
  task — Phase 2B stays gated on the repeated-generation results.

## 3. Sample size (planned)

| population | configurations | conditions | replicates | planned generations |
|---|---|---|---:|---:|
| **Primary** | 18 | direct + primed | 3 | **108** |
| Exploratory (Dola 3.8 Fast + Pro) | 2 | direct + primed | 3 | 12 |
| **Total (kit)** | 20 | | | **120** |

Prompt files prepared: 180 (direct × 60; primed msg1+msg2 × 120).
Run manifest: `outputs/plan.json` (120 rows, unique deterministic run
ids); hash-only manifest: `operator-prompts/manifest.json` (180 files);
human collection checklist in replicate-block order:
`outputs/collection-checklist.md`.

### Run IDs

```
<date>__<provider>__<model>__<model_version>__<condition>__<replicate>
date = 2026-09-08 ; condition = direct | primed ; replicate = r01 | r02 | r03
```

Six-field extension of the canonical scheme — no collision with Phase-1
(`…__direct`) or Phase-2A (`…__p2a-ctl|p2a-primed`) five-field ids.

### Authoritative hashes (byte gates)

| input | SHA-256 | source |
|---|---|---|
| Polish source story | `5de968a6214d3d64bdb586b5121f494c4bb107e33546487a86bf8ecc57280723` | Phase-1/2A authoritative input |
| Corpus `phase2a-authentic-isv` v1 | `aaad28e43935a40313585d77a33bfc788d97e8d69b081f9486af74d52ca1a857` | Phase-2A authoritative combined three-register corpus |

`prepare` fails loudly if source/corpus bytes drift. Replicate prompt
linguistic bodies are byte-identical within (configuration, condition) —
only run metadata differs.

## 4. Protocol and interface-deviation record

Protocol per §2 above. Known Phase-2A interface constraints are preserved
and recorded per run as metadata, never silently normalized:

- Gemini corpus-delivery limitation (msg1 may need parts) and
  model/toggle behaviour (extended-thinking reset between messages).
- Claude free-tier interruptions and token-limit continuations; Claude
  Sonnet 5 max practical runtime/token-limit problems.
- GPT Interslavic Teacher's unknown custom system prompt (recorded
  identity only).
- Dola (exploratory): interface-header identity, not independently
  verifiable.

Collection record (fill after execution): date(s), per-run start/end
times, model/configuration, condition, replicate, visible interface
settings (thinking/reasoning ON/OFF, Fast/Thinking/Max/Medium mode,
displayed model name, visible temperature/sampling, web/search — or "not
exposed"), continuations/retries, deviations.

## 5. Intake validation

Reused from Phase 1/2A without change: output present, non-empty,
expected end marker, no source/story echo, plausible length, metadata
matches the manifest, prompt hash matches, corpus hash matches (primed),
no corpus contamination in direct records (fingerprint rejection), no
unexpected source/corpus corruption. Raw outputs are immutable — a
partial/corrupted/interrupted/unusable run is preserved, marked unusable
with the reason, never silently replaced; a later re-run receives a NEW
run id.

## 6. Metrics (definitions unchanged)

Per usable output, from the unmodified deterministic evaluator +
orthography audit: lexical token count, canonical coverage, broader
resource-supported coverage, unresolved rate, orthography audit with
anomaly buckets. Metric definitions are identical to Phase 1 and Phase 2A
for comparability.

## 7. Statistical approach

- Per (configuration, condition): n=3 **small-sample descriptive
  statistics** — n, mean, median, standard deviation, min, max, range for
  canonical coverage; the same for broader coverage; mean unresolved rate;
  orthography anomaly mean/min/max. Explicitly labelled descriptive;
  no normality-based claims, no p-values on n=3.
- Primary priming quantity:
  `Δ mean canonical = mean(primed replicates) − mean(direct replicates)`,
  plus the same for broader coverage; direct/primed SD and range reported
  alongside. Kept explicitly distinct from the old `P2A_single − P1_single`
  (Figure D).
- r01/r02/r03 block differences are reported as a **secondary descriptive
  view only** — replicate numbering is not a matched-samples pairing.
- Baseline dependence revisited descriptively: Spearman between repeated
  direct mean and repeated Δ mean, compared with the Task-024 single-run
  ρ ≈ −0.86 (Figure E) — follow-up/descriptive, not causal.

## 8. Results

_No results yet._ Once collected: per-configuration tables (§7), figures
A–E, selection views, candidate reproducibility answers, Task-024
comparison, supported/suggestive/not-established conclusions, and the
model-selection reading (absolute quality / stability / priming
responsiveness / orthography cleanliness — no winner score) will be
filled in here and in `analysis/analysis.md`.

## 9. Figures (planned)

- **Figure A** — replicate distributions: 3 direct + 3 primed
  observations per configuration with mean markers and connecting mean
  difference (dot/strip + mean/range).
- **Figure B** — distribution of priming deltas
  (`mean primed − mean direct`, sorted); replicate-level differences shown
  faintly.
- **Figure C** — stochastic spread: within-condition SD/range per
  configuration ("how random is the model?").
- **Figure D** — old single-run delta (Task 024) vs repeated mean delta.
- **Figure E** — baseline dependence revisited (repeated direct mean vs
  repeated priming delta; Task-024 ρ ≈ −0.86 reference).

Generated deterministically (SVG, standard library) by
`scripts/analyze_exp004_repeats.py` only when usable observations exist;
until then placeholder files + `status: no_results` scaffold.

## 10. Comparison with Task 024 (method)

Task 024 (2026-09-07) analysed the completed single-run dataset (18
original + 2 exploratory Dola) with `scripts/analyze_exp004_phase2a.py`:
priming Δ table (original 18: mean +6.00 pp canonical, 18/18 positive),
exploratory exact paired tests, descriptive baseline dependence
(ρ ≈ −0.86 canonical), families/orthography, charts A–G. Task 025 is the
recommended controlled-repeat follow-up: the same 18 configurations and
the same inputs, but 3 independent generations per condition, so the
Task-024 single-run deltas can be compared with the repeated mean delta
and with each model's stochastic spread. Dola Fast's +28.20 pp and the
candidate configurations (Claude Sonnet 5 Medium, DeepSeek V3 Expert
ON/OFF, Qwen 3.8 Max Fast, Gemini 3.6 Flash ON, Dola Fast/Pro —
exploratory) get explicit reproducibility questions, answered only by
data.

## 11. Limitations

- n=3 per condition is small-sample descriptive; SDs are noisy estimates
  and no population-level model behaviour is established.
- Replicates are not matched samples; block differences are descriptive.
- Interface/server variation is unavoidable and recorded as metadata, not
  removed.
- Coverage is evidence about resource grounding, not linguistic
  correctness or naturalness.
- Observing repetition does not identify WHY a distribution shifts.

## 12. Recommended next step (after collection)

Decide from the repeated-generation results whether the priming shift
exceeds stochastic variation for enough configurations to justify the
Phase-2B unseen-topic transfer experiment — and which candidate
configurations deserve it. No Phase 2B work was prepared by this task.

---
Artifacts: `outputs/plan.json` (120-run plan), `operator-prompts/
manifest.json` (hash-only), `outputs/collection-checklist.md`,
`analysis/` (no-results scaffold), this report. Generator scripts:
`scripts/run_exp004_repeats.py`, `scripts/analyze_exp004_repeats.py`;
tests: `tests/test_exp004_repeats.py` (25; full suite 237 green).
