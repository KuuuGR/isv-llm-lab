#!/usr/bin/env python3
"""EXP-004 authentic-corpus self-evaluation (SODA Task 029, 2026-09-09).

Question:

> How does the authentic Medžuslovjansky corpus score when evaluated
> against the same lexical resources, canonical evaluator and orthography
> audit used for generated model outputs?

The model outputs of EXP-004 (Phase 1 direct, Phase 2A primed, controlled
repeats) are measured with resource-based metrics
(`isv-eval`, unchanged since Task 008) plus the Task-015 orthography
audit. This script applies the EXACT same deterministic stack to the
authentic reference corpus itself:

  - combined corpus  `phase2a/corpus/phase2a-authentic-isv-corpus.txt`
    (the exact bytes presented to models in Phase 2A Prompt 1 — including
    the three `=== REGISTER n: ... ===` plain-text section headers);
  - Register 1 — literary / narrative  (`tuta-historija-excerpt.txt`);
  - Register 2 — artistic / poetic     (`album-ahoj-slovjani-artistic-isv.txt`);
  - Register 3 — informative / encyclopedic (`wiki-sadovnistvo-encyclopedic-isv.txt`).

The register files are the byte-exact register components consumed by the
corpus builder (headers exist only in the combined file), so per-register
self-evaluation preserves the register boundaries exactly as established
in Phase 2A.

WHAT THIS IS NOT (recorded, never claimed):

  - the evaluator measures resource coverage, not linguistic correctness;
  - the corpus is NOT a perfect upper bound on Interslavic — it is one
    authentic corpus assembled from three registers;
  - no special "corpus score", no composite score, no quality ranking;
  - proper-name and sanctioned forms are handled by the established audit
    policy; nothing is "fixed".

The result is a reference point for interpreting model coverage: a
reference ceiling/benchmark for the chosen evaluator, evidence about
evaluator/resource mismatch, evidence about whether low model coverage
could partly arise from resource limitations, and information about
whether the three-register corpus expands lexical coverage.

Outputs (deterministic; generated locally from the gitignored corpus):

  experiments/exp004-modelscreen/phase2a/corpus-selfeval/
    corpus_selfeval.json   machine-readable metrics + orthography
    corpus_selfeval.md     corpus tables + cross-register composition
    model_comparison.md    descriptive corpus-vs-model-outputs table
    README.md              method + interpretation (committed)

Cross-register composition uses only the per-token classifications and
broader-resource flags already produced by the unmodified `isv-eval` CLI
(`tokens.json`) — no evaluator change, no new resource lookups.

Model-output comparison reads the local (gitignored) EXP-004 rosters when
present; rows are omitted with a note otherwise. Comparison is
descriptive resource-coverage comparison only — never "distance from
native quality", never "model reached corpus % therefore as good as the
corpus".
"""

from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(ROOT / "src"))

from isv_eval.orthography import scan_file  # noqa: E402

EXP = ROOT / "experiments" / "exp004-modelscreen"
CORPUS_DIR = EXP / "phase2a" / "corpus"
OUT_DIR = EXP / "phase2a" / "corpus-selfeval"
SCRATCH_DIR = OUT_DIR / ".scratch"  # CLI artifacts; never committed

CORPUS_SHA256 = "aaad28e43935a40313585d77a33bfc788d97e8d69b081f9486af74d52ca1a857"

DATASETS = [
    {
        "id": "combined",
        "label": "Combined authentic corpus",
        "register": None,
        "file": CORPUS_DIR / "phase2a-authentic-isv-corpus.txt",
        "sha256": CORPUS_SHA256,
    },
    {
        "id": "register1",
        "label": "Register 1 — literary / narrative",
        "register": 1,
        "file": CORPUS_DIR / "tuta-historija-excerpt.txt",
    },
    {
        "id": "register2",
        "label": "Register 2 — artistic / poetic",
        "register": 2,
        "file": CORPUS_DIR / "album-ahoj-slovjani-artistic-isv.txt",
    },
    {
        "id": "register3",
        "label": "Register 3 — informative / encyclopedic",
        "register": 3,
        "file": CORPUS_DIR / "wiki-sadovnistvo-encyclopedic-isv.txt",
    },
]

# The task-029 §12 comparison table columns.
TABLE_HEADER = ("| Dataset | Tokens | Canonical | Broader | Unresolved | "
                "Orthography out |")
TABLE_HEADER_SEP = ("|---|---:|---:|---:|---:|---:|")

REGISTER_MD_TITLE = {
    1: "Register 1 — literary / narrative (`Tuta historija`)",
    2: "Register 2 — artistic / poetic (album *Ahoj, Slovjani!*)",
    3: "Register 3 — informative / encyclopedic (Wikipedia *Sadovničstvo*)",
}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


# ---------------------------------------------------------------------------
# deterministic evaluation (identical stack to EXP-004 output evaluation)
# ---------------------------------------------------------------------------

def run_isv_eval_cli(text_path: Path, out_dir: Path) -> None:
    """The unmodified `python -m isv_eval.cli` evaluation call (same as
    `run_exp004_repeats.py evaluate`)."""
    cmd = [sys.executable, "-m", "isv_eval.cli", str(text_path),
           "--out", str(out_dir)]
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(
            f"isv-eval failed on {text_path}: {proc.stderr[-500:]}")


def evaluate_dataset(ds: dict, scratch: Path, reuse: bool = False) -> dict:
    path = ds["file"]
    actual = sha256_file(path)
    if ds.get("sha256") and actual != ds["sha256"]:
        raise RuntimeError(
            f"{path} sha256 {actual[:16]}... does not match the recorded "
            f"corpus {ds['sha256'][:16]}... (fail loudly; corpus edits "
            "are a new corpus version, never a silent fix)")
    work = scratch / ds["id"]
    work.mkdir(parents=True, exist_ok=True)
    report_path = work / "report.json"
    tokens_path = work / "tokens.json"
    if reuse and report_path.is_file() and tokens_path.is_file():
        report = json.loads(report_path.read_text(encoding="utf-8"))
        tokens = json.loads(tokens_path.read_text(encoding="utf-8"))
    else:
        run_isv_eval_cli(path, work)
        report = json.loads(report_path.read_text(encoding="utf-8"))
        tokens = json.loads(tokens_path.read_text(encoding="utf-8"))
    ortho = scan_file(path).as_dict()
    metrics = report["metrics"]
    return {
        "dataset_id": ds["id"],
        "label": ds["label"],
        "register": ds["register"],
        "file": _rel(path),
        "sha256": actual,
        "bytes": path.stat().st_size,
        "evaluator": report["evaluator"],
        "metrics": metrics,
        "orthography": ortho,
        "tokens": tokens,  # per-token classifications (for composition)
    }


# ---------------------------------------------------------------------------
# cross-register vocabulary composition (exploratory, NOT a quality score)
# ---------------------------------------------------------------------------

def _surface_stats(tokens: list) -> dict:
    """Per unique lexical surface (normalized): support status across all
    its occurrences (canonical if any A/B occurrence; broader if any
    occurrence is canonical-supported or broader_resource_supported;
    else unresolved)."""
    per = {}
    for t in tokens:
        if not t.get("is_lexical"):
            continue
        surface = t.get("normalized") or t.get("folded") or t.get("token")
        cls = t.get("classification")
        if surface is None or cls in (None, "non_lexical"):
            continue
        status = per.setdefault(surface, {"n": 0, "canonical": False,
                                          "broader": False})
        status["n"] += 1
        if cls in ("A", "B"):
            status["canonical"] = True
            status["broader"] = True
        elif t.get("broader_resource_supported"):
            status["broader"] = True
    return per


def register_surface_set(tokens: list) -> set:
    return set(_surface_stats(tokens))


def cross_register(records: list) -> dict:
    regs = {r["register"]: r for r in records if r["register"] is not None}
    surfaces = {k: register_surface_set(v["tokens"])
                for k, v in sorted(regs.items())}
    names = {k: (regs[k].get("label") or f"Register {k}")
             for k in surfaces}
    pair = {}
    keys = sorted(surfaces)
    for i, a in enumerate(keys):
        for b in keys[i + 1:]:
            key = f"{a}_x_{b}"
            pair[key] = {
                "registers": [a, b],
                "shared_surfaces": len(surfaces[a] & surfaces[b]),
                "only_in_first": len(surfaces[a] - surfaces[b]),
                "only_in_second": len(surfaces[b] - surfaces[a]),
            }
    all_three = surfaces[keys[0]] & surfaces[keys[1]] & surfaces[keys[2]]
    union_all = surfaces[keys[0]] | surfaces[keys[1]] | surfaces[keys[2]]
    return {
        "per_register_unique_surfaces": {
            str(k): len(v) for k, v in surfaces.items()},
        "register_labels": {str(k): names[k] for k in keys},
        "pairwise": pair,
        "all_three_shared": len(all_three),
        "union_all_registers": len(union_all),
        "note": (
            "Exploratory corpus-composition analysis (lexical surface "
            "overlap only). 'Unique to one register' does NOT mean "
            "'incorrect'; this is NOT a quality score."),
    }


# ---------------------------------------------------------------------------
# model-output comparison sources (local gitignored rosters; omitted when
# absent — the comparison is descriptive only)
# ---------------------------------------------------------------------------

def _mean_metrics(rows: list) -> dict | None:
    if not rows:
        return None
    keys = ("total_tokens", "canonical_supported_tokens",
            "canonical_coverage", "broader_resource_supported_coverage",
            "unresolved_rate", "unresolved_tokens")
    out = {}
    for k in keys:
        vals = [r["metrics"][k] for r in rows
                if r.get("metrics", {}).get(k) is not None]
        out[k] = (statistics.fmean(vals) if vals else None)
    ortho_vals = [r["orthography"]["outside_inventory"] for r in rows
                  if r.get("orthography", {}).get("outside_inventory")
                  is not None]
    out["orthography_out_mean"] = (
        statistics.fmean(ortho_vals) if ortho_vals else None)
    out["n"] = len(rows)
    return out


def _load_roster(path: Path) -> list:
    if not path.is_file():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return data["rows"] if isinstance(data, dict) else data


def model_output_groups() -> list[dict]:
    """Descriptive dataset-level groups from the local EXP-004 rosters.
    Each group is mean-over-runs (Phase 1 / Phase 2A) or
    mean-over-configuration-means (repeats), primary population only
    (exploratory Dola excluded)."""
    groups = []
    p1_rows = [r for r in _load_roster(EXP / "outputs" / "roster.json")
               if r.get("usable") and r.get("provider") != "bytedance"]
    if p1_rows:
        stats = _mean_metrics(p1_rows)
        if stats:
            groups.append({
                "id": "phase1_direct",
                "label": "EXP-004 Phase 1 direct outputs (primary, usable)",
                "basis": "mean over usable primary runs",
                **stats,
            })
    p2a_rows = [r for r in _load_roster(EXP / "phase2a" / "outputs"
                                        / "roster.json")
                if r.get("usable") and r.get("provider") != "bytedance"
                and r.get("condition") == "p2a-primed"]
    if p2a_rows:
        stats = _mean_metrics(p2a_rows)
        if stats:
            groups.append({
                "id": "phase2a_primed",
                "label": "EXP-004 Phase 2A primed outputs (primary, usable)",
                "basis": "mean over usable primary runs",
                **stats,
            })
    rep_rows = _load_roster(EXP / "repeats" / "outputs" / "roster.json")
    for condition, cid, clabel in (
            ("direct", "repeat_direct",
             "EXP-004 repeated direct outputs (primary, usable)"),
            ("primed", "repeat_primed",
             "EXP-004 repeated primed outputs (primary, usable)")):
        rows = [r for r in rep_rows if r.get("usable")
                and r.get("primary") and r.get("condition") == condition]
        if not rows:
            continue
        # mean of per-configuration means (one mean per configuration)
        by_cfg: dict = {}
        for r in rows:
            by_cfg.setdefault(r["run_id"].rsplit("__", 2)[0], []).append(r)
        cfg_means = [_mean_metrics(v) for v in by_cfg.values()]
        cfg_means = [m for m in cfg_means if m]
        if not cfg_means:
            continue
        def fmean_field(field):
            vals = [m[field] for m in cfg_means if m.get(field) is not None]
            return statistics.fmean(vals) if vals else None
        groups.append({
            "id": cid,
            "label": clabel,
            "basis": "mean over configuration means "
                     f"({len(cfg_means)} configurations)",
            "n": len(cfg_means),
            "total_tokens": fmean_field("total_tokens"),
            "canonical_coverage": fmean_field("canonical_coverage"),
            "broader_resource_supported_coverage":
                fmean_field("broader_resource_supported_coverage"),
            "unresolved_rate": fmean_field("unresolved_rate"),
            "orthography_out_mean": fmean_field("orthography_out_mean"),
        })
    return groups


# ---------------------------------------------------------------------------
# markdown rendering
# ---------------------------------------------------------------------------

def _pct(x) -> str:
    return "n/a" if x is None else f"{x * 100:.2f} %"


def _num(x, digits: int = 0) -> str:
    return "n/a" if x is None else f"{x:,.{digits}f}"


def corpus_table_row(rec: dict) -> str:
    m = rec["metrics"]
    o = rec["orthography"]
    return (f"| {rec['label']} | {m['total_tokens']:,} | "
            f"{_pct(m['canonical_coverage'])} | "
            f"{_pct(m['broader_resource_supported_coverage'])} | "
            f"{_pct(m['unresolved_rate'])} | {o['outside_inventory']:,} |")


def render_md(records: list, cross: dict, out_md: list[str]) -> str:
    lines = [
        "# EXP-004 — authentic corpus self-evaluation (SODA Task 029)",
        "",
        "Deterministic application of the unchanged EXP-004 evaluation "
        "stack (`isv-eval` metrics + Task-015 orthography audit) to the "
        "authentic Medžuslovjansky reference corpus — the same stack "
        "used for generated model outputs. Resource-coverage evidence, "
        "NOT linguistic-correctness claims; no composite score.",
        "",
        f"Corpus: `phase2a-authentic-isv` v1, SHA-256 `{CORPUS_SHA256}`.",
        "",
        "## Corpus overview",
        "",
        TABLE_HEADER,
        TABLE_HEADER_SEP,
    ]
    for rec in records:
        lines.append(corpus_table_row(rec))
    lines += ["",
              "Tokens = lexical tokens (denominator policy of `isv-eval`); "
              "Canonical = (A+B)/lexical; Broader = "
              "(canonical-supported + exact alternative-resource "
              "attestation)/lexical; Unresolved = C/lexical; Orthography "
              "out = characters outside the official Interslavic "
              "inventory.", ""]

    # per-register detail
    regs = [r for r in records if r["register"] is not None]
    for rec in regs:
        m = rec["metrics"]
        o = rec["orthography"]
        lines += [
            f"## {REGISTER_MD_TITLE[rec['register']]}",
            "",
            f"File `{rec['file']}` · SHA-256 `{rec['sha256'][:16]}…` · "
            f"{rec['bytes']:,} bytes.",
            "",
            "| metric | value |",
            "|---|---:|",
            f"| lexical tokens | {m['total_tokens']:,} |",
            f"| exact dictionary matches (A) | {m['exact_dictionary_matches']:,} |",
            f"| morphologically valid (B) | {m['morphologically_valid_forms']:,} |",
            f"| unresolved (C) | {m['unresolved_tokens']:,} |",
            f"| canonical coverage | {_pct(m['canonical_coverage'])} |",
            f"| broader resource-supported coverage | "
            f"{_pct(m['broader_resource_supported_coverage'])} |",
            f"| unresolved rate | {_pct(m['unresolved_rate'])} |",
            "",
            "Orthography (outside-inventory):",
            "",
            "| character class | count |",
            "|---|---:|",
            f"| Cyrillic | {o['cyrillic']:,} |",
            f"| Polish-specific | {o['polish_specific']:,} |",
            f"| other Latin | {o['other_latin']:,} |",
            f"| other script | {o['other_script']:,} |",
            f"| unexpected non-letter | {o['unexpected_nonletters']:,} |",
            f"| **outside inventory (total)** | **{o['outside_inventory']:,}** |",
            "",
        ]

    # cross-register composition
    lines += [
        "## Cross-register vocabulary composition (exploratory)",
        "",
        "Lexical-surface overlap between registers (normalized surfaces; "
        "not a quality score — 'unique to one register' does not mean "
        "'incorrect').",
        "",
        "| register | unique lexical surfaces |",
        "|---|---:|",
    ]
    for k in sorted(cross["per_register_unique_surfaces"]):
        lines.append(
            f"| {cross['register_labels'][k]} | "
            f"{cross['per_register_unique_surfaces'][k]:,} |")
    lines += [
        "",
        "| overlap | shared surfaces |",
        "|---|---:|",
    ]
    for key in sorted(cross["pairwise"]):
        pw = cross["pairwise"][key]
        lines.append(
            f"| register {pw['registers'][0]} × register "
            f"{pw['registers'][1]} | {pw['shared_surfaces']:,} |")
    lines += [
        f"| all three registers | {cross['all_three_shared']:,} |",
        f"| union of the three registers | {cross['union_all_registers']:,} |",
        "",
    ]

    lines += ["## Interpretation (recorded, descriptive)", ""]
    lines += out_md
    return "\n".join(lines) + "\n"


def _interpretation_text(records: list) -> list[str]:
    by_id = {r["dataset_id"]: r for r in records}
    lines = [
        "- The authentic corpus itself is the **reference point** for "
        "interpreting model coverage under the same metrics: generated "
        "outputs are compared with what an authentic, human-produced "
        "Medžuslovjansky text scores.",
        "- The corpus is **not** a perfect upper bound on Interslavic, and "
        "the evaluator measures resource coverage, not linguistic "
        "correctness. A model reaching (or exceeding) the corpus "
        "percentage would not thereby be 'as good as the corpus'.",
        "- Register differences are descriptive: the combined corpus can "
        "hide substantial variation between registers.",
    ]
    if "register2" in by_id:
        lines.append(
            "- The artistic register is expected to contain poetic/"
            "rhyme-driven forms absent from the dictionary; the "
            "orthography audit policy for proper names and sanctioned "
            "forms is unchanged (nothing is 'fixed').")
    return lines


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="EXP-004 authentic-corpus self-evaluation "
                    "(deterministic; no LLM, no corpus edits)")
    parser.add_argument("--scratch", default=None,
                        help="scratch dir for isv-eval artifacts "
                             "(default: corpus-selfeval/.scratch)")
    parser.add_argument("--reuse-scratch", action="store_true",
                        help="reuse cached isv-eval artifacts when present "
                             "(md/json re-render only; the evaluator is "
                             "not re-run)")
    args = parser.parse_args(argv)
    scratch = Path(args.scratch) if args.scratch else SCRATCH_DIR
    scratch.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    records = []
    for ds in DATASETS:
        rec = evaluate_dataset(ds, scratch, reuse=args.reuse_scratch)
        records.append(rec)

    # drop per-token payloads from the committed JSON (size) but keep a
    # compact register composition computed from them
    cross = cross_register(records)
    compact = []
    for rec in records:
        rec = {k: v for k, v in rec.items() if k != "tokens"}
        compact.append(rec)

    payload = {
        "experiment_id": "exp004",
        "artifact": "corpus_selfeval",
        "corpus": {"id": "phase2a-authentic-isv", "version": "v1",
                   "sha256": CORPUS_SHA256},
        "note": (
            "Deterministic self-evaluation of the authentic corpus with "
            "the unchanged EXP-004 evaluation stack (isv-eval metrics + "
            "Task-015 orthography audit). Reference point for "
            "interpreting model coverage; not linguistic-correctness "
            "claims; no composite score."),
        "datasets": compact,
        "cross_register": cross,
        "generator": "scripts/selfeval_exp004_corpus.py",
    }
    (OUT_DIR / "corpus_selfeval.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8")

    out_md = _interpretation_text(records)
    (OUT_DIR / "corpus_selfeval.md").write_text(
        render_md(records, cross, out_md), encoding="utf-8")

    groups = model_output_groups()
    if groups:
        write_model_comparison(records, groups)
    else:
        (OUT_DIR / "model_comparison.md").write_text(
            "# EXP-004 — authentic corpus vs model outputs (descriptive)\n\n"
            "Local EXP-004 rosters not present; comparison not generated.\n",
            encoding="utf-8")

    print("[corpus-selfeval] wrote corpus_selfeval.json / "
          "corpus_selfeval.md / model_comparison.md under "
          f"{OUT_DIR.relative_to(ROOT)}")
    return 0


def write_model_comparison(records: list, groups: list) -> None:
    lines = [
        "# EXP-004 — authentic corpus vs generated model outputs "
        "(descriptive resource-coverage comparison)",
        "",
        "How close do generated outputs get to the resource-coverage "
        "properties of the authentic reference corpus under the same "
        "metrics? Descriptive only — this is NOT 'distance from native "
        "quality', and reaching the corpus percentage would not make a "
        "model 'as good as the corpus'.",
        "",
        "| Dataset | Tokens | Canonical | Broader | Unresolved | "
        "Orthography out | Basis |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for rec in records:
        cells = [c.strip() for c in corpus_table_row(rec).strip("|").split("|")]
        cells.append("per-token (corpus)")
        lines.append("| " + " | ".join(cells) + " |")
    for g in groups:
        def f(x, d=2):
            return "n/a" if g.get(x) is None else (
                _pct(g[x]) if x.endswith(("coverage", "rate"))
                else _num(g[x], d))
        lines.append(
            f"| {g['label']} | {f('total_tokens', 0)} | "
            f"{f('canonical_coverage')} | "
            f"{f('broader_resource_supported_coverage')} | "
            f"{f('unresolved_rate')} | {f('orthography_out_mean', 0)} | "
            f"{g['basis']} |")
    lines += ["", "Sources: local EXP-004 rosters "
                  "(`outputs/roster.json`, `phase2a/outputs/roster.json`, "
                  "`repeats/outputs/roster.json`)."]
    (OUT_DIR / "model_comparison.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
