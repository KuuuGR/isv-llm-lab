# References needed / pending camera-ready verification

Policy: do **not** fabricate bibliographic entries. Verified entries used in `latex/references.bib` are listed below as confirmed. Items in this file still need a full peer-reviewed citation or author confirmation before submission.

Updated after `SCIENTIFIC_AUDIT.md` (2026-09-18).

## Confirmed and used in `references.bib`

| Key | Verification | Sentence-support note (audit) |
|---|---|---|
| `brown2020language` | NeurIPS 2020 / arXiv:2005.14165 | ICL / few-shot framing — OK |
| `hendy2023good` | arXiv:2302.09210 | LLM-MT evaluation / domain-prompt sensitivity — OK |
| `jiao2023chatgpt` | arXiv:2301.08745 | LLM translator engine differences — OK |
| `koehn-knowles-2017-six` | ACL Anthology W17-3204 | Low-resource / NMT challenges — OK |
| `papineni-etal-2002-bleu` | ACL Anthology P02-1040 | Cited to contrast *non*-use as primary metric — OK |
| `rei-etal-2020-comet` | ACL Anthology 2020.emnlp-main.213 | Same contrast / future eval options — OK |
| `maillard-etal-2023-small` | ACL Anthology 2023.acl-long.154 | Minimal-data MT motivation — OK |
| `kocmi-federmann-2023-large` | ACL Anthology 2023.eamt-1.19 | LLM-as-evaluator literature — OK |
| `zhu2023multilingual` | arXiv:2304.04675 | Multilingual LLM-MT — OK; **confirm final venue** |
| `moslem2023adaptive` | arXiv:2301.13294 | Adaptive/example-conditioned LLM MT — OK; **confirm final venue** |

## Still needed (not invented) — concrete audit list

1. **Interslavic language description (P1)** — At least one peer-reviewed or stable archival citation for Interslavic/Medžuslovjansky suitable for Related Work / Introduction (e.g. verified Merunka and/or van Steenbergen publications with complete BibTeX). Community websites alone are weak for CUP NLP. Until added, keep restrained operational wording (current draft strategy).

2. **Venue-of-record confirmation (P2)** — Replace or annotate arXiv-only entries for Zhu et al. and Moslem et al. with published venue BibTeX when available.

3. **Optional denser LLM-MT prompting set (P2)** — Add only after ACL Anthology/arXiv verification (e.g. established prompting-for-MT papers such as verified Zhang/Vilar-type entries). Do not invent titles.

4. **Optional human MT evaluation standards (P2)** — MQM/DA references only if a future revision expands human-evaluation discussion beyond coverage metrics.

## Action

Before submission:
- Resolve item (1), or keep the manuscript’s restrained ISV paragraph that avoids unverified citations.
- Confirm (2) for camera-ready.
- Do not fabricate any Interslavic bibliographic entry.
