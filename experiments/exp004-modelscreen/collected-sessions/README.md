# EXP-004 Phase 1 — collected raw sessions (immutable provenance)

The 19 session files in this directory are the **raw collected material**
from the Phase 1 screening (SODA Task 018): each file is what the author
saved during one external web/chat session — the prompt header (possibly
hand-annotated with the model label the interface showed), the unmodified
instruction/source body, and the model's raw reply appended after the
prompt's closing `## Output` line.

These files are **experimental data**: they are preserved byte-for-byte and
are never modified, cleaned, or edited (D-035). They embed the copyrighted
source story and the raw model outputs, so the directory is **gitignored** —
only this README and the audit evidence are committed.

## Files

The 19 raw session files (author naming, preserved as-is):

| File | Reconciled run (run-id model-version) |
|---|---|
| `01-gpt-5.6-luna-thinkoff.md` | gpt-5.6-luna-thinkoff |
| `02-gpt-5.6-luna-thinkon.md` | gpt-5.6-luna-thinkon |
| `03-gpt-isv-teacher-unknown.md` | gpt-isv-teacher-unknown |
| `04-claude-sonnet-5.md` | claude-sonnet-5 |
| `05-gemini-3.1-Pro-rozszerzony.md` | gemini-3.1-pro-extthinkon |
| `06-deepseek-v3-instant-deepthinkoff.md` | deepseek-v3-instant-deepthinkoff |
| `07-deepseek-v3-instant-deepthinkon.md` | deepseek-v3-instant-deepthinkon |
| `08-grok-unknown.md` | grok-unknown\* |
| `09-kimi-unknown.md` | kimi-k2.6-instant |
| `10-qwen-3.8-Max-Thinking.md` | qwen-3.8-max-thinking |
| `11-glm-unknown.md` | glm-4.5 (failed artifact: service-error page) |
| `12-claude-sonnet-5-max.md` | claude-sonnet-5-max |
| `13-gemini-3.6-Flash-myslenierozszerzoneoff.md` | gemini-3.6-flash-extthinkoff |
| `14-gemini-3.6-Flash-myslenierozszerzoneon.md` | gemini-3.6-flash-extthinkon |
| `15-deepseek-v4-pro-deepthinkoff.md` | deepseek-v3-expert-deepthinkoff |
| `16-deepseek-v4-pro-deepthinkon.md` | deepseek-v3-expert-deepthinkon |
| `17-qwen-3.7-Plus-Thinking.md` | qwen-3.7-plus-thinking |
| `18-qwen-3.7-Plus-Fast.md` | qwen-3.7-plus-fast |
| `19-qwen-3.8-Max-Fast.md` | qwen-3.8-max-fast |

The author's filenames/headers were NOT trusted as identity: every session
was audited against the canonical prompt package (instruction+source body
byte-identity, reply end-marker, duplicates) by
`scripts/audit_exp004_collected.py`. Known author-annotation discrepancies
(fixed in metadata, never in the files): rows 15/16 filenames say
`deepseek-v4-pro` but the executed model was **DeepSeek V3 Expert**
(header + author confirmation); row 19 filename says `Max-Fast` while its
header said `Max-Thinking` (**Fast** confirmed by the author); Qwen session
headers carry an `EXP-004q` typo; GLM's file contains only the service
error page, not a translation.

\* **Row 08 — canonical Grok identity (Task 031):** the row-08 session is
the **Grok 4.5 Fast** configuration, operator-reported (`Grok 4.5, built
by xAI (fast)`, recorded Tasks 021/026; not independently verified). The
author's session filename / reconciled token `grok-unknown` are the
historical values recorded at Task 018 and are preserved; canonical alias
`xai__grok__fast`. See `../grok-identity.md` (authoritative) +
`../grok-identity-map.json`.

## Audit evidence

- `collection_audit.json` / `collection_audit.md` — read-only reconciliation
  evidence (regenerate with `python scripts/audit_exp004_collected.py`).

## How the replies became runs

Each session's reply was extracted deterministically (the suffix after the
prompt's closing `## Output` line) and stored byte-for-byte as
`../outputs/<run_id>/output.txt` via
`scripts/run_exp004_phase1.py collect-session --run <run_id> --session
<file>`. `outputs/<run_id>/meta.json` records the session-file SHA-256 and
the canonical prompt hash, so every stored output maps to exactly one run
and one session.
