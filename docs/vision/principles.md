# Engineering Principles

## Purpose of this document

The operating principles that govern technical decisions on this project.

**Why it exists:** Principles are decision-compression. Rather than reasoning
from first principles on every choice — and reaching different conclusions
depending on who is reasoning — we agree on a small number of defaults and apply
them consistently. This makes decisions faster and, more importantly, makes them
*predictable* to other contributors.

**How to use it:** When facing a technical choice, check whether a principle
applies. Deviating from one is allowed but must be argued explicitly and
recorded in `../decisions/DECISIONS.md`.

**What future contributors should add:** Principles earned from experience. A
principle that came from a real mistake is worth more than one that sounded
sensible. Retire principles that stop being useful — an unfollowed principle
corrodes the credibility of the ones that are followed.

---

## The priority order

When principles conflict, resolve in this order:

**1. Data quality → 2. Evaluation → 3. Reproducibility → 4. Low operating cost
→ 5. Maintainability**

This ordering is from [`../../PROJECT_CONTEXT.md`](../../PROJECT_CONTEXT.md) and
is the tiebreaker for genuinely hard calls.

---

## P-1. Reuse before building

The default answer to "should we build this?" is **no** — find what exists first.
Building is justified only when nothing adequate exists, or what exists cannot be
adapted, or the thing genuinely is our differentiator.

*Why:* every component we build is one we maintain forever. In a small project,
maintenance capacity is the real constraint, not build capacity.

## P-2. Train only for proprietary advantage

Training is a last resort. The proposal must articulate what advantage the
trained model creates that adaptation cannot, and must cost the alternative of
not training. See A-004 and A-005.

*Why:* a trained model carries data cost, compute cost, evaluation cost, and
permanent maintenance burden. It is a liability that must earn its keep.

## P-3. Data quality beats model sophistication

Given a fixed budget, spend it on better data before better models. For a
low-resource language this is not close — data quality is the binding constraint
on nearly everything.

*Why:* no model exceeds the quality of what it learned from. In high-resource
settings the model choice matters because the data is abundant; here it is not.

## P-4. Evaluation comes before capability

Build the way to measure a thing before building the thing. A capability without
evaluation cannot be improved, compared, or honestly described.

*Why:* this is the easiest principle to skip under delivery pressure and the most
expensive to have skipped. Retrofitting evaluation onto a shipped capability
means discovering, late, that it never worked.

## P-5. If it is not reproducible, it did not happen

Pin versions. Fix seeds. Record hardware. Commit configs. Any result that cannot
be reproduced from this repository does not count as a result.

*Why:* irreproducible results cannot be built on, and quietly poison every
decision that cites them.

## P-6. Optimise for low volume

Design for the cost of running continuously at low usage, not for hypothetical
scale. Re-architect when there is real load, not before.

*Why:* premature scaling costs money continuously and complicates everything it
touches. See A-008 and N-8.

## P-7. Prefer boring technology

Choose the well-documented, widely-used, actively-maintained option. Novelty is a
cost paid in debugging, hiring, and abandonment risk.

*Why:* interesting infrastructure fails in interesting ways, at inconvenient
times, with nobody to ask.

## P-8. Measure before claiming

No performance, quality, or capability claim without a number and a method behind
it. This applies to internal documents as much as external ones.

*Why:* unverified claims propagate, get cited, and eventually get discovered —
usually by a user rather than by us.

## P-9. Licensing is a hard constraint

Verify the licence of every model, dataset, and dependency before adopting it.
Unclear licensing is disqualifying.

*Why:* we are infrastructure others build on. We cannot pass on rights we do not
have, and a downstream user inheriting our licensing problem is a serious
failure. See A-009.

## P-10. Morphology is not an implementation detail

Tigrinya's morphology affects tokenization, retrieval, embeddings, and search
quality. Approaches designed for analytic languages need adaptation, not
assumption.

*Why:* getting this wrong at the primitive layer propagates into every capability
above it, and is expensive to correct later. Flagged as A-007 — currently an
assumption pending verification.

## P-11. Services are independent

Each service under `services/` runs, tests, and deploys on its own. Cross-service
imports are a design smell.

*Why:* independent services can be replaced when research changes our mind about
how they should work — which, this early, it will.

## P-12. Write it down

Decisions go in `DECISIONS.md`. Findings go in `docs/research/`. Rejections go in
`rejected_options.md`. Assumptions go in `assumptions.md`.

*Why:* undocumented knowledge is repeatedly rediscovered at full cost. This is
the single largest avoidable expense on a project structured like this one.

## P-13. Negative results are results

"This does not work", "this does not exist", "this is unusable for Tigrinya" —
write these down as carefully as positive findings.

*Why:* unrecorded negative results are rediscovered at the same cost as the
original search, by someone who does not know it was already done.

## P-14. State uncertainty honestly

Distinguish verified from believed from unknown. "I could not determine this" is
a legitimate and useful output.

*Why:* blurring confidence levels destroys the reader's ability to calibrate on
anything else in the document — including the parts that are solid.

---

## Applying these

Principles are defaults, not laws. Deviating is fine when justified; deviating
silently is not. If you deviate, record it in `../decisions/DECISIONS.md` with
the reasoning — a documented exception strengthens a principle, an undocumented
one erodes it.
