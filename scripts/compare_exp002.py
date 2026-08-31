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

import difflib
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


def align_lexical(
    before_tokens: list[dict],
    after_tokens: list[dict],
) -> list[tuple[dict | None, dict | None]]:
    """Align lexical token sequences (by normalized form) with LCS (difflib).

    Returns aligned pairs; unmatched positions carry None. Pairs are used to
    describe evaluator-state transitions per position — never as a claim about
    linguistic correctness.
    """
    b = [t for t in before_tokens if t.get("is_lexical")]
    a = [t for t in after_tokens if t.get("is_lexical")]
    b_norms = [t["normalized"] for t in b]
    a_norms = [t["normalized"] for t in a]
    matcher = difflib.SequenceMatcher(None, b_norms, a_norms, autojunk=False)
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
    pairs: list[tuple[dict | None, dict | None]],
) -> tuple[dict[str, int], dict[str, list[dict]]]:
    """Per-position before→after evaluator-class transitions.

    matrix keys: A→A, A→B, A→C, B→A, B→B, B→C, C→A, C→B, C→C, plus
    unmatched_before / unmatched_after for alignment gaps.
    detail: A_to_C, B_to_C, C_to_A, C_to_B, A_to_B, B_to_A — lists of
    {"form", "replacement", "count"} aggregated over aligned positions where
    the surface changed. Evaluator-state transitions only.
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
        key = f"{b_cls}→{a_cls}"
        matrix[key] += 1
        b_form, a_form = b_tok["normalized"], a_tok["normalized"]
        if b_form != a_form:
            form_pairs[(b_cls, a_cls)][(b_form, a_form)] += 1
    detail: dict[str, list[dict]] = {}
    for pair_key, list_key in [
        (("A", "C"), "A_to_C"),
        (("B", "C"), "B_to_C"),
        (("C", "A"), "C_to_A"),
        (("C", "B"), "C_to_B"),
        (("A", "B"), "A_to_B"),
        (("B", "A"), "B_to_A"),
    ]:
        entries = [
            {"form": f, "replacement": r, "count": c}
            for (f, r), c in sorted(form_pairs[pair_key].items())
        ]
        if entries:
            detail[list_key] = entries
    return dict(matrix), detail


def candidate_usage(
    records: list[dict],
    pairs: list[tuple[dict | None, dict | None]],
    after_tokens: list[dict],
    after_lexical: set[str],
) -> list[dict]:
    """Per selected form: supplied candidates, usage in revised output,
    evaluator acceptance, whether the original form disappeared, and which
    surfaces actually replaced it at its aligned positions."""
    out: list[dict] = []
    for rec in records:
        form = rec["form"]
        form_key = form.lower()
        supplied = sorted({alt["surface"].lower()
                           for alt in rec.get("alternatives", [])})
        supplied_set = set(supplied)
        used = sorted(supplied_set & after_lexical)
        accepted = sorted({t["token"].lower() for t in after_tokens
                           if t["token"].lower() in supplied_set
                           and t.get("classification") in ("A", "B")})
        replacements: Counter = Counter()
        for b_tok, a_tok in pairs:
            if (b_tok is not None and a_tok is not None
                    and b_tok["normalized"].lower() == form_key):
                replacements[a_tok["normalized"]] += 1
        replacement_surfaces = {s: c for s, c in sorted(replacements.items())}
        other = sorted({s for s in replacements
                        if s.lower() != form_key and s.lower() not in supplied_set})
        out.append({
            "form": form,
            "stratum": rec.get("stratum"),
            "candidate_surfaces_supplied": supplied,
            "candidate_surfaces_used_in_revised": used,
            "candidate_surfaces_accepted_in_revised": accepted,
            "original_form_disappeared": form_key not in after_lexical,
            "replacement_surfaces_at_form_positions": replacement_surfaces,
            "non_supplied_surfaces_introduced": other,
        })
    return out


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

    before_tokens = load_tokens(before_dir)
    after_tokens = load_tokens(after_dir)
    before_lexical = {t["token"].lower() for t in before_tokens}
    after_lexical = {t["token"].lower() for t in after_tokens}
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
    for t in after_tokens:
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

    # Evaluator-state transitions (token-aligned) and per-form candidate usage.
    pairs = align_lexical(before_tokens, after_tokens)
    transition_matrix, transition_detail = transition_stats(pairs)
    usage = candidate_usage(records, pairs, after_tokens, after_lexical)

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
        "transitions": {
            "method": "per-position LCS alignment of lexical tokens; "
                      "before→after evaluator class; evaluator-state "
                      "transitions only, no linguistic judgment",
            "matrix": transition_matrix,
            "detail": transition_detail,
        },
        "candidate_usage": usage,
        "note": "Metrics from the same isv-eval evaluator; replacement "
                "bookkeeping is deterministic and evidence-based; no "
                "linguistic quality score.",
    }
    return comparison


def load_tokens(eval_dir: Path) -> list[dict]:
    with open(eval_dir / "tokens.json", encoding="utf-8") as fh:
        return json.load(fh)


def render_transitions(comparison: dict, lines: list[str]) -> None:
    t = comparison.get("transitions")
    if not t:
        return
    matrix = t["matrix"]
    lines += [
        "",
        "## Evaluator-state transitions (token-aligned, same evaluator)",
        "",
        "| transition | count |",
        "|---|---:|",
    ]
    order = ["A→A", "A→B", "A→C", "B→A", "B→B", "B→C", "C→A", "C→B", "C→C",
             "unmatched_before", "unmatched_after"]
    for key in order:
        lines.append(f"| {key} | {matrix.get(key, 0)} |")
    lines.append("")
    detail = t["detail"]
    for key, label in [
        ("A_to_C", "A→C regressions (previously exact → unresolved)"),
        ("B_to_C", "B→C regressions (previously morphologically valid → unresolved)"),
        ("C_to_A", "C→A resolutions (previously unresolved → exact)"),
        ("C_to_B", "C→B resolutions (previously unresolved → morphologically valid)"),
        ("A_to_B", "A→B (previously exact → morphologically valid only)"),
        ("B_to_A", "B→A (previously morphologically valid → exact)"),
    ]:
        entries = detail.get(key)
        if entries:
            lines.append(f"{label}:")
            lines.append("  " + "; ".join(
                f"{e['form']} → {e['replacement']} (×{e['count']})"
                for e in entries))
            lines.append("")


def render_candidate_usage(comparison: dict, lines: list[str]) -> None:
    usage = comparison.get("candidate_usage")
    if not usage:
        return
    lines += [
        "",
        "## Candidate usage per selected form",
        "",
        "| form | supplied | used | accepted | original gone | replacement(s) | "
        "other non-supplied |",
        "|---|---|---|---|---|---|---|",
    ]
    for u in usage:
        supplied = ", ".join(u["candidate_surfaces_supplied"][:4])
        if len(u["candidate_surfaces_supplied"]) > 4:
            supplied += " …"
        repl = ", ".join(f"{s}×{c}" for s, c
                         in u["replacement_surfaces_at_form_positions"].items()) or "—"
        other = ", ".join(u["non_supplied_surfaces_introduced"]) or "—"
        lines.append(
            f"| {u['form']} | {len(u['candidate_surfaces_supplied'])} "
            f"({supplied}) | {len(u['candidate_surfaces_used_in_revised'])} | "
            f"{len(u['candidate_surfaces_accepted_in_revised'])} | "
            f"{'yes' if u['original_form_disappeared'] else 'no'} | "
            f"{repl} | {other} |")
    lines.append("")


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
    render_transitions(comparison, lines)
    render_candidate_usage(comparison, lines)
    lines += ["", "No linguistic quality score is assigned.", ""]
    return "\n".join(lines)


def _pct(v: float | None) -> str:
    return f"{v * 100:.2f}%" if v is not None else "n/a"


def _pctd(v: float | None) -> str:
    if v is None:
        return "n/a"
    return f"{v * 100:+.2f}%"


def render_human_pairs(pairs: list[tuple[str, str, str, str]]) -> str:
    """Complete before/after text pairs for holistic Project-Owner reading.

    Qualitative evidence only — no word-by-word annotation, no scoring.
    Each pair is the COMPLETE original translation and the COMPLETE revised
    output of one pilot run, stored verbatim. Each pair carries only an
    outcome category (a descriptive label of evaluator coverage change), so
    the Project Owner can select examples without lexical annotation.
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
        "Each pair is labeled only with the observed outcome category "
        "(evaluator coverage change); no word-by-word annotation is given.",
        "",
    ]
    for i, (run_id, outcome, before, after) in enumerate(pairs, start=1):
        lines += [
            f"## Pair {i} — {run_id}",
            "",
            f"**Outcome category:** {outcome}",
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


# Representative outcome categories for holistic reading. Selected
# deterministically to cover different observed outcomes; raw outputs stay
# byte-for-byte. The categories are evaluator-coverage labels only.
HUMAN_PAIR_SELECTION: dict[str, str] = {
    "exp002__2026-08-31__openai__chatgpt__unknown":
        "clear improvement, no new unresolved unique forms",
    "exp002__2026-08-31__google__gemini__unknown":
        "improvement with no A→C regression",
    "exp002__2026-08-31__anthropic__claude__unknown":
        "improvement with A→C regression (različ-* → růz-* spellings)",
    "exp002__2026-08-31__deepseek__deepseek__unknown":
        "little improvement (+0.35 pp)",
    "exp002__2026-08-31__unknown__bielik__unknown":
        "no change (formatting-only revision)",
}


def main(argv: list[str] | None = None) -> int:
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot-run", default=None,
                        help="single pilot run id; default: all with a revised output")
    parser.add_argument("--human-pairs", type=int, default=len(HUMAN_PAIR_SELECTION),
                        help="number of complete before/after pairs to write "
                             "into the human-review doc")
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

    # Human review pairs: complete before/after texts, selected across
    # outcome categories in HUMAN_PAIR_SELECTION order (deterministic).
    by_id = {c["pilot_run_id"]: c for c in comparisons}
    pairs: list[tuple[str, str, str, str]] = []
    for run_id in HUMAN_PAIR_SELECTION:
        c = by_id.get(run_id)
        if not c or len(pairs) >= max(1, args.human_pairs):
            continue
        pilot_input = INPUT_DIR / run_id
        revised = OUTPUTS_DIR / run_id / "revised.txt"
        pairs.append((run_id, HUMAN_PAIR_SELECTION[run_id],
                      (pilot_input / "original.txt").read_text(encoding="utf-8"),
                      revised.read_text(encoding="utf-8")))
    (COMPARISON_DIR / "human_review.md").write_text(
        render_human_pairs(pairs), encoding="utf-8")
    print(f"[human-review] wrote {len(pairs)} complete before/after pair(s) to "
          f"{COMPARISON_DIR / 'human_review.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
