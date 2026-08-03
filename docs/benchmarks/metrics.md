# Metrics

> **Status: translation metrics selected and validated** (DEC-009, 2026-08-03).
> Remaining capabilities are still unresearched — those rows are a scaffold, not
> a recommendation.
>
> **Evidence:** `../research/reports/08_evaluation/001-metric-validity-and-harness.md`,
> `../../experiments/003-metric-validity/`

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
| Translation | **chrF** (primary) + **BLEU** (comparability only) | **Yes — measured** | NLLB-3.3B COMET 0.82 ET / 0.80 ER `[reported]` | DEC-009. Never report BLEU alone |
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

## Validated metrics

### chrF — translation and surface generation `[PRIMARY]`

- **What it measures:** character n-gram F-score between hypothesis and reference.
- **How it is computed:** `sacrebleu.corpus_chrf`, **sacrebleu 2.6.0**, default
  parameters. **Pin these** — character n-gram order, word n-gram order, and β
  all change the number.
- **Range:** 0–100, higher better.
- **Validity evidence for Tigrinya:** measured in
  `experiments/003-metric-validity/` on FLORES+ parallel data (same 30 sentences,
  English and Tigrinya). Under inflectional near-misses chrF retains **74.9%** of
  a perfect score where BLEU retains **41.5%** — and **the advantage widens as
  quality falls** (1.18× → 1.46× → 1.80× at 10/20/30% corruption).
- **Known failure modes:** rewards surface overlap, so a fluent-but-wrong output
  sharing character sequences can score respectably. Not a semantic metric.
- **Morphology sensitivity:** **low** — this is the reason it was chosen. A right
  stem with a wrong affix keeps most of its character n-grams.
- **Tokenization dependence:** **none** — it never tokenizes into words, which
  matters because Ge'ez tokenization is itself unsettled (Experiment 002).
- **Reported alongside:** BLEU, always.

### BLEU — translation `[COMPARABILITY ONLY]`

- **What it measures:** modified n-gram precision on whitespace-delimited words,
  with a brevity penalty.
- **How it is computed:** `sacrebleu.corpus_bleu`, **sacrebleu 2.6.0**.
- **Validity evidence for Tigrinya:** measured — BLEU is **~1.08× harsher** on
  Tigrinya than English at an identical error rate. Real, consistent, and about
  **half** the size the standard warning about morphologically rich languages
  implies. The test was ~1.44× harsher on Tigrinya by construction (a Ge'ez
  character is a consonant+vowel pair, a Latin letter is one phoneme), which
  biased *toward* a larger penalty — so ~8% is an **upper** estimate.
- **Known failure modes:** treats an inflectional near-miss as a total miss.
  Loses information fastest exactly where low-resource systems operate.
- **⛔ Prohibited use:** **never compare Tigrinya BLEU to another language's BLEU
  without stating the ~8% penalty.** This is a documented error, not a
  judgement call.
- **Reported alongside:** chrF, always. Never reported alone.

### COMET — ⚠️ NOT validated

**Untested.** Learned metrics require model downloads from an egress-blocked
domain. This matters because **NLLB's published Tigrinya numbers use COMET**, so
we cannot compare against them until it is resolved (**A-09**). Recorded here so
its absence is visible rather than silently assumed away.

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
