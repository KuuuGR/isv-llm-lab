#!/usr/bin/env python3
"""EXP-002 pilot — prepare dictionary-guided revision input packages.

For a chosen EXP-001 source run, this script:

1. reads the run's unresolved forms (plus Task-005 cross-resource audit evidence),
2. generates a deterministic candidate list per form (canonical dictionary /
   orthographic variant / alternative resource / morphology-derived / none),
3. applies a deterministic stratified pilot selection,
4. renders the complete revision prompt (template + candidate table + the
   COMPLETE original translation) and writes an immutable input package:

    experiments/exp002-pilot/input/<pilot_run_id>/
        original.txt       complete original translation (byte-for-byte copy)
        candidates.json    per-form candidate evidence (machine-readable)
        prompt.txt         the COMPLETE revision prompt to send to an LLM
        meta.json          provenance + selection + candidate statistics

LLM execution is external (this project has no LLM API client — D-007). The
operator sends prompt.txt to an LLM and saves the returned text byte-for-byte
as experiments/exp002-pilot/outputs/<pilot_run_id>/revised.txt; the comparison
is then produced by scripts/compare_exp002.py using the SAME evaluator.

Candidate kinds (evidence categories, not judgments):
  canonical_dictionary    surface form / lemma is canonical (basic.json/lexicon)
  orthographic_variant    a canonical/attested form via diacritic/fold variant
  alternative_resource    exact attestation in hunspell / interslavicfreq / slovnik
  morphology_derived      canonical dictionary lemma with a generated paradigm
  none                    no defensible candidate (leave unchanged)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from isv_eval.cli import git_commit, load_manifest
from isv_eval.lexicon import HEADWORD, Lexicon
from isv_eval.morphology import MORPHOLOGY_PACKAGE, morphology_version
from isv_eval.normalize import normalize_word

EXP001 = ROOT / "experiments" / "exp001-baseline"
OUTPUTS001 = EXP001 / "outputs"
AUDIT_JSON = EXP001 / "manual-audit" / "cross-resource-audit.json"
EXP002 = ROOT / "experiments" / "exp002-pilot"
INPUT_DIR = EXP002 / "input"
TEMPLATE = EXP002 / "prompt_template.txt"
BASIC_JSON = ROOT / "data" / "dictionary" / "basic.json"
LEXICON_TSV = ROOT / "data" / "dictionary" / "lexicon.tsv"

NAME_PATTERNS = [
    ("bronislaw", re.compile(r"^bronislav")),
    ("teofil", re.compile(r"^teofil")),
    ("julianna", re.compile(r"^juli")),
    ("przemyslaw", re.compile(r"^przemys")),
    ("miedzyrzecze", re.compile(r"^medzureč|^medžureč|^mežurěč|^meždurěč|^međuzeml")),
    ("antoni", re.compile(r"^antoni")),
]
QUOTED_EXAMPLES = {"pul", "pui"}  # source story quotes these as example words


def name_or_special(form: str) -> tuple[str | None, str | None]:
    """Deterministic name-family / special-case detection.

    A superset of the Task-005 audit's detection: character/place-name stems
    and the story's quoted example words. Used only to EXCLUDE such forms from
    the revision candidate table (they are preserved, not revised), not to
    classify anything.
    """
    for family, pat in NAME_PATTERNS:
        if pat.match(form):
            return family, None
    if form in QUOTED_EXAMPLES:
        return None, "quoted_story_example_word"
    return None, None

# Deterministic per-stratum caps for the pilot selection.
STRATUM_CAPS = {
    "ortho": 5,        # orthographic-variant candidates
    "resource": 5,     # alternative-resource exact attestation
    "morphology": 5,   # morphology-derived canonical lemma
    "high_freq": 4,    # remaining top-frequency
    "shared": 4,       # remaining shared-by-many (model_count >= 2)
    "specific": 4,     # remaining model-specific (model_count == 1)
    "no_candidate": 3, # remaining forms with no candidate
}
MAX_ALTERNATIVES = 6   # prompt cap per form


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------
def load_run(source_run_id: str) -> dict:
    run_dir = OUTPUTS001 / source_run_id
    meta = json.loads((run_dir / "meta.json").read_text(encoding="utf-8"))
    unresolved = json.loads((run_dir / "unresolved.json").read_text(encoding="utf-8"))
    original = (run_dir / "output.txt").read_bytes()
    return {"meta": meta, "unresolved": unresolved, "original": original}


def load_audit() -> dict[str, dict]:
    data = json.loads(AUDIT_JSON.read_text(encoding="utf-8"))
    return {r["form"]: r for r in data["records"]}


def load_headwords() -> set[str]:
    """Normalized canonical headwords: basic.json `isv` + `addition` variants,
    plus lexicon headword entries."""
    data = json.loads(BASIC_JSON.read_text(encoding="utf-8"))
    header = [str(h) for h in data["wordList"][0]]
    rows = [dict(zip(header, r)) for r in data["wordList"][1:]]
    heads: set[str] = set()
    for row in rows:
        isv = str(row.get("isv") or "").strip()
        if isv:
            heads.add(normalize_word(isv))
        for part in str(row.get("addition") or "").split(","):
            part = part.strip()
            if part:
                heads.add(normalize_word(part))
    return heads


# ---------------------------------------------------------------------------
# Candidate generation
# ---------------------------------------------------------------------------
def build_lemma_forms(lexicon: Lexicon) -> dict[str, list[str]]:
    """Canonical paradigm surface forms per lemma (built once)."""
    lemma_forms: dict[str, list[str]] = {}
    for entry in lexicon.entries:
        lemma_forms.setdefault(normalize_word(entry.lemma), []).append(entry.form)
    for lemma in lemma_forms:
        lemma_forms[lemma] = sorted(set(lemma_forms[lemma]))
    return lemma_forms


def paradigm_forms(lemma_forms: dict[str, list[str]], lemma: str) -> list[str]:
    return lemma_forms.get(normalize_word(lemma), [])


def generate_candidates(form: str, audit: dict, unresolved_rec, lexicon: Lexicon,
                        headwords: set[str],
                        lemma_forms: dict[str, list[str]]) -> dict:
    """Deterministic candidate list for one unresolved form."""
    cands: list[dict] = []
    seen: set[tuple] = set()

    def add(surface: str, lemma: str | None, kind: str, source: str, detail: str,
            structured: dict | None = None):
        key = (normalize_word(surface), kind, source)
        if key in seen:
            return
        seen.add(key)
        cands.append({
            "surface": surface, "lemma": lemma, "kind": kind,
            "source": source, "detail": detail, "structured": structured or {},
        })

    ar = audit.get(form, {})
    res = ar.get("resources", {})

    # 1. Canonical orthographic variant (full-form lexicon ORTHOGRAPHIC_VARIANT)
    #    and the alternative snapshots' orthographic hits (basic_json/slovnik
    #    have the same hit shape with `entries`).
    for key in ("full_form_lexicon", "basic_json", "slovnik"):
        ev = res.get(key, {}).get("evidence")
        if ev != "ORTHOGRAPHIC_VARIANT":
            continue
        for hit in res.get(key, {}).get("hits", []):
            for entry in hit.get("entries", []):
                surface = entry.get("form") or entry.get("isv")
                if not surface:
                    continue
                add(surface, entry.get("lemma"), "orthographic_variant",
                    "canonical_dictionary" if key == "full_form_lexicon" else key,
                    f"{key} form '{surface}' (lemma {entry.get('lemma') or surface}) "
                    f"via {hit.get('matched', 'variant')}",
                    {"matched": hit.get("matched"), "lemma": entry.get("lemma"),
                     "upos": entry.get("upos"), "xpos": entry.get("xpos"),
                     "pos": entry.get("partOfSpeech")})

    # 2. Alternative-resource exact attestation + their orthographic variants
    for key, resname in (("hunspell", "hunspell isv.dic"),
                         ("interslavicfreq", "interslavicfreq wordlist"),
                         ("slovnik", "slovnik snapshot")):
        ev = res.get(key, {}).get("evidence")
        if ev == "EXACT_FORM":
            hits = res.get(key, {}).get("hits", [])
            detail = f"attested verbatim in {resname}"
            structured = {}
            if key == "hunspell" and hits:
                structured["tags"] = hits[0].get("tags")
            if key == "interslavicfreq" and hits:
                structured["cB"] = hits[0].get("cB")
                structured["wordlist"] = hits[0].get("wordlist")
            add(form, None, "alternative_resource", key, detail, structured)
        elif ev == "ORTHOGRAPHIC_VARIANT":
            for hit in res.get(key, {}).get("hits", []):
                surface = hit.get("form") or form
                lemma = None
                if key == "hunspell":
                    tags = hit.get("tags", "")
                    for tok in tags.split():
                        if tok.startswith("st:"):
                            lemma = tok[3:]
                elif key == "interslavicfreq":
                    # matched field carries the attested surface, e.g.
                    # "diacritic-stripped:bratri" -> "bratri"
                    matched = hit.get("matched", "")
                    if ":" in matched:
                        surface = matched.split(":", 1)[1]
                add(surface, lemma, "orthographic_variant", key,
                    f"{resname} form '{surface}' via {hit.get('matched', 'variant')}",
                    {"matched": hit.get("matched"), "tags": hit.get("tags"),
                     "cB": hit.get("cB")})

    # 3. Morphology-derived: candidate lemmas that are canonical headwords.
    #    Supplied ONLY when no orthographic/alternative-resource evidence
    #    exists for the form: where strong evidence exists the attested/canonical
    #    forms are the precise candidates, and prefix-matched lemmas on top of
    #    them would only add noise (e.g. `rekla` -> `reklama`). Where morphology
    #    is the only signal, the canonical-lemma pool is the defensible source.
    #    Prefix/suffix entries (e.g. `pra-`) are excluded: they are not free
    #    words an LLM should be invited to use. Lemmas must be morphologically
    #    close to the form: some paradigm form shares a >=5-char prefix with it
    #    (>=3 for short forms).
    has_strong_evidence = any(
        a["kind"] in ("orthographic_variant", "alternative_resource")
        for a in cands)
    raw_pool = {c for c in (unresolved_rec.get("candidates") or [])
                if normalize_word(c) in headwords
                and not c.startswith("-") and not c.endswith("-")}
    if not has_strong_evidence:
        min_shared = 5 if len(form) >= 5 else 3
        lemma_pool = sorted(c for c in raw_pool if any(
            normalize_word(f)[:min_shared] == form[:min_shared]
            for f in paradigm_forms(lemma_forms, c)))
        for lemma in lemma_pool[:MAX_ALTERNATIVES]:
            forms = paradigm_forms(lemma_forms, lemma)
            if not forms:
                continue
            n = len(forms)
            add(lemma, lemma, "morphology_derived", "js_morphology",
                f"canonical dictionary lemma '{lemma}'; paradigm generated by "
                f"{MORPHOLOGY_PACKAGE} ({n} form{'s' if n != 1 else ''})",
                {"lemma": lemma, "generated_form_count": n,
                 "example_forms": forms[:5]})

    # 4. Canonical dictionary exact hit (defensive; a C-form rarely triggers)
    if normalize_word(form) in headwords:
        add(form, form, "canonical_dictionary", "canonical_dictionary",
            f"canonical headword '{form}'", {})

    # cap deterministically (sorted by (kind priority, surface))
    kind_rank = {"canonical_dictionary": 0, "orthographic_variant": 1,
                 "alternative_resource": 2, "morphology_derived": 3}
    cands.sort(key=lambda c: (kind_rank.get(c["kind"], 9),
                              normalize_word(c["surface"])))
    cands = cands[:MAX_ALTERNATIVES]

    has_candidate = bool(cands)
    return {"form": form, "has_candidate": has_candidate,
            "alternatives": cands}


# ---------------------------------------------------------------------------
# Stratified pilot selection
# ---------------------------------------------------------------------------
def assign_stratum(info: dict) -> str | None:
    """Deterministic primary stratum for a form."""
    if info["name_family"] or info["special_reason"]:
        return None                    # names/special are preserved, not revised
    if info["ortho_candidates"]:
        return "ortho"
    if info["resource_candidates"]:
        return "resource"
    if info["morph_candidates"]:
        return "morphology"
    return None


def _revisable(forms: list[dict]) -> list[dict]:
    """Forms that are legitimate revision targets (exclude names/special)."""
    return [f for f in forms
            if not f["name_family"] and not f["special_reason"]]


def select_pilot(forms: list[dict]) -> dict[str, list[str]]:
    """Deterministic stratified pick. Each form lands in one stratum or none."""
    picked: dict[str, list[str]] = {k: [] for k in STRATUM_CAPS}
    used: set[str] = set()
    revisable = _revisable(forms)

    # first pass: evidence-based strata
    for stratum in ("ortho", "resource", "morphology"):
        eligible = [f for f in revisable if assign_stratum(f) == stratum
                    and f["form"] not in used]
        eligible.sort(key=lambda f: (-f["total_frequency"], f["form"]))
        for f in eligible[:STRATUM_CAPS[stratum]]:
            picked[stratum].append(f["form"])
            used.add(f["form"])

    # second pass: remaining forms by frequency / sharedness
    remaining = [f for f in revisable if f["form"] not in used]
    remaining.sort(key=lambda f: (-f["total_frequency"], f["form"]))
    for f in remaining[:STRATUM_CAPS["high_freq"]]:
        picked["high_freq"].append(f["form"])
        used.add(f["form"])

    rem2 = [f for f in remaining if f["form"] not in used]
    shared = sorted((f for f in rem2 if f["model_count"] >= 2),
                    key=lambda f: (-f["total_frequency"], f["form"]))
    for f in shared[:STRATUM_CAPS["shared"]]:
        picked["shared"].append(f["form"])
        used.add(f["form"])

    rem3 = [f for f in rem2 if f["form"] not in used]
    specific = sorted((f for f in rem3 if f["model_count"] == 1),
                      key=lambda f: (-f["total_frequency"], f["form"]))
    for f in specific[:STRATUM_CAPS["specific"]]:
        picked["specific"].append(f["form"])
        used.add(f["form"])

    rem4 = [f for f in rem3 if f["form"] not in used]
    no_cand = sorted((f for f in rem4 if not f["has_candidate"]),
                     key=lambda f: (-f["total_frequency"], f["form"]))
    for f in no_cand[:STRATUM_CAPS["no_candidate"]]:
        picked["no_candidate"].append(f["form"])
        used.add(f["form"])

    return picked


# ---------------------------------------------------------------------------
# Prompt rendering
# ---------------------------------------------------------------------------
def render_table(picked: dict[str, list[str]], info_by_form: dict[str, dict]) -> str:
    lines = ["## Words to revise — suggested Interslavic alternatives",
             "", "Word — suggested alternatives — evidence",
             "(alternatives are supplied with their deterministic provenance;",
             " use them only where they fit the context and in grammatically",
             " appropriate forms).", ""]
    for stratum in ("ortho", "resource", "morphology", "high_freq",
                    "shared", "specific", "no_candidate"):
        for form in picked[stratum]:
            info = info_by_form[form]
            lines.append(f"- Word: «{form}»  (occurs {info['total_frequency']}× in "
                         f"the original; unresolved in {info['model_count']} model(s))")
            if info["alternatives"]:
                lines.append("  Suggested alternatives:")
                for alt in info["alternatives"]:
                    lines.append(f"    · {alt['surface']}  — {alt['kind'].replace('_', ' ')}; "
                                 f"{alt['detail']}")
            else:
                lines.append("  No defensible candidate found — leave unchanged.")
            lines.append("")
    return "\n".join(lines)


def build_prompt(template_text: str, table: str, original_text: str) -> str:
    return (template_text
            .replace("[CANDIDATE TABLE]", table)
            .replace("[COMPLETE ORIGINAL TRANSLATION]", original_text))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-run", required=True,
                        help="EXP-001 run id under experiments/exp001-baseline/outputs/")
    args = parser.parse_args(argv)

    source_run_id = args.source_run
    run = load_run(source_run_id)

    print(f"[load] source run {source_run_id}: "
          f"{len(run['unresolved'])} unresolved records")
    audit = load_audit()
    print(f"[load] cross-resource audit: {len(audit)} forms")

    lex = Lexicon.load_tsv(LEXICON_TSV)
    headwords = load_headwords()
    lemma_forms = build_lemma_forms(lex)
    print(f"[load] lexicon {len(lex)} entries; {len(headwords)} headwords; "
          f"{len(lemma_forms)} lemmas indexed")

    # distinct unresolved forms in the source run
    by_form: dict[str, dict] = {}
    for rec in run["unresolved"]:
        f = rec["normalized"]
        by_form.setdefault(f, {
            "form": f, "count": 0, "model_count": 0, "candidates": [],
            "sentence": rec.get("sentence"),
        })
        by_form[f]["count"] += 1
        by_form[f]["candidates"] = rec.get("candidates") or []

    # cross-model counts from the audit; names/special from the audit, with the
    # pilot's superset detection as a fallback (audit patterns miss inflected
    # name forms such as `przemysłavy`).
    for f, info in by_form.items():
        ar = audit.get(f, {})
        info["model_count"] = ar.get("model_count", 0)
        info["name_family"] = ar.get("name_family")
        info["special_reason"] = ar.get("special_reason")
        if not info["name_family"] and not info["special_reason"]:
            info["name_family"], info["special_reason"] = name_or_special(f)
        info["total_frequency"] = ar.get("total_frequency") or info["count"]

    forms = []
    for f, info in by_form.items():
        cand = generate_candidates(f, audit, info, lex, headwords, lemma_forms)
        info.update(cand)
        info["ortho_candidates"] = any(
            a["kind"] == "orthographic_variant" for a in info["alternatives"])
        info["resource_candidates"] = any(
            a["kind"] == "alternative_resource" for a in info["alternatives"])
        info["morph_candidates"] = any(
            a["kind"] == "morphology_derived" for a in info["alternatives"])
        forms.append(info)

    picked = select_pilot(forms)
    info_by_form = {f["form"]: f for f in forms}
    selected = [f for stratum in picked for f in picked[stratum]]

    print("\n[pilot selection]")
    for stratum, forms_ in picked.items():
        print(f"  {stratum:14s} ({len(forms_):2d}): {', '.join(forms_[:6])}")

    original_text = run["original"].decode("utf-8")
    table = render_table(picked, info_by_form)
    prompt = build_prompt(TEMPLATE.read_text(encoding="utf-8"), table, original_text)

    pilot_run_id = f"exp002__{source_run_id}"
    out_dir = INPUT_DIR / pilot_run_id
    if out_dir.exists():
        print(f"error: {out_dir} already exists; refusing to overwrite an input package")
        return 2
    out_dir.mkdir(parents=True, exist_ok=True)

    (out_dir / "original.txt").write_bytes(run["original"])
    (out_dir / "prompt.txt").write_text(prompt, encoding="utf-8")

    candidates_payload = {
        "selected_forms": [
            {
                "form": info_by_form[f]["form"],
                "total_frequency": info_by_form[f]["total_frequency"],
                "model_count": info_by_form[f]["model_count"],
                "stratum": next(s for s, fl in picked.items() if f in fl),
                "name_family": info_by_form[f]["name_family"],
                "special_reason": info_by_form[f]["special_reason"],
                "sentence_context": info_by_form[f]["sentence"],
                "alternatives": info_by_form[f]["alternatives"],
            }
            for f in selected
        ],
        "selection_strata": picked,
        "candidate_kinds": {
            "canonical_dictionary": "surface form / lemma is canonical (basic.json/lexicon)",
            "orthographic_variant": "canonical/attested form via diacritic/fold variant",
            "alternative_resource": "exact attestation in hunspell / interslavicfreq / slovnik",
            "morphology_derived": "canonical dictionary lemma with generated paradigm",
        },
        "note": "Evidence-only candidates; no linguistic judgment; no invented lexical candidates.",
    }
    (out_dir / "candidates.json").write_text(
        json.dumps(candidates_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    manifest = load_manifest() or {}
    meta = {
        "experiment_id": "exp002-pilot",
        "pilot_run_id": pilot_run_id,
        "prepared_at": datetime.now(timezone.utc).isoformat(),
        "prepared_by": "scripts/prepare_exp002_pilot.py",
        "source": {
            "exp001_run_id": source_run_id,
            "exp001_output_sha256": run["meta"]["output_sha256"],
            "exp001_display_name": run["meta"].get("display_name"),
            "exp001_model": run["meta"].get("model"),
        },
        "prompt": {
            "template": str(TEMPLATE),
            "file": str(out_dir / "prompt.txt"),
            "sha256": sha256_bytes(prompt.encode("utf-8")),
            "bytes": len(prompt.encode("utf-8")),
        },
        "original": {
            "file": str(out_dir / "original.txt"),
            "sha256": sha256_bytes(run["original"]),
            "bytes": len(run["original"]),
        },
        "candidates": {
            "file": str(out_dir / "candidates.json"),
            "selected_forms": len(selected),
            "forms_with_candidates": sum(
                1 for f in selected if info_by_form[f]["has_candidate"]),
            "forms_without_candidates": sum(
                1 for f in selected if not info_by_form[f]["has_candidate"]),
            "alternatives_total": sum(
                len(info_by_form[f]["alternatives"]) for f in selected),
        },
        "evaluation": {
            "evaluator_commit": git_commit(),
            "dictionary_manifest": manifest,
            "morphology_package": MORPHOLOGY_PACKAGE,
            "morphology_version": morphology_version(),
            "same_evaluator_as_exp001": True,
        },
        "resources_used": {
            "canonical_dictionary": {
                "basic.json": str(BASIC_JSON),
                "lexicon.tsv": str(LEXICON_TSV),
                "note": "headwords + addition variants for orthographic-variant "
                        "candidates and the canonical-lemma pool",
            },
            "alternative_resources": {
                "hunspell_isv.dic": "exact-form and orthographic evidence "
                                    "(full-form tags recorded per candidate)",
                "interslavicfreq_wordlists": "exact-form and orthographic "
                                             "evidence (cB frequency recorded)",
                "slovnik_snapshot": "exact-form and orthographic evidence "
                                    "(same-lineage snapshot; never promoted)",
            },
            "morphology": {
                "engine": MORPHOLOGY_PACKAGE,
                "version": morphology_version(),
                "note": "canonical-lemma paradigms as supporting evidence for "
                        "morphology_derived candidates",
            },
            "task005_evidence": {
                "cross_resource_audit": str(AUDIT_JSON),
                "note": "post-hoc cross-resource evidence; used only as "
                        "attestation evidence, never as a lexical source",
            },
        },
        "revision": {
            "model": "unknown", "model_version": "unknown",
            "provider": "unknown", "generation_date": "unknown",
            "status": "awaiting_external_execution",
        },
        "layout": {
            "revised_output": str(EXP002 / "outputs" / pilot_run_id / "revised.txt"),
            "instructions": "Send prompt.txt to an LLM; save returned text "
                            "byte-for-byte as the revised_output path; then run "
                            "scripts/compare_exp002.py.",
        },
    }
    (out_dir / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n[write] {out_dir.relative_to(ROOT)}")
    print("  original.txt, candidates.json, prompt.txt, meta.json")
    print(f"\n[pilot] {len(selected)} selected forms; "
          f"{meta['candidates']['forms_with_candidates']} with candidates, "
          f"{meta['candidates']['forms_without_candidates']} without")
    print("\nNext: send prompt.txt to an LLM externally; save the returned text "
          "byte-for-byte; run scripts/compare_exp002.py.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
