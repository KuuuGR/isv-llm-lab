# Conflict policy — when sources disagree

**Status:** design policy. Aligns with RESOURCE_POLICY “preserve, do not
promote” and GRAMMAR_AUDIT discrepancy handling.

## Non-negotiables

1. **No majority vote** across tiers or within Tier S.
2. **No silent overwrite** of Tier C by Tier S attestation.
3. **No deletion** of a conflicting fact when a preferred status is
   chosen for packaging; link via `conflict_group_id`.
4. **Canonical evaluation stays Tier-C-defined** regardless of package
   content.

---

## Status vocabulary

| Status | Meaning |
|---|---|
| `canonical` | Supported by Tier C (dictionary lemma and/or morphology-generated form) |
| `accepted_variant` | Documented dual allowance (Steen and/or engines emit both) |
| `attested_variant` | Orthographic folded/stripped variant of a Tier-C form |
| `resource_only` | Tier S exact surface; no Tier-C path |
| `historical` | Tier H only |
| `documented_optional` | Steen allows; engines may omit generation |
| `documented_avoid` | Steen prose discourages; may still appear in tables/engines |
| `morphology_coverage_gap` | Lemma exists; expected cell not generated |
| `conflicting` | Explicit disagreement among N/C/A (or N-internal tension) |
| `uncertain` | Insufficient evidence to label |
| `unsupported` | No audited layer supports the claim/form |

These extend — and must remain compatible with — RESOURCE_POLICY decision
classes 1–5 for **forms**. Rule-level statuses above apply to
`fact_kind=rule` as well.

---

## Resolution behavior (packaging, not ontology)

When packaging for an LLM:

| Situation | Package behavior |
|---|---|
| Single `canonical` fact | Present as default guidance |
| `accepted_variant` pair | Present both; mark both acceptable |
| `conflicting` | Present short conflict note; optionally pick Tier-C default **labeled as engine/default**, not as absolute truth |
| `resource_only` candidates | Show only if Mode B/C explicitly includes broader evidence; label clearly |
| `morphology_coverage_gap` | Warn that evaluator may still mark C even if form “looks regular” |
| `documented_avoid` | Prefer omission in Mode A/B generation guidance; mention in Mode C if the candidate uses it |

Choosing a **default for generation** is allowed as an operational
convenience **if and only if** the package states that it is a default,
not a resolution of linguistic truth.

---

## Known seed conflicts (from GRAMMAR_AUDIT)

Must be entered early if an aggregator seed is built:

- Vocative f2/neuter: JS vs Rust vs Steen prose/tables.
- Locative m/n alternates documented but not generated.
- Preposition government: Rust table vs JS (dictionary POS only).
- Comparative generation gaps vs Hunspell comparative tags.
- Homograph traps in Hunspell/freq (`seli` etc.).

---

## What “winning” is not

A form does not “win” by:

- appearing more often in Tier S frequency lists;
- being preferred by one LLM;
- matching Polish morphology by analogy;
- being present in `slovnik` historical snapshot.
