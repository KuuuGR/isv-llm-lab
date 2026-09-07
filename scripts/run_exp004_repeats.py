#!/usr/bin/env python3
"""EXP-004 Phase repeat (controlled repeated generation) — run orchestrator
(SODA Task 025, 2026-09-08).

Phase repeat measures RUN-TO-RUN STOCHASTIC VARIATION and makes the
EXP-004 Phase 1 → Phase 2A comparison scientifically stronger. Central
question:

> When exactly the same model/configuration is given exactly the same
> translation task, how much does the measured Interslavic resource
> coverage vary between independent generations, and is the observed
> Phase-2A corpus-priming shift larger than that variation?

Design (see experiments/exp004-modelscreen/repeats/README.md and DESIGN
§14): for every original-18 usable configuration (GLM 4.5 excluded because
its Phase-1 intake failed) prepare, per condition:

  Condition direct — 3 independent fresh-session generations of the same
  Polish source story using the same direct-translation prompt as
  Phase 1 (base instruction + source, byte-identical linguistic content,
  no corpus/scaffold/dictionary/examples);

  Condition primed — 3 independent fresh-session generations using the
  same Phase-2A protocol: msg1 = the authoritative three-register
  authentic corpus `phase2a-authentic-isv` v1 (byte-identical, SHA-256
  pinned) with the same study-as-reference instruction; msg2 = the same
  Polish source story and translation instruction; translation generated
  after the corpus has been presented in the same fresh session.

Primary population: exactly the 18 original configurations
(18 × 2 conditions × 3 replicates = 108 planned runs). The two
exploratory Dola 3.8 configurations (Fast/Pro) get the same 3×2 design
prepared (12 additional runs) but stay `exploratory: true` and are NEVER
merged into the primary n=18 statistics; the research lead decides
whether to execute them.

Independence discipline: each replicate is a fresh independent model
session; never continue one generation into another replicate, never feed
a previous translation into the next session, never ask the model to
improve or evaluate, never reuse conversation history, never tell the
model this is a repeat. The three replicate prompt FILES of one
(configuration, condition) are byte-identical BY DESIGN (the model must
not be able to tell replicates apart); only the file name / run id carry
the replicate tag (r01/r02/r03). Replicate labels are replication blocks,
NOT matched linguistic samples.

Run ids (canonical 5-field scheme extended by the replicate field):

  <date>__<provider>__<model>__<model_version>__<condition>__<replicate>
  condition = direct | primed ; replicate = r01 | r02 | r03

Example: 2026-09-08__anthropic__claude__sonnet-5__primed__r02. The extra
sixth field and the distinct condition tokens keep repeat ids
unambiguously different from Phase-1 (…__direct, 5 fields) and Phase-2A
(…__p2a-ctl|p2a-primed, 5 fields) run ids.

LLM execution is EXTERNAL (D-007): this script only prepares runs,
registers externally produced outputs byte-for-byte (D-035), verifies
them (Phase-1 structural completeness gate, L-027, plus the Phase-2A
contamination controls where a session transcript is supplied), evaluates
them with the Task 008 evaluator (unmodified) plus the Task 015
orthographic audit, and reports status/roster. It never calls an LLM and
never fabricates outputs. The Task-025 statistical analysis lives in
scripts/analyze_exp004_repeats.py (run only after collection).

Commands:

  prepare  --date YYYY-MM-DD [--force]
           hash-gate the authoritative source story and corpus (fail
           loudly on any byte drift), render the replicate prompt files
           into repeats/operator-prompts/ (direct: one file per run;
           primed: msg1+msg2 per run — content identical across r01..r03),
           write the prompt manifest
           (repeats/operator-prompts/manifest.json, hashes + run
           enumeration), the run plan (repeats/outputs/plan.json; 108
           primary + 12 exploratory rows, block-ordered r01 direct+primed,
           r02, r03) and a human collection checklist
           (repeats/outputs/collection-checklist.md). Deterministic:
           regenerating with the same --date yields byte-identical prompt
           files, manifest, plan, checklist. Nothing is collected here.

  collect-session  --run <run_id> --session <path>
           [--generation-date DATE] [--status …] [--access-verdict …]
           [--access-note …] [--interface-settings TEXT] [--note …]
           register the model reply embedded in an author session file
           (prompt + raw reply in one markdown file; or the canonical
           prompt file itself with the reply appended after its closing
           '## Output' marker — msg2-style, Tasks 021/023 shape). For a
           session whose file IS the run's canonical prompt file the
           prompt part through the '## Output' marker is validated
           byte-identical to the canonical prompt (msg2-style record);
           otherwise the session must carry the canonical instruction body
           (direct: exactly the direct body; primed: msg2 body) and the
           condition contamination controls are applied: primed sessions
           must contain all three corpus-register fingerprints BEFORE the
           translation instruction; direct sessions must contain NONE of
           them. The reply is extracted after the closing '## Output'
           marker and stored byte-for-byte as outputs/<run>/output.txt.
           The session file is never modified; its SHA-256 is recorded.

  collect-msg2  --run <run_id>
           [same option set as collect-session, except --session]
           register a primed run whose collected record is the canonical
           operator-prompts *-msg2.md file with the raw reply appended
           after its '## Output' marker (the Phase-2A/Task-021 record
           shape). Reply sliced deterministically at the marker, stored
           byte-for-byte. No machine same-session corpus-before-
           translation proof is claimed for this record shape (documented
           provenance mode, D-048).

  verify  [--run <run_id> | --all] [--size-floor BYTES]
           integrity checks (output hash vs meta, plan consistency) plus
           the structural completeness gate (L-027): non-empty output,
           byte size >= floor (default 0.60 × source bytes), head sanity,
           ISV-tolerant story-name stems, end marker KONIEC/KONEC/KONĖC.
           Verdict complete/partial/failed preserved as data (D-035);
           partial/failed runs are never silently deleted or rerun.

  evaluate  --run <run_id> [--force]
           run the gate if no intake.json exists, refuse for verdict
           'failed' (unless --force), then the Task 008 evaluator
           (isv-eval, unmodified) and the orthographic audit; write
           evaluation.json + orthography.json + evaluation.md.
           No composite score.

  status    show planned / collected / verified / evaluated / usable per
            run (primary vs exploratory separated).

  roster    join plan + meta + intake + evaluation + orthography into
            repeats/outputs/roster.json and roster.md (per-dimension
            only, no ranking, no composite).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(ROOT / "src"))

import run_exp004_phase1 as p1  # noqa: E402
import run_exp004_phase2a as p2a  # noqa: E402  (imports p1 itself)

from isv_eval.cli import git_commit  # noqa: E402
from isv_eval.orthography import scan_file  # noqa: E402

EXP = ROOT / "experiments" / "exp004-modelscreen"
REPEATS = EXP / "repeats"
OPERATOR_PROMPTS = REPEATS / "operator-prompts"
OUTPUTS_DIR = REPEATS / "outputs"
SESSION_DIR = REPEATS / "collected-sessions"

PHASE = "repeat"
CONDITIONS = ("direct", "primed")
REPLICATES = ("r01", "r02", "r03")
REPLICATES_PER_CONDITION = len(REPLICATES)  # 3
RUN_ID_FIELDS = ("date", "provider", "model", "model_version", "condition",
                 "replicate")

# Source story + corpus are the AUTHORITATIVE bytes pinned by Phase 1/2A.
SOURCE_SHA256 = p2a.SOURCE_SHA256            # = p1.EXP003_SOURCE_SHA256
CORPUS_ID = p2a.CORPUS_ID                    # phase2a-authentic-isv
CORPUS_VERSION = p2a.CORPUS_VERSION          # v1
AUTH_CORPUS_SHA256 = p2a.AUTH_CORPUS_SHA256  # aaad28e4…a857
CORPUS_ANCHORS = p2a.CORPUS_ANCHORS
TRANSLATION_START = p2a.TRANSLATION_START

# Model-visible wording constants — copied byte-for-byte from the
# authoritative Phase-2A prompt kit (run_exp004_phase2a.py rendering) so
# the primed instruction regions stay identical to Phase 2A. The block
# below is the exact text between "Below are three authentic texts" and
# "## Reference texts" in _render_primed_msg1 (checked by tests).
PRIMED_MSG1_STUDY_TEXT = (
    "Below are three authentic texts written in Medžuslovjansky "
    "(Interslavic) by experienced users of the language. Treat them "
    "as REFERENCE MATERIAL ONLY.\n"
    "\n"
    "The three texts show Medžuslovjansky used in three different "
    "registers:\n"
    "- REGISTER 1 — literary / narrative: a prose excerpt with "
    "narration and dialogue (\"Tuta historija\");\n"
    "- REGISTER 2 — artistic / poetic: lyrics of songs and sea "
    "shanties (album \"Ahoj, Slovjani!\"). Songs are poetry: they may "
    "contain unusual or stylised forms chosen deliberately for rhyme, "
    "rhythm, metre or musical effect, and should NOT automatically be "
    "treated as grammatical templates;\n"
    "- REGISTER 3 — informative / encyclopedic: a Wikipedia article "
    "(\"Sadovničstvo\") written in ordinary expository prose.\n"
    "\n"
    "Study the texts carefully as language reference material. Pay "
    "attention to:\n"
    "- vocabulary and word formation;\n"
    "- morphology (noun and adjective endings, verb forms, pronouns, "
    "cases);\n"
    "- syntax and word order;\n"
    "- phraseology and natural collocations;\n"
    "- orthography and spelling conventions;\n"
    "- stylistic patterns in each register.\n"
    "\n"
    "The three sections demonstrate that Medžuslovjansky is used "
    "across different registers of real communication. Do NOT "
    "translate, summarize, reproduce, modify or continue these texts.\n"
    "Do NOT imitate their particular sentences. Do NOT answer "
    "questions about their content. Do NOT reproduce the songs or "
    "imitate their subject matter. Do NOT produce any Medžuslovjansky "
    "text in this message.\n"
    "\n"
    "Retain the useful language information — vocabulary, morphology, "
    "syntax, phraseology, orthography and style — for the translation "
    "task in the next message of this same conversation. If you have "
    "understood and are ready, reply with a short confirmation only "
    "(one or two sentences). No translation."
)
PRIMED_MSG1_HEADING = "## Reference texts (authentic Medžuslovjansky, " \
                      "three registers)"
# The transition sentence that starts the primed translation task (msg2).
PRIMED_MSG2_INTRO = (
    "Using the authentic Medžuslovjansky text from the previous message "
    "of this conversation as a language reference, translate the Polish "
    "text below into Medžuslovjansky."
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


# ---------------------------------------------------------------------------
# Roster rows (authoritative — never reconstructed from filenames)
# ---------------------------------------------------------------------------

def primary_rows() -> list[dict]:
    """Exactly the 18 original EXP-004 usable configurations (Phase-2A
    roster = Phase-1 usable roster minus the failed GLM run)."""
    rows = p2a.ROSTER  # 18 (module raises if Phase-1 roster changed)
    return [dict(row) for row in rows]


def exploratory_rows() -> list[dict]:
    """The two exploratory Dola 3.8 configurations (Fast/Pro). Never merged
    into the primary population."""
    return [dict(row) for row in p1.DIRECT_EXPLORATORY_ROWS]


def config_number(row: dict) -> int:
    """Stable per-configuration number for filenames/ordering: the
    Phase-1 roster number (1..19, GLM 11 absent) for primary rows and the
    author's run number (20/21) for the exploratory Dola rows."""
    if row.get("exploratory"):
        return int(row["run_number"])
    return _phase1_number_lookup(row)


def _phase1_number_lookup(row: dict) -> int:
    for i, r in enumerate(p1.ROSTER):
        if (r["provider"] == row["provider"] and r["model"] == row["model"]
                and r["model_version"] == row["model_version"]):
            return i + 1
    raise ValueError(f"row not in the Phase-1 roster: {row.get('label')}")


def run_id_for(date: str, row: dict, condition: str, replicate: str) -> str:
    if condition not in CONDITIONS:
        raise ValueError(f"unknown repeat condition {condition!r}")
    if replicate not in REPLICATES:
        raise ValueError(f"unknown replicate {replicate!r}")
    return (f"{date}__{row['provider']}__{row['model']}__"
            f"{row['model_version']}__{condition}__{replicate}")


def parse_run_id(run_id: str) -> dict:
    parts = run_id.split("__")
    if len(parts) != 6 or parts[4] not in CONDITIONS \
            or parts[5] not in REPLICATES:
        raise ValueError(
            f"run id must be <date>__<provider>__<model>__<model_version>__"
            f"direct|primed__r01|r02|r03, got: {run_id!r}")
    return dict(zip(RUN_ID_FIELDS, parts))


def roster_entry(run_id: str) -> dict | None:
    try:
        parts = parse_run_id(run_id)
    except ValueError:
        return None
    pools: list[list[dict]] = [primary_rows(), exploratory_rows()]
    for pool in pools:
        for row in pool:
            if (row["provider"] == parts["provider"]
                    and row["model"] == parts["model"]
                    and row["model_version"] == parts["model_version"]):
                return row
    return None


def phase1_baseline_run_id_for(row: dict) -> str:
    """Phase-1 direct baseline run id for this configuration (real Phase-1
    plan preferred; documented fallback date otherwise)."""
    p1_plan = p1.load_plan()
    for r in p1_plan.get("runs", []):
        if (r["provider"] == row["provider"] and r["model"] == row["model"]
                and r["model_version"] == row["model_version"]):
            return r["run_id"]
    return (f"{p2a.PHASE1_PLAN_DATE}__{row['provider']}__{row['model']}__"
            f"{row['model_version']}__direct")


def phase2a_primed_run_id_for(row: dict) -> str | None:
    """Phase-2A primed run id for this configuration (exists only for the
    18 primary rows; Dola exploratory rows have their own p2a ids but are
    reported via the p2a plan when present)."""
    p2a_plan = p2a.load_plan()
    for r in p2a_plan.get("runs", []):
        if r.get("condition") != "p2a-primed":
            continue
        if (r["provider"] == row["provider"] and r["model"] == row["model"]
                and r["model_version"] == row["model_version"]):
            return r["run_id"]
    return None


def load_plan() -> dict:
    plan = OUTPUTS_DIR / "plan.json"
    if not plan.is_file():
        return {}
    return json.loads(plan.read_text(encoding="utf-8"))


def load_meta(run_id: str) -> dict:
    meta_path = OUTPUTS_DIR / run_id / "meta.json"
    if not meta_path.is_file():
        return {}
    return json.loads(meta_path.read_text(encoding="utf-8"))


def plan_entry(run_id: str) -> dict | None:
    return next((r for r in load_plan().get("runs", [])
                 if r["run_id"] == run_id), None)


def _base_instruction_text(source_text: str) -> str:
    return p1.BASE_INSTRUCTION.read_text(encoding="utf-8").replace(
        "{STORY}", source_text).rstrip() + "\n"


# ---------------------------------------------------------------------------
# prompt rendering (model-visible regions identical to Phase 1 / Phase 2A;
# replicate never appears inside a prompt file's content)
# ---------------------------------------------------------------------------

def _operator_header(row: dict, interface_target: str) -> str:
    """The '> ' operator block at the very top. Identical across the three
    replicates of a configuration+condition (never names the replicate)."""
    return "\n".join([
        f"> COPY THIS ENTIRE FILE INTO {row['interface']} in a NEW, "
        "FRESH session.",
        "> Do not modify anything. Run this message exactly once in that "
        "session;",
        "> do not chain it with previous messages and do not send "
        "follow-up messages.",
        "> Save the model's complete reply byte-for-byte and hand it to "
        "the collect step.",
    ])


def render_direct_prompt(row: dict, source_text: str) -> str:
    """Direct replicate prompt: metadata header + the byte-identical
    Phase-1 direct instruction body (base instruction with the story)."""
    setting = row["generation_parameters"]
    lines = [
        f"# EXP-004 — Interslavic translation — {row['label']}",
        "",
        _operator_header(row, row["interface"]),
        "",
        "---",
        "",
        "Experiment ID: EXP-004",
        "Task: direct translation (single message)",
        f"Target model: {row['label']}",
        f"Provider / interface: {row['provider']} / {row['interface']}",
        f"Model version / settings: {row['model_version']} ({setting})",
        "Condition: direct translation — no reference material",
        "",
        "---",
        "",
        _base_instruction_text(source_text).rstrip("\n") + "\n",
    ]
    return "\n".join(lines)


def render_primed_msg1(row: dict, corpus_text: str) -> str:
    """Primed message 1: metadata header + the byte-identical Phase-2A
    study instruction + the authoritative corpus text."""
    setting = row["generation_parameters"]
    lines = [
        f"# EXP-004 — Interslavic translation — {row['label']} — "
        "reference texts (message 1 of 2)",
        "",
        "> COPY THIS ENTIRE FILE INTO " + row["interface"]
        + " as the FIRST message of a NEW, FRESH session.",
        "> Do not modify anything. Send message 1, WAIT for the model's",
        "> short confirmation, THEN send message 2 (the file ending",
        "> \"-msg2\") in the SAME session.",
        "",
        "---",
        "",
        "Experiment ID: EXP-004",
        "Task: translation with reference texts (message 1 of 2)",
        f"Target model: {row['label']}",
        f"Provider / interface: {row['provider']} / {row['interface']}",
        f"Model version / settings: {row['model_version']} ({setting})",
        "Condition: reference texts only — no translation in this message",
        "",
        "---",
        "",
        PRIMED_MSG1_STUDY_TEXT,
        "",
        PRIMED_MSG1_HEADING,
        "",
        corpus_text.rstrip("\n"),
    ]
    return "\n".join(lines) + "\n"


def render_primed_msg2(row: dict, source_text: str) -> str:
    """Primed message 2: metadata header + the byte-identical Phase-2A
    translation task (intro sentence + base instruction with the story)."""
    setting = row["generation_parameters"]
    lines = [
        f"# EXP-004 — Interslavic translation — {row['label']} — "
        "translation task (message 2 of 2)",
        "",
        "> COPY THIS ENTIRE FILE INTO " + row["interface"]
        + " as the SECOND message of the SAME session as message 1 (send "
        "it after the model's short confirmation).",
        "> Do not modify anything. Save the model's complete reply (the "
        "translation) byte-for-byte.",
        "",
        "---",
        "",
        "Experiment ID: EXP-004",
        "Task: translation with reference texts (message 2 of 2)",
        f"Target model: {row['label']}",
        f"Provider / interface: {row['provider']} / {row['interface']}",
        f"Model version / settings: {row['model_version']} ({setting})",
        "Condition: primed — translation generated after the reference "
        "texts in this session",
        "",
        "---",
        "",
        PRIMED_MSG2_INTRO,
        "",
        _base_instruction_text(source_text).rstrip("\n") + "\n",
    ]
    return "\n".join(lines)


def prompt_filenames(row: dict, condition: str, replicate: str) -> list[str]:
    nn = config_number(row)
    base = f"{nn:02d}-{row['model']}-{row['model_version']}"
    if condition == "direct":
        return [f"direct-{base}-{replicate}.md"]
    return [f"primed-{base}-{replicate}-msg1.md",
            f"primed-{base}-{replicate}-msg2.md"]


def _rel_or_abs(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def _translation_body(text: str) -> str:
    """Invariant region of a translation prompt: from the standard
    instruction start through the closing '## Output' line."""
    start = text.find(TRANSLATION_START)
    if start < 0:
        return ""
    end = text.rfind("## Output")
    if end < 0:
        return text[start:]
    return text[start:end + len("## Output")]


def _split_reply(raw: bytes) -> tuple[bytes, bytes]:
    """Split a prompt+reply record at the closing '## Output\\n' marker
    (same slicing rule as p1.split_session_reply)."""
    marker = b"## Output\n"
    idx = raw.rfind(marker)
    if idx < 0:
        return raw, b""
    pos = idx + len(marker)
    while pos < len(raw) and raw[pos:pos + 1] in (b"\n", b"\r"):
        pos += 1
    return raw[:idx], raw[pos:]


def _strip_trailing_prompt_boilerplate(reply: bytes) -> bytes:
    boilerplate = (b"Return the complete Interslavic translation of the "
                   b"source text, and nothing\nelse.\n")
    if reply.startswith(boilerplate):
        return reply[len(boilerplate):]
    return reply


def _corpus_fingerprints() -> tuple[bytes, ...]:
    return tuple(a.encode("utf-8") for a in CORPUS_ANCHORS)


# ---------------------------------------------------------------------------
# prepare
# ---------------------------------------------------------------------------

def _ensure_source() -> Path:
    src = EXP / "input" / "source.txt"
    if not src.is_file():
        raise RuntimeError(
            f"Polish source story missing at {src}; run "
            "scripts/run_exp004_phase1.py prepare --date YYYY-MM-DD first")
    actual = sha256_file(src)
    if actual != SOURCE_SHA256:
        raise RuntimeError(
            f"{src} sha256 {actual[:16]}... does not match the canonical "
            f"source {SOURCE_SHA256[:16]}...; refusing to use a different "
            "story (fail loudly on any byte drift)")
    return src


def _ensure_corpus() -> Path:
    if not p2a.CORPUS_FILE.is_file():
        raise RuntimeError(
            f"reference corpus missing at {p2a.CORPUS_FILE}; build it with "
            "scripts/build_phase2a_corpus.py (three-register combined "
            "corpus, SODA Task 020)")
    actual = sha256_file(p2a.CORPUS_FILE)
    if actual != AUTH_CORPUS_SHA256:
        raise RuntimeError(
            f"{p2a.CORPUS_FILE} sha256 {actual[:16]}... does not match the "
            f"recorded corpus {AUTH_CORPUS_SHA256[:16]}...; an accidental "
            "edit would break the fixed-corpus fairness invariant (fail "
            "loudly, do not regenerate)")
    return p2a.CORPUS_FILE


def _all_rows() -> list[dict]:
    rows = []
    for row in primary_rows():
        rows.append(dict(row, primary=True, exploratory=False))
    for row in exploratory_rows():
        rows.append(dict(row, primary=False, exploratory=True))
    return rows


def _ordered_rows() -> list[dict]:
    """Block ordering: r01 direct+primed, r02 direct+primed, r03
    direct+primed per configuration (primary first by Phase-1 number,
    Dola appended as 20/21)."""
    out: list[tuple[dict, str, str]] = []
    for row in _all_rows():
        for rep in REPLICATES:
            for cond in CONDITIONS:
                out.append((row, cond, rep))
    out.sort(key=lambda t: (t[0].get("exploratory", False),
                            config_number(t[0]),
                            REPLICATES.index(t[2]),
                            CONDITIONS.index(t[1])))
    return out


def run_prepare(date: str, force: bool = False) -> int:
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date or ""):
        print("error: --date YYYY-MM-DD is required (run ids carry the "
              "planned generation date)", file=sys.stderr)
        return 2
    source = _ensure_source()
    corpus = _ensure_corpus()
    source_text = source.read_text(encoding="utf-8")
    corpus_text = corpus.read_text(encoding="utf-8")
    source_sha = sha256_bytes(source_text.encode("utf-8"))
    corpus_sha = sha256_bytes(corpus_text.encode("utf-8"))

    plan_path = OUTPUTS_DIR / "plan.json"
    if plan_path.is_file() and not force:
        print(f"error: {plan_path} already exists; use --force to rewrite "
              "(regenerating is safe ONLY before any collection; after "
              "collection it invalidates recorded run ids)",
              file=sys.stderr)
        return 2

    OPERATOR_PROMPTS.mkdir(parents=True, exist_ok=True)
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

    ordered = _ordered_rows()
    files: list[dict] = []
    runs: list[dict] = []
    for row, cond, rep in ordered:
        if cond == "direct":
            rendered = [render_direct_prompt(row, source_text)]
        else:
            rendered = [render_primed_msg1(row, corpus_text),
                        render_primed_msg2(row, source_text)]
        names = prompt_filenames(row, cond, rep)
        run_id = run_id_for(date, row, cond, rep)
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
                "replicate": rep, "message": message,
                "primary": row["primary"], "exploratory": row["exploratory"],
                "prompt_sha256": prompt_sha,
                "bytes": len(text.encode("utf-8")),
            })
        translation_sha = sha256_bytes(
            rendered[-1].encode("utf-8"))
        runs.append({
            "run_id": run_id,
            "phase": PHASE,
            "condition": cond,
            "replicate": rep,
            "primary": row["primary"],
            "exploratory": row["exploratory"],
            "phase1_number": (config_number(row)
                              if not row["exploratory"] else None),
            "run_number": (int(row["run_number"])
                           if row["exploratory"] else None),
            "provider": row["provider"], "model": row["model"],
            "model_version": row["model_version"], "label": row["label"],
            "interface": row["interface"],
            "generation_parameters": row["generation_parameters"],
            "custom_gpt": row["custom_gpt"],
            "prompt_files": run_files,
            "translation_prompt_sha256": translation_sha,
            "source_sha256": source_sha,
            "corpus_sha256": corpus_sha if cond == "primed" else None,
            "phase1_baseline_run_id": phase1_baseline_run_id_for(row),
            "phase2a_primed_run_id": phase2a_primed_run_id_for(row),
            "identity_note": row.get("identity_note"),
            "status": "pending_manual_collection",
        })

    plan = {
        "experiment_id": "exp004",
        "artifact": "repeat_plan",
        "phase": PHASE,
        "date": date,
        "generator": "scripts/run_exp004_repeats.py prepare",
        "generator_commit": git_commit(),
        "research_question": (
            "For the same model/configuration and the same translation "
            "task, how much does measured Interslavic resource coverage "
            "vary between independent generations, and is the observed "
            "Phase-2A corpus-priming shift larger than that variation?"),
        "source": {"file": _rel_or_abs(source),
                   "sha256": source_sha, "bytes": len(source_text.encode(
                       "utf-8"))},
        "corpus": {"id": CORPUS_ID, "version": CORPUS_VERSION,
                   "file": _rel_or_abs(p2a.CORPUS_FILE),
                   "sha256": corpus_sha,
                   "bytes": len(corpus_text.encode("utf-8"))},
        "conditions": list(CONDITIONS),
        "replicates": list(REPLICATES),
        "counts": {
            "primary_configurations": len(primary_rows()),
            "exploratory_configurations": len(exploratory_rows()),
            "runs_per_configuration_per_condition": REPLICATES_PER_CONDITION,
            "primary_runs": len(primary_rows()) * 2
                * REPLICATES_PER_CONDITION,
            "exploratory_runs": len(exploratory_rows()) * 2
                * REPLICATES_PER_CONDITION,
            "total_runs": len(runs),
        },
        "note": (
            "Controlled repeated generation (SODA Task 025). Replicates are "
            "independent fresh-session generations; r01/r02/r03 are "
            "replication blocks, NOT matched linguistic samples. Replicate "
            "prompt file contents are byte-identical within a "
            "(configuration, condition) by design. Dola rows are "
            "exploratory and never merged into the primary n=18 statistics. "
            "No LLM was called by this script."),
        "runs": runs,
    }
    plan_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2),
                         encoding="utf-8")

    manifest = {
        "artifact": "repeat_prompt_manifest",
        "experiment_id": "exp004",
        "phase": PHASE,
        "date": date,
        "generator": "scripts/run_exp004_repeats.py prepare",
        "generator_commit": git_commit(),
        "source": dict(plan["source"]),
        "corpus": dict(plan["corpus"]),
        "counts": dict(plan["counts"]),
        "note": ("Prompt hashes + run enumeration only (no story text, no "
                 "model output). Files under operator-prompts/ are "
                 "gitignored; this manifest is the committed record."),
        "files": sorted(files, key=lambda f: f["file"]),
    }
    (OPERATOR_PROMPTS / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8")

    _write_checklist(plan, date)
    print(f"[prepare] {date}: {len(runs)} runs "
          f"({plan['counts']['primary_runs']} primary + "
          f"{plan['counts']['exploratory_runs']} exploratory); "
          f"{len(files)} prompt files")
    print(f"  source sha256 {source_sha}")
    print(f"  corpus sha256 {corpus_sha}  ({CORPUS_ID} {CORPUS_VERSION})")
    return 0


def _write_checklist(plan: dict, date: str) -> None:
    """Human collection checklist grouped by configuration × replicate
    block (direct then primed). Deterministic."""
    lines = [
        f"# EXP-004 — Phase repeat — collection checklist "
        f"(prepared {date})",
        "",
        "Mark each row after collecting. Every replicate is a FRESH, "
        "independent session — never chain messages, never reuse a "
        "session, never tell the model this is a repeat. The three "
        "replicate files of a (configuration, condition) are byte-"
        "identical by design; the run id / file name carries the "
        "replicate tag.",
        "",
        "Checklist: for every usable output, run "
        "`scripts/run_exp004_repeats.py collect-session --run <run_id> "
        "--session <file>` (or `collect-msg2 --run <run_id>` for primed "
        "msg2-style records), then `verify` + `evaluate`.",
        "",
    ]
    last_label = None
    for r in plan["runs"]:
        if r["label"] != last_label:
            lines.append("")
            flag = "EXPLORATORY (optional)" if r["exploratory"] else "primary"
            lines.append(f"## {r['label']}  —  {flag}")
            last_label = r["label"]
        cond = r["condition"].upper()
        mark = "[ ]"
        if r["condition"] == "direct":
            fname = r["prompt_files"][0]
            lines.append(
                f"- {mark} {cond} {r['replicate']}  "
                f"`{r['run_id']}`  file `operator-prompts/{fname}`")
        else:
            lines.append(
                f"- {mark} {cond} {r['replicate']}  "
                f"`{r['run_id']}`  files "
                f"`{', '.join('operator-prompts/' + f for f in r['prompt_files'])}`")
    lines.append("")
    (OUTPUTS_DIR / "collection-checklist.md").write_text(
        "\n".join(lines), encoding="utf-8")


# ---------------------------------------------------------------------------
# collect-session / collect-msg2
# ---------------------------------------------------------------------------

def _meta_base(run_id: str, row: dict, pe: dict,
               generation_date: str) -> dict:
    parts = parse_run_id(run_id)
    plan = load_plan()
    return {
        "run_id": run_id,
        "experiment_id": "exp004",
        "phase": PHASE,
        "condition": parts["condition"],
        "replicate": parts["replicate"],
        "primary": pe["primary"],
        "exploratory": pe["exploratory"],
        "label": row["label"],
        "interface": row["interface"],
        "model": row["model"],
        "provider": row["provider"],
        "model_version": row["model_version"],
        "generation_parameters": row["generation_parameters"],
        "custom_gpt": row.get("custom_gpt", False),
        "generation_date": (generation_date if generation_date != "unknown"
                            else parts["date"]),
        "phase1_baseline_run_id": pe["phase1_baseline_run_id"],
        "phase2a_primed_run_id": pe["phase2a_primed_run_id"],
        "source": {"sha256": plan["source"]["sha256"]},
        "corpus": dict(plan["corpus"]) if pe["condition"] == "primed" else None,
        "resources": p1.resource_versions(),
    }


def _common_collect_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--generation-date", default="unknown",
                        help="actual generation date (default: run-id date)")
    parser.add_argument("--status", default="collected_external_output",
                        choices=p1.STATUSES)
    parser.add_argument("--access-verdict", default="unknown",
                        choices=p1.ACCESS_VERDICTS)
    parser.add_argument("--access-note", default="",
                        help="observed practical quota / free-access note")
    parser.add_argument("--interface-settings", default="",
                        help="visible interface settings affecting "
                             "generation (mode, thinking toggle, model name "
                             "displayed, temperature if exposed…); record "
                             "'not exposed' where nothing is visible")
    parser.add_argument("--note", default="", help="free-text deviation note")


def _finish_collect(run_id: str, row: dict, pe: dict, reply: bytes,
                    args: argparse.Namespace, *, session: Path | None,
                    session_bytes: bytes | None,
                    contamination: dict | None) -> int:
    out_dir = OUTPUTS_DIR / run_id
    dst = out_dir / "output.txt"
    if dst.exists():
        print(f"error: {dst} already exists; refusing to overwrite "
              "(never overwrite an existing run)", file=sys.stderr)
        return 2
    if not reply.strip():
        print(f"error: no model reply found after the '## Output' marker",
              file=sys.stderr)
        return 2
    out_dir.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(reply)  # byte-for-byte raw reply, never modified

    meta = _meta_base(run_id, row, pe, args.generation_date)
    meta.update({
        "status": args.status,
        "access": {
            "filter_verdict": args.access_verdict,
            "quota_observed": args.access_note,
            "criteria": "D-036/§5.1 (as recorded in Phase 1); observed by "
                        "the operator at execution time.",
        },
        "interface_settings": (args.interface_settings if
                               args.interface_settings else "not exposed"),
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "collected_by": "scripts/run_exp004_repeats.py "
                        + ("collect-session" if session is not None
                           else "collect-msg2"),
        "prompt": {"files": pe["prompt_files"],
                   "translation_prompt_sha256":
                       pe["translation_prompt_sha256"]},
        "output": {"file": str(dst), "sha256": sha256_bytes(reply),
                   "bytes": len(reply)},
        "note": ("Raw LLM output stored byte-for-byte; never modified. "
                 "Empty/failed runs are preserved and documented, not "
                 "deleted." + (f" {args.note}" if args.note else "")),
    })
    if session is not None:
        meta["session"] = {
            "file": str(session),
            "name": session.name,
            "sha256": sha256_bytes(session_bytes or b""),
            "msg2_style_record": session.resolve() in {
                (OPERATOR_PROMPTS / f).resolve()
                for f in pe["prompt_files"]},
            "corpus_anchors": list(CORPUS_ANCHORS),
            "contamination_checks": contamination or {},
        }
    (out_dir / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[collect] {run_id}")
    print(f"  label/interface: {row['label']} / {row['interface']}")
    print(f"  condition: {meta['condition']}  replicate: {meta['replicate']}"
          f"  exploratory: {meta['exploratory']}")
    print(f"  output sha256: {meta['output']['sha256']}  "
          f"({len(reply)} B)")
    return 0


def _validate_session_record(run_id: str, pe: dict, session: Path) -> tuple[
        bytes, bytes, dict | None]:
    """Validate an author session record against the run's canonical
    prompt and the condition contamination controls; return
    (canonical_check, reply, contamination_checks) or raise a ValueError
    with a human message on protocol violation."""
    session_bytes = session.read_bytes()
    session_text = session_bytes.decode("utf-8", errors="replace")
    canonical_file = OPERATOR_PROMPTS / pe["prompt_files"][-1]
    canonical_text = canonical_file.read_text(encoding="utf-8")
    canonical_body = _translation_body(canonical_text)
    if not canonical_body:
        raise ValueError(f"cannot locate the canonical translation body in "
                         f"{canonical_file.name}")
    anchors = _corpus_fingerprints()
    contamination: dict = {}

    is_msg2_style = session.resolve() == canonical_file.resolve()
    if is_msg2_style:
        # The record IS the canonical prompt file with the reply appended
        # after its closing '## Output' marker (Tasks 021/023 shape).
        _prefix, reply = _split_reply(session_bytes)
        reply = _strip_trailing_prompt_boilerplate(reply)
        prompt_part = _prefix + b"## Output\n"
        if _translation_body(
                prompt_part.decode("utf-8", errors="replace")) \
                != canonical_body:
            raise ValueError(
                "msg2-style record's prompt part (through the closing "
                "'## Output' marker) does not match the canonical prompt "
                f"for {run_id}; refusing to collect")
        contamination = {
            "record_shape": "msg2-style (prompt file == session record)",
            "prompt_part_matches_canonical": True,
            "corpus_in_direct_record": bool(
                pe["condition"] == "direct"
                and any(a in session_bytes for a in anchors)),
        }
        if pe["condition"] == "direct" and contamination[
                "corpus_in_direct_record"]:
            raise ValueError(
                f"direct record for {run_id} CONTAINS the reference corpus "
                "(or one of its register fingerprints); refusing to collect "
                "(condition contamination)")
        return canonical_body, reply, contamination

    if pe["condition"] == "direct":
        if _translation_body(session_text) != canonical_body:
            raise ValueError(
                "session file's translation instruction body does not match "
                f"the canonical direct prompt for {run_id}; refusing to "
                "collect")
        if any(a in session_bytes for a in anchors):
            raise ValueError(
                f"direct session for {run_id} CONTAINS the reference corpus "
                "(or one of its register fingerprints) — the direct "
                "condition must never include ISV reference material; "
                "refusing to collect (conversation contamination)")
        contamination = {"corpus_in_control": False}
        _prefix, reply = _split_reply(session_bytes)
        reply = _strip_trailing_prompt_boilerplate(reply)
        return canonical_body, reply, contamination

    # primed: msg1 (all three corpus registers) must precede the
    # translation instruction; msg2 body must match the canonical msg2.
    body_start = session_text.find(TRANSLATION_START)
    before = session_bytes[:body_start] if body_start >= 0 else b""
    if not all(a in before for a in anchors):
        raise ValueError(
            f"primed session for {run_id} does not contain all three corpus "
            "registers BEFORE the translation instruction — the priming "
            "condition requires msg1 (the complete three-register corpus) "
            "and msg2 (translation) in the same session; refusing to "
            "collect")
    if _translation_body(session_text) != canonical_body:
        raise ValueError(
            "session file's translation instruction body does not match "
            f"the canonical Prompt-2 (msg2) for {run_id}; refusing to "
            "collect")
    contamination = {"corpus_before_translation": True}
    _prefix, reply = _split_reply(session_bytes)
    reply = _strip_trailing_prompt_boilerplate(reply)
    return canonical_body, reply, contamination


def run_collect_session(args: argparse.Namespace) -> int:
    run_id = args.run
    row = roster_entry(run_id)
    if row is None:
        print(f"error: unknown run id {run_id!r} (not a Phase-repeat "
              f"roster row)", file=sys.stderr)
        return 2
    pe = plan_entry(run_id)
    if pe is None:
        print("error: run not in the repeat plan; run "
              "`scripts/run_exp004_repeats.py prepare --date <date>` first",
              file=sys.stderr)
        return 2
    session = Path(args.session)
    if not session.is_file():
        print(f"error: session file not found: {session}", file=sys.stderr)
        return 2
    try:
        _body, reply, contamination = _validate_session_record(
            run_id, pe, session)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    session_bytes = session.read_bytes()
    return _finish_collect(run_id, row, pe, reply, args, session=session,
                           session_bytes=session_bytes,
                           contamination=contamination)


def run_collect_msg2(args: argparse.Namespace) -> int:
    run_id = args.run
    row = roster_entry(run_id)
    if row is None:
        print(f"error: unknown run id {run_id!r} (not a Phase-repeat "
              f"roster row)", file=sys.stderr)
        return 2
    pe = plan_entry(run_id)
    if pe is None:
        print("error: run not in the repeat plan; run "
              "`scripts/run_exp004_repeats.py prepare --date <date>` first",
              file=sys.stderr)
        return 2
    if pe["condition"] != "primed":
        print("error: collect-msg2 applies to primed runs only (direct "
              "msg2-style records go through collect-session)",
              file=sys.stderr)
        return 2
    msg2_name = pe["prompt_files"][-1]
    src = OPERATOR_PROMPTS / msg2_name
    if not src.is_file():
        print(f"error: author msg2 file not found: {src}",
              file=sys.stderr)
        return 2
    raw = src.read_bytes()
    if TRANSLATION_START.encode("utf-8") not in raw:
        print(f"error: {src.name} does not contain the translation "
              f"instruction ({TRANSLATION_START!r}); not a msg2 file",
              file=sys.stderr)
        return 2
    _prefix, reply = _split_reply(raw)
    reply = _strip_trailing_prompt_boilerplate(reply)
    msg1_name = pe["prompt_files"][0]
    msg1 = OPERATOR_PROMPTS / msg1_name
    anchors = _corpus_fingerprints()
    msg1_corpus_ok = (msg1.is_file()
                      and all(a in msg1.read_bytes() for a in anchors))
    contamination = {
        "record_shape": "msg2-style (operator-prompts msg2 file + appended "
                        "reply; no machine same-session transcript proof, "
                        "operator-confirmed)",
        "msg1_file_contains_all_three_corpus_registers": msg1_corpus_ok,
        "msg2_prompt_part_matches_canonical": bool(_translation_body(
            _prefix.decode("utf-8", errors="replace"))
            and _translation_body(_prefix.decode("utf-8",
                                                 errors="replace"))
            == _translation_body(src.read_text(encoding="utf-8"))),
    }
    return _finish_collect(run_id, row, pe, reply, args, session=src,
                           session_bytes=raw, contamination=contamination)


# ---------------------------------------------------------------------------
# verify / evaluate / status / roster
# ---------------------------------------------------------------------------

def _verify_integrity(run_id: str, pe: dict | None) -> list[str]:
    errors: list[str] = []
    out_dir = OUTPUTS_DIR / run_id
    meta = load_meta(run_id)
    if not meta:
        errors.append("meta.json missing")
    output_path = out_dir / "output.txt"
    if not output_path.is_file():
        errors.append("output.txt missing")
    elif meta:
        recorded = meta.get("output", {}).get("sha256")
        actual = sha256_bytes(output_path.read_bytes())
        if recorded is None:
            errors.append("meta.json has no output sha256")
        elif recorded != actual:
            errors.append(f"output sha256 mismatch: meta={recorded} "
                          f"actual={actual}")
    if pe is not None and meta:
        if meta.get("condition") != pe["condition"]:
            errors.append("condition mismatch meta vs plan")
        if meta.get("replicate") != pe["replicate"]:
            errors.append("replicate mismatch meta vs plan")
        if (meta.get("prompt", {}).get("translation_prompt_sha256")
                != pe["translation_prompt_sha256"]):
            errors.append("translation prompt hash differs from plan")
        if meta["source"].get("sha256") != pe["source_sha256"]:
            errors.append("source hash differs from plan")
        if pe["condition"] == "primed":
            recorded_corpus = (meta.get("corpus") or {}).get("sha256")
            if recorded_corpus != pe["corpus_sha256"]:
                errors.append("corpus hash differs from plan")
        pf = OPERATOR_PROMPTS / Path(meta["prompt"]["files"][-1]).name
        if meta.get("session", {}).get("msg2_style_record"):
            sess_sha = meta.get("session", {}).get("sha256")
            if sess_sha is None:
                errors.append("msg2-style record has no session sha256")
            elif sha256_bytes(pf.read_bytes()) != sess_sha:
                errors.append("msg2-style record file changed since "
                              "collection (session sha256 mismatch)")
        elif sha256_bytes(pf.read_bytes()) != pe["translation_prompt_sha256"]:
            errors.append("prompt file content no longer matches recorded "
                          "hash")
    return errors


def run_verify(run_id: str | None = None,
               size_floor: int | None = None) -> int:
    plan = load_plan()
    runs: list[tuple[str, dict | None]] = []
    if run_id:
        runs.append((run_id, plan_entry(run_id)))
    else:
        for r in plan.get("runs", []):
            runs.append((r["run_id"], r))
    if not runs:
        print("nothing to verify; prepare a plan first", file=sys.stderr)
        return 2
    src = plan.get("source") or {}
    sp = (Path(src["file"]) if src.get("file")
          and Path(src["file"]).is_absolute() else ROOT / (src["file"] or ""))
    source_bytes = sp.stat().st_size if sp.is_file() else 0

    problems = 0
    for rid, pe in runs:
        out_dir = OUTPUTS_DIR / rid
        if not (out_dir / "output.txt").is_file():
            print(f"[skip] {rid}: no collected output")
            continue
        integrity = _verify_integrity(rid, pe)
        floor = size_floor if size_floor is not None else int(
            0.60 * source_bytes)
        gate = p1._gate_checks(out_dir, source_bytes, floor)
        verdict = p1._intake_verdict(gate)
        meta = load_meta(rid)
        intake = {
            "run_id": rid,
            "condition": meta.get("condition"),
            "replicate": meta.get("replicate"),
            "verdict": verdict,
            "checks": gate["checks"],
            "reasons": gate["reasons"],
            "floor_bytes": floor,
            "integrity_errors": integrity,
            "meta_status": meta.get("status", None),
        }
        (out_dir / "intake.json").write_text(
            json.dumps(intake, ensure_ascii=False, indent=2),
            encoding="utf-8")
        flag = "OK " if not integrity else "FAIL"
        if integrity:
            problems += 1
        print(f"[{flag}] {rid} -> {verdict.upper()}"
              f"{' (FAILS: ' + '; '.join(integrity) + ')' if integrity else ''}")
        if gate["reasons"]:
            print("    reasons: " + "; ".join(gate["reasons"]))
    print(f"\n{len(runs)} planned run(s) checked.")
    return 1 if problems else 0


def _pct(v: float | None) -> str:
    return f"{v * 100:.2f}%" if v is not None else "n/a"


def run_evaluate(run_id: str, force: bool = False) -> int:
    out_dir = OUTPUTS_DIR / run_id
    text = out_dir / "output.txt"
    if not text.is_file():
        print(f"error: no output.txt for {run_id}; collect it first",
              file=sys.stderr)
        return 2
    meta = load_meta(run_id)
    if not meta:
        print(f"error: no meta.json for {run_id}; collect it first",
              file=sys.stderr)
        return 2
    intake_path = out_dir / "intake.json"
    if not intake_path.is_file():
        print("[evaluate] no intake.json; running the completeness gate "
              "first")
        rc = run_verify(run_id)
        if rc == 2:
            return 2
    intake = json.loads(intake_path.read_text(encoding="utf-8"))
    if intake["verdict"] == "failed" and not force:
        print(f"error: intake verdict for {run_id} is 'failed' "
              f"({'; '.join(intake['reasons'])}); refusing to evaluate a "
              "non-translation output (--force to override)",
              file=sys.stderr)
        return 2

    eval_dir = out_dir / "evaluation"
    eval_dir.mkdir(parents=True, exist_ok=True)
    cmd = [sys.executable, "-m", "isv_eval.cli", str(text),
           "--out", str(eval_dir)]
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    if proc.returncode != 0:
        print(f"error: isv-eval failed on {text}: {proc.stderr[-500:]}",
              file=sys.stderr)
        return 2
    report = json.loads((eval_dir / "report.json").read_text(
        encoding="utf-8"))
    m = report["metrics"]
    summary = {
        "run_id": run_id,
        "evaluator": report["evaluator"],
        "phase": PHASE,
        "condition": meta.get("condition"),
        "replicate": meta.get("replicate"),
        "primary": meta.get("primary"),
        "exploratory": meta.get("exploratory"),
        "label": meta.get("label"),
        "model": meta.get("model"),
        "provider": meta.get("provider"),
        "model_version": meta.get("model_version"),
        "generation_parameters": meta.get("generation_parameters"),
        "phase1_baseline_run_id": meta.get("phase1_baseline_run_id"),
        "phase2a_primed_run_id": meta.get("phase2a_primed_run_id"),
        "intake_verdict": intake["verdict"],
        "usable": intake["verdict"] == "complete",
        "metrics": m,
        "output_files": report["output_files"],
    }
    (out_dir / "evaluation.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8")

    ortho = scan_file(text)
    od = ortho.as_dict()
    (out_dir / "orthography.json").write_text(json.dumps({
        "run_id": run_id,
        "inventory": "official Interslavic alphabet "
                     "(src/isv_eval/orthography.py, D-040)",
        "metrics": od,
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        f"# EXP-004 Phase repeat — evaluation — {run_id}",
        "",
        f"{meta.get('label', '?')} ({meta.get('provider')}, version "
        f"{meta.get('model_version')}) · {meta.get('condition')} "
        f"{meta.get('replicate')} · generated "
        f"{meta.get('generation_date')} · intake "
        f"{intake['verdict']} · usable {summary['usable']}",
        "",
        "| metric | value |",
        "|---|---:|",
        f"| lexical tokens | {m['total_tokens']} |",
        f"| canonical supported tokens (A+B) | {m['canonical_supported_tokens']} |",
        f"| canonical coverage | {_pct(m['canonical_coverage'])} |",
        f"| broader resource-supported tokens | {m['broader_resource_supported_tokens']} |",
        f"| broader resource-supported coverage | {_pct(m['broader_resource_supported_coverage'])} |",
        f"| unresolved tokens (C) | {m['unresolved_tokens']} |",
        f"| unresolved rate | {_pct(m['unresolved_rate'])} |",
        f"| exact dictionary matches (A) | {m['exact_dictionary_matches']} |",
        f"| morphologically valid (B) | {m['morphologically_valid_forms']} |",
        "",
        "Orthography (outside-inventory): "
        f"cyrillic {od['cyrillic']} · polish-specific {od['polish_specific']} "
        f"· other-latin {od['other_latin']} · other-script "
        f"{od['other_script']} · unexpected non-letter "
        f"{od['unexpected_nonletters']} (total {od['outside_inventory']})",
        "",
        "Coverage is evidence, not linguistic correctness; no composite "
        "quality score is assigned.",
        "",
    ]
    (out_dir / "evaluation.md").write_text("\n".join(lines),
                                          encoding="utf-8")
    print(f"[evaluate] {run_id} ({meta.get('condition')} "
          f"{meta.get('replicate')}, intake {intake['verdict']}, "
          f"usable {summary['usable']})")
    print(f"  canonical: {_pct(m['canonical_coverage'])}  "
          f"broader: {_pct(m['broader_resource_supported_coverage'])}  "
          f"unresolved: {_pct(m['unresolved_rate'])}")
    print(f"  orthography outside-inventory: {od['outside_inventory']} "
          f"(cyr {od['cyrillic']}, pol {od['polish_specific']}, "
          f"lat {od['other_latin']})")
    return 0


def run_status() -> int:
    plan = load_plan()
    runs = plan.get("runs", [])
    if not runs:
        print("nothing planned yet; run prepare first", file=sys.stderr)
        return 2
    prim = [r for r in runs if r["primary"]]
    expl = [r for r in runs if not r["primary"]]
    print(f"EXP-004 phase repeat — {len(runs)} planned runs "
          f"({len(prim)} primary + {len(expl)} exploratory)")
    print(f"{'run_id':76s} cond  rep   st  c/e  intake")
    for r in runs:
        meta = load_meta(r["run_id"])
        intake_path = OUTPUTS_DIR / r["run_id"] / "intake.json"
        verdict = "-"
        if intake_path.is_file():
            verdict = json.loads(intake_path.read_text(
                encoding="utf-8"))["verdict"][:4]
        st = meta.get("status", "planned")[:12]
        ce = "P" if r["primary"] else "E"
        print(f"{r['run_id']:76s} {r['condition']:6s} {r['replicate']:4s} "
              f"{st:12s} {ce:3s} {verdict}")
    n_ok = sum(1 for r in runs
               if (OUTPUTS_DIR / r["run_id"] / "evaluation.json").is_file())
    print(f"\nevaluated: {n_ok}/{len(runs)}")
    return 0


def _metric_value(run_id: str) -> dict | None:
    ev = OUTPUTS_DIR / run_id / "evaluation.json"
    if not ev.is_file():
        return None
    d = json.loads(ev.read_text(encoding="utf-8"))
    return {
        "metrics": d["metrics"],
        "intake_verdict": d["intake_verdict"],
        "usable": d["usable"],
    }


def run_roster() -> int:
    plan = load_plan()
    runs = plan.get("runs", [])
    if not runs:
        print("nothing planned yet; run prepare first", file=sys.stderr)
        return 2
    rows = []
    for r in runs:
        meta = load_meta(r["run_id"])
        ev = _metric_value(r["run_id"])
        ortho_path = OUTPUTS_DIR / r["run_id"] / "orthography.json"
        ortho = (json.loads(ortho_path.read_text(encoding="utf-8"))["metrics"]
                 if ortho_path.is_file() else None)
        rows.append({
            "run_id": r["run_id"],
            "phase": PHASE,
            "condition": r["condition"],
            "replicate": r["replicate"],
            "primary": r["primary"],
            "exploratory": r["exploratory"],
            "label": r["label"],
            "model": r["model"], "provider": r["provider"],
            "model_version": r["model_version"],
            "generation_parameters": r["generation_parameters"],
            "generation_date": meta.get("generation_date"),
            "interface_settings": meta.get("interface_settings"),
            "status": meta.get("status"),
            "intake": (json.loads((OUTPUTS_DIR / r["run_id"] /
                                   "intake.json").read_text(
                                       encoding="utf-8"))
                       if (OUTPUTS_DIR / r["run_id"] /
                           "intake.json").is_file() else None),
            "usable": bool(ev and ev["usable"]),
            "metrics": ev["metrics"] if ev else None,
            "orthography": ortho,
        })
    roster = {
        "experiment_id": "exp004",
        "artifact": "repeat_roster",
        "phase": PHASE,
        "date": plan.get("date"),
        "generator": "scripts/run_exp004_repeats.py roster",
        "generator_commit": git_commit(),
        "counts": {
            "planned": len(runs),
            "collected": sum(1 for r in rows if r["status"]),
            "intake_complete": sum(1 for r in rows
                                   if r["intake"]
                                   and r["intake"]["verdict"] == "complete"),
            "usable": sum(1 for r in rows if r["usable"]),
        },
        "note": ("Per-dimension evidence only — no ranking, no composite "
                 "score. Primary (n=18) and exploratory Dola rows are "
                 "kept separate everywhere."),
        "rows": rows,
    }
    (OUTPUTS_DIR / "roster.json").write_text(
        json.dumps(roster, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        f"# EXP-004 Phase repeat — roster "
        f"(planned {plan.get('date')})",
        "",
        f"Collected {roster['counts']['collected']}/{len(rows)} · intake "
        f"complete {roster['counts']['intake_complete']} · usable "
        f"{roster['counts']['usable']}",
        "",
        "Per-dimension evidence only — no ranking, no composite score.",
        "",
        "| run_id | cond | rep | P/E | intake | usable | canonical | broader | unresolved | ortho-out |",
        "|---|---|---|---|---|---|---:|---:|---:|---:|",
    ]
    for r in rows:
        m = r["metrics"]
        o = r["orthography"]
        can = _pct(m["canonical_coverage"]) if m else "—"
        bro = _pct(m["broader_resource_supported_coverage"]) if m else "—"
        unr = _pct(m["unresolved_rate"]) if m else "—"
        orth = str(o["outside_inventory"]) if o else "—"
        iv = (r["intake"]["verdict"] if r["intake"] else "—")
        pe = "P" if r["primary"] else "E"
        lines.append(
            f"| {r['run_id']} | {r['condition']} | {r['replicate']} | "
            f"{pe} | {iv} | {r['usable']} | {can} | {bro} | {unr} | "
            f"{orth} |")
    lines.append("")
    (OUTPUTS_DIR / "roster.md").write_text("\n".join(lines),
                                           encoding="utf-8")
    print(f"[roster] {len(rows)} rows written to outputs/roster.json + "
          f"roster.md (usable {roster['counts']['usable']})")
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="EXP-004 Phase repeat — controlled repeated generation "
                    "orchestrator (SODA Task 025). Never calls an LLM.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_prep = sub.add_parser("prepare", help="render prompts + write plan/manifest/checklist")
    p_prep.add_argument("--date", required=True,
                        help="planned generation date YYYY-MM-DD (run ids)")
    p_prep.add_argument("--force", action="store_true",
                        help="overwrite existing plan/prompts (only safe "
                             "before any collection)")
    p_prep.set_defaults(fn=lambda a: run_prepare(a.date, a.force))

    def _add_collect_subcommand(name: str, fn) -> argparse.ArgumentParser:
        p = sub.add_parser(name, help="register a collected raw reply")
        p.add_argument("--run", required=True)
        _common_collect_options(p)
        p.set_defaults(fn=fn)
        return p

    p_cs = _add_collect_subcommand("collect-session", run_collect_session)
    p_cs.add_argument(
        "--session", required=True,
        help="author session file (prompt + reply in one markdown file; or "
             "the run's canonical prompt file with the reply appended "
             "after its '## Output' marker, msg2-style)")
    p_cm = _add_collect_subcommand("collect-msg2", run_collect_msg2)

    p_ver = sub.add_parser("verify", help="completeness gate + integrity")
    p_ver.add_argument("--run", default=None)
    p_ver.add_argument("--size-floor", type=int, default=None)
    p_ver.set_defaults(fn=lambda a: run_verify(a.run, a.size_floor))

    p_ev = sub.add_parser("evaluate", help="run isv-eval + orthography")
    p_ev.add_argument("--run", required=True)
    p_ev.add_argument("--force", action="store_true")
    p_ev.set_defaults(fn=lambda a: run_evaluate(a.run, a.force))

    p_st = sub.add_parser("status", help="collection status")
    p_st.set_defaults(fn=lambda a: run_status())

    p_ro = sub.add_parser("roster", help="write roster.json + roster.md")
    p_ro.set_defaults(fn=lambda a: run_roster())

    args = parser.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
