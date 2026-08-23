# Roadmap — 90 Days

> ⚠️ **Superseded as a plan, kept as a record.** This was written **before any
> research** — when the research phases were still hypothetical. All 13 research domains are now complete, two packages are
> built, and **[`READINESS_PLAN.md`](READINESS_PLAN.md) is the plan of record.**
>
> **The research it projected over a quarter completed faster**, and produced 24 decisions plus six experiments. What it did not anticipate is that finishing the research would leave the project gated almost entirely on human actions rather than on further work.

## Purpose of this document

The quarter-scale plan: the research phases expected to complete in the first
three months, and what they should produce.

**Why it exists:** A month is too short to see the shape of the research
programme; a year is too far out to plan honestly before any research exists. The
quarter is where sequencing decisions actually get made.

**How to use it:** Use it to sequence work and to check whether the current month
is serving the quarter. Pull items into `30_days.md` as capacity allows.

**What future contributors should add:** Concrete dates and scope once the first
30 days establish how fast research actually moves. The estimates below are
guesses about a project that has not run yet.

> **Horizon: 2026-07-29 → 2026-10-27**
> **Confidence: low.** These are intentions, not commitments. Pace is unknown
> until we have measured it.

---

## Theme of the quarter

**Understand the problem thoroughly enough to design a solution.**

The quarter succeeds if it ends with an evidence-backed picture of what exists,
what the data situation actually is, and what can be measured. It does not
require any code.

---

## Planned research phases

### Phase 1 — Foundations (Month 1)
`00_project_definition` · `01_ecosystem` — see [`30_days.md`](30_days.md).

### Phase 2 — Language and data (Month 2)

**`02_linguistics`** — the linguistic facts that drive technical design.
- Morphology and its consequences for tokenization and lemmatization.
- Ge'ez script handling: Unicode, normalisation, encoding pitfalls.
- Orthographic variation in real text.
- Dialectal variation and whether it matters for our use cases.
- **Resolves assumption A-007**, which currently sits upstream of several
  architectural choices while being unverified.

**`03_data_strategy`** — likely the highest-leverage domain in the project.
- What Tigrinya text exists, at what scale, under what licence.
- What can be collected legally and ethically.
- Cleaning and normalisation requirements.
- Annotation needs and costs.
- **Tests assumption A-006** on evaluation data scarcity, which affects
  sequencing across the whole project.

### Phase 3 — Measurement (Month 3)

**`08_evaluation`** — deliberately early, before model strategy.
- Which metrics are valid for Tigrinya, and how we would know.
- What evaluation data exists and what must be built.
- Contamination control.
- Baselines.

**Why evaluation precedes model strategy:** models cannot be compared without a
trustworthy way to measure them. Running `04_model_strategy` first would produce
recommendations backed by numbers we cannot defend — which is worse than no
recommendation, because it looks like evidence.

### Phase 4 — Model landscape (Month 3, if capacity allows)

**`04_model_strategy`** — begins only once evaluation is usable.
- Which existing models handle Tigrinya at all, measured rather than claimed.
- Licence terms and inference costs.
- Where adaptation closes the gap; where nothing viable exists.

---

## Expected outputs by end of quarter

- Research reports and summaries across domains 00, 01, 02, 03, 08.
- A populated `references/` covering papers, projects, datasets, and models.
- A meaningful decision log — plausibly 10–20 records.
- `assumptions.md` largely resolved: validated, invalidated, or evidenced.
- A first honest assessment of the Tigrinya data situation.
- A first view of whether standard metrics work for Tigrinya at all.
- Enough grounding to make `6_months.md` a real plan rather than a wish.

---

## Explicitly not this quarter

- No production code.
- No model training.
- No infrastructure provisioning.
- No public API.
- No commitments about capability quality — we will not have the evidence.

---

## Decision points

| Point | Question | Timing |
| --- | --- | --- |
| DP-1 | Is there enough usable Tigrinya data for the planned capabilities? | End of Phase 2 |
| DP-2 | Do standard metrics work for Tigrinya, or must we build our own? | End of Phase 3 |
| DP-3 | Do any existing models handle Tigrinya adequately? | End of Phase 4 |
| DP-4 | Does the scope need narrowing given what we now know? | End of quarter |

**DP-4 is the important one.** The capability scope is wide. If the data and
model situation is worse than hoped, the correct response is to narrow scope
deliberately rather than to attempt everything badly — and this is the point at
which we will have the evidence to do that.

## Risks

| Risk | Mitigation |
| --- | --- |
| Data situation is far worse than assumed | Surface early via DP-1; be prepared to narrow scope at DP-4 |
| Research produces reports but no decisions | Every Analyst report reaches Architect stage or states what blocks it |
| Scope stays wide because narrowing feels like failure | Narrowing on evidence is the intended use of DP-4, not a setback |
| Pace estimates are badly wrong | Re-plan after month 1 with measured throughput |
