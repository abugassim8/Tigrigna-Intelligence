# Service: Grammar Checking

> **Status: not designed, not implemented.** This is a scoping document. No
> technology has been selected and no decision has been recorded.
>
> **Gated on:** `../../docs/research/reports/02_linguistics/`

## Purpose of this service

Detection and correction of grammatical errors in Tigrinya text.

## Responsibilities

- Detect grammatical errors.
- Suggest corrections with explanations where possible.
- Distinguish errors from legitimate dialectal or stylistic variation.
- Report confidence, and prefer silence over a wrong correction.

## Design considerations

- Requires a clear position on what counts as correct Tigrinya — a normative question with real sensitivity, given dialectal variation. Should be settled in `02_linguistics` and `00_project_definition`, not decided implicitly in code.
- **False positives are worse than false negatives here.** A tool that flags correct writing as wrong is quickly abandoned, and it is worse than that for a language where users may be uncertain of their own correctness.
- Error-annotated Tigrinya data does not plausibly exist and would need creating.
- Depends heavily on morphological analysis quality.

## Dependencies

`tokenizer`, `morphology`. Possibly `spellcheck`.

## Before implementing this service

1. The research in `../../docs/research/reports/02_linguistics/` must be complete, with a summary.
2. A decision must be recorded in
   `../../docs/decisions/DECISIONS.md` covering the approach.
3. An evaluation method must exist — see `../../docs/benchmarks/`. **A capability
   is not built before there is a way to measure it** (**P-4**).
4. The service must be independently runnable and testable (**P-11**).

## Expected layout once implemented

```
grammar/
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
