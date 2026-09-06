# EXP-004 Phase 2A — corpus (author-supplied reference text)

The Phase 2A corpus-priming reference text lives in this directory:

- `tuta-historija-excerpt.txt` — **gitignored**, stays local.

## The text

- **Work / corpus id:** `tuta-historija` — "Tuta historija", an authentic
  Medžuslovjansky (Interslavic) text **supplied directly by the project
  author in SODA Task 019 (2026-09-06)**.
- **Excerpt:** `Prolog` + `Razděl 1. Věčna Zima`, beginning
  "Ljudi govoret, že v tamtoj denj bylo je veliko spokojno…" and ending
  "…da by prěžiti v tutoj težkoj době." The excerpt contains both narrative
  prose and dialogue (description, character speech, questions, answers,
  everyday constructions). The internal line "„Utračena Krajina", prolog"
  is part of the supplied text and is preserved verbatim.
- **Spelling / structure:** the file is byte-for-byte as supplied in the
  task (no reflow, no spelling/punctuation changes). Line breaks within a
  paragraph are preserved verbatim and are a paste artifact of the author's
  message, not linguistic structure; blank lines mark paragraphs.

## Provenance & license/copyright

- Source: supplied in full by the project author (SODA Task 019,
  2026-09-06). No URL is referenced; nothing was fetched from the web.
- License/copyright status: the author supplied the text for use as the
  fixed Phase 2A reference corpus. Distribution status is not recorded in
  the repository, so the text is **kept local (gitignored)** like the
  Polish source story; only hashes and this provenance record are
  committed. It is embedded into the generated operator Prompt-1 files,
  which are likewise gitignored.

## Size & hash (v1, 2026-09-06)

| Field | Value |
|---|---:|
| bytes | 4 820 |
| characters | 4 563 |
| approximate words | 791 |
| paragraphs (blank-line separated) | 9 |
| lines | 85 |
| SHA-256 | `413830fa4ff6aaa8833895a22e7ef1fa5fa3807e5a5a105b7e4050cf7b67a29c` |

The hash is pinned in `scripts/run_exp004_phase2a.py`
(`TUTA_EXCERPT_SHA256`) and asserted by the test suite; any accidental edit
of the corpus file is therefore detected. A corpus change is a **new corpus
version** (id `tuta-historija`, version token + new hash), never a silent
edit.

## Why this text is suitable

- **Genuinely Medžuslovjansky:** the text is authentic ISV source material
  (official Latin orthography with `ě š ž č ć`, Medžuslovjansky lexicon and
  morphology). It is not machine-made scaffolding and not a translation of
  the target story.
- **Language reference content:** continuous prose with ordinary narrative
  and dialogue constructions — vocabulary, morphology, syntax, word
  formation, orthography and style can be studied from it.
- **Thematic relation to the Polish story:** the Polish source story
  ("Opowieść o Słów, Które Były Jak Siostry" — a fable about two languages)
  and this text (a fantasy narrative about an eternal winter) share **no
  plot, characters, setting or sentences**. A contamination probe over the
  corpus confirmed that none of the story's title words, character names
  (Bronisława, Teofil, Julianna, Przemysława, Antoni), or the place name
  Międzyrzecze appear in the corpus, and the corpus is not a translation of
  the story. Phase 2A tests assert this separation.
- **Role:** the text is a **language reference only**. It is never the
  target to reproduce, translate, summarize, continue or answer questions
  about. The model is asked to study it in-context (Prompt 1) and then to
  produce a NEW translation of the Polish story (Prompt 2). Different
  wording and sentence structures from the reference text are expected and
  are not a failure — Phase 2A tests contextual grounding (in-context
  learning / corpus priming / reference-text conditioning), **not** textual
  reconstruction and **not** model training (weights are never changed).

## Fairness note

Every model in the primed condition receives exactly this same corpus
(Prompt 1) in a fresh session; the corpus is short enough (≈4.5 KB) to fit
all 18 Phase-1-usable interfaces, so no per-model truncation or subset is
needed. If an interface ever cannot accept the full corpus, that run is
recorded as an execution/access limitation — the corpus is never silently
shortened per model.
