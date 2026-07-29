# 05 — Architecture

## Purpose of this document

This directory holds full Analyst-stage research reports for **05 — Architecture**.

It covers system design: service boundaries, data flow, storage, interfaces between components, and how the pieces fit together.

## Why this domain exists

The capability list is wide, and a design that couples capabilities tightly will be impossible to evolve as research changes our minds — which, this early, it will repeatedly. Service independence (**P-11**) exists so that individual components can be replaced without rewriting the platform.

## Research questions this domain must answer

- What are the right service boundaries, and why?
- What is the data flow from raw text to each capability's output?
- What storage is needed — document store, vector store, graph store, cache — and can any be avoided?
- How do services communicate, and what are the contracts?
- What is shared infrastructure versus per-service?
- How do we version models and data behind stable service interfaces?
- What does the minimum viable architecture look like — the smallest thing that works?
- How does the design handle a capability being replaced entirely?
- Where are the single points of failure, and which are acceptable?

Every report in this directory must also answer the nine questions in
[`../../CHECKLIST.md`](../../CHECKLIST.md).

## How to use this directory

1. Check [`../../summaries/`](../../summaries/) first — the answer may already exist.
2. Run a **Scout** pass to map the option space; write the short summary.
3. Run an **Analyst** pass on the shortlist using
   [`../../templates/research_report_template.md`](../../templates/research_report_template.md).
4. Write the report here as `NNN-slug.md`.
5. Write the ≤2-page summary to `../../summaries/NNN-slug.md`. **The report is
   not finished without it.**
6. Hand to the **Architect** stage: record decisions in
   [`../../../decisions/DECISIONS.md`](../../../decisions/DECISIONS.md).

## Dependencies

**Depends on:** `00_project_definition`, `04_model_strategy`.

**Gates:** `06_ml_pipeline`, `07_api_mcp`, `10_infrastructure`, and all service implementation.

## What future researchers should add

Reports answering the questions above, each with a summary. Add new questions to
this list as they surface — the question list is expected to grow as the domain
is explored, and an unanswered question recorded here is more useful than one
carried in someone's head.

## Status

**No research conducted.** This directory contains only this scoping document.
