# Research questions — ISV Grammar Aggregator

**Status:** design framing only. No aggregator experiment has been run.

## Primary question

> Can a **provenance-preserving Interslavic grammar/morphology evidence
> store**, retrieved as **small targeted context packages**, improve
> Polish→ISV LLM translation relative to dictionary-only assistance —
> without dumping entire grammars into the prompt, and without treating
> alternative resources as automatic proof of correctness?

## Secondary questions

1. Which grammar categories are actually useful for generation-time
   guidance (vs useful only for human reference or post-hoc diagnosis)?
2. How should disagreements among Steen documentation, JS morphology,
   Rust morphology, and community surface inventories be represented so
   that an LLM (and a later human auditor) can see conflict rather than
   a silently chosen “winner”?
3. Does targeted grammar guidance produce more **stable** effects across
   model configurations than large-context corpus priming?
4. Can Mode C (diagnostic/repair) reduce orthographic or morphological
   anomalies without introducing A→C regressions of the kind measured in
   EXP-002?
5. Where does the boundary lie between the aggregator (evidence) and the
   translator (source analysis, package construction, generation)?

## Relation to existing experiments

| Prior work | Relation |
|---|---|
| EXP-003 B/C | Lexical scaffolding already measured; aggregator must not re-test “dictionary helps” as if novel. |
| EXP-003 D | Closest prior rung: lexical + thin grammatical annotations. Aggregator proposes a **structured, reusable** evidence layer beyond that thin annotation format. |
| EXP-004 Phase 2B | Corpus priming is a separate intervention; a future comparison may include priming, but this track does **not** redesign EXP-004. |
| RESOURCE_POLICY / EXP-005 | Two-tier metrics and evidence classes are binding constraints on any aggregator claim language. |

## Non-questions (out of scope for this track)

- Fine-tuning or training an ISV LM.
- Declaring a single normative grammar as “correct ISV”.
- Replacing `isv-eval` A/B/C with community-resource majority vote.
- Implementing retrieval or running LLM sessions as part of this design
  pass.
