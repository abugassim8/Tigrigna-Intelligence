# Infrastructure Architecture

> **Status: not designed.** This document is a scaffold. It contains **no design
> decisions, no technology selections, and no recommendations.** Anything that
> looks like a conclusion here is a placeholder heading.
>
> **Gated on:** `docs/research/reports/10_infrastructure/` and `05_architecture/`.

## Purpose of this document

How the platform is deployed and operated: compute, containers, orchestration, networking, monitoring, secrets, and the operational cost of running it.

## Why this document exists

Low operating cost is a stated priority and infrastructure is where it is honoured or lost. The governing question for this project is cost at *low* volume sustained over years — not cost at scale, which is what most infrastructure guidance optimises for. Over-building here is a continuous expense that buys nothing.

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

**P-6** optimise for low volume · **P-7** prefer boring technology · **P-12** write it down

## Sections to be completed

### Deployment targets
Where things run, and what the realistic options are at this budget.

### Containerisation
Image strategy, build pipeline, size and cold-start implications.

### Orchestration
Whether Kubernetes is justified at our size, or something simpler is better —
see **N-8**, **P-6**.

### Compute profile
CPU vs GPU per capability, and what each actually requires.

### Cost model
Monthly cost at realistic volume, broken down by component, with assumptions
stated.

### Scale-to-zero and cold starts
Behaviour and tradeoffs per capability.

### Networking and ingress

### Secrets and configuration management
Environments, rotation, and what never enters git.

### Monitoring, logging, and alerting
The cheapest adequate option, not the most complete one.

### Backup and disaster recovery

### Scaling path
What we would do when load is real — documented, not built.

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
