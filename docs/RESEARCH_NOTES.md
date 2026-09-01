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
| **Generation-time lexical scaffolding** | EXP-003 (designed, B/C) | Polish source + deterministic Polish→ISV lexical scaffold (vocabulary guidance only) |
| **Generation-time lexical + grammatical constraints** | EXP-003 (designed, D) | Polish source + scaffold + alternatives + reliable ISV-side grammatical annotations |

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

## 4. EXP-003 — generation-time lexical scaffolding (design, Task 009)

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

## 6. Open questions for future work

- Does generation-time scaffolding beat post-hoc revision on the *same*
  unresolved forms? (EXP-002 candidate data vs EXP-003 results — a direct
  comparison is possible because both use the same source and evaluator.)
- Does the scaffold effect persist on a second story (out-of-domain)?
- Do grammatical annotations (D) help any model, or only some?
- Is the 12 A→C regression class from EXP-002 reproduced, avoided, or changed
  by generation-time guidance?
