# Proposed minimal experiment — Grammar Aggregator track

**Status:** `PROPOSED` only. **Do not launch.** Does not modify EXP-004.

## Goal

Obtain an informative first measurement of **targeted grammar packages**
relative to lexical assistance and (optionally) corpus priming, without
combinatorial explosion.

## Independent variable

**Assistance package type** at generation time (within configuration):

| Arm | Contents |
|---|---|
| **A — Direct** | No resource package (baseline) |
| **B — Dictionary** | EXP-003-B-style single canonical candidate scaffold |
| **C — Dictionary + grammar** | Mode B packages from the future aggregator |
| **D — Corpus priming** | Optional; only if reusing an already-frozen corpus + source regime |
| **E — Grammar + corpus** | Optional deferred; **not** in the minimal first cut |

### Minimal first cut (recommended)

Run **A / B / C** only on a **small configuration set**.

Rationale:

- A vs B re-anchors known lexical effects (should not rediscover EXP-003
  blindly on a huge roster).
- B vs C isolates the **grammar add-on**.
- A vs C estimates combined lexical+grammar vs none.
- Priming (D) is scientifically interesting for H4 but doubles protocol
  complexity (multi-message Gemini, long context). Defer to a second
  experiment unless resources are already frozen and operator cost is low.

## Held constant

- Same frozen Polish source text (hash recorded).
- Same configuration identities and vendor mode switches.
- Same Direct/Primed-style fresh-session discipline where applicable.
- Same deterministic evaluator (`isv-eval`) and orthography audit.
- Same package builder version / fact pin set (when implemented).
- No fine-tuning; no hidden LLM inside the package builder.

## Source texts

Prefer **one short narrative** already used in scaffolding work (or a
short slice) so results are comparable to EXP-003 without claiming
identical replication.

Optional second source later: a short technical/expository text
(UNSEEN-like) — **not** required for the first cut.

Avoid HIGH-overlap corpus-aligned stories if the first cut includes no
priming arm (prevents confounding “grammar” with thematic overlap).

## Configurations and repeats

To avoid explosion:

- **2 configurations** that previously showed divergent D-vs-B behaviour
  (historically Claude vs ChatGPT in EXP-003) **or** one strong + one
  weak scaffolder — exact IDs chosen at freeze time from documented
  rosters.
- **n = 3** independent fresh-session repeats per cell (descriptive;
  matches Phase 2B discipline).
- Minimal cut cell count: `2 configs × 3 arms × 3 repeats = 18` runs.

Do **not** expand to 7 configs × 5 arms × 3 in the first experiment.

## Metrics

Primary (descriptive):

- Canonical coverage; paired or arm-wise Δ vs A and vs B.
- Broader resource-supported coverage (labeled evidence, not validity).
- Unresolved rate.
- Orthography outside-inventory counts (H3).

Regression bookkeeping:

- Token-aligned A→C / C→A style transitions where comparable to prior
  scaffolds (EXP-002/003 practice).

**No** significance tests required for the first descriptive pack; no
composite quality score.

## Qualitative audit

Required for all valid pairs/arms:

- Whether the model copied package lemmas wholesale vs inflected them.
- Agreement/government errors despite guidance.
- Over-application of optional variants.
- Any package-induced unnatural constructions (human note; not a score).

## What would count as informative

Any of the following is scientifically useful (including negatives):

- C ≫ B on canonical coverage for a configuration (supports H2 locally).
- C ≈ B (grammar add-on idle) — still informative.
- C < B with identifiable conflict/overprompting — informative failure.
- Orthography improves without coverage gain (or vice versa) — supports
  separating H1/H3.
- Opposite signs across the two configurations — supports H5.

Non-informative would be: changing multiple variables at once (new
source + new models + priming + grammar) so the grammar effect cannot be
attributed.

## Explicit non-goals of the first cut

- Ranking vendors.
- Claiming quality = coverage.
- Testing all pipeline orderings in `translation-method.md` §6.
- Redesigning EXP-004 Phase 2B.
