# EXP-004 — outputs

Immutable raw LLM outputs and their metadata. One directory per run:

```
outputs/<run_id>/
  output.txt          raw model reply, stored byte-for-byte, never modified
  meta.json           run metadata (provider/model/version/settings,
                      generation date, prompt/source hashes, output SHA-256,
                      status, access filter verdict, session provenance,
                      resource pins)
  intake.json         completeness-gate result (verdict complete/partial/
                      failed + checks + reasons; L-027)
  evaluation.json     Task 008 evaluator summary (+ evaluation/ detail);
                      carries 'usable' = (intake verdict complete)
  orthography.json    Task 015 character-level orthographic audit
  evaluation.md       human-readable metric table
```

`<run_id>` = `<date>__<provider>__<model>__<model_version>__direct`
(variant settings such as `thinkoff`/`deepthinkon`/`extthinkon`/`fast` are
part of `model_version`; the Phase 1 condition token is always `direct`).
Raw outputs embed the copyrighted story's translation and are **gitignored**
— they stay local.

- `plan.json` — the reconciled executed roster (19 concrete runs, Task 018),
  written by `scripts/run_exp004_phase1.py prepare --date 2026-09-06`. The
  original planned 11-row package (Task 017) is reproducible from the same
  command; the committed `operator-prompts/manifest.json` records the
  canonical prompt hashes of the executed set. **Task 022 (2026-09-07):
  `extend-direct --date 2026-09-07` appended two exploratory Phase-1
  DIRECT rows for Dola 3.8 Fast/Pro (run ids
  `…__bytedance__dola-3.8__fast|pro__direct`, status
  `pending_manual_collection`, `exploratory: true`)**. **Task 023
  (2026-09-07): both baselines were executed by the author and collected
  through the Phase-1 `collect-session` intake (msg2-style records — the
  raw reply lives inside the canonical operator prompt file, which is the
  session record); they passed `verify` (verdict `complete`, usable) and
  were evaluated, so the two Dola rows now have real
  `intake.json`/`evaluation.json`/`orthography.json` under `outputs/` and
  no longer report a pending status.** The original 18 usable baselines
  are unchanged.
- `roster.json` / `roster.md` — Phase 1 evidence table (access verdict,
  intake, usability, canonical/broader coverage, unresolved rate, token
  count, orthography-out count per row; no ranking, no composite score),
  written by `scripts/run_exp004_phase1.py roster`.
- `orthography_report.json` / `.md` — experiment-wide character-level
  orthography report (`scripts/check_orthography.py --experiments exp004`).

Status of the executed set (Task 018): **19 collected runs; 18 intake
`complete` and evaluated (usable); 1 failed (GLM 4.5 — service-error
artifact, excluded from quantitative evaluation exactly as the intake
protocol specifies).** Failed/partial/refused runs are preserved and
documented in `meta.json` + `intake.json`; they are never silently deleted,
repaired, or overwritten (D-023, D-035, L-027).
