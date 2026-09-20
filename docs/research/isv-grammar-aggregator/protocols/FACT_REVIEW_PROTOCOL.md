# Fact review protocol

**Status:** design protocol.

## Lifecycle

```text
candidate
   ↓
needs_review
   ↓
verified
   ↓
accepted
```

Alternative terminals / side states:

```text
rejected
conflicting
historical
deferred
```

These map onto `review_state` / `status` fields in `FACT_SCHEMA.md` and
remain compatible with `CONFLICT_POLICY.md` status vocabulary.

---

## Stage definitions

| Stage | Meaning |
|---|---|
| `candidate` | Proposed from ≥1 observation; not yet checked |
| `needs_review` | Queued; missing confirmation or conflict check |
| `verified` | Evidence standard for this claim type met; not yet packaged as accepted current knowledge |
| `accepted` | Approved for versioned KB / eligible for LLM packages (still may be variant/historical) |
| `rejected` | Not admitted; provenance retained |
| `conflicting` | Held as linked disagreement; not silently resolved |
| `historical` | Accepted as historical/non-current description |
| `deferred` | Parked (license, ASR uncertainty, low priority) |

---

## Evidence standards (claim-type dependent)

**Do not use one bar for every fact.**

### A. Current normative / preferred rule (`current_preferred` target)

Require **at least one** of:

- explicit statement in Tier-N normative material with location, **or**
- consistent Tier-C computational generation from a canonical lemma **plus**
  alignment with Tier-N or project audit notes,

and additionally:

- conflict check against the ledger,
- temporal fields not asserting dates without evidence
  (`TEMPORAL_MODEL.md`, `CURRENT_ISV_STATUS.md`).

Independent second source is **preferred** but not always available for
constructed-language normative prose; when absent, say so in notes.

### B. Accepted variant (documented dual forms)

Require:

- Tier-N documentation of optionality, **and/or**
- Tier-C/A engines emitting both forms as designed variants,

not mere frequency in Tier S.

### C. Attested / resource-only surface

Require:

- exact Tier-S (or corpus) attestation with pin,

and label status `resource_only` / `attested_variant` — **never** auto-upgrade
to canonical.

Multiple independent attestations may raise **confidence** without changing
normative status (`SOURCE_RELIABILITY.md`).

### D. Historical usage

Require:

- dated or explicitly historical source, **or**
- Tier-H lineage note,

and set temporal status accordingly. Historical acceptance ≠ current
preferred.

### E. Engine discrepancy / coverage gap

Require:

- reproducible engine observation (version pinned),
- link to `GRAMMAR_AUDIT` or new audit note,

status often `conflicting` or `morphology_coverage_gap`.

### F. Video / ASR-derived claims

Require human verification of the relevant span before `verified`.
Unverified ASR → `deferred` or `rejected` as fact evidence (may keep
observation).

---

## Review checklist

- [ ] `source_id` + `observation_id`s present
- [ ] observation ≠ interpretation collapsed
- [ ] tier/status consistent with hierarchy
- [ ] conflicts searched / ledger updated
- [ ] temporal fields not fabricated
- [ ] license wall respected
- [ ] Slavic analogy not used as sole warrant

## Packaging gate

Only `accepted` facts (including `historical` / `accepted_variant` as
labeled) may enter LLM context packages. `conflicting` facts may be
**summarized** as conflict notes, not presented as resolved rules.
