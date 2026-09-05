#!/usr/bin/env python3
"""Prepare the EXP-003 sentence-level forced-choice human preference test.

Replaces the holistic complete-text review (`comparison/human_review.md`,
DESIGN §11 / Task 012) as the PRIMARY human-evaluation method for EXP-003
(SODA Task 014): the Project Owner found comparing four complete long
translations too cognitively demanding, so the holistic format is superseded
for primary use and kept only as a historical/provisional design. No holistic
human result was obtained and none is recorded or inferred here.

Question format (one question = one Polish source sentence):
  1. select a Polish source sentence from the original story;
  2. retrieve the corresponding sentence from each of the four EXP-003
     conditions (A/B/C/D) of the same model;
  3. randomize the four Interslavic versions deterministically (fixed seed);
  4. present them as Version 1 .. Version 4;
  5. the Project Owner ticks the version that sounds most natural as
     Medžuslovjansky (best-choice only; no full ranking, no worst choice).
The participant-facing document contains NO model names, NO A/B/C/D
condition labels, and NO automatic metrics. The private answer key records
the source sentence identity, section, run ids, seed, and per-question
display order so later analysis can map preferences back to conditions.

Deterministic pipeline (all reproducible, no LLM calls, no metric computed):
  1. line-based segmentation into sentence units and heading markers
     (identical punctuation rules on the Polish source and every output);
  2. monotonic dynamic-programming sentence alignment (token-length based,
     1:1 / 1:2 / 2:1 + skips) between the Polish source and each condition
     output;
  3. quadruple pool: source sentences with a 1:1 anchor in all four
     conditions of a model that (a) pass an all-pairs cross-run token
     overlap >= OVERLAP_MIN (the four versions really render the same
     source sentence), (b) have at least MIN_WORDS words, and (c) are not
     token-identical across all four conditions;
  4. stratified deterministic sampling per model (story section x dialogue),
     PER_MODEL questions per model (~100 total), covering different parts
     of the story and mixing dialogue/narration;
  5. deterministic per-question version-order randomization (fixed seed;
     alphabetical display order is rejected for a question).

Writes:
  experiments/exp003-scaffold/comparison/sentence_review.md       (participant)
  experiments/exp003-scaffold/comparison/sentence_review_key.json (private)

The script refuses to overwrite an existing questionnaire unless --force:
a partially answered questionnaire must never be silently clobbered.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXP = ROOT / "experiments" / "exp003-scaffold"
SOURCE_FILE = EXP / "input" / "source.txt"
OUTPUTS_DIR = EXP / "outputs"
COMPARISON_DIR = EXP / "comparison"

CONDITIONS = ("A", "B", "C", "D")
DEFAULT_SEED = 20260905          # Task 014 preparation date
PER_MODEL = 50                   # ~100 questions total across 2 models
MIN_WORDS = 4                    # drop fragments / interjections
OVERLAP_MIN = 0.30               # all-pairs cross-run token overlap floor
ALIGN_GAP = 0.30                 # DP skip penalty

_DOC_NAME = "sentence_review.md"
_KEY_NAME = "sentence_review_key.json"

SENT_TERM = re.compile(r"[.!?…][”»„ʼ'’]?$")
SENT_SPLIT = re.compile(r"(?<=[.!?…])\s+")
WORD_RE = re.compile(r"[^\W\d_]+(?:['’\-][^\W\d_]+)*", re.UNICODE)
DIALOGUE_START = ("–", "—", "„", "“", "«", '"')

# --------------------------------------------------------------------------
# Segmentation
# --------------------------------------------------------------------------


def words(text: str) -> list[str]:
    """Word tokens (no punctuation-only tokens, no standalone dashes)."""
    return WORD_RE.findall(text)


def n_words(text: str) -> int:
    return len(words(text))


def norm_tokens(text: str) -> tuple[str, ...]:
    return tuple(w.lower() for w in words(text))


def segment_lines(text: str) -> list[tuple[str, str]]:
    """Line-based segmentation into ('sent', ...) and ('marker', ...) units.

    A line ending with sentence-final punctuation is split into sentence
    units at punctuation boundaries; an unpunctuated line (title, section
    heading, end marker such as KONEC, or a heading glued to the previous
    paragraph by a bare newline) becomes a marker and never enters the
    content pool.
    """
    out: list[tuple[str, str]] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if SENT_TERM.search(line):
            for part in SENT_SPLIT.split(line):
                part = part.strip()
                if part:
                    out.append(("sent", part))
        else:
            out.append(("marker", line))
    return out


def content_sentences(segments: list[tuple[str, str]], min_words: int = MIN_WORDS):
    """List of (text, section) for sentence units with >= min_words words.

    section is the text of the nearest preceding marker (heading/title).
    """
    section = "(title)"
    out: list[tuple[str, str]] = []
    for kind, text in segments:
        if kind == "marker":
            section = text
        elif n_words(text) >= min_words:
            out.append((text, section))
    return out


# --------------------------------------------------------------------------
# Alignment
# --------------------------------------------------------------------------


def _len_cost(a: str, b: str) -> float:
    la, lb = n_words(a), n_words(b)
    if la == 0 or lb == 0:
        return 5.0
    return 1.0 - min(la, lb) / max(la, lb)


def align_monotonic(A: list[str], B: list[str],
                    gap: float = ALIGN_GAP) -> list[tuple[int, int]]:
    """Monotonic length-based alignment of two sentence lists.

    Transitions: 1:1, 1:2, 2:1 (merged renderings) and 1:0 / 0:1 skips.
    Returns only the 1:1 anchor pairs (i, j) used for the quadruple pool.
    """
    n, m = len(A), len(B)
    INF = 1e9
    dp = [[INF] * (m + 1) for _ in range(n + 1)]
    back = [[None] * (m + 1) for _ in range(n + 1)]
    dp[0][0] = 0.0
    for i in range(n + 1):
        for j in range(m + 1):
            cur = dp[i][j]
            if cur == INF:
                continue
            if i < n and j < m:
                c = cur + _len_cost(A[i], B[j])
                if c < dp[i + 1][j + 1]:
                    dp[i + 1][j + 1] = c
                    back[i + 1][j + 1] = (i, j, "11")
            if i < n and j + 1 < m:
                c = cur + 0.5 * (_len_cost(A[i], B[j]) +
                                 _len_cost(A[i], B[j + 1])) + 0.05
                if c < dp[i + 1][j + 2]:
                    dp[i + 1][j + 2] = c
                    back[i + 1][j + 2] = (i, j, "12")
            if i + 1 < n and j < m:
                c = cur + 0.5 * (_len_cost(A[i], B[j]) +
                                 _len_cost(A[i + 1], B[j])) + 0.05
                if c < dp[i + 2][j + 1]:
                    dp[i + 2][j + 1] = c
                    back[i + 2][j + 1] = (i, j, "21")
            if i < n:
                c = cur + gap
                if c < dp[i + 1][j]:
                    dp[i + 1][j] = c
                    back[i + 1][j] = (i, j, "sA")
            if j < m:
                c = cur + gap
                if c < dp[i][j + 1]:
                    dp[i][j + 1] = c
                    back[i][j + 1] = (i, j, "sB")
    anchors: list[tuple[int, int]] = []
    i, j = n, m
    while i > 0 or j > 0:
        pi, pj, kind = back[i][j]
        if kind == "11":
            anchors.append((i - 1, j - 1))
        elif kind == "12":
            pass  # merged ISV rendering of one source sentence: no 1:1 anchor
        elif kind == "21":
            pass  # one ISV rendering of two source sentences: no 1:1 anchor
        i, j = pi, pj
    anchors.reverse()
    return anchors


def token_overlap(a: str, b: str) -> float:
    ta, tb = set(norm_tokens(a)), set(norm_tokens(b))
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / min(len(ta), len(tb))


# --------------------------------------------------------------------------
# Pool construction
# --------------------------------------------------------------------------


def discover_runs(outputs_dir: Path) -> dict[str, dict[str, Path]]:
    """models -> condition -> run directory, for complete runs only.

    Only runs with meta.json status == collected_external_output are used
    (D-035); a model participates only if all four conditions are complete.
    """
    found: dict[str, dict[str, Path]] = {}
    for run_dir in sorted(p for p in outputs_dir.iterdir() if p.is_dir()):
        meta_path = run_dir / "meta.json"
        out_path = run_dir / "output.txt"
        if not (meta_path.exists() and out_path.exists()):
            continue
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        if meta.get("status") != "collected_external_output":
            continue
        model = meta.get("model")
        cond = meta.get("condition")
        if model and cond and cond in CONDITIONS:
            found.setdefault(model, {})[cond] = run_dir
    return {m: c for m, c in found.items() if set(c) == set(CONDITIONS)}


def build_pool(source_sents: list[str],
               runs: dict[str, list[str]]) -> list[dict]:
    """Deterministic quadruple pool for one model.

    Each candidate: a source sentence (by index into source_sents) with a
    1:1 anchor in every condition that renders the same content (all-pairs
    cross-run token overlap >= OVERLAP_MIN) and is not identical across all
    four conditions.
    """
    align = {c: dict(align_monotonic(source_sents, runs[c])) for c in CONDITIONS}
    anchors = {c: {i: j for i, j in align[c].items()} for c in CONDITIONS}
    pool: list[dict] = []
    for i in sorted(set.intersection(*[set(anchors[c]) for c in CONDITIONS])):
        texts = {c: runs[c][anchors[c][i]] for c in CONDITIONS}
        if all(token_overlap(texts["A"], texts[c]) < OVERLAP_MIN
               for c in ("B", "C", "D")):
            continue  # conservative: must clear the floor against A
        ov_min = min(token_overlap(texts["A"], texts[c]) for c in ("B", "C", "D"))
        if ov_min < OVERLAP_MIN:
            continue
        if len({norm_tokens(t) for t in texts.values()}) == 1:
            continue  # all four versions identical -> no signal
        pool.append({"source_index": i,
                     "texts": texts,
                     "overlap_min": ov_min})
    return pool


# --------------------------------------------------------------------------
# Deterministic stratified sampling
# --------------------------------------------------------------------------


def _allocate(counts: list[int], total: int) -> list[int]:
    """Largest-remainder proportional allocation, deterministic (ties by
    group order), never exceeding group capacities."""
    out = [0] * len(counts)
    if total <= 0 or sum(counts) == 0:
        return out
    total = min(total, sum(counts))
    remaining = total
    for _ in range(total):
        # pick the group with the largest current deficit vs its fair share
        best, best_score = -1, -1.0
        for k, cap in enumerate(counts):
            if out[k] >= cap:
                continue
            fair = cap * total / sum(counts)
            deficit = fair - out[k]
            # tiny deterministic tie-breaker on group order
            score = (deficit, -k)
            if best == -1 or score > best_score:
                best, best_score = k, score
        out[best] += 1
        remaining -= 1
    return out


def _spread(items: list, take: int) -> list:
    """Evenly spaced deterministic selection from an ordered list."""
    n = len(items)
    if take >= n:
        return list(items)
    if take <= 1:
        return [items[0]] if items else []
    idxs = sorted({round(t * (n - 1) / (take - 1)) for t in range(take)})
    return [items[i] for i in idxs if i < n]


def sample_stratified(pool: list[dict], source_sents: list[str],
                      sections: list[str], per_model: int) -> list[dict]:
    """Sample `per_model` questions from the pool, stratified by
    (story section x dialogue) with even spacing inside each stratum.

    Within a stratum, quadruples whose four versions are all pairwise
    distinct are preferred (only pairs are used if a stratum has fewer
    fully-distinct candidates than its allocation), so the questionnaire
    maximises genuine four-way variation while keeping story coverage.
    """
    def key_of(cand: dict) -> tuple[str, bool]:
        i = cand["source_index"]
        return (source_sents[i][1],  # section label
                source_sents[i][0].lstrip().startswith(DIALOGUE_START))

    def all_distinct(cand: dict) -> bool:
        return len({norm_tokens(t) for t in cand["texts"].values()}) == 4

    groups: dict[tuple[str, bool], list[dict]] = {}
    for cand in pool:
        groups.setdefault(key_of(cand), []).append(cand)
    # deterministic group order: section appearance order, then narration
    # before dialogue
    def section_rank(s: str) -> int:
        try:
            return sections.index(s)
        except ValueError:
            return len(sections)

    ordered_keys = sorted(groups,
                          key=lambda k: (section_rank(k[0]), 1 if k[1] else 0))
    counts = [len(groups[k]) for k in ordered_keys]
    alloc = _allocate(counts, per_model)
    selected: list[dict] = []
    for k, take in zip(ordered_keys, alloc):
        group = sorted(groups[k], key=lambda c: c["source_index"])
        distinct = [c for c in group if all_distinct(c)]
        rest = [c for c in group if not all_distinct(c)]
        take_d = min(take, len(distinct))
        selected.extend(_spread(distinct, take_d))
        if take_d < take:
            selected.extend(_spread(rest, take - take_d))
    selected.sort(key=lambda c: c["source_index"])
    return selected


def _rel_to_root(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


# --------------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------------

_INSTRUCTIONS = """\
# EXP-003 — sentence preference test

Thank you for evaluating these translations. This test takes about 10 to 15
minutes. There are {n_questions} questions.

## What you will see

Each question shows one Polish sentence from the story, followed by four
candidate Medžuslovjansky versions of that same sentence, labelled
**Version 1** to **Version 4**. The four versions were produced in different
ways; your task is only to judge how they read as Medžuslovjansky.

## What to choose

For each question, choose the version that, **as a whole, sounds the most
natural and plausible as Medžuslovjansky** to you.

- Do NOT try to verify individual words against a dictionary, and do not
  try to decide whether a single word is "officially correct".
- You may encounter forms you do not recognise — that is expected. Judge
  the overall sentence impression, not individual words.
- This is not an expert linguistic classification task. A holistic reader's
  impression is exactly what is wanted.

## How to answer

- Tick exactly **one** checkbox (Version 1, 2, 3 or 4) per question.
- The comment line is optional.
- There is no time limit and there are no right or wrong answers.
- When you have answered every question, save this file. The mapping from
  the version labels back to the four production settings is kept
  separately and is only looked at after the answers are recorded.
"""


def _render_question(q: dict, number: int) -> list[str]:
    lines = [f"### Question {number}", "",
             f"**Polish source sentence:** {q['source_text']}", ""]
    for k, cond in enumerate(q["display_order"], start=1):
        lines.append(f"- [ ] **Version {k}** — {q['texts'][cond]}")
    lines += ["", "Comment (optional):", "", "---", ""]
    return lines


def render_document(questions: list[dict]) -> str:
    n = len(questions)
    head = _INSTRUCTIONS.format(n_questions=n)
    body: list[str] = []
    for num, q in enumerate(questions, start=1):
        body.extend(_render_question(q, num))
    return head + "\n" + "\n".join(body)


# --------------------------------------------------------------------------
# Question assembly
# --------------------------------------------------------------------------


def assemble_questions(model_pools: dict[str, list[dict]],
                       source_sents: list[str], sections: list[str],
                       seed: int, per_model: int) -> list[dict]:
    """Sample per model, then build the final question list with a
    deterministic overall order and per-question randomized display order."""
    rng = random.Random(seed)
    questions: list[dict] = []
    for model in sorted(model_pools):
        sampled = sample_stratified(model_pools[model], source_sents,
                                    sections, per_model)
        for cand in sampled:
            i = cand["source_index"]
            src_text, section = source_sents[i]
            questions.append({
                "model": model,
                "section": section,
                "source_sentence_index": i,
                "source_text": src_text,
                "dialogue": src_text.lstrip().startswith(DIALOGUE_START),
                "texts": cand["texts"],
                "overlap_min": round(cand["overlap_min"], 4),
            })
    rng.shuffle(questions)          # interleave models, deterministic
    for q in questions:
        order = list(CONDITIONS)
        for _ in range(100):        # never show alphabetical condition order
            rng.shuffle(order)
            if order != list(CONDITIONS):
                break
        q["display_order"] = order
    return questions


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------


def build(source_path: Path, outputs_dir: Path, out_dir: Path,
          seed: int = DEFAULT_SEED, per_model: int = PER_MODEL,
          force: bool = False) -> dict:
    """Run the full pipeline; returns a status summary dict."""
    doc_path = out_dir / _DOC_NAME
    key_path = out_dir / _KEY_NAME
    if not force and (doc_path.exists() or key_path.exists()):
        raise FileExistsError(
            f"{doc_path.name}/{key_path.name} already exist; refusing to "
            "overwrite an (possibly answered) questionnaire — rerun with "
            "--force only to regenerate from scratch")
    out_dir.mkdir(parents=True, exist_ok=True)

    source_text = source_path.read_text(encoding="utf-8")
    source_sha = hashlib.sha256(source_text.encode("utf-8")).hexdigest()

    src_sents = content_sentences(segment_lines(source_text), MIN_WORDS)
    sections: list[str] = []
    for _t, sec in src_sents:
        if sec not in sections:
            sections.append(sec)

    runs = discover_runs(outputs_dir)
    if not runs:
        raise SystemExit("no complete-run models found under "
                         f"{outputs_dir} (need 4 conditions x >=1 model, "
                         "status collected_external_output)")

    model_pools: dict[str, list[dict]] = {}
    run_ids: dict[str, dict[str, str]] = {}
    doc_texts: dict[str, dict[str, str]] = {}
    for model in sorted(runs):
        run_sents = {c: [t for t, _s in content_sentences(
            segment_lines((runs[model][c] / "output.txt")
                          .read_text(encoding="utf-8")), MIN_WORDS)]
            for c in CONDITIONS}
        pool = build_pool([t for t, _s in src_sents], run_sents)
        if not pool:
            print(f"[skip] model {model}: no aligned quadruples", file=sys.stderr)
            continue
        model_pools[model] = pool
        run_ids[model] = {c: runs[model][c].name for c in CONDITIONS}
        doc_texts[model] = {c: (runs[model][c] / "output.txt")
                            .read_text(encoding="utf-8") for c in CONDITIONS}

    if not model_pools:
        raise SystemExit("no model produced any aligned quadruple")

    questions = assemble_questions(model_pools, src_sents, sections,
                                   seed, per_model)
    # stable numbering by final order
    for num, q in enumerate(questions, start=1):
        q["question"] = num

    doc = render_document(questions)
    doc += "\n\nYou are done. Save this file.\n"
    content_sha = hashlib.sha256(doc.encode("utf-8")).hexdigest()
    doc += f"\n(internal: document sha-256 {content_sha})\n"
    doc_sha = hashlib.sha256(doc.encode("utf-8")).hexdigest()

    key = {
        "protocol": "EXP-003 sentence-level forced-choice preference test",
        "prepared": "2026-09-05",
        "supersedes": "comparison/human_review.md (holistic complete-text "
                      "review; superseded 2026-09-05 — format found too "
                      "cognitively demanding; kept as historical artifact)",
        "target": f"{per_model} per model (~100 total)",
        "seed": seed,
        "source": {"file": _rel_to_root(source_path),
                   "sha256": source_sha},
        "runs": run_ids,
        "pool_sizes": {m: len(model_pools[m]) for m in sorted(model_pools)},
        "sample_sizes": {m: sum(1 for q in questions if q["model"] == m)
                         for m in sorted(model_pools)},
        "filters": {"min_words": MIN_WORDS,
                    "overlap_min": OVERLAP_MIN,
                    "align_gap": ALIGN_GAP,
                    "identical_across_all_conditions_excluded": True},
        "sampling": "stratified systematic: (story section x dialogue) "
                    "largest-remainder allocation, even spacing by source "
                    "position; question order shuffled with the recorded "
                    "seed; per-question display order = seeded shuffle of "
                    "A/B/C/D (alphabetical order rejected)",
        "document": {"file": _DOC_NAME,
                     "sha256": doc_sha,
                     "content_sha256": content_sha},
        "questions": questions,
    }
    doc_path.write_text(doc, encoding="utf-8")
    key_path.write_text(json.dumps(key, ensure_ascii=False, indent=2),
                        encoding="utf-8")
    return {
        "models": sorted(model_pools),
        "pool_sizes": key["pool_sizes"],
        "sample_sizes": key["sample_sizes"],
        "n_questions": len(questions),
        "document": str(doc_path),
        "document_sha256": doc_sha,
        "content_sha256": content_sha,
        "key": str(key_path),
        "sections_in_sample": sorted({q["section"] for q in questions}),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Prepare the EXP-003 sentence-level forced-choice "
                    "preference test (participant doc + private key).")
    ap.add_argument("--seed", type=int, default=DEFAULT_SEED,
                    help="randomization seed (default %(default)s)")
    ap.add_argument("--per-model", type=int, default=PER_MODEL,
                    help="questions per model (default %(default)s)")
    ap.add_argument("--force", action="store_true",
                    help="overwrite an existing questionnaire")
    args = ap.parse_args(argv)

    try:
        summary = build(SOURCE_FILE, OUTPUTS_DIR, COMPARISON_DIR,
                        seed=args.seed, per_model=args.per_model,
                        force=args.force)
    except FileExistsError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(f"models: {', '.join(summary['models'])}")
    for m in summary["models"]:
        print(f"  pool {m}: {summary['pool_sizes'][m]} aligned quadruples; "
              f"sampled {summary['sample_sizes'][m]}")
    print(f"questions: {summary['n_questions']} "
          f"(sections covered: {len(summary['sections_in_sample'])})")
    print(f"participant document: {summary['document']}")
    print(f"document sha-256:     {summary['document_sha256']} "
          f"(content: {summary['content_sha256']})")
    print(f"private answer key:   {summary['key']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
