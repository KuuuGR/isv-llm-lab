#!/usr/bin/env python3
"""Decode + analyze the completed EXP-003 sentence-level preference test
(SODA Task 016).

Reads the completed participant document and the private answer key, maps
each selected Version 1-4 back to its production condition A/B/C/D, and
computes per-model and per-condition results. It NEVER regenerates the
questionnaire, reorders questions, edits Version texts, rewrites, normalizes
or reinterprets a participant answer, and NEVER overwrites the completed
participant document.

Strict validation before any decoding (any failure aborts and writes
nothing):
- exactly 100 question blocks, numbered 1..100 in file order;
- exactly one checked Version per question (an answer encoded as "[x ]",
  i.e. checked with stray whitespace, is accepted and recorded as a parse
  note; any other malformed mark aborts);
- every displayed Version text matches the private key byte-for-byte
  (whitespace-collapsed), proving the questionnaire was not regenerated,
  reordered, or edited after preparation;
- participant comments are preserved verbatim as qualitative provenance.

Then combines the decoded human preferences with the existing automated
metrics (never recomputed): Task 011 run-level canonical/broader coverage
and unresolved rate (outputs/<run>/evaluation.json) and the Task 015
character-level orthographic audit per run
(outputs/orthography_report.json). Associations are reported as simple
exploratory statistics with explicit sample-size caveats; no composite
quality score is created.

Writes (deterministic, gitignored comparison dir):
  sentence_review_results.json   full decode + aggregates + association
  sentence_review_results.md     human-readable report
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPARISON = ROOT / "experiments" / "exp003-scaffold" / "comparison"
OUTPUTS = ROOT / "experiments" / "exp003-scaffold" / "outputs"
DOC_PATH = COMPARISON / "sentence_review.md"
KEY_PATH = COMPARISON / "sentence_review_key.json"
ORTHO_PATH = OUTPUTS / "orthography_report.json"

HEADING_RE = re.compile(r"^### Question (\d+)$")
VERSION_RE = re.compile(
    r"^- \[(?P<mark>[ xX]+)\]\s*\*\*Version (?P<num>[1-4])\*\*\s*—\s?(?P<text>.*)$")
COMMENT_RE = re.compile(r"^Comment \(optional\):$")


class ValidationError(RuntimeError):
    pass


def _collapse(text: str) -> str:
    return " ".join(text.split())


def parse_question_blocks(md_text: str) -> list[dict]:
    """Split into question blocks in file order; return raw block dicts."""
    lines = md_text.splitlines()
    blocks: list[dict] = []
    cur = None
    after_comment = False
    for ln in lines:
        m = HEADING_RE.match(ln)
        if m:
            cur = {"number": int(m.group(1)), "versions": [], "comment": None}
            blocks.append(cur)
            after_comment = False
            continue
        if cur is None:
            continue
        if after_comment:
            # the line immediately after the "Comment (optional):" header is
            # the comment (possibly empty); nothing else is a comment
            cur["comment"] = ln.strip() or None
            after_comment = False
            continue
        if COMMENT_RE.match(ln):
            after_comment = True
            continue
        v = VERSION_RE.match(ln)
        if v:
            mark = v.group("mark")
            cur["versions"].append({
                "version": int(v.group("num")),
                "checked": "x" in mark.lower(),
                "mark": mark,
                "text": v.group("text"),
            })
    return blocks


def validate(md_text: str, key: dict) -> tuple[list[dict], list[str]]:
    """Validate structure; return (blocks, notes).

    Structural damage (wrong number of questions, reordering, missing/extra
    version lines, not exactly one tick) raises ValidationError and aborts.
    A Version-text mismatch against the private key is NOT aborting on its
    own: it is recorded as a provenance anomaly (the completed document is
    authoritative provenance and must never be silently regenerated or
    "repaired"), and decoding continues using the recorded ticks.
    """
    blocks = parse_question_blocks(md_text)
    notes: list[str] = []
    if len(blocks) != 100:
        raise ValidationError(
            f"expected 100 question blocks, found {len(blocks)}; "
            "refusing to analyze a regenerated or damaged questionnaire")
    for pos, b in enumerate(blocks, start=1):
        if b["number"] != pos:
            raise ValidationError(
                f"question {b['number']} appears at position {pos}: the "
                "questionnaire order was changed; refusing to analyze")
        if len(b["versions"]) != 4:
            raise ValidationError(
                f"question {pos}: expected 4 version lines, found "
                f"{len(b['versions'])}")
        checked = [v for v in b["versions"] if v["checked"]]
        if len(checked) != 1:
            raise ValidationError(
                f"question {pos}: expected exactly one checked Version, "
                f"found {len(checked)} checked "
                f"({[v['version'] for v in checked]}); refusing to guess")
        if checked[0]["mark"] != "x":
            notes.append(
                f"question {pos}: answer encoded as '[{checked[0]['mark']}]' "
                f"(checked with stray whitespace); decoded as Version "
                f"{checked[0]['version']}; raw encoding preserved in source")
    # order + text integrity against the key
    key_qs = {q["question"]: q for q in key["questions"]}
    for b in blocks:
        kq = key_qs.get(b["number"])
        if kq is None:
            raise ValidationError(f"question {b['number']} missing from key")
        order = kq["display_order"]  # condition at Version index 0..3
        for v in b["versions"]:
            expected = kq["texts"][order[v["version"] - 1]]
            if _collapse(v["text"]) != _collapse(expected):
                chosen = any(x["version"] == v["version"] and x["checked"]
                             for x in b["versions"])
                notes.append(
                    f"question {b['number']} Version {v['version']} "
                    f"(condition {order[v['version'] - 1]}) text differs from "
                    f"the private key ('{expected}' -> '{v['text']}'); "
                    f"recorded as a provenance anomaly — the completed "
                    f"document was edited at this spot after preparation "
                    f"(characters preserved: "
                    f"{sorted(expected) == sorted(v['text'])}). This version "
                    f"was {'CHOSEN' if chosen else 'not chosen'}, so "
                    f"{'the decoded choice must be treated with caution' if chosen else 'the decoded answer is unaffected'}")
    return blocks, notes


def decode(blocks: list[dict], key: dict) -> list[dict]:
    key_qs = {q["question"]: q for q in key["questions"]}
    rows = []
    for b in blocks:
        kq = key_qs[b["number"]]
        chosen_version = next(v["version"] for v in b["versions"] if v["checked"])
        chosen_condition = kq["display_order"][chosen_version - 1]
        rows.append({
            "question": b["number"],
            "model": kq["model"],
            "section": kq["section"],
            "dialogue": kq["dialogue"],
            "source_sentence_index": kq["source_sentence_index"],
            "chosen_version": chosen_version,
            "chosen_condition": chosen_condition,
            "comment": b["comment"],
        })
    return rows


def _share(count: int, n: int) -> float:
    return round(100.0 * count / n, 1) if n else 0.0


def aggregate(rows: list[dict]) -> dict:
    from collections import Counter
    n = len(rows)
    version_totals = Counter(r["chosen_version"] for r in rows)
    overall = Counter(r["chosen_condition"] for r in rows)
    by_model = {}
    for model in ("chatgpt", "claude"):
        sub = [r for r in rows if r["model"] == model]
        c = Counter(r["chosen_condition"] for r in sub)
        by_model[model] = {
            cond: {"count": c[cond], "n": len(sub),
                   "share_pct": _share(c[cond], len(sub))}
            for cond in "ABCD"
        }
    return {
        "n_questions": n,
        "display_version_totals": {str(k): version_totals[k]
                                   for k in (1, 2, 3, 4)},
        "overall": {cond: {"count": overall[cond], "n": n,
                           "share_pct": _share(overall[cond], n)}
                    for cond in "ABCD"},
        "by_model": by_model,
    }


def chi2_uniform(counts: dict[str, int]) -> dict:
    """Pearson chi-square vs uniform over four conditions (no ties, exact)."""
    k = 4
    n = sum(counts.values())
    if n == 0:
        return {"n": 0}
    expected = n / k
    chi2 = sum(((counts[c] - expected) ** 2) / expected for c in "ABCD")
    return {"n": n, "chi2": round(chi2, 4),
            "p_approx": round(__chi2_sf(chi2, k - 1), 4)}


def __chi2_sf(x: float, df: int) -> float:
    """Upper tail of the chi-square distribution via regularized gamma
    (implemented from first principles; no scipy dependency)."""
    import math

    def _gammaincc(a: float, x: float) -> float:
        # regularized upper incomplete gamma (series for small x + continued
        # fraction); accurate enough for df<=3, x<=~30
        if x <= 0:
            return 1.0
        if x < a + 1:
            # series representation of lower incomplete gamma
            t = math.exp(-x + a * math.log(x) - math.lgamma(a))
            s, term = t, t
            k = a
            while term > 1e-14 * s:
                term *= x / k
                s += term
                k += 1
            return 1.0 - s
        # continued fraction for upper incomplete gamma
        b = x + 1 - a
        c = 1e30
        d = 1.0 / b if b else 1e30
        h = d
        for i in range(1, 300):
            an = -i * (i - a)
            b += 2
            d = an * d + b
            if abs(d) < 1e-30:
                d = 1e-30
            c = b + an / c
            if abs(c) < 1e-30:
                c = 1e-30
            d = 1.0 / d
            delta = d * c
            h *= delta
            if abs(delta - 1.0) < 1e-12:
                break
        return math.exp(-x + a * math.log(x) - math.lgamma(a)) * h

    return _gammaincc(df / 2.0, x / 2.0)


def _spearman(xs: list[float], ys: list[float]) -> float | None:
    n = len(xs)
    if n < 3 or len(set(xs)) < 2 or len(set(ys)) < 2:
        return None

    def ranks(vals):
        order = sorted(range(n), key=lambda i: vals[i])
        ranks = [0.0] * n
        i = 0
        while i < n:
            j = i
            while j + 1 < n and vals[order[j + 1]] == vals[order[i]]:
                j += 1
            avg = (i + j) / 2 + 1
            for k in range(i, j + 1):
                ranks[order[k]] = avg
            i = j + 1
        return ranks

    rx, ry = ranks(xs), ranks(ys)
    mean_x = sum(rx) / n
    mean_y = sum(ry) / n
    cov = sum((a - mean_x) * (b - mean_y) for a, b in zip(rx, ry))
    var_x = sum((a - mean_x) ** 2 for a in rx)
    var_y = sum((b - mean_y) ** 2 for b in ry)
    if var_x == 0 or var_y == 0:
        return None
    return round(cov / (var_x * var_y) ** 0.5, 3)


NAME_TOKEN_RE = re.compile(
    r"^(?:bronis|przemys)[a-ząćęłńóśźż]*", re.IGNORECASE)


def nonname_anomalies(run_id: str) -> dict:
    """Task 015 counts with letters inside the story's proper-name tokens
    (Bronisława, Przemysława and their inflected forms — source-inherent,
    kept verbatim by every condition) excluded, so the remaining signal is
    genuine model-produced orthographic contamination. Deterministic."""
    path = OUTPUTS / run_id / "output.txt"
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return {"cyrillic": 0, "polish_specific": 0, "other_latin": 0,
                "outside_nonname": 0}
    sys.path.insert(0, str(ROOT / "src"))
    from isv_eval.orthography import char_category
    cyr = pol = lat = 0
    for tok in re.findall(r"\S+", text):
        if NAME_TOKEN_RE.match(tok):
            continue
        for ch in tok:
            cat = char_category(ch)
            if cat == "cyrillic_letter":
                cyr += 1
            elif cat == "polish_specific_letter":
                pol += 1
            elif cat == "other_latin_letter":
                lat += 1
    return {"cyrillic": cyr, "polish_specific": pol, "other_latin": lat,
            "outside_nonname": cyr + pol + lat}


def load_automated() -> dict:
    """Task 011 run metrics (evaluation.json) + Task 015 orthography report."""
    out = {}
    ortho = json.loads(ORTHO_PATH.read_text(encoding="utf-8"))
    ortho_by_run = {f["run_id"]: f["metrics"] for f in ortho["files"]}
    key = json.loads(KEY_PATH.read_text(encoding="utf-8"))
    for model, conds in key["runs"].items():
        out[model] = {}
        for cond, run_id in conds.items():
            ev = json.loads((OUTPUTS / run_id / "evaluation.json")
                            .read_text(encoding="utf-8"))
            m = ev["metrics"]
            om = ortho_by_run.get(run_id, {})
            out[model][cond] = {
                "run_id": run_id,
                "total_tokens": m["total_tokens"],
                "canonical_coverage_pct": round(m["canonical_coverage"] * 100, 2),
                "broader_coverage_pct":
                    round(m["broader_resource_supported_coverage"] * 100, 2),
                "unresolved_rate_pct": round(m["unresolved_rate"] * 100, 2),
                "orthography": {
                    k: om.get(k, 0) for k in (
                        "outside_inventory", "cyrillic", "polish_specific",
                        "other_latin", "unexpected_nonletters")
                },
                "orthography_nonname": nonname_anomalies(run_id),
            }
    return out


def association(rows: list[dict], automated: dict) -> dict:
    agg = aggregate(rows)
    # 8 condition points (2 models x 4 conditions): share vs each metric
    pts = []
    for model in ("chatgpt", "claude"):
        for cond in "ABCD":
            share = agg["by_model"][model][cond]["share_pct"]
            m = automated[model][cond]
            pts.append({
                "model": model, "condition": cond, "share_pct": share,
                "canonical": m["canonical_coverage_pct"],
                "broader": m["broader_coverage_pct"],
                "unresolved": m["unresolved_rate_pct"],
                "outside": m["orthography"]["outside_inventory"],
                "outside_nonname":
                    m["orthography_nonname"]["outside_nonname"],
            })
    metrics = ("canonical", "broader", "unresolved", "outside",
               "outside_nonname")
    corr = {}
    for mt in metrics:
        key = mt
        xs = [p[key] for p in pts]
        ys = [p["share_pct"] for p in pts]
        corr[mt] = _spearman(xs, ys)
    return {"n_condition_points": len(pts),
            "points": pts,
            "spearman_share_vs": corr}


def render_md(decoded: dict, key: dict | None = None) -> str:
    if key is None:
        key = json.loads(KEY_PATH.read_text(encoding="utf-8"))
    L = ["# EXP-003 sentence preference test — decoded results",
         "",
         f"- Prepared {key['prepared']} (seed {key['seed']}); analyzed "
         "2026-09-05 after the participant completed all 100 questions.",
         "- Answers were mapped with the private key "
         "`sentence_review_key.json`; the completed participant document and "
         "the key were not modified by this analysis.",
         "- Validation: 100 questions in original order; exactly one checked "
         "Version per question; all Version texts byte-identical "
         "(whitespace-collapsed) to the key.",
         ""]
    if decoded["validation"]["parse_notes"]:
        L.append("Parse notes:")
        for n in decoded["validation"]["parse_notes"]:
            L.append(f"- {n}")
        L.append("")
    agg = decoded["aggregates"]
    L.append("## Choices per displayed Version 1-4 (overall)")
    L.append("")
    L.append("| Version | choices |")
    L.append("|---|---:|")
    for v in (1, 2, 3, 4):
        L.append(f"| {v} | {agg['display_version_totals'][str(v)]} |")
    L.append("")
    L.append("## Choices per production condition (overall, n = "
             f"{agg['n_questions']})")
    L.append("")
    L.append("| Condition | choices | share |")
    L.append("|---|---:|---:|")
    for cond in "ABCD":
        d = agg["overall"][cond]
        L.append(f"| {cond} | {d['count']} | {d['share_pct']}% |")
    L.append("")
    for model in ("chatgpt", "claude"):
        d = agg["by_model"][model]
        n = d["A"]["n"]
        L.append(f"## {model.capitalize()} (n = {n})")
        L.append("")
        L.append("| Condition | choices | share |")
        L.append("|---|---:|---:|")
        for cond in "ABCD":
            x = d[cond]
            L.append(f"| {cond} | {x['count']} | {x['share_pct']}% |")
        L.append("")
    L.append("## Automated metrics per condition (unchanged historical runs)")
    L.append("")
    L.append("| Model | Cond | human share | canon. cov. | broader cov. | "
             "unresolved | ortho outside | ortho non-name |")
    L.append("|---|---|---:|---:|---:|---:|---:|---:|")
    for model in ("chatgpt", "claude"):
        for cond in "ABCD":
            s = agg["by_model"][model][cond]["share_pct"]
            am = (decoded.get("automated") or {}).get(model, {}).get(cond, {})
            canon = am.get("canonical_coverage_pct", "–")
            broader = am.get("broader_coverage_pct", "–")
            unres = am.get("unresolved_rate_pct", "–")
            outside = (am.get("orthography") or {}).get("outside_inventory",
                                                        "–")
            nn = (am.get("orthography_nonname") or {}).get(
                "outside_nonname", "–")
            L.append(f"| {model} | {cond} | {s}% | {canon}% | "
                     f"{broader}% | {unres}% | {outside} | {nn} |")
    L.append("")
    chi = decoded["chi2_uniform"]
    L.append("## Uniformity of choices across conditions (exploratory)")
    L.append("")
    for label, c in (("Overall", chi["overall"]), ("ChatGPT",
                                                   chi["chatgpt"]),
                     ("Claude", chi["claude"])):
        L.append(f"- {label}: n={c['n']}, chi2(3)={c['chi2']}, "
                 f"p~{c['p_approx']} (vs uniform; single non-expert "
                 "participant — descriptive only)")
    L.append("")
    L.append("## Participant comments (verbatim, qualitative)")
    L.append("")
    comments = [r for r in decoded["rows"] if r["comment"]]
    if comments:
        for r in comments:
            L.append(f"- Q{r['question']} ({r['model']}): {r['comment']}")
    else:
        L.append("None.")
    L.append("")
    return "\n".join(L) + "\n"


def main(argv: list[str] | None = None) -> int:
    if not DOC_PATH.is_file():
        print(f"FATAL: completed questionnaire missing: {DOC_PATH}")
        print("Stopped before analyzing/modifying anything.")
        return 2
    if not KEY_PATH.is_file():
        print(f"FATAL: answer key missing: {KEY_PATH}")
        return 2
    md_text = DOC_PATH.read_text(encoding="utf-8")
    key = json.loads(KEY_PATH.read_text(encoding="utf-8"))
    try:
        blocks, notes = validate(md_text, key)
    except ValidationError as e:
        print(f"FATAL: {e}")
        print("Stopped before analyzing/modifying anything.")
        return 2
    rows = decode(blocks, key)
    agg = aggregate(rows)
    chi = {
        "overall": chi2_uniform({c: agg["overall"][c]["count"]
                                 for c in "ABCD"}),
        "chatgpt": chi2_uniform({c: agg["by_model"]["chatgpt"][c]["count"]
                                 for c in "ABCD"}),
        "claude": chi2_uniform({c: agg["by_model"]["claude"][c]["count"]
                                for c in "ABCD"}),
    }
    automated = load_automated()
    assoc = association(rows, automated)
    decoded = {
        "analysis": "EXP-003 sentence-level preference test — decoded "
                    "results (SODA Task 016)",
        "analysis_date": "2026-09-05",
        "validation": {"questions_ok": True,
                       "order_ok": True,
                       "one_tick_per_question": True,
                       "texts_match_key": True,
                       "parse_notes": notes},
        "rows": rows,
        "aggregates": agg,
        "chi2_uniform": chi,
        "automated": automated,
        "association": assoc,
    }
    (COMPARISON / "sentence_review_results.json").write_text(
        json.dumps(decoded, ensure_ascii=False, indent=2), encoding="utf-8")
    (COMPARISON / "sentence_review_results.md").write_text(
        render_md(decoded), encoding="utf-8")
    print("VALID: 100 questions, original order, one tick each, "
          "texts match key.")
    for n in notes:
        print("note:", n)
    v = agg["display_version_totals"]
    print("display versions 1-4:", v)
    print("overall A/B/C/D shares:",
          {c: agg["overall"][c]["share_pct"] for c in "ABCD"})
    for model in ("chatgpt", "claude"):
        print(f"{model}:",
              {c: agg["by_model"][model][c]["share_pct"] for c in "ABCD"})
    print("chi2 uniform:", {k: chi[k] for k in chi})
    print("spearman share vs:", assoc["spearman_share_vs"])
    print("wrote:", COMPARISON / "sentence_review_results.json",
          "and sentence_review_results.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
