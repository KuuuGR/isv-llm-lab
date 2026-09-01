#!/usr/bin/env python3
"""EXP-003 — comparison and analysis (per run, within model, within condition).

For every collected run (outputs/<run_id>/output.txt) this script:

1. evaluates the run with the SAME Task 008 evaluator (isv-eval, unmodified;
   reuses outputs/<run_id>/evaluation.json when already computed);
2. writes per-run comparison/<run_id>/comparison.json + comparison.md with:
   - the two-tier metrics (canonical / broader / unresolved),
   - NEW clearly-labelled name-excluded diagnostics (proper-name policy),
   - supplied-candidate usage / adoption (surface-level, clearly labelled),
   - invented / non-supplied vocabulary breakdown;
3. computes within-model pairwise comparisons (A vs B/C/D, B vs C, …) with
   token-aligned evaluator-state transitions, A->C / B->C regression lists,
   C->A / C->B resolutions, metric deltas, output-length and structural
   changes (comparison/within_model/<model>.json);
4. computes within-condition model comparisons (comparison/within_condition/
   <condition>.json);
5. writes blinded complete-text human-review pairs
   (comparison/human_review.md) with the label mapping kept separately
   (comparison/human_review_key.json) so automatic metrics stay hidden during
   holistic judgment.

No composite quality score is ever assigned.
"""
from __future__ import annotations

import difflib
import hashlib
import json
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

EXP = ROOT / "experiments" / "exp003-scaffold"
OUTPUTS_DIR = EXP / "outputs"
COMPARISON_DIR = EXP / "comparison"
SCAFFOLD = EXP / "scaffolds" / "op-pl" / "scaffold.json"

CONDITIONS = ("A", "B", "C", "D")
MODELS = ("chatgpt", "claude", "bielik")

PAIR_KEYS = ["A_vs_B", "A_vs_C", "A_vs_D", "B_vs_C", "B_vs_D", "C_vs_D"]


def _pct(v: float | None) -> str:
    return f"{v * 100:.2f}%" if v is not None else "n/a"


def _pctd(v: float | None) -> str:
    if v is None:
        return "n/a"
    return f"{v * 100:+.2f}%"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_scaffold() -> dict:
    return json.loads(SCAFFOLD.read_text(encoding="utf-8"))


def supplied_surfaces() -> set[str]:
    """All scaffold candidate surfaces (normalized + folded) — the vocabulary
    the scaffold supplies to the model."""
    scaffold = load_scaffold()
    surfaces: set[str] = set()
    for sent in scaffold["sentences"]:
        for tok in sent["tokens"]:
            for cand in tok.get("isv_candidates", []):
                surfaces.add(cand["surface"].lower())
                surfaces.add(" ".join(cand["surface"].split()).lower())
    return surfaces


def scaffold_names() -> set[str]:
    """Proper names from the scaffold (kept as name tokens, D-031)."""
    scaffold = load_scaffold()
    names: set[str] = set()
    for sent in scaffold["sentences"]:
        for tok in sent["tokens"]:
            if tok["kind"] == "name":
                names.add(tok["pl_surface"].lower())
                names.add(tok["pl_surface"].capitalize().lower())
    return names


def evaluate(text_path: Path, out_dir: Path) -> dict:
    cmd = [sys.executable, "-m", "isv_eval.cli", str(text_path),
           "--out", str(out_dir)]
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"isv-eval failed on {text_path}: "
                           f"{proc.stderr[-500:]}")
    return json.loads((out_dir / "report.json").read_text(encoding="utf-8"))


def load_tokens(eval_dir: Path) -> list[dict]:
    return json.loads((eval_dir / "tokens.json").read_text(encoding="utf-8"))


def run_evaluation(run_id: str) -> dict:
    """Return (report, tokens) for a run, evaluating on demand."""
    out_dir = OUTPUTS_DIR / run_id
    text = out_dir / "output.txt"
    eval_dir = out_dir / "evaluation"
    if not (eval_dir / "report.json").is_file():
        eval_dir.mkdir(parents=True, exist_ok=True)
        evaluate(text, eval_dir)
    report = json.loads((eval_dir / "report.json").read_text(encoding="utf-8"))
    tokens = load_tokens(eval_dir)
    return report, tokens


def align_lexical(before_tokens: list[dict],
                  after_tokens: list[dict]) -> list[tuple[dict | None, dict | None]]:
    """LCS alignment of two ISV outputs' lexical sequences (difflib)."""
    b = [t for t in before_tokens if t.get("is_lexical")]
    a = [t for t in after_tokens if t.get("is_lexical")]
    matcher = difflib.SequenceMatcher(
        None, [t["normalized"] for t in b], [t["normalized"] for t in a],
        autojunk=False)
    pairs: list[tuple[dict | None, dict | None]] = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            for k in range(i2 - i1):
                pairs.append((b[i1 + k], a[j1 + k]))
        elif tag == "replace":
            n = min(i2 - i1, j2 - j1)
            for k in range(n):
                pairs.append((b[i1 + k], a[j1 + k]))
            for k in range(n, i2 - i1):
                pairs.append((b[i1 + k], None))
            for k in range(n, j2 - j1):
                pairs.append((None, a[j1 + k]))
        elif tag == "delete":
            for k in range(i2 - i1):
                pairs.append((b[i1 + k], None))
        elif tag == "insert":
            for k in range(j2 - j1):
                pairs.append((None, a[j1 + k]))
    return pairs


def transition_stats(
        pairs: list[tuple[dict | None, dict | None]]
) -> tuple[dict[str, int], dict[str, list[dict]]]:
    """Before->after evaluator-state transitions + regression/resolution lists.

    Evaluator-state transitions only (no linguistic judgment). Keyed by
    A/B/C; unmatched positions are counted separately.
    """
    matrix: dict[str, int] = defaultdict(int)
    form_pairs: dict[tuple[str, str], Counter] = defaultdict(Counter)
    for b_tok, a_tok in pairs:
        if b_tok is None:
            matrix["unmatched_after"] += 1
            continue
        if a_tok is None:
            matrix["unmatched_before"] += 1
            continue
        b_cls, a_cls = b_tok["classification"], a_tok["classification"]
        matrix[f"{b_cls}→{a_cls}"] += 1
        if b_tok["normalized"] != a_tok["normalized"]:
            form_pairs[(b_cls, a_cls)][(b_tok["normalized"], a_tok["normalized"])] += 1
    detail: dict[str, list[dict]] = {}
    for pair_key, list_key in [
        (("A", "C"), "A_to_C"), (("B", "C"), "B_to_C"),
        (("C", "A"), "C_to_A"), (("C", "B"), "C_to_B"),
        (("A", "B"), "A_to_B"), (("B", "A"), "B_to_A"),
    ]:
        entries = [
            {"form": f, "replacement": r, "count": c}
            for (f, r), c in sorted(form_pairs[pair_key].items())
        ]
        if entries:
            detail[list_key] = entries
    return dict(matrix), detail


def text_structure(text: str) -> dict:
    """Coarse structural fingerprint: paragraphs, dialogue lines, tokens.

    Clearly a heuristic, reported only as structural change signal.
    """
    lines = [ln.strip() for ln in text.splitlines()]
    paragraphs = sum(1 for ln in lines if ln)
    dialogue = sum(1 for ln in lines
                   if ln.startswith("–") or ln.startswith("—")
                   or ln.startswith("«") or ln.startswith('"'))
    return {"paragraphs": paragraphs, "dialogue_lines": dialogue}


def candidate_usage(tokens: list[dict], supplied: set[str]) -> dict:
    lexical = [t for t in tokens if t.get("is_lexical")]
    output_forms = set(t["normalized"].lower() for t in lexical)
    present = sorted(s for s in supplied if s in output_forms)
    accepted = sorted(
        t["normalized"].lower()
        for t in lexical
        if t["normalized"].lower() in supplied
        and t.get("classification") in ("A", "B"))
    return {
        "supplied_surfaces_total": len(supplied),
        "supplied_surfaces_present_in_output": len(present),
        "supplied_surfaces_accepted_by_evaluator": len(accepted),
        "present_surfaces": present,
        "accepted_surfaces": accepted,
        "adoption_note": (
            "surface-level adoption (output form equals a supplied candidate "
            "surface, normalized); position-targeted adoption is not "
            "computable across Polish->ISV without a translation model, so it "
            "is reported as this clearly-labelled proxy, not as ground truth."),
    }


def invented_forms(tokens: list[dict], supplied: set[str],
                   names: set[str]) -> dict:
    """Non-supplied vocabulary breakdown (analytical signal, not correctness).

    Categories mirror the design: supplied / canonical-but-independently-
    generated / broader-resource-supported / unresolved / proper-name-like.
    """
    lexical = [t for t in tokens if t.get("is_lexical")]
    by_form: dict[str, dict] = {}
    for t in lexical:
        norm = t["normalized"].lower()
        if norm in by_form:
            continue
        is_capitalized = t["token"][:1].isupper()
        if norm in supplied:
            category = "supplied_scaffold_vocabulary"
        elif norm in names or (is_capitalized and t["classification"] == "C"):
            category = "proper_name_like"
        elif t.get("classification") in ("A", "B"):
            category = "canonical_independently_generated"
        elif t.get("broader_supported"):
            category = "broader_resource_supported"
        else:
            category = "unresolved"
        by_form[norm] = {
            "form": t["normalized"],
            "category": category,
            "classification": t.get("classification"),
            "broader_supported": t.get("broader_supported"),
        }
    grouped: dict[str, list[str]] = defaultdict(list)
    for rec in by_form.values():
        grouped[rec["category"]].append(rec["form"])
    return {
        "note": ("Forms in the output that were not supplied by the scaffold. "
                 "This is an analytical signal, not a correctness oracle."),
        "categories": {
            cat: sorted(forms) for cat, forms in sorted(grouped.items())
        },
        "counts": {cat: len(forms) for cat, forms in grouped.items()},
    }


def name_excluded_diagnostics(tokens: list[dict], names: set[str]) -> dict:
    """NEW clearly-labelled metric: coverage excluding proper-name tokens.

    Historical EXP-001/002 numbers are never changed; this is an additional
    diagnostic for EXP-003 so names do not distort comparisons.
    """
    lexical = [t for t in tokens if t.get("is_lexical")]
    excluded = [t for t in lexical if t["normalized"].lower() in names
                or (t["token"][:1].isupper()
                    and t.get("classification") == "C")]
    kept = [t for t in lexical if t not in excluded]
    kept_lex = len(kept)
    if kept_lex == 0:
        return {"kept_tokens": 0, "excluded_name_tokens": len(excluded)}
    kept_a = sum(1 for t in kept if t["classification"] == "A")
    kept_b = sum(1 for t in kept if t["classification"] == "B")
    kept_c = sum(1 for t in kept if t["classification"] == "C")
    kept_broader = sum(1 for t in kept if t.get("broader_supported"))
    return {
        "label": ("name-excluded diagnostic (NEW, EXP-003; historical "
                  "EXP-001/002 metrics are unchanged)"),
        "kept_tokens": kept_lex,
        "excluded_name_tokens": len(excluded),
        "canonical_supported_tokens_excl_names": kept_a + kept_b,
        "canonical_coverage_excl_names": (kept_a + kept_b) / kept_lex,
        "broader_resource_supported_tokens_excl_names": kept_broader,
        "broader_coverage_excl_names": kept_broader / kept_lex,
        "unresolved_tokens_excl_names": kept_c,
        "unresolved_rate_excl_names": kept_c / kept_lex,
    }


def run_analysis(run_id: str, supplied: set[str], names: set[str]) -> dict:
    report, tokens = run_evaluation(run_id)
    meta = json.loads((OUTPUTS_DIR / run_id / "meta.json").read_text(
        encoding="utf-8"))
    text = (OUTPUTS_DIR / run_id / "output.txt").read_text(encoding="utf-8")
    m = report["metrics"]
    return {
        "run_id": run_id,
        "condition": meta["condition"],
        "model": meta["model"],
        "metrics": m,
        "name_excluded": name_excluded_diagnostics(tokens, names),
        "candidate_usage": candidate_usage(tokens, supplied),
        "invented_forms": invented_forms(tokens, supplied, names),
        "structure": text_structure(text),
        "output": {
            "bytes": len(text.encode("utf-8")),
            "sha256": sha256_bytes(text.encode("utf-8")),
        },
    }


def pairwise(first: dict, second: dict,
             first_tokens: list[dict] | None = None,
             second_tokens: list[dict] | None = None) -> dict:
    """Comparison of two runs (same or different model/condition).

    Token sequences may be injected for pure testing; by default they are
    loaded from the runs' evaluation output.
    """
    t1 = first_tokens if first_tokens is not None else _tokens(first["run_id"])
    t2 = second_tokens if second_tokens is not None else _tokens(second["run_id"])
    pairs = align_lexical(t1, t2)
    matrix, detail = transition_stats(pairs)
    m1, m2 = first["metrics"], second["metrics"]
    return {
        "first": {"run_id": first["run_id"], "condition": first["condition"]},
        "second": {"run_id": second["run_id"], "condition": second["condition"]},
        "deltas": {
            "lexical_tokens": m2["total_tokens"] - m1["total_tokens"],
            "canonical_supported_tokens": (
                m2["canonical_supported_tokens"] - m1["canonical_supported_tokens"]),
            "canonical_coverage": _delta_pct(
                m1["canonical_coverage"], m2["canonical_coverage"]),
            "broader_resource_supported_coverage": _delta_pct(
                m1["broader_resource_supported_coverage"],
                m2["broader_resource_supported_coverage"]),
            "unresolved_tokens": m2["unresolved_tokens"] - m1["unresolved_tokens"],
            "unresolved_rate": _delta_pct(
                m1["unresolved_rate"], m2["unresolved_rate"]),
        },
        "structure": {
            "first": first["structure"],
            "second": second["structure"],
        },
        "transitions": {
            "method": "per-position LCS alignment of the two ISV outputs' "
                      "lexical tokens; before->after evaluator class; "
                      "evaluator-state transitions only, no linguistic "
                      "judgment",
            "matrix": matrix,
            "detail": detail,
        },
        "note": "Pairwise comparison only; no composite quality score.",
    }


def _delta_pct(a: float | None, b: float | None) -> float | None:
    if a is None or b is None:
        return None
    return b - a


_EVAL_CACHE: dict[str, list[dict]] = {}


def _tokens(run_id: str) -> list[dict]:
    if run_id not in _EVAL_CACHE:
        _, tokens = run_evaluation(run_id)
        _EVAL_CACHE[run_id] = tokens
    return _EVAL_CACHE[run_id]


def collected_runs() -> list[str]:
    if not OUTPUTS_DIR.is_dir():
        return []
    return sorted(p.name for p in OUTPUTS_DIR.iterdir()
                  if p.is_dir() and (p / "output.txt").is_file()
                  and not p.name.startswith((".", "plan")))


def render_run_md(a: dict) -> str:
    m = a["metrics"]
    ne = a["name_excluded"]
    cu = a["candidate_usage"]
    inv = a["invented_forms"]
    lines = [
        f"# EXP-003 — run — {a['run_id']}",
        "",
        f"condition {a['condition']} · model {a['model']}",
        "",
        "## Metrics (Task 008 evaluator)",
        "",
        "| metric | value |",
        "|---|---:|",
        f"| lexical tokens | {m['total_tokens']} |",
        f"| canonical supported tokens | {m['canonical_supported_tokens']} |",
        f"| canonical coverage | {_pct(m['canonical_coverage'])} |",
        f"| broader resource-supported tokens | {m['broader_resource_supported_tokens']} |",
        f"| broader resource-supported coverage | {_pct(m['broader_resource_supported_coverage'])} |",
        f"| unresolved tokens | {m['unresolved_tokens']} |",
        f"| unresolved rate | {_pct(m['unresolved_rate'])} |",
        "",
        "## Name-excluded diagnostic (new, EXP-003)",
        "",
        f"- excluded name tokens: {ne.get('excluded_name_tokens', 0)}",
        f"- canonical coverage excluding names: "
        f"{_pct(ne.get('canonical_coverage_excl_names'))}",
        f"- broader coverage excluding names: "
        f"{_pct(ne.get('broader_coverage_excl_names'))}",
        f"- unresolved rate excluding names: "
        f"{_pct(ne.get('unresolved_rate_excl_names'))}",
        "",
        "## Supplied-candidate usage (surface-level proxy)",
        "",
        f"- supplied surfaces: {cu['supplied_surfaces_total']}",
        f"- present in output: {cu['supplied_surfaces_present_in_output']}",
        f"- accepted by evaluator (A/B): {cu['supplied_surfaces_accepted_by_evaluator']}",
        "",
        "## Non-supplied vocabulary (analytical signal, not correctness)",
        "",
    ]
    for cat, forms in inv["categories"].items():
        lines.append(f"- {cat}: {len(forms)} — "
                     f"{', '.join(forms[:12])}"
                     + (" …" if len(forms) > 12 else ""))
    lines += ["", "No linguistic quality score is assigned.", ""]
    return "\n".join(lines)


def render_pair_md(p: dict, title: str) -> str:
    d = p["deltas"]
    t = p["transitions"]
    lines = [
        f"## {title}",
        "",
        f"`{p['first']['run_id']}` → `{p['second']['run_id']}`",
        "",
        "| metric | Δ |",
        "|---|---:|",
        f"| lexical tokens | {d['lexical_tokens']:+d} |",
        f"| canonical supported tokens | {d['canonical_supported_tokens']:+d} |",
        f"| canonical coverage | {_pctd(d['canonical_coverage'])} |",
        f"| broader coverage | {_pctd(d['broader_resource_supported_coverage'])} |",
        f"| unresolved tokens | {d['unresolved_tokens']:+d} |",
        f"| unresolved rate | {_pctd(d['unresolved_rate'])} |",
        "",
        "### Token-aligned evaluator-state transitions",
        "",
        "| transition | count |",
        "|---|---:|",
    ]
    for key in ["A→A", "A→B", "A→C", "B→A", "B→B", "B→C", "C→A", "C→B",
                "C→C", "unmatched_before", "unmatched_after"]:
        lines.append(f"| {key} | {t['matrix'].get(key, 0)} |")
    lines.append("")
    for key, label in [
        ("A_to_C", "A→C regressions (canonical → unresolved)"),
        ("B_to_C", "B→C regressions (valid → unresolved)"),
        ("C_to_A", "C→A resolutions (unresolved → canonical)"),
        ("C_to_B", "C→B resolutions (unresolved → valid)"),
    ]:
        entries = t["detail"].get(key)
        if entries:
            lines.append(f"{label}:")
            lines.append("  " + "; ".join(
                f"{e['form']} → {e['replacement']} (×{e['count']})"
                for e in entries))
            lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", default=None,
                        help="single run id; default: all collected runs")
    parser.add_argument("--no-evaluate", action="store_true",
                        help="only reuse existing evaluation.json "
                             "(fail for runs without one)")
    args = parser.parse_args(argv)

    if args.no_evaluate:
        # ensure every run already has evaluation.json
        for run_id in collected_runs():
            if not (OUTPUTS_DIR / run_id / "evaluation.json").is_file():
                print(f"error: --no-evaluate but {run_id} has no "
                      "evaluation.json; run evaluate first", file=sys.stderr)
                return 2

    runs = collected_runs()
    if args.run:
        runs = [r for r in runs if r == args.run]
        if not runs:
            print(f"error: run {args.run!r} not collected", file=sys.stderr)
            return 2
    if not runs:
        print("no collected runs; run `scripts/run_exp003_pilot.py collect` "
              "first", file=sys.stderr)
        return 2

    supplied = supplied_surfaces()
    names = scaffold_names()

    analyses: dict[str, dict] = {}
    for run_id in runs:
        print(f"[analyze] {run_id}")
        analyses[run_id] = run_analysis(run_id, supplied, names)
        run_dir = COMPARISON_DIR / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        (run_dir / "comparison.json").write_text(
            json.dumps(analyses[run_id], ensure_ascii=False, indent=2),
            encoding="utf-8")
        (run_dir / "comparison.md").write_text(
            render_run_md(analyses[run_id]), encoding="utf-8")

    by_key: dict[tuple[str, str], dict] = {
        (a["model"], a["condition"]): a for a in analyses.values()}

    within_model: dict[str, dict] = {}
    within_condition: dict[str, dict] = {}
    pair_docs: list[str] = []
    for model in MODELS:
        model_pairs = {}
        for key in PAIR_KEYS:
            c1, c2 = key.split("_vs_")
            a1, a2 = by_key.get((model, c1)), by_key.get((model, c2))
            if not (a1 and a2):
                continue
            model_pairs[key] = pairwise(a1, a2)
            pair_docs.append(render_pair_md(
                model_pairs[key], f"{model} — {c1} vs {c2}"))
        if model_pairs:
            (COMPARISON_DIR / "within_model" / model).parent.mkdir(
                parents=True, exist_ok=True)
            (COMPARISON_DIR / "within_model" / f"{model}.json").write_text(
                json.dumps(model_pairs, ensure_ascii=False, indent=2),
                encoding="utf-8")
            within_model[model] = model_pairs
    for condition in CONDITIONS:
        cond_pairs = {}
        for i, m1 in enumerate(MODELS):
            for m2 in MODELS[i + 1:]:
                a1, a2 = by_key.get((m1, condition)), by_key.get((m2, condition))
                if not (a1 and a2):
                    continue
                key = f"{m1}_vs_{m2}"
                cond_pairs[key] = pairwise(a1, a2)
                pair_docs.append(render_pair_md(
                    cond_pairs[key], f"condition {condition} — {m1} vs {m2}"))
        if cond_pairs:
            (COMPARISON_DIR / "within_condition" / condition).parent.mkdir(
                parents=True, exist_ok=True)
            (COMPARISON_DIR / "within_condition" / f"{condition}.json").write_text(
                json.dumps(cond_pairs, ensure_ascii=False, indent=2),
                encoding="utf-8")
            within_condition[condition] = cond_pairs

    # ---- summary ----
    summary = [
        "# EXP-003 — comparison summary", "",
        f"{len(analyses)} run(s) analysed.", "",
    ]
    for run_id, a in sorted(analyses.items()):
        m = a["metrics"]
        summary.append(
            f"- `{run_id}` ({a['condition']}): canonical coverage "
            f"{_pct(m['canonical_coverage'])} · broader "
            f"{_pct(m['broader_resource_supported_coverage'])} · unresolved "
            f"{m['unresolved_tokens']} tokens "
            f"({_pct(m['unresolved_rate'])}).")
    summary += [
        "",
        "Within-model pair comparisons: "
        f"{COMPARISON_DIR / 'within_model'}",
        "Within-condition model comparisons: "
        f"{COMPARISON_DIR / 'within_condition'}",
        "Pairwise transition tables:",
        "",
    ] + pair_docs
    summary += ["", "No linguistic quality score is assigned.", ""]
    (COMPARISON_DIR / "summary.md").write_text(
        "\n".join(summary), encoding="utf-8")

    # ---- blinded human-review pairs ----
    human_review, key_lines = render_human_pairs(analyses)
    (COMPARISON_DIR / "human_review.md").write_text(human_review, encoding="utf-8")
    (COMPARISON_DIR / "human_review_key.json").write_text(
        json.dumps(key_lines, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\ncomparison written under {COMPARISON_DIR}/")
    print(f"human review: {COMPARISON_DIR / 'human_review.md'} "
          f"(metrics hidden; key kept in human_review_key.json)")
    return 0


def render_human_pairs(analyses: dict[str, dict]) -> tuple[str, list[dict]]:
    """Blinded complete-text pairs within each model (B/C/D vs A, C vs B, D vs C).

    Only blinded labels ("Version N") are shown; the model/condition mapping
    goes to human_review_key.json, kept separate from the review document.
    """
    out: list[str] = [
        "# EXP-003 — human review (blinded, holistic)", "",
        "Below are complete Interslavic translations grouped by source model.",
        "**Do not consult automatic metrics while reading.** The labels are",
        "blinded; the label mapping is kept separately and only unblinded",
        "after the holistic judgment is recorded.", "",
        "For each model, compare the versions and note: which sounds more",
        "natural Interslavic, which you would prefer to read, which feels",
        "more mechanically constructed, and which better preserves the",
        "original meaning and style.", "",
    ]
    key: list[dict] = []
    version = 0
    for model in MODELS:
        conds = {
            a["condition"]: a for a in analyses.values() if a["model"] == model}
        if len(conds) < 2:
            continue
        labels: dict[str, str] = {}
        out.append(f"## Model group — model {model}")
        out.append("")
        for condition in sorted(conds):
            version += 1
            label = f"Version {version}"
            labels[condition] = label
            text = (OUTPUTS_DIR / conds[condition]["run_id"]
                    / "output.txt").read_text(encoding="utf-8")
            out += [f"### {label}", "", "```", text.rstrip("\n"), "```", ""]
        key.append({
            "group": model,
            "blinded_labels": labels,
            "runs": {c: conds[c]["run_id"] for c in conds},
        })
    return "\n".join(out), key


if __name__ == "__main__":
    sys.exit(main())
