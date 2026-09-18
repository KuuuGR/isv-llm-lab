# EXP-004 Phase 2B — UNSEEN candidate validation

**Document type:** methodological validation + **operator freeze record**  
**Date:** 2026-09-16  
**Candidate title:** `Ćwiczenie 2.2 — Biofizyka głosu ludzkiego`  
**Intended domain label:** medical biophysics / voice acoustics / speech biophysics  
**Machine-readable companion:** `validation.json`  
**Recommendation:** **`APPROVE`**  
**Operator decision:** **`APPROVE`** (2026-09-16)  
**Freeze status:** **`v1 FROZEN`** — SHA-256 `cd3bfb9a819b415e3cfb382e0737ba22540ccb679d0d34983c40dfbf89a9f7f4`

> Rejected in-repo candidates (`about/pl/about.md`, `Biofizyka ogólnie.md`, and other near-misses) remain rejected and are not reused here.  
> Freeze does **not** prepare a prompt kit or authorize LLM sessions.

---

## 1. Observations

### Source integrity

- The supplied text is continuous Polish educational prose with a clear sectioning:
  - title / exercise id,
  - `Część teoretyczna`,
  - `I. Opis fizycznych cech głosu`,
  - `II. Biofizyka głosu`,
  - `IIa. Wytwarzanie dźwięków mowy`.
- Paragraphs form a coherent argument from basic acoustics → resonance → source–filter voice production → formants / articulation.
- No OCR garbling, broken words, duplicated paste blocks, or dangling “see Fig./Eq.” references were found.
- Markdown heading levels are slightly uneven (several `##` headings in a row), but this does not impair experimental use as plain source text.
- The text is self-contained as a **theory** excerpt: it does not require lab procedure steps, figures, or formulas to remain comprehensible.
- Domain vocabulary is dense enough for an UNSEEN scientific/educational condition (e.g. częstotliwość podstawowa, widmo harmoniczne, rezonans/tłumienie, fałdy głosowe, ciśnienie podgłośniowe, układ „źródło–filtr”, formanty).

### Domain / regime fit

- Genre is **expository scientific/educational**, not narrative fiction (unlike HIGH `Iskra i Wieloryb` and LOW `Podkłady`).
- Topic is human-voice acoustics / speech biophysics — aligned with the intended UNSEEN domain examples (biomedical measurement / physical phenomena in medicine / acoustics in a biophysical context).
- Related teaching **topic labels** exist elsewhere in project materials (syllabus bullet; electromedicine exercise `2.2` stub title; Q&A flashcards for §2.2), but those materials are **not** this continuous prose candidate.

### Leakage scan (summary)

- No ≥40-character identical windows vs frozen authentic corpus, HIGH story, or LOW story.
- No ≥50-character identical windows vs the local Q&A lab file covering the same exercise topic.
- Content-token Jaccard (tokens length ≥5) is near-zero vs corpus and only ordinary shared Polish wording vs HIGH/LOW.
- Distinctive candidate terms (`formanty`, `fałdów głosowych`, `ciśnienie podgłośniowe`, `źródło–filtr`, etc.) are absent from the authentic corpus and from HIGH/LOW.

---

## 2. Measured facts

### Hash basis (exact text used for SHA-256)

| Field | Value |
|---|---|
| Encoding | UTF-8 |
| Newlines | LF only |
| Normalization | Body blocks joined with blank lines (`\n\n`); **one trailing newline**; no CRLF; no further transforms |
| Character count | 5242 |
| Byte count | 5676 |
| Line count | 51 |
| Whitespace-token count | 675 |
| **SHA-256** | `cd3bfb9a819b415e3cfb382e0737ba22540ccb679d0d34983c40dfbf89a9f7f4` |

The exact UTF-8 string used for this hash is stored under `candidate_text_utf8` in `validation.json` and is byte-identical to the frozen v1 source.

### Freeze locations (after operator APPROVE)

| Artifact | Path |
|---|---|
| Frozen v1 (local / gitignored) | `input/versions/exercise-2-2-voice-biophysics-v1.txt` |
| Meta (local / gitignored) | `input/unseen-domain-source.meta.json` |
| Freeze report | `UNSEEN_VALIDATION.md` |

### Comparator integrity (unchanged)

| Artifact | SHA-256 |
|---|---|
| Authentic corpus | `aaad28e43935a40313585d77a33bfc788d97e8d69b081f9486af74d52ca1a857` |
| HIGH story v1 | `ab8a0dcf7352789c09c4aca132c086999c861407e4cd682ee9414aab5b792f63` |
| LOW story v1 | `ce1c4fca03fe9cb2c5f8181ab45c91767759a0c785f0a066543d95bc32f5271b` |

### Length context (descriptive)

| Source | Approx. bytes |
|---|---:|
| Candidate (this validation) | 5676 |
| LOW `Podkłady` | 15249 |
| HIGH `Iskra i Wieloryb` | 30061 |

### Overlap quantification

| Check | Result |
|---|---|
| Identical 40-char windows vs corpus / HIGH / LOW | 0 / 0 / 0 |
| Identical 50-char windows vs `Q & A - lab.md` | 0 |
| Jaccard (len≥5 tokens) vs corpus / HIGH / LOW | ≈0.0011 / ≈0.0133 / ≈0.0188 |
| Shared HIGH/LOW named entities / corpus register titles | none found in candidate |

Shared HIGH/LOW tokens are ordinary Polish function/generic wording (e.g. `przez`, `jednak`, `powietrza`, `dźwięk` in unrelated narrative contexts) — **not** treated as meaningful leakage.

### Same-topic project materials (not passage reuse)

| Material | Relation |
|---|---|
| `Q & A - lab.md` § `2.2 – Biofizyka głosu ludzkiego` | Same teaching topic; flashcard genre; no long shared sequences with candidate |
| `electromedicine_2_2.json` | Title stub `2.2 Biofizyka głosu`; no theory body |
| Syllabus PL bullet “Biofizyka głosu ludzkiego” | Topic name only |

---

## 3. Methodological interpretation

### Domain-unseen

The authentic priming corpus is literary narrative, artistic song, and encyclopedic gardening. HIGH/LOW are Polish **stories**. This candidate is an educational biophysics/acoustics theory text on voice production.

**Assessment:** **clearly domain-unseen** relative to the frozen authentic corpus and clearly distinct in subject/genre from HIGH and LOW. Polish language alone is not used as evidence of domain novelty.

### Experimental usability

- Suitable as a standalone Direct/Primed source under the existing Phase 2B protocol (same authentic corpus for Primed; no special domain instructions required beyond the source itself).
- Genre shift (narrative → scientific exposition) and shorter length vs HIGH/LOW are **expected UNSEEN confounds to disclose**, not grounds for rejection: UNSEEN is designed as a different domain/genre regime.
- No parallel ISV version of **this** continuous text was found in MedBioPhys About / corpus / Phase 2B inputs. (Syllabus/Q&A topic labels are unrelated to the prior About parallel-ISV issue.)

### Provenance

**Known (operator-stated):** external Polish teaching/exercise-derived text on human voice biophysics; lightly edited by the operator; supplied for UNSEEN validation.

**Not established from repository evidence:** exact original publication / bibliographic citation.

**Explicitly not provenance:** rejected `about/pl/about.md` and `Biofizyka ogólnie.md`.

Limited bibliographic provenance is recorded; it does **not** by itself invalidate the candidate.

---

## 4. Unresolved uncertainty

- Exact upstream teaching-handout edition / author / year is unknown from available evidence.
- Whether operator light edits changed scientific wording relative to an unpublished original cannot be audited here.
- Cross-regime Δ comparisons will mix genre and length differences with domain-unseen effects; interpretation must remain descriptive.

---

## 5. Final recommendation

### `APPROVE` → **frozen v1**

Methodologically suitable as a Phase 2B UNSEEN candidate: coherent, self-contained educational scientific prose; clearly domain-unseen vs the authentic corpus; no meaningful passage leakage into corpus/HIGH/LOW; provenance limited but adequate.

**Operator APPROVE recorded 2026-09-16.** Source frozen as **v1** (`cd3bfb9a…f7f4`).

**Still not done:** kit preparation, prompts, LLM sessions, or changes to HIGH/LOW/corpus.

---

## Operator freeze gate

**Closed — APPROVE.** See `UNSEEN_VALIDATION.md` for the freeze ledger. Next step is optional kit preparation.
