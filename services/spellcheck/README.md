# Service: Spell Correction

> **Status: not designed, not implemented.** This is a scoping document. No
> technology has been selected and no decision has been recorded.
>
> **Gated on:** `../../docs/research/reports/02_linguistics/`

## Purpose of this service

Detection and correction of spelling errors in Tigrinya text, plus transliteration between Ge'ez script and Latin representations.

## Responsibilities

- Detect misspelled words.
- Rank correction candidates.
- Handle morphologically inflected forms without flagging them as errors.
- Provide transliteration: Ge'ez ↔ Latin, in both directions.

## Design considerations

- Naive dictionary-based spellchecking fails badly on morphologically rich languages, since the set of valid inflected forms is far larger than any word list. Morphological analysis is likely required rather than optional (**P-10**).
- Requires a decision on orthographic standards, given real variation in written Tigrinya.
- Transliteration schemes vary; which to support is a research question, and supporting several may be necessary.
- This is one of the most immediately useful capabilities to end users, which makes quality expectations high.

## Dependencies

`tokenizer`, `morphology`, `dictionaries` data.

## Before implementing this service

1. The research in `../../docs/research/reports/02_linguistics/` must be complete, with a summary.
2. A decision must be recorded in
   `../../docs/decisions/DECISIONS.md` covering the approach.
3. An evaluation method must exist — see `../../docs/benchmarks/`. **A capability
   is not built before there is a way to measure it** (**P-4**).
4. The service must be independently runnable and testable (**P-11**).

## Expected layout once implemented

```
spellcheck/
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
