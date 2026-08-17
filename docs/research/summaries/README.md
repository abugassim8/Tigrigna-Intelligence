# Research Summaries

## Purpose of this document

This directory holds compressed summaries of every piece of research conducted
on this project. **This is the most-read directory in the repository, and it
should be.**

## Why this directory exists

Full reports are the evidence record. They are long, thorough, and — realistically —
almost never read end to end. The next contributor does not have time; the next
AI research session does not have the context budget.

Summaries are the working memory. They are what makes accumulated research
affordable to consult, which is the difference between a project that builds on
its own findings and one that rediscovers them.

**Read summaries first. Always.** Open a full report only when a summary cannot
answer the specific question in front of you. Loading a forty-page report to
answer a question the two-page summary already answered is precisely the waste
this repository is structured to prevent.

## How to use this directory

**When starting any research task:**

1. Scan the index below and the filenames here.
2. Read anything related to your topic.
3. Only then decide whether new research is needed.
4. If the topic is covered, build on it or challenge it — do not redo it.

**When finishing any research task:**

Write a summary here. Every report gets one. A report without a summary is
incomplete, and will be treated as such in review.

## The rules

1. **Hard limit: 2 pages.** Roughly 800–1000 words. This constraint is the whole
   point. If it does not fit, you have not finished compressing — and a summary
   that runs long will go unread exactly like the report it was meant to replace.
2. **Use [`../templates/summary_template.md`](../templates/summary_template.md).**
3. **Lead with the conclusion.** The one-line answer goes at the top.
4. **Keep every number that matters.** The `Important Numbers` section is what
   makes a summary reusable without reopening the report.
5. **Always record rejected alternatives.** This is what stops the same option
   being re-proposed next quarter.
6. **Mark evidential status.** `[verified]`, `[reported]`, `[unverified]` — so a
   reader can calibrate.
7. **Never delete a superseded summary.** Mark it superseded and link the
   replacement.

## Naming

`NNN-slug.md`, matching the source report number where one exists.

Examples: `001-tigrinya-corpus-survey.md`, `007-tokenizer-options.md`

## Index

| ID | Title | Stage | Domain | Date | Status |
| --- | --- | --- | --- | --- | --- |
| [001](001-tigrinya-nlp-ecosystem-scan.md) | Tigrinya NLP Ecosystem Scan | Scout → Analyst | `01_ecosystem` | 2026-07-29 | Current |
| [002](002-scope-users-and-dialect.md) | Scope, Users, and Dialect Definition | Scout → Analyst | `00_project_definition` | 2026-07-29 | Current |
| [003](003-morphology-script-and-tokenization.md) | Morphology, Ge'ez Script, and the Tokenization Constraint | Scout → Analyst | `02_linguistics` | 2026-07-29 | Current |
| [004](004-geez-tooling-survey.md) | Ge'ez Tooling Survey and the HornMorpho Question | Scout → Analyst | `02_linguistics` | 2026-07-29 | Current |
| [005](005-corpus-inventory-and-contamination.md) | Corpus Inventory and Confirmed Contamination | Scout → Analyst | `03_data_strategy` | 2026-07-29 | Current |

Keep this table current. It is the first thing anyone reads.

**Start with 001.** It is the load-bearing finding: most of the model layer we
planned to build already exists, and our differentiator is the primitives layer,
the evaluation harness, and the integration surface.

⚠️ **Every summary carries an evidence caveat.** The 2026-07-29 session's egress
policy blocked arxiv, ACL Anthology, publisher sites, and Semantic Scholar, so
paper-derived figures are `[reported]` from search summaries rather than read
from source. Hugging Face cards, PyPI metadata, and anything **measured by
running code** are `[verified]`.

**Before researching anything, read
[`../RESEARCH_ACCESS.md`](../RESEARCH_ACCESS.md)** — it maps which sources are
reachable and how, so you do not repeat the discovery. A session with
unrestricted egress should work the verification backlog listed there.

### 006 — Metric validity and the evaluation harness

BLEU is **~8% harsher** on Tigrinya than English — real, and about half the size
the standard warning implies. **chrF adopted as primary** because its advantage
widens as quality falls. Our two evaluation anchors appear to be in **different
varieties**, so no aggregate Tigrinya score may be reported.
→ `006-metric-validity-and-harness.md` · DEC-009, DEC-010

### 007 — Translation model selection

**Every NLLB variant is CC-BY-NC-4.0** — the model behind essentially every
published Tigrinya MT number cannot be shipped. **MADLAD-400-3B is Apache-2.0,
covers Tigrinya, and is the shippable choice** at 4.8× the parameters (1.4 GB at
Q4, so A-008 survives).
→ `007-translation-model-selection.md` · DEC-011

### 008 — Architecture: tiers and runtime

Capabilities differ by **~150× in memory**, so the system decomposes **by
resource profile, not by domain**. DEC-006's MVP is Tier 0+1 = **191 MB**;
adding translation is an 8.3× jump. One MIT runtime (CTranslate2) serves every
model we have.
→ `008-architecture-tiers-and-runtime.md` · DEC-012, DEC-013, DEC-014

### 009 — The pipeline without training

Our pipeline is **acquire → screen → convert → evaluate → release**; training is
a contingency. Testing two self-claims found reproducibility held where designed
in (2/3 experiments, now 3/3) while **DEC-008's screening gates had no
implementation at all** — now executable.
→ `009-pipeline-without-training.md` · DEC-015, DEC-016

### 010 — Training strategy

**Zero cleanly-licensed parallel training data.** So if MADLAD (adopted without
quality measurement) underperforms, **we cannot fine-tune our way out** — which
makes **A-05 the insurance policy on DEC-011**. If triggered, LoRA is ~23×
cheaper than a full fine-tune. From-scratch is foreclosed by A-002.
→ `010-training-triggers.md` · DEC-017

### 011 — Infrastructure: cost model and enforcement

Tiering cuts standing resource cost **22×**. But **Tier 2's deployment mode is
not decidable yet** — break-even is as low as **~1 req/min** if cold start is
slow, and it is unmeasured (**A-14**). CI now enforces the five decision-log
rules that nothing was checking.
→ `011-cost-model-and-enforcement.md` · DEC-018, DEC-019

## Turning findings into action

Blockers surfaced by this research live in [`../../ACTIONS.md`](../../ACTIONS.md)
— emails to send, licences to obtain, decisions to confirm, with drafts. **When
a summary produces something a human must do, add it there** rather than leaving
it buried in a findings list.

## What future researchers should add

One summary per research effort — Scout summaries and Analyst report summaries
alike. Update the index. Mark superseded entries rather than removing them: the
record of a conclusion that later turned out to be wrong is valuable, because it
tells the next person that the question is harder than it looks.

## Status

**5 summaries, 1 experiment.** Four research domains complete:
`00_project_definition`, `01_ecosystem`, `02_linguistics`, `03_data_strategy`.

**Summary 004 supersedes part of 003's build plan:** the decomposition layer
003 said to build already exists (Epitran). Read 003 for *why* the problem
exists, 004 for *what to do about it*.

**Summary 005 is the one to read if you touch data.** The corpus is measured
(~67K monolingual rows, 1.4M parallel pairs) but **~99% is unlicensed**, and a
dataset advertised for pretraining **verifiably contains** our evaluation anchor's
data. → **DEC-008**: screen everything, quarantine unlicensed data.

Next: `08_evaluation` (build the harness on FLORES-200 + TiQuAD) or
`04_model_strategy`. Both are now unblocked by the data picture.
