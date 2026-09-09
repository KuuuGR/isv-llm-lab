# EXP-004 — Canonical Grok configuration identity (Task 031)

**Authoritative note.** Any other file that needs to say who "Grok" is in
the current EXP-004 experimental line should reference this document (and
the machine-readable map next to it, `grok-identity-map.json`) instead of
repeating the full statement.

## Canonical identity (current experimental line)

- **Canonical configuration label:** `Grok 4.5 Fast`
  (use in filenames, run-id tokens where the convention permits, tables,
  roster entries, summaries, experiment headings).
- **Fuller operator-observed identity:** `Grok 4.5, built by xAI (fast)`
  (use in metadata/provenance notes).
- **Identity evidence:** `operator_reported` / operator-observed. This is
  the identity the operator recorded in the run metadata (Tasks 021/026
  operator-header edits and identity notes). It is **not** an
  independently verified model identity (provider metadata is not
  machine-verifiable in these records) and is never upgraded to one.
- **Provider / model / version tokens:** provider `xai`, model `grok`,
  canonical version token `fast` → canonical configuration id
  `xai__grok__fast`.

## Historical transparency

The Phase-1 roster row 08 was recorded with version token `unknown` when
collected (Task 018, genuinely unannotated — the D-018 `unknown`
fallback). Runs and files generated before the operator-observed identity
existed therefore carry `…__grok__unknown__…` / `*-grok-unknown-*`
identifiers. **Task 031 does not rewrite those identifiers**: historical
run ids, prompt-file names, manifests, raw outputs and genuinely-recorded
reports keep the `unknown` tokens as historical provenance. Every such
identifier maps canonically to `Grok 4.5 Fast`:

- historical configuration id `xai__grok__unknown` →
  canonical alias id `xai__grok__fast`;
- historical run-id token `__xai__grok__unknown__` →
  alias `__xai__grok__fast__` (function `grok_run_id_alias` in
  `scripts/run_exp004_phase1.py`; full per-run mapping in
  `grok-identity-map.json`).

Forward-looking kits (Phase-2B HIGH, and future LOW/UNSEEN kits prepared
by the same machinery) are **born canonical**: the generator applies the
canonical overlay (`canonical_grok_row` in `scripts/run_exp004_phase1.py`)
so new run ids, prompt files and headers read `grok…fast` / "Grok 4.5
Fast" from day one.

## Historical exception: no Grok Build run exists in these records

The task brief mentioned one early historical Grok **Build**
configuration that must stay identifiable as Build. **Repository evidence
contains no Grok Build run**: filenames, manifests, plans, rosters,
reports, documentation and git history were searched
(`build`/`beta`/`Grok Build` variants). The single early Grok condition —
EXP-001/EXP-002 (August 2026), run `exp002__2026-08-31__unknown__grok__unknown`
— was genuinely unannotated at the time and is preserved exactly as
recorded (`unknown`). It predates the operator-observed identity and is
**not** part of the current EXP-004 experimental line, so it is not
back-ported to Fast. If a Grok Build session exists outside these records,
it is not part of EXP-004 and is untouched by Task 031.

## Per-phase status

| Phase | Grok configuration | Identity status |
|---|---|---|
| Phase 1 (row 08, direct baseline) | `Grok 4.5 Fast` | operator-reported (recorded Tasks 021/026 for the row-08 line); run id/file keep historical `unknown` tokens with canonical alias |
| Phase 2A (primed; ctl = Phase-1 baseline) | `Grok 4.5 Fast` | operator-reported (Task-021 msg1 header edit); identifiers historical |
| Phase repeat (Task 025/026, 6 runs) | `Grok 4.5 Fast` | operator-reported (Task-026 header edits in all 9 files); identifiers historical |
| Phase 2B / HIGH-overlap (2026-09-09 kit) | `Grok 4.5 Fast` | operator-reported; kit regenerated with canonical `fast` run ids/files/headers (never collected) |
| Future LOW / UNSEEN | `Grok 4.5 Fast` (default) | operator-reported; to be prepared canonically by the generator unless the research lead specifies another Grok configuration |
| EXP-001/EXP-002 (August 2026) | recorded `unknown` | genuinely unknown — historical, preserved |

## Where the canonical overlay lives

- `scripts/run_exp004_phase1.py` — authoritative constants + helpers
  (`GROK_CANONICAL_*`, `is_grok_historical`, `canonical_grok_row`,
  `grok_run_id_alias`).
- `scripts/run_exp004_phase2b.py` — Phase-2B (and future regime) kits
  apply the overlay at `shortlist_rows()`; prompt headers render the
  identity note.
- `scripts/analyze_exp004_repeats.py` and
  `scripts/build_assistant_research_bundle.py` — display-layer
  canonicalization for analysis figures/dataset and the assistant
  research bundle (additive canonical fields; recorded values untouched).

## Audit table (run level)

| artifact/run | old identity | canonical identity | evidence | action |
|---|---|---|---|---|
| `2026-09-06__xai__grok__unknown__direct` (Phase 1) | `Grok` / `unknown` | Grok 4.5 Fast | row-08 line; operator identity recorded Tasks 021/026 | canonicalize rendered identity; alias `…__grok__fast__direct` |
| `2026-09-07__xai__grok__unknown__p2a-ctl` (Phase 2A ctl) | `Grok` / `unknown` | Grok 4.5 Fast | ctl = Phase-1 baseline slot | canonicalize rendered identity; alias |
| `2026-09-07__xai__grok__unknown__p2a-primed` (Phase 2A) | `Grok` / `unknown` | Grok 4.5 Fast | Task-021 msg1 header edit ("Grok 4.5, built by xAI, fast") | canonicalize rendered identity; alias |
| `2026-09-08__xai__grok__unknown__{direct,primed}__r01..r03` (repeats, 6 runs) | `Grok` / `unknown (unknown)` | Grok 4.5 Fast | Task-026 header edits in all 9 files + audit deviation `grok-identity-header-edit` | canonicalize rendered identity; aliases `…__grok__fast__…` |
| `2026-09-09__p2b-high__xai__grok__unknown__…` (Phase 2B, 6 old ids) | `Grok` / `unknown` | Grok 4.5 Fast | Task-030 kit, never collected | regenerated → canonical `…__grok__fast__…` ids/files |
| `2026-09-09__p2b-high__xai__grok__fast__{direct,primed}__r01..r03` (Phase 2B, 6 new ids) | — | Grok 4.5 Fast | canonical kit regeneration; identity note in headers | canonicalize |
| `exp002__2026-08-31__unknown__grok__unknown` (EXP-001/002 era) | `unknown` | preserved `unknown` | genuinely unannotated at the time; outside the current line | preserve (no Build evidence) |

Machine-readable statuses: `unknown_but_reconcilable` (Phase 1/2A),
`grok_4_5_fast_operator_reported` (repeats + new Phase-2B ids),
`superseded_by_regeneration` (old Phase-2B ids), `genuinely_unknown`
(EXP-001/002). No `historical_build` and no `conflicting_metadata` rows
remain.
