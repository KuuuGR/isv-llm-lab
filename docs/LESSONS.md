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

## L-014 · 2026-08-31 · The operator interface is part of the experiment; audit file contents, not filenames

**Observation.** Task 006 generated a perfectly usable `prompt.txt` (complete
revision instructions, candidate table with provenance, and the byte-exact
complete original translation) — but it was not discoverable as such. The
Project Owner reasonably assumed `prompt.txt` was only the generic instruction
and that the material had to be assembled from `source.txt` + `candidates.json`
+ `meta.json`. The audit then found there is no `source.txt` at all (the
byte-for-byte EXP-001 output is `original.txt`), that `prompt.txt` alone was
sufficient, and that only one LLM-facing element was missing: an explicit
statement that the model must use supplied alternatives rather than discover
new ones.

**Why it matters.** An experiment that cannot be executed without understanding
the internal JSON architecture has a usability failure at the operator
boundary — the Project Owner's "don't turn a small experiment into Microsoft
Office" concern. Filename-based assumptions corrupt the mental model
(`source.txt` vs `original.txt` vs `prompt.txt`), while content-based
inspection resolves it in minutes. The fix (one clearly named, self-contained
Markdown file per condition, whole file pasted into the LLM) is a packaging
transform, not new architecture.

**Next time.** Design the *operator handoff* (what a human copies into an LLM)
at the same time as the experiment layout; name files by their operator role;
and when auditing usability, verify actual file contents and code paths before
trusting either names or the README.

## L-015 · 2026-08-31 · Unique-form bookkeeping hides token-level regressions — align tokens, not forms

**Observation.** When finalizing EXP-002, the old "resolved unique form"
view counted a form as resolved if it was no longer C in the revised text —
which silently included C→C re-spellings (`sěli → seli`, `reći → reci`) and
hid A→C regressions on forms that were already C elsewhere. Example: ChatGPT
changed a valid `někogda` (A) into the supplied `někdy` (C), but because
`někdy` was already unresolved elsewhere in the same text, the unique-form
diff showed no regression. Only a **token-aligned transition matrix** (LCS of
lexical tokens, before→after class, all nine C/A/B transitions) exposed it —
and it also revealed a third Claude regression (`različna → různa`) that the
unique-form diff had missed.

**Why it matters.** Regression analysis is the central safety signal of a
revision experiment. Form-level diffing is cheap but blind to the *positions*
where changes happen; a model can over-apply a correct candidate to an
already-valid form and no form-level metric will see it.

**Next time.** For any before/after comparison, report both form-level counts
and the token-aligned transition matrix; treat "new unresolved unique form"
and "A→C regression" as different signals that must be tracked separately.

## L-016 · 2026-08-31 · Candidate sources and the evaluator must share one resource policy, or measured gains are uninterpretable

**Observation.** EXP-002 supplied candidates from `interslavicfreq`, hunspell
`isv.dic`, and the `slovnik` snapshot — but the evaluator is strictly
canonical-dictionary-driven (exact/folded lexicon match + morphology over
prefix-matching canonical lemmas). 113 alternative-resource surfaces used in
revisions were invisible to the evaluator, and adopted replacements `seli`,
`sedeli`, `reci`, `rekl`, `dejstvitelno` produced zero measurable coverage
gain. The mechanism works (models use supplied candidates) but the *measured*
effect depends entirely on whether the supplied surface happens to coincide
with the canonical dictionary. Individual causes were verified: `reći` is
absent from the canonical dictionary; `bojati sę` is excluded from lemma-driven
morphology (multi-token reflexive lemma); `dejstvitelno` has no
prefix-matching canonical lemma at all; comparatives such as `dalše` are not
generated.

**Why it matters.** A revision experiment is only as interpretable as the
agreement between what it *offers* (candidates from any documented resource)
and what it *measures* (canonical coverage). With two inconsistent layers, a
"good" or "bad" result can be an artifact of the resource gap.

**Next time.** Reconcile candidate generation and evaluation under one
documented resource policy before running a larger experiment — or record an
explicit, labeled attestation tier so alternative-resource forms are visible
to the analysis without silently changing the canonical A/B/C classes.

## L-017 · 2026-08-31 · A no-change model output is a result, not a failure of the analysis — verify it byte-level and keep hypotheses labeled

**Observation.** Bielik returned the input with formatting-only changes:
identical lexical token sequences (1561 = 1561, 0 positional diffs), no added
or removed surface forms; only the leading blank line, 33 dialogue `- `
markers, and indentation changed. No target form was replaced and no supplied
candidate was introduced. Byte-level verification (positional diff of lexical
tokens + surface-set diff) is what makes this a *result* rather than a guess.

**Why it matters.** A control that does nothing is informative (the mechanism
is model-dependent), but only if the "nothing" is proven, not assumed. And the
reason the model did nothing is unknowable from the output — hypotheses (echo
behavior, formatting-only interpretation, instruction-following failure) must
stay labeled as hypotheses.

**Next time.** When a model is expected to change a document and appears not
to, verify at the token level before reporting, and record possible
explanations as labeled hypotheses, never as internal-cause claims.

## L-018 · 2026-08-31 · Resource disagreements decompose into a small set of kinds — classify them before choosing a next step

**Observation.** The `interslavicfreq`/canonical discrepancy looked like one
problem but, probed against the actual data, decomposes into three kinds with
different fixes: (1) evaluator matching limits — candidate-prefix matching
does not fold etymological characters (`sedeli` cannot reach the canonical
lemma `sěděti` although `sěděli` is bucket A) and multi-token lemmas
(`bojati sę`) are excluded; (2) morphology-engine coverage — `sěsti`'s past
forms are not generated and synthetic comparatives (`dalše`) are absent from
the `inflect()`-generated lexicon; (3) resource-layer differences — `reći` and
`dejstvitelno` are simply absent from the canonical dictionary, so no lemma
path exists while the community resources attest the surfaces.

**Why it matters.** "Reconcile the resources" is not actionable until each
discrepancy is attributed: matching/normalization gaps, engine coverage, and
dictionary coverage imply different implementations, and fixing the wrong one
solves nothing (e.g. adding `reći` to a wordlist would not fix the `sedeli`
prefix gap).

**Next time.** When resources disagree, probe each form against every layer
(canonical headword, lexicon, live morphology generation, hunspell tags,
frequency, historical snapshot) before proposing a reconciliation; classify
the disagreement, then decide.

## L-019 · 2026-08-31 · `isv.dic` is a full-form enumeration, not a rule-based dictionary

**Observation.** The Hunspell resource has no affix rules: `isv.aff` (74 lines)
contains only `SET/WORDCHARS/TRY`, 3 `MAP`, 65 `ICONV` transliteration rules and
one `REP što→čto`. Every surface is pre-enumerated in `isv.dic` (~1,042,916
lines, ~500,952 distinct forms) with pipeline-generated tags. "Present in
`isv.dic`" therefore means "the generating pipeline enumerated it with these
tags" — it is surface attestation, not evidence of morphological regularity,
and the tags can be artifacts (`byh st:abak …`, L-011) or disagree with other
layers (`seli st:seliti` = present 3sg of "settle", while the story's `seli`
is the past of "sit down").

**Why it matters.** Treating `isv.dic` membership as "canonical Interslavic"
imports both the pipeline's coverage and its tag interpretation; treating it
as a spellchecker inventory ("would not be flagged") is defensible and
reproducible.

**Next time.** Document the generative structure of a dictionary resource
(affix rules vs full-form, ICONV/REP normalization) before assigning it an
evidence role; record raw tags as evidence and distrust them as annotation.

## L-020 · 2026-08-31 · Canonical-lemma existence does not imply canonical-form coverage

**Observation.** A lemma can be a canonical headword while the engine fails to
generate its forms: `sěsti` is in `basic.json`, yet the JS engine generates no
`sěl`-forms, so `sěli` is bucket C; and `inflect()` emits no synthetic
comparative cells at all, so `dalše` is bucket C although `daleko`/`daleky`/
`dalj` are canonical. A full-form lexicon is only as complete as the generator
path that built it.

**Why it matters.** "Canonical coverage" can understate even regular
morphology when the generation path has gaps; the broader-resource tier exists
precisely to surface this, and interpreting a low canonical number as "the
models wrote non-Interslavic" would be wrong.

**Next time.** When reporting coverage, state what the generator path does and
does not emit (the lexicon manifest), and check morphology-coverage gaps
before attributing unresolved forms to the models.
## L-021 · 2026-09-01 · An evidence layer can be added without touching the classification: keep the "what" (A/B/C) frozen and add the "why" (provenance) as a separate pass

**Observation.** Task 008 added the two-layer resource policy to `isv-eval`
without modifying `classifier.py` at all. The canonical A/B/C assignments stay
byte-identical; a separate `evidence.attach_evidence()` pass attaches per-token
provenance (layer/source/kind) and a broader-support flag. The key rule that
made it safe: only an exact surface attestation in the audited alternative
resources counts toward the broader tier; diacritic-stripped/folded near-misses
(`sěli` vs `seli`) and historical presence (`slovnik`) are recorded as evidence
but never count. Verifying all 7 EXP-001 runs reproduced their A/B/C counts and
`morphologically_valid_coverage` byte-for-byte, while the new broader metrics
matched the Task 007 demonstration exactly, turned a risky refactor into a
checkable claim.

**Why it matters.** "The evaluator must change" invites regressions; "the
evaluator must gain a clearly-separated evidence layer" invites a design where
historical semantics are frozen by construction. The dual coverage pair
(canonical vs broader) is now an invariant every future report can rely on:
the two numbers can only agree or widen, never silently reinterpret the old
one.

**Next time.** When a policy change targets an existing metric, implement the
new capability as an additive layer over the old one, keep a deterministic
cross-check against a known historical run, and state the "what counts" rule
(the inclusion/exclusion list) in the report so provenance can be audited.

## L-022 · 2026-09-01 · The dictionary's per-language translation columns are a reverse-indexable resource — measure coverage before proposing NLP infrastructure

**Observation.** Task 009's EXP-003 design needed Polish→Interslavic
alignment. The repository contains no Polish lemmatizer, and a naive
suffix-stripping fallback was measured to rescue only ~5% of unique story
forms — but `basic.json` turned out to carry a Polish translation column
(`pl`, 18,916 normalized keys). Building a reverse index from it covers
lemma-level Polish vocabulary directly (`być→byti`, `się→sę`,
`pierwszy→pŕvy`, `dziś→[dnėś, tutdėnj, sego dnja]`, `tam→[tam, tamo, onamo,
onde]`), with the canonical dictionary as both the source and the filter.
The design's alignment pipeline (multiword table → exact reverse-index hit →
dictionary-verified lemma recovery → name pass-through → curated residual →
`[?]`) came out of *measuring* the gap first: 36% unique direct hits, ~5%
recoverable, the rest names plus genuinely inflected forms.

**Why it matters.** The reflexive move would have been to add a Polish
morphological analyzer dependency (heavyweight, network-downloaded, licensing
questions) before checking what the audited dictionary already encodes. The
per-language columns are real translation-equivalence evidence created by the
dictionary's editors — exactly the kind of provenance the resource policy
wants, and it costs nothing new. When it still falls short (inflected forms),
the honest answer is an explicit, committed curation table for the story, not
a silent weak heuristic.

**Next time.** Before proposing NLP infrastructure for a language pair, check
whether the canonical dictionary's per-language translation columns provide
the mapping; build the reverse index, measure exact-hit coverage on the actual
corpus, and size the residual *before* deciding whether a lemmatizer or
curation is needed. Record the measured percentages in the design.

## L-023 · 2026-09-01 · When the scaffold is the experimental variable, its generator must be deterministic and free of hidden LLM calls; measure the residual's composition before committing to a curation approach

**Observation.** EXP-003's design had to answer "how is the scaffold
generated?" before anything else. Two traps appeared. First, an LLM-assisted
generation step would silently change the variable under test
(`Polish → LLM → scaffold → LLM → ISV` claims a dictionary-scaffold result).
The design therefore adopts a fully deterministic generator and, if an LLM is
ever used for disambiguation, requires it to be an explicitly documented
experimental variable. Second, the first-pass description of the unaligned
residual said "mostly names" — measuring the actual story corrected that:
of 578 unique Polish forms, 36 % hit the `pl` reverse index directly, ~5 %
were recoverable by dictionary-verified suffix stripping, and the residual of
371 forms splits into only ~54 name-like tokens versus **~317 genuinely
inflected non-name forms** needing per-surface curation. The curation table
is therefore a substantial, explicit, committed artifact for one story, not a
small footnote.

**Why it matters.** A scaffold pipeline that hides a model call cannot answer
the question it claims to answer; and a curation workload sized from a wrong
guess about the residual's composition leads to either an over- or
under-scoped implementation. Measuring the composition (names vs inflection)
upfront makes the cost honest and the design auditable.

**Next time.** When the input transformation is the experimental variable,
(a) forbid hidden LLM calls inside it unless the LLM step is itself a labeled
condition, and (b) quantify the automatic-coverage percentage and the
*composition* of the residual (names / closed-class / inflected open-class)
before choosing between a heuristic, a curation table, or a new dependency.

## L-024 · 2026-09-01 · Dictionary headwords carry annotation artifacts that must be separated at the scaffold boundary, not shown as surfaces

**Observation.** `basic.json`'s `isv` headword field stores two kinds of
annotation inside the "surface": trailing parenthetical notes (11 headwords —
verb-government or domain notes such as `pozirati (na)`, `vråta (sport)`) and
comma-separated orthographic variants (245 headwords — `někȯgda, někȯgdy`,
`v, vȯ`). Before the cleaning step, the scaffold rendered `pozirati (na)` as
a "candidate surface" the LLM might copy verbatim, and variants remained
merged in one line (`někȯgda, někȯgdy`) so Condition B's "one candidate" was
false (two surfaces in one line) and output-matching treated the pair as one
surface. Cleaning at the candidate builders fixed both: notes become
`headword note: (…)` detail metadata, and comma-split surfaces become distinct
candidates with the first canonical and the rest `orthographic_variant`
(layer + kind + explicit "orthographic variant of …" note). In the op-pl
story this produced 20 distinct variant pairs / 131 variant candidates; none
of the 11 noted headwords occur in this story, but the handling is tested.

**Why it matters.** The scaffold is the only interface between the resource
and the LLM; a single malformed surface (`pozirati (na)`) invites mechanical
copying and contaminates candidate-adoption matching. Provenance that belongs
in metadata must never ride along inside a surface string.

**Next time.** When consuming a community-generated dictionary, profile the
headword field's value shapes for embedded annotations *before* rendering it
anywhere an LLM or matcher sees it; separate surface from metadata at the
data boundary, not downstream.

## L-025 · 2026-09-01 · When a design document contradicts itself, resolve toward reproducibility and record the decision

**Observation.** The EXP-003 design's curation section (§6.2/§6.3) describes
the curated residual table as an explicit, *committed* artifact, while §19's
directory listing marks `curation/` (and `scaffolds/`) as gitignored
("embeds story tokens"). Task 010 resolved this toward the design's own
rationale: the curation tables are committed (they are the reproducibility
record that makes the scaffold regenerable and auditable), while the aligned
scaffolds, inputs, operator prompts, and outputs stay gitignored (they embed
the story / model output, per the copyright policy). Regeneration on a fresh
clone is therefore half-reproducible (tables + code committed; story must be
restored locally), exactly like EXP-001/002.

**Why it matters.** An internal contradiction left unresolved would produce
an arbitrary choice at implementation time with no record. Making the choice,
documenting the tension, and recording the resolution (D-032) turns an
ambiguity into auditable methodology.

**Next time.** When implementing a design, actively look for contradictions
between its prose and its structure lists; resolve them explicitly in the
SODA record with a one-line rationale, and prefer the option that preserves
reproducibility.

## L-026 · 2026-09-01 · A deterministic candidate ordering is not automatically the semantically-best ordering for the LLM

**Observation.** The automatic candidate sort (dictionary `type` ascending,
alternative-attestation count, variant index, lexicographic) is deterministic
and provenance-correct, but for Condition B the model sees exactly one
candidate per form, so "first candidate" becomes "the word the model is most
likely to use". The automatic first picks were sometimes wrong for the story
sense: `słowa → rěč` (speech) over `slovo` (word), `tego → ov` over the
deictic `tȯj`, `wydaje → izdavati` (publishing) over `sdavati sę` (seems),
`chodzi → hoditi` (walking) over `idti o` (is about). Task 010 reviewed every
curated entry and reordered to best-sense-first, recording the rationale in
each row's basis note (D-034).

**Why it matters.** An experiment whose variable is "the supplied vocabulary"
can silently bias against a condition if the single supplied candidate is the
wrong sense — the model then avoids it, exactly as if the scaffold had not
helped. Deterministic ≠ semantically correct; for curated entries the
human-judgment layer is the place to encode sense.

**Next time.** For any generation-time guidance where one candidate is shown,
treat first-candidate order as a research decision, review it against the
actual source sense, and record the ordering rationale with the candidate —
not as an afterthought.


## L-027 · 2026-09-01 · Verify output completeness before trusting a model's coverage numbers — small-context models truncate silently

**Observation.** EXP-003 intake (Task 011) found that 4/4 Bielik replies were
not usable translations: two truncated mid-story (≈3 of 7 acts, ~40 % of the
text, ending mid-sentence/mid-word), one was a Croatian paraphrase/echo of the
prompt scaffold (no translation), and one was a service error page. The
complete ChatGPT/Claude replies were ~10 KB with all 9 story sections and an
end marker; the truncated ones were ~4.8 KB and stopped before the Epilog.
Structural checks (section headings, end markers, head/tail lines) identified
all four failures in seconds; the echo and the error page had zero story
sections.

**Why it matters.** A coverage number computed on a truncated translation is
not a coverage number — it silently measures a prefix of the story (Bielik
partial canonical coverage 57 % / 39 % looks "low" for reasons that have
nothing to do with vocabulary quality). Had the pipeline registered and
evaluated every file without a completeness gate, the analysis would have
mixed non-comparable texts. The completeness gate (structural inspection +
documented run status, D-035) is what keeps the comparison meaningful.

**Next time.** Any externally executed run collection should start with a
structural completeness check per file (expected section markers, end marker,
head/tail, byte size relative to complete peers) before any evaluation or
comparison — and failures must be recorded as data (status + note), never
silently rerun, repaired, or excluded from the record.

## L-028 · 2026-09-05 · Pre-register model-selection criteria before screening; a roster decided after the fact is a rationalization risk

**Observation.** EXP-004 preparation (Task 013) had to fix which models belong
in the main screening. The coordinator supplied an explicit practical filter
(web/chat interface without local install; free access sufficient for ~1 full
story per day; identifiable model/version/settings) plus explicit exclusions
(Venice AI as a platform, Mistral as unavailable, Bielik as a preserved
qualitative negative result). Writing those criteria into a design document
(D-036) *before any run* made the roster auditable and prevented the model set
from being argued from the results later.

**Why it matters.** Model choice is the first place selection bias enters a
benchmark: without a stated filter, a roster can be quietly adjusted until a
desired ordering appears. The same discipline applies to guidance methods
(D-037): no strategy is assumed to win, and Phase B scope is decided from
Phase A evidence, not from prior preference.

**Next time.** Any multi-model or multi-method experiment should fix its
selection criteria, roster, and exclusion rationale in the design document
before execution, and record the criteria as a decision — even (especially)
when the roster contains models the project already has opinions about.

## L-029 · 2026-09-05 · A human-evaluation format that over-taxes the reviewer is a format problem — pre-test the cognitive load of the task, not just its content

**Observation.** EXP-003's prepared human review asked the Project Owner to
compare four complete long translations of the same story and form holistic
judgments (Task 012). When the Project Owner attempted it, the format itself
failed: holding four full texts in working memory while judging them is too
cognitively demanding, and the resulting subjective judgments would be
unreliable. No result about any condition was inferred from the attempt —
the failure was methodological (D-038). The replacement is a sentence-level
forced-choice test: ~100 questions, each asking for a single best-choice among
four short renderings of one source sentence, designed to be answerable in
seconds.

**Why it matters.** A review instrument can be content-valid and correctly
blinded and still produce noise if the *task* exceeds the reviewer's
cognitive capacity. The earlier design (Task 012) validated the artifact
mechanically (blinding, determinism, byte-exactness) but not its workload.
The Project Owner's attempted reading was the de facto pilot that exposed the
workload problem — and the correct response was to redesign the measurement,
not to salvage a low-reliability holistic verdict or to invent results.

**Next time.** Any human-evaluation instrument should include a workload
pre-test with the intended reviewer on a small slice (e.g. 5–10 items of the
real format) before full preparation, and the format should minimize
working-memory load (single decision per item, short items, no full-text
ranking). When a format fails for cognitive-load reasons, record the
supersession as a decision, preserve the old artifact as historical, and
report that no result was obtained.

## L-030 · 2026-09-05 · Machine-checkable alignment beats eyeballing when a questionnaire must pair sentences across conditions

**Observation.** Building the EXP-003 sentence-level test (Task 014) needed to
pair, for each question, one Polish source sentence with the corresponding
sentence from each of the four conditions (A/B/C/D) of the same model —
across outputs whose paragraph breaks and even sentence boundaries differ.
Blind indexing would drift after the first merge/split; manual pairing of
~200 quadruples would be error-prone and unreviewable. The implemented
approach: identical punctuation segmentation rules on every document,
monotonic length-based DP alignment (1:1/1:2/2:1 + skips), then an all-pairs
cross-run token-overlap floor so only quadruples whose four Interslavic
versions share real content enter the pool (99/101 candidates per model on
real data). Tests assert that every displayed version contains the source
sentence's content marker.

**Why it matters.** A preference test built on mispaired sentences measures
nothing; the pairing is the data-generation step and must be deterministic,
conservative, and verifiable. The overlap floor deliberately errs toward
dropping ambiguous sentences (the pool is large enough to be selective).

**Next time.** When an artifact pairs items across independently formatted
documents, implement the pairing as a deterministic, tested function with a
conservative content-consistency check and record its parameters (min words,
overlap floor, seed) in the metadata — never hand-pair or index-align blind.

## L-031 · 2026-09-05 · The alphabet for an orthographic audit comes from the language's own definition — and the audit stays a separate, read-only dimension

**What happened.** A character-level sanity check over EXP-001/002/003
outputs was needed because a token/word-level lexical evaluator cannot see a
Cyrillic letter or a Polish `ł` inside an otherwise plausible output. Two
temptations arose and were rejected: (a) treat "any Latin letter" as valid
— wrong, because q/w/x are excluded from the ISV alphabet and letters like
ł/ů/ř/ü belong to national orthographies, not Interslavic; (b) derive the
inventory from our own canonical dictionary or from the model outputs —
attractive because our data is at hand, but it would silently enshrine our
data's conventions and biases as "the language". The accepted inventory was
taken verbatim from the official Interslavic orthography definition
(https://steen.free.fr/interslavic/orthography.html, fetched 2026-09-05),
including its etymological extension letters and its sanctioned alternative
graphemes, with the exact source recorded in the module and the docs.

A second trap: conflating the new metric with existing lexical/resource
coverage. A word missing from the canonical dictionary is not automatically
invalid Interslavic, and a stray character is not proof that a whole
translation is linguistically bad. The audit is therefore read-only (never
normalizes, transliterates, or repairs text), reports its own per-run
metrics, and deliberately does not recompute or alter any historical
EXP-001/002/003 score or comparison artifact — both signals are archived
side by side for later analysis of their relationship.

**Why it matters.** Orthography and lexical coverage answer different
questions; merging them would corrupt two already-committed historical
comparisons and would make it impossible to study whether character
contamination and resource coverage move together or independently. And an
audit that "helpfully" repairs text would destroy the very evidence it is
supposed to surface.

**Next time.** For any constructed-language output audit, source the letter
inventory from the language community's authoritative definition (record the
URL and fetch date), classify non-letter characters explicitly (punctuation
vs formatting vs control), report counts and locations rather than verdicts
per file, and keep the layer read-only and separate from every existing
score.

