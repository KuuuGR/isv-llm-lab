# Phase 2B HIGH-overlap — input (story provenance; gitignored except this README)

This directory holds the **frozen** HIGH-overlap Polish story
("Iskra i Wieloryb — wersja z oryginalnymi nazwami") and its provenance.
Everything under `input/` is local-only (the story is author-owned and
copyrighted, like the Phase-1 source story): only this README is
committed.

## Status: HIGH-overlap story frozen (Task 030, 2026-09-09)

The author supplied the story inside a multi-story bank file
(`InterslavicTesty.md`, kept outside the repository, sha256
`3662cda9…`); section `# 3. Iskra i Wieloryb — wersja z oryginalnymi
nazwami` was extracted deterministically
(`scripts/extract_phase2b_high_story.py`) and frozen as **v1**:

| Field | Value |
|---|---|
| Story id | `iskra-wieloryb-original-names` |
| Title | `Iskra i Wieloryb — wersja z oryginalnymi nazwami` |
| Version | `v1` (immutable; a revised story becomes v2, never an overwrite) |
| Frozen file | `versions/iskra-wieloryb-original-names-v1.txt` (gitignored) |
| SHA-256 | `ab8a0dcf7352789c09c4aca132c086999c861407e4cd682ee9414aab5b792f63` |
| Bytes / lines | 30 061 B / 440 lines |
| Classification | **`high_overlap_corpus_inspired`** (NOT `independent_same_topic`) |
| Regime | `high` (HIGH-overlap Phase-2B-A) |
| Source (read-only) | bank section 3 (lines 603–1058 of the author's file) |

**Extraction rule (documented; nothing else was edited).** The bank is a
source bank, not an experimental input. Only Markdown structural markers
were removed — the H1 section number (`# 3.`), `## ` heading prefixes,
`> ` song-blockquote prefixes, `*` emphasis markers and lone `---`
rules — and runs of blank lines were collapsed; all 227 story content
lines were preserved exactly (verified parity) and the story title was
added as the first line. Other bank sections were excluded and are
retained in the bank, untouched: section 1 (`Opowieść o Faktach…`) and
section 2 (`Opowieść o sygnale`) are not part of the current experiment;
section 4 (`Podkłady`) supplies the **LOW-overlap** story (clean prose
frozen separately as `podklady-v1`; see below). Do not clean or
"de-corpus" this HIGH story: its deliberate
overlap with the authentic corpus is the HIGH-overlap experimental
condition.

Provenance record (full note, frozen date, source path): gitignored
`high-overlap-story.meta.json` in this directory.

## Status: LOW-overlap story frozen (2026-09-15)

Clean prose from bank section `# 4. Podkłady` was frozen as **v1** after
human **APPROVE** of the clean-story boundary (casting notes + ElevenLabs
API/billing preamble excluded; trailing blanks excluded). The bank file
was not modified.

| Field | Value |
|---|---|
| Story id | `podklady` |
| Title | `Podkłady` |
| Version | `v1` (immutable) |
| Frozen file | `versions/podklady-v1.txt` (gitignored) |
| SHA-256 | `ce1c4fca03fe9cb2c5f8181ab45c91767759a0c785f0a066543d95bc32f5271b` |
| Bytes / lines | 15 249 B / 141 lines |
| Classification | **`low_overlap`** |
| Regime | `low` |
| Boundary | bank lines 1107–1247 (first: `Katarzyna odłożyła teczkę…`; last: `I po raz pierwszy od lat pomyślała…`) |
| Provenance | gitignored `low-overlap-story.meta.json` |

LOW prompt kit is **not** prepared yet. Do not mix LOW into the HIGH
manifest.

## Freezing a revised HIGH version (future, if the author supplies one)

```bash
python scripts/run_exp004_phase2b.py freeze-story \
    --src <path-to-author-file> \
    --version-label v2 \
    --note "..."
```

What happens:

- `versions/iskra-wieloryb-original-names-v2.txt` — a new immutable frozen
  copy (previous versions are never overwritten or deleted).
- `high-overlap-story.meta.json` — provenance updated: new `current_version`
  = v2, both versions recorded.
- The author's original file is only read, never modified.

`prepare` hash-gates the current frozen story against the meta file and
fails loudly on any byte drift (or when no story is frozen).
