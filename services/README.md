# Services

## Purpose of this directory

The runtime components of the platform. One directory per capability.

## Why this directory exists

The platform is a collection of capabilities, not a monolith. Each gets its own
service so that it can be developed, evaluated, deployed, and — critically —
**replaced** independently. Research will change our minds about how several of
these should work; the structure exists so that changing our mind is a
replacement rather than a rewrite (**P-11**).

> ⚠️ **This layout predates DEC-013.** "One directory per capability" is a
> *domain* decomposition, which DEC-013 explicitly rejected in favour of
> **resource tiers** after measuring a ~150× memory spread across capabilities.
> [`primitives/`](primitives/) is the built Tier 0 and spans what this table
> calls `tokenizer/`, `morphology/`, and part of `spellcheck/`. Reconciling the
> rest of the layout with DEC-013 is outstanding.

## Built

| Package | Tier | Status |
| --- | --- | --- |
| [`primitives/`](primitives/) | **Tier 0** | ✅ normalisation, tokenization, transliteration — 61 property tests passing. **Morphology blocked on A-07** |

## Services (scaffold — pre-DEC-013)

| Service | Capability | Depends on |
| --- | --- | --- |
| [`tokenizer/`](tokenizer/) | Segmentation and Ge'ez script normalisation | — |
| [`morphology/`](morphology/) | Morphological analysis, lemmatization | tokenizer |
| [`embeddings/`](embeddings/) | Vector representations | tokenizer, morphology |
| [`retrieval/`](retrieval/) | Semantic and cross-language search, RAG retrieval | embeddings |
| [`translation/`](translation/) | Machine translation to and from Tigrinya | tokenizer |
| [`spellcheck/`](spellcheck/) | Spell correction and transliteration | morphology |
| [`grammar/`](grammar/) | Grammar checking | morphology |
| [`ner/`](ner/) | Named entity recognition | morphology |
| [`knowledge_graph/`](knowledge_graph/) | Entity linking, knowledge graph | ner, retrieval |
| [`api/`](api/) | Public HTTP interface | all capabilities |
| [`mcp/`](mcp/) | Model Context Protocol server | all capabilities |

## Build order

The dependency structure implies the order. `tokenizer` and `morphology` are the
base primitives — everything else degrades if they are wrong, usually in ways
that are hard to attribute back to them. `api` and `mcp` aggregate and come late.
`knowledge_graph` depends on nearly everything.

This ordering is a consequence of the dependencies, not a schedule. Actual
sequencing comes from `../docs/research/reports/12_master_blueprint/`.

## Rules for every service

1. **Independent.** Runs, tests, and deploys on its own. Cross-service imports
   are a design smell — raise them rather than working around them (**P-11**).
2. **Decision first.** Nothing is implemented without a record in
   `../docs/decisions/DECISIONS.md`.
3. **Evaluation first.** No capability is built before there is an agreed way to
   measure it (**P-4**).
4. **Honest about uncertainty.** Services report confidence and say when output
   is unreliable. Consumers usually cannot evaluate Tigrinya output themselves,
   which makes silent low quality actively dangerous (**P-14**).
5. **Cheap to run.** Operating cost at low volume is a design constraint, not an
   afterthought (**P-6**).
6. **Documented.** Each service README describes what it does, its measured
   performance, and its known limitations.

## What future contributors should add

Implementations, once the gating research and decisions exist. Update each
service README to describe reality rather than intent.

## Status

**No services implemented.** Every directory contains only a scoping document.
