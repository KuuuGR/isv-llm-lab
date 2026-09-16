# Phase 2B HIGH vs LOW — cross-regime synthesis

Derived / committed synthesis artifacts for the exploratory descriptive
comparison of Phase 2B HIGH-overlap and LOW-overlap priming results.

**Not** a causal test. **Not** a model ranking. **Does not** overwrite
HIGH or LOW primary aggregates.

## Contents

| file | content |
|---|---|
| `analysis.json` | machine-readable matched tables, stability classes, mechanisms, conclusions |
| `analysis.md` | human-readable synthesis (Analyses 1–5 + conclusion layers) |
| `EVIDENCE.md` | article-ready fact / interpretation / not-established record |
| `README.md` | this file |

## Scope

- HIGH: 7 configurations / 42 runs (published FULL aggregate retained for
  reference).
- LOW primary: **6 valid** configurations (Qwen excluded as
  `INVALID — MODEL MISMATCH`).
- Primary cross-regime comparison: **matched 6** configurations.
- Qualitative: HIGH + LOW audits; Qwen/Gemini infrastructure notes kept
  separate from linguistic findings.

## Method

Manual / scripted synthesis from existing:

- `phase2b/analysis/{dataset,analysis}.{json,md}`
- `phase2b/analysis/low/{dataset,analysis}.{json,md}`
- `phase2b/QUALITATIVE_AUDIT.md` + `phase2b/qualitative_audit.json`
- `phase2b/analysis/low/QUALITATIVE_AUDIT.md` + `qualitative_audit.json`
- `phase2b/analysis/low/QWEN_INCIDENT.md`

No LLM sessions. No frozen story/corpus edits. No HIGH/LOW primary overwrite.

## Constraints

- n = 3 descriptive only; no significance tests.
- Do not cite historical Qwen LOW −12.08 pp as priming.
- Do not treat matched aggregate Δ difference (+1.14 pp) as meaningful alone.
- UNSEEN remains unexecuted.
