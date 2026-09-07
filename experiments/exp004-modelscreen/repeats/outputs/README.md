# Phase-repeat outputs (EXP-004, SODA Task 025)

Artifacts in this directory are **gitignored** (raw collected outputs are
copyrighted material and must stay local; D-035 never-modify discipline).
This README is committed.

| file | written by | content |
|---|---|---|
| `plan.json` | `prepare` | the 120-run phase-repeat plan (18 primary configurations + 2 exploratory Dola × direct/primed × r01–r03): run ids, condition, replicate, primary/exploratory flags, prompt files + hashes, source/corpus hashes, Phase-1 baseline + Phase-2A primed run links, generation-date. Deterministic output of `scripts/run_exp004_repeats.py prepare --date 2026-09-08` |
| `collection-checklist.md` | `prepare` | human collection checklist in replicate-block order (per configuration: r01 direct+primed → r02 → r03), with run ids + condition/replicate labels — makes omissions, duplicates, direct/primed confusion and exploratory/primary mixing impossible |
| `<run_id>/output.txt` | `collect-msg2` / `collect-session` | the model's raw reply, byte-for-byte, never modified |
| `<run_id>/meta.json` | `collect-msg2` / `collect-session` | condition, replicate, primary/exploratory, status, access verdict/note, interface settings, hashes (prompt/source/corpus/output/session), collection time, session record checks (msg2-style flag, contamination checks, corpus anchors) |
| `<run_id>/intake.json` | `verify` | completeness-gate verdict (complete/partial/failed) + integrity checks (hash re-checks vs plan/meta) |
| `<run_id>/evaluation.json` | `evaluate` | Task-008 evaluator metrics (canonical/broader/unresolved, A/B/C, token counts) — definitions unchanged from Phase 1/2A |
| `<run_id>/orthography.json` | `evaluate` | orthographic audit (official Interslavic alphabet, anomaly buckets) |
| `roster.json` / `roster.md` | `roster` | joined per-run evidence table (per-dimension only — no composite score). Rows carry `usable` + metrics only after evaluation |
| `analysis/` (sibling dir) | `analyze_exp004_repeats.py` | deterministic repeated-generation analysis (dataset/analysis JSON+MD, figures A–E) — no-results scaffold until usable observations exist |

Rules: a run is never overwritten; `prepare --force` is safe ONLY before
any collection (after collection it invalidates recorded run ids/session
hashes); an unusable run is preserved + marked with the reason, and a
re-run receives a NEW run id.
