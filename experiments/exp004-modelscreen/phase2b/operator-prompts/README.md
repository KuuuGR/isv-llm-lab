# Phase 2B HIGH-overlap — operator prompts (gitignored except this README + manifests)

Generated deterministically by
`scripts/run_exp004_phase2b.py prepare --date YYYY-MM-DD`
(and `prepare --regime low --date YYYY-MM-DD` for LOW).

## HIGH (Task 030, 2026-09-09)

**Status: generated** for the frozen v1 HIGH story —
63 prompt files exist locally (21 direct; 42 primed msg1+msg2) and
`manifest.json` (committed) records their SHA-256/byte counts:

- 21 direct prompt files `high-direct-<nn>-<model>-<version>-rNN.md`;
- 42 primed prompt files `high-primed-<nn>-<model>-<version>-rNN-msg1.md`
  (corpus message) + `...-msg2.md` (translation task);
- `manifest.json` — committed hash-only record (run enumeration,
  per-file SHA-256 + byte counts; never story/corpus/output text).

## LOW (2026-09-15)

**Status: generated and validated** for frozen `podklady` v1 —

- 21 direct `low-direct-…-rNN.md`;
- 42 primed `low-primed-…-rNN-msg1.md` + `…-msg2.md`;
- `manifest-low.json` — committed hash-only record;
- plan/checklist: `../outputs/low/`.

The three replicate files of a (configuration, condition) are
byte-identical by design (fresh sessions; only the run id / file name
carries the replicate tag). Prompt file contents embed the copyrighted
story and the local-only corpus, so the files themselves stay local.
No model output is part of the LOW kit.
