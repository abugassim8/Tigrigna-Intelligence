# 03 — Data Strategy

## Purpose of this document

This directory holds full Analyst-stage research reports for **03 — Data Strategy**.

It covers where data comes from, under what licence, how it is cleaned and normalised, how it is annotated, and how quality is assured.

## Why this domain exists

Data quality is the first priority in the project's philosophy, and for a low-resource language it is the binding constraint on nearly everything. This is likely the highest-leverage domain in the project. It is also where the most serious legal and ethical risks live — licensing, provenance, and consent are not paperwork, they determine whether anything built on the data can be used at all (**A-009**, **P-9**).

## Research questions this domain must answer

- What Tigrinya text data exists, where, at what scale, and under what licence?
- What is the realistic total volume of usable Tigrinya text available?
- What data can be collected legally and ethically, and how?
- What cleaning and normalisation is required before the data is usable? (See `02_linguistics`.)
- What annotation is needed, for which capabilities, at what cost?
- How do we build evaluation sets that are trustworthy and uncontaminated by training data?
- What dictionaries, terminology resources, and parallel corpora exist?
- How do we handle dialectal and register variation in the corpus?
- What are the provenance, consent, and ethical obligations for human-sourced data?
- How is data versioned, stored, and made reproducible?

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

**Depends on:** `01_ecosystem`, `02_linguistics`.

**Gates:** `04_model_strategy`, `08_evaluation`, `09_training_strategy`, and everything built on them.

## What future researchers should add

Reports answering the questions above, each with a summary. Add new questions to
this list as they surface — the question list is expected to grow as the domain
is explored, and an unanswered question recorded here is more useful than one
carried in someone's head.

## Status

**1 report complete.** `001-corpus-inventory-and-contamination.md` (2026-07-29)
**measured** the available corpus rather than estimating it: 67,153
monolingual/QA rows plus 1.4M parallel pairs. Two findings dominate —
**~99% of rows carry no usable licence** (cleanly licensed: 15,053 documents),
and `farefaine/tigrinya-pretraining` **verifiably contains** TiQuAD validation data
despite being advertised for pretraining. → **DEC-008**.
See `../../summaries/005-corpus-inventory-and-contamination.md`.

**Open:** verify the `farefaine`/TiQuAD row overlap (egress-blocked); licence
clarification outreach; HornMT; orthographic-variation survey for DEC-007.
