---
fact_id: "ga:adj.comparison.lexicon_gap_dalše"
domain: "adj.comparison"
fact_kind: "diagnostic"
statement: "Surfaces like dalše may be absent from the Tier-C lexicon path because inflect() emits no comparative cells, while isv.dic may tag them—coverage gap + resource-layer difference, not proof the surface is non-ISV."
formal_pattern: null
source: "resource_policy"
source_ids:
- "src:resource_policy"
primary_source_id: "src:resource_policy"
source_version: "docs/RESOURCE_POLICY.md Task 007 (2026-08-31)"
source_location: "docs/RESOURCE_POLICY.md §2 / dalše"
observation_ids:
- "obs:ga:adj.comparison.lexicon_gap_dalše"
resource_tier: "S"
status: "morphology_coverage_gap"
confidence: "high"
examples:
-
  surface: "dalše"
  note: "Hunspell example in RESOURCE_POLICY; not promoted"
variants: []
conflict_group_id: null
conflict_ledger_id: "CL-004"
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
license_notes: "Hunspell MIT lineage; dictionary UNRESOLVED. Single cited example only—no bulk import."
isv_eval_implications: "Canonical C possible while broader tier attests; do not promote Hunspell tags to A/B."
llm_guidance: "Unresolved comparatives may be engine/lexicon gaps—do not invent forms from other Slavic languages alone."
schema_version: "ga-fact-0.1"
created_at: "2026-09-20"
updated_at: "2026-09-20"
---
## Observation

Canonical path fails; Hunspell/freq may attest; inflect() lacks comparative cells.

## Interpretation

False-negative diagnostic.

## Notes

_none_
