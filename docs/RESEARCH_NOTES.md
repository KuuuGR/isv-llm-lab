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
  the DESIGN §11 review document (`comparison/human_review.md`) for the 8
  complete runs: two neutral sets ("Set 1"/"Set 2"), per-set deterministic
  randomized "Version 1..4" labels (fixed seed, reproducible; the model is
  never named in the document), the four holistic questions, a
  preference-ordering template, a clearly separated post-unblinding section
  (scaffold-constraint question, B/C/D only), and a recording checklist;
  automatic metrics stay hidden until the initial judgment is recorded. The
  mapping lives in `human_review_key.json` (set → model → condition → version
  → run id). See §4.10.

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

### 4.10 Blinded holistic human naturalness review — cohort prepared (SODA Task 012, 2026-09-01); **SUPERSEDED (Task 014)**

> **Supersession note (2026-09-05).** The Project Owner attempted this
> holistic complete-text review and found the format too cognitively
> demanding (comparing four complete long translations → unreliable
> subjective judgments). This is a format problem, not a result about any
> condition; **no holistic human result was obtained and none is recorded or
> inferred**. The holistic artifact is preserved as a historical/provisional
> review design (superseded banner in `human_review.md`). The primary
> EXP-003 human-evaluation method is now the sentence-level forced-choice
> test described in §4.12 (D-038).

The human-review artifact is prepared for the Project Owner; no answers exist
yet (they are recorded verbatim when the review is performed).

- **Review cohort: 8 runs.** ChatGPT A/B/C/D and Claude A/B/C/D — exactly the
  complete, quantitatively usable runs. **Bielik is excluded from the
  quantitative human comparison** because all four Bielik runs were
  incomplete/failed (Task 011); its outputs remain preserved as qualitative
  experimental artifacts. DeepSeek and Grok were never part of EXP-003.
- **Blinding.** The review document (`experiments/exp003-scaffold/comparison/
  human_review.md`) shows two neutral sets ("Set 1", "Set 2") with per-set
  labels "Version 1..4"; conditions A/B/C/D are mapped to the versions by a
  **deterministic seeded shuffle** (seed `20260901` in `compare_exp003.py`),
  so presentation order is reproducible and never alphabetical. The model
  behind each set and the version→condition mapping are recorded only in
  `human_review_key.json`.
- **Metrics withheld.** No automatic metric (canonical/broader coverage,
  unresolved counts, regressions, candidate usage) and no model identity
  appears in the review document before the initial holistic judgment. The
  four DESIGN §11 questions + preference ordering are answered first; the
  scaffold-constraint question (B/C/D only) is in a clearly separated PART 2,
  answered only after unblinding.
- **Not collapsed.** The human naturalness/preference judgment is a separate
  qualitative evidence layer; it is never converted into a numerical quality
  score and never merged with evaluator coverage. Recording keeps the date,
  verbatim answers, presentation order, randomized mapping, and the
  before/after-unblinding split.

### 4.11 EXP-004 model screening — preparation (SODA Task 013, 2026-09-05)

**Status: design only. Not approved, not executed, no LLM called.** Design:
`experiments/exp004-modelscreen/DESIGN.md`. The EXP-003 human review remains
open and untouched; nothing here assumes or claims its outcome.

- **Purpose.** The next major phase is model screening: determine which LLMs
  are practically useful for Polish → Medžuslovjansky translation under a
  real-world workflow (web/chat interface, free access sufficient for ~1 full
  story per day), then (later) which forms of external deterministic
  linguistic guidance improve those models.
- **Central hypothesis (unchanged, still a hypothesis):** LLMs can produce
  plausible-looking Slavic text from learned patterns without reliably
  consulting or reproducing Medžuslovjansky vocabulary and morphology;
  supplying deterministic linguistic resources may improve quality. Many
  assistance strategies are candidates; none is assumed to win (D-037).
- **Two phases (D-037).** Phase A = model screening: one identical story, one
  equivalent no-guidance instruction per roster row; outputs are a per-model
  access verdict and versioned baseline numbers (canonical/broader coverage)
  under full recording. Phase B = guidance-method experiments on Phase-A
  models, scoped from Phase A evidence (headroom, access) plus the pending
  EXP-003 report. Screening and method experiments are deliberately separate.
- **Access filter (D-036).** Main-roster criterion: normal-user web/chat use,
  free access sufficient for ~1 story/day, identifiable model/version/
  settings. Local deployment, paid-only ordinary use, and one-off trial
  credits are out of scope. Venice AI is a platform, not an independent model;
  Mistral is not assumed available; Bielik remains a preserved qualitative
  negative result (its free-web access failed this exact task in EXP-003) and
  no new quantitative conclusion about it is invented.
- **Roster (candidate; access to confirm):** GPT-5.6 Luna thinking OFF and ON;
  the custom GPT "Interslavic / Medžuslovjansky Language Teacher" (separate
  row; internal system prompt unknown — D-018 confound, exploratory);
  Claude Sonnet 5; Gemini; DeepSeek-V4-Pro DeepThink OFF and ON; Grok; Kimi;
  Qwen; GLM (conditional on web access). Versions/settings are recorded per
  run; variant rows (thinking toggles) are explicit conditions.
- **Protocol essentials.** Byte-identical story-only source (same as EXP-003);
  equivalent base instruction; no guidance in Phase A; byte-for-byte
  collection with SHA-256, documented statuses (D-035), completeness gate
  before evaluation (L-027); context/window limitations and free-access
  observations recorded; Task 008 two-tier evaluator unmodified, metrics not
  redefined; no manual word-by-word classification; holistic human review is
  not part of Phase A.
- **Recording decision:** selection criteria and roster are fixed in the
  design *before* execution (L-028) so the model set is not rationalized post
  hoc.

### 4.12 Sentence-level forced-choice human test — prepared (SODA Task 014, 2026-09-05)

**Status: ANSWERED and analyzed (Task 016, 2026-09-05) — results in §4.14
and `experiments/exp003-scaffold/REPORT.md`.** This is the ONE planned
human-evaluation exercise for EXP-003 (D-038). Participant document:
`experiments/exp003-scaffold/comparison/sentence_review.md` (self-contained);
private answer key: `comparison/sentence_review_key.json`. Decoded results:
`comparison/sentence_review_results.{json,md}` (no result existed until the
participant answered all 100 questions).

- **Why the format changed.** The Project Owner found the holistic
  complete-text comparison (four full translations per model) too cognitively
  demanding; that is a methodological property of the format, and no holistic
  result was recorded (supersession note in §4.10).
- **One question = one source sentence.** A Polish source sentence from the
  original story, shown together with the corresponding sentence from each of
  the four EXP-003 conditions (A/B/C/D) of the same model. The four
  Interslavic versions are displayed as neutral "Version 1..4" in a
  per-question deterministic randomized order (fixed seed `20260905`,
  reproducible; alphabetical order rejected). The Project Owner ticks the
  version that sounds most natural as Medžuslovjansky (best-choice only; no
  full ranking and no worst choice — a fast, reliable best-choice signal).
- **Bias control.** The instructions explicitly ask for a holistic sentence
  impression, say that unfamiliar forms may appear, and instruct the
  reviewer NOT to verify individual words against a dictionary (the reviewer
  is a Polish native with Russian/Czech exposure). No model names, no A/B/C/D
  condition labels, no automatic metrics, and no hints appear in the
  participant document.
- **Sampling (all from existing EXP-003 data).** Monotonic length-based DP
  alignment (1:1/1:2/2:1 + skips) between the source sentence list and each
  condition output; the pool keeps only source sentences with a 1:1 anchor in
  all four conditions of a model whose four versions pass an all-pairs
  cross-run token-overlap floor (same content), have ≥ 4 words (no
  truncation fragments), and are not token-identical across all four
  conditions. ~50 questions per model are drawn by deterministic stratified
  sampling (story section × dialogue/narration, even spacing); fully
  distinct-version questions are preferred. Real pools on 2026-09-05:
  99 (ChatGPT) and 101 (Claude) aligned quadruples → 100 questions (50+50),
  covering all nine story sections with 35 dialogue items. Filters and pool
  sizes are recorded in the key (D-039).
- **Answer key and analysis.** `sentence_review_key.json` records per
  question: model, story section, source-sentence index + text, dialogue
  flag, run ids, version texts, the display order (Version label → A/B/C/D),
  and the seed + document hashes. Later analysis can compute preference
  counts by displayed version, mapped back to A/B/C/D, preference rates,
  results by model and by condition, and uncertainty/sample-size
  information. No composite quality score combining human preference with
  evaluator coverage is created.

### 4.13 Character-level orthographic sanity audit — added (SODA Task 015, 2026-09-05)

**Purpose.** One more automated quality-control layer run over ALL generated
translation outputs of EXP-001, EXP-002 and EXP-003 before EXP-003 closure:
a deterministic, character-level audit that catches a basic orthographic
class of problem the token/word-level lexical evaluator cannot see — a
translation containing Cyrillic letters or source-language-specific Latin
letters (e.g. Polish `ł`, Czech `ů`/`ř`).

**Authoritative alphabet source.** The letter inventory is taken verbatim
from the Interslavic project's own definition, NOT derived from this
project's dictionaries, lexicons, Hunspell, or model outputs:

> https://steen.free.fr/interslavic/orthography.html — "Orthography
> (Pravopisanje)", fetched 2026-09-05.

The page defines (a) the standard Latin alphabet of 27 letters — all of
a–z except `q w x`, plus `č š ž ě` (digraphs `dž lj nj` add no letters) —
and (b) the optional etymological alphabet: `ę ų å ė ȯ ć đ ĺ ń ŕ ś ź`, with
page-sanctioned alternative graphemes `ť ď` (for `t́ d́`), `ľ` (for `ĺ`),
`ň` (for `ń`), `ř` (for `ŕ`), `è ò` (for `ė ȯ`), and the `t́`/`d́` spellings
via combining acute. The validator accepts exactly this union (both cases);
`q w x` and every other Latin letter (e.g. `á é í ý ú`, macron forms like
`ē`, OCS-style `ǫ` where ISV uses `ų`, `ü`) are outside the inventory.

**Exact validation policy (D-040).** For each character the checker reports
one of: allowed ISV letter; Cyrillic letter (any Cyrillic block — all three
experiments requested Latin-script output, so any Cyrillic letter is
unexpected); Polish-specific letter `ą ł ó ż` (lower/upper) — deliberately
NOT `ć ę ń ś ź`, which are valid etymological ISV letters and therefore
allowed; other Latin letter outside the inventory; other-script letter;
or an unexpected non-letter. Non-letters are never "alphabet errors":
whitespace (any Unicode space), ASCII digits `0–9`, and an explicit prose
punctuation set (`. , ; : ! ? … – — - ( ) « » „ “ ” " " ' ' ' ‘ ’`), which
was cross-checked against the actual corpus documents, are accepted; any
other non-letter (control characters, emoji, markdown/formatting glyphs
such as `# *`, scaffold glyphs like `→ ‡`) is reported as a formatting/symbol
note, never as an alphabet violation. Per output the audit reports total
Unicode characters, allowed letters, accepted non-letters, characters
outside the accepted inventory, and the outside-inventory breakdown
(Cyrillic / Polish-specific / other Latin / other script / unexpected
non-letter), plus every distinct unexpected character with its frequency
and the 1-based line numbers where it occurs. The audit NEVER modifies,
normalizes, transliterates, or repairs text.

**Audit-only; historical scores untouched.** The check is a separate quality
dimension (D-041). `resource-grounded lexical/morphological coverage`
answers "is a token/word grounded in the canonical/broader resources";
`character-level orthographic sanity` answers "does the character stream
stay inside the ISV alphabet". They are reported side by side, never
combined, and no existing lexical coverage score, A/B/C classification, or
EXP-001/002/003 comparison artifact was recomputed or changed. Full per-file
reports are regenerated deterministically by `scripts/check_orthography.py`
into each experiment's gitignored `outputs/orthography_report.{json,md}`;
implementation `src/isv_eval/orthography.py`; tests `tests/test_orthography.py`.

**Results across the existing outputs** (2026-09-05; totals over the 7
EXP-001, 7 EXP-002, 12 EXP-003 run files; per-run detail in the reports):

| Experiment | files | total chars | outside inventory | Cyrillic | Polish-spec. | other Latin | other script | non-letter |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| EXP-001 | 7 | 66 007 | 267 | 31 | 46 | 48 | 0 | 142 |
| EXP-002 | 7 | 65 410 | 309 | 67 | 45 | 55 | 0 | 142 |
| EXP-003 | 12 | 87 797 | 1 297 | 98 | 342 | 508 | 0 | 349 |

Every EXP-003 condition file has at least one character outside the accepted
inventory; the cleanest files are ChatGPT-A (34 outside of ~8 000 chars) and
Bielik-A (14). No EXP-001/002/003 file contains script characters other than
Latin or Cyrillic; there are no control characters.

**Anomalies found.** (1) **Cyrillic in Latin-script output** — EXP-001 Claude
(23) and EXP-002 Claude (59, incl. `М е ж ь` in headings), EXP-003 Claude
a–d (9–45 each), EXP-003 ChatGPT-B (3), Bielik-A (2), plus 1–4 stray
Cyrillic letters in EXP-001/002 DeepSeek, gpt-isvt, Bielik. Notably
EXP-003 Claude-C inserts Cyrillic *inside* Latin words (`Може`, `ь` inside
`četyrьnadsęt`, `vęzь`, `prěvь`; `я` inside `neясno`). (2) **Polish
orthography in proper names** — `ł`/`w` occur almost exclusively in the
story's Polish names `Bronisława`/`Przemysława` kept verbatim (EXP-003: 300
`ł`; all 269 `w` are inside that name); a minority of `ł` are genuine
Polish-flavored verb forms (`mečtała`, `pokušała`). (3) **Czech/Slovak
contamination** — EXP-003 ChatGPT a–d and Claude use accented Czech/Slovak
long vowels (`myslíš`, `musím`, `právě`, `původu`); Bielik-B's truncated
output drifts into largely Czech lexis (`lidé`, `může`, `být`, `odpovídal`,
`která`), the single largest outside-inventory file (214). (4)
**Non-ISV diacritics** — Gemini EXP-001/002 writes `dējstvitelno` (macron
`ē`, ISV would use `ě`), gpt-isvt writes `Myslǫ` (OCS-style `ǫ`; ISV uses
`ų`). (5) **Markdown formatting in EXP-001/002 outputs** — `#` (50) and `*`
(92) heading/bold markers across Claude/Gemini/ChatGPT/GPT-ISVT/Grok runs;
EXP-003 Bielik-C echoes the operator prompt, contributing `→ ‡ [ ]`
(349 non-letter surprises). These formatting notes are reported as
non-letter surprises, not alphabet errors. As required, a character anomaly
is NOT treated as proof that a whole translation is linguistically invalid —
it is one independent signal, analyzed against lexical coverage later.

### 4.14 EXP-003 results — human test decoded, combined with automated evidence, experiment closed (SODA Task 016, 2026-09-05)

The participant answered all 100 forced-choice questions. Decoding
(`scripts/analyze_exp003_sentence_review.py`, D-043) validated the completed
document against the private key (100 questions, original order, one tick
each, 399/400 Version texts byte-identical) and recorded two provenance
notes: Q58 answered as `[x ]` (stray-whitespace encoding) and Q67 Version 2
(non-chosen, condition D) corrupted during the answering session
(`sę, že` → `, žesę`, same character multiset) — neither affects decoding,
and the document was not modified or regenerated. Full write-up: the
experiment's final report `experiments/exp003-scaffold/REPORT.md`; decoded
artifacts `comparison/sentence_review_results.{json,md}`.

- **Human preference (n = 100; 50 per model).** Choices per displayed
  Version 1–4: 25 / 29 / 22 / 24 (no position bias). Per condition: A 26 %
  (26), B 16 % (16), C 19 % (19), **D 39 % (39)**; χ²(3) vs. uniform =
  12.56, p ≈ 0.006. Per model: ChatGPT A 26 % / B 12 % / C 26 % / D 36 %
  (χ² p ≈ 0.12); Claude A 26 % / B 20 % / C 12 % / **D 42 %** (χ² p ≈ 0.02).
  Guidance vs. baseline: **B+C+D = 74 % vs. A = 26 % — identical for both
  models**. The baseline was chosen at ≈ chance (26 % vs. 25 % expected).
- **Automated evidence (Task 011, unchanged).** Coverage and preference
  agree for Claude at the extremes (D: canonical 85.6 / broader 92.0 /
  unresolved 14.4 %, human favorite 42 %; C: 75.4 / 84.5 / 24.6 %, human
  least favorite 12 %) but diverge for ChatGPT: B is the automated best
  (85.7 / 90.8 / 14.3 %, orthographically cleanest) yet the human least
  preferred (12 %), while D (84.0 / 88.8, not the coverage best) is the
  human favorite (36 %). Exploratory Spearman over the 8 condition points:
  share vs. broader +0.49, canonical +0.23, unresolved −0.23, orthographic
  outside −0.20 (n = 8 — descriptive only, no inference).
- **Orthographic sanity (Task 015) vs. preference.** Raw condition-level
  Polish/other-Latin counts are dominated by the story names kept verbatim
  (`Bronisława`/`Przemysława` → ł/w), so a non-name refinement was added to
  the decoder (letters inside name tokens excluded). The refined signal
  tracks the Claude extremes only: C has by far the most non-name
  contamination (70; Cyrillic 45 incl. intra-word) and is the human least
  favorite; D the least (11) and the human favorite. For ChatGPT, D is the
  favorite but not the cleanest (non-name 16 vs. B 7), so orthography does
  not explain ChatGPT's preference.
- **No composite score; separate signals (D-042).** Human preference,
  resource coverage, orthographic sanity, and linguistic correctness remain
  four separate constructs; none is ground truth, and the divergence for
  ChatGPT-B is the key caution against ranking conditions by coverage alone
  (L-033).
- **One verbatim participant comment** (Q7, vocabulary uncertainty, not a
  linguistic annotation) preserved as qualitative provenance.
- **EXP-003 is closed.** The experiment supports, on this story with this
  participant: guidance preferred over baseline ~3:1; D favored for both
  models; coverage gains for ChatGPT (all conditions) and Claude (D). It
  does not support: general claims beyond this pilot, coverage-based
  naturalness claims, any composite ranking, or any claim about Bielik.
  Limitations: one story, one non-expert participant, sentence-sample
  forced choice, run-level vs. sentence-level comparison only, the two
  provenance artifacts, exploratory statistics only.

## 5. Standing methodological rules learned so far (research-relevant)

- The letter inventory for a constructed-language output audit comes from the
  language community's own authoritative definition (the official
  Interslavic orthography page), never inferred from this project's
  dictionaries, resources, or model outputs (Task 015; D-040, L-031).
- Character-level orthographic sanity is a quality dimension separate from
  resource-grounded lexical/morphological coverage; both are reported side
  by side and never combined, and an audit layer never rewrites or repairs
  text nor recomputes historical scores (Task 015; D-041, L-031).
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
- Human-evaluation formats must be workload-pre-tested with the intended
  reviewer; a format that exceeds working memory (e.g. holistic comparison of
  several full texts) is a methodological problem, not a result about the
  conditions — replace the measurement, preserve the old artifact as
  superseded, and record that no result was obtained (Task 014; D-038,
  L-029).
- Pairing items across independently formatted documents (e.g. the same
  source sentence across condition outputs) must be a deterministic,
  content-checked function (monotonic alignment + cross-run overlap floor),
  never blind indexing or hand pairing (Task 014; D-039, L-030).
- A completed questionnaire is provenance: validate it against the private
  key (structure, tick counts, Version-text identity) before decoding; abort
  on structural damage; record answer-encoding and text artifacts (e.g. `[x ]`,
  an accidental transposition in a non-chosen option) as provenance notes;
  never regenerate, repair, or modify the completed document (Task 016;
  D-043, L-032).
- Automated-best is not human-preferred: resource coverage, orthographic
  sanity, and human naturalness are separate signals that can diverge within
  one model (EXP-003 ChatGPT-B is coverage-best but human-least-preferred;
  D is human-favorite for both models); report them side by side, never as a
  composite score (Task 016; D-042, L-033).

## 6. Open questions for future work

- Does generation-time scaffolding beat post-hoc revision on the *same*
  unresolved forms? (EXP-002 candidate data vs EXP-003 results — a direct
  comparison is possible because both use the same source and evaluator.)
- EXP-003 (one story, one participant) showed guidance preferred over
  baseline (74 % vs. 26 %) and condition D favored by both models, but
  ChatGPT-B was coverage-best yet human-least-preferred: is the
  coverage-vs-naturalness divergence a model property, a condition-design
  property (D's grammar annotations changing wording the reader preferred),
  or an artifact of one participant? What would a second participant or a
  second story show?
- Does the scaffold effect persist on a second story (out-of-domain)?
- Do grammatical annotations (D) help any model, or only some? (Task 011:
  D strongly helped Claude, not ChatGPT, on this story — open whether that
  splits by model or by other factors.)
- Is the 12 A→C regression class from EXP-002 reproduced, avoided, or changed
  by generation-time guidance?
- Why did alternatives (C) fail to beat the single-candidate scaffold (B) for
  both models on this dataset — prompt load, candidate competition, or
  condition design? (Human preference mirrors the coverage result for B vs C
  only in part: for Claude, C is the human least favorite too.)
- **Answered by Task 016:** the human test showed guidance (B/C/D) preferred
  over baseline A (74 % vs. 26 %), D the favorite for both models (ChatGPT
  36 %, Claude 42 %), with no display-position bias; per-condition and
  per-model tables in §4.14 and `experiments/exp003-scaffold/REPORT.md`.
- How do character-level anomalies (Cyrillic in Latin output, Polish/Czech
  letter contamination, non-ISV diacritics) relate to lexical/resource
  coverage: do files with more outside-inventory characters also show lower
  canonical or broader coverage, or are the two dimensions independent
  (Task 015 metrics are now available per run for exactly this analysis)?
  First Task 016 look (condition level, n = 8): the refined non-name
  orthographic signal tracks human preference only at the Claude extremes
  (C dirtiest → least preferred; D cleanest → most preferred), and does not
  explain ChatGPT's preference for D over the cleaner B.
- Which models pass the practical access filter, and how do their
  versioned no-guidance baselines on the canonical story compare (EXP-004
  Phase A)? How large is each model's headroom (unresolved rate) before
  guidance-method experiments are scoped to it?
