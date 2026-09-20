# Paper 2 — submission checklist

**Paper:** Paper 2 (ISV Grammar Aggregator / language knowledge base)  
**Research package:** `docs/research/isv-grammar-aggregator/`  
**Manuscript:** not started  
**Policy:** `docs/PUBLICATION_VERSIONING.md`  
**Intended tag (when submitting):** `paper2-submission-v1` — **do not create until submission**

Fill this checklist when a manuscript exists and is ready to freeze.

## Identity

| Item | Record at submission |
|---|---|
| Journal / venue | |
| Submission date | |
| Corresponding author | |
| Coauthor status | |

## Exact versions

| Item | Path / identifier | Recorded value |
|---|---|---|
| Manuscript sources | *(to be added)* | |
| Research package | `docs/research/isv-grammar-aggregator/` | |
| Fact seed (if cited) | `…/seed/` + `seed/generated/facts.json` | |
| Seed counts | 48 total / 47 accepted / 1 needs_review (as of 2026-09-20 checkpoint) — update if changed | |
| Relevant evaluator / resource policy pins | `docs/RESOURCE_POLICY.md`, morphology pin | |
| Git commit (full SHA) | | |
| Git tag | `paper2-submission-v1` | |

## Scientific freeze checks

- [ ] No silent resolution of open conflicts (e.g. CL-001…006;
      `ga:noun.athematic.archaic_label` remains `needs_review` unless newly evidenced)
- [ ] Provenance present for every cited fact
- [ ] Claims remain hypotheses where untested

## Availability / disclosure wording

- [ ] Data/code availability matches public vs gitignored materials
- [ ] **Related-paper note:** Paper 1 (EXP-004 Phase 2B corpus priming) may
      share evaluator/resource infrastructure and project framing; disclose
      overlap
- [ ] Licensing limits (dictionary UNRESOLVED; Steen cite-only) stated honestly

## Tag command (for submission day only)

```bash
git tag -a paper2-submission-v1 -m "Paper 2 submission v1 — VENUE, YYYY-MM-DD"
git push origin paper2-submission-v1
```

Later packages: `paper2-revision-v2`, etc. Do not mutate tags.
