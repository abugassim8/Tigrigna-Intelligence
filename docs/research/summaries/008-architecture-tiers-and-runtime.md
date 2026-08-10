# Summary: Architecture — Tier by Resource Profile, Not by Domain

| Field | Value |
| --- | --- |
| **Summary ID** | `008-architecture-tiers-and-runtime` |
| **Full report** | `docs/research/reports/05_architecture/001-service-decomposition-and-runtime.md` |
| **Date** | 2026-08-03 |
| **Status** | Current |
| **Confidence** | High on footprints and runtime support (verified); **no latency measured** |

**One-line answer:** Our capabilities differ by **~150× in memory**, so the
system decomposes **by resource profile, not by domain** — and one MIT runtime
(CTranslate2) serves every model we have.

---

## Key Findings

- **⭐ The memory spread *is* the architecture.**

  | Capability | Footprint | Tier |
  | --- | ---: | --- |
  | normalisation / tokenization / transliteration / morphology | 0–48 MB | **0** |
  | embeddings (`tiroberta-bi-encoder` int8) | 119 MB | **1** |
  | **translation (MADLAD-400-3B Q4)** | **1,402 MB** | **2** |

  A translation request needs ~150× the memory of a tokenization request, and
  cold start differs by a similar factor. **Co-locating them would mean a 1.6 GB
  resident footprint to normalise a string** — and, under the scale-to-zero that
  A-008 pushes toward, a multi-second cold start on a microsecond operation.
  → **DEC-013**

  | Tier | Cumulative | Behaviour |
  | --- | ---: | --- |
  | 0 — primitives | **72 MB** | always warm |
  | 1 — + embeddings | **191 MB** | warm |
  | 2 — + translation | **1,593 MB** | lazily loaded; may scale to zero |

- **DEC-006's MVP fits in 191 MB, and adding translation is an 8.3× jump.**
  DEC-006 excluded translation from the minimum platform on *gap-filling*
  grounds. The cost arithmetic independently agrees — **a decision gets support
  from evidence it was not built on.** It also sharpens the boundary: translation
  is not merely "later," it is where the cost profile changes by an order of
  magnitude.

- **✅ One MIT runtime covers every model we have** `[verified]` by installing
  **CTranslate2 4.8.1** and inspecting its converter registry (42 HF
  architectures):

  | Config | Our model | Capability |
  | --- | --- | --- |
  | `T5Config` | `madlad400-3b-mt` | translation (DEC-011) |
  | `M2M100Config` | `nllb-200-*` | comparison baseline (DEC-011) |
  | `RobertaConfig` | `tiroberta-bi-encoder` | embeddings (DEC-003) |

  One dependency, one quantisation story, one operational surface, MIT
  throughout. `llama-cpp-python` (MIT) would serve the published MADLAD GGUFs but
  **not** the Roberta encoder — two runtimes instead of one, so **P-7** favours
  CTranslate2. → **DEC-014**

- **Library-first, because of who our users are and how little volume we have.**
  **DEC-002** makes application developers primary — they want `pip install`, not
  a service to operate. **P-6/A-008** want low-volume economy, and **a library
  has zero serving cost at zero volume**, which no service topology matches.
  Requiring a running service for microsecond operations would impose
  infrastructure on exactly the users who least want it. → **DEC-012**

- **Tiering dissolves the low-volume cold-start bind.** A 1.4 GB model kept warm
  costs idle memory; scaled to zero it costs a multi-second cold start. Neither
  is acceptable platform-wide; both are fine **per tier** — Tier 0 is cheap
  enough to stay warm, and translation users already expect to wait seconds.
  **The tension is only unresolvable if the tiers are merged.**

- **What this forecloses:** no shared mutable state; no cross-service imports
  (shared logic goes in a library, not another service); **no single
  "do-everything" container** — the 150× spread is the standing counter-argument.

## Important Decisions

| Decision | ID | Status |
| --- | --- | --- |
| Library-first; services are thin wrappers over libraries | DEC-012 | Accepted |
| Tier by resource profile; never co-locate tiers in one process | DEC-013 | Accepted |
| CTranslate2 is the single model runtime | DEC-014 | Accepted |

## Rejected Alternatives

| Alternative | Rejected because |
| --- | --- |
| Decompose by domain (translation service, morphology service, …) | Ignores the 150× resource spread — the thing that actually determines deployment and cost |
| One container serving everything | 1.6 GB resident to normalise a string; multi-second cold start on microsecond operations |
| Service-first, libraries extracted later | Imposes infrastructure on developer users (DEC-002) and adds network latency to microsecond operations; extraction never happens once services exist |
| `llama-cpp-python` as runtime | Serves MADLAD GGUF but not the Roberta encoder — two runtimes where one suffices (P-7) |
| Keep all tiers warm | Pays idle cost for 1.4 GB continuously at low volume (A-008) |
| Scale everything to zero | Multi-second cold start on tokenization, which should take microseconds |

## Important Numbers

| Metric | Value | Basis |
| --- | --- | --- |
| **Memory spread, tokenize → translate** | **~150×** | arithmetic |
| Tier 0 (primitives) | **72 MB** | arithmetic |
| **Tier 0+1 = DEC-006 minimum viable platform** | **191 MB** | arithmetic |
| Tier 0+1+2 (with translation) | 1,593 MB | arithmetic |
| **Cost of adding translation** | **8.3×** | arithmetic |
| CTranslate2 | 4.8.1, **MIT**, 42 HF architectures | `[verified]` |

## Recommended Next Steps

1. **Write `system_overview.md` from DEC-012/013/014** — it is no longer gated.
2. **Measure, don't assume, latency and cold start** — this report contains no
   speed figures on purpose (**A-09**).
3. **Verify CTranslate2 conversion actually works** on MADLAD-3B and
   `tiroberta-bi-encoder`. Support is verified; conversion is an experiment
   needing the weights.
4. **Build Tier 0 first** — it is 72 MB, unblocked, and everything above depends
   on it.
5. **Resolve HornMorpho (A-07)** — its ~48 MB is an estimate, and if it is
   unusable Tier 0 loses morphology.

## References

1. CTranslate2 4.8.1 converter registry — inspected 2026-08-03 `[verified]`
2. `docs/research/summaries/007-translation-model-selection.md` — parameter counts
3. PyPI metadata for runtime candidates `[verified]`

---

**Open questions / uncertainty:** Does CTranslate2 conversion succeed on these
specific checkpoints? What is the real cold-start cost for Tier 2? Is HornMorpho
usable at all (**A-07**)? Does the API surface change any of this — gated on
**A-02**.
