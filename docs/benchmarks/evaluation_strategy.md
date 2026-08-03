# Evaluation Strategy

> **Status: translation evaluation designed** (DEC-009, DEC-010, 2026-08-03).
> Metrics are validated by measurement. Other capabilities remain unresearched.
>
> **Evidence:** `../research/reports/08_evaluation/001-metric-validity-and-harness.md`

## Purpose of this document

The overall approach to measuring whether the platform's capabilities work — what
gets evaluated, how, how often, and to what standard.

## Why this document exists

**Evaluation comes before capability** (P-4). Without trustworthy measurement we
cannot compare approaches, detect regressions, justify decisions, or honestly
describe what we have built. Every claim this project makes rests on whatever
this document ends up specifying.

There is also a risk specific to this project that this document exists to guard
against: standard NLP metrics were largely developed and validated on
high-resource, morphologically simple languages. Whether they mean anything for
Tigrinya is an open question, not a safe assumption. Borrowing a metric because
it is standard, and then trusting the number it produces, is a way to be
confidently wrong for a long time.

## How to use it

- Before building a capability, check what this document says about measuring it.
  If it says nothing, the evaluation design is the work that comes first.
- Before claiming any result, check it was measured the way this document
  specifies.
- When evaluation practice changes, update this document and record why.

## Sections to be completed

### Evaluation philosophy
What we consider adequate evidence that a capability works.

### Metric validity for Tigrinya — **ANSWERED BY MEASUREMENT**

The foundational question is settled for translation, and settled by experiment
rather than by citation (the literature is egress-blocked).

**BLEU is ~1.08× harsher on Tigrinya than English** at an identical error rate —
real, but roughly half the size the standard warning implies. **chrF is primary**
because its advantage over BLEU *widens as quality falls* (1.18× → 1.80× at
10% → 30% corruption), and low-resource systems live in that regime.

Both are always reported together. See `metrics.md` and **DEC-009**.

**Still open:** COMET is unvalidated and is what NLLB's published Tigrinya numbers
use.

### Evaluation sets
What we use for each capability, where it came from, and how it is maintained.
See `datasets.md`.

### Contamination control — and three other gates

**DEC-008** requires contamination screening before any dataset enters training
use. Research since has added three more failure modes to the same gate, each
found the hard way:

1. **Contamination** — `farefaine/tigrinya-pretraining` was **confirmed** to
   contain TiQuAD validation data while advertised as pretraining text.
2. **Licence** — ~99% of measured Tigrinya data carries no usable licence.
3. **Quality** — both cleanly-licensed corpora have undocumented defects
   (encoding corruption; PDF column-scrambling that preserves words but destroys
   sentences). Found in Experiment 002.
4. **Variety** — evaluation sets must be variety-audited (**DEC-010**).

A dataset passes all four or it does not enter use.

### Baselines
What we measure against. Without a baseline a number is not a result.

### Human evaluation
Where it is required, how it is run, how raters are recruited and calibrated,
and what it costs.

### Dialectal and register coverage — **variety-scoped, never aggregated**

**DEC-010:** every result carries a variety label — Eritrean, Ethiopian, or
`unknown`. Scores from different varieties are **never combined into a single
"Tigrinya score."**

This is not hypothetical. Our two DEC-005 anchors appear to be in **different
varieties**: TiQuAD is `[verified]` Eritrean-sourced, while FLORES+ Tigrinya
carries Ethiopian markers and is `[verified]` orthographically inconsistent with
itself. An aggregate across them would describe a language nobody speaks.

`unknown` is a real and expected label — most existing Tigrinya resources do not
state their variety, and guessing defeats the purpose.

### Automated evaluation in the pipeline
What runs automatically, when, and what gates model promotion.

### Regression detection
How quality loss is noticed by us rather than reported by a user.

### Reporting standards
How results are recorded so they are comparable over time and reproducible.

## What future contributors should add

The actual strategy, once `08_evaluation` research is complete. Then keep it
current — evaluation approaches drift, and an evaluation document that no longer
describes what is actually run is actively misleading.

## Related

- `metrics.md` — the specific metrics and their validity
- `datasets.md` — the evaluation data
- `../vision/success_metrics.md` — project-level success criteria
- `../research/reports/08_evaluation/` — the research that will produce this
