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

## Planned (not started)

- **EXP-002 — Constrained generation (documented in DESIGN.md, not implemented).**

