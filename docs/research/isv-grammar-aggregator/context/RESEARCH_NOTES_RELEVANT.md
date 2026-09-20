# Curated extract — Research Notes (selected sections)

> **Type:** curated extract (original wording preserved; not a rewrite).
> **Canonical source:** `docs/RESEARCH_NOTES.md`
> **Extraction date:** 2026-09-20
> **Included line ranges (1-indexed):** 17–34, 72–128, 1289–1386
> **Note:** Includes methodological taxonomy, EXP-003 RQ/design core, and standing methodological rules; omits full EXP-004 narrative results.
> This extract is for the Grammar Aggregator working package only.
> The canonical file remains authoritative; do not silently rewrite policy language.

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
- For any multi-model generation round, pre-register the completeness gate
  from observed complete peers BEFORE execution (e.g. byte floor = 0.60 ×
  source size, final-line end marker, name coverage, head sanity) and encode
  it in the runner; verdicts (complete/partial/failed) are data, and
  evaluation of `failed` intakes is refused (Task 017; D-044, L-034).
- When screening models for practical use, record the practical-access
  verdict (free quota sufficient for ≥ 1 full task/day or every other day,
  not a one-time trial) as part of each run's metadata at execution time —
  do not assume an advertised free tier is usable (Task 017; D-036).
- With one paired generation per configuration, an observed Phase-1 →
  Phase-2A delta is not a measured "priming effect": it also contains
  stochastic generation variation, model/interface behaviour,
  configuration differences and baseline dependence. Report deltas with
  that decomposition caveat, label exploratory paired tests as
  exploratory (n = 1 per condition), and always check the descriptive
  correlation between the baseline level and the change before reading a
  large delta (EXP-004 Task-024: ρ ≈ −0.86 canonical / −0.84 broader over
  the original 18; D-051, L-041).
- Research analysis of a completed experiment is deterministic,
  read-only, and free of composite/winner scores: dimensions stay
  separate, "large observed change" ≠ "evidence of a large causal
  effect", exploratory additions (Dola) keep their status everywhere, and
  interpretation is stated as supported / suggestive / not-established
  (Task 024; D-051, L-041).
- A single generation per condition confounds the experimental variable
  with stochastic generation variation; controlled repetition with 3
  fresh-session replicates per condition turns a single-run delta into a
  distribution-shift-vs-variation statement, and the direction of a
  single-run delta can still be a useful prior even when magnitudes
  fluctuate (Task 025/026; L-042, L-043).
- Collection at scale must be audited before analysis, treating the
  operator's "I may have made a mistake" as a design feature: reconcile
  every planned run against the manifest and byte-identical authoritative
  renders (missing/duplicate/wrong/stale detection), preserve raw outputs
  untouched, and record execution deviations (mode changes, header
  edits, split messages) as metadata with a usability assessment rather
  than repairing or renaming anything (Task 026; L-044).

