# Roadmap — 1 Year

> ⚠️ **Superseded as a plan, kept as a record.** This was written **before any
> research** — as a direction-holding exercise, explicitly not a commitment. All 13 research domains are now complete, two packages are
> built, and **[`READINESS_PLAN.md`](READINESS_PLAN.md) is the plan of record.**
>
> Still useful as direction. Read `READINESS_PLAN.md` for what is actually next, and treat anything dated here as intent.

## Purpose of this document

The one-year horizon: what the platform could plausibly be after a year of work.

**Why it exists:** To hold a direction without pretending to precision.
Year-scale planning before any research is done is genuinely low-value, but
having *no* long view means near-term decisions get made without considering
where they lead. This document exists for that second reason and no other.

**How to use it:** As direction, not as a plan. Do not schedule against it.

**What future contributors should add:** Replace this entirely once the master
blueprint exists and the first services are real. At that point a one-year plan
can be built from measured throughput rather than guesswork.

> **Horizon: 2026-07-29 → 2027-07-29**
> **Confidence: very low.** Written before any research on a project with wide
> scope in a domain where information is scarce. Treat as direction only.

---

## What a good year looks like

Not a feature list — a description of a state worth reaching.

**The platform is real and someone is using it.** A small number of capabilities
work well enough that someone outside the project has built something on them.
This matters more than breadth: infrastructure succeeds when others build on it.

**Quality claims are defensible.** Every capability has an evaluation set, a
metric validated for Tigrinya, and a measured baseline. Nothing is claimed that
cannot be shown.

**The data foundation is solid.** A documented, licensed, cleanly processed
Tigrinya corpus with reproducible pipelines and clear provenance — an asset that
retains value regardless of which models come and go.

**Operating cost is sustainable.** The platform runs continuously at a cost the
project can carry indefinitely (**A-008**, **P-6**).

**It is genuinely usable.** A developer can install an SDK, make a call, and get
a useful result without understanding Tigrinya morphology.

**The project is maintainable.** Documented decisions, reproducible results, and
enough structure that a new contributor can become productive without a founder
explaining things.

---

## Plausible capability state

Deliberately vague. Which capabilities land depends on what the research finds.

| Tier | Description |
| --- | --- |
| **Likely** | Evaluation infrastructure · foundational primitives (tokenization, morphology, lemmatization) · embeddings · basic API |
| **Possible** | Semantic search · translation · spell correction · MCP server · Python SDK |
| **Uncertain** | Grammar checking · NER · cross-language retrieval · JavaScript SDK |
| **Unlikely** | Knowledge graph · entity linking · RAG · summarization · question answering |

The ordering follows the dependency structure in `../vision/goals.md`: primitives
and evaluation first, applied capabilities last. Knowledge-layer capabilities
depend on nearly everything above them and are correspondingly further out.

---

## What matters more than capability count

If the year produces **three capabilities that genuinely work**, with honest
evaluation and sustainable cost, that is a better outcome than twelve that
partially work.

Partially-working infrastructure is worse than absent infrastructure: people
build on it, hit its limits, and lose trust in the whole platform. Anti-metrics
in `../vision/success_metrics.md` say this too — capability count is explicitly
not something we optimise for.

---

## Open questions at this horizon

- Is the project sustainably funded, or running on volunteer effort?
- Is there a community around it, or is it one or two people?
- Did any capability require training, and if so, can we maintain it?
- Did scope narrow, and was that recorded as a deliberate decision?
- Are other people building on this, or only us?

The last question is the real test of whether this is infrastructure.

## Risks

| Risk | Note |
| --- | --- |
| Breadth pursued at the cost of quality | The dominant risk at this horizon; see the anti-metrics |
| Maintenance burden exceeds capacity | Every component built is maintained forever (**P-1**) |
| Sustainability unresolved | `11_business` should have answered this by month 6 |
| Nobody uses it | Infrastructure with no consumers has failed regardless of its quality |
