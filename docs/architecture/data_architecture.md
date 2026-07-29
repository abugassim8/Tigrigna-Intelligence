# Data Architecture

> **Status: not designed.** This document is a scaffold. It contains **no design
> decisions, no technology selections, and no recommendations.** Anything that
> looks like a conclusion here is a placeholder heading.
>
> **Gated on:** `docs/research/reports/03_data_strategy/` and `02_linguistics`.

## Purpose of this document

How data moves and lives in the platform: ingestion, storage, processing pipelines, versioning, and lineage — from raw source to served artefact.

## Why this document exists

Data quality is the first priority in the project's philosophy, and data architecture is where that priority becomes concrete or gets quietly abandoned. Lineage matters especially here: for a low-resource language, knowing exactly which data produced which artefact is what makes results reproducible and licensing defensible.

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

**P-3** data quality beats model sophistication · **P-5** reproducibility · **P-9** licensing is a hard constraint

## Sections to be completed

### Data sources and ingestion
Where data comes from and how it enters the system.

### Storage layers
Raw, processed, evaluation, and derived data. What is stored where, and why.

### Processing pipelines
Transformation steps from raw to usable. Must be script-driven and repeatable —
see `scripts/data_processing/`.

### Normalisation
Ge'ez script normalisation, orthographic variation handling, encoding rules.
Depends on `02_linguistics` findings.

### Versioning and lineage
How a data artefact traces back to its sources and transformations. Required for
**P-5**.

### Train/eval separation
How contamination is prevented structurally, not by convention. This is the one
form of sloppiness that invalidates everything downstream.

### Licence and provenance tracking
How licence obligations travel with the data — see **P-9**, **A-009**.

### Retention, backup, and durability

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
