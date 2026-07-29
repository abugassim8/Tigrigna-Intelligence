# 10 — Infrastructure

## Purpose of this document

This directory holds full Analyst-stage research reports for **10 — Infrastructure**.

It covers compute, deployment, hosting, monitoring, and the operational cost of running the platform.

## Why this domain exists

Low operating cost is a stated priority (**A-008**, **P-6**), and infrastructure is where that priority is either honoured or quietly abandoned. The relevant question for this project is cost at *low* volume sustained over a long period — not cost at scale, which is the question most infrastructure guidance answers.

## Research questions this domain must answer

- What does the platform cost to run at realistic low volume?
- Where does it get hosted, and what are the real options at this budget?
- CPU or GPU inference — what does each capability actually need?
- What does the minimum viable deployment look like?
- How do cold starts, scale-to-zero, and idle cost behave for each capability?
- Docker, Kubernetes, or something simpler — and is Kubernetes justified at our size?
- What monitoring and alerting is needed, and what is the cheapest adequate option?
- How are secrets, configuration, and environments managed?
- What is the backup, recovery, and data durability story?
- What does scaling up look like *when needed* — without paying for it now?

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

**Depends on:** `05_architecture`, `04_model_strategy` (model choice drives hardware and therefore cost).

**Gates:** Deployment, `11_business` (operating cost is an input to sustainability).

## What future researchers should add

Reports answering the questions above, each with a summary. Add new questions to
this list as they surface — the question list is expected to grow as the domain
is explored, and an unanswered question recorded here is more useful than one
carried in someone's head.

## Status

**No research conducted.** This directory contains only this scoping document.
