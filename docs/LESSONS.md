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