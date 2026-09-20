# Resource hierarchy — Grammar Aggregator

**Status:** design proposal derived from `docs/RESOURCE_POLICY.md`,
`docs/GRAMMAR_AUDIT.md`, `SOURCES.md`, and decisions D-001–D-003, D-009,
D-022.  
**Not validated experimentally.**

## Design principle

The aggregator inherits the project’s central policy:

> Canonical resource coverage is **not** identical to proof that a form is
> correct Interslavic. Alternative resources may provide useful evidence
> without automatically becoming canonical.

Therefore hierarchy is about **evidence strength and role**, not about
declaring a single absolute truth.

---

## Proposed tiers

These labels are aggregator-facing; they map onto RESOURCE_POLICY vocabulary.

### Tier N — Normative reference (human)

| Item | Role |
|---|---|
| Steen grammar documentation (cited locations) | Normative *intent* and optional-variant prose |
| `docs/GRAMMAR_AUDIT.md` | Project-verified comparison notes |

**Use:** author rule statements and mark documented optionality.  
**Do not:** bulk-ingest HTML into prompts or treat every table cell as
mandatory ISV.

### Tier C — Canonical computational (project evaluation spine)

| Item | Role |
|---|---|
| `basic.json` headwords / additions | Canonical lemmas and lexical metadata |
| `@interslavic/morphology` (+ generated `lexicon.tsv`) | Canonical inflection generation path |

**Use:** default facts for Mode B lexical packages and for alignment with
`isv-eval` canonical coverage.  
**Do not:** pretend engine coverage gaps are linguistic impossibilities
(L-020).

### Tier A — Alternate computational (independent implementation)

| Item | Role |
|---|---|
| Rust morphology (when available) | Parity / representational alternate |
| Rust `prepositions.rs` government table | Independent structured case-government evidence |

**Use:** conflict detection and richer diagnostic packages.  
**Do not:** silently override Tier C in evaluation metrics.

### Tier S — Supporting surface attestation

| Item | Role |
|---|---|
| Hunspell `isv.dic` exact surfaces | Broader-tier attestation |
| `interslavicfreq` exact surfaces | Broader-tier attestation + frequency signal |

**Use:** Mode B/C “also attested” notes; never promote into canonical A/B.  
**Do not:** trust pipeline morphological tags as gold annotation (L-019).

### Tier H — Historical / same-lineage

| Item | Role |
|---|---|
| `slovnik` snapshot | Lineage archaeology / provenance only |

**Use:** optional `historical_evidence` flag.  
**Do not:** give independent weight (RESOURCE_POLICY §5).

### Tier X — Excluded from machine KB by default

Community informal sites, unpinned scrapes, live Google Sheets, OOV
heuristic POS guesses.

**Use:** human bibliography only unless separately licensed and curated.

---

## Mapping to RESOURCE_POLICY layers

| RESOURCE_POLICY layer | Aggregator tier |
|---|---|
| Educational / reference (Steen) | N |
| Canonical dictionary | C (lexical) |
| Morphological rules (JS) | C (morphology) |
| Morphological rules (Rust) | A |
| Alternative resources | S |
| Historical reference (`slovnik`) | H |
| Community informal | X |

---

## What happens when two resources disagree?

**Rule (binding for this design):**

1. **Preserve both** (or all) statements as sibling evidence records linked
   by a shared `conflict_group_id`.
2. **Do not majority-vote.** Surface count in Tier S does not outvote Tier C
   or Tier N.
3. Assign an explicit status (`protocols/CONFLICT_POLICY.md`): e.g. `canonical`,
   `accepted_variant`, `attested_variant`, `engine_optional`,
   `documented_avoid`, `conflicting`, `uncertain`, `unsupported`.
4. Prefer **descriptive packaging** to the LLM: show the recommended /
   default form *and* note alternatives when the sources document them
   (e.g. 1sg `-u` vs `-em`; JS vocative cell vs Rust `None`).
5. For evaluation alignment, **canonical metrics remain Tier-C-defined**.
   Broader metrics may mention Tier-S attestation separately.
6. When Steen prose and Steen tables disagree (vocative), mark
   `source_internal_tension: true` and cite GRAMMAR_AUDIT — do not invent
   a resolution.

### Worked examples (already known)

| Conflict | Representation |
|---|---|
| JS emits f2 vocative `kosti`; Rust returns `None`; Steen prose says avoid | Status `conflicting` / `documented_avoid` + both engine outputs |
| Locative m/n recommended `-u`; alternates `-ě/-i` documented but not generated | Default `canonical`/`engine_default` + variant `documented_optional_not_generated` |
| Form in Hunspell/freq but missing from lexicon | Tier S `attested_variant` / `resource_only`; canonical path empty |
| Lemma in `basic.json` but form not generated (`sěsti` past) | `morphology_coverage_gap` — not “illegal ISV” |

---

## Relation to EXP-003 D

EXP-003 D already used Tier-C POS/aspect + a few lexicon example forms.
The hierarchy above is compatible: D was a **thin consumer** of Tier C.
The aggregator proposes to make Tier N/A/S conflicts **first-class**,
which D did not.
