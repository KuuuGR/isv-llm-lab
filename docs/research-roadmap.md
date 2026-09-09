# Research Roadmap — `isv-llm-lab`

**Status labels used in this document:** `COMPLETED` (measured, recorded,
immutable) · `CURRENT` (in progress or the agreed next step) ·
`PROPOSED` (designed or scoped, not executed) · `HYPOTHESIS` (a claim
that is being tested, not an established result).

> This document is the **high-level source of truth** for the project's
> scientific direction: hypothesis, research questions, completed
> experiments, key findings, limitations, the current Phase 2B plan, the
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

## 4. Experiment record (`COMPLETED`)

All quantitative claims below carry their source location. Full records:
`docs/EXPERIMENTS.md` (canonical experiment log), per-experiment
`DESIGN.md`/`REPORT.md`. Nothing below is a new result.

### EXP-001 — direct baseline (unconstrained)

- Seven whole-document direct translations (ChatGPT, GPTs ISV Teacher,
  Gemini, Claude, DeepSeek, Bielik, Grok) of one complete Polish short
  story (`opowiadania-set-isv/op-pl.txt`, SHA-256
  `e3164ffc…29e643`; source: `docs/EXPERIMENTS.md` §EXP-001).
- Canonical coverage: ChatGPT **75.95 %**, GPTs ISV Teacher **79.83 %**,
  Gemini 71.72 %, Claude 73.55 %, DeepSeek 74.42 %, Bielik 55.48 %,
  Grok 76.56 % (lexical-token denominators; `docs/EXPERIMENTS.md`,
  `experiments/exp001-baseline/outputs/comparison.md`).
- GPTs ISV Teacher was the strongest baseline in that experiment; Bielik
  was a clear negative qualitative case.
- Methodological conclusion (kept): the canonical evaluator measures
  **resource coverage**, not "is this valid Interslavic".

### EXP-002 — post-hoc lexical revision (pilot)

- Models were given their unresolved forms plus deterministic candidate
  alternatives and asked to revise the whole translation.
- Canonical changes: ChatGPT **+1.25 pp**, Claude **+1.28 pp**, Gemini
  **+0.88 pp**, Grok **+0.95 pp**, GPTs ISV Teacher **+0.53 pp**,
  DeepSeek **+0.35 pp**, Bielik **+0.00 pp** (`docs/EXPERIMENTS.md`
  §EXP-002; Bielik not usable quantitatively).
- Token-aligned analysis: **90 C→A / C→B resolutions, 12 A→C
  regressions** (with some model-specific regressions)
  (`docs/RESEARCH_NOTES.md`).
- Exposed a resource/evaluator mismatch: forms supported by the audited
  alternative resources are not accepted by the canonical evaluator →
  drove the two-tier resource policy (EXP-005 / Tasks 007–008).

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

### Orthography audit (`COMPLETED`)

- Deterministic, audit-only orthography validator (`scripts/
  check_orthography.py`; Task 015). Authoritative alphabet source: Jan van
  Steenbergen's Interslavic orthography page
  (https://steen.free.fr/interslavic/orthography.html, fetched
  2026-09-05).
- Distinguishes allowed ISV letters, Cyrillic, Polish-specific letters,
  other Latin, other scripts, unexpected non-letters.
- Proper-name effects (e.g. Polish names `Bronisława`, `Przemysława`)
  must not be interpreted as model language failure.
- The audit is **diagnostic, not a rewriting step**, and is part of the
  standard evaluation stack (reported side by side with coverage; never
  merged into a composite).

## 5. EXP-004 Phase 1 — model screening (`COMPLETED`, Tasks 017/018)

- 18 usable configurations (reconciled roster, `experiments/
  exp004-modelscreen/README.md` + `outputs/roster.md`):
  1. GPT-5.6 Luna — thinking OFF
  2. GPT-5.6 Luna — thinking ON
  3. GPT Interslavic Teacher (custom GPT)
  4. Claude Sonnet 5 — Medium (default)
  5. Gemini 3.1 Pro — extended thinking ON
  6. DeepSeek V3 Instant — DeepThink OFF
  7. DeepSeek V3 Instant — DeepThink ON
  8. Grok
  9. Kimi K2.6 Instant (Standard)
  10. Qwen 3.8 Max — Thinking
  11. Claude Sonnet 5 — max (long reasoning)
  12. Gemini 3.6 Flash — extended thinking OFF
  13. Gemini 3.6 Flash — extended thinking ON
  14. DeepSeek V3 Expert — DeepThink OFF
  15. DeepSeek V3 Expert — DeepThink ON
  16. Qwen 3.7 Plus — Thinking
  17. Qwen 3.7 Plus — Fast
  18. Qwen 3.8 Max — Fast
- GLM 4.5 failed (service errors, no usable quantitative result).
  Venice excluded as a platform/interface rather than a model. Local /
  self-hosted models excluded from the practical screening. Bielik
  retained as a negative qualitative case, not rerun.
- Phase 1 canonical leaders: Qwen 3.8 Max Fast **82.35 %**; Gemini 3.1
  Pro ext-thinking ON **81.27 %**; Gemini 3.6 Flash ext-thinking OFF
  **81.07 %**; DeepSeek V3 Expert ON **80.49 %**; DeepSeek V3 Expert OFF
  **79.92 %**; Qwen 3.8 Max Thinking **79.87 %**
  (`experiments/exp004-modelscreen/outputs/roster.json` local).
- Practical observations (recorded, Task 018):
  - Claude Sonnet 5 max (long reasoning) took **> 45 min** and exhausted
    the free-tier token allowance (long wait/continuation) — a practical
    limitation, preserved as availability data, not a quality signal.
  - GPT-5.6 ON and OFF were very similar.
  - Thinking ON is not universally better.
  - Qwen 3.8 Max Fast was the Phase 1 canonical leader but later showed
    unusually high stochastic variation (EXP-004 repeats, §9).
  - DeepSeek V3 Expert ON/OFF had very high coverage and exceptionally
    clean orthography.
  - Gemini 3.1 Pro and Gemini 3.6 Flash had very high broader coverage.
  - Grok's operator-reported identity is "Grok 4.5, built by xAI (fast)",
    **not independently verified**.

## 6. EXP-004 Phase 2A — authentic corpus priming (`COMPLETED`, Tasks 019–024)

- Corpus registers (id `phase2a-authentic-isv` v1;
  `experiments/exp004-modelscreen/DESIGN.md` §13.3):
  - R1 literary/narrative — *Tuta historija* excerpt (author-supplied);
  - R2 artistic/poetic — complete Latin-script album *Ahoj, Slovjani!*
    (cleaned: Latin script only, Cyrillic duplicates removed, HTML
    removed, verbatim repeated stanzas/refrains deduplicated, wording
    preserved exactly, unusual artistic/rhyme forms preserved, **no
    normalization**);
  - R3 informative/encyclopedic — authentic Interslavic Wikipedia
    article *Sadovničstvo* (retrieved 2026-09-07, cleaned into authentic
    prose).
- Combined corpus: **58,459 bytes, ≈ 8,184 whitespace tokens**; SHA-256
  `aaad28e43935a40313585d77a33bfc788d97e8d69b081f9486af74d52ca1a857`.
- Authoritative Polish source (EXP-003/EXP-004 canonical story-only
  file): SHA-256
  `5de968a6214d3d64bdb586b5121f494c4bb107e33546487a86bf8ecc57280723`.
  (EXP-001/002 used the full `op-pl.txt` document, SHA-256
  `e3164ffc…29e643`; the story-only canonical file was registered by
  EXP-003.)
- Protocol: **control** = fresh session, direct translation, no corpus;
  **primed** = fresh session, Prompt 1 = authentic ISV corpus,
  Prompt 2 = exact Polish story + translation instruction. The same
  corpus bytes were used across all configurations. The corpus is
  **inference-time reference context**, never "training".

### Phase 2A single-run results (Task 024; original 18 configurations)

| Configuration | P1 canonical → P2A canonical | Δ |
|---|---|---|
| GPT-5.6 Luna OFF | 76.76 → 80.90 | +4.14 |
| GPT-5.6 Luna ON | 76.84 → 80.60 | +3.76 |
| GPT Interslavic Teacher | 76.68 → 82.86 | +6.18 |
| Claude Sonnet 5 Medium | 72.97 → 84.63 | +11.66 |
| Gemini 3.1 Pro ON | 81.27 → 83.01 | +1.74 |
| DeepSeek V3 Instant OFF | 73.61 → 81.19 | +7.58 |
| DeepSeek V3 Instant ON | 73.30 → 81.85 | +8.55 |
| Grok | 75.20 → 82.38 | +7.18 |
| Kimi K2.6 Instant | 76.63 → 79.69 | +3.06 |
| Qwen 3.8 Max Thinking | 79.87 → 82.94 | +3.07 |
| Claude Sonnet 5 max | 74.71 → 83.03 | +8.31 |
| Gemini 3.6 Flash OFF | 81.07 → 84.27 | +3.20 |
| Gemini 3.6 Flash ON | 69.86 → 84.19 | +14.33 |
| DeepSeek V3 Expert OFF | 79.92 → 84.62 | +4.70 |
| DeepSeek V3 Expert ON | 80.49 → 85.63 | +5.14 |
| Qwen 3.7 Plus Thinking | 79.39 → 82.86 | +3.47 |
| Qwen 3.7 Plus Fast | 66.35 → 75.29 | +8.94 |
| Qwen 3.8 Max Fast | 82.35 → 85.38 | +3.04 |

Source: `experiments/exp004-modelscreen/analysis/` (Task-024
deterministic dataset) + per-configuration rows reproduced in
`repeats/REPORT.md` old-delta columns and the Phase-1 roster
(`outputs/roster.json`, local).

Exploratory Dola (Tasks 021–023; identities operator-recorded, **not
independently verified**; never part of the original 18):
- Dola Fast: direct 38.87 / broader 51.67; primed 67.07 / broader 78.81;
  canonical Δ **+28.20 pp**.
- Dola Pro: direct 65.08 / broader 82.27; primed 71.75 / broader 82.26;
  canonical Δ **+6.67 pp**.

**Do not use Dola for strong conclusions.**

## 7. EXP-004 repeated generations (`COMPLETED`, Tasks 025/026)

Design: n = 3 direct + n = 3 primed per configuration, fresh-session
intent, no scaffolding/guidance, r01/r02/r03 are replication blocks (not
matched samples). Collection record:
- **120 planned** (108 primary + 12 exploratory Dola); **114 collected**;
  **106 usable**; **8 partial**; **0 invalid**; **6 missing**.
- Primary: 108 planned / 102 collected / 99 usable / 3 partial / 6
  missing. Exploratory: 12 / 12 / 7 usable / 5 partial.
- Missing primary runs: Gemini 3.1 Pro extended-thinking ON primed
  r01–r03; Qwen 3.8 Max Thinking primed r01–r03. Never fabricated;
  repeated Δ n/a for those two configurations.
- Partial outputs were excluded by the intake gate (their end markers
  were wrapped in Markdown: `## KONEC` etc.) even when content appeared
  complete; **not repaired retrospectively** (audit, Task 026).

Recorded collection deviations (not repaired; full detail in
`deviations.json` of the assistant-research-bundle + `repeats/REPORT.md`):
- **Claude Sonnet 5 max:** thinking disabled for the repeats (the
  thinking-enabled run took > 45 min and exhausted the free-tier token
  allowance, requiring a multi-hour wait). Configuration name remains
  "Claude Sonnet 5 max"; do not rename. Record the deviation wherever
  methodological comparability is discussed (Task-024 record ran with
  reasoning).
- **Gemini:** in some primed runs the corpus was split across two
  messages (interface/context limit); operator used a continuation
  instruction; corpus byte identity verified; no model switch or corpus
  corruption found → usable with a documented interface deviation.
- **Grok:** operator-reported identity "Grok 4.5, built by xAI (fast)" —
  documented as operator-reported, not independently verified.
- **Fresh-session proof:** operator reported fresh sessions, but
  machine-verifiable proof was unavailable
  (`fresh_session_proof: unavailable`) — a methodological limitation,
  not a reason to fabricate proof.

## 8. Repeated-generation results (`COMPLETED`, Task 026)

- **16 assessable primary configurations** (both conditions usable).
- Repeated mean canonical Δ (`mean(primed) − mean(direct)`):
  **+6.93 pp**; **16/16** positive.
- Repeated mean broader Δ: **+3.88 pp**; **16/16** positive.
- vs Task-024 single-run (15 comparable rows): **15/15** same direction;
  old mean Δ ≈ +6.33 pp; repeated mean Δ ≈ +6.73 pp; 12 configurations
  broadly similar magnitude; some effects substantially larger in
  repeats; **no comparable configuration reversed direction**.

Repeated canonical Δ (sorted; source `repeats/REPORT.md`):
Gemini 3.6 Flash ON **+15.91** · Gemini 3.6 Flash OFF **+11.88** ·
Claude Sonnet 5 max **+9.91** · Claude Sonnet 5 Medium **+9.12** ·
GPT Interslavic Teacher **+8.35** · Qwen 3.7 Plus Fast **+6.98** ·
DeepSeek V3 Instant OFF **+6.89** · DeepSeek V3 Instant ON **+6.56** ·
DeepSeek V3 Expert OFF **+6.47** · Kimi **+6.08** · GPT-5.6 Luna OFF
**+5.67** · GPT-5.6 Luna ON **+4.71** · Grok **+4.50** · DeepSeek V3
Expert ON **+3.77** · Qwen 3.7 Plus Thinking **+2.30** · Qwen 3.8 Max
Fast **+1.72**.

Repeated direct/primed means (mean ± SD; `repeats/REPORT.md`):
- Gemini 3.6 Flash ON: direct 67.0 ± 2.5; primed 82.9 ± 0.6.
- Gemini 3.6 Flash OFF: direct 73.3 ± 0.9; primed 85.1 ± 0.2.
- Claude Sonnet 5 Medium: direct 74.6 ± 2.0; primed 83.7 ± 0.8.
- DeepSeek V3 Expert ON: direct 81.3 ± 1.5; primed 85.1 ± 0.6.
- Qwen 3.8 Max Fast: direct 80.1 ± 1.5; primed 81.8 ± 5.8.
- GPT-5.6 Luna OFF: direct ≈ 76.8 ± 0.4; primed ≈ 82.5 ± 1.7.
- GPT-5.6 Luna ON: direct ≈ 75.4 ± 2.8; primed ≈ 80.1 ± 1.3.
- Median direct SD ≈ **1.49 pp**; median primed SD ≈ **0.87 pp**.

Spread vs effect:
- In **15/16** assessable configurations the priming shift exceeded the
  primed SD.
- **Exception: Qwen 3.8 Max Fast** — primed SD ≈ 5.83 pp, larger than its
  +1.72 pp mean improvement. Model-specific stochastic behaviour.

Baseline dependence (descriptive): Spearman ρ ≈ **−0.84** between direct
baseline canonical coverage and repeated canonical Δ (n = 16); Task-024
single-run ρ ≈ −0.86. Lower-baseline configurations tended to benefit
more. **Descriptive, not causal.**

## 9. Current scientific interpretation

Strongest currently supported statements (`COMPLETED` evidence):
1. In the collected repeated experiment, authentic ISV corpus priming
   improved canonical coverage in **all 16 assessable primary
   configurations**.
2. The average canonical improvement was ≈ **+6.93 pp**.
3. The direction of the earlier single-run effect was largely reproduced
   (**15/15** comparable configurations kept the same direction).
4. The effect is not limited to one model family.
5. Lower-baseline configurations tended to show larger improvements
   (ρ ≈ −0.84).
6. Stochastic variation exists and is model-specific.
7. Qwen 3.8 Max Fast is an important counterexample (mean effect small
   relative to primed variance).
8. Thinking ON is not universally superior.
9. DeepSeek Expert ON, Claude Medium and the Gemini Flash configurations
   are particularly interesting for further investigation, for different
   reasons (clean high-coverage output; stable/reproducible shift;
   large/reproducible shift).

Do **NOT** claim (`docs/ROADMAP.md`, `repeats/REPORT.md` §11,
`translation-method.md` §9):
- corpus priming causally improves *all* LLM translation;
- canonical coverage equals translation quality;
- the highest-canonical-coverage model is the best translator;
- corpus priming necessarily improves human naturalness;
- the EXP-003 human result proves anything general;
- Dola results establish a model effect;
- three registers are definitively optimal;
- reasoning/thinking *causes* the observed differences;
- the current results prove generalization to unseen topics.

## 10. Current preferred Phase 2B shortlist (`PROPOSED`, recorded Task 028)

Seven representative configurations (not "winners"):
1. Gemini 3.6 Flash — extended thinking ON (strong priming effect)
2. Gemini 3.6 Flash — extended thinking OFF (strong priming effect)
3. Claude Sonnet 5 Medium (stable high-performance configuration)
4. DeepSeek V3 Expert — DeepThink ON (clean output, high baseline)
5. Qwen 3.8 Max Fast (small-effect/high-variance counterexample)
6. GPT-5.6 Luna (neutral general-purpose reference)
7. Grok 4.5 Fast (independent model-family reference; operator-reported
   identity)

Phase 2B repeated testing is scoped as **7 configurations × 3
repetitions × 2 conditions = 42 translations**, giving **21 direct/primed
paired comparisons** — considered a reasonable, manageable next
experiment. Phase 2B is **not started**.

## 11. Phase 2B experimental questions (`PROPOSED`)

The most important scientific question:

> Does authentic ISV corpus priming generalize to source material whose
> topic is absent from the priming corpus?

This is stronger than another model ranking. Two variants are
documented:

- **Phase 2B-A — corpus-inspired Polish story:** use the ISV corpus as
  inspiration to generate a new Polish story; the Polish story must be
  manually reviewed by the author for Polish-language correctness before
  translation; then compare direct vs authentic-ISV-corpus priming. This
  probes whether corpus-like narrative/style/topic characteristics
  interact with the priming effect, but is **not** the strongest
  generalization test (the generated story may inherit corpus-influenced
  structures/concepts).
- **Phase 2B-B — unseen-topic scientific material:** a Polish educational
  text from biomedical physics / electromedicine, adapted from a real
  academic/teaching source available to the author, not duplicating the
  priming corpus — a genuinely different domain. Framing (legitimate):
  the project asks whether an LLM can act as a practical translator for
  scientific educational material into Interslavic;
  biomedical-physics/electromedicine is an unseen-domain application case
  because the author works in a medical-biophysics environment with
  access to suitable material. **Do not** falsely claim the whole project
  originated as a medical project: the medical/bioengineering material is
  a later application/generalization case.

### Original-story point

The original story used in EXP-001…EXP-004 is **not** about biomedical
physics — the initial priming experiment was already not a
"same-topic retrieval" test. The biomedical/electromedicine Phase 2B test
is still valuable because it creates a deliberately **stronger**
unseen-domain generalization test.

### Gemini corpus handling (recorded rule)

For the main experiment **do not** shorten the corpus specifically for
Gemini. The main methodology remains: Prompt 1 = the same complete
authentic corpus; Prompt 2 = the translation task. Gemini's interface
requirement to split Prompt 1 across two messages is an
interface/context-window limitation recorded as a deviation. Silently
creating a Gemini-specific shorter corpus would introduce a confound. A
future, separate **corpus-length ablation** (25 % / 50 % / 75 % / 100 %)
may be interesting — scientific question: "How much authentic
target-language context is sufficient to obtain the priming effect?" —
but it is a future experiment and must **not** be mixed into Phase 2B.

## 12. Dictionary/morphology intervention status (`COMPLETED` + `PROPOSED`)

Dictionary-based interventions are **already tested**; do not propose
them as untested. Tested: EXP-002 (post-hoc lexical revision); EXP-003 B
(one lexical candidate during generation); EXP-003 C (multiple lexical
alternatives); EXP-003 D (lexical + morphology/grammar scaffolding).
Conceptual intervention ladder A–E and the tested results are documented
in [`docs/translation-method.md`](translation-method.md).

## 13. Publication direction (`PROPOSED`)

Enough experimental material exists to begin preparing a scientific paper
while Phase 2B is completed. Framing:

> Can authentic target-language corpus context improve LLM translation
> into a low-resource constructed language **without fine-tuning**?

(Not: "Which LLM translates Interslavic best?")

Potential working titles (recorded, not final):
- "Corpus Priming Improves LLM Translation into Interslavic: A Repeated
  Multi-Model Study"
- "Can Large Language Models Learn Interslavic from an Authentic Corpus?
  Inference-Time Corpus Priming for Low-Resource Translation"

Indicative structure: introduction; related work; Interslavic as a
low-resource translation case study; resources and corpus construction;
evaluation methodology; EXP-001 baseline; EXP-002 lexical intervention;
EXP-003 lexical/morphological scaffolding; EXP-004 model screening and
corpus priming; repeated-generation analysis; Phase 2B unseen-topic
transfer; practical translation pipeline; limitations; conclusion. The
paper must explicitly distinguish: resource coverage, linguistic
validity, human naturalness, generalization, model-specific behaviour.
An affiliation to a medical-biophysics department can be naturally
connected to the later biomedical/electromedicine application case but
must not misrepresent the origin or scope of the research.

## 14. Literature-review direction (`PROPOSED`)

Maintain a research thread on: low-resource machine translation;
extremely low-resource languages; LLM translation; inference-time
adaptation; in-context learning; corpus priming; target-language
conditioning; multilingual transfer; constructed languages;
Interslavic / Neoslavonic; human intelligibility of Slavic languages;
evaluation of LLM translation. Look for prior work showing **both**
positive and negative effects of additional context — do not assume
"more context = better". Venue selection (low-resource MT/NLP workshops
and related computational-linguistics venues) is not yet final.

## 15. Long-term tool objective (`PROPOSED`)

A reproducible method that says: "Given this Polish input, use
configuration X, then perform steps Y and Z." The eventual software could
automate prompt construction, resource lookup, audit and repair
orchestration while leaving the actual LLM calls under the user's control
where appropriate. Architecture sketch and evaluation philosophy:
[`docs/translation-method.md`](translation-method.md).

## 16. Stopping rule (`CURRENT` rule, recorded Task 028)

The project should not grow indefinitely. Intended sequence:
1. complete the seven-configuration × three-repeat Phase 2B test;
2. run the corpus-inspired story test (Phase 2B-A) if still useful;
3. run the unseen-topic biomedical/electromedicine test (Phase 2B-B);
4. analyse whether priming generalizes;
5. begin writing the paper;
6. optionally perform a small pipeline-optimization experiment;
7. implement the practical translation tool.

Do not add more model families merely to increase the model count unless
a specific scientific question requires it. Do not run more human
evaluation unless a specific expert/validated protocol is justified. The
goal is to move from "more experiments" to "stronger causal/mechanistic
interpretation and a reproducible translation method".

## 17. Source map (where each thread lives)

| Thread | Source of truth |
|---|---|
| Day-by-day project state | `docs/STATE.md` |
| Task roadmap (past + planned) | `docs/ROADMAP.md` |
| Experiment log (canonical per experiment) | `docs/EXPERIMENTS.md` |
| Research notes (4.x per experiment; standing rules L-xxx) | `docs/RESEARCH_NOTES.md` |
| Decision log | `docs/DECISIONS.md` |
| Lessons learned | `docs/LESSONS.md` |
| Resource policy + two metrics | `docs/RESOURCE_POLICY.md` |
| Orthography audit spec | `docs/GRAMMAR_AUDIT.md` + Task-015 records in `docs/STATE.md` |
| EXP-004 design + corpus + protocol | `experiments/exp004-modelscreen/DESIGN.md` |
| EXP-004 repeated-generation report | `experiments/exp004-modelscreen/repeats/REPORT.md` |
| Compact machine-readable research export | `experiments/exp004-modelscreen/assistant-research-bundle/` (Task 027) |
| Intervention ladder + pipelines + evaluation layers | `docs/translation-method.md` |
