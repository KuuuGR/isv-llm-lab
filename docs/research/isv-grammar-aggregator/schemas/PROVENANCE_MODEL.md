# Provenance model — Grammar Aggregator

**Status:** proposed minimal schema. No production database yet.

## Requirement

> No grammar rule should become an unexplained fact with lost provenance.

The system must answer:

1. Where did this rule/form come from?
2. Are there alternative forms or conflicting sources?

This extends the form-level evidence model in `docs/RESOURCE_POLICY.md` §4
to **rules, paradigms, diagnostics, and packages**.

---

## Core record: `GrammarFact`

Minimal fields (JSON-shaped; implementation deferred):

```text
fact_id              stable id (e.g. ga:noun.loc.sg.m1.default)
domain               taxonomy code (see GRAMMAR_TAXONOMY.md)
fact_kind            rule | lexical_paradigm | evidence_example | diagnostic
statement            short human-readable claim
formal_pattern       optional compact pattern / template
source               resource key (steen_grammar | morphology_js | lexicon |
                     basic_json | hunspell | interslavicfreq | slovnik |
                     grammar_audit | rust_morphology | …)
source_version       pin / npm version / git SHA / retrieval date / URL etag
source_location      page path, section heading, file:line, lemma id, …
resource_tier        N | C | A | S | H | X
status               canonical | accepted_variant | attested_variant |
                     historical | uncertain | conflicting |
                     documented_optional | documented_avoid |
                     morphology_coverage_gap | unsupported
confidence           high | medium | low | unknown
                     (epistemic label — not a statistical CI)
examples             list of {surface, lemma?, feats?, note?}
variants             list of related fact_ids or inline alt statements
conflict_group_id    optional link among disagreeing facts
applies_when         optional retrieval predicates (POS, case need, …)
notes                free text; must record known caveats
created_at           ISO date of aggregator entry
review_state         draft | reviewed | blocked
```

### Kind semantics (do not collapse)

| `fact_kind` | Meaning |
|---|---|
| `rule` | General morphological/syntactic pattern |
| `lexical_paradigm` | Lemma-linked inflection set / selected cells |
| `evidence_example` | Attested surface or cited illustrative form |
| `diagnostic` | Constraint for checking/repairing a candidate |

---

## Package provenance

Every LLM context package should carry a header:

```text
package_id
mode                 A | B | C
source_text_hash     Polish source (or candidate ISV) hash
retrieved_fact_ids   list
excluded_conflicts   summary of conflict_group_ids shown/omitted
builder_version      future retrieval code version
generated_at
```

So a later auditor can ask: *what exact evidence did the model see?*

---

## Provenance rules

1. **Cite or do not assert.** A Tier-N rule without `source_location` is
   invalid for packaging.
2. **Pin versions.** Morphology facts must record
   `@interslavic/morphology` version; dictionary facts the
   `basic.json` SHA from `manifest.json` when available.
3. **Separate observation from interpretation.** “Engine emits X” is an
   observation; “X is preferred ISV” is an interpretation requiring Tier-N
   or explicit project decision.
4. **Conflicts stay linked.** Resolving a conflict requires a new reviewed
   fact with `notes` explaining *why*, not deletion of losers.
5. **License wall.** Facts derived from unresolved-license dictionary data
   remain local; packages used in public papers must respect
   redistribution limits (describe method; do not dump proprietary rows).

---

## Example (illustrative only)

```text
fact_id:        ga:verb.1sg.present.double
domain:         verb.person_number
fact_kind:      rule
statement:      "1sg present may appear as -u/-ju or alternate -em/-im"
source:         steen_grammar + morphology_js
source_location: Steen verbs page (present endings); JS emits both cells
resource_tier:  N+C
status:         accepted_variant
examples:       [dělajų/dělam, …]   # from engine/lexicon, not invented
conflict_group: none (documented dual allowance)
```

```text
fact_id:        ga:noun.voc.f2.js_vs_rust
domain:         noun.case.vocative
fact_kind:      rule
statement:      "Engines disagree on emitting vocatives for f2/neuter"
source:         grammar_audit
source_location: docs/GRAMMAR_AUDIT.md §Cases / Vocative
resource_tier:  N+C+A
status:         conflicting
variants:       js_emits_cell | rust_returns_none | steen_prose_avoid
```
