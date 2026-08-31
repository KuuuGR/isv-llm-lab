# EXP-002 Pilot — operator instructions

This directory implements the **dictionary-guided revision pilot** (SODA
Task 006): for each of the seven EXP-001 translations, unresolved words are
given deterministic, evidence-backed Interslavic alternatives; an external LLM
revises the **complete** translation using only the supplied alternatives; and
the revised output is evaluated with the **same** `isv-eval` evaluator.

The project has **no LLM API integration** by design (D-007), so LLM execution
is external. Everything here prepares, records, and evaluates that external
execution; nothing fabricates LLM output.

## Status

All seven input packages are prepared:

| pilot run | source EXP-001 run |
|---|---|
| `exp002__2026-08-31__anthropic__claude__unknown` | Claude |
| `exp002__2026-08-31__deepseek__deepseek__unknown` | DeepSeek |
| `exp002__2026-08-31__google__gemini__unknown` | Gemini |
| `exp002__2026-08-31__openai__chatgpt__unknown` | ChatGPT |
| `exp002__2026-08-31__openai__gpt-isvt__unknown` | GPTs Interslavic Teacher |
| `exp002__2026-08-31__unknown__bielik__unknown` | Bielik |
| `exp002__2026-08-31__unknown__grok__unknown` | Grok |

`scripts/run_exp002_pilot.py status` always reflects the live state.

## Layout

```
DESIGN.md                  — experiment specification (read first)
prompt_template.txt        — revision prompt template (shared by all runs)
input/<pilot_run_id>/      — immutable input package per source run:
    original.txt               complete original translation (byte-for-byte)
    candidates.json            selected forms + full candidate evidence
    prompt.txt                 THE complete revision prompt to send to an LLM
    meta.json                  provenance: source run, hashes, selection, layout
outputs/<pilot_run_id>/    — created by `collect`:
    revised.txt                raw LLM reply, stored byte-for-byte
    meta.json                  revision metadata (model/provider/version/date)
comparison/<pilot_run_id>/ — created by `compare`:
    before/  after/            isv-eval artifacts (report/tokens/unresolved)
    comparison.json / .md      before/after metrics + replacement bookkeeping
comparison/comparison.md   — summary across runs
comparison/human_review.md — complete before/after text pairs (holistic reading)
```

Input packages, revised outputs, and comparison artifacts embed raw model
output and are **gitignored** (`.gitignore`).

## Reproduce the input packages

```bash
# all seven source runs
python scripts/run_exp002_pilot.py prepare --all

# a single source run
python scripts/run_exp002_pilot.py prepare --source-run 2026-08-31__openai__chatgpt__unknown
```

Packages are deterministic: regenerating yields byte-identical files (only the
`prepared_at` timestamp differs). Existing packages are never overwritten.

## Execute externally

1. Pick a pilot run.
2. Send `input/<pilot_run_id>/prompt.txt` to the LLM **as one complete
   document**. Do not split the story.
3. Save the returned text **byte-for-byte** (no cleaning, no markdown
   stripping) to a file, e.g. `revision.txt`.
4. Register it:

```bash
python scripts/run_exp002_pilot.py collect \
    --pilot-run exp002__2026-08-31__openai__chatgpt__unknown \
    --revised revision.txt \
    --model chatgpt --provider openai \
    --model_version unknown --generation_date unknown
```

`collect` verifies the file is non-empty, copies it byte-for-byte, records the
SHA-256 and the revision metadata (unknowns stay `unknown`), and **refuses to
overwrite** an existing revision.

## Evaluate

```bash
python scripts/run_exp002_pilot.py compare                      # all runs
python scripts/run_exp002_pilot.py compare --pilot-run <id>    # one run
```

This runs the same `isv-eval` evaluator as EXP-001 on the original and the
revised text and writes the before/after comparison plus a human-review doc
with complete before/after pairs for holistic Project-Owner reading.

## Integrity rules

- Raw LLM outputs are experimental artifacts: never modified, cleaned, or
  re-encoded. If a transformation is ever required, preserve the original and
  document it.
- Original EXP-001 outputs are never touched.
- The dictionary remains the canonical lexical source; candidates are evidence,
  not judgments, and no candidate is invented.
