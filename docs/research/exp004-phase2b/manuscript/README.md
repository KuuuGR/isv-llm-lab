# EXP-004 Phase 2B — Manuscript (working draft)

**Paper ID:** **Paper 1** (see [`docs/research/PAPERS.md`](../../PAPERS.md))  
**Status:** working LaTeX draft (public repository development)  
**Not submission-ready** until authorship/funding/COI placeholders are resolved and remaining checklist items are complete.  
**Submission freeze:** use [`SUBMISSION_CHECKLIST.md`](SUBMISSION_CHECKLIST.md); intended tag `paper1-submission-v1` (**not created yet**).  
**Versioning policy:** [`docs/PUBLICATION_VERSIONING.md`](../../../PUBLICATION_VERSIONING.md)

## Target journal

Primary: **Natural Language Processing** (Cambridge University Press; formerly *Natural Language Engineering*)  
Also kept modular for later adaptation to *Machine Translation* (Springer) or TACL.

## Working title

**Corpus Priming in Polish-to-Interslavic Translation with Large Language Models: A Controlled Study Across Source Regimes**

## Paths

| Item | Path |
|---|---|
| LaTeX source | [`latex/main.tex`](latex/main.tex) |
| PDF build | [`latex/build/manuscript.pdf`](latex/build/manuscript.pdf) |
| Bibliography | [`latex/references.bib`](latex/references.bib) |
| Evidence map | [`EVIDENCE_MAP.md`](EVIDENCE_MAP.md) |
| Authorship pending | [`AUTHORSHIP_PENDING.md`](AUTHORSHIP_PENDING.md) |
| References needed | [`REFERENCES_NEEDED.md`](REFERENCES_NEEDED.md) |
| Submission checklist | [`SUBMISSION_CHECKLIST.md`](SUBMISSION_CHECKLIST.md) |

## Word count (texcount, current draft)

From `texcount -inc -total latex/main.tex`:

- Words in text: **6912**
- Words in headers: **393**
- Words outside text (captions, etc.): **134**
- Combined: **~7.4k** (first draft; journal approximate band is 8–12k — optional expansion remains for revision)
- Abstract: ~300 words (within target)

Re-run:

```bash
cd latex && texcount -inc -total main.tex
```

## Build

```bash
cd docs/research/exp004-phase2b/manuscript/latex
latexmk -pdf -outdir=build main.tex
cp -f build/main.pdf build/manuscript.pdf
```

Requires a TeX Live install with `pgfplots`, `natbib`, `booktabs`, etc.

## Unresolved before submission

1. Confirm/exclude coauthor **Dr Jacek Kapała** (`AUTHORSHIP_PENDING.md`)
2. Funding statement
3. Competing-interests statement
4. Interslavic language-description bibliography (`REFERENCES_NEEDED.md`)
5. Optional: expand body to full 8–12k words if the editor expects the upper band
6. Human proofreading of all numbers against `EVIDENCE_MAP.md`

## Scientific guardrails (preserved)

- No claim that priming universally improves translation quality
- No causal attribution to overlap/length/genre
- No model ranking / “best model”
- Qwen LOW remains `INVALID — MODEL MISMATCH`
- Matched-six means: HIGH **+7.39**, LOW **+8.53**, UNSEEN **+5.78** pp
- Canonical experiment root remains `experiments/exp004-modelscreen/phase2b/`

## Corresponding author (confirmed)

Grzegorz R. Kulesza  
Department of Medical Biophysics  
Medical University of Bialystok  
Email: grzegorz.kulesza@umb.edu.pl
