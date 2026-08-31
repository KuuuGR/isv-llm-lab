"""Experiment 001 — comparative analysis across model runs.

Reads every run directory under
`experiments/exp001-baseline/outputs/` (each produced by scripts/run_exp001.py)
and writes, into the same directory:

- `comparison.json`      machine-readable metrics table + unresolved overlap
- `comparison.md`        human-readable report (table + per-form frequencies)

No linguistic interpretation is performed: this only aggregates the automatic
isv-eval measurements and the set-based overlap of unresolved vocabularies
(Task 003 §9–§10). Human linguistic judgment is a later stage.
"""

from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUTS_DIR = PROJECT_ROOT / "experiments" / "exp001-baseline" / "outputs"

RUN_DIR_HINT = "outputs/<YYYY-MM-DD>__<provider>__<model>__<model_version>/"


def load_runs() -> list[dict]:
    runs = []
    for run_dir in sorted(OUTPUTS_DIR.iterdir()):
        if not run_dir.is_dir():
            continue
        meta_path = run_dir / "meta.json"
        report_path = run_dir / "report.json"
        unresolved_path = run_dir / "unresolved.json"
        if not (meta_path.is_file() and report_path.is_file()
                and unresolved_path.is_file()):
            print(f"skip {run_dir.name}: missing artifacts "
                  "(meta.json/report.json/unresolved.json)")
            continue
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        report = json.loads(report_path.read_text(encoding="utf-8"))
        unresolved = json.loads(unresolved_path.read_text(encoding="utf-8"))
        runs.append({
            "run_id": run_dir.name,
            "meta": meta,
            "report": report,
            "unresolved": unresolved,
        })
    return runs


def model_label(meta: dict) -> str:
    return meta.get("display_name") or meta.get("model") or meta.get("provider", "?")


def summarize(runs: list[dict]) -> dict:
    table = {}
    for run in runs:
        label = model_label(run["meta"])
        m = run["report"]["metrics"]
        table[label] = {
            "provider": run["meta"]["provider"],
            "model": run["meta"]["model"],
            "model_version": run["meta"]["model_version"],
            "run_id": run["run_id"],
            "total_tokens": m["total_tokens"],
            "tokens_total": m["tokens_total"],
            "exact_dictionary_matches": m["exact_dictionary_matches"],
            "morphologically_valid_forms": m["morphologically_valid_forms"],
            "unresolved_forms": m["unresolved_forms"],
            "exact_dictionary_coverage": m["exact_dictionary_coverage"],
            "morphologically_valid_coverage": m["morphologically_valid_coverage"],
            "unresolved_rate": m["unresolved_rate"],
        }
    return table


def unresolved_overlap(runs: list[dict]) -> dict:
    """Per-normalized-form frequencies across models + set overlaps."""
    per_model = {}
    for run in runs:
        label = model_label(run["meta"])
        counts = Counter(u["normalized"] for u in run["unresolved"])
        per_model[label] = counts

    all_forms = sorted({f for counts in per_model.values() for f in counts})
    form_table = []
    for form in all_forms:
        row = {"form": form}
        for label, counts in per_model.items():
            row[label] = counts.get(form, 0)
        row["models_with_form"] = sum(1 for label in per_model
                                      if per_model[label].get(form, 0))
        form_table.append(row)

    labels = list(per_model)
    overlaps = {}
    for i, a in enumerate(labels):
        for b in labels[i + 1:]:
            key = f"{a} ∩ {b}"
            overlaps[key] = sorted(set(per_model[a]) & set(per_model[b]))

    n_models = len(labels)
    shared = {
        "unique_unresolved_forms": len(all_forms),
        "shared_by_2_or_more_models": sum(
            1 for row in form_table if row["models_with_form"] >= 2),
        "shared_by_3_or_more_models": sum(
            1 for row in form_table if row["models_with_form"] >= 3),
        "shared_by_all_models": sum(
            1 for row in form_table if row["models_with_form"] == n_models),
    }

    return {
        "per_model_unresolved_counts": {
            label: dict(counts) for label, counts in per_model.items()
        },
        "form_table": form_table,
        "pairwise_overlaps": overlaps,
        "shared_summary": shared,
    }


def render_markdown(table: dict, overlap: dict) -> str:
    lines = ["# Experiment 001 — baseline comparison",
             "", "_Automatic measurements only. No linguistic interpretation._",
             "", "## Metrics", "",
             "| Model | Lexical Tokens | Exact (A) | Morph. Valid (B) | "
             "Unresolved (C) | Valid Coverage | Unresolved Rate |",
             "| --- | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for label, row in table.items():
        lines.append(
            f"| {label} | {row['total_tokens']} | {row['exact_dictionary_matches']} "
            f"| {row['morphologically_valid_forms']} | {row['unresolved_forms']} "
            f"| {_fmt(row['morphologically_valid_coverage'])} "
            f"| {_fmt(row['unresolved_rate'])} |")
    lines += ["", "Model versions: " + "; ".join(
        f"{label}={table[label]['model_version']} ({table[label]['run_id']})"
        for label in table), ""]

    lines += ["## Unresolved forms (normalized, frequency per model)", ""]
    for row in overlap["form_table"]:
        if row["models_with_form"] < 2:
            continue  # shared forms first (Task 003 §9)
        cells = " · ".join(f"{label}: {row[label]}" for label in table
                           if row[label] > 0)
        lines.append(f"- `{row['form']}` — {cells}")
    only_one = [row for row in overlap["form_table"]
                if row["models_with_form"] < 2]
    if only_one:
        lines += ["", "Forms found in exactly one model "
                      f"({len(only_one)}): "
                  + ", ".join(f"`{r['form']}`" for r in only_one[:60])
                  + ("…" if len(only_one) > 60 else "")]

    lines += ["", "## Pairwise overlap of unresolved vocabularies (sets)", ""]
    for key, forms in overlap["pairwise_overlaps"].items():
        lines.append(f"- {key}: {len(forms)} — "
                     + ", ".join(f"`{f}`" for f in forms[:20])
                     + ("…" if len(forms) > 20 else ""))

    s = overlap["shared_summary"]
    lines += ["", "## Shared unresolved forms", "",
              f"- unique unresolved forms: **{s['unique_unresolved_forms']}**",
              f"- shared by 2+ models: **{s['shared_by_2_or_more_models']}**",
              f"- shared by 3+ models: **{s['shared_by_3_or_more_models']}**",
              f"- shared by all models: **{s['shared_by_all_models']}**"]
    return "\n".join(lines) + "\n"


def _fmt(value) -> str:
    if value is None:
        return "n/a"
    return f"{value * 100:.2f}%"


def main() -> int:
    if not OUTPUTS_DIR.is_dir():
        sys.exit(f"error: no outputs directory at {OUTPUTS_DIR}")
    runs = load_runs()
    if not runs:
        sys.exit(f"no completed runs under {OUTPUTS_DIR}\n"
                 f"expected layout: {RUN_DIR_HINT}")
    table = summarize(runs)
    overlap = unresolved_overlap(runs)
    summary = {
        "runs": table,
        "unresolved_overlap": overlap,
        "note": ("Automatic coverage measurements only; human linguistic "
                 "evaluation is a separate later stage."),
    }
    (OUTPUTS_DIR / "comparison.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUTPUTS_DIR / "comparison.md").write_text(
        render_markdown(table, overlap), encoding="utf-8")
    print(f"wrote {OUTPUTS_DIR / 'comparison.json'}")
    print(f"wrote {OUTPUTS_DIR / 'comparison.md'}")
    for label, row in table.items():
        print(f"{label:10} tokens={row['total_tokens']:5} "
              f"A={row['exact_dictionary_matches']:5} "
              f"B={row['morphologically_valid_forms']:5} "
              f"C={row['unresolved_forms']:5} "
              f"valid_cov={_fmt(row['morphologically_valid_coverage'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
