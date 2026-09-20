# TODO — Grammar Aggregator research track

**Status:** design complete for v0 spec. Implementation not started.

## Next concrete implementation step (recommended)

1. **Seed a tiny reviewed fact set (human-curated JSON), not a database.**
   - Start from `docs/GRAMMAR_AUDIT.md` conflict rows + a handful of
     high-priority Tier-C rules (animate ACC, 1sg variants, prep+case
     samples from documented sources).
   - Each entry must satisfy `PROVENANCE_MODEL.md` (source_location
     required).
   - Target size: on the order of **20–50 facts**, enough to exercise
     Mode A/B package rendering offline (no LLM).

2. Only after (1): a dry-run **package renderer** that prints Mode A/B
   text for the EXP-003 story lemmas — still no LLM calls.

3. Only after (2): freeze a minimal A/B/C experiment kit per
   `EXPERIMENT_DESIGN.md`.

Do **not** begin with full Steen HTML scraping, Hunspell ingestion, or
translator refactors.

---

## Open / unresolved questions

1. Dictionary data license remains **UNRESOLVED** — public redistribution
   of lemma/paradigm packages may be blocked even if research use is
   local (`SOURCES.md`, D-009).
2. Should Rust preposition government be promoted to packaging defaults
   while JS lacks a table? (Conflict vs enrichment.)
3. How much Polish-side analysis is allowed before it becomes a confound
   (tagger LLM vs deterministic heuristics)?
4. Exact package token budgets for each vendor context window.
5. Whether Mode C should share EXP-002’s candidate-generation codepaths
   or a new diagnostic query API.
6. How to version facts when `@interslavic/morphology` or `basic.json`
   snapshots move.
7. Whether a future paper cites Steen extensively enough to need
   permissioning beyond fair-use quotation of short rules.

---

## Integration points (do not edit yet)

| Document / component | Possible future touch | Action now |
|---|---|---|
| `docs/translation-method.md` | Mention aggregator as structured rung-D evidence layer | **Deferred** — record only here |
| `docs/research-roadmap.md` | New research-track pointer | Deferred |
| `docs/RESOURCE_POLICY.md` | Already compatible; no change required for design | None |
| Translator / scaffold scripts | Consumer of packages | No modification in this pass |
| EXP-004 artifacts | None | **Do not touch** |

---

## Explicitly out of scope until decided

- Production Python/TS/Rust aggregator service.
- Automatic conflict resolution UI.
- Running LLM sessions for this track.
- Changing canonical experiment results or frozen corpora.
- Redesigning EXP-004.

---

## Possible conflicts with existing project documents

| Document | Tension? | Notes |
|---|---|---|
| `RESOURCE_POLICY.md` | **No conflict** | Hierarchy and statuses extend it. |
| `GRAMMAR_AUDIT.md` | **No conflict** | Seed source for conflicts. |
| `translation-method.md` | **Soft staleness, not design conflict** | Still describes Phase 2B as unexecuted in one paragraph; aggregator design does not depend on editing it. Rung D is compatible. |
| `RESEARCH_NOTES.md` §1 | **No conflict** | Taxonomy of lexical vs grammatical guidance remains valid; aggregator refines the grammatical side. |
| EXP-003 D results | **Interpretive caution** | D is evidence that *thin* grammar annotations can help some models; it is **not** validation of this aggregator architecture. |
| EXP-004 Phase 2B | **No conflict** if priming remains a separate optional arm | Do not redesign. |

If any future implementation would require changing A/B/C semantics or
promoting Tier S into canonical coverage, that would **conflict** with
RESOURCE_POLICY and must be rejected or separately decided.
