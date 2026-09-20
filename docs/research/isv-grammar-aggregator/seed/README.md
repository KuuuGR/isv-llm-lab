# Initial reviewed GrammarFact seed

**Created:** 2026-09-20  
**Schema:** `ga-fact-0.1` (`../schemas/FACT_SCHEMA.md`)  
**Storage:** Option D — human-review Markdown+YAML cards + generated JSON  
**External research:** none (project-internal sources only)

## Layout

```text
seed/
├── README.md              (this file)
├── facts/                 (one card per fact)
└── generated/
    └── facts.json         (structured export of all cards)
```

## Counts

| Review state | Count |
|---|---:|
| `accepted` | **47** |
| `needs_review` | **1** |
| **Total** | **48** |

Target band was 20–50 accepted facts: **met** (47 accepted).

| `fact_kind` | Count |
|---|---:|
| `rule` | 36 |
| `diagnostic` | 12 |
| `lexical_paradigm` | 0 |
| `evidence_example` | 0 |

No `lexical_paradigm` / `evidence_example` cards were forced: this seed is rule- and diagnostic-heavy because `GRAMMAR_AUDIT.md` and `RESOURCE_POLICY.md` document patterns and evaluator limits, not lemma-by-lemma paradigm dumps (also constrained by dictionary **UNRESOLVED** license).

## Sources used

| Source | Role |
|---|---|
| `docs/GRAMMAR_AUDIT.md` | Primary linguistic/computational agreement & conflict evidence |
| `docs/RESOURCE_POLICY.md` | Evaluator limits, disagreement examples, non-proofs |
| Conflict ledger CL-001…006 | Linked from relevant facts |
| Pinned engine versions cited in audit | `@interslavic/morphology@0.1.2`; Rust HEAD `599954b` |

**Not used:** Wikipedia, YouTube, Steen HTML scrape, Hunspell bulk, any web fetch.

## Licensing

- Steen: **© cite-only** — facts paraphrase via the project audit; no wholesale grammar text.
- Dictionary data: **UNRESOLVED** — no row dumps; aspect/headword existence cited only where the audit/policy already state it.
- Hunspell: MIT lineage — **single illustrative surfaces** from RESOURCE_POLICY only.
- JS morphology MIT; Rust MIT OR Apache-2.0 (as documented).

## Conflict coverage (unresolved preserved)

| Ledger | Seed facts |
|---|---|
| CL-001 vocative f2/neuter | `ga:noun.voc.f2_neuter.conflict` |
| CL-002 locative alternates | `ga:noun.loc.sg.mn.default_u`, `ga:noun.loc.sg.mn.optional_e_i` |
| CL-003 prep government table | `ga:prep.case.table.js_vs_rust`, related prep facts |
| CL-004 comparative gaps | `ga:adj.comparison.*`, `ga:adj.comparison.lexicon_gap_dalše` |
| CL-005 homographs / tags | `ga:verb.sesti.past_gap`, `ga:diag.hunspell.tags_untrusted` |
| CL-006 OOV heuristics | `ga:diag.oov.heuristics_untrusted` |

## Domain balance (approximate)

| Area | Coverage in this seed |
|---|---|
| Noun / adjective morphology | Strong (classes, animacy, locative, vocative, adj endings/comparison) |
| Verb morphology | Strong (stems, 1sg variants, tense/mood, aspect, irregulars, participles) |
| Pronouns / number | Moderate (personal n-, reflexive, possessives, dual avoid, demonstratives) |
| Preposition + case | Moderate (high-level rule + JS/Rust table conflict + Mode C note) |
| Orthography / evaluator diagnostics | Strong relative to seed size |
| Word formation / derivation | Thin (hard/soft o/e–y/i; fleeting vowels sit under noun declension) |

## Quality checks performed

1. Every fact has provenance fields (`source*`, `observation_ids`, audit location).
2. Facts map to GRAMMAR_AUDIT / RESOURCE_POLICY (no memory-only Slavic analogy).
3. Conflicts preserved (`conflicting` / ledger links), not resolved for cleanliness.
4. Historical/archaic wording not promoted to dated `current_preferred` without evidence (`ga:noun.athematic.archaic_label` = `needs_review`).
5. Licensing limitations recorded on cards.
6. No large source passages copied.
7. Unique `fact_id`s; cards ↔ `generated/facts.json` emitted together.
8. `isv_eval_implications` and compact `llm_guidance` present where package-eligible.
9. Evaluator **not** modified.

## Research assessment

### How many facts were successfully accepted?
**47** accepted; **1** needs_review.

### Which domains are well covered?
Noun declension/case (including known conflicts), core verb conjugation/tense, adjective basics, evaluator/orthography diagnostics tied to RESOURCE_POLICY.

### Which domains are weak?
- Full **lexical_paradigm** cards (license + no bulk lexicon dump).
- Detailed **prep→case** inventories (JS gap; Rust table not runnable here).
- **Derivation/productivity** beyond hard/soft and fleeting vowels.
- **Numerals**, syntax beyond prep/pronoun notes.
- Rich **evidence_example** attestations from corpora.

### Which conflicts remain unresolved?
All seeded ledger items CL-001–CL-006 remain **unresolved**; seed represents them, does not close them.

### Which resources contributed the most facts?
1. `GRAMMAR_AUDIT.md`  
2. `RESOURCE_POLICY.md` (diagnostics / gaps)  
3. Conflict ledger (linkage only)

### What cannot yet be represented reliably?
- Calendar-dated “current vs archaic” preference without Steen retrieval dates beyond audit prose.
- Exhaustive government tables without ingesting Rust/dictionary annotations under license constraints.
- Lemma-level paradigms without a license-cleared lexicon export policy.
- Community usage frequency as normative preference.

### Is the schema adequate?
**Mostly yes** for rule/diagnostic seeds. Exposed design frictions (document, do not paper over):

1. **`morphology_coverage_gap` overloaded** for evaluator matching limits (e.g. `sedeli`) vs true engine non-generation (`sěsti` past)—may need a distinct `evaluator_matching_limit` status later.
2. **`documented_avoid` vs `deferred`** used for “do not generate dual” vs “not a packaging rule”—works but overlapping.
3. **`lexical_paradigm` / `evidence_example` kinds unused**—schema supports them; seed could not populate safely without lexicon dumps.
4. **`status_at_time: current_preferred`** applied cautiously to high-agreement engine+audit rules; still weaker than a dated normative edition pin.
5. Card format is Markdown+YAML front matter; a future generator should validate required keys rather than trusting hand edits.

## Regeneration note

Cards and `generated/facts.json` were produced together in the curation pass. If cards are edited by hand, regenerate JSON from cards (future tool) or re-export deliberately—do not let them drift silently.

## Non-goals (still)

No retrieval implementation, no LLM runs, no `isv-eval` changes, no EXP-004 changes, no external intake.
