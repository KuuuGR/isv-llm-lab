# Roadmap

Status: updated 2026-09-05 (Task 015 — character-level orthographic sanity
audit completed over all EXP-001/002/003 outputs as an independent,
audit-only quality dimension; no historical score changed. EXP-003 human
judgment remains the immediate pending step: the sentence-level
forced-choice test is ready and unanswered; EXP-004 stays design-only).

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

## Next recommended task (single)

- [ ] **Project Owner answers the EXP-003 sentence-level questionnaire**:
  open `experiments/exp003-scaffold/comparison/sentence_review.md` and tick
  exactly one "Version 1..4" box per question (100 questions, ~10–15
  minutes). Judge which version sounds most natural as Medžuslovjansky as a
  whole; do not verify individual words. Do not open
  `sentence_review_key.json` before finishing. A follow-up SODA task then
  maps the recorded ticks back to conditions via the key and writes the
  EXP-003 analysis report (`REPORT.md`), combining the automatic coverage /
  transition / regression / candidate-usage evidence (Task 011) with the
  human preferences.

## After the EXP-003 human review is recorded and reported

- [ ] **EXP-004 Phase A (model screening)** — gated on: (a) approval of
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
