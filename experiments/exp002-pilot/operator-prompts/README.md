# EXP-002 Pilot — operator prompts

One self-contained Markdown file per condition. **No manual assembly is
needed**: each file contains the full revision instructions, the complete
original EXP-001 translation, and the candidate table with provenance.

## How to execute (one condition)

```text
1. Open operator-prompts/<file>.md
2. Copy the entire file.
3. Paste it into the specified LLM.
4. Save the model's complete reply byte-for-byte (no cleaning).
5. Register it with the collect script (see the pilot README).
6. Run the comparison.
```

## Files

| File | Condition | Paste into |
|---|---|---|
| `01-chatgpt.md` | ChatGPT | ChatGPT |
| `02-gpt-isv-teacher.md` | GPTs — Interslavic / Medžuslovjansky Language Teacher | that GPTs chat |
| `03-gemini.md` | Gemini | Google Gemini |
| `04-claude.md` | Claude | Anthropic Claude |
| `05-deepseek.md` | DeepSeek | DeepSeek |
| `06-bielik.md` | Bielik | Bielik |
| `07-grok.md` | Grok | xAI Grok |

## Provenance and reproducibility

- Generated deterministically by `scripts/package_operator_prompts.py` from
  the prepared input packages (`experiments/exp002-pilot/input/<run>/prompt.txt`).
  Regenerating is byte-identical (no timestamps); `manifest.json` records the
  generator commit and every file's SHA-256.
- The packaging script reads only the prepared input packages; it does not
  change candidate selection, the selected 30 forms, EXP-001 outputs, the
  dictionary, or the evaluator.
- The `.md` files embed the complete original EXP-001 translation (model
  output) and are therefore **gitignored** — they stay local. Only this
  README and `manifest.json` are committed.
