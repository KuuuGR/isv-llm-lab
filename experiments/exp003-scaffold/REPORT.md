# EXP-003 — generation-time lexical scaffolding: final report

**Status: COMPLETED — CLOSED (SODA Task 016, 2026-09-05).**
This report is the source of truth for EXP-003. It combines (a) the automatic
evidence collected at intake (Task 011), (b) the character-level orthographic
audit (Task 015), and (c) the human sentence-level forced-choice test
(Task 014, answered by the participant; decoded and analyzed in Task 016).
All historical metrics, classifications, and artifacts are unchanged by this
report; nothing was recomputed or regenerated.

- Design: `DESIGN.md` (Task 009). Scaffold generator: `scripts/build_exp003_scaffold.py`
  (Task 010). Execution/intake: Task 011. Human-test preparation: Task 014.
  Orthographic audit: Task 015. Decoder + this report: Task 016.

---

## 1. What EXP-003 tested

Whether supplying an LLM with a deterministic Polish→Interslavic **lexical
scaffold at generation time** improves Interslavic output relative to
unconstrained direct translation of the same source by the same model
(distinct from EXP-002's post-hoc revision). Four conditions per model:

| Condition | The model received |
|---|---|
| A | Polish source → direct Interslavic translation (within-experiment baseline) |
| B | + lexical scaffold: one canonical candidate per form |
| C | + multiple resource-supported alternatives |
| D | + reliable grammatical annotations (dictionary POS, verb aspect, generated example forms) |

Models in the first wave: **ChatGPT, Claude, Bielik** (4 × 3 = 12 runs).
Of these, **8 runs are complete and usable** (ChatGPT A–D, Claude A–D);
Bielik A–D are incomplete/failed (A/B truncated mid-story, C prompt echo,
D service error) and are preserved as qualitative artifacts, excluded from
the quantitative comparison (D-035). All coverage numbers below are the
Task 008 two-tier evaluator's **canonical / broader resource-supported
coverage** over lexical tokens; A/B/C classification semantics unchanged.

---

## 2. Human preference results (the sentence-level forced-choice test)

**Instrument.** `comparison/sentence_review.md` — 100 questions (50 ChatGPT +
50 Claude), each showing one Polish source sentence and the corresponding
sentence from the four conditions of the same model in a per-question
deterministic randomized neutral order "Version 1..4" (seed `20260905`),
one forced-choice answer, no dictionary checking, no model/condition labels
(protocol D-038/D-039). Private mapping: `comparison/sentence_review_key.json`.

**Answer recovery and provenance (Task 016).** The completed document was
validated before decoding by `scripts/analyze_exp003_sentence_review.py`:
100 question blocks in original order; exactly one checked Version per
question; 399/400 displayed Version texts byte-identical to the private key.
Two provenance notes, both recorded and preserved (the document was not
modified, regenerated, or repaired):

1. **Q58** answer was encoded `[x ]` (checked with stray whitespace) —
   decoded as Version 1; raw encoding preserved.
2. **Q67 Version 2** (condition D, *not chosen*) was accidentally corrupted
   during the answering session (`sę, že` → `, žesę`; same character
   multiset — an editor artifact, not a regeneration). The decoded answer
   (Version 3) is unaffected. One participant comment exists (below).

**No position bias.** Choices per displayed Version: V1 = 25, V2 = 29,
V3 = 22, V4 = 24 (n = 100) — balanced across display positions.

**Choices per production condition — overall (n = 100):**

| Condition | choices | share |
|---|---:|---:|
| A (baseline) | 26 | 26.0 % |
| B (one canonical candidate) | 16 | 16.0 % |
| C (+ alternatives) | 19 | 19.0 % |
| D (+ grammatical annotations) | 39 | 39.0 % |

Exploratory uniformity test vs. uniform (no-preference) choice: χ²(3) =
12.56, p ≈ 0.006 (overall); the choices are not uniform.

**Per model:**

| Model (n = 50) | A | B | C | D |
|---|---:|---:|---:|---:|
| ChatGPT | 13 (26.0 %) | 6 (12.0 %) | 13 (26.0 %) | 18 (36.0 %) |
| Claude | 13 (26.0 %) | 10 (20.0 %) | 6 (12.0 %) | 21 (42.0 %) |

χ²(3) vs. uniform: ChatGPT p ≈ 0.12 (not distinguishable from uniform at
α = 0.05), Claude p ≈ 0.02.

**Guidance vs. baseline.** Pooling the three scaffolded conditions
(B + C + D): **74 % guided vs. 26 % baseline — identically for both models
(37/50 each)**. The unguided baseline was chosen at ≈ chance level (26 % vs.
25 % expected), i.e. the participant did not prefer the baseline; scaffolded
versions were preferred ~3:1.

**Dialogue subset.** 35 of the 100 questions are dialogue; dialogue choices
per condition: A 7, B 9, C 10, D 9.

**Participant comments.** Exactly one comment was recorded (Q7, ChatGPT),
verbatim and preserved as qualitative, non-expert provenance — it is a
vocabulary-uncertainty note, not a linguistic annotation, and it is not
treated as evidence:

> "a do not know whe 1 have prababi not prababica" (sic)

---

## 3. Automated evidence (Task 011, unchanged)

Run-level metrics from `outputs/<run>/evaluation.json` (canonical /
broader coverage over lexical tokens; unresolved rate):

| Model | Cond | canonical cov. | broader cov. | unresolved rate | total tokens |
|---|---|---:|---:|---:|---:|
| ChatGPT | A | 76.27 % | 87.05 % | 23.73 % | 1513 |
| ChatGPT | B | 85.72 % | 90.80 % | 14.28 % | 1510 |
| ChatGPT | C | 84.82 % | 89.16 % | 15.18 % | 1516 |
| ChatGPT | D | 84.04 % | 88.82 % | 15.96 % | 1512 |
| Claude | A | 75.81 % | 87.51 % | 24.19 % | 1513 |
| Claude | B | 78.97 % | 86.42 % | 21.03 % | 1510 |
| Claude | C | 75.41 % | 84.47 % | 24.59 % | 1510 |
| Claude | D | 85.62 % | 92.02 % | 14.38 % | 1501 |

ChatGPT: every scaffolded condition (B/C/D) raises canonical coverage over A
by ≈ 8–9.5 pp; B is the automated best. Claude: only D clearly raises
coverage (≈ +9.8 pp canonical, +4.5 pp broader); B gains are small and C is
flat-to-worse vs. A. These are run-level whole-story numbers (the human test
covered a filtered subset of sentences, D-039); Bielik remains excluded.

---

## 4. Character-level orthographic audit (Task 015, unchanged)

Per-run outside-inventory counts (official Interslavic alphabet, D-040) and
a **non-name** refinement that removes letters inside the story's proper-name
tokens (`Bronisława`, `Przemysława` and inflections — source-inherent and
kept verbatim by every condition):

| Model | Cond | outside inv. | cyrillic | polish-spec. | other Latin | ortho non-name |
|---|---|---:|---:|---:|---:|---:|
| ChatGPT | A | 34 | 0 | 13 | 21 | 15 |
| ChatGPT | B | 71 | 3 | 34 | 34 | 7 |
| ChatGPT | C | 72 | 0 | 38 | 34 | 8 |
| ChatGPT | D | 82 | 0 | 43 | 39 | 16 |
| Claude | A | 82 | 14 | 34 | 34 | 14 |
| Claude | B | 101 | 25 | 40 | 36 | 33 |
| Claude | C | 138 | 45 | 59 | 34 | 70 |
| Claude | D | 79 | 9 | 35 | 35 | 11 |

Main findings: (a) raw polish-spec./other-Latin counts are dominated by the
proper-name pass-through (≈ 26 ł/w per run), so the **raw** condition deltas
are mostly names; (b) the genuine **non-name** contamination is dominated by
Cyrillic in Claude runs (A 14 → D 9, B 25, C 45 — incl. intra-word Cyrillic
in C) and by a few Polish/Czech-flavored forms elsewhere; (c) ChatGPT is
orthographically cleanest (non-name ≤ 16 across conditions, almost all
`á é í`-type Czech-flavored vowels, no Cyrillic except 3 letters in B).

---

## 5. Human preference vs. automated metrics

**Question-level pairing is not possible** (coverage is run-level, human
choices are sentence-level within each run), so the comparison is made at
the **condition level** (2 models × 4 conditions = 8 points).

| Model | Cond | human share | canon. | broader | unresolved | ortho non-name |
|---|---|---:|---:|---:|---:|---:|
| ChatGPT | A | 26.0 % | 76.27 | 87.05 | 23.73 | 15 |
| ChatGPT | B | 12.0 % | 85.72 | 90.80 | 14.28 | 7 |
| ChatGPT | C | 26.0 % | 84.82 | 89.16 | 15.18 | 8 |
| ChatGPT | D | 36.0 % | 84.04 | 88.82 | 15.96 | 16 |
| Claude | A | 26.0 % | 75.81 | 87.51 | 24.19 | 14 |
| Claude | B | 20.0 % | 78.97 | 86.42 | 21.03 | 33 |
| Claude | C | 12.0 % | 75.41 | 84.47 | 24.59 | 70 |
| Claude | D | 42.0 % | 85.62 | 92.02 | 14.38 | 11 |

Exploratory Spearman (8 points; single non-expert participant — descriptive
only, no inference): human share vs. broader coverage +0.49, canonical +0.23,
unresolved −0.23, raw outside-inventory −0.20, ortho non-name −0.16. None is
strong, and pooling across models conflates them, so the directional reading
below is per model:

- **Claude: the two signals agree at the extremes.** D is both the automated
  best (85.6 / 92.0, lowest unresolved 14.4 %) and the human favorite
  (42 %); C is the automated worst (75.4 / 84.5, unresolved 24.6 %), the
  orthographically worst (non-name 70), and the human least favorite (12 %).
  The mid-points A/B swap (automated: B > A; human: A > B).
- **ChatGPT: the signals diverge sharply.** B is the automated best
  (85.7 / 90.8, lowest unresolved, cleanest orthography) yet the human
  **least** preferred (12 %); D — not the automated best (84.0 / 88.8) but
  the only condition with grammatical annotations that changed wording in a
  way the reader preferred — is the human favorite (36 %). Human preference
  did not track resource coverage for ChatGPT.
- **Orthographic sanity** is a weak negative correlate in the raw and non-name
  forms and cannot explain ChatGPT's preference for D (D is not the cleanest);
  it tracks the Claude extremes only (the dirtiest condition C is the least
  preferred, the cleanest-condition-among-scaffolded D the most preferred).

**Conclusion of the comparison.** Human sentence preference and resource
coverage point in **similar directions for Claude (especially at the D/C
extremes) but in different directions for ChatGPT** (the coverage-best B is
human-worst). No single signal is ground truth: resource-grounded lexical
coverage measures dictionary-justifiability, character-level sanity measures
orthographic hygiene, and the human forced choice measures holistic
naturalness as read by one Polish-native non-expert. They answer different
questions and are reported separately (D-041).

---

## 6. What EXP-003 supports and what it does not support

**Supported (on this one Polish story, n = 8 usable runs):**

- Generation-time lexical scaffolding (B/C/D) is systematically preferred
  over the unguided baseline by the participant: **74 % guided vs. 26 %
  baseline, identically for ChatGPT and Claude** — a preference not
  attributable to display position.
- Scaffolding raised canonical resource coverage for ChatGPT (all of
  B/C/D: +8–9.5 pp) and for Claude only D clearly (+9.8 pp).
- For Claude, the condition that is both coverage-best and orthographically
  cleanest (D, grammatical annotations) is also the human favorite; the
  coverage-worst and orthographically-dirtiest (C) is the human least
  favorite.
- The character-level audit (Task 015) caught genuine anomalies the lexical
  evaluator cannot see (Cyrillic inside Latin words in Claude C), and the
  anomaly pattern is a plausible component of the human impression at the
  Claude extremes.

**Not supported / not claimable:**

- No general statement that "scaffolding beats baselines" beyond this story,
  these prompts, this participant. n = 100 questions, one participant, two
  models.
- No claim that resource coverage predicts naturalness: ChatGPT-B is the
  counterexample (automated best, human worst).
- No composite "quality score" is created or implied (D-042).
- No claim about Bielik (excluded; qualitative negative case only).
- No claim about which *specific* scaffold component caused D's preference:
  D packages candidate + POS/aspect + example forms together; the experiment
  cannot separate these mechanisms.
- The single comment and the Q58/Q67 artifacts are provenance, not data.

**Limitations:** one story; one non-expert participant; forced-choice on
sampled sentences (not full texts); run-level automated metrics vs.
sentence-level human choices (condition-level comparison only); a weak
per-question instrument (no "both bad" option); the two provenance notes
above; no significance testing beyond exploratory χ²/Spearman with the
caveats stated.

---

## 7. Decisions and lessons recorded

- D-038/D-039 (test protocol), D-040/D-041 (orthographic audit), and now
  **D-042** (EXP-003 closure interpretation rules: separate signals, no
  composite score, exploratory statistics only, no further human-evaluation
  exercises) and **D-043** (completed-questionnaire provenance handling:
  validate before decoding; document anomalies — e.g. Q67 — and never
  regenerate or repair the participant document). Lessons **L-032**
  (completed-questionnaire provenance) and **L-033** (automated-best ≠
  human-preferred; signals can diverge per model). See `docs/DECISIONS.md`
  and `docs/LESSONS.md`.

## 8. Artifacts

- Participant document + key: `comparison/sentence_review.md`,
  `comparison/sentence_review_key.json` (unchanged).
- Decoded results + full JSON: `comparison/sentence_review_results.md`,
  `comparison/sentence_review_results.json` (Task 016; deterministic;
  `scripts/analyze_exp003_sentence_review.py`).
- Orthographic audit: `outputs/orthography_report.{json,md}` per experiment
  (Task 015). Run metrics: `outputs/<run>/evaluation.json` (Task 011).

## 9. Next step (not started here)

EXP-004 Phase 1 — practical model screening with a **clean direct-translation
baseline** (no scaffolding yet), roster and protocol finalized in
`experiments/exp004-modelscreen/DESIGN.md` §12/§5 (Task 016); execution gated
on design approval + access confirmations. No new human-evaluation exercise
will be designed (EXP-003 collected the planned human signal).
