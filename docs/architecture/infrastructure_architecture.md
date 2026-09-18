# Infrastructure Architecture

> **Status: designed, with one input missing** (DEC-018, DEC-019 — 2026-08-17).
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

## Still to be designed

Covered below: the cost model, deployment mode, CI, orchestration, and compute
profile. **These are genuinely undone**, and are listed rather than left implied:

| Area | Blocked on |
| --- | --- |
| **Deployment target** | **A-14** (Tier 2 cold start) and **A-02** — nothing can be chosen without them |
| **Containerisation** | The target. Image size matters directly: Tier 0's 3.03 s cold start is 98.7% one dependency |
| Networking and ingress | The target |
| Secrets and configuration | Nothing is deployed and no secret exists yet |
| Monitoring, logging, alerting | The target. **The cheapest adequate option, not the most complete one** |
| Backup and disaster recovery | Data lives in git at present, which is the whole story at this size |
| Scaling path | **Documented, not built**, when load is real |

## Cost model — GB-hours, not dollars

Vendor pricing is volatile and was not verifiable when this was written, so cost
is modelled in **resource-hours**. The arithmetic survives price changes.

| Tier | Footprint | Always-warm |
| --- | ---: | ---: |
| **0** — primitives | **0.113 GB** *(measured; 0.072 GB was the estimate)* | **82.8 GB-h/month** |
| **1** — + embeddings | 0.191 GB | 139.4 GB-h/month |
| **2** — + translation | 1.593 GB | **1,162.9 GB-h/month** |

**Tiering (DEC-013) cuts standing resource-hours by ~14×** versus one merged
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
| CI enforces checkable rules | DEC-018 | 2026-08-17 | Six rules implemented and locally verified — ⚠️ **not installed (A-15)** |
| Tier 2 mode by measured duty cycle | DEC-019 | 2026-08-17 | Rule stated; input (**A-14**) still missing |
| Tier by resource profile | DEC-013 | 2026-08-10 | ~14× standing-cost saving confirms it (22× was the pre-build estimate) |
| Single model runtime | DEC-014 | 2026-08-10 | CTranslate2 (MIT), CPU int8 — no GPU tier, no second runtime |
| Machine-checkable experiment artefacts | DEC-016 | 2026-08-13 | The reproducibility job doubles as a dependency regression test |
| Library-first | DEC-012 | 2026-08-10 | Services are thin wrappers, so a tier is a deployment unit rather than a capability boundary |

## What future contributors should add

The deployment target, once **A-14** (Tier 2 cold start) and **A-02** resolve.
Keep the cost model in GB-hours — vendor pricing is unverifiable from here and
volatile, while the arithmetic survives price changes. An architecture document
that has drifted from reality is worse than none, because people trust it.
