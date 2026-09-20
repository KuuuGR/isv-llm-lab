# ISV Grammar Aggregator — Research Track

**Status:** research / design only (2026-09-20)  
**Experiments run for this track:** none  
**Implementation status:** not started  

## What it is

A proposed **knowledge/evidence layer** that aggregates Interslavic
(Medžuslovjansky) morphology and grammar facts from the project's already
audited resources, with **explicit provenance, tier, confidence, and
conflict status**.

The intended downstream use is **small, targeted LLM context packages** for
Polish → ISV translation assistance — conceptually the next step beyond
EXP-003 Condition D's thin grammatical annotations, and a structured
realization of intervention-ladder rung **D**
(`docs/translation-method.md`).

Pipeline idea (not yet built):

```text
multiple ISV language resources
        ↓
structured evidence (rules / paradigms / attestations / diagnostics)
        ↓
grammar–morphology knowledge base (provenance-preserving)
        ↓
retrieval → compact context package
        ↓
LLM Polish → ISV generation
        ↓
deterministic isv-eval (+ optional repair)
```

## What it is not

- Not a full translation engine.
- Not a dump of Steen's grammar into an LLM prompt.
- Not a claim that aggregated grammar will improve translation.
- Not a claim that any single resource is the only correct ISV grammar.
- Not a redesign of EXP-004 or a change to canonical experiment artifacts.
- Not a replacement for the two-tier resource policy
  (`docs/RESOURCE_POLICY.md`): **canonical coverage ≠ proof of correct
  Interslavic**; alternative resources remain evidence, not automatic
  promotion into the canonical tier.

## Why the project needs it

Measured work already shows:

- Lexical scaffolding can raise coverage (EXP-003 B/C).
- Adding morphology/grammar annotations (EXP-003 D) can help, but effects
  are **model-dependent**.
- Corpus priming (EXP-004) is a different intervention with its own
  configuration heterogeneity.

What is still missing is a **reusable, provenance-preserving grammar
evidence store** that can:

1. encode disagreements between Steen prose, JS/Rust engines, and
   community inventories without silently resolving them;
2. retrieve only the rules/forms relevant to a given Polish source or
   candidate ISV output;
3. support later controlled comparison of grammar guidance vs
   dictionary-only assistance vs corpus priming.

## Existing resources it builds upon

See [`RESOURCE_INVENTORY.md`](RESOURCE_INVENTORY.md) and
[`RESOURCE_HIERARCHY.md`](RESOURCE_HIERARCHY.md). Primary anchors:

| Role | Resource |
|---|---|
| Normative prose reference | Steen grammar pages (`SOURCES.md` §8); audit in `docs/GRAMMAR_AUDIT.md` |
| Canonical dictionary | `basic.json` snapshot lineage (`SOURCES.md` §10–11) |
| Computational morphology | `@interslavic/morphology` via `src/morphology_backend/` |
| Generated paradigms | `lexicon.tsv` (local, gitignored) |
| Supporting surface evidence | Hunspell `isv.dic` / `isv.aff`; `interslavicfreq` wordlists |
| Historical same-lineage snapshot | `medzuslovjansky/slovnik` test fixture |
| Alternate morphology implementation | Rust `gold-silver-copper/interslavic` (parity reference; not required locally) |
| Evaluation policy | `docs/RESOURCE_POLICY.md` |

## How provenance is preserved

Every grammar fact is a record with source, version/pin, location, tier,
status, variants, and notes — see [`PROVENANCE_MODEL.md`](PROVENANCE_MODEL.md).
No rule may become an unexplained fact with lost provenance.

## How it could later feed an LLM

Not as one giant prompt. Three designed retrieval modes
([`LLM_CONTEXT_DESIGN.md`](LLM_CONTEXT_DESIGN.md)):

- **Mode A** — grammar-only targeted rules;
- **Mode B** — lexical candidates + grammatical guidance;
- **Mode C** — diagnostic/repair guidance for an existing ISV candidate.

## Documents in this track

| File | Contents |
|---|---|
| [`RESEARCH_QUESTION.md`](RESEARCH_QUESTION.md) | Framing questions |
| [`HYPOTHESES.md`](HYPOTHESES.md) | H1–H5 (untested) |
| [`RESOURCE_INVENTORY.md`](RESOURCE_INVENTORY.md) | Audited resource inventory |
| [`RESOURCE_HIERARCHY.md`](RESOURCE_HIERARCHY.md) | Tier model + disagreement rule |
| [`PROVENANCE_MODEL.md`](PROVENANCE_MODEL.md) | Minimal fact schema |
| [`GRAMMAR_TAXONOMY.md`](GRAMMAR_TAXONOMY.md) | Knowledge categories + rule/example split |
| [`LLM_CONTEXT_DESIGN.md`](LLM_CONTEXT_DESIGN.md) | Context package modes |
| [`CONFLICT_POLICY.md`](CONFLICT_POLICY.md) | Conflict/status policy |
| [`EXPERIMENT_DESIGN.md`](EXPERIMENT_DESIGN.md) | Proposed minimal future experiment |
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | Aggregator vs translator boundary |
| [`TODO.md`](TODO.md) | Next steps and open questions |

## Explicit non-claims

This track does **not** claim that:

- an aggregated grammar will improve translation;
- grammar guidance is superior to corpus priming;
- EXP-003 D already validated this architecture (D used thin annotations,
  not a provenance-preserving aggregator);
- the proposed experiment or hierarchy has been validated.

All outcome statements remain **hypotheses** until measured.
