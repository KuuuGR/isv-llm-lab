# EXP-003 per-story curation

Per-story, explicit, human-reviewed alignment tables for the scaffold
generator (`scripts/build_exp003_scaffold.py`). Every entry is provenance-
bearing; nothing here invents an ISV word.

The tables are **story-derived** (they embed Polish surface tokens from the
copyrighted story) and are therefore **gitignored** — only this README is
committed. The dictionary (`basic.json`) is never modified for the scaffold.

Files (one per story under `curation/<story_id>/`):

| file | purpose | columns |
|---|---|---|
| `names.tsv` | proper names (all observed inflected forms) | `form<TAB>note` |
| `multiword.tsv` | multi-word expressions mapped as one unit | `expression<TAB>isv1,isv2<TAB>note` |
| `residual.tsv` | residual inflected forms not covered automatically | `form<TAB>isv1,isv2 | NONE<TAB>basis` |

`#` starts a comment line. Forms are normalized (NFC, lowercase) before
matching. `NONE` in the candidates column records "reviewed; no defensible
candidate found" so the decision is preserved instead of silently dropped.

Candidate provenance policy (DESIGN.md §7):

- Every ISV candidate is either a canonical `basic.json` headword whose
  Polish translation gloss matches the identified Polish lemma, or an explicit
  reviewer-judged equivalent recorded with its `basis`.
- Where the reverse index verifies the lemma (the ISV headword's `pl` gloss
  literally contains the Polish lemma), the `basis` records the lemma and the
  verified gloss.
- `reviewer-judged` marks a human choice; the chosen ISV form must still be a
  canonical dictionary headword.
- Entries are ordered most-specific-first; for one surface form the candidate
  order in the table is the order presented to the LLM.

`residual.tsv` generation: the pipeline marks a form "residual" when exact
reverse-index lookup and dictionary-verified lemma recovery both fail. The
table below is the auditable, human-reviewed completion of that residual for
`op-pl` (SODA Task 010).
