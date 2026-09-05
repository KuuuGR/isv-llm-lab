# EXP-004 — outputs

Immutable raw LLM outputs and their metadata. One directory per run:

```
outputs/<run_id>/
  output.txt          raw model reply, stored byte-for-byte, never modified
  meta.json           run metadata (provider/model/version/settings,
                      generation date, prompt/source hashes, output SHA-256,
                      status, access filter verdict, resource pins)
  intake.json         completeness-gate result (verdict complete/partial/
                      failed + checks + reasons; L-027)
  evaluation.json     Task 008 evaluator summary (+ evaluation/ detail);
                      carries 'usable' = (intake verdict complete)
  orthography.json    Task 015 character-level orthographic audit
  evaluation.md       human-readable metric table
```

`<run_id>` = `<date>__<provider>__<model>__<model_version>__direct`
(variant settings such as `thinkoff`/`deepthinkon` are part of
`model_version`; the Phase 1 condition token is always `direct`). Raw
outputs embed the copyrighted story's translation and are **gitignored** —
they stay local.

- `plan.json` — the fixed Phase 1 roster (11 candidate rows), written by
  `scripts/run_exp004_phase1.py prepare`.
- `roster.json` / `roster.md` — screening summary (coverage pair, unresolved
  rate, orthography, access verdict, usability per row; no ranking, no
  composite score), written by `scripts/run_exp004_phase1.py roster`.
- Failed, partial, or refused runs are preserved and documented in
  `meta.json` + `intake.json`; they are never silently deleted, repaired,
  or overwritten (D-023, D-035, L-027).
