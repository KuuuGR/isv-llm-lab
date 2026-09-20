# Temporal model

**Status:** design model. **Do not assign dates without evidence.**

## Purpose

Support questions:

- What is the **current preferred** form/rule?
- Was this form used **historically**?
- Is this a **current variant** or a **legacy** rule?
- Is chronology **unresolved**?

## Fields (on facts and, where useful, observations)

```text
valid_from           ISO date | year | unknown
valid_to             ISO date | year | open | unknown
status_at_time       current_preferred | current_variant | transitional |
                     deprecated | historical_usage | unknown
temporal_evidence    list of {source_id, location, what_it_shows}
historical_notes     free text
chronology_confidence high | medium | low | unknown
```

`open` on `valid_to` means “no end date in evidence,” not “forever true.”

## Categories

| Category | Meaning |
|---|---|
| Current rule | Intended as presently normative/preferred for packaging defaults |
| Historical rule | Described as past or superseded |
| Transitional | Explicitly in flux in sources (rare; needs strong evidence) |
| Deprecated form | Sources discourage or mark obsolete |
| Community variant | Living alternate without normative elevation |
| Unresolved chronology | Attested, but when/whether current is unknown |

## Rules

1. **No invented dates.** If only “older snapshot vs newer snapshot” is
   known, record those retrieval/publication dates — do not infer a reform
   year.
2. **Absence of end date ≠ current.** A Steen page retrieved today is
   evidence of *present documentation*, not proof that community usage
   matches it.
3. **Engine pins are temporal.** `@interslavic/morphology@0.1.2` behavior
   is dated to that version; upgrades need new observations.
4. **Conflicts may be temporal.** Prefer ledger entries that ask whether
   disagreement is synchronic (same era) or diachronic (change over time)
   — default `unknown` until evidenced.
5. Packaging defaults for “current preferred” follow
   `CURRENT_ISV_STATUS.md`, not the newest URL alone.
