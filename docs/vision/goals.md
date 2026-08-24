# Goals

## Purpose of this document

What this project is trying to achieve, at a level between the mission (abstract,
stable) and the roadmap (concrete, dated).

**Why it exists:** A mission is too abstract to plan against and a roadmap is too
specific to survive contact with research findings. Goals sit in between: stable
enough to be useful for months, concrete enough to test a proposal against.

**How to use it:** When prioritising work, check which goal it serves. Work that
serves no goal on this list either needs a goal added — with justification — or
should not be done.

**What future contributors should add:** Refine goals as research clarifies what
is achievable. Move goals to `../roadmap/` once they have dates. Retire goals
that are met or abandoned, with a note on which.

> **Status:** ⚠️ **Written pre-research; all 13 research domains are now
> complete** (updated 2026-08-23). The goals themselves held up — none was
> abandoned — but research changed what each costs, and two changed shape:
>
> | Goal | What research did to it |
> | --- | --- |
> | **G-1** primitives | **Partly delivered.** Normalisation, tokenization and transliteration are built; morphology is a stub (**A-07**) |
> | **G-2** evaluation | **Delivered for translation, and redefined for the rest.** DEC-023 established that primitives are evaluated *intrinsically*, so most of this needs no annotated data — the gold-standard requirement shrank from four capabilities to one |
> | **G-3** translation | **Deprioritised by DEC-006**, which excludes translation from the minimum platform. A model is adopted (DEC-011) but has never been scored |
> | **G-8** data foundation | ⚠️ **Harder than assumed.** Licensing, not scarcity, is the binding constraint: **~99%** of discovered Tigrinya data carries no stated licence |
> | **G-11** contribute back | **Overdue.** A confirmed contamination finding in someone else's dataset is still unreported (**A-03**) |
>
> Nothing here is dated, deliberately. `../roadmap/READINESS_PLAN.md` carries
> the sequence.

---

## Primary goals

### G-1. Make Tigrinya computationally tractable

Provide the foundational primitives — tokenization, morphological analysis,
lemmatization, embeddings — that everything else depends on. Without these,
every downstream capability is built on sand.

*Why it is first:* every other goal has a dependency on this one.

### G-2. Establish trustworthy evaluation for Tigrinya NLP

Build or assemble evaluation sets and metrics that genuinely measure Tigrinya
capability, rather than borrowing metrics validated on other languages and hoping
they transfer.

*Why it matters more than it sounds:* without this, we cannot tell whether
anything we build works, cannot compare approaches, and cannot honestly claim
anything. Evaluation infrastructure is likely to outlive every model we ship.

### G-3. Deliver usable translation and cross-language capability

Translation to and from Tigrinya, and retrieval that works across languages, at
a quality level people will actually use rather than tolerate.

### G-4. Deliver semantic search and retrieval

Embeddings and retrieval that handle Tigrinya's morphology properly — where
searching for one inflected form finds the others, rather than failing on
surface-form mismatch.

### G-5. Deliver correction and assistance tools

Spell correction, grammar checking, and transliteration. These are the
capabilities most immediately visible to end users and the ones whose absence is
felt daily.

### G-6. Build a knowledge layer

Named entity recognition, entity linking, and a knowledge graph — the
infrastructure for question answering and RAG over Tigrinya content.

### G-7. Make it accessible to developers

Clean APIs, an MCP server, and SDKs in Python and JavaScript. Infrastructure
nobody can use is not infrastructure. This goal is why the platform exists in
the form it does rather than as a research artefact.

---

## Supporting goals

### G-8. Build a high-quality Tigrinya data foundation

Corpora, dictionaries, and terminology — sourced legally, cleaned carefully,
documented thoroughly. Data quality is the first priority in the project's
philosophy because nothing downstream can exceed it.

### G-9. Keep operating cost low

The platform must be sustainable to run continuously at low volume. Architectures
that only make sense at scale we do not have are out of scope.

### G-10. Make everything reproducible

Any result that cannot be reproduced from this repository does not exist. This
applies to models, evaluations, and data pipelines alike.

### G-11. Contribute back to the ecosystem

Where licensing and strategy allow, release datasets, evaluation sets, and tools
publicly. A low-resource language ecosystem is not a zero-sum competition;
raising the floor benefits everyone including us.

---

## Goal dependencies

```
G-8 (data) ──────┬──> G-1 (primitives) ──┬──> G-3 (translation)
                 │                       ├──> G-4 (search)
G-2 (evaluation) ┤                       ├──> G-5 (correction)
                 │                       └──> G-6 (knowledge)
                 └──> [gates every claim about every capability]
                                                    │
                                                    v
                                          G-7 (developer access)

G-9, G-10, G-11 apply across all of the above.
```

G-8 and G-2 come first not because they are exciting but because everything else
is invalid without them.

---

## What we are explicitly not committing to

Nothing on this list has a date, a quality target, or a delivery guarantee. Those
require research we have not done. Assigning them now would produce numbers with
no basis, which is worse than having none — see `../roadmap/`.
