# Project State

Updated: 2026-09-09 (SODA Task 028 — RESEARCH-STATE RECONSTRUCTION,
ROADMAP + TRANSLATION-METHOD SPECIFICATION: externally-discussed research
direction recorded in-repo — `docs/research-roadmap.md` (hypothesis,
completed-experiment record, key findings, Phase-2B shortlist + plan,
publication direction, stopping rule) + `docs/translation-method.md`
(intervention ladder A–E, pipeline hypotheses, evaluation layers); no
new experiments, no raw-output modification — see the Task-028
paragraph below. SODA Task 027 — EXP-004 ASSISTANT RESEARCH
BUNDLE COMPLETE: compact deterministic machine-readable export (120 per-run records, summary, audit, deviations, provenance,
methodology, figures A–E) — see the Task-027 paragraph below; SODA Task 026 — EXP-004 PHASE-REPEAT
EXECUTED, AUDITED AND ANALYSED: 114/120 planned runs collected by the
research lead, full Task-026 audit of the collected dataset against the
Task-025 manifest/authoritative renders with every raw output preserved,
**106 usable** runs (99 primary + 7 exploratory) evaluated through the
unmodified pipeline, repeated-generation analysis complete — see the
Task-026 paragraph below; Task 025 — EXP-004 PHASE-REPEAT KIT
PREPARED: controlled repeated generation to estimate run-to-run
stochastic variation and replace the single-run Phase-1 → Phase-2A delta
with a distribution-shift-vs-variation statement; Task 024 — EXP-004
FULL ANALYSIS COMPLETE:
Phase 1 → Phase 2A corpus-priming evidence base over the whole
20-configuration dataset, 18 original + 2 exploratory Dola 3.8, generated
deterministically by `scripts/analyze_exp004_phase2a.py`; artifacts under
`experiments/exp004-modelscreen/analysis/` — dataset/analysis JSON+MD,
charts A–G, poster draft, committed README; rankings on four separate
dimensions, priming Δ table, descriptive statistics + exploratory exact
paired tests, descriptive Spearman baseline-dependence (ρ ≈ −0.86
canonical / −0.84 broader over the original 18) and baseline-vs-primed
correlations, family + orthography analyses, practical-usability
dimension, master table, supported/suggestive/not-established
conclusions, research candidates, ≤ 3 recommended next experiments — **no
composite score, no winner**; Phase 2B not executed).

SODA Task 026 (2026-09-09) — AUDITED THE COLLECTED REPEATED-GENERATION
DATASET AND RAN THE REPEATED-GENERATION ANALYSIS. The research lead
collected **114/120** planned runs (102 primary + 12 exploratory Dola;
msg2-style records — raw reply appended to the canonical prompt file
after its `## Output` marker). `scripts/audit_exp004_repeats.py` (new;
tests `tests/test_audit_exp004_repeats.py`, 10) reconciled every run
against the Task-025 manifest + authoritative deterministic renders
without modifying any raw output; machine-readable + human audit in
`repeats/outputs/audit.{json,md}` (local, gitignored).
**Reconciliation: planned 120 (108 primary + 12 exploratory); collected
114; usable 106 (99 primary + 7 exploratory); partial 8 (3 primary + 5
exploratory — markdown-wrapped end markers only, e.g. `## KONEC`;
content complete; preserved and excluded from usable stats); invalid 0;
missing 6** — Gemini 3.1 Pro ext-think-ON primed r01–r03 and Qwen 3.8
Max Thinking primed r01–r03 were never collected (pristine prompt
files); no runs were fabricated and their repeated Δ is n/a. Hash gates
(source `5de968a6…`, corpus `aaad28e4…`, per-run plan shas) all OK; no
duplicate output, source echo, cross-run contamination, wrong
model/condition/replicate, stale file or malformed metadata found.
**Recorded deviations (not repaired):** (1) Grok identity
operator-metadata header edit in all 6 Grok runs (`unknown (unknown)` →
`Grok 4.5, built by xAI (fast)`, operator-reported, model-facing bytes
identical — identity recorded as operator-reported, not independently
verifiable); (2) **Claude Sonnet 5 — max ran with thinking/reasoning OFF
for all 6 repeats** (execution deviation; configuration identity NOT
renamed; not silently merged with the Task-024 record — comparability
affected); (3) Gemini primed reference-corpus message delivered in two
messages (`continue last prompt:`-style) for all 6 Gemini 3.6 Flash
primed runs — stored msg1 records verified to carry the byte-identical
study instruction + full authoritative corpus, so corpus integrity is
established; same class as the Task-021/024 Gemini deviation; (4) Dola
Pro primed r03 msg1 one extra blank header line (trivial).
`fresh_session_proof: unavailable` for all runs (msg2-style records carry
no machine-visible session provenance — absence of proof is not proof of
violation). All usable runs evaluated with the unmodified Task-008
evaluator + orthography audit; `scripts/analyze_exp004_repeats.py` wrote
the full deterministic results (`repeats/analysis/`, local). **Headline
(descriptive): repeated mean Δ canonical `mean(primed) − mean(direct)`
positive for 16/16 primary configurations with both conditions usable —
mean +6.93 pp (range +1.72…+15.91); Task-024 single-run direction
replicated in 15/15 rows with an old delta (mean old +6.33 pp vs mean
repeated +6.73 pp); stochastic spread typically smaller than the shift
(median SD ≈ 1.49 pp direct / ≈ 0.87 pp primed; only Qwen 3.8 Max Fast's
Δ +1.72 pp is below its own primed SD 5.83 pp); Gemini 3.6 Flash ON
+14.33 → +15.91 reproduced; Claude Sonnet 5 Medium +11.66 → +9.12
(stable primed SD 0.80, operationally clean); DeepSeek Expert ON
+5.14 → +3.77 (ON > OFF in both conditions); Dola Pro exploratory
+12.41 pp; Dola Fast's old +28.20 pp not re-estimable (repeated direct
condition unusable — intake partial); baseline dependence persists
(ρ ≈ −0.84 vs old ≈ −0.86).** Tests updated (`tests/
test_exp004_repeats.py` 26) + new audit suite; full suite green.
Recommended next experiment: Phase-2B unseen-topic transfer test.
Historical Task-024 conclusions untouched (reported as new follow-up
findings where repetition changed confidence). Full record:
`experiments/exp004-modelscreen/repeats/REPORT.md` (results written) +
`repeats/analysis/`; DESIGN §14 status updated.

SODA Task 027 (2026-09-09) — PACKAGED THE EXP-004 RESULTS AS A COMPACT
ASSISTANT-RESEARCH-BUNDLE FOR INDEPENDENT ANALYSIS. `scripts/
build_assistant_research_bundle.py` (deterministic, std-lib; tests
`tests/test_assistant_research_bundle.py`) generated
`experiments/exp004-modelscreen/assistant-research-bundle/` (1.5 MB, 21
files): **`results.json` + `results.csv` — one record per planned run
(120 = 108 primary + 12 exploratory Dola)** with per-replicate
r01–r03 metrics, hashes, orthography counts, deviation flags
(usable 106 / partial 8 / missing 6 — never fabricated; the missing
Gemini 3.1 Pro + Qwen 3.8 Max Thinking primed runs and the partial
runs stay excluded with reasons); `summary.json` (per-configuration
descriptive statistics recomputed over usable replicates + repeated
deltas + Task-024 old singles marked `historical_task024` — never
mixed into replicate distributions); `audit.json` (run-level Task-026
audit projection incl. hash gates + mechanical checks);
`deviations.json` (structured registry — Claude Max thinking OFF, Grok
identity, Gemini split corpus, Dola Pro blank line, fresh-session
proof, intake-partial); `provenance.json` (source `5de968a6…` + corpus
`aaad28e4…` + kit hashes + commits bc06858/2db827d/048c026 + evaluator
isv-eval 0.1.0); `manifest.json` (SHA-256 for every file);
`methodology.md`; `figures/` (A–E PNG + SVG). **Standalone
reconstruction: the verifier loads ONLY results/summary/audit and
recomputes every Task-026 headline (120/114/106/8/6; 16/16 positive
Δ canonical mean +6.93 pp; broader +3.88 pp; Task-024 direction 15/15;
median SD 1.49/0.87 pp; Qwen 3.8 Max Fast exception) — 15/15 checks
green; generator run twice → byte-identical.** Raw outputs are NOT
copied (raw/README.md explains on-demand export by run ID). Docs:
EXP-004 README + repeats/analysis README updated; full suite green.

SODA Task 028 (2026-09-09) — RECONSTRUCTED THE RESEARCH STATE AND
DIRECTION IN THE REPOSITORY (documentation only; no LLM calls, no new
experiments, no raw-output modification, no Phase 2B; all numbers
cross-checked against repo records — no historical correction was
required). New high-level docs:
`docs/research-roadmap.md` — project identity + scientific framing
(authentic target-language corpus context can improve LLM translation
into Interslavic without fine-tuning; generalization is the open
question), two goals (scientific vs practical translation workflow),
COMPLETED experiment record (EXP-001 baseline incl. broader-coverage
estimates; EXP-002 revision; EXP-003 scaffolding + one non-expert human
test, not repeated; EXP-005 = cross-resource audit of the 1 050
unresolved forms; orthography audit; EXP-004 Phase 1 leaders +
exclusions + Claude-Max >45-min limitation; Phase 2A corpus registers
R1–R3 + protocol + single-run table; repeated generation counts +
deviations + results), current interpretation (supported vs explicitly
NOT-claimed), PROPOSED Phase-2B shortlist of 7 representative configs
(Gemini 3.6 Flash ON/OFF, Claude Sonnet 5 Medium, DeepSeek V3 Expert
ON, Qwen 3.8 Max Fast, GPT-5.6 Luna, Grok 4.5 Fast; 7 × 3 × 2 = 42
translations, 21 paired comparisons) with variants 2B-A (corpus-inspired
Polish story) and 2B-B (unseen-topic biomedical-physics/electromedicine
material); original-story-not-biomedical distinction; do-not-shorten-
corpus-for-Gemini rule + separate future corpus-length ablation;
publication framing + working titles + paper structure; literature-
review direction; stopping rule.
`docs/translation-method.md` — evaluation layers 1–3 (never collapsed
into a composite), metric definitions, intervention ladder A–E with
COMPLETED evidence per rung (EXP-002 revision = output-side repair),
HYPOTHESIS pipeline orderings 1–5, non-additivity principle (effects
must be measured, not assumed to add), PROPOSED post-Phase-2B
pipeline-optimization experiment (2–3 configs; EXAMPLE-only numbers),
conceptual software architecture (automation with LLM calls under user
control).
Both are indexed from `README.md`, this layout, and `docs/ROADMAP.md`
(Task-028 entry). One clarification recorded: EXP-001/002 used the full
`op-pl.txt` source (`e3164ffc…`), EXP-003/004 the canonical story-only
file (`5de968a6…`). Full suite green.

SODA Task 025 (2026-09-08 planned generation date; kit prepared
2026-09-07) — prepared the deterministic controlled-repeat kit under
`experiments/exp004-modelscreen/repeats/` — **no LLM called, no results
yet; the research lead will manually execute the prepared prompts**.
Planned sample: **108 primary runs** (the original 18 usable EXP-004
configurations × direct/primed × 3 independent fresh-session replicates
`r01`/`r02`/`r03`) + **12 exploratory runs** (Dola 3.8 Fast/Pro × the
same 6-run scheme; `exploratory: true`, never merged into the primary
n=18 statistics; the research lead decides whether to execute them). 180
deterministic prompt files generated hash-gated by
`scripts/run_exp004_repeats.py prepare --date 2026-09-08` (source story
SHA-256 `5de968a6…`, Phase-2A corpus `phase2a-authentic-isv` v1 SHA-256
`aaad28e4…` — byte-identical to the authoritative records, fail-loud byte
gates; replicate prompt linguistic contents byte-identical within
(configuration, condition); only run metadata changes across replicates;
fresh-session rule encoded in the operator kit). Reuses the Phase-1/2A
machinery: intake validation via the existing completeness gate +
integrity checks (msg2-style records preserved; direct/primed
contamination controls incl. corpus-in-direct rejection; no repair of raw
outputs — unusable runs preserved + marked, new run id on re-runs);
Task-008 evaluator + orthography audit unmodified. Deterministic analysis
kit (`scripts/analyze_exp004_repeats.py`, std-lib only): small-sample
descriptive statistics (n=3: mean/median/sd/min/max/range), the new
primary quantity `mean(primed replicates) − mean(direct replicates)` kept
explicitly distinct from the old `P2A_single − P1_single`, replicate
blocks as a secondary descriptive view only (not paired tests), figures
A–E (replicate distributions / priming-delta distribution / stochastic
spread / old-vs-new delta / baseline-dependence revisit vs Task-024
ρ ≈ −0.86), three research-facing selection views + orthography
dimension, candidate focus (Claude Sonnet 5 Medium, DeepSeek V3 Expert
ON/OFF, Qwen 3.8 Max Fast, Gemini 3.6 Flash ON/OFF, Dola Fast/Pro),
supported/suggestive/not-established interpretation rules; with no
collected observations it writes an explicit no-results scaffold. Tests
`tests/test_exp004_repeats.py` (25 tests: 108+12 plan counts, no
duplicate ids, direct/primed separation, prompt/source/corpus hashes,
replicate byte-identity, msg2-style records, contamination rejection,
exact stats/deltas, deterministic figures); full suite **237 green**.
Companion `REPORT.md` + READMEs under `repeats/`; analysis scaffold at
`repeats/analysis/` (status: no_results).

SODA Task 021 (2026-09-07) executed, collected, audited and evaluated
EXP-004 Phase 2A — all 18 primed sessions completed by the author + two
exploratory runs of a newly discovered model recorded as **Dola 3.8**
(runs 20/21, "ByteDance — official web interface", author-recorded header
identity only, NOT part of the 18-model roster, NO Phase-1 baseline at
that time, no priming effect claimed); records
registered via `collect-msg2` (each run's operator msg2 prompt file + raw
reply appended after `## Output`; no machine same-session proof —
documented protocol deviation); corpus integrity re-verified (combined
file SHA-256 `aaad28e4…`, corpus id `phase2a-authentic-isv` v1
byte-identical in all 20 primed msg1 files); all 20 evaluated
deterministically (19 complete, 1 partial end-marker) and the 18
baseline-backed configurations compared primed-vs-Phase-1
(`phase2a/outputs/compare.md`); manual-execution constraints (Gemini
two-message corpus delivery / 3.1 Pro ingestion-vs- translation model
split / extended-thinking reset; Claude token-limit continuations)
documented; tests updated + new exploratory suite — full suite green.
**SODA Task 022 (2026-09-07) prepared the Phase-1 DIRECT baselines for the
two exploratory Dola 3.8 configurations** (runs 20/21 Fast/Pro):
canonical Phase-1 direct operator prompts rendered via
`run_exp004_phase1.py extend-direct` and plan rows marked
`pending_manual_collection` (nothing collected at that point, no metrics,
no fabricated deltas); `run_exp004_phase2a.py link-baselines` wired the
Dola p2a-primed rows' `baseline_run_id` to the prepared direct run ids
(`baseline_status: pending_collection`). **SODA Task 023 (2026-09-07): the
author executed both Dola Phase-1 direct baselines (fresh ByteDance
sessions, direct translation only); the raw replies were collected
msg2-style inside the operator prompt files through the existing Phase-1
`collect-session` intake, verified complete, and evaluated with the same
deterministic pipeline. `compare` now reports REAL within-Dola
Phase 1 → Phase 2A deltas for runs 20/21** (canonical coverage: Dola Fast
38.87 % → 67.07 % [+28.20 pp]; Dola Pro 65.08 % → 71.75 % [+6.67 pp];
full deltas in `phase2a/outputs/compare.md`). Dola stays an exploratory
extension (not part of the original 18-configuration roster; Task-020/021
historical records unchanged); no priming effect is claimed beyond the
recorded deltas.

## What this project is

**Interslavic LLM Lab** (`isv-llm-lab`) — a research lab for improving
LLM-generated Interslavic by constraining generation with existing lexical and
morphological resources. This is an open-source, non-profit, community research
project. **It is not an official Interslavic project.**

Research hypothesis:
> Modern LLMs can generate plausible-looking Interslavic while introducing
> vocabulary or forms actually borrowed from individual Slavic languages.
> Constraining generation with existing Interslavic resources may reduce this.

This is a hypothesis. The first experiment must establish a baseline before
any constrained system is judged against it.

## Current status (as of SODA Task 028)

| Area | Status |
|---|---|
| Repository initialized | ✅ README + SODA docs + source inventory |
| Dictionary resources audited | ✅ `sonic16x/interslavic` + generated `basic.json` |
| Morphology engines audited | ✅ JS (`@interslavic/morphology`, tested live) and Rust (`gold-silver-copper/interslavic`, static) |
| Frequency/synonym resources audited | ✅ `medzuslovjansky/interslavicfreq` |
| Grammar consistency audit | ✅ `docs/GRAMMAR_AUDIT.md` |
| Ecosystem survey | ✅ `SOURCES.md` ("Not used" section) |
| Dictionary snapshot | ✅ `data/dictionary/basic.json` (19,100 rows, local, gitignored) + `manifest.json` (SHA-256, URL, retrieval time, schema, license status) |
| Full-form lexicon | ✅ `data/dictionary/lexicon.tsv` (320,824 entries) generated from `@interslavic/morphology@0.1.2` |
| Evaluation harness | ✅ `isv-eval` CLI: tokenizer, lexical lookup, morphological validation, A/B/C classification, metrics, serialization |
| Smoke tests | ✅ 31 tests (tokenizer, normalization, classifier, B-fallback, end-to-end corpus) |
| **Experiment 001 (baseline)** | ✅ **RUN COMPLETED** — 7 model conditions evaluated on the complete Polish story; comparison in `experiments/exp001-baseline/outputs/comparison.md` |
| **Manual audit sample (Task 004)** | ✅ **PREPARED** — stratified ~100-form sample of unresolved forms + statistics under `experiments/exp001-baseline/manual-audit/` (local, gitignored) for human review; no linguistic classification performed |
| **Cross-resource audit (Task 005)** | ✅ **COMPLETE** — all 1,050 unresolved forms re-checked against hunspell `isv.dic`, `interslavicfreq` wordlists, and the `slovnik` snapshot (evidence only; no resource modified); report under `experiments/exp001-baseline/manual-audit/` (local, gitignored) |
| **EXP-002 pilot (Task 006/006.1)** | ✅ **EXECUTED** — all seven conditions run externally (via `operator-prompts/` copy/paste), collected byte-for-byte, compared with the same evaluator |
| **EXP-002 finalization (Task 006.2)** | ✅ **COMPLETE** — 7/7 runs verified (SHA-256); token-aligned transition matrix (C→A=90, A→C=12, B→C=0); per-form candidate usage; `interslavicfreq` discrepancy explained; Bielik no-change case verified; 5 human-review pairs; final report + recommendation in `experiments/exp002-pilot/REPORT.md` |
| **Resource reconciliation + evaluation policy (Task 007)** | ✅ **COMPLETE** — all resources audited into a layered evidence model (canonical dictionary / morphology / alternative resources / historical reference / reference material); `interslavicfreq` discrepancy explained from the data (three kinds of disagreement: evaluator matching limits, morphology coverage, resource-layer differences); evaluator diagnosed as answering "canonical resource coverage", not "is this valid Interslavic"; two-metric policy proposed (canonical coverage + broader resource-supported coverage) with a labeled per-run demonstration (+6–23 pp alternative-attested share); policy report `docs/RESOURCE_POLICY.md`; evidence table `data/dictionary/resource-policy/evidence.json` (local) generated by `scripts/audit_resource_layers.py` |
| **Two-layer policy implemented (Task 008)** | ✅ **COMPLETE** — the Task 007 policy is implemented in `isv-eval`: a separate evidence layer (`src/isv_eval/evidence.py`) loads the audited alternative resources (`isv.dic` exact surfaces, `interslavicfreq` wordlists, `slovnik` snapshot) and records per-token evidence provenance (layer/source/kind); the report now carries `canonical_coverage` and `broader_resource_supported_coverage` side by side (`metrics.py`, `cli.py`); A/B/C semantics untouched; alternative hits are never promoted into A/B; only exact-surface attestation counts toward the broader tier (orthographic variants and historical presence are recorded but never count); 14 focused policy tests added (45 total); historical A/B/C + canonical coverage byte-identical on all 7 EXP-001 runs, and the new broader metrics reproduce the Task 007 §6 demonstration exactly (e.g. ChatGPT 75.95 → 86.27) |
| **EXP-003 designed (Task 009)** | ✅ **DESIGN COMPLETE** — generation-time lexical-scaffold experiment specified (`experiments/exp003-scaffold/DESIGN.md`): conditions A (baseline) / B (scaffold, single canonical candidate) / C (+ alternatives) / D (+ reliable grammatical annotations); alignment via a verified Polish→ISV reverse index built from `basic.json`'s `pl` column (18,916 keys) + dictionary-verified lemma recovery + an explicit curated residual table (`[?]` for the rest) — measured 36% direct + ~5% recovery on the story; residual of 371 forms = ~54 names + ~317 inflected non-names; Polish lemmatization is not available and is stated as a limitation, not hidden; **scaffold generator is deterministic with no hidden LLM calls (D-029)**; token-aligned scaffold representation; blinded human evaluation; research record created (`docs/RESEARCH_NOTES.md`); reuse of the Task 008 two-tier evaluator and the EXP-002 external-execution/comparison machinery; recommendation: **GO** as a controlled pilot on the existing story with 3 models × 4 conditions; **not implemented** |
| **EXP-003 implemented (Task 010)** | ✅ **INFRASTRUCTURE PREPARED — EXPERIMENT NOT EXECUTED** — deterministic scaffold generator (`scripts/build_exp003_scaffold.py`; reverse index + multiword/names/residual alignment; per-story curation tables committed; candidate provenance incl. headword-note cleaning and orthographic-variant splitting D-033; grammar annotations for condition D); 12 self-contained operator prompts (4 conditions × 3 models, `experiments/exp003-scaffold/operator-prompts/`, packaging script deterministic); run orchestrator (`scripts/run_exp003_pilot.py` prepare/collect/evaluate/status, byte-for-byte immutable collection, plan + meta.json with prompt/source/scaffold hashes + resource pins); comparison tool (`scripts/compare_exp003.py`: per-run two-tier metrics, name-excluded diagnostics D-030, candidate-usage proxy, invented-forms analysis, within-model/within-condition pairwise token-aligned transitions + regression lists, blinded human-review pairs); integrity verifier (`scripts/verify_exp003_runs.py`); tests added (30 new; full suite 75 green); scaffold determinism verified (two builds byte-identical). **No LLM called. No experiment results exist.** Next action: Project Owner executes the 12 prompts externally and returns raw replies for `collect` |
| **EXP-003 intake (Task 011)** | ✅ **COMPLETE — PRELIMINARY ANALYSIS, NOT A VERDICT** — all 12 external replies located, hashed, inspected (structure/completeness/commentary/format) and registered byte-for-byte (`experiments/exp003-scaffold/outputs/`, meta.json with real model info: ChatGPT GPT-5.6 Luna thinking OFF, Claude Sonnet 5 Medium, Bielik 3.0; generation parameters + documented status now recorded, D-035). **8/12 runs are complete translations** (ChatGPT A–D, Claude A–D; all sections present, ending marker KONEC/KONĖC, no commentary). **4/12 Bielik runs are not usable**: A and B truncated mid-story (≈3 of 7 acts, ~40% of the text), C replied with a Croatian paraphrase/echo of the prompt (no translation), D returned a service-error page (no translation). 10 processable runs evaluated with the Task 008 evaluator unmodified; comparison run on the 8 complete runs (Bielik preserved but excluded, D-035). Preliminary headline coverage (canonical / broader): ChatGPT A 76.3/87.1 → B 85.7/90.8 → C 84.8/89.2 → D 84.0/88.8; Claude A 75.8/87.5 → B 79.0/86.4 → C 75.4/84.5 → D 85.6/92.0. **No composite score, no ranking by coverage alone; naturalness is a separate (human) question. Bielik cannot participate quantitatively.** Full analysis in `docs/EXPERIMENTS.md` § EXP-003 and `docs/RESEARCH_NOTES.md` § 4.9. Next action: blinded human naturalness assessment of the 8 complete runs (4 per model) |
| **EXP-003 holistic human review prepared (Task 012)** | ✅ **HISTORICAL — SUPERSEDED (Task 014)** — the DESIGN §11 blinded holistic review was packaged for the Project Owner: `experiments/exp003-scaffold/comparison/human_review.md` contains ONLY the 8 complete runs (ChatGPT A–D, Claude A–D) in two neutral sets ("Set 1"/"Set 2") with per-set deterministic randomized "Version 1..4" labels (seed `20260901` in `compare_exp003.py`, reproducible); four holistic questions + preference ordering + a clearly separated post-unblinding section + a recording checklist; no automatic metric or model identity appears; the mapping lives in `human_review_key.json`. **The Project Owner attempted the holistic review and found comparing four complete long translations too cognitively demanding (D-038), so this format is superseded as the primary method; the artifact is preserved (superseded banner) and NO holistic result was obtained or recorded.** Bielik (incomplete/failed) excluded, preserved as qualitative artifacts |
| **EXP-003 sentence-level forced-choice test prepared (Task 014)** | ✅ **COMPLETE — ANSWERED AND DECODED (Task 016)** — the ONE planned human-evaluation exercise for EXP-003: `experiments/exp003-scaffold/comparison/sentence_review.md` (prepared by `scripts/prepare_exp003_sentence_review.py`) contains 100 questions; each shows one Polish source sentence plus the corresponding sentence from each of the four EXP-003 conditions (A/B/C/D) of the same model (50 per model, ChatGPT and Claude), with per-question deterministic randomized neutral "Version 1..4" labels (seed `20260905`, reproducible; alphabetical order rejected). Sentences are aligned by a monotonic length-based DP plus an all-pairs cross-run token-overlap floor (misaligned or truncated fragments excluded); sampling is stratified by story section × dialogue; 98/100 questions have four pairwise-different versions. The document contains no model names, no A/B/C/D condition labels, no automatic metrics, no hints; instructions ask for a holistic sentence impression (do NOT verify individual words). The private answer key `sentence_review_key.json` records source sentence identity, section, dialogue flag, run ids, version texts, display order, seed, and hashes. **The participant answered all 100 questions (2026-09-05); the decoder (`scripts/analyze_exp003_sentence_review.py`) validated the completed document (original order, one tick each, 399/400 Version texts byte-identical to the key) and decoded the answers with two recorded provenance artifacts (Q58 `[x ]` encoding; Q67 non-chosen Version-2 corruption — neither affects decoding; D-043).** Results: `comparison/sentence_review_results.{json,md}` and `experiments/exp003-scaffold/REPORT.md` |
| **EXP-003 character-level orthographic sanity audit (Task 015)** | ✅ **COMPLETE — AUDIT-ONLY QC LAYER** — deterministic character-level check over ALL generated outputs (EXP-001: 7, EXP-002: 7, EXP-003: 12 run files). The accepted letter inventory is the OFFICIAL Interslavic alphabet definition (https://steen.free.fr/interslavic/orthography.html, fetched 2026-09-05): standard 27-letter Latin alphabet (no q/w/x) + etymological letters + sanctioned alternative graphemes (D-040). Per file the report gives total chars, allowed letters, accepted non-letters, and outside-inventory breakdown (Cyrillic / Polish-specific `ą ł ó ż` / other Latin / other script / unexpected non-letter) with distinct chars, frequencies, and line numbers. Text is never modified, and NO lexical/resource coverage score, A/B/C classification, or comparison artifact was recomputed — character sanity is an independent quality dimension reported side by side with resource coverage (D-041). 21 new tests. Outside-inventory totals: EXP-001 267, EXP-002 309, EXP-003 1 297 chars; findings incl. Cyrillic in Latin output (Claude EXP-001/002/003, intra-word `Може`/`ь` in EXP-003 Claude-C), Polish name orthography kept verbatim (`Bronisława` → `ł`/`w`), Czech/Slovak accented drift (EXP-003 ChatGPT; Bielik-B largely Czech), Markdown formatting in EXP-001/002 outputs (per-run reports under each experiment's gitignored `outputs/orthography_report.{json,md}`; details in `docs/RESEARCH_NOTES.md` §4.13). **Task 016 added a deterministic non-name refinement (letters inside the story's proper-name tokens excluded) to the EXP-003 decoder, because raw condition-level Polish/other-Latin counts are dominated by the names kept verbatim; the refined signal tracks the human preference only at the Claude extremes (C dirtiest → least preferred; D cleanest → most preferred) and does not explain ChatGPT's preference for D over the cleaner B (REPORT.md §4–5)** |
| **EXP-003 human judgment (COMPLETE — Task 016)** | ✅ **DONE — EXP-003 IS CLOSED** — the sentence-level forced-choice questionnaire was answered by the participant and decoded against the private key (validation: 100 questions, original order, one tick each, texts match key; provenance artifacts Q58/Q67 recorded, D-043). Results (n = 100; 50/model): per condition A 26 % / B 16 % / C 19 % / D 39 % (χ²(3) = 12.56, p ≈ 0.006); ChatGPT A 26 / B 12 / C 26 / D 36 %; Claude A 26 / B 20 / C 12 / D 42 %; **guidance (B+C+D) vs. baseline A = 74 % vs. 26 % for both models**; no display-position bias (25/29/22/24). Human vs. automated: agree for Claude at the extremes (D best coverage + favorite; C worst + least favorite), diverge for ChatGPT (coverage-best B is human-least preferred at 12 %; D the favorite at 36 %). Task 015 orthographic signal (non-name refinement) tracks the Claude extremes only. One verbatim participant comment preserved (Q7). Final report `experiments/exp003-scaffold/REPORT.md` is the source of truth; the report was deferred until answers existed and now exists. No composite score; no further human-evaluation exercise will be designed (D-042) |
| **EXP-004 model screening prepared (Task 013)** | ✅ **DONE — EXECUTED AND RECONCILED IN TASK 018 (2026-09-06); this row records the historical plan** — `experiments/exp004-modelscreen/DESIGN.md` specifies the practical model-screening phase (D-036 access filter; D-037 two-phase split): identical story-only source, equivalent no-guidance instruction per roster row, full recording incl. context/window + access observations, byte-for-byte collection with documented statuses (D-035) and completeness gate (L-027), Task 008 two-tier evaluator unmodified, no manual word-by-word classification; Phase 2 guidance-method experiments designed for but not started; anti-leak rule (no encoded winner). **Task 016 finalized the Phase 1 roster and protocol: clean direct-translation baseline only (no scaffolding yet); models with web/chat access, free access, enough practical free quota for at least one full story per day/every other day, practically usable by the author — GPT-5.6 Luna OFF/ON, custom GPT ISV Teacher, Claude Sonnet 5, Gemini (conditional on free quota), DeepSeek V4 Pro OFF/ON, Grok, Kimi, Qwen, GLM (conditional); Venice AI excluded (not an independent model), local/self-hosted excluded (out of scope), Bielik documented as an already-observed negative qualitative case (no new full baseline without a methodological reason).** **Task 017 (approved execution):** `scripts/run_exp004_phase1.py prepare --date 2026-09-06` packaged 11 operator prompts from the single `base_instruction.txt` (identical instruction bodies across rows — no guidance of any kind) + prompt manifest + fixed `outputs/plan.json` (run ids `<date>__<provider>__<model>__<version>__direct`); `collect/verify/evaluate/status/roster` implemented (byte-for-byte intake; structural completeness gate calibrated on EXP-003 data — size ≥ 0.6×source, final line KONIEC/KONĖC, ≥3/5 story names, head sanity — verdicts complete/partial/failed preserved as data, L-027/D-035; Task 008 evaluator + Task 015 orthography per run; D-044); 10 new tests (128 total). No LLM was called in Tasks 013–017; execution by the author happened afterwards and is recorded in the Task 018 row below. No human evaluation in EXP-004 |
| **EXP-004 model screening executed + reconciled (Task 018)** | ✅ **EXECUTED — COLLECTED SET AUDITED, RECONCILED, EVALUATED** — the author executed the screening sessions externally; the planned 11-row roster expanded into **19 concrete runs** (Claude Sonnet 5 Medium + max; DeepSeek V3 Instant + V3 Expert × DeepThink OFF/ON — no V4-Pro output; Qwen 3.8 Max Thinking/Fast + 3.7 Plus Thinking/Fast; Gemini 3.1 Pro ext-thinking ON + 3.6 Flash OFF/ON; GPT-5.6 Luna OFF/ON; ISV Teacher; Grok; Kimi K2.6 Instant; GLM 4.5). All 19 raw sessions preserved byte-for-byte (`collected-sessions/`, gitignored) and audited by `scripts/audit_exp004_collected.py` against the canonical prompt package (instruction-body byte identity OK for all 19; no duplicates; GLM artifact = service-error page). Reconciliation fixed author-naming drift (15/16 = V3 Expert; 19 = 3.8 Max Fast; `EXP-004q` header typo) and calibrated the gate's name check to ISV-tolerant stems (D-045, L-035). **18 runs intake `complete` and evaluated (usable); GLM 4.5 intake `failed` and excluded per protocol.** Evidence table `experiments/exp004-modelscreen/outputs/roster.md` (per-dimension only — no composite score, no coverage-only ranking). Claude Sonnet 5 max >45 min + free-tier exhaustion recorded as an availability constraint, not a quality score. Phase 2 remains closed |
| **EXP-004 Phase 2A corpus priming prepared (Task 019); corpus revised to three authentic registers (Task 020)** | ✅ **PREPARED — EXECUTION-READY, NOT EXECUTED** — full-roster (18 Phase-1-usable configurations; GLM excluded) corpus-priming kit under `experiments/exp004-modelscreen/phase2a/`; reference corpus revised by Task 020 to a combined three-register authentic corpus (corpus id `phase2a-authentic-isv` v1; corpus files local/gitignored, README + hashes committed): literary/narrative `tuta-historija-excerpt.txt` (unchanged Task-019 excerpt, 4 820 B, SHA-256 `413830fa…`); artistic/poetic `album-ahoj-slovjani-artistic-isv.txt` (complete Latin-script album "Ahoj, Slovjani!" — 11 songs in order, 76 unique stanzas, 322 lines, 9 407 B, SHA-256 `7e25a56f…`; Cyrillic duplicates + HTML removed, 24 verbatim repeats deduplicated, forms NOT normalized); informative/encyclopedic `wiki-sadovnistvo-encyclopedic-isv.txt` (authentic retrieved ISV Wikipedia article "Sadovničstvo", 2026-09-07 wikitext API, cleaned running prose, 84 paragraphs, 44 101 B, SHA-256 `b03402fe…`, CC BY-SA 4.0); authoritative combined file `phase2a-authentic-isv-corpus.txt` = 58 459 B, ≈8 200 tokens, SHA-256 `aaad28e4…`; two conditions per configuration — control `p2a-ctl` (the Phase-1 clean direct task; Phase-1 outputs satisfy it, fresh control optional) and corpus-primed `p2a-primed` (msg1 = study reference text as language reference — no translation/summary/imitation/questions; msg2 = same Polish story, standard instruction + reference cue, SAME session); contamination control mechanical (corpus-before-translation required in primed session files; corpus in a control session rejected); run ids `<date>__…__p2a-ctl|p2a-primed` each linked to its Phase-1 `baseline_run_id`; 36-run plan + 54 operator prompt files + manifest (hashes only); `scripts/run_exp004_phase2a.py` (prepare/collect/collect-session/verify/evaluate/status/roster/**compare** — per-dimension deltas, no composite); 19 new tests in Task 019 (155 total green); Task 020 updated `tests/test_exp004_phase2a.py` and added the real-corpus suite `tests/test_exp004_phase2a_corpus.py` (all green). **No LLM called.** Next step: author executes the primed sessions externally (fresh session per run; Claude Sonnet 5 max row carries its known >45-min/free-tier constraint), then collect/verify/evaluate/compare. Phase 2B (Wikipedia-length authentic reference + independent story) documented as future work |
| **EXP-004 Phase 2A executed + audited + evaluated (Task 021)** | ✅ **EXECUTED, COLLECTED, AUDITED, EVALUATED** — the author completed all 18 primed sessions and added two exploratory primed runs of a newly discovered model recorded as **Dola 3.8** ("ByteDance — official web interface", proprietary; runs 20/21 = "Dola 3.8 — Fast"/"Dola 3.8 — Pro", author-recorded in prompt-file headers only, not independently verifiable — **NOT part of the original 18-model roster, NO Phase-1 baseline, treated as two distinct exploratory observations, never collapsed**). Task 021: (1) audited all 20 runs — Prompt-1 corpus region byte-identical to authoritative `aaad28e4…` in all 20 msg1 files; Prompt-2 Polish story byte-identical; (2) registered each run via new `collect-msg2` (record = operator msg2 prompt file + raw reply after `## Output`; reply sliced at the marker, stored byte-for-byte; meta records no machine same-session proof — central protocol deviation; raw bytes never edited; **`prepare --force` must not be re-run**, replies now live in operator-prompts); (3) `extend-exploratory` appended Dola rows to plan (38 rows) + manifest (58 entries) idempotently; (4) corpus-integrity re-run (20/20 primed msg1 corpus tails identical; combined file SHA-256 unchanged; controls corpus-free); (5) evaluated all 20 via the unmodified deterministic pipeline — intake 19 complete + 1 partial (run 12 Claude Sonnet 5 max, final line `**KONEC**` bold-wrapped; end-marker rule) — and `compare` produced the 18-row primed-vs-Phase-1 delta table (Dola rows: no-baseline, no priming effect claimed); (6) manual-execution constraints documented (Gemini two-message corpus ~83%+~17%; Gemini 3.1 Pro corpus ingested in 3.6 Flash then model switched to 3.1 Pro for translation — ingestion model ≠ translation model; Gemini extended-thinking reset per prompt; Claude token-limit 3-attempt continuations — raw history not stored) as protocol conditions, not quality judgments. Full evidence `phase2a/outputs/roster.md` + `compare.md`; 3 new tests (`tests/test_exp004_phase2a_exploratory.py`); full suite green. **No Phase 2B work; no model selection** — research lead decides next |
| **EXP-004 Dola Phase-1 baselines prepared (Task 022), collected + evaluated (Task 023)** | ✅ **PREPARED (022) → COLLECTED + EVALUATED (023)** — retrospective Phase-1 DIRECT baselines for the two exploratory Dola 3.8 configurations (Fast/Pro, runs 20/21) that were added without a baseline at Task 021. `scripts/run_exp004_phase1.py extend-direct --date 2026-09-07` rendered the two canonical Phase-1 direct operator prompts (`operator-prompts/20-dola-3.8-fast.md`, `21-dola-3.8-pro.md` — same Polish source story + same direct-translation instruction as the original 18; corpus-free, no scaffold/dictionary/grammar material, fresh-session requirement explicit) and appended their plan/manifest rows as `pending_manual_collection`; `scripts/run_exp004_phase2a.py link-baselines` then wired each Dola p2a-primed row's `baseline_run_id` to its prepared direct id (`baseline_status: pending_collection`). **Task 023 (2026-09-07): the author executed both baselines in fresh ByteDance sessions (direct translation only) and saved each raw reply msg2-style inside its operator prompt file; both records passed the Phase-1 `collect-session` intake + `verify` completeness gate (verdict complete, usable) and were evaluated with the same deterministic pipeline. `compare` now reports the real within-Dola Phase 1 → Phase 2A deltas** (canonical coverage: Dola Fast 38.87 % → 67.07 % [+28.20 pp]; Dola Pro 65.08 % → 71.75 % [+6.67 pp]; broader/unresolved/token deltas in `phase2a/outputs/compare.md`). Dola stays `exploratory: true` (not part of the original 18-configuration roster); Task-020/021 historical results unchanged; no priming effect claimed beyond the recorded deltas. New tests in `tests/test_exp004_phase1_dola_baselines.py` (msg2-style collect + verify, no false prompt-drift FAIL, real compare deltas); full suite green |
| **EXP-004 FULL ANALYSIS (Task 024, 2026-09-07)** | ✅ **COMPLETE — PHASE 1 → PHASE 2A CORPUS-PRIMING EVIDENCE BASE** — deterministic, read-only research analysis of the whole 20-configuration dataset (18 original + 2 exploratory Dola 3.8) via `scripts/analyze_exp004_phase2a.py` (std-lib only; byte-identical chart regeneration, deterministic tables): 20-config dataset (`analysis/dataset.json`; Dola rows `exploratory: true`, never merged), Phase-1 + Phase-2A rankings on four separate dimensions (canonical / broader / unresolved / orthography — no composite, no winner), priming Δ table sorted by Δ canonical (original 18: mean +6.00 pp, median +4.92 pp, sd 3.39 pp, 18/18 positive; broader mean +2.36 pp, 14/18 positive; 20-config set labelled exploratory), exploratory exact paired tests (sign test canonical p ≈ 7.6e-6, broader p ≈ 0.031; sign-flip permutation p ≈ 7.6e-6 / 9.6e-4 — n = 1 per condition caveat explicit), descriptive Spearman baseline-dependence (P1 canonical vs Δ canonical ρ = −0.86; broader ρ = −0.84; n = 18), P1-vs-P2A ρ = +0.45 / +0.37, family tables (GPT/Claude/Gemini/DeepSeek/Qwen/Dola), orthography-bucket analysis, separate practical-usability dimension, research-facing master table, charts A–G (`analysis/figures/`), poster draft (`analysis/poster.{md,html}`) + committed `analysis/README.md` (supported/suggestive/not-established conclusions; research candidates: Claude Sonnet 5 Medium, DeepSeek V3 Expert ON/OFF, Qwen 3.8 Max Fast, Gemini 3.6 Flash ON, Dola Fast/Pro — exploratory; ≤ 3 recommended next experiments, none executed). Dola Fast's +28.20 pp is reported as a large observed change consistent with baseline dependence, NOT as evidence of stronger corpus learning. Phase 2B not executed. `tests/test_analyze_exp004_phase2a.py` (19 tests); full suite green (212) |
| **EXP-004 PHASE REPEAT (Task 025, 2026-09-07)** | ✅ **PREPARED — EXECUTION-READY, NO LLM RESULTS YET** — controlled repeated-generation kit (`experiments/exp004-modelscreen/repeats/`) to estimate run-to-run stochastic variation in EXP-004: **108 primary planned generations** (the original 18 usable configurations × `direct`/`primed` × 3 independent fresh-session replicates r01–r03) + **12 exploratory Dola 3.8 Fast/Pro rows** (`exploratory: true`, never merged into primary n=18; research lead decides whether to execute). Deterministic hash-gated prompt prep (`scripts/run_exp004_repeats.py prepare --date 2026-09-08` → 120-run `outputs/plan.json` + hash-only `operator-prompts/manifest.json` + human `outputs/collection-checklist.md`; 180 prompt files, source `5de968a6…`/corpus `aaad28e4…` byte-gates, replicate contents byte-identical within (config, condition), fresh-session rule encoded, no scaffolding/hints). Collection/verify/evaluate/roster reuse the Phase-1/2A completeness gate + integrity checks + Task-008 evaluator + orthography audit unmodified (msg2-style records; corpus-in-direct contamination rejected; raw outputs never repaired; unusable runs preserved + marked; re-run gets a new id). Analysis (`scripts/analyze_exp004_repeats.py`, std-lib): n=3 small-sample descriptive stats; primary quantity `mean(primed) − mean(direct)` vs old single delta; block differences secondary only; figures A–E; three selection views + ortho; candidate focus; supported/suggestive/not-established rules; explicit no-results scaffold written. 25 new tests (`tests/test_exp004_repeats.py`); full suite **237 green**. `REPORT.md` (no results yet) + READMEs committed; analysis scaffold `repeats/analysis/` status `no_results`. Next: research lead executes the prepared prompts (replicate blocks r01→r03), then collect/verify/evaluate/analyze. No Phase 2B; no human evaluation |
| **EXP-004 PHASE REPEAT EXECUTED + AUDITED (Task 026, 2026-09-09)** | ✅ **EXECUTED, AUDITED, EVALUATED, ANALYSED** — 114/120 planned runs collected (msg2-style); Task-026 audit script `scripts/audit_exp004_repeats.py` + `tests/test_audit_exp004_repeats.py` (10) reconciled every run against the Task-025 manifest + authoritative renders with raw outputs untouched (`repeats/outputs/audit.{json,md}` local). **Counts: planned 120 (108 primary + 12 exploratory) / collected 114 (102 + 12) / usable 106 (99 + 7) / partial 8 (3 + 5; markdown-wrapped end markers only) / invalid 0 / missing 6** (Gemini 3.1 Pro ON + Qwen 3.8 Max Thinking primed r01–r03 — never collected, not fabricated; repeated Δ n/a for those two). Hash gates OK; no duplicates/source-echo/cross-run contamination/stale files. Deviations recorded, not repaired: Grok identity operator-header edit (6 runs; operator-reported "Grok 4.5, built by xAI (fast)"; model-facing bytes identical); **Claude Sonnet 5 — max thinking/reasoning OFF for all repeats** (execution deviation; not renamed; comparability with Task 024 affected); Gemini primed corpus two-message delivery (6 runs; corpus tail byte-verified — same class as Task-021/024); Dola Pro r03 msg1 blank header line (trivial). `fresh_session_proof: unavailable`. **Results (descriptive): repeated Δ canonical positive 16/16 (mean +6.93 pp); Task-024 direction replicated 15/15 (mean old +6.33 pp vs repeated +6.73 pp); shift > within-condition spread for most configs (median SD ≈ 1.49 pp direct / ≈ 0.87 pp primed); Gemini Flash ON +15.91, Claude Medium +9.12 (stable), DeepSeek Expert ON +3.77 (ON > OFF), Qwen 3.8 Max Fast +1.72 with primed SD 5.83; Dola Pro +12.41, Dola Fast not re-estimable.** `REPORT.md` results + `analysis/` complete; full suite green; recommended next: Phase-2B unseen-topic transfer. Phase 2B not executed; no human evaluation |

| **EXP-004 ASSISTANT RESEARCH BUNDLE (Task 027, 2026-09-09)** | ✅ **COMPLETE — COMPACT MACHINE-READABLE EXPORT FOR INDEPENDENT ANALYSIS** — `experiments/exp004-modelscreen/assistant-research-bundle/` (1.5 MB): `results.json`/`results.csv` (120 planned runs, one record per run, replicate metrics, hashes, deviations), `summary.json` (per-config descriptive stats + repeated Δ + Task-024 old singles as `historical_task024`), `audit.json`, `deviations.json`, `provenance.json`, `manifest.json` (per-file SHA-256), `methodology.md`, figures A–E PNG+SVG; standalone verifier reconstructs every Task-026 headline from the bundle alone (15/15 checks); deterministic (two builds byte-identical); no raw outputs, no secrets |
| **Research-state reconstruction (Task 028, 2026-09-09)** | ✅ **COMPLETE — DOCUMENTATION ONLY** — `docs/research-roadmap.md` (high-level source of truth: framing, COMPLETED experiment record EXP-001→EXP-004 + EXP-005 audit, interpretation, PROPOSED Phase-2B shortlist 7 configs × 3 reps × 2 conditions = 42 translations, 2B-A/2B-B variants, publication direction, stopping rule) + `docs/translation-method.md` (evaluation layers, intervention ladder A–E, pipeline hypotheses, proposed pipeline-optimization experiment, conceptual software). Indexed from README; numbers cross-checked against repo records; no historical correction needed; no tests changed; no experiments run |
| Translator / LLM integration | ❌ Not implemented (out of scope) |


### Experiment 001 headline numbers

Seven whole-story translations were evaluated against the snapshot dictionary
+ generated full-form lexicon (denominators = lexical tokens):

| Condition | Lexical Tokens | Exact (A) | Morph. Valid (B) | Unresolved (C) | Valid Coverage |
|---|---:|---:|---:|---:|---:|
| ChatGPT | 1522 | 1153 | 3 | 366 | 75.95% |
| GPTs — ISV Teacher | 1522 | 1213 | 2 | 307 | 79.83% |
| Gemini | 1471 | 1054 | 1 | 416 | 71.72% |
| Claude | 1486 | 1092 | 1 | 393 | 73.55% |
| DeepSeek | 1431 | 1064 | 1 | 366 | 74.42% |
| Bielik | 1561 | 862 | 4 | 695 | 55.48% |
| Grok | 1472 | 1127 | 0 | 345 | 76.56% |

Order is not a ranking. Full table, per-model unresolved vocabularies,
pairwise overlaps and shared-form statistics are in
`experiments/exp001-baseline/outputs/comparison.{md,json}` (gitignored) and
summarized in `docs/EXPERIMENTS.md` § EXP-001.

## Repository layout

```
README.md                    — project intro + index
SOURCES.md                   — source/dependency inventory
pyproject.toml               — Python package (`isv-eval`), console script
src/
  isv_eval/                  — tokenizer, lexicon, morphology client,
  |                            classifier, metrics, evidence (Task 008), CLI
  morphology_backend/        — Node stdio backend (inflect + translit),
                               pinned deps + committed package-lock.json
scripts/
  fetch_dictionary.py        — snapshot basic.json + write manifest
  generate_lexicon.py        — build full-form lexicon TSV + manifest
  sample_exp001_audit.py     — build the manual-audit sample of unresolved forms
  audit_exp001_resources.py  — cross-resource audit of all unresolved forms (Task 005)
  audit_resource_layers.py   — resource-layer audit + policy evidence (Task 007)
  prepare_exp002_pilot.py    — EXP-002 candidate generation + prompt packages
  compare_exp002.py          — EXP-002 before/after evaluation + transition matrix + human-review pairs
  run_exp002_pilot.py        — EXP-002 orchestrator (prepare / collect / compare / status)
  package_operator_prompts.py — EXP-002 operator-facing single-file Markdown prompts
  verify_exp002_runs.py      — EXP-002 completeness + SHA-256 integrity check (Task 006.2)
  build_exp003_scaffold.py   — EXP-003 deterministic scaffold generator (Task 010)
  package_exp003_prompts.py  — EXP-003 12 operator prompts (4 conditions × 3 models)
  run_exp003_pilot.py        — EXP-003 orchestrator (prepare / collect / evaluate / status)
  compare_exp003.py          — EXP-003 per-run + pairwise + blinded holistic human-review analysis (holistic review superseded Task 014; output carries a superseded banner)
  prepare_exp003_sentence_review.py — EXP-003 sentence-level forced-choice test preparation (Task 014): alignment, stratified sampling, deterministic randomization; writes comparison/sentence_review.md + key
  verify_exp003_runs.py      — EXP-003 completeness + SHA-256 integrity check
  run_exp004_phase1.py       — EXP-004 Phase 1 orchestrator (prepare/extend-direct/collect/collect-session/verify/evaluate/status/roster; Tasks 017/018/022/023)
  run_exp004_phase2a.py      — EXP-004 Phase 2A orchestrator (prepare/collect/collect-session/collect-msg2/extend-exploratory/link-baselines/verify/evaluate/status/roster/compare; Tasks 019/020/021/022/023)
  build_phase2a_corpus.py    — EXP-004 Phase 2A deterministic corpus builder (Task 020)
  audit_exp004_collected.py  — EXP-004 collection audit + reconciliation evidence (Task 018)
  analyze_exp004_phase2a.py  — EXP-004 Task-024 deterministic full analysis (dataset/rankings/Δ table/stats + exploratory tests/correlations/families/orthography/master table/charts A–G/poster; std-lib only)
  run_exp004_repeats.py      — EXP-004 phase-repeat orchestrator (prepare/collect-session/collect-msg2/verify/evaluate/status/roster; Task 025; hash-gated 108+12-run plan)
  audit_exp004_repeats.py   — EXP-004 phase-repeat collection audit + reconciliation evidence (Task 026; machine-readable audit.json + audit.md; roster-verdict merge)
  analyze_exp004_repeats.py  — EXP-004 Task-025/026 deterministic repeated-generation analysis (stochastic stats, mean-primed−mean-direct vs old delta, figures A–E, selection views; std-lib only)
  build_assistant_research_bundle.py — EXP-004 assistant-research-bundle generator + standalone verifier (Task 027; deterministic, std-lib)
data/
  dictionary/README.md       — how to regenerate the (gitignored) data
  dictionary/audit/          — downloaded audit inputs (hunspell, frequency, slovnik), gitignored
tests/
  fixtures/smoke_corpus.txt  — synthetic smoke corpus
  test_*.py                  — normalize/tokenizer/classifier/smoke/resource-evidence tests
docs/
  STATE.md                   — this file
  ROADMAP.md                 — SODA task roadmap + future ideas (scientific direction: research-roadmap.md)
  DECISIONS.md               — decision log
  EXPERIMENTS.md             — experiment log
  GRAMMAR_AUDIT.md           — grammar consistency audit (Task 001 deliverable)
  RESOURCE_POLICY.md         — resource reconciliation + evaluation policy (Task 007 deliverable, spec for Task 008)
  LESSONS.md                 — lessons learned (SODA mechanism)
  RESEARCH_NOTES.md          — lightweight research record for a future publication (methodological taxonomy, measured numbers, standing rules; created Task 009)
  research-roadmap.md       — high-level research state + direction (hypothesis, experiment record, key findings, Phase-2B plan, publication direction, stopping rule; Task 028)
  translation-method.md     — translation method thread (intervention ladder A–E, pipeline hypotheses, evaluation layers; Task 028)
experiments/
  exp001-baseline/
    DESIGN.md                — Experiment 001 design (input/storage/metrics/reproducibility)
    manual-audit/README.md   — manual audit sample of unresolved forms + cross-resource audit index (data is gitignored)
  exp002-pilot/
    DESIGN.md                — EXP-002 pilot design (candidate generation, prompt, evaluation)
    README.md                — operator instructions (prepare / execute externally / evaluate)
    REPORT.md                — final report: results, regressions, `interslavicfreq` discrepancy, recommendation
    prompt_template.txt      — revision prompt template (shared)
    operator-prompts/        — ONE self-contained Markdown prompt per condition (generated, .md gitignored)
    input/  outputs/  comparison/  — run artifacts (all gitignored; all 7 runs executed and compared)
  exp003-scaffold/
    DESIGN.md                — EXP-003 lexical-scaffold experiment design (Task 009; implemented in Task 010)
    README.md                — operator instructions for the controlled pilot (Task 010)
    prompt_template.txt      — shared prompt template (Task 010)
    curation/op-pl/          — per-story curation tables (names/multiword/residual; committed, D-032)
    operator-prompts/        — 12 self-contained operator prompts (generated, .md gitignored)
    input/  scaffolds/  outputs/  comparison/  — run artifacts (gitignored; 12 replies collected Task 011, 8 complete)
    comparison/README.md — documents the review artifacts: historical holistic review (superseded, Task 014) + primary sentence-level forced-choice test (sentence_review.md + private key)
    temp/                    — Project Owner's raw operator replies (gitignored, Task 011)
  exp004-modelscreen/
    DESIGN.md                — EXP-004 practical model-screening design (Task 013) + Phase 2A corpus-priming design §13 (Task 019)
    README.md                — status + pointer to DESIGN
    base_instruction.txt     — the single direct-translation instruction (shared by Phase 1 and Phase 2A control/Prompt-2)
    input/  operator-prompts/  outputs/  collected-sessions/
                             — Phase 1 artifacts (all gitignored except committed READMEs + manifest/audit evidence; 18 evaluated runs, Task 018; Dola direct prompts 20/21 prepared Task 022 + collected/evaluated msg2-style records Task 023)
    phase2a/                 — Phase 2A corpus-priming kit (Tasks 019/020/021/022/023): README (protocol + 18-config roster + Dola exploratory + Task-021 record + Task-022 prepared / Task-023 collected+evaluated Phase-1 baselines) + corpus/ (three-register authentic corpus — narrative/artistic/encyclopedic — local; README provenance committed) + operator-prompts/ (58 prompt files incl. 4 exploratory Dola entries; manifest committed; msg2 files carry the collected replies after `## Output`) + outputs/ (38-run plan incl. 2 exploratory Dola rows; collected+verified+evaluated runs; roster + compare incl. real Dola deltas; gitignored) + collected-sessions/ (author saves raw sessions here; Task-021 records are the msg2 prompt+reply files above)
    analysis/                — Task-024 full analysis: README.md (committed; interpretation levels, candidates, next experiments) + dataset.json / analysis.{json,md} / figures/chart_a..g.svg / poster.{md,html} (gitignored, deterministic outputs of scripts/analyze_exp004_phase2a.py)
    repeats/                 — Phase-repeat experiment (Tasks 025/026): README.md (protocol + manifest + collection record + audit record) + REPORT.md (dedicated report — status: COLLECTED, AUDITED, ANALYSED; results written 2026-09-09) + operator-prompts/ (180 prompt files incl. 12 exploratory Dola; collected raw replies live msg2-style after `## Output`; gitignored — embed source/corpus; manifest.json hash-only committed) + outputs/ (120-run plan dated 2026-09-08, collection-checklist.md, roster.json/md, audit.json/md, run dirs; gitignored except README.md) + analysis/ (README.md committed with results summary; dataset/analysis JSON+MD + figures A–E — deterministic outputs of analyze_exp004_repeats.py, gitignored)
    assistant-research-bundle/  — EXP-004 compact machine-readable research export for independent analysis (Task 027): results.json/csv, summary.json, audit.json, deviations.json, provenance.json, manifest.json, methodology.md, raw/README.md, figures A–E — committed; generator + standalone verifier scripts/build_assistant_research_bundle.py
```

## Working agreements

- Python is the default language for the evaluation pipeline unless an existing
  Interslavic component requires another runtime (the JS morphology engine is
  the expected primary backend; Node is therefore also an accepted runtime).
- Reuse existing resources; do not reimplement morphology or synonym ranking.
- Keep experiments small and reproducible; never overwrite previous results.
- Do not build production infrastructure.

## To run the evaluator

```bash
python3 -m venv .venv && .venv/bin/pip install -e ".[dev]"   # once
npm ci                                                       # once, in src/morphology_backend/
python3 scripts/fetch_dictionary.py                          # once (network)
python3 scripts/generate_lexicon.py                          # once (~90 s)
.venv/bin/isv-eval path/to/text.txt --out results/           # evaluate
```

Generated data (`data/dictionary/basic.json`, `lexicon.tsv`, manifests) is
local and gitignored because the dictionary data license is unresolved
(SOURCES.md).

The broader resource-supported tier uses the audited alternative resources
under `data/dictionary/audit/` (hunspell cache, `interslavicfreq` wordlists,
`slovnik` snapshot — all gitignored). When they are present the CLI loads them
automatically; `--no-alternative-resources` skips them (the broader tier then
equals the canonical tier).
