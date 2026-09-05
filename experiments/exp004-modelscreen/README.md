# EXP-004 — practical LLM model screening (Polish → Medžuslovjansky)

**Status: DESIGN ONLY — not approved, not executed.** Prepared as SODA Task
013 (2026-09-05). No LLM has been called and no translation run exists.

Purpose: screen which LLMs are practically usable by the project (web/chat
interface, free access sufficient for ~1 story/day, identifiable
model/version/settings) and record their versioned no-guidance baseline
quality on the canonical story, before investing in guidance-method
experiments.

Design: `DESIGN.md` (Task 013). It specifies a two-phase structure —
Phase A model screening (this experiment) and Phase B guidance-method
experiments (later, separate) — the practical access filter, the candidate
roster, the protocol (identical source, equivalent instruction, full
recording, Task 008 two-tier evaluator unmodified), and the open items that
must be confirmed by the Project Coordinator before any execution.

This experiment does **not** depend on, modify, or claim results from the
open EXP-003 blinded human review. No files in `input/`, `operator-prompts/`,
`outputs/`, or `comparison/` exist yet; they will be created only after the
design is approved and access is confirmed (raw story and outputs stay local
and gitignored per the repository copyright policy).
