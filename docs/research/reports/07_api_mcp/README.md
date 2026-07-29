# 07 — API, MCP, and SDKs

## Purpose of this document

This directory holds full Analyst-stage research reports for **07 — API, MCP, and SDKs**.

It covers the developer-facing surface: the HTTP API, the MCP server, and the Python and JavaScript SDKs.

## Why this domain exists

Infrastructure nobody can use is not infrastructure (**G-7**). This is the domain that determines whether the platform is adopted or admired. API design is also unusually hard to change once external users depend on it, which makes getting it right early disproportionately valuable.

## Research questions this domain must answer

- What is the right API surface for each capability?
- REST, gRPC, GraphQL, or a combination — and what does the choice cost?
- How are authentication, rate limiting, and quotas handled — and are they needed yet?
- What does the MCP server expose, and how do MCP tools map onto capabilities?
- What are the MCP design conventions we should follow, and what do good MCP servers do?
- What should the Python and JavaScript SDKs look like idiomatically in each language?
- How do we version the API without breaking consumers?
- What does the developer onboarding path look like — install to first successful call?
- How are errors, partial results, and low-confidence outputs communicated honestly?
- What does batch versus streaming look like for each capability?

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

**Depends on:** `05_architecture`, `00_project_definition` (the user question determines the surface).

**Gates:** SDK and service implementation, adoption.

## What future researchers should add

Reports answering the questions above, each with a summary. Add new questions to
this list as they surface — the question list is expected to grow as the domain
is explored, and an unanswered question recorded here is more useful than one
carried in someone's head.

## Status

**No research conducted.** This directory contains only this scoping document.
