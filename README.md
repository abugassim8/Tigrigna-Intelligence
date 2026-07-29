# Tigrinya Language Intelligence Platform

**Building the foundational AI infrastructure for Tigrinya language
intelligence.**

Tigrinya (ትግርኛ) is spoken by millions of people and is served by almost none of
the language technology that speakers of high-resource languages take for
granted. This project exists to build that missing layer — not as an
application, but as infrastructure that others can build on.

> **Status: Phase 0 — workspace initialisation.** The research operating system
> is in place. No research has been conducted, no technology selected, and no
> architecture designed. See [`PROJECT_CONTEXT.md`](PROJECT_CONTEXT.md).

---

## What this project is

Language infrastructure: models, data, services, and developer interfaces that
make Tigrinya computationally tractable.

The platform is scoped to eventually provide translation, semantic search,
cross-language retrieval, embeddings, grammar checking, spell correction,
transliteration, morphological analysis, lemmatization, named entity
recognition, entity linking, a knowledge graph, RAG capabilities,
summarization, question answering, developer APIs, an MCP server, and SDKs.

**This is not a news application.** It is not a content product of any kind. If
work starts drifting toward an end-user media experience, it has left scope.

## Core philosophy

Reuse existing models whenever possible. Train only when proprietary advantage
exists. Prioritise, in this order: **data quality → evaluation →
reproducibility → low operating cost → maintainability.**

Full statement in [`PROJECT_CONTEXT.md`](PROJECT_CONTEXT.md).

---

## How this repository is organised

```
.
├── README.md                  You are here
├── PROJECT_CONTEXT.md         Read this first — mission, philosophy, constraints
├── CONTRIBUTING.md            How to contribute research, decisions, and code
├── CHANGELOG.md               Notable changes to the project and its direction
│
├── docs/
│   ├── vision/                Mission, goals, non-goals, success metrics, principles
│   ├── research/              The research operating system
│   │   ├── AI_RESEARCH_RULES.md   Mandatory rules for AI assistants
│   │   ├── CHECKLIST.md           Questions every report must answer
│   │   ├── templates/             Report, summary, decision, experiment templates
│   │   ├── reports/               Full research reports, by domain (00–12)
│   │   ├── summaries/             Compressed 2-page summaries — read these first
│   │   └── references/            Papers, projects, datasets, links
│   ├── architecture/          System, data, ML, API, MCP, infrastructure design
│   ├── decisions/             DECISIONS.md, rejected_options.md, assumptions.md
│   ├── benchmarks/            Evaluation strategy, datasets, metrics
│   └── roadmap/               30 days, 90 days, 6 months, 1 year, 2 years
│
├── datasets/                  raw · processed · evaluation · dictionaries · terminology
├── models/                    experiments · checkpoints · evaluations
├── services/                  api · translation · embeddings · retrieval · morphology
│                              tokenizer · ner · grammar · spellcheck
│                              knowledge_graph · mcp
├── sdk/                       python · javascript · examples
├── infrastructure/            docker · kubernetes · terraform · monitoring
├── experiments/               notebooks · results · logs
└── scripts/                   data_processing · evaluation · deployment
```

The separation is deliberate and load-bearing:

- **Research is separate from decisions.** `docs/research/` holds what we
  *found*. `docs/decisions/` holds what we *chose*. Findings inform decisions;
  they are not decisions.
- **Experimentation is separate from production design.** `experiments/` and
  `models/experiments/` are allowed to be messy and are allowed to fail.
  `services/` and `docs/architecture/` are not.

---

## Research workflow

Every research task runs through three roles: **Scout → Analyst → Architect.**

| Role | Purpose | Output | Lives in |
| --- | --- | --- | --- |
| **Scout** | Discover options — map the space, find what exists | Short research summary | `docs/research/summaries/` |
| **Analyst** | Deep technical evaluation of the shortlist | Full report | `docs/research/reports/NN_*/` |
| **Architect** | Convert research into implementation decisions | Decision records + architecture updates | `docs/decisions/`, `docs/architecture/` |

The full protocol — including how to avoid repeating research and how to compress
findings — is in [`docs/research/README.md`](docs/research/README.md).

Before recommending anything, read
[`docs/research/AI_RESEARCH_RULES.md`](docs/research/AI_RESEARCH_RULES.md) and
[`docs/decisions/DECISIONS.md`](docs/decisions/DECISIONS.md).

Every report must answer the nine questions in
[`docs/research/CHECKLIST.md`](docs/research/CHECKLIST.md). A report that cannot
answer them is not finished.

---

## Development workflow

Development has not started and will not start until the research phases that
gate it have produced decisions. When it does:

1. **A decision precedes the code.** Nothing lands in `services/` without a
   corresponding entry in `docs/decisions/DECISIONS.md`.
2. **Evaluation precedes the capability.** A service is not built until there is
   an agreed way to measure whether it works — see `docs/benchmarks/`.
3. **Experiments live in `experiments/`.** Promote to `services/` only after the
   experiment produces a result worth operationalising, recorded in
   `models/evaluations/`.
4. **Every service is independently runnable and independently testable.**
5. **Reproducibility is a merge requirement**, not a nice-to-have.

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the specifics.

---

## Future roadmap

Planning horizons live in `docs/roadmap/`:
[30 days](docs/roadmap/30_days.md) ·
[90 days](docs/roadmap/90_days.md) ·
[6 months](docs/roadmap/6_months.md) ·
[1 year](docs/roadmap/1_year.md) ·
[2 years](docs/roadmap/2_years.md)

These are currently scaffolds. They become real once Phase 1 research produces
enough grounding to make dated commitments honest rather than aspirational.

---

## Getting started

1. Read [`PROJECT_CONTEXT.md`](PROJECT_CONTEXT.md) — the whole thing.
2. Read [`docs/research/AI_RESEARCH_RULES.md`](docs/research/AI_RESEARCH_RULES.md).
3. Check [`docs/research/summaries/`](docs/research/summaries/) for what is
   already known.
4. Check [`docs/decisions/DECISIONS.md`](docs/decisions/DECISIONS.md) for what is
   already decided.
5. Pick up the next open item from
   [`docs/research/reports/00_project_definition/`](docs/research/reports/00_project_definition/).

## Licence

Not yet selected. Licence choice is itself a decision that must be recorded in
`docs/decisions/DECISIONS.md`, and it interacts with the licensing of every
model and dataset the platform adopts — so it is deliberately deferred until
after the data and model strategy research is complete.
