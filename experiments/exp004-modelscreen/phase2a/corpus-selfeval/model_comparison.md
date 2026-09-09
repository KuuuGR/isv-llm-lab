# EXP-004 — authentic corpus vs generated model outputs (descriptive resource-coverage comparison)

How close do generated outputs get to the resource-coverage properties of the authentic reference corpus under the same metrics? Descriptive only — this is NOT 'distance from native quality', and reaching the corpus percentage would not make a model 'as good as the corpus'.

| Dataset | Tokens | Canonical | Broader | Unresolved | Orthography out | Basis |
|---|---:|---:|---:|---:|---:|---|
| Combined authentic corpus | 8,096 | 80.50 % | 89.17 % | 19.50 % | 47 | per-token (corpus) |
| Register 1 — literary / narrative | 770 | 95.97 % | 99.48 % | 4.03 % | 1 | per-token (corpus) |
| Register 2 — artistic / poetic | 1,600 | 90.56 % | 100.00 % | 9.44 % | 0 | per-token (corpus) |
| Register 3 — informative / encyclopedic | 5,717 | 75.72 % | 84.83 % | 24.28 % | 25 | per-token (corpus) |
| EXP-004 Phase 1 direct outputs (primary, usable) | 1,482 | 76.51 % | 86.47 % | 23.49 % | 47 | mean over usable primary runs |
| EXP-004 Phase 2A primed outputs (primary, usable) | 1,512 | 82.49 % | 88.78 % | 17.51 % | 28 | mean over usable primary runs |
| EXP-004 repeated direct outputs (primary, usable) | 1,481 | 75.72 % | 85.27 % | 24.28 % | 53 | mean over configuration means (18 configurations) |
| EXP-004 repeated primed outputs (primary, usable) | 1,515 | 82.21 % | 88.75 % | 17.79 % | 36 | mean over configuration means (16 configurations) |

Sources: local EXP-004 rosters (`outputs/roster.json`, `phase2a/outputs/roster.json`, `repeats/outputs/roster.json`).
