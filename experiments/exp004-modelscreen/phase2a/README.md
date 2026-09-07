# EXP-004 Phase 2A — full-roster corpus priming (prepared kit)

Status (Task 020, 2026-09-07): **prepared but NOT executed — the next
operator step is the manual external execution of the 18 primed sessions
(no LLM calls happen in this task).**

Phase 2A tests the project's core corpus-grounding hypothesis:

> Does exposing an LLM to authentic Medžuslovjansky text immediately before
> translation cause it to generate Medžuslovjansky that is more consistent
> with the real language than the same model translating without that
> exposure?

This is an **in-context learning / corpus priming / contextual grounding /
reference-text conditioning** experiment, NOT model training (weights are
never changed) and NOT textual reconstruction (the reference text is never
the target; new translations with different wording are expected).

## Design in one paragraph

For every Phase-1-usable configuration (the reconciled 18-model roster,
GLM excluded) Phase 2A prepares two conditions:

- **Control (`p2a-ctl`)** — the same clean direct-translation task as
  Phase 1 (same base instruction, same Polish source story, fresh session,
  no corpus). The **Phase-1 baseline outputs satisfy this condition**; the
  compare step uses a freshly collected Phase-2A control when the author
  executes one, otherwise the Phase-1 output of the same configuration.
- **Corpus-primed (`p2a-primed`)** — two sequential prompts in ONE fresh
  session:
  - Prompt 1 (`*-msg1.md`): the fixed combined corpus of THREE authentic
    Medžuslovjansky registers — literary/narrative, artistic/poetic and
    informative/encyclopedic (≈58 KB / ≈8 200 tokens — see
    `corpus/README.md`) — with an explicit study-as-language-reference
    instruction (vocabulary, morphology, syntax, word formation,
    phraseology, orthography, stylistic patterns). The artistic section
    may contain deliberate poetic choices and is not a normative grammar
    template. No translation is requested; the model must not
    translate/summarize/reproduce/continue/analyze the corpus or answer
    questions about it, and receives no word-level correctness claims,
    dictionary candidates, grammatical annotations or translations.
  - Prompt 2 (`*-msg2.md`): the SAME Polish source story as Phase 1 with
    the standard direct-translation instruction and an explicit reference
    to the preceding authentic text. The story bytes are unchanged; there
    is no lexical scaffolding, no candidate list, no dictionary injection,
    no morphology annotation, no repair instruction.

The key comparison is **primed vs Phase-1 direct baseline for the same
model/configuration** (delta per dimension; no composite score, no ranking).

## The 18-model Phase-2A roster (authoritative: Phase-1 reconciled roster)

| # | label | provider / model / version | primed run |
|---|---|---|---|
| 01 | GPT-5.6 Luna — thinking OFF | openai / gpt-5.6-luna / thinkoff | `<date>__openai__gpt-5.6-luna__thinkoff__p2a-primed` |
| 02 | GPT-5.6 Luna — thinking ON | openai / gpt-5.6-luna / thinkon | `…__gpt-5.6-luna__thinkon__p2a-primed` |
| 03 | GPT Interslavic Teacher (GPT) | openai / gpt-isv-teacher / unknown | `…__gpt-isv-teacher__unknown__p2a-primed` |
| 04 | Claude Sonnet 5 | anthropic / claude / sonnet-5 | `…__claude__sonnet-5__p2a-primed` |
| 05 | Gemini 3.1 Pro — extended thinking ON | google / gemini-3.1-pro / extthinkon | `…__gemini-3.1-pro__extthinkon__p2a-primed` |
| 06 | DeepSeek V3 Instant — DeepThink OFF | deepseek / deepseek-v3-instant / deepthinkoff | `…__deepseek-v3-instant__deepthinkoff__p2a-primed` |
| 07 | DeepSeek V3 Instant — DeepThink ON | deepseek / deepseek-v3-instant / deepthinkon | `…__deepseek-v3-instant__deepthinkon__p2a-primed` |
| 08 | Grok | xai / grok / unknown | `…__grok__unknown__p2a-primed` |
| 09 | Kimi K2.6 Instant (Standard) | moonshot / kimi / k2.6-instant | `…__kimi__k2.6-instant__p2a-primed` |
| 10 | Qwen 3.8 Max — Thinking | alibaba / qwen-3.8-max / thinking | `…__qwen-3.8-max__thinking__p2a-primed` |
| 12 | Claude Sonnet 5 — max (long reasoning) | anthropic / claude / sonnet-5-max | `…__claude__sonnet-5-max__p2a-primed` |
| 13 | Gemini 3.6 Flash — ext. thinking OFF | google / gemini-3.6-flash / extthinkoff | `…__gemini-3.6-flash__extthinkoff__p2a-primed` |
| 14 | Gemini 3.6 Flash — ext. thinking ON | google / gemini-3.6-flash / extthinkon | `…__gemini-3.6-flash__extthinkon__p2a-primed` |
| 15 | DeepSeek V3 Expert — DeepThink OFF | deepseek / deepseek-v3-expert / deepthinkoff | `…__deepseek-v3-expert__deepthinkoff__p2a-primed` |
| 16 | DeepSeek V3 Expert — DeepThink ON | deepseek / deepseek-v3-expert / deepthinkon | `…__deepseek-v3-expert__deepthinkon__p2a-primed` |
| 17 | Qwen 3.7 Plus — Thinking | alibaba / qwen-3.7-plus / thinking | `…__qwen-3.7-plus__thinking__p2a-primed` |
| 18 | Qwen 3.7 Plus — Fast | alibaba / qwen-3.7-plus / fast | `…__qwen-3.7-plus__fast__p2a-primed` |
| 19 | Qwen 3.8 Max — Fast | alibaba / qwen-3.8-max / fast | `…__qwen-3.8-max__fast__p2a-primed` |

GLM 4.5 (Phase-1 #11) is excluded: its Phase-1 intake failed, so it has no
usable baseline. The roster is derived in code from
`run_exp004_phase1.ROSTER` and never reconstructed from filenames.

## Run ids and phases

`<date>__<provider>__<model>__<model_version>__<condition>` with
`<condition>` = `direct` (Phase 1 baseline) | `p2a-ctl` (Phase-2A control) |
`p2a-primed` (Phase-2A corpus-primed). The three identities can never be
confused. Every Phase-2A plan row records its `baseline_run_id` (the
Phase-1 `direct` run of the same configuration).

## Corpus

Fixed combined corpus of THREE authentic Medžuslovjansky registers
(SODA Task 020, 2026-09-07), all under `corpus/`:

1. **Register 1 — literary / narrative:** "Tuta historija" excerpt
   (Prolog + Razděl 1 "Věčna Zima"; Task 019, unchanged) — 4 820 B,
   SHA-256 `413830fa4ff6aaa8833895a22e7ef1fa5fa3807e5a5a105b7e4050cf7b67a29c`.
2. **Register 2 — artistic / poetic:** complete Latin-script song album
   *Ahoj, Slovjani!* in original order (11 songs, 76 unique stanzas /
   322 lines), from the author-supplied copy of the public album page;
   Cyrillic duplicates and webpage/HTML material removed, verbatim
   repeated stanzas/refrains deduplicated, linguistic forms NOT
   normalized or corrected — 9 407 B, SHA-256
   `7e25a56f67a52976083f625fabf040b6cd5ae399317cb36a59a302a3a52dcacf`.
3. **Register 3 — informative / encyclopedic:** cleaned running prose of
   the authentic Medžuslovjansky Wikipedia article *Sadovničstvo*
   (isv.wikipedia.org, retrieved 2026-09-07 from the Wikimedia wikitext
   API; the ISV article itself, not a translation) — 84 paragraphs,
   44 101 B, SHA-256
   `b03402fef2384730b90a5ab879af78be63b5e6d0e4fa00db4c3c3525844c8345`.

The **authoritative combined file** `phase2a-authentic-isv-corpus.txt`
(58 459 B, ≈ 8 184 whitespace tokens, SHA-256
`aaad28e43935a40313585d77a33bfc788d97e8d69b081f9486af74d52ca1a857`; corpus
id `phase2a-authentic-isv`, v1), with plain-text `=== REGISTER … ===`
section headers, is embedded byte-identically in every primed `msg1` for
all 18 configurations. ≈58 KB / ≈8 200 tokens is well within every roster
model's context window and is **not** truncated or subsetted per model.
All corpus text files are gitignored/local-only; only this README,
`corpus/README.md` and the pinned hashes are committed. See
`corpus/README.md` for per-register provenance, license notes,
suitability and contamination checks.

## Conversation-contamination control (critical)

- Each run = a NEW fresh session. Never reuse a session that contains other
  ISV material.
- Primed runs: Prompt 1 and Prompt 2 MUST be in the SAME session (that is
  the manipulation). Send msg1, wait for the one-or-two-sentence
  confirmation, then send msg2.
- Control runs: never contain any ISV reference material; the collector
  mechanically rejects a control session that contains the corpus.
- `collect-session` verifies for primed runs that the corpus is present in
  the session BEFORE the translation instruction — i.e. it proves Prompt 1
  actually ran in the same session.

## Execution protocol (author)

1. Open a **new fresh session** per run in the model's interface.
2. **Primed run**: copy `*-msg1.md` → send → wait for the short
   confirmation → copy `*-msg2.md` → send.
   **Control run (optional)**: copy `ctl-*.md` → send.
3. Save the final translation byte-for-byte (D-035): either the whole
   session file under `collected-sessions/` (then
   `collect-session --run <id> --session <file>`), or the plain reply file
   (then `collect --run <id> --output <file>`). Never edit, truncate or
   paraphrase the reply.
4. Record the practical free-access verdict (pass/fail/unknown) and any
   quota observation — same discipline as Phase 1 (D-036/§5.1).

Claude Sonnet 5 — max (run #12) took >45 minutes in Phase 1 with repeated
continuations and free-tier exhaustion (see RESEARCH_NOTES §4.16/§4.17).
It stays in the roster; if a primed session is impractical on the day,
record it as an execution limitation — do not silently substitute another
model or another corpus.

## Orchestration (never calls an LLM)

```bash
# regenerate the kit for a different execution date (prompts identical;
# run ids/manifest/plan dates change) — commit the refreshed manifest
python3 scripts/run_exp004_phase2a.py prepare --date YYYY-MM-DD [--force]

python3 scripts/run_exp004_phase2a.py status                 # progress
python3 scripts/run_exp004_phase2a.py roster                 # joined roster
python3 scripts/run_exp004_phase2a.py compare                # primed-vs-baseline deltas
```

`collect`, `collect-session`, `verify`, `evaluate` mirror the Phase-1
commands (see `scripts/run_exp004_phase2a.py` docstring for details).
Outputs land under `phase2a/outputs/` (gitignored; `outputs/README.md`
committed). Nothing is evaluated without a collected file; outputs are
never modified or deleted; no composite scores are produced.

## Future Phase 2B (documented, NOT executed)

A follow-up with a longer authentic reference text (an actual ISV
Wikipedia article) plus an independently written Polish story inspired by
its subject — planned to isolate corpus *length/complexity* effects from
corpus *content* effects. Not implemented in this task.
