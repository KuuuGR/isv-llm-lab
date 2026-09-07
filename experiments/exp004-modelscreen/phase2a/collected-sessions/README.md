# Phase 2A collected sessions (EXP-004)

The author saves each external session here, **byte-for-byte and never
edited** (D-035), then registers the run with:

```bash
python3 scripts/run_exp004_phase2a.py collect-session \
    --run <run_id> --session collected-sessions/<file>.md \
    [--access-verdict pass|fail|unknown] [--access-note "..."]
```

Files here are **gitignored** (they contain the copyrighted Polish source
story, the reference corpus, and raw model outputs); this README is
committed.

## Naming convention (mirrors Phase 1)

`<run_id>.md` for a full session, e.g.
`2026-09-07__openai__gpt-5.6-luna__thinkoff__p2a-primed.md`.

## What a primed session file must contain (in order)

1. Prompt 1 (msg1) in full — including the reference corpus.
2. The model's short confirmation reply.
3. Prompt 2 (msg2) in full.
4. The model's final translation reply.

The collector verifies that (a) the corpus appears before the translation
instruction (same-session proof) and (b) the translation instruction +
story body matches the canonical Prompt-2 bytes. It extracts the final
reply and stores it as `output.txt` — the session file itself is never
modified.

## Task 021 addendum — the actual collected records (msg2 prompt+reply files)

For the 20 completed Phase-2A primed runs the author saved each run as the
**operator-prompts `*-msg2.md` file with the raw model reply appended after
its closing `## Output` marker** (18 original runs + the two exploratory
Dola runs 20/21). No full same-session transcripts were stored in this
directory for those runs.

These msg2 files were therefore registered with the Task-021
`collect-msg2` command (see `scripts/run_exp004_phase2a.py`): the reply is
extracted deterministically at the final `## Output` marker — the same
slicing rule `collect-session` applies to a 2-message session — and stored
byte-for-byte as `output.txt`. Because no full transcript exists, no
machine corpus-before-translation (same-session) proof is claimed for these
runs; that condition rests on the prepared msg1 prompt files (corpus
verified byte-identical) and the author's execution notes, and is recorded
as a protocol deviation (see `phase2a/README.md`, "Task 021 collection
record"). Raw replies were never edited; the msg2 files remain preserved
unmodified.

## What a control session file must contain

Only the single control prompt (or its copy with the reply starting after
the `## Output` marker) followed by the model's reply — and **nothing
else**: no corpus, no reference text. Sessions containing the corpus are
rejected as conversation contamination.
