# 00 — Project Definition

## Purpose of this document

This directory holds full Analyst-stage research reports for **00 — Project Definition**.

It answers the most basic and most consequential questions: who this is for, what problem is being solved, and what "good" means. Everything downstream inherits these answers.

## Why this domain exists

Scope questions look obvious until you try to answer them, at which point they turn out to determine API design, data priorities, licensing, and sequencing. Getting them wrong is not recoverable by good engineering later — it just means building the right thing for the wrong user. This domain runs first for that reason.

## Research questions this domain must answer

- Who are the primary users? Developers, researchers, institutions, or end-user product teams? (Currently **open** — see `assumptions.md`.)
- What are the concrete use cases, ranked by value?
- What does each capability in the scope list actually mean in practice, and what would "working" look like for each?
- Which capabilities are foundational and which are downstream of them?
- What is the minimum useful platform — the smallest thing that is genuinely valuable to someone?
- Which dialects, registers, and orthographic conventions of Tigrinya are in scope?
- What are the hard functional and non-functional requirements?
- What existing needs are documented by Tigrinya-speaking communities, and what do they say they need?

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

**Depends on:** Nothing. This is the entry point.

**Gates:** Every other domain. Do not start elsewhere without a reason.

## What future researchers should add

Reports answering the questions above, each with a summary. Add new questions to
this list as they surface — the question list is expected to grow as the domain
is explored, and an unanswered question recorded here is more useful than one
carried in someone's head.

## Status

**No research conducted.** This directory contains only this scoping document.
