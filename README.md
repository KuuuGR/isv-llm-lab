# isv-llm-lab

**Interslavic LLM Lab**

> Research lab for improving LLM-generated Interslavic using existing lexical and morphological resources.

Can we make LLMs generate better Interslavic by giving them **less freedom, not more**?

This is an experimental, open-source, non-profit **community research project**.
It is **not an official Interslavic project** and does not present itself as such.
The initial purpose is experimentation and benchmarking, not a production
translation application.

## Status

See [`docs/STATE.md`](docs/STATE.md) for the current project state. As of
2026-09-05 (SODA Task 016): **EXP-003 is COMPLETED and CLOSED** — the
participant answered the 100-question blinded sentence-level forced-choice
test, the answers were decoded against the private key
(`scripts/analyze_exp003_sentence_review.py`; provenance artifacts Q58/Q67
recorded, no document modified) and combined with the automatic evidence.
Final report: [`experiments/exp003-scaffold/REPORT.md`](
experiments/exp003-scaffold/REPORT.md). Headline human result: scaffolded
guidance (B/C/D) preferred over the unguided baseline (A) **74 % vs. 26 %**,
identically for ChatGPT and Claude; condition D (grammatical annotations) was
the favorite for both models (36 % / 42 %). Human preference and resource
coverage agree for Claude at the extremes but diverge for ChatGPT (the
coverage-best ChatGPT-B is the human least preferred) — the signals are
reported separately, and no composite quality score is used. The
character-level orthographic audit (Task 015) remains an independent,
audit-only quality dimension over all EXP-001/002/003 outputs, now with a
deterministic non-name refinement used in the EXP-003 analysis. EXP-003 is
closed to new runs, and no further human-evaluation exercise will be designed
(`docs/DECISIONS.md` D-042/D-043, `docs/LESSONS.md` L-032/L-033). The
EXP-004 practical model-screening experiment (Phase 1, clean direct-
translation baseline) has its **roster and screening protocol finalized**
but is **not approved and not executed** (`experiments/exp004-modelscreen/
DESIGN.md`).
The evaluator reports **canonical coverage** and **broader
resource-supported coverage** side by side, with per-token evidence
provenance, while the historical A/B/C classifications and all EXP-001/EXP-002
results remain unchanged. Experiments: `docs/EXPERIMENTS.md`. Raw inputs and
outputs stay out of git (copyrighted); per-run hashes make everything
reproducible.

## Documentation

| File | Contents |
|---|---|
| [`SOURCES.md`](SOURCES.md) | Source & dependency inventory (licenses, commits, preservation plan) |
| [`docs/STATE.md`](docs/STATE.md) | Project state |
| [`docs/ROADMAP.md`](docs/ROADMAP.md) | Roadmap + future ideas |
| [`docs/DECISIONS.md`](docs/DECISIONS.md) | Decision log |
| [`docs/EXPERIMENTS.md`](docs/EXPERIMENTS.md) | Experiment log |
| [`docs/GRAMMAR_AUDIT.md`](docs/GRAMMAR_AUDIT.md) | Grammar consistency audit (Steen docs vs JS vs Rust) |
| [`docs/LESSONS.md`](docs/LESSONS.md) | Lessons learned (SODA) |
| [`experiments/exp001-baseline/DESIGN.md`](experiments/exp001-baseline/DESIGN.md) | Experiment 001 design (baseline evaluation) |

## The evaluator (`isv-eval`)

Takes any Interslavic text and measures how much of its vocabulary is
justifiable by the available lexical and morphological resources, under a
two-layer resource policy (`docs/RESOURCE_POLICY.md`):

- **A** — exact lexical match (headword or inflected form in the full-form
  lexicon generated from the dictionary snapshot + `@interslavic/morphology`);
- **B** — morphologically valid (rescued by re-inflecting candidate lemmas);
- **C** — unresolved (preserved with sentence context for manual review);
- **canonical coverage** — `(A + B) / lexical_tokens` (the historical
  `morphologically_valid_coverage`, renamed/documented);
- **broader resource-supported coverage** — canonical-supported tokens plus
  tokens with an **exact surface attestation** in the audited alternative
  resources (`isv.dic`, `interslavicfreq` wordlists), divided by
  `lexical_tokens`. An *evidence estimate*, never a validity claim.
- per-token evidence (layer + source + kind) explains **why** every token was
  or was not counted.

```bash
python3 -m venv .venv && .venv/bin/pip install -e ".[dev]"
npm ci                              # in src/morphology_backend/
python3 scripts/fetch_dictionary.py # snapshots basic.json + manifest (network)
python3 scripts/generate_lexicon.py # builds the full-form lexicon (~90 s)
.venv/bin/isv-eval text.txt --out results/
```

The broader tier is enabled automatically when the audited alternative
resources are present under `data/dictionary/audit/` (gitignored local
artifacts); pass `--no-alternative-resources` to skip them.

See `docs/STATE.md` and `experiments/exp001-baseline/DESIGN.md` for details.
The dictionary snapshot and lexicon are gitignored (license unresolved).

## Research question

> Modern LLMs can generate plausible-looking Interslavic while introducing
> vocabulary or forms that are actually borrowed from individual Slavic
> languages or are otherwise not supported by the established Interslavic
> resources.

Proposed direction: constrain generation using existing Interslavic lexical and
morphological resources. This is a hypothesis — the first experiment establishes
the unconstrained baseline before any constrained system is judged.

## Stack principles

- Python for orchestration/analysis (default), Node for the existing
  `@interslavic/morphology` engine.
- Reuse existing Interslavic resources; do not reimplement morphology.
- Keep the project small and reproducible.
