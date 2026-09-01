#!/usr/bin/env python3
"""EXP-003 — deterministic Interslavic lexical scaffold generator.

EXP-003 (SODA Task 010) tests whether supplying an LLM with a *generation-time*
lexical scaffold — derived from the Polish source with the project's
dictionary/resources — improves Interslavic lexical correctness. This script
builds that scaffold.

Guarantees (D-029, see experiments/exp003-scaffold/DESIGN.md §6):

- NO LLM call anywhere in the pipeline. The only LLM calls in the experiment
  are the externally executed translation conditions.
- Deterministic and reproducible: regenerating with the same inputs produces
  byte-identical artifacts (the ``generator.commit`` field is repo state and
  is the only documented nondeterministic-ish field).
- Every ISV candidate retains provenance (layer / source / kind / detail),
  and nothing is invented: a candidate is either a canonical ``basic.json``
  headword whose Polish translation gloss matches the source form/lemma, or
  an explicit entry in the per-story curation table.

Alignment pipeline (per sentence, deterministic order):

    1. multiword expressions    (curation/multiword.tsv, greedy, longest first)
    2. proper names             (curation/names.tsv; kept as name tokens —
                                 takes precedence over the dictionary, D-031)
    3. exact reverse-index hit  (Polish gloss -> ISV headword in basic.json)
    4. dictionary-verified lemma recovery (frozen suffix table, stem must
       re-look-up in the reverse index)
    5. curated residual         (curation/residual.tsv: explicit human-judged
       entries with recorded basis)
    6. unmapped                 (rendered as [?]; no invented candidate)

Limitation (documented, not hidden): there is no reliable Polish lemmatizer
in the project. Step 3 is a small audited rule, strictly filtered by the
reverse index; anything it cannot recover goes to the per-story curation table
(step 5) — the honest cost of aligning one story.

Outputs (experiments/exp003-scaffold/scaffolds/<story_id>/):
    scaffold.json          full machine-readable scaffold + provenance + stats
    scaffold_B.txt         rendered Condition-B block (one canonical candidate)
    scaffold_C.txt         rendered Condition-C block (all candidates)
    scaffold_D.txt         rendered Condition-D block (candidates + grammar)

Usage:
    python scripts/build_exp003_scaffold.py clean-source
    python scripts/build_exp003_scaffold.py build [--force] [--out DIR]
    python scripts/build_exp003_scaffold.py stats
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from isv_eval.normalize import normalize_word  # noqa: E402
from isv_eval.tokenizer import tokenize  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
EXP = ROOT / "experiments" / "exp003-scaffold"
INPUT_DIR = EXP / "input"
CURATION_DIR = EXP / "curation"
SCAFFOLD_DIR = EXP / "scaffolds"

BASIC_JSON = ROOT / "data" / "dictionary" / "basic.json"
DEFAULT_LEXICON = ROOT / "data" / "dictionary" / "lexicon.tsv"
DEFAULT_MANIFEST = ROOT / "data" / "dictionary" / "manifest.json"

STORY_ID = "op-pl"
EXPERIMENT_ID = "exp003"

# The EXP-001 source file this story is cleaned from (see clean-source).
EXP001_SOURCE = (ROOT / "experiments" / "exp001-baseline" / "input"
                 / "source.txt")
# The instruction line embedded in the EXP-001 source, removed by clean-source.
EXP001_INSTRUCTION = "Przetłumacz to opowiadanie na medżusłowiański:"

# ---------------------------------------------------------------------------
# Polish-side normalization
# ---------------------------------------------------------------------------

# Bound-form / annotation markers used by basic.json pl glosses, stripped
# before indexing (a lookup convenience, not a linguistic analyzer).
_PL_MARKER_RE = re.compile(r"^[-!*+()~]+")
_PL_PAREN_RE = re.compile(r"\s*\(.*$")


def norm_pl(word: str) -> str:
    """Normalized Polish lookup key: NFC + lowercase, markers stripped.

    Kept identical to the project's word normalization (NFC + lowercase) so
    reverse-index keys match evaluator tokens. Markers are the bound-form /
    annotation characters used in basic.json pl glosses.
    """
    s = _PL_MARKER_RE.sub("", (word or "").strip())
    s = _PL_PAREN_RE.sub("", s).strip()
    return normalize_word(s)


# ---------------------------------------------------------------------------
# Reverse index: Polish gloss -> ISV headword
# ---------------------------------------------------------------------------


class PolishReverseIndex:
    """Polish->ISV reverse index built from basic.json's ``pl`` column.

    Every key is a normalized Polish gloss; every value is the list of
    dictionary rows carrying that gloss (each row: isv headword, POS, type,
    row id, the original gloss string). Built deterministically from the
    dictionary snapshot. Never modifies the dictionary.
    """

    def __init__(self, by_key: dict[str, list[dict]], row_count: int,
                 gloss_keys: int, source: str, sha256: str,
                 headword_pos: dict[str, tuple[str, str]] | None = None):
        self._by_key = by_key
        self.row_count = row_count
        self.gloss_keys = gloss_keys
        self.source = source
        self.sha256 = sha256
        self.headword_pos = headword_pos or {}

    @classmethod
    def load(cls, path: Path) -> "PolishReverseIndex":
        raw = path.read_bytes()
        data = json.loads(raw)
        wordlist = data["wordList"]
        header = [str(h) for h in wordlist[0]]
        by_key: dict[str, list[dict]] = {}
        headword_pos: dict[str, tuple[str, str]] = {}
        row_count = 0
        for row in wordlist[1:]:
            if not row:
                continue
            rec = dict(zip(header, row))
            row_count += 1
            row_id = str(rec.get("id", ""))
            isv = str(rec.get("isv", ""))
            pos = str(rec.get("partOfSpeech", "") or "")
            typ = str(rec.get("type", "") or "")
            for hw in (part.strip() for part in isv.split(",")):
                hw_key, _ = _clean_headword(hw)
                if hw_key:
                    headword_pos.setdefault(normalize_word(hw_key), (pos, typ))
            for gloss in (rec.get("pl") or "").split(","):
                key = norm_pl(gloss)
                if not key:
                    continue
                by_key.setdefault(key, []).append({
                    "isv": isv, "pos": pos, "type": typ, "id": row_id,
                    "pl_gloss": gloss.strip(),
                })
        return cls(by_key, row_count, len(by_key), str(path),
                   hashlib.sha256(raw).hexdigest(),
                   headword_pos=headword_pos)

    def lookup(self, pl_form: str) -> list[dict]:
        return self._by_key.get(norm_pl(pl_form), [])

    def __contains__(self, pl_form: str) -> bool:
        return norm_pl(pl_form) in self._by_key

    def __len__(self) -> int:
        return self.gloss_keys


# ---------------------------------------------------------------------------
# Curation tables (per-story, explicit, provenance-bearing, local)
# ---------------------------------------------------------------------------

_EMPTY_MARKER = "NONE"  # residual.tsv marker: reviewed, no defensible candidate


def _parse_table(path: Path) -> list[tuple[str, str, str]]:
    """Parse a curation TSV (form<TAB>value<TAB>note); '#' comments ignored."""
    if not path.is_file():
        return []
    rows: list[tuple[str, str, str]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.rstrip("\n")
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        parts = line.split("\t")
        form = parts[0].strip()
        value = parts[1].strip() if len(parts) > 1 else ""
        note = parts[2].strip() if len(parts) > 2 else ""
        if form:
            rows.append((form, value, note))
    return rows


def load_curation(story_id: str = STORY_ID) -> dict:
    """Load the per-story curation tables into a deterministic structure."""
    base = CURATION_DIR / story_id
    multiword: dict[str, dict] = {}
    for expr, value, note in _parse_table(base / "multiword.tsv"):
        norm_expr = " ".join(norm_pl(t) for t in expr.split())
        multiword[norm_expr] = {
            "isv": [c.strip() for c in value.split(",") if c.strip()],
            "note": note,
        }
    names: dict[str, dict] = {}
    for form, _value, note in _parse_table(base / "names.tsv"):
        names[norm_pl(form)] = {"note": note or "proper name — keep as-is"}
    residual: dict[str, dict] = {}
    for form, value, basis in _parse_table(base / "residual.tsv"):
        if value == _EMPTY_MARKER:
            residual[norm_pl(form)] = {"isv": [], "basis": basis}
        else:
            residual[norm_pl(form)] = {
                "isv": [c.strip() for c in value.split(",") if c.strip()],
                "basis": basis,
            }
    return {
        "story_id": story_id,
        "dir": str(base),
        "multiword": multiword,
        "names": names,
        "residual": residual,
    }


# ---------------------------------------------------------------------------
# Lemma recovery (dictionary-verified only)
# ---------------------------------------------------------------------------

# Small frozen, audited table of common Polish inflectional endings, longest
# first. Applied ONLY when the exact form misses; the recovered stem must
# re-look-up in the reverse index or the attempt is discarded. This is a
# documented limitation (no reliable Polish lemmatizer), not a language
# analyzer: its yield on the EXP-003 story is ~5% of unaligned forms.
POLISH_SUFFIX_STRIPS = (
    "owie", "owego", "owej", "owych", "owymi",   # adjectives: -owy paradigm
    "ami", "emu", "ego", "ymi", "ych", "ym",     # noun/adjective plurals
    "ach", "om", "ej", "ów", "em", "ie", "ę",    # fem/dative/locative forms
    "ą", "li", "ły", "ła", "ł",                  # past-tense verb forms
    "y", "i", "o", "a", "e", "u",                # short word-final vowels
)


def lemma_recovery(form: str, idx: PolishReverseIndex):
    """Dictionary-verified lemma recovery.

    Returns (stem, hits) when a stripped stem re-looks-up in the reverse
    index; otherwise None. The suffix rule that fired is recorded by the
    caller via ``stem``. Deterministic: longest suffix first, first hit wins.
    """
    key = norm_pl(form)
    for suffix in POLISH_SUFFIX_STRIPS:
        if len(key) > len(suffix) + 2 and key.endswith(suffix):
            stem = key[:-len(suffix)]
            hits = idx.lookup(stem)
            if hits:
                return stem, hits
    return None


# ---------------------------------------------------------------------------
# Alternative-resource annotations (never create candidates)
# ---------------------------------------------------------------------------


def alternative_annotations(surface: str, provider) -> list[dict]:
    """Exact-surface attestation of a candidate in the audited alternative
    resources (isv.dic / interslavicfreq), plus orthographic-variant notes.

    This only annotates an existing candidate — it never creates one. When the
    alternative resources are unavailable, returns [].
    """
    if provider is None:
        return []
    key = normalize_word(surface)
    anns: list[dict] = []
    tags = provider.hunspell_forms.get(key)
    if tags is not None:
        anns.append({"kind": "alternative_attestation", "source": "isv.dic",
                     "detail": {"tags": tags}})
    cb = provider.freq_isv.get(key)
    if cb is not None:
        anns.append({"kind": "alternative_attestation",
                     "source": "interslavicfreq.small_isv", "detail": {"cB": cb}})
    cb = provider.freq_isvx.get(key)
    if cb is not None:
        anns.append({"kind": "alternative_attestation",
                     "source": "interslavicfreq.small_isvx", "detail": {"cB": cb}})
    return anns


# ---------------------------------------------------------------------------
# Grammar annotations for Condition D
# ---------------------------------------------------------------------------

_LEX_VERB_FEATS = ("VerbForm", "Tense", "Person", "Number", "Gender")


def build_lemma_forms(lexicon_path: Path) -> dict[str, list[tuple[str, dict]]]:
    """lemma -> [(surface, feats), ...] from lexicon.tsv (deterministic order).

    Used only for Condition-D example forms of verb candidates. A large
    generated artifact (35 MB); loaded once per build.
    """
    import csv
    out: dict[str, list[tuple[str, dict]]] = {}
    with open(lexicon_path, newline="", encoding="utf-8") as fh:
        for row in csv.reader(fh, delimiter="\t"):
            if len(row) < 5 or not row[0]:
                continue
            form, lemma, feats = row[0], row[1], row[4]
            if not lemma or " " in lemma or "," in lemma:
                continue
            feats_d = json.loads(feats) if feats else None
            out.setdefault(normalize_word(lemma), []).append((form, feats_d or {}))
    return out


def example_forms(lemma_forms: dict[str, list[tuple[str, dict]]],
                  lemma: str) -> list[str]:
    """Up to 3 deterministic example paradigm forms: infinitive, 1sg present,
    past m.sg (verbs only). Empty when the lemma has no lexicon forms."""
    forms = lemma_forms.get(normalize_word(lemma))
    if not forms:
        return []
    picked: list[str] = []
    for surf, feats in forms:
        if feats.get("VerbForm") == "Inf":
            picked.append(surf)
            break
    for surf, feats in forms:
        if (feats.get("VerbForm") == "Fin"
                and feats.get("Tense") == "Pres"
                and feats.get("Person") == "1"
                and feats.get("Number") == "Sing"):
            picked.append(surf)
            break
    for surf, feats in forms:
        if (feats.get("VerbForm") == "Part"
                and feats.get("Tense") == "Past"
                and feats.get("Gender") == "Masc"
                and feats.get("Number") == "Sing"):
            picked.append(surf)
            break
    return picked[:3]


def _sort_key(cand: dict) -> tuple:
    typ = cand["type"]
    typ_int = int(typ) if str(typ).isdigit() else 999
    alt = sum(1 for a in cand["annotations"]
              if a["kind"] == "alternative_attestation")
    return (typ_int, -alt, cand.get("_variant_index", 0), cand["surface"])


def _clean_headword(surface: str) -> tuple[str, str]:
    """Separate a trailing parenthetical headword note from the surface.

    basic.json stores 11 headwords with a parenthetical note (verb
    government or domain), e.g. 'pozirati (na)', 'vråta (sport)'. The note is
    provenance detail, not part of the surface the LLM should choose from.
    """
    m = re.search(r"\s*\(([^)]*)\)\s*$", surface)
    if not m:
        return surface, ""
    return surface[:m.start()].rstrip(), m.group(1)


def candidates_from_hits(hits: list[dict], kind: str, detail_note: str,
                         provider, lemma_forms: dict | None) -> list[dict]:
    """Canonical candidates from reverse-index hits, deduplicated and ordered.

    Order: dictionary type ascending, alternative attestation count
    descending, orthographic-variant order, headword lexicographic
    (deterministic; design §7). Comma-separated headwords in basic.json are
    variant spellings of one entry (e.g. 'někȯgda, někȯgdy'); the first is
    canonical, the rest are emitted as ``orthographic_variant`` candidates
    with the same row provenance.
    """
    seen: set[str] = set()
    cands: list[dict] = []
    for h in hits:
        parts = [p.strip() for p in h["isv"].split(",") if p.strip()]
        for variant_index, raw in enumerate(parts):
            surface, hw_note = _clean_headword(raw)
            if not surface or surface in seen:
                continue
            seen.add(surface)
            detail = detail_note.format(gloss=h["pl_gloss"], id=h["id"])
            if hw_note:
                detail = f"{detail} headword note: ({hw_note})"
            if variant_index > 0:
                detail = f"orthographic variant of '{parts[0]}'; " + detail
            cands.append({
                "surface": surface,
                "pos": h["pos"],
                "type": h["type"],
                "layer": ("canonical" if variant_index == 0
                          else "orthographic_variant"),
                "source": "basic.json",
                "kind": kind if variant_index == 0 else "orthographic_variant",
                "detail": detail,
                "annotations": alternative_annotations(surface, provider),
                "_variant_index": variant_index,
            })
    cands.sort(key=_sort_key)
    for cand in cands:
        cand.pop("_variant_index", None)
    if lemma_forms is not None:
        for cand in cands:
            _add_grammar(cand, lemma_forms)
    return cands


def _add_grammar(cand: dict, lemma_forms: dict,
                 headword_pos: dict[str, tuple[str, str]] | None = None) -> None:
    """Attach the Condition-D grammar annotation (POS + verb examples).

    POS comes from the candidate's own dictionary row when available; curated
    candidates fall back to a headword->POS lookup in basic.json (design
    §8.3: dictionary POS only where resources generate it reliably). Multiword
    composed candidates (e.g. 'idti o') that are not dictionary headwords
    receive no annotation.
    """
    pos = cand.get("pos") or ""
    if not pos and headword_pos:
        hit = headword_pos.get(normalize_word(cand["surface"]))
        if hit:
            pos = hit[0]
    if pos.startswith("v"):
        examples = example_forms(lemma_forms, cand["surface"])
        cand["annotations"].append({
            "kind": "grammar", "pos": pos, "examples": examples,
        })
    elif pos:
        cand["annotations"].append({"kind": "grammar", "pos": pos,
                                    "examples": []})


def curated_candidates(isv_list: list[str], source: str, basis: str,
                       provider, lemma_forms: dict | None,
                       headword_pos: dict[str, tuple[str, str]] | None = None
                       ) -> list[dict]:
    cands = []
    for surface in isv_list:
        surface, hw_note = _clean_headword(surface)
        detail = basis
        if hw_note:
            detail = f"{detail} headword note: ({hw_note})"
        cands.append({
            "surface": surface,
            "pos": "",
            "type": "",
            "layer": "curated",
            "source": source,
            "kind": "curated",
            "detail": detail,
            "annotations": alternative_annotations(surface, provider),
        })
    if lemma_forms is not None:
        for cand in cands:
            _add_grammar(cand, lemma_forms, headword_pos)
    return cands


# ---------------------------------------------------------------------------
# Alignment
# ---------------------------------------------------------------------------


def _token_record(surface: str, kind: str, candidates: list[dict],
                  note: str | None = None) -> dict:
    return {
        "pl_surface": surface,
        "pl_normalized": norm_pl(surface),
        "kind": kind,
        "isv_candidates": candidates,
        "note": note,
        "mapped": kind not in ("name", "unmapped"),
    }


def align_story(story_text: str, idx: PolishReverseIndex, curation: dict,
                provider=None, lemma_forms: dict | None = None) -> dict:
    """Align every Polish lexical token to ISV candidates. Deterministic."""
    tokens = [t for t in tokenize(story_text) if t.is_lexical]
    multiword = curation["multiword"]
    names = curation["names"]
    residual = curation["residual"]
    # NOTE: the names table takes precedence over the dictionary (design §8).
    # One op-pl token ('Międzyrzecze', the town name) coincides with a real
    # basic.json pl gloss ('międzyrzecze' → 'međurěčje'); the per-story names
    # table is the explicit human-reviewed record that the town name is a
    # proper name, so it is checked before the exact dictionary lookup
    # (D-031, Task 010).

    sentences: dict[int, list] = {}
    for tok in tokens:
        sentences.setdefault(tok.sentence_id, []).append(tok)

    mw_exprs = sorted(multiword.keys(), key=lambda e: (-len(e.split()), e))
    stats = {
        "exact": 0, "recovery": 0, "name": 0, "multiword": 0,
        "curated": 0, "unmapped": 0,
    }
    unique = {k: set() for k in stats}

    sentence_payloads: list[dict] = []
    for sentence_id in sorted(sentences):
        toks = sentences[sentence_id]
        records: list[dict] = []
        i = 0
        while i < len(toks):
            tok = toks[i]
            # 1. multiword (greedy, longest first)
            matched = False
            for expr in mw_exprs:
                expr_tokens = expr.split()
                if i + len(expr_tokens) > len(toks):
                    continue
                window = [t.normalized for t in toks[i:i + len(expr_tokens)]]
                if window == expr_tokens:
                    entry = multiword[expr]
                    surface = " ".join(t.surface for t in toks[i:i + len(expr_tokens)])
                    rec = _token_record(
                        surface, "multiword",
                        curated_candidates(entry["isv"], "curation/multiword.tsv",
                                           entry["note"], provider, lemma_forms,
                                           idx.headword_pos),
                        entry["note"])
                    records.append(rec)
                    stats["multiword"] += len(expr_tokens)
                    unique["multiword"].add(expr)
                    i += len(expr_tokens)
                    matched = True
                    break
            if matched:
                continue
            # 2. proper name (per-story table; takes precedence over the
            #    dictionary — see D-031)
            norm = tok.normalized
            if norm in names:
                records.append(_token_record(tok.surface, "name", [],
                                             names[norm]["note"]))
                stats["name"] += 1
                unique["name"].add(norm)
                i += 1
                continue
            # 3. exact reverse-index hit
            hits = idx.lookup(norm)
            if hits:
                cands = candidates_from_hits(
                    hits, "pl_gloss_exact",
                    "pl gloss '{gloss}' (basic.json row {id})", provider,
                    lemma_forms)
                records.append(_token_record(tok.surface, "exact", cands))
                stats["exact"] += 1
                unique["exact"].add(norm)
                i += 1
                continue
            # 4. dictionary-verified lemma recovery
            recovered = lemma_recovery(norm, idx)
            if recovered:
                stem, rhits = recovered
                cands = candidates_from_hits(
                    rhits, "lemma_recovery",
                    "recovered stem '{gloss}' (suffix rule; basic.json row {id})",
                    provider, lemma_forms)
                records.append(_token_record(tok.surface, "recovery", cands,
                                             note=f"recovered lemma '{stem}'"))
                stats["recovery"] += 1
                unique["recovery"].add(norm)
                i += 1
                continue
            # 5. curated residual
            if norm in residual:
                entry = residual[norm]
                if entry["isv"]:
                    cands = curated_candidates(
                        entry["isv"], "curation/residual.tsv", entry["basis"],
                        provider, lemma_forms, idx.headword_pos)
                    records.append(_token_record(tok.surface, "curated", cands,
                                                 entry["basis"]))
                    stats["curated"] += 1
                    unique["curated"].add(norm)
                else:
                    records.append(_token_record(
                        tok.surface, "unmapped", [],
                        "reviewed; no defensible candidate"))
                    stats["unmapped"] += 1
                    unique["unmapped"].add(norm)
                i += 1
                continue
            # 6. unmapped
            records.append(_token_record(
                tok.surface, "unmapped", [],
                "no mapping found; use your judgment"))
            stats["unmapped"] += 1
            unique["unmapped"].add(norm)
            i += 1
        sentence_payloads.append({
            "sentence_id": sentence_id,
            "text": toks[0].sentence if toks else "",
            "tokens": records,
        })

    return {
        "sentences": sentence_payloads,
        "statistics": {
            "lexical_tokens": len(tokens),
            "by_kind_tokens": dict(stats),
            "by_kind_unique": {k: len(v) for k, v in unique.items()},
            "tokens_with_candidates": sum(
                1 for sent in sentence_payloads
                for t in sent["tokens"] if t["mapped"]),
            "candidate_surfaces": sum(
                1 for sent in sentence_payloads
                for t in sent["tokens"] for _ in t["isv_candidates"]),
            "candidate_surfaces_unique": len({
                c["surface"] for sent in sentence_payloads
                for t in sent["tokens"] for c in t["isv_candidates"]}),
        },
    }


# ---------------------------------------------------------------------------
# Rendering (per condition)
# ---------------------------------------------------------------------------

_CURATION_MARKER = "‡"
_LEGEND = (
    "Provenance: candidates are Interslavic headwords from the project's\n"
    "canonical dictionary (basic.json), matched through its Polish translation\n"
    "gloss, or from the per-story curation table (marked ‡). Full per-candidate\n"
    "evidence is in scaffolds/op-pl/scaffold.json."
)


def _grammar_note(tok: dict) -> str | None:
    """Single grammar note for a token's candidates (Condition D)."""
    parts: list[str] = []
    seen_pos: set[str] = set()
    for cand in tok["isv_candidates"]:
        for ann in cand["annotations"]:
            if ann["kind"] != "grammar":
                continue
            pos = ann.get("pos") or ""
            if pos not in seen_pos:
                seen_pos.add(pos)
                if ann.get("examples"):
                    parts.append(f"{pos}; e.g. {', '.join(ann['examples'])}")
                else:
                    parts.append(pos)
    return "; ".join(parts) or None


def render_scaffold(payload: dict, condition: str) -> str:
    """Human-readable scaffold block for the prompt (B/C/D)."""
    assert condition in ("B", "C", "D"), condition
    lines: list[str] = []
    for sent in payload["sentences"]:
        for tok in sent["tokens"]:
            surf = tok["pl_surface"]
            kind = tok["kind"]
            if kind == "name":
                lines.append(f"{surf:<14} → [{surf}]  (proper name — keep as-is)")
                continue
            if kind == "unmapped":
                lines.append(f"{surf:<14} → [?]")
                continue
            marker = _CURATION_MARKER if kind in ("curated", "multiword") else ""
            if condition == "B":
                first = tok["isv_candidates"][0]
                lines.append(f"{surf:<14} → [{first['surface']}]{marker}")
            else:
                surfaces = ", ".join(c["surface"] for c in tok["isv_candidates"])
                if condition == "D":
                    ann = _grammar_note(tok)
                    if ann:
                        lines.append(f"{surf:<14} → [{surfaces}]{marker}  ({ann})")
                    else:
                        lines.append(f"{surf:<14} → [{surfaces}]{marker}")
                else:
                    lines.append(f"{surf:<14} → [{surfaces}]{marker}")
        lines.append("")
    body = "\n".join(lines).rstrip() + "\n"
    return body + _LEGEND + "\n"


# ---------------------------------------------------------------------------
# Source cleaning (story-only input)
# ---------------------------------------------------------------------------

_CLEANED_SOURCE_NOTE = (
    "Cleaned from experiments/exp001-baseline/input/source.txt: removed the "
    "markdown fence lines, the EXP-001 instruction line "
    "('Przetłumacz to opowiadanie na medżusłowiański:'), and surrounding "
    "blank lines. The story text (title, headings, body, 'KONIEC' marker) is "
    "preserved byte-for-byte."
)


def clean_source() -> int:
    """Register the story-only source text with a documented derivation."""
    if not EXP001_SOURCE.is_file():
        print(f"error: EXP-001 source not found: {EXP001_SOURCE}",
              file=sys.stderr)
        return 2
    dst = INPUT_DIR / "source.txt"
    if dst.exists():
        print(f"error: {dst} already exists; refusing to overwrite "
              "(never overwrite an existing source)", file=sys.stderr)
        return 2
    raw = EXP001_SOURCE.read_text(encoding="utf-8")
    lines = [ln for ln in raw.splitlines()
             if ln.strip() not in ("```markdown", "```")]
    lines = [ln for ln in lines if ln.strip() != EXP001_INSTRUCTION]
    story = "\n".join(lines).strip() + "\n"
    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    (INPUT_DIR / "source.txt").write_text(story, encoding="utf-8")
    meta = {
        "experiment_id": EXPERIMENT_ID,
        "story_id": STORY_ID,
        "filename": "source.txt",
        "sha256": hashlib.sha256(story.encode("utf-8")).hexdigest(),
        "size_bytes": len(story.encode("utf-8")),
        "derivation": {
            "from": str(EXP001_SOURCE),
            "from_sha256": hashlib.sha256(raw.encode("utf-8")).hexdigest(),
            "note": _CLEANED_SOURCE_NOTE,
        },
        "provision_timestamp": datetime.now(timezone.utc).isoformat(),
        "copyright_note": (
            "Project Owner owns the story and permits its use in this "
            "project; keep local, do not commit or redistribute."
        ),
    }
    (INPUT_DIR / "source.meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"source registered: {dst} ({meta['sha256']})")
    return 0


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------


def git_commit() -> str:
    try:
        proc = subprocess.run(
            ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=10,
        )
        return proc.stdout.strip() if proc.returncode == 0 else "unknown"
    except (OSError, subprocess.SubprocessError):
        return "unknown"


def _serialize(payload: dict) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)


def build_scaffold(out_dir: Path, force: bool = False) -> int:
    """Generate scaffold.json + scaffold_B/C/D.txt into out_dir."""
    source_path = INPUT_DIR / "source.txt"
    if not source_path.is_file():
        print(f"error: no story source at {source_path}; run "
              "`python scripts/build_exp003_scaffold.py clean-source` first",
              file=sys.stderr)
        return 2
    if not BASIC_JSON.is_file():
        print(f"error: dictionary snapshot not found: {BASIC_JSON}",
              file=sys.stderr)
        return 2

    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / "scaffold.json"
    if target.exists() and not force:
        print(f"error: {target} already exists; use --force to rebuild "
              "(scaffold changes invalidate collected runs)",
              file=sys.stderr)
        return 2

    idx = PolishReverseIndex.load(BASIC_JSON)
    curation = load_curation()
    provider = _load_provider()
    lemma_forms = (build_lemma_forms(DEFAULT_LEXICON)
                   if DEFAULT_LEXICON.is_file() else None)
    story_text = source_path.read_text(encoding="utf-8")

    aligned = align_story(story_text, idx, curation, provider, lemma_forms)

    manifest = {}
    if DEFAULT_MANIFEST.is_file():
        try:
            manifest = json.loads(DEFAULT_MANIFEST.read_text(encoding="utf-8"))
        except ValueError:
            manifest = {}
    payload = {
        "experiment_id": EXPERIMENT_ID,
        "story_id": STORY_ID,
        "generator": {
            "script": "scripts/build_exp003_scaffold.py",
            "commit": git_commit(),
        },
        "sources": {
            "source_text": {
                "file": str(source_path),
                "sha256": hashlib.sha256(
                    story_text.encode("utf-8")).hexdigest(),
            },
            "reverse_index": {
                "source": idx.source,
                "sha256": idx.sha256,
                "rows": idx.row_count,
                "pl_gloss_keys": len(idx),
            },
            "dictionary_manifest": manifest,
            "alternative_resources": _provider_provenance(provider),
            "curation": {
                "story_id": curation["story_id"],
                "dir": curation["dir"],
                "multiword_entries": len(curation["multiword"]),
                "name_forms": len(curation["names"]),
                "residual_entries": len(curation["residual"]),
                "residual_unmapped": sum(
                    1 for e in curation["residual"].values()
                    if not e["isv"]),
            },
        },
        "sentences": aligned["sentences"],
        "statistics": aligned["statistics"],
        "note": (
            "Deterministic scaffold. Candidates are dictionary-verified or "
            "curated (see DESIGN.md); unmapped source forms are [?]. No "
            "LLM was involved in generating this file."
        ),
    }
    serialized = _serialize(payload)
    payload["scaffold_sha256"] = hashlib.sha256(
        serialized.encode("utf-8")).hexdigest()
    serialized = _serialize(payload)
    (out_dir / "scaffold.json").write_text(serialized, encoding="utf-8")
    for condition in ("B", "C", "D"):
        (out_dir / f"scaffold_{condition}.txt").write_text(
            render_scaffold(payload, condition), encoding="utf-8")

    stats = payload["statistics"]
    print(f"[build] {out_dir}/")
    print(f"  lexical tokens: {stats['lexical_tokens']}")
    for kind in ("exact", "recovery", "name", "multiword", "curated",
                 "unmapped"):
        print(f"  {kind:10s}: {stats['by_kind_tokens'][kind]} tokens "
              f"({stats['by_kind_unique'][kind]} unique)")
    print(f"  scaffold_sha256: {payload['scaffold_sha256']}")
    return 0


def _load_provider():
    try:
        from isv_eval.evidence import load_default_provider
        return load_default_provider()
    except Exception:  # pragma: no cover - defensive
        return None


def _provider_provenance(provider) -> dict:
    if provider is None:
        return {"available": False,
                "note": "audited alternative resources not loaded; "
                        "no candidate annotations"}
    return {"available": True, "provenance": provider.provenance}


def stats() -> int:
    target = SCAFFOLD_DIR / STORY_ID / "scaffold.json"
    if not target.is_file():
        print(f"error: no scaffold at {target}; build it first", file=sys.stderr)
        return 2
    payload = json.loads(target.read_text(encoding="utf-8"))
    s = payload["statistics"]
    print(f"story: {payload['story_id']}  scaffold_sha256: "
          f"{payload['scaffold_sha256']}")
    print(f"lexical tokens: {s['lexical_tokens']}")
    print(f"tokens with candidates: {s['tokens_with_candidates']}")
    for kind in ("exact", "recovery", "name", "multiword", "curated",
                 "unmapped"):
        print(f"  {kind:10s}: {s['by_kind_tokens'][kind]} tokens "
              f"({s['by_kind_unique'][kind]} unique)")
    print(f"candidate surfaces: {s['candidate_surfaces']} total, "
          f"{s['candidate_surfaces_unique']} unique")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("clean-source", help="register the story-only source")
    p_build = sub.add_parser("build", help="build the scaffold + renderings")
    p_build.add_argument("--force", action="store_true",
                         help="overwrite an existing scaffold")
    p_build.add_argument("--out", default=str(SCAFFOLD_DIR / STORY_ID),
                         help="output directory")
    sub.add_parser("stats", help="show scaffold statistics")
    args = parser.parse_args(argv)

    if args.command == "clean-source":
        return clean_source()
    if args.command == "build":
        return build_scaffold(Path(args.out), force=args.force)
    if args.command == "stats":
        return stats()
    return 2


if __name__ == "__main__":
    sys.exit(main())
