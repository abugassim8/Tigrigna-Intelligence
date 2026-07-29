# ML Architecture

> **Status: not designed.** This document is a scaffold. It contains **no design
> decisions, no technology selections, and no recommendations.** Anything that
> looks like a conclusion here is a placeholder heading.
>
> **Gated on:** `docs/research/reports/04_model_strategy/`, `06_ml_pipeline/`, and `08_evaluation/`.

## Purpose of this document

How models are organised, served, versioned, and updated: the structure of the machine learning layer, from artefact storage through inference serving to quality monitoring.

## Why this document exists

Model choices will change repeatedly as research progresses. The ML architecture determines whether that is a routine update or a rewrite. It also determines whether reproducibility holds across the platform, since reproducibility is a pipeline property rather than a per-model one.

## How to use it

- **Reading:** this is the current design of record for this area. Where it
  conflicts with a decision in
  [`../decisions/DECISIONS.md`](../decisions/DECISIONS.md), the decision wins and
  this document needs updating.
- **Writing:** update it when an Architect-stage decision changes the design. Do
  not use it as a scratchpad for ideas — exploratory thinking belongs in
  `../research/`. This document holds what we have *decided*, not what we are
  *considering*.
- **Every design element here must trace to a decision record.** Design without a
  recorded decision behind it is how projects end up unable to explain
  themselves.

## Relevant principles

**P-1** reuse before building · **P-2** train only for proprietary advantage · **P-4** evaluation before capability · **P-5** reproducibility

## Sections to be completed

### Model inventory
Which models serve which capabilities, with version and licence.

### Model storage and registry
Where artefacts live, how they are versioned and retrieved.

### Inference serving
How each capability is served, and on what hardware. Cost per request is a
first-class concern here — see **P-6**.

### Batching, caching, and quantisation
Cost and latency levers, and what each trades away.

### Model versioning and promotion
The path from `experiments/` to `services/`, and what gates it.

### Automated evaluation gates
What must pass before a model is promoted — see **P-4**.

### Rollback
How a bad model is reverted, and how quickly.

### Quality monitoring
How production regression would be detected rather than reported by a user.

### Fallback behaviour
What happens when a model is unavailable or returns low-confidence output.

## Open questions

To be populated by research. Record questions here as they surface, even before
they can be answered — a written open question is worth more than one someone is
carrying around in their head.

## Decision log for this area

| Decision | ID | Date | Summary |
| --- | --- | --- | --- |
| — | — | — | *No decisions recorded* |

## What future contributors should add

The actual design, once research supports it. Diagrams where they clarify.
Rationale linked to decision records. Keep it current — an architecture document
that has drifted from reality is worse than none, because people trust it.
