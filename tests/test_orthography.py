"""Character-level orthographic sanity check tests (SODA Task 015).

Covers the deterministic validator in src/isv_eval/orthography.py:
allowed Interslavic letters (standard + etymological + sanctioned
alternatives, sourced from the official Interslavic orthography page),
Cyrillic, Polish-specific letters, other Latin letters, punctuation /
whitespace / digits, apostrophes / quotation marks / dashes used by the
corpus, empty text, clean translations, a single invalid character,
mixed Latin/Cyrillic, t́/d́ combining-acute spelling, and the audit-only
guarantee (text and lexical metrics are never touched).
"""
import json

from isv_eval.orthography import (ACCEPTED_PUNCTUATION, ALLOWED_LETTERS,
                                  ALPHABET_SOURCE_URL, POLISH_ONLY_LETTERS,
                                  char_category, scan_text)

CLEAN = ("V dolině okruženej holmami ležalo městečko Medžurěčje. "
         "– Kako byti dobrym bratom? – vprašala Bronislava.\n"
         "Ljudi govorili jedinym jezykom, a potom dvěma.\n")


def counts(report):
    return report.as_dict()


def test_alphabet_source_is_the_official_interslavic_site():
    assert ALPHABET_SOURCE_URL == \
        "https://steen.free.fr/interslavic/orthography.html"


def test_standard_latin_letters_allowed():
    for ch in "abcdefghijklmnoprstuvyz":
        assert char_category(ch) == "allowed_letter"
    for ch in "čěšž":
        assert char_category(ch) == "allowed_letter"
    for ch in "ABCDEFGHIJKLMNOPRSTUVYZČĚŠŽ":
        assert char_category(ch) == "allowed_letter"
    # the standard alphabet explicitly excludes q, w, x
    for ch in "qwxQWX":
        assert char_category(ch) == "other_latin_letter"


def test_etymological_letters_allowed():
    for ch in "ęųåėȯćđĺńŕśź":
        assert char_category(ch) == "allowed_letter", ch
    for ch in "ĘŲÅĖȮĆĐĹŃŔŚŹ":
        assert char_category(ch) == "allowed_letter", ch


def test_sanctioned_alternative_graphemes_allowed():
    # page-sanctioned spellings: ť/ď (t́/d́), ľ (ĺ), ň (ń), ř (ŕ), è/ò (ė/ȯ)
    for ch in "ťďľňřèò":
        assert char_category(ch) == "allowed_letter", ch
    for ch in "ŤĎĽŇŘÈÒ":
        assert char_category(ch) == "allowed_letter", ch


def test_combining_acute_only_after_t_d():
    assert char_category("\u0301", prev="t") == "t/d_combining_acute"
    assert char_category("\u0301", prev="d") == "t/d_combining_acute"
    assert char_category("\u0301", prev="D") == "t/d_combining_acute"
    assert char_category("\u0301", prev="e") == "unexpected"
    assert char_category("\u0301", prev="") == "unexpected"


def test_cyrillic_letters_classified():
    for ch in "яжіъеМоНыюь":
        assert char_category(ch) == "cyrillic_letter", ch
    # Cyrillic letters are letters, never punctuation or whitespace
    assert scan_text("Може").as_dict()["cyrillic"] == 4


def test_polish_specific_letters():
    # Polish letters that are NOT in the ISV inventory
    for ch in "ąłóż":
        assert char_category(ch) == "polish_specific_letter", ch
    for ch in "ĄŁÓŻ":
        assert char_category(ch) == "polish_specific_letter", ch
    # ... while ć ę ń ś ź ARE valid etymological ISV letters -> allowed
    for ch in "ćęńśź":
        assert char_category(ch) == "allowed_letter", ch
    assert set(POLISH_ONLY_LETTERS) == set("ąłóżĄŁÓŻ")


def test_other_latin_letters_classified():
    for ch in "áéíýúāēū":
        assert char_category(ch) == "other_latin_letter", ch
    assert char_category("ǫ") == "other_latin_letter"  # ISV uses ų, not ǫ
    assert char_category("ü") == "other_latin_letter"  # page: no ü for borrowings
    assert char_category("W") == "other_latin_letter"


def test_other_script_letters_classified():
    for ch in "αβγא":
        assert char_category(ch) == "other_script_letter", ch


def test_punctuation_whitespace_digits_never_errors():
    text = ("Akt 1 — Prolog. V: slovo „citata“ (2026): !\n"
            "Line 2 – konec... «Guillemet» \"ascii\" 'ap' 42.")
    rep = scan_text(text).as_dict()
    assert rep["cyrillic"] == 0
    assert rep["polish_specific"] == 0
    assert rep["other_latin"] == 0
    assert rep["other_script"] == 0
    assert rep["unexpected_nonletters"] == 0
    # every accepted prose-punctuation char in the text stays accepted
    for ch in text:
        if ch in ACCEPTED_PUNCTUATION or ch.isspace() or ch in "0123456789":
            assert char_category(ch) != "unexpected"
    # a non-accepted punctuation glyph IS reported (as a formatting/symbol
    # note, never as an alphabet error)
    rep2 = scan_text("50% za 100%").as_dict()
    assert rep2["unexpected_nonletters"] == 2
    assert rep2["cyrillic"] == 0 and rep2["other_latin"] == 0


def test_corpus_quotes_apostrophes_dashes_accepted():
    # glyphs observed in the actual corpus documents
    text = ("– Věru, „dva jezyky“ sut kako sestry. "
            "Ona rekla: \"ne vždy\"; on – ’nikogda’... (to jest).\n")
    rep = scan_text(text).as_dict()
    assert rep["outside_inventory"] == 0


def test_digits_accepted():
    rep = scan_text("V lětě 2026 bylo 42 jezykov.").as_dict()
    assert rep["outside_inventory"] == 0
    # non-ASCII digit-like chars are reported, not silently accepted
    assert scan_text("²").as_dict()["unexpected_nonletters"] == 1


def test_empty_text():
    rep = scan_text("").as_dict()
    assert rep["total_chars"] == 0
    assert rep["outside_inventory"] == 0
    assert rep["unexpected"] == {}


def test_clean_translation_has_no_anomalies():
    rep = scan_text(CLEAN).as_dict()
    assert rep["outside_inventory"] == 0
    assert rep["allowed_letters"] > 0
    assert rep["unexpected"] == {}
    # every character accounted for
    assert rep["total_chars"] == (rep["allowed_letters"]
                                  + rep["accepted_nonletters"]
                                  + rep["outside_inventory"])


def test_single_invalid_character_detected_with_line():
    text = "Dobry den.\nTo jest čisto.\nAle tuto jest žle.\n"
    rep = scan_text(text).as_dict()
    assert rep["outside_inventory"] == 0
    dirty = "Dobry den.\nTo jest čisto.\nAle tuto jest złe.\n"
    rep2 = scan_text(dirty).as_dict()
    assert rep2["outside_inventory"] == 1
    assert rep2["polish_specific"] == 1
    (ch, detail), = rep2["unexpected"].items()
    assert ch == "ł"
    assert detail["category"] == "polish_specific_letter"
    assert detail["count"] == 1
    assert detail["lines"] == [3]


def test_single_cyrillic_character_detected():
    rep = scan_text("To jest medžuslovjansky текст.").as_dict()
    assert rep["cyrillic"] == 5   # т е к с т
    assert rep["outside_inventory"] == 5


def test_mixed_latin_cyrillic_split():
    text = "Može byti, a Може ne. ь"
    rep = scan_text(text).as_dict()
    assert rep["cyrillic"] == 5          # М о ж е (4) + ь (1)
    assert rep["polish_specific"] == 0
    assert rep["other_latin"] == 0
    assert rep["outside_inventory"] == 5


def test_unexpected_unicode_characters_reported_not_repaired():
    for ch in ["#", "*", "→", "‡", "\x00", "😀"]:
        rep = scan_text(f"abc{ch}def").as_dict()
        assert rep["unexpected_nonletters"] == 1, ch
        assert rep["cyrillic"] == 0
        assert rep["polish_specific"] == 0
        assert rep["other_latin"] == 0
        (uch, detail), = rep["unexpected"].items()
        assert uch == ch
        assert detail["count"] == 1
        assert detail["lines"] == [1]


def test_scan_is_deterministic_and_pure():
    a = scan_text(CLEAN).as_dict()
    b = scan_text(CLEAN).as_dict()
    assert a == b
    # the audit never modifies its input
    orig = CLEAN
    scan_text(orig)
    assert orig == CLEAN


def test_allowed_letter_inventory_is_explicit_and_documented():
    # no letter is silently accepted just because it is Latin; verify a few
    # near-miss Polish/Czech lookalikes are NOT allowed
    assert "ł" not in ALLOWED_LETTERS
    assert "ó" not in ALLOWED_LETTERS
    assert "ž" in ALLOWED_LETTERS     # ISV ž (haček), not Polish ż
    assert "ż" not in ALLOWED_LETTERS
    assert "č" in ALLOWED_LETTERS
    assert "ć" in ALLOWED_LETTERS     # etymological
    assert "x" not in ALLOWED_LETTERS
    assert "q" not in ALLOWED_LETTERS
    assert "w" not in ALLOWED_LETTERS


# ---------------------------------------------------------------------------
# runner script (scripts/check_orthography.py) — deterministic reports
# ---------------------------------------------------------------------------

def _load_script():
    import importlib.util
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    spec = importlib.util.spec_from_file_location(
        "check_orthography", root / "scripts" / "check_orthography.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_runner_writes_deterministic_reports(tmp_path):
    mod = _load_script()
    cfg = {"dir": tmp_path / "outputs", "label": "EXP-T", "globs": ("*/output.txt",)}
    cfg["dir"].mkdir(parents=True)
    for run in ("run_a", "run_b"):
        d = cfg["dir"] / run
        d.mkdir()
        (d / "meta.json").write_text(json.dumps(
            {"status": "collected_external_output"}), encoding="utf-8")
        (d / "output.txt").write_text(
            "Medžuslovjansky tekst jest čisty.\n"
            if run == "run_a" else "Polski tekst: złe ł i я.\n",
            encoding="utf-8")
    result = mod.audit_experiment(cfg)
    assert result["summary"]["files_scanned"] == 2
    by_run = {f["run_id"]: f for f in result["files"]}
    assert by_run["run_a"]["metrics"]["outside_inventory"] == 0
    m = by_run["run_b"]["metrics"]
    assert m["polish_specific"] == 2       # ł in "złe" + standalone ł
    assert m["cyrillic"] == 1              # я
    assert m["outside_inventory"] == 3
    assert by_run["run_b"]["status"] == "collected_external_output"
    # deterministic: identical on second run
    result2 = mod.audit_experiment(cfg)
    assert result == result2
    # markdown renderer includes the metrics table
    md = mod.render_md(result)
    assert "outside" in md and "run_a" in md and "EXP-T" in md
