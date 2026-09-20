# Storage proposal (not implemented)

**Status:** design comparison. **Do not implement a database in this pass.**

## Options

### Option A — JSON files

One file per fact/source (or small collections).

| Criterion | Assessment |
|---|---|
| Human editability | Moderate (verbose) |
| Provenance | Good if fields enforced |
| Diffability | Good in git |
| Version control | Excellent |
| Query capability | Weak (grep / scripts) |
| Reproducibility | Strong |
| LLM retrieval later | Easy to load; weak indexing |

### Option B — JSONL records

Append-only lines for observations/facts.

| Criterion | Assessment |
|---|---|
| Human editability | Poor for review discussions |
| Provenance | Good |
| Diffability | Fair (line-oriented) |
| Version control | Good |
| Query capability | Better streaming/filter |
| Reproducibility | Strong |
| LLM retrieval later | Good for bulk export |

### Option C — SQLite

Relational store.

| Criterion | Assessment |
|---|---|
| Human editability | Poor without UI |
| Provenance | Excellent with constraints |
| Diffability | Poor (binary) |
| Version control | Awkward |
| Query capability | Excellent |
| Reproducibility | Needs dump discipline |
| LLM retrieval later | Strong |

### Option D — YAML/Markdown for human review + generated JSON

Humans edit Markdown/YAML fact cards; a future tool emits JSON for machines.

| Criterion | Assessment |
|---|---|
| Human editability | **Best** for research review |
| Provenance | Excellent in prose + fields |
| Diffability | Excellent |
| Version control | Excellent |
| Query capability | Via generated JSON index |
| Reproducibility | Strong if generator pinned |
| LLM retrieval later | JSON side serves retrieval |

---

## Recommendation for the current research stage

**Prefer Option D** (human-reviewed Markdown/YAML cards + generated JSON),
with a possible **tiny Option A JSON seed** only if a generator does not yet
exist.

Rationale: the schema is still stabilizing; review notes and conflict
narratives matter as much as fields; git-friendly diffs match the repo’s
documentation culture; SQLite is premature.

Defer Option C until query volume and multi-user needs justify it.
Use JSONL (B) as an optional export format for observations, not as the
primary human interface.

## Non-goals now

- No production DB migration.
- No automatic Steen/Wikipedia/Hunspell bulk load into any store.
