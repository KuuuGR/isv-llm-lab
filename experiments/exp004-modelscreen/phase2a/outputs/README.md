# Phase 2A outputs (EXP-004)

Artifacts in this directory are **gitignored** (raw collected outputs are
copyrighted material and must stay local; D-035 never-modify discipline).
This README is committed.

| file | written by | content |
|---|---|---|
| `plan.json` | `prepare` | the 36-run Phase-2A plan (18 configurations × p2a-ctl / p2a-primed): run ids, conditions, prompt file + hash, baseline run id, corpus + source hashes. Task 021: `extend-exploratory` appended the two Dola 3.8 exploratory `p2a-primed` rows (`baseline_run_id: null`) → 38 rows |
| `<run_id>/output.txt` | `collect` / `collect-session` / `collect-msg2` | the model's raw reply, byte-for-byte, never modified. Task 021: `collect-msg2` registered the 20 primed runs from the author's `*-msg2.md` prompt+reply files (reply sliced at the final `## Output` marker) |
| `<run_id>/meta.json` | `collect` / `collect-session` / `collect-msg2` | condition, status, access verdict, hashes, session checks. `collect-msg2` records `machine_same_session_proof: false` (msg2-only record; see `../README.md`, Task 021 collection record) |
| `<run_id>/intake.json` | `verify` | completeness-gate verdict + integrity checks |
| `<run_id>/evaluation.json` + `evaluation/` | `evaluate` | Task 008 evaluator metrics (canonical/broader/unresolved, A/B/C) |
| `<run_id>/orthography.json` | `evaluate` | orthographic audit (official Interslavic alphabet) |
| `roster.json` / `roster.md` | `roster` | joined per-run evidence (no composite score). Task 021: 38 rows — 19 complete, 1 partial (run 12 end-marker), 18 controls not collected |
| `compare.json` / `compare.md` | `compare` | primed-vs-baseline per-dimension deltas (no ranking). Task 021: 18 configurations compared; the two Dola rows have no baseline and report no-baseline (no priming effect claimed) |
