# System Overview

> **Status: designed** (DEC-012, DEC-013, DEC-014 — 2026-08-03).
> Every element below traces to a decision record. The API surface is **not**
> designed — that is `07_api_mcp`, gated on **A-02**.
>
> **Evidence:** `../research/reports/05_architecture/001-service-decomposition-and-runtime.md`

## Purpose of this document

The top-level view of the platform: what the major components are, how they
relate, and how a request flows through the system. It is the map that orients
everything else in this directory.

## Why this document exists

Someone new to the project — or an AI session with no prior context — needs one
document that explains the shape of the system before descending into any
particular part. Without it, understanding the platform requires reading
everything.

## How to use it

- **Reading:** this is the current design of record for this area. Where it
  conflicts with a decision in
  [`../decisions/DECISIONS.md`](../decisions/DECISIONS.md), the decision wins and
  this document needs updating.
- **Writing:** update it when an Architect-stage decision changes the design.
  Exploratory thinking belongs in `../research/`.
- **Every design element here must trace to a decision record.**

## Relevant principles

**P-11** services are independent · **P-6** optimise for low volume ·
**P-7** prefer boring technology

---

## The organising idea

**The platform is tiered by resource profile, not by domain** (**DEC-013**).

This is the single most important thing to understand about the design, and it is
not the obvious decomposition. Our capabilities differ by **~150× in memory**:
normalising a string is free, while translating one needs a 1.4 GB model. Cold
start differs by a similar factor — microseconds against seconds.

Grouping by domain (a "translation service", a "morphology service") would ignore
the property that actually determines cost, latency, and deployment shape.
Grouping by resource profile makes each tier scale on its own economics.

## Component inventory

| Tier | Components | Footprint | Backing |
| --- | --- | ---: | --- |
| **0** | normalisation · tokenization · transliteration · morphology | **113.4 MB** *(measured; 72 MB was the pre-build estimate)* | pure computation + small tables |
| **1** | embeddings | **+119 MB** | `fgaim/tiroberta-bi-encoder` (Apache-2.0) |
| **2** | translation | **+1,402 MB** | `google/madlad400-3b-mt` (Apache-2.0, DEC-011) |

**Cumulative:** Tier 0 = **113.4 MB** (measured; the 72 MB estimate is superseded) · Tier 0+1 = **232 MB** · Tier 0+1+2 = 1,634 MB.

**Tier 0 + Tier 1 is exactly the DEC-006 minimum viable platform.** Adding
translation multiplies the footprint by **8.3×** — the boundary is a cost cliff,
not a roadmap preference.

## Component relationships

Every capability is an **importable library**; services are **thin wrappers**
(**DEC-012**).

```
  developer's application                    HTTP client / MCP client
            │                                          │
            │ pip install                              │ network
            ▼                                          ▼
  ┌───────────────────────────┐            ┌───────────────────────┐
  │   capability libraries    │◀───────────│  API / MCP services   │
  │  (the actual logic)       │   import   │  transport, auth,     │
  └───────────────────────────┘            │  validation only      │
                                           └───────────────────────┘
```

**No capability logic lives only behind a network call.** The API service imports
exactly what an external developer imports.

## Request lifecycle

A representative Tier 0 request — no model weights, no network hop if used as a
library:

```
  text ──▶ normalise (Ge'ez, orthographic variants)
        ──▶ tokenize (raw Ge'ez — DEC-007 amendment 2)
        ──▶ capability (morphology / embedding / translation)
        ──▶ result, with surface form preserved verbatim
```

**The surface form is never reconstructed from an analysis form** (DEC-007
amendment 1). Analysis is lossy by design; what is returned to a user is always
derived from the original text.

## Service boundaries

Boundaries follow tiers, not domains (**DEC-013**). Consequences:

- **Tiers are never co-located in one process.** A Tier 0 call must never pay
  Tier 2's memory or cold start.
- **Model weights load lazily, per tier, on first use.**
- **No cross-service imports.** Shared logic belongs in a library (**DEC-012**),
  which removes the reason anyone would want one.
- **No shared mutable state between services.** Nothing here needs it and it
  would break P-11 independence.

## Shared vs. per-service infrastructure

| Shared | Per-tier |
| --- | --- |
| Capability libraries (imported, not called over a network) | Model weights |
| Ge'ez normalisation rules | Runtime processes |
| Evaluation harness (DEC-009, DEC-010) | Scaling policy |

## Deployment topology

| Tier | Mode | Rationale |
| --- | --- | --- |
| **0** (113.4 MB measured; 72 MB estimated) | **Always warm**, trivially replicated | Cheap enough that idle cost is negligible; serves latency-sensitive calls. Call `warmup()` at boot — lazy loading defers 3.0 s onto the first caller |
| **1** (191 MB) | Warm, moderate replication | Embedding calls are interactive |
| **2** (1,593 MB) | **Lazily loaded; may scale to zero** | Translation is seconds-scale; users already expect to wait, so cold start is proportionally far less damaging |

This resolves the **A-008** low-volume bind. A 1.4 GB model kept warm costs idle
memory; scaled to zero it costs a cold start on every request. Neither is
acceptable platform-wide — **both are fine for the right tier.** The tension only
exists if the tiers are merged.

## Model runtime

**CTranslate2 (MIT)** serves every model-backed capability (**DEC-014**) —
`T5Config` for MADLAD, `M2M100Config` for the NLLB comparison baseline,
`RobertaConfig` for the embedding encoder. One runtime, one quantisation story
(native int8), one operational surface.

⚠️ **Support is verified; conversion is not.** Converting these specific
checkpoints is an experiment that needs the weights (**A-09**). If it fails, the
fallback is `llama-cpp-python` for MADLAD plus `transformers` for the encoder —
at the cost of two runtimes.

## Failure modes

| Failure | Effect | Acceptable? |
| --- | --- | --- |
| Tier 2 cold / unavailable | Translation unavailable; **Tiers 0–1 unaffected** | Yes — that is why they are separate |
| Model conversion fails | Capability blocked until fallback runtime adopted | Yes, with a recorded decision |
| HornMorpho unusable (**A-07**) | Tier 0 loses morphology; other primitives unaffected | Yes — tier boundaries do not move |
| A tier co-located with another | 150× memory penalty on the cheap path | **No** — this is the failure the design exists to prevent |

## Evolution path

New capabilities join the tier matching their **resource profile**, not their
subject matter. A capability that needs a multi-GB model is Tier 2 regardless of
what it does.

Replacing a model means replacing a library implementation; the service wrapper
and the API surface do not change (**DEC-012**).

## Open questions

- What is the **measured** cold-start cost for Tier 2? Nothing here is measured —
  memory is arithmetic, latency is an experiment (**A-09**).
- Does CTranslate2 conversion succeed on MADLAD-3B and `tiroberta-bi-encoder`?
- Is HornMorpho usable at all, and is its ~48 MB estimate right (**A-07**)?
- Does the API surface (`07_api_mcp`, gated on **A-02**) change any boundary?
- Where does the surface↔analysis alignment layer live if morphology later needs
  it? DEC-007 amendment 2 took it off the critical path; it is in no tier because
  nothing currently needs it.

## Decision log for this area

| Decision | ID | Date | Summary |
| --- | --- | --- | --- |
| Library-first; services are thin wrappers | DEC-012 | 2026-08-03 | Capability logic is importable; no logic exists only behind a network call |
| Tier by resource profile | DEC-013 | 2026-08-03 | ~150× memory spread drives decomposition; tiers never co-located |
| CTranslate2 as single runtime | DEC-014 | 2026-08-03 | One MIT runtime serves T5, M2M100, and Roberta |
| Translation model | DEC-011 | 2026-08-03 | MADLAD-400-3B (Apache-2.0); NLLB quarantined as NC |
| Minimum viable platform | DEC-006 | 2026-07-29 | Primitives + embeddings = Tier 0+1 = 191 MB |
