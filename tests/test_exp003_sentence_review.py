"""EXP-003 — sentence-level forced-choice review preparation tests (Task 014).

Covers the deterministic pipeline in scripts/prepare_exp003_sentence_review.py:
- deterministic / reproducible build (identical document + answer key);
- deterministic per-question randomization of the display order;
- source/output sentence alignment (each question's four versions render the
  same source sentence);
- exclusion of unusable sentences (all-four-identical, misaligned content);
- absence of model/condition/run labels from the participant document;
- answer-key correctness (permutation mapping, verbatim provenance,
  numbering, uniqueness);
- refusal to overwrite an (possibly answered) questionnaire.
"""
import hashlib
import importlib.util
import json
import re
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"

NUM = ["one", "two", "three", "four", "five", "six", "seven", "eight"]
MARKERS = ["alpha", "beta", "gamma", "delta",
           "epsilon", "zeta", "eta", "theta"]
# per-sentence distinctive vocabulary (no shared content words across
# sentences, so the cross-run overlap floor reliably discriminates true
# alignments from shifted ones)
WORDS = [
    ["rover", "quietly", "measured", "dusty", "craters"],            # len 6
    ["engineers", "assembled", "bright", "mechanical", "wings",
     "overnight", "hangar", "humming"],                              # len 9
    ["whispered", "cautious", "instructions", "through", "narrow",
     "stone", "corridors", "hidden", "tunnels", "empty", "chambers"],  # len 12
    ["mountains", "rose", "above", "sleeping", "town", "silently"],   # len 7
    ["dreamed", "distant", "summer", "journeys", "golden", "meadows",
     "fragrant", "herbs", "warm"],                                    # len 10
    ["candles", "flickered", "beside", "open", "window", "nightfall",
     "gentle"],                                                       # len 8
    ["travellers", "rested", "near", "bridge", "shared", "stories",
     "campfire", "beneath", "stars", "murmured"],                     # len 11
    ["winter", "cold", "winds", "returned"],                          # len 5
]
DIALOGUE_IDX = (2, 4)
# sentence 3 (index 2) is corrupted in condition B with unrelated content
CORRUPT_INDEX = 2
CORRUPT_TEXT = ("zulu unconnected foreign noise interrupts nothing "
                "anywhere ever regardless somehow outside truly.")
# sentence 8 (index 7) is rendered identically by all four conditions
IDENTICAL_INDEX = 7


def _source_sentence(idx: int) -> str:
    prefix = "– " if idx in DIALOGUE_IDX else ""
    return prefix + " ".join([MARKERS[idx]] + WORDS[idx]) + "."


SOURCE_TEXT = "\n".join([
    "Pověst Test",
    "Prolog",
    "",
    _source_sentence(0),
    _source_sentence(1),
    _source_sentence(2),
    _source_sentence(3),
    "Akt Prvy: Some Heading",
    _source_sentence(4),
    _source_sentence(5),
    _source_sentence(6),
    _source_sentence(7),
]) + "\n"


@pytest.fixture(scope="module")
def prep_mod():
    spec = importlib.util.spec_from_file_location(
        "prepare_exp003_sentence_review",
        SCRIPTS / "prepare_exp003_sentence_review.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _render(cond: str, idx: int) -> str:
    """Synthetic 'translation' of source sentence idx for one condition.

    Translations preserve the source content word-for-word (so the true
    alignment has maximal token overlap) and add a unique per-condition
    suffix token ("plus-b/c/d") so the four versions of one sentence stay
    pairwise distinct. Sentence 3 (index 2) is corrupted in condition B
    with unrelated, token-disjoint content; sentence 8 (index 7) is
    rendered identically by all four conditions.
    """
    base = " ".join([MARKERS[idx]] + WORDS[idx])
    prefix = "– " if idx in DIALOGUE_IDX else ""
    if idx == CORRUPT_INDEX and cond == "B":
        return CORRUPT_TEXT                      # deliberately misaligned
    if idx == IDENTICAL_INDEX:
        return f"{prefix}{base}."                # identical for all conditions
    suffix = {"A": "", "B": " plus-b", "C": " plus-c", "D": " plus-d"}[cond]
    return f"{prefix}{base}{suffix}."


def _write_scaffold(tmp_path: Path) -> tuple[Path, Path]:
    """Write synthetic source + complete-run outputs; return (source, outputs)."""
    src = tmp_path / "source.txt"
    src.write_text(SOURCE_TEXT, encoding="utf-8")
    outs = tmp_path / "outputs"
    outs.mkdir(exist_ok=True)
    for model in ("mod1", "mod2"):
        for cond in ("A", "B", "C", "D"):
            d = outs / f"{model}_{cond}"
            d.mkdir(exist_ok=True)
            (d / "meta.json").write_text(
                json.dumps({"model": model, "condition": cond,
                            "status": "collected_external_output"}),
                encoding="utf-8")
            text = "\n\n".join(_render(cond, i) for i in range(8))
            (d / "output.txt").write_text(text + "\n", encoding="utf-8")
    return src, outs


def _build(tmp_path, prep_mod, *, seed=12345, per_model=6,
           out_name="cmp", force=False):
    src, outs = _write_scaffold(tmp_path)
    out_dir = tmp_path / out_name
    summary = prep_mod.build(src, outs, out_dir, seed=seed,
                             per_model=per_model, force=force)
    doc = (out_dir / prep_mod._DOC_NAME).read_text(encoding="utf-8")
    key = json.loads((out_dir / prep_mod._KEY_NAME)
                     .read_text(encoding="utf-8"))
    return summary, doc, key, src, outs, out_dir


def parse_doc(doc: str) -> dict[int, dict]:
    """Question number -> {'source': str, 'versions': {1..4: text}}."""
    parsed: dict[int, dict] = {}
    cur = None
    for line in doc.splitlines():
        mq = re.match(r"^### Question (\d+)$", line.strip())
        if mq:
            cur = int(mq.group(1))
            parsed[cur] = {"source": None, "versions": {}}
            continue
        if cur is None:
            continue
        ms = re.match(r"^\*\*Polish source sentence:\*\* (.*)$", line.strip())
        if ms:
            parsed[cur]["source"] = ms.group(1)
        mv = re.match(r"^- \[ \] \*\*Version ([1-4])\*\* — (.*)$", line.strip())
        if mv:
            parsed[cur]["versions"][int(mv.group(1))] = mv.group(2)
    return parsed


def content_sha_from_marker(doc: str) -> str:
    line = [l for l in doc.splitlines() if "document sha-256" in l][-1]
    return line.split("document sha-256 ")[1].rstrip(")")


def test_build_is_deterministic_and_reproducible(tmp_path, prep_mod):
    """Same inputs + same seed -> byte-identical document and key; the key's
    recorded hashes match the written file (file sha + content sha printed
    inside the document)."""
    _, doc1, key1, _, _, _ = _build(tmp_path, prep_mod, out_name="cmp1")
    _, doc2, key2, _, _, _ = _build(tmp_path, prep_mod, out_name="cmp2")
    assert doc1 == doc2
    assert key1 == key2
    assert hashlib.sha256(doc1.encode("utf-8")).hexdigest() == \
        key1["document"]["sha256"]
    assert key1["document"]["content_sha256"] == content_sha_from_marker(doc1)
    assert hashlib.sha256(
        doc1.split("\n(internal: document sha-256 ")[0].encode("utf-8")
    ).hexdigest() == key1["document"]["content_sha256"]


def test_display_order_is_deterministic_and_never_alphabetical(
        tmp_path, prep_mod):
    """Per-question Version labels are seeded permutations of A/B/C/D,
    never alphabetical, and independent across questions; a different seed
    changes the orders."""
    _, doc1, key1, _, _, _ = _build(tmp_path, prep_mod, seed=12345,
                                    out_name="s12345")
    _, doc2, key2, _, _, _ = _build(tmp_path, prep_mod, seed=999,
                                    out_name="s999")
    assert doc1 != doc2
    orders1 = [tuple(q["display_order"]) for q in key1["questions"]]
    orders2 = [tuple(q["display_order"]) for q in key2["questions"]]
    assert len(set(orders1)) >= 2, "orders must be independent per question"
    for order in orders1 + orders2:
        assert sorted(order) == ["A", "B", "C", "D"]
        assert order != ("A", "B", "C", "D")
    assert orders1 != orders2


def test_pool_excludes_misaligned_and_all_identical_sentences(
        tmp_path, prep_mod):
    """Sentences corrupted in one condition (misaligned content) or rendered
    identically by all four conditions never become questions; with
    per_model == pool size every usable sentence is sampled."""
    _, doc, key, _, _, _ = _build(tmp_path, prep_mod)
    qs = key["questions"]
    assert len(qs) == 12                       # 2 models x 6 usable
    assert {m: sum(1 for q in qs if q["model"] == m)
            for m in ("mod1", "mod2")} == {"mod1": 6, "mod2": 6}
    assert all(q["source_sentence_index"] not in (CORRUPT_INDEX,
                                                  IDENTICAL_INDEX)
               for q in qs)
    assert "zulu" not in doc                    # corrupted text never shown
    assert "gamma" not in doc                   # corrupted sentence never shown
    assert "theta" not in doc                   # identical sentence never shown
    # all shown source sentences pass the word-count floor
    assert all(len(prep_mod.words(q["source_text"])) >= prep_mod.MIN_WORDS
               for q in qs)


def test_each_question_renders_the_same_source_sentence(tmp_path, prep_mod):
    """Alignment check: every displayed version contains the distinctive
    marker token of the question's source sentence (same content, 4 ways)."""
    src, _outs = _write_scaffold(tmp_path)
    src_sents = prep_mod.content_sentences(
        prep_mod.segment_lines(src.read_text(encoding="utf-8")),
        prep_mod.MIN_WORDS)
    markers = [prep_mod.words(t)[0] for t, _s in src_sents]
    _, _doc, key, _, _, _ = _build(tmp_path, prep_mod)
    assert len(markers) == 8
    for q in key["questions"]:
        marker = markers[q["source_sentence_index"]]
        assert marker in prep_mod.words(q["source_text"])
        for text in q["texts"].values():
            assert marker in prep_mod.words(text), \
                f"Q{q['question']}: version does not render the source sentence"


def test_participant_document_is_blinded(tmp_path, prep_mod):
    """No model names, run ids, condition labels, or metrics in the
    participant-facing document; only Version 1..4 answer controls."""
    _, doc, _key, _, _, _ = _build(tmp_path, prep_mod)
    low = doc.lower()
    for bad in ("mod1", "mod2", "run_", "condition", "scaffold", "coverage",
                "canonical", "metric", "%", "zulu", "gamma", "theta"):
        assert bad not in low, f"blinding leak: {bad!r}"
    assert "Version 5" not in doc
    for line in doc.splitlines():
        s = line.strip()
        if s.startswith("- [ ]"):
            assert re.match(r"^- \[ \] \*\*Version [1-4]\*\* — ", s), s
    parsed = parse_doc(doc)
    assert len(parsed) == 12
    for q in parsed.values():
        assert q["source"] is not None
        assert sorted(q["versions"]) == [1, 2, 3, 4]


def test_answer_key_matches_participant_document(tmp_path, prep_mod):
    """Key correctness: each question maps Version k -> condition via a
    permutation of A/B/C/D; the displayed texts equal the condition texts in
    that order and are verbatim in the corresponding run outputs."""
    _, doc, key, _, outs, _ = _build(tmp_path, prep_mod)
    parsed = parse_doc(doc)
    assert len(parsed) == len(key["questions"])
    seen: set[tuple[str, int]] = set()
    numbers = sorted(parsed)
    assert numbers == list(range(1, len(numbers) + 1))
    for q in key["questions"]:
        assert q["question"] in parsed
        assert sorted(q["display_order"]) == ["A", "B", "C", "D"]
        assert q["display_order"] != ["A", "B", "C", "D"]
        assert parsed[q["question"]]["source"] == q["source_text"]
        for k, cond in enumerate(q["display_order"], start=1):
            assert parsed[q["question"]]["versions"][k] == q["texts"][cond]
            run_id = key["runs"][q["model"]][cond]
            raw = (outs / run_id / "output.txt").read_text(encoding="utf-8")
            assert q["texts"][cond] in raw
            assert q["texts"][cond] in doc
        dupe = (q["model"], q["source_sentence_index"])
        assert dupe not in seen
        seen.add(dupe)


def test_questionnaire_not_overwritten_without_force(tmp_path, prep_mod):
    """A generated (possibly answered) questionnaire is never clobbered
    unless --force is passed."""
    _write_scaffold(tmp_path)
    out_dir = tmp_path / "cmp"
    prep_mod.build(tmp_path / "source.txt", tmp_path / "outputs", out_dir,
                   seed=12345, per_model=6, force=False)
    (out_dir / prep_mod._DOC_NAME).write_text(
        "- [x] Version 1  (already answered)", encoding="utf-8")
    with pytest.raises(FileExistsError):
        prep_mod.build(tmp_path / "source.txt", tmp_path / "outputs", out_dir,
                       seed=12345, per_model=6, force=False)
    # --force regenerates from scratch
    prep_mod.build(tmp_path / "source.txt", tmp_path / "outputs", out_dir,
                   seed=12345, per_model=6, force=True)
    assert "already answered" not in \
        (out_dir / prep_mod._DOC_NAME).read_text(encoding="utf-8")
