# Wikipedia audit protocol

**Status:** design protocol. **Do not bulk-import Wikipedia in this pass.**

## Stance

- Wikipedia is **evidence**, not automatically normative authority.
- An unusual form is an **observation**, not a grammar rule.
- Citation quality, article age, and revision id matter.
- Distinguish editorial error from accepted variant.
- **Do not “correct” Wikipedia** based solely on the aggregator; the
  aggregator may record suspected errors for research, not for drive-by
  wiki editing as a project deliverable.

## Procedure

1. **IDENTIFY** article title, language edition (expect Interslavic /
   related), URL, revision id, revision timestamp.
2. **ARCHIVE** locator + revision id (prefer permalink to revision).
3. **EXTRACT** observations (quotes with section headings).
4. **CHECK CITATIONS** on the relevant claim (present / absent / offline /
   unreliable) — record, do not invent.
5. **COMPARE** to Tier N/C/A/S facts and the conflict ledger.
6. **CLASSIFY** each finding (below).
7. **PROPOSE** facts only via normal review — never wiki→rule shortcut.

## Classification vocabulary

| Class | Meaning |
|---|---|
| `CONFIRMED` | Matches accepted Tier N/C (or documented variant) |
| `NEW_EVIDENCE` | Novel attested usage/rule claim worth intake |
| `VARIANT` | Plausible alternate; not necessarily preferred |
| `HISTORICAL` | Explicitly old/superseded in context, or only historically plausible |
| `SUSPECTED_ERROR` | Likely mistake relative to stronger evidence |
| `UNRESOLVED` | Insufficient basis to classify |
| `NOT_RELEVANT` | Orthography noise, off-topic, non-linguistic |

## Suspected error record (required fields)

```text
article_title
article_url
revision_id
revision_date
exact_example
reason_for_suspicion
stronger_supporting_evidence   (source_ids / fact_ids)
classification                 SUSPECTED_ERROR
notes
```

Suspected errors remain research observations until human review. They do
**not** authorize silent changes to historical experiment outputs.
