# Source record schema

**Status:** schema design. Unknown fields must remain explicitly `unknown`.
Do not invent missing metadata.

## Purpose

One `SourceRecord` per distinct retrievable source (or pinned version of a
computational resource). Facts and observations point at `source_id`.

## Fields

```text
source_id            stable id (e.g. src:steen.grammar.verbs)
title                string | unknown
author_or_org        string | unknown
source_type          enum (see below)
url_or_locator       URL, DOI, path, repo+path, ISBN, …
publication_date     ISO date | year | unknown
retrieval_date       ISO date (required when URL/live material)
language             ISO-ish tag or unknown
version              version / commit / revision / edition | unknown
license_rights       documented license text or status
                     (e.g. MIT | UNRESOLVED | © cite-only | unknown)
provenance           how we obtained it (fetch script, manual, pin, …)
description          short factual description
reliability_notes    free text; no numeric “truth score”
temporal_scope       current | historical | mixed | unknown
relevance            why it matters to the aggregator
archival_location    local path or “locator-only (no local copy)”
resource_tier_hint   N|C|A|S|H|X|unknown   (provisional; review may change)
related_source_ids   optional list (forks, mirrors, transcripts of video)
notes                caveats
created_at           ISO date of this record
updated_at           ISO date
```

### `source_type` (non-exhaustive)

```text
normative_prose
computational_morphology
dictionary
surface_inventory
frequency_list
corpus
wikipedia_article
web_page
pdf
book_or_scan
video
transcript
author_handout
poster_or_slides
community_forum
source_repository
project_audit
other
```

## Rules

1. Prefer one record per **pinned** computational version (npm version / git
   SHA), not one forever-live “latest”.
2. Mirrors of the same lineage (e.g. `slovnik` vs live `basic.json`) are
   **separate** source_ids with notes linking them.
3. License/rights must never be guessed; use `UNRESOLVED` / `unknown` /
   `© cite-only` as documented in `SOURCES.md` / inventory.
4. A transcript of a video is either:
   - a linked `related_source_id` of type `transcript`, or
   - fields on the video record — but ASR method must be explicit
     (`VIDEO_SOURCE_PROTOCOL.md`).
