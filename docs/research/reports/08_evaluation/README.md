# 08 — Evaluation

## Purpose of this document

This directory holds full Analyst-stage research reports for **08 — Evaluation**.

It establishes how we measure whether anything works: benchmarks, test sets, metrics, and their validity for Tigrinya specifically.

## Why this domain exists

Evaluation comes before capability (**P-4**). Without trustworthy evaluation we cannot compare approaches, detect regressions, or honestly describe what we have built. This domain is also where a subtle and serious risk lives: standard NLP metrics were validated largely on high-resource, morphologically simple languages, and whether they mean anything for Tigrinya is an open question rather than an assumption we may make. Evaluation infrastructure is likely to outlive every model this project ships.

## Research questions this domain must answer

- Which metrics are valid for Tigrinya, and how do we know?
- Do standard metrics behave sensibly under rich morphology, or do they mismeasure?
- What evaluation datasets exist, and are any of them trustworthy?
- What evaluation sets must we build, at what cost, and to what standard?
- How do we prevent train/eval contamination, and how do we detect it after the fact?
- How do we evaluate capabilities where no reference standard exists?
- What is the role of human evaluation, and how do we run it affordably?
- How do we evaluate against dialectal and register variation?
- What baselines do we measure against?
- How does evaluation run automatically in the pipeline?

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

**Depends on:** `02_linguistics`, `03_data_strategy`.

**Gates:** `04_model_strategy` (models cannot be compared without this), `06_ml_pipeline`, and every capability claim the project makes.

## What future researchers should add

Reports answering the questions above, each with a summary. Add new questions to
this list as they surface — the question list is expected to grow as the domain
is explored, and an unanswered question recorded here is more useful than one
carried in someone's head.

## Status

**No research conducted.** This directory contains only this scoping document.
