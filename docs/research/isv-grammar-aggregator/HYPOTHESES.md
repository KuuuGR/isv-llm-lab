# Hypotheses — ISV Grammar Aggregator

**Status:** hypotheses only. **None established.** No experiment for this
track has been run.

Framing: these are directional research questions for a *future* minimal
experiment (`EXPERIMENT_DESIGN.md`). They must not be cited as findings.

---

### H1 — Grammar vs none

Targeted grammar guidance (Mode A or B) **raises canonical ISV coverage**
relative to an unassisted Direct baseline on the same source and
configuration.

*Motivation:* EXP-003 showed scaffolding gains; D sometimes added more.
Unclear whether a structured aggregator would reproduce that.

### H2 — Lexical + grammar vs lexical-only

Lexical + grammar packages (Mode B) **outperform** lexical-only assistance
(EXP-003-B style) on canonical coverage and/or unresolved rate for at
least some configurations.

*Motivation:* EXP-003 D beat B for Claude but not for ChatGPT —
model-dependence is expected; H2 is not assumed universal.

### H3 — Error-type reduction

Grammar guidance **reduces** orthographic outside-inventory counts and/or
selected morphological anomaly classes relative to lexical-only or Direct,
without claiming communicative quality improvement.

*Motivation:* Layer-2 orthography audits are diagnostic; morphology
mismatches are a plausible pathway for grammar packages.

### H4 — Stability vs corpus priming

Targeted grammar packages produce **more configuration-stable** coverage
shifts than large-context authentic-corpus priming (EXP-004-style), on a
matched small configuration set.

*Motivation:* Phase 2B showed priming is common but not universal
(e.g. HIGH Gemini negatives). H4 asks whether compact grammar context is
less brittle — **untested**.

### H5 — Configuration dependence

Any benefit of grammar packages **depends on model configuration**
(vendor/mode), i.e. mean effects hide sign or magnitude heterogeneity.

*Motivation:* Consistent with EXP-003 D and EXP-004 Phase 2B
heterogeneity; treat configuration as a factor, not a nuisance.

---

## Explicitly rejected as assumptions

- Linear additivity of lexical + grammar + corpus effects.
- Majority-vote resolution of resource conflicts.
- Equivalence of coverage gains and translation quality.
- Superiority of grammar over priming before measurement.
