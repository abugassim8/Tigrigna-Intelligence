# Infrastructure: A Cost Model in Resource-Hours, and Rules That Should Enforce Themselves

| Field | Value |
| --- | --- |
| **Report ID** | `001-cost-model-and-enforcement` |
| **Domain** | `10_infrastructure` |
| **Stage** | Scout → Analyst → Architect |
| **Date** | 2026-08-03 |
| **Status** | Accepted |
| **Summary** | `docs/research/summaries/011-cost-model-and-enforcement.md` |
| **Related decisions** | **DEC-018**, **DEC-019**; qualifies DEC-013; enforces DEC-015, DEC-016, DEC-001 |

---

## Objective

Decide how the platform is deployed and operated, under **A-008** (affordable at
low volume) and **P-6** (optimise for low volume).

**Method note.** Vendor pricing is not verifiable from this environment and
changes constantly, so **no dollar figure appears in this report**. Cost is
modelled in **GB-hours**, which is vendor-independent, and the deployment
question is expressed as a **break-even** — arithmetic that stays true whatever
anyone charges.

---

## Finding 1 — Tiering cuts standing resource cost 22×

Monthly resource-hours if a tier is kept always-warm (730 h/month):

| Tier | Footprint | Always-warm |
| --- | ---: | ---: |
| **0** — primitives | 0.072 GB | **52.6 GB-h** |
| **1** — + embeddings | 0.191 GB | 139.4 GB-h |
| **2** — + translation | 1.593 GB | **1,162.9 GB-h** |

Against the **DEC-013 counterfactual** — one merged always-warm process:

| Shape | Standing cost |
| --- | ---: |
| Merged, always warm | **1,162.9 GB-h/month** |
| Tier 0 warm + Tier 2 to zero | **52.6 GB-h/month** + per-request |

**Tiering cuts standing resource-hours by 22× while keeping the latency-sensitive
path warm.** DEC-013 was decided on the memory spread; it holds on cost too.

## Finding 2 — ⚠️ Tier 2's deployment mode is **not** decidable yet, and I nearly said otherwise

DEC-013 states Tier 2 "may scale to zero." Testing that against arithmetic
produced a correction worth recording.

Break-even is where per-request GB-hours equal a month kept warm. With ~2 s of
actual service time and **cold start left as a free parameter, because it is
unmeasured**:

| Cold start | s/request | Break-even | req/hour | req/min |
| ---: | ---: | ---: | ---: | ---: |
| 1 s | 3 s | 876,000/mo | 1,200 | 20.0 |
| 5 s | 7 s | 375,429/mo | 514 | 8.6 |
| 10 s | 12 s | 219,000/mo | 300 | 5.0 |
| 30 s | 32 s | 82,125/mo | 112 | 1.9 |
| **60 s** | 62 s | 42,387/mo | **58** | **1.0** |

**Below the break-even rate scale-to-zero uses fewer resource-hours; above it,
always-warm is both cheaper and faster.**

**The correction:** my first pass concluded that scale-to-zero "wins across the
whole plausible range." **That was wrong, and it contradicted the table I had
just computed.** At a 60 s cold start the break-even is roughly **one request per
minute** — a rate a modestly-used translation service would exceed easily.

Stated as duty cycle, which is more intuitive: scale-to-zero is cheaper exactly
while the service is idle most of the time. At 1 req/min with a 60 s cold start,
Tier 2 is busy **100% of the hour** — it is warm in all but name, while also
paying cold-start latency on every request. That is the worst of both.

**So the deployment mode is a function of a number we do not have.** DEC-013's
tiering is unaffected — only Tier 2's *mode* is contingent. → **DEC-019**, and
measuring cold start becomes **A-14**.

## Finding 3 — The decision log has rules nothing checks, and that has already failed once

**DEC-008 spent three months as policy with no mechanism and was silently ignored
the entire time** — screening reimplemented three times, differently, with zero
files in `scripts/data_processing/`. That was found by measurement in
`06_ml_pipeline`, not by anyone noticing.

Several newer rules are in exactly the same position — true, agreed, and enforced
by nobody:

| Rule | Source | Checkable? |
| --- | --- | --- |
| Experiments reproduce byte-identically | DEC-016 | ✅ yes |
| Datasets carry a screening record | DEC-015 | ✅ yes |
| Every report has a summary | DEC-001 | ✅ yes |
| Summaries stay within two pages | DEC-001 | ✅ yes |
| Every decision names rejected alternatives | CONTRIBUTING | ✅ yes |

**`ci/verify.yml` implements all five, and every check was run locally before
commit.** ⚠️ **It is not yet running:** GitHub refused the push (an app token
cannot write `.github/workflows/` without `workflows` permission), so it awaits a
one-command install (**A-15**). **Until then DEC-018 is itself policy without
mechanism** — the very failure it addresses.


| Check | Result |
| --- | --- |
| 3 experiments re-run and diffed | ✅ all byte-identical |
| Screening fails closed with no licence/eval-set | ✅ correctly fails |
| Known-corrupted sample still detected | ✅ still fails quality |
| 10 summaries under the word limit | ✅ all pass |
| 17 decisions have rejected alternatives | ✅ all pass |

**The reproducibility job doubles as a dependency regression test.** If `epitran`,
`tokenizers`, or `sacrebleu` changes behaviour, an experiment stops reproducing
and CI says so — which is the only thing standing between DEC-007's amended
numbers and silent drift.

→ **DEC-018.**

## Finding 4 — What the infrastructure does *not* need

Recorded so it is not built:

- **No orchestration layer.** Three tiers, one runtime, low volume. Kubernetes
  would be a continuous expense buying nothing (**P-7**).
- **No GPU.** DEC-014's CTranslate2 path is CPU int8; DEC-017 puts training
  behind a ladder that is blocked on data anyway.
- **No model registry.** DEC-011 adopts published checkpoints; DEC-017 means we
  are not producing our own.
- **No feature store, no vector DB yet.** Retrieval is not in DEC-006's minimum
  platform.
- **No autoscaling policy beyond scale-to-zero-or-warm.** Finding 2 shows the
  interesting decision is binary and rate-dependent, not a scaling curve.

**The infrastructure this project needs is a container runtime, object storage
for weights, and CI.** Everything else is premature.

## Limits of this report

- **No dollar figures**, deliberately. Vendor pricing is unverifiable here and
  volatile; GB-hours and break-even rates survive price changes.
- **Cold start is unmeasured**, which is precisely why Finding 2 cannot conclude.
  The 2 s service-time assumption is also unmeasured.
- **⚠️ CI is written, verified locally, and NOT INSTALLED.** GitHub refused the
  push without `workflows` permission (**A-15**). The shell logic and tools were
  exercised by hand; GitHub Actions has never run it. **DEC-018 is unenforced
  until installed.**
- **No deployment target chosen.** That depends on cold-start behaviour
  (**A-14**) and on A-02's answer about who is using this.

---

## Decisions arising

- **DEC-018** — CI enforces the machine-checkable rules in the decision log.
- **DEC-019** — Tier 2's deployment mode is set by measured duty cycle against a
  stated rule, not fixed in advance.

**Evidence:** resource arithmetic from
`docs/research/summaries/008-architecture-tiers-and-runtime.md`; CI checks run
locally `[verified]` 2026-08-03.
