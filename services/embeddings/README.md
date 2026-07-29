# Service: Embeddings

> **Status: not designed, not implemented.** This is a scoping document. No
> technology has been selected and no decision has been recorded.
>
> **Gated on:** `../../docs/research/reports/04_model_strategy/`

## Purpose of this service

Vector representations of Tigrinya text — the representational substrate for semantic search, retrieval, clustering, deduplication, and similarity.

## Responsibilities

- Produce embeddings for words, sentences, and documents.
- Support batch embedding for corpus-scale work.
- Maintain embedding version compatibility — re-embedding a corpus is expensive.
- Expose dimensionality and model version explicitly.

## Design considerations

- This is a high-leverage service: one good embedding model enables several capabilities at once (**G-4**).
- Morphology matters here more than almost anywhere. If inflected forms of the same lemma embed far apart, every retrieval capability above this degrades (**P-10**, **A-007**).
- Model changes invalidate stored vectors. Versioning must be designed in from the start, not retrofitted.
- Cost per embedding matters at corpus scale — see **P-6**.

## Dependencies

`tokenizer`. Likely `morphology`.

## Before implementing this service

1. The research in `../../docs/research/reports/04_model_strategy/` must be complete, with a summary.
2. A decision must be recorded in
   `../../docs/decisions/DECISIONS.md` covering the approach.
3. An evaluation method must exist — see `../../docs/benchmarks/`. **A capability
   is not built before there is a way to measure it** (**P-4**).
4. The service must be independently runnable and testable (**P-11**).

## Expected layout once implemented

```
embeddings/
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
