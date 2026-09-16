# EXP-004 Phase 2B — HIGH / LOW source-regime tests

**Status (2026-09-16):**

| Regime | Status |
|---|---|
| **HIGH-overlap** | executed + analysed (42/42; descriptive Δ_HIGH; 2026-09-15) |
| **LOW-overlap** | executed + analysed (42/42; descriptive Δ_LOW; 2026-09-16) |
| **UNSEEN DOMAIN** | planned / scoped; **not frozen / not executed** |

Intake and analysis used existing replies and deterministic scripts only —
**no LLM calls** during intake/analysis. Frozen stories and the authentic
corpus were not modified by analysis.

### HIGH artifacts
[`EVIDENCE.md`](EVIDENCE.md) · [`analysis/`](analysis/) ·
[`QUALITATIVE_AUDIT.md`](QUALITATIVE_AUDIT.md) +
[`qualitative_audit.json`](qualitative_audit.json)

### LOW artifacts
[`analysis/low/EVIDENCE.md`](analysis/low/EVIDENCE.md) ·
[`analysis/low/`](analysis/low/) ·
[`analysis/low/QUALITATIVE_AUDIT.md`](analysis/low/QUALITATIVE_AUDIT.md) +
[`analysis/low/qualitative_audit.json`](analysis/low/qualitative_audit.json)

LOW preparation validation (boundary + freeze):
[`LOW_VALIDATION.md`](LOW_VALIDATION.md).

## Purpose

Phase 2B asks the central EXP-004 follow-up question
(`docs/research-roadmap.md` §11):

> Does authentic ISV corpus priming generalize to source material whose
> topic/theme is absent from the priming corpus?

To answer it, the project distinguishes **three source-text regimes**:

| Regime | Description | Item | Status |
|---|---|---|---|
| **HIGH-overlap** | a new Polish story strongly inspired by the corpus, deliberately sharing themes/motifs/imagery/narrative patterns | `Iskra i Wieloryb — wersja z oryginalnymi nazwami` (frozen v1, Task 030) | **executed + analysed** (42/42; descriptive Δ_HIGH) |
| **LOW-overlap** | a new Polish story with very little thematic/fabular overlap with the corpus | **`Podkłady`** (bank section 4; clean prose frozen v1; casting/API preamble excluded) | **executed + analysed** (42/42; descriptive Δ_LOW) |
| **UNSEEN DOMAIN** | a Polish scientific/educational source from a domain absent from the corpus | future biomedical-physics / electromedicine educational material | scoped, NOT prepared |

HIGH and LOW are complete as descriptive paired datasets. UNSEEN-domain
runs must not be mixed into either manifest, and UNSEEN remains unexecuted.

## HIGH-overlap story identity and classification

- Story: **"Iskra i Wieloryb — wersja z oryginalnymi nazwami"** (author-
  owned Polish story; keep local).
- Classification: **`high_overlap_corpus_inspired`** — deliberately
  NOT `independent_same_topic`, and NOT an independent control.
- Source/provenance (Task 030): author's story bank `InterslavicTesty.md`
  (outside the repo, sha256 `3662cda9…`), section `# 3.`, extracted
  deterministically by `scripts/extract_phase2b_high_story.py`
  (Markdown structural markers removed only; all 227 story content
  lines preserved exactly, verified) and frozen as **v1** — SHA-256
  `ab8a0dcf7352789c09c4aca132c086999c861407e4cd682ee9414aab5b792f63`,
  30 061 B / 440 lines. Bank sections 1 and 2 are retained but not used;
  section 4 (`Podkłady`) is the reserved LOW-overlap source.
- The story deliberately shares substantial corpus material: eternal
  winter; the Red/Scarlet Spark; Zimorodzice; an inherited key; a
  grandfather's legacy; Mogiła Szronu; songs used as narrative
  mechanisms; whale imagery; the Heart of the Earth; sacrifice and
  transformation; maritime and storm imagery.
- Overlap is the *point* of this test (hypothesis H-HIGH below), not an
  error. The story is NOT an additional corpus component, is never added
  to the corpus, and the corpus is never modified to fit it.

## Planned sample (Phase 2B-A HIGH-overlap)

7 representative configurations (behavioural sample from
`docs/research-roadmap.md` §10; not a winners list) × 2 conditions
(direct, primed) × 3 replicates (r01–r03, fresh independent sessions)
= **42 planned translations** (21 direct + 21 primed), giving 21
direct/primed paired comparisons.

| # | Configuration | Representative role |
|---|---|---|
| 1 | Gemini 3.6 Flash — extended thinking ON | strong priming effect |
| 2 | Gemini 3.6 Flash — extended thinking OFF | strong priming effect |
| 3 | Claude Sonnet 5 Medium | stable high-performance configuration |
| 4 | DeepSeek V3 Expert — DeepThink ON | clean output, high baseline |
| 5 | Qwen 3.8 Max Fast | small-effect/high-variance counterexample |
| 6 | GPT-5.6 Luna — thinking OFF (pinned Task 029) | neutral general-purpose reference |
| 7 | Grok 4.5 Fast (operator-reported identity) | independent model-family reference |

GPT-5.6 Luna is pinned to the thinking-OFF ("Luna" default) variant;
the ON variant remains available only if a later research question needs
it. Grok's identity ("Grok 4.5, built by xAI (fast)") is
operator-reported, not independently verified.

## Protocols

- **Direct condition:** fresh session; the HIGH-overlap Polish story +
  the identical direct-translation instruction used since Phase 1. No
  ISV corpus, no dictionary injection, no lexical candidates, no
  morphology scaffolding, no human guidance.
- **Primed condition:** fresh session; message 1 = the complete
  authoritative three-register corpus `phase2a-authentic-isv` v1
  (SHA-256 `aaad28e43935a40313585d77a33bfc788d97e8d69b081f9486af74d52ca1a857`)
  with the same study-as-reference instruction as Phase 2A; message 2 =
  the HIGH-overlap story + translation instruction. No dictionary
  candidates, no morphology annotations, no "use these words"
  instructions — the design isolates corpus conditioning.
- **Gemini handling (recorded rule):** the corpus is never shortened for
  Gemini (or any model). If Gemini's interface requires splitting
  message 1, the split is recorded as an interface deviation, not as a
  corpus edit.
- **Replicates:** each replicate is a fresh independent model session;
  never chain messages, never reuse a session, never tell the model this
  is a repeat. The three replicate prompt files of a (configuration,
  condition) are byte-identical by design.
- **No human evaluation:** this experiment is automated/resource-based.

## Hypothesis (recorded, NOT a result)

**H-HIGH** — corpus priming may produce a larger improvement in
resource-supported Interslavic generation when the target text is
strongly thematically/motivically aligned with the priming corpus.

Potential alternative explanation: the model may simply benefit from
stronger lexical/topic overlap or may reproduce corpus-specific
structures. The eventual interpretation compares `Δ_HIGH` (this kit)
with `Δ_LOW` and `Δ_UNSEEN`; no such relationship is claimed until those
tests are actually run.

## Corpus self-evaluation reference point

Task 029 also measured the authentic corpus itself under the same
evaluation stack (reference ceiling for reading model coverage):
`../phase2a/corpus-selfeval/README.md`. Combined corpus: 8 096 lexical
tokens, canonical 80.50 %, broader 89.17 %, unresolved 19.50 %,
orthography-out 47; registers differ substantially (see that README).

## Kit layout (committed vs local)

- `EVIDENCE.md` — article-ready evidence record (fact / interpretation /
  hypothesis layers; points at machine-readable analysis).
- `QUALITATIVE_AUDIT.md` + `qualitative_audit.json` — descriptive paired
  Direct→Primed qualitative audit of all 21 pairs (derived; does not
  modify raw outputs).
- `input/` — frozen HIGH-overlap story versions + provenance
  (gitignored; `README.md` committed with the v1 hash/bytes/lines
  record). Story frozen as v1 (Task 030).
- `operator-prompts/` — 63 prompt files (21 direct; 42 primed msg1+msg2)
  + `manifest.json` (hash-only committed record). Generated by
  `prepare`; gitignored except `manifest.json`. Collected replies live
  msg2-style after `## Output` (local).
- `outputs/` — `plan.json` (42 rows, dated 2026-09-09) +
  `collection-checklist.md` + per-run dirs (gitignored; `README.md`
  committed). All 42 runs collected / verified / evaluated.
- `analysis/` — aggregate analysis (`dataset.json`, `analysis.json`,
  `analysis.md`; gitignored except `README.md`). Regenerated by
  `scripts/analyze_exp004_phase2b.py`.
- `scripts/run_exp004_phase2b.py` — deterministic orchestrator (extends
  the repeats machinery; collect/verify/evaluate/status; never calls an
  LLM during analysis).
- `scripts/extract_phase2b_high_story.py` — deterministic extraction of
  the HIGH-overlap story from the author's story bank (Task 030).
- `scripts/analyze_exp004_phase2b.py` — deterministic paired aggregate
  analysis (integrity gate + descriptive stats; no LLM).

## Commands (already executed for v1 on 2026-09-09)

```bash
# 1) Extract the HIGH story from the author's bank (deterministic,
#    read-only on the bank):
python scripts/extract_phase2b_high_story.py --bank InterslavicTesty.md \
    --out phase2b/input/_extracted/high-overlap-story.txt

# 2) Freeze it (read-only source; frozen copies immutable):
python scripts/run_exp004_phase2b.py freeze-story \
    --src phase2b/input/_extracted/high-overlap-story.txt \
    --version-label v1 --note "..."

# 3) Prepare the 42-run kit (deterministic, hash-gated; executed with
#    --date 2026-09-09):
python scripts/run_exp004_phase2b.py prepare --date YYYY-MM-DD
#    --force only BEFORE any collection. Regenerating with the same
#    --date is byte-identical (verified).
```

## Aggregate results pointer (descriptive, n=3)

Canonical mean Δ (full tables + individual D/P/Δ + run IDs in
`analysis/analysis.md` and `EVIDENCE.md`):

| Configuration | Direct mean | Primed mean | Mean Δ |
|---|---:|---:|---:|
| Gemini 3.6 Flash — ext. thinking ON | 68.68% | 68.13% | −0.55 pp |
| Gemini 3.6 Flash — ext. thinking OFF | 67.20% | 65.45% | −1.75 pp |
| Claude Sonnet 5 Medium | 69.29% | 83.57% | +14.28 pp |
| DeepSeek V3 Expert ON | 74.53% | 83.78% | +9.25 pp |
| Qwen 3.8 Max Fast | 76.36% | 81.54% | +5.18 pp |
| GPT-5.6 Luna | 73.54% | 82.16% | +8.62 pp |
| Grok 4.5 Fast | 68.35% | 82.84% | +14.49 pp |

**Interpretation constraints:** n=3; descriptive only; no significance
tests; no causal priming claim; Gemini ON/OFF and Qwen have mixed-sign
replicate Δs; orthography is a separate diagnostic; unresolved is
structurally related to canonical coverage. H-HIGH remains a hypothesis
until LOW/UNSEEN exist.

## Related documents

- `EVIDENCE.md` — article-ready fact / interpretation / hypothesis record.
- `QUALITATIVE_AUDIT.md` — qualitative Direct→Primed audit (all 21 pairs).
- `analysis/README.md` — computational aggregate artifacts.
- `docs/research-roadmap.md` §10–12 — shortlist, Phase-2B questions,
  corpus self-evaluation record.
- `docs/translation-method.md` — intervention ladder, pipelines,
  evaluation layers.
- `../DESIGN.md` §15 — Phase-2B source-text regimes design record.
- `../phase2a/corpus-selfeval/` — corpus self-evaluation (Task 029).
- `../repeats/` — Task-025/026 controlled repeated generation.
