# Phase 2A operator prompts (EXP-004)

Files in this directory are **gitignored** (they embed the copyrighted
Polish source story and the reference corpus, which is local-only); this
README and `manifest.json` (hashes only) are committed.

## Inventory (58 prompt files, 18 original configurations + 2 exploratory)

- `ctl-<NN>-<model>-<version>.md` (18) — control condition, single message:
  identical task to Phase-1's baseline. Only needed if the author chooses
  to re-execute a fresh control; otherwise the Phase-1 baseline output IS
  the control data.
- `primed-<NN>-<model>-<version>-msg1.md` (18) — corpus-priming message 1:
  study the combined reference corpus of three authentic Medžuslovjansky
  registers (literary/narrative, artistic/poetic, informative/encyclopedic)
  as a language reference only (vocabulary, morphology, syntax, word
  formation, phraseology, orthography, stylistic patterns). The artistic
  register is not normalized and may contain deliberate poetic choices — it
  is not a normative grammar template. NO translation requested; the model
  must not translate/summarize/reproduce/continue/analyze the corpus or
  answer questions about it, and receives no word-level correctness claims,
  dictionary candidates, grammatical annotations or translations.
- `primed-<NN>-<model>-<version>-msg2.md` (18) — corpus-priming message 2:
  the same Polish source story as Phase 1, translated using the preceding
  text as reference.

`<NN>` is the model's Phase-1 roster number (01–19, GLM=11 absent) so any
prompt maps back to its Phase-1 identity. The translation instruction +
story body is byte-identical across all control and msg2 files (headers and
the msg2 lead sentence differ only).

**Exploratory additions (Task 021, runs 20/21) — author-created, NOT part
of the 18-configuration kit and not produced by `prepare`:**

- `primed-20-dola-3.8-Fast-msg1.md` / `primed-20-dola-3.8-Fast-msg2.md` —
  Dola 3.8 — Fast (run 20);
- `primed-21-dola-3.8-Pro-msg1.md` / `primed-21-dola-3.8-Pro-msg2.md` —
  Dola 3.8 — Pro (run 21).

These were built by the author from the Qwen-3.8-Max-THINKING kit template
(header metadata edited; Qwen title / "COPY THIS ENTIRE FILE INTO Qwen
Chat (web)" operator lines and a msg1 `Condition:` line mislabelled
"(translation task)" remain as cosmetic copy-paste artifacts). Both msg1
files embed the authoritative three-register corpus **byte-identically**;
both msg2 bodies are byte-identical to the canonical prompt. Identity is
author-recorded in the headers only and is not independently verifiable
(Dola had no Phase-1 baseline at Task 021). `manifest.json` records all four
exploratory entries (58 entries total) with `"exploratory": true`.

**Task 022 + Task 023 — the Phase-1 DIRECT baselines for the two Dola
configurations live in the Phase-1 kit, NOT here:** see
`../operator-prompts/20-dola-3.8-fast.md` and
`../operator-prompts/21-dola-3.8-pro.md` under `experiments/
exp004-modelscreen/operator-prompts/` (rendered by
`scripts/run_exp004_phase1.py extend-direct`, Task 022). They are
corpus-free fresh-session Phase-1 direct prompts; the Phase-2A Dola rows
point at them via `baseline_run_id` (`link-baselines`, Task 022). **Task
023 (2026-09-07): the author executed both baselines and they were
collected + evaluated (msg2-style records inside the Phase-1 prompt
files; `verify` verdict `complete`, usable) — `compare` now reports the
real within-Dola Phase 1 → Phase 2A deltas for runs 20/21.**

## Collected replies live inside the msg2 files (Task 021)

The author saved each completed run as the **operator-prompts `*-msg2.md`
file with the raw model reply appended after its closing `## Output`
marker** (no full same-session transcripts were stored). Consequences:

- The on-disk msg2 files of runs 01–19 therefore differ from the hashes
  recorded in the Task-020 manifest (the reply was appended; the prompt
  part through the `## Output` marker is byte-identical to the canonical
  prompt). Run 08's msg1 header was also edited to record the actual model
  ("Grok 4.5, built by xAI, fast"); its corpus region is unchanged.
- **Never run `prepare --force` in the real kit again** — it would
  overwrite the collected replies. Post-collection writes are only
  `extend-exploratory` (plan/manifest rows for Dola) and `collect-msg2`
  (registers the reply after the marker as the run output).

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
  present in control sessions; altered translation instruction). For the
  Task-021 msg2-only records, `collect-msg2` instead records that no
  machine same-session proof is available (see the deviation note in
  `collected-sessions/README.md` and `phase2a/README.md`).
