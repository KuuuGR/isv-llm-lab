# Experiment 004 — Design: Practical LLM Model Screening for Polish → Medžuslovjansky Translation

Status: **DESIGN ONLY (SODA Task 013, 2026-09-05).** This document specifies
EXP-004 as a *prepared, not approved, not executed* experiment. No LLM was
called, no translation run exists, and no execution may start until (a) this
design is explicitly approved and (b) the access/availability items in §11
are confirmed by the Project Coordinator. The EXP-003 blinded human review
(§3.3) is still open and is **not** part of this experiment.

---

## 1. Executive summary

EXP-001 measured unconstrained direct translation by 7 model conditions
(historical baseline, versions unknown). EXP-002 tested *correcting an
existing translation* with supplied alternatives (post-hoc revision).
EXP-003 tested *generation-time dictionary scaffolding* (conditions B/C/D vs
A) on ChatGPT and Claude; its blinded holistic human review is prepared and
awaiting the Project Owner (Task 012) — **no human judgment exists yet**.

EXP-004 is the next major research phase: **model screening**, followed (in a
separate later phase) by **guidance-method experiments**. It answers a
practical question first: *which LLMs can the project actually use, at a
normal-user level, for roughly one Polish → Medžuslovjansky story translation
per day — and what is their baseline quality when nothing is added to the
prompt?* Only models that pass this practical screening become candidates for
the later, more expensive question: *which forms of external deterministic
linguistic guidance improve which models.*

Central hypothesis (unchanged from the project's research question, and still
a hypothesis, not a result): LLMs can generate plausible-looking Slavic text
from learned patterns without reliably consulting or reproducing the actual
vocabulary and morphology of Medžuslovjansky; supplying deterministic
linguistic resources at the right point may therefore improve translation
quality. EXP-004 is designed to discover, empirically, which models are worth
that investment and which assistance strategies are worth testing on them.
**No method and no model is assumed to win.** The experiment must remain able
to produce results that surprise us (§8).

## 2. Why a screening phase before guidance-method experiments

The coordinator's working assumption, adopted as a design premise: a normal
user of the project has many Polish stories and wants to translate roughly one
story per day (or every other day) through ordinary web/chat interfaces, with
free access. Guidance-method experiments multiply cost (several guidance
conditions × several models × whole-story generations, plus curation work for
deterministic guidance). Spending that effort on models that a normal user
cannot practically drive is waste. Therefore:

1. **Phase A — practical model screening (this experiment).** One condition
   per model row: direct translation of one identical Polish story with an
   equivalent basic instruction, executed through the model's ordinary
   web/chat interface, with full recording (§6). Outputs: (i) a per-model
   **access verdict** (usable in practice at ~1 story/day? context/truncation
   behavior under free access?), and (ii) **versioned baseline numbers**
   (canonical and broader resource-supported coverage) under the full
   recording discipline, directly comparable across the roster because the
   source and instruction are the same.
2. **Phase B — guidance-method experiments (later, separate design).** The
   assistance strategies enumerated in §7 are compared empirically on the
   models that pass Phase A. Phase B is *designed for* here (the machinery is
   chosen so Phase B can be layered on) but is not specified as an execution
   plan in this document.

Phase A does **not** need the EXP-003 human judgment. Phase B scoping may be
informed by it (and by the EXP-003 report), which is one reason EXP-004
execution should not race ahead of the open human-review stage (§3.3).

## 3. Relationship to prior work (what is reused, what is new)

### 3.1 Reused, unchanged

- The **canonical story-only Polish source** registered by EXP-003
  (`experiments/exp003-scaffold/input/source.txt`, SHA-256
  `5de968a6…57280723`; story-only per the Task 003.1 rule). EXP-004 registers
  its own byte-identical copy under its own input dir (both gitignored).
  Identical source for every model row is a hard requirement (§6.1).
- The **Task 008 two-tier evaluator** (`isv-eval`), used unmodified:
  canonical coverage and broader resource-supported coverage side by side,
  never merged (D-027); A/B/C classification preserved; per-token evidence
  provenance.
- The **collection/orchestration discipline** from EXP-002/EXP-003:
  byte-for-byte immutable collection, SHA-256 in run metadata, documented
  statuses (`collected_external_output` / `collected_partial_output` /
  `failed_external_output`, D-035), completeness gate before evaluation
  (L-027), external execution convention with no LLM API client (D-007),
  metadata recorded as `unknown` when not supplied (D-018/D-023).
- **Historical numbers** (EXP-001, EXP-002, EXP-003 §4.9 of
  `docs/RESEARCH_NOTES.md`) stay untouched and are used only as context in
  the eventual Phase A report — never as a scoring input.

### 3.2 New in Phase A

- The **access filter** (§5) applied as an explicit, pre-registered criterion,
  and a per-model **access verdict** recorded as experimental output.
- **Versioned, settings-recorded direct-translation runs** for the roster
  (EXP-001's runs have `unknown` versions/settings; EXP-004 is the first
  versioned direct-translation layer on the same story).
- Within-provider **variant rows** are explicit screening conditions
  (e.g. GPT-5.6 Luna thinking OFF vs ON; DeepSeek-V4-Pro DeepThink OFF vs ON),
  so a documented generation setting is a row of the roster, not an
  afterthought.

### 3.3 The open EXP-003 human review is untouched

The blinded holistic review of the 8 complete EXP-003 runs is prepared and
the project is **waiting for the Project Owner's answers**; no answers exist.
EXP-004 does not depend on those answers, does not modify the review protocol,
does not reuse EXP-003's output texts as input, and must not claim any
human-review result. The current human-evaluation stage remains open while
this design is prepared.

## 4. Two phases and their separation (recorded for the future record)

The distinction between **model screening** and **guidance-method
experiments** is a methodological decision (D-037):

- *Model screening* asks: which models are practically usable and what is
  their no-guidance baseline? One source, one equivalent instruction, one
  direct-translation condition per row.
- *Guidance-method experiments* ask: given a usable model, which form of
  external deterministic linguistic guidance changes quality, by how much,
  and at what cost? Multiple conditions per model; deterministic guidance
  generators; before/after or between-condition comparison with the same
  evaluator.

Phase B is deliberately **not** folded into Phase A: mixing "which model" and
"which method" in one matrix is expensive and confounds the access question
with the method question. Phase A results (including headroom: each model's
unresolved rate on direct translation) are the evidence base for deciding
which methods deserve a Phase B on which models — a decision to be made from
data, not from prior assumptions.

## 5. Model-selection principle (practical access filter)

### 5.1 The filter (D-036)

A model is generally considered for the main Phase A roster if **all** hold:

1. A normal user can use it through a **web/chat interface** without
   installing and running the model locally;
2. its **free access is practically sufficient** to perform at least
   approximately **one full story translation per day** (the story is
   ~10.8 KB of Polish; the complete-task prompt fits ordinary chat
   interfaces, and the run should be completable within the free tier's
   ordinary daily allowance — not one-off trial credits);
3. the provider/version/settings are **identifiable and recordable**.

Not in scope of the main screening:

- local model deployment and hardware requirements (free weights do not
  qualify a model if it must be run locally);
- models that require a paid subscription for ordinary use;
- temporary trial credits that are exhausted after one story;
- quotas that make normal daily translation impractical.

The filter exists because the target workflow is real-world use by the
project coordinator, not benchmark convenience. It is recorded as a decision
(D-036) so future model choices are judged against a stated criterion rather
than rationalized post hoc.

### 5.2 Roster under the filter (to be confirmed, §11)

Repo-known facts are cited; everything else is an assumption to confirm.
Rows are *candidate* rows; the final roster is set when access is confirmed
and the plan is approved.

| # | Roster row | Provider / interface | Repo evidence | Access/version to confirm |
|---|---|---|---|---|
| 1 | GPT-5.6 Luna, thinking OFF | OpenAI ChatGPT | EXP-003 ChatGPT condition; complete in all 4 runs (Task 011) | none beyond daily free allowance |
| 2 | GPT-5.6 Luna, thinking ON | OpenAI ChatGPT | not used in EXP-003 (thinking OFF was the setting) | availability of thinking ON in free web UI; version id |
| 3 | Custom GPT "Interslavic / Medžuslovjansky Language Teacher" | OpenAI ChatGPT (custom GPT) | EXP-001 condition `gpt-isvt`: highest EXP-001 coverage (79.83 %); internal system prompt unknown (D-018 — a recorded confound) | still available to coordinator; kept as a separate row from ChatGPT |
| 4 | Claude Sonnet 5 | Anthropic Claude | EXP-003 condition; complete in all 4 runs; recorded as "Sonnet 5 Medium" | free-tier daily sufficiency for one story |
| 5 | Gemini | Google Gemini | EXP-001 baseline (version unknown) | current free model id/version |
| 6 | DeepSeek-V4-Pro, DeepThink OFF | DeepSeek chat | DeepSeek EXP-001 baseline (older version, unknown); V4-Pro noted outside EXP-003 (RESEARCH_NOTES §4.9) | DeepThink OFF availability; free daily sufficiency |
| 7 | DeepSeek-V4-Pro, DeepThink ON | DeepSeek chat | V4-Pro DeepThink ON referenced in RESEARCH_NOTES §4.9 (not used in EXP-003) | free daily sufficiency (DeepThink is heavier) |
| 8 | Grok | xAI (Grok chat) | EXP-001 baseline (version unknown) | current version; free access |
| 9 | Kimi | Moonshot Kimi | no repo evidence | version; free access; interface |
| 10 | Qwen | Alibaba Qwen Chat | no repo evidence | version; free access; interface |
| 11 | GLM | Zhipu GLM | no repo evidence | **conditional**: only if current web access satisfies §5.1 |
| 12 | (custom GPT variant of row 3 is NOT a separate model) | — | — | — |

### 5.3 Explicit exclusions and statuses

- **Bielik** — not in the main roster. Observed evidence (EXP-003, preserved):
  all four runs failed/truncated under its free web access (2 truncated at
  ~40 % of the story, 1 prompt echo, 1 service error page). Under §5.1 this
  access does not satisfy the practical-sufficiency criterion for this task.
  Bielik remains an important **qualitative negative result**; its evidence
  and documentation are preserved unchanged, and **no new quantitative
  conclusion about Bielik is invented here**.
- **Mistral** — not assumed available: the project coordinator currently does
  not have access. It can be added if access changes.
- **Venice AI** — not treated as an independent model: it is a
  platform/interface, not a single underlying model. Any Venice-based run
  would require identifying the underlying model, which defeats the screening
  purpose; it is excluded from the model comparison.
- **Local-only models** (free weights requiring local installation) — outside
  the main practical screening by §5.1.
- The **EXP-003 second-cohort idea** (RESEARCH_NOTES §4.9(H)) is superseded
  for practical purposes by this roster: the screening tests more models and
  records versions/settings; EXP-004 does not start from EXP-003's Bielik
  dataset.

## 6. Phase A protocol (screening runs)

### 6.1 Source identity

One Polish story — the same byte-identical story-only source as EXP-003
(SHA-256 above). Identical for every model row; registered under
`experiments/exp004-modelscreen/input/source.txt` (gitignored) with a
`source.meta.json` recording the hash and its derivation (Task 003.1 rule:
story only; translation instructions belong in the prompt).

### 6.2 Instruction equivalence

A single **base translation instruction** (draft in §6.9) is used for every
roster row: translate the complete Polish story into Interslavic
(Medžuslovjansky); keep title, headings, paragraphs, names, and dialogue in
order; produce natural idiomatic Interslavic; return only the translation.
Phase A adds **no guidance** (no scaffold, no candidates, no grammar notes,
no metrics, no model comparisons, no request for explanations).

- Roster rows that are the same provider with a different setting
  (thinking toggles) receive byte-identical prompts differing only in the
  setting documented in metadata, never in linguistic content.
- The custom GPT row (row 3) additionally receives the same visible
  instruction; its built-in system prompt is unknown and is recorded as a
  confound (D-018) — the row is exploratory, kept separate from ChatGPT.
- Interface-specific packaging (copy/paste formatting) is allowed and is
  recorded; it must not change the instruction's meaning.

### 6.3 Recording (deterministic and traceable)

Per run, recorded in `meta.json` (following EXP-003's `collect` metadata
model, extended where needed):

- provider, model, model version/id, interface, generation settings
  (e.g. thinking toggle) — supplied values only; `unknown` when not supplied
  (D-018);
- generation date;
- prompt hash, source hash, instruction version;
- **context/window limitations**: declared window (from provider docs when
  available, else `unknown`) **and** observed behavior (complete reply?
  truncation? where did it stop? — L-027 completeness gate);
- status (D-035): `collected_external_output` /
  `collected_partial_output` / `failed_external_output`;
- free-access observation: was the run completable within the ordinary free
  allowance in one session? (the practical verdict input);
- output SHA-256.

Run ids follow the established scheme
`<date>__<provider>__<model>__<version>__<condition>`; Phase A condition
token is `direct` (no guidance), variant settings (e.g. `thinkon`,
`deepthink-on`) are part of the model/version token so every row is
addressable and unique. The exact id set is fixed in `plan.json` when the
roster is approved.

### 6.4 Output handling

- Raw replies are saved byte-for-byte (no cleaning, no trimming), never
  overwritten (D-023).
- Failures and truncations are **recorded as data** with status + note; they
  are never silently discarded, repaired, or rerun to make the table look
  better (D-035, L-027).
- The structural completeness gate (expected sections + end marker + head/tail
  + byte size vs complete peers) runs **before** any evaluation (L-027).

### 6.5 Evaluation

- Task 008 evaluator, **unmodified**; metric definitions are **not**
  redefined to favor any outcome (§8).
- Per run: canonical coverage and broader resource-supported coverage side by
  side (never merged), unresolved rate, lexical-token denominator,
  per-token evidence; name-excluded diagnostics as in EXP-003 where useful.
- Phase A computes **within-provider variant deltas** (e.g. thinking ON vs
  OFF) as descriptive comparisons — same model family, same source, same
  instruction.
- Phase A does **not** rank models into a winner list as a research output:
  the table of numbers plus access verdicts is the output. Ordering claims,
  if any are made in the eventual report, must be explicitly tied to the
  metric and stated as story-conditional.

### 6.6 Human involvement in Phase A

- **No manual word-by-word classification** by any human reviewer is required
  (A/B/C classification is automatic; two-tier metrics are automatic).
- The Project Owner/coordinator acts as **operator** (executes prompts,
  saves replies, reports access observations), not as annotator.
- Holistic human naturalness reading is **not** part of Phase A; it remains a
  separate, later, blinded step for Phase B candidates only (pattern of
  EXP-003 §11), to be designed when Phase B is scoped.

### 6.7 Analyses and outputs

Per-run analysis files, a roster summary table (coverage pair, unresolved
rate, completeness, access verdict per row), variant-delta notes, and a Phase
A report draft structure — reusing `compare_exp003.py`'s per-run analysis
pattern. No composite score is ever computed.

### 6.8 Success criteria of Phase A

- A confirmed roster with a recorded **access verdict** per model;
- versioned, settings-recorded direct-translation baseline numbers for every
  completed run, failures preserved;
- an evidence-based shortlist for Phase B scoping (usable models; headroom
  visible from unresolved rates);
- a written Phase A report (later SODA task) that keeps observed facts,
  hypotheses, and open questions distinct.

### 6.9 Draft base instruction (Phase A, subject to approval)

```text
Translate the Polish story below into Interslavic (Medžuslovjansky).

## Rules
- Translate the complete document: the title, the section headings, and all
  paragraphs, in their original order.
- Preserve paragraph breaks, character names, and quoted dialogue exactly as
  they appear.
- Produce natural, idiomatic Interslavic. The result must read as one
  coherent story, not as a word-for-word rendering of Polish.
- Return only the Interslavic translation — no explanations, no comments, no
  notes about your choices, and no alternative versions.

## Source text (Polish)
{STORY}

## Output
Return the complete Interslavic translation of the source text, and nothing
else.
```

(Equivalent in wording to EXP-003's prompt minus any scaffold/condition
block, so EXP-004 direct runs stay comparable in spirit to EXP-003 condition A
— but EXP-004 is a self-contained experiment; it does not depend on EXP-003's
condition A outputs.)

## 7. Extensibility: the guidance-method space Phase B will explore

Phase B will compare assistance strategies empirically; **none is assumed to
win**. The strategies under consideration (list from the coordinator, mapped
onto the project's machinery/taxonomy; RESEARCH_NOTES §1):

| Strategy (candidate Phase B condition) | Kind | Existing machinery it maps to |
|---|---|---|
| Direct translation, no guidance | control | Phase A rows (also EXP-001 pattern) |
| Lexical candidate hints (unspecified) | lexical, generation-time | EXP-003 scaffold format (deterministic, D-029) |
| One canonical dictionary candidate per form | lexical, generation-time | EXP-003 condition B |
| Multiple alternatives `[a/b/c/d]` | lexical, generation-time | EXP-003 condition C |
| Lemma + POS information | lexical/grammatical | EXP-003 scaffold provenance fields (POS) |
| Lemma + grammatical features | grammatical | EXP-003 condition D (dictionary POS, verb aspect, example forms) |
| Candidate inflected forms | lexical/grammatical | EXP-003 generated example forms; full-form lexicon |
| Lexical + grammatical scaffolding | combined | EXP-003 conditions C+D (deterministic, curated) |
| Pre-translation linguistic analysis | analysis step before generation | new (must be deterministic or an explicitly recorded LLM variable — D-029 rule) |
| Post-generation dictionary/morphology validation | validation after generation | evaluator output fed back (deterministic) |
| LLM repair after deterministic evaluation | multi-call | EXP-002 revision pattern (multi-pass; cost recorded) |
| Iterative draft → evaluate → repair workflows | multi-call | EXP-002 loop pattern, extended |

Design constraints for Phase B (recorded now so Phase A does not paint it into
a corner):

- Each strategy is a condition in a conditions registry; conditions reuse the
  deterministic-guidance discipline (no hidden LLM calls in guidance
  generation, D-029; provenance-bearing candidates, D-033; curation is
  committed human judgment where needed, D-032).
- Multi-call strategies (repair/iterate) are explicitly recorded as
  multi-pass with their extra cost; they are not silently compared with
  single-call conditions on equal footing.
- Evaluation stays the Task 008 two-tier evaluator; the human holistic
  review, when used, is blinded and separate (EXP-003 §11 pattern).
- Which strategies run on which models is decided **after** Phase A, from
  headroom and access evidence — not from an assumption that a particular
  strategy "must" win.

## 8. Anti-leak rule: no future conclusions in the implementation

EXP-004 must remain capable of surprising us. Therefore this design and any
later implementation must **not** encode:

- "candidate lists are definitely better than one candidate";
- "grammar scaffolding is definitely better than lexical scaffolding";
- "model X is definitely the best translator";
- "the previous winner deserves special treatment" (no EXP-003 model or
  condition is privileged in Phase A or in Phase B scoping);
- "EXP-003's B > A result is a general law" (it is a story-conditional pilot
  result of EXP-003, preliminary and not a verdict).

Those are hypotheses, not facts. Metrics are not redefined to make any
outcome look better; canonical and broader resource-supported coverage stay
side by side; failures stay recorded as data. Where this document or the
eventual report states an expectation, it is labelled as a hypothesis.

## 9. Reproducibility and artifact policy

- Deterministic packaging (prompt files + manifest) once the roster is
  approved; no timestamps in artifacts; byte-identical on regeneration.
- Story, prompts embedding the story, and raw outputs stay local (gitignored,
  copyright policy); committed: this design, curation tables when Phase B
  needs them (D-032 pattern), scripts, tests, README, and the metadata
  conventions.
- Every run reproducible from: source hash, prompt hash, evaluator commit,
  dictionary manifest, lexicon hash, recorded model/version/settings.
- Small traceable commits; SODA records (DECISIONS/LESSONS/STATE/ROADMAP/
  EXPERIMENTS/RESEARCH_NOTES) updated when the phase produces evidence.

## 10. Deliverables

At design approval: `experiments/exp004-modelscreen/` with DESIGN.md (this
file), README.md, input/ source registration, and the finalized roster +
plan.json. After execution (later tasks): collected runs, per-run analyses,
roster summary, Phase A report. This design itself changes nothing in
EXP-001/002/003 and starts no LLM run.

## 11. Open items requiring confirmation from the Project Coordinator

1. Final roster rows and versions, from §5.2 — especially: Gemini current
   model id; Grok current model; Kimi and Qwen interface/version; whether
   **GLM** web access currently satisfies §5.1; whether **GPT-5.6 Luna
   thinking ON** and **DeepSeek-V4-Pro DeepThink OFF** are available in the
   free web interfaces the coordinator uses.
2. The custom GPT "Interslavic / Medžuslovjansky Language Teacher" is still
   available to the coordinator and is to be included as its own row.
3. Practical free-tier sufficiency per model (~1 full story/day or every
   other day) — to be verified during execution, not assumed.
4. Approximate scheduling: EXP-004 execution is gated on (a) approval of this
   design, (b) the confirmations above, and (c) the standing rule that new
   translation runs do not start before the open EXP-003 human review is
   recorded and reported (ROADMAP). **EXP-003 is now closed (Task 016,
   2026-09-05) — the standing condition (c) is satisfied**; the remaining
   gates are (a) design approval and (b) the confirmations above.
5. Whether Phase 1 should reuse the same story as EXP-001/002/003 (this
   design assumes yes, for comparability) or whether a second licensed story
   is available.
6. Any model the coordinator can access that is missing from §5.2, and any
   row in §5.2 the coordinator cannot access.
7. Roster wording finalized by the Project Owner (Task 016): **Gemini is
   included only if it passes the practical free-access/quota criterion**;
   **GLM only if practical web access satisfies the project filter**; Venice
   is not an independent model; local/self-hosted models are out of scope;
   **Bielik remains an already-observed negative qualitative case and is not
   given another full baseline run unless a methodological reason arises**.

## 12. Status / approval gate

> Naming: this design's **Phase A/B** correspond to **Phase 1 / Phase 2** as
> used in the Task-016 instructions and the ROADMAP (Phase A = practical
> model screening = Phase 1; Phase B = guidance-method experiments = Phase 2).

- **Prepared:** 2026-09-05 (Task 013). No LLM called; no output produced;
   no metric, evaluator, or experiment changed.
- **Roster and screening protocol FINALIZED (Task 016, 2026-09-05):** the
   candidate roster of §5.2 is confirmed as the Phase 1 list
   (GPT-5.6 Luna thinking OFF/ON, GPT Interslavic Teacher custom GPT, Claude
   Sonnet 5, Gemini conditional on the free-access/quota criterion,
   DeepSeek-V4-Pro DeepThink OFF/ON, Grok, Kimi, Qwen, GLM conditional on
   web access; exclusions in §5.3 as updated in §11.7). Phase 1 tests a
   **clean direct-translation baseline only** — no scaffolding, candidates,
   morphology/POS or grammar guidance, alternatives, or repair loops yet
   (§6.2). Only after Phase 1 selects the strongest/practical models are the
   assistance methods tested systematically, in this order (Phase 2):
   1. direct translation; 2. lexical candidate guidance; 3. multiple
   resource-supported alternatives; 4. POS/morphology guidance; 5. grammar
   guidance; 6. lexical + morphology/grammar combinations; 7. evaluator/
   repair loop — the goal is the best model × method combination, not a
   blind matrix. EXP-004 designs **no human-evaluation exercise** (D-042):
   it relies on deterministic resource-grounded evaluation, with EXP-003's
   human results as the independent signal already collected.
- **Not approved for execution.** Execution begins only after Project
   Coordinator / Architect approval of this design and confirmation of §11.
   Until then the repository's next *pending* step is Phase 1 execution;
   EXP-003 is closed and its report (`../exp003-scaffold/REPORT.md`) is the
   source of truth for that experiment.

