# Source & Dependency Inventory

Status: snapshot of the audit performed during SODA Task 001 (2026-08-31),
updated at the end of Task 002 with what the harness actually consumes, and at
Task 006.2 with the EXP-002 pilot's finding that the canonical evaluator does
not consume the alternative resources listed below.

This file records every external source relevant to the project, how we intend
to use it, and how we plan to preserve it. See `docs/DECISIONS.md` for the
rationale behind the preservation choices.

Legend for "How we intend to use it":
- **Use now** — needed for Experiment 001.
- **Use later** — needed for the future constrained-generation experiment, not for baseline.
- **Reference** — read/consult only, no code or data copied.
- **Record only** — documented for provenance, not consumed directly.

---

## 1. Interslavic Dictionary PWA (sonic16x/interslavic)

| Field | Value |
|---|---|
| Name | Interslavic dictionary (PWA) |
| Repository | https://github.com/sonic16x/interslavic |
| Purpose | Community Interslavic dictionary web app; defines how dictionary data is produced and consumed. |
| License | MIT (`LICENSE.md`) |
| Version / tag / commit inspected | App version 1.31.11 (`package.json`); git HEAD `0fab0c5` |
| Relevant files | `src/consts.ts` (spreadsheet/sheet IDs, language list), `src/services/loadTablesData.ts` (Google Sheets fetcher), `src/services/generateDictionary.ts` (build script), `src/services/dictionary.ts` (word-form generation via `@interslavic/utils`), `src/services/dictionary-test` (snapshot tests) |
| How we intend to use it | **Reference + generated data.** We consume the *generated* dictionary data (`basic.json` on the live site), not the app code. The app code documents the exact data pipeline and metadata semantics. |
| Preservation strategy | Pin the generated data artifact (see item 11). Do not vendor the app. |
| Notes | The app itself is a React/Redux PWA with a Cloudflare worker API; none of that is needed. It depends on the **deprecated** `@interslavic/utils@3.4.0` for morphology (see item 4). |

## 2. Interslavic Dictionary fork (medzuslovjansky/slovnik)

| Field | Value |
|---|---|
| Name | Interslavic dictionary (org fork) |
| Repository | https://github.com/medzuslovjansky/slovnik |
| Purpose | Maintained fork of the dictionary app under the `medzuslovjansky` org; same code base, deployed at interslavic-dictionary.com. |
| License | MIT |
| Version / tag / commit inspected | Not cloned; identified via GitHub metadata during ecosystem survey. |
| Relevant files | — (same structure as item 1) |
| How we intend to use it | **Reference.** Confirms that the *actively maintained* dictionary codebase lives in the `medzuslovjansky` org. If the data pipeline changes, this is the repo to watch. |
| Preservation strategy | None required (no direct dependency). |
| Notes | The live site data we snapshot is produced by this lineage. The Task 005 audit additionally used its test-fixture snapshot `src/services/dictionary-test/basic.json` (master, 2026-07; copy at `data/dictionary/audit/slovnik/`, gitignored) as an independent earlier snapshot of the same lineage — it contributed 0 headword matches for the unresolved population. In Task 006 the EXP-002 pilot reads the same snapshot for exact/orthographic candidate evidence (attested `isv` surface + POS). Task 006.2: same-lineage snapshots are never promoted to canonical evidence; the canonical evaluator consumes only the `basic.json`/lexicon lineage (see `experiments/exp002-pilot/REPORT.md` §6). |

## 3. `@interslavic/utils` (legacy npm package)

| Field | Value |
|---|---|
| Name | @interslavic/utils |
| Repository | Published on npm; source lineage: sonic16x `interslavic` → refactored into `medzuslovjansky/js-utils` (item 5). |
| Purpose | Legacy JS morphology/dictionary-utils engine used by the dictionary app. |
| License | MIT |
| Version / tag / commit inspected | `3.4.0` (deprecated on npm; superseded by the `js-utils` monorepo) |
| Relevant files | dist bundle; exports: declension/conjugation functions, POS types (incl. `Preposition`), translit. |
| How we intend to use it | **Reference only.** Useful to explain historical parity targets and dictionary build behavior. Not a new dependency. |
| Preservation strategy | None. Replaced by `@interslavic/morphology` (item 5). |
| Notes | npm marks it deprecated. The Rust crate's parity harness compares against it byte-for-byte. |

## 4. `medzuslovjansky/js-utils` monorepo (active JS morphology)

| Field | Value |
|---|---|
| Name | Interslavic JS utilities (monorepo) |
| Repository | https://github.com/medzuslovjansky/js-utils |
| Purpose | Actively maintained morphological engine + linguistic utilities for Interslavic. |
| License | MIT |
| Version / tag / commit inspected | git HEAD `eca5154`; published packages: `@interslavic/morphology@0.1.2`, `@interslavic/inflect@0.1.1`, `@interslavic/translit@0.1.0`, `@interslavic/conllu@0.1.0`, `@interslavic/levenshtein@0.1.0` (+ stemmer/lunr) |
| Relevant files | `packages/morphology` (inflection, POS detection, derivation → CoNLL-U tokens), `packages/translit` (Latin⇄Cyrillic⇄Glagolitic⇄IPA), `packages/conllu` (token/feature conventions), `packages/levenshtein` (cross-Slavic lexical distance), `packages/stemmer` (script-agnostic stemmer + tokenizer), `docs/conllu-conventions.md`, `docs/hunspell.md`, `docs/removed.md`, `tools/dump` (full-paradigm dumper → TSV/CoNLL-U) |
| How we intend to use it | **Use now** (baseline evaluation) and **Use later** (constrained generation). The deterministic morphology engine (`@interslavic/morphology`) and translit are the core building blocks. |
| Task 002 usage | `@interslavic/morphology@0.1.2` + `@interslavic/translit@0.1.0` are pinned in `src/morphology_backend/package.json` (committed lockfile). The full-form lexicon is generated via the published `inflect()` API driven directly from `basic.json` rows — NOT via `tools/dump`, which is coupled to the monorepo's internal fixtures. |
| Preservation strategy | Pin exact npm versions in the evaluation environment; the package content is small enough to vendor later if npm access becomes an issue. MIT license permits vendoring. |
| Task 006 usage | The EXP-002 pilot derives `morphology_derived` candidates from the evaluator's B-fallback candidate lemmas that are canonical headwords, and records the JS engine's generated paradigm (via the full-form lexicon) as supporting evidence (`scripts/prepare_exp002_pilot.py`). |
| Notes | This is the *successor* to `@interslavic/utils`. The dictionary app still pins the old package; our project should use the new one. Verified locally: `more` → ins.sg. `morętem`/`morętom`; `dělati` produces the full paradigm incl. Long/Short present variants. |

## 5. `gold-silver-copper/interslavic` (Rust morphology)

| Field | Value |
|---|---|
| Name | Interslavic inflection library (Rust) |
| Repository | https://github.com/gold-silver-copper/interslavic |
| Purpose | Fast deterministic morphology engine (Rust) with dictionary-derived metadata. Explicit goal: parity with the JS implementation. |
| License | MIT OR Apache-2.0 (workspace `Cargo.toml`); no separate LICENSE file at root |
| Version / tag / commit inspected | git HEAD `599954b` (crate versions in `Cargo.toml`) |
| Relevant files | `crates/interslavic-core` (dependency-free rule engine; `noun.rs`, `verb.rs`, `adjective.rs`, `pronoun.rs`, `prepositions.rs`, `case_endings.rs`, `types.rs`), `crates/interslavic` (public API + embedded dictionary metadata), `crates/interslavic-extractor` (offline metadata generator from the dictionary TSV), `INTEGRATION.md` (downstream integration conventions), `xtask` (refresh/check/parity harness) |
| How we intend to use it | **Use later** (constrained generation) — a possible alternate/parallel morphology backend; **Reference now** — confirms the grammar rules and dictionary metadata semantics that the JS engine also implements. |
| Preservation strategy | Pin a git revision as a Cargo dependency, or treat as a submodule if used. Both licenses permit vendoring. |
| Notes | API follows the task's desired interface (`lemma + features → valid ISV form`), e.g. `noun_with`, `verb_with_present_hint`, `adj`, `pronoun`, `vocative`. The vocative is deliberately a standalone function (returns `None` for feminine consonant stems and neuters) — see `docs/GRAMMAR_AUDIT.md`. No Rust toolchain was available during this audit; analysis is static + documentation-based. |

## 6. `medzuslovjansky/interslavicfreq` (Python frequency/synonyms)

| Field | Value |
|---|---|
| Name | Interslavic frequency / intelligibility / synonym library (Python) |
| Repository | https://github.com/medzuslovjansky/interslavicfreq |
| Purpose | Word/text analysis: frequency, intelligibility (`razumlivost`), spellcheck, correctness, quality index, synonyms, `best_synonym()`. |
| License | MIT (`LICENSE.md`, Copyright (c) 2026 gorlatoff) |
| Version / tag / commit inspected | git HEAD `b84535b`; `pyproject.toml` requires Python ≥ 3.10 |
| Relevant files | `interslavicfreq/__init__.py` (public API), `interslavicfreq/synonyms.py` (Google-Sheet-driven synonym maps, pickle cache), `interslavicfreq/data/` (msgpack.gz frequency lists, `hunspell/isv.dic`, `isv.aff`), `pyproject.toml` (deps: `msgpack`, `regex`) |
| How we intend to use it | **Use now** (evaluation: candidate ranking / plausibility signal for suspicious forms) and **Use later** (constrained generation: synonym/frequency/intelligibility ranking). |
| Task 002 usage | **Not integrated into the baseline evaluator.** It remains a planned signal for ranking suspicious/unresolved forms; the core metrics deliberately do not depend on it (D-012, ROADMAP). |
| Preservation strategy | Pin via PyPI if published (verify), otherwise pin the git revision; vendoring permitted (MIT). The bundled frequency and Hunspell data are snapshotted assets — pin them separately. |
| Notes | Fork of `wordfreq`. The synonym maps derive from a Google Spreadsheet at build time; the shipped pickle/msgpack files are the frozen artifacts we actually consume. |
| Task 005 usage | Audit inputs acquired at the pinned revision (`b84535b`) under `data/dictionary/audit/` (gitignored): `data/frequency/small_isv{.x}.msgpack.gz` wordlists and `data/hunspell/isv.dic`/`isv.aff`. Synonyms/quality were NOT testable locally (runtime Google-Sheet fetch). |
| Task 006 usage | EXP-002 pilot candidate generation (`scripts/prepare_exp002_pilot.py`) reads the frozen wordlists again for exact-form/orthographic candidate evidence (attested surface + `cB` frequency recorded per candidate). |
| Task 006.2 finding | **Evaluator/resource discrepancy documented.** The canonical `isv-eval` evaluator never consumes this resource. Surfaces attested verbatim here (e.g. `seli`, `sedeli`, `reci`, `rekl`, `dejstvitelno`, `rekla`, `bojala`) were supplied as candidates and often adopted by the revising LLMs, but are invisible to the canonical evaluator (bucket C), producing no measurable coverage gain. The evidence does not judge which layer is right; see `experiments/exp002-pilot/REPORT.md` §6. No resource modified. |

## 7. `medzuslovjansky/isv_hunspell_dict`

| Field | Value |
|---|---|
| Name | Interslavic Hunspell dictionary builder |
| Repository | https://github.com/medzuslovjansky/isv_hunspell_dict |
| Purpose | Builds the Interslavic Hunspell dictionary (`isv.dic`/`isv.aff`) from an OpenCorporaXML dictionary; releases the spellchecker files. |
| License | MIT |
| Version / tag / commit inspected | Remote HEAD `fcf22a2` (not cloned) |
| Relevant files | Released artifacts: `isv.dic` + `isv.aff` (also vendored inside `interslavicfreq`) |
| How we intend to use it | **Use now** — the Hunspell `isv.dic` provides a ready-made list of accepted surface forms (a second, independent validity signal for the baseline evaluation, complementary to the morphology engine). |
| Task 002 usage | **Not yet integrated** — recorded as a future independent validity signal (ROADMAP "Future ideas"); the baseline uses the generated full-form lexicon + live morphology only. |
| Preservation strategy | Download the pinned release artifacts (or reuse the copies already bundled in `interslavicfreq`). No code needed. |
| Notes | MIT-licensed data; safe to snapshot. Used in the Task 005 cross-resource audit: 54 of the 1,050 unresolved forms are listed in `isv.dic` with full-form morphological tags (copy at `data/dictionary/audit/hunspell/`, gitignored). In Task 006 the EXP-002 pilot uses those attested surfaces + tags as alternative-resource candidates. Task 006.2 documented that the canonical evaluator does not consume `isv.dic` either: surfaces attested here (e.g. `dalše`) are supplied as candidates but stay bucket C in evaluation (see `experiments/exp002-pilot/REPORT.md` §6). |

## 8. Jan van Steenbergen — Interslavic grammar documentation

| Field | Value |
|---|---|
| Name | Interslavic grammar (official documentation) |
| Repository | https://steen.free.fr/interslavic/grammar.html (plus nouns/adjectives/verbs/pronouns/numerals/conjugator/declinator/orthography pages) |
| Purpose | The normative prose description of Interslavic grammar used for the consistency audit. |
| License | © Jan van Steenbergen. Site is freely readable; no explicit data license. **Treat content as copyright; do not redistribute wholesale.** |
| Version / tag / commit inspected | Live site fetched 2026-08-31 (plain-text conversions kept in audit workspace `/tmp`, not committed) |
| Relevant files | grammar.html, nouns.html, adjectives.html, verbs.html, pronouns.html, numerals.html, conjucator.html, declinator.html, orthography.html |
| How we intend to use it | **Reference.** Primary reference for the grammar audit and for evaluating morphological validity. |
| Preservation strategy | External reference only. If we ever need a frozen copy for reproducibility, store the fetched HTML/text under `data/reference/` with a date stamp — but keep it out of git until copyright is cleared. |
| Notes | Server misconfigured for HTTPS (HTTP only works). Contains a few internal tensions (e.g. the vocative appears in declension tables while the prose says it "is to be avoided" for feminine consonant stems and neuters) — see `docs/GRAMMAR_AUDIT.md`. |

## 9. Jan van Steenbergen — Interslavic dictionary (source data)

| Field | Value |
|---|---|
| Name | Interslavic dictionary (source of dictionary rows) |
| Repository | http://steen.free.fr/interslavic/dynamic_dictionary.html |
| Purpose | The lexical database behind the community dictionary. |
| License | **Unresolved.** The dictionary PWA uses it (MIT app), but the data's own license is not stated explicitly. Do not assume. |
| Version / tag / commit inspected | Live site referenced by the dictionary app's acknowledgements |
| Relevant files | — (online lookup; no static artifact observed) |
| How we intend to use it | **Reference.** Explains provenance of the dictionary content. |
| Preservation strategy | None until the license is clarified. |
| Notes | License status must be resolved before any redistribution of derived dictionary data. |

## 10. Google Spreadsheet (live dictionary source of truth)

| Field | Value |
|---|---|
| Name | Interslavic dictionary Google Spreadsheet |
| Repository | Spreadsheet ID `1N79e_yVHDo-d026HljueuKJlAAdeELAiPzdFzdBuKbY` (shared across sheets), referenced in `sonic16x/interslavic/src/consts.ts` |
| Purpose | The live editorial source the dictionary app fetches and transforms into `basic.json`. |
| License | **Unresolved** — content inherits the dictionary data license (see item 9). |
| Version / tag / commit inspected | Referenced in code; not fetched directly during the audit (the generated artifact was fetched instead) |
| Relevant files | Published CSV URLs per sheet |
| How we intend to use it | **Reference / Use later.** If we ever need to rebuild the dictionary data ourselves rather than snapshot the generated artifact, this is the feed. |
| Preservation strategy | Do not rely on it as a stable dependency. Snapshot the *generated* artifact instead (item 11). |
| Notes | Not versioned. The app is the transformation layer; we want its output, not its input. |

## 11. Generated dictionary artifact (`basic.json`)

| Field | Value |
|---|---|
| Name | Interslavic dictionary generated data |
| Repository | `https://interslavic-dictionary.com/data/basic.json` (generated by `sonic16x/interslavic` `generate-dictionary`) |
| Purpose | The consumable lexical dataset: `wordList` (19,101 rows) + `searchIndex`. |
| License | **Unresolved** (derived from items 9–10; the app that generates it is MIT, the data provenance is not stated). |
| Version / tag / commit inspected | Live snapshot fetched 2026-08-31, SHA-256 `512ebf0c…d1d0e` (recorded in `data/dictionary/manifest.json`) |
| Relevant files | `basic.json`; columns: `id, isv, addition, partOfSpeech, type, en, ru, be, uk, pl, cs, sk, sl, hr, sr, mk, bg, intelligibility` |
| How we intend to use it | **Use now.** This is the exact-match lexical reference for the baseline evaluation (`exact_dictionary_coverage`, headword lookup). |
| Task 002 usage | Snapshot + manifest implemented by `scripts/fetch_dictionary.py` (URL, retrieved_at, SHA-256, size, row count, schema, `license_status=UNRESOLVED`). The snapshot stays **out of git** (`.gitignore`); the manifest's content is embedded in every `isv-eval` report for reproducibility. |
| Task 006 usage | EXP-002 candidate generation uses `basic.json` as the canonical-dictionary source: headwords (plus `addition` variants) for orthographic-variant candidates and the canonical-lemma pool for morphology-derived candidates. |
| Task 006.2 finding | `basic.json`/lexicon is the **sole canonical evaluation source**: the evaluator never consumes alternative resources (hunspell, `interslavicfreq`, `slovnik`), which is exactly why EXP-002 candidates attested only in those resources were rejected. Task 006.2 recommends reconciling the resource layers under one documented policy before any larger experiment (see `experiments/exp002-pilot/REPORT.md` §6, §11). This snapshot was not modified. |
| Preservation strategy | **Snapshot locally** under `data/dictionary/basic.json` (+ SHA-256 manifest and fetch-date record) — done in Task 002. Because the data license is unresolved, the snapshot stays out of git until licensing is cleared; the provenance record is reproducible from the fetch script + manifest. This is the single most important reproducibility artifact. |
| Notes | `type` encodes word provenance: 1 = universal, 2 = predominantly, 3 = regionally, 4 = Church Slavonic, 5 = neologism, 9 = doubtful. `intelligibility` marks per-language `+`/`-`/`~`. Both are candidate-ranking inputs for the future experiment. |

## 12. Polish source story + model outputs (Experiment 001 inputs)

| Field | Value |
|---|---|
| Name | One complete Polish short story + seven LLM-generated Interslavic translations |
| Repository | Provided by the Project Owner (Task 003) in `opowiadania-set-isv/` — `op-pl.txt` (source) + `op-gpt.txt`, `op-gemini.txt`, `op-claude.txt`, `op-deepSeek.txt`, `op-bielik.txt`, `op-grok.txt`, `op-gpt-isvt.txt` |
| Purpose | The single source text for the baseline translation experiment and the seven unconstrained whole-story translations evaluated as separate conditions |
| License | Copyrighted literary work (source) and derived translations — for internal experimentation only; do not publish the source text or model outputs without clearing rights |
| Version / tag / commit inspected | Source SHA-256 `e3164ffc6a812640967ff749158db4746bea358cb4ac9c1532c214852b29e643` (10,827 bytes); per-output SHA-256 + size recorded in each run's `meta.json` |
| Relevant files | `opowiadania-set-isv/op-*.txt` (raw inputs, gitignored); copies + hashes in `experiments/exp001-baseline/outputs/<run_id>/` (gitignored) |
| How we intend to use it | **Use now** (Experiment 001 input). |
| Preservation strategy | Raw files stay out of git (`.gitignore`: `opowiadania-set-isv/`); registered under `experiments/exp001-baseline/input/source.txt` with `source.meta.json` (SHA-256, size, provision timestamp, preprocessing note). Run dirs hold byte-for-byte copies (`source.txt`, `output.txt`) plus hashes for reproducibility. |
| Notes | The supplied source file wraps the story in a markdown fence with an embedded Polish instruction line — documented in `source.meta.json`, not modified. See `experiments/exp001-baseline/DESIGN.md` and `docs/EXPERIMENTS.md`. |

## 13. Task 002 artifacts (our generated dependencies)

| Field | Value |
|---|---|
| Name | Full-form lexicon + Node morphology backend |
| Location | `data/dictionary/lexicon.tsv` (generated, gitignored) · `src/morphology_backend/` (committed) |
| Contents | `lexicon.tsv`: 320,824 rows `form\tlemma\txpos\tupos\tfeats\tentry_type` (headwords + generated paradigms), derived from `basic.json` via `@interslavic/morphology@0.1.2`. `backend.mjs`: line-delimited-JSON stdio service exposing `inflect` and `translit`. |
| License | Derived from dictionary data whose license is **UNRESOLVED** → lexicon stays out of git. Backend code is ours (MIT project). |
| Preservation strategy | Regenerate via `scripts/generate_lexicon.py` (records dictionary hash + morphology version in `lexicon.manifest.json`). Node deps pinned via committed `package-lock.json`. |
| Task 006 usage | The EXP-002 pilot's orthographic-variant candidates come from the lexicon's `ORTHOGRAPHIC_VARIANT` evidence (canonical surface forms reachable from a C-form by diacritic/fold normalization), and morphology-derived candidates use the prebuilt lemma→paradigm index. |

---

## Not used (surveyed, rejected or deferred)

| Project | Why not used now |
|---|---|
| UDPipe / UD tools (generic CoNLL-U) | No Interslavic UD model exists. Not needed for baseline; the JS morphology engine already emits CoNLL-U tokens. |
| `@interslavic/stemmer`, `@interslavic/lunr` | Search-index oriented; not needed for Experiment 001. Possible future idea (tokenization/search). |
| `@interslavic/levenshtein` | Cross-Slavic lexical distance; *Use later* for the constrained experiment's candidate ranking, not for baseline. |
| LibreOffice/Firefox spellchecker extensions | Distribution packaging of item 7; nothing for us to integrate. |

## Licensing status summary

| Asset | Status |
|---|---|
| App code (dictionary, js-utils, interslavicfreq, isv_hunspell_dict) | MIT (clear) |
| Rust morphology crate | MIT OR Apache-2.0 (clear) |
| Dictionary **data** (spreadsheet → basic.json) | **Unresolved — investigate before any redistribution** |
| Steen grammar pages | Copyrighted reference; cite, do not redistribute |
| Polish source story | Copyrighted; local-only, do not publish |
