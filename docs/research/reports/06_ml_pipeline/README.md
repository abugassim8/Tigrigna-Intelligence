# 06 — ML Pipeline

## Purpose of this document

This directory holds full Analyst-stage research reports for **06 — ML Pipeline**.

It covers the machinery around models: training pipelines where training happens, inference serving, model versioning, experiment tracking, and the path from experiment to production.

## Why this domain exists

Models are the visible part; the pipeline is what makes them reproducible, updatable, and operable. Reproducibility (**P-5**) is a platform property, not a per-model one — it either holds across the pipeline or it does not hold at all.

## Research questions this domain must answer

- How are experiments tracked, and what is the minimum tooling that achieves reproducibility?
- How do models get versioned, stored, and deployed?
- What does inference serving look like for each capability, given the cost constraint?
- How are models evaluated automatically before promotion?
- What is the path from `experiments/` to `services/`, and what gates it?
- How is data lineage tracked from raw source to trained artefact?
- What does the fine-tuning pipeline look like, where fine-tuning is justified?
- How do we roll back a bad model?
- What is monitored in production, and how would we notice quality regression?

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

**Depends on:** `04_model_strategy`, `05_architecture`.

**Gates:** Service implementation, `10_infrastructure`.

## What future researchers should add

Reports answering the questions above, each with a summary. Add new questions to
this list as they surface — the question list is expected to grow as the domain
is explored, and an unanswered question recorded here is more useful than one
carried in someone's head.

## Status

**No research conducted.** This directory contains only this scoping document.
