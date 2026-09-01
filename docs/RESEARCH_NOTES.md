# Research Notes

Lightweight record for a potential future publication on LLM-assisted
translation of Interslavic (a low-resource constructed language). This file
captures research-relevant facts across experiments — questions, hypotheses,
methodology, quantitative results, negative results, limitations — without
replacing the experiment documents (`experiments/*/DESIGN.md`, `REPORT.md`) or
the SODA log (`docs/DECISIONS.md`, `docs/LESSONS.md`). It exists so that later
we can answer: *what did we test, why, what exactly did the model receive,
what happened, what did we learn.*

Created: 2026-09-01 (SODA Task 009). Updated whenever an experiment produces
research-relevant information. Negative results are preserved.

---

## 1. The methodological taxonomy (the space EXP-003 fills)

There are four distinguishable ways to use lexical resources in LLM
Interslavic generation. Keeping them distinct is itself a research result:

| Approach | Where tested | What the model receives |
|---|---|---|
| **Direct translation** | EXP-001 (7 models, baseline) | Polish source + plain translate instruction; no resource guidance |
| **Post-hoc lexical revision** | EXP-002 (pilot) | An existing LLM translation + table of supplied ISV alternatives for selected unresolved forms; model revises the whole document |
| **Generation-time lexical scaffolding** | EXP-003 (B/C — scaffold implemented, runs not yet executed) | Polish source + deterministic Polish→ISV lexical scaffold (vocabulary guidance only) |
| **Generation-time lexical + grammatical constraints** | EXP-003 (D — implemented, not yet executed) | Polish source + scaffold + alternatives + reliable ISV-side grammatical annotations |

The research hypothesis motivating EXP-003: vocabulary guidance *at generation
time* may give the LLM the resource-supported words while still letting it
build natural grammar and discourse — possibly superior to (1) unconstrained
translation and to (2) correcting an already-generated translation, because in
(2) the model's initial wrong vocabulary is already entrenched in the text.

## 2. EXP-001 — direct translation baseline (historical)

- Seven models on one Polish story (each condition a whole-story translation):
  ChatGPT, Gemini, Claude, DeepSeek, Bielik, Grok,
  GPTs "Interslavic — Medžuslovjansky Language Teacher".
- Key result: **canonical coverage** (A+B over lexical tokens) 55.5–79.8 %
  across models; unresolved forms (~1,050 unique across models) are mostly
  story content (names, topic vocabulary) plus lexical choices borrowed from
  other Slavic languages.
- Limitation recorded: the source file embeds an instruction line + markdown
  fences (preprocessing artifact); EXP-001 prompts are recorded as `unknown`
  (no prompt versions kept).

## 3. EXP-002 — post-hoc lexical revision (historical)

- Deterministic candidate generation for unresolved forms (canonical dict /
  orthographic variant / alternative resource / morphology-derived lemma /
  none), stratified pilot selection, complete-document revision prompt,
  external execution (no LLM API client in this project — D-007).
- Key results: 90 C→A/C→B resolutions; **12 A→C regressions**; B→C = 0;
  candidate usage statistics per form; a documented `interslavicfreq`
  discrepancy decomposed into three kinds (evaluator matching limits,
  morphology coverage, resource-layer differences).
- Lesson generalized (L-015): unique-form bookkeeping hides token-level
  regressions → token-aligned transition matrices are the regression standard.

## 4. EXP-003 — generation-time lexical scaffolding (implemented, Task 010; executed externally, intake + preliminary analysis in Task 011)

**Status update (Task 011):** the 12 external replies were registered,
verified and preliminarily analyzed. **8 of 12 runs (ChatGPT A–D, Claude A–D)
are complete translations and are quantitatively comparable. All 4 Bielik
runs are unusable as quantitative data** (2 truncated, 1 prompt paraphrase/
echo, 1 service error page) — see §4.9. The quantitative core of EXP-003 is
therefore 2 models × 4 conditions; Bielik is a qualitative observation for
this experiment. No methodology was changed; failures are preserved as data
(D-035).

### 4.1 Research question and hypotheses
See `experiments/exp003-scaffold/DESIGN.md` §2–§3. Summary:
- Primary: does a deterministic Polish→ISV lexical scaffold raise canonical /
  broader resource-supported coverage while preserving naturalness, vs
  unconstrained direct translation of the same source by the same model?
- H1/H2 directional (coverage gains); H3 regressions near zero; H4–H6
  two-sided (alternatives / grammatical annotations / naturalness are
  empirical questions; D is **not** assumed best).

### 4.2 Key design finding — the alignment resource already exists
- `basic.json` carries a **Polish translation column (`pl`)**:
  19,100 rows → 18,916 unique normalized Polish gloss keys.
- A reverse index Polish→ISV covers lemma vocabulary: `być→byti`, `się→sę`,
  `dobrze→dobro`, `pierwszy→pŕvy`, `dziś→[dnėś, tutdėnj, sego dnja]`,
  `tam→[tam, tamo, onamo, onde]`.
- **Measured on the actual story** (578 unique Polish forms):
  - 207 (36 %) direct reverse-index hits;
  - ~28 (~5 %) recovered by dictionary-verified suffix stripping
    (stem must re-look-up in the index);
  - residual 371 forms (64 %): ~54 name-like (pass-through) +
    **~317 genuinely inflected non-name forms** → handled by an explicit
    per-story curation table (human, committed, provenance-bearing).
- **Limitation, stated:** no Polish lemmatizer is a project dependency; Polish
  inflection is morphophonological (suppletion `był→być`, alternations
  `słów→słowo`), so rule-based recovery is bounded (~5 %). Curation is the
  honest cost for one story; a lemmatizer is a deferred, separately approved
  dependency for multi-story scale-up.

### 4.3 Scaffold-generation method decision
- The scaffold generator is **deterministic and contains no hidden LLM calls**.
  Rejected for EXP-003 v1: generation "from Polish lemmas" and "lemmas +
  grammatical features" (require unavailable Polish NLP) and any
  **LLM-assisted semantic mapping**, which would produce
  `Polish → LLM → scaffold → LLM → ISV` and mislabel the tested variable.
  If an LLM is ever used for disambiguation, it must be an explicitly
  documented experimental variable.
- Rationale: we want to know the effect of *the scaffold itself*; the
  experimental variable is the dictionary-derived vocabulary guidance.

### 4.4 Experimental conditions
A = direct baseline (no scaffold); B = scaffold, one canonical candidate;
C = + dictionary-supported alternatives; D = + reliable ISV-side grammatical
annotations (dictionary POS, verb aspect, a few generated example forms).
Nested information B ⊆ C ⊆ D; A is the disjoint control. All four conditions:
same source, same model, prompts byte-identical except condition content.

### 4.5 Evaluation design
- Task 008 two-tier evaluator: canonical coverage and broader
  resource-supported coverage reported side by side (never merged), plus
  unresolved rate, token-aligned A/B/C transitions, A→C and B→C regression
  lists, candidate usage/adoption, and an invented-forms proxy (new unresolved
  forms neither in A nor supplied).
- **No numerical naturalness score.** Naturalness is holistic human judgment
  on complete texts (blinded, preference-order rubric), recorded verbatim.
- Three dimensions kept separate: resource evidence / automatic metrics /
  human holistic judgment.

### 4.6 Planned scope
- Dataset: the existing Polish story (controlled continuation of EXP-001/002);
  one story cannot support generalization claims — a validation story is a
  later wave.
- Models (first wave): Claude, ChatGPT (strong translators, structured-prompt
  adherence) + Bielik (weakest EXP-001 coverage; stress case). Not based on
  the coverage ranking alone. GPTs ISV Teacher excluded from the main wave
  (unknown system prompt is a confound).
- External execution per the project's operator-interface convention
  (no LLM API client).

### 4.7 Expected quantitative outputs (to be preserved)
Per model: A/B/C/D canonical + broader coverage, unresolved rate, transition
matrix, regression lists, candidate usage, invented-forms proxy, human
preference ordering. **Negative results (scaffolding hurts / regressions /
unnatural outputs) are preserved and reported.**

### 4.8 Implementation (SODA Task 010) — the exact method that will be executed

Implementation-level methodology, recorded so a future paper can state
precisely what each model received and how the numbers were produced. Status:
**infrastructure ready; run execution external (Task 011: 8/12 complete).**

- **Scaffold generation is fully deterministic and free of LLM calls** (D-029).
  `scripts/build_exp003_scaffold.py` reads (a) the cleaned story-only source
  `input/source.txt`, (b) `basic.json` via a Polish→ISV reverse index over the
  `pl` column, (c) the committed per-story curation tables
  `curation/op-pl/{names,multiword,residual}.tsv`, (d) the prebuilt full-form
  lexicon for example forms. Per-sentence alignment order: **multiword →
  names → exact reverse-index hit → dictionary-verified lemma recovery
  (suffix stripping where the stem re-looks-up in the index) → curated
  residual → `[?]`** (D-031: the names table precedes the dictionary, e.g.
  `Międzyrzecze`). No timestamps in any artifact; two builds verified
  byte-identical.
- **Alignment limitations (stated).** No Polish lemmatizer is a dependency;
  Polish inflection is morphophonological (suppletion `był→być`, alternations
  `słów→słowo`). Rule-based recovery is bounded (~5 % of unique story forms);
  everything else is curated per surface form in `residual.tsv` (313 unique
  forms in this story), with `[?]` for the 3 forms with no defensible mapping.
  The curation tables are committed and provenance-bearing (D-032); they are
  story-specific human judgment, not a general resource.
- **Candidate provenance policy.** Every ISV candidate carries
  `{surface, pos, type, layer, source, kind, detail}`. Layers follow the
  design §7 hierarchy: `canonical` (basic.json row, `pl_gloss_exact` /
  `recovery`) → `orthographic_variant` (comma-separated second+ headword
  spellings) → `alternative_attestation` (isv.dic / interslavicfreq notes on
  the candidate) → historical (not present in this story). Parenthetical
  headword notes (`pozirati (na)`) are metadata, never surfaces (D-033).
  Weaker evidence is annotated, never promoted to canonical; no candidate is
  invented.
- **Condition definitions (what the prompt actually contains).** A: source +
  translate instruction only. B: + the rendered scaffold with exactly one
  canonical candidate per form. C: + all resource-supported alternatives
  (deterministic order, provenance shown). D: + grammatical annotations —
  dictionary POS, verb aspect, and a few generated example forms (verb
  infinitive / 1sg present / past m.sg from the prebuilt lexicon); no Polish
  morphological analysis, no full grammar engine (D-028). The scaffold is
  vocabulary guidance; prompts state the model remains responsible for word
  order, inflection, and natural grammar, and may depart from any supplied
  candidate.
- **Prompt-control policy.** The four prompts for one model are byte-identical
  except the condition block (scaffold B/C/D + two additive sentences for
  alternatives/grammar). No model-specific linguistic advice, no baseline
  scores, no model comparisons, no request for explanations; the expected
  output is the complete Interslavic story only. Model metadata
  (provider/model/version/generation date) is recorded as `unknown` when the
  Project Owner does not supply it (D-018/D-023); nothing is inferred.
- **Proper-name treatment.** Names are scaffolded as `[Name] (proper name —
  keep as-is)`, carry no candidates, are never deleted from the translation,
  and are excluded from coverage denominators only in **new, clearly-labelled
  name-excluded diagnostics** (historical metrics unchanged, D-030). The
  invented-forms analysis keeps a separate `proper_name_like` category.
- **Evaluation policy.** The Task 008 evaluator runs **unmodified**; canonical
  and broader resource-supported coverage are reported side by side and never
  merged (D-027). A/B/C transitions are token-aligned (LCS of lexical token
  sequences), with A→C/B→C regression lists and C→A/C→B resolutions.
  Candidate adoption is reported as a clearly-labelled **surface-level proxy**
  (an output form equal to a supplied surface, normalized); position-targeted
  adoption is not computable Polish→ISV without a translation model and is not
  claimed. Invented/non-supplied vocabulary is categorized
  (supplied / canonical-independently-generated / broader-resource-supported /
  unresolved / proper-name-like) and stated to be an analytical signal, not a
  correctness oracle. No composite quality score exists.
- **Reproducibility strategy.** Every planned run has a run id
  `<date>__<provider>__<model>__<version>__<condition>` in `outputs/plan.json`
  with prompt/source/scaffold SHA-256s; `collect` stores raw output
  byte-for-byte, never overwrites, and records output SHA-256, model
  metadata, evaluator commit, dictionary manifest, lexicon hash, scaffold
  generator commit, and curation-table hashes; `verify_exp003_runs.py` checks
  everything including tamper detection. Failed/empty runs are preserved and
  documented (Bielik's context window is the known risk — D-023/D-028).
- **Human evaluation is holistic and blinded.** `compare_exp003.py` writes
  complete-text pairs (`comparison/human_review.md`) with blinded labels and a
  separate `human_review_key.json`; automatic metrics stay hidden during the
  initial naturalness/preference judgment.

### 4.9 Intake, integrity, and preliminary quantitative results (SODA Task 011, 2026-09-01)

**Model conditions actually used (recorded in run metadata as supplied by the
Project Owner; nothing inferred):** ChatGPT = GPT-5.6 Luna, thinking OFF;
Claude = Sonnet 5 Medium (no generation parameters supplied → `unknown`);
Bielik = Bielik 3.0 (provider not supplied → `unknown`). DeepSeek
(DeepSeek-V4-Pro, DeepThink ON) is outside EXP-003's design and was not used.

**Output integrity.** All 12 replies were inspected for structure, truncation,
commentary and format anomalies before any evaluation (no linguistic judgment;
the evaluator quantifies lexical evidence later). All were registered
byte-for-byte through `run_exp003_pilot.py collect` (SHA-256 in meta.json;
temp == collected verified byte-identical; nothing overwritten, no original
`.txt` modified). `verify_exp003_runs.py`: 12/12 OK. Full test suite 77 green.

**Completeness matrix (structure only).** ChatGPT and Claude replies are
complete in all four conditions: all story sections (Prolog + 7 acts +
Epilog), end marker (`KONEC`/`KONĖC`), no preamble/commentary, no format
anomalies; 9.9–10.4 KB. Bielik: A = truncated after ≈2.5 acts (mid-sentence),
B = truncated during act 3 (mid-word `Š`), C = Croatian paraphrase/echo of the
prompt scaffold (no translation; ≈6 % of the prompt length), D = service
error page (`Przepraszamy, Bielik ma chwilowe problemy techniczne`). Bielik A/B
also show Croatian- / Czech-flavored orthography (observed fact, quantified by
the evaluator's coverage). Bielik A/B were registered
`collected_partial_output`, C/D `failed_external_output` (D-035).

**Evaluator results (Task 008 evaluator, unmodified; lexical-token
denominators).** 10 processable runs were evaluated; Bielik C/D were recorded
as not evaluable rather than producing a fabricated number.

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
| Bielik A (partial text) | 750 | 57.07 % | 78.67 % | 42.93 % |
| Bielik B (partial text) | 674 | 38.81 % | 49.19 % | 61.19 % |

**Comparison highlights (8 complete runs; `compare_exp003.py`; no composite
score, no ranking).**

- **B vs A (scaffold effect):** canonical +9.45 pp (ChatGPT), +3.16 pp
  (Claude). Broader: +3.75 pp (ChatGPT), −1.08 pp (Claude) — ChatGPT's B
  raises both tiers; Claude's B raises canonical coverage at a small cost in
  alternative-attested forms.
- **C vs B (alternatives):** −0.90 pp (ChatGPT), −3.56 pp (Claude) canonical.
  Supplying alternatives did not beat the single canonical candidate for
  either model; Claude's C is even below its own unconstrained baseline A
  (−0.40 pp).
- **D vs C / D vs B (grammar info):** Claude D is the strongest run of the set
  (+10.21 pp vs its C, +6.65 pp vs its B, +9.81 pp vs its A; broader 92.02 %);
  ChatGPT D does not add over B (−1.68 pp) or C (−0.78 pp). The D effect is
  model-dependent in this dataset.
- **Within-condition model deltas:** A ≈ tied (ChatGPT 76.27 vs Claude
  75.81); B/C ChatGPT ahead by 6.8–9.4 pp canonical; D Claude ahead (+1.58 pp).
- **Name-excluded diagnostics** reproduce the same ordering (names do not
  distort the comparison). **Supplied-candidate adoption proxy** (667 supplied
  surfaces): ChatGPT A 112 → B 195 → C 195 → D 180; Claude A 111 → B 131 →
  C 139 → D 196 present in output. **Invented (non-supplied, non-name)
  unresolved forms** fall with scaffold use: ChatGPT A 139 → B 85; Claude
  A 155 → D 82.
- **Transition bookkeeping** is the designed token-aligned evidence (e.g.
  ChatGPT B→C A→C regressions `byl→měl`, `dlja→dla`; Claude B→C `ako→jesli`
  ×7) — evidence for the analysis, not linguistic verdicts.

**Bielik-specific findings (treated as data, not hidden).** Observed facts:
all 4 Bielik replies fail to deliver a complete translation; 2/4 truncate at
≈40 % of the story with no end marker; 1/4 is a prompt paraphrase/echo; 1/4 is
a service error page. Quantified: Bielik partial lexical tokens ≈750/674 vs
≈1,475–1,533 for complete runs; partial-text canonical coverage 57.1 % / 38.8 %
(non-comparable to complete runs). Possible explanation (hypothesis only, not
proven by the artifacts): Bielik's smaller effective context truncated
generation and the model then produced non-task output; the artifacts do not
themselves prove the cause. No prompt was shortened and Bielik was not rerun.

**Answerable validity questions (evidence-based; full A–H answers in
`docs/EXPERIMENTS.md` § EXP-003).** (A) 8/12 runs executed the intended
conditions; Bielik C/D produced no translation, A/B truncated. (B) Only 8/12
are sufficiently complete for quantitative comparison. (C) Bielik failed to
follow the experimental instructions in 3 of 4 conditions (A/B partial, C
echo); ChatGPT and Claude complied in all 4. (D) Bielik C (paraphrase/echo)
and D (error page) are unexpected behaviors; A/B truncation is systematic. (E)
No scaffold-side unwanted effect is measurable from these artifacts: B
improves coverage for both models and the residual → `[?]`/name handling did
not produce anomalies in the outputs. (F) Yes — alternatives (C) never beat
the single-candidate scaffold (B) on canonical coverage, and Claude C is
below its own baseline A. (G) D's value is model-dependent and not yet
uniformly measurable: Claude D strongly outperforms its C, ChatGPT D does
not. (H) **No — Bielik is not usable as a quantitative participant in this
experiment.** Its results are recorded as qualitative data; a second model
cohort could repeat the experiment later if desired, but EXP-004 must not
start from this dataset.

**Methodological consequences.** (1) The quantitative core of EXP-003 is the
8 complete runs (2 models × 4 conditions); coverage deltas above are
preliminary, not a verdict, and naturalness remains a separate (human)
question — higher coverage is resource-supported vocabulary, not "better
Interslavic". (2) Completeness gating is now part of run intake (D-035,
L-027): structural inspection before evaluation, documented statuses, failed
runs preserved. (3) The scaffold worked at generation time for both models
(B > A), consistent with the EXP-003 hypothesis direction; the
alternatives/grammar increments split by model.

## 5. Standing methodological rules learned so far (research-relevant)

- Token-aligned transition matrices, not unique-form counts, are the
  regression standard (EXP-002; L-015).
- The evaluator answers *canonical resource coverage*, not "is this valid
  Interslavic"; two-tier metrics (canonical / broader) must stay side by side
  (Task 007/008; L-016).
- An evidence layer can be added without changing classification semantics
  (Task 008; L-021).
- Per-language translation columns in the canonical dictionary are a
  reverse-indexable resource — measure coverage before proposing NLP
  infrastructure (Task 009; L-022).
- An experimental-variable generator (e.g. the scaffold) must not hide LLM
  calls (Task 009; L-023).
- External-interface constraints (no API client, manual copy/paste operator
  prompts) are part of the method, recorded per run (D-007, D-024).
- Dictionary headword fields can carry embedded annotations (parenthetical
  government/domain notes, comma-separated orthographic variants); surfaces
  handed to an LLM must be clean, with annotations preserved as provenance
  metadata (Task 010; L-024, D-033).
- Deterministic candidate ordering is not automatically the best-sense
  ordering; when a single candidate is shown, ordering is a research decision
  to be reviewed and documented (Task 010; L-026, D-034).
- Externally produced runs must pass a structural completeness check
  (section markers, end markers, head/tail, byte size vs complete peers)
  before evaluation; failed/partial runs are preserved with a documented
  status and excluded from the quantitative comparison, never silently
  rerun or repaired (Task 011; D-035, L-027).
- A model's failure to complete a condition is experimental data: distinguish
  model-capability, prompt/context, scaffold-design, evaluator, resource, and
  actual-effect explanations, and never collapse them (Task 011; §4.9).

## 6. Open questions for future work

- Does generation-time scaffolding beat post-hoc revision on the *same*
  unresolved forms? (EXP-002 candidate data vs EXP-003 results — a direct
  comparison is possible because both use the same source and evaluator.)
- Does the scaffold effect persist on a second story (out-of-domain)?
- Do grammatical annotations (D) help any model, or only some? (Task 011:
  D strongly helped Claude, not ChatGPT, on this story — open whether that
  splits by model or by other factors.)
- Is the 12 A→C regression class from EXP-002 reproduced, avoided, or changed
  by generation-time guidance?
- Why did alternatives (C) fail to beat the single-candidate scaffold (B) for
  both models on this dataset — prompt load, candidate competition, or
  condition design?
- What does the blinded human judgment say about naturalness across the
  8 complete runs (the automatic-metric ordering is not a naturalness
  ordering)?
