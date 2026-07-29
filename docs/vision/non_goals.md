# Non-Goals

## Purpose of this document

An explicit list of things this project is **not** doing.

**Why it exists:** Scope creep in a project this broad is not a hypothetical
risk; it is the default outcome. Every capability we build suggests three
adjacent capabilities, each individually reasonable. Stating non-goals makes
declining them a decision already made rather than an argument to be had every
time.

Non-goals also protect focus in a specific way: they let contributors say "no"
without seeming unambitious, because the "no" is the project's position rather
than a personal judgement.

**How to use it:** Check proposals against this list. If a proposal is here, it
needs an argument for why the non-goal should change — not just an argument that
the proposal is good. Good ideas that are out of scope are still out of scope.

**What future contributors should add:** New non-goals as scope questions get
settled. The "what should not be built?" answer from every research report
(see `../research/CHECKLIST.md`) is the natural source. Include the reason —
a non-goal without a reason gets overturned by whoever argues hardest.

---

## Hard non-goals

These are structural. Changing one would make this a different project.

### N-1. This is not a news application

Not a news app, reader, aggregator, feed, or media platform. This is the most
important non-goal because it is the most likely drift direction: Tigrinya
content processing naturally suggests content products, and the suggestion is
wrong for us.

*The test:* if we are building something an end user opens to consume content,
we have drifted. We build what content products are built *on*.

### N-2. This is not a consumer product

No consumer-facing app, no chat interface as the primary deliverable, no social
features. Our users are developers, researchers, and institutions who build
things. If we build a demo, it is a demo — it demonstrates the platform, it is
not the platform.

### N-3. This is not a general-purpose multilingual platform

We are building for Tigrinya. Other languages appear only where they serve
Tigrinya capability — translation pairs, cross-language retrieval, transfer
learning from related languages. "We should support Amharic too" is a scope
change requiring a decision record, not an obvious extension.

### N-4. This is not a research lab producing papers

Research here exists to enable building. If a research direction is intellectually
interesting but does not lead to a decision or a capability, it is not our work.
Publishing is welcome as a by-product, never as the objective.

---

## Current-phase non-goals

These are "not now" rather than "not ever". Each names what would change it.

### N-5. We are not training foundation models from scratch

Adaptation and fine-tuning of existing models, yes — where justified. Pre-training
a base model from scratch, no. The cost, data requirements, and permanent
maintenance burden are not justifiable against the alternatives available.

*Would change if:* no existing base model can be adapted to handle Ge'ez script
and Tigrinya morphology adequately, **and** the capability is essential, **and**
the cost is credibly within reach. All three, not any one.

### N-6. We are not building speech capability yet

No ASR, no TTS, no speech translation. Speech is a substantial and largely
separate infrastructure problem with its own data requirements. Adding it now
would halve the attention available for text, which is not yet solved.

*Would change if:* text infrastructure reaches a stable, useful state and speech
becomes the highest-leverage remaining gap.

### N-7. We are not building OCR or handwriting recognition

Ge'ez-script OCR is a real and valuable problem — and a computer vision problem
with a different skill set, different data needs, and different evaluation.
Better solved by a project focused on it, ideally one we can then consume.

*Would change if:* it becomes the binding constraint on data acquisition and no
usable external option exists.

### N-8. We are not optimising for scale we do not have

No architecture chosen for hypothetical millions of requests. We optimise for
low cost at low volume, and re-architect when there is real load. Premature
scaling is expensive, and the expense is paid continuously.

*Would change if:* sustained real traffic makes the current architecture the
bottleneck.

### N-9. We are not building a hosted commercial service yet

No billing, no accounts, no SLAs, no support tier. Business model questions are
`11_business` research and premature to answer.

*Would change if:* research establishes that hosted service is the right
sustainability model and there is demand to serve.

### N-10. We are not building UI or tooling beyond developer needs

No web dashboards, admin panels, or annotation UIs beyond the minimum required
to do the data work. Where a tool is needed, buy or adopt it before building it.

*Would change if:* annotation volume makes a purpose-built tool cheaper than the
alternatives, established by actual measurement.

---

## How to challenge a non-goal

1. Say which non-goal you are challenging and why the stated reason no longer
   holds.
2. Show what changed — new evidence, new constraint, new opportunity.
3. Cost the change, including opportunity cost against current goals.
4. Record it in `../decisions/DECISIONS.md` if accepted, and update this file.

"It would be cool" is not a challenge. Most things would be cool.
