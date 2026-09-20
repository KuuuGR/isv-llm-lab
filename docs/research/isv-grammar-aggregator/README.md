# ISV Grammar Aggregator — Research Package

**Status:** research / design package (updated 2026-09-20)  
**Experiments run for this track:** none  
**Implementation / database / seed facts:** not started  

## What it is

A **self-contained working research package** for an Interslavic
(Medžuslovjansky) **language knowledge / evidence layer**: provenance-preserving
grammar and morphology facts, conflict tracking, and (later) small LLM
context packages for Polish → ISV assistance.

Conceptually this is intervention-ladder rung **D**
(`docs/translation-method.md`; see `context/TRANSLATION_METHOD_RELEVANT.md`),
extended beyond EXP-003 Condition D’s thin annotations.

## Core design principle

> The purpose of the project is to model Interslavic as a language system
> in its own right. Similarity to other Slavic languages is contextual
> evidence, not permission to invent ISV forms.

Also preserved from project policy:

> Canonical resource coverage is not identical to proof that a form is
> correct Interslavic. Alternative resources may provide useful evidence
> without automatically becoming canonical.

## Complete workflow

```text
collect source
→ preserve source metadata          (SourceRecord)
→ extract evidence                  (Observation ≠ rule)
→ compare with existing KB          (incl. conflict ledger)
→ propose fact                      (candidate GrammarFact)
→ review                            (claim-type evidence bar)
→ version                           (accepted / historical / …)
→ retrieve
→ render compact LLM package        (Modes A / B / C)
```

```text
raw source → source record → observation → candidate fact
→ reviewed fact → versioned KB → LLM context package
```

## What it is not

- Not a full translation engine.
- Not a dump of Steen / Wikipedia / Hunspell into prompts.
- Not a claim that aggregated grammar will improve translation.
- Not bulk ingestion (Steen scrape, Wikipedia dump, YouTube harvest) —
  protocols exist; execution is future work.
- Not a redesign of EXP-004 or a change to canonical experiment artifacts.
- Not a replacement for `docs/RESOURCE_POLICY.md` two-tier metrics.

## Package layout

```text
docs/research/isv-grammar-aggregator/
├── README.md                          (this file)
├── RESEARCH_QUESTION.md
├── HYPOTHESES.md
├── TODO.md
├── context/                           (local mirrors / extracts)
├── protocols/                         (intake, evidence, review, …)
├── schemas/                           (source, fact, provenance, storage)
├── architecture/                      (system boundary + LLM modes)
├── experiments/                       (proposed A/B/C design)
├── resources/                         (inventory + hierarchy)
└── seed/                              (initial reviewed GrammarFact cards + JSON)
```

### Start here

| Need | Document |
|---|---|
| Self-contained policy context | [`context/CONTEXT_README.md`](context/CONTEXT_README.md) |
| Add a new external source | [`protocols/SOURCE_INTAKE_PROTOCOL.md`](protocols/SOURCE_INTAKE_PROTOCOL.md) |
| Observation vs fact | [`protocols/EVIDENCE_EXTRACTION_PROTOCOL.md`](protocols/EVIDENCE_EXTRACTION_PROTOCOL.md) |
| Review / accept | [`protocols/FACT_REVIEW_PROTOCOL.md`](protocols/FACT_REVIEW_PROTOCOL.md) |
| Known disagreements | [`protocols/CONFLICT_LEDGER.md`](protocols/CONFLICT_LEDGER.md) |
| LLM package modes | [`architecture/LLM_CONTEXT_DESIGN.md`](architecture/LLM_CONTEXT_DESIGN.md) |
| Future experiment | [`experiments/EXPERIMENT_DESIGN.md`](experiments/EXPERIMENT_DESIGN.md) |
| Reviewed fact seed | [`seed/README.md`](seed/README.md) |

### Index

| Path | Role |
|---|---|
| [`RESEARCH_QUESTION.md`](RESEARCH_QUESTION.md) | Framing questions |
| [`HYPOTHESES.md`](HYPOTHESES.md) | H1–H5 (untested) |
| [`resources/RESOURCE_INVENTORY.md`](resources/RESOURCE_INVENTORY.md) | Resource inventory |
| [`resources/RESOURCE_HIERARCHY.md`](resources/RESOURCE_HIERARCHY.md) | Tiers N→C→A→S→H→X |
| [`schemas/PROVENANCE_MODEL.md`](schemas/PROVENANCE_MODEL.md) | Provenance rules + core fact fields |
| [`schemas/FACT_SCHEMA.md`](schemas/FACT_SCHEMA.md) | Extended GrammarFact schema |
| [`schemas/SOURCE_RECORD_SCHEMA.md`](schemas/SOURCE_RECORD_SCHEMA.md) | Source-level schema |
| [`schemas/GRAMMAR_TAXONOMY.md`](schemas/GRAMMAR_TAXONOMY.md) | Domains + knowledge kinds |
| [`schemas/STORAGE_PROPOSAL.md`](schemas/STORAGE_PROPOSAL.md) | Storage options (recommend D) |
| [`protocols/`](protocols/) | Intake, evidence, review, temporal, reliability, Wikipedia, video, author, current-ISV, backward audit, lifecycle, conflict policy + ledger |
| [`architecture/ARCHITECTURE.md`](architecture/ARCHITECTURE.md) | Aggregator vs translator |
| [`TODO.md`](TODO.md) | Next steps |

## Authority

> `docs/research/isv-grammar-aggregator/` is the working research package;
> canonical project policies remain authoritative in their original locations.

See `context/CONTEXT_README.md`.

## Explicit non-claims

This package does **not** claim that grammar guidance works, that it beats
corpus priming, that EXP-003 D validated this architecture, or that seeded
conflicts are resolved. Outcomes remain hypotheses until measured.
