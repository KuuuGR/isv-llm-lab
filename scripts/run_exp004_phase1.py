#!/usr/bin/env python3
"""EXP-004 Phase 1 (practical model screening) — run orchestrator.

Phase 1 asks one question: which practically accessible LLMs are worth
taking forward as candidate engines for Polish → Medžuslovjansky? It
establishes a CLEAN direct-translation baseline per roster row: same
byte-identical Polish source story, same direct-translation instruction,
NO lexical scaffolding, NO candidate word lists, NO morphology/POS or
grammar annotations, NO previous translations, NO evaluator feedback, NO
iterative repair (D-037, EXP-004 DESIGN §6.2).

LLM execution is EXTERNAL (the project has no LLM API client, D-007): the
operator executes one self-contained prompt per roster row in the model's
web/chat interface and returns the raw reply. This script only prepares
runs, registers externally produced outputs byte-for-byte, verifies them
(structural completeness gate, L-027), evaluates them with the Task 008
evaluator (unmodified) plus the Task 015 character-level orthographic
audit, and reports status. It never calls an LLM and never fabricates
outputs.

Commands:

  prepare  --date YYYY-MM-DD [--force]
           provision the local story source (byte-identical copy of the
           EXP-003 canonical source), render one self-contained operator
           prompt per roster row into operator-prompts/, write the prompt
           manifest (operator-prompts/manifest.json, prompt hashes only),
           and write outputs/plan.json (the fixed roster: run ids +
           provider/model/version/interface/access metadata + hashes).
           Deterministic: regenerating with the same --date yields
           byte-identical prompts, manifest, and plan.

  extend-direct  --date YYYY-MM-DD
           append the two exploratory Phase-1 DIRECT baselines for the
           author-discovered Dola 3.8 configurations (runs 20/21 — Fast and
           Pro; SODA Task 022) to outputs/plan.json and their operator
           prompts to operator-prompts/ (+ manifest entries), idempotently.
           The prompts use the identical Phase-1 direct protocol (same base
           instruction + same Polish source story, fresh session, NO corpus/
           scaffold/dictionary/morphology content) and are marked
           exploratory + pending manual collection — nothing is fabricated.
           Do not re-run `prepare --force` afterwards (it would drop the
           appended rows).

  collect  --run <run_id> --output <path>
           register an externally generated raw output: copied byte-for-byte,
           never modified, never overwritten; meta.json records prompt/source
           hashes, provider/model/version, generation date + parameters,
           status (D-035), the practical free-access verdict (§5.1/D-036,
           observed by the operator at execution time), output SHA-256, and
           resource pins.

  collect-session  --run <run_id> --session <path>
           [same option set as collect]
           register the raw model reply EMBEDDED in an author session file
           (the author saved each external session as one markdown file:
           annotated prompt header + unmodified instruction/source body +
           the model's raw reply appended after the prompt's closing
           '## Output' line). Validates the instruction body against the
           canonical prompt (clean-baseline invariant), extracts the reply
           byte-for-byte into outputs/<run_id>/output.txt, and records the
           session file's SHA-256 + the reply SHA-256 in meta.json. The
           session file itself is never modified.

  verify   [--run <run_id> | --all] [--size-floor BYTES] [--no-plan]
           integrity checks (output hash vs meta, plan consistency) plus the
           structural completeness gate (L-027): non-empty output, byte size
           >= floor (default 0.60 x source bytes), head sanity, presence of
           the story's main character-name tokens, and the end marker
           (KONIEC/KONEC/KONĖC) as the final non-empty line. Writes
           outputs/<run>/intake.json with a verdict:
             complete  — passes the gate (quantitatively usable)
             partial   — real translation but truncated / marker missing
             failed    — not a usable translation (echo, error page, empty)
           The verdict is recorded as data; partial/failed runs are NEVER
           silently deleted, repaired, or rerun (D-035, L-027).

  evaluate --run <run_id> [--force]
           run the completeness gate if no intake.json exists, refuse for
           verdict 'failed' (unless --force), then run the Task 008
           evaluator (isv-eval, unmodified) and the orthographic audit
           (isv_eval.orthography) on the collected output; write
           outputs/<run>/evaluation.json (+ evaluation/ detail),
           outputs/<run>/orthography.json, and evaluation.md. evaluation.json
           carries 'usable' = (intake verdict complete). Metrics are evidence
           dimensions, never merged and never a composite score.

  status   show planned / collected / verified / evaluated / usable per row.

  roster   join plan + meta + intake + evaluation + orthography for every
           collected run into outputs/roster.json and outputs/roster.md
           (coverage pair, unresolved rate, orthography counts, access
           verdict, usability per row — no ranking, no composite score).

Run id: <date>__<provider>__<model>__<model_version>__direct (condition
token 'direct'; variant settings such as thinkon/deepthinkoff are part of
the model_version token). Failures are preserved as data.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from isv_eval.cli import git_commit  # noqa: E402
from isv_eval.orthography import scan_file  # noqa: E402

EXP = ROOT / "experiments" / "exp004-modelscreen"
INPUT_DIR = EXP / "input"
OPERATOR_PROMPTS = EXP / "operator-prompts"
OUTPUTS_DIR = EXP / "outputs"
SESSION_DIR = EXP / "collected-sessions"
BASE_INSTRUCTION = EXP / "base_instruction.txt"
EXP003_SOURCE = (ROOT / "experiments" / "exp003-scaffold" / "input"
                 / "source.txt")
DEFAULT_MANIFEST = ROOT / "data" / "dictionary" / "manifest.json"
DEFAULT_LEXICON = ROOT / "data" / "dictionary" / "lexicon.tsv"
EXP003_SOURCE_SHA256 = (
    "5de968a6214d3d64bdb586b5121f494c4bb107e33546487a86bf8ecc57280723")

CONDITION = "direct"
END_MARKER_RE = re.compile(r"^\s*(KONIEC|KONEC|KONĖC)\s*$")
# Story's main character names. EXP-003 outputs kept the Polish spellings
# verbatim; EXP-004 Phase-1 models transliterate them (Bronisława →
# Bronislava/Bronisława; Przemysław → Przemyslava/Przemysław; Antoni →
# Anton/Antonij; Julianna → Julianna/Julijana), so names are matched by
# case/diacritic-folded, w/v-tolerant stems (Task 018 calibration).
NAME_STEMS = {
    "bronislawa": ("bronislav", "bronislaw"),
    "teofil": ("teofil",),
    "julianna": ("julian", "julij"),
    "przemyslawa": ("przemyslav", "przemyslaw"),
    "antoni": ("anton",),
}
_DIACRITIC_FOLD = str.maketrans({
    "ł": "l", "š": "s", "ś": "s", "ě": "e", "ć": "c", "č": "c",
    "ż": "z", "ž": "z", "ń": "n", "à": "a", "é": "e", "è": "e", "ů": "u",
})


def _fold_for_names(text: str) -> str:
    return text.lower().translate(_DIACRITIC_FOLD)


def instruction_body(text: str) -> str:
    """The clean-baseline invariant region: from the instruction's first
    line through the prompt's closing '## Output' marker (excludes the
    editable header and any appended reply)."""
    start = text.find("Translate the Polish story below into Interslavic")
    if start < 0:
        return ""
    end = text.rfind("## Output")
    if end < 0:
        return text[start:]
    return text[start:end + len("## Output")]


def split_session_reply(raw: bytes) -> tuple[bytes, bytes]:
    """Split an author session file (prompt + appended raw reply) at the
    prompt's closing '## Output\\n' marker. The canonical prompt always ends
    '## Output\\n\\n'; the model's reply is everything after that marker and
    the following blank line(s). Returns (prompt_prefix, reply). The reply is
    the model's raw output and is never modified."""
    marker = b"## Output\n"
    idx = raw.rfind(marker)
    if idx < 0:
        return raw, b""
    pos = idx + len(marker)
    while pos < len(raw) and raw[pos:pos + 1] in (b"\n", b"\r"):
        pos += 1
    return raw[:idx], raw[pos:]

# ---------------------------------------------------------------------------
# Reconciled executed roster (EXP-004 Phase 1, actual collected runs, SODA
# Task 018)
# ---------------------------------------------------------------------------
# The planned 11-row roster (EXP-004 DESIGN §5.2) expanded during manual
# collection into the concrete executed set below. Model/version tokens are
# the reconciled identities: author filename/header annotations were
# audited against each other and the deterministic prompt package
# (scripts/audit_exp004_collected.py); three contradictory annotations were
# resolved with the author (2026-09-06): 15/16 DeepSeek = V3 Expert (not the
# stale 'v4-pro' filename), 19 Qwen = 3.8 Max Fast (header 'Thinking' was a
# copy error), 05 Gemini = 3.1 Pro extended-thinking ON. Confidence is
# recorded in the registry; model identity beyond the prompt package rests
# on the operator's annotations (D-018 'unknown' fallback where absent).
# session_file = the author's raw session file name (prompt+reply), kept
# byte-for-byte under collected-sessions/.
ROSTER = [
    {
        "provider": "openai", "model": "gpt-5.6-luna", "model_version": "thinkoff",
        "label": "GPT-5.6 Luna — thinking OFF", "interface": "ChatGPT (web)",
        "generation_parameters": "thinking OFF", "custom_gpt": False,
        "variant_of": None, "conditional": "",
        "session_file": "01-gpt-5.6-luna-thinkoff.md",
    },
    {
        "provider": "openai", "model": "gpt-5.6-luna", "model_version": "thinkon",
        "label": "GPT-5.6 Luna — thinking ON", "interface": "ChatGPT (web)",
        "generation_parameters": "thinking ON", "custom_gpt": False,
        "variant_of": "thinkoff", "conditional": "",
        "session_file": "02-gpt-5.6-luna-thinkon.md",
    },
    {
        "provider": "openai", "model": "gpt-isv-teacher", "model_version": "unknown",
        "label": "GPT Interslavic Teacher (custom GPT)", "interface": "ChatGPT (custom GPT)",
        "generation_parameters": "custom GPT; built-in system prompt unknown (D-018)",
        "custom_gpt": True, "variant_of": None, "conditional": "",
        "session_file": "03-gpt-isv-teacher-unknown.md",
    },
    {
        "provider": "anthropic", "model": "claude", "model_version": "sonnet-5",
        "label": "Claude Sonnet 5 — Medium (default)", "interface": "Claude (web)",
        "generation_parameters": "Sonnet 5 Medium (default)",
        "custom_gpt": False, "variant_of": None, "conditional": "",
        "session_file": "04-claude-sonnet-5.md",
    },
    {
        "provider": "google", "model": "gemini-3.1-pro", "model_version": "extthinkon",
        "label": "Gemini 3.1 Pro — extended thinking ON", "interface": "Google Gemini (web)",
        "generation_parameters": "3.1 Pro, extended thinking ON "
                                 "(declared 'Rozszerzony - Myslenie rozszerzone')",
        "custom_gpt": False, "variant_of": None,
        "conditional": "run only if practical free access/quota satisfies "
                       "§5.1 (>= 1 full story per day or every other day)",
        "session_file": "05-gemini-3.1-Pro-rozszerzony.md",
    },
    {
        "provider": "deepseek", "model": "deepseek-v3-instant",
        "model_version": "deepthinkoff",
        "label": "DeepSeek V3 Instant — DeepThink OFF", "interface": "DeepSeek chat (web)",
        "generation_parameters": "DeepSeek-V3-Instant, DeepThink OFF",
        "custom_gpt": False, "variant_of": None, "conditional": "",
        "session_file": "06-deepseek-v3-instant-deepthinkoff.md",
    },
    {
        "provider": "deepseek", "model": "deepseek-v3-instant",
        "model_version": "deepthinkon",
        "label": "DeepSeek V3 Instant — DeepThink ON", "interface": "DeepSeek chat (web)",
        "generation_parameters": "DeepSeek-V3-Instant, DeepThink ON",
        "custom_gpt": False, "variant_of": "deepthinkoff", "conditional": "",
        "session_file": "07-deepseek-v3-instant-deepthinkon.md",
    },
    {
        "provider": "xai", "model": "grok", "model_version": "unknown",
        "label": "Grok", "interface": "Grok (web)",
        "generation_parameters": "unknown", "custom_gpt": False,
        "variant_of": None, "conditional": "",
        "session_file": "08-grok-unknown.md",
    },
    {
        "provider": "moonshot", "model": "kimi", "model_version": "k2.6-instant",
        "label": "Kimi K2.6 Instant (Standard)", "interface": "Kimi (web)",
        "generation_parameters": "K2.6 Instant (Standard)",
        "custom_gpt": False, "variant_of": None, "conditional": "",
        "session_file": "09-kimi-unknown.md",
    },
    {
        "provider": "alibaba", "model": "qwen-3.8-max", "model_version": "thinking",
        "label": "Qwen 3.8 Max — Thinking", "interface": "Qwen Chat (web)",
        "generation_parameters": "Qwen3.8-Max (Thinking)",
        "custom_gpt": False, "variant_of": None, "conditional": "",
        "session_file": "10-qwen-3.8-Max-Thinking.md",
    },
    {
        "provider": "zhipu", "model": "glm", "model_version": "4.5",
        "label": "GLM 4.5", "interface": "Zhipu GLM (web)",
        "generation_parameters": "GLM 4.5 (default)",
        "custom_gpt": False, "variant_of": None,
        "conditional": "run only if practical web access satisfies the "
                       "project filter (§5.1/D-036)",
        "session_file": "11-glm-unknown.md",
    },
    {
        "provider": "anthropic", "model": "claude", "model_version": "sonnet-5-max",
        "label": "Claude Sonnet 5 — max (long reasoning)", "interface": "Claude (web)",
        "generation_parameters": "Sonnet 5 max (intensive reasoning)",
        "custom_gpt": False, "variant_of": "sonnet-5", "conditional": "",
        "session_file": "12-claude-sonnet-5-max.md",
    },
    {
        "provider": "google", "model": "gemini-3.6-flash", "model_version": "extthinkoff",
        "label": "Gemini 3.6 Flash — extended thinking OFF", "interface": "Google Gemini (web)",
        "generation_parameters": "3.6 Flash, extended thinking OFF",
        "custom_gpt": False, "variant_of": None, "conditional": "",
        "session_file": "13-gemini-3.6-Flash-myslenierozszerzoneoff.md",
    },
    {
        "provider": "google", "model": "gemini-3.6-flash", "model_version": "extthinkon",
        "label": "Gemini 3.6 Flash — extended thinking ON", "interface": "Google Gemini (web)",
        "generation_parameters": "3.6 Flash, extended thinking ON",
        "custom_gpt": False, "variant_of": "extthinkoff", "conditional": "",
        "session_file": "14-gemini-3.6-Flash-myslenierozszerzoneon.md",
    },
    {
        "provider": "deepseek", "model": "deepseek-v3-expert",
        "model_version": "deepthinkoff",
        "label": "DeepSeek V3 Expert — DeepThink OFF", "interface": "DeepSeek chat (web)",
        "generation_parameters": "DeepSeek-V3-Expert, DeepThink OFF",
        "custom_gpt": False, "variant_of": None, "conditional": "",
        "session_file": "15-deepseek-v4-pro-deepthinkoff.md",
    },
    {
        "provider": "deepseek", "model": "deepseek-v3-expert",
        "model_version": "deepthinkon",
        "label": "DeepSeek V3 Expert — DeepThink ON", "interface": "DeepSeek chat (web)",
        "generation_parameters": "DeepSeek-V3-Expert, DeepThink ON",
        "custom_gpt": False, "variant_of": "deepthinkoff", "conditional": "",
        "session_file": "16-deepseek-v4-pro-deepthinkon.md",
    },
    {
        "provider": "alibaba", "model": "qwen-3.7-plus", "model_version": "thinking",
        "label": "Qwen 3.7 Plus — Thinking", "interface": "Qwen Chat (web)",
        "generation_parameters": "Qwen3.7-Plus (Thinking)",
        "custom_gpt": False, "variant_of": None, "conditional": "",
        "session_file": "17-qwen-3.7-Plus-Thinking.md",
    },
    {
        "provider": "alibaba", "model": "qwen-3.7-plus", "model_version": "fast",
        "label": "Qwen 3.7 Plus — Fast", "interface": "Qwen Chat (web)",
        "generation_parameters": "Qwen3.7-Plus (Fast)",
        "custom_gpt": False, "variant_of": "thinking", "conditional": "",
        "session_file": "18-qwen-3.7-Plus-Fast.md",
    },
    {
        "provider": "alibaba", "model": "qwen-3.8-max", "model_version": "fast",
        "label": "Qwen 3.8 Max — Fast", "interface": "Qwen Chat (web)",
        "generation_parameters": "Qwen3.8-Max (Fast)",
        "custom_gpt": False, "variant_of": "thinking", "conditional": "",
        "session_file": "19-qwen-3.8-Max-Fast.md",
    },
]

# ---------------------------------------------------------------------------
# Exploratory Phase-1 DIRECT baselines (SODA Task 022, 2026-09-07) — NOT
# part of the reconciled 19-row executed roster and never merged into it.
#
# During manual Phase-2A execution the author discovered a model/service
# recorded as "Dola 3.8" (Fast = run 20, Pro = run 21) on the ByteDance web
# interface (see run_exp004_phase2a.EXPLORATORY_ROWS, Task 021). Those two
# Phase-2A primed runs exist and are valid, but they have no Phase-1 direct
# baseline. Task 022 prepares those baselines RETROSPECTIVELY with the
# identical Phase-1 direct protocol: same base instruction + same Polish
# source story, fresh session, direct translation only, no corpus/scaffold/
# dictionary/morphology content. Identity is author-recorded in operator
# prompt headers only and is not independently verifiable; the rows are
# exploratory and stay pending manual collection (extend-direct never
# fabricates outputs or metrics). run_number keeps the author's 20/21
# numbering; session_file is the suggested future author session filename.
# ---------------------------------------------------------------------------
DOLA_IDENTITY_NOTE = (
    "Author-recorded in the operator prompt headers only (ByteDance — "
    "official web interface; 'proprietary closed-source, decoder-only "
    "transformer architecture — default settings'); template copied from "
    "the Qwen-3.8-Max-THINKING kit prompts. Not independently verifiable "
    "from provider metadata or UI exports. Exploratory configuration: at "
    "Task 021 it had no Phase-1 baseline; Task 022 prepares a Phase-1 "
    "direct baseline retrospectively (pending manual collection).")
DIRECT_EXPLORATORY_ROWS = [
    {
        "provider": "bytedance", "model": "dola-3.8", "model_version": "fast",
        "label": "Dola 3.8 — Fast",
        "interface": "ByteDance — official web interface",
        "generation_parameters": "proprietary closed-source, decoder-only "
        "transformer architecture — default settings",
        "custom_gpt": False, "variant_of": None, "conditional": "",
        "exploratory": True, "run_number": 20,
        "session_file": "20-dola-3.8-Fast.md",
        "identity_note": DOLA_IDENTITY_NOTE,
    },
    {
        "provider": "bytedance", "model": "dola-3.8", "model_version": "pro",
        "label": "Dola 3.8 — Pro",
        "interface": "ByteDance — official web interface",
        "generation_parameters": "proprietary closed-source, decoder-only "
        "transformer architecture — default settings",
        "custom_gpt": False, "variant_of": None, "conditional": "",
        "exploratory": True, "run_number": 21,
        "session_file": "21-dola-3.8-Pro.md",
        "identity_note": DOLA_IDENTITY_NOTE,
    },
]

STATUSES = ("collected_external_output", "collected_partial_output",
            "failed_external_output")
ACCESS_VERDICTS = ("pass", "fail", "unknown")
RUN_ID_FIELDS = ("date", "provider", "model", "model_version", "condition")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def run_id_for(date: str, row: dict) -> str:
    return (f"{date}__{row['provider']}__{row['model']}__"
            f"{row['model_version']}__{CONDITION}")


def parse_run_id(run_id: str) -> dict:
    parts = run_id.split("__")
    if len(parts) != 5:
        raise ValueError(
            f"run id must be <date>__<provider>__<model>__<model_version>__"
            f"direct, got: {run_id!r}")
    return dict(zip(RUN_ID_FIELDS, parts))


def roster_entry(run_id: str) -> dict | None:
    try:
        parts = parse_run_id(run_id)
    except ValueError:
        return None
    for pool in (ROSTER, DIRECT_EXPLORATORY_ROWS):
        for row in pool:
            if (row["provider"] == parts["provider"]
                    and row["model"] == parts["model"]
                    and row["model_version"] == parts["model_version"]):
                return row
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


def resource_versions() -> dict:
    versions: dict = {
        "evaluator_commit": git_commit(),
        "dictionary_manifest": (json.loads(
            DEFAULT_MANIFEST.read_text(encoding="utf-8"))
            if DEFAULT_MANIFEST.is_file() else None),
        "dictionary_lexicon": {
            "path": str(DEFAULT_LEXICON),
            "bytes": (DEFAULT_LEXICON.stat().st_size
                      if DEFAULT_LEXICON.is_file() else 0),
            "sha256": (sha256_file(DEFAULT_LEXICON)
                       if DEFAULT_LEXICON.is_file() else None),
        },
        "orthography_inventory": "src/isv_eval/orthography.py (official "
                                 "Interslavic alphabet; D-040)",
        "base_instruction": {
            "file": "experiments/exp004-modelscreen/base_instruction.txt",
            "sha256": (sha256_file(BASE_INSTRUCTION)
                       if BASE_INSTRUCTION.is_file() else None),
        },
    }
    return versions


# ---------------------------------------------------------------------------
# prepare
# ---------------------------------------------------------------------------

def _ensure_source(date: str, force: bool = False) -> Path:
    """Provision the local story source (byte-identical EXP-003 copy)."""
    source = INPUT_DIR / "source.txt"
    meta = INPUT_DIR / "source.meta.json"
    if source.is_file():
        actual = sha256_file(source)
        if actual != EXP003_SOURCE_SHA256:
            raise RuntimeError(
                f"{source} exists but sha256 {actual[:16]}... does not match "
                f"the canonical EXP-003 source {EXP003_SOURCE_SHA256[:16]}...; "
                "refusing to proceed with a different source")
        return source
    if not EXP003_SOURCE.is_file():
        raise RuntimeError(
            f"canonical source missing at {EXP003_SOURCE}; provide it first")
    if sha256_file(EXP003_SOURCE) != EXP003_SOURCE_SHA256:
        raise RuntimeError("EXP-003 source does not match its recorded hash")
    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(EXP003_SOURCE, source)
    (INPUT_DIR / "source.meta.json").write_text(json.dumps({
        "experiment_id": "exp004",
        "story_id": "op-pl",
        "filename": "source.txt",
        "sha256": sha256_file(source),
        "size_bytes": source.stat().st_size,
        "derivation": {
            "from": str(EXP003_SOURCE),
            "from_sha256": EXP003_SOURCE_SHA256,
            "note": "Byte-identical copy of the EXP-003 canonical story-only "
                    "source (itself cleaned from "
                    "experiments/exp001-baseline/input/source.txt; see "
                    "exp003 input/source.meta.json). Story text only "
                    "(title, headings, body, KONIEC marker).",
        },
        "copyright_note": "Project Owner owns the story and permits its use "
                          "in this project; keep local, do not commit or "
                          "redistribute.",
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    return source


def _prompt_filename(row: dict) -> str:
    nn = ROSTER.index(row) + 1
    return f"{nn:02d}-{row['model']}-{row['model_version']}.md"


def _render_prompt(row: dict, source_text: str,
                   extra_operator_lines: tuple = ()) -> str:
    """Canonical Phase-1 direct prompt. extra_operator_lines are additional
    '> ' header lines for the operator (e.g. Task-022 Dola baseline notes);
    they sit in the editable header region only, so the instruction+source
    body stays byte-identical across every direct baseline."""
    setting = row["generation_parameters"]
    cond = f"conditional filter: {row['conditional']}" if row[
        "conditional"] else "no conditional filter"
    lines = [
        f"# EXP-004 — Phase 1 — direct baseline — {row['label']}",
        "",
        "> COPY THIS ENTIRE FILE INTO " + row["interface"] + ".",
        "> Do not modify anything. Save the model's complete reply",
        "> byte-for-byte and hand it to the collect step.",
    ]
    for note in extra_operator_lines:
        lines.append("> " + note)
    lines += [
        "",
        "---",
        "",
        "Experiment ID: EXP-004",
        "Phase: 1 (practical model screening)",
        f"Target model: {row['label']}",
        f"Provider / interface: {row['provider']} / {row['interface']}",
        f"Model version / settings: {row['model_version']} ({setting})",
        f"Condition: {CONDITION} (no guidance — no scaffold, no candidates, "
        "no morphology/POS, no grammar notes, no evaluator feedback)",
        cond,
        "",
        "---",
        "",
        BASE_INSTRUCTION.read_text(encoding="utf-8").replace(
            "{STORY}", source_text).rstrip() + "\n",
    ]
    return "\n".join(lines)


def run_prepare(date: str, force: bool = False) -> int:
    if not date:
        print("error: --date YYYY-MM-DD is required (run ids carry the "
              "planned generation date)", file=sys.stderr)
        return 2
    if not BASE_INSTRUCTION.is_file():
        print(f"error: base instruction missing: {BASE_INSTRUCTION}",
              file=sys.stderr)
        return 2
    source = _ensure_source(date)
    source_text = source.read_text(encoding="utf-8")
    source_sha = sha256_bytes(source_text.encode("utf-8"))

    plan_path = OUTPUTS_DIR / "plan.json"
    if plan_path.is_file() and not force:
        print(f"error: {plan_path} already exists; use --force to rewrite "
              "(changing the plan invalidates collected runs)",
              file=sys.stderr)
        return 2

    OPERATOR_PROMPTS.mkdir(parents=True, exist_ok=True)
    files = []
    runs = []
    for row in ROSTER:
        fname = _prompt_filename(row)
        path = OPERATOR_PROMPTS / fname
        prompt_text = _render_prompt(row, source_text)
        prompt_sha = sha256_bytes(prompt_text.encode("utf-8"))
        if path.is_file() and not force:
            if sha256_bytes(path.read_bytes()) != prompt_sha:
                print(f"error: {path} exists with different content; "
                      "--force to overwrite", file=sys.stderr)
                return 2
        path.write_text(prompt_text, encoding="utf-8")
        run_id = run_id_for(date, row)
        files.append({"file": fname, "run_id": run_id,
                      "prompt_sha256": prompt_sha,
                      "bytes": len(prompt_text.encode("utf-8"))})
        runs.append({
            "run_id": run_id,
            "provider": row["provider"],
            "model": row["model"],
            "model_version": row["model_version"],
            "label": row["label"],
            "interface": row["interface"],
            "generation_parameters": row["generation_parameters"],
            "custom_gpt": row["custom_gpt"],
            "variant_of": row["variant_of"],
            "conditional": row["conditional"],
            "session_file": row["session_file"],
            "condition": CONDITION,
            "prompt_file": (str(path.relative_to(ROOT))
                            if path.is_relative_to(ROOT)
                            else str(path)),
            "prompt_sha256": prompt_sha,
            "source_sha256": source_sha,
        })

    manifest = {
        "artifact": "operator-prompt-manifest",
        "experiment_id": "exp004",
        "date": date,
        "generator": "scripts/run_exp004_phase1.py prepare",
        "generator_commit": git_commit(),
        "note": "Prompt files embed the copyrighted story and stay local "
                "(gitignored); this manifest records prompt hashes only.",
        "files": files,
    }
    (OPERATOR_PROMPTS / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    plan = {
        "experiment_id": "exp004",
        "artifact": "run-plan",
        "phase": "1",
        "date": date,
        "generator": "scripts/run_exp004_phase1.py prepare",
        "generator_commit": git_commit(),
        "source": {"file": (str(source.relative_to(ROOT))
                            if source.is_relative_to(ROOT)
                            else str(source)),
                   "sha256": source_sha,
                   "bytes": source.stat().st_size},
        "note": "Fixed Phase-1 roster (clean direct-translation baseline). "
                "LLM execution is external; this plan never calls an LLM.",
        "runs": runs,
    }
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    plan_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2),
                         encoding="utf-8")
    print(f"[prepare] prompts -> {OPERATOR_PROMPTS}/")
    print(f"[prepare] plan     -> {plan_path}")
    for r in runs:
        print(f"  {r['run_id']:64s} prompt {r['prompt_sha256'][:12]}")
    print(f"{len(runs)} planned run(s); source sha256 {source_sha[:16]}...")
    return 0


# ---------------------------------------------------------------------------
# extend-direct (SODA Task 022: retrospective Phase-1 direct baselines for
# the exploratory Dola 3.8 configurations — runs 20/21)
# ---------------------------------------------------------------------------

def _direct_prompt_filename(row: dict) -> str:
    """Prompt file name following the NN-model-model_version.md convention
    with the author's run number (20/21) as NN."""
    return (f"{row['run_number']:02d}-{row['model']}-"
            f"{row['model_version']}.md")


def _direct_operator_notes(row: dict, run_id: str) -> tuple[str, ...]:
    """Header-only operator notes for the Dola Phase-1 direct prompts. They
    make the task unambiguous to the author (which configuration, Phase-1
    direct baseline, fresh session, no priming material, exact run id to
    record) while the instruction+source body below stays byte-identical to
    every Phase-1 direct baseline of the original roster."""
    return (
        f"Exploratory Phase-1 DIRECT baseline for the Dola 3.8 "
        f"configuration '{row['label']}' (Phase-2A run "
        f"{row['run_number']}; SODA Task 022) — retrospective baseline, "
        "NOT part of the original 18-configuration roster.",
        "Open a NEW, FRESH session — never continue an earlier "
        "conversation (in particular not the Phase-2A primed session).",
        "This session must contain ONLY this single message: no reference "
        "text, no Medžuslovjansky examples, no dictionary material, no "
        "previous translation.",
        "Select exactly the configuration named in 'Target model' below "
        "in the interface before sending.",
        f"When the reply is complete, save it byte-for-byte; the planned "
        f"run id is {run_id}.",
    )


def run_extend_direct(date: str) -> int:
    """Append the exploratory Dola 3.8 Phase-1 DIRECT baseline rows (runs
    20/21) to outputs/plan.json, render their operator prompts into
    operator-prompts/ (same canonical Phase-1 direct template, byte-identical
    instruction+source body), and add their entries to
    operator-prompts/manifest.json — idempotently. Rows are marked
    exploratory and pending_manual_collection; nothing is collected or
    evaluated here. Do not re-run `prepare --force` afterwards: it would
    rewrite the plan/manifest from ROSTER only and drop these rows."""
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date or ""):
        print("error: --date YYYY-MM-DD is required (run ids carry the "
              "planned generation date)", file=sys.stderr)
        return 2
    plan_path = OUTPUTS_DIR / "plan.json"
    manifest_path = OPERATOR_PROMPTS / "manifest.json"
    if not plan_path.is_file() or not manifest_path.is_file():
        print("error: Phase-1 plan/manifest missing; run "
              "`scripts/run_exp004_phase1.py prepare --date YYYY-MM-DD` "
              "first", file=sys.stderr)
        return 2
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    if plan.get("source", {}).get("sha256") != EXP003_SOURCE_SHA256:
        print("error: plan source hash does not match the canonical "
              "EXP-003 source; refusing to extend a foreign plan",
              file=sys.stderr)
        return 2
    source = _ensure_source(date)
    source_text = source.read_text(encoding="utf-8")
    source_sha = sha256_bytes(source_text.encode("utf-8"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    existing_runs = {r["run_id"] for r in plan["runs"]}
    existing_files = {f["file"] for f in manifest["files"]}
    added_runs = added_files = 0
    for row in DIRECT_EXPLORATORY_ROWS:
        run_id = run_id_for(date, row)
        fname = _direct_prompt_filename(row)
        prompt_text = _render_prompt(
            row, source_text,
            _direct_operator_notes(row, run_id))
        prompt_sha = sha256_bytes(prompt_text.encode("utf-8"))
        path = OPERATOR_PROMPTS / fname
        if path.is_file():
            if sha256_bytes(path.read_bytes()) != prompt_sha:
                print(f"error: {path} exists with different content; "
                      "refusing to overwrite", file=sys.stderr)
                return 2
        else:
            path.write_text(prompt_text, encoding="utf-8")
        if run_id not in existing_runs:
            plan["runs"].append({
                "run_id": run_id,
                "provider": row["provider"],
                "model": row["model"],
                "model_version": row["model_version"],
                "label": row["label"],
                "interface": row["interface"],
                "generation_parameters": row["generation_parameters"],
                "custom_gpt": row["custom_gpt"],
                "variant_of": row["variant_of"],
                "conditional": row["conditional"],
                "session_file": row["session_file"],
                "condition": CONDITION,
                "prompt_file": (str(path.relative_to(ROOT))
                                if path.is_relative_to(ROOT)
                                else str(path)),
                "prompt_sha256": prompt_sha,
                "source_sha256": source_sha,
                "exploratory": True,
                "run_number": row["run_number"],
                "identity_note": row["identity_note"],
                "status": "pending_manual_collection",
            })
            existing_runs.add(run_id)
            added_runs += 1
        if fname not in existing_files:
            manifest["files"].append({
                "file": fname, "run_id": run_id,
                "prompt_sha256": prompt_sha,
                "bytes": len(prompt_text.encode("utf-8")),
                "exploratory": True,
            })
            existing_files.add(fname)
            added_files += 1
    if added_runs or added_files:
        manifest["files"] = sorted(manifest["files"],
                                   key=lambda f: f["file"])
        plan_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2),
                             encoding="utf-8")
        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2),
            encoding="utf-8")
    print(f"[extend-direct] plan runs +{added_runs} "
          f"(now {len(plan['runs'])}); manifest files +{added_files} "
          f"(now {len(manifest['files'])})")
    for row in DIRECT_EXPLORATORY_ROWS:
        print(f"  {run_id_for(date, row)}  "
              f"prompt {_direct_prompt_filename(row)}  "
              f"pending_manual_collection")
    return 0


# ---------------------------------------------------------------------------
# collect
# ---------------------------------------------------------------------------

def run_collect(run_id: str, output: Path, generation_date: str,
                model: str, provider: str, model_version: str,
                generation_parameters: str = "unknown",
                status: str = "collected_external_output",
                access_verdict: str = "unknown",
                access_note: str = "",
                note: str = "") -> int:
    row = roster_entry(run_id)
    if row is None:
        print(f"error: unknown run id {run_id!r} (not a Phase-1 roster row)",
              file=sys.stderr)
        return 2
    if status not in STATUSES:
        print(f"error: unknown status {status!r}", file=sys.stderr)
        return 2
    if access_verdict not in ACCESS_VERDICTS:
        print(f"error: unknown access verdict {access_verdict!r}",
              file=sys.stderr)
        return 2
    plan = load_plan()
    plan_entry = next((r for r in plan.get("runs", [])
                       if r["run_id"] == run_id), None)
    if plan_entry is None:
        print("error: run not in the plan; run "
              "`scripts/run_exp004_phase1.py prepare --date <date>` first",
              file=sys.stderr)
        return 2

    out_dir = OUTPUTS_DIR / run_id
    dst = out_dir / "output.txt"
    if dst.exists():
        print(f"error: {dst} already exists; refusing to overwrite "
              "(never overwrite an existing run)", file=sys.stderr)
        return 2
    if not output.is_file():
        print(f"error: output file not found: {output}", file=sys.stderr)
        return 2

    data = output.read_bytes()
    out_dir.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(data)  # byte-for-byte, never modified

    parts = parse_run_id(run_id)
    meta = {
        "run_id": run_id,
        "experiment_id": "exp004",
        "phase": "1",
        "condition": CONDITION,
        "label": row["label"],
        "interface": row["interface"],
        "model": model if model != "unknown" else row["model"],
        "provider": (provider if provider != "unknown"
                     else row["provider"]),
        "model_version": (model_version if model_version != "unknown"
                          else row["model_version"]),
        "generation_parameters": (generation_parameters
                                  if generation_parameters != "unknown"
                                  else row["generation_parameters"]),
        "generation_date": generation_date if generation_date != "unknown"
                           else parts["date"],
        "status": status,
        "access": {
            "filter_verdict": access_verdict,
            "quota_observed": access_note,
            "criteria": "D-036/§5.1: web/chat interface; free access with "
                        "practical quota >= 1 full story/day or every other "
                        "day; not a one-time trial; usable by the project "
                        "author. Observed by the operator at execution time.",
        },
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "collected_by": "scripts/run_exp004_phase1.py collect",
        "prompt": {"file": plan_entry["prompt_file"],
                   "sha256": plan_entry["prompt_sha256"]},
        "source": {"sha256": plan_entry["source_sha256"]},
        "output": {"file": str(dst), "sha256": sha256_bytes(data),
                   "bytes": len(data)},
        "resources": resource_versions(),
        "note": ("Raw LLM output stored byte-for-byte; never modified. "
                 "Empty or failed runs are preserved and documented, not "
                 "deleted." + (f" {note}" if note else "")),
    }
    (out_dir / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[collect] {run_id}")
    print(f"  label/interface: {row['label']} / {row['interface']}")
    print(f"  output sha256: {meta['output']['sha256']}")
    print(f"  status: {meta['status']}; access filter: "
          f"{meta['access']['filter_verdict']}")
    return 0


# ---------------------------------------------------------------------------
# collect-session (register a raw reply extracted from an author session file)
# ---------------------------------------------------------------------------

def run_collect_session(run_id: str, session: Path, generation_date: str,
                        model: str, provider: str, model_version: str,
                        generation_parameters: str = "unknown",
                        status: str = "collected_external_output",
                        access_verdict: str = "unknown",
                        access_note: str = "",
                        note: str = "") -> int:
    """Register the model reply embedded in an author session file.

    The author saved each external session as one markdown file: prompt
    header (possibly annotated) + unmodified instruction/source body + the
    model's raw reply appended after the prompt's closing '## Output' line
    (SODA Task 018). This function:

    - verifies the run is in the plan and the session file exists;
    - validates the session file's instruction+source body against the
      canonical prompt body for the run (byte-identical clean-baseline
      invariant; rejects altered instructions);
    - extracts the reply (everything after the '## Output\\n' marker),
      stored byte-for-byte as outputs/<run_id>/output.txt — never modified,
      never overwritten;
    - records meta.json with the canonical prompt hash, the session-file
      SHA-256 + name, the reply SHA-256, status, access verdict, and notes.
    """
    row = roster_entry(run_id)
    if row is None:
        print(f"error: unknown run id {run_id!r} (not a roster row)",
              file=sys.stderr)
        return 2
    if status not in STATUSES:
        print(f"error: unknown status {status!r}", file=sys.stderr)
        return 2
    if access_verdict not in ACCESS_VERDICTS:
        print(f"error: unknown access verdict {access_verdict!r}",
              file=sys.stderr)
        return 2
    plan = load_plan()
    plan_entry = next((r for r in plan.get("runs", [])
                       if r["run_id"] == run_id), None)
    if plan_entry is None:
        print("error: run not in the plan; run "
              "`scripts/run_exp004_phase1.py prepare --date <date>` first",
              file=sys.stderr)
        return 2
    if not session.is_file():
        print(f"error: session file not found: {session}", file=sys.stderr)
        return 2

    out_dir = OUTPUTS_DIR / run_id
    dst = out_dir / "output.txt"
    if dst.exists():
        print(f"error: {dst} already exists; refusing to overwrite "
              "(never overwrite an existing run)", file=sys.stderr)
        return 2

    # integrity: the session file must carry the canonical instruction body
    session_bytes = session.read_bytes()
    session_text = session_bytes.decode("utf-8", errors="replace")
    pf = OPERATOR_PROMPTS / Path(plan_entry["prompt_file"]).name
    canonical_text = pf.read_text(encoding="utf-8")
    if instruction_body(session_text) != instruction_body(canonical_text):
        print(f"error: session file's instruction body does not match the "
              f"canonical prompt for {run_id}; refusing to collect "
              "(altered instruction = broken clean-baseline invariant)",
              file=sys.stderr)
        return 2

    prefix, reply = split_session_reply(session_bytes)
    if not reply.strip():
        print(f"error: no model reply found after the '## Output' marker "
              f"in {session.name}", file=sys.stderr)
        return 2

    out_dir.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(reply)  # byte-for-byte raw reply, never modified

    parts = parse_run_id(run_id)
    meta = {
        "run_id": run_id,
        "experiment_id": "exp004",
        "phase": "1",
        "condition": CONDITION,
        "label": row["label"],
        "interface": row["interface"],
        "model": model if model != "unknown" else row["model"],
        "provider": (provider if provider != "unknown"
                     else row["provider"]),
        "model_version": (model_version if model_version != "unknown"
                          else row["model_version"]),
        "generation_parameters": (generation_parameters
                                  if generation_parameters != "unknown"
                                  else row["generation_parameters"]),
        "generation_date": generation_date if generation_date != "unknown"
                           else parts["date"],
        "status": status,
        "access": {
            "filter_verdict": access_verdict,
            "quota_observed": access_note,
            "criteria": "D-036/§5.1: web/chat interface; free access with "
                        "practical quota >= 1 full story/day or every other "
                        "day; not a one-time trial; usable by the project "
                        "author. Reconciled from the actual session evidence "
                        "(Task 018).",
        },
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "collected_by": "scripts/run_exp004_phase1.py collect-session",
        "prompt": {"file": plan_entry["prompt_file"],
                   "sha256": plan_entry["prompt_sha256"]},
        "source": {"sha256": plan_entry["source_sha256"]},
        "session": {
            "file": str(session),
            "name": session.name,
            "sha256": sha256_bytes(session_bytes),
            "reply_extracted_from": "suffix after the prompt's closing "
                                    "'## Output' line",
        },
        "output": {"file": str(dst), "sha256": sha256_bytes(reply),
                   "bytes": len(reply)},
        "resources": resource_versions(),
        "note": ("Raw model reply extracted from the author's session file "
                 "and stored byte-for-byte; never modified. The session file "
                 "itself is preserved unmodified under collected-sessions/."
                 + (f" {note}" if note else "")),
    }
    (out_dir / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[collect-session] {run_id}")
    print(f"  session: {session.name} -> output.txt "
          f"({len(reply)} B)")
    print(f"  output sha256: {meta['output']['sha256']}")
    print(f"  status: {meta['status']}; access filter: "
          f"{meta['access']['filter_verdict']}")
    return 0


# ---------------------------------------------------------------------------
# verify (integrity + structural completeness gate, L-027)
# ---------------------------------------------------------------------------

def _gate_checks(run_dir: Path, source_bytes: int,
                 size_floor: int) -> dict:
    output = run_dir / "output.txt"
    checks: dict = {}
    if not output.is_file():
        return {"verdict": "failed", "checks": {"file": False},
                "reasons": ["no output.txt"]}
    data = output.read_bytes()
    checks["non_empty"] = len(data) > 0
    checks["size_bytes"] = len(data)
    checks["size_floor"] = size_floor
    text = data.decode("utf-8", errors="replace")
    lines = text.splitlines()
    nonempty = [ln for ln in lines if ln.strip()]
    checks["head_sane"] = bool(nonempty) and len(nonempty[0].strip()) >= 10
    checks["end_marker"] = bool(nonempty) and bool(
        END_MARKER_RE.match(nonempty[-1]))
    folded = _fold_for_names(text)
    found = [name for name, stems in NAME_STEMS.items()
             if any(stem in folded for stem in stems)]
    checks["names_present"] = len(found)
    checks["names_required"] = 3
    reasons: list[str] = []
    if not checks["non_empty"]:
        reasons.append("empty output")
    if checks["non_empty"] and checks["size_bytes"] < size_floor:
        reasons.append(f"size {checks['size_bytes']} < floor {size_floor}")
    if checks["non_empty"] and not checks["head_sane"]:
        reasons.append("first non-empty line implausibly short "
                       "(service-error page?)")
    if not checks["end_marker"]:
        reasons.append("final non-empty line is not KONIEC/KONEC/KONĖC "
                       "(truncated?)")
    if checks["names_present"] < checks["names_required"]:
        reasons.append(f"only {checks['names_present']}/5 main story names "
                       "found (not a translation?)")
    return {"checks": checks, "reasons": reasons}


def _intake_verdict(gate: dict) -> str:
    reasons = gate.get("reasons", [])
    if not gate.get("checks", {}).get("non_empty", False):
        return "failed"
    # only hard failures that mean "not a usable translation"
    hard = [r for r in reasons if any(k in r for k in (
        "empty output", "implausibly short", "not a translation"))]
    if hard:
        return "failed"
    if any(r.startswith(("size", "final non-empty")) for r in reasons):
        return "partial"
    return "complete"


def _verify_integrity(run_id: str, plan_entry: dict | None) -> list[str]:
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
    if plan_entry is not None and meta:
        if meta.get("condition") != plan_entry["condition"]:
            errors.append("condition mismatch meta vs plan")
        if meta["prompt"].get("sha256") != plan_entry["prompt_sha256"]:
            errors.append("prompt hash differs from plan")
        if meta["source"].get("sha256") != plan_entry["source_sha256"]:
            errors.append("source hash differs from plan")
        pf = OPERATOR_PROMPTS / Path(meta["prompt"].get("file", "")).name
        if meta["prompt"].get("file") is None:
            errors.append("meta.json prompt has no file")
        elif not pf.is_file():
            errors.append(f"prompt file missing: {pf}")
        elif sha256_bytes(pf.read_bytes()) != meta["prompt"]["sha256"]:
            errors.append("prompt file content no longer matches recorded "
                          "hash")
    return errors


def run_verify(run_id: str | None = None, size_floor: int | None = None,
               no_plan: bool = False) -> int:
    plan = load_plan()
    runs: list[tuple[str, dict | None]] = []
    if run_id:
        runs.append((run_id, next((r for r in plan.get("runs", [])
                                   if r["run_id"] == run_id), None)))
    else:
        for r in plan.get("runs", []):
            runs.append((r["run_id"], r))
    if not runs:
        print("nothing to verify; prepare a plan first", file=sys.stderr)
        return 2

    source_bytes = 0
    src = plan.get("source")
    if src:
        sp = (Path(src["file"]) if Path(src["file"]).is_absolute()
              else ROOT / src["file"])
        source_bytes = sp.stat().st_size if sp.is_file() else 0
    problems = 0
    for rid, plan_entry in runs:
        out_dir = OUTPUTS_DIR / rid
        if not (out_dir / "output.txt").is_file():
            print(f"[skip] {rid}: no collected output")
            continue
        integrity = _verify_integrity(rid, None if no_plan else plan_entry)
        floor = size_floor if size_floor is not None else int(
            0.60 * source_bytes)
        gate = _gate_checks(out_dir, source_bytes, floor)
        verdict = _intake_verdict(gate)
        meta = load_meta(rid)
        intake = {
            "run_id": rid,
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
        # consistency between the recorded meta status and content verdict
        if verdict == "complete" and meta.get("status") == \
                "collected_partial_output":
            print("    note: content looks complete but meta.status says "
                  "collected_partial_output")
        if verdict == "partial" and meta.get("status") == \
                "collected_external_output":
            print("    note: content looks partial but meta.status says "
                  "collected_external_output")
    print(f"\n{len(runs)} planned run(s) checked.")
    return 1 if problems else 0


# ---------------------------------------------------------------------------
# evaluate
# ---------------------------------------------------------------------------

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
        print(f"[evaluate] no intake.json; running the completeness gate "
              f"first")
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
        "phase": "1",
        "condition": meta.get("condition"),
        "label": meta.get("label"),
        "model": meta.get("model"),
        "provider": meta.get("provider"),
        "model_version": meta.get("model_version"),
        "generation_parameters": meta.get("generation_parameters"),
        "intake_verdict": intake["verdict"],
        "usable": intake["verdict"] == "complete",
        "metrics": m,
        "output_files": report["output_files"],
    }
    (out_dir / "evaluation.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8")

    # orthographic sanity audit (independent dimension, Task 015 inventory)
    ortho = scan_file(text)
    od = ortho.as_dict()
    (out_dir / "orthography.json").write_text(json.dumps({
        "run_id": run_id,
        "inventory": "official Interslavic alphabet "
                     "(src/isv_eval/orthography.py, D-040)",
        "metrics": od,
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        f"# EXP-004 Phase 1 — evaluation — {run_id}",
        "",
        f"{meta.get('label', '?')} ({meta.get('provider')}, version "
        f"{meta.get('model_version')}) · generated "
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
    print(f"[evaluate] {run_id} (intake {intake['verdict']}, "
          f"usable {summary['usable']})")
    print(f"  canonical: {_pct(m['canonical_coverage'])}  "
          f"broader: {_pct(m['broader_resource_supported_coverage'])}  "
          f"unresolved: {_pct(m['unresolved_rate'])}")
    print(f"  orthography outside-inventory: {od['outside_inventory']} "
          f"(cyr {od['cyrillic']}, pol {od['polish_specific']}, "
          f"lat {od['other_latin']})")
    return 0


def _pct(v: float | None) -> str:
    return f"{v * 100:.2f}%" if v is not None else "n/a"


# ---------------------------------------------------------------------------
# status / roster
# ---------------------------------------------------------------------------

def run_status() -> int:
    plan = load_plan()
    if not plan.get("runs"):
        print("no plan; run `scripts/run_exp004_phase1.py prepare "
              "--date YYYY-MM-DD` first")
        return 0
    print(f"{'run_id':<66} {'output':<7} {'intake':<10} {'eval':<5} "
          f"{'usable':<7}")
    n_out = n_int = n_ev = n_us = 0
    for r in plan["runs"]:
        rid = r["run_id"]
        out_dir = OUTPUTS_DIR / rid
        has_out = (out_dir / "output.txt").is_file()
        intake = (out_dir / "intake.json")
        has_intake = intake.is_file()
        verdict = (json.loads(intake.read_text(encoding="utf-8"))
                   .get("verdict", "") if has_intake else "")
        has_ev = (out_dir / "evaluation.json").is_file()
        usable = False
        if has_ev:
            usable = json.loads((out_dir / "evaluation.json").read_text(
                encoding="utf-8")).get("usable", False)
        n_out += has_out
        n_int += has_intake
        n_ev += has_ev
        n_us += usable
        print(f"{rid:<66} {'yes' if has_out else 'no':<7} "
              f"{verdict or '-':<10} {'yes' if has_ev else 'no':<5} "
              f"{'yes' if usable else 'no':<7}")
    print(f"\n{len(plan['runs'])} planned; {n_out} collected; {n_int} "
          f"verified; {n_ev} evaluated; {n_us} usable (complete).")
    return 0


def run_roster() -> int:
    plan = load_plan()
    runs = plan.get("runs", [])
    if not runs:
        print("no plan; prepare first", file=sys.stderr)
        return 2
    rows = []
    for r in runs:
        rid = r["run_id"]
        out_dir = OUTPUTS_DIR / rid
        meta = load_meta(rid)
        intake_p = out_dir / "intake.json"
        ev_p = out_dir / "evaluation.json"
        ortho_p = out_dir / "orthography.json"
        row = {
            "run_id": rid,
            "label": r["label"],
            "provider": r["provider"],
            "model": r["model"],
            "model_version": r["model_version"],
            "generation_parameters": r["generation_parameters"],
            "interface": r["interface"],
            "conditional": r["conditional"],
            "collected": (out_dir / "output.txt").is_file(),
            "status": meta.get("status", None),
            "access": meta.get("access", {}),
            "intake_verdict": (json.loads(intake_p.read_text(
                encoding="utf-8")).get("verdict")
                if intake_p.is_file() else None),
            "intake_reasons": (json.loads(intake_p.read_text(
                encoding="utf-8")).get("reasons", [])
                if intake_p.is_file() else []),
            "metrics": (json.loads(ev_p.read_text(encoding="utf-8"))
                        .get("metrics") if ev_p.is_file() else None),
            "usable": (json.loads(ev_p.read_text(encoding="utf-8"))
                       .get("usable") if ev_p.is_file() else None),
            "orthography": (json.loads(ortho_p.read_text(
                encoding="utf-8")).get("metrics")
                if ortho_p.is_file() else None),
        }
        rows.append(row)
    out = {"experiment_id": "exp004", "phase": "1",
           "generator": "scripts/run_exp004_phase1.py roster",
           "note": "Metrics are separate evidence dimensions; no ranking "
                   "and no composite score.",
           "rows": rows}
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUTS_DIR / "roster.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = [
        "# EXP-004 Phase 1 — screening roster (clean direct baseline)",
        "",
        "| run | label | access | intake | usable | canon. | broader | "
        "unres. | tok | ortho out |",
        "|---|---|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        m = row["metrics"] or {}
        o = row["orthography"] or {}
        access = (row["access"] or {}).get("filter_verdict", "—")
        lines.append(
            f"| {row['run_id']} | {row['label']} | {access} | "
            f"{row['intake_verdict'] or '—'} | "
            f"{'yes' if row['usable'] else 'no'} | "
            f"{_pct(m.get('canonical_coverage')) if m else '—'} | "
            f"{_pct(m.get('broader_resource_supported_coverage')) if m else '—'} | "
            f"{_pct(m.get('unresolved_rate')) if m else '—'} | "
            f"{m.get('total_tokens', '—') if m else '—'} | "
            f"{o.get('outside_inventory', '—')} |")
    (OUTPUTS_DIR / "roster.md").write_text("\n".join(lines) + "\n",
                                           encoding="utf-8")
    print(f"[roster] wrote outputs/roster.json + roster.md "
          f"({len(rows)} rows; "
          f"{sum(1 for x in rows if x['usable'])} usable)")
    return 0


# ---------------------------------------------------------------------------
# cli
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p_prep = sub.add_parser("prepare", help="package prompts + write plan")
    p_prep.add_argument("--date", required=True, help="YYYY-MM-DD")
    p_prep.add_argument("--force", action="store_true")

    p_col = sub.add_parser("collect", help="register an external raw output")
    p_col.add_argument("--run", required=True, dest="run_id")
    p_col.add_argument("--output", required=True, type=Path)
    p_col.add_argument("--generation-date", default="unknown")
    p_col.add_argument("--model", default="unknown")
    p_col.add_argument("--provider", default="unknown")
    p_col.add_argument("--model-version", default="unknown")
    p_col.add_argument("--generation-parameters", default="unknown")
    p_col.add_argument("--status", default="collected_external_output",
                       choices=STATUSES)
    p_col.add_argument("--access-verdict", default="unknown",
                       choices=ACCESS_VERDICTS,
                       help="operator's practical free-access verdict "
                            "(D-036 filter), observed at execution time")
    p_col.add_argument("--access-note", default="",
                       help="free-access/quota observation (e.g. 'complete "
                            "in one free session')")
    p_col.add_argument("--note", default="",
                       help="observed facts about the reply "
                            "(e.g. truncation)")

    p_sec = sub.add_parser(
        "collect-session",
        help="register the raw reply embedded in an author session file "
             "(prompt + reply in one file, Task 018)")
    p_sec.add_argument("--run", required=True, dest="run_id")
    p_sec.add_argument("--session", required=True, type=Path,
                       help="author session file (prompt+reply, unmodified)")
    p_sec.add_argument("--generation-date", default="unknown")
    p_sec.add_argument("--model", default="unknown")
    p_sec.add_argument("--provider", default="unknown")
    p_sec.add_argument("--model-version", default="unknown")
    p_sec.add_argument("--generation-parameters", default="unknown")
    p_sec.add_argument("--status", default="collected_external_output",
                       choices=STATUSES)
    p_sec.add_argument("--access-verdict", default="unknown",
                       choices=ACCESS_VERDICTS)
    p_sec.add_argument("--access-note", default="")
    p_sec.add_argument("--note", default="")

    p_ver = sub.add_parser("verify", help="integrity + completeness gate")
    p_ver.add_argument("--run", default=None, dest="run_id")
    p_ver.add_argument("--size-floor", type=int, default=None)
    p_ver.add_argument("--no-plan", action="store_true")

    p_ev = sub.add_parser("evaluate", help="evaluate a collected output")
    p_ev.add_argument("--run", required=True, dest="run_id")
    p_ev.add_argument("--force", action="store_true")

    sub.add_parser("status", help="show run progress")
    sub.add_parser("roster", help="write the screening roster summary")
    p_ext = sub.add_parser(
        "extend-direct",
        help="append the exploratory Dola 3.8 Phase-1 DIRECT baseline rows "
             "(runs 20/21) to plan and manifest + render their operator "
             "prompts, idempotently (Task 022; pending manual collection)")
    p_ext.add_argument("--date", required=True, help="YYYY-MM-DD")
    args = parser.parse_args(argv)

    if args.command == "prepare":
        return run_prepare(args.date, args.force)
    if args.command == "extend-direct":
        return run_extend_direct(args.date)
    if args.command == "collect":
        return run_collect(args.run_id, args.output, args.generation_date,
                           args.model, args.provider, args.model_version,
                           args.generation_parameters, args.status,
                           args.access_verdict, args.access_note, args.note)
    if args.command == "collect-session":
        return run_collect_session(args.run_id, args.session,
                                   args.generation_date, args.model,
                                   args.provider, args.model_version,
                                   args.generation_parameters, args.status,
                                   args.access_verdict, args.access_note,
                                   args.note)
    if args.command == "verify":
        return run_verify(args.run_id, args.size_floor, args.no_plan)
    if args.command == "evaluate":
        return run_evaluate(args.run_id, args.force)
    if args.command == "status":
        return run_status()
    if args.command == "roster":
        return run_roster()
    return 2


if __name__ == "__main__":
    sys.exit(main())
