# Roadmap

Status: updated 2026-09-07 (Task 024 — EXP-004 FULL ANALYSIS COMPLETE:
the deterministic research analysis of the whole 20-configuration dataset
(18 original + 2 exploratory Dola 3.8) — `scripts/analyze_exp004_phase2a.py`
→ `experiments/exp004-modelscreen/analysis/` (README committed;
dataset/analysis JSON+MD, charts A–G, poster draft gitignored); rankings
on four separate dimensions, priming Δ table, descriptive statistics +
exploratory exact paired tests, descriptive Spearman baseline-dependence
(ρ ≈ −0.86 canonical / −0.84 broader) and baseline-vs-primed
correlations, family + orthography analyses, practical-usability
dimension, master table, supported/suggestive/not-established conclusions,
research candidates, ≤ 3 recommended next experiments — no composite
score, no winner; Phase 2B not executed). Phase-1/Phase-2A collection and
evaluation were completed in Tasks 018/021; the Dola Phase-1 baselines in
Task 023.

## Done

- [x] **Task 002 — Baseline experiment harness**
  - [x] Snapshot `basic.json` into `data/dictionary/` with hash manifest
        (`scripts/fetch_dictionary.py` → `manifest.json`).
  - [x] Full-form lexicon from the dictionary via `@interslavic/morphology`
        (`scripts/generate_lexicon.py` → 320,824-entry TSV).
  - [x] Evaluation pipeline: tokenizer + exact-match lookup + morphological
        validation (Node stdio backend), A/B/C classification + review (D).
  - [x] Metrics: `exact_dictionary_coverage`, `morphologically_valid_coverage`,
        `unresolved_forms`, `total_tokens` (denominator policy documented).
  - [x] Smoke tests (31) incl. edge cases (`more → morem` corrected, folded
        etymological matching, hyphenation, Cyrillic).
- [x] **Experiment 001 (baseline) — RUN COMPLETED** (Task 003):
  - [x] Source registered (`opowiadania-set-isv/op-pl.txt`, SHA-256
        `e3164ffc…e643`; preprocessing artifact documented in `source.meta.json`).
  - [x] Seven independent whole-story conditions evaluated with `isv-eval`:
        ChatGPT, Gemini, Claude, DeepSeek, Bielik, Grok,
        GPTs "Interslavic — Medžuslovjansky Language Teacher"
        (`condition_type = specialized_custom_gpt`, kept separate from ChatGPT).
  - [x] Per-run reproducibility (source/output SHA-256, dict manifest,
        morphology version, evaluator commit `48f2523`).
  - [x] Cross-model comparison (`scripts/compare_exp001.py`): metrics table,
        per-model unresolved vocabularies + frequencies, pairwise overlaps,
        shared-form summary (1050 unique / 219 in 2+ / 83 in 3+ / 8 in all 7).
  - [x] B-bucket fallback batched (one morphology call per chunk of distinct
        candidate lemmas) — cut full-story runtime from minutes to seconds.
  - [x] Results: `experiments/exp001-baseline/outputs/comparison.md` + docs/EXPERIMENTS.md.
- [x] **Task 004 — Manual audit sample prepared** (follow-up analysis of
  EXP-001, not a new experiment):
  - [x] Dataset statistics (1,050 unique unresolved forms / 2,888 occurrences;
        831 in exactly one model, 8 in all seven).
  - [x] Stratified ~100-form sample (`scripts/sample_exp001_audit.py`):
        A 25 high-frequency, B 25 shared (2–6 models), C 25 model-specific,
        D 15 diverse/edge-case, E 10 story-name representatives, plus the
        8 shared-by-all forms as a diagnostic appendix.
  - [x] Worksheet with blank human-review columns
        (`experiments/exp001-baseline/manual-audit/`), no automatic
        linguistic classification.
- [x] **Task 005 — Cross-resource audit of unresolved forms** (post-hoc
  evidence audit of EXP-001, not a new experiment):
  - [x] All **1,050** unresolved forms re-checked against every documented
        Interslavic resource (`scripts/audit_exp001_resources.py`): `basic.json`,
        generated lexicon, `slovnik` snapshot, hunspell `isv.dic`, and
        `interslavicfreq` wordlists; JS morphology (deterministic via lexicon),
        Rust morphology recorded NOT_TESTABLE (no toolchain).
  - [x] Per-form evidence matrix + report
        (`experiments/exp001-baseline/manual-audit/cross-resource-audit.{json,csv}`,
        `cross-resource-summary.md`); evidence categories, no linguistic
        judgments, no resource modification.
  - [x] Audit inputs downloaded at documented pins and stored locally
        (`data/dictionary/audit/`, gitignored).
  - [x] Key finding: 403 forms (38.4%) are attested verbatim in an alternative
        resource; 450 have candidate lemmas but no resource evidence; 116 have
        neither; 45 orthographic-variant candidates; 36 names/special only.
- [x] **Task 006 — EXP-002 pilot prepared** (dictionary-guided revision;
  *pilot only*, no production pipeline, EXP-002 not yet run):
  - [x] DESIGN (`experiments/exp002-pilot/DESIGN.md`): loop under test, two
        separate questions (resource question A vs revision question B),
        candidate sources, prompt rules, pilot scope, evaluation.
  - [x] Deterministic candidate generation + stratified selection
        (`scripts/prepare_exp002_pilot.py`): canonical dictionary /
        orthographic variant / alternative resource / morphology-derived /
        none, with full provenance per candidate; name/special forms are
        excluded from revision targets.
  - [x] Revision prompt template + complete-document prompt per run
        (`prompt_template.txt`, input packages under
        `experiments/exp002-pilot/input/`, gitignored).
  - [x] Before/after evaluation with the SAME `isv-eval` evaluator
        (`scripts/compare_exp002.py`) + human-review before/after pairs doc.
  - [x] Reproducible orchestrator (`scripts/run_exp002_pilot.py`):
        prepare / collect / compare / status; collect never overwrites and
        stores external LLM output byte-for-byte.
  - [x] Input packages prepared for **all 7** EXP-001 source runs (30 forms
        per run; ~24 with candidates). LLM execution is external (no API
        client, D-007).
- [x] **Task 006.1 — operator packaging of the EXP-002 pilot** (usability
  only; no experiment change):
  - [x] Audited all seven input packages: `prompt.txt` is a complete
        self-contained revision prompt (instructions + candidate table with
        provenance + the complete original translation, byte-exact tail).
        There is no `source.txt` — the file is `original.txt` (byte-for-byte
        EXP-001 output). `candidates.json` adds machine-readable structure
        (sentence context, stratum, POS/tags/cB/paradigm evidence) not needed
        to run the experiment.
  - [x] Created one clearly named, self-contained Markdown prompt per
        condition (`experiments/exp002-pilot/operator-prompts/01-…07-….md`,
        generated by `scripts/package_operator_prompts.py`, byte-identical on
        rerun, no timestamps): explicit target, revision instructions, full
        original translation, candidate alternatives with provenance,
        no-candidate controls, whole-document output, preservation rules,
        vocabulary constraint, and the explicit "use supplied alternatives,
        not independent discovery" distinction.
  - [x] Prompt template gained the explicit controlled-experiment statement
        (the only LLM-facing gap the audit found); packages regenerated and
        the **30-form selection verified byte-identical** (packaging changed
        nothing about candidate generation or the experiment).
  - [x] `.md` operator files gitignored (they embed complete model output);
        README + manifest.json committed. Pilot README now documents the
        copy/paste workflow.
- [x] **Task 006.2 — EXP-002 pilot executed, finalized, and analyzed**:
  - [x] All seven conditions executed externally via the operator prompts,
        collected byte-for-byte, compared with the SAME evaluator as EXP-001.
  - [x] Completeness + SHA-256 integrity verified for all 7 runs
        (`scripts/verify_exp002_runs.py`; 7/7 pass).
  - [x] Regression bookkeeping improved: **token-aligned evaluator-state
        transition matrix** (C→A / C→B / C→C / A→A / A→B / A→C / B→A / B→B /
        B→C) with A→C and B→C regression lists, plus a per-selected-form
        candidate-usage table (`scripts/compare_exp002.py`). This exposed A→C
        regressions the old unique-form bookkeeping missed.
  - [x] Results: 6/7 models improved coverage (+0.35…+1.28 pp); C→A = 90,
        A→C = 12, B→C = 0. Grok (7) and Claude (3) introduced non-supplied
        spellings; ChatGPT (2) over-applied supplied candidates to valid forms.
  - [x] `interslavicfreq` discrepancy explained: alternative-resource surfaces
        are invisible to the strictly canonical evaluator (adopted `seli`,
        `sedeli`, `reci`, `rekl`, `dejstvitelno` produced no measurable gain);
        an evaluator/resource integration gap by design, not an error in either
        layer. No resource modified.
  - [x] Bielik no-change case byte-verified (formatting-only revision;
        hypotheses recorded, no internal-cause claim).
  - [x] 5 curated complete before/after human-review pairs
        (`comparison/human_review.md`) across outcome categories.
  - [x] Final report + single recommendation
        (`experiments/exp002-pilot/REPORT.md`).
- [x] **Task 007 — Interslavic resource reconciliation and evaluation policy**
  (policy definition, not a new experiment; no resource/evaluator changes):
  - [x] Audited every resource already present into a **layered evidence
        model**: canonical dictionary (`basic.json`/lexicon), morphological
        rules (JS + Rust), alternative resources (`isv.dic`, `interslavicfreq`
        wordlists), historical reference (`slovnik` snapshot), reference
        material (Steen grammar, community material — not ingested).
  - [x] Explained the **`interslavicfreq` discrepancy from the data**: three
        kinds of disagreement — evaluator matching limits (folded-prefix gap
        `sedeli`↔`sěděti`; multi-token lemma exclusion `bojati sę`),
        morphology coverage (`sěsti` past forms; comparatives absent from the
        `inflect()`-generated lexicon), and resource-layer differences
        (`reći`, `dejstvitelno` absent from the canonical dictionary).
  - [x] Diagnosed `isv-eval`: it answers "can this surface be
        generated/recognized from the canonical dictionary + morphology?"
        (a coverage metric), **not** "is this form valid Interslavic?".
        Adopted the term **canonical coverage** for future reports.
  - [x] Proposed the **two-metric policy**: canonical coverage + broader
        resource-supported coverage; a labeled per-run demonstration shows
        +6–23 pp alternative-attested share of EXP-001 unresolved vocabulary
        (e.g. ChatGPT 75.95 % → 86.27 %, Bielik 55.48 % → 78.99 %).
  - [x] Defined candidate-generation weighting by layer (canonical surface >
        generated inflection > orthographic variant > alternative-resource
        attestation > historical snapshot), all with provenance.
  - [x] Deliverables: `docs/RESOURCE_POLICY.md`,
        `scripts/audit_resource_layers.py`,
        `data/dictionary/resource-policy/{README.md,evidence.json}` (local);
        SODA docs updated. No resource modified, no evaluator code changed,
        historical results preserved.
- [x] **Task 008 — Two-layer resource evaluation policy implemented in
  `isv-eval`** (evaluator change only; no resource/experiment change):
  - [x] New evidence layer `src/isv_eval/evidence.py`: loads the audited
        alternative resources (`isv.dic` exact surfaces, `interslavicfreq`
        wordlists, `slovnik` snapshot) and attaches per-token evidence
        provenance (layer/source/kind) to every token.
  - [x] A/B/C semantics untouched; alternative-resource hits never become A/B;
        only exact-surface attestation counts toward the broader tier;
        orthographic variants (folded/diacritic-stripped) and historical
        presence are recorded but never count (no double counting).
  - [x] `metrics.py` reports `canonical_coverage` (== historical
        `morphologically_valid_coverage`) and
        `broader_resource_supported_coverage` side by side, plus
        `canonical_supported_tokens`, `broader_resource_supported_tokens`,
        `unresolved_tokens`; `cli.py` exposes them with full provenance and a
        `--no-alternative-resources` opt-out.
  - [x] 14 focused policy tests (`tests/test_resource_evidence.py`); full
        suite green (45 tests). Historical A/B/C + canonical coverage verified
        byte-identical on all 7 EXP-001 runs; broader metrics reproduce the
        Task 007 §6 demonstration exactly (e.g. ChatGPT 75.95 % → 86.27 %).
- [x] **Task 009 — EXP-003 lexical-scaffold experiment DESIGNED** (design
  only; nothing implemented, no LLM called):
  - [x] Verified the primary alignment resource exists in-repo: `basic.json`
        has a Polish translation column (`pl`, 18,916 keys); a reverse index
        covers lemma vocabulary (`być→byti`, `się→sę`, `dziś→[dnėś, tutdėnj,
        sego dnja]`); measured on the story: 207/578 (36 %) direct hits,
        ~28 (~5 %) dictionary-verified recovery, residual 371 = ~54 names +
        ~317 inflected non-name forms. Polish lemmatization is not a project
        dependency — stated as a limitation, handled by dictionary-verified
        lemma recovery + an explicit curated residual table + `[?]`
        (no silent heuristics).
  - [x] Four conditions specified (A baseline / B scaffold single candidate /
        C + alternatives / D + reliable grammatical annotations), token-aligned
        scaffold representation, prompt design that treats the scaffold as
        vocabulary guidance (never a surface template), reuse of the Task 008
        two-tier evaluator and the EXP-002 external-execution/comparison
        machinery, reproducibility plan, blinded human holistic-reading
        protocol.
  - [x] Scaffold-generation method decided (D-029): deterministic pipeline,
        no hidden LLM calls; lemma-based / LLM-assisted generation rejected
        for v1; curated residual is explicit human judgment.
  - [x] Research record created: `docs/RESEARCH_NOTES.md` (methodological
        taxonomy: direct translation / post-hoc revision / generation-time
        scaffolding / generation-time lexical+grammatical constraints;
        measured alignment numbers; standing rules).
  - [x] Deliverable: `experiments/exp003-scaffold/DESIGN.md`; SODA docs
        updated (STATE, ROADMAP, DECISIONS D-028/D-029, EXPERIMENTS,
        LESSONS L-022/L-023, RESEARCH_NOTES).
        Recommendation: **GO** for a controlled pilot (existing story,
        3 models × 4 conditions). Not started.
- [x] **Task 010 — EXP-003 scaffold pipeline implemented** (implementation
  of the approved design; no LLM called, no results produced):
  - [x] Deterministic scaffold generator `scripts/build_exp003_scaffold.py`:
        Polish→ISV reverse index from `basic.json` `pl` column, pipeline
        multiword → names (D-031) → exact hit → dictionary-verified lemma
        recovery → curated residual → `[?]`; per-story committed curation
        tables (`curation/op-pl/{names,multiword,residual}.tsv`, D-032);
        candidate provenance incl. headword-note cleaning and
        comma-separated orthographic-variant splitting (D-033); grammar
        annotations for condition D (dictionary POS + verb aspect + a few
        generated example forms); `scaffold.json` + rendered `scaffold_B/C/D.txt`.
  - [x] 12 self-contained operator prompts (4 conditions × 3 models:
        ChatGPT, Claude, Bielik) via `scripts/package_exp003_prompts.py`;
        deterministic, no timestamps, cross-model prompts byte-identical
        except the condition block; manifest with hashes.
  - [x] Run orchestrator `scripts/run_exp003_pilot.py`
        (prepare / collect / evaluate / status): plan.json with run ids +
        prompt/source/scaffold hashes; collect stores external replies
        byte-for-byte, never overwrites, records SHA-256 + model metadata +
        resource pins; evaluate runs the Task 008 evaluator unmodified.
  - [x] Comparison `scripts/compare_exp003.py`: per-run two-tier metrics,
        name-excluded diagnostics (D-030), candidate-usage proxy,
        invented/non-supplied forms breakdown, within-model and
        within-condition pairwise token-aligned transitions + A→C/B→C
        regression lists + metric/structure deltas, blinded complete-text
        human-review pairs with a separate label key.
  - [x] Integrity verifier `scripts/verify_exp003_runs.py` (completeness,
        SHA-256 byte-for-byte integrity, meta self-consistency).
  - [x] 30 new focused tests (scaffold, provenance, candidate hierarchy,
        proper names, determinism, prompt packaging, condition separation,
        run integrity, comparison logic); full suite **75 green**.
  - [x] Determinism verified: two independent scaffold builds byte-identical.
  - [x] Scaffold stats (op-pl story): 1453 lexical tokens; 136 exact
        reverse-index, 102 dictionary-verified recovery, 509 curated,
        3 unmapped `[?]` (per-token stats); per-kind stats reconciled
        (`sum(by_kind_tokens) == lexical_tokens`).
  - [x] Scope held: no evaluator change, no LLM API client, no UI/db/service.
        SODA docs updated (DECISIONS D-030…D-034, LESSONS L-024…L-026,
        RESEARCH_NOTES §4.8, EXPERIMENTS, STATE, SOURCES).
        **Experiment not executed — the Project Owner runs the 12 prompts
        externally and returns raw replies.**
- [x] **Task 011 — EXP-003 intake, integrity check and preliminary analysis**
  (no LLM called, no methodology changed, no output repaired):
  - [x] All 12 external replies located in `experiments/exp003-scaffold/temp/`,
        inspected (existence/bytes/SHA-256/completeness/truncation/commentary/
        story structure/format anomalies), and registered byte-for-byte via
        `run_exp003_pilot.py collect` with the real model metadata
        (ChatGPT GPT-5.6 Luna thinking OFF; Claude Sonnet 5 Medium; Bielik 3.0;
        unknowns kept `unknown`; new additive fields `generation_parameters`
        and documented `status`, D-035). Never overwrote; temp files untouched.
  - [x] Completeness matrix: **8/12 complete** (ChatGPT A–D, Claude A–D —
        all story sections + end marker, no commentary); **4/12 Bielik runs
        unusable**: A/B truncated mid-story (≈3/7 acts; ≈40 % of text), C =
        Croatian paraphrase/echo of the prompt (no translation), D = service
        error page (no translation). Bielik C/D recorded
        `failed_external_output` (not evaluable — no fabricated result);
        Bielik A/B `collected_partial_output` (evaluated, partial text only).
  - [x] Evaluated the 10 processable runs with the Task 008 evaluator
        unmodified; ran the comparison tool on the 8 complete runs
        (Bielik preserved but excluded, D-035).
  - [x] Preliminary coverage (canonical/broader): ChatGPT
        A 76.3/87.1 → B 85.7/90.8 → C 84.8/89.2 → D 84.0/88.8; Claude
        A 75.8/87.5 → B 79.0/86.4 → C 75.4/84.5 → D 85.6/92.0.
        B helps both models (+9.4 / +3.2 pp); alternatives (C) do not beat B;
        Claude D is the strongest run (+10.2 pp over its C), ChatGPT D does not
        add over B/C. No composite score; no ranking by coverage alone.
  - [x] Integrity: `verify_exp003_runs.py` 12/12 OK; temp == collected
        byte-identical; full test suite 77 green (2 new tests for collect
        status/parameters and compare run-partition exclusion).
  - [x] Validity (evidence-based): 8/12 executed the intended conditions;
        only 8/12 are quantitatively comparable; Bielik failed 3/4 conditions;
        no scaffold-side artifact defect observed; C did not beat B for either
        model (Claude C below its own A); D is model-dependent; **Bielik is
        not usable as a quantitative participant**.
  - [x] SODA docs updated (DECISIONS D-035, LESSONS L-027, RESEARCH_NOTES
        §4.9, EXPERIMENTS, STATE, ROADMAP).
- [x] **Task 012 — blinded holistic human naturalness review prepared**
  (**SUPERSEDED as the primary method by Task 014** — kept as a
  historical/provisional artifact; no LLM called, no output modified, no
  evaluator change, no metrics exposed):
  - [x] `compare_exp003.py`'s `render_human_pairs` upgraded to the DESIGN
        §11-compliant artifact: neutral "Set 1/Set 2" labels (model identity
        only in the key file), per-set deterministic randomized
        "Version 1..4" mapping (fixed seed `20260901`, reproducible), the
        four holistic questions verbatim, preference-ordering template,
        clearly separated post-unblinding section (scaffold-constraint
        question, B/C/D only), and a recording checklist; translations
        embedded byte-exact from the collected outputs.
  - [x] `human_review.md` regenerated for the 8 complete runs (ChatGPT A–D,
        Claude A–D); Bielik excluded (all four runs incomplete/failed,
        preserved as qualitative artifacts); `human_review_key.json` holds
        the set→model→condition→version→run mapping.
  - [x] 2 new tests (blinding/content/determinism/byte-exactness; exclusion
        of incomplete models); full suite **79 green**.
  - [x] Docs: RESEARCH_NOTES §4.10 (review cohort), comparison README,
        STATE, ROADMAP.
  - [x] **Task 014 follow-up: superseded.** The Project Owner attempted the
        holistic review and found comparing four complete long translations
        too cognitively demanding (format problem, not a result about any
        condition — D-038). `human_review.md` now carries a superseded
        banner; no holistic human result was obtained and none is recorded.
- [x] **Task 013 — EXP-004 practical model screening DESIGNED** (no LLM
  called, no output produced, no evaluator/metric/experiment changed; the
  open EXP-003 human review is untouched):
  - [x] Design document `experiments/exp004-modelscreen/DESIGN.md`
        (DESIGN ONLY — not approved, not executed): central hypothesis
        restated as hypothesis; two-phase structure (Phase A model
        screening / Phase B guidance-method experiments, D-037);
        practical model-access filter (D-036); candidate roster with
        repo-evidence vs to-confirm status (GPT-5.6 Luna OFF/ON, custom GPT
        ISV Teacher, Claude Sonnet 5, Gemini, DeepSeek-V4-Pro OFF/ON, Grok,
        Kimi, Qwen, GLM conditional; Venice AI excluded as platform, Mistral
        not assumed, Bielik preserved qualitative only); Phase A protocol
        (identical story-only source, equivalent no-guidance instruction,
        full recording incl. context/window + access observations,
        byte-for-byte collection with D-035 statuses + L-027 completeness
        gate, Task 008 two-tier evaluator unmodified, no manual word-by-word
        classification); Phase B extensibility (strategy list mapped to
        existing machinery, deterministic-guidance discipline); anti-leak
        rule (no encoded winner); open items requiring coordinator
        confirmation.
  - [x] SODA docs updated (DECISIONS D-036/D-037, LESSONS L-028,
        RESEARCH_NOTES §4.11 + open questions, EXPERIMENTS, STATE,
        ROADMAP). Full test suite 79 green (no code changed).
- [x] **Task 014 — EXP-003 human evaluation replaced by a sentence-level
  forced-choice test** (no LLM judge; no holistic result inferred; EXP-004
  untouched, stays design-only; old holistic artifact preserved as
  superseded):
  - [x] New method decided and recorded (D-038): the Project Owner found the
        holistic complete-text comparison too cognitively demanding, so the
        PRIMARY EXP-003 human-evaluation method is now ONE sentence-level
        forced-choice experiment — this is the ONE planned human-evaluation
        exercise for EXP-003. No holistic human result exists.
  - [x] `scripts/prepare_exp003_sentence_review.py` (deterministic, pure):
        line-based segmentation; monotonic length-based DP alignment
        (1:1/1:2/2:1 + skips) between the Polish source and each of the four
        conditions per model; quadruple pool with all-pairs cross-run token
        overlap floor (same content), ≥4-word completeness, exclusion of
        all-four-identical sentences; stratified sampling (story section ×
        dialogue) ~50/model; per-question seeded randomization of the
        A/B/C/D → "Version 1..4" display order (seed `20260905`, never
        alphabetical).
  - [x] Participant document `comparison/sentence_review.md` (100 questions,
        self-contained, blinded: no model names, no A/B/C/D condition
        labels, no metrics, no hints; instructions ask for a holistic
        sentence impression and explicitly say NOT to verify words against a
        dictionary) + private answer key `comparison/sentence_review_key.json`
        (source sentence identity/text, section, dialogue flag, run ids,
        version texts, display order, seed, hashes; opened only after
        answering).
  - [x] Holistic artifact marked superseded: `compare_exp003.py`'s
        `render_human_pairs` emits a SUPERSEDED banner; comparison README
        documents both artifacts; no answers were recorded anywhere.
  - [x] 7 new tests (determinism/reproducibility, per-question randomization
        and non-alphabetical orders, alignment content check, exclusion of
        misaligned/all-identical sentences, blinding of the participant
        document, answer-key↔document correctness, no-overwrite guard); full
        suite **86 green**.
  - [x] Docs updated (DECISIONS D-038/D-039, LESSONS L-029, RESEARCH_NOTES
        §4.12 + supersession note, EXPERIMENTS, STATE, ROADMAP, comparison
        README, exp003 README).
- [x] **Task 015 — character-level orthographic sanity audit over all
  EXP-001/002/003 outputs** (audit-only; EXP-003 closure-relevant QC; EXP-004
  untouched; no score or comparison artifact changed):
  - [x] Authoritative inventory: the Interslavic alphabet as defined by the
        Interslavic project on its official site —
        https://steen.free.fr/interslavic/orthography.html (fetched
        2026-09-05): standard 27-letter Latin alphabet (no q/w/x) +
        etymological letters `ę ų å ė ȯ ć đ ĺ ń ŕ ś ź` + sanctioned
        alternatives `ť ď ľ ň ř è ò` and combining-acute `t́ d́`. NOT derived
        from our dictionaries/resources/outputs (D-040).
  - [x] `src/isv_eval/orthography.py` deterministic validator: per char —
        allowed ISV letter / Cyrillic / Polish-specific `ą ł ó ż` (ć ę ń ś ź
        are valid etymological ISV letters and allowed) / other Latin /
        other script / unexpected non-letter. Whitespace, ASCII digits and
        an explicit prose-punctuation set are accepted; markdown/control/
        formatting glyphs are reported as non-letter notes, never alphabet
        errors. Text is never modified, transliterated, or repaired.
  - [x] `scripts/check_orthography.py` runs all EXP-001 (7) / EXP-002 (7) /
        EXP-003 (12) outputs deterministically and writes per-experiment
        `outputs/orthography_report.{json,md}` (gitignored) with per-file
        totals, outside-inventory breakdown, distinct unexpected chars,
        frequencies, and line numbers. Result is a SEPARATE quality dimension
        (D-041): resource-grounded lexical coverage is untouched.
  - [x] Anomalies recorded (see RESEARCH_NOTES §4.13): Cyrillic in
        Latin-script output (EXP-001/002 Claude 23/59; EXP-003 Claude a–d
        9–45 incl. intra-word `Може`/`ь`); Polish names kept verbatim
        (`Bronisława`/`Przemysława` → `ł`, `w`); Czech/Slovak accented drift
        in EXP-003 ChatGPT/Claude and largely Czech Bielik-B; non-ISV
        diacritics (`ē` in Gemini `dējstvitelno`, OCS-style `ǫ` in gpt-isvt
        `Myslǫ`); Markdown `#`/`*` in EXP-001/002 outputs; Bielik-C prompt
        echo (`→ ‡ [ ]`). Outside-inventory totals: 267 / 309 / 1 297 chars.
  - [x] 21 new tests (inventory exactness, Cyrillic/Polish/other-Latin/
        other-script classification, t́/d́ combining acute, punctuation/
        whitespace/digits, corpus quotes/dashes, empty text, clean vs single
        invalid character, mixed Latin/Cyrillic, determinism/purity, runner
        determinism); full suite **107 green**.
  - [x] Docs updated (DECISIONS D-040/D-041, LESSONS L-031, RESEARCH_NOTES
        §4.13 + §5/§6, EXPERIMENTS follow-up + status, STATE, ROADMAP).
- [x] **Task 016 — EXP-003 closed: human test decoded + analyzed; EXP-004
      Phase-1 roster/protocol finalized (2026-09-05).**
  - [x] Completed questionnaire recovered and verified against the private
        key: 100 questions, original order, one tick each, 399/400 Version
        texts byte-identical; two provenance artifacts recorded (Q58 `[x ]`
        encoding; Q67 non-chosen Version-2 accidental transposition — no
        effect on decoding; document never modified/regenerated, D-043).
  - [x] `scripts/analyze_exp003_sentence_review.py` decodes Version→A/B/C/D
        deterministically, computes per-version/per-condition/per-model
        results with sample sizes, and combines them with the unchanged
        Task 011 coverage/unresolved metrics and the Task 015 orthographic
        audit incl. a deterministic non-name refinement; writes
        `comparison/sentence_review_results.{json,md}`. No composite score.
  - [x] Human results (n = 100; 50/model): per condition A 26 % / B 16 % /
        C 19 % / D 39 % (χ²(3) = 12.56, p ≈ 0.006); ChatGPT A 26 / B 12 /
        C 26 / D 36 % (p ≈ 0.12); Claude A 26 / B 20 / C 12 / D 42 %
        (p ≈ 0.02); guidance vs. baseline 74 % vs. 26 % for both models;
        no display-position bias; one verbatim comment (Q7).
  - [x] Final report `experiments/exp003-scaffold/REPORT.md` written:
        human results, automated evidence, Task 015 orthographic findings
        (incl. non-name refinement), human-vs-automated comparison
        (agreeing for Claude at the D/C extremes, diverging for ChatGPT-B),
        what EXP-003 supports / does not support, limitations.
  - [x] 11 new decoder tests; full suite green.
  - [x] Docs updated (DECISIONS D-042/D-043, LESSONS L-032/L-033,
        RESEARCH_NOTES §4.14 + §5/§6, EXPERIMENTS follow-up + status,
        STATE, ROADMAP, exp003 REPORT/README, comparison README).
  - [x] EXP-004 Phase-1 roster/screening protocol finalized in DESIGN §11.7/
        §12 (clean baseline first; methods 1–7 only after Phase 1 selects
        models; no human evaluation; exclusions: Venice/local/Bielik).
        **Not executed** — gated on design approval + access confirmations.
- [x] **Task 017 — EXP-004 Phase 1 execution: screening kit prepared
      (approved; LLM output pending the author's external sessions,
      2026-09-05)** → the external sessions then happened and are recorded
      in Task 018 below.
  - [x] Design approved for execution (§12) — EXP-003 closed, no new human
        evaluation (D-042).
  - [x] `base_instruction.txt`: single direct-translation instruction
        (§6.9 wording); byte-identical instruction body across all 11
        roster rows.
  - [x] `scripts/run_exp004_phase1.py` — prepare (prompts + manifest +
        `outputs/plan.json`, run ids `<date>__<provider>__<model>__
        <model_version>__direct`; deterministic), collect (byte-for-byte,
        never overwrite; status + per-row practical free-access verdict
        D-036), verify (structural completeness gate calibrated on EXP-003
        data — size ≥ 0.6×source, final KONIEC/KONĖC, ≥ 3/5 story names,
        head sanity; verdicts complete/partial/failed preserved as data,
        D-044), evaluate (Task 008 evaluator unmodified + Task 015
        orthography; refused for `failed` intakes; `usable` = complete),
        status, roster (coverage pair/unresolved/orthography/access — no
        ranking, no composite).
  - [x] `scripts/check_orthography.py` includes EXP-004.
  - [x] 10 new tests; full suite **128 green**.
  - [x] Prompts packaged locally with `prepare --date 2026-09-06`
        (11 files; gitignored), prompt manifest + READMEs committed.
  - [x] Docs updated (DECISIONS D-044, LESSONS L-034, STATE, ROADMAP,
        EXPERIMENTS follow-up + status, exp004 DESIGN §12 + README).
  - [x] **Remaining (now DONE — Task 018 below):** author executes the 11
        operator prompts in the models' web/chat interfaces (recording per-
        row status + access verdict), returns raw replies byte-for-byte →
        collect/verify/evaluate/roster → Phase 1 report + Phase 2
        shortlist. Phase 2 must not start before then.
- [x] **Task 018 — EXP-004 Phase 1 collected outputs audited + reconciled
      (execution completed by the author; 2026-09-06).**
  - [x] Author executed 19 sessions externally; planned 11-row roster
        expanded into 19 concrete runs (Claude Sonnet 5 Medium + max;
        DeepSeek V3 Instant + V3 Expert × DeepThink OFF/ON; Qwen 3.8 Max
        Thinking/Fast + 3.7 Plus Thinking/Fast; Gemini 3.1 Pro ext-thinking
        ON + 3.6 Flash OFF/ON; GPT-5.6 Luna OFF/ON; ISV Teacher custom GPT;
        Grok; Kimi K2.6 Instant; GLM 4.5 failed).
  - [x] `collected-sessions/` archive: 19 raw session files (prompt+reply)
        preserved byte-for-byte (gitignored; README committed).
  - [x] `scripts/audit_exp004_collected.py`: read-only audit (instruction-
        body byte identity vs canonical prompts — all 19 OK; reply
        extraction boundary; end markers; duplicate detection — none).
  - [x] `run_exp004_phase1.py collect-session`: deterministic reply
        extraction + integrity check + refusal to overwrite; 19 runs
        registered (meta records session SHA-256 + canonical prompt hash +
        access verdicts reconciled from execution evidence).
  - [x] Reconciliation resolved author-naming drift with the author:
        15/16 = DeepSeek V3 Expert (stale `v4-pro` filenames); 19 = Qwen
        3.8 Max Fast (header copy error); 05 = Gemini 3.1 Pro ext-thinking
        ON. GLM disposition from evidence (service-error artifact →
        `failed_external_output`, excluded per protocol — no special rule).
        Claude Sonnet 5 max >45 min / free-tier exhaustion kept as
        availability data only.
  - [x] Completeness gate name check recalibrated to ISV-tolerant folded
        stems (Kimi/DeepSeek V3 Expert OFF and others transliterate proper
        names); end marker accepts KONIEC/KONEC/KONĖC (D-045, L-035).
  - [x] Intake: **18/19 complete; GLM failed**. Evaluate + orthography
        audit on all eligible runs; roster regenerated (18 usable rows +
        GLM excluded). Tests: +8 (collect-session, stem gate, audit
        helpers/end-to-end); full suite green.
  - [x] Docs updated (D-045, L-035, DESIGN §12, exp004 README +
        operator-prompts/collected-sessions/outputs READMEs, STATE, ROADMAP,
        EXPERIMENTS, RESEARCH_NOTES).
- [x] **Task 019 — EXP-004 Phase 2A corpus priming PREPARED (full roster;
      execution-ready; 2026-09-06).** No external LLM call in this task.
  - [x] Hypothesis fixed: does exposing an LLM to authentic
        Medžuslovjansky immediately before translation change its generated
        Medžuslovjansky (in-context learning / corpus priming / contextual
        grounding / reference-text conditioning — NOT training, NOT
        reconstruction). Coordinator's 3–5-model "Phase 2 shortlist" idea
        explicitly NOT taken: full reconciled 18-configuration Phase-1
        roster (GLM excluded), derived in code from the Phase-1 roster.
  - [x] Fixed reference corpus: "Tuta historija" excerpt (Prolog + Razděl 1
        "Věčna Zima") supplied by the author in the task text — no URL,
        embedded directly in Prompt-1 files; 4 820 B; SHA-256
        `413830fa4ff6aaa8833895a22e7ef1fa5fa3807e5a5a105b7e4050cf7b67a29c`;
        local/gitignored (distribution status not recorded); provenance +
        contamination probe in `phase2a/corpus/README.md`. (Revised by Task
        020: combined three-register corpus — see the next entry.)
  - [x] Two conditions: control `p2a-ctl` (Phase-1 clean direct task —
        Phase-1 outputs satisfy it; fresh control optional and preferred by
        compare when executed) and corpus-primed `p2a-primed` (msg1 = study
        reference text; no translation/summary/reproduction/imitation/
        questions — msg2 = same Polish story + standard instruction +
        reference cue, SAME session). Translation instruction + story body
        byte-identical across all control/msg2 prompts.
  - [x] Contamination control mechanical: fresh session per run;
        `collect-session` requires the corpus BEFORE the translation
        instruction in primed sessions (same-session proof), rejects
        control sessions containing corpus material, rejects altered
        translation instructions.
  - [x] Run identity: `<date>__…__p2a-ctl|p2a-primed`, each linked to its
        Phase-1 `baseline_run_id` (all 36 resolved against the actual
        Phase-1 plan); 36-run plan + 54 prompt files + manifest (hashes);
        deterministic kit.
  - [x] `scripts/run_exp004_phase2a.py` — prepare/collect/collect-session/
        verify/evaluate/status/roster/**compare** (per-dimension deltas vs
        baseline; no composite score, no ranking).
  - [x] Tests: 19 new (roster = 18 usable configs; run identity + condition
        separation vs Phase 1; corpus/source hash consistency; prompt
        separation; no corpus in control; primed session requires corpus;
        contamination rejection; compare); full suite **155 green**.
  - [x] Docs updated (D-046, L-036, RESEARCH_NOTES §4.17 Claude-Sonnet-5-max
        availability observation + §4.18 Phase 2A prep, DESIGN §13, exp004
        README + phase2a READMEs, STATE, ROADMAP, EXPERIMENTS).
  - [x] Phase 2B (Wikipedia-length authentic reference + independent Polish
        story) documented as future work — not started.
- [x] **Task 020 — EXP-004 Phase 2A corpus revised to three authentic
      registers PREPARED (execution-ready; 2026-09-07).** No external LLM
      call in this task.
  - [x] Combined three-register corpus under
        `experiments/exp004-modelscreen/phase2a/corpus/` (all corpus text
        files local/gitignored; corpus README provenance + hashes
        committed; corpus id `phase2a-authentic-isv` v1):
        1. literary/narrative — `tuta-historija-excerpt.txt` (unchanged
           Task-019 excerpt, 4 820 B, SHA-256 `413830fa…67a29c`);
        2. artistic/poetic — `album-ahoj-slovjani-artistic-isv.txt`
           (complete Latin-script album "Ahoj, Slovjani!" — 11 songs in
           order, 76 unique stanzas, 322 lines, 9 407 B, SHA-256
           `7e25a56f…52dcacf`; source: author-supplied copy of
           melacpise.wordpress.com/album-ahoj-slovjani-teksty-pesnej/;
           Cyrillic duplicates + webpage/HTML removed; 24 verbatim
           repeated stanzas/refrains deduplicated; linguistic forms NOT
           normalized/corrected; license/distribution status not
           established → local-only);
        3. informative/encyclopedic —
           `wiki-sadovnistvo-encyclopedic-isv.txt` (cleaned running prose
           of the authentic Medžuslovjansky Wikipedia article
           "Sadovničstvo", retrieved 2026-09-07 from the Wikimedia
           MediaWiki wikitext API — raw kept at `corpus/sources/`;
           boilerplate/templates/links removed; 84 paragraphs, 44 101 B,
           SHA-256 `b03402fe…4c8345`; CC BY-SA 4.0; authentic ISV
           article, NOT a project translation of any other-language
           version).
  - [x] Authoritative combined file `phase2a-authentic-isv-corpus.txt`:
        58 459 B, ≈8 184 whitespace tokens, SHA-256 `aaad28e4…a857`;
        register section headers `=== REGISTER 1: LITERARY / NARRATIVE ===`
        … `=== REGISTER 3: INFORMATIVE / ENCYCLOPEDIC ===`; built
        deterministically by `scripts/build_phase2a_corpus.py`.
  - [x] Prompt-1/msg1 declares the three authentic registers and asks the
        model to study the corpus as a language reference (vocabulary,
        morphology, syntax, word formation, phraseology, orthography,
        stylistic patterns); warns the artistic register may contain
        deliberate poetic choices and is not a normative grammar template;
        forbids translating/summarizing/reproducing/continuing/analyzing
        the corpus or answering questions about it. msg2 (same Polish
        story task) unchanged; control prompts corpus-free; every primed
        msg1 embeds the SAME corpus bytes for all 18 configurations;
        prompt regeneration deterministic; manifest regenerated (54 prompt
        files).
  - [x] `scripts/run_exp004_phase2a.py` updated: `AUTH_CORPUS_SHA256` =
        `aaad28e4…a857`; `CORPUS_ANCHORS` = 3 fingerprint phrases (one per
        register); collect-session requires ALL THREE anchors before the
        translation instruction in primed sessions, rejects ANY anchor in
        control sessions. Tests updated (`tests/test_exp004_phase2a.py`) +
        new real-corpus suite (`tests/test_exp004_phase2a_corpus.py`).
  - [x] Docs updated (STATE, EXPERIMENTS, this file; corpus README records
        provenance).
  - [x] Kit remains execution-ready, NOT executed — next operator step:
        the author executes the 18 primed sessions externally (control
        `p2a-ctl` + corpus-primed `p2a-primed` per Phase-1-usable
        configuration).

- [x] **Task 021 — EXP-004 Phase 2A executed, collected, audited and
      evaluated (2026-09-07).** No LLM call in this task.
  - [x] Inventory + validation of the author's completed runs: all 18
        original primed configurations + two exploratory primed runs of a
        newly discovered model recorded as **Dola 3.8** (runs 20/21;
        author-recorded "ByteDance — official web interface", proprietary;
        labels "Dola 3.8 — Fast"/"Dola 3.8 — Pro"; NOT part of the
        original 18-model roster, NO Phase-1 baseline, preserved as two
        distinct exploratory observations). Dola prompt files were copied
        from the Qwen-3.8-Max-THINKING template with header metadata
        edited (leftover Qwen title/"COPY THIS ENTIRE FILE INTO Qwen
        Chat (web)" lines + a msg1 `Condition:` label mislabelled
        "(translation task)" recorded as cosmetic artifacts); msg1 corpus
        regions byte-identical to the authoritative corpus in all 20 runs;
        msg2 Polish-story bodies byte-identical.
  - [x] Collection: no full same-session transcripts were stored — each
        run's record is the operator msg2 prompt file with the raw model
        reply appended after the closing `## Output` marker; new
        `collect-msg2` command registers these (reply sliced at the
        marker, stored byte-for-byte; meta records no machine same-session
        proof — documented protocol deviation; raw bytes never edited).
  - [x] `extend-exploratory` appended the two Dola rows to `plan.json`
        (38 rows; `baseline_run_id: null`) and 4 manifest entries
        (`exploratory: true`; 58 total) idempotently — the original 36-run
        / 54-file preregistered protocol was never modified.
  - [x] Corpus integrity re-run: combined file still SHA-256 `aaad28e4…a857`
        (58 459 B); 20/20 primed msg1 corpus tails byte-identical;
        controls corpus-free; corpus NOT regenerated.
  - [x] Verify + evaluate: 19 runs intake `complete`, 1 `partial` (run 12 —
        Claude Sonnet 5 max — final line `**KONEC**` bold-wrapped); all 20
        evaluated through the unmodified deterministic pipeline
        (`phase2a/outputs/` per-run evaluation + orthography; roster 38
        rows); `compare` = 18-row primed-vs-Phase-1 delta table, Dola rows
        report no-baseline (no priming effect claimed).
  - [x] Manual execution constraints recorded (Gemini two-message corpus
        ~83%+~17%; Gemini 3.1 Pro corpus ingestion in 3.6 Flash then
        switch to 3.1 Pro for the translation — ingestion model ≠
        translation model; Gemini extended-thinking reset per prompt;
        Claude token-limit continuations) — protocol conditions, not
        quality judgments, evaluator unchanged.
  - [x] Tests: `tests/test_exp004_phase2a_exploratory.py` (3 new; Dola
        distinctness, extend-exploratory idempotency, collect-msg2 reply
        extraction/rejection, no-baseline guard); full suite green.
  - [x] Docs updated (STATE, EXPERIMENTS, RESEARCH_NOTES §4.20, DECISIONS
        D-048, LESSONS L-038, ROADMAP this file; exp004 README +
        phase2a READMEs). No Phase 2B work; no model selection — the
        research lead decides what the results mean.
- [x] **Task 022 — Phase-1 DIRECT baselines prepared for the two
      exploratory Dola 3.8 configurations (2026-09-07).** No LLM call in
      this task.
  - [x] Prepared the two missing Phase-1 direct baselines retrospectively
        through the existing Phase-1 direct protocol — Dola was discovered
        after the 18-configuration roster was fixed (Task 021), so this is
        an **exploratory extension**, NOT part of the original planned 18:
        `scripts/run_exp004_phase1.py extend-direct --date 2026-09-07`
        rendered the canonical direct operator prompts
        (`operator-prompts/20-dola-3.8-fast.md` = run id
        `2026-09-07__bytedance__dola-3.8__fast__direct`;
        `21-dola-3.8-pro.md` = `…__pro__direct`) — exact same Polish source
        story and direct-translation instruction as the original 18,
        corpus-free, no scaffold/dictionary/morphology/grammar material,
        no previous Dola conversation, fresh-session requirement explicit,
        Dola configuration named per configuration (`Dola 3.8 — Fast` /
        `Dola 3.8 — Pro`; author-recorded ByteDance identity preserved,
        `exploratory: true` kept, no independently verified claim).
  - [x] Plan/manifest rows appended as `pending_manual_collection`
        (idempotent; manifest entries + sha256 hashes) — **nothing
        collected, no metrics, no placeholder results, no false completed
        baseline**; the original 18 Phase-1 baselines untouched.
  - [x] `scripts/run_exp004_phase2a.py link-baselines` wired each Dola
        p2a-primed plan row's `baseline_run_id` to its prepared direct id
        (`baseline_status: pending_collection`); `compare` reports those
        rows as pending (no fabricated deltas). Pairing is unambiguous:
        direct `fast` ↔ Phase-2A run 20 (`…__fast__p2a-primed`); direct
        `pro` ↔ Phase-2A run 21 (`…__pro__p2a-primed`).
  - [x] Tests: `tests/test_exp004_phase1_dola_baselines.py` (new module:
        corpus-free prompts with exact Polish source/instruction, distinct
        Dola metadata, no Phase-2A link, no false completed baseline,
        unambiguous pairing, original 18 unchanged, full lifecycle
        pending→collected→delta); full suite green.
  - [x] Docs updated (STATE, EXPERIMENTS, RESEARCH_NOTES §4.21, DECISIONS
        D-049, LESSONS L-039, ROADMAP this file; exp004 README +
        phase2a README).
- [x] **Task 023 — Phase-1 DIRECT baselines for the exploratory Dola 3.8
      configurations executed, collected, validated and compared
      (2026-09-07).** No LLM call in this task.
  - [x] The author executed both Dola Phase-1 direct baselines in fresh
        ByteDance sessions (direct translation only — no corpus, no
        scaffold, no dictionary, no previous Dola conversation) and saved
        each raw reply **msg2-style inside its operator prompt file**
        (`operator-prompts/20-dola-3.8-fast.md`,
        `21-dola-3.8-pro.md`: prompt part through the closing `## Output`
        marker byte-identical to the canonical prompt; the trailing
        "Return the complete …" boilerplate replaced by the reply — the
        same record shape the Phase-2A runs used in Task 021).
  - [x] Intake validated for both records (correct Dola config per
        operator note, exact Phase-1 DIRECT prompt, fresh-session/direct
        condition, corpus-free, no Medžuslovjansky reference, exact Polish
        story, exact direct-translation instruction, complete raw reply,
        expected ending marker, no accidental Phase-2A continuation, no
        contamination); collected via the existing Phase-1
        `collect-session` workflow and passed `verify` (verdict
        `complete`, usable) — the Phase-1 verifier now accepts msg2-style
        records without a false prompt-drift FAIL (`_session_is_prompt_record`
        helper; immutability checked against the recorded session SHA-256).
  - [x] Both baselines evaluated with the same deterministic pipeline
        (evaluation.json + orthography.json under the Phase-1 outputs).
  - [x] Pairing verified: Dola Fast direct ↔ Phase-2A run 20; Dola Pro
        direct ↔ Phase-2A run 21; `compare` now reports **real
        within-Dola Phase 1 → Phase 2A deltas** (canonical coverage:
        Fast 38.87 % → 67.07 % [+28.20 pp]; Pro 65.08 % → 71.75 %
        [+6.67 pp]; broader/unresolved/token/A/B/C deltas in
        `phase2a/outputs/compare.md`).
  - [x] Original 18 Phase-1 baselines untouched; no P2A corpus
        contamination in the P1 records; `exploratory: true` preserved;
        Task-020/021 history not rewritten.
  - [x] Tests: `tests/test_exp004_phase1_dola_baselines.py` extended
        (msg2-style collect + verify accepts the prompt file as the
        record, tamper-after-collection caught, real compare deltas);
        full suite green.
  - [x] Docs updated (STATE, EXPERIMENTS, RESEARCH_NOTES §4.22, DECISIONS
        D-050, LESSONS L-040, ROADMAP this file; exp004 README +
        phase2a README).
- [x] **Task 024 — EXP-004 full analysis: Phase 1 → Phase 2A corpus
      priming (2026-09-07).** Research-analysis task. No LLM call; no new
      model outputs; no raw-output/corpus modification; no Phase 2B; no
      human evaluation; no new evaluator; evaluation definitions
      unchanged.
  - [x] Deterministic 20-configuration dataset (18 original + 2
        exploratory Dola 3.8) from the Phase-1 roster + Phase-2A roster +
        `compare.json` via `scripts/analyze_exp004_phase2a.py` (std-lib
        only; every recomputed delta cross-checked against `compare`; Dola
        rows keep `exploratory: true` and their run 20/21 pairing; input
        SHA-256s recorded).
  - [x] Phase-1 and Phase-2A landscape rankings on four separate
        dimensions (canonical / broader / unresolved / orthography) — no
        composite, no "best model score".
  - [x] Priming Δ table sorted by Δ canonical then Δ broader (original 18:
        mean +6.00 pp, median +4.92 pp, sd 3.39 pp, min +1.74, max +14.33,
        positive 18/18; broader mean +2.36 pp, median +2.14, −0.92 …
        +11.23, positive 14/18; the 20-config set reported separately as
        exploratory, mean +7.15 pp).
  - [x] Exploratory exact paired tests over the original 18 (two-sided
        sign test canonical p ≈ 7.6e-6, broader p ≈ 0.031; exact
        sign-flip permutation test on the mean p ≈ 7.6e-6 / 9.6e-4) with
        the n = 1-per-condition limitation stated alongside; descriptive
        Spearman baseline-dependence (P1 canonical vs Δ canonical
        ρ = −0.86; broader ρ = −0.84) and baseline-vs-primed (ρ = +0.45 /
        +0.37, n = 18).
  - [x] Dola analysed separately: Fast +28.20 pp canonical from the
        experiment's lowest Phase-1 baseline (38.87 %), Pro +6.67 pp from
        65.08 % — recorded as **large observed changes consistent with
        baseline dependence**, NOT as evidence of stronger corpus
        learning; both Dola rows highlighted in the figures without
        altering the data.
  - [x] Family (GPT/Claude/Gemini/DeepSeek/Qwen/Dola), orthography
        (outside-inventory by audit category, high-coverage + zero-anomaly
        configurations listed without a composite), and separate
        practical-usability dimensions (Claude interruptions/
        continuations; Gemini two-message corpus + 3.1 Pro ingestion-model
        split + thinking-toggle reset; Dola identity recorded-but-
        unverifiable; GLM exclusion) — reproduced in the master table
        Notes column.
  - [x] Research-facing master table (20 rows; status incl.
        `exploratory` for Dola; P1/P2A/Δ canonical + broader, P2A
        unresolved + orthography-out, notes), charts A–G (deterministic
        SVG in `analysis/figures/`), and a first poster draft
        (`analysis/poster.{md,html}`) — no winner score anywhere.
  - [x] Interpretation split into supported / suggestive / not-established
        (incl. the nine candidate statements from the brief); research
        candidates (Claude Sonnet 5 Medium, DeepSeek V3 Expert ON/OFF,
        Qwen 3.8 Max Fast, Gemini 3.6 Flash ON, Dola Fast/Pro —
        exploratory) and ≤ 3 next-experiment recommendations (controlled
        repeated generation; Phase 2B unseen-topic transfer; matched-
        variant comparison under strict interface controls) — none
        executed; Phase 2B not started.
  - [x] Artifacts under `experiments/exp004-modelscreen/analysis/`
        (committed README; gitignored dataset/analysis JSON+MD, figures,
        poster); tests `tests/test_analyze_exp004_phase2a.py` (19 new:
        20-config composition, original/Dola separation, Dola pairing,
        exact deltas + `compare` agreement, loud failure on missing
        metrics/baseline, no fabricated metrics, deterministic ordering/
        stats/chart inputs, byte-identical chart regeneration); full suite
        green (212).
  - [x] Docs updated (STATE, EXPERIMENTS, RESEARCH_NOTES §4.23 + §5/§6,
        DECISIONS D-051, LESSONS L-041, ROADMAP this file; exp004 README +
        DESIGN §13.8 + new analysis README).

## Next recommended task (single)

- [x] ~~Project Owner answers the EXP-003 sentence-level questionnaire~~ —
  **DONE (2026-09-05)** and the follow-up analysis is also done (Task 016).
  EXP-003 is closed; results in `experiments/exp003-scaffold/REPORT.md`.
  Headline human result: guidance (B/C/D) preferred over baseline A
  **74 % vs. 26 %** (identical for ChatGPT and Claude); D favored by both
  models (ChatGPT 36 %, Claude 42 %); ChatGPT-B is the automated best but
  the human least preferred — signals reported separately, no composite
  score. Provenance artifacts Q58/Q67 recorded (D-043). One verbatim
  participant comment preserved. Lessons L-032/L-033, decisions D-042/D-043.
- [x] ~~EXP-004 Phase 1 — practical model screening (NEXT, not started)~~ —
  **EXECUTED AND RECONCILED (Task 018, 2026-09-06)**: the author ran 19
  sessions in the external web/chat interfaces; all raw sessions are
  preserved and audited; 18 runs are intake-complete and evaluated, GLM 4.5
  failed/excluded per protocol. Evidence table:
  `experiments/exp004-modelscreen/outputs/roster.md` (per-dimension metrics;
  no composite score, no coverage-only ranking). Clean direct-translation
  baseline only (no scaffolding). Models that actually ran: GPT-5.6 Luna
  OFF/ON, GPT Interslavic Teacher, Claude Sonnet 5 Medium + max, Gemini 3.1
  Pro + 3.6 Flash, DeepSeek V3 Instant + V3 Expert, Grok, Kimi K2.6 Instant,
  Qwen 3.8 Max + 3.7 Plus. Venice/local/Bielik remain excluded as before.
- [x] **EXP-004 Phase 2A — corpus priming: execute the primed sessions** —
  **EXECUTED, COLLECTED, AUDITED AND EVALUATED (Task 021, 2026-09-07)**:
  the author completed all 18 corpus-primed sessions + two exploratory
  Dola 3.8 runs (20/21; separate from the 18-model roster, no Phase-1
  baseline); records registered via `collect-msg2` (operator msg2
  prompt+reply files; msg2-only provenance, no machine same-session
  proof — documented deviation), verified (19 complete / 1 partial
  end-marker), evaluated through the unmodified deterministic pipeline,
  and **compare** produced the 18-row primed-vs-Phase-1 delta table
  (`experiments/exp004-modelscreen/phase2a/outputs/compare.md`; no
  composite score, no ranking; Dola rows no-baseline). Phase-1 baseline
  outputs served as the control condition (`p2a-ctl`); no fresh controls
  were collected. Claude Sonnet 5 max: executed despite the known
  >45-min/free-tier constraint; its reply needed three token-limit
  continuations (documented, raw history not stored); intake `partial`
  (final line `**KONEC**` bold-wrapped) — recorded, preserved, not
  repaired.
- [x] **EXP-004 — Dola Phase-1 DIRECT baselines: author executes the two
  prepared baselines (Task 022 follow-up)** — **EXECUTED, COLLECTED,
  VALIDATED AND EVALUATED (Task 023, 2026-09-07)**: the author ran both
  baselines in fresh ByteDance sessions (Fast ↔ Phase-2A run 20; Pro ↔
  Phase-2A run 21; direct translation only — no corpus, no scaffold, no
  dictionary, no previous Dola conversation), saved each raw reply
  msg2-style inside the canonical prompt file, and
  `collect-session`/`verify`/`evaluate` + `compare` now report the real
  within-Dola Phase 1 → Phase 2A deltas (canonical coverage: Fast
  38.87 % → 67.07 % [+28.20 pp]; Pro 65.08 % → 71.75 % [+6.67 pp];
  `experiments/exp004-modelscreen/phase2a/outputs/compare.md`). Dola
  remains an exploratory extension; no priming effect is claimed beyond
  the recorded deltas.
- [ ] **EXP-004 Phase 1 report** — write the Phase 1 report from
  `outputs/roster.md` + per-run evaluation/orthography artifacts (18 usable
  runs; GLM preserved as the failed/excluded case; Claude Sonnet 5 max
  runtime recorded as availability data) using the documented
  multi-dimensional judgment (practical availability, completeness/
  reliability, lexical/resource evidence, orthographic cleanliness,
  morphology/evidence, obvious quality issues — NOT coverage ranking alone,
  per the EXP-003 lesson). No human-evaluation exercise in EXP-004
  (D-042). A Phase-2A addendum section should then fold in the Task-021
  primed-vs-baseline evidence, the Dola exploratory observations, and the
  Task-023 within-Dola Phase 1 → Phase 2A deltas for runs 20/21
  (`experiments/exp004-modelscreen/phase2a/outputs/compare.md`). **Task
  024 (2026-09-07) completed the full deterministic research analysis**
  (`experiments/exp004-modelscreen/analysis/` — README committed;
  dataset/analysis JSON+MD, charts A–G, poster draft gitignored) that the
  report should cite as its quantitative evidence base; the analysis
  itself does not select a winner and leaves the multi-dimensional
  judgment to the report.

## After the EXP-003 human review is recorded and reported

**STATUS: this gate is satisfied — EXP-003 is recorded and reported
(2026-09-05, Task 016). The section below is kept for the historical rule.**

- [x] ~~EXP-004 Phase A (model screening)~~ — gated on: (a) approval of
  `experiments/exp004-modelscreen/DESIGN.md`, (b) the coordinator's access
  confirmations listed in its §11, and (c) the standing rule above (new
  translation runs start only after the EXP-003 review is recorded and its
  report written). Phase A output: per-model access verdicts + versioned
  no-guidance baseline numbers on the canonical story; then Phase B
  (guidance-method experiments) is scoped from that evidence.
  Do not run EXP-004 translations before the design is approved and access
  details are confirmed.

## Later

- [ ] **Manual linguistic review of the Experiment 001 unresolved sample** —
  annotate `experiments/exp001-baseline/manual-audit/sample.csv`
  (100 stratified forms + 8 shared-by-all diagnostic forms, prepared in Task
  004; full contexts in `sample.json`). The Task 005 cross-resource evidence
  (`cross-resource-audit.csv`) and the new per-token two-layer evidence
  (`resource_evidence` in `tokens.json`) are available as inputs to the review.
    Human classification only — no automatic language-origin detection.
- [ ] Investigate dictionary **data licensing** (Steen source data / Google
  Spreadsheet) before any redistribution of derived data.
- [ ] Decide primary morphology backend for constrained generation
  (JS `@interslavic/morphology` vs Rust `interslavic`) based on integration cost
  and Experiment 001 validation results.
- [ ] Verify whether `interslavicfreq` is published on PyPI; pin accordingly
  (planned signal for suspicious-form ranking, not yet integrated).
- [ ] Precomputed lexicon index (e.g. serialized dict) to cut lexicon load time
  if full-story runs get slow.

## Future ideas (recorded, not implemented)

- Translation-length metrics for future experiments (do NOT compare raw file
  sizes across source vs outputs — the source may carry prompt/formatting
  content, Task 003.1): character count excluding formatting, lexical token
  count, average word length, output/source length ratio.
- `@interslavic/levenshtein` as an approximate-intelligibility signal for
  ranking candidate lexemes in the constrained system.
- `@interslavic/stemmer`/`@interslavic/lunr` for cross-script search over the
  generated lexicon.
- Hunspell `isv.dic` as an independent surface-form validity signal and/or a
  spellcheck-style fuzzy fallback for unresolved forms (Task 005 confirmed it
  covers 54 of the 1,050 unresolved forms with full-form morphological tags;
  integration decision still open).
- Dictionary `type` and `intelligibility` columns as provenance-aware features
  in the candidate ranking (e.g. down-weight neologisms/doubtful entries).
- A lightweight manual-review workflow for "suspicious forms" with sentence
  context preserved (no language-origin classifier in Task 001).
- Token-aligned evaluator-state transitions (implemented in `compare_exp002.py`
  for EXP-002) reused as a standard regression signal in any future
  before/after comparison.
- Two-layer resource evidence in the evaluator (implemented in Task 008):
  per-token `resource_evidence` provenance and the canonical/broader coverage
  pair; a future step could surface the broader tier in the comparison scripts
  (`compare_exp001.py` / `compare_exp002.py`) as a standard additive signal.
- Corpus building: collected raw model outputs + validated analysis as a seed
  evaluation set for later experiments.
