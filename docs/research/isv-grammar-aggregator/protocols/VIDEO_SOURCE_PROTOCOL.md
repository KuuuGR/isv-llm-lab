# Video / YouTube source protocol

**Status:** design protocol. **Do not bulk-import YouTube in this pass.**

## Required metadata

```text
url
channel_or_speaker
video_title
publication_date          date | unknown
retrieval_date            required
transcript_source         official | youtube_auto | human | none | unknown
transcription_method      human | youtube_auto | whisper | other | n/a
timestamp                 start[/end]
transcript_confidence     high | medium | low | unknown
license_rights            as documented | unknown
```

Plus standard `SourceRecord` fields.

## Three distinct event types

| Event | Meaning | Fact eligibility |
|---|---|---|
| Speaker **explicitly states a rule** | Metalinguistic claim | May support `explicit_rule` observation → review |
| Speaker **casually uses a form** | Usage attestation | Usage observation only; weak alone for `current_preferred` |
| **ASR produced a questionable string** | Possible error | **Not** GrammarFact evidence without verification |

A transcript is **not** automatically an authoritative grammatical
statement.

## Verification rules

1. Prefer human-checked spans for any candidate fact.
2. If only YouTube auto-captions exist, set `asr_uncertainty` appropriately;
   defer fact proposal until verified.
3. Record speaker identity carefully (author vs community learner vs TTS).
4. Do not infer normative authority from subscriber count or virality.

## Intake path

Follow `SOURCE_INTAKE_PROTOCOL.md` →
`EVIDENCE_EXTRACTION_PROTOCOL.md` (AV fields) → review.
