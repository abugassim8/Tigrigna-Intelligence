# Service: MCP Server

> **Status: not designed, not implemented.** This is a scoping document. No
> technology has been selected and no decision has been recorded.
>
> **Gated on:** `../../docs/research/reports/07_api_mcp/`

## Purpose of this service

The Model Context Protocol server — how AI assistants and agents consume the platform's capabilities.

## Responsibilities

- Expose platform capabilities as MCP tools.
- Provide clear, self-describing tool schemas.
- Handle errors and low-confidence output in a way callers can act on.
- Keep parity with the HTTP API where it makes sense.

## Design considerations

- MCP has different design constraints from a REST API: tools must be usable by a caller with no prior knowledge of Tigrinya linguistics, based on the tool description alone.
- Tool granularity is the key design question — one broad tool or several narrow ones changes usability substantially.
- **Uncertainty communication matters unusually much here.** An AI caller cannot evaluate Tigrinya output quality itself, so the tool must say when it is unsure (**P-14**).
- Whether this shares an implementation with the HTTP API is an architecture decision with real maintenance consequences.

## Dependencies

The capability services it exposes, and possibly `api`.

## Before implementing this service

1. The research in `../../docs/research/reports/07_api_mcp/` must be complete, with a summary.
2. A decision must be recorded in
   `../../docs/decisions/DECISIONS.md` covering the approach.
3. An evaluation method must exist — see `../../docs/benchmarks/`. **A capability
   is not built before there is a way to measure it** (**P-4**).
4. The service must be independently runnable and testable (**P-11**).

## Expected layout once implemented

```
mcp/
├── README.md           This file, updated with the real design
├── src/                Implementation
├── tests/              Unit and integration tests
├── config/             Configuration, no secrets
├── Dockerfile
└── pyproject.toml      Or equivalent
```

## What future contributors should add

The real design and implementation, once the gating research and decision exist.
Update this README to describe what the service actually does — including its
measured performance and its known limitations.
