# Mission

## Purpose of this document

The definitive statement of why this project exists. It is the reference point
for judging whether any proposed work belongs here.

**Why it exists:** Projects with wide scope drift. Without a fixed statement of
purpose, every plausible adjacent idea looks like it belongs, and the project
slowly becomes something nobody chose. This document is the thing you hold work
up against.

**How to use it:** When evaluating any proposal — a feature, a service, a
research direction — ask whether it advances this mission. If the honest answer
is "not really, but it would be interesting", the answer is no.

**What future contributors should add:** Very little. This should change rarely.
Amendments belong in `CHANGELOG.md` with reasoning. If it is changing often, the
project does not know what it is.

---

## Mission

**Build the foundational AI infrastructure for Tigrinya language intelligence.**

---

## The problem

Tigrinya (ትግርኛ) is spoken by millions of people across Eritrea and Ethiopia and
by a substantial diaspora. It has a rich literary tradition and a written history
in the Ge'ez script going back centuries.

It has almost none of the language technology that speakers of high-resource
languages use without thinking about it. Where speakers of English, Mandarin, or
Spanish have translation, search that understands their queries, spell checking,
grammar assistance, and voice interfaces available by default, Tigrinya speakers
mostly have none of it — or have versions so poor as to be unusable.

This is not because the problems are unsolvable. It is because the foundational
layer nobody sees — the tokenizers, embeddings, morphological analysers,
evaluation sets, and APIs that everything else is built on — has not been built.

## What we are building

**Language infrastructure.** The layer underneath the applications.

We are building the components that a developer, researcher, institution, or
product team needs in order to build something useful in Tigrinya *without*
first having to solve computational linguistics themselves.

Concretely, this eventually means translation, semantic search, cross-language
retrieval, embeddings, grammar checking, spell correction, transliteration,
morphological analysis, lemmatization, named entity recognition, entity linking,
a knowledge graph, RAG capabilities, summarization, question answering,
developer APIs, an MCP server, and SDKs.

The full scope is in [`../../PROJECT_CONTEXT.md`](../../PROJECT_CONTEXT.md).
Scope is not roadmap — sequencing is a research output.

## What we are not building

**We are not building a news application.** We are not building a content
product, a reader, an aggregator, or a media platform of any kind. If work
starts trending toward an end-user content experience, it has left the mission.

The test: *would another team be able to build their product on top of this?* If
what we are building is itself the product, we have drifted.

See [`non_goals.md`](non_goals.md) for the maintained list.

## Why infrastructure rather than an application

Three reasons.

**Leverage.** One good Tigrinya embedding model enables search, retrieval,
clustering, deduplication, and recommendation across every application anyone
builds. One good application enables one application.

**Durability.** Applications are replaced. Infrastructure — tokenizers,
evaluation sets, morphological analysers, annotated corpora — remains useful for
decades. The most valuable thing this project could produce is a well-built
evaluation set that outlives every model we ever ship.

**Honesty about advantage.** We have no particular advantage in building
consumer products. The advantage available here is in doing the unglamorous
foundational work that nobody else is doing, and doing it carefully.

## How we work

Reuse before building. Measure before claiming. Document before moving on.

The core philosophy — reuse existing models whenever possible, train only when
proprietary advantage exists, and prioritise data quality, evaluation,
reproducibility, low operating cost, and maintainability in that order — is
stated in full in [`../../PROJECT_CONTEXT.md`](../../PROJECT_CONTEXT.md) and
elaborated in [`principles.md`](principles.md).

## What success looks like

Someone builds something valuable in Tigrinya, quickly, because this platform
existed — and they never had to think about tokenization, morphology, or
evaluation to do it.

Measurable definitions are in [`success_metrics.md`](success_metrics.md).
