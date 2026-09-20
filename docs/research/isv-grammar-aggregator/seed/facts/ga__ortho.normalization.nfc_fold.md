---
fact_id: "ga:ortho.normalization.nfc_fold"
domain: "ortho.inventory"
fact_kind: "diagnostic"
statement: "Normalization uses NFC+lowercase primary keys; etymological folding is secondary. Folded matches are orthographic variants (flagged), not silent exact matches."
formal_pattern: null
source: "resource_policy"
source_ids:
- "src:resource_policy"
primary_source_id: "src:resource_policy"
source_version: "docs/RESOURCE_POLICY.md §3; D-014"
source_location: "docs/RESOURCE_POLICY.md §3; decisions D-014"
observation_ids:
- "obs:ga:ortho.normalization.nfc_fold"
resource_tier: "C"
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
acceptance_basis: "computational"
applies_when: null
package_eligibility: true
seed_from_project_audit: true
license_notes: "Steen: © cite-only (no wholesale copy). Dictionary data license UNRESOLVED where referenced. JS morphology MIT; Rust MIT OR Apache-2.0 per SOURCES.md/RESOURCE_POLICY. Hunspell MIT lineage when cited."
isv_eval_implications: "Defines A vs variant bookkeeping."
llm_guidance: "Prefer standard etymological spelling; folded near-matches are variants, not free diacritic deletion."
schema_version: "ga-fact-0.1"
created_at: "2026-09-20"
updated_at: "2026-09-20"
---
## Observation

A = exact or folded lexicon match; folded flagged.

## Interpretation

Orthographic policy for evaluator and packages.

## Notes

_none_
