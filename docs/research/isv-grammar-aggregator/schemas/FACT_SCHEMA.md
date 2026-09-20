# GrammarFact schema (extended)

**Status:** schema design. Builds on `PROVENANCE_MODEL.md`.

## Identity and core

```text
fact_id
domain
fact_kind            rule | lexical_paradigm | evidence_example | diagnostic
statement
formal_pattern       optional
```

## Provenance and tier

```text
source_ids[]         preferred over single source when multi-supported
primary_source_id    optional
source_version       pin(s)
source_location
observation_ids[]    required for accepted facts from intake
resource_tier        N|C|A|S|H|X (primary warrant tier)
status               see CONFLICT_POLICY.md vocabulary
confidence           high|medium|low|unknown
```

## Variation and conflict

```text
examples[]
variants[]
conflict_group_id
conflict_ledger_id   optional CL-###
```

## Temporal

```text
valid_from
valid_to
status_at_time       see TEMPORAL_MODEL.md
temporal_evidence[]
historical_notes
chronology_confidence
```

## Review lifecycle

```text
review_state         candidate|needs_review|verified|accepted|
                     rejected|conflicting|historical|deferred
reviewed_by          person id | unknown
reviewed_at          ISO date | unknown
acceptance_basis     normative|computational|multi_attestation|
                     mixed|operational_default|other
```

## Retrieval aids

```text
applies_when
package_eligibility  true|false
notes
created_at
updated_at
schema_version       e.g. ga-fact-0.1
```

## Invariants

1. Accepted facts without `observation_ids` / `source_ids` are invalid
   unless explicitly marked `seed_from_project_audit` with audit location.
2. `status_at_time=current_preferred` requires
   `CURRENT_ISV_STATUS.md` gate.
3. Changing an accepted statement creates a **new version** (new
   `fact_id` or explicit `supersedes` link) — no silent overwrite.
