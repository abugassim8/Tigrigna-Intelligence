# Service: Translation

> **Status: not designed, not implemented.** This is a scoping document. No
> technology has been selected and no decision has been recorded.
>
> **Gated on:** `../../docs/research/reports/04_model_strategy/` and `03_data_strategy/`

## Purpose of this service

Machine translation to and from Tigrinya.

## Responsibilities

- Translate Tigrinya → other languages and other languages → Tigrinya.
- Expose language-pair support explicitly, including quality per pair.
- Handle document-level and sentence-level input.
- Report confidence, and be honest when output is unreliable.

## Design considerations

- Which language pairs matter is an open question (`00_project_definition`).
- Translation quality metrics may not be valid for Tigrinya — see `../../docs/benchmarks/metrics.md`. A BLEU score alone will not be sufficient evidence.
- Reuse before training (**P-1**, **P-2**). Existing multilingual models are the first thing to evaluate, measured on Tigrinya rather than trusted on multilingual averages.
- Parallel data availability is likely the binding constraint.

## Dependencies

`tokenizer`. Possibly `morphology`.

## Before implementing this service

1. The research in `../../docs/research/reports/04_model_strategy/` and `03_data_strategy/` must be complete, with a summary.
2. A decision must be recorded in
   `../../docs/decisions/DECISIONS.md` covering the approach.
3. An evaluation method must exist — see `../../docs/benchmarks/`. **A capability
   is not built before there is a way to measure it** (**P-4**).
4. The service must be independently runnable and testable (**P-11**).

## Expected layout once implemented

```
translation/
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
