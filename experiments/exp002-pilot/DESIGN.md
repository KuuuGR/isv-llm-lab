# Experiment 002 — Pilot: Dictionary-Guided Revision of Experiment 001 Outputs

Status: **PILOT PREPARED (Task 006, 2026-08-31).** The pilot's input packages
(revision prompts, candidate lists, original translations) are built. LLM
execution is **external** — this project has no LLM API client by design
(D-007). Revised outputs are dropped into the run layout and evaluated with the
**same evaluator** as EXP-001. This document is the specification; §9 records
the implemented layout.

---
## 1. Objective

Test the hypothesis:

> If an LLM is given explicit Interslavic lexical alternatives for forms that
> are not present in the canonical dictionary, can it revise its own complete
> translation into a version with better lexical/morphological resource
> coverage while preserving the meaning and coherence of the original text?

This is an experiment, not a production translator. EXP-001 is historical data
and is never modified.

### Two separate questions (kept distinct)

- **A. Resource question.** Can an unresolved form be replaced by a form that
  the canonical resources support? — answered *deterministically* by
  candidate generation (no LLM).
- **B. Revision question.** Can an LLM *use* supplied alternatives correctly in
  context in a complete-document rewrite? — answered by the actual pilot run.

## 2. Loop under test

```
EXP-001 output
    ↓
identify unresolved forms
    ↓
deterministic candidate generation (canonical dict / Task-005 evidence / morphology)
    ↓
stratified pilot selection of unresolved forms
    ↓
revision prompt = complete original translation + candidate table
    ↓
EXTERNAL LLM  →  complete revised translation
    ↓
same evaluator (isv-eval) on original and revised
    ↓
before/after comparison + replacement metrics
```

## 3. Candidate generation (question A)

For every unresolved form selected for the pilot, a candidate list is built
deterministically from these sources, in priority order. Provenance is recorded
for every candidate.

1. **Canonical dictionary evidence** — the form (or an orthographic
   normalization of it) is a headword in `basic.json` / the full-form lexicon.
   A C-form is by definition not a canonical hit, so this usually appears via
   (2); recorded when it does occur.
2. **Orthographic-variant evidence** — the diacritic-stripped / folded form
   IS a canonical form (e.g. `dněv` → `dnev`). The canonical form is the
   candidate. Marked `orthographic_variant`, never silently upgraded to a
   match (§ task 8).
3. **Alternative-resource evidence** — exact hit in a Task-005 resource
   (hunspell `isv.dic`, `interslavicfreq` wordlists, `slovnik` snapshot).
   The attested surface form is the candidate; the resource and its
   annotation (tags / cB) are recorded.
4. **Morphology-derived candidate** — for a candidate lemma (the evaluator's
   B-fallback candidates recorded in EXP-001 `unresolved.json`) that IS a
   canonical dictionary headword, the JS morphology engine is asked to
   generate the paradigm; the **lemma itself** is a candidate (the LLM uses it
   in a grammatically appropriate form). The generated paradigm is recorded as
   supporting evidence. Distinguished from "candidate lemma exists":
   a lemma that generates the observed form exactly would have made the form
   bucket B in EXP-001; here we supply *lemmas* the model can use, not claims
   that the observed form is generated.
5. **No candidate** — nothing defensible; the form is left unresolved and is
   listed in the prompt as "leave unchanged".

Rules:

- No lexical candidate is invented.
- A diacritic-stripped similarity is recorded as an orthographic candidate,
  not proof of equivalence.
- No language-origin classification (no Polish/Russian/Czech labels).
- Multiple plausible candidates are preserved; the LLM chooses by context.
- Candidate counts are capped for prompt size; the cap and the truncation
  order are deterministic and documented.

## 4. Revision prompt (question B)

The prompt supplies:

- the **complete original translation** (byte-for-byte copy of the EXP-001
  output, one document — never split into sentences/paragraphs);
- a **candidate table** for the pilot-selected forms only, in the form:

```
Original form: X   (occurs N×, models: …)
  suggested alternatives:
    A  — canonical dictionary (lemma: …)
    B  — hunspell isv.dic (tag: …)
    C  — morphology-derived lemma (…)
  evidence: …
```

Explicit instructions to the LLM:

- preserve the meaning of the original translation;
- preserve story structure and paragraph order;
- preserve character names and quoted material unless a supplied candidate
  explicitly concerns them;
- replace unresolved vocabulary only where an appropriate supplied
  alternative exists;
- use supplied alternatives in grammatically appropriate forms;
- do not introduce new invented vocabulary;
- forms with no candidate → leave unchanged;
- do not add explanations, commentary or analysis;
- return only the revised story.

## 5. Pilot scope and selection

The pilot does **not** target all 1,050 unresolved forms. Selection is
deterministic (`scripts/prepare_exp002_pilot.py`) over ONE EXP-001 source run,
covering a small, stratified, inspectable set of forms:

| stratum | intent |
|---|---|
| high-frequency | top-frequency unresolved forms in the source run |
| shared-by-many | unresolved forms shared by ≥2 models (cross-run) |
| model-specific | unresolved forms occurring in only the source model |
| canonical/resource-supported | forms with a canonical or alternative-resource candidate |
| morphology-derived | forms whose candidates include a canonical lemma with a generated paradigm |
| orthographic-variant | forms with an orthographic candidate |
| no defensible candidate | control: forms with no candidate (tests that the LLM leaves them unchanged) |

Selection is a deterministic stratified pick with exclusion (a form belongs to
one stratum; strata fill in a fixed order; ties broken by form). The chosen
source run and per-stratum counts are recorded in the run meta.

## 6. Execution (external LLM)

The project has **no LLM API integration** (D-007). The pilot therefore
prepares, for each source run:

```
experiments/exp002-pilot/input/<pilot_run_id>/
    original.txt       # complete original translation (byte-for-byte copy)
    candidates.json    # selected forms + full candidate evidence
    prompt.txt         # the COMPLETE revision prompt (template + table + original)
    meta.json          # provenance: source run, candidates, prompt hash, layout
```

The Project Owner / operator sends `prompt.txt` to an LLM and saves the
returned text **byte-for-byte** as:

```
experiments/exp002-pilot/outputs/<pilot_run_id>/revised.txt
```

Raw LLM outputs are experimental artifacts: never modified, cleaned, or
re-encoded. If a transformation is ever required, the original is preserved and
the transformation documented.

## 7. Evaluation (same evaluator)

`scripts/compare_exp002.py` runs `isv-eval` (the **same evaluator commit** as
EXP-001 analysis) on:

1. the original EXP-001 translation (the pilot input copy),
2. the revised EXP-002 output,

and writes per-run before/after comparison:

- lexical token count, exact (A), morph. valid (B), unresolved (C),
  valid coverage, unresolved rate;
- unique unresolved forms before / after;
- forms resolved after revision (C-before that are A/B or absent in revised);
- new unresolved forms introduced by revision (C-after not C-before);
- replacement-specific metrics:
  - supplied candidate forms used (appearing in revised output),
  - supplied candidates accepted by evaluator (A/B in revised),
  - supplied candidates not used,
  - unresolved forms replaced without a supplied candidate (must be 0;
    flagged if not).

No invented quality score.

## 8. Human evaluation

After automated comparison, a small number of **complete before/after text
pairs** are prepared for holistic reading by the Project Owner (naturalness,
Interslavic character). This is qualitative evidence, not automatic ground
truth. No word-by-word annotation task is created.

## 9. Layout (implemented)

```
experiments/exp002-pilot/
    DESIGN.md                  — this document
    prompt_template.txt        — revision prompt template (shared)
    README.md                  — operator instructions (how to execute/evaluate)
    input/<pilot_run_id>/      — prepared immutable input packages (gitignored)
    outputs/<pilot_run_id>/    — revised.txt + meta.json dropped in by operator
    comparison/                — before/after comparison artifacts (gitignored)
```

`<pilot_run_id>` = `exp002__<source_exp001_run_id>`.

## 10. Success criteria

The pilot succeeds if it lets us answer:

1. Can supported alternatives be generated deterministically? (A)
2. Can they be supplied in a complete-document revision task? (pipeline)
3. Does the revised output measurably reduce unresolved vocabulary?
4. Does it avoid introducing *additional* unresolved vocabulary?
5. Does the model preserve meaning/structure well enough to justify a larger
   EXP-002?
6. Which categories of unresolved forms are worth sending through the
   mechanism?

No assumption that the answer is yes. The pilot stops after preparing inputs,
executing externally, and reporting evidence.

## 11. Out of scope

No UI, database, web service, general-purpose translator, LLM API client,
synonym ranking system, language-origin classifier, or production pipeline.
No modification of Experiment 001 data.
