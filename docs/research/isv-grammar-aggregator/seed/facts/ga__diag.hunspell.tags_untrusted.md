---
fact_id: "ga:diag.hunspell.tags_untrusted"
domain: "ortho.inventory"
fact_kind: "diagnostic"
statement: "Hunspell isv.dic is a full-form surface enumeration; pipeline morphological tags are often artifactual and must not be treated as gold annotation or canonical proof."
formal_pattern: null
source: "resource_policy"
source_ids:
- "src:resource_policy"
primary_source_id: "src:resource_policy"
source_version: "docs/RESOURCE_POLICY.md; pin b84535b in inventory"
source_location: "docs/RESOURCE_POLICY.md §1; §5; CL-005"
observation_ids:
- "obs:ga:diag.hunspell.tags_untrusted"
resource_tier: "S"
status: "resource_only"
confidence: "high"
examples: []
variants: []
conflict_group_id: null
conflict_ledger_id: "CL-005"
valid_from: "unknown"
valid_to: "open"
status_at_time: "unknown"
chronology_confidence: "unknown"
historical_notes: null
review_state: "accepted"
reviewed_by: "seed-curation-2026-09-20"
reviewed_at: "2026-09-20"
acceptance_basis: "other"
applies_when: null
package_eligibility: true
seed_from_project_audit: true
license_notes: "Hunspell MIT lineage; policy examples only—no dictionary dump."
isv_eval_implications: "Broader tier uses exact surfaces; tags ignored for A/B."
llm_guidance: "Spellcheck lists may attest a surface without proving tagged lemma/features."
schema_version: "ga-fact-0.1"
created_at: "2026-09-20"
updated_at: "2026-09-20"
---
## Observation

Policy cites artifactual tags (e.g. byh st:abak).

## Interpretation

Tier S = attestation only.

## Notes

_none_
