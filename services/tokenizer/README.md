# Service: Tokenizer

> **Status: not designed, not implemented.** This is a scoping document. No
> technology has been selected and no decision has been recorded.
>
> **Gated on:** `../../docs/research/reports/02_linguistics/`

## Purpose of this service

Text segmentation and normalisation for Tigrinya — the lowest-level primitive in the platform.

## Responsibilities

- Segment Tigrinya text into tokens or subwords.
- Normalise Ge'ez script: Unicode normalisation, variant character handling.
- Handle punctuation, numerals, and mixed-script text.
- Provide consistent, reversible tokenization across all services.

## Design considerations

- **Everything depends on this.** A tokenizer that handles Ge'ez script or Tigrinya morphology poorly degrades every capability above it, usually in ways that are hard to attribute back to the tokenizer.
- Ge'ez script normalisation is a real problem: variant spellings and Unicode representation issues must be handled consistently or identical words will fail to match.
- Subword tokenizer fertility on Tigrinya is worth measuring early — poor fertility inflates cost and degrades quality simultaneously.
- Changing the tokenizer later invalidates embeddings and trained models. This is a decision to get right early.

## Dependencies

None. This is the base primitive and should be among the first things built.

## Before implementing this service

1. The research in `../../docs/research/reports/02_linguistics/` must be complete, with a summary.
2. A decision must be recorded in
   `../../docs/decisions/DECISIONS.md` covering the approach.
3. An evaluation method must exist — see `../../docs/benchmarks/`. **A capability
   is not built before there is a way to measure it** (**P-4**).
4. The service must be independently runnable and testable (**P-11**).

## Expected layout once implemented

```
tokenizer/
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
