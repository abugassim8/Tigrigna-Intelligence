# API Architecture

> **Status: not designed.** This document is a scaffold. It contains **no design
> decisions, no technology selections, and no recommendations.** Anything that
> looks like a conclusion here is a placeholder heading.
>
> **Gated on:** `docs/research/reports/07_api_mcp/` and `00_project_definition` — the API surface depends on who the users are, which is currently open.

## Purpose of this document

The design of the developer-facing HTTP API: surface, conventions, versioning, authentication, error handling, and the contract we offer consumers.

## Why this document exists

Infrastructure nobody can use is not infrastructure. The API is where the platform meets its users, and it is unusually expensive to change once external consumers depend on it — which makes early care here disproportionately valuable.

## How to use it

- **Reading:** this is the current design of record for this area. Where it
  conflicts with a decision in
  [`../decisions/DECISIONS.md`](../decisions/DECISIONS.md), the decision wins and
  this document needs updating.
- **Writing:** update it when an Architect-stage decision changes the design. Do
  not use it as a scratchpad for ideas — exploratory thinking belongs in
  `../research/`. This document holds what we have *decided*, not what we are
  *considering*.
- **Every design element here must trace to a decision record.** Design without a
  recorded decision behind it is how projects end up unable to explain
  themselves.

## Relevant principles

**P-7** prefer boring technology · **P-8** measure before claiming · **P-14** state uncertainty honestly

## Sections to be completed

### API surface
Endpoints per capability, and the reasoning behind the grouping.

### Protocol and conventions
Request/response shapes, naming, pagination, idempotency.

### Versioning strategy
How the API evolves without breaking consumers.

### Authentication and authorisation
If and when needed — see **N-9**, no hosted commercial service yet.

### Rate limiting and quotas

### Error handling
Including how low-confidence output and partial results are communicated
honestly rather than silently.

### Batch and streaming
Which capabilities need which, and why.

### Documentation and discoverability
Including the install-to-first-successful-call path.

### SDK alignment
How the Python and JavaScript SDKs map onto this surface.

## Open questions

To be populated by research. Record questions here as they surface, even before
they can be answered — a written open question is worth more than one someone is
carrying around in their head.

## Decision log for this area

| Decision | ID | Date | Summary |
| --- | --- | --- | --- |
| — | — | — | *No decisions recorded* |

## What future contributors should add

The actual design, once research supports it. Diagrams where they clarify.
Rationale linked to decision records. Keep it current — an architecture document
that has drifted from reality is worse than none, because people trust it.
