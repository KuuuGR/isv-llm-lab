# Roadmap

Status: updated 2026-08-31 (Task 007 — resource reconciliation and evaluation
policy completed; next recommended task is implementing that policy in the
evaluator). This is a plan, not a commitment; the Architect/Research Lead
re-prioritizes as evidence arrives.

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

## Next recommended task (single)

- [ ] **Implement the documented resource policy in `isv-eval`** (Task 007
  outcome B, concretized): add a clearly-labeled **alternative-resource
  attestation tier** and report **canonical coverage** and **broader
  resource-supported coverage** side by side, while leaving the historical
  A/B/C classifications and all existing reports untouched. This is the
  smallest step that makes future experiment numbers interpretable under the
  policy in `docs/RESOURCE_POLICY.md`. Do not start it from this roadmap entry
  alone — it requires a SODA task.

## Parallel (not blocking the pilot)

- [ ] **Manual linguistic review of the Experiment 001 unresolved sample** —
  annotate `experiments/exp001-baseline/manual-audit/sample.csv`
  (100 stratified forms + 8 shared-by-all diagnostic forms, prepared in Task
  004; full contexts in `sample.json`). The Task 005 cross-resource evidence
  (`cross-resource-audit.csv`) is available as an input to the review.
  Human classification only — no automatic language-origin detection.

## Later

- [ ] **Experiment 002/003 — full-scale constrained/dictionary-guided
  generation** — only after the evaluator implements the two-tier resource
  policy (next recommended task) makes coverage numbers interpretable; the
  pilot evidence will then decide which unresolved-form categories benefit
  from supplied alternatives.
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
- An explicit, clearly-labeled alternative-resource attestation tier in the
  evaluator (separate from canonical A/B/C), so forms attested in
  `interslavicfreq`/hunspell can be recorded without silently changing the
  canonical classification (candidate direction from Task 006.2
  recommendation B; promoted to the recommended next task by Task 007).
- Corpus building: collected raw model outputs + validated analysis as a seed
  evaluation set for later experiments.
