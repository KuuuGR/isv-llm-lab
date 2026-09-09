# Phase 2B HIGH-overlap — input (story provenance; gitignored except this README)

This directory holds the **frozen** HIGH-overlap Polish story
("Iskra i Wieloryb — wersja z oryginalnymi nazwami") and its provenance.
Everything under `input/` is local-only (the story is author-owned and
copyrighted, like the Phase-1 source story): only this README is
committed.

## Current status: story not yet supplied

The HIGH-overlap story text itself has **not yet been provided to the
repository** (checked 2026-09-09, Task 029). The classification and
provenance are recorded; the frozen text is a required author input.

- Do **not** fabricate or generate the story (no LLM may write it; it is
  the research lead's own creative input).
- Do **not** "clean" the story to make it independent: its deliberate
  overlap with the corpus is the HIGH-overlap experimental condition
  (classification `high_overlap_corpus_inspired`, never
  `independent_same_topic`).
- Do **not** modify the author's original file. The freeze step below
  only reads it and stores an immutable frozen copy.

## Freezing the story (author or engineer step)

```bash
python scripts/run_exp004_phase2b.py freeze-story \
    --src <path-to-author-file> \
    --version-label v1 \
    --note "original version with original names; <any provenance note>"
```

What happens:

- `versions/iskra-wieloryb-original-names-v1.txt` — an immutable frozen
  copy (previous versions are never overwritten or deleted; a revised
  story is a new version, e.g. `--version-label v2`).
- `high-overlap-story.meta.json` — provenance record: title, story id
  `iskra-wieloryb-original-names`, classification
  `high_overlap_corpus_inspired`, version, SHA-256, bytes, read-only
  source path, note, freeze date.
- The author's original file is only read, never modified.

`prepare` then hash-gates the frozen story against the meta file and
fails loudly on any byte drift (or when no story is frozen).

## Provenance note (recorded in the meta file)

This Polish story deliberately shares substantial motifs with the
authentic corpus (eternal winter; the Red/Scarlet Spark; Zimorodzice; an
inherited key; a grandfather's legacy; Mogiła Szronu; songs used as
narrative mechanisms; whale imagery; the Heart of the Earth; sacrifice
and transformation; maritime and storm imagery). It is an experimental
input for the HIGH-overlap corpus-priming test — NOT an independent
same-topic control and NOT part of the corpus. The corpus remains
authentic reference material; the story is an independent (if
deliberately aligned) experimental input.
