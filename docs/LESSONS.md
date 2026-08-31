# Lessons Learned

SODA lessons mechanism. Newest last. Each lesson records what was observed,
why it matters, and what to do differently next time.

---

## L-001 · 2026-08-31 · A complete full-form lexicon makes bucket B nearly invisible — keep B as the safety net, not the headline

**Observation.** Generating every paradigm for all 19,100 dictionary rows
produced a 320k-entry lexicon in ~86 s. On real text, essentially every valid
inflected form is already an exact match (bucket A), so the live morphological
fallback (bucket B) fires almost never. The DESIGN.md procedure is correct; its
role is resilience against lexicon-generation gaps, not day-to-day coverage.

**Why it matters.** Reporting a headline "morphologically_valid_coverage" that
is dominated by bucket A is fine and intended — but the B fallback must keep
existing and tested (it is the mechanism that prevents
"not a headword = unknown"), otherwise a future lexicon gap silently inflates
unresolved counts.

**Next time.** Test bucket B with a deliberately incomplete synthetic lexicon
(as `tests/test_classifier.py::test_morphological_fallback_classifies_valid_form_as_B`
does) rather than relying on real data to exercise it.

## L-002 · 2026-08-31 · Dictionary `addition` is not a single-purpose column

**Observation.** The `addition` column mixes morphology hints (`(piše)`,
`(oka/očese; pl. oči)`) with numeric metadata annotations (`(+2)`, `(+6)`,
~200 rows) that must never reach the morphology engine as principal parts.

**Why it matters.** Passing `(+2)` as a "form" would silently corrupt
paradigms. The filter is a one-line regex (`strip (+\d+)`), cheap and
essential.

**Next time.** When consuming a community-generated dataset, profile every
column's value shapes before mapping it onto an external API.

## L-003 · 2026-08-31 · `process.exit()` on stdin close truncates unflushed stdout in Node subprocesses

**Observation.** The backend called `process.exit(0)` on readline 'close'.
Large batch responses (>64 KB) came back truncated with a clean exit code, so
`subprocess.run` reported success with a half-written JSON line.

**Why it matters.** Silent truncation is the worst kind of subprocess failure:
it looks like success and fails only at JSON parse time with a confusing
message. The fix (let the process exit naturally after stdout drains) is
invisible but load-bearing for the whole 19,100-row generation.

**Next time.** For stdio-servant scripts, never `process.exit()` immediately
after writes; verify a large response round-trips before trusting the protocol.

## L-004 · 2026-08-31 · Etymological-orthography folding must be scoped to etymological characters

**Observation.** The first folding map used acute-accent code points (`ć ś ź`)
where the ISV set uses caron letters (`č š ž ě`) as *standard* characters.
Result: standard letters were not folded (correct) but the intended fold
targets (e.g. `ų`, `ȯ`) were mixed up, and no lookup matched.

**Why it matters.** A 1:1 `str.maketrans` map silently no-ops for any
character not literally in the map; the failure only shows up as zero matches.
Getting the character inventory right (from the actual data charset) before
coding the map saves a confusing debugging round.

**Next time.** Derive the character set from the real corpus (a one-liner
`set(isv_column)`) instead of from memory of the orthography.

## L-005 · 2026-08-31 · Per-token subprocess calls are the runtime bottleneck; batch at the text level

**Observation.** With the full-form lexicon in place, bucket B was expected to
fire rarely (L-001), but the *fallback transport* still dominated runtime: the
classifier opened one Node subprocess per unresolved token. A 10 KB story
produced hundreds of unresolved tokens → minutes per run and an apparent hang.
Batching distinct candidate lemmas into one `inflect` call per 2000-item chunk
(deduplicated across tokens) cut each run to seconds with identical
classification (D-017).

**Why it matters.** Any per-token subprocess or network pattern is O(tokens)
process spawns — the constant factor explodes on real-length text even when
the logical work per token is small. The ROADMAP item was real; the design
"one morphology call per text" should have been the default from the start.

**Next time.** Before scaling to full-length inputs, profile the number of
subprocess/network round-trips, not just total tokens.

## L-006 · 2026-08-31 · Raw experiment inputs can carry hidden preprocessing artifacts — document, don't fix

**Observation.** The supplied Polish source (`op-pl.txt`) wraps the story in
markdown code fences and includes an embedded instruction line
("Przetłumacz to opowiadanie na medżusłowiański:"). The file was hashed and
used byte-for-byte; the artifact is recorded in `source.meta.json` and
propagates into every run's `prompt.txt`.

**Why it matters.** "Use the files exactly as supplied" and "document
preprocessing issues, create a derived artifact rather than changing the raw
output" conflict with any instinct to clean the input. An undocumented
artifact silently breaks future reproducibility; a documented one is evidence.

**Next time.** Always diff the raw input against expectations (fences,
BOMs, embedded instructions) *before* hashing, and record the observation in
the same meta file as the hash.

## L-007 · 2026-08-31 · Unknown metadata must be recorded explicitly, and shared unresolved forms are mostly story content

**Observation.** All seven baseline outputs were generated externally, so
model versions, dates, prompts and (for two) providers are unknown. Recording
`unknown` explicitly (D-018) costs nothing and prevents later false precision.
Also, the 8 forms unresolved by *all* models turn out to be character names
(`Bronislava`, `Teofil`), the story's quoted in-text example words
(`pul`/`pui`), and verbs every output uses (`bojala`, `bojati`, `dokazano`,
`rekla`) — i.e. shared because they are story content, not because models
converge on errors.

**Why it matters.** A naive reading of "shared by all models" as
"systematically hard for all models" would be wrong for proper nouns and
quoted content; the correct next step is to look at the sentence context that
the evaluator already preserves.

**Next time.** When reporting overlap statistics, check the preserved
sentence context before interpreting what "shared" means.

## L-008 · 2026-08-31 · Keep the translation instruction out of the source corpus

**Observation.** The supplied Polish source (`op-pl.txt`) begins with
`Przetłumacz to opowiadanie na medżusłowiański:` followed by the story; the
model outputs contain only the translation. Raw byte size is therefore NOT a
valid source-vs-output length comparison — the source carries prompt/formatting
content the outputs do not. Experiment 001 recorded sizes only for input
integrity, which is correct; the source-vs-prompt rule is set for future
controlled experiments (`source.txt = Polish story only`,
`prompt.txt = translation instructions + source text`), without retroactively
changing Experiment 001.

**Why it matters.** A byte-size comparison between a source carrying an
instruction and a translation of only the story would be an artifact of input
formatting, not of translation length or quality — exactly the kind of false
signal a baseline must avoid.

**Next time.** Separate the translation instruction (prompt) from the corpus
(source) at experiment design time, so raw file sizes and derived length
metrics compare like with like. If an input artifact is discovered after the
fact, document it and record length as future metrics rather than comparing
raw bytes.

## L-009 · 2026-08-31 · Stratify audit samples by cross-model spread; do not let simple heuristics stand in for evidence

**Observation.** When building the manual-audit sample of unresolved forms, a
"capitalized mid-sentence" heuristic seemed like a cheap way to identify
proper names — but it flagged dialogue-initial words (`ali`, `bile`, `bio`)
that simply follow a dash. The reliable basis turned out to be the explicit
name families that occur in the Polish source story (Bronisława, Teofil,
Julianna, Przemysława, Antoni, Międzyrzecze), matched against normalized forms
— and even then the first pattern set missed `przemysława` (ł) and `julijana`
(juli-jana) until the patterns covered the orthographic variants.

**Why it matters.** Sampling by raw frequency alone produces a worksheet
dominated by a few hundred tokens of story content (character names), which
is exactly what a manual audit must not drown in. Cross-model spread
(shared-by-N) and model-specific strata surface different information than
frequency. And any heuristic that silently misfires corrupts the "evidence"
a human reviewer is meant to trust.

**Next time.** For an audit sample: stratify by (frequency, shared-by-many,
model-specific, orthographic/edge features, names), keep every selection
deterministic, and validate name grouping against the actual source text
rather than a surface heuristic. Record what the sample is NOT claiming
(here: no language-origin judgment) in the worksheet itself.