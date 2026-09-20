# Grammar taxonomy — categories useful for LLM-assisted translation

**Status:** design taxonomy. Categories are retrieval buckets, **not** a
mandate to invent rules for every cell.

Guiding filter: keep a category only if it can (a) change generation
choices, (b) support Mode C diagnostics, or (c) encode a known conflict
the model might otherwise invent.

---

## 1. Knowledge kinds (orthogonal to domains)

See also `PROVENANCE_MODEL.md` `fact_kind`.

| Kind | Example | Role in packages |
|---|---|---|
| **Rule knowledge** | “Animate masculine accusative = genitive (sg+pl)” | Mode A/B compact bullets |
| **Lexical knowledge** | lemma `dělati` → selected paradigm cells + aspect | Mode B candidate rows |
| **Evidence examples** | attested surface in Hunspell/freq; Steen table form | Optional illustration; never proof alone |
| **Diagnostic constraints** | “If candidate has Polish *ł*, flag orthography” | Mode C |

These four must coexist without being confused: a Hunspell hit is
**evidence**, not a **rule**.

---

## 2. Domain taxonomy (initial)

### High priority for translation packages

| Domain code | Contents | Why useful for LLM MT |
|---|---|---|
| `noun.declension` | m1–n3 classes; hard/soft; fleeting vowels | Core PL→ISV noun endings |
| `noun.animacy` | animate acc=gen | Frequent Slavic transfer error |
| `adj.declension` | hard/soft; animate agreement | NP agreement |
| `verb.conjugation` | present stems; 1st/2nd/contracted; 1sg variants | Finite verbs |
| `verb.aspect` | ipf/pf/biaspectual dictionary flags | Pair selection / tense reading |
| `verb.tense_mood` | compound past, future `budu`+inf, conditional, imperative inventory | Avoid overgenerating optional tenses |
| `pronoun.personal` | full/clitic; n- after preposition | High-frequency closed class |
| `prep.case` | preposition → allowed cases (Rust table + dictionary `(+N)` notes) | Case government |
| `ortho.inventory` | accepted Latin inventory; etymological letters | Aligns with Layer-2 audits |
| `ortho.alternation` | o/e, y/i, k/g→č/ž before -e, etc. | Spelling regularity |

### Medium priority (include when source triggers)

| Domain code | Contents | Notes |
|---|---|---|
| `verb.participles` | L-participle, active/passive participles, gerund, verbal noun | Needed for past/relative clauses |
| `adj.comparison` | synthetic vs analytic; irregulars; **engine gap** on some comparatives | Mark coverage gaps explicitly |
| `numeral` | cardinal/ordinal inflection | Sparse but brittle |
| `noun.irregular` | n3 s-stems, `-anin`, pluralia tantum | Exception lists beat generic rules |
| `derivational` | productive affixes (light touch) | Only curated, high-confidence items |

### Low priority / defer

| Domain code | Why defer |
|---|---|
| Dual number | Not standard ISV; engines do not generate |
| Marginal demonstratives (`sej`/`ov`) | Documented as marginal; not implemented |
| Full discourse/pragmatics | Out of aggregator scope |
| Complete derivational morphology | Explosion risk; weak provenance |

---

## 3. Feature inventory (for indexing, not for dumping)

Useful atomic features for retrieval predicates:

- gender: M/F/N  
- number: SG/PL  
- case: NOM/ACC/GEN/DAT/INS/LOC/(VOC)  
- person: 1/2/3  
- animacy: animate/inanimate (masc.)  
- aspect: ipf/pf/biaspectual  
- tense/mood slots as above  
- orthographic: hard/soft stem; etymological character class  

Vocative remains **special-cased** because engines and Steen disagree
(GRAMMAR_AUDIT).

---

## 4. What EXP-003 D already used (baseline thin set)

Condition D annotated POS/aspect and a few example forms (infinitive /
1sg present / past m.sg) from the lexicon — **no Polish morphological
analysis**, no full paradigms (`experiments/exp003-scaffold/DESIGN.md`).

The aggregator taxonomy is a **superset for retrieval**, not a
requirement that every package include every domain. Packages should stay
small (see `../architecture/LLM_CONTEXT_DESIGN.md`).

---

## 5. Non-goals of the taxonomy

- Do not create empty rule stubs “because the category exists”.
- Do not treat the taxonomy as a linguistic theory of Interslavic.
- Do not equate taxonomy completeness with translation quality.
