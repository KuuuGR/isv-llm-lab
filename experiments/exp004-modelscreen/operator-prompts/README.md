# EXP-004 Phase 1 — operator prompts (canonical package)

One self-contained Markdown file per reconciled roster row (19 rows, Task
018) **plus two exploratory Phase-1 DIRECT prompts for Dola 3.8 Fast/Pro
added retrospectively by Task 022 `extend-direct`** (pending manual
collection — see below; NOT part of the 19-row roster).
**No manual assembly is needed**: each file contains the experiment
header (target model/provider/version/settings, condition `direct`), the
complete Phase 1 instruction (identical for every row), and the full Polish
source story. The prompts are written by `scripts/run_exp004_phase1.py
prepare`; the prompt files embed the copyrighted story and are
**gitignored** — they stay local. The committed `manifest.json` records
prompt hashes only.

These files are the **canonical prompts** (identity of record for each run:
`meta.prompt.sha256` points here). The prompts as actually pasted during the
screening sessions are not independently recoverable byte-for-byte: the
author annotated some headers before running (e.g. recording the exact model
label shown by the interface) and saved the whole session (prompt + reply)
as one file. Those **raw session files** are preserved unmodified under
`../collected-sessions/` (Task 018). Header annotation never changed the
instruction/source body, which is byte-identical in every session file
(verified by `scripts/audit_exp004_collected.py`).

## Files (canonical prompt per reconciled roster row)

| File | Reconciled roster row | Paste into |
|---|---|---|
| `01-gpt-5.6-luna-thinkoff.md` | GPT-5.6 Luna — thinking OFF | ChatGPT (web) |
| `02-gpt-5.6-luna-thinkon.md` | GPT-5.6 Luna — thinking ON | ChatGPT (web) |
| `03-gpt-isv-teacher-unknown.md` | GPT Interslavic Teacher (custom GPT) | ChatGPT custom GPT |
| `04-claude-sonnet-5.md` | Claude Sonnet 5 — Medium (default) | Claude (web) |
| `05-gemini-3.1-pro-extthinkon.md` | Gemini 3.1 Pro — extended thinking ON | Gemini (web) |
| `06-deepseek-v3-instant-deepthinkoff.md` | DeepSeek V3 Instant — DeepThink OFF | DeepSeek chat |
| `07-deepseek-v3-instant-deepthinkon.md` | DeepSeek V3 Instant — DeepThink ON | DeepSeek chat |
| `08-grok-unknown.md` | Grok | Grok (web) |
| `09-kimi-k2.6-instant.md` | Kimi K2.6 Instant (Standard) | Kimi (web) |
| `10-qwen-3.8-max-thinking.md` | Qwen 3.8 Max — Thinking | Qwen Chat |
| `11-glm-4.5.md` | GLM 4.5 | Zhipu GLM (web) |
| `12-claude-sonnet-5-max.md` | Claude Sonnet 5 — max (long reasoning) | Claude (web) |
| `13-gemini-3.6-flash-extthinkoff.md` | Gemini 3.6 Flash — ext. thinking OFF | Gemini (web) |
| `14-gemini-3.6-flash-extthinkon.md` | Gemini 3.6 Flash — ext. thinking ON | Gemini (web) |
| `15-deepseek-v3-expert-deepthinkoff.md` | DeepSeek V3 Expert — DeepThink OFF | DeepSeek chat |
| `16-deepseek-v3-expert-deepthinkon.md` | DeepSeek V3 Expert — DeepThink ON | DeepSeek chat |
| `17-qwen-3.7-plus-thinking.md` | Qwen 3.7 Plus — Thinking | Qwen Chat |
| `18-qwen-3.7-plus-fast.md` | Qwen 3.7 Plus — Fast | Qwen Chat |
| `19-qwen-3.8-max-fast.md` | Qwen 3.8 Max — Fast | Qwen Chat |

Rows 5/13/14 (Gemini) and 11 (GLM) were **conditional** (DESIGN §5.1/D-036).
Gemini satisfied the practical free-access/quota criterion in execution and
was run; GLM 4.5 could not execute (repeated service errors) and its
artifact is preserved as a failed external output.

## Exploratory Phase-1 DIRECT prompts added retrospectively (Task 022 — pending)

| File | Configuration | Prepared baseline run id | Pairs with Phase-2A |
|---|---|---|---|
| `20-dola-3.8-fast.md` | Dola 3.8 — Fast (exploratory) | `2026-09-07__bytedance__dola-3.8__fast__direct` | run 20 (`…__fast__p2a-primed`) |
| `21-dola-3.8-pro.md` | Dola 3.8 — Pro (exploratory) | `2026-09-07__bytedance__dola-3.8__pro__direct` | run 21 (`…__pro__p2a-primed`) |

Rendered by `scripts/run_exp004_phase1.py extend-direct --date 2026-09-07`
(Task 022) with the same direct-translation instruction and the same Polish
source story as the 19 canonical rows above — **corpus-free by
construction, no scaffold/dictionary/morphology/grammar material, no
previous Dola conversation** — and explicit operator notes (Dola
configuration to select, fresh session, Phase-1 direct baseline, exact text
to submit, where to record the raw reply). These are **NOT part of the
original 19-row reconciled roster**: the Dola configurations are
exploratory (discovered Task 021; `exploratory: true` preserved) and the
plan/manifest rows are `pending_manual_collection` — nothing is collected
or claimed yet, and the original 18 usable Phase-1 baselines are unchanged.
Register replies exactly as described below (prefer
`collect-session`), then `verify` + `evaluate`; the Phase-2A `compare` then
reports the within-Dola Phase 1 → Phase 2A deltas for runs 20/21.

## How to execute one run (operator workflow, as used)

```text
1. Open a canonical operator-prompts/<file>.md OR the corresponding session
   template, copy the entire file.
2. Paste it into the specified model (row-specific interface/settings, e.g.
   thinking toggle ON/OFF, DeepThink ON/OFF, the custom GPT).
3. Save the model's complete reply byte-for-byte (no cleaning, no trimming).
4. If the model refuses or truncates the reply, save the partial reply and
   record the failure exactly as it happened — do not shorten the prompt.
5. Register the reply with the collect step:
   python scripts/run_exp004_phase1.py collect \
     --run <run_id> --output <reply-file> \
     --generation-date <actual date> \
     --model <as-shown> --provider <as-shown> --model-version <as-shown> \
     --generation-parameters <as-shown> \
     --status collected_external_output|collected_partial_output|failed_external_output \
     --access-verdict pass|fail|unknown --access-note "<quota observation>"
   then: python scripts/run_exp004_phase1.py verify  (completeness gate)
         python scripts/run_exp004_phase1.py evaluate --run <run_id>
```

When the operator saves prompt+reply as ONE session file, use
`collect-session --run <run_id> --session <file>` instead of `collect`
(Task 018): it validates the instruction body against the canonical prompt
and extracts the raw reply after the prompt's closing `## Output` line.

## Prompt-control policy

- Every row receives the **same direct-translation instruction** (from
  `base_instruction.txt`): no scaffold, no candidates, no morphology/POS or
  grammar annotations, no previous translations, no evaluator feedback, no
  iterative repair (EXP-004 DESIGN §6.2).
- Rows of the same provider differ only in the documented generation setting
  (thinking / DeepThink / extended thinking / Fast), never in linguistic
  content.
- The custom GPT row receives the same visible instruction; its built-in
  system prompt is unknown and is recorded as a confound (D-018) — the row
  is exploratory and kept separate from plain ChatGPT.
- Byte-for-byte preservation of prompts and raw replies is a hard rule
  (D-023/D-035); never clean, trim, or rephrase a reply before collecting.
- The canonical prompt files are deterministic: `prepare --force
  --date <date>` regenerates byte-identical prompts + manifest (repository
  evidence of the package).

## Access filter (D-036 / DESIGN §5.1) — recorded verdicts

The per-row access verdicts recorded in `outputs/<run_id>/meta.json` were
reconciled in Task 018 from the actual execution evidence: rows that
produced a complete story translation in one session received `pass`
(Gemini conditional rows included); GLM 4.5 received `fail` (no usable
output; repeated interface errors); Claude Sonnet 5 max received `pass`
with the recorded constraint that the single run took >45 min and exhausted
the free-tier allowance (practical-availability data, not a quality score).
Daily free-quota sufficiency beyond the observed single run was not
independently verified and is recorded as such.
