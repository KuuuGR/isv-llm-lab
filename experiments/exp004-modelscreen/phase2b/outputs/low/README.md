# Phase 2B LOW-overlap — outputs (gitignored except this README)

Deterministic plan/checklist artifacts produced by:

```bash
.venv/bin/python scripts/run_exp004_phase2b.py prepare \
  --regime low --date 2026-09-15
```

**Status (2026-09-15): generated and validated** for frozen LOW story
`podklady` v1.

| Artifact | Role |
|---|---|
| `plan.json` | 42-run LOW plan (`…__p2b-low__…`); source/corpus SHA-256; no model output |
| `collection-checklist.md` | human collection checklist |

- Source: `podklady` v1, SHA-256
  `ce1c4fca03fe9cb2c5f8181ab45c91767759a0c785f0a066543d95bc32f5271b`
- Corpus: `phase2a-authentic-isv` v1, SHA-256
  `aaad28e43935a40313585d77a33bfc788d97e8d69b081f9486af74d52ca1a857`
- Prompt manifest (committed): `../operator-prompts/manifest-low.json`

This directory is **separate from** the HIGH plan at `../plan.json`.
Do not mix HIGH and LOW run ids. No LLM sessions have been executed for
LOW.
