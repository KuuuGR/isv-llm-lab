# EXP-003 — generation-time lexical scaffolding (controlled pilot)

Tests whether supplying an LLM with a deterministic Polish→Interslavic
**lexical scaffold** at generation time improves Interslavic lexical
correctness while preserving natural language, compared with unconstrained
direct translation of the same source by the same model. **Distinct from
EXP-002** (post-hoc revision of an existing translation): here the Polish
source is the starting point and the scaffold is vocabulary guidance *during*
generation — there is **no hidden intermediate LLM translation**.

- Design: `DESIGN.md` (SODA Task 009, approved).
- Status (2026-09-05): **executed externally — intake and preliminary
  analysis done (Task 011); 8 of 12 runs complete** (ChatGPT A–D, Claude A–D);
  Bielik A–D incomplete/failed, preserved as qualitative artifacts. The
  holistic complete-text human review (Task 012) was attempted and
  **superseded as too cognitively demanding (Task 014, D-038)** — no holistic
  result was obtained; the artifact is preserved as historical with a
  superseded banner. The primary human-evaluation exercise is now a
  **sentence-level forced-choice test (Task 014)**:
  `comparison/sentence_review.md` — 100 questions (each: one Polish source
  sentence + the corresponding sentence from the four conditions of the same
  model, randomized into "Version 1..4"), prepared deterministically
  (`scripts/prepare_exp003_sentence_review.py`), with the private mapping in
  `comparison/sentence_review_key.json`. **No answers exist yet; the test
  awaits the Project Owner.** EXP-003 is closed to new runs; the next step is
  the human test, then the EXP-003 report. EXP-004 remains design-only.

## Conditions and models

Conditions (nested information; no assumed ordering of outcomes):

| Condition | What the model receives |
|---|---|
| A | Polish source → direct Interslavic translation (within-experiment baseline) |
| B | + lexical scaffold, one canonical candidate per form |
| C | + multiple resource-supported alternatives |
| D | + reliable grammatical annotations (dictionary POS, verb aspect, a few generated example forms) |

Models (first wave): **ChatGPT, Claude, Bielik** — 4 conditions × 3 models =
12 runs.

## Pipeline

```text
python scripts/build_exp003_scaffold.py clean-source    # register story-only source (once)
python scripts/build_exp003_scaffold.py build --force   # deterministic scaffold (once)
python scripts/package_exp003_prompts.py                # 12 operator prompts (once)
python scripts/run_exp003_pilot.py prepare --date YYYY-MM-DD
```

The scaffold generator is **deterministic and contains no hidden LLM calls**
(D-029). The only LLM calls in the experiment are the externally executed
translation conditions.

## How the experiment was executed (historical record — completed in Task 011)

```text
1. For each of the 12 files in operator-prompts/:
     open the file → copy everything → paste into the target model.
2. Save the model's complete reply byte-for-byte (no cleaning, no trimming).
3. If a model refuses or truncates the reply (Bielik's context window is
   small — known from EXP-001), STOP that run, keep the partial reply, and
   record the failure exactly. Do not silently shorten the prompt.
4. Register each reply:
     python scripts/run_exp003_pilot.py collect \
       --run <run_id from outputs/plan.json> --output /path/to/reply.txt
5. Evaluate:
     python scripts/run_exp003_pilot.py evaluate --run <run_id>   # per run
6. Compare:
     python scripts/compare_exp003.py
7. Verify integrity:
     python scripts/verify_exp003_runs.py
```

Raw outputs are stored byte-for-byte and never overwritten (D-023). The
comparison writes per-run analyses, within-model and within-condition
pairwise comparisons (token-aligned transitions, A→C/B→C regressions,
candidate usage, invented-forms proxy), and **blinded complete-text
human-review pairs** (`comparison/human_review.md`; automatic metrics hidden;
the label mapping is in `comparison/human_review_key.json`).

## What is local (gitignored) vs committed

- **Local (gitignored):** `input/` (story), `scaffolds/` (aligned story token
  stream), `outputs/` (raw model outputs), `comparison/` (raw texts), and the
  `operator-prompts/*.md` files (they embed the copyrighted story). These
  follow the repository's copyright policy.
- **Committed:** design, `prompt_template.txt`, the per-story **curation
  tables** (`curation/op-pl/`) — the explicit, provenance-bearing residual
  mappings that make the scaffold reproducible (D-032), all scripts, tests,
  and this README.
