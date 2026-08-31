from isv_eval.tokenizer import NUMBER, PUNCT, WORD, tokenize


def buckets(text):
    return [(t.surface, t.kind, t.is_lexical, t.sentence_id,
             t.paragraph_id) for t in tokenize(text)]


def test_basic_words_and_punctuation():
    toks = tokenize("Brat i žena. Oni spijut!")
    kinds = [t.kind for t in toks]
    assert kinds == [WORD, WORD, WORD, PUNCT, WORD, WORD, PUNCT]
    assert [t.surface for t in toks if t.kind == WORD] == [
        "Brat", "i", "žena", "Oni", "spijut"]


def test_surface_and_normalized_preserved():
    toks = tokenize("Žena")
    assert toks[0].surface == "Žena"
    assert toks[0].normalized == "žena"
    assert toks[0].folded == "žena"


def test_numbers_are_non_lexical():
    toks = tokenize("V 2024 godu. Cena 3,5.")
    nums = [t for t in toks if t.kind == NUMBER]
    assert [t.surface for t in nums] == ["2024", "3,5"]
    assert all(not t.is_lexical for t in nums)


def test_hyphenated_word_is_single_token():
    toks = tokenize("Po-mojemu to jest.")
    assert toks[0].surface == "Po-mojemu"
    assert toks[0].kind == WORD
    assert toks[0].is_lexical


def test_em_dash_and_quotes_are_punctuation():
    toks = tokenize('"Dobro!" — rekla.')
    punct = [t.surface for t in toks if t.kind == PUNCT]
    assert '"' in punct
    assert "—" in punct
    assert "!" in punct


def test_ellipsis():
    toks = tokenize("Oni čekali…")
    assert toks[-1].kind == PUNCT


def test_paragraph_splitting():
    toks = tokenize("Prvy.\n\nVtory.")
    paras = {t.paragraph_id for t in toks}
    assert paras == {0, 1}


def test_sentence_context_retained():
    toks = tokenize("Brat ima knigy. On je čita.")
    assert toks[0].sentence == "Brat ima knigy."
    assert toks[0].sentence_id == 0
    later = [t for t in toks if t.surface == "čita"][0]
    assert later.sentence == "On je čita."
    assert later.sentence_id == 1


def test_apostrophe_handling():
    # Internal apostrophes stay part of the word (like hyphens).
    assert [t.surface for t in tokenize("l'arnaque")] == ["l'arnaque"]
    # Standalone apostrophes are punctuation.
    assert [t.surface for t in tokenize("prepravka ' konec")] == [
        "prepravka", "'", "konec"]
