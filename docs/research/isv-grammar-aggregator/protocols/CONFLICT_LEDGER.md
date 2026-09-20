# Conflict ledger

**Status:** ledger format + seeded unresolved conflicts from
`docs/GRAMMAR_AUDIT.md` (mirrored in `context/GRAMMAR_AUDIT.md`).
**Do not resolve conflicts merely for completeness.**

Related policy: `CONFLICT_POLICY.md`.

## Entry schema

```text
conflict_id
topic
domain                 taxonomy code
fact_A                 fact_id or provisional statement
fact_B                 fact_id or provisional statement
fact_other[]           optional
sources                source_ids / audit locations
temporal_interpretation synchronic | diachronic | unknown
current_status         conflicting | partially_documented | deferred
resolution_status      unresolved | operational_default_only | resolved
operational_default    optional packaging default (must be labeled default)
review_notes
opened_at
updated_at
```

`resolution_status=operational_default_only` means: we pick a Tier-C (or
documented) default for packages **without** claiming linguistic closure.

---

## Seed conflicts (unresolved)

### CL-001 — Vocative for feminine consonant stems / neuters

| Field | Value |
|---|---|
| topic | Vocative emission for f2 / neuter |
| domain | `noun.case.vocative` |
| fact_A | JS morphology emits vocative cells (e.g. patterns like `kosti` / `noču` per audit) |
| fact_B | Rust returns `None` (address with nominative); Steen prose says vocative to be avoided for these |
| sources | `docs/GRAMMAR_AUDIT.md` §Cases / Vocative; Steen grammar pages; JS vs Rust engines |
| temporal_interpretation | unknown (likely synchronic documentation tension) |
| current_status | conflicting |
| resolution_status | **unresolved** |
| operational_default | none yet — packages should show conflict if topic retrieved |
| review_notes | Steen tables vs prose internally tense per audit |

### CL-002 — Locative singular masculine/neuter alternates

| Field | Value |
|---|---|
| topic | Locative sg m/n: recommended `-u` vs documented `-ě`/`-i` |
| domain | `noun.case.locative` |
| fact_A | Engines generate recommended `-u` (aligned with dative) for m1/m2/n1 |
| fact_B | Steen documents alternative `-ě`/`-i` after hard/soft; not generated |
| sources | GRAMMAR_AUDIT §Cases / Locative singular |
| temporal_interpretation | unknown |
| current_status | partially_documented (`documented_optional` not generated) |
| resolution_status | **unresolved** (optional variant recorded, not closed) |
| operational_default | Tier-C `-u` labeled engine default if packaging nouns |

### CL-003 — Preposition government table

| Field | Value |
|---|---|
| topic | Structured preposition → case inventory |
| domain | `prep.case` |
| fact_A | JS: Preposition POS in dictionary; no case-government table |
| fact_B | Rust: curated `PREPOSITIONS` table from dictionary `(+N)` annotations |
| sources | GRAMMAR_AUDIT §Preposition / case relationships |
| temporal_interpretation | unknown |
| current_status | conflicting (representational / coverage) |
| resolution_status | **unresolved** |
| operational_default | none; Mode C may cite Rust table as Tier-A enrichment when available |

### CL-004 — Comparative / adjective degree coverage gaps

| Field | Value |
|---|---|
| topic | Synthetic comparatives in lexicon path vs community tags |
| domain | `adj.comparison` |
| fact_A | `inflect()` / lexicon path does not emit synthetic comparative cells (audit/RESOURCE_POLICY examples e.g. `dalše`) |
| fact_B | Hunspell may tag comparative surfaces; lemmas may be absent from canonical dictionary |
| sources | RESOURCE_POLICY disagreement examples; GRAMMAR_AUDIT adjective comparison notes |
| temporal_interpretation | unknown |
| current_status | morphology_coverage_gap + resource-layer difference |
| resolution_status | **unresolved** |
| operational_default | do not present Hunspell comparative tags as Tier-C |

### CL-005 — Homograph / tag traps in surface inventories

| Field | Value |
|---|---|
| topic | Surface attestation vs intended lemma (e.g. `seli`) |
| domain | lexical attestation |
| fact_A | Canonical/morphology path may miss or differ for a story form |
| fact_B | Hunspell/freq attest a surface with possibly unrelated stem tags |
| sources | RESOURCE_POLICY §2; LESSONS L-019 |
| temporal_interpretation | n/a |
| current_status | conflicting evidence classes |
| resolution_status | **unresolved** (policy: preserve layers; distrust pipeline tags) |
| operational_default | exact surface attestation only; ignore unreliable tags for facts |

### CL-006 — OOV morphology heuristics

| Field | Value |
|---|---|
| topic | Trust of POS/paradigm guesses for out-of-vocabulary lemmas |
| domain | morphology.oov |
| fact_A | `@interslavic/morphology` can emit heuristic paradigms for OOV |
| fact_B | Project decision: do not trust POS heuristics in evaluation (D-005) |
| sources | GRAMMAR_AUDIT “Needs further investigation”; D-005 |
| temporal_interpretation | n/a |
| current_status | deferred for fact seeding |
| resolution_status | **unresolved** — operational ban on treating OOV heuristics as normative |
| operational_default | exclude OOV heuristic outputs from accepted rules |

---

## Maintenance

New disagreements discovered during intake **must** add a `CL-###` entry
before accepting either side as sole `current_preferred`.
