#!/usr/bin/env python3
"""EXP-004 Phase 1 — audit + reconciliation of the collected operator files.

The project author executed the Phase 1 screening manually in external LLM
web/chat interfaces and saved each session as ONE markdown file under
operator-prompts/ whose content is: the (possibly edited) prompt header +
the unmodified instruction/source body + the model's raw reply appended
after the prompt's closing "## Output" line. Filenames and header lines were
annotated by hand and may contain mistakes or inconsistent naming (SODA
Task 018).

This script is READ-ONLY evidence gathering: it never modifies a collected
file. For every operator-prompts/*.md (excluding README.md/manifest.json) it:

- verifies the instruction+source body is byte-identical to the canonical
  package prompt body (the clean-baseline invariant: identical instruction
  and story for every row, no guidance content);
- locates the reply boundary (everything after the prompt's closing
  "## Output\\n\\n");
- extracts the raw reply bytes and reports their SHA-256, size, first/last
  non-empty lines, and end-marker presence (KONIEC/KONĖC);
- parses the declared model identity from the header (Target model /
  Model version / settings / Experiment ID lines) and the filename;
- matches the file to the canonical roster row(s) whose prompt body it
  carries (identity evidence independent of the author's naming);
- detects duplicate replies across files and files without a reply
  (error-page artifacts such as the GLM run).

Writes operator-prompts/collection_audit.json + .md (gitignored, local
evidence). Exit code 0 when every file has an identified canonical row body;
1 when a file's instruction body differs from all canonical prompts
(quarantine candidate).
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from run_exp004_phase1 import (BASE_INSTRUCTION, EXP, ROSTER, SESSION_DIR,  # noqa: E402
                               _render_prompt, instruction_body, sha256_bytes,
                               sha256_file, split_session_reply)

EXCLUDE = {"README.md", "manifest.json", "collection_audit.json",
           "collection_audit.md"}
END_MARKER_RE = re.compile(r"^\s*(KONIEC|KONEC|KONĖC)\s*$")
# the canonical prompt text for each roster row is derived deterministically
# from the same source story; bodies (instruction+story) are identical across
# rows, so identity is established by the header + filename, while the body
# check proves the instruction was not altered.


def canonical_prompts() -> dict[str, str]:
    """Regenerate the deterministic per-row canonical prompts (row number)."""
    source_text = (EXP / "input" / "source.txt").read_text(encoding="utf-8")
    out = {}
    for i, row in enumerate(ROSTER, start=1):
        out[f"{i:02d}"] = _render_prompt(row, source_text)
    return out


def split_reply(text: str) -> tuple[str, str, str]:
    """Split at the LAST '## Output' line that is followed by a blank line.
    The canonical prompt always ends with '## Output\\n\\n'; replies may not
    contain '## Output' themselves, so the last occurrence is the boundary
    between the prompt and the raw model reply."""
    idx = text.rfind("## Output\n")
    if idx < 0:
        return text, "", ""
    marker_end = idx + len("## Output")
    # consume the following blank line(s) that separate marker from reply
    rest = text[marker_end:]
    m = re.match(r"\n{1,3}", rest)
    if m:
        marker_end += m.end()
    return text[:idx], text[idx:marker_end], text[marker_end:]


def header_lines(text: str) -> dict[str, str]:
    """Parse the declared identity from the prompt header (author-typed)."""
    head = text.split("\n---\n", 2)
    block = head[1] if len(head) > 1 else head[0]
    fields = (("Experiment ID", "Experiment ID:"),
              ("Phase", "Phase:"),
              ("Target model", "Target model:"),
              ("Provider", "Provider / interface:"),
              ("Model version", "Model version / settings:"),
              ("Condition", "Condition:"),
              ("conditional filter", "conditional filter:"))
    out: dict[str, str] = {}
    for line in block.splitlines():
        for key, prefix in fields:
            if line.startswith(prefix):
                out[key] = line.split(":", 1)[1].strip()
    return out


def row_number_from_name(filename: str) -> str:
    m = re.match(r"(\d{2})-", filename)
    return m.group(1) if m else ""


def audit(session_dir: Path | None = None) -> dict:
    canon = canonical_prompts()
    scan_dir = session_dir or SESSION_DIR
    # canonical body per row (identical across rows by design)
    canon_body = {n: instruction_body(t) for n, t in canon.items()}
    # sanity: all canonical bodies identical
    bodies = list(canon_body.values())
    body_identity_ok = all(b == bodies[0] for b in bodies)

    entries = []
    for f in sorted(scan_dir.glob("*.md")):
        if f.name in EXCLUDE:
            continue
        raw = f.read_bytes()
        text = raw.decode("utf-8", errors="replace")
        prefix, marker, reply = split_reply(text)
        _, reply_bytes = split_session_reply(raw)
        ibody = instruction_body(text)
        # which canonical row does the instruction body belong to?
        matching_rows = [n for n, b in canon_body.items() if b == ibody]
        hdr = header_lines(text)
        ne = [ln for ln in reply.splitlines() if ln.strip()]
        reply_lines = len(ne)
        reply_first = ne[0].strip()[:80] if ne else ""
        reply_last = ne[-1].strip()[:80] if ne else ""
        entry = {
            "file": f.name,
            "filename_row": row_number_from_name(f.name),
            "declared": hdr,
            "instruction_body_matches_canonical": bool(matching_rows),
            "canonical_rows_matching_body": matching_rows,
            "reply": {
                "present": bool(reply_bytes.strip()),
                "bytes": len(reply_bytes),
                "sha256": sha256_bytes(reply_bytes),
                "nonempty_lines": len(
                    [ln for ln in reply.splitlines() if ln.strip()]),
                "first_nonempty": reply_first,
                "last_nonempty": reply_last,
                "end_marker": bool(ne) and bool(END_MARKER_RE.match(ne[-1])),
            },
            "prompt_prefix_sha256": sha256_bytes(
                prefix.encode("utf-8")),
        }
        entries.append(entry)

    # duplicate-reply detection across files
    by_hash: dict[str, list[str]] = {}
    for e in entries:
        by_hash.setdefault(e["reply"]["sha256"], []).append(e["file"])
    dups = {h: files for h, files in by_hash.items() if len(files) > 1}

    result = {
        "experiment_id": "exp004",
        "artifact": "collection-audit",
        "phase": "1",
        "generator": "scripts/audit_exp004_collected.py",
        "scan_dir": str(scan_dir),
        "note": "Read-only audit of the author-collected session files "
                "(collected-sessions/, Task 018). Raw files are never "
                "modified.",
        "canonical_body_identical_across_rows": body_identity_ok,
        "files": entries,
        "duplicate_replies": dups,
        "summary": {
            "files_scanned": len(entries),
            "files_with_reply": sum(1 for e in entries
                                    if e["reply"]["present"]),
            "files_with_end_marker": sum(1 for e in entries
                                         if e["reply"]["end_marker"]),
            "files_with_noncanonical_body": [e["file"] for e in entries
                                             if not e[
                    "instruction_body_matches_canonical"]],
            "duplicate_reply_groups": len(dups),
        },
    }
    (scan_dir / "collection_audit.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# EXP-004 Phase 1 — collection audit (reconciliation evidence)",
        "",
        "Read-only audit of the author-collected session files (Task 018). "
        "Raw files are never modified.",
        "",
        "| file | row# | declared model (header) | body ok | reply | end | sha256 |",
        "|---|---|---|---|---:|---|---|",
    ]
    for e in entries:
        d = e["declared"]
        model = d.get("Target model", "?")[:38]
        lines.append(
            f"| {e['file']} | {e['filename_row']} | {model} | "
            f"{'yes' if e['instruction_body_matches_canonical'] else 'NO'} | "
            f"{e['reply']['bytes']} B | "
            f"{'yes' if e['reply']['end_marker'] else 'no'} | "
            f"{e['reply']['sha256'][:12]} |")
    lines += ["", "## Duplicate replies", ""]
    if dups:
        for h, files in dups.items():
            lines.append(f"- `{h[:12]}`: {', '.join(files)}")
    else:
        lines.append("none")
    (scan_dir / "collection_audit.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8")

    for e in entries:
        flag = "OK " if e["instruction_body_matches_canonical"] else "BODY?"
        print(f"[{flag}] {e['file']} reply={e['reply']['bytes']}B "
              f"end={'Y' if e['reply']['end_marker'] else 'N'} "
              f"sha={e['reply']['sha256'][:12]} "
              f"rows={len(e['canonical_rows_matching_body'])}")
    print(f"\n{result['summary']['files_scanned']} file(s); "
          f"{result['summary']['files_with_reply']} with reply; "
          f"duplicate groups: {len(dups)}; "
          f"body mismatches: "
          f"{len(result['summary']['files_with_noncanonical_body'])}")
    return result


def main(argv: list[str] | None = None) -> int:
    result = audit()
    if result["summary"]["files_with_noncanonical_body"]:
        print("error: at least one file has a non-canonical instruction "
              "body; quarantine it before proceeding", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
