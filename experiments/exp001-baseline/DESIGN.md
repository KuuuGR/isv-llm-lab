# Experiment 001 — Baseline: Unconstrained LLM Translation (Polish → Interslavic)

Status: **RUN COMPLETED (Task 003, 2026-08-31).** Seven conditions evaluated
on the complete Polish story; results in `outputs/comparison.md` and
`docs/EXPERIMENTS.md` § EXP-001. This document is the specification that
Task 002 implemented; §7 records how the harness was built, and §3 lists the
actual seven conditions used.

---

## 1. Objective

Establish a quantitative baseline for how well current LLMs produce
Interslavic when given no external constraint, specifically measuring how much
of their output is justifiable by the established Interslavic lexical and
morphological resources. Later experiments will compare this baseline against a
constrained-generation system.

Null hypothesis to keep in mind: the constrained system may not outperform
direct LLM translation. The baseline must be trustworthy before any comparison.

## 2. Input

- One complete **Polish short story**, provided by the Project Owner.
- The **entire story is one translation task** per model. Do NOT translate
  sentence-by-sentence. Rationale: preserve context, narrative consistency,
  terminology, character names, stylistic consistency across the text.
- Sentence splitting happens only **after** translation, for analysis.
- **Source vs prompt separation (Task 003.1 rule for future experiments):**
  the source corpus should contain *only* the actual Polish story. Translation
  instructions (e.g. `Przetłumacz to opowiadanie na medžuslovjansky…` or the
  standardized prompt) belong in the **prompt**, not inside the source corpus.
  Conceptually:
  ```
  source.txt = Polish story only
  prompt.txt = translation instructions + source text
  ```
  Experiment 001 is not retroactively modified: its supplied `op-pl.txt`
  contained an embedded instruction line and markdown fence, which were hashed
  and evaluated as-is (documented in `input/source.meta.json`). As a result,
  raw file size is not a valid comparison of translation length for
  Experiment 001 — byte sizes are recorded for input integrity only.

## 3. Model outputs

Each of the following models receives the same complete source text
independently (no cross-model interaction):

1. ChatGPT (`op-gpt.txt`)
2. Gemini (`op-gemini.txt`)
3. Claude (`op-claude.txt`)
4. DeepSeek (`op-deepSeek.txt`)
5. Bielik (`op-bielik.txt`)
6. Grok (`op-grok.txt`)
7. GPTs — "Interslavic — Medžuslovjansky Language Teacher" (`op-gpt-isvt.txt`,
   `condition_type = specialized_custom_gpt`, kept separate from ordinary
   ChatGPT; internal system instructions not available)

One run per model. A **different model version is a different experimental
condition** and gets its own run, even if it is the "same" model name.
All outputs were generated externally: model versions, generation dates,
providers (for Bielik/Grok) and prompts are recorded as `unknown`
(`prompt_status = unknown`); none can be confirmed to have used
`prompt_template.txt`.

## 4. Reproducibility & storage

Every run is stored under:

```
experiments/exp001-baseline/
  input/
    source.txt                     # the story (fixed filename, hashed)
    source.meta.json               # provenance: title/author/date/license note
  outputs/
    <run_id>/
      prompt.txt                   # the exact prompt sent
      output.txt                   # RAW model output, byte-for-byte
      meta.json                    # structured metadata (below)
      tokens.json                  # tokenization + analysis results (generated later)
```

`<run_id>` = `YYYY-MM-DD__<provider>__<model>__<model_version>`.

`meta.json` schema:

```json
{
  "experiment_id": "exp001",
  "date": "2026-08-31",
  "provider": "openai",
  "model": "chatgpt",
  "model_version": "exact version string given by the API",
  "prompt": "path to prompt.txt",
  "source_text": "path to source.txt",
  "output_text": "path to output.txt",
  "parameters": {"temperature": null, "seed": null, "notes": ""}
}
```

Rules:

- Raw outputs are preserved byte-for-byte; never regenerate or overwrite.
- Never edit an existing `outputs/<run_id>/` directory.
- A repeated run under the same condition gets a fresh run id (e.g. a `-2`
  suffix) — do not overwrite.
- Store inputs/outputs on a local or data path if copyright is a concern; do
  not commit the story or model outputs to git without clearing rights.

## 5. Analysis pipeline

1. **Tokenization.** Split the model output into tokens (surface forms). Keep
   the sentence/paragraph context for every token. Implemented: conservative
   stdlib-regex tokenizer (paragraph = blank-line block, sentence = split
   after `. ! ? …`; hyphenated/apostrophe compounds stay single tokens).
   Tokens carry both surface and normalized forms; Cyrillic is transliterated
   via `@interslavic/translit` before matching. See D-013/D-014.
2. **Classification** of each token into one of four buckets (below).
3. **Metric computation** and **artifact generation** (unresolved-form lists).

### A. Exact lexical match

Is the surface form **directly present** in the relevant Interslavic data?

Reference data (snapshot, `data/dictionary/`):

- `basic.json` `wordList` (19,101 rows) — headwords plus `addition` variants.
- A **full-form lexicon** generated once from `@interslavic/morphology` via its
  paradigm dumper (or built during the pipeline): every inflected form for every
  dictionary lemma, in both Latin and Cyrillic. This is what makes
  "exact lexical match" meaningful for inflected text, not just headwords.

Match is case-insensitive and script-normalized.

### B. Morphological validity

If the surface form is not a direct lexical match, can it be **associated with
a known Interslavic lemma and recognized/generated as a valid inflected form**?

Procedure (lemma-driven, NOT surface-POS-driven — `detectPos`-style heuristics
are unreliable for this):

1. Collect candidate lemmas whose paradigms could contain the surface form:
   - reverse lookup via the generated full-form lexicon (primary),
   - plus a lemma search over the dictionary headwords for the stemmed form.
2. Ask the morphology engine to generate the candidate's paradigm(s):
   - `@interslavic/morphology` (JS, primary backend; `inflect(lemma)`),
   - optionally cross-checked against the Rust engine later.
3. If the surface form is in any generated paradigm, classify VALID and record
   the lemma(s), UPOS, and morphological features (CoNLL-U `feats`) that justify it.

Example (the intended semantics of the task's example pair):

```
dictionary lemma: brat
generated form:   brata      → VALID (gen.sg. / acc.sg. of brat)
```

⚠️ **Correction to the task's worked example**: the pair `more → morem`
does NOT reproduce with the actual resources. The dictionary headword for "sea"
is `morje` (instrumental `morjem`); the lemma `more` is an n-stem neuter whose
instrumental singular is `morętem`/`morętom`. `morem` is not a generated form
and not a headword — verified live against **both** morphology engines
(`@interslavic/morphology@0.1.2` and the legacy `@interslavic/utils@3.4.0`).
See `docs/GRAMMAR_AUDIT.md`. The metric's *procedure* is unchanged; only the
example must be corrected.

Design decision (D-004/D-006): do not classify an inflected form as unknown
merely because it is not a dictionary headword.

### C. Unresolved forms

Forms that cannot be associated with an accepted Interslavic lemma or
morphological form by steps A/B. This is the primary negative metric.

### D. Suspicious forms (preserved for manual analysis)

Every unresolved form is retained with enough context for later manual review —
no language-origin classifier is built in Task 001. At minimum record:
surface form (normalized + original), sentence/context, position, model,
lemma candidates considered, and why each failed (missing headword vs. failed
morphological association).

## 6. Metrics

| Metric | Definition |
|---|---|
| `total_tokens` | number of analyzed tokens — the *lexical* tokens (word-like), excl. punctuation/numbers per the stated convention |
| `exact_dictionary_coverage` | tokens in bucket A / `total_tokens` |
| `morphologically_valid_coverage` | **(A + B) / `total_tokens`** (the important number: headword-or-justified; reconciled with the task formula — see D-015) |
| `unresolved_forms` | count of bucket C tokens (and rate = C / total) |

Since SODA Task 008 (two-layer resource policy; spec
`docs/RESOURCE_POLICY.md`) the same evaluator additionally reports:

| Metric | Definition |
|---|---|
| `canonical_supported_tokens` / `canonical_coverage` | the A+B set under the **canonical coverage** name (`morphologically_valid_coverage` is kept unchanged for historical comparability and equals `canonical_coverage`) |
| `broader_resource_supported_tokens` / `broader_resource_supported_coverage` | canonical-supported tokens plus lexical tokens with an **exact surface attestation** in the audited alternative resources (`isv.dic`, `interslavicfreq` wordlists), divided by `total_tokens` — an *evidence estimate*, never a validity claim |
| `unresolved_tokens` | bucket C (identical to `unresolved_forms`) |

Per token, `tokens.json` now also records `canonical_status`, the
`resource_evidence` list (layer/source/kind) and `broader_resource_supported`,
so every counted or excluded form can be justified.

Denominator policy (repeated in every report's `denominator_policy`): coverage
denominators are lexical tokens; punctuation and numbers are excluded from all
vocabulary coverage. `tokens_total` reports every token (lexical +
non-lexical) for completeness.

Also retained as artifacts:

- List of unresolved forms: surface form, normalized form, sentence/context,
  model, count/frequency within the text.
- Summary table per model: A / B / C / D counts and rates.

The evaluation distinguishes:
- "not literally present as a headword" (still potentially VALID), from
- "cannot be justified by the available Interslavic lexical/morphological
  resources" (bucket C).

The second is the important metric.

## 7. Implementation notes (Task 002 — implemented)

Status: the harness is implemented; the experiment is not run.

- **Runtime split.** Python (`isv_eval` package, stdlib-only) does tokenization,
  lookup, classification, metrics and serialization. Morphology is a **Node
  stdio backend** (`src/morphology_backend/backend.mjs`, pinned
  `@interslavic/morphology@0.1.2` + `@interslavic/translit@0.1.0`, committed
  `package-lock.json`) exposing exactly two line-delimited-JSON operations:
  `inflect` (lemma → paradigm) and `translit` (Cyrillic → ISV Latin).
- **Lexicon.** `scripts/fetch_dictionary.py` snapshots `basic.json` + writes a
  manifest (URL, retrieved_at, SHA-256, size, row count, schema,
  license_status=UNRESOLVED). `scripts/generate_lexicon.py` expands every row
  (POS + `addition` hints; comma-variants split; `(+N)` annotations filtered)
  into a 320,824-entry TSV: headwords + full paradigms. Both artifacts stay
  gitignored (license).
- **Classification.** A = exact match in the full-form lexicon (headwords or
  paradigms; multiple lemmas preserved; folded etymological matches flagged).
  B = bounded live fallback: re-inflect candidate dictionary lemmas (shared
  3–4-char prefix, ≤150 candidates, dictionary POS as hint) and match. With a
  complete lexicon B rarely fires — it is the safety net for lexicon gaps.
  C = unresolved; every C token carries sentence context + candidates +
  `review: true` (the D convention: manual review, no automatic language
  classification).
- **Metrics.** `morphologically_valid_coverage = (A + B) / lexical_tokens`
  (the important number: "headword-or-justified"). Denominator policy is
  emitted in every report; see §6.
- **Tests.** 31 pytest cases: normalization (NFC, folding, Cyrillic), tokenizer
  (paragraphs, sentences, punctuation, numbers, hyphenation), classifier
  (A/B/C, folded matches, multi-lemma, fallback), and an end-to-end smoke run
  on `tests/fixtures/smoke_corpus.txt` with committed expected numbers.
- **`interslavicfreq`** is deliberately NOT integrated into the baseline
  metrics (optional plausibility signal for later). Hunspell `isv.dic` also
  remains a future independent validity signal.
- **Two-layer resource policy (SODA Task 008)** — the evaluator now also
  reports `canonical_coverage` and `broader_resource_supported_coverage`:
  `data/dictionary/audit/` resources (`isv.dic` exact surfaces,
  `interslavicfreq` wordlists, `slovnik` historical snapshot) are loaded as a
  separate evidence layer (`src/isv_eval/evidence.py`). A/B/C semantics are
  untouched; alternative-resource hits are never promoted into A/B; only
  exact-surface attestation counts toward the broader tier; orthographic
  variants and historical presence are recorded as provenance but never count.
- `more → morem` is NOT hard-coded anywhere; it is used only as the audit
  warning. A token `morem` evaluates to C against the current lexicon, and
  `morje`/`morjem` evaluate to A (verified live).

## 8. Future experiment (documented, NOT implemented)

Compare the baseline against a **constrained system**:

```
Baseline                          Constrained
Polish                             Polish
  ↓                                   ↓
LLM                                  LLM analysis
  ↓                                   ↓
Interslavic                       lemmas + grammatical features
                                       ↓
                                   Interslavic dictionary
                                       ↓
                                   candidate selection
                                       ↓
                                   optional synonym / frequency / intelligibility ranking
                                       ↓
                                   LLM contextual choice
                                       ↓
                                   deterministic morphology
                                       ↓
                                   validation
                                       ↓
                                   Interslavic
```

Critical hypothesis to test:
> Restricting vocabulary and delegating morphology to deterministic linguistic
> software may reduce the tendency of LLMs to produce language-specific Slavic
> forms that are not established Interslavic.

This must be measured with the same metrics as the baseline (identical analysis
pipeline), so the two conditions are directly comparable.
