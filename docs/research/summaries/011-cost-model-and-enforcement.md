# Summary: Infrastructure — Cost in Resource-Hours, Rules That Enforce Themselves

| Field | Value |
| --- | --- |
| **Summary ID** | `011-cost-model-and-enforcement` |
| **Full report** | `docs/research/reports/10_infrastructure/001-cost-model-and-enforcement.md` |
| **Date** | 2026-08-03 |
| **Status** | Current |
| **Confidence** | High on arithmetic and CI; **cold start unmeasured, and it is decisive** |

**One-line answer:** Tiering cuts standing resource cost **22×**, but **Tier 2's
deployment mode cannot be decided yet** — the scale-to-zero break-even is as low
as **~1 request/minute** if cold start is slow, and we have never measured it.
Separately, a CI workflow is written for the decision-log rules nothing was
checking — **though it is not yet installed (A-15)**.

---

## Key Findings

- **No dollar figures in this domain, deliberately.** Vendor pricing is
  unverifiable from here and volatile. Cost is modelled in **GB-hours** and as
  **break-even rates** — arithmetic that stays true whatever anyone charges.

- **Tiering cuts standing cost 22×** — DEC-013 was decided on the memory spread
  and holds on cost too:

  | Shape | Standing cost |
  | --- | ---: |
  | Merged, always warm | **1,162.9 GB-h/month** |
  | Tier 0 warm + Tier 2 to zero | **52.6 GB-h/month** + per-request |

- **⚠️ Tier 2's deployment mode is NOT decidable, and my first pass got it
  wrong.** I concluded scale-to-zero "wins across the whole plausible range" —
  which contradicted the table I had just computed.

  | Cold start | Break-even | req/min |
  | ---: | ---: | ---: |
  | 5 s | 514/hour | 8.6 |
  | 10 s | 300/hour | 5.0 |
  | **60 s** | **58/hour** | **1.0** |

  At a 60 s cold start, break-even is **about one request per minute** — a rate a
  modestly-used service exceeds easily. Above it, always-warm is **both cheaper
  and faster**. At 1 req/min with slow cold start, Tier 2 is busy 100% of the
  hour: warm in all but name, *and* paying cold-start latency every request —
  the worst of both.

  **DEC-013's tiering is unaffected; only Tier 2's *mode* is contingent.**
  → **DEC-019**, and measuring cold start becomes **A-14**.

- **⭐ The decision log has rules nothing checks — and that has already failed
  once.** DEC-008 spent three months as policy with no mechanism, silently
  ignored, found only by measurement. Five newer rules were in the same position:

  | Rule | Source |
  | --- | --- |
  | Experiments reproduce byte-identically | DEC-016 |
  | Datasets carry a screening record | DEC-015 |
  | Every report has a summary | DEC-001 |
  | Summaries stay within two pages | DEC-001 |
  | Every decision names rejected alternatives | CONTRIBUTING |

  `ci/verify.yml` implements all five. ⚠️ **NOT YET ACTIVE** — GitHub refused the
  push without `workflows` permission, so it awaits a one-command install
  (**A-15**). Until then DEC-018 is itself unenforced. **Every check was run
  locally before commit:** 3 experiments byte-identical ✅ · screening fails closed ✅ ·
  corrupted sample still detected ✅ · 10 summaries under limit ✅ · 17 decisions
  have rejected alternatives ✅. → **DEC-018**

- **The reproducibility job doubles as a dependency regression test.** If
  `epitran`, `tokenizers`, or `sacrebleu` changes behaviour, an experiment stops
  reproducing and CI says so — the only thing standing between DEC-007's amended
  numbers and silent drift.

- **What infrastructure this project does *not* need**, recorded so it is not
  built: no orchestration layer (P-7), no GPU (DEC-014 is CPU int8; DEC-017's
  training is blocked on data anyway), no model registry (we adopt, not produce),
  no vector DB yet, no autoscaling curve. **A container runtime, object storage
  for weights, and CI.** Everything else is premature.

## Important Decisions

| Decision | ID | Status |
| --- | --- | --- |
| CI enforces the machine-checkable rules in the decision log | DEC-018 | Accepted |
| Tier 2 deployment mode set by measured duty cycle, not fixed in advance | DEC-019 | Accepted |

## Rejected Alternatives

| Alternative | Rejected because |
| --- | --- |
| Fixing Tier 2 as scale-to-zero now | Break-even is ~1 req/min at slow cold start — the answer depends on a number we have not measured |
| Fixing Tier 2 as always-warm now | Equally unfounded in the other direction; at genuinely low volume it wastes 1,162.9 GB-h/month |
| Costing infrastructure in dollars | Vendor pricing is unverifiable here and volatile; GB-hours survive price changes |
| Kubernetes / orchestration | Three tiers, one runtime, low volume — a continuous expense buying nothing (P-7) |
| Leaving DEC-015/DEC-016 unenforced | DEC-008 already demonstrated what happens: silently ignored for three months |
| Quietly dropping the workflow when the push was refused | The work would have been lost and DEC-018 would have claimed enforcement that did not exist — the exact failure it names |
| GPU infrastructure | DEC-014's runtime is CPU int8; DEC-017's training is blocked on data, not hardware |

## Important Numbers

| Metric | Value | Basis |
| --- | --- | --- |
| Tier 0 always-warm | **52.6 GB-h/month** | arithmetic |
| Tier 2 always-warm | **1,162.9 GB-h/month** | arithmetic |
| **Standing-cost saving from tiering** | **22×** | arithmetic |
| Break-even at 10 s cold start | 300 req/hour | arithmetic |
| **Break-even at 60 s cold start** | **58 req/hour (~1/min)** | arithmetic |
| CI checks passing locally | **5 of 5** | `[verified]` |

## Recommended Next Steps

1. **Measure Tier 2 cold start (A-14).** It decides DEC-019 and nothing else can
   settle it.
2. **Install the workflow (A-15)** — one command; until then six rules are
   enforced by nobody, and DEC-018 is policy without mechanism.
3. **Choose a deployment target** once A-14 and A-02 resolve.
4. **Add a screening-record check to CI** once datasets carry committed records.
5. **Re-run the break-even model** with measured service time, not the assumed 2 s.

## References

1. `docs/research/summaries/008-architecture-tiers-and-runtime.md` — tier footprints
2. `ci/verify.yml` — the enforcement mechanism (**awaiting install, A-15**)
3. Local CI verification runs `[verified]` 2026-08-03

---

**Open questions / uncertainty:** What is Tier 2's actual cold start — everything
about deployment mode hangs on it. Is 2 s a realistic service time? Does CI pass
on a real runner? Which hosting target, once A-02 tells us who is calling this?
