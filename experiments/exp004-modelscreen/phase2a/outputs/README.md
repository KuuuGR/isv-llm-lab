# Phase 2A outputs (EXP-004)

Artifacts in this directory are **gitignored** (raw collected outputs are
copyrighted material and must stay local; D-035 never-modify discipline).
This README is committed.

| file | written by | content |
|---|---|---|
| `plan.json` | `prepare` | the 36-run Phase-2A plan (18 configurations × p2a-ctl / p2a-primed): run ids, conditions, prompt file + hash, baseline run id, corpus + source hashes |
| `<run_id>/output.txt` | `collect` / `collect-session` | the model's raw reply, byte-for-byte, never modified |
| `<run_id>/meta.json` | `collect` / `collect-session` | condition, status, access verdict, hashes, session checks |
| `<run_id>/intake.json` | `verify` | completeness-gate verdict + integrity checks |
| `<run_id>/evaluation.json` + `evaluation/` | `evaluate` | Task 008 evaluator metrics (canonical/broader/unresolved, A/B/C) |
| `<run_id>/orthography.json` | `evaluate` | orthographic audit (official Interslavic alphabet) |
| `roster.json` / `roster.md` | `roster` | joined per-run evidence (no composite score) |
| `compare.json` / `compare.md` | `compare` | primed-vs-baseline per-dimension deltas (no ranking) |
