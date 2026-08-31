# Experiment 001 — input

This directory holds the authoritative Polish source story. It is **local
only** and gitignored: the Project Owner's story is copyrighted and must not
be published without clearing rights.

| File | Contents |
|---|---|
| `source.txt` | The complete Polish story, byte-for-byte as supplied (Project Owner's `source_pl.txt`) |
| `source.meta.json` | Provenance: title/author/date/license note |

## How to add the source

1. Drop the Project Owner's file at the repository root as `source_pl.txt`.
2. Run:

```bash
python3 scripts/run_exp001.py --ingest-source source_pl.txt
```

which copies it to `input/source.txt`, records `source.meta.json` (including
SHA-256), and verifies every later model run used the identical source hash.

Do not edit, normalize, rewrite, shorten, or split the source.
