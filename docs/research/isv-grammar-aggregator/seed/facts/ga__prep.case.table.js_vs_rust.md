---
fact_id: "ga:prep.case.table.js_vs_rust"
domain: "prep.case"
fact_kind: "diagnostic"
statement: "JS exposes Preposition POS without a case-government table; Rust provides a curated PREPOSITIONS table from dictionary (+N) annotations (single-word; multi-word/particles excluded)."
formal_pattern: null
source: "grammar_audit"
source_ids:
- "src:grammar_audit"
primary_source_id: "src:grammar_audit"
source_version: "Rust HEAD 599954b; morphology@0.1.2"
source_location: "docs/GRAMMAR_AUDIT.md §Preposition / case relationships"
observation_ids:
- "obs:ga:prep.case.table.js_vs_rust"
resource_tier: "A"
status: "conflicting"
confidence: "high"
examples: []
variants: []
conflict_group_id: "cg:prep.table"
conflict_ledger_id: "CL-003"
valid_from: "unknown"
valid_to: "open"
status_at_time: "unknown"
chronology_confidence: "unknown"
historical_notes: null
review_state: "accepted"
reviewed_by: "seed-curation-2026-09-20"
reviewed_at: "2026-09-20"
acceptance_basis: "computational"
applies_when: null
package_eligibility: true
seed_from_project_audit: true
license_notes: "Steen: © cite-only (no wholesale copy). Dictionary data license UNRESOLVED where referenced. JS morphology MIT; Rust MIT OR Apache-2.0 per SOURCES.md/RESOURCE_POLICY. Hunspell MIT lineage when cited."
isv_eval_implications: "Not required for baseline A/B/C; useful for Mode C later."
llm_guidance: "Detailed prep→case lists are incomplete on the JS Tier-C path; use dictionary sense notes / future Tier-A data."
schema_version: "ga-fact-0.1"
created_at: "2026-09-20"
updated_at: "2026-09-20"
---
## Observation

⚠️ JS none; Rust curated table.

## Interpretation

Unresolved representational conflict; Rust = Tier-A enrichment candidate.

## Notes

_none_
