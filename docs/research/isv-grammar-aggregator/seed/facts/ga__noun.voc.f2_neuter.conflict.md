---
fact_id: "ga:noun.voc.f2_neuter.conflict"
domain: "noun.case.vocative"
fact_kind: "rule"
statement: "Engines disagree on vocatives for feminine consonant stems and neuters: JS emits cells; Rust returns None (nominative address); Steen prose says avoid while tables list forms."
formal_pattern: null
source: "grammar_audit"
source_ids:
- "src:grammar_audit"
primary_source_id: "src:grammar_audit"
source_version: "morphology@0.1.2; Rust 599954b"
source_location: "docs/GRAMMAR_AUDIT.md §Cases / Vocative forms"
observation_ids:
- "obs:ga:noun.voc.f2_neuter.conflict"
resource_tier: "N"
status: "conflicting"
confidence: "high"
examples:
-
  surface: "kosti"
  note: "JS-side example in audit"
-
  surface: "noču"
  note: "cited in audit summary"
variants:
- "JS emits vocative cell"
- "Rust returns None"
- "Steen prose: avoid"
conflict_group_id: "cg:voc.f2_neuter"
conflict_ledger_id: "CL-001"
valid_from: "unknown"
valid_to: "open"
status_at_time: "unknown"
chronology_confidence: "unknown"
historical_notes: null
review_state: "accepted"
reviewed_by: "seed-curation-2026-09-20"
reviewed_at: "2026-09-20"
acceptance_basis: "mixed"
applies_when: null
package_eligibility: true
seed_from_project_audit: true
license_notes: "Steen: © cite-only (no wholesale copy). Dictionary data license UNRESOLVED where referenced. JS morphology MIT; Rust MIT OR Apache-2.0 per SOURCES.md/RESOURCE_POLICY. Hunspell MIT lineage when cited."
isv_eval_implications: "JS lexicon may mark some vocatives A; Rust-style check would not."
llm_guidance: "Vocative f2/neuter: sources conflict. Prefer nominative address if unsure; do not treat one engine as settled truth."
schema_version: "ga-fact-0.1"
created_at: "2026-09-20"
updated_at: "2026-09-20"
---
## Observation

❗ discrepancy; Steen tables vs prose tense.

## Interpretation

Keep conflicting; no silent resolution.

## Notes

_none_
