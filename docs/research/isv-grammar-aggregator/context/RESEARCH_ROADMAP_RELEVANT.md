# Curated extract — Research Roadmap (selected sections)

> **Type:** curated extract (original wording preserved; not a rewrite).
> **Canonical source:** `docs/research-roadmap.md`
> **Extraction date:** 2026-09-20
> **Included line ranges (1-indexed):** 1–115, 153–204, 720–727, 828–856
> **Note:** Omits full EXP-004 Phase 1/2A/2B result tables; includes framing, EXP-005/003 brief, morphology-intervention status, tool objective, stopping rule.
> This extract is for the Grammar Aggregator working package only.
> The canonical file remains authoritative; do not silently rewrite policy language.

---

# Research Roadmap — `isv-llm-lab`

**Status labels used in this document:** `COMPLETED` (measured, recorded,
immutable) · `CURRENT` (in progress or the agreed next step) ·
`PROPOSED` (designed or scoped, not executed) · `HYPOTHESIS` (a claim
that is being tested, not an established result).

> This document is the **high-level source of truth** for the project's
> scientific direction: hypothesis, research questions, completed
> experiments, key findings, limitations, the Phase 2B plan (HIGH, LOW,
> and UNSEEN executed + aggregated descriptively as of 2026-09-18; no
> three-regime paper synthesis yet), the
> publication direction, the long-term tool objective and the stopping
> rule. It was created in SODA Task 028 (2026-09-09) to reconstruct in
> the repository the research direction and decisions that had previously
> existed only in external research-lead discussion. Full per-task
> detail lives in `docs/STATE.md`, `docs/EXPERIMENTS.md`,
> `docs/RESEARCH_NOTES.md`, `docs/DECISIONS.md`, `docs/LESSONS.md` and
> the per-experiment `DESIGN.md`/`REPORT.md` files; this document is a
> pointer-rich summary, not a replacement for any of them.
> The companion document for the translation-method thread is
> [`docs/translation-method.md`](translation-method.md).

## 1. Project identity and scientific framing

- `isv-llm-lab` is an open-source, non-profit **community research
  project** (`README.md`). It is **not** an official Interslavic /
  Medžuslovjansky project and does not present itself as an official
  language authority.
- The research asks whether modern LLMs can generate plausible
  Interslavic translations, and whether providing authentic Interslavic
  resources **at inference time** can improve the output.
- The central scientific hypothesis (`HYPOTHESIS`, evolved over EXP-001…
  EXP-004):

  > Authentic target-language corpus context can improve LLM translation
  > into Interslavic **without fine-tuning**, and the important question
  > is whether that improvement **generalizes beyond the lexical/thematic
  > content of the priming corpus**.

- Terminology to use consistently (matching the repo and the literature):
  low-resource machine translation; inference-time adaptation; in-context
  learning; **corpus priming**; contextual grounding; reference-text
  conditioning. Corpus priming is **never** called "training" or
  "fine-tuning".
- Interslavic is the **case study / target language** of a general
  low-resource question. The project is **not** framed as a contest to
  identify "the best LLM".
- The evaluator measures **canonical resource coverage**, not "is this
  valid Interslavic" (see §4, EXP-005, and `docs/RESOURCE_POLICY.md`).

## 2. Two project goals

The project now has two related but distinct goals (`COMPLETED` framing
decision, recorded Task 028; both goals are live and complementary).

### Scientific goal

Determine:
- whether authentic Interslavic corpus priming improves LLM translation;
- whether the effect is **reproducible** (EXP-004 repeated generation);
- whether it **generalizes to unseen topics** (planned Phase 2B);
- how the effect depends on **baseline model performance** (descriptive
  ρ ≈ −0.84, §9);
- how different **assistance mechanisms** compare (EXP-002/EXP-003 vs
  EXP-004 corpus priming — the intervention ladder, see
  `docs/translation-method.md`);
- what the **automated metrics can and cannot establish** (EXP-005
  policy; §4).

### Practical goal

Develop a robust, reproducible Polish → Interslavic translation workflow:

```
Polish source
→ preparation
→ target-language corpus/reference conditioning
→ LLM translation
→ lexical/resource audit
→ morphology/grammar audit
→ targeted repair
→ final Interslavic output
```

The practical objective is **not** to choose one LLM; it is to determine
whether a **sequence of interventions** can reliably improve a PL → ISV
translation. The eventual software should hide that complexity from the
user and tell the user which model/configuration and which prompts/steps
to use for their input.

## 3. Research questions

Answered (descriptively) so far:
- What is the unguided baseline coverage of current LLMs on one canonical
  Polish story? → EXP-001.
- Can post-hoc lexical revision improve coverage? → EXP-002.
- Can deterministic generation-time lexical/morphology scaffolding
  improve coverage? → EXP-003.
- Does authentic-corpus priming shift coverage, and is the shift larger
  than run-to-run stochastic variation? → EXP-004 Phase 2A + repeated
  generation (Tasks 024/026).
- Does the effect depend on baseline performance? → descriptive negative
  dependence (§9) — `CURRENT`-level confidence only.

Open (`PROPOSED`/`HYPOTHESIS`):
- Does priming **generalize to source topics absent from the corpus**?
  (Phase 2B; §11.)
- How much authentic context is sufficient for the effect? (future
  corpus-length ablation; §11.)
- Which *ordering* of interventions is best? (pipeline optimization;
  `docs/translation-method.md` §7.)
- What can automated metrics not capture (naturalness, intelligibility,
  communicative adequacy)? → Layer 3 evaluation remains open (no expert
  protocol yet).

### EXP-005 — resource audit / reconciliation (cross-resource audit; Tasks 005/007/008)

Repo note: the repository records this thread as the EXP-001
cross-resource audit + resource-policy work (Tasks 005/007/008), not as a
separate "EXP-005" experiment directory.

- The audit covered the **1,050 unique unresolved forms** across EXP-001
  (`docs/ROADMAP.md`, `docs/RESOURCE_POLICY.md`;
  `experiments/exp001-baseline/manual-audit/` local artifacts).
- Breakdown (`docs/ROADMAP.md`): **403 (38.4 %)** attested verbatim in an
  alternative resource (mostly Interslavicfreq wordlists; 54 have exact
  Hunspell evidence); **450** candidate lemmas only (no resource
  evidence); **116** no evidence and no candidates; **45** orthographic
  candidates only; **36** proper-name/story-specific/special cases.
- Conclusion: apparent unresolved vocabulary must **not** be read as
  "non-Interslavic". The evaluator is described as measuring **canonical
  resource coverage**, not validity.
- Two metrics are maintained (implemented in `isv-eval`, Task 008):
  1. **canonical coverage** = (A + B) / lexical tokens;
  2. **broader resource-supported coverage** = canonical-supported tokens
     + exact alternative-resource attestations, over lexical tokens.
- Historical broader-coverage estimates for EXP-001 (`docs/RESOURCE_POLICY.md`
  §6): Claude 86.00 %, DeepSeek 82.81 %, Gemini 82.32 %, ChatGPT 86.27 %,
  GPTs ISV Teacher 88.44 %, Bielik 78.99 %, Grok 86.41 %.

### EXP-003 — generation-time scaffolding (+ human sentence test)

- Conditions: A = direct baseline; B = lexical scaffold with one
  canonical candidate per unresolved form; C = lexical scaffold with
  multiple resource-supported alternatives; D = lexical scaffold +
  grammar annotations / morphology information.
- Scaffold generated deterministically from the Polish source plus
  explicit per-story residual mappings (`curation/op-pl/`).
- The project deliberately rejected a Polish lemmatizer/analyzer
  dependency and rejected LLM-assisted semantic mapping (a second hidden
  LLM variable) (`experiments/exp003-scaffold/DESIGN.md` §6).
- Results (canonical / broader; `docs/EXPERIMENTS.md` §EXP-003):
  - ChatGPT A 76.27 / 87.05 · B 85.72 / 90.80 · C 84.82 / 89.16 ·
    D 84.04 / 88.82;
  - Claude A 75.81 / 87.51 · B 78.97 / 86.42 · C 75.41 / 84.47 ·
    D 85.62 / 92.02;
  - B vs A: ChatGPT **+9.45 pp**, Claude **+3.16 pp** (canonical);
  - C vs B: ChatGPT −0.90 pp, Claude −3.56 pp;
  - Claude D was its strongest condition.
- Key conclusion: **more dictionary alternatives are not automatically
  better**.
- Human evaluation: one sentence-level forced-choice test, 100 questions,
  **one participant, non-expert** (`experiments/exp003-scaffold/REPORT.md`;
  decisions D-042/D-043). Guidance (B/C/D) was preferred over baseline A
  74 % vs 26 % for both models, but this must **not** be used as a strong
  selection criterion. Per D-042, human evaluation is **not repeated** for
  the current project unless a justified expert protocol exists.

## 12. Dictionary/morphology intervention status (`COMPLETED` + `PROPOSED`)

Dictionary-based interventions are **already tested**; do not propose
them as untested. Tested: EXP-002 (post-hoc lexical revision); EXP-003 B
(one lexical candidate during generation); EXP-003 C (multiple lexical
alternatives); EXP-003 D (lexical + morphology/grammar scaffolding).
Conceptual intervention ladder A–E and the tested results are documented
in [`docs/translation-method.md`](translation-method.md).

## 15. Long-term tool objective (`PROPOSED`)

A reproducible method that says: "Given this Polish input, use
configuration X, then perform steps Y and Z." The eventual software could
automate prompt construction, resource lookup, audit and repair
orchestration while leaving the actual LLM calls under the user's control
where appropriate. Architecture sketch and evaluation philosophy:
[`docs/translation-method.md`](translation-method.md).

## 16. Stopping rule (`CURRENT` rule, recorded Task 028)

The project should not grow indefinitely. Intended sequence:
1. ~~complete the seven-configuration × three-repeat Phase 2B HIGH test~~
   (**done 2026-09-15** — descriptive aggregates preserved);
2. ~~LOW-overlap (`Podkłady`)~~ (**done 2026-09-16** — descriptive
   Δ_LOW + qualitative audit preserved under `phase2b/analysis/low/`);
3. decide whether UNSEEN-domain tests are justified after reviewing
   HIGH↔LOW evidence;
4. analyse whether priming generalizes across regimes (UNSEEN still
   missing from the planned trio);
5. begin writing the paper from preserved evidence records;
6. optionally perform a small pipeline-optimization experiment;
7. implement the practical translation tool.

Do not add more model families merely to increase the model count unless
a specific scientific question requires it. Do not run more human
evaluation unless a specific expert/validated protocol is justified. The
goal is to move from "more experiments" to "stronger causal/mechanistic
interpretation and a reproducible translation method".
