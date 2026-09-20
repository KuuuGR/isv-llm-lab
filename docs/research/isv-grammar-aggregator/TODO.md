# TODO — Grammar Aggregator research package

**Status:** context pack + intake/review protocols complete (2026-09-20).  
**Implementation / seed facts / experiments:** not started.

## Next concrete steps (ordered)

1. **Do not bulk-ingest.** Protocols are ready; execution waits.
2. When authorized: seed **20–50** reviewed facts from
   `protocols/CONFLICT_LEDGER.md` + high-priority Tier-C rules, each with
   provenance (`schemas/FACT_SCHEMA.md` / `PROVENANCE_MODEL.md`).
3. Offline Mode A/B package renderer (no LLM).
4. Freeze minimal A/B/C experiment kit (`experiments/EXPERIMENT_DESIGN.md`).

## Deferred (explicitly not this pass)

- Scrape Steen / bulk Wikipedia / bulk YouTube / bulk Hunspell.
- Implement aggregator software or database.
- Create the fact seed.
- Run A/B/C experiment.
- Modify translator, EXP-004, or canonical language resources.
- Reinterpret old experiment results (backward audit is protocol-only).

## Open design questions

1. Dictionary data license **UNRESOLVED** (public redistribution limits).
2. Rust prep-government table as packaging default vs Tier-A enrichment only.
3. Polish-side phenomenon detection (deterministic vs LLM tagger confound).
4. Package token budgets per vendor.
5. Mode C vs EXP-002 candidate codepaths.
6. Fact versioning when morphology/`basic.json` pins move.
7. Steen quotation depth vs copyright for publications.
8. Whether Option D storage cards live under this tree or gitignored local
   data until license clarity.

## Integration points (do not edit yet)

| Document | Action |
|---|---|
| `docs/translation-method.md` | Deferred pointer to this package as structured rung-D evidence layer |
| `docs/research-roadmap.md` | Deferred research-track pointer |
| `docs/RESOURCE_POLICY.md` | Compatible; no change required |
| EXP-004 / translator | **Do not touch** |

## Consistency notes vs canonical policy

| Document | Status |
|---|---|
| `RESOURCE_POLICY.md` | Aligned (tiers, no promotion of alt resources) |
| `GRAMMAR_AUDIT.md` | Aligned (ledger seeds unresolved) |
| `translation-method.md` | Soft staleness on Phase 2B wording in canonical file; package does not depend on editing it |
| EXP-003 D | Thin annotations ≠ this architecture; do not over-claim |

If implementation would change A/B/C semantics or promote Tier S into
canonical coverage, that would **conflict** with RESOURCE_POLICY and must be
rejected or separately decided.
