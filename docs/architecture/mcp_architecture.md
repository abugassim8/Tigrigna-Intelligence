# MCP Architecture

> **Status: not designed.** This document is a scaffold. It contains **no design
> decisions, no technology selections, and no recommendations.** Anything that
> looks like a conclusion here is a placeholder heading.
>
> **Gated on:** `docs/research/reports/07_api_mcp/`.

## Purpose of this document

The design of the Model Context Protocol server: which tools it exposes, how they map onto platform capabilities, and how AI assistants interact with the platform through it.

## Why this document exists

MCP is how AI assistants consume this platform. It is a distinct interface from the HTTP API with different design constraints — tools must be self-describing, appropriately granular, and safe to call without the caller fully understanding Tigrinya linguistics. A well-designed MCP surface makes the platform usable by any AI agent; a poorly designed one makes it usable by none.

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

**P-7** prefer boring technology · **P-14** state uncertainty honestly · **P-11** services are independent

## Sections to be completed

### Tool inventory
Which capabilities are exposed as MCP tools, and which are deliberately not.

### Tool granularity
Where the line sits between one broad tool and several narrow ones.

### Tool descriptions and schemas
How tools describe themselves well enough to be used correctly without prior
knowledge.

### Resources and prompts
What the server exposes beyond tools, if anything.

### Transport and deployment
How the server runs and is connected to.

### Error and uncertainty communication
How a tool reports low confidence or partial success — important given that
callers cannot evaluate Tigrinya output themselves.

### Authentication
If needed.

### Relationship to the HTTP API
Shared implementation or separate, and the tradeoff.

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
