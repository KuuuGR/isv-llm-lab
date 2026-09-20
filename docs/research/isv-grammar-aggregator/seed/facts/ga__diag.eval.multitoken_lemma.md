---
fact_id: "ga:diag.eval.multitoken_lemma"
domain: "verb.conjugation"
fact_kind: "diagnostic"
statement: "Multi-token lemmas such as bojati sę are excluded from lemma-driven matching, so forms like bojala can be canonical-C despite Hunspell participle tags."
formal_pattern: null
source: "resource_policy"
source_ids:
- "src:resource_policy"
primary_source_id: "src:resource_policy"
source_version: "docs/RESOURCE_POLICY.md"
source_location: "docs/RESOURCE_POLICY.md §2 / bojala"
observation_ids:
- "obs:ga:diag.eval.multitoken_lemma"
resource_tier: "C"
status: "morphology_coverage_gap"
confidence: "high"
examples:
-
  surface: "bojala"
  lemma: "bojati sę"
variants: []
conflict_group_id: null
conflict_ledger_id: null
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
license_notes: "Example from RESOURCE_POLICY; no Hunspell dump."
isv_eval_implications: "Canonical C despite possible Tier-S attestation."
llm_guidance: "Reflexive multi-word lemmas may need special handling."
schema_version: "ga-fact-0.1"
created_at: "2026-09-20"
updated_at: "2026-09-20"
---
## Observation

Structural evaluator limit.

## Interpretation

resource_policy_limitation for backward audit.

## Notes

_none_
