#!/usr/bin/env python3
"""SODA Task 007 — resource-layer audit and policy evidence.

Deterministic audit of the project's Interslavic resource layers and of the
EXP-002 `interslavicfreq` discrepancy. It writes a machine-readable evidence
table that underpins `docs/RESOURCE_POLICY.md`. It modifies nothing.

Sections produced:
  1. resource inventory — every audited resource, its pin/provenance, row
     counts and file hashes, plus the layer it belongs to;
  2. discrepancy probe — for the EXP-002 discrepancy forms and their observed
     variants, what every layer contains (canonical headword / lexicon /
     morphology generation / hunspell tags / frequency cB / slovnik) and how
     the live evaluator classifies them;
  3. layer overlap — over the full 1,050-form unresolved population, how many
     forms are attested in which layer, and their combinations;
  4. broader-coverage demonstration — a separate, clearly labeled analysis:
     per EXP-001 run, how much of the unresolved vocabulary is attested in
     alternative resources (hunspell `isv.dic` exact / `interslavicfreq`
     exact) in addition to the canonical A/B coverage. This is NOT a
     recalculation of the historical metrics; it is a new metric estimate.

Outputs (gitignored; derived from dictionary data whose license is unresolved):
  data/dictionary/resource-policy/evidence.json

Read-only inputs (all existing artifacts):
  data/dictionary/{basic.json,lexicon.tsv}
  data/dictionary/audit/{hunspell/isv.dic,hunspell/_isv_forms.pkl.gz,
      frequency/small_isv.msgpack.gz,frequency/small_isvx.msgpack.gz,
      slovnik/basic.json}
  experiments/exp001-baseline/{outputs/comparison.json,
      manual-audit/cross-resource-audit.json}
"""

from __future__ import annotations

import gzip
import hashlib
import json
import pickle
import sys
import unicodedata
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from isv_eval.classifier import classify
from isv_eval.lexicon import HEADWORD, Lexicon
from isv_eval.morphology import MorphologyBackend
from isv_eval.normalize import fold_etymological, lookup_keys, normalize_word
from isv_eval.tokenizer import tokenize

EXP001 = ROOT / "experiments" / "exp001-baseline"
DICT = ROOT / "data" / "dictionary"
OUT_DIR = DICT / "resource-policy"

BASIC_JSON = DICT / "basic.json"
LEXICON_TSV = DICT / "lexicon.tsv"
SLOVNIK_JSON = DICT / "audit" / "slovnik" / "basic.json"
HUNSPELL_DIC = DICT / "audit" / "hunspell" / "isv.dic"
HUNSPELL_CACHE = DICT / "audit" / "hunspell" / "_isv_forms.pkl.gz"
FREQ_ISV = DICT / "audit" / "frequency" / "small_isv.msgpack.gz"
FREQ_ISVX = DICT / "audit" / "frequency" / "small_isvx.msgpack.gz"
COMPARISON_JSON = EXP001 / "outputs" / "comparison.json"
AUDIT_JSON = EXP001 / "manual-audit" / "cross-resource-audit.json"

# The EXP-002 discrepancy forms (from the pilot report) plus the observed
# surface variants that explain the layers' behavior.
PROBE_FORMS = [
    "seli", "sěli",
    "sedeli", "sěděli", "seděli",
    "reci", "reći", "rěci",
    "rekl", "řekl", "rekla",
    "dejstvitelno", "dējstvitelno",
    "dalše", "dalši", "daľši",
    "bojala", "bojati",
]

RUN_DISPLAY = {
    "Claude": "Claude", "DeepSeek": "DeepSeek", "Gemini": "Gemini",
    "ChatGPT": "ChatGPT", "GPTs — ISV Teacher": "GPTs — ISV Teacher",
    "Bielik": "Bielik", "Grok": "Grok",
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


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
    if cache_path.exists():
        with gzip.open(cache_path, "rb") as fh:
            forms, stems = pickle.load(fh)
        return forms, stems
    forms: dict[str, str] = {}
    stems: set[str] = set()
    with open(dic_path, encoding="utf-8") as fh:
        fh.readline()
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
    return forms, stems


def load_freq(path: Path) -> dict[str, int]:
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


def strip_diacritics(word: str) -> str:
    decomposed = unicodedata.normalize("NFD", word)
    return "".join(ch for ch in decomposed if unicodedata.category(ch) != "Mn")


# ---------------------------------------------------------------------------
# 1. Resource inventory
# ---------------------------------------------------------------------------
def resource_inventory() -> list[dict]:
    return [
        {
            "id": "basic_json",
            "name": "basic.json (live dictionary artifact)",
            "layer": "canonical dictionary",
            "provenance": "https://interslavic-dictionary.com/data/basic.json; "
                          "generated by sonic16x/medzuslovjansky dictionary app; "
                          "license UNRESOLVED (SOURCES.md item 11)",
            "rows": len(load_dict_json(BASIC_JSON)),
            "sha256": sha256_bytes(BASIC_JSON.read_bytes()),
            "note": "headwords + `addition` variants + POS + type(1..9) + intelligibility",
        },
        {
            "id": "full_form_lexicon",
            "name": "lexicon.tsv (generated full-form lexicon)",
            "layer": "canonical dictionary / morphology",
            "provenance": "generated by scripts/generate_lexicon.py from basic.json "
                          "via @interslavic/morphology@0.1.2; gitignored",
            "rows": sum(1 for _ in open(LEXICON_TSV, encoding="utf-8")),
            "sha256": sha256_bytes(LEXICON_TSV.read_bytes()),
            "note": "headwords + generated paradigms (form\\tlemma\\txpos\\tupos\\tfeats\\tentry_type)",
        },
        {
            "id": "slovnik",
            "name": "medzuslovjansky/slovnik test-fixture snapshot",
            "layer": "historical reference (same lineage as basic.json)",
            "provenance": "src/services/dictionary-test/basic.json, master, 2026-07; "
                          "gitignored copy at data/dictionary/audit/slovnik/",
            "rows": len(load_dict_json(SLOVNIK_JSON)),
            "sha256": sha256_bytes(SLOVNIK_JSON.read_bytes()),
            "note": "earlier snapshot of the same dictionary lineage (18k rows); "
                    "0 headword hits for the unresolved population (Task 005)",
        },
        {
            "id": "hunspell",
            "name": "isv.dic / isv.aff (full-form Hunspell dictionary)",
            "layer": "alternative resource (attested surface forms)",
            "provenance": "medzuslovjansky/interslavicfreq data/hunspell, pinned "
                          "b84535b; built by medzuslovjansky/isv_hunspell_dict; MIT",
            "rows": None,
            "sha256": sha256_bytes(HUNSPELL_DIC.read_bytes()),
            "note": "1,042,916 lines; ~500,952 distinct surface forms with "
                    "full-form tags; no affix rules (all surfaces enumerated); "
                    "pipeline-generated tags (artifacts possible, L-011)",
        },
        {
            "id": "interslavicfreq",
            "name": "small_isv / small_isvx frequency wordlists",
            "layer": "alternative resource (surface frequency data)",
            "provenance": "medzuslovjansky/interslavicfreq data/frequency, pinned "
                          "b84535b; MIT; frozen msgpack.gz wordlists",
            "rows": None,
            "sha256": sha256_bytes(FREQ_ISV.read_bytes()) + " / "
                      + sha256_bytes(FREQ_ISVX.read_bytes()),
            "note": "579,860 / 252,461 word->cB entries; surface wordforms, no "
                    "POS/paradigm linkage; homograph ambiguity without disambiguation",
        },
        {
            "id": "js_morphology",
            "name": "@interslavic/morphology@0.1.2 (JS engine)",
            "layer": "morphological rules",
            "provenance": "medzuslovjansky/js-utils monorepo, pinned npm version, "
                          "committed lockfile; MIT",
            "rows": None,
            "sha256": None,
            "note": "deterministic rule engine: lemma + POS (+ present hint) -> "
                    "full paradigm; runs via src/morphology_backend/backend.mjs",
        },
        {
            "id": "rust_morphology",
            "name": "gold-silver-copper/interslavic (Rust engine)",
            "layer": "morphological rules (alternate implementation)",
            "provenance": "github.com/gold-silver-copper/interslavic HEAD 599954b; "
                          "MIT OR Apache-2.0; NOT_TESTABLE here (no Rust toolchain)",
            "rows": None,
            "sha256": None,
            "note": "same rule engine, parity harness vs JS (99.98% nouns, 100% "
                    "others); representational differences only (GRAMMAR_AUDIT.md)",
        },
    ]


# ---------------------------------------------------------------------------
# 2. Discrepancy probe
# ---------------------------------------------------------------------------
def probe_forms(lex: Lexicon, backend: MorphologyBackend, basic_index: dict,
                slovnik_index: dict, hunspell_forms: dict, hunspell_stems: set,
                freq: dict, freqx: dict) -> tuple[list[dict], dict[str, str]]:
    # live evaluator classification of the probe forms
    text = " ".join(PROBE_FORMS) + "."
    tokens = tokenize(text)
    classify(tokens, lex, backend)
    cls = {t.normalized: t for t in tokens if t.is_lexical}

    # canonical headwords set (for "is the lemma canonical" checks)
    headwords = set()
    for row in basic_index.values():
        for e in row:
            headwords.add(normalize_word(e.get("isv") or ""))
            for a in str(e.get("addition") or "").split(","):
                a = a.strip()
                if a:
                    headwords.add(normalize_word(a))
    headwords.discard("")

    # batch-inflect the union of candidate lemmas that are canonical headwords
    lemma_items = []
    lemma_ids: dict[str, set[str]] = {}
    for form in PROBE_FORMS:
        for cand in lex.candidate_lemmas(form):
            if normalize_word(cand) in headwords:
                lemma_ids.setdefault(cand, set()).add(form)
    for lemma in sorted(lemma_ids):
        lemma_items.append({"id": lemma, "form": lemma,
                            "xpos": lex.lemma_xpos(lemma), "addition": None})
    generated: dict[str, list[str]] = {}
    if lemma_items:
        results = backend.inflect(lemma_items)
        for lemma, tokens_ in results.items():
            generated[lemma] = [t[0] for t in tokens_]

    records = []
    for form in PROBE_FORMS:
        norm = normalize_word(form)
        folded = fold_etymological(norm)
        stripped = strip_diacritics(norm)
        tok = cls.get(norm)

        # canonical headword / addition
        head = [{"isv": e.get("isv"), "pos": e.get("partOfSpeech"),
                 "type": e.get("type")}
                for e in basic_index.get(norm, [])]
        # lexicon exact hit
        lex_hits = [{"form": e.form, "lemma": e.lemma,
                     "entry_type": e.entry_type}
                    for e in lex.lookup(norm)[:5]] if norm in {
                        k for k in lex._by_key} else []
        # morphology generation: does any canonical candidate lemma's paradigm
        # contain the form (normalized or folded)?
        gen_by_lemma = {}
        for lemma in sorted(lemma_ids.get(form, ())):
            forms = generated.get(lemma, [])
            keys = set(lookup_keys(norm))
            hit = sorted({f for f in forms if normalize_word(f) in keys
                          or fold_etymological(f) in keys})
            if hit:
                gen_by_lemma[lemma] = hit
        # hunspell
        h_tags = hunspell_forms.get(norm) or hunspell_forms.get(folded) or None
        h_stem = norm in hunspell_stems
        # frequency
        f_exact = freq.get(norm) if norm in freq else None
        f_exactx = freqx.get(norm) if norm in freq else None
        f_stripped = (freq.get(stripped) if stripped != norm and stripped in freq
                      else None)
        f_strippedx = (freqx.get(stripped) if stripped != norm and stripped in freqx
                       else None)
        # slovnik
        s_head = [{"isv": e.get("isv"), "pos": e.get("partOfSpeech")}
                  for e in slovnik_index.get(norm, [])]

        cands = sorted(set(tok.candidates or []) if tok else [])
        records.append({
            "form": form,
            "normalized": norm,
            "canonical_dictionary": {
                "headword_or_addition": head or None,
                "in_lexicon": bool(lex_hits),
                "lexicon_hits": lex_hits,
                "candidate_lemmas": cands,
            },
            "morphology": {
                "generated_from_canonical_lemma": gen_by_lemma,
                "note": ("paradigm of the canonical candidate lemma(s) contains "
                         "the form" if gen_by_lemma else
                         "no canonical candidate lemma generates the form"),
            },
            "hunspell": {
                "exact": norm in hunspell_forms,
                "folded": (folded if folded != norm and folded in hunspell_forms else None),
                "stem": h_stem,
                "tags": h_tags,
            },
            "interslavicfreq": {
                "exact_isv_cB": f_exact,
                "exact_isvx_cB": f_exactx,
                "stripped_isv_cB": f_stripped,
                "stripped_isvx_cB": f_strippedx,
                "stripped_form": stripped if stripped != norm else None,
            },
            "slovnik": {
                "headword_or_addition": s_head or None,
            },
            "evaluator": {
                "classification": tok.classification if tok else None,
                "matches": (tok.matches[:3] if tok and tok.matches else None),
            },
        })
    return records, headwords


# ---------------------------------------------------------------------------
# 3. Layer overlap over the 1050-form unresolved population
# ---------------------------------------------------------------------------
def layer_overlap(audit_data: dict) -> dict:
    recs = audit_data["records"]

    def ev(r: dict, k: str) -> str:
        return r["resources"][k]["evidence"]

    positive = {
        "basic_json": 0, "full_form_lexicon": 0, "slovnik": 0,
        "hunspell": 0, "interslavicfreq": 0,
    }
    combos: Counter = Counter()
    for r in recs:
        bits = []
        if ev(r, "basic_json") == "EXACT_FORM":
            positive["basic_json"] += 1
            bits.append("canonical")
        if ev(r, "full_form_lexicon") in ("EXACT_FORM", "MORPHOLOGICAL_FORM"):
            positive["full_form_lexicon"] += 1
        if ev(r, "slovnik") == "EXACT_FORM":
            positive["slovnik"] += 1
            bits.append("slovnik")
        if ev(r, "hunspell") in ("EXACT_FORM", "LEMMA_FOUND"):
            positive["hunspell"] += 1
            bits.append("hunspell")
        if ev(r, "interslavicfreq") == "EXACT_FORM":
            positive["interslavicfreq"] += 1
            bits.append("freq")
        combos["+".join(sorted(bits)) if bits else "none"] += 1
    return {
        "population_unique_forms": len(recs),
        "positive_per_layer": positive,
        "attestation_combinations": dict(combos.most_common()),
        "note": "canonical/full_form_lexicon are 0 by construction: the "
                "population is the set of forms the canonical evaluator "
                "classifies C.",
    }


# ---------------------------------------------------------------------------
# 4. Broader-resource coverage demonstration (separate, labeled analysis)
# ---------------------------------------------------------------------------
def broader_coverage(audit_data: dict, comparison: dict) -> dict:
    """Per EXP-001 run: canonical coverage (A+B, historical) and the share of
    lexical tokens that are *also* attested in alternative resources (hunspell
    exact / frequency exact). NEW metric estimate; not a recalculation of the
    historical A/B/C report."""
    by_form = {r["form"]: r for r in audit_data["records"]}

    def alt_attested(form: str) -> bool:
        r = by_form.get(form)
        if not r:
            return False
        res = r["resources"]
        return (res["hunspell"]["evidence"] == "EXACT_FORM"
                or res["interslavicfreq"]["evidence"] == "EXACT_FORM")

    runs = {}
    for display, d in comparison["runs"].items():
        lex_tokens = d["total_tokens"]
        a = d["exact_dictionary_matches"]
        b = d["morphologically_valid_forms"]
        # count C-tokens whose form is alternative-attested
        alt_tokens = 0
        for row in comparison["unresolved_overlap"]["form_table"]:
            if alt_attested(row["form"]):
                alt_tokens += row.get(display, 0) or 0
        runs[display] = {
            "lexical_tokens": lex_tokens,
            "canonical_coverage": round((a + b) / lex_tokens, 4),
            "alternative_attested_unresolved_tokens": alt_tokens,
            "broader_resource_supported_coverage": round(
                (a + b + alt_tokens) / lex_tokens, 4),
        }
    return runs


def main() -> int:
    print("[load] resources ...")
    basic_rows = load_dict_json(BASIC_JSON)
    basic_index = build_dict_index(basic_rows)
    slovnik_rows = load_dict_json(SLOVNIK_JSON)
    slovnik_index = build_dict_index(slovnik_rows)
    lex = Lexicon.load_tsv(LEXICON_TSV)
    hunspell_forms, hunspell_stems = load_hunspell(HUNSPELL_DIC, HUNSPELL_CACHE)
    freq = load_freq(FREQ_ISV)
    freqx = load_freq(FREQ_ISVX)
    audit_data = json.loads(AUDIT_JSON.read_text(encoding="utf-8"))
    comparison = json.loads(COMPARISON_JSON.read_text(encoding="utf-8"))
    print(f"  basic.json {len(basic_rows)} rows; slovnik {len(slovnik_rows)} rows; "
          f"lexicon {len(lex)} entries; hunspell {len(hunspell_forms)} forms; "
          f"freq {len(freq)}/{len(freqx)}")

    print("[probe] discrepancy forms with the live evaluator ...")
    backend = MorphologyBackend()
    probes, _headwords = probe_forms(
        lex, backend, basic_index, slovnik_index, hunspell_forms, hunspell_stems,
        freq, freqx)
    backend = None

    print("[stats] layer overlap over the unresolved population ...")
    overlap = layer_overlap(audit_data)

    print("[demo] broader-resource coverage per EXP-001 run ...")
    broader = broader_coverage(audit_data, comparison)

    evidence = {
        "meta": {
            "task": "SODA Task 007 — resource-layer audit and policy evidence",
            "note": "Evidence-only; no linguistic judgments; no resource "
                    "modifications; no evaluator changes.",
        },
        "resource_inventory": resource_inventory(),
        "discrepancy_probe": probes,
        "layer_overlap": overlap,
        "broader_resource_supported_coverage_demonstration": broader,
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "evidence.json"
    out_path.write_text(json.dumps(evidence, ensure_ascii=False, indent=1),
                        encoding="utf-8")
    print(f"\n[wrote] {out_path.relative_to(ROOT)}")

    print("\n== broader-resource coverage demonstration (labeled, new analysis) ==")
    for display, d in broader.items():
        print(f"  {display:20s} canonical={d['canonical_coverage']:.4f}  "
              f"+alt={d['alternative_attested_unresolved_tokens']:4d}  "
              f"broader={d['broader_resource_supported_coverage']:.4f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
