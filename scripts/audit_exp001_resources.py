#!/usr/bin/env python3
"""Post-hoc cross-resource audit of Experiment 001 unresolved forms (SODA Task 005).

Evidence-only audit: for every unique unresolved form from Experiment 001, record
what each locally available Interslavic resource says about it. No resource is
modified and no linguistic judgment is made.

Resources audited:
  * basic_json           — data/dictionary/basic.json snapshot (canonical headwords)
  * full_form_lexicon    — generated data/dictionary/lexicon.tsv (JS morphology dump)
  * slovnik              — medzuslovjansky/slovnik src/services/dictionary-test/basic.json
                           (independent earlier snapshot of the same lineage)
  * hunspell             — isv.dic / isv.aff (full-form Interslavic Hunspell dict,
                           vendored in medzuslovjansky/interslavicfreq data)
  * interslavicfreq      — small_isv / small_isvx frequency wordlists (frozen msgpack)
  * js_morphology        — @interslavic/morphology via the generated lexicon;
                           "can the engine generate the observed form"
  * rust_morphology      — gold-silver-copper/interslavic (NOT_TESTABLE: no toolchain)

Evidence categories are NOT final judgments (see task §7).
Outputs (written next to this script's results):
  experiments/exp001-baseline/manual-audit/cross-resource-audit.json
  experiments/exp001-baseline/manual-audit/cross-resource-audit.csv
"""

from __future__ import annotations

import csv
import gzip
import json
import pickle
import re
import sys
import time
import unicodedata
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from isv_eval.lexicon import HEADWORD, PARADIGM, Lexicon
from isv_eval.normalize import fold_etymological, is_cyrillic, lookup_keys, normalize_word

# ----------------------------------------------------------------------------
# Evidence categories (task §7). These describe what a resource contains for a
# given form; they are NOT linguistic-quality judgments.
# ----------------------------------------------------------------------------
EXACT_FORM = "EXACT_FORM"                # the form itself is listed (or is a headword)
MORPH_FORM = "MORPHOLOGICAL_FORM"        # listed as a generated inflection of a lemma
LEMMA_FOUND = "LEMMA_FOUND"              # the resource exposes the form as a lemma/stem,
#                                        # but not as a surface form
ORTHO_VARIANT = "ORTHOGRAPHIC_VARIANT"   # only via an orthographic transformation
SIMILAR_FORM = "SIMILAR_FORM"            # reserved; not assigned in this audit
NO_MATCH = "NO_MATCH"
NOT_TESTABLE = "NOT_TESTABLE"

EVIDENCE_ORDER = [
    EXACT_FORM, MORPH_FORM, LEMMA_FOUND, ORTHO_VARIANT, SIMILAR_FORM, NO_MATCH, NOT_TESTABLE,
]

# ----------------------------------------------------------------------------
# Paths
# ----------------------------------------------------------------------------
EXP_DIR = ROOT / "experiments" / "exp001-baseline"
OUTPUTS = EXP_DIR / "outputs"
AUDIT_DIR = EXP_DIR / "manual-audit"
DICT_DIR = ROOT / "data" / "dictionary"

COMPARISON_JSON = OUTPUTS / "comparison.json"
BASIC_JSON = DICT_DIR / "basic.json"
LEXICON_TSV = DICT_DIR / "lexicon.tsv"
SLOVNIK_JSON = DICT_DIR / "audit" / "slovnik" / "basic.json"
HUNSPELL_DIC = DICT_DIR / "audit" / "hunspell" / "isv.dic"
HUNSPELL_CACHE = DICT_DIR / "audit" / "hunspell" / "_isv_forms.pkl.gz"
FREQ_ISV = DICT_DIR / "audit" / "frequency" / "small_isv.msgpack.gz"
FREQ_ISVX = DICT_DIR / "audit" / "frequency" / "small_isvx.msgpack.gz"

# ----------------------------------------------------------------------------
# Deterministic special-case detection (task §11). Character/place-name families
# and quoted example words from the source story; no linguistic-origin judgment.
# ----------------------------------------------------------------------------
NAME_PATTERNS = [
    ("bronislaw", re.compile(r"^bronislav")),
    ("teofil", re.compile(r"^teofil")),
    ("julianna", re.compile(r"^juli(j)?an")),
    ("przemyslaw", re.compile(r"^przemys[łl]aw|^prěmyslav|^přemyslav|^premis")),
    ("miedzyrzecze", re.compile(r"^medzureč|^medžureč|^mežurěč|^meždurěč|^međuzeml")),
    ("antoni", re.compile(r"^antoni")),
]
QUOTED_EXAMPLE_WORDS = {"pul", "pui"}  # source story quotes these as example words


def special_case(form: str) -> tuple[str | None, str | None]:
    """Return (name_family, special_reason) deterministically, else (None, None)."""
    for family, pat in NAME_PATTERNS:
        if pat.match(form):
            return family, None
    if form in QUOTED_EXAMPLE_WORDS:
        return None, "quoted_story_example_word"
    return None, None


# ----------------------------------------------------------------------------
# Loading
# ----------------------------------------------------------------------------
def load_dict_json(path: Path) -> list[dict]:
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    wordlist = data["wordList"]
    header = [str(h) for h in wordlist[0]]
    return [dict(zip(header, row)) for row in wordlist[1:]]


def build_dict_index(rows: list[dict]) -> dict[str, list[dict]]:
    """Index headwords and comma-split `addition` variants under normalized keys."""
    index: dict[str, list[dict]] = {}
    for row in rows:
        isv = row.get("isv", "").strip()
        keys = [isv] if isv else []
        addition = row.get("addition", "").strip()
        if addition:
            keys += [a.strip() for a in addition.split(",") if a.strip()]
        for k in keys:
            norm = normalize_word(k)
            if not norm:
                continue
            index.setdefault(norm, []).append(row)
    return index


def load_hunspell(dic_path: Path, cache_path: Path) -> tuple[dict[str, str], set[str]]:
    """Return (surface_form -> tag_annotation, set_of_stems) from isv.dic.

    Each non-header line is `FORM st:STEM po:... gen:... case:... num:... id:...`.
    A leading '-' is a stem-prefix marker used by the pipeline; we strip it from
    the surface token. Tags are kept verbatim as evidence.
    """
    if cache_path.exists():
        with gzip.open(cache_path, "rb") as fh:
            forms, stems = pickle.load(fh)
        return forms, stems
    forms: dict[str, str] = {}
    stems: set[str] = set()
    t0 = time.time()
    with open(dic_path, encoding="utf-8") as fh:
        fh.readline()  # header = entry count
        for line in fh:
            if not line.strip():
                continue
            parts = line.split()
            surface = parts[0].lstrip("-")
            tags = " ".join(parts[1:])
            if surface not in forms:
                forms[surface] = tags
            for p in parts[1:]:
                if p.startswith("st:"):
                    stems.add(p[3:])
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(cache_path, "wb") as fh:
        pickle.dump((forms, stems), fh, protocol=pickle.HIGHEST_PROTOCOL)
    print(f"[hunspell] {len(forms)} surface forms, {len(stems)} stems "
          f"({time.time() - t0:.1f}s, cache saved)")
    return forms, stems


def load_freq(path: Path) -> dict[str, int]:
    """Decode a cBpack wordlist into word -> cB (centibel, negative)."""
    import msgpack

    with gzip.open(path, "rb") as fh:
        payload = msgpack.unpackb(fh.read(), raw=False)
    buckets = payload[1:]
    out: dict[str, int] = {}
    for cB, words in enumerate(buckets):
        neg_cb = -cB
        for w in words:
            out[w] = neg_cb
    return out


def load_form_table() -> list[dict]:
    with open(COMPARISON_JSON, encoding="utf-8") as fh:
        comp = json.load(fh)
    return comp["unresolved_overlap"]["form_table"]


def load_candidates() -> dict[str, list[str]]:
    """Union of per-record candidate lemmas across all runs' unresolved.json."""
    cands: dict[str, set[str]] = {}
    for run_dir in sorted(OUTPUTS.glob("*")):
        if not run_dir.is_dir():
            continue
        unresolved_path = run_dir / "unresolved.json"
        if not unresolved_path.exists():
            continue
        with open(unresolved_path, encoding="utf-8") as fh:
            records = json.load(fh)
        for rec in records:
            if rec.get("classification") != "C":
                continue
            norm = rec.get("normalized")
            if not norm:
                continue
            for cand in rec.get("candidates") or []:
                cands.setdefault(norm, set()).add(cand)
    return {k: sorted(v) for k, v in cands.items()}


# ----------------------------------------------------------------------------
# Orthography helpers (task §8). Transformed comparisons are recorded separately;
# they are never silently upgraded into a match.
# ----------------------------------------------------------------------------
def strip_diacritics(word: str) -> str:
    """NFD + drop combining marks (covers ё/е, é/e, ě/e, ...). Does not touch
    base letters that do not decompose (e.g. ł), which are folded separately."""
    decomposed = unicodedata.normalize("NFD", word)
    return "".join(ch for ch in decomposed if unicodedata.category(ch) != "Mn")


def check_resource(index: dict[str, list[dict]], norm: str, folded: str, stripped: str):
    """Common dictionary-style check (basic.json / slovnik).

    Returns (evidence, details) where details lists what was matched.
    """
    exact = index.get(norm)
    if exact:
        return EXACT_FORM, [{"matched": "headword", "entries": exact}]
    if folded != norm and index.get(folded):
        return ORTHO_VARIANT, [{"matched": f"folded:{folded}", "entries": index[folded]}]
    return NO_MATCH, []


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------
def main() -> None:
    t_start = time.time()

    form_table = load_form_table()
    print(f"[input] {len(form_table)} unique unresolved forms")
    candidates_by_form = load_candidates()
    print(f"[input] candidate lemmas for {len(candidates_by_form)} forms")

    print("[load] basic.json ...")
    basic_rows = load_dict_json(BASIC_JSON)
    basic_index = build_dict_index(basic_rows)
    print(f"[load] basic.json: {len(basic_rows)} rows indexed")

    print("[load] lexicon.tsv ...")
    lex = Lexicon.load_tsv(LEXICON_TSV)
    lex_keys = lex._by_key  # normalized (primary) and folded keys -> entries
    print(f"[load] lexicon: {len(lex)} entries")

    print("[load] slovnik snapshot ...")
    slovnik_rows = load_dict_json(SLOVNIK_JSON)
    slovnik_index = build_dict_index(slovnik_rows)
    print(f"[load] slovnik: {len(slovnik_rows)} rows indexed")

    print("[load] hunspell isv.dic ...")
    hunspell_forms, hunspell_stems = load_hunspell(HUNSPELL_DIC, HUNSPELL_CACHE)

    print("[load] interslavicfreq wordlists ...")
    freq_isv = load_freq(FREQ_ISV)
    freq_isvx = load_freq(FREQ_ISVX)
    print(f"[load] frequency: isv={len(freq_isv)}, isvx={len(freq_isvx)}")

    # ------------------------------------------------------------------
    # Per-form evidence
    # ------------------------------------------------------------------
    records = []
    for rec in form_table:
        form = rec["form"]
        norm = normalize_word(form)
        folded = fold_etymological(norm)
        stripped = strip_diacritics(norm)
        cyr = is_cyrillic(norm)

        name_family, special_reason = special_case(norm)
        candidates = candidates_by_form.get(norm, [])

        # ---- basic.json (canonical snapshot) -------------------------
        b_ev, b_det = check_resource(basic_index, norm, folded, stripped)
        if b_ev == NO_MATCH and stripped != norm and stripped in basic_index:
            b_ev = ORTHO_VARIANT
            b_det = [{"matched": f"diacritic-stripped:{stripped}", "entries": basic_index[stripped]}]

        # ---- full-form lexicon (JS morphology dump) -------------------
        lex_ev, lex_det, lex_lemmas, lex_gen = NO_MATCH, [], [], []
        for entry in lex_keys.get(norm, ()):
            lex_det.append({
                "form": entry.form, "lemma": entry.lemma, "xpos": entry.xpos,
                "upos": entry.upos, "entry_type": entry.entry_type,
            })
            lex_lemmas.append(entry.lemma)
        if lex_det:
            any_head = any(e["entry_type"] == HEADWORD for e in lex_det)
            lex_ev = EXACT_FORM if any_head else MORPH_FORM
            lex_gen = sorted(set(lex_lemmas))
        elif folded != norm and lex_keys.get(folded):
            lex_ev = ORTHO_VARIANT
            lex_det = [{
                "matched": f"folded:{folded}",
                "entries": [e.as_dict() for e in lex_keys.get(folded)],
            }]
        elif stripped != norm and lex_keys.get(stripped):
            lex_ev = ORTHO_VARIANT
            lex_det = [{
                "matched": f"diacritic-stripped:{stripped}",
                "entries": [e.as_dict() for e in lex_keys.get(stripped)],
            }]

        # ---- slovnik (alternative snapshot of the same lineage) --------
        s_ev, s_det = check_resource(slovnik_index, norm, folded, stripped)
        if s_ev == NO_MATCH and stripped != norm and stripped in slovnik_index:
            s_ev = ORTHO_VARIANT
            s_det = [{"matched": f"diacritic-stripped:{stripped}", "entries": slovnik_index[stripped]}]

        # ---- hunspell isv.dic (full-form dictionary) --------------------
        h_ev, h_det = NO_MATCH, []
        if norm in hunspell_forms:
            h_ev = EXACT_FORM
            h_det = [{"form": norm, "tags": hunspell_forms[norm]}]
        elif norm in hunspell_stems:
            h_ev = LEMMA_FOUND
            h_det = [{"form": norm, "matched": "stem"}]
        elif folded != norm and folded in hunspell_forms:
            h_ev = ORTHO_VARIANT
            h_det = [{"form": folded, "matched": "folded", "tags": hunspell_forms[folded]}]
        elif stripped != norm and stripped in hunspell_forms:
            h_ev = ORTHO_VARIANT
            h_det = [{"form": stripped, "matched": "diacritic-stripped", "tags": hunspell_forms[stripped]}]

        # ---- interslavicfreq wordlists ----------------------------------
        f_ev, f_det = NO_MATCH, []
        if norm in freq_isv:
            f_ev = EXACT_FORM
            f_det = [{"wordlist": "small_isv", "cB": freq_isv[norm]}]
        elif norm in freq_isvx:
            f_ev = EXACT_FORM
            f_det = [{"wordlist": "small_isvx", "cB": freq_isvx[norm]}]
        elif stripped != norm and (stripped in freq_isv or stripped in freq_isvx):
            f_ev = ORTHO_VARIANT
            f_det = [{"wordlist": "small_isv" if stripped in freq_isv else "small_isvx",
                      "cB": freq_isv.get(stripped) or freq_isvx.get(stripped),
                      "matched": f"diacritic-stripped:{stripped}"}]

        # ---- JS morphology engine ---------------------------------------
        # The generated lexicon is a complete dump of the engine's paradigms
        # for every basic.json lemma. A form absent from the lexicon cannot be
        # generated from any dictionary lemma; the classifier's live fallback
        # additionally tested the recorded candidate lemmas without success
        # (that is precisely why the form is classified C).
        if lex_ev in (EXACT_FORM, MORPH_FORM):
            js_ev = MORPH_FORM if lex_ev == MORPH_FORM else EXACT_FORM
            js_note = None
        else:
            js_ev = NO_MATCH
            js_note = (
                "Not in generated full-form lexicon; candidate lemmas present "
                "but the evaluator's morphology fallback did not generate it."
                if candidates else
                "Not in generated full-form lexicon and no candidate lemmas."
            )

        # ---- Rust morphology --------------------------------------------
        rust_ev, rust_note = NOT_TESTABLE, "No Rust toolchain in environment; gold-silver-copper/interslavic not compiled."

        # ---- Analytical buckets (task §13; non-exclusive) ---------------
        alt_found = (s_ev == EXACT_FORM) or (h_ev in (EXACT_FORM, LEMMA_FOUND)) or (f_ev == EXACT_FORM)
        morph_found = lex_ev in (EXACT_FORM, MORPH_FORM)
        ortho_candidate = (
            b_ev == ORTHO_VARIANT or lex_ev == ORTHO_VARIANT
            or s_ev == ORTHO_VARIANT or h_ev == ORTHO_VARIANT or f_ev == ORTHO_VARIANT
        )
        is_special = bool(name_family or special_reason)
        positive = (
            b_ev == EXACT_FORM or lex_ev in (EXACT_FORM, MORPH_FORM)
            or s_ev == EXACT_FORM or h_ev in (EXACT_FORM, LEMMA_FOUND)
            or f_ev == EXACT_FORM
        )
        buckets: list[str] = []
        if alt_found:
            buckets.append("FOUND_IN_ALTERNATIVE_RESOURCE")
        if morph_found:
            buckets.append("FOUND_BY_MORPHOLOGY_ENGINE")
        if ortho_candidate:
            buckets.append("ORTHOGRAPHIC_VARIANT_CANDIDATE")
        if is_special:
            buckets.append("PROPER_NAME_OR_SPECIAL")
        if not positive and not ortho_candidate and not is_special:
            buckets.append("CURRENT_RESOURCES_AGREE_NO_MATCH")
        if not positive and candidates and not lex_gen:
            buckets.append("AMBIGUOUS")  # candidate lemmas exist but cannot generate the form
        elif not positive and ortho_candidate:
            buckets.append("AMBIGUOUS")  # only an orthographic candidate, no exact evidence

        per_model = {m: rec[m] for m in (
            "Claude", "DeepSeek", "Gemini", "ChatGPT", "GPTs — ISV Teacher", "Bielik", "Grok"
        ) if rec.get(m)}

        records.append({
            "form": form,
            "normalized_form": norm,
            "models": [m for m, c in per_model.items() if c],
            "model_count": rec.get("models_with_form", len([m for m, c in per_model.items() if c])),
            "per_model": per_model,
            "total_frequency": sum(per_model.values()),
            "candidate_lemma_count": len(candidates),
            "candidate_lemmas": candidates,
            "generating_lemmas": lex_gen,
            "name_family": name_family,
            "special_reason": special_reason,
            "orthography": {
                "surface": form,
                "normalized": norm,
                "folded": folded,
                "diacritic_stripped": stripped,
                "is_cyrillic": cyr,
            },
            "resources": {
                "basic_json": {"evidence": b_ev, "hits": b_det},
                "full_form_lexicon": {"evidence": lex_ev, "hits": lex_det},
                "slovnik": {"evidence": s_ev, "hits": s_det},
                "hunspell": {"evidence": h_ev, "hits": h_det},
                "interslavicfreq": {"evidence": f_ev, "hits": f_det},
                "js_morphology": {"evidence": js_ev, "note": js_note},
                "rust_morphology": {"evidence": rust_ev, "note": rust_note},
            },
            "buckets": buckets,
        })

    # ------------------------------------------------------------------
    # Outputs
    # ------------------------------------------------------------------
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    with open(AUDIT_DIR / "cross-resource-audit.json", "w", encoding="utf-8") as fh:
        json.dump({"meta": {
            "task": "SODA Task 005 — post-hoc cross-resource audit of Experiment 001 unresolved forms",
            "forms_audited": len(records),
            "note": "Evidence-only; no linguistic judgments; no resource modifications.",
        }, "records": records}, fh, ensure_ascii=False, indent=1)

    csv_path = AUDIT_DIR / "cross-resource-audit.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow([
            "form", "model_count", "models", "total_frequency", "candidate_lemma_count",
            "name_family", "special_reason", "ortho_stripped", "basic_json",
            "full_form_lexicon", "slovnik", "hunspell", "interslavicfreq",
            "js_morphology", "rust_morphology", "orthographic_variant_candidate", "buckets",
        ])
        for r in records:
            writer.writerow([
                r["form"], r["model_count"], "|".join(r["models"]), r["total_frequency"],
                r["candidate_lemma_count"], r["name_family"] or "", r["special_reason"] or "",
                r["orthography"]["diacritic_stripped"],
                r["resources"]["basic_json"]["evidence"],
                r["resources"]["full_form_lexicon"]["evidence"],
                r["resources"]["slovnik"]["evidence"],
                r["resources"]["hunspell"]["evidence"],
                r["resources"]["interslavicfreq"]["evidence"],
                r["resources"]["js_morphology"]["evidence"],
                r["resources"]["rust_morphology"]["evidence"],
                "yes" if "ORTHOGRAPHIC_VARIANT_CANDIDATE" in r["buckets"] else "",
                ";".join(r["buckets"]),
            ])

    # ------------------------------------------------------------------
    # Statistics (also used by cross-resource-summary.md)
    # ------------------------------------------------------------------
    n = len(records)
    counts = {
        "total_unique_forms": n,
        "total_occurrences": sum(r["total_frequency"] for r in records),
        "forms_per_resource": {},
        "found_alt_resource_exact": 0,
        "found_morphology": 0,
        "ortho_variant_candidates": 0,
        "proper_name_or_special": 0,
        "still_unsupported": 0,
        "ambiguous": 0,
    }
    res_names = ["basic_json", "full_form_lexicon", "slovnik", "hunspell",
                 "interslavicfreq", "js_morphology", "rust_morphology"]
    for r in records:
        for rn in res_names:
            ev = r["resources"][rn]["evidence"]
            if ev in (EXACT_FORM, MORPH_FORM, LEMMA_FOUND):
                counts["forms_per_resource"].setdefault(rn, 0)
                counts["forms_per_resource"][rn] += 1
        if "FOUND_IN_ALTERNATIVE_RESOURCE" in r["buckets"]:
            counts["found_alt_resource_exact"] += 1
        if "FOUND_BY_MORPHOLOGY_ENGINE" in r["buckets"]:
            counts["found_morphology"] += 1
        if "ORTHOGRAPHIC_VARIANT_CANDIDATE" in r["buckets"]:
            counts["ortho_variant_candidates"] += 1
        if "PROPER_NAME_OR_SPECIAL" in r["buckets"]:
            counts["proper_name_or_special"] += 1
        if "CURRENT_RESOURCES_AGREE_NO_MATCH" in r["buckets"]:
            counts["still_unsupported"] += 1
        if "AMBIGUOUS" in r["buckets"]:
            counts["ambiguous"] += 1

    with open(AUDIT_DIR / "cross-resource-summary.json", "w", encoding="utf-8") as fh:
        json.dump(counts, fh, ensure_ascii=False, indent=1)

    print("\n===== AUDIT STATISTICS =====")
    for k, v in counts.items():
        if k == "forms_per_resource":
            for rn in res_names:
                print(f"  found in {rn}: {v.get(rn, 0)}")
        else:
            print(f"  {k}: {v}")
    print(f"\n[time] {time.time() - t_start:.1f}s total")
    print(f"wrote: {AUDIT_DIR/'cross-resource-audit.json'}")
    print(f"       {AUDIT_DIR/'cross-resource-audit.csv'}")
    print(f"       {AUDIT_DIR/'cross-resource-summary.json'}")


if __name__ == "__main__":
    main()
