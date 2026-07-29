# The Research Operating System

## Purpose of this document

This document defines *how research is done* on this project. It is the
operating manual for turning open questions into recorded decisions without
wasting effort — and, critically, without repeating work that has already been
done.

**Why it exists:** Research on a project like this is mostly a context problem,
not an intelligence problem. The expensive failure is not "we could not find the
answer"; it is "we found the answer four times and forgot it three times." This
system exists to make findings durable and cheap to re-load.

**How to use it:** Read it before starting any research task. Follow the
protocol below. Do not improvise a different structure.

**What future researchers should add:** Refine the protocol when it fails you.
If a stage consistently produces low-value output, change the stage — but record
the change as a decision, not a silent edit.

---

## The protocol: Scout → Analyst → Architect

Every research task follows three stages, in order. Each has a distinct purpose
and a distinct output. **Do not collapse them.** The most common failure mode in
technical research is jumping straight to a recommendation before the option
space has been mapped — which produces confident advocacy for the first
plausible option rather than the best one.

### Stage 1 — Scout

**Purpose:** Discover options.

Map the territory. Find out what already exists: models, datasets, libraries,
papers, products, prior art, standards. Cast wide. Do not evaluate deeply, do
not rank, and do not recommend. The Scout's job is to make sure the Analyst
never says "I did not know that existed."

A Scout pass is done when adding another hour of searching stops surfacing new
categories of option.

**Output:** A **short research summary** — written to
`docs/research/summaries/` using
[`templates/summary_template.md`](templates/summary_template.md).

**Scout output must include:**
- The option space: what exists, grouped by approach.
- Rough viability signal for each (maintained? licensed usably? Tigrinya
  coverage at all?).
- What was searched and what was *not* found — negative results matter.
- A shortlist for the Analyst, with the reason each item made the cut.

### Stage 2 — Analyst

**Purpose:** Deep technical evaluation.

Take the Scout's shortlist and evaluate it seriously: quality, cost,
performance, licensing, maintenance burden, integration difficulty, failure
modes. Run experiments where cheap experiments would settle a question that
argument cannot.

The Analyst is the stage where numbers appear. A report with no numbers in it is
usually a Scout summary wearing a costume.

**Output:** A **full report** — written to
`docs/research/reports/NN_domain/` using
[`templates/research_report_template.md`](templates/research_report_template.md).

**Every full report must:**
- Answer all nine questions in [`CHECKLIST.md`](CHECKLIST.md).
- Include a cost analysis and an explicit build-vs-buy position.
- Document alternatives considered and *why each was not chosen*.
- Cite sources, added to [`references/`](references/).
- State uncertainty explicitly, including what would change the conclusion.
- **Ship with a ≤2-page summary** in [`summaries/`](summaries/). A report without
  a summary is not finished — the summary is the artefact future sessions will
  actually read.

### Stage 3 — Architect

**Purpose:** Convert research into implementation decisions.

Take the Analyst's report and *decide*. Research that never becomes a decision
is a cost with no return. The Architect turns findings into commitments, records
what was rejected, and updates the system design.

**Output:**
- A decision record appended to
  [`../decisions/DECISIONS.md`](../decisions/DECISIONS.md), using
  [`templates/decision_template.md`](templates/decision_template.md).
- Rejected options logged in
  [`../decisions/rejected_options.md`](../decisions/rejected_options.md).
- Updates to the relevant document in [`../architecture/`](../architecture/).
- Any new assumption surfaced, added to
  [`../decisions/assumptions.md`](../decisions/assumptions.md).

The Architect stage is also where a report can be sent back: if the research
does not support a decision, say so and specify exactly what is missing.

---

## Directory layout and what each part is for

```
docs/research/
├── README.md              This file — the protocol
├── AI_RESEARCH_RULES.md   Mandatory rules for AI assistants
├── RESEARCH_ACCESS.md     Which sources are reachable, and how — READ FIRST
├── CHECKLIST.md           The nine questions every report answers
├── templates/             Use these; do not invent structures
├── reports/               Full Analyst reports, by domain
│   ├── 00_project_definition/   Scope, problem framing, users, requirements
│   ├── 01_ecosystem/            Prior art, existing tools, communities, competition
│   ├── 02_linguistics/          Tigrinya structure: morphology, orthography, syntax
│   ├── 03_data_strategy/        Sourcing, licensing, cleaning, annotation
│   ├── 04_model_strategy/       Which models to reuse, adapt, or train
│   ├── 05_architecture/         System design, service boundaries, storage
│   ├── 06_ml_pipeline/          Training, inference, serving, versioning
│   ├── 07_api_mcp/              Developer API surface, MCP server, SDKs
│   ├── 08_evaluation/           Benchmarks, test sets, quality measurement
│   ├── 09_training_strategy/    When and how to train, if at all
│   ├── 10_infrastructure/       Compute, deployment, cost, operations
│   ├── 11_business/             Sustainability, funding, licensing, governance
│   └── 12_master_blueprint/     The synthesis: everything above, resolved
├── summaries/             Compressed ≤2-page summaries — READ THESE FIRST
└── references/            Papers, projects, datasets, links
```

### Reports vs. summaries — the most important distinction here

| | `reports/` | `summaries/` |
| --- | --- | --- |
| Length | However long the evidence needs | **≤2 pages, hard limit** |
| Audience | Someone who needs the full argument | Someone who needs the conclusion *now* |
| Read frequency | Rarely, on demand | Every session, always |
| Purpose | The evidence record | The working memory |

**Read summaries first. Always.** Open a full report only when the summary is
insufficient for the specific question in front of you. This ordering is the
single largest determinant of whether this repository stays cheap to work in.

---

## Rules that keep this system working

1. **Search before you research.** Check `summaries/` and `references/` first.
   Duplicated research is the most expensive mistake available here.
   Then check [`RESEARCH_ACCESS.md`](RESEARCH_ACCESS.md) for how to reach
   sources — and **check PyPI before assuming you must build something.**
2. **Every report gets a summary.** No exceptions.
3. **Research is not decision.** Findings go in `research/`. Choices go in
   `decisions/`. Keeping these separate is what lets us revisit a choice without
   re-doing the research behind it.
4. **Record what you rejected.** An option rejected without a written reason
   will be proposed again within a quarter.
5. **Cite sources.** Every non-obvious claim gets a reference.
6. **State uncertainty.** "Unknown" and "could not determine" are legitimate
   findings. Manufactured confidence is not.
7. **Numbers over adjectives.** "Fast" is not a finding; "38ms p50 on a 4-core
   container" is.
8. **Negative results are results.** "No usable Tigrinya dataset exists for X" is
   valuable and must be written down, or it will be rediscovered.

---

## Naming conventions

| Artefact | Pattern | Example |
| --- | --- | --- |
| Report | `reports/NN_domain/NNN-slug.md` | `reports/03_data_strategy/001-corpus-survey.md` |
| Summary | `summaries/NNN-slug.md` | `summaries/001-corpus-survey.md` |
| Decision | `DEC-NNN` in `DECISIONS.md` | `DEC-007` |
| Experiment | `experiments/NNN-slug/` | `experiments/004-tokenizer-fertility/` |

Summary numbers match their source report where one exists. Numbers are never
reused and never renumbered.

---

## Research status

**No research has been conducted.** `reports/`, `summaries/`, and `references/`
contain only scaffolding. Phase 1 begins with
`reports/00_project_definition/`.
