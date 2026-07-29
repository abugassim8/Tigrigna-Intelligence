# System Overview

> **Status: not designed.** This document is a scaffold. It contains **no design
> decisions, no technology selections, and no recommendations.** Anything that
> looks like a conclusion here is a placeholder heading.
>
> **Gated on:** `docs/research/reports/05_architecture/`, which in turn depends on `00_project_definition` and `04_model_strategy`.

## Purpose of this document

The top-level view of the platform: what the major components are, how they relate, and how a request flows through the system. It is the map that orients everything else in this directory.

## Why this document exists

Someone new to the project — or an AI session with no prior context — needs one document that explains the shape of the system before descending into any particular part. Without it, understanding the platform requires reading everything.

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

**P-11** services are independent · **P-6** optimise for low volume · **P-7** prefer boring technology

## Sections to be completed

### Component inventory
The major components and what each is responsible for.

### Component relationships
How components depend on and communicate with each other.

### Request lifecycle
End-to-end flow for a representative request through the system.

### Service boundaries
Where the lines are drawn and why — see **P-11**, services are independent.

### Shared vs. per-service infrastructure
What is common, what is isolated, and what that costs.

### Deployment topology
What runs where.

### Failure modes
What breaks, what happens when it does, and which failures are acceptable.

### Evolution path
How the system changes as capabilities are added — and how a capability gets
replaced without rewriting the platform.

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
