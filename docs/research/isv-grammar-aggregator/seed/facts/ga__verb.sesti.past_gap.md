---
fact_id: "ga:verb.sesti.past_gap"
domain: "verb.conjugation"
fact_kind: "diagnostic"
statement: "Lemma sěsti may be a canonical headword while past forms like sěli are not generated—morphology_coverage_gap, with homograph risk vs Hunspell seli."
formal_pattern: null
source: "resource_policy"
source_ids:
- "src:resource_policy"
primary_source_id: "src:resource_policy"
source_version: "docs/RESOURCE_POLICY.md 2026-08-31"
source_location: "docs/RESOURCE_POLICY.md §2 / sěli"
observation_ids:
- "obs:ga:verb.sesti.past_gap"
resource_tier: "C"
status: "morphology_coverage_gap"
confidence: "high"
examples:
-
  surface: "sěli"
  lemma: "sěsti"
  note: "not generated → canonical C"
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
acceptance_basis: "computational"
applies_when: null
package_eligibility: true
seed_from_project_audit: true
license_notes: "Steen: © cite-only (no wholesale copy). Dictionary data license UNRESOLVED where referenced. JS morphology MIT; Rust MIT OR Apache-2.0 per SOURCES.md/RESOURCE_POLICY. Hunspell MIT lineage when cited."
isv_eval_implications: "Canonical unresolved despite “regular-looking” past; broader tier homograph risk."
llm_guidance: "For past of sěsti, do not trust a random seli attestation—verify lemma identity."
schema_version: "ga-fact-0.1"
created_at: "2026-09-20"
updated_at: "2026-09-20"
---
## Observation

Headword exists; sěl-forms missing; Hunspell seli may be a different word.

## Interpretation

Explains false negatives; no majority vote on Hunspell.

## Notes

_none_
