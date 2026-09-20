# Architecture — aggregator vs translator boundary

**Status:** design diagram. No implementation.

## Boundary statement

The **Grammar Aggregator** is a **knowledge/evidence layer**.

The **translator / orchestration layer** remains responsible for:

- analyzing the Polish source (deterministically first);
- selecting which facts to retrieve;
- constructing the LLM context package;
- invoking or instructing the LLM;
- running deterministic evaluation;
- optionally requesting repair (Mode C).

The aggregator must **not** silently become a full translation engine,
a prompt monolith, or an automatic rewriter.

---

## Diagram

```text
┌─────────────────────────────────────────────────────────┐
│  Resources (Tier N/C/A/S/H)                             │
│  Steen (cited) · basic.json · morphology JS · lexicon   │
│  Rust (optional) · Hunspell · interslavicfreq · audit   │
└───────────────────────────┬─────────────────────────────┘
                            │ curated ingest (future)
                            ▼
┌─────────────────────────────────────────────────────────┐
│  Grammar Aggregator                                     │
│  · GrammarFact store (rules / paradigms / examples /    │
│    diagnostics)                                         │
│  · provenance + tier + status + conflict_group          │
│  · query API (by domain, lemma, phenomenon, status)     │
│  Does NOT: call LLMs, score quality, emit final ISV     │
└───────────────────────────┬─────────────────────────────┘
                            │ retrieve facts
                            ▼
┌─────────────────────────────────────────────────────────┐
│  Retrieval / Context Builder  (translator-side)         │
│  · Mode A / B / C package assembly                      │
│  · size budgets, status legend, package provenance      │
└───────────────────────────┬─────────────────────────────┘
                            │ prompt + package
                            ▼
┌─────────────────────────────────────────────────────────┐
│  LLM Translator                                         │
│  · Polish → ISV generation (or repair)                  │
│  · under operator/API control as today                  │
└───────────────────────────┬─────────────────────────────┘
                            │ raw output (preserved)
                            ▼
┌─────────────────────────────────────────────────────────┐
│  Deterministic Evaluator (isv-eval)                     │
│  · canonical + broader coverage · orthography           │
└───────────────────────────┬─────────────────────────────┘
                            │ optional
                            ▼
┌─────────────────────────────────────────────────────────┐
│  Optional Repair (Mode C loop)                          │
│  · diagnostics from aggregator + evaluator flags        │
│  · model revises; re-evaluate; no silent auto-edit      │
└─────────────────────────────────────────────────────────┘
```

---

## Interface sketch (future)

Aggregator exposes read-only queries, e.g.:

- `get_facts(domain=…, status_in=…)`
- `get_paradigm(lemma=…, cells=…)`
- `get_conflicts(group_id=…)`
- `get_diagnostics(surfaces=[…])`

Translator owns:

- `build_package(mode, source, candidates?, candidate_isv?)`
- `run_translation(…)` / operator kit
- `evaluate(…)`
- `maybe_repair(…)`

---

## Relation to existing code (no changes in this design pass)

| Existing component | Future relation |
|---|---|
| `src/morphology_backend/` | Fact generator / Tier C source |
| `src/isv_eval/` | Evaluator after generation; evidence layer inspiration |
| EXP-003 scaffold builder | Prototype of Mode B lexical half |
| EXP-004 operator kits | Unrelated priming path; optional later arm |

`docs/translation-method.md` already places morphology/grammar at rung D
and lists pipeline hypotheses; this architecture is the evidence-layer
refinement of that rung — recorded as a future integration point in
`TODO.md` rather than editing that document in this pass.
