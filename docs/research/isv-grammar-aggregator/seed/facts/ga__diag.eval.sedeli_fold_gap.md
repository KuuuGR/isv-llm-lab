---
fact_id: "ga:diag.eval.sedeli_fold_gap"
domain: "ortho.alternation"
fact_kind: "diagnostic"
statement: "Candidate-prefix matching does not fold etymological ě: sedeli cannot reach lemma sěděti even though sěděli is generable/A—an evaluator matching limit."
formal_pattern: null
source: "resource_policy"
source_ids:
- "src:resource_policy"
primary_source_id: "src:resource_policy"
source_version: "docs/RESOURCE_POLICY.md 2026-08-31"
source_location: "docs/RESOURCE_POLICY.md §2 / sedeli; §3 known limits"
observation_ids:
- "obs:ga:diag.eval.sedeli_fold_gap"
resource_tier: "C"
status: "morphology_coverage_gap"
confidence: "high"
examples:
-
  surface: "sedeli"
-
  surface: "sěděli"
  lemma: "sěděti"
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
license_notes: "Steen: © cite-only (no wholesale copy). Dictionary data license UNRESOLVED where referenced. JS morphology MIT; Rust MIT OR Apache-2.0 per SOURCES.md/RESOURCE_POLICY. Hunspell MIT lineage when cited."
isv_eval_implications: "metric_false_negative candidate."
llm_guidance: "Prefer etymological ě where required (sěděti → sěděli)."
schema_version: "ga-fact-0.1"
created_at: "2026-09-20"
updated_at: "2026-09-20"
---
## Observation

sedeli → C; sěděli → A.

## Interpretation

False-negative pathway for backward audit.

## Notes

Status class reused for evaluator gap; finer vocabulary may be needed later.
