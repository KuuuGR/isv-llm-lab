# Experiment 003 — Design: Interslavic Lexical Scaffold (Generation-Time Dictionary Guidance)

Status: **DESIGN ONLY (SODA Task 009, 2026-09-01).** This document specifies
EXP-003. It is not implemented. Task 010 (implementation) starts only after
Project Owner / Architect approval of the GO recommendation in §20.

---

## 1. Executive summary

EXP-001 measured unconstrained LLM translation (baseline). EXP-002 tested
*correcting an existing translation* with supplied alternatives (revision).
EXP-003 tests the remaining, untested mechanism: **supplying dictionary
guidance at generation time** — a deterministic *lexical scaffold* derived from
the Polish source via the project's audited resources — and asking the LLM to
translate with that scaffold as vocabulary guidance.

The core technical finding of this design is that the project already contains
the primary alignment resource: `basic.json` has a **Polish translation column
(`pl`, 18,916 unique Polish gloss keys)**. A Polish→Interslavic reverse index
built from it covers lemma-level Polish vocabulary well (verified live:
`być→byti`, `się→sę`, `dobrze→dobro`, `pierwszy→pŕvy`, `dziś→[dnėś, tutdėnj,
sego dnja]`, `tam→[tam, tamo, onamo, onde]`). What it does **not** cover is
inflected Polish forms (`był`, `bawił`, `morzem`), because the repository has
**no Polish lemmatizer** and none is a current dependency.

Measured on the actual story (578 unique Polish forms): 207 (36 %) hit the
reverse index directly; dictionary-verified lemma recovery adds ~28 (~5 %);
the residual of 371 forms splits into ~54 name-like tokens (pass-through) and
**~317 genuinely inflected non-name forms** — these are handled by an
**explicit, committed, provenance-bearing curation table** for this one story.
Anything still unmapped is scaffolded `[?]` rather than guessed. This keeps
the "no silent weak heuristics" rule (see §6.3, §7).

The scaffold is generated **deterministically, with no hidden LLM calls**
(§6.4): the experimental variable is the scaffold itself, so its generator
must not smuggle in a translation step (`Polish → LLM → scaffold → LLM → ISV`
would not test a dictionary scaffold at all).

Four conditions are specified (A = direct baseline, B = scaffold with one
canonical candidate, C = scaffold with dictionary-supported alternatives,
D = C + reliable grammatical annotations). The evaluator is already ready
(Task 008 two-tier policy). The recommendation is **GO** for a controlled
pilot on the existing story with 3 models; generalization claims require more
stories later. Research-relevant decisions and measurements are recorded in
`docs/RESEARCH_NOTES.md` (§15).

## 2. Research question

> Does providing an LLM with a deterministic Interslavic lexical scaffold —
> generated from the Polish source using the project's audited dictionary and
> morphology resources — improve the lexical resource-support of its
> translation (canonical coverage and broader resource-supported coverage)
> while preserving natural language, compared with unconstrained direct
> translation of the same source by the same model?

Two narrower, equally important sub-questions:

1. Can the scaffold guide vocabulary **without** dictating word order or
   grammatical surface forms (i.e., without turning into a bad translation)?
2. Does adding alternatives (C) and grammatical annotations (D) each provide
   measurable additional value, or do they add noise?

## 3. Hypotheses

| # | Hypothesis | Direction | Test |
|---|---|---|---|
| H1 | Scaffold conditions (B/C/D) achieve higher **canonical coverage** than baseline A on the same model/source | B,C,D ≥ A | evaluator metrics, within-model |
| H2 | Scaffold conditions achieve higher **broader resource-supported coverage** than A | B,C,D ≥ A | evaluator metrics, within-model |
| H3 | Scaffolding does **not** introduce regressions: A→C and B→C transition counts in B/C/D (vs A) stay near zero | small | token-aligned transitions |
| H4 | Alternatives (C) vs single candidate (B) change outcomes | two-sided (may help or hurt) | B vs C |
| H5 | Grammatical annotations (D) add value over C | two-sided | C vs D |
| H6 | Naturalness is preserved (not sacrificed for coverage) | no directional claim | human holistic reading |

H4–H6 are explicitly two-sided: the experiment exists to find out. No
directional claim is assumed for adding information (L-016 applies to
candidate layers; here it applies to prompt complexity).

## 4. Experimental conditions

All conditions receive the **same Polish source text** and the **same
model**; prompts differ only by the condition content (§8).

### Condition A — Direct baseline (control)
- Prompt: source + normal "translate into Interslavic" instruction.
- No scaffold. As close to EXP-001 as reasonably possible (EXP-001's exact
  prompts are recorded as `unknown`; A is the within-EXP-003 control, and the
  scientifically primary comparison is A vs B/C/D under identical conditions).

### Condition B — Lexical scaffold (single canonical candidate)
- Prompt: source + scaffold in the aligned format (§5), **one** canonical ISV
  candidate per Polish token (deterministic selection, §7).
- The scaffold guides vocabulary; word order, inflection and constructions
  remain entirely the model's choice.

### Condition C — Lexical scaffold + alternatives
- Same as B, but each line may carry **multiple** dictionary-supported ISV
  candidates where the resources genuinely support more than one (e.g.
  `tam → [tam, tamo, onamo, onde]`).
- The model chooses among supplied alternatives by context; it may also
  inflect them.

### Condition D — Scaffold + alternatives + grammatical annotations
- Same as C, plus per-candidate grammatical annotations **only where the
  existing resources generate them reliably**: dictionary POS, verb aspect
  (`ipf.`/`pf.` from the dictionary xpos), and — for a bounded subset —
  a few example paradigm forms generated by `@interslavic/morphology`.
- The model remains fully responsible for choosing surface forms, agreement,
  and natural discourse; the annotations are hints, not mandates.
- What is **not** annotated: the Polish source form's morphological analysis
  (no Polish morphological analyzer exists in the project) and any mapping of
  Polish tense/aspect onto ISV. That would be silently invented information.

Conditions are nested: B ⊆ C ⊆ D in *information added* (not in expected
outcome). A is the disjoint control.

## 5. Recommended scaffold representation

**Recommendation: token-aligned, one line per Polish surface token, grouped by
sentence, with alternatives as an inline bracketed list.** Example (rendered
form, Condition C):

```
Dziś       → [dnėś]
Tomek      → [Tomek]            (proper name — keep as-is)
był        → [byti]
pierwszy   → [pŕvy]
raz        → [raz]
nad        → [nad]
morzem     → [morje]
i          → [i]
dobrze     → [dobro, pravilno]
się        → [sę]
tam        → [tam, tamo, onamo, onde]
bawił      → [baviti]
```

Why this over the alternatives the task proposed:

- **Linear `[dnes] [byti] …`** reads like a surface-form sequence; models
  tend to treat it as a template and copy it mechanically — exactly the
  failure mode the task wants to avoid ("accidentally giving it a machine-
  generated bad translation"). Rejected as the primary form.
- **Token-aligned `Dziś → [dnėś]`** makes every mapping explicit and
  inspectable (reproducibility), prevents word-order leakage (a vertical list
  is not a sentence), and keeps sentence grouping so the model still sees
  discourse structure. **Adopted.**
- **Alternatives inline** (`[dobro, pravilno]`) keep the alignment
  one-line-per-token and the ordering is meaningful (§7), rather than a
  separate table that breaks the 1:1 correspondence.

**Token boundaries vs lemmas/concepts.** The scaffold preserves **Polish
surface token boundaries** (one line per source token) because lemma-level
input representation would require a Polish lemmatizer (not available, §6.3).
The *semantic units* on the ISV side, however, are **lemmas/concepts**, not
surface forms: a scaffolded candidate is an ISV headword the model inflects
itself. The alignment mapping (Polish surface → ISV lemma) is exactly the
direction the reverse index + curation provide. Repeated Polish words map
identically (memoized) — no special representation. Punctuation is **not**
scaffolded (the model owns it); sentence/paragraph boundaries are preserved
by the grouping. Multi-token entries render as a single quoted unit, e.g.
`na przykład → [napriměr]` and `bać się → [bojati sę]` (one concept needing
multiple ISV words, or one Polish multiword needing one ISV headword).

Machine-readable form: the scaffold is generated as `scaffold.json` (per
sentence: list of `{pl_surface, pl_normalized, isv_candidates[], note}` with
full provenance), and the prompt embeds a deterministic human-readable
rendering of it.

## 6. Polish-to-scaffold alignment strategy

### 6.1 Primary mechanism — Polish reverse index from the canonical dictionary

`basic.json` rows carry a Polish translation column (`pl`, plus other
languages). Verified: 18,916 unique normalized Polish gloss keys across
19,100 rows. Building the reverse index:

1. For each row, split the `pl` gloss on commas (each comma-part is a
   distinct Polish gloss);
2. strip documented gloss artifacts — leading bound-form markers (`-`,
   `!`, `*`, …) and parenthetical disambiguation (`(engine)`), mirroring how
   the project already distrusts machine annotation (L-011);
3. normalize (NFD + lowercase, consistent with `isv_eval.normalize`);
4. map gloss → `(isv_headword, partOfSpeech, type, row)`.

The reverse index **is** the Polish→Interslavic lexicon, grounded entirely in
the canonical dictionary. No new dependency.

### 6.2 Alignment pipeline (deterministic, per sentence)

For each Polish token (tokenized with the project's existing tokenizer,
sentence-grouped):

1. **Multiword expressions** — a per-story table (`na przykład → napriměr`,
   `bać się → bojati sę`, …) is applied greedily before single-token
   mapping. Entries are committed artifacts with provenance (§17). This
   covers Polish multiword expressions and multi-word ISV headwords (`sego
   dnja`).
2. **Exact reverse-index hit** → ISV candidate list (canonical layer,
   `source = basic.json`, `kind = pl_gloss_exact`). Multiple candidates
   preserved (e.g. `tam → [tam, tamo, onamo, onde]`).
3. **Dictionary-verified lemma recovery** — only when the exact form misses.
   A small, frozen, audited table of common Polish inflectional endings is
   tried; the recovered stem is kept **only if it re-looks-up in the reverse
   index** (so the dictionary filters everything; nothing is invented).
   Measured on the actual story: this rescues only ~28 forms (~5 % of unique)
   — Polish inflection is morphophonological (suppletion `był→być`,
   alternations `słów→słowo`), which a suffix stripper cannot handle. This
   is the honest upper bound of what a rule-based fallback can do.
4. **Proper names** — deterministic: capitalized in the source + no reverse
   hit + no recovered lemma → name; scaffold `[Name] (proper name — keep
   as-is)`. Reuses the project's existing name-family detection
   (`prepare_exp002_pilot.NAME_PATTERNS`) plus a per-story names table for
   story-specific names (e.g. `teofil`, `bronisława`, `julianna`,
   `przemysław`, `antoni` in the current story).
5. **Residual (inflected non-name forms)** — an explicit, committed, per-story
   **curation table**: Polish surface → ISV candidates, each entry carrying
   provenance (basis: reverse-index verification where possible, the `pl`
   gloss, and human review). Measured composition of the residual (371 unique
   forms): ~54 name-like (handled in step 4) + **~317 inflected non-name
   forms** to curate. This is a manageable, fully auditable set for one
   story; its size is a direct consequence of having no lemmatizer (§6.3).
6. **Unmapped** — anything still without a mapping is scaffolded `[?]` and
   the scaffold notes "no mapping found". It is never silently guessed.

### 6.3 Limitation — stated, not hidden

**Reliable Polish lemmatization is not achievable with the current project
dependencies** (no Polish morphological analyzer; none proposed in this task
because it would add a heavyweight, network-downloaded dependency). The
design handles this explicitly: dictionary-verified recovery + a curated
residual table for one story, `[?]` otherwise. The curation is human
judgment, but it is *explicit, committed, provenance-bearing, and
reviewable* — it is not a silent weak heuristic presented as reliable
linguistic analysis. If EXP-003 later expands to multiple stories, adding an
audited Polish lemmatizer (e.g. Stanza-pl, Apache-2.0) becomes a separately
approved dependency decision (§18).

### 6.4 Scaffold generation method — deterministic and auditable

The task's critical question: should the scaffold be generated (1)
automatically from Polish, (2) from Polish lemmas, (3) from Polish lemmas +
grammatical features, (4) through an LLM-assisted semantic mapping, or (5)
another method? Decision for EXP-003 v1:

| Method | Verdict | Why |
|---|---|---|
| (1) Automatic from Polish surface tokens (deterministic pipeline: §6.2) | **ADOPTED** | Reproducible, no hidden computation, directly traceable to the audited dictionary; the scaffold is exactly the dictionary's evidence, nothing more. |
| (2) From Polish lemmas | **REJECTED for v1** | Requires reliable Polish lemmatization, which is not a project dependency (§6.3). Dictionary-verified lemma recovery is the available subset of this option. |
| (3) Polish lemmas + grammatical features | **REJECTED for v1** | Requires a Polish lemmatizer *and* a Polish morphological analyzer — neither exists in-repo. Note: Condition D supplies **ISV-side** grammatical annotations from ISV resources; that is different and supported. |
| (4) LLM-assisted semantic mapping | **REJECTED for v1** | Would create `Polish → LLM → scaffold → LLM → ISV` and claim a dictionary-scaffold effect. If ever used later, it must be an explicitly documented *experimental variable*, not a hidden step (see §18). |
| (5) Other | — | None needed; the pipeline is the smallest reliable mechanism. |

Consequences of the decision:

- **No hidden LLM calls in the scaffold generator.** The only non-automatic
  element is the curated residual table, which is explicit human judgment
  committed as a versioned file, not an opaque model step.
- **What the model receives is fully specified**: every scaffold candidate is
  traceable to a resource (canonical dictionary / verified recovery /
  curation / `[?]`), recorded in `scaffold.json` with provenance.
- This keeps the measured effect attributable to the scaffold itself (§9).

## 7. Candidate-generation strategy

Candidates follow the Task 007/008 resource policy. Each candidate carries
provenance: `{surface, pos, layer, source, kind, detail}`.

**Layer ordering (deterministic, by policy weight):**

1. **Canonical** — ISV headword from the reverse index (`basic.json` `pl`
   gloss). `source = basic.json`, `kind = pl_gloss_exact`.
2. **Canonical (lemma-recovered, verified)** — recovered stem that re-looked
   up in the index. `kind = lemma_recovery`, detail records the suffix rule.
3. **Orthographic variant** — folded/diacritic variant of a canonical form
   (e.g. `pŕvy` ↔ `prvy`), rendered as an *annotation*, never as a separate
   candidate (`kind = orthographic_note`).
4. **Alternative attestation** — `isv.dic` / `interslavicfreq` attestation of
   a candidate's surface, used to **annotate** candidates (e.g. `attested:
   isv.dic`, `cB −508`) and to tie-break ordering — **never** to create a
   candidate from a Polish gloss the dictionary does not support. This is a
   deliberate asymmetry, grounded in the policy: alternative resources attest
   ISV surfaces; they do **not** encode Polish↔ISV equivalence, so they cannot
   ground Polish→ISV mappings.
5. **Historical (`slovnik`)** — never promoted; recorded only as provenance.
6. **Curated (human, explicit)** — entries from the per-story curation table
   (§6.2 step 5), each with its recorded basis. Ranked after automatic layers
   so automatic evidence always wins where both exist.

**Candidate ordering** (for Condition B's single pick and C's list order):
exact-pl-gloss first, then dictionary `type` ascending (type 1 = universal
before neologisms), then headword lexicographic. Deterministic and documented.

**No new linguistic evidence is invented.** Frequency never becomes
correctness; alternative attestation never becomes canonical; orthographic
similarity is always flagged as a variant note.

## 8. Prompt design

### 8.1 Shared skeleton (all conditions)

- Task statement: translate the given Polish story into Interslavic
  (Medžuslovjansky).
- Whole-document constraint: one translation, preserve paragraph order,
  preserve character names and quoted material.
- Output contract: return only the translation; no explanations, commentary
  or analysis.
- Recording: the exact prompt text is stored per run (hashed) — prompt
  wording is an experimental artifact, not incidental.

### 8.2 Scaffold semantics (conditions B/C/D) — the core instruction

The model must understand: **the scaffold is lexical guidance, not a finished
translation.** Explicit rules:

- **Allowed:** change word order freely; inflect the supplied candidates
  (case, number, gender, tense, person, aspect); choose grammatical
  constructions; preserve natural discourse; choose among supplied
  alternatives by context (C/D).
- **Forbidden:** treat the scaffold as a mandatory surface-form sequence;
  mechanically copy it; invent unrelated vocabulary where an appropriate
  supplied candidate exists; produce explanations instead of the translation.
- A note explains that `[?]` means no mapping was found — the model should
  use its best judgment there (this is where residual uncertainty is
  *exposed*, not hidden).

### 8.3 Condition D — grammatical information

The prompt states explicitly what is supplied (dictionary POS, verb aspect,
a few generated example forms) and what remains the model's responsibility
(choosing surface forms, agreement, tense interpretation). The annotations
are generated only "where this can be generated reliably by existing project
resources" — otherwise the line carries no annotation.

### 8.4 Attribution discipline

Across A/B/C/D the prompt text is **byte-identical except the condition
content**: A has no scaffold block; B/C/D share one scaffold block template,
and C/D add the alternatives / annotations within the block. This keeps
differences attributable to the intended variable as much as possible. The
residual confound — that scaffolded prompts are longer — is acknowledged in
§16.

## 9. Experimental controls

- **Source:** the existing Polish story (same as EXP-001), used as a cleaned
  story-only file (see below).
- **Source cleaning (documented, forward-applied D-020):** the historical
  EXP-001 `source.txt` embeds an instruction line + markdown fences (a known,
  documented artifact, hashed as-is in EXP-001). EXP-003 introduces
  `experiments/exp003-scaffold/input/source.txt` = the story text **only**
  (title + body), with a `source.meta.json` recording the derivation (parent
  EXP-001 source SHA-256, what was removed, new SHA-256). This is a
  forward-applied rule for future experiments; EXP-001 data is untouched.
- **Models:** same model runs A/B/C/D; 3 models in the first wave (§13).
- **Prompts:** stored per run; differ only by condition content (§8).
- **Settings:** temperature/seed recorded (`unknown` where the interface
  cannot fix them; the operator prompt requests a stated default).
- **Recording:** model/provider/version, generation date, per-file SHA-256,
  resource versions (dictionary `manifest.json`, lexicon manifest, audit
  pins), evaluator commit, scaffold generator commit.
- **External execution:** no LLM API client (D-007). The operator interface
  is one self-contained Markdown file per (model × condition)
  (D-024 pattern). Raw outputs are saved **byte-for-byte** and never
  overwritten (`collect` refuses existing outputs; D-023).
- **Determinism:** scaffold generation is deterministic (byte-identical on
  rerun except the timestamp, L-013); curated tables are committed files.

## 10. Evaluation metrics

Uses the Task 008 two-tier evaluator, same evaluator commit across all
conditions and models.

Per run (A/B/C/D):

- `lexical_tokens`, `canonical_supported_tokens`, `canonical_coverage`,
  `broader_resource_supported_tokens`, `broader_resource_supported_coverage`,
  `unresolved_tokens`, `unresolved_rate`, plus A/B/C bucket counts.

Comparisons (per model, B/C/D vs baseline A):

- **Token-aligned evaluator-state transition matrix** (the EXP-002 standard,
  L-015): A→A, A→B, A→C, B→A, B→B, B→C, C→A, C→B, C→C.
- **A→C and B→C regression lists** — canonical forms the model *lost* under
  scaffolding. Must be near-empty; any non-empty list is a finding.
- **C→A / C→B resolutions** — unresolved forms the scaffold helped resolve.
- **Candidate usage/adoption:** per supplied scaffold candidate — present in
  output? accepted by evaluator (A/B)? used at the aligned position (targeted
  adoption)? (reuses `compare_exp002` bookkeeping).
- **Invented / non-supplied forms:** new unresolved forms in B/C/D that were
  neither in A's output nor supplied in the scaffold — the closest
  deterministic proxy for "the model invented vocabulary despite guidance".
- **No invented numerical "naturalness" score** (D-023). Naturalness is a
  human holistic judgment (§11).

The two coverage metrics are reported **side by side, never merged**: a
scaffold that only raises the broader tier without the canonical tier is a
different result from one that raises both, and both are different from a
high-coverage-but-unnatural output (§11).

## 11. Human evaluation procedure

> **Superseded (2026-09-05, SODA Task 014, D-038).** The procedure below was
> implemented (Task 012) and attempted by the Project Owner, who found the
> holistic complete-text comparison too cognitively demanding — a format
> problem, not a result about any condition. **No holistic human result was
> obtained or recorded.** The holistic artifact (`comparison/human_review.md`)
> is preserved as a historical/provisional review design with a superseded
> banner. The actual EXP-003 human-evaluation protocol is now the
> sentence-level forced-choice test (`comparison/sentence_review.md`,
> prepared by `scripts/prepare_exp003_sentence_review.py`): ~100 questions,
> each showing one Polish source sentence plus the corresponding sentence
> from each of the four conditions (A/B/C/D) of the same model in a
> per-question deterministic randomized order ("Version 1..4", seed
> `20260905`); the Project Owner ticks the version that sounds most natural
> as Medžuslovjansky as a whole (explicitly NOT checking individual words
> against a dictionary). The mapping is in `comparison/sentence_review_key.json`.
> This is the ONE planned human-evaluation exercise for EXP-003.

The Project Owner is **not** a manual lexical annotator and will not classify
words.

Procedure (qualitative, holistic):

1. **Complete-text comparison, not word lists.** For each model, the complete
   A, B, C, D translations are compared as whole documents (the
   `human_review.md` pattern from EXP-002).
2. **Blinded presentation.** Conditions are relabeled neutrally (e.g.
   "Version 1/2/3/4") with the mapping randomized per model and recorded in
   the review file. Automatic scores are **not** shown before the holistic
   judgment, to avoid biasing it (the task explicitly requests this).
3. **A small fixed rubric of holistic questions** (no per-word judgment):
   - Which version sounds more naturally Interslavic?
   - Which version would you prefer to read?
   - Does one version feel more mechanically constructed?
   - Which version preserves the meaning and style of the Polish original
     better?
   - (B/C/D only, after unblinding) Does the scaffolded text feel
     constrained by the scaffold?
4. **Preference ordering** (best to worst among the four versions, per model)
   plus a one-paragraph justification.
5. **Recording for research:** the reviewer's verbatim answers, the
   presentation-order mapping, the date, and the model are written to
   `comparison/human_review.md`; the mapping key (which version label is which
   condition) is kept in the same file after the initial judgment is recorded.
   No scoring is computed from the answers. These records are research
   evidence for the future paper (§15).

This preserves the three-way distinction the task demands:
resource-supported vocabulary (deterministic), automatic metrics (evaluator),
holistic naturalness judgment (human) — never collapsed into one score.

## 12. Dataset recommendation

**Recommendation: the existing Polish story only, for the first run.**

Rationale:

- It has established EXP-001 and EXP-002 baselines — the only corpus with
  historical numbers, maximizing comparability; a controlled continuation.
- Cost and interpretability: one story × 4 conditions × 3 models is already
  a bounded first dataset.
- One story **cannot** support generalization claims; EXP-003 v1 is therefore
  framed as a controlled within-story comparison (a pilot-scale design with
  the same discipline as EXP-002's pilot).
- The repository contains no other licensed story; "several existing stories"
  would require new copyrighted sources plus licensing work — a separate
  decision.

**Limitation, stated:** one story, one genre, one set of characters — any
conclusion is story-conditional. **Later validation set:** a second story
(with its own curation table) is a drop-in extension and should be added as
a separate wave *if* the first wave shows a direction-consistent effect; the
pipeline is parameterized by story, so this is not a redesign. The design
does not request ten stories now.

## 13. Model recommendation

**Recommendation: staged — first wave with 3 models × 4 conditions:**
**Claude, ChatGPT, and Bielik.**

Reasoning:

- The inference unit is the **within-model A vs B/C/D contrast**; 3 models
  give 3 independent replications of the scaffold effect. All seven models
  multiply cost (7×4=28 full-story generations) without multiplying the
  answer to the primary question.
- Claude and ChatGPT are strong general translators (represent the
  "competent translator" regime, where scaffolding must help rather than
  interfere), and have demonstrated structured-prompt adherence in EXP-002.
- Bielik is a Polish-language model with the **lowest** EXP-001 coverage
  (55.5 %): it is the highest-risk, highest-signal stress case (worst
  baseline → largest possible effect; Polish-native behavior may confound or
  amplify scaffold effects — that is a finding, not a bug). It is also the
  best test of whether the scaffold helps a weak baseline.
- GPTs "ISV Teacher" is excluded from the main wave because its internal
  system prompt is unavailable (a confound by construction, D-018); it may
  return later as a separate exploratory condition.
- Selection is **not** based on the coverage ranking alone: it balances
  strength spread (2 strong, 1 weak) against cost, availability,
  structured-prompt adherence, and the research question.

A second wave (remaining models and/or a second story) is triggered only if
the first wave shows a real, direction-consistent effect.

## 14. Reproducibility plan

Every EXP-003 run records (mirroring `run_exp001.py`/`run_exp002_pilot.py`
meta conventions):

research question · hypotheses · conditions · source identity + SHA-256 ·
model/provider/version · prompt (committed, hashed) · generation date ·
parameters (temperature/seed where available, else `unknown`) · resource
versions (`basic.json` manifest, lexicon manifest, audit pins) ·
candidate-generation procedure (script commit + scaffolds + curation tables +
hashes) · scaffold-generation procedure (same) · evaluator version (commit) ·
raw outputs (immutable, hashed, gitignored per copyright) · automatic
metrics · deviations · failures · limitations · conclusions.

- Scaffold regeneration is deterministic and verified byte-identical on rerun
  (except timestamps, L-013).
- **Negative results are preserved**: a condition where scaffolding hurts
  (A→C regressions, or lower naturalness) is reported, never deleted.
- Raw LLM outputs are never regenerated or cleaned (D-023); the story and
  source-derived artifacts (scaffolds, curation tables containing story
  tokens, operator prompts embedding the source) are **gitignored**, with the
  generators, manifests and READMEs committed — the same copyright policy as
  EXP-001/002.

## 15. Research-notes / publication considerations

The project may become the basis for a publication on LLM-assisted translation
of a low-resource constructed language. EXP-003 introduces a genuinely new
methodological distinction, recorded in `docs/RESEARCH_NOTES.md`:

> **generation-time lexical scaffolding** (EXP-003 B/C) and
> **generation-time lexical + grammatical constraints** (EXP-003 D) are
> distinct from **direct translation** (EXP-001) and **post-hoc lexical
> revision** (EXP-002).

The research record captures, per task instruction §18: what we test, why,
what the model receives, what happened, what we learned — including measured
alignment coverage, the lemmatization limitation, the scaffold-generation
method decision (no hidden LLM calls), and the rule that negative results are
preserved. Lightweight by design; no research-management system is created.

Paper-relevant properties of the design:

- Every artifact is deterministic and versioned (scripts + commits + resource
  pins + hashes), so the pipeline can be re-run and the numbers re-derived.
- The two-tier metric terminology (canonical coverage vs broader
  resource-supported coverage) matches the published policy
  (`docs/RESOURCE_POLICY.md`), so results map to the policy document.
- Unknowns stay unknown (model versions, providers, EXP-001 prompts) and are
  recorded as such (D-018), so a future paper states its own provenance
  limits honestly.
- Source licensing is documented (story + derived artifacts stay out of git);
  the method description can cite the deterministic scaffold pipeline and
  the curated-table provenance model.
- Human evaluation is a described qualitative protocol (blinded holistic
  paired comparison), not an ad-hoc score.

## 16. Risks and limitations

1. **Alignment gaps (main risk).** Polish inflectional forms are not
   lemmatizable with current dependencies (measured: ~317 unique inflected
   non-name forms in the story require curation). Mitigation: exact reverse
   index + dictionary-verified recovery + explicit curated residual table +
   `[?]` fallback. The residual curation is human judgment — but it is
   *explicit*, committed, provenance-bearing, and reviewable; it is not a
   silent heuristic. A second story would need its own curation table.
2. **Prompt-length confound.** Scaffolded prompts are longer and more
   structured than A. A vs B is the cleanest contrast; B/C/D are nested. This
   is documented, not eliminable, with the external-interface constraint.
3. **Hidden-LLM confound (guarded by design).** If the scaffold generator
   contained LLM calls, the measured effect would be "LLM-assisted scaffold",
   not "dictionary scaffold". The generator is deterministic (§6.4); any
   future LLM-assisted variant becomes an explicit experimental variable.
4. **LLM non-compliance.** Models may (a) mechanically copy the scaffold
   (word-order leakage) or (b) ignore it entirely. Both are detected by
   candidate-usage statistics and the transition matrix; neither is assumed
   away.
5. **Alternative-resource evidence cannot ground Polish→ISV mappings.** The
   scaffold is canonically centered; alternative attestation only annotates.
   This is a scope limit of the mechanism, stated in §7.
6. **Etymological orthography.** Canonical headwords use etymological
   characters (`dnėś`, `pŕvy`); models may render base-letter spellings.
   The Task 008 evaluator folds these (they count as canonical), and the
   scaffold may annotate the folded form as an orthographic note (§7.3) — but
   the model's spelling choices remain its own.
7. **One story, one domain.** No generalization claim is made; conclusions are
   story-conditional until a validation story is run.

## 17. Required implementation work for the next task (Task 010)

1. `scripts/build_exp003_scaffold.py` — reverse index (from `basic.json`),
   alignment pipeline (multiword → exact → verified recovery → names →
   curated residual → `[?]`), candidate provenance, scaffold renderer for
   B/C/D, deterministic output + `scaffold.json`.
2. Per-story artifacts: cleaned `input/source.txt` + `source.meta.json`;
   curated residual table; multiword table; story names table (gitignored;
   generators + README committed).
3. `scripts/package_exp003_prompts.py` — operator prompts (model × condition),
   deterministic, manifest with SHA-256 (D-024 pattern).
4. `scripts/run_exp003_pilot.py` + `scripts/compare_exp003.py` — prepare /
   collect / compare / status; A-vs-B/C/D token-aligned transitions,
   regression lists, candidate usage, invented-forms proxy (extend
   `compare_exp002.py`).
5. `scripts/verify_exp003_runs.py` — completeness + SHA-256 integrity.
6. Tests: reverse-index construction, alignment cases (names, inflected,
   multiword, ambiguity), candidate provenance shape, scaffold determinism,
   comparison math.
7. README + operator instructions under `experiments/exp003-scaffold/`.

**No evaluator changes are required** — the Task 008 policy already provides
the two-tier metrics and per-token provenance.

## 18. Explicitly deferred work

**Required for EXP-003 (in scope, Task 010):** everything in §17. Nothing
else.

**Useful later (deferred, decided on evidence):**
- Second story as validation set (with its own curation table); remaining
  models (Gemini, DeepSeek, Grok; GPTs ISV Teacher as an explicitly-labeled
  exploratory condition).
- Audited Polish lemmatizer (e.g. Stanza-pl) — only if multi-story scale-up
  demands it; a separately approved dependency decision.
- LLM-assisted semantic disambiguation in the scaffold pipeline — only as an
  explicitly documented experimental variable, never hidden (§6.4).

**Not justified now (future research directions, not part of EXP-003):**
Wikipedia translation, corpus creation, fine-tuning, mobile application, web
service, automated human feedback loops, multiple translation agents,
production translator, API integration. None of these become part of EXP-003
unless justified by the experiment's results and separately approved.

## 19. Expected artifacts and directory structure

```
experiments/exp003-scaffold/
  DESIGN.md                 — this document (committed)
  README.md                 — operator instructions (committed)
  prompt_template.txt       — shared prompt skeleton (committed)
  input/
    source.txt              — cleaned story-only source (gitignored; embeds story)
    source.meta.json        — derivation + hashes (gitignored)
  curation/                 — per-story curated tables (gitignored; embeds story tokens)
  scaffolds/<story_id>/     — scaffold.json + rendered B/C/D scaffolds (gitignored)
  operator-prompts/         — <NN>-<model>-<condition>.md + README.md + manifest.json
                              (committed: README/manifest; gitignored: .md files)
  outputs/<run_id>/         — meta.json + output.txt (immutable, gitignored)
  comparison/<run_id>/      — comparison.{json,md} (gitignored)
  comparison/human_review.md (gitignored)
```

`<run_id>` = `2026-09-XX__<provider>__<model>__<model_version>__<condition>`.
It is always obvious which files are design / generated scaffolds / prompts /
raw outputs / evaluation reports / human-review material / metadata /
reproducibility info; copyrighted story material stays out of git per
repository policy.

## 20. Recommendation

**GO — implement EXP-003 as a controlled pilot** (Task 010): the existing
story, 4 conditions × 3 models, using the pipeline in §17.

Justification:

- The primary alignment resource already exists in the repository (verified:
  the `pl` reverse index covers lemma vocabulary; the alignment gaps are
  known, measured — 36 % direct + ~5 % recovery + explicit curation — and
  handled explicitly, not hidden).
- The scaffold generator is deterministic with no hidden LLM calls, so the
  measured effect is attributable to the scaffold (§6.4).
- The evaluator already implements the required two-tier metrics and
  per-token provenance (Task 008) — no evaluator change is needed.
- The EXP-002 infrastructure (operator prompts, byte-for-byte collection,
  token-aligned comparisons, human-review pairs) is directly reusable.
- The experiment answers the central, untested question (generation-time
  guidance vs post-hoc revision), with a within-model controlled design that
  is cheap enough to run and interpretable enough to decide the next step.

Conditions on GO: (1) the curated residual table for the story is completed
with full provenance during Task 010; (2) B/C/D prompts are byte-identical
except condition content; (3) the first wave stays at 3 models — expanding
is a separate decision after evidence; (4) the research record
(`docs/RESEARCH_NOTES.md`) is updated with the run's results, including
negative results.

---

## Final recommendation

> **GO** for EXP-003 implementation (Task 010), scoped as a controlled pilot
> on the existing Polish story with 3 models × 4 conditions. The design is
> grounded in a verified existing resource (the dictionary's Polish column),
> handles the known alignment limitation explicitly rather than silently,
> keeps the scaffold generator deterministic and free of hidden LLM calls,
> and reuses the project's established evaluation and execution machinery.
> No implementation was performed; no LLM was called.
