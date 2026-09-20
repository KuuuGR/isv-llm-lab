# Paper 1 — submission checklist

**Paper:** Paper 1 (EXP-004 Phase 2B corpus-priming study)  
**Manuscript:** `docs/research/exp004-phase2b/manuscript/`  
**Policy:** `docs/PUBLICATION_VERSIONING.md`  
**Intended tag (when submitting):** `paper1-submission-v1` — **do not create until submission**

Fill this checklist at freeze time. Leave blanks until then.

## Identity

| Item | Record at submission |
|---|---|
| Journal / venue | *Natural Language Processing* (Cambridge) — confirm |
| Submission date | |
| Corresponding author | Grzegorz R. Kulesza |
| Coauthor status | see `AUTHORSHIP_PENDING.md` |

## Exact versions

| Item | Path / identifier | Recorded value |
|---|---|---|
| Manuscript sources | `docs/research/exp004-phase2b/manuscript/latex/` | |
| Manuscript PDF | `…/latex/build/manuscript.pdf` | |
| Evidence map | `…/manuscript/EVIDENCE_MAP.md` | |
| Canonical experiment root | `experiments/exp004-modelscreen/phase2b/` | |
| Combined analysis | `…/phase2b/analysis/combined/` (`analysis.json`, tables) | |
| Corpus SHA-256 | priming corpus hash in combined analysis | |
| Source hashes | HIGH / LOW / UNSEEN `*.meta.json` | |
| Git commit (full SHA) | | |
| Git tag | `paper1-submission-v1` (create only when sending) | |

## Scientific freeze checks

- [ ] No claims changed relative to the frozen analysis artifacts
- [ ] Qwen LOW remains `INVALID — MODEL MISMATCH`
- [ ] Matched-six means still HIGH +7.39 / LOW +8.53 / UNSEEN +5.78 pp
- [ ] Numbers spot-checked against `EVIDENCE_MAP.md`

## Availability / disclosure wording (draft placeholders)

- [ ] **Data/code availability** text matches what is actually public vs
      gitignored (raw model outputs / copyrighted sources may be local-only)
- [ ] **Related-paper note:** Paper 2 (Grammar Aggregator) may share
      `isv-eval` / resource-policy infrastructure; disclose if both are under
      review or published
- [ ] Funding / competing interests / ethics placeholders resolved or honestly
      stated as none/N/A

## Tag command (for submission day only)

```bash
git tag -a paper1-submission-v1 -m "Paper 1 submission v1 — Natural Language Processing (Cambridge), YYYY-MM-DD"
git push origin paper1-submission-v1
```

Do **not** move or delete this tag after the journal has the package.
Later packages use `paper1-revision-v2`, etc.
