# Service: Knowledge Graph

> **Status: not designed, not implemented.** This is a scoping document. No
> technology has been selected and no decision has been recorded.
>
> **Gated on:** `../../docs/research/reports/05_architecture/`

## Purpose of this service

Entity linking and the structured knowledge layer — connecting recognised entities to a knowledge base and supporting structured queries.

## Responsibilities

- Link recognised entities to canonical knowledge base identifiers.
- Store and serve entity relationships.
- Support structured queries over the graph.
- Underpin question answering and knowledge-grounded RAG.

## Design considerations

- Requires a decision on the knowledge base: existing external base, our own, or a hybrid. Each has very different cost and maintenance profiles (**P-1**).
- Tigrinya coverage in existing knowledge bases is likely sparse — worth measuring before designing around it.
- Graph storage choice has operating-cost implications (**P-6**).
- This is among the most dependency-heavy capabilities in the platform and correspondingly furthest out — see `../../docs/roadmap/1_year.md`.

## Dependencies

`ner`, `embeddings`, `retrieval`.

## Before implementing this service

1. The research in `../../docs/research/reports/05_architecture/` must be complete, with a summary.
2. A decision must be recorded in
   `../../docs/decisions/DECISIONS.md` covering the approach.
3. An evaluation method must exist — see `../../docs/benchmarks/`. **A capability
   is not built before there is a way to measure it** (**P-4**).
4. The service must be independently runnable and testable (**P-11**).

## Expected layout once implemented

```
knowledge_graph/
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
