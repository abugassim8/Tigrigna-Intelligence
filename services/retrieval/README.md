# Service: Retrieval

> **Status: not designed, not implemented.** This is a scoping document. No
> technology has been selected and no decision has been recorded.
>
> **Gated on:** `../../docs/research/reports/05_architecture/` and `08_evaluation/`

## Purpose of this service

Semantic search and cross-language retrieval over Tigrinya content — including the RAG retrieval layer.

## Responsibilities

- Index documents and serve semantic search.
- Support cross-language retrieval: query in one language, retrieve in another.
- Support hybrid retrieval combining lexical and semantic signals, if research supports it.
- Serve as the retrieval layer for RAG capabilities.

## Design considerations

- Lexical retrieval over a morphologically rich language needs morphological normalisation, or surface-form mismatch will cause silent recall failures.
- Vector store choice is an architecture decision with operating-cost implications (**P-6**).
- Retrieval quality metrics require a Tigrinya evaluation set that does not currently exist.
- Cross-language retrieval quality is bounded by the translation and embedding layers beneath it.

## Dependencies

`embeddings`, `tokenizer`. Likely `morphology`.

## Before implementing this service

1. The research in `../../docs/research/reports/05_architecture/` and `08_evaluation/` must be complete, with a summary.
2. A decision must be recorded in
   `../../docs/decisions/DECISIONS.md` covering the approach.
3. An evaluation method must exist — see `../../docs/benchmarks/`. **A capability
   is not built before there is a way to measure it** (**P-4**).
4. The service must be independently runnable and testable (**P-11**).

## Expected layout once implemented

```
retrieval/
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
