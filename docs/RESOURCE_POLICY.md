# Interslavic Resource Reconciliation and Evaluation Policy

Status: SODA Task 007 deliverable (2026-08-31).

This document reconciles the project's Interslavic resources into a layered,
transparent evaluation/reference policy. It answers one question:

> **What is the smallest rigorous and reproducible resource/evaluation layer we
> can build so that, in the next experiment, we can tell whether an LLM is
> actually producing Interslavic rather than merely producing something that
> looks Slavic?**

The answer, supported by the audit in this document, is: **the existing
resource set is sufficient to define a useful policy; nothing new needs to be
ingested.** The smallest rigorous layer is (1) a documented evidence model that
keeps every resource's role explicit, and (2) two metrics reported side by
side — *canonical coverage* (already computed) and *broader resource-supported
coverage* (attestation in the audited ecosystem). Neither alone proves
"this is Interslavic"; together they bound it, and holistic human reading
remains the separate validity judgment.

Machine-readable evidence tables behind this document:
`data/dictionary/resource-policy/evidence.json` (local, gitignored; regenerated
by `scripts/audit_resource_layers.py`).

---

## 1. Resource matrix

| Resource | Layer | Evidence type | Can validate forms? | Limitations | License / provenance |
|---|---|---|---|---|---|
| `basic.json` (19,100 rows) | canonical dictionary | headwords + `addition` variants; POS; `type` (1–9 provenance); per-language intelligibility | Headword membership only; no inflection | Single editorial lineage; `type=9` (doubtful) and neologisms present; no form generation | Data **UNRESOLVED** (app MIT); live snapshot 2026-08-31 (SOURCES.md §11) |
| full-form lexicon `lexicon.tsv` (320,824 rows) | canonical dictionary + morphology | headwords + every generated paradigm form (`form ↔ lemma ↔ POS ↔ feats`), headword vs paradigm flagged | **Yes** — deterministic surface↔lemma lookup (bucket A basis) | Only what `inflect()` can generate: no synthetic comparatives, no multi-token lemmas; generated artifact | Derived from UNRESOLVED data; engine MIT; gitignored |
| `@interslavic/morphology` 0.1.2 (JS) | morphology rules | deterministic generator: lemma + POS (+ present hint) → full paradigm | **Yes** for inflections of canonical lemmas | Rule engine has coverage gaps (verified live: no past forms of `sěsti`; no comparatives via `inflect()`); OOV heuristics exist (GRAMMAR_AUDIT) | MIT; pinned npm + committed lockfile |
| `gold-silver-copper/interslavic` (Rust) | morphology rules (alternate implementation) | same rule engine; parity harness vs JS (99.98 % nouns, 100 % others) | **Yes in principle** (same grammar rules) | **NOT_TESTABLE in this environment** (no Rust toolchain); representational API differences (vocative, pronoun styles, preposition table) | MIT OR Apache-2.0; HEAD `599954b` |
| `isv.dic` / `isv.aff` (~500,952 distinct surfaces) | alternative resource | full-form surface inventory + pipeline-generated tags; ICONV (65) + REP (1) normalization; **no affix rules** — every surface enumerated | **Surface attestation only**; not canonical, not morphological annotation | Pipeline tags carry artifacts (e.g. `byh st:abak …`); homograph ambiguity (`seli st:seliti` vs past of "sit"); stems prefixed `-` | MIT (`isv_hunspell_dict` lineage; vendored in `interslavicfreq`, pinned `b84535b`) |
| `interslavicfreq` wordlists (579,860 / 252,461 entries) | alternative resource | surface → `cB` frequency (log-scale, more negative = rarer) | Attestation + frequency signal only; no lemma/paradigm | Surface wordforms; homographs not disambiguated; diacritic-stripped matches implicit (no orthographic metadata) | MIT; frozen msgpack.gz; pinned `b84535b` |
| `slovnik` snapshot (18,464 rows) | historical reference (same lineage as `basic.json`) | same schema as `basic.json` | Same as `basic.json` but weaker | Same lineage — **not an independent witness**; 0 headword hits for the unresolved population (Task 005) | MIT app; data UNRESOLVED |
| Steen grammar pages + community material | educational / reference | prose grammar, orthography, course/forum content | No (not machine-readable; no frozen license-cleared copy) | Copyrighted; not ingestible under current license status | © Jan van Steenbergen; Interslavic.fun, Forum courses, LibreLingo, Sekyra, Steen material — reference only (SOURCES.md §13) |

Layer vocabulary used in the rest of this document is the terminology these
resources and the existing docs actually support: *canonical dictionary*,
*generated full-form lexicon*, *morphological rules*, *alternative resources*
(surface attestation / frequency), *historical reference*, *reference material*.

## 2. Disagreement examples

The EXP-002 discrepancy forms are all unresolved (C) by the canonical
evaluator while attested in alternative resources. Per-form findings from the
audit (live evaluator + resource probes, `evidence.json`):

| Form | Canonical (`basic.json`/lexicon) | JS morphology (live) | `isv.dic` | `interslavicfreq` | Nature of the disagreement |
|---|---|---|---|---|---|
| `sěli` ("(they) sat down") | lemma `sěsti` is a headword, but **no `sěl`-form is generated** → C | does not generate the past of `sěsti` | `seli st:seliti` (present 3sg / imperative 2sg — a **different word**) | `seli` cB −619 | morphology-coverage gap **+** homograph: `seli` means "settles" here vs past of "sit down" in the story |
| `sedeli` | not in lexicon; candidates `sedlati/sedlo/sedm…`; `sěděti` **not reachable** because candidate-prefix matching uses `sed-`, not folded `sěd-` | generates `sěděli` from `sěděti` (which is **A** in the lexicon) | absent | `sedeli` cB −619 | **evaluator normalization gap**: `ě` is not folded in candidate-lemma prefix matching, so the correct lemma cannot be found from the un-`ě` spelling |
| `reci` / `reći` | `reći` is **absent from the canonical dictionary** → no lemma, C | cannot generate (no lemma) | absent | `reci` cB −580 | **resource-layer difference**: dictionary coverage |
| `rekl` / `řekl` | same as `reci` (candidates are only `reklama…` noise) | cannot generate | absent | `rekl` cB −486 | resource-layer difference: dictionary coverage |
| `dejstvitelno` | **no canonical lemma starts with `dej`** → empty candidate list, C | n/a | absent | `dejstvitelno` cB −650 | resource-layer difference: dictionary coverage |
| `dalše` | candidates `daleko/daleky/dalj`; none generate the comparative; `daľši` is not a headword | `inflect()` emits **no comparative cells** at all | `dalše st:daľši po:adj deg:cmp` (lemma `daľši`, not canonical) | `dalše` cB −495 | **comparative coverage gap** + resource-layer difference |
| `bojala` | canonical lemma is `bojati sę` — **multi-token**, excluded from lemma-driven matching → C | cannot generate (lemma excluded) | `bojala st:bojati … part past sg fem` | `bojala` cB −529 | **multi-token lemma exclusion** (a structural evaluator limit) |

For comparison, `sěděli` is resolved by every layer (lexicon paradigm of
`sěděti` = A; `isv.dic` exact; freq cB −508): it is **not** a discrepancy
form — only its `ě`-less spelling `sedeli` is.

**Conclusion.** The discrepancies are of three kinds, and the evidence does
not say any layer is "right" or "wrong":

1. **Evaluator normalization/matching limits** (structural): candidate-prefix
   matching does not use folded keys (`sedeli` ↔ `sěděti`); multi-token
   lemmas are excluded (`bojati sę`).
2. **Morphology-engine coverage** (`sěsti` past forms; synthetic comparatives
   not emitted by the lexicon-generating `inflect()` path).
3. **Resource-layer differences** (dictionary coverage): `reći`,
   `dejstvitelno` are simply absent from the canonical dictionary, so no
   canonical lemma path exists, while the community resources attest the
   surfaces.

These are preserved, not resolved — no resource and no evaluator behavior was
changed.

## 3. Evaluator diagnosis

`isv-eval` answers the **narrower** question:

> **Can this surface be generated/recognized from the canonical dictionary and
> morphology resources?**

not the broader question *"is this form valid Interslavic?"*.

- **A** = exact or etymological-folded match in the generated full-form
  lexicon (headword or paradigm form). Folded matches are flagged
  (`folded_match`) and are orthographic variants, not exact spellings.
- **B** = the JS engine generates the surface from a prefix-matching canonical
  lemma (3–4 character prefix, ≤150 single-token lemmas). Bucket B is nearly
  empty in practice because the lexicon already contains the whole paradigm.
- **C** = unresolved: no canonical lexical or morphological path.
- **non_lexical** = punctuation/numbers, excluded from all denominators.

Known limits of the *question it answers* (all verified, see §2):

1. Canonical-only: alternative resources are never consulted (this is what the
   `interslavicfreq` discrepancy is).
2. Candidate-prefix matching does not fold etymological characters
   (`sedeli` cannot find `sěděti`), and skips multi-token lemmas (`bojati sę`).
3. The lexicon contains only what `inflect()` emits — e.g. no synthetic
   comparatives, no past forms of `sěsti` — so "canonical coverage" can be low
   for perfectly regular morphology the engine does not generate.
4. It is a coverage metric against resources, never a linguistic-quality
   judgment.

**Metric terminology.** `morphologically_valid_coverage` (= (A+B)/lexical
tokens) is an accurate *resource* metric but its name invites
overinterpretation as "valid Interslavic". Future reports should label it
**canonical coverage** (this document adopts that term) and state the narrower
question explicitly. Historical reports already state the denominator and
definition and are **not** rewritten.

## 4. Proposed evidence model

Minimal, documented schema — one record per form. Categories are derived from
the audited layers, not invented:

```text
FORM
 ├── surface                 observed surface form
 ├── canonical               canonical dictionary evidence
 │     ├── headword/addition (basic.json) + POS + type
 │     └── lexicon entry     (headword | paradigm form) + lemma + feats
 ├── morphology              morphological rules evidence
 │     └── generated from canonical lemma(s)? (which lemma, which form)
 ├── hunspell                alternative resource
 │     └── exact surface? + raw tags (pipeline-generated, distrust the tag)
 ├── frequency               alternative resource
 │     └── wordlist + cB (verbatim | diacritic-stripped)
 ├── variant                 orthographic relationship
 │     └── folded / diacritic-stripped / REP (a candidate, never a match)
 ├── history                 slovnik snapshot hit (same lineage; no weight)
 └── provenance              which resources were checked, their pins/hashes
```

Decision classes (the five outcomes the model can express):

| Class | Meaning | Typical evidence |
|---|---|---|
| 1. canonical form | headword or `addition` variant in `basic.json` | canonical + lexicon headword |
| 2. generated inflection | generated by `@interslavic/morphology` from a canonical lemma | lexicon paradigm form, lemma-linked |
| 3. attested variant | orthographic variant (folded/stripped) of a canonical or alternative-attested form | variant edge, `folded_match` |
| 4. resource-only evidence | exact surface in `isv.dic` / frequency wordlists, no canonical path | hunspell exact / freq exact, canonical empty |
| 5. unresolved / no evidence | nothing in any audited layer | all layers empty |

No database is needed; a JSON record (as produced by
`scripts/audit_resource_layers.py` and the Task 005 audit) is sufficient. The
model's purpose is to make "which layer supports this form, with what
strength" explicit and machine-checkable.

## 5. Proposed evaluation policy

Reproducible rules for future experiments:

**What counts as:**
- **Canonical Interslavic vocabulary** — a surface whose normalized key is a
  `basic.json` headword or `addition` variant.
- **Valid inflected form** — a surface generated by `@interslavic/morphology`
  from a canonical lemma (lexicon membership), i.e. the current A/B basis.
- **Accepted variant** — a folded (etymological) or documented orthographic
  variant of a canonical or generated form; always recorded as a variant, with
  `folded_match`-style flags, never silently upgraded to an exact match.
- **Alternative-resource evidence** — an exact surface in `isv.dic` or the
  frequency wordlists. It is **evidence**, not canonical validity; it is
  reported in the broader tier, never promoted into the canonical A/B/C.
- **Unresolved form** — no canonical path; if it also has no
  alternative-resource attestation, it is `unresolved / no evidence`.
- **Orthographic variant** — reachable only by the documented folding /
  diacritic-stripping / `REP što→čto` rules.
- **Proper name / special token** — deterministic name-family detection and
  quoted-example patterns (existing Task 005 / pilot logic); excluded from
  revision targets and reported separately.

**What must NOT count as proof:**
- Mere similarity to another Slavic language (no cross-Slavic likeness check
  is a validity signal).
- Diacritic-stripped or folded similarity **alone** (that is a candidate for
  the *variant* class, not a match).
- Presence in a historical snapshot of the same lineage (`slovnik`) — it adds
  no independent weight.
- Pipeline-generated Hunspell tags as canonical morphological annotation
  (`byh st:abak`, `jeden st:jedeny` are artifacts).
- Frequency alone (a rare-but-attested surface is attested, not canonical).

**Two metrics (recommended for every future report):**
- **Canonical coverage** — (A + B) / lexical tokens (the current
  `morphologically_valid_coverage`, renamed/documented).
- **Broader resource-supported coverage** — (A + B + tokens attested exactly
  in `isv.dic` or the frequency wordlists) / lexical tokens. This is an
  *evidence* estimate, clearly labeled as not-a-validity-claim.

Both are reproducible by code: the first is already implemented; the second is
defined and demonstrated in §6. Implementation of the broader tier inside
`isv-eval` is the recommended next task, not part of this one.

## 6. EXP-002 interpretation under the new policy

The pilot's measured gains (+0.35 … +1.28 pp) were **canonical-coverage**
gains, because the evaluator is canonical-only. A separate, labeled estimate
(not a recalculation of the historical reports) of the **broader
resource-supported coverage** of the same EXP-001 outputs:

| Run | Canonical coverage | Unresolved tokens attested in alt. resources | Broader resource-supported coverage |
|---|---:|---:|---:|
| Claude | 73.55 % | 185 | **86.00 %** |
| DeepSeek | 74.42 % | 120 | **82.81 %** |
| Gemini | 71.72 % | 156 | **82.32 %** |
| ChatGPT | 75.95 % | 157 | **86.27 %** |
| GPTs — ISV Teacher | 79.83 % | 131 | **88.44 %** |
| Bielik | 55.48 % | 367 | **78.99 %** |
| Grok | 76.56 % | 145 | **86.41 %** |

Interpretation:

- A large share of what the canonical metric reports as "unresolved" is
  **attested in community resources** (this is L-010 quantified at the token
  level). The canonical metric therefore **understates resource support**, and
  the two metrics together give a fair picture: canonical control vs ecosystem
  support.
- Adopted pilot replacements such as `seli`, `sedeli`, `reci`, `rekl`,
  `dejstvitelno` are **resource-supported but not canonical** — under the
  two-metric policy they would register in the broader tier but correctly stay
  out of canonical coverage. The 12 A→C regressions remain regressions under
  **both** metrics (they replace canonical forms with non-canonical,
  non-attested surfaces).
- The mechanism's real effect is therefore *larger* than the canonical metric
  showed, but as **resource-supported evidence**, not canonical validity —
  which is exactly the kind of over-interpretation the two-tier policy
  prevents.

## 7. Candidate-generation implications

The `unresolved word → dictionary alternatives → LLM chooses → deterministic
validation` loop should weight candidate evidence by **layer**, not treat all
sources equally (the evidence, not an a-priori rule, supports this order):

1. **Canonical dictionary surface** (headword/addition) — strongest: every
   accepted targeted adoption in the pilot coincided with a canonical form.
2. **Generated inflection** of a canonical lemma (morphology-derived) — strong:
   canonical-lemma candidates worked; keep the closeness filter and
   no-stronger-evidence condition (L-012).
3. **Orthographic variant** of a canonical form — medium: a candidate, never a
   match (folding/stripping does not prove equivalence).
4. **Alternative-resource attestation** (`isv.dic` / frequency) — evidence
   with provenance; must be labeled so it is never read as canonical support.
   Under the current canonical evaluator such adoptions are invisible; that is
   an evaluator-scope fact, not a candidate-quality fact.
5. **Historical snapshot** (`slovnik`) — no independent weight (same lineage).

Every candidate keeps provenance (kind + source + layer + structured
evidence), which the current `prepare_exp002_pilot.py` already does.

## 8. Reference material (§13 of the task)

Interslavic.fun, Interslavic Forum courses, LibreLingo, Sekyra's and Steen's
educational material were surveyed and are recorded in `SOURCES.md` as
reference material. They are **educational/reference content**, not
machine-readable lexical evidence for a deterministic policy; their
redistribution rights are unclear, so nothing is ingested. They stay relevant
for the future human holistic evaluation, not for the machine layer. No new
repositories were added — the existing set is sufficient.

## 9. Recommendation (one next task)

**B — implement the documented resource policy in the evaluator/resource
layer** (concretely):

> Add to `isv-eval` a clearly-labeled **alternative-resource attestation tier**
> and report **canonical coverage** and **broader resource-supported coverage**
> side by side, while leaving the historical A/B/C classifications and all
> existing reports untouched.

Rationale: the audit shows the resource set is sufficient and the discrepancies
are explained (three kinds, §2); the policy is defined (this document); the
remaining gap is purely that the current evaluator cannot *report* the broader
tier. This is the smallest next step that makes future experiment numbers
interpretable under the policy. Not started here. (A larger experiment,
candidate-generation changes, or prompt changes are all premature until the
evaluator can measure the effect of resource-supported forms; abandoning the
approach is not supported by the evidence.)

## 10. Tests / checks performed

- `scripts/audit_resource_layers.py` — deterministic audit; writes
  `data/dictionary/resource-policy/evidence.json` (verified: loads all
  resources, probes 18 forms against every layer, computes population overlap,
  demonstrates the broader-coverage estimate).
- Live evaluator classifications reproduced for all probe forms (A/B/C + match
  lists) with the real `isv-eval` + Node backend.
- Live JS-morphology generation probed (`sěsti` → no past forms; `sěděti` →
  `sěděl/sěděli`; comparatives not emitted by `inflect()`).
- Hunspell `isv.dic`/`isv.aff` structure inspected (no affix rules; ICONV/REP;
  tag artifacts confirmed).
- Frequency wordlist probes for all discrepancy forms and their variants.
- Layer-overlap statistics over the full 1,050-form unresolved population.
- Broader-coverage estimate per EXP-001 run (labeled, separate analysis).

## 11. Central question — answer

The smallest rigorous and reproducible layer is the **existing resource set +
this policy**: the canonical tier (dictionary + deterministic morphology)
answers "is this form supported by the canonical Interslavic resources?"; the
broader tier answers "is it attested in the audited ecosystem?"; neither alone
proves "this is Interslavic" — both bound it, and the human holistic reading
remains the separate judgment for the parts the machine cannot decide
(especially the 60 %+ of unresolved vocabulary with no resource support).
That is the honest, minimal, reproducible answer.

## 12. Artifacts

- `docs/RESOURCE_POLICY.md` — this document.
- `scripts/audit_resource_layers.py` — deterministic evidence generation.
- `data/dictionary/resource-policy/{README.md, evidence.json}` — evidence
  table (README committed; JSON local/gitignored).
- SODA documentation: `docs/STATE.md`, `docs/EXPERIMENTS.md`,
  `docs/ROADMAP.md`, `docs/DECISIONS.md`, `docs/LESSONS.md`, `SOURCES.md`.
