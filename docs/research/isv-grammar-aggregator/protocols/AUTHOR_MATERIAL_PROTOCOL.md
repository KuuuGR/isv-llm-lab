# Author / poster / slide material protocol

**Status:** design protocol.

Covers materials from language authors, maintainers, community organizers,
presentation slides, posters, and downloadable handouts.

## Required recording

```text
author
date                      publication or event date | unknown
edition_or_version        string | unknown
material_role             normative | explanatory | historical | informal | unknown
explicit_rule_stated      true | false | mixed
form_attested_elsewhere   true | false | unknown
venue                     conference / site / workshop | unknown
license_rights            documented | © cite-only | unknown
```

## Rules

1. **Do not infer normative authority merely from the author’s identity.**
   Even Steen-authored material must be located and quoted; slides may be
   simplified or outdated relative to the grammar pages.
2. Distinguish **explicit rule slides** from **illustrative example slides**.
3. Posters/handouts often lack versioning — mark `edition_or_version=unknown`
   rather than guessing.
4. If the same author maintains Tier-N pages and a slide deck, link
   `related_source_ids` but evaluate each claim on its own excerpt.
5. Community organizer materials default to Tier X/S until curated.

## Intake path

Same as general intake; prefer PDF hash + page number in `location`.
