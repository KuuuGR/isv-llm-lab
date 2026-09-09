# EXP-004 — authentic-corpus self-evaluation (SODA Task 029)

> How does the authentic Medžuslovjansky corpus score when evaluated
> against the same lexical resources, canonical evaluator and orthography
> audit used for generated model outputs?

Deterministic application of the **unchanged** EXP-004 evaluation stack
(`isv-eval` metrics, Task 008; Task-015 orthography audit) to the
authentic reference corpus itself. Resource-coverage evidence — **not**
linguistic-correctness claims, no composite score, no "corpus score".

Corpus: `phase2a-authentic-isv` v1 · SHA-256
`aaad28e43935a40313585d77a33bfc788d97e8d69b081f9486af74d52ca1a857`.

## Result table

| Dataset | Tokens | Canonical | Broader | Unresolved | Orthography out |
|---|---:|---:|---:|---:|---:|
| Combined authentic corpus | 8,096 | 80.50 % | 89.17 % | 19.50 % | 47 |
| Register 1 — literary / narrative | 770 | 95.97 % | 99.48 % | 4.03 % | 1 |
| Register 2 — artistic / poetic | 1,600 | 90.56 % | 100.00 % | 9.44 % | 0 |
| Register 3 — informative / encyclopedic | 5,717 | 75.72 % | 84.83 % | 24.28 % | 25 |

Tokens = lexical tokens (`isv-eval` denominator policy); Canonical =
(A+B)/lexical; Broader = (canonical-supported + exact alternative-resource
attestation)/lexical; Unresolved = C/lexical; Orthography out =
characters outside the official Interslavic inventory.

Full machine-readable metrics, per-register detail and the orthography
character-class breakdown: `corpus_selfeval.json` / `corpus_selfeval.md`
(regenerated deterministically by `scripts/selfeval_exp004_corpus.py`;
inputs are the gitignored local corpus files, so the generator needs a
local checkout with the corpus present).

## Descriptive interpretation (recorded, non-claims)

1. **The authentic corpus scores 80.5 % canonical / 89.2 % broader at
   the combined level.** The corpus is the reference point for reading
   model outputs: even authentic, human-produced Medžuslovjansky is not
   fully covered by the canonical resource — 19.5 % of its lexical tokens
   are unresolved (C) under `isv-eval`. A model reaching the corpus
   percentage is therefore not "as good as the corpus"; the corpus is
   **not** a perfect upper bound on Interslavic.
2. **Register differences are large and descriptive.** Register 1
   (narrative) is 95.97 % canonical; Register 2 (artistic) 90.56 %
   canonical but 100.00 % broader (every artistic surface is attested in
   the canonical or the audited alternative resources); Register 3
   (encyclopedic) is only 75.72 % canonical / 24.28 % unresolved — proper
   names, specialist gardening/agricultural terminology and common
   encyclopedic vocabulary are the thinnest part of the resource
   coverage. The combined corpus hides this variation.
3. **Generated outputs vs the corpus (descriptive comparison in
   `model_comparison.md`):** Phase-1 direct outputs average ≈ 76.5 %
   canonical; Phase-2A primed outputs ≈ 82.5 %; repeated primed
   ≈ 82.2 %. The corpus combined canonical (80.5 %) lies *between* the
   direct and primed model means, and primed outputs sit slightly above
   it. Broader coverage is closer: corpus 89.2 % vs primed outputs
   ≈ 88.8 %. Two consequences: (a) low *canonical* model coverage can
   partly arise from resource limitations, not only from model error —
   the authentic corpus itself is only 80.5 % canonical; (b) at the
   corpus level, canonical coverage alone does not separate authentic ISV
   from model output — an important reason the project never uses
   canonical coverage as a "valid Interslavic" claim.
4. **Orthography:** the authentic corpus is essentially clean under the
   audit (47 out-of-inventory characters in 58 459 bytes; 0 Cyrillic,
   0 Polish-specific; Register 3 contributes 7 other-Latin characters and
   18 unexpected non-letters — mostly URL/typographic remnants of the
   Wikipedia cleanup; Register 1 has 1; Register 2 has 0). Model outputs
   are much shorter documents (≈ 1 500 lexical tokens vs 8 096), so
   raw outside-inventory counts are not length-comparable; the point is
   that the *resource/corpus* does not explain orthographic contamination
   in model output. Nothing is "fixed": the corpus is measured exactly as
   presented to models.
5. **Cross-register composition (exploratory, not a quality score):**
   the three registers are lexically diverse — only 61 lexical surfaces
   (of 3 425 in the union) appear in all three; Register 3 alone has
   2 639 unique surfaces, and combining the registers expands the
   resource-supported vocabulary presented to models by ≈ 30 % over
   Register 3 alone. "Unique to one register" does not mean "incorrect".

## Method

- Each dataset is the exact byte sequence consumed by the project:
  `phase2a-authentic-isv-corpus.txt` is the combined file presented to
  models in Phase-2A Prompt 1 (including the three plain-text
  `=== REGISTER n: … ===` headers); the register rows are the three
  register component files used by `scripts/build_phase2a_corpus.py`
  (headers exist only in the combined file, so register boundaries are
  preserved exactly as established in Phase 2A).
- Evaluation runs the identical call the EXP-004 pipeline uses for model
  outputs: `python -m isv_eval.cli <file> --out <dir>` (unmodified
  evaluator), plus `isv_eval.orthography.scan_file`.
- The script re-runs deterministically; `--reuse-scratch` re-renders the
  reports from cached per-dataset `isv-eval` artifacts without re-running
  the evaluator. `.scratch/` holds those artifacts and is gitignored.
- Model-output comparison (`model_comparison.md`) reads the local
  EXP-004 rosters (`outputs/`, `phase2a/outputs/`, `repeats/outputs/` —
  gitignored) and is therefore generated only in a local checkout with
  the experiment data; it is descriptive resource-coverage comparison,
  never "distance from native quality".
