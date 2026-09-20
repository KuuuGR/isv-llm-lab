# Source reliability model

**Status:** operational reading of the existing hierarchy
`N → C → A → S → H → X` (`resources/RESOURCE_HIERARCHY.md`).
**Do not replace** this hierarchy without a documented contradiction.
**Do not use simplistic numeric truth scores.** Prefer categorical statuses.

## Tier meanings (operational)

| Tier | Operational meaning | May set `current_preferred` alone? |
|---|---|---|
| **N** Normative reference | Cited Steen (etc.) prose/tables; project grammar audit notes | Contributes strongly; still cite location |
| **C** Canonical computational | `basic.json` + JS morphology / lexicon (evaluation spine) | Yes for engine-default packaging **labeled as Tier-C default** |
| **A** Alternate computational | Rust (parity / extra tables) | No override of C metrics; may enrich diagnostics |
| **S** Supporting surfaces | Hunspell, frequency lists, corpora attestations | **Never** alone |
| **H** Historical same-lineage | e.g. `slovnik` snapshot | **Never** as independent current warrant |
| **X** Excluded by default | Informal community bulk, unpinned scrapes, live Sheets | Cite-only unless separately curated |

## Key principles

### Community evidence ≠ normative override

A form in Tier S can be **useful evidence** (broader coverage, Mode C
hints) without overriding Tier N/C. This is the RESOURCE_POLICY rule:
alternative resources are evidence, not automatic validity.

### Multiple attestations raise confidence, not tier

Ten Hunspell/freq hits may justify `confidence: high` on a
`resource_only` observation. They do **not** promote the form to
`canonical` or `current_preferred`.

### Historical value without current force

Tier H and dated materials can support `historical` facts and backward
audits. They do not, by themselves, define current ISV.

### Computational confirmation is powerful but bounded

Tier C generation confirms “the pinned engine emits this from lemma L.”
That is not identical to “Steen requires this” or “all ISV speakers accept
this,” especially where GRAMMAR_AUDIT records gaps or conflicts.

### Epistemic labels only

Use `confidence: high|medium|low|unknown` as **epistemic** labels tied to
evidence quality — not probabilities, not PageRank, not majority vote.

## Interaction with metrics

- **Canonical coverage** remains Tier-C-defined (`isv-eval`).
- **Broader coverage** may reflect Tier S.
- Aggregator packaging must not redefine those metrics silently.
