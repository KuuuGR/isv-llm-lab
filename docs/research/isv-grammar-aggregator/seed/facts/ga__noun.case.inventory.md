---
fact_id: "ga:noun.case.inventory"
domain: "noun.case"
fact_kind: "rule"
statement: "Noun paradigms are described with seven case labels (Nom Acc Gen Dat Ins Loc Voc); Steen notes vocative is not a “real case” in the same sense (singular; masc/fem; not for adjectives/pronouns)."
formal_pattern: null
source: "grammar_audit"
source_ids:
- "src:grammar_audit"
primary_source_id: "src:grammar_audit"
source_version: "docs/GRAMMAR_AUDIT.md"
source_location: "docs/GRAMMAR_AUDIT.md §Cases / Case inventory"
observation_ids:
- "obs:ga:noun.case.inventory"
resource_tier: "N"
status: "canonical"
confidence: "high"
examples: []
variants: []
conflict_group_id: null
conflict_ledger_id: null
valid_from: "unknown"
valid_to: "open"
status_at_time: "current_preferred"
chronology_confidence: "unknown"
historical_notes: null
review_state: "accepted"
reviewed_by: "seed-curation-2026-09-20"
reviewed_at: "2026-09-20"
acceptance_basis: "normative"
applies_when: null
package_eligibility: true
seed_from_project_audit: true
license_notes: "Steen: © cite-only (no wholesale copy). Dictionary data license UNRESOLVED where referenced. JS morphology MIT; Rust MIT OR Apache-2.0 per SOURCES.md/RESOURCE_POLICY. Hunspell MIT lineage when cited."
isv_eval_implications: "JS lexicon may include vocative surfaces; Rust-style checks would differ (CL-001)."
llm_guidance: "Use the core six cases in syntax; treat vocative as address morphology, not adjective agreement."
schema_version: "ga-fact-0.1"
created_at: "2026-09-20"
updated_at: "2026-09-20"
---
## Observation

Audit: Steen 7 cases; JS emits Voc cell; Rust 6-Case enum + optional vocative().

## Interpretation

Shared inventory; vocative API differs (see conflict facts).

## Notes

_none_
