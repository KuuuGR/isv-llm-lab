# Current ISV status — when may we say `current_preferred`?

**Status:** design gate for labeling facts.

## Core design principle (project)

> The purpose of the project is to model Interslavic as a language system
> in its own right. Similarity to other Slavic languages is contextual
> evidence, not permission to invent ISV forms.

**Forbidden shortcut:**

> “This form exists somewhere in a Slavic language, therefore it is valid
> current ISV.”

---

## Evidence inputs that may support `current_preferred`

Combine as applicable (not all required every time; absence must be noted):

| Input | Role |
|---|---|
| Recent normative material (Tier N) with location | Primary linguistic warrant |
| Current maintained computational resources (Tier C pin) | Operational/default warrant |
| Current documentation aligned with the above | Consistency check |
| Recent independent ISV usage (corpus/wiki/video) | Supporting attestation — not sufficient alone |
| Explicit revision history (changelog, dated reform note) | Temporal warrant |

## Minimum bar (practical)

To label a fact `status_at_time=current_preferred` / packaging default:

1. Tier-N explicit support **or** Tier-C generation + documented alignment
   with Tier-N/audit, **and**
2. No open `resolution_status=unresolved` conflict that directly negates it
   **unless** the package labels an **operational default only**, **and**
3. Temporal fields do not claim dates without evidence, **and**
4. Slavic-analogy-only warrants are rejected.

If only Tier S attestation exists → **not** `current_preferred`.

If only historical sources exist → `historical` / `deprecated` as
appropriate — not current.

## Outputs allowed without `current_preferred`

- `accepted_variant`
- `resource_only`
- `documented_optional`
- `conflicting` (with ledger link)
- `uncertain`

These may still appear in Mode A/B/C packages **with correct labels**.
