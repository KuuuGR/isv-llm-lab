#!/usr/bin/env python3
"""Prepare the Experiment 001 manual-audit sample of unresolved forms.

Reads the completed Experiment 001 outputs (`outputs/comparison.json` plus each
run's `unresolved.json`) and writes a stratified sample of ~100 unique
unresolved forms under `experiments/exp001-baseline/manual-audit/` for human
inspection by the Project Owner / Architect.

The sample is stratified to maximize the information a human reviewer gets:

- A  high-frequency unresolved forms (across all models)
- B  shared-by-multiple-model forms (2..6 models), prioritized by spread
- C  model-specific forms (1 model), spread across the seven conditions
- D  diverse / edge-case forms (orthographic + evaluator-interest features)
- E  representative proper-name / special-case forms (story name families)
- SHARED_ALL  the 8 forms unresolved in all seven models (diagnostic appendix)

No linguistic-origin classification is performed anywhere in this script.
The only judgments encoded are factual resource relationships (e.g. whether a
form matches a lexicon entry once diacritics are stripped) and the explicit
name families that occur in the Polish source story.

Selection is deterministic (fixed seed for tie-breaking only). Run:

    python scripts/sample_exp001_audit.py

"""

from __future__ import annotations

import csv
import json
import re
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from isv_eval.lexicon import Lexicon
from isv_eval.normalize import normalize_word

OUTPUTS_DIR = PROJECT_ROOT / "experiments" / "exp001-baseline" / "outputs"
AUDIT_DIR = PROJECT_ROOT / "experiments" / "exp001-baseline" / "manual-audit"
LEXICON_TSV = PROJECT_ROOT / "data" / "dictionary" / "lexicon.tsv"

MODEL_ORDER = ["ChatGPT", "Gemini", "Claude", "DeepSeek",
               "Bielik", "Grok", "GPTs — ISV Teacher"]

SHARED_ALL_TARGET = 8
MAIN_TARGETS = {"A": 25, "B": 25, "C": 25, "D": 15, "E": 10}
SEED = 20260831

# Name families present in the Polish source story (op-pl.txt), matched
# against the *normalized* unresolved form. These are the story's character
# and place names; their many orthographic variants are exactly what we want
# the human reviewer to look at. This is not language-origin classification.
NAME_PATTERNS = [
    ("Bronislawa", re.compile(r"^bronislav")),
    ("Teofil", re.compile(r"^teofil")),
    ("Julianna", re.compile(r"^juli(j)?an")),
    ("Przemyslawa", re.compile(r"^przemys[łl]aw|^prěmyslav|^přemyslav|^premis")),
    ("Miedzyrzecze", re.compile(r"^medzureč|^medžureč|^mežurěč|^meždurěč|^međuzeml")),
    ("Antoni", re.compile(r"^antoni")),
]

_ETYM_CHARS = set("åęųȯėćđďĺľńŕśťź")
_ISV_CHARS = set("čšžě")


def name_family(normalized: str) -> str | None:
    for family, pattern in NAME_PATTERNS:
        if pattern.match(normalized):
            return family
    return None


def strip_diacritics(text: str) -> str:
    decomposed = unicodedata.normalize("NFD", text)
    return "".join(ch for ch in decomposed
                   if unicodedata.category(ch) != "Mn")


def load_runs(comparison: dict) -> dict[str, dict]:
    runs = {}
    for label, info in comparison["runs"].items():
        run_dir = OUTPUTS_DIR / info["run_id"]
        unresolved = json.loads((run_dir / "unresolved.json").read_text(
            encoding="utf-8"))
        index: dict[str, list] = {}
        for rec in unresolved:
            index.setdefault(rec["normalized"], []).append(rec)
        runs[label] = {
            "run_id": info["run_id"],
            "records": unresolved,
            "index": index,
        }
    return runs


def aggregate_forms(comparison: dict, runs: dict[str, dict], lexicon: Lexicon):
    overlap = comparison["unresolved_overlap"]
    forms = {}
    for row in overlap["form_table"]:
        form = row["form"]
        per_model = {m: row.get(m, 0) for m in MODEL_ORDER}
        occurrences = {}
        for m in MODEL_ORDER:
            recs = runs[m]["index"].get(form, [])
            occurrences[m] = recs
        first = next((rec for recs in occurrences.values() for rec in recs), None)
        cands = sorted({c for recs in occurrences.values() for rec in recs
                        for c in (rec.get("candidates") or [])})
        forms[form] = {
            "form": form,
            "normalized_form": form,
            "per_model": per_model,
            "total_frequency": sum(per_model.values()),
            "model_count": row["models_with_form"],
            "models": [m for m in MODEL_ORDER if per_model[m] > 0],
            "occurrences": occurrences,
            "first_record": first,
            "candidate_lemmas": cands,
            "candidate_count": len(cands),
            "translit": first.get("translit") if first else None,
            "review": bool(first.get("review")) if first else True,
            "name_family": name_family(form),
            "features": {
                "etymological_char": bool(set(form) & _ETYM_CHARS),
                "isv_char": bool(set(form) & _ISV_CHARS),
                "long": len(form) >= 12,
                "zero_candidates": len(cands) == 0,
                "many_candidates": len(cands) >= 30,
            },
        }
        stripped = strip_diacritics(form)
        if stripped != form and lexicon.lookup(stripped):
            forms[form]["features"]["diacritic_variant_of_known"] = True
        else:
            forms[form]["features"]["diacritic_variant_of_known"] = False
    return forms


def pick(sorted_pool, n: int, exclude: set[str]) -> list[str]:
    picked = []
    for form in sorted_pool:
        if form in exclude:
            continue
        picked.append(form)
        if len(picked) >= n:
            break
    return picked


def pick_spread(by_model: dict[str, list[str]], n: int,
                exclude: set[str]) -> list[str]:
    """Pick n model-specific forms, at least one per model, highest-freq first."""
    order = [m for m in MODEL_ORDER if m in by_model]
    buckets = {m: [f for f in by_model[m] if f not in exclude] for m in order}
    picked: list[str] = []
    idx = {m: 0 for m in order}
    # guarantee >= 1 per model first, then fill round-robin
    for m in order:
        if buckets[m]:
            picked.append(buckets[m][0])
            idx[m] = 1
    while len(picked) < n:
        progressed = False
        for m in order:
            if len(picked) >= n:
                break
            if idx[m] < len(buckets[m]):
                picked.append(buckets[m][idx[m]])
                idx[m] += 1
                progressed = True
        if not progressed:
            break
    return picked


def select_sample(forms) -> dict[str, list[str]]:
    shared_all = sorted(f for f in forms if forms[f]["model_count"] == 7)
    assert len(shared_all) == SHARED_ALL_TARGET

    non_names = [f for f in forms if not forms[f]["name_family"]]
    shared_all_set = set(shared_all)

    # A: high frequency across models (non-name, non-shared-all)
    pool_a = sorted(non_names,
                    key=lambda f: (-forms[f]["total_frequency"],
                                   -forms[f]["model_count"], f))
    group_a = pick(pool_a, MAIN_TARGETS["A"], shared_all_set)

    # B: shared by 2..6 models, prioritized by spread
    pool_b = [f for f in non_names
              if 2 <= forms[f]["model_count"] <= 6]
    pool_b.sort(key=lambda f: (-forms[f]["model_count"],
                               -forms[f]["total_frequency"], f))
    group_b = pick(pool_b, MAIN_TARGETS["B"], set(group_a) | shared_all_set)

    # C: model-specific, spread across models
    by_model: dict[str, list[str]] = {}
    for f in non_names:
        if forms[f]["model_count"] != 1:
            continue
        m = forms[f]["models"][0]
        by_model.setdefault(m, []).append(f)
    for m in by_model:
        by_model[m].sort(key=lambda f: (-forms[f]["total_frequency"], f))
    group_c = pick_spread(by_model, MAIN_TARGETS["C"],
                          set(group_a) | set(group_b) | shared_all_set)

    # D: diverse / edge-case from the remaining pool
    pool_d = [f for f in non_names
              if f not in set(group_a) | set(group_b) | set(group_c)
              and f not in shared_all_set]
    group_d = pick_diverse(pool_d, MAIN_TARGETS["D"], forms)

    # E: representative proper names / special cases (non-shared-all).
    # Explicitly curated to cover all six story name families and to expose
    # orthographic/case variants for human review (e.g. same entity spelled
    # with and without diacritics, nominative vs oblique case forms).
    # SHARED_ALL forms (bronislava, teofil, …) are kept out — they live in
    # the diagnostic appendix.
    group_e = ["julianna", "julijana", "antoni", "antonija", "teofilu",
               "przemysława", "prěmyslava", "medžurečje", "bronislavu",
               "bronislavy"]

    return {
        "A": group_a, "B": group_b, "C": group_c,
        "D": group_d, "E": group_e, "SHARED_ALL": shared_all,
    }


def pick_diverse(pool, n: int, forms) -> list[str]:
    """Deterministic feature-bucketed selection of interesting edge cases."""
    def score(f):
        feat = forms[f]["features"]
        s = 0
        s += 3 if feat["diacritic_variant_of_known"] else 0
        s += 2 if feat["zero_candidates"] else 0
        s += 2 if feat["etymological_char"] else 0
        s += 1 if feat["many_candidates"] else 0
        s += 1 if feat["long"] else 0
        s += 1 if feat["isv_char"] else 0
        return s

    def bucket(f):
        feat = forms[f]["features"]
        if feat["diacritic_variant_of_known"]:
            return "diacritic_variant"
        if feat["zero_candidates"]:
            return "zero_candidates"
        if feat["etymological_char"]:
            return "etymological"
        if feat["many_candidates"]:
            return "many_candidates"
        if feat["long"]:
            return "long"
        return "other"

    candidates = sorted(pool, key=lambda f: (-score(f), f))
    buckets: dict[str, list[str]] = {}
    for f in candidates:
        buckets.setdefault(bucket(f), []).append(f)
    picked: list[str] = []
    order = ["diacritic_variant", "zero_candidates", "etymological",
             "many_candidates", "long", "other"]
    idx = {b: 0 for b in order}
    while len(picked) < n:
        progressed = False
        for b in order:
            if len(picked) >= n:
                break
            while idx[b] < len(buckets.get(b, [])):
                picked.append(buckets[b][idx[b]])
                idx[b] += 1
                progressed = True
                if len(picked) >= n:
                    break
        if not progressed:
            break
    return picked


def representative_sentence(forms, runs, form: str) -> dict | None:
    """First occurrence in the model with the highest frequency for the form."""
    per_model = forms[form]["per_model"]
    best_model = max((m for m in MODEL_ORDER if per_model[m] > 0),
                     key=lambda m: (per_model[m], MODEL_ORDER.index(m)))
    recs = forms[form]["occurrences"][best_model]
    rec = min(recs, key=lambda r: (r["sentence_id"], r["position"]))
    return {
        "model": best_model,
        "run_id": runs[best_model]["run_id"],
        "token": rec["token"],
        "sentence": rec["sentence"],
        "sentence_id": rec["sentence_id"],
        "position": rec["position"],
    }


def freq_string(forms, form: str) -> str:
    parts = [f"{m}×{forms[form]['per_model'][m]}"
             for m in MODEL_ORDER if forms[form]["per_model"][m] > 0]
    return "; ".join(parts)


def main() -> None:
    comparison = json.loads((OUTPUTS_DIR / "comparison.json").read_text(
        encoding="utf-8"))
    runs = load_runs(comparison)
    lexicon = Lexicon.load_tsv(LEXICON_TSV)
    forms = aggregate_forms(comparison, runs, lexicon)

    # ----- statistics (§11 of the task) -----
    total_unique = len(forms)
    total_occ = sum(f["total_frequency"] for f in forms.values())
    shared_counts = {n: sum(1 for f in forms.values()
                            if f["model_count"] == n) for n in range(1, 8)}
    per_model_occ = {m: sum(f["per_model"][m] for f in forms.values())
                     for m in MODEL_ORDER}
    candidate_records = sum(len(r["records"]) for r in runs.values())
    no_cand = sum(1 for r in runs.values() for rec in r["records"]
                  if not (rec.get("candidates") or []))
    with_cand = candidate_records - no_cand

    selection = select_sample(forms)
    group_rows = {g: len(sel) for g, sel in selection.items()}
    total_rows = sum(group_rows.values())

    # ----- build sample records -----
    sample = []
    for group in ["A", "B", "C", "D", "E", "SHARED_ALL"]:
        for form in selection[group]:
            f = forms[form]
            rep = representative_sentence(forms, runs, form)
            occurrences = []
            sentence_context = []
            for m in MODEL_ORDER:
                recs = f["occurrences"][m]
                if not recs:
                    continue
                first = min(recs, key=lambda r: (r["sentence_id"], r["position"]))
                sentence_context.append({
                    "model": m,
                    "sentence": first["sentence"],
                    "sentence_id": first["sentence_id"],
                })
                for rec in recs:
                    occurrences.append({
                        "model": m,
                        "run_id": runs[m]["run_id"],
                        "token": rec["token"],
                        "sentence": rec["sentence"],
                        "sentence_id": rec["sentence_id"],
                        "paragraph_id": rec["paragraph_id"],
                        "position": rec["position"],
                        "candidates": rec.get("candidates") or [],
                        "review": bool(rec.get("review")),
                    })
            sample.append({
                "id": f"g{group}-{form}",
                "group": group,
                "form": f["form"],
                "normalized_form": f["normalized_form"],
                "models": f["models"],
                "model_count": f["model_count"],
                "total_frequency": f["total_frequency"],
                "frequency_per_model": {m: f["per_model"][m]
                                        for m in MODEL_ORDER
                                        if f["per_model"][m] > 0},
                "sentence_context": sentence_context,
                "representative_sentence": rep,
                "translit": f["translit"],
                "classification": "C",
                "review": f["review"],
                "name_family": f["name_family"],
                "features": f["features"],
                "candidate_lemmas": f["candidate_lemmas"],
                "candidate_lemma_count": f["candidate_count"],
                "candidate_forms": [],
                "occurrence_count": sum(len(f["occurrences"][m])
                                        for m in MODEL_ORDER),
                "occurrences": occurrences,
            })

    source_meta = json.loads(
        (PROJECT_ROOT / "experiments" / "exp001-baseline" / "input"
         / "source.meta.json").read_text(encoding="utf-8"))
    stats = {
        "experiment": "exp001",
        "source_sha256": source_meta.get("sha256"),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generator_script": "scripts/sample_exp001_audit.py",
        "total_unique_unresolved_forms": total_unique,
        "total_unresolved_occurrences": total_occ,
        "forms_shared_by_n_models": shared_counts,
        "unresolved_occurrences_per_model": per_model_occ,
        "candidate_stats": {
            "unresolved_records_total": candidate_records,
            "records_with_no_candidate_lemmas": no_cand,
            "records_with_candidate_lemmas": with_cand,
        },
        "shared_by_all_forms": selection["SHARED_ALL"],
        "sample_composition": group_rows,
        "sample_total_rows": total_rows,
    }

    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    (AUDIT_DIR / "statistics.json").write_text(
        json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")
    (AUDIT_DIR / "sample.json").write_text(
        json.dumps({"statistics": stats, "sample": sample},
                   ensure_ascii=False, indent=2), encoding="utf-8")

    # ----- CSV worksheet -----
    csv_path = AUDIT_DIR / "sample.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow([
            "id", "group", "form", "normalized_form", "models",
            "model_count", "total_frequency", "frequency_per_model",
            "sentence", "sentence_model", "sentence_id",
            "candidate_lemmas", "candidate_lemma_count", "candidate_forms",
            "translit", "human_class", "human_notes", "confidence",
        ])
        for rec in sample:
            lemmas = rec["candidate_lemmas"]
            if len(lemmas) > 12:
                lemma_str = " | ".join(lemmas[:12]) + \
                    f" | ... (+{len(lemmas) - 12} more)"
            elif lemmas:
                lemma_str = " | ".join(lemmas)
            else:
                lemma_str = "(none)"
            writer.writerow([
                rec["id"], rec["group"], rec["form"], rec["normalized_form"],
                "; ".join(rec["models"]), rec["model_count"],
                rec["total_frequency"], freq_string(forms, rec["form"]),
                rec["representative_sentence"]["sentence"],
                rec["representative_sentence"]["model"],
                rec["representative_sentence"]["sentence_id"],
                lemma_str, rec["candidate_lemma_count"],
                "(none produced by evaluator)", rec["translit"] or "",
                "", "", "",
            ])

    print(f"wrote {AUDIT_DIR/'statistics.json'}")
    print(f"wrote {AUDIT_DIR/'sample.json'}")
    print(f"wrote {csv_path}")
    print("sample composition:", group_rows)
    print(f"total rows: {total_rows} "
          f"(main groups: {sum(group_rows[k] for k in 'ABCDE')} "
          f"+ SHARED_ALL appendix: {group_rows['SHARED_ALL']})")


if __name__ == "__main__":
    main()
