# Changelog

## Purpose of this document

This file records notable changes to the **project** — its structure, direction,
decisions, and capabilities. It is not a git log. Git already records every
commit; this file records the small subset of changes that a future contributor
would need to know about to understand how the project got to where it is.

**How to use it:** Read the top entries to understand recent direction. Add an
entry when you change project structure, supersede a decision, complete a
research phase, or ship a capability.

**What future contributors should add:** One entry per meaningful change, newest
first. If you find yourself writing "fixed typo" here, it does not belong here.

**Format:** Loosely [Keep a Changelog](https://keepachangelog.com/). Dates are
ISO-8601. The project is pre-release and unversioned; versioning begins when the
first service is deployed.

---

## [Unreleased]

### Phase 1 research complete — 2026-07-29

The first two research domains were executed and documented. **This changed the
plan**, and the change is the most important entry in this file so far.

**Reports and summaries added**
- `docs/research/reports/01_ecosystem/001-tigrinya-nlp-ecosystem-scan.md`
  + summary `001-tigrinya-nlp-ecosystem-scan.md`
- `docs/research/reports/00_project_definition/001-scope-users-and-dialect.md`
  + summary `002-scope-users-and-dialect.md`
- `docs/research/references/` populated: `papers.md`, `models.md`,
  `datasets.md`, `projects.md`, `communities.md`, `commercial.md`

**The finding that changed the plan**

Most of the Tigrinya model layer we intended to build **already exists**. One
group (GeezLab / `fgaim`) has published a coherent stack — base language models,
an Apache-2.0 `sentence-transformers` embedding model, POS tagging, NER data,
human-annotated QA data. Meanwhile **no** Tigrinya API, MCP server, SDK, or
production morphology service exists anywhere.

The gaps are at the **bottom** (Ge'ez normalisation, tokenization, morphology)
and the **top** (API, MCP, SDKs) of the stack — not in the middle. This inverts
the naive build order and is now recorded as A-010.

**Decisions recorded**
- **DEC-002** *(Proposed — needs owner confirmation)* — primary users are
  application developers; researchers secondary.
- **DEC-003** — adopt the existing model layer; build primitives, evaluation,
  and integration.
- **DEC-004** — support both Tigrinya varieties; evaluate and report separately.
  Grounded in a measured dialect gap (COMET 0.82 Ethiopian vs 0.80 Eritrean).
- **DEC-005** — FLORES-200 and TiQuAD as initial evaluation anchors.
- **DEC-006** — the minimum viable platform is the primitives layer, **not**
  translation.

Nine alternatives rejected with reasons (R-004 … R-012).

**Assumptions updated**
- **A-006 partially invalidated** — more human-annotated Tigrinya evaluation
  data exists than assumed (FLORES-200, TiQuAD, TiALD). Narrowed: we must still
  build evaluation sets for retrieval, morphology, spell, and grammar, where
  nothing was found.
- **A-007 supported, confidence raised** — morphology-aware tokenization reduced
  one Tigrinya sentence from 21 tokens to 6. *But* the same source reports no
  significant downstream translation gain, so the benefit is cost and fidelity,
  not assumed accuracy.
- **A-009 escalated to an active blocker** — several key reuse candidates carry
  no stated licence.
- **A-001, A-004 supported.** **A-010 added.**
- Two previously-open scope questions closed (users, dialect); register scope,
  language pairs, deployment model, and diaspora needs remain open.

**Blocking items surfaced**
1. Licence resolution on the `fgaim` models — blocks DEC-003.
2. HornMorpho maintenance status — now on the critical path via DEC-006.
3. DEC-002 owner confirmation.

**Evidence limitation — recorded prominently**

The session's egress policy blocked `arxiv.org`, `aclanthology.org`, publisher
domains, and `api.semanticscholar.org` at the proxy. Hugging Face Hub data is
`[verified]` against the API; **all paper-derived figures are `[reported]` from
search-engine summaries and were not read from source.** This is flagged in both
summaries, both reports, and `references/README.md`. Re-verification is a
standing action item.

### Added — 2026-07-29

Initial repository scaffold and research operating system.

- Root documents: `README.md`, `PROJECT_CONTEXT.md`, `CONTRIBUTING.md`,
  `CHANGELOG.md`, `.gitignore`.
- **Vision layer** (`docs/vision/`): mission, goals, non-goals, success metrics,
  and engineering principles.
- **Research operating system** (`docs/research/`):
  - `README.md` defining the Scout → Analyst → Architect protocol.
  - `AI_RESEARCH_RULES.md` — mandatory operating rules for AI assistants,
    written to prevent duplicated research and unfounded recommendations.
  - `CHECKLIST.md` — the nine questions every research report must answer.
  - Four templates: research report, summary, decision, experiment.
  - Thirteen report domains (`00_project_definition` … `12_master_blueprint`),
    each with a scoping README.
  - `summaries/` and `references/` as the compressed, read-first layer.
- **Decision system** (`docs/decisions/`): `DECISIONS.md` with a fixed record
  format, `rejected_options.md`, and `assumptions.md` seeded with the project's
  standing assumptions.
- **Architecture placeholders** (`docs/architecture/`): system, data, ML, API,
  MCP, and infrastructure documents, each explicitly marked as un-designed and
  gated on research.
- **Benchmark layer** (`docs/benchmarks/`): evaluation strategy, datasets, and
  metrics scaffolds.
- **Roadmap horizons** (`docs/roadmap/`): 30 days, 90 days, 6 months, 1 year,
  2 years.
- **Working directories** with READMEs: `datasets/`, `models/`, `services/`
  (eleven capability services), `sdk/`, `infrastructure/`, `experiments/`,
  `scripts/`.

### Notes on this change

The tree specification placed the project under a
`tigrinya-language-intelligence/` root directory. That root is mapped onto the
repository root rather than nested inside it, since the repository *is* the
project. All paths below it match the specification exactly.

**No research was conducted, no technology evaluated, and no architecture
designed as part of this change.** Every technical document added is a scaffold
that explicitly states it contains no findings. This was deliberate: the
workspace is built before the research so that the research has somewhere
disciplined to land.
