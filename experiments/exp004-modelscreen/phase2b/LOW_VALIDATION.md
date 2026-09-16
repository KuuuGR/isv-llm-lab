# Phase 2B LOW — preparation / validation report

**Date:** 2026-09-15  
**Boundary decision:** **APPROVED** (human operator)  
**Story freeze:** **v1 frozen** — exact approved clean-prose bytes  
**42-run kit:** **READY** (prepared + validated; no LLM sessions)

HIGH artifacts and the authentic ISV corpus were not modified.
`InterslavicTesty.md` was not modified.

---

## Boundary approval (recorded)

| Field | Value |
|---|---|
| Decision | **APPROVE** |
| First story line | starts `Katarzyna odłożyła teczkę…` (bank L1107) |
| Last story line | starts `I po raz pierwszy od lat pomyślała…` (bank L1247) |
| Story lines | 141 |
| Story bytes | 15 249 |
| SHA-256 | `ce1c4fca03fe9cb2c5f8181ab45c91767759a0c785f0a066543d95bc32f5271b` |
| Internal contamination | PASS |
| HIGH leakage sanity check | PASS |

---

## Kit locations

| Artifact | Path |
|---|---|
| Frozen story v1 | `input/versions/podklady-v1.txt` |
| Freeze metadata | `input/low-overlap-story.meta.json` |
| Plan | `outputs/low/plan.json` |
| Checklist | `outputs/low/collection-checklist.md` |
| Manifest | `operator-prompts/manifest-low.json` |
| Prompts | `operator-prompts/low-*.md` (63 files) |
| Priming corpus (unchanged) | `phase2a-authentic-isv` v1 — `aaad28e43935a40313585d77a33bfc788d97e8d69b081f9486af74d52ca1a857` |

Prepare command:

```bash
.venv/bin/python scripts/run_exp004_phase2b.py prepare \
  --regime low --date 2026-09-15
```

---

## Status

| Step | Status |
|---|---|
| Clean boundary identified | done |
| Human boundary approval | **APPROVED** |
| Story freeze v1 | **done** |
| LOW prompt kit (42 runs) | **READY** |
| LLM sessions | **none** |

---

## Single next action

**Execute the 42 LOW runs manually using the prepared kit (fresh sessions; Direct corpus-free; Primed full corpus then story) — no evaluation until collection completes.**
