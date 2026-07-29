# Scope, Users, and Dialect Definition

| Field | Value |
| --- | --- |
| **Report ID** | `001-scope-users-and-dialect` |
| **Domain** | `00_project_definition` |
| **Stage** | Scout → Analyst |
| **Date** | 2026-07-29 |
| **Status** | Accepted — one recommendation requires owner confirmation |
| **Summary** | `docs/research/summaries/002-scope-users-and-dialect.md` |
| **Related decisions** | DEC-002 (proposed), DEC-004, DEC-006 |

---

## Evidence note

Same egress limitation as `01_ecosystem/001`: primary academic sources and
Wikipedia/Ethnologue were blocked at the proxy. Demographic figures below are
`[reported]` from search-engine summaries of secondary sources and **disagree
with each other** — that disagreement is itself reported rather than smoothed
over. Hugging Face data is `[verified]`.

---

## Objective

Close the scope questions that are currently blocking other work: **who the
users are**, **which dialects and registers are in scope**, and **what the
minimum useful platform is**. Three of these sit open in `assumptions.md` and
gate API design, data collection, and sequencing.

## Research Questions

1. How many Tigrinya speakers are there, and where?
2. Who are the plausible users of language *infrastructure* for Tigrinya?
3. Which dialects and registers must be in scope?
4. What is the minimum useful platform?
5. Which capabilities are foundational versus downstream?

---

## Finding 1 — Speaker population

`[reported]`, and **sources conflict**:

| Source type | Estimate |
| --- | --- |
| Recent aggregate (2022–2023) | ~9.9M native speakers |
| Range across sources | 5M – 9.9M |
| Ethiopia (Tigray region) | ~4.32M |
| Eritrea | ~2.54M |

The regional figures (~6.9M combined) do not reconcile with the ~9.9M headline,
which suggests different base years, differing treatment of the diaspora, or
differing native/total-speaker definitions. **We do not resolve this here.**

**What matters for us is not the precise figure but its order of magnitude and
its distribution**, and both are clear enough to plan against:

- Speakers number in the **millions**, not the tens of thousands. This is not a
  micro-language; a platform has a real potential user base.
- Speakers are **split across two countries** with roughly a 60/40 Ethiopia/
  Eritrea balance, plus a substantial diaspora.

That split is the consequential fact, and it drives Finding 3.

## Finding 2 — Who the users are

No direct user research was possible this session (no survey data, and community
forums were not reachable). This finding is therefore **inferential**, drawn
from what the ecosystem scan showed about who is active and what is missing.

Three candidate user groups:

| Group | Evidence they exist | What they need from us |
| --- | --- | --- |
| **Application developers** | Mature consumer keyboards (GeezIME, GeezKTB, Mesmer) exist and ship features — GeezKTB advertises dictionary, translation, and grammar check. These teams are building language features **today**, without an infrastructure layer. | Clean APIs, SDKs, spell/grammar/morphology endpoints |
| **Researchers** | Active and productive: GeezLab, L3S Hannover, HLTDI, plus many independent HF contributors | Datasets, evaluation harnesses, reproducible baselines |
| **Institutions** (media, government, education, NGOs) | Newspaper corpora exist (*Haddas Ertra*); asylum-summarisation model found on HF, implying humanitarian demand | Translation, search, summarization — mostly via applications, not directly |

**The strongest evidence points to application developers.** The existence of
several independently-built Ge'ez keyboard products, each re-solving word
suggestion and dictionary lookup separately, is direct evidence of demand for a
shared layer underneath them. That is exactly the shape of the gap this project
proposes to fill.

Researchers are a close second and are cheap to serve simultaneously — the
evaluation harness and datasets they need are things we must build anyway
(**G-2**, **G-8**).

**Recommendation:** primary users are **application developers**; secondary are
**researchers**. Institutions are served indirectly, through the applications
developers build.

> ⚠️ **This is a product-owner decision, not a research finding.** The evidence
> supports it but does not compel it. Recorded as **DEC-002, status Proposed**,
> pending the owner's confirmation. Everything else in this report holds
> regardless of how it is resolved.

## Finding 3 — Dialect scope

**This question is settled by evidence, and the answer is: both varieties, with
separate evaluation.**

`[reported]` from CoDET (arXiv 2305.17267): NLLB-3.3B scores **COMET 0.82 on the
Ethiopian variety versus 0.80 on the Eritrean variety.**

Two things follow:

1. **The gap is real but modest.** These are not different languages requiring
   separate models. A single model can plausibly serve both.
2. **The gap is measurable, and it is asymmetric.** An aggregate score hides it.
   Reporting one number for "Tigrinya" would systematically under-serve Eritrean
   users while appearing fine on the dashboard — precisely the failure mode
   `docs/benchmarks/metrics.md` warns about when it requires subset reporting.

Corroborating signal: the corpora found are split by origin — `haddas-tigrinya-corpus`
is explicitly Eritrean (*Haddas Ertra* newspaper), while much other work is
Ethiopian-sourced. Training-data provenance will skew variety coverage whether
or not we attend to it.

**Recommendation:** support both varieties; **evaluate them separately and
report both scores, always.** Do not aggregate into a single "Tigrinya" number.
Recorded as **DEC-004**.

**Registers** remain open. TiALD is YouTube comments (informal); TiQuAD is news
(formal). Both extremes have data, which is fortunate, but nothing was found
characterising the distance between them for Tigrinya. → `02_linguistics`.

## Finding 4 — Capability dependency structure

The ecosystem scan resolves which capabilities are foundational, because it
shows which layer is *missing* rather than merely which is logically prior.

```
        ┌─ Ge'ez normalisation ─┐          NOBODY HAS BUILT THIS
Layer 0 │      Tokenization     │  ◄────── as production infrastructure.
        └─   Morphology  ───────┘          This is our critical path.
                    │
Layer 1     Embeddings · POS · NER    ◄──── EXISTS and is reusable
                    │                        (fgaim stack)
Layer 2   Search · Retrieval · Translation ◄─ partially exists
                    │
Layer 3   Spell · Grammar · Summarization · QA
                    │
Layer 4   Knowledge graph · Entity linking · RAG
                    │
Layer 5        API · MCP · SDKs        ◄──── NOBODY HAS BUILT THIS
```

Layers 0 and 5 are the gaps. Layers 1–2 largely exist. **This inverts the naive
plan**: the valuable work is at the very bottom and the very top, not in the
middle where the models are.

## Finding 5 — Minimum useful platform

Given the above, the smallest thing genuinely valuable to someone:

**A Tigrinya text-processing API providing normalisation, tokenization,
morphological analysis, and embeddings — with a documented evaluation harness
proving it works.**

Rationale:
- It fills the actual gap (Layer 0) rather than duplicating Layer 1.
- Every listed keyboard product could use it immediately.
- Every researcher could use the evaluation harness immediately.
- It is achievable by adopting existing models plus focused primitives work.
- It does not require training anything (**P-2**, **A-004**).

Translation is deliberately **excluded** from the minimum platform: Google
Translate already serves it, reportedly better than the open alternatives. We
should measure against it before deciding we can improve on it.

---

## Alternatives Considered

**A — Lead with translation.** Highest visible demand. Rejected as the *starting*
point: strong incumbents, no clear advantage available to us, and it does
nothing for the primitives gap that everything else depends on.

**B — Lead with the primitives + evaluation layer.** **Recommended.** Fills the
real gap; unblocks everything; no training required.

**C — Lead with an end-user product.** Rejected — violates **N-1**, **N-2**.

**D — Lead with the knowledge graph / RAG.** Rejected for now: most
dependency-heavy layer, no Tigrinya groundwork found.

---

## Cost Analysis

| Item | Effort | Basis |
| --- | --- | --- |
| Adopt + evaluate existing models | 1–2 weeks | No training; small models |
| Tokenizer + normalisation work | Weeks | Informed by MoVoC |
| Morphology (adopt HornMorpho) | Days–weeks | If maintained |
| Morphology (build) | Months | Fallback if not |
| Evaluation harness | 2–4 weeks | FLORES-200 + TiQuAD exist |
| API + SDK layer | Weeks | Standard engineering |

Operating cost is expected to be low: the candidate models are ~124M parameters
and CPU-servable (**P-6**, **A-008**). **Not yet measured** — see
`10_infrastructure`.

---

## Build vs Buy Decision

Buy/reuse the model layer. Build the primitives, the evaluation harness, and the
integration surface. Detail in `01_ecosystem/001`.

---

## Recommended Approach

1. Primary users: **application developers**; secondary: **researchers**.
   *(DEC-002, Proposed — owner confirmation needed.)*
2. Dialect scope: **both varieties, evaluated separately, always reported
   separately.** *(DEC-004, Accepted — evidence-backed.)*
3. Minimum useful platform: **normalisation + tokenization + morphology +
   embeddings + evaluation harness, behind an API.** *(DEC-006, Accepted.)*
4. Translation is **not** in the minimum platform; benchmark against Google
   Translate first.

Confidence: **medium-high** on 2–4; **medium** on 1, which is a judgement call
on thin direct evidence.

---

## Implementation Plan

1. Confirm DEC-002 with the project owner. *(Only blocking item.)*
2. Proceed to `02_linguistics` — Ge'ez normalisation and morphology are the
   critical path.
3. Run `03_data_strategy` on the located corpora, licence-checking as you go.
4. Stand up the evaluation harness (`08_evaluation`) on FLORES-200 + TiQuAD.

---

## Risks

| Risk | Likelihood | Impact | Mitigation |
| --- | --- | --- | --- |
| User assumption wrong | Medium | High — reshapes API and SDK priorities | Marked Proposed; cheap to revisit before API design |
| Dialect handling under-serves Eritrean users | Medium | **High — equity issue, not just quality** | DEC-004 mandates separate reporting |
| Register mismatch (news-trained, informal use) | Medium | Medium | `02_linguistics`; evaluate out-of-domain |
| Demographic figures wrong | High | Low | Only order of magnitude is load-bearing |
| Primitives harder than expected | Medium | High | It is the critical path — sequence it first, fail early |

---

## Open Questions

- **Which language pairs matter most for translation?** Still open. En↔Ti is
  best resourced; Am↔Ti has data and cultural proximity.
- **Register distance** between formal and informal Tigrinya — unknown.
- **Do the diaspora's needs differ** from in-country users' needs? Unknown, and
  plausibly relevant to transliteration priority.
- **Deployment model** (self-hosted vs managed) — still open.

---

## References

1. Speaker demographics — worlddata.info, worldmapper.org, and aggregate summaries (conflicting; all `[reported]`)
2. CoDET: Contrastive Dialectal Evaluation of MT — arXiv 2305.17267
3. TiQuAD — https://hf.co/datasets/fgaim/tiquad
4. TiALD — https://hf.co/datasets/fgaim/tigrinya-abusive-language-detection
5. `haddas-tigrinya-corpus` — https://hf.co/datasets/SIMBA9657/haddas-tigrinya-corpus
6. GeezIME, GeezKTB, Mesmer Tigrinya — consumer Ge'ez keyboards
7. `docs/research/reports/01_ecosystem/001-tigrinya-nlp-ecosystem-scan.md`

---

## Checklist

- [x] **What exists?** Millions of speakers across two countries; active researchers; mature consumer keyboards; no infrastructure layer.
- [x] **What can be reused?** Layer 1 models and existing evaluation benchmarks — see `01_ecosystem/001`.
- [x] **What should be built?** Layer 0 primitives, the evaluation harness, and the Layer 5 integration surface.
- [x] **What should not be built?** Consumer keyboards or input tools; translation as the opening move; knowledge graph now.
- [x] **Cost estimate?** Reuse path is weeks not months; no training required. Absolute operating cost unmeasured.
- [x] **Maintenance burden?** Low — adopting small models; our own build surface is deliberately narrow.
- [x] **Licensing?** Covered in `01_ecosystem/001`. Several key models lack stated licences — blocking.
- [x] **Technical risks?** Primitives difficulty; dialect equity; register mismatch; user assumption.
- [x] **Final recommendation?** Developers first; both dialects evaluated separately; primitives + evaluation as the minimum platform.

## Completion

- [x] Summary written to `docs/research/summaries/002-scope-users-and-dialect.md`
- [x] References added
- [x] Decisions recorded: DEC-002 (proposed), DEC-004, DEC-006
- [x] Assumptions updated: A-002, A-006, A-007; open scope items closed or narrowed
