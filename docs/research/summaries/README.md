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

Keep this table current. It is the first thing anyone reads.

**Start with 001.** It is the load-bearing finding: most of the model layer we
planned to build already exists, and our differentiator is the primitives layer,
the evaluation harness, and the integration surface.

⚠️ **Both summaries carry an evidence caveat.** The 2026-07-29 session's egress
policy blocked arxiv, ACL Anthology, publisher sites, and Semantic Scholar, so
all paper-derived figures are `[reported]` from search summaries rather than
read from source. Hugging Face data is `[verified]`. A session with unrestricted
egress should verify the flagged numbers first.

## What future researchers should add

One summary per research effort — Scout summaries and Analyst report summaries
alike. Update the index. Mark superseded entries rather than removing them: the
record of a conclusion that later turned out to be wrong is valuable, because it
tells the next person that the question is harder than it looks.

## Status

**3 summaries.** Phase 1 (`00_project_definition`, `01_ecosystem`) and the
critical-path half of Phase 2 (`02_linguistics`) are complete.

Next: `03_data_strategy` — a corpus survey is now the blocking dependency for
the orthographic-variation and normalisation work (DEC-007), and the verified
40M-token data ceiling is the number to plan against.
