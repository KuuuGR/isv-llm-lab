# EXP-003 — operator prompts

One self-contained Markdown file per (model, condition). **No manual assembly
is needed**: each file contains the experiment header, the complete
instructions, the full Polish source story, and (for B/C/D) the lexical
scaffold block with alternatives and grammar annotations where applicable.

## Files

| File | Model | Condition | Paste into |
|---|---|---|---|
| `01-chatgpt-A.md` | ChatGPT | A — direct baseline | ChatGPT |
| `02-chatgpt-B.md` | ChatGPT | B — lexical scaffold | ChatGPT |
| `03-chatgpt-C.md` | ChatGPT | C — scaffold + alternatives | ChatGPT |
| `04-chatgpt-D.md` | ChatGPT | D — scaffold + alternatives + grammar | ChatGPT |
| `05-claude-A.md` | Claude | A — direct baseline | Claude |
| `06-claude-B.md` | Claude | B — lexical scaffold | Claude |
| `07-claude-C.md` | Claude | C — scaffold + alternatives | Claude |
| `08-claude-D.md` | Claude | D — scaffold + alternatives + grammar | Claude |
| `09-bielik-A.md` | Bielik | A — direct baseline | Bielik |
| `10-bielik-B.md` | Bielik | B — lexical scaffold | Bielik |
| `11-bielik-C.md` | Bielik | C — scaffold + alternatives | Bielik |
| `12-bielik-D.md` | Bielik | D — scaffold + alternatives + grammar | Bielik |

## How to execute one run

```text
1. Open operator-prompts/<file>.md.
2. Copy the entire file.
3. Paste it into the specified model.
4. Save the model's complete reply byte-for-byte (no cleaning, no trimming).
5. If the model refuses or truncates the reply, save the partial reply and
   record the failure exactly as it happened — do not shorten the prompt.
6. Register the reply with the collect step (see the experiment README).
```

## Prompt-control policy

- The four prompts for one model are byte-identical except the condition
  content: A has no scaffold block; B/C/D share one scaffold-block template,
  with C and D adding one sentence each about alternatives and grammar
  annotations.
- No prompt contains model-specific linguistic advice, baseline scores, or
  information about any other model.
- Every prompt asks for the complete Interslavic translation only.

## Bielik context size

The scaffolded prompts are long: the D prompt is about 95 KB of text. Bielik's
context window is small (known from EXP-001). If Bielik cannot process a full
prompt, **stop that run and record the failure** (keep the partial reply) —
do not silently shorten the experiment to make it fit.

## Provenance and reproducibility

- Generated deterministically by `scripts/package_exp003_prompts.py` from the
  committed `prompt_template.txt` + the cleaned story source + the rendered
  scaffold blocks. Regenerating is byte-identical (no timestamps).
- `manifest.json` records the generator commit, the source hash, the scaffold
  block hashes, and every file's prompt-text and output SHA-256, with model /
  provider / version per file.
- The `.md` files embed the copyrighted Polish story and are therefore
  **gitignored** — they stay local. Only this README and `manifest.json` are
  committed.
