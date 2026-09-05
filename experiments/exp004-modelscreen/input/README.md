# EXP-004 — input

Story-only source used by the Phase 1 operator prompts.

- `source.txt` — the Polish story, **story text only** (title, headings,
  paragraphs, `KONIEC` marker), byte-for-byte identical to the EXP-003
  canonical source (SHA-256 `5de968a6…57280723`; see `source.meta.json` for
  the derivation).
- `source.meta.json` — derivation record (parent file SHA-256, copy note,
  new SHA-256).

Both files embed the copyrighted story and are **gitignored** — they stay
local. Regenerate with:

```bash
python scripts/run_exp004_phase1.py prepare --date YYYY-MM-DD
```
