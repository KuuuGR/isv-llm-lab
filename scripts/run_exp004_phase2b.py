#!/usr/bin/env python3
"""EXP-004 Phase 2B — source-text-regime kits: deterministic preparation
(SODA Task 029, 2026-09-09).

Phase 2B asks the central EXP-004 follow-up question (recorded in
`docs/research-roadmap.md` §11):

> Does authentic ISV corpus priming generalize to source material whose
> topic/theme is absent from the priming corpus?

To answer it, the project distinguishes THREE source-text regimes (Task
029 §1):

  HIGH-overlap    a new Polish story strongly inspired by the corpus and
                  deliberately sharing themes/motifs/imagery/narrative
                  patterns with it  (this kit: `Iskra i Wieloryb`);
  LOW-overlap     a new Polish story with very little thematic/fabular
                  overlap with the corpus  (`Opowieść o sygnale` and/or
                  `Podkłady` — NOT prepared here);
  UNSEEN DOMAIN   a Polish scientific/educational source from a domain
                  absent from the corpus (future biomedical-physics /
                  electromedicine material — NOT prepared here).

THIS MODULE prepares only the HIGH-overlap condition (`--regime high`).
It never calls an LLM, never collects translations, never modifies raw
experimental data, never modifies the authoritative corpus and never
prepares LOW-overlap or UNSEEN-domain runs. It extends the EXP-004
repeated-generation machinery (`scripts/run_exp004_repeats.py`) by
importing its prompt-rendering constants and helpers — it does not
re-implement or fork them.

HIGH-overlap design (Phase 2B-A, scoped in Task 028 §10-11 and refined in
Task 029):

  - source story: "Iskra i Wieloryb — wersja z oryginalnymi nazwami"
    (author-owned Polish story; classification
    `high_overlap_corpus_inspired`, deliberately NOT an independent
    same-topic control);
  - configurations: the seven representative Phase-2B configurations from
    `docs/research-roadmap.md` §10 (behavioural coverage, not winners);
    the Grok shortlist entry is rendered with its canonical identity
    "Grok 4.5 Fast" (operator-reported, Task 031) — the historical
    roster token 'unknown' is mapped to the canonical 'fast' run-id/file
    token in this forward-looking kit only;
  - per configuration: 3 direct repetitions + 3 primed repetitions, each
    replicate an independent FRESH model session with byte-identical
    prompt files within a (configuration, condition);
  - 7 x 2 x 3 = 42 planned translations (21 direct + 21 primed);
  - direct condition: same Phase-1 direct instruction + the HIGH-overlap
    Polish story, no corpus/dictionary/scaffolding/human guidance;
  - primed condition: the exact authoritative three-register authentic
    corpus `phase2a-authentic-isv` v1 (SHA-256
    aaad28e43935a40313585d77a33bfc788d97e8d69b081f9486af74d52ca1a857,
    never shortened for any model — Gemini interface splits are recorded
    as deviations, not as corpus edits) in msg1, then the translation
    task in msg2.

Run ids (7-field scheme; repeats' 6-field scheme extended by the phase
token so Phase-2B ids can never collide with Task-025 repeat ids):

  <date>__p2b-high__<provider>__<model>__<model_version>__<condition>__<rep>
  condition = direct | primed ; replicate = r01 | r02 | r03

Example: 2026-09-09__p2b-high__anthropic__claude__sonnet-5__primed__r02

Commands:

  freeze-story --src PATH [--version-label v1] [--note TEXT]
           registers a frozen copy of the HIGH-overlap story under
           phase2b/input/versions/ and records provenance in
           phase2b/input/high-overlap-story.meta.json (sha256, bytes,
           title, classification high_overlap_corpus_inspired,
           provenance note). The author's original file at --src is only
           READ, never modified. Existing frozen versions are never
           overwritten or deleted; a new freeze becomes the current
           version. If the story text has not yet been supplied, prepare
           fails loudly below (do not fabricate a source).

  prepare --date YYYY-MM-DD [--force]
           hash-gates the frozen HIGH-overlap story (against
           input/high-overlap-story.meta.json) and the authoritative
           corpus (against aaad28e4…a857), renders the 63 replicate
           prompt files into phase2b/operator-prompts/ (21 direct; 42
           primed msg1+msg2), writes the prompt manifest
           (phase2b/operator-prompts/manifest.json — the committed
           hash-only record), the run plan
           (phase2b/outputs/plan.json; 42 rows) and a human collection
           checklist (phase2b/outputs/collection-checklist.md).
           Deterministic: regenerating with the same --date yields
           byte-identical prompt files, manifest, plan and checklist.
           Nothing is collected here.

The experiment is NOT executed in this task: the 42 HIGH-overlap
translations are the next manual operator step (fresh sessions, external
LLM execution per D-007).
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(ROOT / "src"))

import run_exp004_repeats as rep  # noqa: E402  (imports phase1/phase2a)
import run_exp004_phase1 as p1  # noqa: E402  (canonical Grok identity)

from isv_eval.cli import git_commit  # noqa: E402

EXP = ROOT / "experiments" / "exp004-modelscreen"
PHASE2B = EXP / "phase2b"
INPUT_DIR = PHASE2B / "input"
VERSIONS_DIR = INPUT_DIR / "versions"
OPERATOR_PROMPTS = PHASE2B / "operator-prompts"
OUTPUTS_DIR = PHASE2B / "outputs"

PHASE = "p2b-high"
CONDITIONS = ("direct", "primed")
REPLICATES = ("r01", "r02", "r03")
RUN_ID_FIELDS = ("date", "phase", "provider", "model", "model_version",
                 "condition", "replicate")

SUPPORTED_REGIMES = ("high",)
REGIME_LABELS = {
    "high": "HIGH-overlap",
}
# The frozen HIGH-overlap source file + provenance (gitignored input/).
STORY_META_NAME = "high-overlap-story.meta.json"
STORY_TITLE = "Iskra i Wieloryb — wersja z oryginalnymi nazwami"
STORY_ID = "iskra-wieloryb-original-names"
STORY_CLASSIFICATION = "high_overlap_corpus_inspired"
STORY_MOTIFS = (
    "eternal winter; the Red/Scarlet Spark; Zimorodzice; an inherited "
    "key; a grandfather's legacy; Mogiła Szronu; songs used as narrative "
    "mechanisms; whale imagery; the Heart of the Earth; sacrifice and "
    "transformation; maritime and storm imagery."
)

# ---------------------------------------------------------------------------
# Phase-2B representative shortlist (docs/research-roadmap.md §10 — the
# selection is a behavioural sample, never a "winners" list). Rows are
# resolved from the authoritative Phase-1/Phase-2A roster at prepare time;
# the tuples below pin the selection. GPT-5.6 Luna is pinned to the
# thinking-OFF variant ("Luna" default general-purpose configuration; the
# ON variant stays available only if a later research question needs it).
# ---------------------------------------------------------------------------

SHORTLIST_KEYS = (
    ("google", "gemini-3.6-flash", "extthinkon"),   # 1 strong priming
    ("google", "gemini-3.6-flash", "extthinkoff"),  # 2 strong priming
    ("anthropic", "claude", "sonnet-5"),             # 3 stable high perf.
    ("deepseek", "deepseek-v3-expert", "deepthinkon"),  # 4 clean, high base
    ("alibaba", "qwen-3.8-max", "fast"),             # 5 counterexample
    ("openai", "gpt-5.6-luna", "thinkoff"),          # 6 neutral reference
    ("xai", "grok", "unknown"),  # 7 independent family — canonical
    #                                identity "Grok 4.5 Fast" (operator-
    #                                reported, Tasks 021/026); the roster
    #                                key keeps the historical 'unknown'
    #                                token (Task 031; overlay below)
)

SHORTLIST_ROLE = {
    ("google", "gemini-3.6-flash", "extthinkon"):
        "strong priming effect (large reproduced Δ)",
    ("google", "gemini-3.6-flash", "extthinkoff"):
        "strong priming effect (large reproduced Δ)",
    ("anthropic", "claude", "sonnet-5"):
        "stable high-performance configuration",
    ("deepseek", "deepseek-v3-expert", "deepthinkon"):
        "clean output, high baseline",
    ("alibaba", "qwen-3.8-max", "fast"):
        "small-effect/high-variance counterexample",
    ("openai", "gpt-5.6-luna", "thinkoff"):
        "neutral general-purpose reference",
    ("xai", "grok", "unknown"):
        "independent model-family reference; operator-reported identity",
}

IDENTITY_NOTES = {
    ("xai", "grok", "unknown"):
        "Operator-reported model identity: 'Grok 4.5, built by xAI "
        "(fast)'. Not independently verified (recorded Task 021/026).",
}


def sha256_bytes(data: bytes) -> str:
    return rep.sha256_bytes(data)


def sha256_file(path: Path) -> str:
    return rep.sha256_file(path)


# ---------------------------------------------------------------------------
# Roster resolution (authoritative rows, never reconstructed from names)
# ---------------------------------------------------------------------------

def shortlist_rows() -> list[dict]:
    """The seven representative configurations resolved against the
    authoritative Phase-1/Phase-2A roster (18 primary rows). Fails loudly
    if the roster drifts and a pinned configuration disappears."""
    available = {(r["provider"], r["model"], r["model_version"]): r
                 for r in rep.primary_rows()}
    rows = []
    for key in SHORTLIST_KEYS:
        row = available.get(key)
        if row is None:
            raise RuntimeError(
                f"Phase-2B shortlist configuration {key} missing from the "
                "authoritative Phase-1/Phase-2A roster; refusing to "
                "prepare a Phase-2B kit against a drifted roster")
        row = dict(row)
        # Task 031: forward-looking kits apply the canonical Grok overlay
        # (label "Grok 4.5 Fast", version token 'fast'). The historical
        # roster row keeps 'unknown' (Phase-1/2A/repeats provenance).
        if p1.is_grok_historical(row):
            row = p1.canonical_grok_row(row)
        row["primary"] = True
        row["exploratory"] = False
        row["phase2b_role"] = SHORTLIST_ROLE[key]
        note = IDENTITY_NOTES.get(key)
        if note:
            row["identity_note"] = note
        else:
            row.setdefault("identity_note", None)
        rows.append(row)
    return rows


def run_id_for(date: str, row: dict, condition: str, replicate: str) -> str:
    if condition not in CONDITIONS:
        raise ValueError(f"unknown phase-2B condition {condition!r}")
    if replicate not in REPLICATES:
        raise ValueError(f"unknown replicate {replicate!r}")
    return (f"{date}__{PHASE}__{row['provider']}__{row['model']}__"
            f"{row['model_version']}__{condition}__{replicate}")


def parse_run_id(run_id: str) -> dict:
    parts = run_id.split("__")
    if len(parts) != 7 or parts[1] != PHASE \
            or parts[5] not in CONDITIONS or parts[6] not in REPLICATES:
        raise ValueError(
            f"run id must be <date>__p2b-high__<provider>__<model>__"
            f"<model_version>__direct|primed__r01|r02|r03, got: "
            f"{run_id!r}")
    return dict(zip(RUN_ID_FIELDS, parts))


# ---------------------------------------------------------------------------
# Frozen HIGH-overlap story (input/, gitignored)
# ---------------------------------------------------------------------------

def _story_meta_path() -> Path:
    return INPUT_DIR / STORY_META_NAME


def load_story_meta() -> dict:
    meta_path = _story_meta_path()
    if not meta_path.is_file():
        return {}
    return json.loads(meta_path.read_text(encoding="utf-8"))


def _ensure_story() -> tuple[Path, dict]:
    """Hash-gate the frozen HIGH-overlap story. Fails loudly (never
    fabricates) when the author has not yet supplied the story text."""
    meta = load_story_meta()
    current = meta.get("current_version") if meta else None
    if not meta or not current:
        raise RuntimeError(
            "HIGH-overlap story provenance missing at "
            f"{_story_meta_path()}. The author's story text "
            f"({STORY_TITLE!r}) has not been frozen yet. Register it "
            "with: scripts/run_exp004_phase2b.py freeze-story --src "
            "<author-file> --note '...'  (the author's original file is "
            "only read, never modified). Do NOT fabricate the story.")
    version = meta["versions"][current]
    path = INPUT_DIR / version["file"]
    if not path.is_file():
        raise RuntimeError(
            f"frozen story version {current} missing at {path}; freeze it "
            "again with the freeze-story command")
    actual = sha256_file(path)
    if actual != version["sha256"]:
        raise RuntimeError(
            f"{path} sha256 {actual[:16]}... does not match the recorded "
            f"frozen version {version['sha256'][:16]}...; refusing to use "
            "edited story bytes (fail loudly)")
    return path, version


def _ensure_corpus() -> Path:
    """Hash-gate the authoritative Phase-2A corpus (exact bytes presented
    to models; never shortened, never edited)."""
    if not rep.p2a.CORPUS_FILE.is_file():
        raise RuntimeError(
            f"reference corpus missing at {rep.p2a.CORPUS_FILE}; build it "
            "with scripts/build_phase2a_corpus.py (three-register combined "
            "corpus, SODA Task 020)")
    actual = sha256_file(rep.p2a.CORPUS_FILE)
    if actual != rep.AUTH_CORPUS_SHA256:
        raise RuntimeError(
            f"{rep.p2a.CORPUS_FILE} sha256 {actual[:16]}... does not match "
            f"the recorded corpus "
            f"{rep.AUTH_CORPUS_SHA256[:16]}...; an accidental edit would "
            "break the fixed-corpus fairness invariant (fail loudly, do "
            "not regenerate)")
    return rep.p2a.CORPUS_FILE


# ---------------------------------------------------------------------------
# freeze-story
# ---------------------------------------------------------------------------

def run_freeze_story(src: str, version_label: str | None, note: str) -> int:
    src_path = Path(src).expanduser()
    if not src_path.is_file():
        print(f"error: source story file not found: {src_path}",
              file=sys.stderr)
        return 2
    label = version_label or "v1"
    if not re.fullmatch(r"v\d+", label):
        print("error: --version-label must look like v1, v2, ...",
              file=sys.stderr)
        return 2
    if src_path.resolve() == (INPUT_DIR / "versions").resolve() \
            or label == "v0":
        print("error: refusing to freeze from inside the frozen store",
              file=sys.stderr)
        return 2
    data = src_path.read_bytes()
    digest = sha256_bytes(data)
    meta = load_story_meta()
    versions = meta.get("versions", {}) if meta else {}
    if label in versions:
        print(f"error: version {label} already exists (versions are "
              "immutable); use a new --version-label", file=sys.stderr)
        return 2
    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    VERSIONS_DIR.mkdir(parents=True, exist_ok=True)
    out_name = f"{STORY_ID}-{label}.txt"
    out_path = VERSIONS_DIR / out_name
    out_path.write_bytes(data)  # frozen bytes; never overwritten later
    versions[label] = {
        "version": label,
        "file": f"versions/{out_name}",
        "sha256": digest,
        "bytes": len(data),
        "title": STORY_TITLE,
        "story_id": STORY_ID,
        "classification": STORY_CLASSIFICATION,
        "source_file_read_only": str(src_path),
        "note": note or "",
        "frozen_by": "scripts/run_exp004_phase2b.py freeze-story",
        "frozen_date": "2026-09-09",
    }
    meta = {
        "story_id": STORY_ID,
        "title": STORY_TITLE,
        "classification": STORY_CLASSIFICATION,
        "regime": "high",
        "classification_note": (
            "HIGH-overlap: this Polish story is deliberately corpus-"
            "inspired and shares substantial themes/motifs with the "
            "authentic corpus (e.g. eternal winter; the Red/Scarlet "
            "Spark; Zimorodzice; an inherited key; a grandfather's "
            "legacy; Mogiła Szronu; songs used as narrative mechanisms; "
            "whale imagery; the Heart of the Earth; sacrifice and "
            "transformation; maritime and storm imagery). It is an "
            "experimental input for the HIGH-overlap corpus-priming "
            "test, NOT an independent same-topic control and NOT part "
            "of the corpus."),
        "current_version": label,
        "versions": versions,
    }
    _story_meta_path().write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[freeze-story] {STORY_TITLE!r} frozen as {label}")
    print(f"  file {_rel_or_abs(out_path)}")
    print(f"  sha256 {digest}  bytes {len(data)}")
    print("  (the author's original file was only read, never modified)")
    return 0


# ---------------------------------------------------------------------------
# prompt rendering (reuses the EXP-004 repeated-generation renderers;
# only the operator-facing header is Phase-2B specific — the model-visible
# instruction regions stay byte-identical to Phase 1 / Phase 2A / repeats)
# ---------------------------------------------------------------------------

def _operator_block(row: dict, kind: str) -> list[str]:
    """The '> ' operator instructions at the top, mirroring the repeats
    kit (direct: single message; msg1/msg2: two-message primed flow)."""
    if kind == "direct":
        return [
            f"> COPY THIS ENTIRE FILE INTO {row['interface']} in a NEW, "
            "FRESH session.",
            "> Do not modify anything. Run this message exactly once in "
            "that session;",
            "> do not chain it with previous messages and do not send "
            "follow-up messages.",
            "> Save the model's complete reply byte-for-byte and hand it "
            "to the collect step.",
        ]
    if kind == "msg1":
        return [
            f"> COPY THIS ENTIRE FILE INTO {row['interface']} as the "
            "FIRST message of a NEW, FRESH session.",
            "> Do not modify anything. Send message 1, WAIT for the "
            "model's short",
            "> confirmation, THEN send message 2 (the file ending "
            '"-msg2") in the',
            "> SAME session.",
        ]
    return [
        f"> COPY THIS ENTIRE FILE INTO {row['interface']} as the SECOND "
        "message of the",
        "> SAME session as message 1 (send it after the model's short "
        "confirmation).",
        "> Do not modify anything. Save the model's complete reply (the "
        "translation) byte-for-byte.",
    ]


def _identity_lines(row: dict) -> list[str]:
    """Optional operator-metadata identity lines (Task 031). Only rows with
    a recorded identity note (currently: the canonical Grok configuration)
    emit lines; never part of the model-visible instruction region."""
    note = row.get("identity_note")
    if not note:
        return []
    return [f"Identity note: {note}"]


def _p2b_header(row: dict, kind: str, task_line: str,
                condition_line: str) -> list[str]:
    """Phase-2B operator metadata block (above the first '---'). Never
    appears in the model-visible instruction region."""
    setting = row["generation_parameters"]
    return [
        f"# EXP-004 Phase 2B — HIGH-overlap test — {row['label']}",
        "",
        *_operator_block(row, kind),
        "",
        "---",
        "",
        "Experiment ID: EXP-004 (Phase 2B, HIGH-overlap test)",
        task_line,
        f"Target model: {row['label']}",
        f"Provider / interface: {row['provider']} / {row['interface']}",
        f"Model version / settings: {row['model_version']} ({setting})",
        *_identity_lines(row),
        f"Representative role: {row['phase2b_role']}",
        f"Source regime: HIGH-overlap (story: {STORY_TITLE})",
        condition_line,
        "",
        "---",
        "",
    ]


def render_direct_prompt(row: dict, source_text: str) -> str:
    """Direct Phase-2B prompt: Phase-2B operator header + the byte-identical
    Phase-1/Phase-2A direct instruction body (base instruction + story)."""
    lines = _p2b_header(
        row, "direct", "Task: direct translation (single message)",
        "Condition: direct translation — no reference material")
    lines.append(
        rep._base_instruction_text(source_text).rstrip("\n") + "\n")
    return "\n".join(lines)


def render_primed_msg1(row: dict, corpus_text: str) -> str:
    """Primed message 1: Phase-2B operator header + the byte-identical
    Phase-2A study instruction + the full authoritative corpus."""
    lines = _p2b_header(
        row, "msg1",
        "Task: translation with reference texts (message 1 of 2)",
        "Condition: reference texts only — no translation in this "
        "message")
    lines += [
        rep.PRIMED_MSG1_STUDY_TEXT,
        "",
        rep.PRIMED_MSG1_HEADING,
        "",
        corpus_text.rstrip("\n"),
    ]
    return "\n".join(lines) + "\n"


def render_primed_msg2(row: dict, source_text: str) -> str:
    """Primed message 2: Phase-2B operator header + the byte-identical
    Phase-2A translation task (intro sentence + base instruction)."""
    lines = _p2b_header(
        row, "msg2",
        "Task: translation with reference texts (message 2 of 2)",
        "Condition: primed — translation generated after the reference "
        "texts in this session")
    lines += [
        rep.PRIMED_MSG2_INTRO,
        "",
        rep._base_instruction_text(source_text).rstrip("\n") + "\n",
    ]
    return "\n".join(lines)


def prompt_filenames(row: dict, condition: str, replicate: str,
                     nn: int) -> list[str]:
    base = f"{nn:02d}-{row['model']}-{row['model_version']}"
    if condition == "direct":
        return [f"high-direct-{base}-{replicate}.md"]
    return [f"high-primed-{base}-{replicate}-msg1.md",
            f"high-primed-{base}-{replicate}-msg2.md"]


# ---------------------------------------------------------------------------
# prepare
# ---------------------------------------------------------------------------

def _ordered_runs(rows: list[dict]) -> list[tuple[dict, int, str, str]]:
    """Block ordering per configuration: r01 direct+primed, r02, r03
    (replicates are blocks, matching the Task-025 convention)."""
    out = []
    for nn, row in enumerate(rows, start=1):
        for rep in REPLICATES:
            for cond in CONDITIONS:
                out.append((row, nn, cond, rep))
    return out


def _write_checklist(plan: dict, date: str) -> None:
    lines = [
        "# EXP-004 Phase 2B — HIGH-overlap test — collection checklist "
        f"(prepared {date})",
        "",
        "Mark each row after collecting. Every replicate is a FRESH, "
        "independent session — never chain messages, never reuse a "
        "session, never tell the model this is a repeat. The three "
        "replicate files of a (configuration, condition) are byte-"
        "identical by design; the run id / file name carries the "
        "replicate tag.",
        "",
        f"Source regime: HIGH-overlap — {STORY_TITLE} "
        f"(classification {STORY_CLASSIFICATION}).",
        f"Corpus: phase2a-authentic-isv v1, sha256 "
        f"{plan['corpus']['sha256']} (never shortened for any model).",
        "",
        "Checklist: for every usable output, register the raw reply "
        "(msg2-style: append the raw reply in its prompt file after the "
        "closing '## Output' marker, or save the full session and "
        "collect it), then verify + evaluate with the EXP-004 "
        "machinery.",
        "",
    ]
    last_label = None
    for r in plan["runs"]:
        if r["label"] != last_label:
            if last_label is not None:
                lines.append("")
            lines.append(f"### {r['label']} — {r['phase2b_role']}")
            lines.append("")
            last_label = r["label"]
        files = "`, `".join(r["prompt_files"])
        lines.append(f"- [ ] {r['run_id']}  files `{files}`")
    (OUTPUTS_DIR / "collection-checklist.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8")


def run_prepare(date: str, force: bool = False) -> int:
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date or ""):
        print("error: --date YYYY-MM-DD is required (run ids carry the "
              "planned generation date)", file=sys.stderr)
        return 2
    story_path, story_version = _ensure_story()
    corpus_path = _ensure_corpus()
    source_text = story_path.read_text(encoding="utf-8")
    corpus_text = corpus_path.read_text(encoding="utf-8")
    source_sha = sha256_bytes(source_text.encode("utf-8"))
    corpus_sha = sha256_bytes(corpus_text.encode("utf-8"))
    if source_sha != story_version["sha256"]:
        print("error: story sha mismatch — refusing to proceed",
              file=sys.stderr)
        return 2
    if corpus_sha != rep.AUTH_CORPUS_SHA256:
        print("error: corpus sha mismatch — refusing to proceed",
              file=sys.stderr)
        return 2

    plan_path = OUTPUTS_DIR / "plan.json"
    if plan_path.is_file() and not force:
        print(f"error: {plan_path} already exists; use --force to rewrite "
              "(regenerating is safe ONLY before any collection; after "
              "collection it invalidates recorded run ids)",
              file=sys.stderr)
        return 2

    OPERATOR_PROMPTS.mkdir(parents=True, exist_ok=True)
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

    rows = shortlist_rows()
    runs: list[dict] = []
    files: list[dict] = []
    for row, nn, cond, rep_ in _ordered_runs(rows):
        if cond == "direct":
            rendered = [render_direct_prompt(row, source_text)]
        else:
            rendered = [render_primed_msg1(row, corpus_text),
                        render_primed_msg2(row, source_text)]
        names = prompt_filenames(row, cond, rep_, nn)
        run_id = run_id_for(date, row, cond, rep_)
        run_files: list[str] = []
        for fname, text in zip(names, rendered):
            path = OPERATOR_PROMPTS / fname
            prompt_sha = sha256_bytes(text.encode("utf-8"))
            if path.is_file() and not force:
                if sha256_bytes(path.read_bytes()) != prompt_sha:
                    print(f"error: {path} exists with different content; "
                          "--force to overwrite (safe only before "
                          "collection)", file=sys.stderr)
                    return 2
            path.write_text(text, encoding="utf-8")
            run_files.append(fname)
            message = None if cond == "direct" else (
                1 if fname.endswith("-msg1.md") else 2)
            files.append({
                "file": fname, "run_id": run_id, "condition": cond,
                "replicate": rep_, "message": message,
                "regime": "high",
                "prompt_sha256": prompt_sha,
                "bytes": len(text.encode("utf-8")),
            })
        translation_sha = sha256_bytes(rendered[-1].encode("utf-8"))
        runs.append({
            "run_id": run_id,
            "phase": PHASE,
            "regime": "high",
            "condition": cond,
            "replicate": rep_,
            "provider": row["provider"], "model": row["model"],
            "model_version": row["model_version"], "label": row["label"],
            "phase2b_role": row["phase2b_role"],
            "interface": row["interface"],
            "generation_parameters": row["generation_parameters"],
            "prompt_files": run_files,
            "translation_prompt_sha256": translation_sha,
            "source_sha256": source_sha,
            "source_story_id": STORY_ID,
            "source_classification": STORY_CLASSIFICATION,
            "corpus_sha256": corpus_sha if cond == "primed" else None,
            "identity_note": row.get("identity_note"),
            "status": "pending_manual_collection",
        })

    counts = {
        "representative_configurations": len(rows),
        "conditions": 2,
        "replicates_per_condition": len(REPLICATES),
        "runs_per_configuration_per_condition": len(REPLICATES),
        "direct_runs": len(rows) * len(REPLICATES),
        "primed_runs": len(rows) * len(REPLICATES),
        "total_runs": len(runs),
        "prompt_files": len(files),
    }
    plan = {
        "experiment_id": "exp004",
        "artifact": "phase2b_high_plan",
        "phase": PHASE,
        "regime": "high",
        "date": date,
        "generator": "scripts/run_exp004_phase2b.py prepare",
        "generator_commit": git_commit(),
        "research_question": (
            "HIGH-overlap test (Phase 2B-A): when the target Polish "
            "story is strongly thematically/motivically aligned with the "
            "authentic corpus (H-HIGH), does corpus priming produce a "
            "larger improvement in resource-supported Interslavic "
            "generation? Descriptive comparison with LOW-overlap and "
            "UNSEEN-domain tests later; hypothesis, not a result."),
        "source": {"story_id": STORY_ID,
                   "title": STORY_TITLE,
                   "classification": STORY_CLASSIFICATION,
                   "file": _rel_or_abs(story_path),
                   "version": story_version["version"],
                   "sha256": source_sha,
                   "bytes": len(source_text.encode("utf-8"))},
        "corpus": {"id": "phase2a-authentic-isv", "version": "v1",
                   "file": _rel_or_abs(corpus_path),
                   "sha256": corpus_sha,
                   "bytes": len(corpus_text.encode("utf-8"))},
        "conditions": list(CONDITIONS),
        "replicates": list(REPLICATES),
        "counts": counts,
        "note": (
            "HIGH-overlap corpus-priming test (SODA Task 029). The "
            "source story is deliberately corpus-inspired "
            "(high_overlap_corpus_inspired) — it is NOT an independent "
            "same-topic control and NOT part of the corpus. Replicates "
            "are independent fresh-session generations; replicate prompt "
            "file contents are byte-identical within a (configuration, "
            "condition) by design. Direct prompts contain no corpus "
            "material; primed prompts embed the complete authoritative "
            "corpus (never shortened per model). No LLM was called by "
            "this script; the 42 translations are the next manual "
            "operator step."),
        "runs": runs,
    }
    plan_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2),
                         encoding="utf-8")

    manifest = {
        "artifact": "phase2b_high_prompt_manifest",
        "experiment_id": "exp004",
        "phase": PHASE,
        "regime": "high",
        "date": date,
        "generator": "scripts/run_exp004_phase2b.py prepare",
        "generator_commit": git_commit(),
        "source": dict(plan["source"]),
        "corpus": dict(plan["corpus"]),
        "counts": dict(counts),
        "note": ("Prompt hashes + run enumeration only (no story text, "
                 "no corpus, no model output). Files under "
                 "operator-prompts/ are gitignored; this manifest is the "
                 "committed record."),
        "files": sorted(files, key=lambda f: f["file"]),
    }
    (OPERATOR_PROMPTS / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8")

    _write_checklist(plan, date)
    print(f"[prepare] {date}: {len(runs)} HIGH-overlap runs "
          f"({counts['direct_runs']} direct + "
          f"{counts['primed_runs']} primed); {len(files)} prompt files")
    print(f"  story sha256 {source_sha}  "
          f"({STORY_ID} {story_version['version']}, "
          f"{STORY_CLASSIFICATION})")
    print(f"  corpus sha256 {corpus_sha}  (phase2a-authentic-isv v1)")
    return 0


def _rel_or_abs(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="EXP-004 Phase 2B — HIGH-overlap kit preparation "
                    "(deterministic; never calls an LLM)")
    sub = parser.add_subparsers(dest="command")

    p_freeze = sub.add_parser(
        "freeze-story",
        help="register a frozen copy of the HIGH-overlap story")
    p_freeze.add_argument("--src", required=True,
                          help="author's original story file (read-only)")
    p_freeze.add_argument("--version-label", default=None)
    p_freeze.add_argument("--note", default="")

    p_prep = sub.add_parser(
        "prepare", help="prepare the 42-run HIGH-overlap kit")
    p_prep.add_argument("--date", required=True, metavar="YYYY-MM-DD")
    p_prep.add_argument("--force", action="store_true",
                        help="rewrite existing plan/prompts (safe only "
                             "before any collection)")

    args = parser.parse_args(argv)
    if args.command == "freeze-story":
        return run_freeze_story(args.src, args.version_label, args.note)
    if args.command == "prepare":
        return run_prepare(args.date, args.force)
    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
