# 04 — Model Strategy

## Purpose of this document

This directory holds full Analyst-stage research reports for **04 — Model Strategy**.

It determines which models to reuse, which to adapt, and — only where genuinely justified — which to train, for each capability in scope.

## Why this domain exists

This is where the core philosophy is applied concretely: reuse whenever possible, train only for proprietary advantage. Every decision here has large and permanent cost implications, in both compute and maintenance. It is also the domain most likely to produce over-confident recommendations, because model choice is the most discussed and least Tigrinya-specific topic in the field — multilingual benchmark averages routinely say nothing about a language they may not even include.

## Research questions this domain must answer

- Which existing models handle Tigrinya at all, and how well — measured, not claimed?
- What is the actual quality of each for our specific capabilities?
- What are the licence terms, and do they permit our intended use?
- What are the inference costs, hardware requirements, and latency characteristics?
- Where does adaptation or fine-tuning close the gap, and at what cost?
- Where is there genuinely no viable existing option?
- What can transfer from Amharic, other Ethio-Semitic languages, or multilingual models?
- What do quantisation and distillation offer for operating cost?
- For each capability: reuse, adapt, train, or decline?

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

**Depends on:** `02_linguistics`, `03_data_strategy`, `08_evaluation` (you cannot compare models without a way to measure them).

**Gates:** `05_architecture`, `06_ml_pipeline`, `09_training_strategy`, `10_infrastructure`.

## What future researchers should add

Reports answering the questions above, each with a summary. Add new questions to
this list as they surface — the question list is expected to grow as the domain
is explored, and an unanswered question recorded here is more useful than one
carried in someone's head.

## Status

**No research conducted.** This directory contains only this scoping document.
