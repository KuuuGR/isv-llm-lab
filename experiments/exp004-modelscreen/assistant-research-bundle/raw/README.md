# raw/ — why there are no raw outputs here

**Raw model outputs are intentionally NOT included in this bundle.**

- The complete experiment directory is roughly **500 MB** (operator
  prompt files embedding the copyrighted Polish source story + the
  reference corpus, and the raw model replies).
- Raw outputs are **immutable experimental evidence**: they were never
  rewritten, normalized, repaired or re-run, and they remain in the
  repository experiment directory
  (`experiments/exp004-modelscreen/repeats/operator-prompts/*.md`,
  msg2-style records: canonical prompt + raw reply after the
  `## Output` marker).
- This bundle contains their **run-level metadata and metrics** instead
  (one record per planned run in `results.json`, one row per run in
  `results.csv`), which is what the Task-025/026 analysis actually used.
- An analyst who needs specific raw outputs can **request selected files
  by run ID** (run IDs are in `results.json`); they can be exported
  individually without shipping the whole directory.
- Prompt/corpus provenance is preserved via SHA-256 hashes
  (`provenance.json`, per-run `prompt_hash`/`source_sha256`/
  `corpus_sha256` in `results.json`) — sufficient to verify that any
  later-provided raw file is the exact generation analysed here.
