# Publication and repository versioning

**Status:** active convention (2026-09-20)  
**Scope:** this public repository as the single source of truth

## Principles

1. **One public repository.** `isv-llm-lab` remains the source of truth for
   experiments, analysis, research documentation, and manuscript development.
   Do **not** create a second/private research repository solely to hide
   manuscripts from reviewers.
2. **Public manuscript development is allowed.** Target venues for the current
   papers use single-anonymized review (e.g. *Natural Language Processing*,
   Cambridge), so reviewers may see this public repository. We do **not**
   rewrite git history or move drafts to private branches for anonymity.
3. **Immutable submission tags.** Each journal submission (and each later
   revision package that must be citable) is frozen with an **annotated,
   immutable** git tag pointing at the exact commit that contains the
   manuscript, analysis, and related materials as submitted.
4. **Ongoing work may coexist.** The repository may contain later research
   (e.g. Grammar Aggregator seed growth) that is **not** part of every paper.
   Tags define what counted for a given submission; they do not erase later
   commits.

## Tag naming (do not create tags until a real submission)

| Event | Tag pattern | Example |
|---|---|---|
| First submission of Paper 1 | `paper1-submission-v1` | first CUP NLP send |
| First submission of Paper 2 | `paper2-submission-v1` | when Paper 2 is ready |
| Later journal revision | `paperN-revision-vK` | `paper1-revision-v2` |
| Optional camera-ready | `paperN-camera-ready-v1` | if needed |

Rules:

- Tags are **immutable** (no moving/force-updating a published tag).
- Increment `vK` for each new frozen package sent to the journal.
- Do **not** rewrite or squash history “for presentation” before tagging.
- Prefer **annotated** tags (`git tag -a`) with a short message naming the
  journal and date.

**No submission tags exist yet.** Create them only at submission time.

## What a tag should freeze

At minimum, the tagged commit should include:

- the manuscript sources/PDF intended for that submission;
- the analysis/evidence artifacts the paper cites (or clear pointers to
  canonical experiment paths + hashes already recorded in the paper);
- any checklist file filled for that submission.

## Paper map

See [`docs/research/PAPERS.md`](research/PAPERS.md) for which directories belong
to Paper 1 vs Paper 2 and where submission checklists live.

## Related-paper disclosure

If two papers share data, evaluator infrastructure, or experimental regimes,
each submission checklist must record a short related-paper / shared-resource
note for the cover letter or data-availability statement.
