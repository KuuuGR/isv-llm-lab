from isv_eval.normalize import (fold_etymological, is_cyrillic, is_lexical,
                                lookup_keys, nfc, normalize_word)


def test_nfc_normalization():
    decomposed = "žena"  # z + U+030C combining caron
    assert nfc(decomposed) == "žena"
    assert nfc("žena") == "žena"


def test_normalize_word_lowercases_and_keeps_diacritics():
    assert normalize_word("Žena") == "žena"
    assert normalize_word("  Brat ") == "brat"
    assert normalize_word("čaj") == "čaj"


def test_fold_etymological_chars():
    assert fold_etymological("ženojų") == "ženoju"
    assert fold_etymological("česnȯk") == "česnok"
    assert fold_etymological("podȯjdti") == "podojdti"
    assert fold_etymological("Česnȯk") == "česnok"  # uppercase folds too


def test_standard_letters_not_folded():
    # č š ž ě are meaningful standard ISV letters and must survive folding.
    assert fold_etymological("žena") == "žena"
    assert fold_etymological("šest") == "šest"
    assert fold_etymological("čaj") == "čaj"


def test_lookup_keys():
    assert lookup_keys("žena") == ["žena"]
    assert lookup_keys("Žena") == ["žena"]
    assert lookup_keys("ženojų") == ["ženojų", "ženoju"]
    assert lookup_keys("ženoju") == ["ženoju"]


def test_is_cyrillic():
    assert is_cyrillic("слово")
    assert is_cyrillic("Slovo") is False


def test_is_lexical():
    assert is_lexical("brat")
    assert is_lexical("brat2")
    assert is_lexical("2024") is False
    assert is_lexical(".") is False
    assert is_lexical("…") is False
    assert is_lexical("—") is False
