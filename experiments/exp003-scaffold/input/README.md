# EXP-003 — input

Cleaned story-only source used by the scaffold generator and the operator
prompts.

- `source.txt` — the Polish story, **story text only** (title, headings,
  paragraphs, `KONIEC` marker), byte-for-byte as cleaned from
  `experiments/exp001-baseline/input/source.txt` (see `source.meta.json` for
  the exact derivation).
- `source.meta.json` — derivation record: parent file SHA-256, what was
  removed (the EXP-001 instruction line and markdown fences), the new
  SHA-256, and the provision timestamp.

Both files embed the copyrighted story and are **gitignored** — they stay
local. Regenerate with:

```bash
python scripts/build_exp003_scaffold.py clean-source
```
