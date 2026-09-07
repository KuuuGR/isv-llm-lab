# EXP-004 Phase 2A — corpus (three authentic Medžuslovjansky registers)

The Phase 2A corpus-priming reference material is a **combined corpus of
three authentic Medžuslovjansky registers** (SODA Task 020, 2026-09-07):

| # | Register | Source | File |
|---|----------|--------|------|
| 1 | literary / narrative | `Tuta historija` excerpt (Task 019) | `tuta-historija-excerpt.txt` |
| 2 | artistic / poetic | song album **Ahoj, Slovjani!** (complete, Latin-script, deduplicated) | `album-ahoj-slovjani-artistic-isv.txt` |
| 3 | informative / encyclopedic | Medžuslovjansky Wikipedia article **Sadovničstvo** (Wikimedia source) | `wiki-sadovnistvo-encyclopedic-isv.txt` |

The **authoritative corpus file** consumed by Phase 2A Prompt 1 is the
deterministic combination of the three:

- **`phase2a-authentic-isv-corpus.txt`** — combined, with plain-text
  section headers:
  - `=== REGISTER 1: LITERARY / NARRATIVE ===`
  - `=== REGISTER 2: ARTISTIC / POETIC ===`
  - `=== REGISTER 3: INFORMATIVE / ENCYCLOPEDIC ===`

The headers are metadata for the LLM (they label the register of the
following text) and are not part of the linguistic source texts.

All corpus text files (including the three component files above and the
raw sources in `sources/`) are **gitignored and stay local**; only this
README and the pinned hashes are committed.

---

## Register 1 — literary / narrative: `Tuta historija`

- **Source title:** *Tuta historija* (author-supplied excerpt).
- **Register:** literary / narrative prose with dialogue.
- **Provenance:** supplied in full by the project author (SODA Task 019,
  2026-09-06). No URL; nothing fetched from the web.
- **Included range:** `Prolog` + `Razděl 1. Věčna Zima`, beginning
  "Ljudi govoret, že v tamtoj denj bylo je veliko spokojno…" and ending
  "…da by prěžiti v tutoj težkoj době." Preserved **byte-for-byte** as
  supplied — no rewriting, normalization or "correction".
- **Transformation policy:** none (source text copied verbatim).
- **License / distribution status:** not established; author-supplied for
  the fixed Phase 2A reference corpus → **local-only**.
- **Size:** 4 820 bytes (≈ 791 whitespace tokens) · SHA-256
  `413830fa4ff6aaa8833895a22e7ef1fa5fa3807e5a5a105b7e4050cf7b67a29c`

---

## Register 2 — artistic / poetic: album *Ahoj, Slovjani!*

- **Source title:** song album *Ahoj, Slovjani!* — **Morske Opověsti** and
  10 further songs by the same Medžuslovjansky creators, as published on
  the page *"Songs interslavis text source"*.
- **Register:** artistic / poetic (sea-shanty style song lyrics).
- **Provenance:** the project author supplied a complete copied webpage
  (Latin-script songs followed by Cyrillic duplicates, with WordPress
  navigation/widget/iframe material). Copied page URL:
  `https://melacpise.wordpress.com/album-ahoj-slovjani-teksty-pesnej/`
  (source retained locally under `sources/`).
- **Included range:** the complete set of **all 11 songs in original page
  order** — Velerman, Santiana, Nikogda Vyše, Rěka Essekibo, Slovjanske
  Děvčiny, Idi, Džoni, Idi, Ješče Raz!, Primorje Barbari, Stara Maui,
  Morske Opověsti, Bude Dobro — as **Latin-script text only**: 11 song
  sections, 76 unique stanzas, 322 retained lines.
- **Transformation policy** (explicitly):
  > Latin-script song text was retained; Cyrillic duplicate versions and
  > webpage/HTML material were removed; repeated song stanzas/refrains
  > were deduplicated; linguistic forms themselves were **not** normalized
  > or corrected.
  Deduplication removed only **verbatim repeated stanza/refrain blocks
  within a song** (24 such repeats dropped). Ordinary repeated words,
  short repeated phrases, linguistically meaningful repetitions, and
  whole different songs were never merged or removed. Original wording —
  including unusual, rhyme/rhythm-driven or otherwise poetic forms — was
  preserved exactly as sung/written. This is an authentic artistic sample,
  **not** a normative grammar reference.
- **License / distribution status:** not established (author-supplied copy
  of a public blog page) → **local-only**.
- **Size:** 9 407 bytes (≈ 1 600 whitespace tokens) · SHA-256
  `7e25a56f67a52976083f625fabf040b6cd5ae399317cb36a59a302a3a52dcacf`

---

## Register 3 — informative / encyclopedic: Wikipedia *Sadovničstvo*

- **Source title:** Medžuslovjansky Wikipedia article **Sadovničstvo**
  ("Gardening"), article `Wp/isv/Medžuslovjansky jezyk` on
  isv.wikipedia.org.
- **Register:** informative / encyclopedic prose.
- **Provenance:** **retrieved externally** from the actual Wikimedia
  source during corpus preparation (2026-09-07) via the MediaWiki API —
  it is the existing Medžuslovjansky article itself, **not** a translation
  produced by this project and not a translation of another-language
  version.
  - Source URL:
    `https://isv.wikipedia.org/wiki/Sadovni%C4%8Dstvo`
  - API: `…/w/api.php?action=parse&page=Sadovničstvo&prop=wikitext&format=json`
  - Raw wikitext retained locally under `sources/` (`sadovnistvo.wikitext`).
- **Included range:** the article's **running encyclopedic prose from the
  lead through the final body section** — first paragraph
  "Sadovničstvo jest proces raščenja rastlin zaradi jih zeleniny,
  ovočev…" through the final sentence "…Asocijacije profesionalnyh
  krajobraznyh dizajnerov." (84 paragraphs). Section headings of the
  article are preserved in the running text (Prědhistorija, Ameriky,
  Historija, Koristi, Kako umětnost, …). Boilerplate was removed:
  navigation/categories, `Gledite takože`/`Iztočniky` tails, file
  inclusions, references, templates (incl. the name-gloss `LatCyr`
  template, of which only the Latin-script gloss was kept), internal
  links and other MediaWiki markup. The article's own Latin orthography
  and wording were **not** rewritten or normalized.
- **Transformation policy:** mechanical MediaWiki cleanup only; no
  linguistic editing, no translation, no content substitution.
- **License:** CC BY-SA 4.0 (per isv.wikipedia.org). The cleaned prose is
  derived from the retrieved article text, so it is kept **local-only**
  with the rest of the corpus until repository distribution policy is
  decided; this README records source URL, retrieval date, size and hash.
- **Size:** 44 101 bytes (≈ 5 772 whitespace tokens) · SHA-256
  `b03402fef2384730b90a5ab879af78be63b5e6d0e4fa00db4c3c3525844c8345`

---

## Combined corpus (`phase2a-authentic-isv-corpus.txt`)

- Built deterministically by `scripts/build_phase2a_corpus.py` from the
  three component texts above.
- **Size:** 58 459 bytes · 55 990 characters · **≈ 8 184 whitespace
  tokens** (rough upper-bound token estimate; actual token count depends
  on the tokenizer).
- **SHA-256:**
  `aaad28e43935a40313585d77a33bfc788d97e8d69b081f9486af74d52ca1a857`
- Pinned in `scripts/run_exp004_phase2a.py` (`AUTH_CORPUS_SHA256`) and
  asserted by the test suite; any edit of the corpus is detected. A corpus
  change is a **new corpus version**, never a silent edit.
- The **exact same bytes** are embedded in every primed `msg1` for all 18
  Phase-1-usable configurations; control prompts contain no corpus; `msg2`
  is unchanged.

### Context-window risk

≈58 KB (≈8 200 tokens) is well within every roster model's context
window, but it is **not** silently truncated or per-model subsetted to
make any single interface easier. If an interface ever cannot accept the
full corpus, that run is recorded as an execution/access limitation —
context-window variability is an already recorded Phase 2A methodological
risk (see `phase2a/README.md`).

## Why these three registers

Medžuslovjansky is used in genuinely different registers by its
community. Register 1 shows literary/dialogue narrative prose, register 2
shows artistic/poetic language (with the deliberate stylistic choices such
language entails), register 3 shows informative/expository prose. Exposing
the LLM to **real existing usage across registers** grounds its generation
in observed vocabulary, morphology, syntax, phraseology, orthography and
style, rather than in an imagined or prescriptively reconstructed Slavic
language. The corpus is reference material — **not** evaluation output and
**not** a normative grammar. In particular, the project's canonical
evaluator is never used as a filter to delete authentic corpus forms
(e.g. artistic forms absent from the dictionary); the artistic section is
explicitly labelled as potentially containing poetic choices.

## Contamination control

None of the registers shares plot, characters, setting or sentences with
the Polish source story ("Opowieść o Słów, Które Były Jak Siostry"); the
corpus is not a translation of the story. Phase 2A tests assert the
three-register anchors appear in every primed prompt and in no control
prompt, and that `msg2` never contains corpus bytes.
