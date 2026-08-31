# EXP-002 Pilot — Final Report (SODA Task 006.2)

Date: 2026-08-31
Status: **PILOT EXECUTED FOR ALL SEVEN CONDITIONS — ANALYSIS COMPLETE**

This report finalizes the EXP-002 dictionary-guided revision pilot. It reports
the before/after results, the improved regression bookkeeping (full
evaluator-state transition matrix), candidate usage, the `interslavicfreq`
discrepancy, the Bielik no-change case, the central-hypothesis assessment, and
exactly one recommendation for the next task.

The report intentionally does **not** claim linguistic correctness: all
categories below are evaluator-state transitions of `isv-eval` (A = exact
dictionary match, B = morphologically valid, C = unresolved), computed with the
**same evaluator** as EXP-001. Raw model outputs are immutable experimental
artifacts; this report never modifies or quotes them beyond what the local
comparison artifacts already contain.

---

## 1. Experiment status

The EXP-002 pilot was executed for all seven EXP-001 conditions. All seven
runs were verified complete and intact:

- input package (`meta.json`, `original.txt`, `prompt.txt`, `candidates.json`),
- output package (`meta.json`, `revised.txt`),
- evaluator artifacts (`before/`, `after/`), comparison (`comparison.json`,
  `comparison.md`).

SHA-256 integrity was re-checked for every artifact (original copy vs input
`meta.json`; prompt vs input `meta.json`; revised vs output `meta.json`).
**7/7 runs pass.** Nothing was missing; nothing was reconstructed. The
revision prompt, candidate data, and original outputs were not modified.

## 2. Before/after results (complete table)

| Model | Baseline | Revised | Δ pp | Unresolved tokens | Unique unresolved | Lexical tokens |
|---|---:|---:|---:|---:|---:|---:|
| ChatGPT | 75.95% | 77.20% | **+1.25** | 366 → 347 | 189 → 184 | 1471 → 1471 |
| Claude | 73.55% | 74.83% | **+1.28** | 393 → 374 | 197 → 195 | 1486 → 1486 |
| Gemini | 71.72% | 72.60% | **+0.88** | 416 → 403 | 197 → 190 | 1472 → 1472 |
| Grok | 76.56% | 77.51% | **+0.95** | 345 → 331 | 176 → 176 | 1561 → 1561 |
| GPTs — ISV Teacher | 79.83% | 80.35% | **+0.53** | 307 → 299 | 175 → 173 | 1477 → 1477 |
| DeepSeek | 74.42% | 74.77% | **+0.35** | 366 → 361 | 176 → 173 | 1475 → 1475 |
| Bielik | 55.48% | 55.48% | **+0.00** | 695 → 695 | 335 → 335 | 1561 → 1561 |

Six of seven models improved evaluator coverage (Δ +0.35 to +1.28 pp).
Lexical token counts are identical in every run (Δ = 0), so the whole-document
constraint was respected at the token level by all seven models.

## 3. Transition analysis (improved regression bookkeeping)

`scripts/compare_exp002.py` now computes a **token-aligned evaluator-state
transition matrix** (LCS alignment of lexical tokens, before → after class).
All nine transitions are reported per run in `comparison/<run>/comparison.json`
and `comparison.md`. These are evaluator-state transitions only; they carry no
linguistic correctness claim.

| Model | A→A | A→B | A→C | B→A | B→B | B→C | C→A | C→B | C→C |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Claude | 1089 | 0 | **3** | 0 | 1 | 0 | 22 | 0 | 371 |
| DeepSeek | 1064 | 0 | **0** | 0 | 1 | 0 | 5 | 0 | 361 |
| Gemini | 1054 | 0 | **0** | 0 | 1 | 0 | 13 | 0 | 403 |
| ChatGPT | 1151 | 0 | **2** | 0 | 3 | 0 | 21 | 0 | 345 |
| GPTs — ISV Teacher | 1213 | 0 | **0** | 0 | 2 | 0 | 8 | 0 | 299 |
| Bielik | 862 | 0 | **0** | 0 | 4 | 0 | 0 | 0 | 695 |
| Grok | 1120 | 0 | **7** | 0 | 0 | 0 | 21 | 0 | 324 |
| **Total** | — | 0 | **12** | — | — | 0 | **90** | 0 | — |

Notes:

- **C→A = 90 token resolutions**, **A→C = 12 token regressions**, **B→C = 0**,
  **C→B = 0**. The B bucket is nearly empty in these texts (1–4 tokens per
  run), so the morphology fallback contributes essentially nothing measurable;
  coverage is effectively A-coverage.
- The previous bookkeeping ("resolved unique forms") counted a form as
  *resolved* when it was no longer C in the revised text — which includes
  forms that were merely re-spelled into **another C form** (C→C), e.g.
  `sěli → seli`, `sědeli → sedeli`, `reći → reci`, `řekl → rekl`. The
  transition matrix separates genuine resolutions (C→A) from C→C rewrites.

## 4. Candidate usage

Per selected unresolved form (30 per run), the comparison now records: the
supplied surfaces, which of them appear in the revised output, whether the
evaluator accepts them, whether the original form disappeared, and which
surfaces actually replaced it at its aligned positions. This makes explicit
the difference between *the model used a supplied candidate* and *the model
produced a form that happens to be accepted by the evaluator*: "accepted" is a
surface-level overlap; "targeted adoption" is a supplied surface found at the
position of the original form.

| Model | supplied surfaces | used in revised | newly introduced by revision | accepted by evaluator | targeted adoptions (accepted) |
|---|---:|---:|---:|---:|---:|
| Claude | 32 | 23 | 5 | 5 | 7 (4) |
| DeepSeek | 26 | 21 | 5 | 5 | 5 (2) |
| Gemini | 41 | 20 | 6 | 7 | 6 (4) |
| ChatGPT | 40 | 23 | 6 | 7 | 6 (6) |
| GPTs — ISV Teacher | 45 | 24 | 5 | 7 | 5 (4) |
| Grok | 42 | 23 | 5 | 6 | 4 (4) |
| Bielik | 47 | 20 | **0** | 2 | **0 (0)** |

Interpretation:

- Every revising model adopted **4–7 supplied surfaces as targeted
  replacements** at the positions of selected forms; Bielik adopted none.
- "Newly introduced by revision" (present in revised, absent from original) is
  the cleanest signal of *using* a supplied candidate: 5–6 surfaces per
  revising model, 0 for Bielik.
- The "accepted" count includes surfaces that were already present in the
  original text (unchanged, already A/B), so it overstates model-introduced
  acceptance; targeted adoptions are the conservative number.
- Targeted adoptions that the evaluator **accepted** almost always coincide
  with canonical dictionary forms (`ne`, `vse`, `prababica`, `primiŕje`,
  `męl/męla/meli`, `mel/mela/meli`, `sto`, `sebe`, `dna`, `drugy`,
  `dostatȯčno`). Targeted adoptions the evaluator **rejected** are alternative-
  resource forms invisible to the canonical evaluator (`seli`, `sedeli`,
  `reci`, `rekl`, `dejstvitelno`, `dalše`, `gledeči`) — see §6.
- Bielik's "accepted = 2" reflects surfaces already present and A/B in its
  unchanged text (`odgovor`, `odgovoriti`); no candidate was newly used.

Forms replaced without a supplied candidate (flagged deterministically):
Claude `različnih`, DeepSeek `pozajmili`, ChatGPT `měli`, `pozajmili`,
`skupaj`. All other runs had none.

## 5. Regression analysis (A→C and B→C)

**B→C regressions: 0 in all seven runs.**

**A→C regressions: 12 tokens total, in three models.**

Claude (3) — non-supplied spellings:

| form → replacement | count |
|---|---:|
| `različja` → `různja` | 1 |
| `različna` → `různa` | 1 |
| `različni` → `různi` | 1 |

Grok (7) — non-supplied spellings:

| form → replacement | count |
|---|---:|
| `iměl` → `imel` | 1 |
| `različni` → `různčni` | 2 |
| `različny` → `různčny` | 3 |
| `različnyh` → `různčnyh` | 1 |

ChatGPT (2) — **supplied-candidate overgeneralization**:

| form → replacement | count |
|---|---:|
| `někogda` → `někdy` | 1 |
| `čto` → `što` | 1 |

Mechanisms differ:

- **Grok and Claude** changed valid `različ-*` forms into `růz-*`/`různč-*`
  spellings that were **not among the supplied alternatives**. This is the
  clearest compliance failure: the models introduced new vocabulary despite
  the constraint.
- **ChatGPT** applied **supplied** candidates (`někdy`, `što` — both supplied
  for the *selected* forms `někdy` and `što`) to positions where the original
  already contained the *valid* forms `někogda` (A) and `čto` (A). This is
  candidate overgeneralization: correct per-rule use of a supplied surface,
  but at the wrong (already-valid) position. These two regressions were **not
  visible** to the old unique-form bookkeeping because `někdy` and `što` were
  already unresolved elsewhere in the text — the improved token-aligned
  bookkeeping is what exposed them.

## 6. `interslavicfreq` discrepancy

**Which forms.** Supplied from `interslavicfreq`, adopted by a model as a
replacement, and **rejected** by the evaluator:

| replacement | supplied for | runs (count) |
|---|---|---|
| `seli` | `sěli` | Claude ×2, DeepSeek ×2, Grok ×2 |
| `sedeli` | `sědeli` / `seděli` | Claude ×2, ChatGPT ×4 |
| `reci` | `reći` | DeepSeek ×2, GPTs-ISV Teacher ×2 |
| `rekl` | `řekl` | Gemini ×6 |
| `dejstvitelno` | `dējstvitelno` | Gemini ×4 |

Beyond these, a broad class of surfaces attested in `interslavicfreq` that were
already C in the original text stayed C after revision (`rekla`, `bojala`,
`dokazano`, `prestala`, `prestal`, `črez`, `gde`, `z`, `nih`, `jazyky`, …) —
113 "used but not accepted" instances across the seven runs. Accepted
`interslavicfreq` surfaces (`dna`, `mela`, `sebe`) were coincident with
canonical dictionary forms; their acceptance does not depend on
`interslavicfreq`.

**Representation in `interslavicfreq`.** Two kinds, both recorded per
candidate:

- `alternative_resource`: verbatim **surface wordform** entries in the
  `small_isv` wordlist, with `cB` = per-billion frequency (log scale, more
  negative = rarer; e.g. `seli`/`rekla` cB≈−619, `dejstvitelno` cB≈−650).
- `orthographic_variant`: **not** a verbatim list entry; recovered by
  diacritic-stripped matching inside the frozen frequency data
  (`wordlist=None`, `cB` recorded).

They are surface wordforms, not lemmas. Some are homographic without
disambiguation in the frequency data (e.g. `seli` = past of "sit down" vs 3sg
present of "settle"); `interslavicfreq` carries no POS/paradigm tags.

**Why the evaluator does not recognize them.** The `isv-eval` evaluator is
strictly canonical-dictionary-driven: bucket A requires an exact or
etymological-folded hit in the generated full-form lexicon
(`data/dictionary/basic.json` + `lexicon.tsv`); bucket B requires the
morphology engine to generate the surface from a **prefix-matching canonical
lemma** (`candidate_lemmas`). Verified per form:

- `rekl` / `reci`: the lemma `reći` is **absent from the canonical
  dictionary**; candidates are only `reklama`, `recept`, … so the past form of
  "to say" cannot be generated.
- `bojala`: the canonical lemma `bojati sę` is excluded from lemma-driven
  morphology because it is a multi-token lemma (reflexive `sę`); candidates
  are only `boj`, `boja`, `bojaznь…`.
- `dalše`: candidates `daleko`/`daleky`/`dalj` do not generate the comparative.
- `dejstvitelno`: **no canonical lemma starts with `dej`** → candidate list is
  empty and the B fallback never runs.
- `seli` / `sedeli`: prefix lemmas (`seler`, `sedlo`, `sedm`…) do not generate
  these surfaces.

**Integration issue vs resource-layer difference.** This is an
**evaluator/resource integration gap by design**: the EXP-001 evaluator was
deliberately scoped to the canonical dictionary (reproducibility decision),
and alternative resources were used only as post-hoc evidence (Task 005) and
EXP-002 candidate sources — the two layers were never reconciled. The
discrepancy is also a **resource-layer difference**: `interslavicfreq` is a
surface-frequency corpus (no lemma/paradigm linkage), while the canonical
dictionary is a headword + generated-paradigm system. The evidence does not
decide which layer "should" win: it shows only that the two layers disagree
about these forms. Nothing here is an error in `interslavicfreq` and nothing
is a bug in the evaluator relative to its documented policy. Whether to
reconcile the layers is a decision for the next task (see §11); the canonical
dictionary was **not** modified.

## 7. Model behavior (descriptive)

All of the following are evaluator-coverage observations, not quality rankings.

- **ChatGPT** — largest clean-looking gain (+1.25 pp), 21 C→A resolutions,
  6/6 targeted adoptions accepted (highest acceptance rate), and the **only**
  run whose A→C regressions (2) come from supplied-candidate
  overgeneralization rather than invented spellings. Flagged without-candidate
  replacements: `měli`, `pozajmili`, `skupaj`.
- **Claude** — largest absolute gain (+1.28 pp), 22 C→A, adopted 7 candidates
  (4 accepted), but introduced 3 A→C regressions with non-supplied `růz-*`
  spellings. Also transliterated `može` to Cyrillic `може` (9 tokens) — an
  A→A style change, not a coverage change.
- **Grok** — solid gain (+0.95 pp), 21 C→A, but the **highest number of A→C
  regressions (7)**, all from non-supplied `různč-*`/`imel` spellings; its
  unique unresolved count did not drop (176 → 176) because the gains and
  regressions cancel at the form level.
- **GPTs — ISV Teacher** — highest baseline (79.83%) and lowest unresolved
  rate (307/299); small clean gain (+0.53 pp), 0 regressions, 5 adoptions
  (4 accepted).
- **DeepSeek** — smallest gain (+0.35 pp), 5 C→A, 0 regressions, 5 adoptions
  (2 accepted). Flagged without-candidate replacement `pozajmili`.
- **Gemini** — clean gain (+0.88 pp), 13 C→A, 0 regressions, 6 adoptions
  (4 accepted); the `rekl`/`dejstvitelno` adoptions are rejected by the
  evaluator (§6).
- **Bielik** — no revision (see §8).

## 8. Bielik (no-change case)

Verified byte-level: the revised text is the original with **formatting-only**
changes.

- Lexical token sequences are **identical**: 0 positional diffs, 0 added
  surfaces, 0 removed surfaces (1561 lexical tokens before and after).
- Changes are limited to layout: removal of the leading blank line, removal of
  the 33 leading `- ` dialogue markers, and re-indentation of dialogue
  paragraphs (4-space prefixes added/removed).
- No selected form was replaced; no supplied candidate was newly introduced
  (`newly introduced by revision = 0`); no lexical or semantic change is
  detectable at the token level.

The model effectively did **not** execute the revision task. Hypotheses
(clearly labeled, no claim about internal causes):

- H1: the model returned its input nearly verbatim (echo / truncated
  generation).
- H2: the model interpreted the task as satisfied by reformatting the text.
- H3: the whole-document revision instruction failed silently for this model.

## 9. Hypothesis assessment

> Can an LLM use explicitly supplied Interslavic alternatives to revise an
> existing translation?

**Evidence supporting the hypothesis:**

1. Six of seven models improved evaluator coverage (+0.35 … +1.28 pp).
2. Every revising model adopted 4–7 supplied surfaces as **targeted
   replacements** at the positions of the selected forms, and 5–6 supplied
   surfaces were newly introduced by each revision.
3. In the cleanest cases, adopted-and-accepted adoptions are frequent
   (ChatGPT 6/6, Grok 4/4, Gemini 4/6, GPTs-ISV Teacher 4/5, Claude 4/7,
   DeepSeek 2/5) — the mechanism produces evaluator-accepted forms whenever
   the supplied alternative coincides with the canonical dictionary.
4. Whole-document compliance held: lexical token counts are identical in all
   seven runs, story structure and characters were preserved, and models
   returned only the revised story.

**Evidence limiting the hypothesis:**

1. **Regressions exist (12 A→C tokens).** Grok (7) and Claude (3) introduced
   non-supplied spellings, so models do not reliably restrict themselves to
   supplied alternatives; ChatGPT (2) over-applied supplied candidates to
   already-valid forms.
2. **Model dependence.** Bielik returned a formatting-only revision: one of
   seven models provided no usable evidence at all.
3. **Resource mismatch confounds measurement.** Adopted candidates attested in
   alternative resources (`seli`, `sedeli`, `reci`, `rekl`, `dejstvitelno`,
   `dalše`) never register as improvements; measured gains depend entirely on
   whether supplied alternatives coincide with the canonical dictionary.
4. **Small magnitude and empty B bucket.** Gains are +0.35 … +1.28 pp; the
   morphology (B) bucket contributes ~0, so "valid coverage" is effectively
   exact-match coverage.
5. The old form-level bookkeeping over-counted "resolved" forms (C→C
   re-spellings counted as resolutions); the corrected transition matrix shows
   genuine C→A = 90 tokens and C→C = 2,798 unchanged-C tokens.

**Conclusion:** the evidence is **consistent with** the hypothesis but does
not prove it. LLMs can use explicitly supplied alternatives in a
whole-document revision when the alternatives are supported by the canonical
resource; their compliance and the measurability of the effect both depend on
factors the pilot has now exposed. No claim of proof is made.

## 10. Human review preparation

`experiments/exp002-pilot/comparison/human_review.md` contains **five complete
before/after text pairs** (byte-for-byte, verbatim), selected deterministically
to represent different outcomes, each labeled only with its outcome category:

| Pair | Run | Outcome category |
|---|---|---|
| 1 | ChatGPT | clear improvement, no new unresolved unique forms |
| 2 | Gemini | improvement with no A→C regression |
| 3 | Claude | improvement with A→C regression (`različ-*` → `růz-*`) |
| 4 | DeepSeek | little improvement (+0.35 pp) |
| 5 | Bielik | no change (formatting-only revision) |

The Project Owner reads the complete texts and answers a high-level question
("Which version sounds more naturally Interslavic?") without word-by-word
annotation. No automatic language/likeness judgment was performed.

## 11. Recommendation (one next task)

**Recommendation: B — improve the evaluator/resource layer first.**

Rationale, based on the observed evidence:

- The pilot's central measurement problem is that **candidate generation
  (alternative resources) and evaluation (canonical dictionary) use
  inconsistent resource layers**: 113 alternative-resource surfaces used in
  revisions were invisible to the evaluator, and adopted replacements such as
  `seli`, `sedeli`, `reci`, `rekl`, `dejstvitelno` produced no measurable
  improvement. Until the layers are reconciled under a single, documented
  resource policy, no larger experiment (option A) can produce interpretable
  coverage numbers.
- Regression bookkeeping is now improved (this task), and the prompt/compliance
  failures are visible and small in magnitude (12 A→C tokens across three
  models) — prompt/constraint tuning (option D) is a reasonable follow-up
  *after* resource reconciliation, not before.
- Candidate generation (option C) is not the dominant problem: candidates were
  used, and rejected adoptions trace to evaluator scope, not candidate quality.
- Abandoning or substantially revising the approach (option E) is not
  supported: six of seven models used supplied candidates, and clean runs
  (ChatGPT, Gemini, GPTs-ISV Teacher, Grok) show the mechanism working when
  the resources agree.

The recommended next task is **not started here**.

## 12. Artifacts

- `scripts/compare_exp002.py` — token-aligned transition matrix (A→C/B→C
  regressions), per-form candidate usage, curated human-review pairs.
- `scripts/verify_exp002_runs.py` — completeness + SHA-256 integrity check
  (7/7 pass).
- `comparison/<run>/{comparison.json,comparison.md}` — per-run before/after,
  transitions, candidate usage (local; embed model output).
- `comparison/comparison.md` — cross-run summary.
- `comparison/human_review.md` — 5 holistic before/after pairs.
- `REPORT.md` — this report.
- SODA documentation: `docs/STATE.md`, `docs/EXPERIMENTS.md`,
  `docs/ROADMAP.md`, `docs/DECISIONS.md`, `docs/LESSONS.md`, `SOURCES.md`.

## 13. Git

See the final SODA commit message and `git status`; reported in the task
summary.
