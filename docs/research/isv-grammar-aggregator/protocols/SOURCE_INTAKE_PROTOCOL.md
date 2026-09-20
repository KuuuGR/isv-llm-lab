# Source Intake Protocol

**Status:** design protocol only. No bulk ingestion in this pass.

Applies to any new external or internal material proposed for the Grammar
Aggregator knowledge workflow, including: web pages, Wikipedia, PDFs, books
or scans (only where legally usable), YouTube and other video, transcripts,
author/publisher pages, community documentation, posters/slides, source
repositories, dictionaries, morphology engines, corpora, and examples from
authentic ISV text.

## Workflow

```text
DISCOVER
   ↓
IDENTIFY
   ↓
ARCHIVE / RECORD
   ↓
EXTRACT EVIDENCE
   ↓
VERIFY
   ↓
CLASSIFY
   ↓
COMPARE AGAINST KNOWLEDGE BASE
   ↓
PROPOSE GrammarFact
   ↓
REVIEW
   ↓
ACCEPT / REJECT / DEFER
```

### 1. DISCOVER

Note how the source was found (search, citation, audit, human tip). Record
enough locator information to retrieve it again. Do not yet treat content as
a rule.

### 2. IDENTIFY

Create or draft a `SourceRecord` (`schemas/SOURCE_RECORD_SCHEMA.md`):

- title, author/org, type, URL/locator,
- publication and retrieval dates (unknown → `unknown`),
- language, version, license/rights status,
- provisional reliability notes and temporal scope.

Do **not invent** missing metadata.

### 3. ARCHIVE / RECORD

Preserve a reproducible handle:

- URL + retrieval date + (if available) revision id / commit / PDF hash,
- local archival path if a copy is kept (respect license walls),
- for video: URL + timestamp range of interest.

Prefer recording locators over redistributing copyrighted full texts.

### 4. EXTRACT EVIDENCE

Follow `EVIDENCE_EXTRACTION_PROTOCOL.md`.

Produce **observations**, not facts:

```text
SOURCE → OBSERVATION → INTERPRETATION → GrammarFact candidate
```

Never:

```text
source → immediate grammar rule
```

### 5. VERIFY

Check that:

- the excerpt is accurate against the source (or ASR caveat recorded),
- the location/timestamp is correct,
- license/rights allow the intended local use,
- the claim type is labeled (explicit rule vs usage vs paraphrase).

### 6. CLASSIFY

Assign provisional:

- source_type,
- resource_tier hint (N/C/A/S/H/X per `SOURCE_RELIABILITY.md`),
- temporal_scope (current / historical / unknown),
- relevance to taxonomy domains.

### 7. COMPARE AGAINST KNOWLEDGE BASE

Search existing facts/conflicts for the same domain/form:

- agrees → strengthen evidence links,
- disagrees → open/update `CONFLICT_LEDGER.md` entry,
- novel → proceed as candidate,
- already rejected with same evidence → defer with pointer.

### 8. PROPOSE GrammarFact

Create a **candidate** fact linking `observation_id`s and `source_id`s.
Separate observation from interpretation in notes
(`schemas/FACT_SCHEMA.md`, `schemas/PROVENANCE_MODEL.md`).

### 9. REVIEW

Follow `FACT_REVIEW_PROTOCOL.md` (evidence standard depends on claim type).

### 10. ACCEPT / REJECT / DEFER

Terminal outcomes are recorded; rejected/deferred items keep provenance.
Accepted facts are versioned; they do not erase conflicting observations.

## Source-type notes (pointers)

| Source type | Protocol |
|---|---|
| Wikipedia | `WIKIPEDIA_AUDIT_PROTOCOL.md` |
| YouTube / video | `VIDEO_SOURCE_PROTOCOL.md` |
| Author slides/posters/handouts | `AUTHOR_MATERIAL_PROTOCOL.md` |
| Computational resources | treat like inventory resources; pin versions |
| Authentic ISV corpus examples | observation = usage; not automatic rule |

## Hard stops

- Do not scrape Steen wholesale or bulk-import Wikipedia/Hunspell/YouTube
  in this research stage.
- Do not promote Tier S/X materials into Tier C by intake alone.
- Do not treat similarity to another Slavic language as permission to invent
  an ISV form (`CURRENT_ISV_STATUS.md`; core design principle in README).
