# Tigrinya Language Intelligence Platform

**Building the foundational AI infrastructure for Tigrinya language
intelligence.**

Tigrinya (ትግርኛ) is spoken by millions of people and is served by almost none of
the language technology that speakers of high-resource languages take for
granted. This project exists to build that missing layer — not as an
application, but as infrastructure that others can build on.

> **Status: 13 research domains complete** — every planned domain, from
> `00_project_definition` through `12_master_blueprint`. **28** decisions
> recorded and **10** reproducible experiments. **Tier 0 is built**: two Python
> packages (`services/primitives`, `services/evaluation`), both test suites
> passing.
> See [`PROJECT_CONTEXT.md`](PROJECT_CONTEXT.md).
>
> **What is not built:** embeddings (**A-09**), the API surface (**A-02**), and
> **no model has been run through the evaluation harness yet** (**A-09**).
> Morphology *is* built (**DEC-028**) but its analyser is GPL-3.0 and never
> bundled, so it is absent unless you install it. Its intrinsic checks now
> exist and are tested — and with no analyser they report **SKIP**, which is
> deliberately not a pass. CI is written but **not installed** (**A-15**).
> **Every remaining task needs a person, not more research** — the autonomous
> backlog is empty. See [`ACTIONS.md`](ACTIONS.md).
>
> **The research changed the plan.** Most of the Tigrinya model layer already
> exists and is largely openly licensed. Our differentiator is the **primitives
> layer** (Ge'ez normalisation, tokenization, morphology), the **evaluation
> harness**, and the **API/MCP/SDK surface** — none of which anyone has built.
> Read [`docs/research/summaries/`](docs/research/summaries/) — **16 summaries**,
> two pages each.

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
├── ACTIONS.md                 Things only a human can do — with email drafts
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

[30 days](docs/roadmap/30_days.md) reflects completed Phase 1 work and the live
blocking items. The longer horizons remain scaffolds until
`12_master_blueprint` gives them enough grounding to be honest rather than
aspirational.

---

## Getting started

### Use the primitives

```bash
pip install -e services/primitives
python -c "
from tigrinya_primitives import normalise, transliterate
print(normalise('ፀሓይ'))                    # -> ጸሓይ
a = transliterate('ሰላም ዓለም')
print(a.analysis, [s.surface for s in a.spans])
"
```

Evaluation, including the Tier 0 intrinsic checks:

```bash
pip install -e services/evaluation
python -m tigrinya_eval.primitives experiments/003-metric-validity/data
```

### Contribute

**If you have time to unblock the project rather than research it, go straight to
[`ACTIONS.md`](ACTIONS.md).** **Two items are blocking** — A-01 and A-02 — and
each has a ready-to-send draft.

⚠️ *This paragraph used to list **A-05** as blocking and describe it as unlocking
**1.4M parallel sentences**. Experiment 009 measured the corpus: **56.9% of the
rows have no English side.** A-05 is now Medium, and DEC-017 stands unchanged
either way.*

**The highest-leverage thing a person can do is A-13** — about 25 minutes of a
Tigrinya speaker's time, and every correctness claim in the project waits behind
it. **A-15 is five commands** and switches on 28 checks that currently enforce
nothing. See [`docs/roadmap/NEXT_SESSION.md`](docs/roadmap/NEXT_SESSION.md) for
the full list in leverage order.

1. Read [`PROJECT_CONTEXT.md`](PROJECT_CONTEXT.md) — the whole thing.
2. Read [`docs/research/AI_RESEARCH_RULES.md`](docs/research/AI_RESEARCH_RULES.md).
3. Check [`docs/research/summaries/`](docs/research/summaries/) for what is
   already known.
4. Check [`docs/decisions/DECISIONS.md`](docs/decisions/DECISIONS.md) —
   **DEC-001 … DEC-030**, eight amended by later measurement.
5. Read [`docs/research/RESEARCH_ACCESS.md`](docs/research/RESEARCH_ACCESS.md)
   before searching for anything — it maps which sources are reachable.
6. **[`docs/roadmap/NEXT_SESSION.md`](docs/roadmap/NEXT_SESSION.md) is the
   live handoff** — what to do next, and the list of things only a person
   can do. Start there.
7. **[`docs/roadmap/READINESS_PLAN.md`](docs/roadmap/READINESS_PLAN.md) is the
   current plan of record** — what "ready" means, what is blocked on whom, and
   the order to do it in.

## Licence

**Chosen by licence class (DEC-020), not one licence for everything:**

| Artefact | Licence |
| --- | --- |
| **Code** | **Apache-2.0** — see [`LICENSE`](LICENSE) |
| **Documentation** | **CC-BY-4.0** — see [`LICENSE-docs`](LICENSE-docs) |
| **Data** | **Inherits** whatever the source imposes |

**No code dependency imposes copyleft** — the upstream licence map was checked in
full. Share-alike enters only through data (FLORES+ is CC-BY-SA-4.0), so the
obligation is contained to derived corpora rather than the platform.

*(This section read "Not yet selected" until 2026-08-23, six days after
DEC-020 closed the question and the LICENSE files were committed.)*
