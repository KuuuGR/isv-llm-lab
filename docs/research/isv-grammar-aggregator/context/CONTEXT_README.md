# Context bundle — ISV Grammar Aggregator

**Extraction / package date:** 2026-09-20

## What this bundle is

A **local, self-contained mirror** of the minimum project documents needed to
understand and operate the Grammar Aggregator research track without loading
the entire repository documentation tree.

## Why it exists

Operators and future contributors should be able to work inside
`docs/research/isv-grammar-aggregator/` with:

- resource-policy language,
- grammar-audit conflicts,
- intervention-ladder framing,
- relevant decisions,

without opening dozens of unrelated experiment reports.

## Authoritative source rule

> `docs/research/isv-grammar-aggregator/` is the working research package;
> canonical project policies remain authoritative in their original locations.

If a context copy disagrees with a canonical file, **the canonical file wins**.
Update the context bundle; do not “fix” policy by editing only the extract.

## Contents

| File | Kind | Canonical path |
|---|---|---|
| [`GRAMMAR_AUDIT.md`](GRAMMAR_AUDIT.md) | **Full copy** | `docs/GRAMMAR_AUDIT.md` |
| [`RESOURCE_POLICY.md`](RESOURCE_POLICY.md) | **Curated extract** | `docs/RESOURCE_POLICY.md` |
| [`TRANSLATION_METHOD_RELEVANT.md`](TRANSLATION_METHOD_RELEVANT.md) | **Curated extract** | `docs/translation-method.md` |
| [`RESEARCH_ROADMAP_RELEVANT.md`](RESEARCH_ROADMAP_RELEVANT.md) | **Curated extract** | `docs/research-roadmap.md` |
| [`DECISIONS_RELEVANT.md`](DECISIONS_RELEVANT.md) | **Curated extract** | `docs/DECISIONS.md` |
| [`RESEARCH_NOTES_RELEVANT.md`](RESEARCH_NOTES_RELEVANT.md) | **Curated extract** | `docs/RESEARCH_NOTES.md` |

Each curated extract header records:

- that it is a curated extract,
- the canonical path,
- the extraction date,
- the included line ranges,
- that original wording is preserved (not rewritten).

## How to update

1. Edit or re-read the **canonical** file under `docs/`.
2. Re-extract or re-copy into this directory (preserve wording; refresh
   line-range headers and the extraction date).
3. Note the update in the research-track `TODO.md` or a short changelog
   entry if the extract scope changed.
4. Never promote a context-only edit into “new policy” without updating the
   canonical document through the normal project process.

## What is intentionally omitted

- Full EXP-004 Phase 1/2A/2B quantitative tables (live under
  `experiments/exp004-modelscreen/` and the research hub).
- Full LESSONS.md narrative (lessons are cited from inventory/protocols when
  needed).
- `SOURCES.md` wholesale (resource inventory already summarizes pins; open
  `SOURCES.md` at repo root when licensing detail is required).
