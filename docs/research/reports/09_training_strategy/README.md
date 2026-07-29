# 09 — Training Strategy

## Purpose of this document

This directory holds full Analyst-stage research reports for **09 — Training Strategy**.

It covers when training or fine-tuning is justified, and how it would be done — data requirements, compute, method, cost, and maintenance.

## Why this domain exists

The default answer to training is **no** (**A-004**, **P-2**, **N-5**). This domain exists to make that default *rigorous* rather than reflexive: to establish what evidence would justify training, and to have a credible plan ready for the cases where it genuinely is warranted. A well-argued yes is as valuable as a well-argued no.

## Research questions this domain must answer

- For which capabilities, if any, does no adequate existing model exist?
- What proprietary advantage would training create that adaptation cannot?
- What is the full cost — data, annotation, compute, evaluation, and ongoing maintenance?
- What is the cost of *not* training: what quality do we accept, and does it clear the usability bar?
- What training data volume would be required, and do we have a credible path to it?
- Which methods suit low-resource conditions — transfer learning, adapters, LoRA, continued pre-training, distillation?
- What compute is required, and what does it cost at realistic prices?
- What is the maintenance commitment over the model's life?
- How would we know the trained model is better, and by how much?
- What is the fallback if training does not work?

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

**Depends on:** `03_data_strategy`, `04_model_strategy`, `08_evaluation`.

**Gates:** Any training work. Nothing gets trained without a decision grounded here.

## What future researchers should add

Reports answering the questions above, each with a summary. Add new questions to
this list as they surface — the question list is expected to grow as the domain
is explored, and an unanswered question recorded here is more useful than one
carried in someone's head.

## Status

**No research conducted.** This directory contains only this scoping document.
