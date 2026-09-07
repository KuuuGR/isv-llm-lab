"""EXP-004 Phase 2A — three-register corpus composition tests (SODA Task 020).

Asserts, against the real local corpus artifacts under
experiments/exp004-modelscreen/phase2a/corpus/:

- the combined corpus has exactly three register sections and register 1
  is the unchanged "Tuta historija" excerpt from Task 019;
- register 2 (artistic/poetic) is Latin-script only, free of Cyrillic and
  webpage material, contains all 11 album songs in their original order,
  is deduplicated only for verbatim repeated stanzas/refrains, and
  preserves the original wording (no linguistic normalization);
- register 3 (informative/encyclopedic) is the cleaned running prose of
  the existing Medžuslovjansky Wikipedia article "Sadovničstvo" — an
  authentic retrieved source text, not a project-generated translation;
- the exact combined-corpus hash is pinned and the SAME corpus bytes
  reach every primed msg1 prompt; controls stay corpus-free; msg2 stays
  byte-identical; prompt hashes regenerate deterministically.

All corpus text files are gitignored (author-supplied / not-yet-cleared
sources, see corpus/README.md); these tests run against the local kit.
"""
import importlib.util
import json
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
ROOT = SCRIPTS.parent
CORPUS_DIR = (ROOT / "experiments" / "exp004-modelscreen" / "phase2a"
              / "corpus")

COMBINED = CORPUS_DIR / "phase2a-authentic-isv-corpus.txt"
TUTA = CORPUS_DIR / "tuta-historija-excerpt.txt"
ARTISTIC = CORPUS_DIR / "album-ahoj-slovjani-artistic-isv.txt"
WIKI = CORPUS_DIR / "wiki-sadovnistvo-encyclopedic-isv.txt"
ALBUM_HTML = CORPUS_DIR / "sources" / "album-ahoj-slovjani-teksty-pesnej.html"
WIKI_RAW = CORPUS_DIR / "sources" / "sadovnistvo.wikitext"

TUTA_SHA256 = ("413830fa4ff6aaa8833895a22e7ef1fa5fa3807e5a5a105b7e4050cf7b67a29c")
ARTISTIC_SHA256 = ("7e25a56f67a52976083f625fabf040b6cd5ae399317cb36a59a302a3a52dcacf")
WIKI_SHA256 = ("b03402fef2384730b90a5ab879af78be63b5e6d0e4fa00db4c3c3525844c8345")
COMBINED_SHA256 = ("aaad28e43935a40313585d77a33bfc788d97e8d69b081f9486af74d52ca1a857")
ALBUM_HTML_SHA256 = ("dd1d8492a404f9691da04160b4c833cfc6fce0028a74bb021ac0fc80297a9100")
WIKI_RAW_SHA256 = ("3c789740dad15efe04152b8859a4003c2800ece511f7e96a7141c65fd1f280e1")

DATE = "2099-01-02"

ALBUM_SONGS = [
    "Velerman", "Santiana", "Nikogda Vyše", "Rěka Essekibo",
    "Slovjanske Děvčiny", "Idi, Džoni, Idi", "Ješče Raz!",
    "Primorje Barbari", "Stara Maui", "Morske Opověsti", "Bude Dobro",
]

REGISTER_HEADERS = (
    "=== REGISTER 1: LITERARY / NARRATIVE ===",
    "=== REGISTER 2: ARTISTIC / POETIC ===",
    "=== REGISTER 3: INFORMATIVE / ENCYCLOPEDIC ===",
)

MSG1_HEADING = ("## Reference texts (authentic Medžuslovjansky, "
                "three registers)")
STORY_TITLE = "Opowieść o Słów, Które Były Jak Siostry"


def _sha(path: Path) -> str:
    import hashlib
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def run_mod():
    return _load("run_exp004_phase2a")


@pytest.fixture(scope="module")
def build_mod():
    return _load("build_phase2a_corpus")


@pytest.fixture(scope="module")
def corpus_files():
    return {
        "combined": COMBINED.read_text(encoding="utf-8"),
        "tuta": TUTA.read_text(encoding="utf-8"),
        "artistic": ARTISTIC.read_text(encoding="utf-8"),
        "wiki": WIKI.read_text(encoding="utf-8"),
    }


def _register_block(text: str, n: int) -> str:
    start = text.find(REGISTER_HEADERS[n - 1])
    assert start >= 0, f"missing register {n} header"
    body = text[start + len(REGISTER_HEADERS[n - 1]):]
    if n < 3:
        nxt = text.find(REGISTER_HEADERS[n], start + 1)
        assert nxt >= 0
        body = body[: nxt - (start + len(REGISTER_HEADERS[n - 1]))]
    return body.strip("\n") + "\n"


def _has_cyrillic(text: str) -> bool:
    return any(0x0400 <= ord(c) <= 0x04FF for c in text)


# ---------------------------------------------------------------------------
# combined corpus structure
# ---------------------------------------------------------------------------

def test_combined_corpus_exists_with_pinned_hash(run_mod, corpus_files):
    assert _sha(COMBINED) == COMBINED_SHA256
    # the pinned constant in the run orchestrator matches the file
    assert run_mod.AUTH_CORPUS_SHA256 == COMBINED_SHA256


def test_combined_corpus_three_register_sections_in_order(corpus_files):
    text = corpus_files["combined"]
    positions = [text.find(h) for h in REGISTER_HEADERS]
    assert all(p >= 0 for p in positions)
    assert positions == sorted(positions)
    # headers are metadata lines, immediately followed by a blank line
    for h in REGISTER_HEADERS:
        i = text.find(h)
        assert text[i + len(h): i + len(h) + 2] == "\n\n"


def test_register1_is_the_unchanged_literary_source(corpus_files):
    assert _sha(TUTA) == TUTA_SHA256  # pinned Task-019 excerpt
    block1 = _register_block(corpus_files["combined"], 1)
    expected = corpus_files["tuta"].rstrip("\n") + "\n"
    assert block1 == expected
    assert "Prolog" in block1 and "Věčna Zima" in block1


# ---------------------------------------------------------------------------
# register 2 — artistic / poetic (album)
# ---------------------------------------------------------------------------

def test_register2_latin_script_only_and_clean(corpus_files):
    block2 = _register_block(corpus_files["combined"], 2)
    art = corpus_files["artistic"]
    assert art == block2  # combined embeds the artistic component verbatim
    assert not _has_cyrillic(art), "artistic corpus must be Latin-script only"
    for bad in ("iframe", "youtube", "wordpress", "wp-block", "Udostępnij",
                "https://", "<p", "<br", "<strong", "<div", "</"):
        assert bad not in art, f"webpage material leaked: {bad!r}"


def test_register2_all_songs_present_in_order(corpus_files):
    art = corpus_files["artistic"]
    lines = [ln for ln in art.split("\n") if ln.strip()]
    seen = [ln for ln in lines if ln in ALBUM_SONGS]
    assert seen == ALBUM_SONGS, "song boundaries missing or reordered"


def test_register2_verbatim_chorus_dedup_policy(corpus_files):
    art = corpus_files["artistic"]
    # the Velerman refrain appears once although the page repeats it after
    # every verse (6 repeats on the source page -> 1 retained)
    chorus = ("Nedolgo prijde velerman\nOn čaj i rum bude dati nam\n"
              "Kogda konca raboty zvon\nTogda my pojdemo von")
    assert art.count(chorus) == 1
    # Nikogda Vyše refrain likewise retained once
    refrain = ("Uže nikogda vyše\nUž nikogda, oh ne\nJa ne budu putovati\n"
               "Už nikogda, oh ne")
    assert art.count(refrain) == 1
    # a linguistically meaningful repeated word/phrase is NOT deduplicated:
    # the refrain words still occur inside the retained chorus
    assert art.count("Uže nikogda vyše") == 1  # only the chorus line


def test_register2_wording_not_normalized(corpus_files):
    """Unusual / poetic forms of the source page are preserved verbatim."""
    art = corpus_files["artistic"]
    for fragment in (
        "žrl peprec ložicami",          # unusual verb form, kept
        "phal dvoma rukami",            # kept as sung
        "morjskoj opověstky",           # poetic form, kept
        "bandžo i gitara",              # as sung
        "I jedna topolja",              # as sung
        "Jest medvěd polarny",          # as sung
        "Oh, plyvemo brati v svět (hej!)",
        "Hej, piva nedostatok",         # complete Morske Opověsti incl. this
        "Poslušajte, brati, šantov",
        "na medžuslovjanskom",
    ):
        assert fragment in art, f"source wording missing/altered: {fragment!r}"


def test_register2_song_boundaries_keep_full_songs(corpus_files):
    art = corpus_files["artistic"]
    # every song keeps multiple stanzas after dedup (no over-merging)
    per = {s: art.count(f"\n{s}\n") + (1 if art.startswith(s + "\n") else 0)
           for s in ALBUM_SONGS}
    assert all(per[s] == 1 for s in ALBUM_SONGS)
    # Morske Opověsti stanza with the krčmar interjection is present
    assert "Prizivajte tut krčmara" in art


# ---------------------------------------------------------------------------
# register 3 — informative / encyclopedic (Wikipedia article)
# ---------------------------------------------------------------------------

def test_register3_is_cleaned_wikipedia_prose(corpus_files):
    block3 = _register_block(corpus_files["combined"], 3)
    wiki = corpus_files["wiki"]
    assert wiki == block3
    assert _sha(WIKI) == WIKI_SHA256
    assert wiki.startswith(
        "Sadovničstvo jest proces raščenja rastlin zaradi jih")
    assert wiki.rstrip().endswith(
        "Asocijacije profesionalnyh krajobraznyh dizajnerov.")
    for bad in ("[[", "]]", "{{", "}}", "<ref", "<br", "Fajl:", "==",
                "Gledite takože", "Iztočniky"):
        assert bad not in wiki, f"wiki markup/boilerplate leaked: {bad!r}"
    assert not _has_cyrillic(wiki)
    for heading in ("Prědhistorija", "Ameriky", "Historija", "Koristi",
                    "Kako umětnost"):
        assert heading in wiki


def test_register3_is_authentic_retrieved_article_not_project_translation(
        corpus_files, build_mod):
    """The informative register is deterministic output of the recorded
    raw ISV article wikitext (retrieved from isv.wikipedia.org), not a text
    this project wrote or translated."""
    if not WIKI_RAW.is_file():
        pytest.skip("raw article wikitext is not present locally")
    assert _sha(WIKI_RAW) == WIKI_RAW_SHA256
    raw = WIKI_RAW.read_text(encoding="utf-8")
    # the raw source is the MediaWiki article (figures + references tail +
    # ISV lead sentence), i.e. an EXISTING ISV page, not our prose
    assert raw.lstrip().startswith("[[Fajl:")
    assert "== Iztočniky ==" in raw
    assert raw.count("LatCyr") > 0  # mediawiki name-gloss templates present
    expected = build_mod._clean_wikitext_prose(raw)
    assert expected == corpus_files["wiki"]
    assert not _has_cyrillic(expected)


def test_register3_and_register1_contain_no_target_story(corpus_files):
    """Neither the encyclopedic register nor the unchanged literary
    register carries any of the Polish source story's identity tokens."""
    story_tokens = ("Bronisława", "Teofil", "Julianna", "Przemysława",
                    "Antoni", "Międzyrzecze", "Słów")
    wiki = corpus_files["wiki"]
    r1 = _register_block(corpus_files["combined"], 1)
    for tok in story_tokens:
        assert tok not in wiki and tok not in r1


# ---------------------------------------------------------------------------
# kit-level corpus invariance (real corpus, temp prompt outputs)
# ---------------------------------------------------------------------------

@pytest.fixture()
def real_kit(run_mod, tmp_path, monkeypatch):
    prompts = tmp_path / "operator-prompts"
    outputs = tmp_path / "outputs"
    prompts.mkdir()
    outputs.mkdir()
    monkeypatch.setattr(run_mod, "OPERATOR_PROMPTS", prompts)
    monkeypatch.setattr(run_mod, "OUTPUTS_DIR", outputs)
    rc = run_mod.run_prepare(DATE)
    assert rc == 0
    return {"tmp": tmp_path, "run_mod": run_mod}


def test_all_18_primed_msg1_embed_identical_corpus_bytes(
        real_kit, corpus_files):
    run_mod = real_kit["run_mod"]
    op = real_kit["tmp"] / "operator-prompts"
    corpus_text = corpus_files["combined"]
    expected_tail = "\n\n" + corpus_text.rstrip("\n") + "\n"
    seen = None
    msg1s = sorted(p for p in op.glob("*.md")
                   if p.name.startswith("primed-") and p.name.endswith("-msg1.md"))
    assert len(msg1s) == 18
    for f in msg1s:
        text = f.read_text(encoding="utf-8")
        assert MSG1_HEADING in text
        body = text.split(MSG1_HEADING, 1)[1]
        assert body == expected_tail, f"{f.name} does not carry the full "
        "three-register corpus"
        h = run_mod.sha256_bytes(body.encode("utf-8"))
        seen = h if seen is None else seen
        assert h == seen  # byte-identical corpus in every primed msg1
    # register markers + anchors present in the embedded corpus
    for hdr in REGISTER_HEADERS:
        assert hdr in corpus_text
    for anchor in run_mod.CORPUS_ANCHORS:
        assert anchor in corpus_text


def test_controls_corpus_free_and_msg2_unchanged(real_kit, corpus_files):
    run_mod = real_kit["run_mod"]
    op = real_kit["tmp"] / "operator-prompts"
    bodies = []
    for f in sorted(op.glob("*.md")):
        text = f.read_text(encoding="utf-8")
        if f.name.startswith("ctl-"):
            assert STORY_TITLE in text
            assert not any(a in text for a in run_mod.CORPUS_ANCHORS)
        elif f.name.endswith("-msg2.md"):
            assert STORY_TITLE in text
            assert not any(a in text for a in run_mod.CORPUS_ANCHORS)
            # the priming cue references the previous message without
            # re-embedding corpus bytes
            assert "from the previous message of this conversation" in text
            bodies.append(run_mod._translation_body(text))
        else:  # msg1
            assert STORY_TITLE not in text
    assert len(bodies) == 18
    assert all(b == bodies[0] for b in bodies)
    assert bodies[0].startswith("Translate the Polish story below")


def test_regeneration_is_deterministic(real_kit):
    run_mod = real_kit["run_mod"]
    tmp = real_kit["tmp"]

    def snap():
        d = {}
        for p in sorted((tmp / "outputs").rglob("*.json")):
            d[str(p.relative_to(tmp))] = p.read_bytes()
        for p in sorted((tmp / "operator-prompts").glob("*.md")):
            d["prompts/" + p.name] = p.read_bytes()
        d["manifest"] = (tmp / "operator-prompts" / "manifest.json").read_bytes()
        return d

    first = snap()
    assert run_mod.run_prepare(DATE, force=True) == 0
    assert snap() == first
    manifest = json.loads((tmp / "operator-prompts" / "manifest.json")
                          .read_text(encoding="utf-8"))
    assert manifest["corpus"]["sha256"] == COMBINED_SHA256
    assert len(manifest["files"]) == 54


def test_no_stale_single_register_corpus_in_kit(run_mod, real_kit):
    """The authoritative corpus file is the combined three-register file,
    not the old one-register Tuta excerpt, and every rendered msg1 embeds
    it."""
    assert run_mod.CORPUS_ID == "phase2a-authentic-isv"
    assert run_mod.CORPUS_VERSION == "v1"
    assert run_mod.CORPUS_FILE.name == "phase2a-authentic-isv-corpus.txt"
    assert run_mod.CORPUS_FILE == COMBINED
    op = real_kit["tmp"] / "operator-prompts"
    for f in op.glob("primed-*-msg1.md"):
        text = f.read_text(encoding="utf-8")
        assert "tuta-historija-excerpt.txt" not in text
        assert "=== REGISTER 3: INFORMATIVE / ENCYCLOPEDIC ===" in text


def test_corpus_readme_records_combined_hash(corpus_files):
    readme = (CORPUS_DIR / "README.md").read_text(encoding="utf-8")
    assert COMBINED_SHA256 in readme
    assert "phase2a-authentic-isv-corpus.txt" in readme
