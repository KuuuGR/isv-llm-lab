"""EXP-003 — operator-prompt packaging tests (self-contained).

Covers: 12 files (4 conditions × 3 models), self-contained content,
condition separation (A has no scaffold block; B one candidate; C/D
alternatives; D grammar note), cross-model prompt control (identical prompt
bodies for the same condition), deterministic regeneration, and the manifest.
"""
import importlib.util
import json
import re
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"

_SOURCE = (
    "Opowieść o Słów.\n"
    "Dom i siostra.\n"
    "KONIEC\n"
)
_SCAFFOLD_B = (
    "Opowieść       → [povědka]\n"
    "Dom            → [dom]\n"
)
_SCAFFOLD_C = (
    "Opowieść       → [povědka, pověsť]\n"
    "Dom            → [dom, budova]\n"
)
_SCAFFOLD_D = (
    "Opowieść       → [povědka, pověsť]  (f.)\n"
    "Dom            → [dom, budova]  (m.; e.g. dom, domu)\n"
)


@pytest.fixture(scope="module")
def pkg_mod():
    spec = importlib.util.spec_from_file_location(
        "package_exp003_prompts", SCRIPTS / "package_exp003_prompts.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture()
def setup(pkg_mod, tmp_path, monkeypatch):
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    (input_dir / "source.txt").write_text(_SOURCE, encoding="utf-8")
    scaf = tmp_path / "scaffolds" / "op-pl"
    scaf.mkdir(parents=True)
    (scaf / "scaffold_B.txt").write_text(_SCAFFOLD_B, encoding="utf-8")
    (scaf / "scaffold_C.txt").write_text(_SCAFFOLD_C, encoding="utf-8")
    (scaf / "scaffold_D.txt").write_text(_SCAFFOLD_D, encoding="utf-8")
    monkeypatch.setattr(pkg_mod, "EXP", tmp_path)
    monkeypatch.setattr(pkg_mod, "INPUT_DIR", input_dir)
    monkeypatch.setattr(pkg_mod, "SCAFFOLD_DIR", scaf)
    # copy the committed template into the temp EXP for self-containedness
    real_template = SCRIPTS.parent / "experiments" / "exp003-scaffold" \
        / "prompt_template.txt"
    (tmp_path / "prompt_template.txt").write_text(
        real_template.read_text(encoding="utf-8"), encoding="utf-8")
    return tmp_path


def pack(pkg_mod, setup, out_name="out"):
    out = setup / out_name
    rc = pkg_mod.main(["--out", str(out)])
    assert rc == 0
    return out


def test_twelve_files_named_correctly(pkg_mod, setup):
    out = pack(pkg_mod, setup)
    files = sorted(p.name for p in out.glob("*.md"))
    models = ["chatgpt"] * 4 + ["claude"] * 4 + ["bielik"] * 4
    conds = ["A", "B", "C", "D"] * 3
    expected = [f"{n:02d}-{model}-{cond}.md"
                for n, (model, cond) in enumerate(zip(models, conds), start=1)]
    assert files == expected


def test_prompt_is_self_contained(pkg_mod, setup):
    out = pack(pkg_mod, setup)
    text = (out / "02-chatgpt-B.md").read_text(encoding="utf-8")
    assert "Experiment ID: EXP-003" in text
    assert "Target model: ChatGPT" in text
    assert "Condition: B" in text
    assert _SOURCE.splitlines()[1] in text  # the story is embedded
    assert "COPY THIS ENTIRE FILE INTO ChatGPT" in text


def test_condition_separation(pkg_mod, setup):
    out = pack(pkg_mod, setup)
    a = (out / "01-chatgpt-A.md").read_text(encoding="utf-8")
    b = (out / "02-chatgpt-B.md").read_text(encoding="utf-8")
    c = (out / "03-chatgpt-C.md").read_text(encoding="utf-8")
    d = (out / "04-chatgpt-D.md").read_text(encoding="utf-8")
    # A has no scaffold block.
    assert "Lexical scaffold" not in a
    assert "Lexical scaffold" in b
    # B embeds the single-candidate scaffold.
    assert "→ [dom]" in b
    assert "→ [dom, budova]" not in b
    # C adds alternatives.
    assert "→ [dom, budova]" in c
    assert "choose the one that best fits" in c
    # D adds grammar note.
    assert "→ [dom, budova]  (m.; e.g. dom, domu)" in d
    assert "Parenthesised annotations" in d
    assert "Parenthesised annotations" not in c


def test_scaffold_block_identical_across_models(pkg_mod, setup):
    """Prompt control: for the same condition, the scaffold block and rules
    are byte-identical across models; only model-name lines differ."""
    out = pack(pkg_mod, setup)

    b_chatgpt = (out / "02-chatgpt-B.md").read_text(encoding="utf-8")
    b_claude = (out / "06-claude-B.md").read_text(encoding="utf-8")

    # Extract from '## Lexical scaffold' to '## Source text'
    def scaffold_block(text):
        start = text.index("## Lexical scaffold")
        end = text.index("## Source text")
        return text[start:end]

    assert scaffold_block(b_chatgpt) == scaffold_block(b_claude)

    # The rules section is identical too.
    def rules(text):
        start = text.index("## Rules")
        end = text.index("## Lexical scaffold")
        return text[start:end]

    assert rules(b_chatgpt) == rules(b_claude)


def test_manifest_records_hashes_and_metadata(pkg_mod, setup):
    out = pack(pkg_mod, setup)
    manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["experiment_id"] == "exp003"
    assert len(manifest["files"]) == 12
    entry = manifest["files"]["01-chatgpt-A.md"]
    assert entry["model"] == "chatgpt"
    assert entry["provider"] == "openai"
    assert entry["model_version"] == "unknown"
    assert entry["condition"] == "A"
    assert len(entry["prompt_text_sha256"]) == 64
    assert len(entry["output_sha256"]) == 64
    assert len(manifest["source"]["sha256"]) == 64
    assert set(manifest["scaffold_blocks"]) == {"B", "C", "D"}


def test_regeneration_is_byte_identical(pkg_mod, setup):
    out1 = pack(pkg_mod, setup, "out1")
    out2 = pack(pkg_mod, setup, "out2")
    for f1 in sorted(out1.iterdir()):
        f2 = out2 / f1.name
        assert f1.read_bytes() == f2.read_bytes(), f1.name
