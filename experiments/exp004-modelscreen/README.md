# EXP-004 — practical LLM model screening (Polish → Medžuslovjansky)

**Status: PHASE 1 EXECUTED + PHASE 2A (corpus priming) EXECUTED, COLLECTED
AND EVALUATED (SODA Tasks 017/018/019/020/021, 2026-09-05…07); TASK 022
(2026-09-07) PREPARED AND TASK 023 (2026-09-07) COLLECTED + EVALUATED —
THE DOLA 3.8 PHASE-1 DIRECT BASELINES; TASK 024 (2026-09-07) FULL
ANALYSIS COMPLETE — PHASE 1 → PHASE 2A CORPUS-PRIMING EVIDENCE BASE;
**TASK 025 (2026-09-07) PHASE-REPEAT KIT PREPARED — controlled repeated
generation, execution-ready, NO LLM RESULTS YET.** EXP-003
is closed; no further human evaluation will be designed or requested
(D-042). **TASK 026 (2026-09-09) REPEAT COLLECTION AUDITED +
EVALUATED + ANALYSED; TASK 027 (2026-09-09) ASSISTANT-RESEARCH-BUNDLE
BUILT; TASK 029 (2026-09-09) PHASE-2B HIGH-OVERLAP KIT PREPARED (NOT
EXECUTED) + AUTHENTIC-CORPUS SELF-EVALUATION COMPLETE; TASK 030
(2026-09-09) HIGH-OVERLAP STORY FROZEN (v1) + 42-RUN KIT GENERATED —
STILL NOT EXECUTED; LOW-OVERLAP (`Podkłady`) RESERVED FOR THE NEXT
STAGE.** The project author executed the Phase 1 screening sessions in the
external web/chat interfaces; the collected material was audited and
reconciled against the deterministic prompt package (Task 018) and the
reconciled runs were run through the intake gate, the deterministic
evaluator, and the orthography audit. **18 of 19 Phase-1 runs are complete
and quantitatively usable; GLM 4.5 is the single failed/excluded run
(service-error artifact).** The author then executed all 18 Phase-2A
corpus-primed sessions plus two exploratory runs of a newly discovered
model recorded as **Dola 3.8** (runs 20/21); Task 021 audited all 20
records, integrated the Dola runs as exploratory additions (separate from
the 18-model roster, no Phase-1 baseline), and evaluated everything through
the same deterministic pipeline. **Task 022 (2026-09-07) prepared the two
missing Phase-1 DIRECT baselines for Dola 3.8 Fast/Pro retrospectively**
(canonical direct operator prompts in `operator-prompts/`, plan rows
`pending_manual_collection`; `link-baselines` wired the Phase-2A Dola rows
to them). **Task 023 (2026-09-07): the author executed both Dola Phase-1
direct baselines; the raw replies were collected through the existing
Phase-1 `collect-session` intake (msg2-style records inside the operator
prompt files), verified complete, and evaluated with the same deterministic
pipeline** — the Phase-2A `compare` now reports real within-Dola
Phase 1 → Phase 2A deltas for runs 20/21 (see `phase2a/outputs/compare.md`).
Dola remains an exploratory extension. **Task 024 (2026-09-07) turned the
completed dataset into a deterministic, read-only research analysis**
(`analysis/` directory + `scripts/analyze_exp004_phase2a.py`): a
20-configuration dataset, Phase-1 and Phase-2A rankings (four separate
dimensions), the priming Δ table, descriptive statistics + exploratory
exact paired tests, baseline-dependence and baseline-vs-primed Spearman
correlations, family and orthography analyses, a master table, charts A–G
and a poster draft — with explicit supported / suggestive / not-established
conclusions and **no single winner score**. Dola stays `exploratory:
true`; Phase 2B is documented but NOT executed. The Phase 1 evidence table is
`outputs/roster.md`; the Phase-2A evidence is under
`phase2a/outputs/roster.md` (38 rows) and `phase2a/outputs/compare.md`;
the raw sessions are preserved byte-for-byte under `collected-sessions/`.
**Task 025 (2026-09-07) prepared the controlled repeated-generation kit**
under `repeats/` (see `repeats/README.md` and `repeats/REPORT.md`):
108 primary planned runs (the original 18 configurations ×
direct/primed × 3 independent fresh-session replicates r01–r03) + 12
exploratory Dola 3.8 Fast/Pro runs (`exploratory: true`, never merged
into the primary n=18 statistics) — deterministic, hash-gated prompt
preparation (`scripts/run_exp004_repeats.py prepare --date 2026-09-08`),
collection/verify/evaluate reusing the existing machinery, and a
deterministic analysis kit that replaces the single Task-024 delta with
`mean(primed) − mean(direct)` over replicate distributions
(`scripts/analyze_exp004_repeats.py`, figures A–E). **Task 026
(2026-09-09) audited, evaluated and analysed the collection** (see
`repeats/README.md`, `repeats/REPORT.md`, `repeats/analysis/README.md`
and the compact independent-analysis export in
`assistant-research-bundle/`, Task 027). No LLM was ever called by any
preparation/audit/analysis script. **Task 029 (2026-09-09) prepared the
Phase-2B HIGH-overlap test and self-evaluated the authentic corpus**:
the HIGH-overlap kit (`phase2b/` + `scripts/run_exp004_phase2b.py`) plans
42 deterministic runs (7 shortlisted configurations × direct/primed × 3
fresh-session replicates) on the deliberately corpus-inspired story
`Iskra i Wieloryb` (regime `high_overlap_corpus_inspired`, NOT
`independent_same_topic`). **Task 030 (2026-09-09) extracted and froze
the HIGH-overlap story (v1: sha256 `ab8a0dcf…`, 30 061 B / 440 lines,
from the author's story bank section `# 3.` via the deterministic
`scripts/extract_phase2b_high_story.py`) and generated the 42-run kit
(`prepare --date 2026-09-09`; regeneration byte-identical, verified)** —
**no translations exist**, and the next manual operator step is the 42
HIGH-overlap translations (`phase2b/outputs/collection-checklist.md`);
the LOW-overlap source `Podkłady` (bank section 4) is reserved for the
next stage and was NOT prepared. The
corpus self-evaluation (`phase2a/corpus-selfeval/` +
`scripts/selfeval_exp004_corpus.py`) measured the authentic corpus itself
with the unchanged evaluation stack as a reference point: combined
8 096 lexical tokens — canonical 80.50 %, broader 89.17 %, unresolved
19.50 %, orthography-out 47; per-register numbers in §9.1 of
`docs/research-roadmap.md`. **Task 030 re-verified reproducibility**:
re-running the deterministic self-evaluation reproduces the stored
reports byte-identically. No LLM was ever called by any
preparation/audit/analysis script.

Purpose: screen which LLMs are practically usable by the project (web/chat
interface, free access sufficient for ~1 story/day, identifiable
model/version/settings) and record their versioned no-guidance baseline
quality on the canonical story, before investing in guidance-method
experiments (Phase 2).

Design: `DESIGN.md` (Task 013; roster + protocol finalized Tasks 016/017;
execution + reconciliation Tasks 017/018; Phase 2A corpus-priming kit
prepared Task 019; corpus revised to three authentic registers Task 020;
Phase-2A execution audited + evaluated + Dola 3.8 exploratory runs
integrated Task 021; Dola Phase-1 direct baselines prepared Task 022,
executed + collected + evaluated Task 023; full Phase 1 → Phase 2A
research analysis Task 024; phase-repeat kit prepared Task 025 — §14;
Phase-2B HIGH-overlap kit prepared + corpus self-evaluation Task 029,
HIGH-overlap story frozen + 42-run kit generated Task 030 — §15).

## Phase 2A — full-roster corpus priming (executed and evaluated, Task 021)

Phase 2A tests whether authentic Medžuslovjansky corpus exposure
immediately before translation changes each model's generation
(in-context learning / corpus priming / contextual grounding /
reference-text conditioning — NOT training, NOT reconstruction). For every
Phase-1-usable configuration (18; GLM excluded) it prepares:

- **control** (`p2a-ctl`): the Phase-1 clean direct task — the Phase-1
  baseline outputs satisfy this condition;
- **corpus-primed** (`p2a-primed`): Prompt 1 = fixed authentic reference
  text — the combined three-register corpus ("Tuta historija" excerpt +
  Latin-script *Ahoj, Slovjani!* songs + ISV Wikipedia *Sadovničstvo*;
  ≈58 KB, ~8 200 tokens, sha256 `aaad28e4…`, corpus id
  `phase2a-authentic-isv` v1) with study-as-reference instructions;
  Prompt 2 = the same Polish story, translated using the reference — both
  in ONE fresh session.

The author completed all 18 primed sessions **and** two exploratory Dola
3.8 runs (20/21; author-recorded "ByteDance" identity, added after the
18-model roster was prepared — see `phase2a/README.md`). Task 021 audited
all 20 runs, registered them via `collect-msg2` (each run's record is the
operator msg2 prompt file with the raw reply appended after `## Output`),
verified corpus integrity (corpus SHA-256
`aaad28e43935a40313585d77a33bfc788d97e8d69b081f9486af74d52ca1a857`
byte-identical in all 20 primed msg1 files), evaluated all 20 through the
deterministic pipeline, and compared the 18 baseline-backed configurations
primed-vs-Phase-1. Dola had **no Phase-1 baseline** at Task 021 — it was
reported as an exploratory observation only, and no priming effect was
claimed.

**Task 022 (2026-09-07) — Phase-1 baselines for Dola prepared:** the two
missing Phase-1 DIRECT baselines for the exploratory Dola configurations
were prepared retrospectively through the existing Phase-1 direct protocol
(`scripts/run_exp004_phase1.py extend-direct --date 2026-09-07` →
`operator-prompts/20-dola-3.8-fast.md` + `21-dola-3.8-pro.md`, plan rows
`pending_manual_collection`; then `link-baselines` wired the Phase-2A Dola
rows' `baseline_run_id`). This is an exploratory extension, NOT part of the
original planned 18.

**Task 023 (2026-09-07) — Dola Phase-1 baselines executed, collected and
evaluated:** the author executed both baselines in fresh ByteDance
sessions (direct translation only — no corpus, no scaffold, no dictionary,
no previous Dola conversation) and saved each raw reply inside the
operator prompt file itself (the prompt part through the closing
`## Output` marker is byte-identical to the canonical prompt; the trailing
'Return the complete …' boilerplate was replaced by the reply — the same
msg2-style record shape used for the Phase-2A runs in Task 021). Both
records passed the Phase-1 `collect-session` intake + `verify` completeness
gate (verdict `complete`, usable) and were evaluated with the same
deterministic pipeline. `compare` now reports real **within-Dola
Phase 1 → Phase 2A** deltas for runs 20/21 (Dola Fast: P1 canonical
38.87 % → P2A 67.07 %; Dola Pro: 65.08 % → 71.75 %; see
`phase2a/outputs/compare.md`). No priming effect is claimed beyond the
recorded deltas; Dola remains exploratory (not part of the original
18-configuration roster).

See `phase2a/README.md` (kit + 18-config roster + Dola exploratory section
+ protocol + Task-021 deviations and manual-execution constraints), the
DESIGN §13, and `phase2a/outputs/` (38-row plan; roster; compare).

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
| 8 | Grok 4.5 Fast\* | xAI Grok | pass | complete |
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

\* Row 8 (Grok): the configuration is **Grok 4.5 Fast** —
operator-reported identity "Grok 4.5, built by xAI (fast)" (recorded in
the row-08 line, Tasks 021/026; not independently verified). The
row-08 prompt-file / run-id token `unknown` was genuinely recorded at
Task 018 and is preserved as historical provenance; canonical alias
`xai__grok__fast`. See `grok-identity.md` (authoritative) and
`grok-identity-map.json`.

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
  recorded (Task 018), Phase 2A corpus-priming design §13 (Task 019).
- `grok-identity.md` / `grok-identity-map.json` — **authoritative canonical
  Grok configuration note + machine-readable audit map (Task 031)**:
  "Grok 4.5 Fast" (operator-reported) for the current line, historical
  `unknown` identifiers preserved with canonical alias `xai__grok__fast`,
  no Grok Build run in repository evidence.
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
- `analysis/` — Task-024 research analysis: `README.md` (committed;
  interpretation, candidates, next experiments) + gitignored
  `dataset.json` / `analysis.json` / `analysis.md`, `figures/chart_a..g.svg`
  and `poster.{md,html}`.
- `phase2a/` — Phase 2A corpus-priming kit (Tasks 019/020/021): `README.md`
  (protocol + 18-config roster + Dola exploratory section + Task-021
  record), `corpus/` (authoritative three-register combined corpus, local),
  58 operator prompt files + `manifest.json` (hashes only; 4 exploratory
  Dola entries), `outputs/` (38-row plan incl. 2 exploratory Dola rows;
  collected+verified+evaluated runs; roster; compare) — executed and
  evaluated Task 021; Dola Phase-1 baselines collected + evaluated Task 023.
- `scripts/run_exp004_phase1.py` — prepare / **extend-direct (Task 022)** /
  collect / collect-session / verify / evaluate / status / roster.
- `scripts/run_exp004_phase2a.py` — Phase 2A prepare / collect /
  collect-session (contamination-controlled) / collect-msg2 /
  extend-exploratory / **link-baselines (Task 022)** / verify / evaluate /
  status / roster / compare
  (Tasks 019/020/021/022; Dola Phase-1 baselines executed + collected via
  `collect-session` + evaluated Task 023).
- `scripts/audit_exp004_collected.py` — read-only collection audit +
  reconciliation evidence (Task 018).
- `scripts/analyze_exp004_phase2a.py` — deterministic Task-024 analysis
  generator (dataset / rankings / Δ table / stats + exploratory tests /
  correlations / families / orthography / master table / charts A–G /
  poster).
- `repeats/` — phase-repeat kit + results (Tasks 025/026): `README.md`
  (protocol + collection record) + `REPORT.md` (dedicated experiment
  report with results) + `operator-prompts/` (180 prompt files — direct /
  primed msg1+msg2 × r01–r03 × 18 primary + 2 exploratory Dola configs;
  gitignored; `manifest.json` hash-only committed) + `outputs/` (120-run
  plan dated 2026-09-08, collection checklist, roster, audit — gitignored;
  `README.md` committed) + `analysis/` (deterministic results set:
  `dataset.json`, `analysis.json`, `analysis.md`, figures A–E — gitignored;
  `README.md` committed).
- `assistant-research-bundle/` — **compact machine-readable research
  export for independent analysis (Task 027)**: per-run `results.json` +
  `results.csv` (120 planned runs), `summary.json`, `audit.json`,
  `deviations.json`, `provenance.json`, `manifest.json`, `methodology.md`
  and figures A–E (PNG + SVG). Self-contained and deterministic — an
  independent analyst can reconstruct every Task-026 quantitative
  conclusion from it without the raw experiment directory.
- `phase2a/corpus-selfeval/` — **authentic-corpus self-evaluation
  reference point (Task 029)**: `corpus_selfeval.json` + `.md`
  (combined + per-register canonical/broader/unresolved/orthography
  metrics through the unchanged Task-008 evaluator + orthography audit),
  `model_comparison.md` (descriptive corpus-vs-model-output comparison),
  `README.md`; per-dataset isv-eval CLI scratch in `.scratch/`
  (gitignored).
- `phase2b/` — **Phase-2B HIGH-overlap test (Task 029; PREPARED — NOT
  EXECUTED)**: `README.md` (protocol: 7 shortlisted configs ×
  direct/primed × 3 replicates = 42 planned translations; H-HIGH
  hypothesis; HIGH/LOW/UNSEEN regime table), `input/` (author-freezes
  the story here; provenance note), `operator-prompts/` (generated
  prompts after `prepare`), `outputs/` (plan + checklist after
  `prepare`).
- `scripts/run_exp004_repeats.py` — phase-repeat orchestrator
  (prepare / collect-session / collect-msg2 / verify / evaluate / status /
  roster; Task 025).
- `scripts/audit_exp004_repeats.py` — read-only Task-026 collection audit
  + reconciliation evidence (gitignored `outputs/audit.json`).
- `scripts/analyze_exp004_repeats.py` — deterministic repeated-generation
  analysis (stochastic stats, mean-primed−mean-direct vs old delta,
  figures A–E, selection views; std-lib only).
- `scripts/build_assistant_research_bundle.py` — deterministic
  assistant-research-bundle generator + standalone verifier (Task 027).
- `scripts/run_exp004_phase2b.py` — Phase-2B HIGH-overlap kit prep
  (`freeze-story` / `prepare`; 7 configs × 2 conditions × 3 replicates
  = 42 planned runs; hash-gated; extends `run_exp004_repeats.py`;
  Task 029; never calls an LLM).
- `scripts/selfeval_exp004_corpus.py` — authentic-corpus self-evaluation
  (combined + 3 registers through the unchanged evaluator + orthography
  audit; cross-register composition; corpus-vs-model comparison;
  Task 029; deterministic).
- `scripts/check_orthography.py` — includes EXP-004 in the character-level
  audit (Task 015 inventory).

## Phase 2

Phase 2 (guidance-method and corpus-priming experiments) must NOT start
before this Phase 1 screening is complete and reported. Task 018 records
only a preliminary screening observation about promising Phase 2
candidates. **Phase 2A (full-roster corpus priming) was executed and
evaluated in Task 021** (20 primed runs: the 18 baseline-backed original
configurations + two Dola 3.8 exploratory runs); the
primed-vs-baseline evidence is in `phase2a/outputs/compare.md`. **Task 022
prepared the Phase-1 DIRECT baselines for the two Dola exploratory runs;
Task 023 executed, collected and evaluated them**, so `compare` now reports
the within-Dola Phase 1 → Phase 2A deltas; no priming effect is claimed
beyond the recorded deltas. **Task 024 (2026-09-07) completed the full
deterministic research analysis of the 20-configuration dataset**
(`analysis/` README + gitignored dataset/analysis JSON/MD, charts A–G,
poster draft; generator `scripts/analyze_exp004_phase2a.py`): rankings,
priming Δ table, descriptive + exploratory statistics, baseline-dependence
and baseline-vs-primed correlations, family/orthography analyses,
supported/suggestive/not-established conclusions, research candidates and
≤ 3 recommended next experiments — no winner score. **Task 025
(2026-09-07) prepared the controlled repeated-generation kit**
(`repeats/`): 108 primary planned runs (18 configurations ×
direct/primed × 3 fresh-session replicates) + 12 exploratory Dola runs;
**Task 026 (2026-09-09) audited the collection (114 collected / 106
usable / 8 partial / 6 missing), evaluated every usable run and analysed
the repeated generation**: repeated Δ canonical is positive in 16/16
assessable primary configurations (mean ≈ +6.93 pp), the Task-024
single-run direction is reproduced in 15/15 rows with an old delta, and
the stochastic spread (median SD ≈ 1.49 pp direct / 0.87 pp primed) is
typically smaller than the shift. Full results: `repeats/REPORT.md` +
`repeats/analysis/`; the compact export for independent analysis is
`assistant-research-bundle/` (Task 027). **Task 029 (2026-09-09)
prepared the Phase-2B HIGH-overlap test** (`phase2b/`): 42 planned
translations on the deliberately corpus-inspired story `Iskra i
Wieloryb` (regime `high_overlap_corpus_inspired`) with the seven
shortlisted configurations — direct prompts corpus-free, primed prompts
full-corpus hash-gated, corpus never shortened for Gemini. The author's
story freeze is still required and **nothing has been executed**; the
next manual operator step is the 42 HIGH-overlap translations.
LOW-overlap and UNSEEN-DOMAIN variants remain future work. The
authentic-corpus self-evaluation reference point (Task 029) is in
`phase2a/corpus-selfeval/`; combined corpus canonical coverage is
80.50 % under the same metrics used for model outputs (roadmap §9.1).
