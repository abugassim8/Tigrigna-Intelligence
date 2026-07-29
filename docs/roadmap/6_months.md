# Roadmap — 6 Months

## Purpose of this document

The half-year horizon: where research should be complete, where design should
begin, and what the first buildable thing might be.

**Why it exists:** This is where the project transitions from understanding to
building. Naming that transition in advance keeps it deliberate rather than
accidental — and gives us a checkpoint to notice if research has become an end in
itself.

**How to use it:** As a directional guide. Do not treat anything here as
committed; check it against what the 90-day research actually found.

**What future contributors should add:** Replace these intentions with a real
plan once `12_master_blueprint` exists. Until then, everything here is
provisional by construction.

> **Horizon: 2026-07-29 → 2027-01-29**
> **Confidence: low.** Written before any research. Expect substantial revision.

---

## Theme

**Complete the research programme. Produce the blueprint. Build the first thing.**

---

## Expected shape

### Months 1–3 — Research foundations
Domains 00–03 and 08. See [`90_days.md`](90_days.md).

### Months 4–5 — Design research

- **`04_model_strategy`** — reuse, adapt, or train, per capability.
- **`05_architecture`** — service boundaries, data flow, storage.
- **`06_ml_pipeline`** — serving, versioning, promotion path.
- **`07_api_mcp`** — developer surface, MCP tools, SDK shape.
- **`09_training_strategy`** — only if the evidence points there. The default
  answer remains no (**A-004**, **P-2**, **N-5**).
- **`10_infrastructure`** — deployment and, critically, cost at low volume.
- **`11_business`** — sustainability, governance, and the licence decision.

### Month 6 — Synthesis and first build

- **`12_master_blueprint`** — the point where all domain findings are forced into
  a single coherent plan and their conflicts resolved.
- **First implementation begins**, on whichever foundational capability the
  blueprint identifies — likely one of the primitives from **G-1**, since
  everything else depends on them.

---

## What might exist at six months

Deliberately hedged: what is buildable depends entirely on what the research
finds.

| Area | Plausible state |
| --- | --- |
| Research | Domains 00–12 complete, each with summaries |
| Decisions | A substantial, evidence-backed decision log |
| Architecture | `docs/architecture/` populated with real design |
| Evaluation | Working evaluation harness and at least one trustworthy Tigrinya evaluation set |
| Data | Documented, licensed corpus with a reproducible processing pipeline |
| Services | One foundational service, working and measured |
| Infrastructure | Minimal deployment, costed |
| SDKs | Not yet — gated on the API being real |

**The most likely first deliverable is evaluation infrastructure**, not a
capability. It is what everything else is measured against, and it is the thing
most likely to still be valuable in five years regardless of which models come
and go.

---

## The scope decision

By six months we will know whether the full capability scope is achievable.

If the data and model situation is worse than hoped, the right response is to
**narrow scope deliberately** — pick the two or three capabilities where we can
do genuinely good work, and decline the rest explicitly in `non_goals.md`.

Doing a small number of things well is more valuable than doing many things
badly, both for users and for the project's credibility. This should be decided
on evidence, recorded as a decision, and not treated as a retreat.

---

## Risks at this horizon

| Risk | Mitigation |
| --- | --- |
| Research becomes an end in itself; building never starts | Month 6 is a hard checkpoint — blueprint delivered, implementation begun |
| The blueprint is internally incoherent | That is precisely what `12_master_blueprint` exists to surface and resolve |
| Scope is maintained past the point of realism | Narrow deliberately at DP-4; record it as a decision |
| The first build starts before evaluation exists | **P-4** — evaluation before capability, enforced in review |
| Data licensing blocks the plan late | **P-9** — licence verification is part of every data report, not a later step |

## Explicitly not at this horizon

- No public launch.
- No hosted commercial service (**N-9**).
- No speech capability (**N-6**).
- No foundation model trained from scratch (**N-5**).
