# Master Blueprint: State of Play, the Central Tension, and the Critical Path

| Field | Value |
| --- | --- |
| **Report ID** | `001-state-of-play-and-critical-path` |
| **Domain** | `12_master_blueprint` |
| **Stage** | Architect |
| **Date** | 2026-08-17 |
| **Status** | Accepted |
| **Summary** | `docs/research/summaries/013-state-of-play.md` |
| **Related decisions** | **DEC-021**; synthesises DEC-001…DEC-020 |

---

## Objective

Synthesise eleven research domains into one picture: what is decided, what is
verified, what is blocked, and what must happen next.

**This report does not restate the summaries.** It reports what is only visible
when they are read together — and the most important thing it found is a
**misalignment between what we are cleared to build and what we decided to
build.**

---

## Finding 1 — ⚠️ We are cleared to build exactly one capability, and it is the one the MVP excludes

**This is the central finding, and it is invisible from inside any single
domain.**

**P-4** gates capability work on evaluation existing. Auditing
`docs/benchmarks/metrics.md` against **DEC-006**'s minimum viable platform:

| Capability | Metric validated? | In DEC-006's MVP? |
| --- | --- | --- |
| **Translation** | ✅ **Yes — measured** (DEC-009) | ❌ **explicitly excluded** |
| Embeddings / similarity | ❌ TBD | ✅ yes |
| Tokenization | ❌ TBD | ✅ yes |
| Morphological analysis | ❌ TBD | ✅ yes |
| Transliteration | ❌ TBD | ✅ yes |
| *(9 others)* | ❌ TBD | no |

**Capabilities with a validated metric: 1. Inside the MVP: 0.**

So the state is: translation has a validated metric (DEC-009), a variety-scoped
reporting rule (DEC-010), a licensed model (DEC-011), a runtime (DEC-014), and a
deployment tier (DEC-013) — while **every capability DEC-006 actually named has
no way to tell whether it works.**

### The root cause is DEC-005, not bad sequencing

**DEC-005 named FLORES-200 and TiQuAD as the evaluation anchors.** FLORES+ is a
translation benchmark; TiQuAD is question-answering. **Neither evaluates
tokenization, morphology, transliteration, or embeddings** — the four things
DEC-006 calls the minimum viable platform.

DEC-005 and DEC-006 were both taken on the same day, and **nobody noticed that
the anchors did not cover the platform.** Each was individually sound; together
they left the MVP unmeasurable.

**This is exactly the failure mode `DECISIONS.md` warns about in its own
preamble** — not contradiction, but two locally sensible decisions that do not
compose.

→ **DEC-021.**

## Finding 2 — What is actually true, versus designed, versus assumed

| Layer | State |
| --- | --- |
| **Measured** | Ge'ez expansion 1.957× · BLEU 1.08× harsher on ti · chrF retains 1.80× at 30% corruption · tokenizer fertility (raw Ge'ez wins 10/10) · corpus 67,153 rows · TiQuAD contamination **confirmed** · 3 experiments reproduce byte-identically |
| **Verified fact** | Every licence in the stack · MADLAD/NLLB parameter counts · CTranslate2 architecture support · 15,053 cleanly-licensed documents · **0** cleanly-licensed parallel sentences |
| **Arithmetic** | Tier footprints (191/1,593 MB; Tier 0 measured 113.4 MB) · ~14× standing-cost saving · LoRA 23× cheaper · break-even curves |
| **Designed, unbuilt** | Evaluation harness · service tiers · screening in CI · every service |
| **Assumed, untested** | MADLAD's Tigrinya quality · Tier 2 cold start · 2 s service time · COMET's validity · that DEC-002's user model is right |

**80% of claims across the twelve summaries carry `[verified]`; 20% are
`[reported]`** — the latter almost entirely paper-derived figures behind the
egress block.

**Nothing has been built.** Three experiments, one screening tool, one CI
workflow (uninstalled). That is appropriate for eleven domains of research and
worth stating plainly rather than letting document count imply otherwise.

## Finding 3 — The critical path, and it does not start where you would guess

Ordered by what unblocks what:

| # | Step | Blocked by | Unblocks |
| --- | --- | --- | --- |
| **1** | **Evaluation for the MVP primitives** | *nothing* | The entire MVP under P-4 |
| **2** | Confirm DEC-002 (**A-02**) | a human | `07_api_mcp`, the last unresearched domain |
| **3** | `fgaim` licences (**A-01**) | a human | Embeddings — the only Tier 1 capability |
| **4** | HornMorpho resolution (**A-07**) | a human | Morphology, a Tier 0 primitive |
| **5** | Build Tier 0 | steps 1, 4 | Everything above it |
| **6** | Parallel-data licence (**A-05**) | a human | DEC-011's only fallback |
| **7** | Measure MADLAD | egress (**A-09**) | Whether step 6 is urgent or merely useful |

**Step 1 is blocked by nothing and gates everything.** It is the only item on
this list that needs no permission, no licence, no egress, and no human decision
— and it is the reason DEC-021 exists.

## Finding 4 — The blockers are not technical

Fifteen action items; **three blocking**, all requiring a person:

| Blocker | Blocks | Resolvable by research? |
| --- | --- | --- |
| **A-01** `fgaim` licences | DEC-003's reuse plan, embeddings | **No** |
| **A-02** confirm DEC-002 | `07_api_mcp`, API surface | **No** |
| **A-05** parallel-data licence | DEC-011's fallback (DEC-017) | **No** |

Plus **A-15**, a one-command CI install that leaves six rules unenforced until
done.

**`11_business` established that money is not the binding constraint** — 52.6
GB-h/month for the always-warm tier. **This is the constraint.** The action
register is the risk register, and no amount of further research moves any of it.

## Finding 5 — What the method itself produced

Recorded because it transfers to other low-resource work, and because it was not
the plan:

1. **Measurement beat citation, repeatedly.** Egress blocked the literature, so
   claims got measured instead — and the measurements were *sharper* than the
   citations would have been. "BLEU is unsuitable for morphologically rich
   languages" became "**BLEU is 1.08× harsher**," which is both true and usable.

2. **Pre-committed thresholds caught overclaiming twice.** Experiment 002 refuted
   DEC-007's central rationale; Experiment 003 refuted all four hypotheses while
   every direction was correct. **Without thresholds written first, both would
   have been written up as successes.**

3. **Policy without mechanism fails silently.** DEC-008 was ignored for three
   months and found only by measurement — which produced DEC-015 (executable
   screening) and DEC-018 (CI). **The failure was structural, not careless.**

4. **Metadata is evidence, not truth.** HF `size_categories` was wrong on 2 of 4
   datasets; PyPI's legacy `license` field reads "NOT STATED" for five correctly
   licensed packages. **A single field is not a check** — and that near-miss would
   have disqualified the metric implementation DEC-009 depends on.

5. **Corrections improved the evidence rather than weakening conclusions.** The
   orthographic-mixing correction gave DEC-010 a baseline it never had; the
   break-even correction turned a wrong claim into a decision rule (DEC-019).

## Limits of this report

- **A synthesis inherits every underlying limit.** Nothing here is more certain
  than the domain it came from.
- **The readiness audit reads `metrics.md`**, which is a document, not the world.
  It is accurate about what we have decided, not about what would actually work.
- **"Nothing has been built" is a statement about scope, not a complaint.**
  Eleven domains of research before code was the deliberate choice in DEC-001.
- **`07_api_mcp` is unresearched** and stays that way until **A-02**.

---

## Decision arising

**DEC-021** — Extend the evaluation anchors to cover the MVP primitives; the next
research is evaluation for Tier 0, not another capability.

**Evidence:** audit of `docs/benchmarks/metrics.md` against DEC-006
`[verified]` 2026-08-17; evidence-marker counts across twelve summaries
`[verified]`.
