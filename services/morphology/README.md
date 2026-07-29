# Service: Morphological Analysis

> **Status: not designed, not implemented.** This is a scoping document. No
> technology has been selected and no decision has been recorded.
>
> **Gated on:** `../../docs/research/reports/02_linguistics/`

## Purpose of this service

Analysis of Tigrinya word structure: segmentation, root and pattern identification, inflectional and derivational features, and lemmatization.

## Responsibilities

- Analyse surface forms into their morphological components.
- Produce lemmas for inflected forms.
- Expose morphological features for downstream consumers.
- Handle orthographic variation encountered in real text.

## Design considerations

- **This may be the most consequential service in the platform.** Tokenization, embeddings, retrieval, spellcheck, and grammar checking all depend on getting morphology right; errors here propagate everywhere and are expensive to correct later (**P-10**).
- Assumption **A-007** — that morphological complexity is a first-order design constraint — is currently unverified and should be resolved early in `02_linguistics`.
- Rule-based, statistical, and neural approaches all warrant evaluation. Rule-based approaches often perform disproportionately well for low-resource languages, and are cheaper to run.
- Existing Ethio-Semitic morphological tools may transfer — check before building (**P-1**).

## Dependencies

`tokenizer`, potentially bidirectionally — the relationship between tokenization and morphological analysis is itself a design question.

## Before implementing this service

1. The research in `../../docs/research/reports/02_linguistics/` must be complete, with a summary.
2. A decision must be recorded in
   `../../docs/decisions/DECISIONS.md` covering the approach.
3. An evaluation method must exist — see `../../docs/benchmarks/`. **A capability
   is not built before there is a way to measure it** (**P-4**).
4. The service must be independently runnable and testable (**P-11**).

## Expected layout once implemented

```
morphology/
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
