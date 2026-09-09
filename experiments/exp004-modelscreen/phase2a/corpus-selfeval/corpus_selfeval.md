# EXP-004 — authentic corpus self-evaluation (SODA Task 029)

Deterministic application of the unchanged EXP-004 evaluation stack (`isv-eval` metrics + Task-015 orthography audit) to the authentic Medžuslovjansky reference corpus — the same stack used for generated model outputs. Resource-coverage evidence, NOT linguistic-correctness claims; no composite score.

Corpus: `phase2a-authentic-isv` v1, SHA-256 `aaad28e43935a40313585d77a33bfc788d97e8d69b081f9486af74d52ca1a857`.

## Corpus overview

| Dataset | Tokens | Canonical | Broader | Unresolved | Orthography out |
|---|---:|---:|---:|---:|---:|
| Combined authentic corpus | 8,096 | 80.50 % | 89.17 % | 19.50 % | 47 |
| Register 1 — literary / narrative | 770 | 95.97 % | 99.48 % | 4.03 % | 1 |
| Register 2 — artistic / poetic | 1,600 | 90.56 % | 100.00 % | 9.44 % | 0 |
| Register 3 — informative / encyclopedic | 5,717 | 75.72 % | 84.83 % | 24.28 % | 25 |

Tokens = lexical tokens (denominator policy of `isv-eval`); Canonical = (A+B)/lexical; Broader = (canonical-supported + exact alternative-resource attestation)/lexical; Unresolved = C/lexical; Orthography out = characters outside the official Interslavic inventory.

## Register 1 — literary / narrative (`Tuta historija`)

File `experiments/exp004-modelscreen/phase2a/corpus/tuta-historija-excerpt.txt` · SHA-256 `413830fa4ff6aaa8…` · 4,820 bytes.

| metric | value |
|---|---:|
| lexical tokens | 770 |
| exact dictionary matches (A) | 739 |
| morphologically valid (B) | 0 |
| unresolved (C) | 31 |
| canonical coverage | 95.97 % |
| broader resource-supported coverage | 99.48 % |
| unresolved rate | 4.03 % |

Orthography (outside-inventory):

| character class | count |
|---|---:|
| Cyrillic | 0 |
| Polish-specific | 0 |
| other Latin | 0 |
| other script | 0 |
| unexpected non-letter | 1 |
| **outside inventory (total)** | **1** |

## Register 2 — artistic / poetic (album *Ahoj, Slovjani!*)

File `experiments/exp004-modelscreen/phase2a/corpus/album-ahoj-slovjani-artistic-isv.txt` · SHA-256 `7e25a56f67a52976…` · 9,407 bytes.

| metric | value |
|---|---:|
| lexical tokens | 1,600 |
| exact dictionary matches (A) | 1,449 |
| morphologically valid (B) | 0 |
| unresolved (C) | 151 |
| canonical coverage | 90.56 % |
| broader resource-supported coverage | 100.00 % |
| unresolved rate | 9.44 % |

Orthography (outside-inventory):

| character class | count |
|---|---:|
| Cyrillic | 0 |
| Polish-specific | 0 |
| other Latin | 0 |
| other script | 0 |
| unexpected non-letter | 0 |
| **outside inventory (total)** | **0** |

## Register 3 — informative / encyclopedic (Wikipedia *Sadovničstvo*)

File `experiments/exp004-modelscreen/phase2a/corpus/wiki-sadovnistvo-encyclopedic-isv.txt` · SHA-256 `b03402fef2384730…` · 44,101 bytes.

| metric | value |
|---|---:|
| lexical tokens | 5,717 |
| exact dictionary matches (A) | 4,328 |
| morphologically valid (B) | 1 |
| unresolved (C) | 1,388 |
| canonical coverage | 75.72 % |
| broader resource-supported coverage | 84.83 % |
| unresolved rate | 24.28 % |

Orthography (outside-inventory):

| character class | count |
|---|---:|
| Cyrillic | 0 |
| Polish-specific | 0 |
| other Latin | 7 |
| other script | 0 |
| unexpected non-letter | 18 |
| **outside inventory (total)** | **25** |

## Cross-register vocabulary composition (exploratory)

Lexical-surface overlap between registers (normalized surfaces; not a quality score — 'unique to one register' does not mean 'incorrect').

| register | unique lexical surfaces |
|---|---:|
| Register 1 — literary / narrative | 410 |
| Register 2 — artistic / poetic | 655 |
| Register 3 — informative / encyclopedic | 2,639 |

| overlap | shared surfaces |
|---|---:|
| register 1 × register 2 | 113 |
| register 1 × register 3 | 109 |
| register 2 × register 3 | 118 |
| all three registers | 61 |
| union of the three registers | 3,425 |

## Interpretation (recorded, descriptive)

- The authentic corpus itself is the **reference point** for interpreting model coverage under the same metrics: generated outputs are compared with what an authentic, human-produced Medžuslovjansky text scores.
- The corpus is **not** a perfect upper bound on Interslavic, and the evaluator measures resource coverage, not linguistic correctness. A model reaching (or exceeding) the corpus percentage would not thereby be 'as good as the corpus'.
- Register differences are descriptive: the combined corpus can hide substantial variation between registers.
- The artistic register is expected to contain poetic/rhyme-driven forms absent from the dictionary; the orthography audit policy for proper names and sanctioned forms is unchanged (nothing is 'fixed').
