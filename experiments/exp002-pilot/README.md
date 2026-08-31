# EXP-002 Pilot — operator instructions

This directory implements the **dictionary-guided revision pilot** (SODA
Task 006): for each of the seven EXP-001 translations, unresolved words are
given deterministic, evidence-backed Interslavic alternatives; an external LLM
revises the **complete** translation using only the supplied alternatives; and
the revised output is evaluated with the **same** `isv-eval` evaluator.

The project has **no LLM API integration** by design (D-007), so LLM execution
is external. Everything here prepares, records, and evaluates that external
execution; nothing fabricates LLM output.

## Execute one condition (no manual prompt assembly)

For each condition, the operator file is a **complete self-contained prompt**
under `experiments/exp002-pilot/operator-prompts/`:

```text
1. Open operator-prompts/<file>.md
2. Copy the entire file.
3. Paste it into the specified LLM (the file says which).
4. Save the model's complete reply byte-for-byte (no cleaning).
5. Register it:
   python scripts/run_exp002_pilot.py collect \
       --pilot-run <pilot_run_id> \
       --revised <saved_reply_file> \
       --model <model> --provider <provider> \
       --model_version unknown --generation_date unknown
6. Evaluate:
   python scripts/run_exp002_pilot.py compare
```

You never need to open `source.txt`/`original.txt`, `candidates.json`,
`meta.json`, or `prompt_template.txt` to run the pilot. The mapping of
operator files to conditions and pilot run ids is in
`operator-prompts/README.md`.

## Status

**EXECUTED AND ANALYZED (Task 006.2, 2026-08-31).** All seven conditions were
run externally and compared; the final report is [`REPORT.md`](REPORT.md). The
pilot packages remain as prepared below.

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
REPORT.md                  — final report: results, regressions, discrepancy, recommendation
prompt_template.txt        — revision prompt template (shared by all runs)
operator-prompts/          — ONE self-contained Markdown prompt per condition
    README.md                  usage + mapping (committed)
    manifest.json              generator commit + per-file SHA-256s (committed)
    01-chatgpt.md … 07-grok.md  complete prompts (gitignored: embed model output)
input/<pilot_run_id>/      — immutable input package per source run:
    original.txt               complete original translation (byte-for-byte)
    candidates.json            selected forms + full candidate evidence
    prompt.txt                 THE complete revision prompt (what the .md files embed)
    meta.json                  provenance: source run, hashes, selection, layout
outputs/<pilot_run_id>/    — created by `collect`:
    revised.txt                raw LLM reply, stored byte-for-byte
    meta.json                  revision metadata (model/provider/version/date)
comparison/<pilot_run_id>/ — created by `compare`:
    before/  after/            isv-eval artifacts (report/tokens/unresolved)
    comparison.json / .md      before/after metrics + transition matrix +
                               per-form candidate usage
comparison/comparison.md   — summary across runs
comparison/human_review.md — 5 complete before/after text pairs (holistic reading)
```

Input packages, revised outputs, comparison artifacts, and the operator `.md`
prompts embed raw model output and are **gitignored** (`.gitignore`).

## Regenerate the input packages

```bash
# all seven source runs
python scripts/run_exp002_pilot.py prepare --all

# a single source run
python scripts/run_exp002_pilot.py prepare --source-run 2026-08-31__openai__chatgpt__unknown
```

Packages are deterministic: regenerating yields byte-identical files (only the
`prepared_at` timestamp differs). Existing packages are never overwritten.

## Regenerate the operator prompts

```bash
python scripts/package_operator_prompts.py
```

Reads the prepared `input/<run>/prompt.txt` files and rewrites the seven
`operator-prompts/*.md` files plus `manifest.json`. Byte-identical on rerun
(no timestamps). It never changes candidate selection or the 30 selected
forms.

## Execute externally (what the operator files are for)

1. Pick a condition and open its file in `operator-prompts/`.
2. Copy the **entire** file and paste it into the specified LLM as one
   complete document. Do not split the story.
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
- The operator files exist for usability only: packaging them changed nothing
  about candidate selection, generation rules, the selected forms, or the
  evaluator (verified byte-identical selection; see Task 006.1 report).
