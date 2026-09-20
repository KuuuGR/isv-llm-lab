# Backward audit protocol

**Status:** design protocol for future re-checking of earlier project
results. **Do not reinterpret historical raw outputs in this pass.**

## Purpose

```text
independent language knowledge base
             ↓
audit old evaluator assumptions
             ↓
audit earlier translation results
             ↓
identify false negatives / questionable classifications
             ↓
document corrections
```

## Hard constraint

The backward audit must **NOT** modify historical raw model outputs,
frozen sources, or canonical experiment byte artifacts.

It produces a **parallel interpretation layer**.

## Classification of historical findings

| Class | Meaning |
|---|---|
| `still_supported` | Prior classification still warranted under current KB |
| `metric_false_negative` | Form likely resource-supported / morphologically regular but marked unresolved due to metric/resource limits |
| `resource_policy_limitation` | Expected under documented Tier-C vs Tier-S split (not an error) |
| `ambiguous` | Insufficient basis to revise interpretation |
| `corrected_interpretation` | New reading of what the metric meant — **not** a rewrite of the raw output |

## Anti-circularity rules

1. Do not change A/B/C labels in historical `evaluation.json` files.
2. Do not “fix” EXP-001/002/003/004 reports in place; add dated audit notes.
3. Do not use the aggregator’s own Mode B packages as proof that older
   Direct outputs were wrong.
4. Prefer linking to RESOURCE_POLICY disagreement types already documented
   (normalization gap, morphology coverage gap, resource-layer difference).

## Suggested future artifact

```text
docs/research/isv-grammar-aggregator/audits/
  BACKWARD_AUDIT_YYYY-MM-DD.md
```

Each entry: run id, token/form, old bucket, new class, evidence fact_ids,
notes.

## Relation to EXP-002/003 regressions

Token-aligned A→C matrices remain historical facts. A backward audit may
explain *why* a regression happened (e.g. resource-only candidate) without
erasing the regression count.
