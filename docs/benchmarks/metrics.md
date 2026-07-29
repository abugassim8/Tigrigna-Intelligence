# Metrics

> **Status: none selected.** No metrics have been chosen or validated for
> Tigrinya. The table below is a scaffold, not a recommendation.
>
> **Gated on:** `../research/reports/08_evaluation/`

## Purpose of this document

The definitive list of metrics used to measure each capability, how each is
computed, and — most importantly — the evidence that it is valid for Tigrinya.

## Why this document exists

A metric is a claim about what matters, disguised as a number. Choosing one
without examining that claim means optimising for something nobody deliberately
chose.

This is a specific and serious risk here. Most standard NLP metrics were
developed and validated on high-resource, morphologically simple languages —
predominantly English. Several have known problems with morphologically rich
languages: surface-form comparison penalises legitimate inflectional variation,
tokenization-dependent scores vary with segmentation choices, and reference-based
metrics assume a quantity and quality of reference data that Tigrinya may not
have.

**We may not assume standard metrics transfer.** Each one must be justified for
Tigrinya specifically, and where a standard metric proves inadequate, that is a
finding to record rather than a problem to route around.

## How to use it

- Use the metric this document specifies for a capability. Do not substitute
  one because it is more convenient or produces a nicer number.
- When reporting any result, state the metric, its version, and the exact
  computation — metric implementations differ, sometimes substantially.
- If a metric appears to be misleading, record it as a finding rather than
  quietly changing it.

## Metric register

| Capability | Metric | Validated for Tigrinya | Baseline | Notes |
| --- | --- | --- | --- | --- |
| Translation | TBD | No | — | Not yet researched |
| Embeddings / similarity | TBD | No | — | Not yet researched |
| Semantic search | TBD | No | — | Not yet researched |
| Cross-language retrieval | TBD | No | — | Not yet researched |
| Tokenization | TBD | No | — | Not yet researched |
| Morphological analysis | TBD | No | — | Not yet researched |
| Lemmatization | TBD | No | — | Not yet researched |
| Spell correction | TBD | No | — | Not yet researched |
| Grammar checking | TBD | No | — | Not yet researched |
| Transliteration | TBD | No | — | Not yet researched |
| NER | TBD | No | — | Not yet researched |
| Entity linking | TBD | No | — | Not yet researched |
| Summarization | TBD | No | — | Not yet researched |
| Question answering | TBD | No | — | Not yet researched |

## Required fields for each metric

```markdown
### [Metric name] — [capability]

- **What it measures:**
- **How it is computed:** exact implementation, library, version, parameters
- **Range and interpretation:** what a good score looks like, and why
- **Validity evidence for Tigrinya:** why we believe this metric is meaningful
  here — this field is the reason this document exists
- **Known failure modes:** where this metric misleads
- **Morphology sensitivity:** how it behaves under rich inflection
- **Tokenization dependence:** whether and how segmentation changes the score
- **Baseline values:** what known systems score
- **Reported alongside:** metrics that must be read together with this one
```

## Standards

1. **No single-metric decisions.** Any metric can be gamed; report a set.
2. **Report variance, not just means.** A mean with no spread hides everything
   interesting, particularly on small evaluation sets.
3. **Report on subsets**, not just aggregates — by domain, register, length, and
   dialect where possible. Aggregate scores routinely hide the failure that
   matters.
4. **Error analysis accompanies numbers.** For low-resource languages the
   qualitative failure pattern is usually more informative than the score.
5. **Pin the implementation.** Metric implementations differ; record library and
   version.
6. **State confidence intervals** where evaluation sets are small — which they
   will be.

## What future contributors should add

Validated metrics with the evidence for their validity. Record metrics that were
considered and **rejected as unsuitable for Tigrinya**, with the reason — that is
a genuinely useful contribution to the wider low-resource NLP ecosystem, not just
to this project.

## Related

- `evaluation_strategy.md` · `datasets.md`
- `../vision/success_metrics.md` · `../research/reports/08_evaluation/`
