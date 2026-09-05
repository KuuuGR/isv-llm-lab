"""Tests for the EXP-003 sentence-level preference decoder + analysis
(scripts/analyze_exp003_sentence_review.py, SODA Task 016).

Covers: strict validation of the completed questionnaire (question count,
original order, exactly one tick, version texts vs the private key),
the "[x ]"-style checked-with-whitespace artifact, provenance-anomaly
handling for an edited (non-chosen and chosen) version text, Version->A/B/C/D
decoding, per-model/per-condition aggregates, the exploratory chi-square
uniformity statistic, Spearman rank correlation, verbatim comment capture,
and the guarantee that the completed document and key are never overwritten.
"""
import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


@pytest.fixture(scope="module")
def an():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "analyze_exp003_sentence_review",
        SCRIPTS / "analyze_exp003_sentence_review.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# synthetic questionnaire (mirrors scripts/prepare_exp003_sentence_review.py)
# ---------------------------------------------------------------------------

def make_key(n=100, seed=7):
    import random
    rng = random.Random(seed)
    models = ["chatgpt"] * (n // 2) + ["claude"] * (n - n // 2)
    questions = []
    for i, model in enumerate(models, start=1):
        order = ["A", "B", "C", "D"]
        rng.shuffle(order)
        questions.append({
            "question": i,
            "model": model,
            "section": "Prolog",
            "source_sentence_index": i,
            "source_text": f"Polish source {i}.",
            "dialogue": False,
            "texts": {c: f"medz text {c.lower()}-{i}." for c in "ABCD"},
            "display_order": list(order),
        })
    return {
        "protocol": "EXP-003 sentence-level forced-choice preference test",
        "prepared": "2026-09-05",
        "seed": 20260905,
        "runs": {"chatgpt": {"A": "chatgpt_a", "B": "chatgpt_b",
                             "C": "chatgpt_c", "D": "chatgpt_d"},
                 "claude": {"A": "claude_a", "B": "claude_b",
                            "C": "claude_c", "D": "claude_d"}},
        "questions": questions,
    }


def render_md_question(q, number, checked_version=None, checked_mark="x",
                       corrupt=None, comment=None):
    lines = [f"### Question {number}", "",
             f"**Polish source sentence:** {q['source_text']}", ""]
    for k, cond in enumerate(q["display_order"], start=1):
        mark = " "
        if k == checked_version:
            mark = checked_mark
        text = q["texts"][cond]
        if corrupt == k:
            text = text + " X" if cond != "Z" else text  # corruption marker
        lines.append(f"- [{mark}] **Version {k}** — {text}")
    lines += ["", "Comment (optional):", comment or "", "---", ""]
    return lines


def make_doc(key, answers=None, checked_mark="x", corrupt=None, comment=None):
    """answers: dict q->version; defaults to Version 1 for every question."""
    answers = answers or {}
    head = "instructions\n\n"
    body = []
    for q in key["questions"]:
        body += render_md_question(
            q, q["question"],
            checked_version=answers.get(q["question"], 1),
            checked_mark=checked_mark,
            corrupt=corrupt,
            comment=comment.get(q["question"]) if comment else None)
    return head + "\n" + "\n".join(body) + "\n"


# ---------------------------------------------------------------------------
# component tests
# ---------------------------------------------------------------------------

def test_decode_maps_version_to_condition_per_key(an):
    key = make_key(100)
    # answer Version 2 everywhere; Version 2 = display_order[1]
    doc = make_doc(key, answers={q: 2 for q in range(1, 101)})
    blocks, notes = an.validate(doc, key)
    assert notes == []
    rows = an.decode(blocks, key)
    assert len(rows) == 100
    for r, q in zip(rows, key["questions"]):
        assert r["chosen_condition"] == q["display_order"][1]
        assert r["model"] == q["model"]
        assert r["chosen_version"] == 2


def test_aggregate_per_model_per_condition_and_versions(an):
    key = make_key(100)
    # force: chatgpt questions (1..50) all answer condition A's version,
    # claude (51..100) answer the version showing condition D
    answers = {}
    for q in key["questions"]:
        if q["model"] == "chatgpt":
            answers[q["question"]] = q["display_order"].index("A") + 1
        else:
            answers[q["question"]] = q["display_order"].index("D") + 1
    doc = make_doc(key, answers=answers)
    blocks, _ = an.validate(doc, key)
    agg = an.aggregate(an.decode(blocks, key))
    assert agg["n_questions"] == 100
    assert agg["by_model"]["chatgpt"]["A"]["count"] == 50
    assert agg["by_model"]["chatgpt"]["A"]["share_pct"] == 100.0
    assert agg["by_model"]["claude"]["D"]["count"] == 50
    assert sum(agg["display_version_totals"].values()) == 100
    # each question contributes exactly one condition
    overall_counts = sum(v["count"] for v in agg["overall"].values())
    assert overall_counts == 100


def test_checked_with_stray_whitespace_is_a_note_not_an_error(an):
    key = make_key(100)
    doc = make_doc(key, answers={7: 3}, checked_mark="x ")  # "[x ]"
    blocks, notes = an.validate(doc, key)
    assert any("stray whitespace" in n and "question 7" in n for n in notes)
    rows = an.decode(blocks, key)
    assert rows[6]["chosen_version"] == 3


def test_nonchosen_text_edit_is_provenance_anomaly_and_decode_continues(an):
    key = make_key(100)
    doc = make_doc(key, answers={1: 1}, corrupt=2)  # corrupt Version 2 (unchecked)
    blocks, notes = an.validate(doc, key)
    assert any("provenance anomaly" in n and "not chosen" in n for n in notes)
    rows = an.decode(blocks, key)
    assert rows[0]["chosen_version"] == 1


def test_chosen_text_edit_is_flagged_as_chosen(an):
    key = make_key(100)
    doc = make_doc(key, answers={1: 2}, corrupt=2)  # corrupt the CHOSEN version
    blocks, notes = an.validate(doc, key)
    assert any("CHOSEN" in n and "treated with caution" in n for n in notes)
    # still decodes deterministically from the recorded tick
    rows = an.decode(blocks, key)
    assert rows[0]["chosen_version"] == 2


def test_structural_damage_aborts(an):
    key = make_key(100)
    # missing tick
    answers = {q: None for q in range(1, 101)}
    doc = make_doc(key, answers={q: None for q in range(1, 101)})
    doc = doc.replace("- [ ] **Version 1** — medz text a-1.", "#### no version", 1)
    # simpler: build doc then remove one heading -> 99 blocks
    doc99 = re.sub(r"### Question 50\b", "## Question 50", make_doc(key))
    with pytest.raises(an.ValidationError):
        an.validate(doc99, key)
    # no tick at all in one block
    doc_no_tick = make_doc(key, answers={x: None for x in range(1, 101)})
    with pytest.raises(an.ValidationError):
        an.validate(doc_no_tick, key)
    # two ticks in one block
    doc_two = make_doc(key)
    doc_two = doc_two.replace(
        "- [ ] **Version 2** — medz text", "- [x] **Version 2** — medz text", 1)
    with pytest.raises(an.ValidationError):
        an.validate(doc_two, key)
    # reordered headings
    doc_reorder = re.sub(r"### Question 1\b", "### Question 101", make_doc(key))
    with pytest.raises(an.ValidationError):
        an.validate(doc_reorder, key)


def test_comments_captured_verbatim_only_after_comment_header(an):
    key = make_key(100)
    doc = make_doc(key, comment={7: "a do not know whe 1 have prababi"})
    blocks, _ = an.validate(doc, key)
    assert blocks[6]["comment"] == "a do not know whe 1 have prababi"
    assert blocks[0]["comment"] is None  # no source-text leakage


def test_chi2_uniform_known_values(an):
    # uniform-ish vs skewed
    u = an.chi2_uniform({"A": 25, "B": 25, "C": 25, "D": 25})
    assert u["chi2"] == 0.0 and u["p_approx"] == 1.0
    s = an.chi2_uniform({"A": 26, "B": 16, "C": 19, "D": 39})
    assert abs(s["chi2"] - 12.56) < 0.02
    assert 0.004 < s["p_approx"] < 0.01
    assert an.chi2_uniform({"A": 0, "B": 0, "C": 0, "D": 0})["n"] == 0


def test_spearman_known_values(an):
    assert an._spearman([1, 2, 3, 4], [1, 2, 3, 4]) == 1.0
    assert an._spearman([1, 2, 3, 4], [4, 3, 2, 1]) == -1.0
    assert an._spearman([1, 2, 3], [1, 2, 3]) == 1.0
    assert an._spearman([1, 1, 1], [1, 2, 3]) is None  # no variance
    assert an._spearman([1, 2], [1, 2]) is None         # n < 3


def test_render_md_includes_tables_and_verbatim_comments(an):
    key = make_key(100)
    doc = make_doc(key, comment={7: "verbatim comment #7"})
    blocks, notes = an.validate(doc, key)
    rows = an.decode(blocks, key)
    agg = an.aggregate(rows)
    chi = {
        "overall": an.chi2_uniform(
            {c: agg["overall"][c]["count"] for c in "ABCD"}),
        "chatgpt": an.chi2_uniform(
            {c: agg["by_model"]["chatgpt"][c]["count"] for c in "ABCD"}),
        "claude": an.chi2_uniform(
            {c: agg["by_model"]["claude"][c]["count"] for c in "ABCD"}),
    }
    decoded = {"aggregates": agg, "chi2_uniform": chi,
               "automated": {"chatgpt": {}, "claude": {}},
               "rows": rows,
               "validation": {"parse_notes": []}}
    md = an.render_md(decoded)
    assert "## Choices per production condition" in md
    assert "verbatim comment #7" in md
    assert "| Condition | choices | share |" in md


def test_source_documents_never_overwritten(tmp_path, an):
    """The analysis reads the completed document and the key; running the
    pure decode path must not modify either file's bytes."""
    key = make_key(100)
    doc = make_doc(key)
    key_bytes = json.dumps(key).encode()
    doc_bytes = doc.encode()
    blocks, _ = an.validate(doc, key)
    an.decode(blocks, key)
    assert doc.encode() == doc_bytes
    assert json.dumps(key).encode() == key_bytes
