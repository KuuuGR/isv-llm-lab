# EXP-004 Phase 2B — HIGH-overlap test (prepared, SODA Task 029; story frozen + kit prepared Task 030; NOT executed)

**Status:** kit machinery + design `PREPARED`, HIGH-overlap source story
**FROZEN v1** and 42-run kit **GENERATED** (2026-09-09, Tasks 029/030).
**Collection NOT started** — no LLM calls were run by these tasks, no
translations exist, and none are claimed. The 42 HIGH-overlap
translations are the next manual operator step.

## Purpose

Phase 2B asks the central EXP-004 follow-up question
(`docs/research-roadmap.md` §11):

> Does authentic ISV corpus priming generalize to source material whose
> topic/theme is absent from the priming corpus?

To answer it, the project distinguishes **three source-text regimes**:

| Regime | Description | Item | Status |
|---|---|---|---|
| **HIGH-overlap** | a new Polish story strongly inspired by the corpus, deliberately sharing themes/motifs/imagery/narrative patterns | `Iskra i Wieloryb — wersja z oryginalnymi nazwami` (frozen v1, Task 030) | kit prepared (Tasks 029/030); NOT executed |
| **LOW-overlap** | a new Polish story with very little thematic/fabular overlap with the corpus | **`Podkłady`** (bank section 4; pinned Task 030; `Opowieść o sygnale` remains banked, not selected) | reserved for the NEXT stage; NOT prepared |
| **UNSEEN DOMAIN** | a Polish scientific/educational source from a domain absent from the corpus | future biomedical-physics / electromedicine educational material | scoped, NOT prepared |

This kit prepares only the HIGH-overlap condition. LOW-overlap and
UNSEEN-domain runs must not be mixed into the HIGH manifest, and neither
experiment may start in this task.

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

- `input/` — frozen HIGH-overlap story versions + provenance
  (gitignored; `README.md` committed with the v1 hash/bytes/lines
  record). Story frozen as v1 (Task 030).
- `operator-prompts/` — 63 prompt files (21 direct; 42 primed msg1+msg2)
  + `manifest.json` (hash-only committed record). Generated by
  `prepare`; gitignored except `manifest.json`.
- `outputs/` — `plan.json` (42 rows, dated 2026-09-09) +
  `collection-checklist.md` (gitignored; `README.md` committed).
- `scripts/run_exp004_phase2b.py` — deterministic orchestrator (extends
  the repeats machinery `scripts/run_exp004_repeats.py`, which it
  imports; never calls an LLM).
- `scripts/extract_phase2b_high_story.py` — deterministic extraction of
  the HIGH-overlap story from the author's story bank (Task 030).

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

After collection (future task): register raw replies msg2-style in the
prompt files, verify + evaluate with the EXP-004 machinery, then analyse
primed-minus-direct deltas (Δ_HIGH) against the repeated-generation
results (`../repeats/`).

## Related documents

- `docs/research-roadmap.md` §10–12 — shortlist, Phase-2B questions,
  corpus self-evaluation record.
- `docs/translation-method.md` — intervention ladder, pipelines,
  evaluation layers.
- `../DESIGN.md` §15 — Phase-2B source-text regimes design record.
- `../phase2a/corpus-selfeval/` — corpus self-evaluation (Task 029).
- `../repeats/` — Task-025/026 controlled repeated generation (the
  direct/primed baselines Δ_HIGH will be compared against).
