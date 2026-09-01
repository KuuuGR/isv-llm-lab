# EXP-003 — outputs

Immutable raw LLM outputs and their metadata. One directory per run:

```
outputs/<run_id>/
  output.txt          raw model reply, stored byte-for-byte, never modified
  meta.json           run metadata (condition, model, provider, version,
                      generation date, prompt/source/scaffold hashes,
                      output SHA-256, resource pins, status)
  evaluation.json     Task 008 evaluator summary (+ evaluation/ detail)
  evaluation.md       human-readable metric table
```

`<run_id>` = `<date>__<provider>__<model>__<model_version>__<condition>`
(condition lowercase). Raw outputs embed the copyrighted story's
translation and are **gitignored** — they stay local.

- `plan.json` — the 12 planned (model × condition) runs, written by
  `scripts/run_exp003_pilot.py prepare`.
- Failed or empty runs are preserved and documented in `meta.json`; they are
  never silently deleted or overwritten (D-023).
