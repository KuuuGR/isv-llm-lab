# Experiment 001 — Manual Audit Sample of Unresolved Forms

This directory prepares **evidence** for the manual linguistic inspection of the
unresolved forms produced by Experiment 001. It is a follow-up analysis of
**EXP-001**, not a new translation experiment.

**The sample was built without any automatic linguistic-origin classification.**
The central question — *are the unresolved forms mostly genuine
non-Interslavic vocabulary, or are we measuring limitations of our current
resources/evaluator?* — is left to the Project Owner / Architect to answer by
inspecting the actual forms and contexts in this worksheet.

## Source data (read-only)

- `../outputs/comparison.json` — cross-model unresolved overlap (form table)
- `../outputs/*/unresolved.json` — per-run unresolved records (sentence
  context, candidate lemmas, review metadata)

None of these files are modified by this task.

## What the sample contains

`sample.csv` (human worksheet) and `sample.json` (full detail) contain
**100 stratified forms + 8 diagnostic forms** in six groups:

| Group | n | Selection rule |
|---|---|---|
| `A` — high-frequency | 25 | Highest total frequency across all models (names excluded) |
| `B` — shared | 25 | Appear in 2–6 models, prioritized by number of models, then frequency |
| `C` — model-specific | 25 | Appear in exactly 1 model, spread across all seven conditions |
| `D` — diverse/edge | 15 | Feature-bucketed: diacritic variants of known lexicon forms, zero-candidate forms, etymological characters, long forms, many candidate lemmas |
| `E` — proper names | 10 | Story name families (Bronisława, Teofil, Julianna, Przemysława, Antoni, Międzyrzecze) spanning orthographic/case variants |
| `SHARED_ALL` — appendix | 8 | The forms unresolved in **all seven** models (diagnostic section) |

Selection is deterministic (`scripts/sample_exp001_audit.py`, fixed seed for
tie-breaking); run the script to reproduce the artifacts.

## The "shared by all models" appendix

The 8 forms unresolved by all seven conditions are `bojala`, `bojati`,
`bronislava`, `dokazano`, `pui`, `pul`, `rekla`, `teofil`. Preserved context
shows they include character names (`Bronislava`, `Teofil`), the story's
quoted in-text example words (`pul` / `pui`), and inflected verb forms used by
every output (`bojala`/`bojati`, `dokazano`, `rekla`). Their universality is
most plausibly explained by story content rather than by models converging on
errors — but this observation is recorded without classifying the forms.

## Per-form fields

For every form the artifacts record:

- `form`, `normalized_form`, `models`, `model_count`, `total_frequency`,
  `frequency_per_model` (e.g. `ChatGPT×4; Gemini×2; …`)
- `sentence_context` — one original, unmodified sentence per model where the
  form occurs (in `sample.json`), plus `sentence`/`sentence_model`/`sentence_id`
  for the highest-frequency model in `sample.csv`
- `candidate_lemmas` (from the evaluator's B-fallback candidate search) and
  `candidate_lemma_count`
- `candidate_forms` — **empty**. The evaluator does not emit candidate *forms*
  for unresolved tokens; it records candidate *lemmas* only. See
  `../outputs/*/tokens.json` for the raw records.
- `classification: "C"` and `review: true` are implied for all rows
  (unresolved by definition)
- every occurrence with its full sentence context is listed in `sample.json`
  under `occurrences` (model, run id, sentence, sentence id, position,
  candidates)

## Using the worksheet

`sample.csv` is meant to be annotated in a spreadsheet. The last three columns
are blank for the human reviewer:

| Column | Purpose |
|---|---|
| `human_class` | one label from the proposed vocabulary below (or `OTHER`) |
| `human_notes` | free-text evidence / reasoning |
| `confidence` | e.g. low / medium / high |

Proposed label vocabulary (for the human reviewer; not populated automatically):

```
VALID_ISV
VALID_ISV_VARIANT
EVALUATOR_MISS
PROPER_NAME
FOREIGN_SLAVIC
POLISH
OTHER
UNKNOWN
```

Do **not** treat `FOREIGN_SLAVIC` as an automatic category — even if a form
looks obviously Russian / Czech / Serbian / etc., the judgment belongs to the
human reviewer.

## Methodological notes

- No LLM or heuristic classifier was used to judge form origin; no external
  dictionaries were queried to produce a classification.
- The "proper name" grouping (group `E`) uses the explicit name families that
  occur in the Polish source story, matched against normalized forms; it is an
  orthographic/identity grouping, not a language classification.
- Model versions, generation dates and prompts for all seven conditions are
  `unknown` (recorded in the run `meta.json` files); this does not affect the
  unresolved-form evidence.
- Raw file sizes are recorded for input integrity only and are not a
  translation-length metric (see `docs/EXPERIMENTS.md`, Task 003.1).

## Artifacts

| File | Contents |
|---|---|
| `sample.csv` | Human audit worksheet (one row per form, blank annotation columns) |
| `sample.json` | Machine-readable sample with full per-occurrence context |
| `statistics.json` | Descriptive statistics of the whole unresolved dataset |
| `README.md` | This file |
