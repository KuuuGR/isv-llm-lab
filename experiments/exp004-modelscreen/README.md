# EXP-004 — practical LLM model screening (Polish → Medžuslovjansky)

**Status: EXECUTED — collected outputs audited, reconciled, and evaluated
(SODA Task 018, 2026-09-06).** EXP-003 is closed; no further human
evaluation will be designed or requested (D-042). The project author
executed the Phase 1 screening sessions in the external web/chat
interfaces; the collected material was audited and reconciled against the
deterministic prompt package (Task 018) and the reconciled runs were run
through the intake gate, the deterministic evaluator, and the orthography
audit. **18 of 19 runs are complete and quantitatively usable; GLM 4.5 is
the single failed/excluded run (service-error artifact).** The Phase 1
evidence table is `outputs/roster.md`; the raw sessions are preserved
byte-for-byte under `collected-sessions/`.

Purpose: screen which LLMs are practically usable by the project (web/chat
interface, free access sufficient for ~1 story/day, identifiable
model/version/settings) and record their versioned no-guidance baseline
quality on the canonical story, before investing in guidance-method
experiments (Phase 2).

Design: `DESIGN.md` (Task 013; roster + protocol finalized Tasks 016/017;
execution + reconciliation Tasks 017/018).

## Phase 1 executed roster (19 concrete runs, reconciled Task 018)

The planned 11-row roster expanded during collection into the concrete
model/configuration runs below (the models the interfaces actually offered
and the author actually used). Identity reconciliation followed the prompt
package + manifest + author confirmation — see
`collected-sessions/collection_audit.md` and `outputs/roster.md`.

| # | Reconciled row | Provider / interface | Access verdict | Intake |
|---|---|---|---|---|
| 1 | GPT-5.6 Luna — thinking OFF | OpenAI ChatGPT | pass | complete |
| 2 | GPT-5.6 Luna — thinking ON | OpenAI ChatGPT | pass | complete |
| 3 | GPT Interslavic Teacher (custom GPT) | OpenAI ChatGPT custom GPT | pass | complete |
| 4 | Claude Sonnet 5 — Medium (default) | Anthropic Claude | pass | complete |
| 5 | Gemini 3.1 Pro — extended thinking ON | Google Gemini | pass | complete |
| 6 | DeepSeek V3 Instant — DeepThink OFF | DeepSeek chat | pass | complete |
| 7 | DeepSeek V3 Instant — DeepThink ON | DeepSeek chat | pass | complete |
| 8 | Grok | xAI Grok | pass | complete |
| 9 | Kimi K2.6 Instant (Standard) | Moonshot Kimi | pass | complete |
| 10 | Qwen 3.8 Max — Thinking | Alibaba Qwen Chat | pass | complete |
| 11 | GLM 4.5 | Zhipu GLM | **fail** | **failed** |
| 12 | Claude Sonnet 5 — max (long reasoning) | Anthropic Claude | pass* | complete |
| 13 | Gemini 3.6 Flash — extended thinking OFF | Google Gemini | pass | complete |
| 14 | Gemini 3.6 Flash — extended thinking ON | Google Gemini | pass | complete |
| 15 | DeepSeek V3 Expert — DeepThink OFF | DeepSeek chat | pass | complete |
| 16 | DeepSeek V3 Expert — DeepThink ON | DeepSeek chat | pass | complete |
| 17 | Qwen 3.7 Plus — Thinking | Alibaba Qwen Chat | pass | complete |
| 18 | Qwen 3.7 Plus — Fast | Alibaba Qwen Chat | pass | complete |
| 19 | Qwen 3.8 Max — Fast | Alibaba Qwen Chat | pass | complete |

\* Row 12 (Claude Sonnet 5 max): the run completed but took >45 min and
exhausted the free-tier allowance (author report) — preserved as a
practical-availability constraint, not a quality signal; the output itself
is complete and evaluated.

### Planned-vs-executed deviations (recorded, Task 018)

- **DeepSeek:** the planned V4-Pro rows were executed on **V3 Instant** and
  **V3 Expert** (the models the interface offered); no V4-Pro output exists.
- **Gemini (conditional):** executed as **3.1 Pro (ext. thinking ON)** and
  **3.6 Flash (ext. thinking OFF/ON)** — the free-access/quota criterion was
  satisfied in practice for these rows.
- **Claude:** split into **Sonnet 5 Medium (default)** and **Sonnet 5 max**
  (long-reasoning run).
- **Qwen:** executed as four concrete variants (**3.8 Max Thinking / Fast,
  3.7 Plus Thinking / Fast**).
- **GLM (conditional):** attempted (**GLM 4.5**) but produced only a
  service-error page after repeated interface errors — classified
  `failed_external_output` by the intake protocol (no special rule) and
  excluded from quantitative evaluation.

## Exclusions (recorded reasons)

- **Bielik** — not in the roster; preserved as an already-observed
  **qualitative negative case** (all four EXP-003 free-web runs failed/
  truncated). No new quantitative baseline run unless a concrete
  methodological reason emerges (§11.7).
- **Venice** — excluded: a platform/interface, not an independent model;
  identifying the underlying model defeats the screening purpose (§5.3).
- **Local / self-hosted models** — out of scope for the practical screening
  (§5.1: the filter requires a normal web/chat interface).
- **Mistral** — not assumed available (the project coordinator currently has
  no access); may be added if access changes.
- **GLM 4.5** — practically unavailable at execution time (repeated service
  errors before any meaningful translation); preserved as a qualitative
  failure artifact.

## Files

- `DESIGN.md` — experiment design (Task 013), roster + protocol finalized
  (Task 016), execution approved (Task 017), execution + reconciliation
  recorded (Task 018).
- `base_instruction.txt` — the single direct-translation instruction
  (identical for every row; no guidance of any kind).
- `input/` — story-only source (gitignored, local) + derivation record.
- `operator-prompts/` — one self-contained canonical prompt per reconciled
  roster row (gitignored; `README.md` + `manifest.json` with prompt hashes
  are committed).
- `collected-sessions/` — the author's 19 raw session files (prompt + reply
  in one file), preserved byte-for-byte (gitignored; `README.md` + the
  read-only `collection_audit.*` evidence committed).
- `outputs/` — plan.json, collected runs, intake/evaluation/orthography,
  roster (gitignored; `README.md` committed).
- `scripts/run_exp004_phase1.py` — prepare / collect / collect-session /
  verify / evaluate / status / roster.
- `scripts/audit_exp004_collected.py` — read-only collection audit +
  reconciliation evidence (Task 018).
- `scripts/check_orthography.py` — includes EXP-004 in the character-level
  audit (Task 015 inventory).

## Phase 2

Phase 2 (guidance-method experiments) must NOT start before this Phase 1
screening is complete and reported. Task 018 records only a preliminary
screening observation about promising Phase 2 candidates — the final Phase 2
selection is a separate step.
