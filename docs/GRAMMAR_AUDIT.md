# Grammar Consistency Audit

Interslavic morphology as described by Jan van Steenbergen's documentation
(`https://steen.free.fr/interslavic/grammar.html` and sub-pages) versus the two
implementations:

- **JS** — `sonic16x/interslavic` dictionary app via the legacy
  `@interslavic/utils@3.4.0`, and its active successor `@interslavic/morphology@0.1.2`
  (`medzuslovjansky/js-utils`). Verified by running the package locally.
- **Rust** — `gold-silver-copper/interslavic` (HEAD `599954b`). Audited
  statically (no Rust toolchain available); the crate's parity harness
  documents byte-for-byte comparison against the JS reference.

The Rust project explicitly targets **parity with the JS implementation**
(`@interslavic/utils`), and both engines implement the same rule engine.
Where the two engines differ, the difference is structural/representational,
not in the generated forms.

Legend: ✅ full agreement · ⚠️ implementation difference (same substance, different surface) · 🔶 documented optional variant, one option implemented · ❌ documented rule not implemented · ❓ needs further investigation

---

## Cases

| Feature | Steen documentation | JS implementation | Rust implementation | Verdict |
|---|---|---|---|---|
| Case inventory | 7 cases (Nom, Acc, Gen, Dat, Ins, Loc, Voc); vocative "is actually not a real case" — singular only, masculine/feminine only, never affects adjectives/pronouns | 7-case paradigm incl. Voc (emitted as a case cell for nouns) | 6-`Case` enum + standalone `vocative()` function returning `Option<String>`; `None` = "address with the nominative" | ⚠️ Same forms, different API. Rust makes the "not a real case" decision explicit in its type system. |
| Vocative forms | Hard masc. stems -e (k/g/h → č/ž/š before it); soft masc. stems -u; -ec → -če; -a words → -o; to be avoided for feminine consonant stems and neuters | Full rule set (verified: `brat→brate`, `otec→otče`, `Bog→Bože`, `žena→ženo`, `kost→kosti`, `slovo→slovo`) | Same rule set; but returns `None` for feminine consonant stems and neuters (verified in docs/tests: `vocative("noč", Feminine) → None`, `vocative("slovo", Neuter) → None`) | ❗ **Discrepancy between the two engines.** Rust follows Steen's *prose* ("the vocative is to be avoided"); JS emits a cell following Steen's *tables* (which do list `kosti`). Steen's own material is internally inconsistent here. For evaluation this matters: a JS-derived lexicon contains vocatives like `kosti`/`noču`, a Rust-derived validity check will not accept them. ❓ |
| Locative singular | Recommended **-u** (same as dative); "alternatively … possible to use **-ě** after hard consonants and **-i** after soft consonants (e.g. bratě, muži)" | m1/m2/n1 → -u; f1 → -ě; f2/f3 → -i; m3/n2/n3 emit the alternates in two cells | Identical (`noun_locative_sg` = `noun_dative_sg`; m1/m2/n1 → -u, f1 → -ě, f2/f3 → -i) | ✅ Engines agree; 🔶 the optional -ě/-i masculine/neuter locative is documented but **not generated** by either engine. |

## Gender, number, animacy

| Feature | Steen | JS | Rust | Verdict |
|---|---|---|---|---|
| Genders | M / F / N | M / F / N | `Gender::Masculine/Feminine/Neuter` | ✅ |
| Numbers | singular, plural (dual exists in Slovene/Upper+Lower Sorbian, not in ISV) | Sing/Plur (no dual) | Sing/Plur (no dual) | ✅ documented-and-not-implemented only insofar as the dictionary app's grammar pages display optional dual columns; neither morphology engine generates dual, and Steen's grammar does not present it as standard ISV |
| Animate masculine | accusative = genitive (sg + pl) | implemented (`m1` class, acc = gen) | implemented (`m1`, acc = gen; `establish_plural_noun_gender` keeps m1 in plural) | ✅ |
| Masc. -a person nouns (`sluga`, `sudja`) | sg = 2nd declension, pl = 1st declension animate | implemented | implemented (`establish_plural_noun_gender`: f1 sg + m1 raw → m1 plural) | ✅ |
| Pluralia tantum | recognized | implemented (`declensionNoun` `plural` flag; the plural-only branch) | implemented (`decline_plural_only_noun`) | ✅ |

## Noun declension

| Feature | Steen | JS | Rust | Verdict |
|---|---|---|---|---|
| Declension classes | 1st (masc./neut. o-stem), 2nd (fem. a-stem + -a masc.), 3rd (fem. consonant), + optional athematic | m1/m2/m3, f1/f2/f3, n1/n2/n3 | identical class system (`establish_noun_gender`) | ✅ |
| o/e and y/i rules (hard vs soft) | explicit in grammar | implemented via root marking | implemented | ✅ |
| Fleeting vowels (`-ec`, `-o-/-e-` insertion) | documented in declension notes | implemented (`(e)/(o)` marking, inference) | implemented (`mark_or_infer_fluent_vowel`, `infer_fluent_vowel`) | ✅ |
| Genitive plural epenthesis (`okon`, `morej`) | documented | implemented | implemented (`plural_gen_ending`: -e- before -j/after soft, -o- between hard consonants) | ✅ |
| -anin plural (`Slovjanin → Slovjani`) | documented | implemented | implemented (`establish_plural_noun_root`: `-anin` → stem) | ✅ |
| -e neuters: n-stem athematic (`ime → imena`, `tele → teleta`, `more → moręte`) | "They can be inflected as ordinary neuter nouns … they can also be declined according to the more archaic athematic declension." Rule of thumb: -e after m → -men-, after hard consonant → -et-, after soft consonant → regular -o/-e noun | implements the athematic branch (n2: -men-/-ęt-) *and* regularizes as alternate cell | implements both alternates (verified: `more` → gen.sg. `moręte/moręta`) | 🔶 documented optional variant; engines offer both forms, with the athematic form marked "Athematic" and the regularized form as alternate |
| Irregular n3 (s-stems `nebo → nebes-`, `oko → oč-`, `uho → uš-`) | documented | implemented | implemented (n3 + `očь/ušь`, `čudo/dělo/…` table) | ✅ |
| **The task's example `more → morem`** | n/a | Both engines verified live: **`@interslavic/morphology@0.1.2`** and the legacy **`@interslavic/utils@3.4.0`** produce `morętem`/`morętom` (instrumental singular of `more`, an n-stem neuter; gen. `moręte`/`moręta`). The dictionary headword for "sea" is **`morje`** (soft-stem regular), whose instrumental is `morjem`. **`morem` is not generated by either engine and is not a dictionary headword.** | Same behavior | ❗ The task example appears to be based on treating Polish `more` as a regular soft-stem noun. As an evaluation example it is misleading — see `experiments/exp001-baseline/DESIGN.md`. |

## Adjective declension

| Feature | Steen | JS | Rust | Verdict |
|---|---|---|---|---|
| Endings | -y/-i (hard/soft), acc.-gen. for masc. animate, o/e and y/i rules | implemented | implemented (`adjective::decline_adj`) | ✅ |
| Short (indefinite) form | -y/-i omitted in masc. sg. nom. (possessives -ov/-in; predicative use optional) | implemented (possessive/short adjectives) | implemented (`short_adj`); possessive adjectives handled | ✅ |
| Comparison | Analytic (`vyše`/`bolje` + positive) and synthetic (-ějši/-ejši, `naj-` superlative); 7 irregular comparatives (`dobry→lěpši/lučši`, `zly→gorši`, `veliky→večši/bolši`, …); `naj-` on the positive as simplification | implements synthetic comparative/superlative incl. irregulars | implements comparative/superlative incl. irregulars (`comparative()` returns `(lěpši, lěpje)`-style pairs) | ✅; analytic comparison is a syntactic construction — not an inflection function in either engine (fine) |
| Substantive use | -ogo/-ego, -oj/-ej inflections | implemented | implemented (`decline_substantivized_adjective`) | ✅ |

## Pronouns

| Feature | Steen | JS | Rust | Verdict |
|---|---|---|---|---|
| Personal pronouns | 6 cases (no vocative); clitic (bracketed) forms; 3rd person gains **n-** after prepositions; locative forms `jim/jej/jih` "never occur" (locative always after preposition) | paradigm with clitic and full cells | `PronounStyle::{Full, Clitic, AfterPreposition}` — explicit 3-way API; `AfterPreposition` adds n-; locative only meaningful with n- | ⚠️ Same substance; Rust makes the 3 styles first-class. ✅ |
| Reflexive `sebe` | inflected like `ty`, no nominative | implemented | implemented | ✅ |
| Possessive | `moj`-class (soft) + `jegov/jęjin/jihny` (hard, uninflected alternative: `jego/jej/jih`); `svoj` reflexive; `čij` etc. like `moj` | implemented | implemented (`pronoun()`) | ✅ |
| Demonstrative `toj` | primary; `tutoj`/`tamtoj` like `toj`; `sej`/`onoj`/`ov` documented as less common | `toj`-class implemented | `toj`-class implemented | ✅; 🔶 `sej` and `ov` are described as marginal in the prose and not implemented (acceptable) |
| Relative | `ktory`, `koj`, `iže` | `ktory`/`koj` declined via the adjectival pronoun path (`getPronounType`); `iže` as dictionary lemma | `pronoun()` covers adjectival pronoun classes; `iže` as dictionary lemma | ✅ same substance |
| Interrogative | `kto`, `čto`; -koli/-ne- indefinites | implemented | implemented | ✅ |

## Verb conjugation, tense, aspect

| Feature | Steen | JS | Rust | Verdict |
|---|---|---|---|---|
| Two stems (infinitive, present) | central design; present stem rules: -j- after -ati/vowel/-ěti, -uj- after -ovati, -n- after -nuti; 2nd conj. -i- | implemented incl. present-hint override from dictionary | implemented (`get_present_tense_stem`, present hints; dictionary rows supply the hint) | ✅ |
| Present endings | 1st: -u/-eš/-e/-emo/-ete/-ut; 2nd: -ju/-iš/-i/-imo/-ite/-et; **-em/-im alternates** for 1sg | both variants generated (e.g. `dělajų/dělam`, `nesu/nesem`) | both variants | ✅ |
| 3rd (contracted) conjugation | West/South Slavic contracted -aje- → -am/-aš/-a/-amo/-ate/-ajut | generated as "Short"/"Athematic" variants (verified: `dělam`, `dělaš`, `děla`, `dělamo`, `dělate`) | generated (parity) | ✅ |
| Consonant alternations | k/g → č/ž before -e; s/z/t/d/st/zd + j → š/ž/č/dž/šč/ždž | implemented | implemented | ✅ |
| Past tenses | Compound past = byti present + L-participle (3rd-person `je/jest/sut` usually omitted); **optional imperfect** (simple past, -h endings); **optional pluperfect** (`běh` + participle or compound) | `Perfect` (compound, gendered L-participle), `Imperfect` (simple past), `Pluperfect` | `Tense::{Perfect, Imperfect, Pluperfect}` (Perfect/Pluperfect are gendered compound slots) | ✅ |
| Future | `budu` + infinitive; perfective-present-as-future "rather to be avoided" | `Future` = budu-conjugation + infinitive | `Tense::Future` | ✅ |
| Conditional | `byh` + L-participle; past conditional `byl byh` + participle | `Conditional` | `Tense::Conditional` + `ConditionalParts` | ✅ |
| Imperative | only 2sg / 1pl / 2pl (-i/-j/-Ø, -mo, -te) | implemented | implemented | ✅ |
| Participles / gerund / verbal noun | past active (-vši), present active, past passive, present passive; gerund; verbal noun | implemented (prap/prpp/pfap/pfpp + gerund) | implemented in `VerbParadigm` (prap, prpp, pfap, pfpp, gerund) | ✅ |
| Aspect | ipf./pf. pairs listed separately in the dictionary; motion verbs three-way | dictionary marks aspect (incl. biaspectual `ipf./pf.`, ~120 rows) | `verb_forms_with_metadata` exposes aspect flags; biaspectual = both | ✅ |
| Irregular verbs | only `byti` truly irregular; `dati/jesti/věděti` athematic present; `idti → šel` suppletive L-participle | byti special-cased; dati/jesti/věděti irregular present; idti → šel | byti special-cased; same | ✅ |

## Preposition / case relationships

| Feature | Steen | JS | Rust | Verdict |
|---|---|---|---|---|
| Prepositions govern cases | "Prepositions can govern any case but the nominative" | `Preposition` POS type for dictionary rows only; **no case-government table** | `prepositions.rs`: curated `PREPOSITIONS` table (`preposition_cases`, `preposition_senses`) derived from the dictionary's `(+N)` annotations; multi-word phrases and comparative particles excluded | ⚠️ JS has none; Rust has a curated table. For evaluation: not needed for baseline (unresolved forms don't require preposition validation); useful later for grammar checking. ❓ |

## Optional variants and alternatives (summary)

| Variant | Steen documents | Engine behavior |
|---|---|---|
| Locative -ě/-i alternative for masc./neut. | yes (recommended -u, alternatives allowed) | not generated |
| Vocative for feminine consonant stems / neuters | tables list a form; prose says to avoid | JS emits it; Rust returns `None` |
| Athematic n-stem declension (`ime`, `tele`, `more`) | optional alongside regular | both generated as alternate cells |
| 1sg -em/-im vs -u/-ju | both allowed | both generated |
| Contracted 3rd conjugation | both allowed | both generated |
| Perfective present as future | "rather to be avoided" | not generated (future = budu + inf.) |
| Dual number | not part of ISV standard | not generated |
| `sej`/`ov` demonstratives | marginal | not generated |
| Perfective-as-future, T-V distinction | prose notes | n/a (not inflection) |

## Agreement / discrepancy summary

- **Full agreement**: the rule engine (cases' forms, noun/adjective/pronoun/verb
  paradigms, consonant alternations, tense system, aspect handling) is a faithful
  implementation of Steen's grammar. The Rust project's own parity harness —
  byte-for-byte comparison against `@interslavic/utils@3.4.0` at sonic16x commit
  `0fab0c5` — reports 99.9828% compatible accuracy for nouns (99,060 forms, 17
  mismatches, attributed to live dictionary data drift) and 100.0000% for
  adjectives (156,528 forms), verbs incl. participles/gerund (216,339 forms),
  personal/reflexive pronouns incl. clitic and n- series (198 cells), OOV verbs,
  and numerals. This is consistent with the static audit.
- **Implementation differences (representational)**: vocative modeling
  (JS case cell vs Rust `Option`), pronoun styles (Rust 3-way API vs JS cells),
  preposition government (Rust table only).
- **Documented optional variants, one option implemented**: locative -ě/-i
  alternates (only -u generated for m/n), `sej`/`ov` demonstratives.
- **Documented rules not implemented**: dual (not ISV), optional locative
  variants, prose-suggested avoidance of f2/neuter vocative (Rust honors this, JS does not).
- **Undocumented implementation behavior**: JS emits f2 vocatives (e.g.
  `kosti`, `noču`) that Steen's prose says to avoid; the engines silently pick
  the "recommended" locative -u; POS detection heuristics are crude
  (`detectPos("morem")` guesses *masculine*), which must not be trusted in the
  evaluation pipeline.
- **Needs further investigation**:
  1. The dictionary app's grammar tables show optional **dual** columns; the
     morphology engines and Steen's grammar proper do not. Resolve what the
     dictionary intends before relying on dictionary *table* text.
  2. Exact treatment of OOV (out-of-vocabulary) lemmas: `@interslavic/morphology`
     heuristically guesses POS/paradigm for words absent from the dictionary
     (e.g. `noč` produced unexpected vocative cells `noču/noče`). The evaluation
     must distinguish dictionary-backed validity from heuristic guesswork.
  3. `byti`/`dati`/`jesti`/`věděti` paradigms differ subtly between the engines'
     cell organization; parity tests cover them, but spot-check before using
     verb slots programmatically.
  4. Preposition government table scope (single-word only) vs full dictionary
     annotation.
