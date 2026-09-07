# Phase-repeat operator prompts (EXP-004, SODA Task 025)

Files in this directory are **gitignored** (they embed the copyrighted
Polish source story and/or the reference corpus, which are local-only);
this README and `manifest.json` (hashes only) are committed.

## Inventory (180 prompt files, 18 primary configurations + 2 exploratory Dola)

Per configuration (Phase-1 roster number `<NN>`; GLM = 11 absent) and per
replicate `r01`/`r02`/`r03`:

- `direct-<NN>-<model>-<version>-r0<k>.md` (60) — **Condition A (direct):**
  the exact Phase-1 direct prompt in a fresh session (same Polish source
  story, same translation instruction; no corpus/dictionary/examples/
  scaffolding).
- `primed-<NN>-<model>-<version>-r0<k>-msg1.md` (60) — **Condition B,
  message 1:** the complete three-register corpus
  (`phase2a-authentic-isv` v1: literary/narrative `Tuta historija`
  excerpt; artistic/poetic Latin-only deduplicated *Ahoj, Slovjani!*
  album; informative/encyclopedic ISV Wikipedia *Sadovničstvo*) presented
  in a fresh session with the Phase-2A study-as-reference instruction —
  no translation/summary/imitation/questions, no hints about vocabulary,
  style, morphology or "naturalness".
- `primed-<NN>-<model>-<version>-r0<k>-msg2.md` (60) — **Condition B,
  message 2:** the exact Polish source story + translation instruction,
  sent in the SAME fresh session after msg1; the translation is collected
  after the corpus has been presented.

The three replicate prompt files of a given (configuration, condition)
are **byte-identical in their model-facing linguistic content** by design
— only the run metadata that surrounds the task changes. Every file's
SHA-256 is recorded in `manifest.json`.

**Primary vs exploratory:** configurations 01–10, 12–19 are the original
18 primary rows; configurations **20 (Dola 3.8 Fast)** and **21 (Dola 3.8
Pro)** are the exploratory extension (12 files), prepared with
`exploratory: true` and never merged into the primary n=18 statistics —
the research lead decides whether to execute them.

**msg2-style records (after collection):** as in Phase-2A (Task 021), the
author saves each raw reply inside its canonical prompt file — the prompt
part through the closing `## Output` marker stays byte-identical to the
prepared file, and the reply replaces the trailing boilerplate.
`collect-msg2` (primed) / `collect-session` (msg2-style or full session
transcripts) validates the record before intake; the file's SHA-256 is
recorded in the run meta so later edits are caught by `verify`.

Run ids follow `<date>__<provider>__<model>__<version>__<condition>__<replicate>`
(e.g. `2026-09-08__anthropic__claude__sonnet-5__primed__r02`).
