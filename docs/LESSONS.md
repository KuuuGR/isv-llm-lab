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

## L-010 · 2026-08-31 · Unresolved ≠ unsupported: community resources answer more than the evaluator's lexicon can

**Observation.** The cross-resource audit of all 1,050 unresolved forms found
that 403 (38.4%) are attested verbatim in `interslavicfreq` wordlists (54 also
in the full-form Hunspell `isv.dic` with morphological tags), while our
canonical `basic.json`-derived lexicon (320k entries) contains none of them by
construction. A full population audit took ~15 s using dictionary-style
lookups — no sampling was needed.

**Why it matters.** The largest single cause of Experiment 001's "unresolved"
vocabulary is *resource coverage*, not model failure: the community's broader
wordlists and full-form dictionary know these forms. Reporting the raw C-count
without this context overstates the "unsupported vocabulary" share. It also
shows an evaluator decision point: is coverage limited to the canonical
lexicon, or should attested forms in community resources count as valid?

**Next time.** Before interpreting unresolved counts, check the forms against
the other already-documented resources (cheap, full population); record
evidence categories per resource and keep orthographic relationships as
candidates, not matches.

## L-011 · 2026-08-31 · Machine-generated dictionaries carry annotation artifacts — trust the form, doubt the tag

**Observation.** `isv.dic` lists `byh` with lemma `st:abak ... case:voc`
(an implausible association) and `jeden` as `st:jedeny` (a participle), while
`bojala st:bojati vf:part tense:past sg fem` is clean. Community data is
pipeline-generated; individual rows are not curated.

**Why it matters.** A full-form hit is strong attestation evidence, but the
accompanying lemma/POS annotation can be wrong. Recording the raw tag as
evidence (with provenance) is correct; propagating it into the canonical
dictionary or metrics would import the artifact.

**Next time.** When auditing against generated resources, store the raw
annotation line as evidence and call out suspicious rows rather than
silently trusting or silently fixing them.

## L-012 · 2026-08-31 · Morphology-derived candidates need a closeness filter and only fire when stronger evidence is absent

**Observation.** When building EXP-002's candidate list from the evaluator's
B-fallback candidate lemmas, prefix-only matching produced semantically
irrelevant suggestions (`rekol` → `reklama`). Restricting to canonical
headwords, adding a paradigm-closeness check (some generated form shares a
≥5-char prefix with the unresolved form; ≥3 for short forms), and suppressing
morphology-derived candidates whenever an orthographic or alternative-resource
candidate already exists made the candidate table defensible. Verification
also showed that candidate `surface` extraction differs per resource shape
(`entry.form` vs `entry.isv`; `hit.form` vs `hit.matched`), and that the
unresolved-form set includes inflected name forms (`przemysłavy`) that the
audit's name regexes missed — the pilot excludes names/special from revision
with its own superset detector.

**Why it matters.** A candidate table is the entire interface between evidence
and the LLM: one noisy suggestion invites the model to invent replacements
(question B becomes untestable), and one name form wrongly selected for
"revision" would corrupt story content. Deterministic, evidence-bound
candidate generation is what keeps question A (can a form be replaced?) from
leaking into question B (can the LLM use alternatives?).

**Next time.** When deriving candidates from morphology engines, always
condition on (1) canonical membership, (2) morphological closeness to the
observed form, and (3) absence of stronger direct evidence; and validate name
exclusion against the *inflected* forms actually observed, not just the source
story's name lemmas.

## L-013 · 2026-08-31 · Wall-clock timestamps are the only nondeterminism in deterministic package generation

**Observation.** Regenerating an EXP-002 input package and diffing it against
the stored copy showed byte-identical output everywhere except the
`prepared_at` ISO timestamp in `meta.json`. Everything a reviewer or operator
acts on (selection, candidates, prompt, original text, hashes) is stable
across regenerations.

**Why it matters.** "Deterministic selection" is only meaningful if it can be
demonstrated. Diffing a regenerated package against the committed layout
(rather than trusting the code) is a cheap, convincing check, and it also
catches accidental nondeterminism in iteration order, set unpacking, or
dictionary ordering.

**Next time.** When a spec promises determinism, verify it by regeneration and
`diff -r`; keep `prepared_at` as the single documented exception.