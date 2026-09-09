# Phase repeat — controlled repeated generation (EXP-004, SODA Task 025)

**Status: COMPLETED — COLLECTED, AUDITED AND ANALYSED (Task 026,
2026-09-09).** This directory runs the controlled repeated-generation
experiment that estimates run-to-run **stochastic variation** in EXP-004
and turns the single-run Phase 1 → Phase 2A delta into a
distribution-shift-vs-variation statement:

> For the same model/configuration and the same translation task, how much
> does measured Interslavic resource coverage vary between independent
> generations, and is the observed Phase-2A corpus-priming shift larger
> than that variation?

Headline (descriptive): the research lead collected **114/120** planned
runs; the Task-026 audit kept every raw output untouched, recorded the
deviations, and found **106 usable** runs (8 partial, 0 invalid, 6 never
collected). The repeated mean Δ `mean(primed) − mean(direct)` canonical
was positive for **16/16** configurations with both conditions usable
(mean **+6.93 pp**), the Task-024 single-run direction reproduced in
**15/15** rows with an old delta, and for most configurations the shift
is larger than the measured within-condition spread (median SD ≈ 1.5 pp
direct / ≈ 0.9 pp primed). Full evidence, tables and figures in
`REPORT.md` + `analysis/`.

## Kit layout (committed vs local)

| path | tracked | content |
|---|---|---|
| `README.md` | committed | this file (protocol, kit, collection record) |
| `REPORT.md` | committed | dedicated experiment report (research question, design, collection audit + reconciliation, deviations, validation, metrics, repeated statistics, Task-024 comparison, figures, limitations, next step) — **results written (Task 026)** |
| `operator-prompts/manifest.json` | committed | hash-only prompt manifest (files: prompt hashes + run ids + source/corpus hashes); no story/corpus text |
| `operator-prompts/*.md` | **gitignored** | operator prompt files incl. the collected raw replies (embed the copyrighted Polish story and/or the reference corpus — local only) |
| `outputs/README.md` | committed | outputs index (below) |
| `outputs/plan.json`, `outputs/collection-checklist.md`, `outputs/audit.json`+`audit.md`, `outputs/roster.json`+`roster.md`, run dirs | **gitignored** | deterministic plan + human checklist + Task-026 machine-readable audit + intake roster + collected outputs (local only) |
| `analysis/README.md` | committed | analysis index + results summary |
| `analysis/*` (dataset/analysis JSON+MD, figures A–E) | **gitignored** | deterministic derived outputs of `scripts/analyze_exp004_repeats.py` |

## Planned sample

- **Primary (108 planned generations):** the original **18 usable EXP-004
  configurations** (Phase-1 roster numbers 01–10, 12–19; GLM 4.5 = 11
  excluded) × 2 conditions × 3 independent fresh-session replicates.
- **Exploratory (12 planned generations):** Dola 3.8 Fast (20) + Dola 3.8
  Pro (21) × the same 6-run scheme — `exploratory: true`, prepared but
  **never merged into the primary n=18 statistics**; the research lead
  decides whether to execute them.
- 120 planned runs / 180 prompt files, dated `2026-09-08` (the planned
  generation date) in the run ids.

### Conditions and replicates

| condition | replicate files | content |
|---|---|---|
| `direct` | `direct-<NN>-<model>-<version>-r0<k>.md` | fresh session; the exact Phase-1 direct prompt (same Polish source + translation instruction); no corpus/dictionary/examples/scaffolding |
| `primed` | `primed-<NN>-…-r0<k>-msg1.md` + `…-msg2.md` | fresh session; msg1 = the complete three-register corpus (`phase2a-authentic-isv` v1, study-as-reference instruction only); msg2 = exact Polish source + translation instruction; translation collected after the corpus |

`r01`/`r02`/`r03` are **replication blocks, not matched linguistic
samples**: each replicate is an independent fresh session with the exact
same prompt bytes; only stochastic generation and unavoidable
interface/server variation may differ.

### Run ids (6-field extension of the canonical scheme)

```
<date>__<provider>__<model>__<model_version>__<condition>__<replicate>
condition = direct | primed ; replicate = r01 | r02 | r03
```

Example: `2026-09-08__anthropic__claude__sonnet-5__primed__r02`. The sixth
field and the distinct condition tokens keep repeat ids unambiguously
different from Phase-1 (`…__direct`, 5 fields) and Phase-2A
(`…__p2a-ctl|p2a-primed`, 5 fields) ids.

## Authoritative hashes reused (fail-loud byte gates in `prepare`)

- Source story: SHA-256 `5de968a6214d3d64bdb586b5121f494c4bb107e33546487a86bf8ecc57280723`
  (the same authoritative Polish source used by Phase 1 / Phase 2A).
- Corpus: SHA-256 `aaad28e43935a40313585d77a33bfc788d97e8d69b081f9486af74d52ca1a857`
  — corpus id `phase2a-authentic-isv` v1, the established three-register
  corpus (literary/narrative `Tuta historija` excerpt; artistic/poetic
  Latin-only deduplicated *Ahoj, Slovjani!* album; informative/
  encyclopedic ISV Wikipedia *Sadovničstvo*), byte-identical across every
  primed replicate.

`scripts/run_exp004_repeats.py prepare --date <date>` refuses to run if
the source or corpus bytes differ from these records, and every generated
prompt is SHA-256-hashed into the manifest. Replicate prompt linguistic
bodies are byte-identical within (configuration, condition) by design —
only run metadata changes between replicates.

## Protocol for the research lead (collection)

1. Work in **replicate blocks** per configuration to reduce temporal/
   interface confounding: `r01` direct → `r01` primed → `r02` direct →
   `r02` primed → `r03` direct → `r03` primed (the checklist in
   `outputs/collection-checklist.md` is ordered exactly so; a different
   global model order is acceptable — timestamps are recorded).
2. **Every session is fresh.** Do NOT continue a generation into another
   replicate, feed a previous translation, ask for improvements, show
   evaluation results, reuse history, reuse a corpus-primed session, tell
   the model it is a repeat, or change wording between replicates.
3. Paste the exact prompt file bytes. For `primed`, send msg1 first, wait,
   then send msg2 in the SAME fresh session and collect the translation.
4. No scaffolding, dictionary candidates, morphology hints, grammar
   annotations, post-hoc repair, evaluator feedback, or human guidance —
   this is a clean stochastic-repeat experiment.
5. Save each raw reply **msg2-style** inside its canonical operator prompt
   file (prompt part through the closing `## Output` marker unchanged;
   the reply replaces the trailing boilerplate) — the same record shape as
   Phase-2A (Task 021) — or save a full session transcript file and point
   `collect-session` at it.
6. Record per run (in `collect-session` / `collect-msg2` metadata):
   collection date/time, model/configuration, condition, replicate,
   visible interface settings (thinking/reasoning toggle, mode, displayed
   model name, visible temperature/sampling, web/search — or "not
   exposed"), any continuation/retry, any deviation from protocol.
7. If an interface forces a deviation, do NOT silently normalize it —
   record it as metadata (known Phase-2A deviations below are expected to
   recur).

### Known Phase-2A interface deviations (preserve + record, do not fix)

- **Gemini:** corpus delivery is limited (msg1 may need to be sent in
  parts); extended-thinking toggle can reset between messages.
- **Claude:** free-tier interruptions / token-limit continuations possible;
  Claude Sonnet 5 max has practical >45-min / token-limit problems.
- **GPT Interslavic Teacher:** custom system prompt unknown (recorded
  identity only).
- **Dola (exploratory):** identity recorded from the interface header,
  not independently verifiable.

## Collection record (Task 026 audit, 2026-09-09)

- 114/120 runs collected by the research lead (102 primary + 12
  exploratory); 6 primary primed runs were **never collected** (Gemini
  3.1 Pro and Qwen 3.8 Max Thinking, all 3 replicates) — pristine prompt
  files, preserved, not fabricated.
- Task-026 audit (`scripts/audit_exp004_repeats.py` → local
  `outputs/audit.json`/`audit.md`): every collected record validated
  against the Task-025 manifest and the authoritative deterministic
  renders (prompt hash gates OK, source/corpus SHA-256 OK); no duplicate
  output, no source echo, no cross-run contamination.
- Intake: **106 usable (complete)**, 8 partial (end-marker soft
  failures only — `## KONEC`-style wrapped markers), 0 failed. Partial
  outputs are preserved and excluded from usable statistics.
- Recorded deviations (not repaired): Grok identity operator-header edit
  (6 runs; model-facing bytes identical); Claude Sonnet 5 — max ran with
  thinking/reasoning **OFF** (6 runs; configuration not renamed, not
  silently merged with its Task-024 record); Gemini primed corpus
  delivered in two messages (6 runs; corpus tail verified intact);
  Dola Pro r03 msg1 one extra blank header line (1 run).
  `fresh_session_proof: unavailable` for all runs.

## Commands

```bash
# 1) Prepare (deterministic, hash-gated) — already done for 2026-09-08:
.venv/bin/python scripts/run_exp004_repeats.py prepare --date 2026-09-08

# 2) After the author saves each raw reply msg2-style in its prompt file:
.venv/bin/python scripts/run_exp004_repeats.py collect-msg2 --run <run_id> \
    --status collected --access-verdict pass --generation-date 2026-09-08 \
    [--interface-settings "…"] [--access-note "…"]

#    or, for full session transcripts saved as separate files:
.venv/bin/python scripts/run_exp004_repeats.py collect-session --run <run_id> \
    --session <path-to-session-file> --status collected --access-verdict pass \
    --generation-date 2026-09-08

# 3) Verify + evaluate + roster + status:
.venv/bin/python scripts/run_exp004_repeats.py verify
.venv/bin/python scripts/run_exp004_repeats.py evaluate --run <run_id>   # per collected run
.venv/bin/python scripts/run_exp004_repeats.py roster
.venv/bin/python scripts/run_exp004_repeats.py status

# 4) Analysis (deterministic; no-results scaffold until data exists):
.venv/bin/python scripts/analyze_exp004_repeats.py
```

Intake rules (unchanged from Phase 1/2A): raw outputs are immutable; a run
that is partial/corrupted/interrupted is preserved, marked unusable with
the reason, and a re-run receives a NEW run id (never an overwrite).
Evaluation uses the unmodified Task-008 evaluator + orthography audit
(canonical / broader coverage, unresolved rate, orthography anomaly
buckets — definitions unchanged for comparability).

## Tests

`tests/test_exp004_repeats.py` (26 tests): exactly 18 primary
configurations × 2 conditions × 3 replicates = 108 planned runs + 12
exploratory; no duplicate run ids; direct/primed separation; prompt/
source/corpus hashes; replicate prompt byte-identity; prompt-body fidelity
vs Phase-1/Phase-2A; contamination rejection (corpus-in-direct, corpus
order in primed transcripts); msg2-style records; no overwrite; exact
stats/deltas (incl. old-delta join, no-Dola-contamination of primary);
deterministic ordering + byte-identical figures; no-results scaffold;
partial/missing-results handling in the selection table (n=0 → n/a, n=1 →
no SD overreach).

`tests/test_audit_exp004_repeats.py` (10 tests): audit script on a
synthetic kit — missing-run detection (pristine files never fabricated),
collected-run detection, prompt-part byte validation (direct/msg1/msg2),
operator-metadata header-edit tolerance (Grok-style), msg1 corpus-tail
integrity, end-marker/structural flags, reply preservation, manifest
consistency (dup/extra/missing), deviation registry presence, roster
verdict merge into reconciliation counts.

Run both with `.venv/bin/python -m pytest tests/test_exp004_repeats.py
tests/test_audit_exp004_repeats.py`.
