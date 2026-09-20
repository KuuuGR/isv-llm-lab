# Evidence extraction protocol

**Status:** design protocol.

## Core distinction

```text
SOURCE
   ↓
OBSERVATION          (what the source literally shows / says)
   ↓
INTERPRETATION       (what we think it means for ISV)
   ↓
GrammarFact candidate
```

**Forbidden shortcut:** `source → immediate grammar rule`.

An observation can support a fact; it is not itself a normative rule.

---

## Observation record

```text
observation_id       stable id
source_id            link to SourceRecord
location             page/section/path/line/byte range/revision id
quote_or_excerpt     verbatim when possible; else labeled paraphrase
normalized_form      optional NFC/lowercase key for indexing
observed_form        surface form(s) as in source
claim_type           explicit_rule | usage_example | paradigm_cell |
                     table_entry | dictionary_row | engine_output |
                     commentary | paraphrase | other
context              surrounding sentence / morphological gloss / UI label
timestamp            for AV sources: start[/end] (e.g. 00:12:04)
extraction_method    manual_copy | manual_paraphrase | pdf_text |
                     html_select | asr_transcript | api_export | other
extractor            person or tool id
transcription_method for AV: human | youtube_auto | whisper | other | n/a
asr_uncertainty      none | low | medium | high | unknown | n/a
direct_quote         true | false
speaker              for AV/dialogue: name/role | unknown | n/a
notes
extracted_at         ISO date
```

### Video / AV required extras

When `source_type=video` or observation comes from AV:

- URL (via source record),
- speaker (if identifiable),
- timestamp,
- transcript text used,
- transcription method,
- ASR uncertainty,
- whether the excerpt is a **direct quote** or paraphrase.

**ASR strings with medium/high uncertainty cannot become GrammarFact
evidence without independent verification**
(`VIDEO_SOURCE_PROTOCOL.md`).

---

## Interpretation (separate note, not a fact yet)

Before proposing a fact, write a short interpretation block:

```text
interpretation_id
observation_ids[]
proposed_meaning
alternative_readings
depends_on_assumptions
suggested_status_if_accepted   (from CONFLICT_POLICY vocabulary)
```

If the source **explicitly states a rule**, say so.
If the source **only uses a form**, say so.
If Steen prose and tables disagree, record tension — do not pick a winner
here.

---

## Claim-type → default caution

| claim_type | Default caution |
|---|---|
| `explicit_rule` | May support `rule` facts after review |
| `usage_example` | Attestation only; needs more for `current_preferred` |
| `engine_output` | Observation about software, not linguistics alone |
| `paraphrase` | Weaker; prefer re-extract as quote |
| `asr_transcript` (via method) | Verify before fact proposal |

---

## Quality checks before leaving EXTRACT

- [ ] Excerpt matches source (or uncertainty labeled)
- [ ] Location/timestamp sufficient to re-find
- [ ] Observation vs interpretation separated
- [ ] No Slavic-analogy invention presented as ISV evidence
