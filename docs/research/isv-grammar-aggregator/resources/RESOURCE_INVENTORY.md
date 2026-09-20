# Resource inventory — inputs to a future Grammar Aggregator

**Status:** design inventory derived from existing project documentation
(`SOURCES.md`, `docs/RESOURCE_POLICY.md`, `docs/GRAMMAR_AUDIT.md`,
`data/dictionary/README.md`).  
**Licenses:** recorded only as documented; nothing invented.  
**Do not assume equal authority.**

Direct contribution = may become a structured fact in the aggregator.  
Supporting evidence only = may appear as attestation/conflict context, never
as silent upgrade to canonical status.

---

## 1. Canonical Interslavic dictionary (`basic.json` lineage)

| Field | Record |
|---|---|
| Name | Live dictionary JSON / PWA data lineage |
| Path / repository | Live URL `interslavic-dictionary.com/data/basic.json`; local snapshot `data/dictionary/basic.json` (gitignored); apps: `sonic16x/interslavic`, fork `medzuslovjansky/slovnik` |
| Resource type | Lexical headword dictionary |
| Language layer | Canonical dictionary (RESOURCE_POLICY) |
| Contents | ~19,100 rows: headwords, `addition` variants, POS, `type` 1–9, per-language glosses (incl. Polish) |
| Machine / human | Machine-readable JSON |
| Current status | Snapshottable; used by evaluator + EXP-003 scaffold; **data license UNRESOLVED** |
| License | App code MIT; **data license unresolved** (`SOURCES.md` §9–11; D-009) |
| Strengths | Project’s sole canonical lexical layer; Polish column enables reverse index |
| Limitations | No inflection; `type=9` / neologisms present; license blocks redistribution |
| Aggregator role | **Direct** for lexical lemma/POS/aspect metadata; **not** a full grammar |

---

## 2. Generated full-form lexicon (`lexicon.tsv`)

| Field | Record |
|---|---|
| Name | Full-form lexicon |
| Path | `data/dictionary/lexicon.tsv` (+ `lexicon.manifest.json`; gitignored) |
| Resource type | Generated paradigm inventory |
| Language layer | Canonical dictionary + morphology |
| Contents | ~320k `form ↔ lemma ↔ POS ↔ feats` rows from `inflect()` over `basic.json` |
| Machine / human | Machine-readable TSV |
| Current status | Regenerable; evaluator bucket A basis |
| License | Derived from unresolved dictionary data → stays local |
| Strengths | Deterministic surface↔lemma lookup; paradigm examples for packages |
| Limitations | Only what `inflect()` emits (documented gaps: e.g. some pasts, no synthetic comparatives via that path) |
| Aggregator role | **Direct** for lexical paradigm evidence and example forms |

---

## 3. `@interslavic/morphology` / `medzuslovjansky/js-utils`

| Field | Record |
|---|---|
| Name | Active JS morphology engine |
| Path / repository | https://github.com/medzuslovjansky/js-utils ; pinned in `src/morphology_backend/` (`@interslavic/morphology@0.1.2`, related packages) |
| Resource type | Computational morphology / rule engine |
| Language layer | Morphological rules (computational) |
| Contents | Inflection, POS detection, derivation → CoNLL-U-ish tokens; translit sibling package |
| Machine / human | Machine-readable API |
| Current status | **Preferred live engine** (D-001); stdio backend |
| License | MIT (packages) |
| Strengths | Faithful implementation of Steen rules per GRAMMAR_AUDIT; project production path |
| Limitations | Coverage gaps; OOV heuristics must not be trusted as normative (D-005; GRAMMAR_AUDIT) |
| Aggregator role | **Direct** for generated paradigms and engine-backed rule operationalization |

---

## 4. Legacy `@interslavic/utils@3.4.0`

| Field | Record |
|---|---|
| Name | Deprecated dictionary-app morphology utils |
| Path / repository | npm `@interslavic/utils@3.4.0`; historically used by `sonic16x/interslavic` |
| Resource type | Legacy morphology engine |
| Language layer | Morphological rules (legacy) |
| Contents | Same family of paradigms; superseded |
| Machine / human | Machine-readable |
| Current status | **Do not use for new work** (D-001); parity reference only |
| License | As published on npm (project treats as superseded) |
| Strengths | Historical baseline for Rust parity harness |
| Limitations | Deprecated; representational differences vs Rust already audited |
| Aggregator role | **Supporting / historical** only — cite via GRAMMAR_AUDIT, do not ingest as primary |

---

## 5. Rust morphology (`gold-silver-copper/interslavic`)

| Field | Record |
|---|---|
| Name | Rust Interslavic morphology crate |
| Path / repository | `gold-silver-copper/interslavic` (HEAD audited `599954b`) |
| Resource type | Alternate morphology implementation |
| Language layer | Morphological rules (alternate) |
| Contents | Same rule engine family; explicit APIs for vocative `Option`, pronoun styles, preposition government table |
| Machine / human | Machine-readable (Rust) |
| Current status | **Use later / reference now** (D-003); not required in current env (no toolchain) |
| License | MIT OR Apache-2.0 |
| Strengths | High JS parity; clearer modeling of some optional/avoided forms; curated preposition–case table |
| Limitations | Not runnable here; JS↔Rust representational disagreements (vocative) are real |
| Aggregator role | **Supporting evidence** for conflict records and preposition–case facts; optional future backend |

---

## 6. Hunspell `isv.dic` / `isv.aff`

| Field | Record |
|---|---|
| Name | Full-form Hunspell inventory |
| Path / repository | `medzuslovjansky/isv_hunspell_dict`; vendored in `interslavicfreq` `data/hunspell/`; local `data/dictionary/audit/hunspell/` (gitignored); pin `b84535b` |
| Resource type | Surface-form spelling inventory |
| Language layer | Alternative resource |
| Contents | ~500k+ distinct surfaces; pipeline tags; ICONV/REP; **no productive affix generation** (enumeration) |
| Machine / human | Machine-readable |
| Current status | Evidence tier in evaluator; broader coverage |
| License | MIT (documented lineage) |
| Strengths | Independent surface attestation |
| Limitations | Tags often artifactual (L-019); not morphological proof; not canonical |
| Aggregator role | **Supporting evidence only** |

---

## 7. `medzuslovjansky/interslavicfreq`

| Field | Record |
|---|---|
| Name | Interslavic frequency / community lexical package |
| Path / repository | https://github.com/medzuslovjansky/interslavicfreq ; local frequency msgpacks under `data/dictionary/audit/frequency/` |
| Resource type | Frequency wordlists (+ runtime synonym tooling) |
| Language layer | Alternative resource |
| Contents | Surface → cB frequency; also ships Hunspell data |
| Machine / human | Machine-readable wordlists |
| Current status | Broader-tier attestation; synonyms not used (live Sheet) |
| License | Package MIT; synonym Sheet content not frozen here |
| Strengths | Large attestation set; explains many canonical-C forms |
| Limitations | Homographs; no lemma/paradigm; frequency ≠ correctness |
| Aggregator role | **Supporting evidence only** |

---

## 8. `medzuslovjansky/slovnik` snapshot

| Field | Record |
|---|---|
| Name | Slovnik dictionary-app fork / test fixture |
| Path / repository | https://github.com/medzuslovjansky/slovnik ; local `data/dictionary/audit/slovnik/basic.json` |
| Resource type | Historical dictionary snapshot (same lineage) |
| Language layer | Historical reference |
| Contents | Same schema family as `basic.json` (~18k rows in fixture) |
| Machine / human | Machine-readable |
| Current status | Provenance-only in evidence layer; **0 independent weight** for unresolved population (Task 005) |
| License | App MIT; data inherits unresolved dictionary status |
| Strengths | Lineage archaeology |
| Limitations | Not an independent witness (RESOURCE_POLICY) |
| Aggregator role | **Supporting / historical provenance only** |

---

## 9. Steen / official Interslavic grammar documentation

| Field | Record |
|---|---|
| Name | Jan van Steenbergen Interslavic grammar pages |
| Path / repository | https://steen.free.fr/interslavic/grammar.html (+ nouns, adjectives, verbs, pronouns, numerals, orthography, conjugator/declinator) |
| Resource type | Normative educational prose + tables |
| Language layer | Educational / reference (normative intent) |
| Contents | Case/gender/number/animacy, declension, conjugation, participles, prepositions, orthography, optional variants |
| Machine / human | Human-readable HTML |
| Current status | Primary reference for `docs/GRAMMAR_AUDIT.md`; **not ingested wholesale** |
| License | © Jan van Steenbergen; freely readable; **no explicit data license — cite, do not redistribute wholesale** (`SOURCES.md` §8) |
| Strengths | Best available normative description; documents optional variants and internal prose/table tensions (e.g. vocative) |
| Limitations | Not machine-readable; copyright; some internal inconsistencies (GRAMMAR_AUDIT) |
| Aggregator role | **Direct** for rule statements **via curated, cited excerpts / paraphrases with location**, never as a bulk dump |

---

## 10. Project grammar audit

| Field | Record |
|---|---|
| Name | Grammar Consistency Audit |
| Path | `docs/GRAMMAR_AUDIT.md` |
| Resource type | Project meta-resource (comparative audit) |
| Language layer | Cross-layer analysis |
| Contents | Steen vs JS vs Rust feature matrix; discrepancy catalog |
| Machine / human | Human-readable (structured tables) |
| Current status | Authoritative project record of known agreements/disagreements |
| License | Project documentation |
| Strengths | Already encodes conflict loci the aggregator must preserve |
| Limitations | Snapshot in time; not a generator |
| Aggregator role | **Direct** seed for conflict/status annotations |

---

## 11. Community / educational materials (reference-only)

| Field | Record |
|---|---|
| Name | Community courses / sites (Interslavic.fun, forum courses, LibreLingo, Sekyra, etc.) |
| Path | Listed under `SOURCES.md` §13 as reference |
| Resource type | Informal / educational |
| Language layer | Community / informal |
| Contents | Pedagogy, examples, orthography notes |
| Machine / human | Mostly human-readable |
| Current status | Reference only; not license-cleared for ingestion |
| License | Typically copyrighted / unclear — **do not ingest** under current policy |
| Strengths | Pedagogical examples |
| Limitations | Informal; provenance weak for a scientific aggregator |
| Aggregator role | **Supporting / cite-only** if ever used; default **exclude from machine KB** |

---

## 12. Project orthography / evaluator stack (diagnostic, not grammar authoring)

| Field | Record |
|---|---|
| Name | `isv-eval` + orthography modules |
| Path | `src/isv_eval/` (`metrics.py`, `orthography.py`, `evidence.py`, …) |
| Resource type | Evaluation / diagnostic tooling |
| Language layer | Project measurement |
| Contents | Canonical/broader coverage; outside-inventory character audit; evidence provenance |
| Machine / human | Machine-readable |
| Current status | Production evaluator |
| License | Project code |
| Strengths | Defines what “improvement” can mean experimentally |
| Limitations | Coverage ≠ quality; must not become a silent rewrite engine |
| Aggregator role | **Consumer** of aggregator outputs in experiments; may supply **diagnostic constraints** (Mode C), not normative rules |

---

## Inventory summary

| Contribute directly | Supporting evidence only | Exclude / cite-only by default |
|---|---|---|
| Steen (curated cited rules) | Hunspell surfaces | Community informal sites (bulk) |
| `@interslavic/morphology` + lexicon | `interslavicfreq` | Live synonym Sheets |
| `basic.json` lemma/POS/aspect metadata | `slovnik` historical | Unpinned web scrapes |
| `GRAMMAR_AUDIT.md` conflict seeds | Rust preposition table / vocative modeling | OOV morphology heuristics as “rules” |
| Resource-policy evidence classes | Legacy utils (historical) | — |
