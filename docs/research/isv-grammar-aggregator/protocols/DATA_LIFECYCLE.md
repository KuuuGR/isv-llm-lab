# Data lifecycle

**Status:** design.

## Stages

```text
raw source
→ source record
→ extracted evidence (observations)
→ candidate fact
→ reviewed fact
→ versioned knowledge base
→ LLM context package
```

Every stage must remain **traceable backward**. No destructive
transformations (do not overwrite raw excerpts with normalized-only forms;
keep both).

## Stage responsibilities

| Stage | Artifact | May delete prior? |
|---|---|---|
| Raw source | Locator / optional local archive | No — supersede with new retrieval record |
| Source record | `SourceRecord` | No — update with history |
| Observation | evidence extract | No |
| Candidate fact | proposed `GrammarFact` | No — reject/defer instead |
| Reviewed fact | accepted/historical/conflict-linked | No — new version on change |
| Versioned KB | tagged snapshot / directory version | No — append versions |
| LLM package | package header + fact id list | Packages are ephemeral outputs; regenerate from KB |

## Forward references

- Intake: `SOURCE_INTAKE_PROTOCOL.md`
- Evidence: `EVIDENCE_EXTRACTION_PROTOCOL.md`
- Review: `FACT_REVIEW_PROTOCOL.md`
- Storage options: [`../schemas/STORAGE_PROPOSAL.md`](../schemas/STORAGE_PROPOSAL.md)
