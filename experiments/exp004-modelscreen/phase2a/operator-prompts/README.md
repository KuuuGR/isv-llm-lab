# Phase 2A operator prompts (EXP-004)

Files in this directory are **gitignored** (they embed the copyrighted
Polish source story and the author-supplied reference corpus); this README
and `manifest.json` (hashes only) are committed.

## Inventory (54 prompt files, 18 configurations)

- `ctl-<NN>-<model>-<version>.md` (18) — control condition, single message:
  identical task to Phase-1's baseline. Only needed if the author chooses
  to re-execute a fresh control; otherwise the Phase-1 baseline output IS
  the control data.
- `primed-<NN>-<model>-<version>-msg1.md` (18) — corpus-priming message 1:
  study the authentic Medžuslovjansky reference text ("Tuta historija"
  excerpt) as a language reference. NO translation requested.
- `primed-<NN>-<model>-<version>-msg2.md` (18) — corpus-priming message 2:
  the same Polish source story as Phase 1, translated using the preceding
  text as reference.

`<NN>` is the model's Phase-1 roster number (01–19, GLM=11 absent) so any
prompt maps back to its Phase-1 identity. The translation instruction +
story body is byte-identical across all control and msg2 files (headers and
the msg2 lead sentence differ only).

## Executing one primed run

1. New fresh session in the target interface (see the file header).
2. Copy `primed-...-msg1.md` in full → send → wait for the model's short
   confirmation (it is told to reply with one or two sentences and no
   translation).
3. Copy `primed-...-msg2.md` in full → send in the SAME session.
4. Save the model's complete reply byte-for-byte.

## Contamination rules

- msg1 and msg2 of one run MUST stay in the same session; msg1 must never
  be sent in a session that will not receive its msg2.
- A control run must be a single message in a session with no ISV reference
  material before or after.
- Never paste any other Medžuslovjansky material into a Phase-2A session.
- `collect-session` mechanically rejects sessions that violate these rules
  (corpus missing before the translation instruction in primed runs; corpus
  present in control sessions; altered translation instruction).
