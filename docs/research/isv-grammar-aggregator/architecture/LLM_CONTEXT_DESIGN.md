# LLM context design — targeted packages (not a grammar dump)

**Status:** design only. No retrieval implementation; no prompts executed.

## Principle

The aggregator is a **queryable evidence store**. The translator (future
orchestration layer) selects what to retrieve. The LLM never needs the
entire KB in context.

```text
Polish source
    ↓
identify relevant lexical / grammatical phenomena
    ↓
query aggregator (filters: domain, lemma, conflict visibility)
    ↓
retrieve relevant rules + examples + statuses
    ↓
build compact ISV guidance package
    ↓
LLM translation (or repair)
```

---

## Size discipline (design targets)

| Budget | Guidance |
|---|---|
| Rules | Prefer ≤10–20 short bullets per package |
| Lexical rows | Prefer unresolved / high-value lemmas only (EXP-003 lesson: more alternatives ≠ better) |
| Examples | 1–3 surfaces per rule max |
| Conflicts | Summarize; do not paste engine dumps |
| Forbidden | Pasting Steen HTML; full 320k lexicon; Hunspell wholesale |

Exact token budgets are deferred until a builder exists.

---

## Mode A — grammar-only

**Input:** Polish source (and/or lightweight phenomenon tags).  
**Output:** compact rule bullets + optional miniature examples.  
**Excludes:** dictionary candidate tables (unless a closed-class form is
itself the rule).

Example payload shape:

```text
[mode=A]
phenomena: animate_acc, prep_case(v + loc/ins), verb_aspect_pairs
rules:
  - (tier=C/N, status=canonical) animate masculine ACC = GEN …
  - (tier=A/C, status=accepted_variant) 1sg present -u/-ju or -em/-im …
conflicts_shown: none | short list
```

**Intended test contrast:** Direct vs Mode A (isolates grammar without
lexical scaffolding).

---

## Mode B — lexical + grammar

**Input:** Polish source + deterministic lexical candidates (EXP-003-style
reverse index / residual tables).  
**Output:** candidate rows **plus** only grammar facts that constrain
those lemmas (agreement, aspect, selected paradigm cells).

Example payload shape:

```text
[mode=B]
candidates:
  - pl: … → isv: … (pos=v, aspect=ipf, examples: inf/1sg/past.m.sg)
grammar_for_candidates:
  - agreement / government bullets tied to chosen POS
status_legend: canonical | orthographic_variant | resource_only (if shown)
```

**Intended test contrast:** EXP-003-B (lexical-only) vs Mode B
(lexical+grammar). Closest successor to EXP-003 D, but with provenance
headers and explicit conflict/status fields.

---

## Mode C — diagnostic / repair

**Input:** an existing ISV candidate (model output) + evaluator signals
(unresolved tokens, orthography counts, optional agreement heuristics).  
**Output:** constraints and suggested checks — **not** an automatic
rewrite.

Example payload shape:

```text
[mode=C]
flags:
  - outside_inventory: {ł, …}
  - unresolved: [form → possible lemmas / attestations by tier]
diagnostics:
  - if prep X then expect case Y (tier=A table / dict note)
  - paradigm mismatch: surface not in Tier-C lexicon for lemma Z
repair_policy: supply alternatives with tier labels; model revises;
              evaluator re-scores (EXP-002-style discipline)
```

**Intended test contrast:** post-hoc repair with vs without grammar
diagnostics (future; keep small).

---

## Retrieval sketch (non-implementation)

Possible future triggers (deterministic first):

1. Dictionary POS/aspect of scaffolded lemmas → pull matching domains.
2. Closed-class detectors (personal pronouns, frequent prepositions).
3. Orthography audit categories → Mode C ortho diagnostics.
4. Conflict groups linked to lemmas present in the candidate set.

LLM-based “phenomenon tagging” of Polish is **optional later** and must
be labeled as a separate experimental factor (it would confound grammar
effects if hidden).

---

## What each mode must always include

- Mode id and package provenance header (`../schemas/PROVENANCE_MODEL.md`).
- Status legend (so the model is not told Tier-S hits are “correct ISV”).
- Explicit statement that coverage metrics remain Tier-C-defined.

## What each mode must never include

- Silent resolution of conflicts.
- Unlabeled community text.
- Instruction claiming grammar guarantees quality.
