# SCIENTIFIC_AUDIT — EXP-004 Phase 2B first manuscript draft

**Audit date:** 2026-09-18  
**Manuscript:** `docs/research/exp004-phase2b/manuscript/latex/main.tex` (+ sections/tables/figures)  
**Canonical synthesis:** `experiments/exp004-modelscreen/phase2b/analysis/combined/`  
**Scope:** scientific reviewer + evidence auditor. **No manuscript edits** in this task.

Machine-readable companion: [`SCIENTIFIC_AUDIT.json`](SCIENTIFIC_AUDIT.json)

---

## A. Executive assessment

The draft is a **serious, evidence-aligned first manuscript**: research questions are clear; Direct/Primed/Δ and the three regimes are correctly framed; claim language is mostly associative; Qwen LOW invalidation and Gemini multi-message constraint are handled honestly; matched-six means (**+7.39 / +8.53 / +5.78 pp**) are correctly reported; qualitative examples checked against audits are real, not invented.

**Readiness:** suitable to enter a **revision stage**, not yet submission-ready.

Main blockers before submission are **format/declarations/authorship**, one **small numerical inconsistency** in Table 5, a few **claim-strength tightenings**, **missing Interslavic bibliographic anchors**, and **methods detail gaps** (evaluator operational definition; prompt/decoding specifics). Length (~7.4k) is not automatically deficient; selective expansion beats padding.

**Overall grade (informal):** scientifically careful draft with limited P0/P1 corrections required.

---

## B. Critical issues

Issues that could materially affect correctness or reviewer trust:

1. **P0 — Table 5 LOW Gemini OFF Primed mean** reports **74.92** while canonical `analysis.json` / `cross_regime_table_full.csv` store **74.91**. Source of drift: `analysis/combined/analysis.md` human table also shows 74.92 (machine JSON is authoritative for synthesis).
2. **P1 — Methods under-specify evaluator mechanics** (how tokens map to inventory hits; script/reference to metric definition). External conceptual reproducibility is only partial.
3. **P1 — Interslavic language not bibliographicly anchored** (known; tracked in `REFERENCES_NEEDED.md`). Reviewers in CUP NLP will notice.
4. **P1 — Not on CUP NLP journal LaTeX template**; generic `article` class. Submission-format gap.
5. **P1 — Pending declarations/authorship** (funding, COI, optional coauthor) still placeholders — correct scientifically, but not submission-complete.
6. **P1 — Mild overstatement risk** in mechanisms/RQ framing (“demonstrates”, “generalization”) despite otherwise careful tone.

No P0 causal overclaim that priming “improves translation quality” was found as an authorial assertion (such language appears mainly in negation).

---

## C. Numerical corrections

| ID | Location | Manuscript value | Canonical value | Required correction | Priority |
|---|---|---|---|---|---|
| N1 | `tables/table5_dp_means.tex` — Gemini OFF, LOW Primed | **74.92** | **74.91** (`analysis.json` `primed_mean_pp`; `cross_regime_table_full.csv`) | Change to 74.91; prefer machine JSON over `analysis.md` prose table | **P0** |
| N2 | (upstream) `analysis/combined/analysis.md` §2 full table LOW Gemini OFF P | 74.92 | 74.91 | Out of manuscript scope here, but manuscript should not follow the drifted prose table | P1 (doc consistency; not a MS edit in this audit task) |

### Verified as matching (no correction)

| Item | Status |
|---|---|
| Matched-six means +7.39 / +8.53 / +5.78 | Match `matched_six` |
| All-config +7.07 / +8.53 / +5.45 | Match `regime_summaries` |
| Table 3 all configuration Δ (incl. Qwen LOW ---) | Match compact/full tables |
| Abstract matched-six sentence | Match |
| Conclusion matched-six sentence | Match |
| Integrity 42/42; valid configs 7/6/7 | Match |
| UNSEEN 21/21 positive replicates; Fig 2 points | Match `delta_values_pp` |
| HIGH mixed-sign appendix values (Gemini/Qwen) | Match HIGH EVIDENCE / combined |
| LOW Grok −1.50 / mean +3.95 | Match |
| SD≈5.90 (Grok HIGH), 5.56 (Qwen HIGH), 1.34 (GPT HIGH), 1.11/1.06 (Claude/DeepSeek UNSEEN) | Match rounded `delta_sd_pp` |
| Qualitative Δ examples (+15.84, +13.82, +8.84, +1.27, ortho 301→11, 365→18, Jaccard ≈0.09) | Match regime qualitative audits |
| Historical −12.08 pp as non-effect | Match `QWEN_INCIDENT.md` |
| DeepSeek attenuation 9.25→6.19→3.83 | Match |
| Table 3 Gemini OFF LOW Δ **+10.40** | Acceptable; raw mean×100 rounds to 10.40 (`delta_mean_pp` field displays 10.4) |

---

## D. Claim-strength corrections

| ID | Location | Claim (paraphrase) | Class | Notes / revision guidance | Priority |
|---|---|---|---|---|---|
| C1 | `mechanisms.tex` | LOW/UNSEEN behaviour “**demonstrates** that [opening-copy] is not required” | **SUPPORTED BUT QUALIFY** | Prefer “indicates” / “is inconsistent with the necessity of C”; still descriptive | P1 |
| C2 | `research_questions.tex` | RQ order described as “**generalization** across sources” | **SUPPORTED BUT QUALIFY** | “Persistence / cross-regime comparison” avoids inferential “generalization” | P1 |
| C3 | Abstract / Discussion / Conclusion | “**generally positive** … coverage shifts” | **SUPPORTED BUT QUALIFY** | Already qualified by Gemini HIGH negatives and “not universal”; keep that pairing mandatory in every reuse | P2 |
| C4 | Discussion “What the experiment **establishes**” | Operational integrity “establishes…” | **SUPPORTED** | OK for documented incidents; keep separate from causal priming claims | — |
| C5 | Cross-regime / Results | Gemini “direction **reversal**”; Claude/DeepSeek/GPT “**persistently** positive” | **SUPPORTED** | Accurate descriptive labels; not rankings | — |
| C6 | Qualitative “**frequently**” lexical borrowing | **SUPPORTED BUT QUALIFY** | True as audit recurrence; not quantified as a rate — avoid implying majority of all tokens | P2 |
| C7 | Implications | Evaluation-in-the-loop future system | **SUPPORTED** | Correctly labeled future engineering, not a result | — |
| C8 | Any conversion of coverage→“translation **quality**” as finding | **SUPPORTED** (as negation) | Paper correctly refuses this; do not let revision reintroduce it | P0 if reintroduced |
| C9 | Causality / overlap causes Δ | **SUPPORTED** (as rejection) | Explicitly rejected; preserve | — |
| C10 | Model ranking / best–worst | **SUPPORTED** (as avoidance) | Grok sentence explicitly rejects best/worst | — |

No **UNSUPPORTED** primary scientific finding was identified. No **OVERSTATED** claim that priming improves quality as an affirmative result.

---

## E. Evidence gaps

| ID | Gap | Why it matters | Priority |
|---|---|---|---|
| E1 | Evaluator operational definition incomplete (tokenization, inventory files, formula) | External readers cannot reconstruct *C* from prose alone | P1 |
| E2 | Exact Direct/Primed prompt templates and decoding/UI settings not quoted | Conceptual reproducibility of the intervention incomplete | P1 |
| E3 | `EVIDENCE_MAP.md` omits Table 5, Appendix A, Abstract, Fig captions | Traceability incomplete for new MS objects | P2 |
| E4 | Qualitative “frequently” not tied to counts | Fine for descriptive audit; optional quantification | P2 |
| E5 | Corpus self-evaluation ceiling mentioned lightly / not tabulated | Optional context for reading absolute coverage levels | P2 |
| E6 | No human evaluation — correctly disclosed, but still a gap for quality talk | Keep as limitation; do not fill with coverage rhetoric | P1 (interpretive discipline) |

Evidence paths for major claims (priming Δ, heterogeneity, regimes, Qwen, Gemini, qualitative categories) **exist** via `EVIDENCE_MAP.md` + combined synthesis; gaps are mostly **methods depth** and **map completeness**, not missing experiment artifacts.

---

## F. Literature gaps

Update applied conceptually here; keep tracking in `REFERENCES_NEEDED.md`.

| ID | Item | Status | Priority |
|---|---|---|---|
| L1 | Interslavic / Medžuslovjansky peer-reviewed or archival citation | **Missing** (known) | P1 |
| L2 | Venue-of-record for `zhu2023multilingual`, `moslem2023adaptive` | arXiv OK for draft; confirm published versions | P2 |
| L3 | Optional denser LLM-MT prompting literature (e.g. verified Zhang/Vilar-type papers) | Optional | P2 |
| L4 | Optional MQM/DA standards if human eval section expands | Optional | P2 |
| L5 | Citations used (Brown, Hendy, Jiao, Koehn&Knowles, BLEU, COMET, Maillard, Kocmi&Federmann, Zhu, Moslem) | **Real**; sentence support broadly appropriate (BLEU/COMET cited to contrast *non*-use) | — |

Do **not** invent Interslavic replacements in revision without verified BibTeX.

---

## G. Structural improvements

| ID | Observation | Recommendation | Size hint | Priority |
|---|---|---|---|---|
| S1 | Results already answer RQ1–RQ3; Discussion re-answers RQ4–RQ6 | Shorten Discussion’s RQ restatement; keep interpretation/limits/external validity | −100–200 words Discussion | P2 |
| S2 | Mechanisms section overlaps Qualitative | Keep hypotheses short; point back to §Qualitative examples | tighten 50–100 | P2 |
| S3 | Methods missing evaluator/prompt detail | Add compact operational subsection | **+150–300** in Evaluation/Design | P1 |
| S4 | Related Work thin on Interslavic | Expand **only after** L1 citation exists | **+200–400** | P1 (blocked on L1) |
| S5 | Absolute coverage levels (Table 5) under-discussed | 1 short paragraph on reading D/P levels vs Δ | +100–200 Results | P2 |
| S6 | Appendix useful but late | Keep; cite Appendix from Results for mixed-sign cells | cross-ref only | P2 |
| S7 | Many short sections (good modularity) vs journal continuous narrative | Optional merge RQ+Design or Mechanisms→Discussion in revision | structural | P2 |
| S8 | Word count ~7.4k | **Scientifically largely complete**; do **not** pad to 8–12k. Expand only S3/S4/S5 as needed | — | — |

Introduction → experiment path: **clear**. Results vs Discussion separation: **mostly good** (some RQ echo). Limitations: **honest**. Conclusion: **matches evidence**.

---

## H. Journal-format issues

Target: **Natural Language Processing** (Cambridge).

| ID | Issue | Priority |
|---|---|---|
| J1 | Not using CUP NLP / Cambridge Overleaf style file (generic `article`) | P1 |
| J2 | Funding / competing interests placeholders | P1 |
| J3 | Authorship pending (Jacek Kapała) correctly excluded — must resolve before submission | P1 |
| J4 | ORCID not provided (allowed as absent; confirm journal preference) | P2 |
| J5 | Abstract ~275 words — within ~300 guidance used in project | OK |
| J6 | Keywords 5 — within 3–5 | OK |
| J7 | `natbib`+`plainnat` vs CUP preferred bib style — verify against current template | P2 |
| J8 | Dual PDF copies `main.pdf` + `manuscript.pdf` — harmless; pick one for submission package | P2 |
| J9 | Data availability points to repo paths; clarify what is public vs gitignored for CUP data policy | P1 |
| J10 | AI-use disclosure present and appropriate | OK |

Scientific issues ≠ format issues; both must be cleared for submission.

---

## I. Revision priority (consolidated)

### P0 — must fix
- **N1** Table 5 Gemini OFF LOW Primed **74.92 → 74.91**
- Do not introduce quality/causal overclaims in revision (**C8**)

### P1 — important
- **E1/E2** Evaluator + prompt/decoding operational detail
- **L1** Interslavic reference (or explicitly keep restrained wording)
- **J1–J3, J9** Template, declarations, authorship resolution, data-availability clarity
- **C1/C2** Soften “demonstrates” / “generalization”
- **N2** Prefer JSON over drifted `analysis.md` figures when syncing tables

### P2 — useful improvement
- Evidence map coverage of Table 5 / Appendix / Abstract (**E3**)
- Discussion/Mechanisms redundancy (**S1/S2**)
- Optional absolute-level commentary (**S5**)
- Venue versions for arXiv entries (**L2**)
- Figure ranking optics (**Fig 1** ordered bars — caption already says descriptive; optional reorder/note)

---

## Dimension checklist (condensed)

| Dimension | Verdict |
|---|---|
| 1 Numerical consistency | One P0 table typo/rounding drift (74.92); matched-six and Δ table OK |
| 2 Evidence traceability | Strong via map + audits; methods depth gaps |
| 3 Claim strength | Mostly careful; minor softens needed |
| 4 HIGH/LOW/UNSEEN | Correct; confounds disclosed; no universal HIGH>LOW>UNSEEN ranking |
| 5 Configuration heterogeneity | Adequately and accurately described; no ranking |
| 6 Qualitative | Spot-checked examples authentic; categories distinguished |
| 7 Methodology | Core definitions clear; evaluator/prompts incomplete |
| 8 Incidents | Qwen + Gemini accurate, neither minimized nor dramatized |
| 9 Literature | Real refs; Interslavic missing |
| 10 Structure | Sound; some repetition |
| 11 Word count | ~7.4k acceptable if methods/ISV gaps addressed selectively |
| 12 Tables/figures | Correct except N1; Fig 1 descriptive OK |
| 13 Journal fit | Content OK; template/declarations incomplete |
| 14 Authorship/declarations | Correctly provisional |

---

## Qualitative example verification (sample)

| Manuscript example | Trace | Verdict |
|---|---|---|
| Claude HIGH mean +14.28; Kit→Velryb; opening | HIGH `QUALITATIVE_AUDIT.md` | OK |
| HIGH Claude r01 ortho 365→18 | HIGH audit r01 | OK |
| LOW Gemini ON r01 +15.84; črěz/govoret | LOW audit | OK |
| LOW Claude r01 301→11, +13.82 | LOW audit | OK |
| LOW Jaccard max ≈0.09 | LOW audit | OK |
| UNSEEN Gemini ON r03 +8.84 little marker echo | UNSEEN audit | OK |
| UNSEEN Qwen r02 +1.27 | UNSEEN audit | OK |
| UNSEEN GPT r03 markdown title | UNSEEN audit | OK |

No invented illustrative strings found in the audited sample.

---

## Stop

No manuscript rewrite performed. No canonical experiment/analysis changes performed. Next step (separate task): apply P0/P1 fixes in a revision pass.
