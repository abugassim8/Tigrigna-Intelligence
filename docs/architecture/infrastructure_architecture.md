# Infrastructure Architecture

> **Status: designed, with one input missing** (DEC-018, DEC-019 — 2026-08-03).
> The cost model and enforcement are settled. **Tier 2's deployment mode is
> deliberately not fixed** — it depends on a cold-start measurement we do not
> have (**A-14**).
>
> **Evidence:** `../research/reports/10_infrastructure/001-cost-model-and-enforcement.md`

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

---

## Cost model — GB-hours, not dollars

Vendor pricing is volatile and was not verifiable when this was written, so cost
is modelled in **resource-hours**. The arithmetic survives price changes.

| Tier | Footprint | Always-warm |
| --- | ---: | ---: |
| **0** — primitives | 0.072 GB | **52.6 GB-h/month** |
| **1** — + embeddings | 0.191 GB | 139.4 GB-h/month |
| **2** — + translation | 1.593 GB | **1,162.9 GB-h/month** |

**Tiering (DEC-013) cuts standing resource-hours by 22×** versus one merged
always-warm process, while keeping the latency-sensitive path warm.

## Deployment mode — a rule, not a choice

**DEC-019.** Tier 2 is scale-to-zero *or* always-warm according to measured duty
cycle:

> Keep Tier 2 warm when sustained request rate exceeds
> `3600 / (cold_start_seconds + service_seconds)` per hour.

⚠️ **Cold start is unmeasured (A-14), and the answer swings hard on it:**

| Cold start | Break-even | req/min |
| ---: | ---: | ---: |
| 5 s | 514/hour | 8.6 |
| 10 s | 300/hour | 5.0 |
| **60 s** | **58/hour** | **1.0** |

The pathological case: at ~1 req/min with slow cold start, Tier 2 is busy 100%
of the hour — **warm in all but name, while still paying cold-start latency every
request.** Fixing scale-to-zero blindly would produce exactly that.

## Continuous integration

`ci/verify.yml` (**DEC-018**) implements every decision-log rule that can be
checked mechanically. ⚠️ **It is not yet installed** — see `ci/README.md` and
**A-15**:

| Check | Rule |
| --- | --- |
| Experiments re-run and diff byte-identically | DEC-016 |
| Screening fails closed without licence/eval-set | DEC-015 |
| Known-corrupted corpus still fails the quality gate | DEC-015 |
| Every research report has a summary | DEC-001 |
| Summaries stay within two pages | DEC-001 |
| Every decision names rejected alternatives | CONTRIBUTING |

**The reproducibility job doubles as a dependency regression test.** If `epitran`,
`tokenizers`, or `sacrebleu` changes behaviour, an experiment stops reproducing
and CI reports it — the only guard between DEC-007's amended numbers and silent
drift.

## What we deliberately do not build

Recorded so it is not built later by reflex:

| Not building | Why |
| --- | --- |
| Orchestration (Kubernetes etc.) | Three tiers, one runtime, low volume — continuous expense buying nothing (**P-7**) |
| GPU infrastructure | DEC-014's runtime is CPU int8; DEC-017's training is blocked on data, not hardware |
| Model registry | DEC-011 adopts published checkpoints; DEC-017 means we do not produce our own |
| Vector database | Retrieval is not in DEC-006's minimum platform |
| Autoscaling curves | The interesting decision is binary and rate-dependent (DEC-019), not a curve |

**What we do need:** a container runtime, object storage for model weights, and
CI. Everything else is premature.

## Open questions

- **What is Tier 2's cold start?** (**A-14**) Everything about deployment mode
  hangs on it.
- Is the assumed 2 s service time realistic?
- Does CI pass on a real runner? Logic is verified locally only.
- Which hosting target — depends on A-14 and on **A-02**.

## Decision log for this area

| Decision | ID | Date | Summary |
| --- | --- | --- | --- |
| CI enforces checkable rules | DEC-018 | 2026-08-03 | Six rules implemented and locally verified — ⚠️ **not installed (A-15)** |
| Tier 2 mode by measured duty cycle | DEC-019 | 2026-08-03 | Rule stated; input (**A-14**) still missing |
| Tier by resource profile | DEC-013 | 2026-08-03 | 22× standing-cost saving confirms it |
