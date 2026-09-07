# Phase repeat — controlled repeated generation (EXP-004, SODA Task 025)

**Status: KIT PREPARED AND TESTED (2026-09-07), EXECUTION-READY — NO LLM
RESULTS YET.** This directory prepares the controlled repeated-generation
experiment that estimates run-to-run **stochastic variation** in EXP-004
and turns the single-run Phase 1 → Phase 2A delta into a
distribution-shift-vs-variation statement:

> For the same model/configuration and the same translation task, how much
> does measured Interslavic resource coverage vary between independent
> generations, and is the observed Phase-2A corpus-priming shift larger
> than that variation?

No LLM has been called by any script here. The research lead executes the
prepared prompts manually in the model interfaces; the raw outputs are
then returned for the deterministic collection/evaluation/analysis
pipeline. Do NOT report experimental results before collection.

## Kit layout (committed vs local)

| path | tracked | content |
|---|---|---|
| `README.md` | committed | this file (protocol, kit, collection record) |
| `REPORT.md` | committed | dedicated experiment report (research question, design, sample, manifest, protocol, deviations, validation, metrics, statistics, results, figures, Task-024 comparison, limitations, next step) — results sections say **no results yet** |
| `operator-prompts/manifest.json` | committed | hash-only prompt manifest (180 files: prompt hashes + run ids + source/corpus hashes); no story/corpus text |
| `operator-prompts/*.md` | **gitignored** | 180 operator prompt files (embed the copyrighted Polish story and/or the reference corpus — local only) |
| `outputs/README.md` | committed | outputs index (below) |
| `outputs/plan.json`, `outputs/collection-checklist.md`, later roster/run dirs | **gitignored** | deterministic plan + human checklist + collected outputs |
| `analysis/README.md` | committed | analysis index + no-results scaffold explanation |
| `analysis/*` (dataset/analysis JSON+MD, figure placeholders) | **gitignored** | deterministic derived outputs of `scripts/analyze_exp004_repeats.py` |

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

`tests/test_exp004_repeats.py` (25 tests): exactly 18 primary
configurations × 2 conditions × 3 replicates = 108 planned runs + 12
exploratory; no duplicate run ids; direct/primed separation; prompt/
source/corpus hashes; replicate prompt byte-identity; prompt-body fidelity
vs Phase-1/Phase-2A; contamination rejection (corpus-in-direct, corpus
order in primed transcripts); msg2-style records; no overwrite; exact
stats/deltas (incl. old-delta join, no-Dola-contamination of primary);
deterministic ordering + byte-identical figures; no-results scaffold.
Run with `.venv/bin/python -m pytest tests/test_exp004_repeats.py`.
