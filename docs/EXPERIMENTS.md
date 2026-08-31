# Experiment Log

Status of all experiments. Newest last. The canonical design of each experiment
lives in `experiments/<exp>/DESIGN.md`.

---

## EXP-001 — Baseline: unconstrained LLM translation Polish → Interslavic

| Field | Value |
|---|---|
| Status | **RUN COMPLETED** (Task 003, 2026-08-31). All seven conditions evaluated on the complete story; results in `experiments/exp001-baseline/outputs/comparison.md`. |
| Design | `experiments/exp001-baseline/DESIGN.md` |
| Input | One complete Polish short story (`opowiadania-set-isv/op-pl.txt`, SHA-256 `e3164ffc6a812640967ff749158db4746bea358cb4ac9c1532c214852b29e643`), used byte-for-byte as one whole-document translation task |
| Models | 7 independent conditions: ChatGPT, Gemini, Claude, DeepSeek, Bielik, Grok, and the custom GPT "Interslavic — Medžuslovjansky Language Teacher" (`gpt-isvt`, kept separate from ordinary ChatGPT). All model versions, generation dates and prompts are **unknown** (externally generated; recorded as `unknown`). |
| Evaluation | Exact dictionary coverage (A), lemma-backed morphological validity (B), unresolved forms (C), lexical/total tokens; per-model unresolved-form lists with sentence context, candidate lemmas and frequencies; cross-model comparison with pairwise overlaps and shared-form counts |
| Harness | `isv-eval` CLI (tokenizer, lexicon lookup, morphology-backed validation, A/B/C + review metadata, metrics, JSON reports); lexicon = `basic.json` snapshot + `@interslavic/morphology@0.1.2` full-form lexicon (320,824 entries) |
| Reproducibility | Seven immutable run dirs under `experiments/exp001-baseline/outputs/<run_id>/`; every report embeds dictionary manifest + morphology version + evaluator commit `48f2523` + source/output SHA-256; raw inputs stay out of git (`.gitignore`) |
| Follow-up | The future constrained-generation experiment compares against this baseline (see DESIGN.md § Future experiment) |

### Results (automatic metrics, lexical-token denominators)

| Condition | Lexical Tokens | Exact (A) | Morph. Valid (B) | Unresolved (C) | Valid Coverage | Unresolved Rate |
|---|---:|---:|---:|---:|---:|---:|
| ChatGPT | 1522 | 1153 | 3 | 366 | 75.95% | 24.05% |
| GPTs — ISV Teacher | 1522 | 1213 | 2 | 307 | 79.83% | 20.17% |
| Gemini | 1471 | 1054 | 1 | 416 | 71.72% | 28.28% |
| Claude | 1486 | 1092 | 1 | 393 | 73.55% | 26.45% |
| DeepSeek | 1431 | 1064 | 1 | 366 | 74.42% | 25.58% |
| Bielik | 1561 | 862 | 4 | 695 | 55.48% | 44.52% |
| Grok | 1472 | 1127 | 0 | 345 | 76.56% | 23.44% |

Order is not a ranking. Bucket B fires rarely (0–4 tokens per run), as expected
with a complete full-form lexicon (L-001).

### Shared unresolved forms

- unique unresolved forms across all conditions: **1050**
- shared by 2+ models: **219** · shared by 3+ models: **83** · shared by all 7: **8**
- the 8 forms unresolved by *all* models are `bojala`, `bojati`, `bronislava`,
  `dokazano`, `pui`, `pul`, `rekla`, `teofil` — character names
  (`Bronislava`, `Teofil`), the story's quoted in-text example words
  (`pul`/`pui`), and inflected verbs common to every output
  (`bojala`/`bojati`, `dokazano`, `rekla`). They are shared because they are
  story content, not because the models converge on errors.
- highest pairwise overlap: **ChatGPT ∩ GPTs — ISV Teacher = 76** unresolved
  forms (both are OpenAI-hosted systems; the custom GPT still differs
  substantially from ordinary ChatGPT in coverage).

### Notable observations (factual only)

- Bielik is the clear outlier: 695 unresolved forms (44.5% unresolved rate)
  vs 20–28% for the other six; its output is also the only one without
  section headings and ends with `KRAJ` instead of `KONEC`.
- The specialized custom GPT (`gpt-isvt`) has the **highest** valid coverage
  (79.83%) and **lowest** unresolved rate (20.17%) of all conditions, while
  ordinary ChatGPT lands mid-table (75.95% / 24.05%).
- No condition produced Cyrillic output; all seven outputs are Latin script.
- Output sizes span 9,863–10,310 bytes (source 10,827 bytes); Bielik has the
  most lexical tokens (1,561), DeepSeek the fewest (1,431).
  **Note (Task 003.1): raw file size is NOT a valid comparison of translation
  length in Experiment 001.** The Polish source file begins with the
  translation instruction `Przetłumacz to opowiadanie na medżusłowiański:`
  (plus a markdown fence), which the model outputs do not contain; the source
  is therefore not byte-comparable with the translations. Byte sizes are
  recorded only for input integrity (hashing), not as a translation-length or
  quality metric. Lexical-token counts above are the informative length signal.
- Per-model titles differ (e.g. Bielik: *Priča o Riječima Koje Su Bile Kao
  Sestre* vs ChatGPT: *Pověst o Slovah, Ktore Byli Jak Sestry*); end markers
  vary (`KONEC`/`KRAJ`).

### Methodological limitations

- Model versions, generation dates, prompts and (for Bielik/Grok) providers
  are unknown and recorded as such; none of the outputs can be confirmed to
  have used `prompt_template.txt` (`prompt_status = unknown` for all runs).
- The custom GPT's internal system instructions are not available
  (`condition_type = specialized_custom_gpt`); the run's `prompt.txt` records
  the standard prompt plus a note, not the actual unseen instructions.
- The supplied source file wraps the story in a markdown code fence with an
  embedded Polish instruction line; the file was hashed and used as-is
  (`source.meta.json` documents this preprocessing artifact). Consequently
  the raw source byte size is not comparable with the translation outputs
  (see Notable observations).
- **Future-experiment rule (Task 003.1):** the source corpus should contain
  *only* the Polish story; translation instructions belong in the prompt.
  Conceptually: `source.txt = Polish story only`, `prompt.txt = translation
  instructions + source text`. Experiment 001 is not retroactively changed;
  this rule governs future controlled experiments.
- Automatic lexical/morphological coverage is not a linguistic-quality
  measure; human evaluation is a separate future task. Raw file size is
  recorded for input integrity only and is not a translation-quality metric.

### Follow-up: manual audit sample (Task 004, 2026-08-31)

A stratified sample of **100 unresolved forms + 8 diagnostic forms** was
prepared for human linguistic inspection (`experiments/exp001-baseline/manual-audit/`,
prepared by `scripts/sample_exp001_audit.py`). It is a follow-up analysis of
EXP-001, not a new experiment; no metrics or raw files were changed and no
linguistic-origin classification was performed. Sample groups: 25
high-frequency (A), 25 shared-by-2–6-models (B), 25 model-specific (C), 15
diverse/edge-case (D), 10 story-name representatives (E), plus the 8 forms
unresolved by all seven models as a diagnostic appendix. Dataset statistics:
1,050 unique unresolved forms / 2,888 occurrences; 831 forms appear in exactly
one model, 8 in all seven.

### Follow-up: cross-resource audit of unresolved forms (Task 005, 2026-08-31)

A **post-hoc evidence audit** re-checked **all 1,050** unique unresolved forms
against the project's other documented Interslavic resources (no sampling, no
resource modification, no linguistic judgment). Prepared by
`scripts/audit_exp001_resources.py`; report and per-form evidence matrix under
`experiments/exp001-baseline/manual-audit/` (local, gitignored).

Resources audited: canonical `basic.json`/lexicon (0 hits — by construction),
the `medzuslovjansky/slovnik` snapshot (0 headword hits), the full-form
Interslavic Hunspell dictionary `isv.dic` (**54** forms, with morphological
tags, e.g. `bojala st:bojati vf:part past sg fem`), and the `interslavicfreq`
wordlists (**403** forms), plus JS morphology (0, deterministic) and Rust
morphology (NOT_TESTABLE — no toolchain).

Primary partition (evidence classes, mutually exclusive): **403** forms
attested verbatim in an alternative resource (38.4%), **450** with recorded
candidate lemmas but no resource evidence (42.9%), **116** with no resource
evidence and no candidates (11.0%), **45** orthographic-variant candidates
only (4.3%), **36** proper-name/story-specific only (3.4%). On direct
evidence, ~48% of the apparent unresolved vocabulary is explained by resource
coverage, evaluator normalization limits, or story-specific names/special
forms; the audit does not claim the remaining ~52% is non-Interslavic (see
`cross-resource-summary.md`). Main research-question answer is evidence-based
and explicitly bounded; no forced conclusion.

## EXP-002 — Pilot: Dictionary-Guided Revision of Experiment 001 Outputs

| Field | Value |
|---|---|
| Status | **EXECUTED AND ANALYZED** (Task 006.2, 2026-08-31). All seven conditions were run externally, compared with the same evaluator, and finalized. Results, transition/regression analysis, the `interslavicfreq` discrepancy, and the recommendation are in `experiments/exp002-pilot/REPORT.md`. |
| Design | `experiments/exp002-pilot/DESIGN.md` |
| Hypothesis | "If an LLM is given explicit Interslavic lexical alternatives for forms that are not present in the canonical dictionary, can it revise its own complete translation into a version with better lexical/morphological resource coverage while preserving the meaning and coherence of the original text?" |
| Loop under test | EXP-001 output → identify unresolved forms → deterministic candidate generation (canonical dictionary / Task-005 cross-resource evidence / morphology) → stratified pilot selection → revision prompt (complete original + candidate table) → EXTERNAL LLM → complete revised translation → SAME `isv-eval` on original and revised → before/after comparison |
| Two questions kept distinct | (A) Can an unresolved form be replaced by a resource-supported form? — deterministic candidate generation, no LLM. (B) Can an LLM use supplied alternatives correctly in context? — the actual pilot research question. |
| Candidate sources | canonical dictionary (`basic.json`/lexicon), orthographic variants, alternative resources (hunspell `isv.dic`, `interslavicfreq`, `slovnik` snapshot), morphology-derived canonical lemmas (JS engine paradigms as supporting evidence), none (leave unchanged). Provenance per candidate; no invented candidates; no language-origin classification. |
| Pilot composition | 30 stratified forms per source run (ortho / resource / morphology / high-freq / shared / specific / no-candidate strata); character names and quoted example words excluded from revision targets. Prepared for all 7 runs by `scripts/prepare_exp002_pilot.py`. |
| Execution | External (no LLM API client, D-007). `scripts/run_exp002_pilot.py collect` stores raw replies byte-for-byte, records metadata (unknowns stay `unknown`), refuses overwrite. All seven runs were executed via the `operator-prompts/` copy/paste interface. |
| Evaluation | `scripts/compare_exp002.py` — before/after: lexical tokens, A/B/C counts, valid coverage, unresolved rate, unique unresolved forms, resolved / newly-introduced forms; replacement metrics: supplied candidates used / accepted / not used / replaced-without-candidate. Since Task 006.2: a **token-aligned evaluator-state transition matrix** (all nine C→A/C→B/C→C/A→A/A→B/A→C/B→A/B→B/B→C transitions, with A→C and B→C regression lists) and a **per-selected-form candidate-usage table**. Same evaluator as EXP-001. |
| Human evaluation | 5 complete before/after text pairs in `comparison/human_review.md` (curated across outcome categories) for holistic Project-Owner reading (qualitative evidence, no word-by-word annotation, no scores). |
| Reproducibility | Selection and candidates deterministic (regeneration byte-identical except `prepared_at`); per-run metadata records source EXP-001 run id, original/revision SHA-256, prompt hash, candidate list, evaluator commit, dictionary manifest, resource provenance, experiment condition. Completeness + SHA-256 verified for all 7 runs by `scripts/verify_exp002_runs.py` (7/7 pass). |
| Layout | `experiments/exp002-pilot/{DESIGN.md, README.md, REPORT.md, prompt_template.txt}` committed; `input/`, `outputs/`, `comparison/` gitignored (embed raw model output). |

### Status (Task 006)

- Prepared: `scripts/prepare_exp002_pilot.py`, `scripts/run_exp002_pilot.py`,
  `scripts/compare_exp002.py`, `prompt_template.txt`, DESIGN + operator README.
- Input packages built for all seven source runs: `exp002__<exp001_run_id>`
  under `experiments/exp002-pilot/input/` (each 30 selected forms; ~24 with
  candidates, ~4–9 without — the "no candidate" stratum is the control).
- No revised outputs yet (`run_exp002_pilot.py status` shows 0/7 with
  revisions); before/after numbers will be recorded here after external
  execution. Success criteria in DESIGN §10; no assumption the answer is yes.

### Follow-up: operator packaging (Task 006.1, 2026-08-31)

Usability audit and packaging of the prepared pilot (no experiment change):

- Audited all seven input packages. `prompt.txt` is a **complete
  self-contained revision prompt**: revision instructions, the candidate table
  with provenance (30 forms per run), and the complete original translation
  (byte-exact tail). There is no `source.txt`; the byte-for-byte EXP-001
  output is `original.txt`. `candidates.json` adds machine-readable structure
  (sentence context, stratum, POS/tags/cB/paradigm evidence) not needed to run
  the experiment.
- Created **one self-contained Markdown prompt per condition**
  (`experiments/exp002-pilot/operator-prompts/01-chatgpt.md … 07-grok.md`,
  generated by `scripts/package_operator_prompts.py`, byte-identical on rerun,
  no timestamps): explicit target, revision instructions, full original
  translation, candidate alternatives with provenance, no-candidate controls,
  whole-document output requirement, preservation rules, vocabulary
  constraint, and the explicit "use supplied alternatives, not independent
  discovery" distinction (added to the prompt template — the only LLM-facing
  gap found).
- Selection verified **byte-identical** after regeneration; EXP-001 outputs,
  metrics, dictionary, and evaluator untouched. Operator `.md` files are
  gitignored (they embed complete model output); README + manifest.json
  committed. The pilot is ready for external execution with copy/paste only.

### Follow-up: execution and finalization (Task 006.2, 2026-08-31)

The pilot was executed for all seven conditions and finalized. Headline
results (same evaluator as EXP-001; lexical-token denominators; Δ pp of valid
coverage):

| Model | Baseline | Revised | Δ pp | Unresolved tokens | Unique unresolved | A→C regressions |
|---|---:|---:|---:|---:|---:|---:|
| ChatGPT | 75.95% | 77.20% | +1.25 | 366 → 347 | 189 → 184 | 2 |
| Claude | 73.55% | 74.83% | +1.28 | 393 → 374 | 197 → 195 | 3 |
| Gemini | 71.72% | 72.60% | +0.88 | 416 → 403 | 197 → 190 | 0 |
| Grok | 76.56% | 77.51% | +0.95 | 345 → 331 | 176 → 176 | 7 |
| GPTs — ISV Teacher | 79.83% | 80.35% | +0.53 | 307 → 299 | 175 → 173 | 0 |
| DeepSeek | 74.42% | 74.77% | +0.35 | 366 → 361 | 176 → 173 | 0 |
| Bielik | 55.48% | 55.48% | +0.00 | 695 → 695 | 335 → 335 | 0 |

- **Bookkeeping improvement.** `compare_exp002.py` now computes a
  **token-aligned evaluator-state transition matrix** (LCS alignment of
  lexical tokens): totals C→A = 90, A→C = 12, B→C = 0, C→B = 0 (the B bucket
  is nearly empty in these texts, 1–4 tokens per run). This exposed A→C
  regressions the old unique-form bookkeeping missed (e.g. ChatGPT
  `někogda→někdy`, `čto→što` — supplied candidates over-applied to
  already-valid forms; and Claude `različna→různa`, the third Claude
  regression).
- **Candidate usage.** All six revising models adopted 4–7 supplied surfaces
  as targeted replacements; 5–6 supplied surfaces were newly introduced by
  each revision; Bielik introduced none. Accepted adoptions almost always
  coincide with canonical dictionary forms; adoptions attested only in
  alternative resources are rejected by the evaluator.
- **A→C regressions (12).** Grok (7) and Claude (3) changed valid `različ-*`
  forms into non-supplied `růz-*`/`různč-*` spellings (compliance failure);
  ChatGPT (2) over-applied supplied candidates to valid forms
  (`někogda→někdy`, `čto→što`). B→C = 0 everywhere.
- **`interslavicfreq` discrepancy.** Supplied surfaces attested in
  `interslavicfreq` are invisible to the canonical evaluator: adopted
  replacements `seli`, `sedeli`, `reci`, `rekl`, `dejstvitelno` produced no
  coverage gain, and 113 alternative-resource surfaces used in revisions were
  never accepted. The evaluator is strictly canonical-dictionary-driven
  (exact/folded lexicon match + morphology over prefix-matching canonical
  lemmas); these forms have no canonical lemma path (e.g. `reći` is absent
  from the canonical dictionary; `bojati sę` is excluded from lemma-driven
  morphology; `dejstvitelno` has no prefix-matching lemma at all). This is an
  evaluator/resource integration gap by design, not an error in either layer.
- **Bielik.** Byte-verified no-change: identical lexical token sequences
  (1561 = 1561), 0 positional diffs; only formatting changed (33 leading `- `
  dialogue markers removed, dialogue re-indented). No target form replaced, no
  supplied candidate introduced; hypotheses recorded, no internal-cause claim.
- **Human review.** 5 curated complete before/after pairs in
  `comparison/human_review.md` (clear improvement / no regression / with
  regression / little improvement / no change) for holistic Project-Owner
  reading.
- **Recommendation.** **B — improve the evaluator/resource layer first**:
  candidate generation and evaluation use inconsistent resource layers, so
  coverage numbers from any larger experiment would be uninterpretable until
  they are reconciled. Not started.

Full report: `experiments/exp002-pilot/REPORT.md`; per-run detail in
`comparison/<run>/` (local, gitignored).

## Planned (not started)

- **Implement the resource policy in `isv-eval` (recommended next task,
  Task 007 outcome B)** — add a clearly-labeled alternative-resource
  attestation tier and report canonical coverage + broader resource-supported
  coverage side by side, leaving historical A/B/C classifications untouched;
  policy in `docs/RESOURCE_POLICY.md`. Not started.
- **EXP-002 full scale / EXP-003** — only after the resource policy is
  implemented in the evaluator (so coverage numbers are interpretable); do not
  proceed automatically.
- **Manual linguistic review** of the EXP-001 unresolved sample (Task 004 artifacts; human-only, no automatic classification).

### Follow-up: resource reconciliation and evaluation policy (Task 007, 2026-08-31)

Not an experiment. The resource set was reconciled into a layered evidence
model and an evaluation policy (`docs/RESOURCE_POLICY.md`; evidence table
`data/dictionary/resource-policy/evidence.json` via
`scripts/audit_resource_layers.py`). Key results:

- **Resource layers** (no resource is "truth"): canonical dictionary
  (`basic.json`/lexicon), morphological rules (JS `@interslavic/morphology`,
  Rust `gold-silver-copper/interslavic` — NOT_TESTABLE, no toolchain),
  alternative resources (`isv.dic`, `interslavicfreq` wordlists), historical
  reference (`slovnik`, same lineage), reference material (Steen/community —
  not ingested).
- **`interslavicfreq` discrepancy explained from data** — three kinds:
  evaluator matching limits (`sedeli`↔`sěděti` folded-prefix gap; `bojati sę`
  multi-token exclusion), morphology coverage (`sěsti` past forms;
  comparatives absent from the `inflect()` lexicon), resource-layer
  differences (`reći`, `dejstvitelno` absent from the canonical dictionary).
- **Evaluator diagnosis**: `isv-eval` answers "canonical resource coverage",
  not "is this valid Interslavic"; metric terminology for future reports is
  **canonical coverage**.
- **Two-metric proposal**: canonical coverage + broader resource-supported
  coverage. Labeled per-run estimate of the broader tier on EXP-001 outputs:
  Claude 73.55→86.00 %, DeepSeek 74.42→82.81 %, Gemini 71.72→82.32 %,
  ChatGPT 75.95→86.27 %, GPTs-ISV Teacher 79.83→88.44 %, Bielik 55.48→78.99 %,
  Grok 76.56→86.41 % (alternative-attested unresolved tokens added). Evidence
  estimate, not a validity claim.
- **No changes**: no resource modified, no evaluator code changed, historical
  results preserved.

