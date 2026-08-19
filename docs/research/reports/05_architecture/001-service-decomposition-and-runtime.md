# Architecture: Tier by Resource Profile, Not by Domain

| Field | Value |
| --- | --- |
| **Report ID** | `001-service-decomposition-and-runtime` |
| **Domain** | `05_architecture` |
| **Stage** | Scout → Analyst → Architect |
| **Date** | 2026-08-03 |
| **Status** | Accepted |
| **Summary** | `docs/research/summaries/008-architecture-tiers-and-runtime.md` |
| **Related decisions** | **DEC-012**, **DEC-013**, **DEC-014**; validates DEC-006; engages DEC-002, DEC-011, A-008, P-6, P-11 |

---

## Objective

Decide the shape of the system: what the services are, where the boundaries fall,
how models are served, and what runs where. `system_overview.md` is a scaffold
gated on this report.

**Method note.** Architecture is usually argued rather than measured. Two things
here *are* measurable and were measured: the **resource footprint** of each
capability (arithmetic from verified parameter counts) and the **runtime
landscape** (installed and inspected, not read about).

---

## Finding 1 — Our capabilities differ by ~150× in memory. That is the architecture.

| Capability | Backing | Footprint | Tier |
| --- | --- | ---: | --- |
| Normalisation | pure Python | ~0 | **0** |
| Tokenization | vocabulary only | 10 MB | **0** |
| Transliteration | epitran tables | 14 MB | **0** |
| Morphology | HornMorpho rules | ~48 MB | **0** |
| Embeddings | `tiroberta-bi-encoder` int8 | 119 MB | **1** |
| **Translation** | **MADLAD-400-3B Q4** | **1,402 MB** | **2** |

**A translation request needs ~150× the memory of a tokenization request.** Cold
start differs by a similar factor: loading a 1.4 GB model takes seconds, while
normalising a string takes microseconds.

**Co-locating these in one process is the mistake this report exists to
prevent.** It would mean a 1.6 GB resident footprint to normalise a string, and —
under scale-to-zero, which **A-008** pushes toward — a multi-second cold start on
an operation that should take microseconds.

The natural decomposition is therefore **not by domain** (translation service,
morphology service, NER service) but **by resource profile**:

| Tier | Contents | Cumulative | Scaling behaviour |
| --- | --- | ---: | --- |
| **0** | normalisation, tokenization, transliteration, morphology | **72 MB** *(estimate; **113.4 MB** measured once built)* | always warm; trivially replicated |
| **1** | + embeddings | **191 MB** | warm; moderate replication |
| **2** | + translation | **1,593 MB** | lazily loaded; may scale to zero |

→ **DEC-013.**

## Finding 2 — DEC-006's minimum viable platform fits in 191 MB

**DEC-006** chose primitives + embeddings as the MVP and explicitly excluded
translation. That decision was made on *gap-filling* grounds — the ecosystem has
holes at Layer 0 and Layer 5, not in the middle.

The resource arithmetic **independently validates it**:

- MVP (Tier 0 + Tier 1) = **191 MB**
- Adding translation = **1,593 MB**, an **8.3× jump** from one capability

A decision taken for strategic reasons turns out to also be the cheap one. That
is worth recording precisely because it was not the argument at the time —
**DEC-006 gets support from evidence it was not built on.**

It also sharpens the boundary: translation is not merely "later," it is the point
where the platform's cost profile changes by an order of magnitude. That belongs
in the deployment story, not as a footnote.

## Finding 3 — One MIT-licensed runtime covers every model we have

`[verified]` by installing **CTranslate2 4.8.1 (MIT)** and inspecting its
converter registry — 42 supported HuggingFace architectures, including:

| Config | Our model | Capability |
| --- | --- | --- |
| `T5Config` | `google/madlad400-3b-mt` | translation (**DEC-011**) |
| `M2M100Config` | `facebook/nllb-200-*` | comparison baseline (**DEC-011**) |
| `RobertaConfig` | `fgaim/tiroberta-bi-encoder` | embeddings (**DEC-003**) |

**A single runtime serves all three.** That is an unusually clean result: one
dependency, one quantisation story (CTranslate2 does int8 natively), one
operational surface, MIT-licensed throughout.

Runtime landscape, `[verified]` from PyPI:

| Package | Version | Licence |
| --- | --- | --- |
| **ctranslate2** | 4.8.1 | **MIT** |
| llama-cpp-python | 0.3.34 | MIT |
| onnxruntime | 1.28.0 | MIT |
| optimum | 2.3.0 | Apache-2.0 |

`llama-cpp-python` remains a viable alternative for the published MADLAD GGUF
quantisations, but it does not serve the Roberta encoder, so it would mean two
runtimes. **P-7 (prefer boring technology)** and one-runtime simplicity favour
CTranslate2.

→ **DEC-014.**

## Finding 4 — Library-first, because our users are developers and our volume is low

Two standing constraints point the same way:

- **DEC-002** — primary users are **application developers**. Developers want
  `pip install`, not a service to operate.
- **P-6 / A-008** — optimise for low volume. **A library has zero serving cost at
  zero volume**, which no service topology can match.

Tier 0 is the decisive case. Normalisation, tokenization, transliteration and
morphology are pure computation over small data. Requiring a running service for
them would impose infrastructure on the exact users who most need the primitives
and least want the operations burden — and would add network latency to
operations measured in microseconds.

**Therefore: every capability is a library first; services are thin wrappers.**
The API service imports the same libraries an external developer would. Nothing
exists only behind a network call.

This also satisfies **P-11** (services independent) and the `CONTRIBUTING.md`
rule that each service be runnable and testable alone — a service whose logic is
in a library is trivially testable without the service.

→ **DEC-012.**

## Finding 5 — The low-volume cold-start tension, and how tiering resolves it

**A-008** says the platform must be affordable at low volume. That creates a bind
for a 1.4 GB model:

- **Keep it warm** → pay for idle memory continuously.
- **Scale to zero** → pay a multi-second cold start on every request.

Neither is acceptable *for the platform as a whole*. Both are acceptable *for the
right tier*:

- **Tier 0 (113.4 MB measured, 72 MB estimated here) stays warm.** Cheap enough that idle cost is negligible, and
  it serves the latency-sensitive operations.
- **Tier 2 (1.4 GB) may scale to zero.** Translation is a
  seconds-scale operation whose users already expect to wait; a cold start is
  proportionally far less damaging than it would be on a tokenize call.

**The tension is only unresolvable if the tiers are merged.** Splitting them
converts an architectural problem into a deployment parameter.

## Finding 6 — What this forecloses, stated plainly

- **No shared mutable state between services.** Nothing here needs it, and
  introducing it would break the independence P-11 requires.
- **No cross-service imports.** `CONTRIBUTING.md` already calls these a design
  smell; the library-first rule removes the reason anyone would want one —
  shared logic goes in a library, not another service.
- **No single "do everything" container.** Finding 1 is the reason. If someone
  proposes it for convenience, the 150× memory spread is the counter-argument.
- **Deferred deliberately:** the surface↔analysis alignment layer. DEC-007's
  second amendment took it off the critical path when the tokenizer moved to raw
  Ge'ez. It is not in any tier because nothing currently needs it.

## Limits of this report

- **Memory is arithmetic; latency is not measured.** Model downloads are
  egress-blocked, so no throughput, cold-start, or per-request figure here is
  measured — the report deliberately contains none. **A-09.**
- **HornMorpho's footprint (~48 MB) is an estimate**, not a measurement — its
  licence and Tigrinya version are still unresolved (**A-07**). If it is
  unusable, Tier 0 loses morphology and the tier boundaries do not change.
- **CTranslate2 conversion is verified as *supported*, not as *working* for these
  specific checkpoints.** The converter registry lists the architectures; actually
  converting MADLAD-3B is an experiment that needs the weights.
- **No API surface design.** That is `07_api_mcp`, and it is gated on **A-02**
  (DEC-002 confirmation).

---

## Decisions arising

- **DEC-012** — Library-first; services are thin wrappers over libraries.
- **DEC-013** — Tier by resource profile; never co-locate tiers in one process.
- **DEC-014** — CTranslate2 is the single model runtime.

**Evidence:** parameter counts `[verified]` from
`docs/research/summaries/007-translation-model-selection.md`; CTranslate2
converter registry `[verified]` by inspection 2026-08-03; PyPI metadata
`[verified]`.
