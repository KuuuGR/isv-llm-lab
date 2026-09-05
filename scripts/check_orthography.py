#!/usr/bin/env python3
"""EXP-001/002/003 character-level orthographic sanity audit (SODA Task 015).

Deterministic, read-only audit of every generated translation output:

- EXP-001  experiments/exp001-baseline/outputs/<run>/output.txt        (7 runs)
- EXP-002  experiments/exp002-pilot/outputs/<run>/revised.txt          (7 runs)
- EXP-003  experiments/exp003-scaffold/outputs/<run>/output.txt       (12 runs)
- EXP-004  experiments/exp004-modelscreen/outputs/<run>/output.txt   (Phase 1)

Uses the authoritative Interslavic letter inventory from the official
Interslavic website (see src/isv_eval/orthography.py). Text is NEVER
modified, transliterated, or repaired, and no lexical/resource coverage
number is recomputed or altered — character-level orthographic sanity is an
independent quality dimension, reported separately.

Writes, per experiment (all local/gitignored, under outputs/):
  orthography_report.json   — full per-file metrics + unexpected characters
  orthography_report.md     — human-readable summary
and prints a compact table to stdout. Deterministic: runs are processed in
sorted path order.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

EXPERIMENTS = {
    "exp001": {
        "dir": ROOT / "experiments" / "exp001-baseline" / "outputs",
        "label": "EXP-001",
        "globs": ("*/output.txt",),
    },
    "exp002": {
        "dir": ROOT / "experiments" / "exp002-pilot" / "outputs",
        "label": "EXP-002",
        "globs": ("*/revised.txt",),
    },
    "exp003": {
        "dir": ROOT / "experiments" / "exp003-scaffold" / "outputs",
        "label": "EXP-003",
        "globs": ("*/output.txt",),
    },
    "exp004": {
        "dir": ROOT / "experiments" / "exp004-modelscreen" / "outputs",
        "label": "EXP-004",
        "globs": ("*/output.txt",),
    },
}

sys.path.insert(0, str(ROOT / "src"))
from isv_eval.orthography import (ALPHABET_SOURCE_NOTE, ALPHABET_SOURCE_URL,
                                  scan_file)  # noqa: E402


def run_status(run_dir: Path) -> str | None:
    meta = run_dir / "meta.json"
    if not meta.exists():
        return None
    try:
        return json.loads(meta.read_text(encoding="utf-8")).get("status")
    except (json.JSONDecodeError, OSError):
        return None


def audit_experiment(cfg: dict) -> dict:
    out = {"experiment": cfg["label"],
           "alphabet_source": {"url": ALPHABET_SOURCE_URL,
                               "note": ALPHABET_SOURCE_NOTE},
           "files": []}
    seen: set[Path] = set()
    for pattern in cfg["globs"]:
        for path in sorted(cfg["dir"].glob(pattern)):
            if path in seen:
                continue
            seen.add(path)
            report = scan_file(path)
            try:
                rel = str(path.relative_to(ROOT))
            except ValueError:
                rel = str(path)
            entry = {
                "file": rel,
                "run_id": path.parent.name,
                "status": run_status(path.parent),
                "metrics": report.as_dict(),
            }
            out["files"].append(entry)
    # deterministic overall summary
    n_outside = [f for f in out["files"] if f["metrics"]["outside_inventory"]]
    out["summary"] = {
        "files_scanned": len(out["files"]),
        "files_with_outside_inventory_chars": len(n_outside),
    }
    return out


def render_md(result: dict) -> str:
    rows = ["| file | total | allowed | outside | cyr | pol | oth-lat | "
            "oth-script | oth-nonletter |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for f in result["files"]:
        m = f["metrics"]
        rows.append(
            f"| {f['run_id']} | {m['total_chars']} | {m['allowed_letters']} "
            f"| {m['outside_inventory']} | {m['cyrillic']} "
            f"| {m['polish_specific']} | {m['other_latin']} "
            f"| {m['other_script']} | {m['unexpected_nonletters']} |")
    lines = [
        f"# {result['experiment']} — character-level orthographic sanity report",
        "",
        "Alphabet source: " + result["alphabet_source"]["url"] + " — " +
        result["alphabet_source"]["note"],
        "",
        "Audit only: no text modified, no lexical/resource coverage "
        "recomputed.",
        "",
        "## Per-file metrics",
        "",
    ] + rows + ["", "## Unexpected characters", ""]
    for f in result["files"]:
        m = f["metrics"]
        if not m["unexpected"]:
            continue
        lines += [f"### {f['run_id']}", ""]
        for ch, d in m["unexpected"].items():
            loc = ", ".join(str(x) for x in d["lines"][:12])
            more = "" if len(d["lines"]) <= 12 else f" (+{len(d['lines']) - 12} lines)"
            lines.append(f"- `{ch}` (U+{ord(ch):04X}) {d['name']} — "
                         f"{d['category']}, x{d['count']}, lines {loc}{more}")
        lines.append("")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--experiments", nargs="*",
                    default=sorted(EXPERIMENTS),
                    choices=sorted(EXPERIMENTS),
                    help="which experiment outputs to audit (default: all)")
    args = ap.parse_args(argv)

    for key in args.experiments:
        cfg = EXPERIMENTS[key]
        result = audit_experiment(cfg)
        base = cfg["dir"]
        (base / "orthography_report.json").write_text(
            json.dumps(result, ensure_ascii=False, indent=2),
            encoding="utf-8")
        (base / "orthography_report.md").write_text(
            render_md(result), encoding="utf-8")
        print(f"[{result['experiment']}] {result['summary']['files_scanned']} "
              f"files; {result['summary']['files_with_outside_inventory_chars']} "
              "with characters outside the accepted inventory")
        for f in result["files"]:
            m = f["metrics"]
            if m["outside_inventory"]:
                print(f"  {f['run_id']}: outside={m['outside_inventory']} "
                      f"(cyr={m['cyrillic']} pol={m['polish_specific']} "
                      f"lat={m['other_latin']} script={m['other_script']} "
                      f"nonlet={m['unexpected_nonletters']})")
        print(f"  reports: {base / 'orthography_report.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
