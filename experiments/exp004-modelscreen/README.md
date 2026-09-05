# EXP-004 — practical LLM model screening (Polish → Medžuslovjansky)

**Status: APPROVED FOR EXECUTION — Phase 1 screening kit ready (SODA Task
017, 2026-09-05).** EXP-003 is closed; no further human evaluation will be
designed or requested (D-042). The candidate roster and the clean
direct-translation protocol from `DESIGN.md` §5–6 are finalized (Task 016)
and execution was explicitly approved (Task 017). No LLM output exists yet:
the prompts are packaged, the plan is fixed, and the remaining step is the
project author executing the operator prompts in the models' web/chat
interfaces (external-execution convention, D-007) and returning the raw
replies.

Purpose: screen which LLMs are practically usable by the project (web/chat
interface, free access sufficient for ~1 story/day, identifiable
model/version/settings) and record their versioned no-guidance baseline
quality on the canonical story, before investing in guidance-method
experiments (Phase 2).

Design: `DESIGN.md` (Task 013; roster + protocol finalized Tasks 016/017).

## Phase 1 roster (11 candidate rows, fixed in `outputs/plan.json`)

| # | Row | Provider / interface | Filter status |
|---|---|---|---|
| 1 | GPT-5.6 Luna — thinking OFF | OpenAI ChatGPT | unconditional |
| 2 | GPT-5.6 Luna — thinking ON | OpenAI ChatGPT | unconditional |
| 3 | GPT Interslavic Teacher (custom GPT) | OpenAI ChatGPT custom GPT | unconditional (built-in system prompt unknown — confound, D-018) |
| 4 | Claude Sonnet 5 | Anthropic Claude | unconditional |
| 5 | Gemini | Google Gemini | **conditional**: only if practical free access/quota passes §5.1 |
| 6 | DeepSeek V4 Pro — DeepThink OFF | DeepSeek chat | unconditional |
| 7 | DeepSeek V4 Pro — DeepThink ON | DeepSeek chat | unconditional |
| 8 | Grok | xAI Grok | unconditional |
| 9 | Kimi | Moonshot Kimi | unconditional |
| 10 | Qwen | Alibaba Qwen Chat | unconditional |
| 11 | GLM | Zhipu GLM | **conditional**: only if practical web access satisfies the filter |

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
- Conditional rows (Gemini, GLM) that fail the practical access/quota check
  at execution time are excluded from the quantitative screening and their
  exclusion is recorded — do not run them on a technically-free but
  practically unusable tier.

## Files

- `DESIGN.md` — experiment design (Task 013), roster + protocol finalized
  (Task 016), execution approved (Task 017).
- `base_instruction.txt` — the single direct-translation instruction
  (identical for every row; no guidance of any kind).
- `input/` — story-only source (gitignored, local) + derivation record.
- `operator-prompts/` — one self-contained prompt per row (gitignored;
  `README.md` + `manifest.json` with prompt hashes are committed).
- `outputs/` — plan.json, collected runs, intake/evaluation/orthography
  (gitignored; `README.md` committed).
- `scripts/run_exp004_phase1.py` — prepare / collect / verify / evaluate /
  status / roster.
- `scripts/check_orthography.py` — includes EXP-004 in the character-level
  audit (Task 015 inventory).

## How to execute a row (operator — the project author)

```text
1. python scripts/run_exp004_phase1.py prepare --date <planned-date>
   (already done for 2026-09-06: prompts + plan written locally)
2. Open operator-prompts/<file>.md, copy the ENTIRE file, paste it into the
   model's web/chat interface with the row's settings (thinking/DeepThink
   toggle, custom GPT), save the complete reply byte-for-byte.
3. python scripts/run_exp004_phase1.py collect --run <run_id>
   --output <reply-file> --generation-date <actual> \
   --status collected_external_output|collected_partial_output|failed_external_output \
   --access-verdict pass|fail|unknown --access-note "<quota observation>"
4. python scripts/run_exp004_phase1.py verify        (completeness gate)
   python scripts/run_exp004_phase1.py evaluate --run <run_id>
5. After all rows: python scripts/run_exp004_phase1.py roster
```

The full protocol (recording, output handling, gate, evaluation,
within-provider variant deltas, anti-leak rules) is in `DESIGN.md` §6–8 and
`operator-prompts/README.md`. Phase 2 (guidance-method experiments) must NOT
start before this Phase 1 screening is complete and reported.
