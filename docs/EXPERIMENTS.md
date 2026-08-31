# Experiment Log

Status of all experiments. Newest last. The canonical design of each experiment
lives in `experiments/<exp>/DESIGN.md`.

---

## EXP-001 — Baseline: unconstrained LLM translation Polish → Interslavic

| Field | Value |
|---|---|
| Status | **Harness implemented (experiment not run)** — Task 002 built the `isv-eval` evaluator; the story input has not been requested from the Project Owner. |
| Design | `experiments/exp001-baseline/DESIGN.md` |
| Input | One complete Polish short story (whole text as a single translation task) |
| Models | ChatGPT, Gemini, Claude, DeepSeek — each receives the entire story independently |
| Evaluation | Exact dictionary coverage, morphological validity (lemma-backed), unresolved forms, total tokens; per-model unresolved-form lists with sentence context |
| Harness | `isv-eval` CLI (tokenizer, lexicon lookup, morphology-backed validation, A/B/C + review metadata, metrics, JSON reports); lexicon = `basic.json` snapshot + `@interslavic/morphology@0.1.2` full-form lexicon (320,824 entries) |
| Reproducibility | Raw outputs stored per run under `experiments/exp001-baseline/outputs/<run_id>/`; run metadata (date, provider, model, model_version, prompt, source, output) never overwritten; every report embeds dictionary manifest + morphology version + code commit |
| Follow-up | The future constrained-generation experiment compares against this baseline (see DESIGN.md § Future experiment) |

## Planned (not started)

- **EXP-002 — Constrained generation (documented in DESIGN.md, not implemented).**
