#!/usr/bin/env python3
"""EXP-002 pilot — before/after evaluation comparison (same evaluator as EXP-001).

For every pilot input package under experiments/exp002-pilot/input/<pilot_run_id>/
that has a corresponding revised output
experiments/exp002-pilot/outputs/<pilot_run_id>/revised.txt, this script:

1. runs the SAME isv-eval evaluator on the original translation copy and on the
   revised output;
2. computes before/after metrics: lexical tokens, A/B/C counts, valid coverage,
   unresolved rate, unique unresolved forms, resolved/newly-unresolved forms,
   and replacement-specific metrics (supplied candidates used / accepted /
   not used; unresolved forms replaced without a supplied candidate);
3. writes, under experiments/exp002-pilot/comparison/<pilot_run_id>/:
   comparison.json (machine-readable) and comparison.md (human-readable),
   plus a summary comparison.md at the experiment root.

Raw LLM outputs are never modified. No invented quality score: only metrics
from the existing evaluator plus the deterministic candidate bookkeeping.
"""

from __future__ import annotations

import json
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXP002 = ROOT / "experiments" / "exp002-pilot"
INPUT_DIR = EXP002 / "input"
OUTPUTS_DIR = EXP002 / "outputs"
COMPARISON_DIR = EXP002 / "comparison"


def evaluate(text_path: Path, out_dir: Path) -> dict:
    """Run the same evaluator (isv-eval CLI) on a text; return report+unresolved."""
    cmd = [sys.executable, "-m", "isv_eval.cli", str(text_path),
           "--out", str(out_dir)]
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"isv-eval failed on {text_path}: {proc.stderr[-500:]}")
    report = json.loads((out_dir / "report.json").read_text(encoding="utf-8"))
    unresolved = json.loads(
        (out_dir / "unresolved.json").read_text(encoding="utf-8"))
    return {"report": report, "unresolved": unresolved}


def unique_unresolved(unresolved: list[dict]) -> Counter:
    return Counter(rec["normalized"] for rec in unresolved)


def load_candidates(pilot_input: Path) -> list[dict]:
    """Return the selected-form records from the pilot candidates.json."""
    data = json.loads((pilot_input / "candidates.json").read_text(encoding="utf-8"))
    return data["selected_forms"]


def compute_comparison(pilot_input: Path, revised_path: Path) -> dict:
    pilot_run_id = pilot_input.name
    out_base = COMPARISON_DIR / pilot_run_id
    before_dir = out_base / "before"
    after_dir = out_base / "after"
    before_dir.mkdir(parents=True, exist_ok=True)
    after_dir.mkdir(parents=True, exist_ok=True)

    original_path = pilot_input / "original.txt"
    before = evaluate(original_path, before_dir)
    after = evaluate(revised_path, after_dir)

    records = load_candidates(pilot_input)

    before_uniq = unique_unresolved(before["unresolved"])
    after_uniq = unique_unresolved(after["unresolved"])
    before_forms = set(before_uniq)
    after_forms = set(after_uniq)

    resolved = sorted(before_forms - after_forms)      # C-before not C-after
    new_unresolved = sorted(after_forms - before_forms)  # C-after not C-before
    still_unresolved = sorted(before_forms & after_forms)

    # Replacement bookkeeping (deterministic, based on the candidate payload).
    selected_forms = [r["form"] for r in records]
    candidate_surfaces: set[str] = set()
    candidate_lemmas: set[str] = set()
    supplied_by_form: dict[str, set[str]] = {}
    for r in records:
        supplied_by_form[r["form"]] = set()
        for alt in r.get("alternatives", []):
            candidate_surfaces.add(alt["surface"].lower())
            if alt.get("lemma"):
                candidate_lemmas.add(alt["lemma"].lower())
            supplied_by_form[r["form"]].add(alt["surface"].lower())

    before_lexical = {t["token"].lower() for t in load_tokens(before_dir)}
    after_lexical = {t["token"].lower() for t in load_tokens(after_dir)}
    # A supplied surface "used" in revised is surface-level overlap, not proof
    # of a targeted replacement: distinguish pre-existing tokens (also present
    # in the original) from tokens newly introduced by the revision.
    used_candidates = sorted(candidate_surfaces & after_lexical)
    used_pre_existing = sorted(candidate_surfaces & before_lexical & after_lexical)
    used_new = sorted((candidate_surfaces & after_lexical) - before_lexical)
    used_lemma_forms = sorted(
        c for c in candidate_lemmas if c in after_lexical)
    # supplied candidates that the evaluator accepts (A/B) in revised output
    accepted = set()
    for t in load_tokens(after_dir):
        if t["token"].lower() in candidate_surfaces and t.get("classification") in ("A", "B"):
            accepted.add(t["token"].lower())

    # unresolved forms replaced without a supplied candidate:
    # a C-before form that is no longer unresolved in revised AND neither the
    # form itself nor ANY of its supplied candidate surfaces appears in the
    # revised output. (Forms with no supplied candidates that simply vanished
    # are flagged too — the prompt told the model to leave them unchanged.)
    replaced_without_candidate: list[str] = []
    for form in resolved:
        supplied_for_form = supplied_by_form.get(form, set())
        if not supplied_for_form and form.lower() not in after_lexical:
            replaced_without_candidate.append(form)
        elif supplied_for_form and not (supplied_for_form & after_lexical):
            replaced_without_candidate.append(form)

    bm, am = before["report"]["metrics"], after["report"]["metrics"]
    comparison = {
        "pilot_run_id": pilot_run_id,
        "source_run": pilot_input.name.removeprefix("exp002__"),
        "metrics": {
            "before": bm,
            "after": am,
            "deltas": {
                "lexical_tokens": am["total_tokens"] - bm["total_tokens"],
                "exact_matches": am["exact_dictionary_matches"] - bm["exact_dictionary_matches"],
                "morph_valid": am["morphologically_valid_forms"] - bm["morphologically_valid_forms"],
                "unresolved_tokens": am["unresolved_forms"] - bm["unresolved_forms"],
                "valid_coverage": (am["morphologically_valid_coverage"]
                                   - bm["morphologically_valid_coverage"]) if
                                  (am["morphologically_valid_coverage"] is not None
                                   and bm["morphologically_valid_coverage"] is not None) else None,
                "unresolved_rate": (am["unresolved_rate"] - bm["unresolved_rate"]) if
                                   (am["unresolved_rate"] is not None
                                    and bm["unresolved_rate"] is not None) else None,
            },
        },
        "unresolved_forms": {
            "before_unique": len(before_forms),
            "after_unique": len(after_forms),
            "resolved": resolved,
            "new_unresolved": new_unresolved,
            "still_unresolved": still_unresolved,
        },
        "replacement": {
            "selected_forms": len(selected_forms),
            "selected_forms_with_candidates": sum(
                1 for r in records if r.get("alternatives")),
            "candidate_surfaces_supplied": len(candidate_surfaces),
            "candidate_surfaces_used_in_revised": len(used_candidates),
            "candidate_surfaces_present_before_and_after": len(used_pre_existing),
            "candidate_surfaces_new_in_revised": len(used_new),
            "candidate_surfaces_accepted_by_evaluator": len(accepted),
            "candidate_lemmas_supplied": len(candidate_lemmas),
            "candidate_lemmas_used_verbatim": len(used_lemma_forms),
            "candidate_surfaces_not_used": sorted(candidate_surfaces - after_lexical),
            "used_candidates": used_candidates,
            "accepted_candidates": sorted(accepted),
            "unresolved_forms_replaced_without_supplied_candidate":
                replaced_without_candidate,
        },
        "note": "Metrics from the same isv-eval evaluator; replacement "
                "bookkeeping is deterministic and evidence-based; no "
                "linguistic quality score.",
    }
    return comparison


def load_tokens(eval_dir: Path) -> list[dict]:
    with open(eval_dir / "tokens.json", encoding="utf-8") as fh:
        return json.load(fh)


def render_md(comparison: dict) -> str:
    bm = comparison["metrics"]["before"]
    am = comparison["metrics"]["after"]
    d = comparison["metrics"]["deltas"]
    u = comparison["unresolved_forms"]
    r = comparison["replacement"]
    lines = [
        f"# EXP-002 pilot — {comparison['pilot_run_id']}",
        "",
        f"Source EXP-001 run: `{comparison['source_run']}`",
        "",
        "## Before / after (same evaluator as EXP-001)",
        "",
        "| metric | before | after | Δ |",
        "|---|---:|---:|---:|",
        f"| lexical tokens | {bm['total_tokens']} | {am['total_tokens']} | {d['lexical_tokens']:+d} |",
        f"| exact dictionary matches (A) | {bm['exact_dictionary_matches']} | {am['exact_dictionary_matches']} | {d['exact_matches']:+d} |",
        f"| morphologically valid (B) | {bm['morphologically_valid_forms']} | {am['morphologically_valid_forms']} | {d['morph_valid']:+d} |",
        f"| unresolved tokens (C) | {bm['unresolved_forms']} | {am['unresolved_forms']} | {d['unresolved_tokens']:+d} |",
        f"| valid coverage (A+B) | {_pct(bm['morphologically_valid_coverage'])} | {_pct(am['morphologically_valid_coverage'])} | {_pctd(d['valid_coverage'])} |",
        f"| unresolved rate | {_pct(bm['unresolved_rate'])} | {_pct(am['unresolved_rate'])} | {_pctd(d['unresolved_rate'])} |",
        "",
        "## Unresolved unique forms",
        "",
        f"- before: {u['before_unique']} · after: {u['after_unique']}",
        f"- resolved after revision (C-before no longer C): {len(u['resolved'])} "
        f"— {', '.join(u['resolved'][:20])}"
        + (" …" if len(u["resolved"]) > 20 else ""),
        f"- new unresolved introduced: {len(u['new_unresolved'])} "
        f"— {', '.join(u['new_unresolved'][:20])}"
        + (" …" if len(u["new_unresolved"]) > 20 else ""),
        f"- still unresolved: {len(u['still_unresolved'])}",
        "",
        "## Replacement bookkeeping (deterministic, evidence-based)",
        "",
        f"- selected forms: {r['selected_forms']} "
        f"({r['selected_forms_with_candidates']} with candidates)",
        f"- candidate surfaces supplied: {r['candidate_surfaces_supplied']}",
        f"- used in revised output: {len(r['used_candidates'])} "
        f"({', '.join(r['used_candidates'][:15])})",
        f"  of which also present in the original: "
        f"{r['candidate_surfaces_present_before_and_after']} · "
        f"newly introduced by revision: {r['candidate_surfaces_new_in_revised']}",
        f"- supplied candidate lemmas used verbatim: {r['candidate_lemmas_used_verbatim']}",
        f"- accepted by evaluator (A/B in revised): {len(r['accepted_candidates'])}",
        f"- not used: {len(r['candidate_surfaces_not_used'])}",
    ]
    if r["unresolved_forms_replaced_without_supplied_candidate"]:
        lines += [
            "",
            "⚠️ FLAG: unresolved forms replaced without a supplied candidate:",
            "  " + ", ".join(r["unresolved_forms_replaced_without_supplied_candidate"]),
        ]
    lines += ["", "No linguistic quality score is assigned.", ""]
    return "\n".join(lines)


def _pct(v: float | None) -> str:
    return f"{v * 100:.2f}%" if v is not None else "n/a"


def _pctd(v: float | None) -> str:
    if v is None:
        return "n/a"
    return f"{v * 100:+.2f}%"


def render_human_pairs(pairs: list[tuple[str, str, str]]) -> str:
    """Complete before/after text pairs for holistic Project-Owner reading.

    Qualitative evidence only — no word-by-word annotation, no scoring.
    Each pair is the COMPLETE original translation and the COMPLETE revised
    output of one pilot run, stored verbatim.
    """
    lines = [
        "# EXP-002 pilot — human review pairs (holistic reading)",
        "",
        "Complete before/after text pairs for qualitative assessment of "
        "naturalness and Interslavic character. This is NOT automatic ground "
        "truth and carries no scores. The pairs below are reproduced "
        "byte-for-byte from the pilot input packages and the raw revised "
        "outputs.",
        "",
    ]
    for i, (run_id, before, after) in enumerate(pairs, start=1):
        lines += [
            f"## Pair {i} — {run_id}",
            "",
            "### Before (original EXP-001 translation)",
            "",
            "```",
            before.rstrip("\n"),
            "```",
            "",
            "### After (revised EXP-002 output)",
            "",
            "```",
            after.rstrip("\n"),
            "```",
            "",
        ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot-run", default=None,
                        help="single pilot run id; default: all with a revised output")
    parser.add_argument("--human-pairs", type=int, default=2,
                        help="number of complete before/after pairs to write "
                             "into the human-review doc (default 2)")
    args = parser.parse_args(argv)

    comparisons = []
    for pilot_input in sorted(INPUT_DIR.iterdir()):
        if not pilot_input.is_dir():
            continue
        if args.pilot_run and pilot_input.name != args.pilot_run:
            continue
        revised = OUTPUTS_DIR / pilot_input.name / "revised.txt"
        if not revised.is_file():
            print(f"[skip] {pilot_input.name}: no revised.txt yet")
            continue
        print(f"[eval] {pilot_input.name}")
        comparison = compute_comparison(pilot_input, revised)
        run_dir = COMPARISON_DIR / pilot_input.name
        run_dir.mkdir(parents=True, exist_ok=True)
        (run_dir / "comparison.json").write_text(
            json.dumps(comparison, ensure_ascii=False, indent=2), encoding="utf-8")
        (run_dir / "comparison.md").write_text(
            render_md(comparison), encoding="utf-8")
        comparisons.append(comparison)

    if not comparisons:
        print("no revised outputs found; drop revised.txt files under "
              "experiments/exp002-pilot/outputs/<pilot_run_id>/ and rerun")
        return 0

    summary_md = ["# EXP-002 pilot — comparison summary", "",
                  f"{len(comparisons)} revised output(s) evaluated.", ""]
    for c in comparisons:
        bm, am = c["metrics"]["before"], c["metrics"]["after"]
        summary_md.append(
            f"- `{c['pilot_run_id']}`: valid coverage "
            f"{_pct(bm['morphologically_valid_coverage'])} → "
            f"{_pct(am['morphologically_valid_coverage'])}; unresolved "
            f"{bm['unresolved_forms']} → {am['unresolved_forms']} tokens; "
            f"unique unresolved {c['unresolved_forms']['before_unique']} → "
            f"{c['unresolved_forms']['after_unique']}.")
    summary_md += ["", "See per-run comparison.md/json for details.", ""]
    (COMPARISON_DIR / "comparison.md").write_text(
        "\n".join(summary_md), encoding="utf-8")
    print("\n" + "\n".join(summary_md))

    # Human review pairs: complete before/after texts, first N pilot runs.
    pairs = []
    for c in comparisons:
        pilot_input = INPUT_DIR / c["pilot_run_id"]
        revised = OUTPUTS_DIR / c["pilot_run_id"] / "revised.txt"
        pairs.append((c["pilot_run_id"],
                      (pilot_input / "original.txt").read_text(encoding="utf-8"),
                      revised.read_text(encoding="utf-8")))
        if len(pairs) >= max(1, args.human_pairs):
            break
    (COMPARISON_DIR / "human_review.md").write_text(
        render_human_pairs(pairs), encoding="utf-8")
    print(f"[human-review] wrote {len(pairs)} complete before/after pair(s) to "
          f"{COMPARISON_DIR / 'human_review.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
