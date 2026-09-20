# Paper 1 — EXP-002 / EXP-003 replication audit

**Date:** 2026-09-20  
**Purpose:** Determine whether historical EXP-002 and EXP-003 evidence is
sufficiently reproducible to support Paper 1 claims about dictionary /
grammar assistance, what is missing, and what (if anything) should be
repeated in a small controlled replication.  
**Paper 1 primary focus (for context):** EXP-004 Phase 2B corpus priming
(`docs/research/PAPERS.md`). EXP-002/003 are **background / intervention-ladder**
evidence, not the Phase 2B priming experiment itself.

**Constraints of this audit:** no new runs; no manuscript edits; no
`isv-eval` changes; no historical result changes; no external web sources.
Documented facts vs recommendations are labeled separately.

---

## 1. Experimental reconstruction

### 1.1 EXP-001 (context only)

| Field | Documented value |
|---|---|
| Role | Unconstrained Polish→ISV baseline providing inputs to EXP-002 |
| Source | `experiments/exp001-baseline/input/source.txt` (`op-pl.txt`), SHA-256 `e3164ffc…e643`; includes markdown fences + embedded instruction line (used byte-for-byte) |
| Models | ChatGPT, Gemini, Claude, DeepSeek, Bielik, Grok, GPTs “ISV Teacher” |
| Prompts | Template exists; **exact historical EXP-001 prompts recorded as `unknown` in EXP-003 DESIGN** (within-EXP-003 A is the proper control for scaffolding) |
| Runs / repeats | One output per model — **no independent repeats documented** |
| Evaluator | `isv-eval` A/B/C; later reports use two-tier canonical/broader (Task 008) |
| Decoding hyperparameters | **not documented** |
| Model version / snapshot | Often `unknown` in later manifests |

### 1.2 EXP-002 — dictionary-guided post-hoc revision (pilot)

| Field | Documented value |
|---|---|
| **Research question** | Can an LLM revise its own complete EXP-001 translation using **supplied** Interslavic alternatives for selected unresolved forms, improving resource coverage while preserving meaning/structure? |
| **Intervention** | Post-hoc **complete-document revision** with a candidate table (not generation-time scaffolding) |
| **Source text** | Not a fresh Polish source: each run revises that model’s **EXP-001 Interslavic output** (byte-for-byte copy). Underlying Polish story = EXP-001 `op-pl` artifact |
| **Model / configuration** | Seven conditions matching EXP-001: ChatGPT, GPTs ISV Teacher, Gemini, Claude, DeepSeek, Bielik, Grok. Manifest IDs use `model_version: unknown` pattern in related packaging |
| **Prompt / scaffold** | Committed template `experiments/exp002-pilot/prompt_template.txt`; full prompts packaged per run (`operator-prompts/manifest.json` records per-file `source_prompt_sha256`). Operator Markdown embeds original translation (**gitignored**) |
| **Candidate generation** | Deterministic (`scripts/prepare_exp002_pilot.py`): canonical / orthographic / alt-resource / morphology-derived / none; stratified selection (~30 forms per run); **no invented candidates** |
| **Evaluator** | Same `isv-eval` as EXP-001; before/after + token-aligned A/B/C transitions (`scripts/compare_exp002.py`) |
| **Metrics** | Canonical coverage Δ (pp); unresolved counts; C→A / A→C transitions; candidate usage / targeted adoption |
| **Number of runs** | **7** (one revision per model) |
| **Repeats** | **None documented** (`n = 1` per model) |
| **Exclusions / failures** | Bielik: formatting-only “revision” (0 lexical change) — included in tables as Δ +0.00; treated as non-execution of the revision task |
| **Final reported results (observed)** | 6/7 models Δ **+0.35 … +1.28** pp; Bielik **+0.00**; total C→A = **90**, A→C = **12**, B→C = **0**; many accepted targeted adoptions are canonical; several adopted alt-resource surfaces remain C under canonical evaluator |

**Not documented / not recoverable from public repo alone:** vendor decoding parameters (temperature, top-p, etc.); exact chat UI model snapshot names beyond provider labels; full candidate tables (in gitignored packages). Prompt **hashes** and procedure **are** documented.

### 1.3 EXP-003 — generation-time lexical scaffolding

| Field | Documented value |
|---|---|
| **Research question** | Does a deterministic Polish→ISV lexical scaffold at **generation time** improve canonical / broader coverage (and naturalness) vs unconstrained direct translation of the **same** source by the **same** model? |
| **Conditions** | **A** Direct; **B** one canonical candidate per form; **C** multiple resource-supported alternatives; **D** C + grammatical annotations (POS, aspect, example paradigm forms) |
| **Source text** | Cleaned story-only Polish: SHA-256 `5de968a6214d3d64bdb586b5121f494c4bb107e33546487a86bf8ecc57280723` (`input/source.meta.json`); derived from EXP-001 by removing fences + instruction line |
| **Model / configuration** | Planned: ChatGPT, Claude, Bielik (3 × 4 = 12). Manifest: `model_version: unknown` |
| **Prompt / scaffold** | Template `prompt_template.txt`; scaffold blocks B/C/D hashed in `operator-prompts/manifest.json`; prompts differ only by condition block within a model |
| **Evaluator** | Task 008 two-tier `isv-eval` (canonical + broader); orthography audit (Task 015) |
| **Metrics** | Canonical / broader coverage; unresolved rate; ortho outside-inventory (+ non-name refinement); human forced-choice (separate) |
| **Number of runs** | 12 collected; **8 usable** for quantitative comparison |
| **Repeats** | **None documented** (`n = 1` per model×condition) |
| **Exclusions / failures** | **Bielik A–D excluded** from quantitative comparison: A/B truncated mid-story; C prompt echo; D service error page — preserved as qualitative artifacts (D-035) |
| **Human evaluation** | One non-expert participant; 100 sentence forced-choice items (50 ChatGPT + 50 Claude); display order randomized (seed `20260905`); exploratory χ²/Spearman only |
| **Final reported automated results (usable 8 runs)** | ChatGPT: B/C/D all raise canonical vs A (~+8–9.5 pp; **B best**). Claude: only **D** clearly raises (~+9.8 pp); **C flat/worse** vs A. Orthography: Claude C worst non-name contamination |
| **Final reported human results** | Guided (B+C+D) **74%** vs A **26%** (identical pooling for both models); D most chosen overall (39%); ChatGPT-B coverage-best but human-worst (12%) |

**Not documented:** decoding hyperparameters; exact vendor model build IDs; ability to separate D’s POS/aspect vs example-form components (by design, D packages them together).

---

## 2. Replication strength

| Experiment | Classification | Rationale (documented design) |
|---|---|---|
| **EXP-002** | **exploratory / developmental** | Explicitly a **pilot**; one revision per model; no independent repeats; model versions largely `unknown`; modest Δ; mechanism = revision of existing text, not generation-time assistance |
| **EXP-003 (automated)** | **exploratory / developmental** (borderline **partially replicated** only in the weak sense of two models × four conditions) | Nested A–D design is clear and prompts/scaffolds are hashed; but **n = 1** per cell, only two quantitatively usable models, Bielik wave failed, no stochastic repeats |
| **EXP-003 (human)** | **exploratory** | Single participant; sentence subsample; not a multi-rater protocol; project already states it is not a strong selection criterion |

**Neither EXP-002 nor EXP-003 is “sufficiently replicated for strong journal claims”** about stable, configuration-general effects of lexical/grammar assistance, because independent repeated runs under frozen configs are absent.

---

## 3. What EXP-002 actually establishes

### Directly observed (historical data)

- Post-hoc, candidate-constrained **whole-document revision** produced small
  **positive canonical-coverage Δ** for 6/7 models (+0.35…+1.28 pp).
- Models can **adopt supplied candidates** at targeted positions (4–7
  targeted adoptions per revising model).
- **A→C regressions** occur (12 tokens total); some from non-supplied
  spellings; some from overgeneralizing supplied candidates.
- **Bielik** did not perform a lexical revision (formatting only).
- Surfaces attested only in alternative resources can be adopted yet remain
  **canonical-C** (evaluator/resource mismatch) — documented extensively in
  REPORT §6 and later RESOURCE_POLICY work.

### Interpretation already documented in the project

- Hypothesis “LLMs can use supplied alternatives” is **supported for some
  models under this pilot**, with small effect sizes and caveats.
- Canonical coverage understates broader resource support when alt-resource
  candidates are used (motivated two-tier policy; not a re-analysis here).

### Claims that would require new replication

- That post-hoc revision **reliably** improves coverage across models/UI
  snapshots (needs repeats + pinned configs).
- That revision is **preferable to** generation-time scaffolding (different
  mechanisms; not crossed in one design).
- Effect-size estimates suitable as portable constants.

---

## 4. What EXP-003 actually establishes

### Intervention ladder (as run)

| Cond | Intervention difference (documented) |
|---|---|
| A | Polish source + translate instruction; **no** scaffold |
| B | + one canonical ISV candidate per Polish token (aligned scaffold) |
| C | + multiple resource-supported candidates where available |
| D | + POS / aspect / example paradigm forms on candidates |

Held constant within model: cleaned source `5de968a6…`, template rules,
external chat execution pattern.

### Supported comparisons (on documented usable data)

| Comparison | Support |
|---|---|
| A vs B/C/D (ChatGPT coverage) | Supported: all scaffolds beat A on canonical coverage (single run) |
| A vs D (Claude coverage) | Supported: D beats A; B small; **C not better** |
| B vs C | Supported directionally: **C can underperform B** (ChatGPT slight; Claude clear) — “more alternatives ≠ better” |
| C vs D | Supported for Claude (D ≫ C); weak/ambiguous for ChatGPT (D slightly below B/C on coverage) |
| Human guided vs A | Supported for this participant/protocol: 74% vs 26% |
| Human vs coverage alignment | **Divergent for ChatGPT**; aligned at extremes for Claude |

### Weakened / not supported

- **Grammar-only effect:** D is **not** a pure grammar intervention; it
  includes lexical alternatives **plus** annotations. C vs D confounds
  “grammar help” with whatever wording changes D induces.
- **Bielik:** no quantitative claim.
- **Generalization** beyond one story / two models / one run.
- Human evaluation as **validator of the evaluator** — explicitly not
  claimed; signals answer different questions (REPORT §5–6).

---

## 5. Missing evidence for Paper 1

| Issue | Where | Why it matters | Fixable from records? | New data required? |
|---|---|---|---|---|
| No independent repeats | EXP-002, EXP-003 | Cannot separate signal from single-draw stochasticity | No | **Yes** |
| Model version `unknown` | Manifests / metas | Snapshot drift undermines exact replication | Partially (hashes of prompts/outputs exist) | **Yes** for pinned configs going forward |
| Decoding params not recorded | EXP-002/003 | Interface defaults unknown | No | Record or accept “vendor default UI” as factor |
| Operator prompts gitignored | Both | Third parties cannot re-read full prompt bytes without local artifacts | Hashes + templates yes; full text no (copyright/model-output) | Local archive policy, not new science |
| EXP-001 prompt `unknown` | EXP-001 | Weak link if comparing to EXP-001 absolute levels | No | Not needed if Paper 1 uses within-EXP-003 A |
| D packages lexical+grammar | EXP-003 D | Cannot claim “grammar guidance” alone | Design note only | Optional D′ grammar-only arm if that claim is wanted |
| C vs B ambiguity | EXP-003 | Multiple alternatives can hurt | Observed once | Repeats to confirm stability |
| Bielik failure modes | EXP-003 | Service/context failures | Documented | Optional third config with integrity gate |
| Human n=1 | EXP-003 | Preference not general | Documented | Not required for coverage claims |
| Single story | Both | Story-specific curation (EXP-003 residual table) | Yes (frozen curation) | New story only if generalization claimed |
| Mechanism mismatch vs Paper 1 core | EXP-004 is priming | EXP-002/003 do not measure corpus priming | N/A | Priming already in Phase 2B; this audit is for assistance ladder claims |

---

## 6. Recommended targeted replication

### Recommendation on the proposed 2–3 configs × 4 conditions × 3 repeats (24–36 runs)

**Accept with small refinements** (below). This design is the **smallest
defensible** strengthening for Paper 1’s intervention-ladder / scaffolding
claims. It should **replicate EXP-003’s generation-time mechanism**, not
EXP-002’s revision loop (unless Paper 1 explicitly needs revision claims).

### Proposed design (refined)

| Factor | Choice |
|---|---|
| Mechanism | Generation-time scaffolding (EXP-003-like), **not** post-hoc revision |
| Configurations | **2** primary (historically divergent: ChatGPT-like + Claude-like), optional **3rd** only if integrity historically reliable |
| Conditions | **A, B, C, D** as in EXP-003 (keep C: historically informative negative) |
| Source | Frozen cleaned story SHA `5de968a6…` **or** explicitly new frozen hash if changed |
| Scaffold | Rebuild with pinned dictionary/morphology versions; record scaffold block hashes |
| Repeats | **n = 3** independent fresh sessions per cell |
| Run count | **2 × 4 × 3 = 24** (preferred minimum); **3 × 4 × 3 = 36** if third config added |
| Evaluator | Same `isv-eval` two-tier + orthography audit; **do not change** metric semantics mid-study |
| Human eval | **Optional / deferred** — not required for coverage claims |

### Per-condition specification

| Cond | Intervention difference | Held constant | Frozen | Valid run | Failure / exclusion | Primary outcomes | Secondary |
|---|---|---|---|---|---|---|---|
| **A** | No scaffold | Source, template rules, config | Source hash; prompt template | Complete story translation; identity metadata OK | Truncation, echo, service error, wrong model | Canonical coverage; broader coverage | Ortho non-name; unresolved rate |
| **B** | One canonical candidate / token | Same as A + scaffold generator | Scaffold B hash; candidate policy | Same integrity as A | Same + scaffold omission | Same | Token-aligned transitions vs A if computed |
| **C** | Multiple resource-supported alternatives | Same + multi-candidate policy | Scaffold C hash | Same | Same | Same | B vs C Δ |
| **D** | C + POS/aspect/example forms | Same + annotation policy | Scaffold D hash; morphology pin | Same | Same | Same | C vs D Δ; **note:** not grammar-only |

**Optional later arm (not in minimum 24):** **D′** = B + grammar annotations
**without** multi-alternative list — only if Paper 1 needs a cleaner
“grammar add-on” estimand.

### What not to repeat in the minimum package

- Full 7-model EXP-002 revision pilot.
- Bielik-class unreliable interfaces (unless testing failure taxonomy).
- Multi-participant human study (unless naturalness is a primary Paper 1 claim).

---

## 7. Statistical / comparative structure

**Do not** require new inferential tests for compatibility with project norms
(descriptive Phase 2B style is acceptable).

Recommended analysis (descriptive, pre-registered in a short DESIGN):

1. **Unit:** configuration × condition × replicate.
2. **Primary estimand:** within-configuration mean  
   \(\Delta_{B-A} = \overline{C}_B - \overline{C}_A\) (canonical coverage, pp),
   similarly \(\Delta_{C-A}\), \(\Delta_{D-A}\), \(\Delta_{C-B}\), \(\Delta_{D-C}\).
3. **Replicate structure:** report mean, SD, min/max, sign consistency of
   three replicates (as in Phase 2B).
4. **Configuration effects:** do **not** pool into one “LLM” mean; report
   per configuration (EXP-003 already showed ChatGPT≠Claude patterns).
5. **Failures:** exclude from primary paired means; preserve with status
   codes (D-035 pattern); never impute as 0.
6. **Secondary:** broader coverage; ortho non-name; optional token-aligned
   transitions vs A.
7. **No composite quality score**; human preference remains a separate layer
   if collected.

---

## 8. Paper 1 claim boundary

| Potential claim | Supported by existing EXP-002/003? | Requires replication? |
|---|---|---|
| Post-hoc dictionary-guided revision can raise canonical coverage for some models (small Δ) | **Partially** (EXP-002 pilot, n=1) | **Yes** if stated as stable/general |
| Generation-time lexical scaffolding can raise canonical coverage vs Direct (this story; ChatGPT) | **Partially** (EXP-003, n=1) | **Yes** for stability |
| Multiple alternatives are not automatically better than one candidate | **Suggestive** (EXP-003 C≤B patterns) | **Yes** to confirm with repeats |
| Lexical + grammar annotations (D) can help some models more than B/C | **Suggestive** (Claude D) | **Yes**; also clarify D≠grammar-only |
| Scaffolding always helps all models | **No** (Claude C; Bielik failures) | Would need broader redesign |
| Human readers prefer scaffolded text | **Exploratory only** (1 participant) | **Yes** for any strong preference claim |
| Coverage = naturalness / quality | **No** (ChatGPT-B counterexample) | Do not claim |
| Alt-resource candidates count as canonical improvement | **No** (documented mismatch) | Policy already forbids; keep |
| Corpus priming effects (Phase 2B) | **Not from EXP-002/003** | Separate evidence pack |

---

## 9. Final recommendation

### `Targeted replication recommended`

**Smallest concrete next experiment:**

> **EXP-003R (name TBD):** 2 vendor configurations × conditions {A,B,C,D} ×
> 3 independent repeats = **24 runs**, generation-time scaffolding on the
> frozen cleaned story (or a newly frozen hash), pinned resources, integrity
> gate, descriptive Δ analysis as in §7.

**Why sufficient for intended Paper 1 assistance claims:** it supplies the
missing **repeat structure** and **pinned configs** for the mechanism Paper 1
actually needs when discussing the intervention ladder (generation-time
lexical ± grammar), without re-running EXP-002’s revision pilot or expanding
to a full multi-story / multi-human redesign.

**If Paper 1 only cites EXP-002/003 as exploratory background** with explicit
`n=1` / pilot caveats and makes **no** stability or generality claims, a
replication could be deferred — but that is a **writing** choice, not an
evidence upgrade. For any claim of reliable assistance effects,
replication remains recommended.

---

## 10. No-action section

Deliberately **not** changed by this audit:

- Any EXP-001/002/003 raw outputs, evaluations, or reports
- `isv-eval` code or A/B/C semantics
- Paper 1 LaTeX manuscript
- Phase 2B / EXP-004 artifacts
- Grammar Aggregator seed
- Historical Bielik failures (remain qualitative)
- Decision not to invent missing decoding parameters or model build IDs
- Decision not to scrape or reconstruct gitignored operator prompt bodies

---

## Appendix — files inspected

| Path | Use |
|---|---|
| `experiments/exp001-baseline/DESIGN.md`, `input/source.meta.json` | Baseline context / source hash |
| `experiments/exp002-pilot/DESIGN.md`, `REPORT.md`, `prompt_template.txt`, `operator-prompts/manifest.json`, `README.md` | EXP-002 reconstruction |
| `experiments/exp003-scaffold/DESIGN.md`, `REPORT.md`, `README.md`, `prompt_template.txt`, `input/source.meta.json`, `operator-prompts/manifest.json`, `comparison/summary.md` | EXP-003 reconstruction |
| `docs/research/PAPERS.md`, `docs/research/exp004-phase2b/manuscript/README.md` | Paper 1 scope context (read only) |
| `docs/RESOURCE_POLICY.md` (via prior project knowledge in REPORT cross-refs) | Evaluator/resource mismatch framing already in EXP-002 REPORT |

**Scientific content changed:** no (this file is documentation only).
