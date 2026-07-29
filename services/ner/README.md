# Service: Named Entity Recognition

> **Status: not designed, not implemented.** This is a scoping document. No
> technology has been selected and no decision has been recorded.
>
> **Gated on:** `../../docs/research/reports/03_data_strategy/` and `04_model_strategy/`

## Purpose of this service

Identification and classification of named entities in Tigrinya text — people, places, organisations, dates, and other domain-relevant types.

## Responsibilities

- Detect entity spans in Tigrinya text.
- Classify entities into an agreed type scheme.
- Report confidence per entity.
- Feed the entity linking and knowledge graph services.

## Design considerations

- The entity type scheme is a design decision that should be driven by use cases (`00_project_definition`), not copied from an English-language standard.
- Annotated Tigrinya NER training data almost certainly does not exist at useful scale and would need to be created — a significant cost to establish before committing.
- Morphological affixes on entity names complicate span detection.
- Transliterated and code-switched names are a known hard case worth scoping early.

## Dependencies

`tokenizer`, `morphology`.

## Before implementing this service

1. The research in `../../docs/research/reports/03_data_strategy/` and `04_model_strategy/` must be complete, with a summary.
2. A decision must be recorded in
   `../../docs/decisions/DECISIONS.md` covering the approach.
3. An evaluation method must exist — see `../../docs/benchmarks/`. **A capability
   is not built before there is a way to measure it** (**P-4**).
4. The service must be independently runnable and testable (**P-11**).

## Expected layout once implemented

```
ner/
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
