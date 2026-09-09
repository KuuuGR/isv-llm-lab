# EXP-004 — Phase repeat: controlled repeated generation, stochastic variation (REPORT)

**Status: EXECUTED, COLLECTED, AUDITED AND ANALYSED (Task 026, 2026-09-09).**
120 planned runs (Task-025 kit, generation date 2026-09-08); the research
lead collected **114**; the audit reconciled every run against the
Task-025 manifest/authoritative renders (no raw output was modified);
**106 runs passed the unmodified intake gate (usable)**, 8 are partial
(end-marker soft failures), 0 failed, **6 were never collected**. All
usable runs were evaluated with the unmodified deterministic evaluator +
orthography audit and analysed with
`scripts/analyze_exp004_repeats.py`. Machine-readable audit:
`outputs/audit.json` (+ `outputs/audit.md`); roster:
`outputs/roster.json`/`roster.md`; full deterministic analysis:
`analysis/` (`analysis.md`, `analysis.json`, `dataset.json`, figures A–E).

**Headline (descriptive, Task-025 statistics):** with the exact same task
generated three times per condition, the primed condition measured above
the direct condition for **every configuration that has both conditions
usable (16/16)**, repeated Δ canonical mean **+6.93 pp** (range
+1.72…+15.91); the old Task-024 single-run direction was reproduced in
**15/15** configurations that have an old delta; and the old *magnitudes*
were mostly the same ballpark (mean old Δ +6.33 pp vs mean new Δ
+6.73 pp on the same 15 rows). Normal within-condition stochastic
variation (median SD ≈ 1.5 pp direct / ≈ 0.9 pp primed) is **smaller
than the observed priming shift for most configurations**, but not for
all (e.g. Qwen 3.8 Max Fast primed SD 5.83 pp vs repeated Δ +1.72 pp).
Full details below — this is a descriptive distribution comparison, not a
causal claim.

---

## 1. Research question

For the same model/configuration and the same translation task, how much
does measured Interslavic resource coverage vary between independent
generations, and is the observed Phase-2A corpus-priming shift larger than
that variation?

> **old (Task 024):** `P2A_single − P1_single` (one direct + one primed
> generation)
> **new (Task 025/026):** `mean(primed replicates) − mean(direct
> replicates)` (3 independent fresh-session generations per condition),
> reported against each model's own within-condition spread.

## 2. Design (unchanged from the kit)

- **Population:** the original **18 usable EXP-004 configurations**
  (Phase-1 numbers 01–10, 12–19; GLM 4.5 excluded).
- **Condition direct:** 3 independent fresh-session generations with the
  authoritative Phase-1 direct prompt.
- **Condition primed:** 3 independent fresh-session generations with the
  Phase-2A protocol (corpus msg1 → translation msg2 in one session).
- **Replicates r01–r03:** replication blocks, not matched samples; each
  replicate is a fresh session with byte-identical prompt content.
- No scaffolding, no post-hoc repair, no human evaluation, no Phase 2B.

## 3. Sample and collection reconciliation (audit)

| population | planned | collected | usable (complete) | partial | invalid | missing |
|---|---:|---:|---:|---:|---:|---:|
| **Primary** (18 configs) | **108** | 102 | **99** | 3 | 0 | **6** |
| Exploratory (Dola Fast/Pro) | 12 | 12 | 7 | 5 | 0 | 0 |
| **Total** | **120** | 114 | **106** | 8 | 0 | 6 |

All collected runs were registered msg2-style (raw reply appended to the
canonical prompt file after its `## Output` marker; reply extracted
byte-for-byte, never modified). No duplicate outputs, no source-echo, no
cross-run output contamination was found (audit). All 114 collected
outputs passed the integrity checks; 8 are intake **partial** solely
because the final non-empty line is a markdown-wrapped end marker
(`## KONEC`, `# KONEC`, `**KONEC**`, `## Konec`, `# KONĘC`) that the
unmodified gate does not accept; content was otherwise complete
(translation + end marker present). Per protocol these 8 are preserved,
documented and **excluded from the usable statistics** (not repaired).

### Missing runs (never collected — pristine prompt files, not fabricated)

The following six primed runs have no collected record (the prompt file
is byte-identical to the prepared kit, i.e. no reply was ever appended):

- `2026-09-08__google__gemini-3.1-pro__extthinkon__primed__r01/r02/r03`
- `2026-09-08__alibaba__qwen-3.8-max__thinking__primed__r01/r02/r03`

Consequence: for **Gemini 3.1 Pro (extended thinking ON)** and **Qwen
3.8 Max — Thinking** the repeated primed condition has **n = 0**; no
repeated Δ is computable for these two configurations, and their Task-024
single-run deltas (+1.74 pp and +3.07 pp) cannot be checked under
repetition.

### Runs whose intake is partial (preserved, excluded from usable stats)

- Primary: `gpt-isv-teacher … direct r02 (# KONEC)`, `… direct r03
  (# KONĘC)`, `deepseek-v3-instant deepthinkon primed r02 (**KONEC**)`
  → GPT Interslavic Teacher repeated **direct n = 1**; DeepSeek V3
  Instant ON repeated **primed n = 2**.
- Exploratory Dola Fast: direct r01 (`## Konec`), r02 (`## KONEC`), r03
  (`# KONEC`), primed r01/r02 (`## KONEC`) → Dola Fast repeated
  **direct n = 0, primed n = 1**.

## 4. Protocol deviations (recorded, not repaired)

| deviation | affected | classification | usability |
|---|---|---|---|
| Grok model identity recorded in operator-metadata headers (`unknown (unknown)` → `Grok 4.5, built by xAI (fast)`; 9 files, all 6 Grok runs) | 6 Grok runs | operator-metadata header edit; model-facing prompt bodies byte-identical to the kit; identity is operator-reported, not independently verifiable | usable |
| Claude Sonnet 5 — max: thinking/reasoning **OFF** during repeats (operator-disabled; enabled mode operationally impractical) | 6 Claude Max runs (direct+primed × r01–r03) | execution deviation; differs from Task-024 Phase-1/2A (intensive reasoning); configuration NOT renamed | usable with recorded deviation — comparability with Task 024 affected |
| Gemini primed reference-texts message delivered as two messages (`continue last prompt:`-style split) | 6 Gemini 3.6 Flash primed runs (OFF+ON × r01–r03) | interface deviation; stored msg1 records carry the byte-identical study+corpus, so the complete corpus was available before the task; same class as the Task-021/024 Gemini deviation | usable with recorded interface deviation |
| Dola Pro primed r03 msg1: one extra blank line in the operator header | 1 run | header whitespace only; corpus tail byte-identical | usable |
| Fresh-session evidence | all 114 | msg2-style records carry no machine-visible session provenance | `fresh_session_proof: unavailable` (absence of proof is not proof of violation) |

Hash gates: source story and Phase-2A corpus SHA-256 match the
authoritative records; every collected record's prompt part was validated
byte-identical (or header-edit-only) against the deterministic Task-025
renders. **No raw output was rewritten, normalized or repaired.**

## 5. Intake / evaluation (unmodified pipeline)

Verdicts above come from the unchanged Phase-1 completeness gate
(`run_exp004_repeats.py verify`), metrics from the unchanged Task-008
evaluator (`isv_eval.cli`) and the Task-015 orthography audit — same code
and same metric definitions as Phase 1 / Phase 2A / Task 024.

## 6. Per-configuration descriptive statistics (usable replicates, n ≤ 3)

Full table in `analysis/analysis.md` §3. Coverage means here are
canonical resource coverage (%). Direct / primed over the usable
replicates of each condition:

| configuration | direct n | dir mean (SD) | primed n | primed mean (SD) | repeated Δ | old Δ |
|---|---:|---:|---:|---:|---:|---:|
| GPT-5.6 Luna — thinking OFF | 3 | 76.84 (0.43) | 3 | 82.50 (1.68) | +5.67 | +4.14 |
| GPT-5.6 Luna — thinking ON | 3 | 75.42 (2.81) | 3 | 80.13 (1.28) | +4.71 | +3.76 |
| GPT Interslavic Teacher | 1 | 75.52 (—) | 3 | 83.86 (0.85) | +8.35 | +6.18 |
| Claude Sonnet 5 — Medium | 3 | 74.57 (1.96) | 3 | 83.69 (0.80) | +9.12 | +11.66 |
| Claude Sonnet 5 — max (thinking OFF) | 3 | 73.37 (1.49) | 3 | 83.28 (0.49) | +9.91 | n/a (Task-021 run partial) |
| Gemini 3.1 Pro — ext think ON | 3 | 79.59 (0.70) | 0 | — | n/a | +1.74 |
| Gemini 3.6 Flash — ext think OFF | 3 | 73.26 (0.91) | 3 | 85.14 (0.22) | +11.88 | +3.20 |
| Gemini 3.6 Flash — ext think ON | 3 | 67.02 (2.46) | 3 | 82.93 (0.63) | +15.91 | +14.33 |
| DeepSeek V3 Instant — OFF | 3 | 75.26 (1.14) | 3 | 82.15 (1.05) | +6.89 | +7.58 |
| DeepSeek V3 Instant — ON | 3 | 74.75 (0.73) | 2 | 81.31 (0.19) | +6.56 | +8.55 |
| DeepSeek V3 Expert — OFF | 3 | 78.35 (3.67) | 3 | 84.81 (0.99) | +6.47 | +4.70 |
| DeepSeek V3 Expert — ON | 3 | 81.33 (1.50) | 3 | 85.10 (0.64) | +3.77 | +5.14 |
| Grok | 3 | 79.33 (2.01) | 3 | 83.83 (0.88) | +4.50 | +7.18 |
| Kimi K2.6 Instant | 3 | 74.03 (0.81) | 3 | 80.11 (0.69) | +6.08 | +3.06 |
| Qwen 3.8 Max — Fast | 3 | 80.09 (1.52) | 3 | 81.82 (5.83) | +1.72 | +3.04 |
| Qwen 3.8 Max — Thinking | 3 | 78.76 (0.90) | 0 | — | n/a | +3.07 |
| Qwen 3.7 Plus — Thinking | 3 | 79.82 (1.04) | 3 | 82.12 (1.43) | +2.30 | +3.47 |
| Qwen 3.7 Plus — Fast | 3 | 65.60 (2.24) | 3 | 72.58 (3.63) | +6.98 | +8.94 |

SD = sample SD over n usable replicates (pp); with n = 3 these are
noisy descriptive quantities, not precise population estimates.

### Exploratory Dola (separate; never primary)

| configuration | direct n | dir mean (SD) | primed n | primed mean (SD) | repeated Δ | old Δ |
|---|---:|---:|---:|---:|---:|---:|
| Dola 3.8 — Fast | 0 | — | 1 | 71.34 (—) | n/a | +28.20 |
| Dola 3.8 — Pro | 3 | 62.65 (6.96) | 3 | 75.06 (1.82) | +12.41 | +6.67 |

Dola Fast's Task-024 +28.20 pp **cannot be checked under repetition**
with the collected data: all three repeated direct runs are intake
partial (end-marker) and two of the three primed runs are partial; the
single usable primed replicate measured 71.34 % (Task-024 primed single:
67.07 %). Dola Pro shows a repeated Δ of +12.41 pp (larger than its
Task-023/024 single-run +6.67 pp) but with a wide direct spread
(SD 6.96 pp, range 13.06 pp).

## 7. How large is stochastic variation vs the priming shift?

Across the primary configurations with n = 3 usable replicates in a
condition, the observed within-condition spread (canonical coverage) is:

- **direct:** SD median ≈ 1.49 pp, max 3.67 pp; range median ≈ 2.6 pp
  (largest: DeepSeek Expert OFF 7.18 pp; GPT-5.6 Luna ON 5.15 pp).
- **primed:** SD median ≈ 0.87 pp, max 5.83 pp; range median ≈ 1.7 pp
  (largest: Qwen 3.8 Max Fast 10.34 pp).

The repeated priming shift is larger than the within-condition spread for
**13 of the 16** configurations with a computable Δ: repeated Δ >
primed SD in all but Qwen 3.8 Max Fast (+1.72 vs SD 5.83), Qwen 3.7 Plus
Thinking (+2.30 vs SD 1.43 — shift still above SD), and Gemini 3.6 Flash
OFF is the clearest case *for* the shift (+11.88 vs SD 0.22). The shift
exceeds the *direct* spread in 15 of 16 (all except Qwen 3.8 Max Fast).
Figures A–C show the replicate-level evidence; do not collapse these into
one scalar.

## 8. Task-024 single-run vs repeated estimate (Figure D)

For all 15 primary configurations with a Task-024 old delta the **sign is
preserved**: every repeated Δ is positive and in the same direction as
the old single-run Δ. Magnitudes on the same 15 rows: old mean +6.33 pp
(min +3.04, max +14.33); repeated mean +6.73 pp (min +1.72, max
+15.91). Per-row classification (no arbitrary thresholds; descriptive):

- **Similar magnitude (new within ±3 pp of old):** Qwen 3.7 Plus Fast
  (+6.98 vs +8.94), Qwen 3.7 Plus Thinking (+2.30 vs +3.47), Qwen 3.8 Max
  Fast (+1.72 vs +3.04), Claude Sonnet 5 Medium (+9.12 vs +11.66),
  DeepSeek Expert ON (+3.77 vs +5.14), DeepSeek Instant OFF (+6.89 vs
  +7.58), DeepSeek Instant ON (+6.56 vs +8.55), DeepSeek Expert OFF
  (+6.47 vs +4.70), GPT-5.6 Luna OFF (+5.67 vs +4.14), GPT-5.6 Luna ON
  (+4.71 vs +3.76), GPT Interslavic Teacher (+8.35 vs +6.18), Grok
  (+4.50 vs +7.18) — 12 rows.
- **Substantially larger under repetition (new > old + 3 pp):** Gemini
  3.6 Flash OFF (+11.88 vs +3.20), Kimi (+6.08 vs +3.06) — 2 rows.
- **Same direction, slightly larger:** Gemini 3.6 Flash ON (+15.91 vs
  +14.33) — 1 row (also the largest shift in both datasets).
- **Not computable:** Claude Sonnet 5 max (no old delta), Gemini 3.1 Pro
  and Qwen 3.8 Max Thinking (primed not collected).

Interpretation discipline: this is descriptive. The headline pattern —
the Task-024 direction was robust; the magnitudes were usually
reproduced within a few pp, occasionally larger, never reversed — is
*consistent with* a corpus-priming effect larger than typical
run-to-run variation for most of these models, but it is **not** a proof
of a universal or causal priming effect (see §11).

## 9. Re-evaluation of the Task-024 candidates (descriptive)

- **Claude Sonnet 5 — Medium:** old 72.97 → 84.63 (+11.66). Repeated:
  74.57 → 83.69 (**+9.12**, SD primed 0.80). Direction reproduced,
  magnitude similar/slightly smaller; primed performance very stable
  across replicates (82.89/83.69/84.48). Repeated Claude Medium runs
  were operationally clean (no continuation/error markers in records).
- **Gemini 3.6 Flash — extended thinking ON:** old 69.86 → 84.19
  (+14.33). Repeated: 67.02 → 82.93 (**+15.91**, SD primed 0.63,
  direct SD 2.46). The large shift **reproduced and is slightly larger**
  under repetition; primed is consistently above direct in all three
  replicates. Two-message corpus delivery deviation recorded (matches
  Task 021/024).
- **Gemini 3.6 Flash — extended thinking OFF:** old +3.20; repeated
  **+11.88** (primed SD 0.22 — the tightest primed spread observed). The
  OFF row shows a *larger* repeated shift than its single-run estimate.
- **DeepSeek V3 Expert ON:** old 80.49 → 85.63 (+5.14). Repeated:
  81.33 → 85.10 (**+3.77**, primed SD 0.64). High primed performance is
  stable; the effect direction reproduces but is smaller than the old
  single estimate. ON remains above OFF in both conditions under
  repetition (primed 85.10 vs 84.81; direct 81.33 vs 78.35).
- **Qwen 3.8 Max Fast:** old 82.35 → 85.38 (+3.04). Repeated:
  80.09 → 81.82 (**+1.72**) — the smallest repeated Δ — and the primed
  condition was the noisiest of the whole dataset (SD 5.83; one replicate
  at 75.09). A high-baseline configuration stays high but shows little
  and *variable* priming room under repetition.
- **Qwen 3.8 Max — Thinking & Gemini 3.1 Pro:** primed condition not
  collected — no repeated estimate possible; nothing can be concluded
  beyond the direct means (78.76 and 79.59).

## 10. Baseline dependence

Repeated direct mean vs repeated Δ mean (canonical): Spearman ρ ≈
**−0.84 (n = 16)** — descriptively similar to the Task-024 single-run
ρ ≈ −0.86 (Figure E). Consistent with the previous observation that
lower-baseline configurations show larger measured priming shifts; still
a descriptive, not causal, association.

## 11. Interpretation (what the data support)

- **Directly supported (observed):** run-to-run variation in measured
  coverage exists for every model (0.2–7.2 pp SD); the primed condition
  measured above the direct condition in **16/16** configurations with
  both conditions usable (all 18 direct conditions + all 16 computable
  Δ's positive); Task-024's single-run direction was **replicated** in
  **15/15** comparisons; the largest Task-024 shift (Gemini 3.6 Flash ON,
  +14.33) reproduced at +15.91.
- **Suggestive:** for most configurations the repeated priming shift is
  larger than the within-condition spread; baseline dependence persists
  under repetition (ρ ≈ −0.84); primed-condition replicates are generally
  *less* variable than direct replicates (median SD 0.87 vs 1.49 pp).
- **Not established:** causality; that corpus priming improves
  Interslavic generally; that any model is "best"; that coverage equals
  naturalness; that reasoning ON is superior (Gemini OFF actually showed
  the tighter primed spread); anything about the two configurations whose
  primed condition was not collected; any population-level behaviour from
  n = 3.
- Claude Sonnet 5 — max repeated results were generated with
  thinking/reasoning **OFF** — they are not directly comparable with its
  Task-024 single-run behaviour and were not merged silently.

## 12. Candidate-selection reading (no winner score)

Separate dimensions (full table in `analysis/analysis.md` §4 and Figure
A–C):

- **Performance (mean canonical/primed):** highest primed means under
  repetition: Gemini 3.6 Flash OFF 85.14, DeepSeek Expert ON 85.10,
  GPT Interslavic Teacher 83.86, Grok 83.83, Claude Sonnet 5 Medium
  83.69, Claude Sonnet 5 max 83.28.
- **Stability:** tightest primed spreads (SD ≤ 0.8 pp): Gemini Flash OFF
  (0.22), DeepSeek Instant ON (0.19), Claude Sonnet 5 max (0.49), Gemini
  Flash ON (0.63), DeepSeek Expert ON (0.64), Kimi (0.69), Claude Medium
  (0.80). Widest: Qwen 3.8 Max Fast primed (5.83), Qwen 3.7 Plus Fast
  (3.63).
- **Priming response (repeated Δ canonical):** Gemini Flash ON +15.91,
  Gemini Flash OFF +11.88, Claude Sonnet 5 max +9.91 (thinking OFF),
  Claude Medium +9.12, GPT Teacher +8.35, Qwen 3.7 Plus Fast +6.98.
- **Cleanliness (orthography outside-inventory anomalies, mean):** see
  §6/analysis.md; e.g. Grok primed 1.3, Claude Medium primed 4.0, Claude
  Max primed 3.0 vs DeepSeek Instant OFF direct 98.0 / GPT Teacher direct
  32.
- **Practical usability:** all interface deviations documented (§4);
  Claude Max thinking-OFF and Gemini two-message delivery are the ones
  that affect cross-task comparability.

## 13. Uncomfortable findings (do not skip)

1. **6 of 120 planned runs were never collected** (Gemini 3.1 Pro and
   Qwen 3.8 Max Thinking, primed) — two configurations are unanswerable
   under repetition; no estimate was fabricated.
2. **8 runs (7 % of collected) are intake-partial** purely because of
   markdown-wrapped end markers — the strict unmodified gate excludes
   them from usable stats even though the translations look complete.
   Dola Fast loses its whole repeated direct condition this way.
3. **Claude Sonnet 5 — max repeats ran with thinking/reasoning OFF**, so
   its large repeated Δ (+9.91 pp) is not directly comparable with its
   Task-024 record (which was itself partial there).
4. **Qwen 3.8 Max Fast** — the only configuration whose repeated Δ
   (+1.72 pp) is smaller than its own primed SD (5.83 pp): priming room
   at high baselines is small and stochastic.
5. **Grok identity** is operator-reported (header edit) — the strongest
   available evidence, but not provider-verifiable from these records.
6. **Fresh-session independence is operator-asserted**, not
   machine-verifiable in msg2-style records.

## 14. Limitations

- n = 3 per condition: descriptive; SDs are noisy estimates.
- Replicates are replication blocks, not matched samples.
- 8 partial + 6 missing runs reduce n for several configurations
  (GPT Teacher direct n = 1, DeepSeek Instant ON primed n = 2, Dola Fast
  direct n = 0).
- Interface/server variation is recorded, not removed; Claude Max mode
  differs from Task 024; Gemini corpus was delivered in two messages.
- Coverage measures resource grounding, not linguistic correctness or
  naturalness.
- Repetition shows *that* the shift persists, not *why*.

## 15. Recommended next experiment

The repeated-generation evidence supports proceeding toward the planned
**Phase 2B unseen-topic transfer test** — the priming shift (a) persists
under repetition for the strongest candidates (Gemini 3.6 Flash ON/OFF,
Claude Sonnet 5 Medium, DeepSeek V3 Expert ON), (b) exceeds
within-condition variation for most configurations, and (c) is
baseline-dependent. A transfer experiment on unseen topics would test
whether the effect is corpus-specific memorisation/lexical reuse or a
generalizable register/orthography influence. Before that, consider
completing the six missing primed runs (Gemini 3.1 Pro, Qwen 3.8 Max
Thinking) so the two unanswerable configurations can be assessed.
No Phase 2B work was prepared by this task.

---
Artifacts: `outputs/plan.json` (120-run plan), `outputs/audit.json` +
`outputs/audit.md` (Task-026 audit), `outputs/roster.json` +
`roster.md` (114 collected / 106 usable), `outputs/collection-checklist.md`,
`analysis/` (deterministic results + figures A–E), this report.
Generator scripts: `scripts/run_exp004_repeats.py`,
`scripts/audit_exp004_repeats.py`, `scripts/analyze_exp004_repeats.py`;
tests: `tests/test_exp004_repeats.py` (26),
`tests/test_audit_exp004_repeats.py` (10).
