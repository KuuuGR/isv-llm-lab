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

## Activity log — follow-ups after EXP-002 (SODA Tasks 007–018)

The pending-work list for the current state of the project is at the end of
this file under **"Planned (not started) — current"**; the blocks below are
chronological records of work done after EXP-002.

### Follow-up: EXP-003 infrastructure implemented (Task 010, 2026-09-01)

Implementation of the approved design; no experiment executed, no LLM called.
Key deliverables and decisions:

- **Deterministic scaffold generator** (`scripts/build_exp003_scaffold.py`):
  reverse index over the `pl` column; pipeline multiword → names (D-031:
  the per-story names table takes precedence over the dictionary —
  `Międzyrzecze`) → exact hit → dictionary-verified lemma recovery → curated
  residual → `[?]`; committed per-story curation tables
  (`curation/op-pl/{names,multiword,residual}.tsv`, D-032: curation is
  committed, aligned scaffolds/inputs/outputs stay gitignored); candidate
  provenance incl. headword-note cleaning and comma-separated
  orthographic-variant splitting (D-033: 11 noted headwords globally, 245
  variant headwords; 20 variant pairs / 131 variant candidates in this
  story); Condition-D grammar annotations (dictionary POS + verb aspect + a
  few generated example forms); Condition-B first-candidate sense-review for
  curated entries (D-034).
- **12 operator prompts** (4 conditions × 3 models: ChatGPT, Claude, Bielik)
  under `experiments/exp003-scaffold/operator-prompts/`, packaged
  deterministically (`scripts/package_exp003_prompts.py`, no timestamps);
  cross-model prompts byte-identical except the condition block.
- **Run orchestrator** (`scripts/run_exp003_pilot.py`): plan with run ids +
  prompt/source/scaffold hashes; byte-for-byte immutable collection with
  SHA-256 + model/provider/version/date metadata (`unknown` when not
  supplied) + resource pins; evaluation via the Task 008 evaluator
  unmodified.
- **Comparison** (`scripts/compare_exp003.py`): per-run two-tier metrics,
  name-excluded diagnostics (D-030), candidate-usage surface proxy,
  invented/non-supplied vocabulary breakdown, within-model and
  within-condition pairwise token-aligned transitions + A→C/B→C regression
  lists + metric/structure deltas, blinded complete-text human-review pairs
  (`comparison/human_review.md` + separate `human_review_key.json`).
- **Integrity verifier** (`scripts/verify_exp003_runs.py`): completeness,
  byte-for-byte SHA-256 integrity, meta self-consistency.
- **Tests**: 30 new (scaffold, provenance, hierarchy, names, determinism,
  prompt packaging, condition separation, run integrity, comparison logic);
  full suite **75 green**. **Determinism**: two independent builds
  byte-identical.
- **Status**: infrastructure prepared — **experiment not executed, result
  unknown**. No evaluator change (Task 008 policy untouched), no LLM API
  client.

### Follow-up: EXP-003 intake, integrity check and preliminary analysis (Task 011, 2026-09-01)

The 12 external replies (3 models × 4 conditions) were registered, verified
and preliminarily analyzed. No LLM was called, no methodology changed, no
output replaced or repaired; failed runs are preserved as data (D-023, D-035).

**Model conditions (recorded in run metadata as supplied by the Project
Owner):** ChatGPT = GPT-5.6 Luna, thinking OFF; Claude = Sonnet 5 Medium
(generation parameters not supplied → `unknown`); Bielik = Bielik 3.0
(provider not supplied → `unknown`). DeepSeek (DeepSeek-V4-Pro, DeepThink ON)
is **not** part of EXP-003's design and was not used.

**12-run completeness matrix (structure inspection, no linguistic judgment):**

| Run | Bytes | Sections (of Prolog+7 Acts+Epilog) | End marker | Status |
|---|---:|---|---|---|
| ChatGPT A | 9,926 | 9/9 | KONEC | ✅ complete |
| ChatGPT B | 10,307 | 9/9 | KONĖC | ✅ complete |
| ChatGPT C | 10,384 | 9/9 | KONĖC | ✅ complete |
| ChatGPT D | 10,413 | 9/9 | KONEC | ✅ complete |
| Claude A | 10,238 | 9/9 | KONEC | ✅ complete |
| Claude B | 10,332 | 9/9 | KONĖC | ✅ complete |
| Claude C | 10,418 | 9/9 | KONEC | ✅ complete |
| Claude D | 10,337 | 9/9 | KONĖC | ✅ complete |
| Bielik A | 4,849 | 3/9 (Prolog + 3 acts, "čin") | none | ⚠️ truncated mid-sentence (~40 % of story) |
| Bielik B | 4,760 | 3/9 (Prolog + 3 acts) | none | ⚠️ truncated mid-word ("Š") |
| Bielik C | 4,087 | 0/9 | none | ❌ no translation (reply paraphrases/echoes the prompt scaffold in Croatian) |
| Bielik D | 128 | 0/9 | none | ❌ no translation (service error page) |

All 8 ChatGPT/Claude replies are single-translation responses: no preamble,
no commentary, complete story structure, ending marker; no format anomalies.
Bielik A and B stop before the story ends (Bielik A after ≈2.5 acts, Bielik B
during act 3) and their orthography is Croatian- / Czech-flavored (observed
fact; the evaluator quantifies the lexical consequence). Bielik C's "echo" is
not a verbatim copy of the prompt — a Croatian paraphrase of the instructions
followed by scaffold prefix lines (≈6 % of the prompt length); Bielik D is a
"Przepraszamy, Bielik ma chwilowe problemy techniczne" service page.

**Integrity:** all 12 temp files registered byte-for-byte through
`run_exp003_pilot.py collect` (never overwritten; SHA-256 in meta.json;
temp == collected verified byte-identical); `verify_exp003_runs.py` 12/12 OK;
full test suite 77 green. Runs recorded with exact model info; new additive
metadata fields `generation_parameters` and documented `status`
(D-035). Bielik C/D have status `failed_external_output` (not evaluable as
translations — recorded explicitly, no fabricated result); Bielik A/B have
`collected_partial_output` (evaluated, but metrics reflect partial text and
are excluded from all comparisons).

**Evaluator results (Task 008 evaluator, unmodified; 10 processable runs;**
lexical-token denominators):

| Run | Lexical tokens | Canonical coverage | Broader coverage | Unresolved rate |
|---|---:|---:|---:|---:|
| ChatGPT A | 1,475 | 76.27 % | 87.05 % | 23.73 % |
| ChatGPT B | 1,478 | 85.72 % | 90.80 % | 14.28 % |
| ChatGPT C | 1,476 | 84.82 % | 89.16 % | 15.18 % |
| ChatGPT D | 1,485 | 84.04 % | 88.82 % | 15.96 % |
| Claude A | 1,513 | 75.81 % | 87.51 % | 24.19 % |
| Claude B | 1,488 | 78.97 % | 86.42 % | 21.03 % |
| Claude C | 1,533 | 75.41 % | 84.47 % | 24.59 % |
| Claude D | 1,516 | 85.62 % | 92.02 % | 14.38 % |
| Bielik A (partial) | 750 | 57.07 % | 78.67 % | 42.93 % |
| Bielik B (partial) | 674 | 38.81 % | 49.19 % | 61.19 % |
| Bielik C / D | — | not evaluated (no translation) | — | — |

**Comparison highlights (8 complete runs; no composite score, no ranking):**

- Scaffold (B) improves canonical coverage over unconstrained baseline (A) for
  both models: ChatGPT +9.45 pp, Claude +3.16 pp. Broader coverage: ChatGPT
  +3.75 pp, Claude −1.08 pp (Claude's B prefers canonical forms but slightly
  fewer alternative-attested ones).
- Alternatives (C) vs B: ChatGPT −0.90 pp canonical (B > C); Claude −3.56 pp
  canonical (B > C). Adding alternatives did not help either model relative to
  the single-candidate scaffold.
- Grammar info (D): Claude D is the best run of the set (85.62 % canonical,
  92.02 % broader; +9.81 pp vs A, +6.65 pp vs B, +10.21 pp vs C); ChatGPT D is
  slightly below its own B (−1.68 pp) and C (−0.78 pp).
- Within-condition model deltas: A nearly tied (ChatGPT 76.27 vs Claude
  75.81); B/C ChatGPT > Claude by 6.8–9.4 pp; D Claude > ChatGPT by +1.58 pp.
- Name-excluded diagnostics reproduce the same ordering (names do not distort
  the comparison). Supplied-candidate adoption proxy (of 667 supplied
  surfaces): ChatGPT A 112 → B 195 → C 195 → D 180; Claude A 111 → B 131 →
  C 139 → D 196. Invented (non-supplied, non-name) unresolved forms fall with
  scaffold use: ChatGPT A 139 → B 85; Claude A 155 → D 82.
- A→C regression lists (e.g. ChatGPT B: `byl→měl`, `dlja→dla`; Claude B→C:
  `ako→jesli` ×7) are the designed token-aligned bookkeeping of different
  translations — evidence for the analysis, not linguistic verdicts.

**Validity answers (evidence-based, § of `docs/RESEARCH_NOTES.md` 4.9):**
(A) 8/12 runs executed the intended conditions; Bielik C/D did not produce a
translation and Bielik A/B truncated before completion. (B) Only 8/12 are
sufficiently complete for quantitative comparison. (C) Bielik (3 of 4
conditions) failed to follow the instructions; ChatGPT and Claude complied in
all 4 conditions. (D) Bielik C (prompt paraphrase/echo) and D (error page)
are unexpected behaviors; Bielik A/B truncation is systematic. (E) No
scaffold-side unwanted effect is measurable from these artifacts; the
scaffold effect is the +3–9 pp B-vs-A gain, while the alternative/grammar
increments differ by model. (F) Yes — where alternatives were supplied (C),
neither model beat its own single-candidate condition (B) on canonical
coverage, and Claude C is even below its baseline A. (G) Condition D's value
is model-dependent and currently not uniform: Claude D is the strongest run
(+10.2 pp over its C), ChatGPT D does not add over B/C. (H) **No — Bielik is
not usable as a quantitative participant**; its four runs either truncate
(2) or contain no translation (2). Its partial numbers are recorded as data
but are not comparable to complete runs.

**Methodological consequences:** the EXP-003 quantitative core is the
8 complete runs (2 models × 4 conditions); Bielik is a qualitative observation
for this experiment. The naturalness question remains open — higher coverage
is not "better Interslavic"; blinded human judgment is the next step.

### Follow-up: sentence-level forced-choice human test prepared (Task 014, 2026-09-05)

The PRIMARY EXP-003 human-evaluation method is now ONE sentence-level
forced-choice experiment (D-038): the Project Owner attempted the holistic
review (Task 012) and found comparing four complete long translations too
cognitively demanding — a format problem, not a result about any condition.
**No holistic human result was obtained and none is recorded.**

- **Participant document** `comparison/sentence_review.md` (prepared by
  `scripts/prepare_exp003_sentence_review.py`, deterministic): **100
  questions** (~50 per model for ChatGPT and Claude); each shows one Polish
  source sentence plus the corresponding sentence from each of the four
  EXP-003 conditions (A/B/C/D) of the same model, in a per-question
  deterministic randomized neutral order "Version 1..4" (seed `20260905`;
  alphabetical order rejected). The Project Owner ticks the version that
  sounds most natural as Medžuslovjansky (best-choice only).
- **Bias control**: instructions ask for a holistic sentence impression,
  state that unfamiliar forms may appear, and say NOT to verify individual
  words against a dictionary. The document has no model names, no A/B/C/D
  condition labels, no automatic metrics, no hints.
- **Sampling**: monotonic length-based DP alignment (source ↔ each condition,
  1:1/1:2/2:1 + skips) + all-pairs cross-run token-overlap floor ≥ 0.30 (the
  four versions render the same source sentence), ≥ 4 words, all-four
  identical excluded; stratified deterministic sampling by story section ×
  dialogue with fully-distinct-version preference. Pools: 99 (ChatGPT) / 101
  (Claude); 9/9 sections covered; 35 dialogue questions; 98/100 questions
  have four pairwise-different versions.
- **Private answer key** `comparison/sentence_review_key.json` (opened only
  after answering): per question — model, section, source-sentence index +
  text, dialogue flag, run ids, version texts, display order (Version →
  A/B/C/D), seed, document hashes. Supports later preference counts by
  displayed version and by condition, rates, per-model/per-condition
  results, and uncertainty/sample-size info. No composite quality score.
- **Superseded artifact preserved**: `human_review.md` (+ key) stays as the
  historical/provisional holistic design with a superseded banner (emitted by
  `compare_exp003.py`); comparison README documents both artifacts. 7 new
  tests; full suite 86 green.
- **Status: test prepared — no answers exist yet.** Next action: the Project
  Owner answers the 100 questions; then the EXP-003 `REPORT.md` combines the
  automatic evidence (Task 011) with the human preferences.

### Follow-up: character-level orthographic sanity audit across EXP-001/002/003 outputs (Task 015, 2026-09-05)

Before EXP-003 closure, all generated translation outputs (EXP-001: 7,
EXP-002: 7, EXP-003: 12 run files) were run through a deterministic,
audit-only character-level sanity check (new `src/isv_eval/orthography.py`,
runner `scripts/check_orthography.py`, 21 new tests). The accepted letter
inventory is the official Interslavic alphabet definition
(https://steen.free.fr/interslavic/orthography.html, fetched 2026-09-05):
standard 27-letter Latin alphabet (no q/w/x) + etymological letters
`ę ų å ė ȯ ć đ ĺ ń ŕ ś ź` + sanctioned alternatives `ť ď ľ ň ř è ò` and
combining-acute `t́ d́`; Polish letters `ą ł ó ż` are flagged separately;
non-letters (whitespace, ASCII digits, explicit prose punctuation) are never
alphabet errors. The audit never modifies text and does NOT recompute or
alter any existing lexical/resource coverage number, A/B/C classification,
or comparison artifact (D-040/D-041) — it is an independent quality
dimension whose per-run reports are regenerated deterministically into each
experiment's gitignored `outputs/orthography_report.{json,md}`.

| Experiment | files | total chars | outside inventory | Cyrillic | Polish-spec. | other Latin | other script | non-letter |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| EXP-001 | 7 | 66 007 | 267 | 31 | 46 | 48 | 0 | 142 |
| EXP-002 | 7 | 65 410 | 309 | 67 | 45 | 55 | 0 | 142 |
| EXP-003 | 12 | 87 797 | 1 297 | 98 | 342 | 508 | 0 | 349 |

Anomalies (see RESEARCH_NOTES §4.13 for detail and line-level per-run data):
Cyrillic letters in Latin-script output (EXP-001/002 Claude 23/59, EXP-003
Claude a–d 9–45 incl. intra-word Cyrillic like `Може`/`ь`; small counts in
DeepSeek/gpt-isvt/Bielik); Polish name orthography kept verbatim
(`Bronisława`/`Przemysława` → `ł` and `w`, the entire EXP-003 `w` count) plus
minor genuine Polish forms (`mečtała`, `pokušała`); Czech/Slovak accented
forms in EXP-003 ChatGPT/Claude (`myslíš`, `právě`, `původu`) and heavy Czech
drift in Bielik-B (`lidé`, `může`, `být`); non-ISV diacritics (Gemini `ē` in
`dējstvitelno`, gpt-isvt OCS-style `ǫ` in `Myslǫ`); EXP-001/002 outputs are
Markdown-formatted (`#` headings, `**bold**`) and Bielik-C echoes its
operator prompt (`→ ‡ [ ]`). Per the methodology, a character anomaly is a
separate signal from lexical/resource coverage — a stray `ł` in a name does
not invalidate a translation, and none of these findings changed any score.

### Follow-up: EXP-003 closed — human results decoded and combined with automated evidence (Task 016, 2026-09-05)

The participant answered all 100 forced-choice questions. Decoder
`scripts/analyze_exp003_sentence_review.py` validated the completed document
against the private key (100 questions, original order, one tick each,
399/400 Version texts byte-identical) and recorded two provenance artifacts
(Q58 `[x ]` encoding; Q67 non-chosen Version-2 text accidentally corrupted
during answering — no effect on decoding; document never modified or
regenerated, D-043). Full results and interpretation: the final
**`experiments/exp003-scaffold/REPORT.md`**; decoded artifacts
`comparison/sentence_review_results.{json,md}`.

**Human preference.** Display positions balanced (V1–V4 = 25/29/22/24).
Overall per condition (n = 100): A 26 %, B 16 %, C 19 %, **D 39 %**
(χ²(3) = 12.56, p ≈ 0.006 vs. uniform). Per model (n = 50): ChatGPT A 26 /
B 12 / C 26 / **D 36 %**; Claude A 26 / B 20 / C 12 / **D 42 %**.
Guidance vs. baseline: **B+C+D 74 % vs. A 26 %, identical for both models**.
One verbatim comment (Q7, vocabulary uncertainty) preserved as qualitative
provenance.

**Human vs. automated.** For Claude the signals agree at the extremes
(D: canonical 85.6 / broader 92.0 / unresolved 14.4 %, human favorite; C:
75.4 / 84.5 / 24.6 %, human least favorite). For ChatGPT they diverge:
B is the automated best (85.7 / 90.8 / 14.3 %) yet the human least
preferred (12 %), while D (84.0 / 88.8, not the coverage best) is the human
favorite (36 %). Exploratory Spearman over the 8 condition points (share vs.
broader +0.49, canonical +0.23, unresolved −0.23, ortho −0.20) is
descriptive only. Task 015 orthographic signal: raw condition deltas are
dominated by the story names kept verbatim; a non-name refinement tracks the
Claude extremes (C dirtiest → least preferred, D cleanest → most preferred)
but does not explain ChatGPT's preference for D over the cleaner B. No
composite score (D-042). Full tables in REPORT.md.

**Status.** EXP-003 is **COMPLETED — CLOSED**. Its human evaluation is
recorded and reported; its automatic evidence and orthographic audit are
unchanged; nothing historical was recomputed. Lessons L-032/L-033, decisions
D-042/D-043; research record §4.14 in RESEARCH_NOTES. Next step (not
started): EXP-004 Phase 1 screening (roster/protocol finalized, execution
gated on approval + access confirmations).

### Follow-up: blinded human naturalness review prepared (Task 012, 2026-09-01) — **SUPERSEDED (Task 014)**

The DESIGN §11 review artifact is ready for the Project Owner
(`comparison/human_review.md` + `comparison/human_review_key.json`,
regenerated by `compare_exp003.py` with a deterministic seeded shuffle):

- **8-run cohort**: ChatGPT A/B/C/D and Claude A/B/C/D — exactly the complete
  runs; Bielik is excluded from the quantitative human comparison (all four
  runs incomplete/failed) and remains preserved as qualitative artifacts.
- **Blinding**: two neutral sets ("Set 1"/"Set 2"); per-set "Version 1..4"
  labels map to A/B/C/D by a reproducible random order (seed `20260901`); the
  document contains no model identity and no automatic metric.
- **Structure**: four DESIGN §11 questions + preference ordering per set
  (PART 1, before unblinding); post-unblinding scaffold-constraint question
  for B/C/D (PART 2); recording checklist (date, verbatim answers,
  presentation order, mapping, before/after split). No score is computed;
  human judgment stays a separate qualitative layer.
- Translations embedded byte-for-byte; 2 new tests; full suite 79 green.
- **Superseded (2026-09-05, Task 014):** the Project Owner attempted this
  holistic review and found comparing four complete long translations too
  cognitively demanding (D-038). The artifact is preserved as a
  historical/provisional review design (superseded banner) and must not be
  performed as the primary evaluation; **no holistic result was obtained**.
  The primary EXP-003 human-evaluation exercise is now the sentence-level
  forced-choice test (Task 014 block above).

### Follow-up: EXP-003 designed — lexical scaffold at generation time (Task 009, 2026-09-01)

Not an experiment — a design task (no implementation, no LLM calls). Deliverable:
`experiments/exp003-scaffold/DESIGN.md`. Research-relevant facts are also
recorded in `docs/RESEARCH_NOTES.md` (methodological taxonomy + measured
numbers). Key verified findings and decisions:

- **Alignment resource already in-repo**: `basic.json` has a Polish
  translation column (`pl`, 18,916 normalized keys). A reverse index covers
  lemma vocabulary (`być→byti`, `się→sę`, `dobrze→dobro`,
  `pierwszy→pŕvy`, `dziś→[dnėś, tutdėnj, sego dnja]`, `tam→[tam, tamo,
  onamo, onde]`). Measured on the actual story (578 unique forms): 207 (36 %)
  direct hits, ~28 (~5 %) via dictionary-verified lemma recovery; the residual
  of 371 splits into ~54 name-like tokens (pass-through) and **~317 inflected
  non-name forms** handled by an explicit per-story curated table; everything
  else maps to `[?]`. Polish lemmatization is **not** a project dependency —
  stated as a limitation, never a silent heuristic.
- **Scaffold-generation method (D-029)**: the generator is **deterministic
  and contains no hidden LLM calls**; lemma-based and LLM-assisted generation
  were analyzed and rejected for v1 (an LLM step would change the variable
  under test). Curated residual table is explicit, committed, provenance-bearing
  human judgment.
- **Conditions**: A = direct baseline; B = scaffold, one canonical candidate;
  C = + alternatives; D = + reliable grammatical annotations (dictionary POS /
  verb aspect / generated example forms only). D is not assumed to be best.
- **Scaffold representation**: token-aligned lines grouped by sentence
  (`Dziś → [dnėś]`), alternatives inline; Polish surface token boundaries are
  preserved while ISV-side units are lemmas/concepts; prompts instruct the
  model that the scaffold is vocabulary guidance, never a surface template.
- **Human evaluation is blinded**: condition labels randomized per model,
  automatic scores withheld until the initial holistic judgment, answers
  recorded verbatim with the mapping key.
- **Scope**: existing story, 3 models × 4 conditions (Claude, ChatGPT,
  Bielik) as a controlled pilot; reuses EXP-002 execution/comparison machinery
  and the Task 008 two-tier evaluator. Recommendation: **GO** for Task 010
  implementation.

### Follow-up: two-layer policy implemented in the evaluator (Task 008, 2026-09-01)

Not an experiment — an evaluator task. The Task 007 policy
(`docs/RESOURCE_POLICY.md`) is implemented in `isv-eval`:

- **Evidence layer** (`src/isv_eval/evidence.py`): loads the audited
  alternative resources (`isv.dic` exact surfaces, `interslavicfreq` wordlists,
  `slovnik` snapshot) and attaches per-token evidence provenance
  (layer/source/kind). A/B/C semantics are untouched; alternative-resource hits
  never become A/B; only exact-surface attestation counts toward the broader
  tier; orthographic variants (`sěli` vs `seli`) and historical presence are
  recorded but never count.
- **Metrics** (`metrics.py`): `canonical_coverage` (== historical
  `morphologically_valid_coverage`) and `broader_resource_supported_coverage`
  reported side by side, plus `canonical_supported_tokens`,
  `broader_resource_supported_tokens`, `unresolved_tokens`. The CLI reports
  both numbers with full resource provenance.
- **Verification**: A/B/C counts and `morphologically_valid_coverage`
  reproduced byte-identically on all 7 EXP-001 runs (raw outputs untouched);
  the new broader metrics reproduce the Task 007 estimate exactly
  (Claude 73.55→86.00 %, DeepSeek 74.42→82.81 %, Gemini 71.72→82.32 %,
  ChatGPT 75.95→86.27 %, GPTs-ISV Teacher 79.83→88.44 %, Bielik 55.48→78.99 %,
  Grok 76.56→86.41 %). 14 focused policy tests added (45 total; full suite
  green).

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


### Follow-up: EXP-004 Phase 1 approved — screening kit prepared, execution pending author sessions (Task 017, 2026-09-05)

EXP-003 is closed; the Project Owner approved the finalized Phase 1 roster +
protocol and ordered its execution (Task 017; DESIGN §12 updated). No further
human-evaluation exercise exists (D-042). The execution kit was built and
tested in the repository:

- `experiments/exp004-modelscreen/base_instruction.txt` — the single
  direct-translation instruction (approved §6.9 wording); all 11 roster rows
  receive byte-identical instruction bodies, differing only in documented
  identity/settings headers (no scaffold, candidates, morphology/POS or
  grammar notes, previous translations, or evaluator feedback anywhere —
  clean baseline).
- `scripts/run_exp004_phase1.py prepare --date 2026-09-06` — packaged 11
  operator prompts (`operator-prompts/`, gitignored), the prompt manifest
  (hashes only, committed), and the fixed `outputs/plan.json` with run ids
  `<date>__<provider>__<model>__<model_version>__direct`. Deterministic:
  byte-identical on regeneration.
- `collect` (byte-for-byte, never overwrite, status + **access filter
  verdict** recorded per row), `verify` (structural completeness gate,
  verdicts complete/partial/failed preserved as data — D-044), `evaluate`
  (Task 008 evaluator unmodified + Task 015 orthographic audit; refused for
  `failed` intakes; `usable` = complete), `status`, `roster` (coverage pair,
  unresolved, orthography, access, usability — no ranking, no composite).
- `scripts/check_orthography.py` now includes EXP-004. 10 new tests
  (128 total, all passing).

**No LLM output exists yet** — the remaining step is the project author
executing the 11 prompts in the models' web/chat interfaces (operator role,
D-007) with the row-specific settings, recording the observed practical
free-access verdict per row (D-036; Gemini/GLM run only if they pass), and
returning the raw replies byte-for-byte for collect → verify → evaluate →
roster. That yields the Phase 1 baseline table and the evidence-based
Phase 2 shortlist (3–5 models), which this task must NOT produce from
assumptions or start before the runs exist.


### Follow-up: EXP-004 Phase 1 executed — collected outputs audited, reconciled, and evaluated (Task 018, 2026-09-06)

The author executed the Phase 1 screening sessions in the external web/chat
interfaces. The planned 11-row roster expanded into **19 concrete
model/configuration runs**; the collected set was audited and reconciled
before evaluation:

- **Raw provenance:** the 19 author session files (prompt + raw reply in
  one markdown file) are preserved byte-for-byte under
  `experiments/exp004-modelscreen/collected-sessions/` (gitignored; README
  committed). `scripts/audit_exp004_collected.py` verified that every
  session's instruction+source body is byte-identical to the canonical
  prompt (clean-baseline invariant holds for all 19), located each reply
  after the prompt's closing `## Output` line, and found **no duplicate
  replies**.
- **Reconciliation (identity from repository evidence, D-045):** DeepSeek's
  planned V4-Pro rows were executed on the models the interface offered —
  **V3 Instant** (DeepThink OFF/ON) and **V3 Expert** (DeepThink OFF/ON);
  Claude split into **Sonnet 5 Medium (default)** and **Sonnet 5 max**;
  Qwen ran as **3.8 Max Thinking, 3.7 Plus Thinking, 3.7 Plus Fast, 3.8
  Max Fast**; Gemini (conditional) ran as **3.1 Pro extended-thinking ON**
  and **3.6 Flash extended-thinking OFF/ON**; Kimi annotated **K2.6
  Instant (Standard)**; Grok version not annotated (recorded `unknown`,
  D-018). Three contradictory author annotations were resolved with the
  author: rows 15/16 = DeepSeek V3 Expert (stale `v4-pro` filenames),
  row 19 = Qwen 3.8 Max **Fast** (header copy error), row 05 = Gemini 3.1
  Pro extended-thinking **ON**.
- **GLM disposition (evidence, no special rule):** the GLM 4.5 session
  artifact is the service error page ("The request couldn't be processed…",
  75 B, no translation, no end marker) after repeated interface errors
  (author report; ~1000 tokens shown, 0 used). It is classified
  `failed_external_output` → intake `failed` and **excluded from
  quantitative evaluation** exactly as the intake protocol specifies; the
  artifact is preserved.
- **Claude Sonnet 5 max (long-reasoning run):** preserved as an execution
  observation (>45 min; exhausted the free-tier allowance). The output is
  complete and passes the intake gate, so the run **is evaluated**; runtime
  is recorded as practical-availability data, not a quality score.
- **Gate calibration (D-045, L-035):** the completeness gate's story-name
  check is now stem-based (ISV-tolerant, case/diacritic-folded, w/v
  variants) because several complete outputs transliterate proper names
  (Bronisława → Bronislava, Przemysław → Przemyslava/Przemyslava, Antoni →
  Anton/Antonij, Julianna → Julianna/Julijana); the end marker accepts
  KONIEC/KONEC/KONĖC. Applied uniformly before evaluation.
- **Results:** 19 collected runs → **18 intake `complete` and evaluated
  (usable); GLM 4.5 is the single failed/excluded run.** The Phase 1
  evidence table (`experiments/exp004-modelscreen/outputs/roster.md`)
  reports per dimension — canonical/broader coverage, unresolved rate,
  orthography-out, access verdict, completeness — with **no composite score
  and no coverage-only ranking**. Preliminary Phase 2 observations (not the
  final selection) are for the Phase 1 report; Phase 2 remains closed.
- **Tests:** 8 added (collect-session, stem gate, audit helpers +
  end-to-end); full suite green (Task 018). Docs updated: D-045, L-035,
  DESIGN §12, exp004 READMEs, STATE, ROADMAP, RESEARCH_NOTES.

### Follow-up: EXP-004 Phase 2A corpus priming — full-roster kit prepared (Task 019, 2026-09-06); reference corpus revised to three authentic registers (Task 020, 2026-09-07)

Phase 2A is the corpus-grounding experiment PREPARED but NOT executed in
Task 019 or Task 020 (no external LLM call). Kit:
`experiments/exp004-modelscreen/phase2a/`; design: DESIGN §13; decision:
D-046. Task 020 (2026-09-07) revised the fixed reference corpus from the
single Task-019 "Tuta historija" excerpt to the combined three-register
authentic corpus below; the kit stays execution-ready.

- **What is tested:** does exposing an LLM to authentic Medžuslovjansky
  immediately before translation change its generated Medžuslovjansky?
  Framed strictly as **in-context learning / corpus priming / contextual
  grounding / reference-text conditioning** (never training; never textual
  reconstruction — the reference text is never the target).
- **Roster:** the FULL reconciled 18-configuration Phase-1 roster (GLM
  excluded), per the author's Task-019 instruction that Phase 2A must not
  be narrowed to a hand-picked shortlist before any corpus experiment. The
  roster is derived in code from `run_exp004_phase1.ROSTER`.
- **Reference corpus — combined three-register authentic corpus (revised
  by Task 020):** under `experiments/exp004-modelscreen/phase2a/corpus/`;
  corpus id `phase2a-authentic-isv` v1; all corpus text files are
  local/gitignored; the committed `corpus/README.md` records provenance +
  hashes.
  1. **Literary / narrative** — `tuta-historija-excerpt.txt` (unchanged
     Task-019 author-supplied "Tuta historija" excerpt — Prolog + Razděl 1
     "Věčna Zima"; 4 820 B; SHA-256 `413830fa…67a29c`).
  2. **Artistic / poetic** — `album-ahoj-slovjani-artistic-isv.txt`
     (complete Latin-script album "Ahoj, Slovjani!" in original order —
     11 songs, 76 unique stanzas, 322 lines, 9 407 B; SHA-256
     `7e25a56f…52dcacf`; source: author-supplied copy of
     melacpise.wordpress.com/album-ahoj-slovjani-teksty-pesnej/; Cyrillic
     duplicates + webpage/HTML removed; 24 verbatim repeated stanzas/
     refrains deduplicated; linguistic forms NOT normalized/corrected;
     license/distribution status not established → local-only).
  3. **Informative / encyclopedic** —
     `wiki-sadovnistvo-encyclopedic-isv.txt` (cleaned running prose of the
     existing authentic Medžuslovjansky Wikipedia article "Sadovničstvo"
     (isv.wikipedia.org), retrieved 2026-09-07 from the actual Wikimedia
     MediaWiki wikitext API — raw wikitext kept at `corpus/sources/`;
     boilerplate/templates/links removed; 84 paragraphs; 44 101 B;
     SHA-256 `b03402fe…4c8345`; CC BY-SA 4.0; authentic ISV article, NOT a
     project translation of any other-language version).
  The authoritative combined file `phase2a-authentic-isv-corpus.txt`
  (58 459 B, ≈8 184 whitespace tokens, SHA-256 `aaad28e4…a857`) joins the
  three under the headers `=== REGISTER 1: LITERARY / NARRATIVE ===`,
  `=== REGISTER 2: ARTISTIC / POETIC ===`, `=== REGISTER 3: INFORMATIVE /
  ENCYCLOPEDIC ===` and is built deterministically by
  `scripts/build_phase2a_corpus.py`. Every primed msg1 embeds the SAME
  combined corpus bytes for all 18 configurations.
- **Prompt-1/msg1 (three-register wording, Task 020):** declares the three
  authentic registers and asks the model to study the corpus as a language
  reference (vocabulary, morphology, syntax, word formation, phraseology,
  orthography, stylistic patterns); warns the artistic register may contain
  deliberate poetic choices and is not a normative grammar template;
  forbids translating/summarizing/reproducing/continuing/analyzing the
  corpus or answering questions about it. msg2 (same Polish story task)
  unchanged; control prompts corpus-free; prompt regeneration
  deterministic; manifest regenerated (54 prompt files).
- **Conditions:** control (`p2a-ctl`; the Phase-1 clean direct task — the
  Phase-1 baseline outputs satisfy it, fresh controls optional) and
  corpus-primed (`p2a-primed`; msg1 = study reference text as language
  reference — no translation/summary/reproduction/imitation/questions;
  msg2 = same Polish story, standard instruction + reference cue, SAME
  session). The translation instruction + story body is byte-identical
  across all control and msg2 prompts (no scaffolding/candidates/
  morphology/repair).
- **Contamination control:** mechanical — `collect-session` requires the
  corpus BEFORE the translation instruction in primed sessions (same-
  session proof), rejects control sessions containing corpus material, and
  rejects altered translation instructions; fresh session per run. Task 020
  added 3 `CORPUS_ANCHORS` fingerprint phrases (one per register;
  `AUTH_CORPUS_SHA256 = aaad28e4…a857`): ALL THREE anchors must appear
  before the translation instruction in primed sessions; ANY anchor in a
  control session is rejected.
- **Run identity:** `<date>__<provider>__<model>__<model_version>__`
  `p2a-ctl|p2a-primed`; every run linked to its Phase-1 `baseline_run_id`;
  36-run plan + 54 prompt files + manifest (hashes); deterministic kit
  (`scripts/run_exp004_phase2a.py prepare --date YYYY-MM-DD`).
- **Result format (`compare`):** per-configuration primed-vs-baseline
  per-dimension deltas (canonical coverage, broader resource-supported
  coverage, unresolved rate, lexical tokens, A/B/C, orthography-out) — no
  composite score, no ranking (L-033). Evaluation reuses the unmodified
  Task 008 evaluator + Task 015 orthography audit.
- **Preserved observation (RESEARCH_NOTES §4.17):** Claude Sonnet 5 max
  (>45 min, continuations, free-tier exhaustion in Phase 1) stays in the
  roster as an availability constraint; an impractical session is recorded
  as an execution limitation, never silently substituted.
- **Tests:** Task 019 added 19 (identity/condition separation, hash
  consistency, prompt separation, no-corpus-in-control, roster coverage,
  contamination rejection, compare; full suite **155 green**). Task 020
  updated `tests/test_exp004_phase2a.py` and added the new real-corpus
  suite `tests/test_exp004_phase2a_corpus.py`; full suite green.
- **Next:** the author executes the 18 primed sessions externally (operator
  protocol in `phase2a/README.md`), then collect/verify/evaluate/compare.
  Phase 2B (Wikipedia-length authentic reference + independent Polish
  story) is documented as future work.

### Task 021 (2026-09-07): Phase 2A executed — audit, Dola 3.8 exploratory integration, evaluation

The author completed all 18 Phase-2A primed sessions **and** added two
primed runs of a newly discovered model/service recorded as **Dola 3.8**
("ByteDance — official web interface"; proprietary; runs 20/21, labels
**"Dola 3.8 — Fast"** and **"Dola 3.8 — Pro"**, author-recorded in the
prompt-file headers only — not independently verifiable from provider
metadata, UI exports or other project evidence). Task 021 treated these as
**exploratory additions beyond the original 18-configuration roster**:
distinct plan rows (`baseline_run_id: null`), distinct manifest entries
(`"exploratory": true`), never merged into the roster, never collapsed into
one observation, and never given a Phase-1 baseline.

- **What was actually collected (protocol deviation).** No full
  same-session transcripts were stored. Each of the 20 runs is recorded as
  the operator-prompts `*-msg2.md` file with the raw model reply appended
  after its closing `## Output` marker. New `collect-msg2` registers these
  (reply sliced at the marker — same rule as `collect-session` — stored
  byte-for-byte; `meta.json` records no machine same-session proof). The
  same-session corpus delivery therefore rests on the prepared msg1 prompt
  files (all present; corpus region byte-identical in all 20) and the
  author's execution notes. Raw replies were never edited; **`prepare
  --force` must not be re-run** (replies now live inside the msg2 files).
- **Dola prompt origin.** The four Dola prompt files were copied from the
  Qwen-3.8-Max-THINKING template with the header metadata edited; the
  translation instruction + Polish story body is byte-identical to the
  canonical prompt and both msg1 files embed the authoritative corpus
  byte-identically. Cosmetic leftovers recorded (Qwen title lines,
  "COPY THIS ENTIRE FILE INTO Qwen Chat (web)" operator line, a msg1
  `Condition:` line mislabelled "(translation task)").
- **Corpus integrity.** Combined corpus SHA-256 still
  `aaad28e43935a40313585d77a33bfc788d97e8d69b081f9486af74d52ca1a857`
  (58 459 B); corpus NOT regenerated; all 20 primed msg1 corpus tails
  byte-identical; controls remain corpus-free.
- **Verify/evaluate.** Intake: **19 `complete`**, 1 `partial` (run 12,
  Claude Sonnet 5 max — final line `**KONEC**` bold-wrapped). All 20
  evaluated through the unmodified Task 008 evaluator + Task 015
  orthography audit (`phase2a/outputs/`); roster 38 rows; `compare`
  produced the 18-row primed-vs-Phase-1 delta table — the Dola rows report
  **no baseline metrics available** and no priming effect is claimed for
  them.
- **Manual execution constraints (author report), recorded as protocol
  conditions, not quality judgments** (see `phase2a/README.md`):
  - Gemini 3.6 Flash: corpus delivered as two messages (~83% + ~17%,
    continuation opened `continue previous prompt`);
  - Gemini 3.1 Pro: corpus ingested in **Gemini 3.6 Flash**, then the model
    was switched to 3.1 Pro for the translation request (interface cannot
    send a second message while remaining in 3.1 Pro) — ingestion model ≠
    translation model;
  - Gemini 3.6 Flash extended thinking: the setting reset to OFF after each
    prompt and was manually re-enabled per prompt (per-message state not
    storable from the saved files);
  - Claude Sonnet 5 / Sonnet 5 max: free-tier token allowance exhausted —
    three attempts/continuations with waiting; final replies are complete
    to their markers and evaluable; the raw continuity history was not
    stored (recorded, never merged/cleaned).
- **Tests:** `tests/test_exp004_phase2a_exploratory.py` (3 new: Dola
  distinctness from the 18 roster; extend-exploratory idempotency;
  collect-msg2 extraction/rejection; no-baseline guard for compare); full
  suite green. No Phase 2B work; no model selection (the research lead
  decides what the results mean).

### Task 022 (2026-09-07): Phase-1 DIRECT baselines for the exploratory Dola configurations — prepared

Dola 3.8 was discovered after the original 18-configuration roster was
fixed, so its two Phase-2A runs (20/21) had **no Phase-1 baseline** at Task
021. Task 022 prepared the two missing Phase-1 direct baselines
**retrospectively** through the existing Phase-1 direct protocol — an
**exploratory extension** (not part of the original planned 18), preserving
the Dola configurations' `exploratory: true` status and their
author-recorded identity ("ByteDance — official web interface";
`dola-3.8`; versions `fast`/`pro`; labels `Dola 3.8 — Fast` / `Dola 3.8 —
Pro`) without upgrading it to an independently verified claim. No LLM was
called; no Phase-2A output or corpus file was touched. Task 023 (below)
records the execution, collection and evaluation of the two baselines.

- **Prompts prepared.** `scripts/run_exp004_phase1.py extend-direct --date
  2026-09-07` rendered two canonical Phase-1 direct operator prompts under
  the Phase-1 kit:
  - `operator-prompts/20-dola-3.8-fast.md` — baseline id
    `2026-09-07__bytedance__dola-3.8__fast__direct`;
  - `operator-prompts/21-dola-3.8-pro.md` — baseline id
    `2026-09-07__bytedance__dola-3.8__pro__direct`.
  Each prompt = fresh-session, single-message, same Polish source story and
  same direct-translation instruction as the original 18 Phase-1 baselines
  — NO authentic-ISV corpus, NO lexical scaffold, NO dictionary, NO
  morphology/grammar material, NO previous Dola conversation, NO Phase-2A
  explanation; explicit operator notes state the Dola configuration to
  select, that it is a Phase-1 direct baseline, the fresh-session rule,
  what exact text to submit, and where to record the raw reply.
- **Status = pending at preparation, never fabricated.** Plan + manifest
  rows were appended as `pending_manual_collection` (idempotent); **no
  outputs, no metrics, no placeholder results** were created at that point;
  the original 18 Phase-1 baselines are unchanged.
- **Pairing (unambiguous).** `link-baselines` (Phase-2A script) set each
  Dola p2a-primed plan row's `baseline_run_id` to its prepared direct id
  (`baseline_status: pending_collection` at Task 022):
  `…__dola-3.8__fast__direct` ↔ Phase-2A run 20; `…__dola-3.8__pro__direct`
  ↔ Phase-2A run 21. No priming effect was claimed at that point.
- **Tests:** `tests/test_exp004_phase1_dola_baselines.py` (new module:
  corpus-free prompts with exact Polish source/instruction, distinct Dola
  configuration metadata, no Phase-2A prompt link, no false completed
  baseline, unambiguous baseline↔Phase-2A pairing, original 18 unchanged,
  full pending→collected→delta lifecycle); full suite green.

### Task 023 (2026-09-07): Dola Phase-1 DIRECT baselines — executed, collected, validated and compared

Follow-up to Task 022: the author executed both Phase-1 direct baselines;
they are now collected, verified and evaluated through the same
deterministic pipeline, and `compare` reports real within-Dola deltas.
Dola remains an **exploratory extension** — Task-020/021 history (Dola
added without a Phase-1 baseline) is not rewritten. No LLM was called; no
Phase-2A output or corpus file was touched; raw replies byte-immutable.

- **Execution + collection.** Each baseline ran in a fresh ByteDance
  session (`Dola 3.8 — Fast` / `Dola 3.8 — Pro` per the recorded operator
  note), direct translation only — same Polish source story, same direct
  instruction, no corpus, no scaffold, no dictionary, no previous Dola
  conversation. The raw reply was saved **msg2-style inside the operator
  prompt file** (`operator-prompts/20-dola-3.8-fast.md`,
  `21-dola-3.8-pro.md`): the prompt part through the closing `## Output`
  marker is byte-identical to the canonical prompt; the trailing "Return
  the complete …" boilerplate was replaced by the reply (same record shape
  as the Task-021 Phase-2A runs).
- **Intake + verify.** Both records passed the Phase-1 `collect-session`
  intake and `verify` gate (verdict `complete`, usable): correct Dola
  configuration, exact Phase-1 DIRECT prompt, fresh-session/direct
  condition, corpus-free, exact Polish story, exact direct-translation
  instruction, complete raw reply with the expected ending marker, no
  accidental Phase-2A continuation, no contamination. The verifier accepts
  msg2-style records (session file == canonical prompt file) without a
  false prompt-drift FAIL — immutability is checked against the recorded
  session SHA-256.
- **Evaluate.** Both baselines evaluated with the same deterministic
  pipeline (evaluation.json + orthography.json under the Phase-1 outputs).
- **Compare (real deltas, exploratory).** Pairing verified (Fast direct ↔
  run 20; Pro direct ↔ run 21). Canonical coverage: Fast 38.87 % → 67.07 %
  [+28.20 pp]; Pro 65.08 % → 71.75 % [+6.67 pp]; broader: Fast 51.67 % →
  78.81 % [+27.14 pp]; Pro 82.27 % → 82.26 % [−0.01 pp]; unresolved: Fast
  61.13 % → 32.93 % [−28.20 pp]; Pro 34.92 % → 28.25 % [−6.67 pp]; tokens:
  Fast 1438 → 1491 [+53]; Pro 1472 → 1494 [+22]. Full per-dimension deltas
  in `phase2a/outputs/compare.md`. No composite score, no ranking, no
  priming effect claimed beyond the recorded deltas.
- **Tests:** `tests/test_exp004_phase1_dola_baselines.py` extended
  (msg2-style collect + verify accepts the prompt file as record; tamper
  after collection caught; compare produces real deltas); full suite green.

## Planned (not started) — current (2026-09-07, SODA Task 023)

Status categories are kept distinct:
- **Completed experiments:** EXP-001 (baseline, historical), EXP-002
  (post-hoc revision pilot, historical), **EXP-003 (generation-time lexical
  scaffolding) — COMPLETED AND CLOSED (Task 016)** with its final report at
  `experiments/exp003-scaffold/REPORT.md`: automatic evidence (Task 011),
  character-level orthographic audit (Task 015), and the decoded human
  sentence-level forced-choice results (Task 014 questionnaire answered by
  the participant). Headline: guidance (B/C/D) preferred over baseline A
  74 % vs. 26 %; D favored by both models; no composite score; the signals
  (human preference / resource coverage / orthographic sanity) are reported
  separately and diverge for ChatGPT-B. Nothing historical was recomputed.
- **QC layer completed (Task 015):** character-level orthographic sanity
  audit over all EXP-001/002/003 outputs (official ISV alphabet source,
  D-040/D-041). Audit-only — no text modified, no lexical/resource coverage
  number or comparison artifact changed; per-run reports are regenerated
  deterministically under each experiment's gitignored `outputs/`
  (`orthography_report.{json,md}`).
- **No further human-evaluation exercise** will be designed: EXP-003
  collected the planned human signal (D-042).
- **Planned experiments:** EXP-004 model screening — **Phase 1 EXECUTED and
  RECONCILED (Task 018, 2026-09-06)**: 19 collected runs, 18 intake-complete
  and evaluated (evidence table in `outputs/roster.md`); GLM 4.5
  failed/excluded per protocol. **Phase 2A (full-roster corpus priming)
  EXECUTED, COLLECTED, AUDITED AND EVALUATED (Task 021, 2026-09-07)** —
  20 primed runs evaluated (18 baseline-backed original configurations +
  2 exploratory Dola 3.8 runs without a baseline); primed-vs-baseline
  evidence in `phase2a/outputs/compare.md`; **Task 022 (2026-09-07)
  prepared the Phase-1 DIRECT baselines for the two exploratory Dola 3.8
  configurations** (canonical direct prompts
  `20-dola-3.8-fast.md`/`21-dola-3.8-pro.md`, plan rows
  `pending_manual_collection`, Dola p2a-primed rows wired via
  `link-baselines`) and **Task 023 (2026-09-07) executed + collected +
  evaluated them** — `compare` now reports the real within-Dola
  Phase 1 → Phase 2A deltas for runs 20/21 (canonical coverage: Fast
  38.87 % → 67.07 % [+28.20 pp]; Pro 65.08 % → 71.75 % [+6.67 pp]); Dola
  stays exploratory; no priming effect is claimed beyond the recorded
  deltas. Phase 2B documented as future work. Phase 2 guidance methods
  stay closed until Phase 1 is complete and reported.

Planned (not started):

- **Manual linguistic review** of the EXP-001 unresolved sample (Task 004
  artifacts; human-only, no automatic classification).
- **EXP-004 Phase 1 — practical model screening (EXECUTED — COLLECTED SET
  RECONCILED + EVALUATED, Task 018, 2026-09-06)**: design at
  `experiments/exp004-modelscreen/DESIGN.md` (Task
  013 design; Task 016 finalized the roster and protocol; Task 017 approved
  execution and prepared the kit; Task 018 audited/reconciled the author's
  19 collected sessions and ran intake/evaluation/orthography). Phase 1
  screens the practically available models on a **clean direct-translation
  baseline** (no scaffolding) under the practical access filter (D-036):
  usable via a web/chat interface, free access, enough practical free quota
  for at least one full story per day or every other day (not a one-time
  trial), practically usable by the project author. Planned roster:
  GPT-5.6 Luna thinking OFF, GPT-5.6 Luna thinking ON, GPT Interslavic
  Teacher custom GPT, Claude Sonnet 5, Gemini (only if it passes the
  free-access/quota criterion), DeepSeek V4 Pro DeepThink OFF, DeepSeek V4
  Pro DeepThink ON, Grok, Kimi, Qwen, GLM (if practical web access
  satisfies the filter). **Executed roster (actual):** Claude Sonnet 5
  Medium + max; DeepSeek V3 Instant + V3 Expert × DeepThink OFF/ON (the
  planned V4-Pro rows ran on the models the interface offered — no V4-Pro
  output); Qwen 3.8 Max Thinking/Fast + 3.7 Plus Thinking/Fast; Gemini 3.1
  Pro (ext. thinking ON) + 3.6 Flash (OFF/ON); GPT-5.6 Luna OFF/ON; ISV
  Teacher; Grok; Kimi K2.6 Instant; GLM 4.5 (**failed**, service-error
  artifact, excluded per protocol). Exclusions: Venice AI (not an
  independent model), local/self-hosted models (out of practical scope),
  Bielik (already-observed negative qualitative case — no new full baseline
  unless a methodological reason arises). Full recording, byte-for-byte
  collection (D-035), Task 008 two-tier evaluator unmodified, no manual
  word-by-word classification, no composite score, no human evaluation.
  **Result:** 18/19 runs intake `complete` and evaluated (usable) — evidence
  table `outputs/roster.md`; GLM 4.5 failed/excluded. After Phase 1 selects
  the strongest/practical models, Phase 2 tests the assistance methods
  systematically (1. direct translation; 2. lexical candidate guidance;
  3. multiple resource-supported alternatives; 4. POS/morphology guidance;
  5. grammar guidance; 6. lexical + morphology/grammar combinations;
  7. evaluator/repair loop) to identify the best model × method
  combination rather than a blind matrix. **Next:** Phase 1 report;
  Phase 2A corpus priming (full roster) is prepared and execution-ready
  (Task 019) — author executes the primed sessions externally, then
  collect/verify/evaluate/compare. Do not start further Phase 2 work
  before Phase 1 is complete and reported.
- **EXP-004 Phase 2A — full-roster corpus priming (PREPARED — NOT
  EXECUTED, Task 019, 2026-09-06; corpus revised to three authentic
  registers in Task 020, 2026-09-07)**: tests the core corpus-grounding
  hypothesis on ALL 18 Phase-1-usable configurations: does authentic ISV
  exposure immediately before translation change generation? Two
  conditions (control = Phase-1 baseline; corpus-primed = msg1 study of a
  three-register authentic corpus — narrative
  (`tuta-historija-excerpt.txt`, 4 820 B) / artistic-poetic
  (`album-ahoj-slovjani-artistic-isv.txt`, 9 407 B, Latin-only, verbatim
  repeats deduplicated, NOT normalized) / encyclopedic
  (`wiki-sadovnistvo-encyclopedic-isv.txt`, 44 101 B, authentic retrieved
  ISV Wikipedia article "Sadovničstvo", CC BY-SA 4.0) + msg2 same Polish
  story in one session); corpus id `phase2a-authentic-isv`, combined file
  58 459 B ≈8 200 tokens, sha256 `aaad28e4…`, identical for every model
  (the Task-019 corpus was the single 4 820 B "Tuta historija" excerpt,
  sha256 `413830fa…`); run ids `…__p2a-ctl|p2a-primed` linked to Phase-1
  baselines; contamination-controlled collection (3 anchors — one per
  register — all required in primed prefix, any in control rejected);
  per-dimension `compare` deltas (no composite score, no ranking). Kit +
  protocol: `experiments/exp004-modelscreen/phase2a/README.md` (DESIGN
  §13, D-046); deterministic builder `scripts/build_phase2a_corpus.py`.
  **No external LLM run exists yet.**
