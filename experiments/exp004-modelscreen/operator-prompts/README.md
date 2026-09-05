# EXP-004 Phase 1 — operator prompts

One self-contained Markdown file per roster row. **No manual assembly is
needed**: each file contains the experiment header (target model/provider/
version/settings, condition `direct`), the complete Phase 1 instruction
(identical for every row), and the full Polish source story. The prompts are
written by `scripts/run_exp004_phase1.py prepare`; the prompt files embed
the copyrighted story and are **gitignored** — they stay local. The
committed `manifest.json` records prompt hashes only.

## Files

| File | Roster row | Paste into |
|---|---|---|
| `01-gpt-5.6-luna-thinkoff.md` | GPT-5.6 Luna — thinking OFF | ChatGPT (web) |
| `02-gpt-5.6-luna-thinkon.md` | GPT-5.6 Luna — thinking ON | ChatGPT (web) |
| `03-gpt-isv-teacher-unknown.md` | GPT Interslavic Teacher (custom GPT) | ChatGPT custom GPT |
| `04-claude-sonnet-5.md` | Claude Sonnet 5 | Claude (web) |
| `05-gemini-unknown.md` | Gemini | Gemini (web) |
| `06-deepseek-v4-pro-deepthinkoff.md` | DeepSeek V4 Pro — DeepThink OFF | DeepSeek chat |
| `07-deepseek-v4-pro-deepthinkon.md` | DeepSeek V4 Pro — DeepThink ON | DeepSeek chat |
| `08-grok-unknown.md` | Grok | Grok (web) |
| `09-kimi-unknown.md` | Kimi | Kimi (web) |
| `10-qwen-unknown.md` | Qwen | Qwen Chat |
| `11-glm-unknown.md` | GLM | Zhipu GLM (web) |

Rows 5 (Gemini) and 11 (GLM) are **conditional**: they are used only if the
practical free-access/quota criterion of DESIGN §5.1 (D-036) is satisfied —
≥ 1 full story per day or every other day on the ordinary free tier, usable
by the project author. If a conditional row fails that check at execution
time, do NOT run it; record the exclusion (see below).

## How to execute one run

```text
1. Open operator-prompts/<file>.md.
2. Copy the entire file.
3. Paste it into the specified model (row-specific interface/settings, e.g.
   thinking toggle ON/OFF, DeepThink ON/OFF, the custom GPT).
4. Save the model's complete reply byte-for-byte (no cleaning, no trimming).
5. If the model refuses or truncates the reply, save the partial reply and
   record the failure exactly as it happened — do not shorten the prompt.
6. Register the reply with the collect step:
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

## Prompt-control policy

- Every row receives the **same direct-translation instruction** (from
  `base_instruction.txt`): no scaffold, no candidates, no morphology/POS or
  grammar annotations, no previous translations, no evaluator feedback, no
  iterative repair (EXP-004 DESIGN §6.2).
- Rows of the same provider differ only in the documented generation setting
  (thinking / DeepThink), never in linguistic content.
- The custom GPT row receives the same visible instruction; its built-in
  system prompt is unknown and is recorded as a confound (D-018) — the row
  is exploratory and kept separate from plain ChatGPT.
- Byte-for-byte preservation of prompts and raw replies is a hard rule
  (D-023/D-035); never clean, trim, or rephrase a reply before collecting.

## Access filter (D-036 / DESIGN §5.1) — record the verdict per row

Before a row is used in the quantitative screening, verify in the actual
interface that it satisfies **all** of:

1. usable through a normal web/chat interface (no local install);
2. free access;
3. enough practical free quota for at least one complete story per day or
   every other day (not merely a one-time trial/credit allocation);
4. realistically usable by the project author.

Document the observed verdict in the collect step (`--access-verdict`,
`--access-note`). If access is technically free but the quota is too
restrictive for this project, classify it as **practically unavailable**
(verdict `fail`) and exclude it from the quantitative screening — the
exclusion and reason are recorded, and the row is not run.
