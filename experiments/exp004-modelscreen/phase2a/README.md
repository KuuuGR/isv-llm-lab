# EXP-004 Phase 2A — full-roster corpus priming (prepared kit)

Status (Task 019, 2026-09-06): **prepared and execution-ready — no external
LLM runs performed in this task.**

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
  - Prompt 1 (`*-msg1.md`): the fixed authentic Medžuslovjansky reference
    text (author-supplied "Tuta historija" excerpt, ~4.5 KB — see
    `corpus/README.md`) with an explicit study-as-language-reference
    instruction. No translation is requested; the model must not
    translate/summarize/reproduce/continue/imitate the text or answer
    questions about it.
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

Fixed authentic reference text: "Tuta historija" excerpt (Prolog + Razděl 1
"Věčna Zima"), supplied by the author in Task 019, 4 820 bytes,
SHA-256 `413830fa4ff6aaa8833895a22e7ef1fa5fa3807e5a5a105b7e4050cf7b67a29c`.
Same corpus for every model in the primed condition (no per-model
truncation). See `corpus/README.md` for provenance, license note,
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
