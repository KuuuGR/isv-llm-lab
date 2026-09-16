# Phase 2B UNSEEN-domain — outputs (plan / checklist)

Deterministic plan/checklist artifacts produced by:

```bash
python scripts/run_exp004_phase2b.py prepare \
  --regime unseen --date 2026-09-16
```

**Status (2026-09-16): kit prepared; no sessions executed** for frozen
UNSEEN source `exercise-2-2-voice-biophysics` v1.

| Artifact | Role |
|---|---|
| `plan.json` | 42-run UNSEEN plan (`…__p2b-unseen__…`); source/corpus SHA-256; no model output |
| `collection-checklist.md` | human collection checklist (also mirrored at `../operator-prompts/collection-checklist-unseen.md`) |

- Source: `exercise-2-2-voice-biophysics` v1, SHA-256
  `cd3bfb9a819b415e3cfb382e0737ba22540ccb679d0d34983c40dfbf89a9f7f4`
- Corpus: `phase2a-authentic-isv` v1, SHA-256
  `aaad28e43935a40313585d77a33bfc788d97e8d69b081f9486af74d52ca1a857`
- Prompt manifest (committed): `../operator-prompts/manifest-unseen.json`

This directory is **separate from** HIGH (`../plan.json`) and LOW
(`../low/`). Do not mix regimes. No LLM sessions have been executed for
UNSEEN.
