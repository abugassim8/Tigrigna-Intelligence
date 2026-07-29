# Evaluation Strategy

> **Status: not designed.** This is a scaffold. No evaluation approach has been
> selected, no metrics validated, and no baselines measured.
>
> **Gated on:** `../research/reports/08_evaluation/`

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

### Metric validity for Tigrinya
Which metrics are trustworthy here and how that was established. This is the
foundational question — see `metrics.md`.

### Evaluation sets
What we use for each capability, where it came from, and how it is maintained.
See `datasets.md`.

### Contamination control
How train/eval separation is guaranteed structurally, and how contamination
would be detected after the fact.

### Baselines
What we measure against. Without a baseline a number is not a result.

### Human evaluation
Where it is required, how it is run, how raters are recruited and calibrated,
and what it costs.

### Dialectal and register coverage
How evaluation reflects real variation rather than one narrow slice.

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
