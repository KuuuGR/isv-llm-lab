# Phase 2A collected sessions (EXP-004)

The author saves each external session here, **byte-for-byte and never
edited** (D-035), then registers the run with:

```bash
python3 scripts/run_exp004_phase2a.py collect-session \
    --run <run_id> --session collected-sessions/<file>.md \
    [--access-verdict pass|fail|unknown] [--access-note "..."]
```

Files here are **gitignored** (they contain the copyrighted Polish source
story, the author-supplied corpus, and raw model outputs); this README is
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

## What a control session file must contain

Only the single control prompt (or its copy with the reply starting after
the `## Output` marker) followed by the model's reply — and **nothing
else**: no corpus, no reference text. Sessions containing the corpus are
rejected as conversation contamination.
