# EXP-004 full analysis — Phase 1 → Phase 2A corpus priming (SODA Task 024, 2026-09-07)

This directory holds the **Task-024 research analysis** of the completed
EXP-004 dataset: 18 original configurations + 2 exploratory Dola 3.8
configurations, each with one Phase-1 direct generation and one Phase-2A
corpus-primed generation.

The analysis is a **read-only, deterministic transformation** of the
recorded evidence. It never calls an LLM, never modifies raw outputs or the
corpus, adds no new evaluator, and defines no composite score.

## Repository discipline

Everything in this directory except this README is **gitignored** (derived
artifacts stay local, like all EXP-004 outputs). Regenerate any of it with:

```bash
.venv/bin/python scripts/analyze_exp004_phase2a.py all   # dataset + tables + charts + poster
.venv/bin/python scripts/analyze_exp004_phase2a.py analyze
.venv/bin/python scripts/analyze_exp004_phase2a.py charts
.venv/bin/python scripts/analyze_exp004_phase2a.py poster
```

Chart regeneration is **byte-identical across runs** (verified by tests);
dataset/tables differ only in the recorded `generated_at` stamp.

## Artifacts (all local except this README)

| file | contents |
|---|---|
| `dataset.json` | assembled 20-configuration dataset: P1 + P2A metrics, orthography, A/B/C buckets, exact P1→P2A deltas, pairing ids, input hashes, `exploratory: true` on Dola rows |
| `analysis.json` | machine-readable analysis: rankings (Phase 1 + Phase 2A, four dimensions each), Δ table sorted by Δ canonical, descriptive statistics + exact sign/permutation tests, Spearman baseline-dependence and baseline-vs-primed correlations, per-family tables, orthography summary, master table |
| `analysis.md` | human-readable quantitative report (sections 1–13 mirror the Task-024 brief) |
| `figures/chart_a..g.svg` | charts A–G (deterministic SVG; no plotting dependency exists in the repo and none was added) |
| `poster.md`, `poster.html` | first research-poster draft (HTML embeds the SVG charts) |

Source datasets (SHA-256 recorded inside `dataset.json`/`analysis.json`):
`experiments/exp004-modelscreen/outputs/roster.json` (Phase 1),
`experiments/exp004-modelscreen/phase2a/outputs/roster.json` (Phase 2A),
`experiments/exp004-modelscreen/phase2a/outputs/compare.json` (pairing +
recorded deltas). The join is on `baseline_run_id`; every recomputed delta
is cross-checked against `compare.json` (no drift — enforced by the
script and by tests).

## Headline results (numbers from `analysis.md` / `analysis.json`)

- **Δ canonical coverage (Phase-2A − Phase-1), original 18:** mean
  **+6.00 pp**, median +4.92 pp, sd 3.39 pp, range +1.74 … +14.33 pp;
  **positive in 18/18**. Including the two exploratory Dola rows:
  mean +7.15 pp, sd 5.90 pp (Fast dominates the tails).
- **Δ broader resource-supported coverage, original 18:** mean **+2.36 pp**,
  median +2.14 pp, range −0.92 … +11.23 pp; **positive in 14/18**.
- **Largest original-18 canonical deltas:** Gemini 3.6 Flash ON +14.33 pp,
  Claude Sonnet 5 +11.66 pp, Qwen 3.7 Plus Fast +8.94 pp, DeepSeek V3
  Instant ON +8.55 pp, Claude Sonnet 5 max +8.31 pp. Smallest: Gemini 3.1
  Pro +1.74 pp, Qwen 3.8 Max Fast +3.04 pp, Kimi +3.06 pp, Qwen 3.8 Max
  Think +3.07 pp.
- **Exploratory Dola:** Fast +28.20 pp canonical (38.87 % → 67.07 %,
  broader +27.14 pp, ortho-out 468 → 24); Pro +6.67 pp (65.08 % →
  71.75 %, broader −0.01 pp, ortho-out 63 → 17). See the baseline-dependence
  warning below — **the large Fast change is observed behaviour, not
  evidence of stronger corpus learning** (Fast had the lowest Phase-1
  baseline of all 20 configurations).
- **Baseline dependence (descriptive Spearman, original 18):** Phase-1
  canonical vs Δ canonical ρ = **−0.86**; Phase-1 broader vs Δ broader
  ρ = **−0.84** (n = 18). Lower Phase-1 baselines gained more.
- **Baseline vs primed (descriptive Spearman, original 18):** Phase-1
  canonical vs Phase-2A canonical ρ = **+0.45**; broader ρ = **+0.37**
  (n = 18) — priming shifts the ordering, not just the level.
- **Exploratory paired tests (original 18):** exact two-sided sign test
  18+ / 0− (p ≈ 7.6e-6 for canonical; 14+ / 4−, p ≈ 0.031 for broader);
  exact sign-flip permutation test on the mean p ≈ 7.6e-6 (canonical) and
  p ≈ 9.6e-4 (broader). **Exploratory only** — n = 18 paired generations,
  one direct + one primed per configuration; not repeated sampling, no
  causal estimate.

## Interpretation (supported / suggestive / not established)

**Supported** — what the collected data directly show:

1. Corpus priming (one primed run) was followed by higher canonical
   resource coverage in **18/18 original configurations** and in all 20
   including Dola; descriptive mean +6.0 pp (original 18).
2. Broader resource-supported coverage rose in **14/18** original
   configurations (mean +2.36 pp) — a smaller, less uniform shift than
   canonical coverage.
3. Observed canonical deltas were **largest for the lowest Phase-1
   baselines** (ρ ≈ −0.86 / −0.84), including the two extreme cases
   (Dola Fast, Gemini 3.6 Flash ON, Qwen 3.7 Plus Fast all started low).

**Suggestive** — patterns worth investigating later:

- Configurations that already scored high in Phase 1 gained least, which
  is consistent with a ceiling/baseline-dependence effect; a controlled
  repeated-generation experiment could separate this from a genuine
  priming gradient.
- In some families the recorded "thinking ON" run out-performed its OFF
  twin (DeepSeek Instant/Expert, Gemini 3.6 Flash), but GPT-5.6 Luna OFF
  slightly exceeded ON and Qwen Fast/Thinking pairs are mixed — no general
  thinking-mode conclusion.
- Dola Pro's +6.67 pp (from a 65 % baseline) sits close to the
  original-18 low-baseline pattern; Dola Fast's +28.20 pp is *consistent
  with* the same baseline-dependence relation extrapolated (it starts far
  below the original-18 range), which makes "Fast learns more" an
  untested hypothesis, not a finding.

**Not established** — claims this experiment cannot support:

- A causal priming effect of any specific size (n = 1 per condition per
  configuration; deltas also contain stochastic variation, interface
  behaviour, configuration differences and baseline dependence).
- That priming improves *naturalness* (no naturalness metric; canonical
  coverage measures resource coverage, not validity or style).
- That Dola Fast "responds particularly strongly to priming".
- That any configuration is "the best" for producing Interslavic (four
  dimensions are reported separately; no composite, no winner).
- That canonical coverage predicts human preference (EXP-003 is a
  separate one-participant experiment and is **not** used here as a
  selection criterion).
- That the three-register corpus is better than a one-register corpus (no
  comparison condition).
- That thinking/reasoning mode generally improves Interslavic generation.
- That baseline quality predicts priming response as a causal rule
  (descriptive ρ only).

## Configurations worth investigating next (research candidates, not winners)

Small set, each with an open question for the next experiment:

- **Claude Sonnet 5 (Medium).** +11.66 pp canonical (72.97 % → 84.63 %),
  broader 91.0 %, **zero** outside-inventory characters, but collected
  under free-tier interruptions/continuations. Question: does a clean,
  repeated run reproduce the delta and the clean orthography?
- **DeepSeek V3 Expert (DeepThink ON).** Highest Phase-2A canonical of the
  original 18 (85.63 %) with zero orthography anomalies; Expert OFF also
  strong. Question: is the ON/OFF gap robust across repeats, and does it
  survive a fresh control?
- **Qwen 3.8 Max Fast.** High Phase-1 (82.35 %) → highest-tier Phase-2A
  (85.38 %) with a small delta (+3.04 pp) — a ceiling-adjacent
  configuration; the strongest *absolute* primed scores in its family.
  Question: can a better-controlled condition show any gain over its
  already-high baseline, or is it at ceiling?
- **Gemini 3.6 Flash (extended thinking ON).** Largest original-18 delta
  (+14.33 pp canonical, +11.23 pp broader) from a low baseline — but the
  corpus was delivered in two messages and the toggle was re-enabled per
  prompt. Question: is the large delta a priming response or a
  baseline/low-quality-artifact effect?
- **Dola 3.8 Fast (explicitly exploratory).** Largest observed change
  (+28.20 pp) from the lowest baseline in the experiment; identity is
  author-recorded and not independently verifiable; not part of the
  original roster. Question: only if a properly controlled, repeated
  within-Dola experiment can be run — does the effect survive, and does
  Fast actually verify as "Dola 3.8 Fast"?

## Next experiments (recommendations only — not executed)

1. **Controlled repeated generation (shortlist, n ≥ 3 per condition).**
   Repeat direct and primed runs for the research candidates above to
   separate stochastic variation from the priming signal and to estimate
   per-configuration delta distributions instead of single deltas.
2. **Phase 2B — unseen-topic generalization.** Fresh Wikipedia-style
   (encyclopedic) source text on a topic absent from the priming corpus,
   same corpus-priming protocol, to test whether the observed canonical
   gains transfer beyond the primed task/story.
3. **Matched-variant priming comparison with strict interface controls.**
   Focus on the ON/OFF and Fast/Thinking pairs inside DeepSeek, Gemini and
   Qwen (same provider session hygiene, controlled corpus delivery,
   documented toggle state) to decide whether the recorded pair
   differences are interface artifacts or model behaviour.

No experiment in this list has been started; Phase 2B remains not
executed.

## Practical interface constraints (separate dimension, Task 021/023 notes)

Reproduced in the master-table `Notes` column and documented in
`docs/EXPERIMENTS.md` (Task 021/023 entries) — never mixed into the
linguistic metrics:

- **Claude (Sonnet 5, Sonnet 5 max):** free-tier token exhaustion and
  repeated waits/continuations; the max run took > 45 min; run 12's P2A
  intake is `partial` (end marker `**KONEC**` bold-wrapped; usable = no by
  the end-marker rule, still evaluated).
- **Gemini:** interface one-message limit forced a **two-message corpus**
  delivery (~83 % + ~17 %); Gemini 3.1 Pro ingested the corpus in a 3.6
  Flash session and then translated in 3.1 Pro (documented deviation:
  ingestion model ≠ translation model); the extended-thinking toggle reset
  between messages and was re-enabled per prompt.
- **GPT Interslavic Teacher:** custom GPT whose built-in system prompt is
  unknown (recorded confound D-018).
- **Dola (exploratory):** identity is author-recorded in the prompt header
  only — not independently verifiable under the web interface available to
  the author.
- **GLM 4.5:** excluded — Phase-1 intake failed (no Phase-2A run).

## Chart inventory (deterministic SVG, `figures/`)

- `chart_a.svg` — Phase 1 vs Phase 2A canonical coverage (grouped bars,
  20 configs; red edge marker = exploratory Dola).
- `chart_b.svg` — priming Δ canonical coverage, descending (Dola Fast
  visible at the top without hiding the original 18).
- `chart_c.svg` — Phase 1 vs Phase 2A broader coverage (equivalent to A).
- `chart_d.svg` — Phase-2A canonical × broader scatter (numbered; legend
  lanes on the right).
- `chart_e.svg` — Phase-2A outside-inventory characters by audit category.
- `chart_f.svg` — Phase-1 canonical × Δ canonical scatter with descriptive
  OLS trend over the original 18 (Dola Fast/Pro highlighted).
- `chart_g.svg` — model configuration map: family lanes, P1 → P2A
  canonical dumbbells with Δ labels (poster base).

No single "winner score" exists anywhere in the analysis.

## Tests

`tests/test_analyze_exp004_phase2a.py` (19 tests): 20-configuration
composition, original/Dola separation, Dola pairing, exact deltas +
agreement with `compare.json`, loud failure on missing metrics/baseline,
no fabricated metrics, deterministic master-table/Δ-table ordering,
deterministic + known statistics and p-values, deterministic chart inputs,
byte-identical chart regeneration. Full suite: green.

## Follow-up: controlled repeated generation (Task 025, prepared 2026-09-07)

Because every delta in this analysis rests on one direct + one primed
generation per configuration (n = 1 per condition), the recommended
controlled-repeat experiment was prepared under
`../repeats/` (`README.md`, `REPORT.md`): 3 independent fresh-session
replicates per condition for the original 18 configurations (108 primary
planned runs) + optional exploratory Dola repeats (12). Once collected and
analysed (`scripts/analyze_exp004_repeats.py`, figures A–E at
`../repeats/analysis/`), it will show which Task-024 deltas exceed the
models' own stochastic variation and whether the descriptive
baseline-dependence ρ ≈ −0.86 survives repetition.

