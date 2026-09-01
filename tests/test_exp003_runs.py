"""EXP-003 — run collection / integrity / comparison-logic tests.

Covers: byte-for-byte collect with immutability, refusal to overwrite,
meta.json hashing, verify's tamper detection, and the pure comparison
functions (transitions, candidate usage, name-excluded diagnostics,
non-supplied vocabulary breakdown).
"""
import importlib.util
import json
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"


@pytest.fixture(scope="module")
def run_mod():
    spec = importlib.util.spec_from_file_location(
        "run_exp003_pilot", SCRIPTS / "run_exp003_pilot.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def cmp_mod():
    spec = importlib.util.spec_from_file_location(
        "compare_exp003", SCRIPTS / "compare_exp003.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture()
def setup(run_mod, tmp_path, monkeypatch):
    """A minimal plan + operator prompt + source, in a temp outputs dir."""
    outputs = tmp_path / "outputs"
    prompts = tmp_path / "operator-prompts"
    outputs.mkdir()
    prompts.mkdir()
    monkeypatch.setattr(run_mod, "OUTPUTS_DIR", outputs)
    monkeypatch.setattr(run_mod, "OPERATOR_PROMPTS", prompts)
    prompt_text = "PROMPT FOR CHATGPT A"
    prompt_sha = run_mod.sha256_bytes(prompt_text.encode("utf-8"))
    (prompts / "01-chatgpt-A.md").write_text(prompt_text, encoding="utf-8")
    (outputs / "plan.json").write_text(json.dumps({
        "runs": [{
            "run_id": "2099-01-01__openai__chatgpt__unknown__a",
            "model": "chatgpt", "provider": "openai", "model_version": "unknown",
            "condition": "A",
            "prompt_file": "01-chatgpt-A.md",
            "prompt_sha256": prompt_sha,
            "source_sha256": "s" * 64,
            "scaffold_sha256": None,
        }],
    }), encoding="utf-8")
    return tmp_path


def _token(surface, cls, broader=False, **kw):
    d = {"token": surface, "normalized": surface.lower(),
         "is_lexical": True, "classification": cls,
         "broader_supported": broader}
    d.update(kw)
    return d


# ---------------------------------------------------------------------------
# Collect / integrity
# ---------------------------------------------------------------------------


def test_collect_copies_byte_for_byte_and_hashes(run_mod, setup):
    src = setup / "reply.txt"
    src.write_bytes(b"Prvnyj tekst.\n" * 3)
    rc = run_mod.run_collect("2099-01-01__openai__chatgpt__unknown__a",
                             src, "2099-01-01", "chatgpt", "openai", "unknown")
    assert rc == 0
    dst = setup / "outputs" / "2099-01-01__openai__chatgpt__unknown__a" \
        / "output.txt"
    assert dst.read_bytes() == src.read_bytes()
    meta = json.loads((dst.parent / "meta.json").read_text(encoding="utf-8"))
    assert meta["condition"] == "A"
    assert meta["model"] == "chatgpt"
    assert meta["prompt"]["sha256"] == run_mod.sha256_bytes(
        b"PROMPT FOR CHATGPT A")
    assert meta["source"]["sha256"] == "s" * 64
    assert meta["output"]["sha256"] == \
        run_mod.sha256_bytes(src.read_bytes())


def test_collect_refuses_overwrite(run_mod, setup):
    src = setup / "reply.txt"
    src.write_bytes(b"one\n")
    run_id = "2099-01-01__openai__chatgpt__unknown__a"
    assert run_mod.run_collect(run_id, src, "2099-01-01", "chatgpt",
                               "openai", "unknown") == 0
    src.write_bytes(b"two\n")
    assert run_mod.run_collect(run_id, src, "2099-01-01", "chatgpt",
                               "openai", "unknown") == 2


def test_verify_detects_tampering(run_mod, setup):
    src = setup / "reply.txt"
    src.write_bytes(b"intact\n")
    run_id = "2099-01-01__openai__chatgpt__unknown__a"
    assert run_mod.run_collect(run_id, src, "2099-01-01", "chatgpt",
                               "openai", "unknown") == 0
    plan_entry = json.loads(
        (setup / "outputs" / "plan.json").read_text(encoding="utf-8")
    )["runs"][0]

    import importlib.util as _ilu
    spec = _ilu.spec_from_file_location(
        "verify_exp003_runs", SCRIPTS / "verify_exp003_runs.py")
    vmod = _ilu.module_from_spec(spec)
    spec.loader.exec_module(vmod)
    vmod.OUTPUTS_DIR = setup / "outputs"
    vmod.OPERATOR_PROMPTS = setup / "operator-prompts"

    assert vmod.verify_run(run_id, plan_entry) == []
    # tamper with the raw output
    (setup / "outputs" / run_id / "output.txt").write_bytes(b"TAMPERED\n")
    errors = vmod.verify_run(run_id, plan_entry)
    assert any("sha256 mismatch" in e for e in errors)


def test_verify_flags_missing_collection(run_mod, setup):
    import importlib.util as _ilu
    spec = _ilu.spec_from_file_location(
        "verify_exp003_runs", SCRIPTS / "verify_exp003_runs.py")
    vmod = _ilu.module_from_spec(spec)
    spec.loader.exec_module(vmod)
    vmod.OUTPUTS_DIR = setup / "outputs"
    vmod.OPERATOR_PROMPTS = setup / "operator-prompts"
    errors = vmod.verify_run(
        "2099-01-01__openai__chatgpt__unknown__a",
        json.loads((setup / "outputs" / "plan.json").read_text(
            encoding="utf-8"))["runs"][0])
    assert "output.txt missing" in errors


def test_collect_records_status_parameters_and_note(run_mod, setup):
    """Failed/partial runs are preserved with a documented status (D-023)."""
    src = setup / "error.txt"
    src.write_bytes("Przepraszamy, Bielik ma chwilowe problemy.\n".encode())
    run_id = "2099-01-01__openai__chatgpt__unknown__a"
    rc = run_mod.run_collect(
        run_id, src, "2026-09-01", "chatgpt", "openai", "GPT-5.6 Luna",
        generation_parameters="thinking OFF",
        status="failed_external_output",
        note="Service error page; no translation content.")
    assert rc == 0
    meta = json.loads(
        (setup / "outputs" / run_id / "meta.json").read_text(
            encoding="utf-8"))
    assert meta["status"] == "failed_external_output"
    assert meta["generation_parameters"] == "thinking OFF"
    assert meta["model_version"] == "GPT-5.6 Luna"
    assert meta["generation_date"] == "2026-09-01"
    assert "no translation content" in meta["note"]
    # default status is the normal complete-run status
    src2 = setup / "ok.txt"
    src2.write_bytes(b"Full translation.\n")
    assert run_mod.run_collect(run_id, src2, "2026-09-01", "chatgpt",
                               "openai", "GPT-5.6 Luna") == 2  # refuse overwrite


# ---------------------------------------------------------------------------
# Comparison logic (pure functions)
# ---------------------------------------------------------------------------


def test_transition_stats_matrix_and_regressions(cmp_mod):
    before = [_token("brat", "A"), _token("woda", "C"), _token("sestra", "B")]
    after = [_token("brat", "A"), _token("vodica", "A"), _token("sestra", "B")]
    pairs = cmp_mod.align_lexical(before, after)
    matrix, detail = cmp_mod.transition_stats(pairs)
    assert matrix["A→A"] == 1
    assert matrix["B→B"] == 1
    assert matrix["C→A"] == 1
    assert "C_to_A" in detail
    assert detail["C_to_A"][0]["form"] == "woda"
    assert detail["C_to_A"][0]["replacement"] == "vodica"


def test_candidate_usage_surface_proxy(cmp_mod):
    supplied = {"brat", "voda", "sestra"}
    tokens = [_token("brat", "A"), _token("voda", "C"), _token("mųž", "C")]
    usage = cmp_mod.candidate_usage(tokens, supplied)
    assert usage["supplied_surfaces_total"] == 3
    assert usage["supplied_surfaces_present_in_output"] == 2
    assert usage["supplied_surfaces_accepted_by_evaluator"] == 1
    assert "brat" in usage["accepted_surfaces"]
    assert "adoption_note" in usage


def test_name_excluded_diagnostics(cmp_mod):
    names = {"tomek", "bronisława"}
    tokens = [
        _token("brat", "A"),
        _token("Tomek", "C"),
        _token("voda", "C"),
        _token("Bronisława", "A"),
    ]
    ne = cmp_mod.name_excluded_diagnostics(tokens, names)
    # 'Tomek' (name) and 'Bronisława' (name, though classified A) excluded.
    assert ne["excluded_name_tokens"] == 2
    assert ne["kept_tokens"] == 2
    assert ne["canonical_supported_tokens_excl_names"] == 1
    assert ne["unresolved_rate_excl_names"] == 0.5
    assert "new" in ne["label"].lower()


def test_invented_forms_categories(cmp_mod):
    supplied = {"brat"}
    names = {"tomek"}
    tokens = [
        _token("brat", "A"),
        _token("sestra", "A"),
        _token("voda", "C", broader=True),
        _token("xyz", "C"),
        _token("Tomek", "C"),
    ]
    inv = cmp_mod.invented_forms(tokens, supplied, names)
    cats = inv["categories"]
    assert cats["supplied_scaffold_vocabulary"] == ["brat"]
    assert cats["canonical_independently_generated"] == ["sestra"]
    assert cats["broader_resource_supported"] == ["voda"]
    assert cats["unresolved"] == ["xyz"]
    assert cats["proper_name_like"] == ["tomek"]
    assert "not a correctness oracle" in inv["note"]


def test_pairwise_deltas(cmp_mod):
    first = {
        "run_id": "r1", "condition": "A",
        "metrics": {"total_tokens": 10, "canonical_supported_tokens": 5,
                    "canonical_coverage": 0.5,
                    "broader_resource_supported_coverage": 0.6,
                    "unresolved_tokens": 4, "unresolved_rate": 0.4},
        "structure": {"paragraphs": 3, "dialogue_lines": 1},
    }
    second = {
        "run_id": "r2", "condition": "B",
        "metrics": {"total_tokens": 12, "canonical_supported_tokens": 8,
                    "canonical_coverage": 0.666666,
                    "broader_resource_supported_coverage": 0.75,
                    "unresolved_tokens": 2, "unresolved_rate": 0.166666},
        "structure": {"paragraphs": 3, "dialogue_lines": 2},
    }
    p = cmp_mod.pairwise(first, second,
                         first_tokens=[_token("brat", "A")],
                         second_tokens=[_token("brat", "A"),
                                        _token("sestra", "A")])
    assert p["deltas"]["lexical_tokens"] == 2
    assert p["deltas"]["canonical_supported_tokens"] == 3
    assert p["deltas"]["unresolved_tokens"] == -2
    assert p["deltas"]["canonical_coverage"] == pytest.approx(0.166666, abs=1e-4)
    assert p["note"]


def test_partition_runs_excludes_failed_and_partial(cmp_mod, tmp_path,
                                                   monkeypatch):
    """Runs with a documented non-complete status are excluded from the
    quantitative comparison but preserved with their reason."""
    outputs = tmp_path / "outputs"
    for run_id, status, cond in [
        ("2099-01-01__openai__chatgpt__unknown__a", "collected_external_output", "A"),
        ("2099-01-01__unknown__bielik__unknown__b", "collected_partial_output", "B"),
        ("2099-01-01__unknown__bielik__unknown__c", "failed_external_output", "C"),
    ]:
        d = outputs / run_id
        d.mkdir(parents=True)
        (d / "output.txt").write_bytes(b"x")
        (d / "meta.json").write_text(json.dumps({
            "status": status,
            "condition": cond,
            "model": "bielik" if "bielik" in run_id else "chatgpt",
            "note": "truncated at act 3" if status == "collected_partial_output"
                    else "echo of the prompt, no translation"
                    if status == "failed_external_output" else "",
        }), encoding="utf-8")
    monkeypatch.setattr(cmp_mod, "OUTPUTS_DIR", outputs)

    complete, excluded = cmp_mod.partition_runs(sorted(
        p.name for p in outputs.iterdir()))
    assert complete == ["2099-01-01__openai__chatgpt__unknown__a"]
    assert set(excluded) == {
        "2099-01-01__unknown__bielik__unknown__b",
        "2099-01-01__unknown__bielik__unknown__c",
    }
    rec = excluded["2099-01-01__unknown__bielik__unknown__b"]
    assert rec["status"] == "collected_partial_output"
    assert rec["excluded_from_quantitative_comparison"] is True
    assert "truncated" in rec["reason"]


# ---------------------------------------------------------------------------
# Blinded human-review artifact (DESIGN §11, Task 012)
# ---------------------------------------------------------------------------


def _make_analyses() -> dict[str, dict]:
    """8 complete-run analyses (chatgpt + claude, A-D) with run ids."""
    analyses = {}
    for model in ("chatgpt", "claude"):
        provider = "openai" if model == "chatgpt" else "anthropic"
        for cond in ("A", "B", "C", "D"):
            rid = f"2099-01-01__{provider}__{model}__unknown__{cond.lower()}"
            analyses[rid] = {"run_id": rid, "model": model,
                             "condition": cond}
    return analyses


def test_human_review_blinding_and_content(cmp_mod, tmp_path, monkeypatch):
    """The review artifact: neutral sets, per-set randomized Version labels,
    byte-exact translations, DESIGN §11 rubric, no model names/metrics."""
    analyses = _make_analyses()
    outputs = tmp_path / "outputs"
    for a in analyses.values():
        d = outputs / a["run_id"]
        d.mkdir(parents=True)
        # distinctive but neutral content so byte-exactness is really checked
        (d / "output.txt").write_text(
            f"Story version {a['condition']} of the set.\n",
            encoding="utf-8")
    monkeypatch.setattr(cmp_mod, "OUTPUTS_DIR", outputs)

    doc, key = cmp_mod.render_human_pairs(analyses)

    # determinism: same seed -> identical artifact
    doc2, key2 = cmp_mod.render_human_pairs(analyses)
    assert doc == doc2
    assert key == key2

    # exactly two neutral sets, four versions each
    assert doc.count("## Set ") == 2
    for set_name in ("Set 1", "Set 2"):
        section = doc.split(f"## {set_name}\n")[1].split("## Set ")[0] \
            if set_name == "Set 1" else doc.split(f"## {set_name}\n")[1]
        assert section.count("### Version ") == 4

    # no model identities, no automatic metrics in the review document.
    # ("coverage" appears only in the instruction NOT to consult coverage
    # numbers, which is the blinding reminder, not a leaked metric.)
    low = doc.lower()
    for bad in ("chatgpt", "claude", "bielik", "canonical", "broader",
                "unresolved", "regression", "candidate", "invented"):
        assert bad not in low, f"blinding leak: {bad!r}"
    assert "%" not in doc
    assert "coverage" not in doc or \
        low.count("do not consult any automatic metric, coverage number") == 1

    # key: every set maps 4 conditions to a permutation of Version 1..4,
    # and the model/run are recorded only here
    assert len(key) == 2
    for entry in key:
        assert entry["model"] in ("chatgpt", "claude")
        labels = entry["blinded_labels"]
        assert sorted(labels.values()) == \
            [f"Version {i}" for i in range(1, 5)]
        assert sorted(entry["runs"]) == ["A", "B", "C", "D"]
        # presentation order is a permutation of the conditions
        assert sorted(entry["presentation_order"]) == ["A", "B", "C", "D"]
        # Version 1 is NOT necessarily condition A (blinding worked)
        assert entry["presentation_order"] != ["A", "B", "C", "D"] or \
            entry["set"] != "Set 1"  # at least one set must be shuffled

    # translations embedded byte-exact (modulo terminal newlines)
    for entry in key:
        for cond, label in entry["blinded_labels"].items():
            raw = (outputs / entry["runs"][cond] / "output.txt") \
                .read_text(encoding="utf-8")
            assert f"### {label}" in doc
            assert raw.rstrip("\n") in doc
            assert f"Story version {cond} of the set." in doc

    # DESIGN §11 rubric present verbatim
    for q in cmp_mod._RUBRIC_QUESTIONS:
        assert q in doc
    assert "Preference ordering" in doc
    assert "Best:" in doc and "Worst:" in doc
    # post-unblinding scaffold question, explicitly separated
    assert "# PART 2" in doc
    assert "does the scaffolded text feel constrained by the" in doc
    assert "# Recording" in doc


def test_human_review_excludes_incomplete_models(cmp_mod, tmp_path,
                                                monkeypatch):
    """Bielik (incomplete) never appears in the review — only complete runs."""
    analyses = _make_analyses()
    # a Bielik A analysis would exist for a partial run; ensure it is ignored
    analyses["2099-01-01__unknown__bielik__unknown__a"] = {
        "run_id": "2099-01-01__unknown__bielik__unknown__a",
        "model": "bielik", "condition": "A"}
    outputs = tmp_path / "outputs"
    for a in analyses.values():
        d = outputs / a["run_id"]
        d.mkdir(parents=True)
        (d / "output.txt").write_text("x\n", encoding="utf-8")
    monkeypatch.setattr(cmp_mod, "OUTPUTS_DIR", outputs)

    doc, key = cmp_mod.render_human_pairs(analyses)
    assert "bielik" not in doc.lower()
    assert len(key) == 2
    assert all(e["model"] in ("chatgpt", "claude") for e in key)
