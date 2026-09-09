# Translation Method — intervention ladder, pipelines, and evaluation layers

**Status labels used in this document:** `COMPLETED` (measured) ·
`CURRENT` (the agreed next step) · `PROPOSED` (designed/scoped, not
executed) · `HYPOTHESIS` (untested claim).

> This document records the project's translation-method thread: what
> intervention ladder has actually been tested, what remains
> hypothetical, the proposed pipeline orderings, the evaluation layers,
> and the conceptual architecture of the eventual PL → ISV translation
> tool. It was created in SODA Task 028 (2026-09-09) so future work does
> not depend on undocumented external discussion. Scientific framing and
> the experiment record live in
> [`docs/research-roadmap.md`](research-roadmap.md); this document
> focuses on the *method*.

## 1. Purpose

The project's practical goal is a reproducible Polish → Interslavic
translation workflow that reliably improves on the unguided baseline
(`docs/research-roadmap.md` §2). The long-term hypothesis
(`HYPOTHESIS`): the best final system may be a **multi-stage pipeline**
rather than a single prompt — and the optimal *ordering* of interventions
must be measured, not assumed.

## 2. Evaluation layers — keep separate, never collapse

Three independent layers are maintained. **No composite "quality score"
exists or should be created** (project convention; `docs/ROADMAP.md`,
EXP-003 REPORT, `assistant-research-bundle` figures).

- **Layer 1 — resource coverage** (machine, implemented):
  - canonical coverage = (A + B) / lexical tokens;
  - broader resource-supported coverage = canonical-supported tokens plus
    exact alternative-resource attestations, over lexical tokens
    (`docs/RESOURCE_POLICY.md`; implemented in `isv-eval`, Task 008).
- **Layer 2 — formal language / orthographic quality** (machine,
  audit-only): allowed ISV alphabet, Cyrillic contamination,
  Polish-specific-letter contamination, other scripts, morphology where
  available, resource-backed lexical evidence (Task 015 orthography
  audit; `scripts/check_orthography.py`). Diagnostic only — never a
  rewriting step.
- **Layer 3 — human quality**: naturalness, intelligibility, readability,
  communicative adequacy. The single EXP-003 human test (100 questions,
  one non-expert participant) is recorded but is not a strong selection
  criterion (D-042/D-043); no further human evaluation is planned unless
  a justified expert protocol exists (`PROPOSED`).

Rationale: the current automated metrics are useful for **controlled
comparison** but are not a complete semantic or linguistic quality
measure (`docs/RESOURCE_POLICY.md` §11; `docs/RESEARCH_NOTES.md`).

## 3. Metric definitions (used everywhere)

- **Canonical coverage** — fraction of lexical tokens (excluding
  non-lexical/name tokens per the evaluator's denominator policy) that
  match the canonical dictionary exactly (A) or are morphologically valid
  against the generated full-form lexicon (B).
- **Broader resource-supported coverage** — canonical coverage plus
  tokens with an exact surface attestation in the audited alternative
  resources (`isv.dic`, `interslavicfreq` wordlists, `slovnik`
  snapshot). An evidence estimate, never a validity claim; alternative
  hits are never promoted into A/B.
- **Unresolved rate** — unresolved (C-tier) lexical tokens / lexical
  tokens.
- **Orthography audit** — character-level counts outside the official ISV
  Latin alphabet, split by category (Cyrillic / Polish-specific / other
  Latin / other script / unexpected non-letter), with proper-name
  effects handled deterministically (non-name refinement, Task 016).

Coverage values are stored as fractions in the machine-readable export
(`experiments/exp004-modelscreen/assistant-research-bundle/`); multiply
by 100 for percentage points.

## 4. The intervention ladder A–E (`COMPLETED` evidence, `HYPOTHESIS` only for the full ladder)

| Rung | Intervention | Status / evidence |
|---|---|---|
| **A** | no assistance (direct baseline) | `COMPLETED` — EXP-001, EXP-003-A, EXP-004 Phase 1 direct |
| **B** | one dictionary candidate per unresolved form (deterministic, supplied at generation time) | `COMPLETED` — EXP-003-B |
| **C** | multiple resource-supported alternatives | `COMPLETED` — EXP-003-C |
| **D** | lexical scaffold + grammar annotations / morphology information | `COMPLETED` — EXP-003-D |
| **E** | authentic corpus priming (reference-text conditioning at inference time) | `COMPLETED` for EXP-004 Phase 2A single-run (Task 024) and repeated (Task 026) |

Post-hoc revision (EXP-002) is a **repair-style** intervention on the
output side of A (whole-document re-generation with supplied candidates),
not one of the generation-time rungs; it informs the repair stages of the
future pipeline (§6).

Key measured findings:
- Dictionary intervention can produce large gains: EXP-003 B vs A
  ChatGPT **+9.45 pp**, Claude **+3.16 pp** canonical
  (`docs/EXPERIMENTS.md` §EXP-003).
- Multiple alternatives can perform *worse* than a single candidate:
  C vs B ChatGPT −0.90 pp, Claude −3.56 pp. **More alternatives are not
  automatically better.**
- Morphology/grammar information (D) can produce additional gains, but
  the result is model-dependent: Claude D is its strongest condition
  (85.62 % canonical / 92.02 % broader); ChatGPT D does not beat its own
  B (`docs/EXPERIMENTS.md` §EXP-003).
- Corpus priming (E) is **qualitatively different**: the model receives
  authentic target-language *examples* (whole reference text) rather than
  explicit word substitutions. Measured effect (EXP-004 repeated,
  descriptive): mean repeated Δ canonical **+6.93 pp**, positive in
  16/16 assessable configurations; repeated broader Δ +3.88 pp; direction
  reproduced vs the single-run estimate in 15/15 rows
  (`experiments/exp004-modelscreen/repeats/REPORT.md`;
  `assistant-research-bundle/summary.json`).
- Corpus priming is inference-time context, **not training /
  fine-tuning**, and the project does not call it that.

The ladder A–E as a single ordered scale is a **conceptual frame**
(`HYPOTHESIS` for the ordering claim); only the individual rungs have
been measured, and only partially on overlapping data (EXP-001/002 used
the full `op-pl.txt` document; EXP-003/EXP-004 used the canonical
story-only file `5de968a6…`).

## 5. What remains hypothetical (`HYPOTHESIS` / `PROPOSED`)

- That rung E (corpus priming) generalizes to topics absent from the
  corpus → Phase 2B (`docs/research-roadmap.md` §11).
- That a *combined* sequence of rungs beats each intervention alone.
- That the best individual interventions are also the best pipeline
  ingredients (ordering question, §7).
- That effects of EXP-003 B/C/D and EXP-004 simply **add** — explicitly
  **do not assume this**; the optimal sequence must be experimentally
  measured (§7).
- That more context is always better (see literature direction,
  `docs/research-roadmap.md` §14 — look for both positive and negative
  prior results).

## 6. Future translation-pipeline hypothesis (`HYPOTHESIS`, untested)

Candidate orderings (recorded, none established):

| # | Ordering |
|---|---|
| Pipeline 1 | lexical scaffolding → morphology/grammar → corpus priming → translation |
| Pipeline 2 | corpus priming → lexical scaffolding → morphology/grammar → translation |
| Pipeline 3 | corpus priming → translation → lexical repair |
| Pipeline 4 | lexical scaffolding → translation → morphology/grammar repair |
| Pipeline 5 | corpus priming → translation → dictionary/resource repair → grammar repair |

These are hypotheses only. The pipeline stages map onto tested rungs:
lexical scaffolding (EXP-003 B/C), morphology/grammar (EXP-003 D),
corpus priming (EXP-004), lexical repair (EXP-002-style post-hoc
revision), grammar/morphology repair (unmeasured; would reuse the
morphology resources and orthography audit as a diagnostic).

## 7. Proposed pipeline-optimization experiment (`PROPOSED`, after Phase 2B)

If Phase 2B remains promising, the next focused experiment should be a
**pipeline-optimization** experiment:

- scope: **2–3 representative strong configurations** — do **not** expand
  to dozens of models;
- compare a **small number of intervention sequences** (e.g. a subset of
  the §6 orderings);
- measure: canonical coverage; broader resource-supported coverage;
  orthographic anomalies; **and inspect regressions** (token-aligned
  A→C bookkeeping as in EXP-002/EXP-003);
- human/linguistic evaluation only if a justified expert protocol exists.

Illustrative example of the intended output shape (numbers are **examples
only and must never be written as results until measured**):

```
Baseline:           76 %
→ lexical assistance: 82 %
→ morphology:        85 %
→ corpus priming:    88 %
→ targeted repair:   91 %
```

The desired final product is a reproducible method that can say: "Given
this Polish input, use configuration X, then perform steps Y and Z."

**Phase-2B status (Task 029):** the Phase-2B HIGH-overlap test kit (7
configurations × direct/primed × 3 replicates = 42 planned translations)
is prepared but not executed
(`experiments/exp004-modelscreen/phase2b/`, `docs/research-roadmap.md`
§10–11); the corpus self-evaluation reference point for reading coverage
numbers lives in `experiments/exp004-modelscreen/phase2a/
corpus-selfeval/`. The pipeline-optimization experiment above remains
after Phase 2B, as scoped.

## 8. Evaluation philosophy for the future software

Maintain the three layers of §2 as separate reporting dimensions; never
collapse them into one arbitrary composite score. The eventual software
should automate prompt construction, resource lookup, audit and repair
orchestration while **leaving the actual LLM calls under the user's
control where appropriate**. The software should hide complexity from the
user and tell the user which model/configuration and which prompts/steps
to use — the automation goal is *recommendation + orchestration*, not
silent black-box translation.

## 9. What must not be claimed

- That any pipeline ordering is optimal before it is measured.
- That intervention effects add linearly.
- That coverage improvement equals translation-quality improvement.
- That corpus priming causes improvement universally (current claim is
  observational/descriptive;
  `experiments/exp004-modelscreen/repeats/REPORT.md` §11).
- That the example numbers in §7 are results.

## 10. Source map

| Thread | Source of truth |
|---|---|
| Resource policy + two metrics | `docs/RESOURCE_POLICY.md` |
| Orthography audit | Task-015/016 records in `docs/STATE.md`, `docs/RESEARCH_NOTES.md` §4.13, `scripts/check_orthography.py` |
| EXP-002 (post-hoc revision) | `docs/EXPERIMENTS.md` §EXP-002, `experiments/exp002-pilot/` |
| EXP-003 (scaffolding A–D + human test) | `docs/EXPERIMENTS.md` §EXP-003, `experiments/exp003-scaffold/DESIGN.md` + `REPORT.md` |
| EXP-004 (corpus priming + repeats) | `experiments/exp004-modelscreen/DESIGN.md`, `repeats/REPORT.md`, `assistant-research-bundle/` |
| Corpus self-evaluation (reference ceiling) | `experiments/exp004-modelscreen/phase2a/corpus-selfeval/` (Task 029) |
| Phase-2B HIGH-overlap test (prepared) | `experiments/exp004-modelscreen/phase2b/` (Task 029) |
| Machine-readable results | `experiments/exp004-modelscreen/assistant-research-bundle/results.json`, `summary.json` |
