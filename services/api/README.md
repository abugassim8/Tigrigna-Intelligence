# Service: API Gateway

> **Status: not designed, not implemented.** This is a scoping document. No
> technology has been selected and no decision has been recorded.
>
> **Gated on:** `../../docs/research/reports/07_api_mcp/`

## Purpose of this service

The public HTTP interface to the platform. It is the front door: routing, validation, authentication where needed, rate limiting, and consistent error handling across every capability.

## Responsibilities

- Expose platform capabilities over a coherent, versioned HTTP API.
- Validate requests and return useful, honest errors.
- Route to the capability services behind it.
- Enforce rate limits and quotas, if and when they are needed.
- Present a single consistent contract, so consumers do not see service boundaries.

## Design considerations

- API surface design is expensive to change once consumers depend on it — this is the service where early care pays most.
- Errors, partial results, and low-confidence output must be communicated honestly (**P-14**). Callers generally cannot evaluate Tigrinya output themselves.
- Versioning strategy must be decided before the first external consumer, not after.
- Authentication may not be needed yet — see **N-9**.

## Dependencies

All capability services. This is the aggregation point, so it should be built after the capabilities it fronts.

## Before implementing this service

1. The research in `../../docs/research/reports/07_api_mcp/` must be complete, with a summary.
2. A decision must be recorded in
   `../../docs/decisions/DECISIONS.md` covering the approach.
3. An evaluation method must exist — see `../../docs/benchmarks/`. **A capability
   is not built before there is a way to measure it** (**P-4**).
4. The service must be independently runnable and testable (**P-11**).

## Expected layout once implemented

```
api/
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
