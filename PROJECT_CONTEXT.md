# PROJECT_CONTEXT.md

> **Read this file first.** Every human and every AI assistant that touches this
> repository starts here. It is the single source of truth for *what we are
> building and why*. If anything elsewhere in the repo contradicts this file,
> this file wins until it is explicitly amended.

---

## Purpose of this document

This document exists to eliminate re-derivation. Without it, every new
contributor — and every new AI research session — spends its first hours (and,
for AI sessions, a large share of its context budget) rediscovering the same
basic facts: what the project is, what it is not, what has already been decided,
and what the standing constraints are.

**How to use it:** Read it in full before doing anything else. It is
deliberately short enough to read completely. Do not skim it and do not
summarise it back to the user — act on it.

**What to add over time:** Amend this file only when the project's identity,
mission, philosophy, or standing constraints change. Routine research findings
belong in `docs/research/`; routine decisions belong in
`docs/decisions/DECISIONS.md`. This file changes rarely and every change should
be a deliberate act, recorded in `CHANGELOG.md`.

---

## Project name

**Tigrinya Language Intelligence Platform**

---

## Vision

Create the most useful AI infrastructure layer for Tigrinya language
understanding.

---

## Mission

Build the foundational AI infrastructure for Tigrinya language intelligence —
the layer that other applications, researchers, institutions, and developers
build *on top of*.

---

## What this project is

This is **language infrastructure**. It is a platform of models, data, services,
and developer interfaces that make Tigrinya computationally tractable.

The platform is intended to eventually provide:

| Capability | Category |
| --- | --- |
| Translation | Generation / transfer |
| Semantic search | Retrieval |
| Cross-language retrieval | Retrieval |
| Embeddings | Representation |
| Grammar checking | Correction |
| Spell correction | Correction |
| Transliteration | Orthography |
| Morphological analysis | Core NLP |
| Lemmatization | Core NLP |
| Named Entity Recognition | Core NLP |
| Entity linking | Knowledge |
| Knowledge graph | Knowledge |
| RAG capabilities | Applied |
| Summarization | Applied |
| Question answering | Applied |
| Developer APIs | Interface |
| MCP server | Interface |
| SDKs | Interface |

This list is a *scope statement*, not a roadmap. Sequencing, prioritisation, and
feasibility are research outputs, not givens. Nothing in this table is committed
to a timeline until a decision recorded in `docs/decisions/DECISIONS.md` says so.

---

## What this project is NOT

- **It is not a news application.** It is not a content product, a reader, an
  aggregator, or a media site. If a proposal starts to look like an end-user
  content app, it has drifted out of scope.
- It is not a research paper or an academic exercise. Everything must be
  buildable, operable, and maintainable.
- It is not a single model. It is a platform with many components, most of which
  should be reused rather than invented.

See `docs/vision/non_goals.md` for the maintained, expanded list.

---

## Core philosophy

**Reuse existing models whenever possible.**
**Train only when proprietary advantage exists.**

Training a model is a liability as much as an asset: it carries data cost,
compute cost, evaluation cost, and permanent maintenance burden. The default
answer to "should we train this?" is **no**, and the burden of proof sits with
whoever proposes it.

### Priorities, in order

1. **Data quality** — Nothing downstream can exceed the quality of the data.
   Tigrinya is low-resource; data work is the highest-leverage work available.
2. **Evaluation** — A capability that cannot be measured cannot be improved,
   claimed, or trusted. Evaluation is built before, not after, the thing it
   evaluates.
3. **Reproducibility** — Any result that cannot be reproduced from what is in
   this repository does not exist.
4. **Low operating cost** — The platform must be affordable to run continuously
   at low volume. Architectures that only make sense at scale we do not have are
   rejected.
5. **Maintainability** — Prefer the boring, well-supported option. Every
   component added is a component that must be kept alive.

When these priorities conflict, they are resolved in the order listed above.

---

## Standing constraints

These hold until a recorded decision changes them:

- Open source is preferred over commercial APIs (see
  `docs/decisions/assumptions.md` for the full assumption set and its rationale).
- Licensing must be verified before any model, dataset, or dependency is
  adopted. "It's on the internet" is not a licence.
- Accuracy is prioritised over latency, unless a specific product requirement
  states otherwise.
- Every non-trivial technical choice produces a decision record.
- Every research effort produces a compressed summary, not just a long report.

---

## Repository map (orientation)

```
docs/vision/        Why the project exists and what "done" means
docs/research/      The research operating system: rules, templates, reports, summaries
docs/architecture/  How the system is designed (populated after research)
docs/decisions/     What we chose, what we rejected, what we assume
docs/benchmarks/    How we measure whether any of it works
docs/roadmap/       Time-boxed planning horizons
datasets/           Data, by lifecycle stage
models/             Experiments, checkpoints, evaluations
services/           Runtime components, one directory per capability
sdk/                Client libraries and examples
infrastructure/     Docker, Kubernetes, Terraform, monitoring
experiments/        Notebooks, results, logs — exploratory, not production
scripts/            Operational tooling
```

---

## Where to go next

| If you are… | Go to |
| --- | --- |
| An AI assistant starting a session | `docs/research/AI_RESEARCH_RULES.md` |
| Starting a research task | `docs/research/README.md` |
| About to recommend anything | `docs/decisions/DECISIONS.md` |
| Looking for prior work | `docs/research/summaries/` **before** `docs/research/reports/` |
| Contributing code or docs | `CONTRIBUTING.md` |

---

## Current status

**Phase 1 complete; Phase 2 critical path complete.**

Three research domains are done:

- `00_project_definition` → scope, users, dialect (DEC-002, DEC-004, DEC-006)
- `01_ecosystem` → the Tigrinya NLP landscape mapped (DEC-003, DEC-005)
- `02_linguistics` → morphology, Ge'ez script, tokenization (DEC-007), plus a
  Ge'ez tooling survey and the project's first experiment

**Read [`docs/research/summaries/`](docs/research/summaries/) before doing
anything else.** Four summaries, ~2 pages each, and they change the plan.
Then read [`docs/research/RESEARCH_ACCESS.md`](docs/research/RESEARCH_ACCESS.md)
before searching for anything — it maps which sources are reachable.

### What the research established

**1. Most of the model layer already exists.** A single group (GeezLab /
`fgaim`) has published a coherent Tigrinya stack including an Apache-2.0
embedding model. **Our differentiator is not models** — it is the primitives
layer, the evaluation harness, and the integration surface (API, MCP, SDKs).
Nobody has built those.

**2. The primitives problem has a specific mechanism.** Tigrinya is templatic
*and* agglutinative, so roots are **discontinuous**; the Ge'ez abugida **fuses
consonant and vowel into one character**. So **a morpheme boundary can fall
inside a single character**, and no subword tokenizer on raw Ge'ez can represent
it. Hence DEC-007: a consonant–vowel decomposition layer beneath tokenization.
This also makes **transliteration core infrastructure**, not a peripheral
feature.

**3. The decomposition layer already exists.** `experiments/001` measured
**Epitran's `tir-Ethi` map**: 384/384 Ge'ez coverage, correct Tigrinya phonology,
and ካተበ → `katəbə` yields the root `[k,t,b]`. It is **not reversible** (22
collisions) — but those collisions are the Ge'ez homophone pairs, so the loss
*is* orthographic normalisation. DEC-007 is amended to dual representation:
Epitran for analysis, surface Ge'ez preserved for output. **We build only the
alignment between them.**

**4. The data ceiling is 40M tokens.** `[verified]` TiRoBERTa — the strongest
available Tigrinya encoder — was pretrained on 40 million tokens. That is small
enough to favour linguistically-informed methods over data-hungry ones, and it
is the number `03_data_strategy` must plan against.

### Blocking items

1. **Licence resolution on the `fgaim` models** — several carry no stated
   licence, including the family's base. Blocks DEC-003 under **P-9**.
2. **HornMorpho maintenance status** — the only established Tigrinya
   morphological analyser, now on the critical path via DEC-006.
3. **DEC-002 needs owner confirmation** — the user determination is inferential.
4. **TiQuAD's copyright position needs legal review** — its authors do not own
   the source-article copyright; it is fair-use "academic research purposes
   only" under a CC-BY-SA-4.0 wrapper. Fine for internal evaluation; **not
   clearly fine for an infrastructure platform.**
5. **Ethiopian-variety QA evaluation is a gap** — TiQuAD is Eritrean-sourced.

### Still not done

**No architecture has been designed. No served model has been selected. No code
has been written.** Everything in `docs/architecture/` remains a scaffold.
Documents outside `docs/research/` and `docs/decisions/` that appear to state
technical conclusions are still placeholders.

⚠️ **Evidence caveat:** the Phase 1 session's egress policy blocked arxiv, ACL
Anthology, publisher sites, and Semantic Scholar. Paper-derived figures are
`[reported]` from search summaries, not read from source; Hugging Face data is
`[verified]`. Verify before relying on precision.

_Last amended: 2026-07-29_
