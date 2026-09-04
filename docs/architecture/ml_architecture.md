# ML Architecture

> **Status: the model, runtime and training policy are decided; nothing has been
> served or trained.** DEC-011, DEC-014 and DEC-017 settle what runs and what may
> not be built. **No model has been run through the evaluation harness** — the
> weights are behind an egress policy (**A-09**).
>
> **Evidence:** `../research/summaries/006-model-selection-and-adaptation.md`,
> `../research/summaries/008-architecture-tiers-and-runtime.md`,
> `../research/summaries/010-training-strategy.md`

## Purpose of this document

How models are organised, served, versioned, and updated: the structure of the machine learning layer, from artefact storage through inference serving to quality monitoring.

## Why this document exists

Model choices will change repeatedly as research progresses. The ML architecture determines whether that is a routine update or a rewrite. It also determines whether reproducibility holds across the platform, since reproducibility is a pipeline property rather than a per-model one.

## How to use it

- **Reading:** this is the current design of record for this area. Where it
  conflicts with a decision in
  [`../decisions/DECISIONS.md`](../decisions/DECISIONS.md), the decision wins and
  this document needs updating.
- **Writing:** update it when an Architect-stage decision changes the design. Do
  not use it as a scratchpad for ideas — exploratory thinking belongs in
  `../research/`. This document holds what we have *decided*, not what we are
  *considering*.
- **Every design element here must trace to a decision record.** Design without a
  recorded decision behind it is how projects end up unable to explain
  themselves.

## Relevant principles

**P-1** reuse before building · **P-2** train only for proprietary advantage · **P-4** evaluation before capability · **P-5** reproducibility

## Model inventory

| Capability | Model | Licence | Status |
| --- | --- | --- | --- |
| **Translation** | `google/madlad400-3b-mt` | Apache-2.0 | **Adopted** (DEC-011); never run here (**A-09**) |
| Translation (baseline) | NLLB-200 variants | **CC-BY-NC-4.0** | ⚠️ **Measurable, never deployable** — research comparison only |
| **Embeddings** | `fgaim/tiroberta-bi-encoder` | Apache-2.0 | Cleared; Tier 1, unbuilt |
| Other GeezLab models | `tiroberta-base`, `tielectra-small`, … | **NOT STATED** | ⚠️ **Quarantined** under P-9 until **A-01** resolves |
| **Morphology** | HornMorpho | Unresolved | ⚠️ Blocked on **A-07** |

**The NC distinction is enforced in code, not by memory.** The evaluation
harness marks a system `shippable=False` and prints `COMPARISON ONLY` in its
report, so a licence violation cannot arrive by someone forgetting.

## Model runtime

**CTranslate2 (MIT) is the single runtime** (DEC-014), CPU int8. One runtime,
not one per model — a second runtime is a second set of conversion bugs,
quantisation semantics and failure modes, for capabilities that do not need it.

**No GPU.** DEC-014's path is CPU; DEC-017 puts training behind a ladder that is
blocked on data anyway. **No model registry**: DEC-011 adopts published
checkpoints and DEC-017 means we are not producing our own, so a registry would
version a set of one.

## Training policy — the ladder (DEC-017)

**From-scratch pretraining is foreclosed**, not deferred. The rungs are climbed
in order, and each needs a *measured* trigger rather than an intuition:

| Rung | What it is | Gate |
| --- | --- | --- |
| 0 | Use the published checkpoint | Always first |
| 1 | Prompt / decoding changes | Measured deficit on a real eval set |
| 2 | **LoRA adaptation** | ~23× cheaper than full fine-tuning |
| 3 | Full fine-tune | Only if LoRA is measurably insufficient |
| ✗ | From scratch | **Foreclosed** — A-002's 40M-token ceiling makes it indefensible |

**The ladder is currently blocked at the bottom by data, not compute.** There
are ~~**0 cleanly-licensed parallel sentences**~~ **2,030** (**A-05**) — far too
few to train a rung on, but not zero.

⚠️ **RETRACTED 2026-09-01 — this was false.** [HornMT](https://github.com/asmelashteka/HornMT) is **2,030 human-translated en–ti pairs under CC-BY-4.0**, now committed at `data/anchors/hornmt/`. The zero was measured behind an egress block that made GitHub unreadable; the corpus was public the whole time. The ladder stays blocked; the reason is now *scale*, not *licence*.

## Evaluation gates (P-4, DEC-009, DEC-010)

Promotion from `experiments/` to `services/` requires the harness in
`services/evaluation`, which enforces two rules structurally:

- **BLEU cannot be reported alone** — `score()` returns chrF and BLEU together,
  because DEC-009 forbids BLEU alone and the cheapest enforcement is to make the
  alternative unrepresentable.
- **`aggregate()` raises.** A single "Tigrinya score" across varieties would
  describe a language nobody speaks (DEC-010).

**chrF is primary** because it degrades more gracefully than BLEU exactly where
low-resource MT lives: its advantage over BLEU widens as quality falls
(retention 1.18× → 1.46× → 1.80× at 10/20/30% corruption). **BLEU is ~1.08×
harsher on Tigrinya than English** at an identical error rate — real, and about
half the size the standard warning implies.

**Tier 0 has no gold standard and does not need one to be gated.** Intrinsic
properties — idempotence, determinism, reversibility, coverage, alignment
integrity — are checked over real text by `tigrinya_eval.primitives` (DEC-023a).
⚠️ **They catch *broken*, not *wrong*:** a transliterator returning
deterministically incorrect phonemes passes every one.

## Quality monitoring, rollback, fallback

- **Regression detection today is the experiment suite.** Five experiments
  reproduce byte-identically, which is the only thing that would catch `epitran`,
  `tokenizers` or `sacrebleu` changing behaviour under DEC-007's amended numbers.
  ⚠️ It runs in CI that is **not yet installed** (**A-15**).
- **Rollback is `pip install` of a pinned version.** Dependencies are pinned, not
  floated, precisely so a rollback is a version change rather than an
  investigation.
- **Fallback is explicit unavailability.** `morphology.is_available()` returns
  `False` rather than degrading silently — a caller that cannot tell the
  difference between "unavailable" and "analysed as empty" will ship the second
  as if it were data.

## What is deliberately not built

Recorded so it is not built by default: **no GPU tier**, **no model registry**,
**no feature store**, **no vector database** (retrieval is not in DEC-006's
minimum platform), **no training pipeline** until the ladder's triggers fire and
**A-05** supplies data.

## Open questions

- **Is MADLAD-400-3B any good at Tigrinya?** Entirely unmeasured (**A-09**). The
  whole translation tier rests on an assumption.
- What is Tier 2's cold start? **A-14** — it decides the deployment mode, and
  Tier 0's 3.03 s says nothing about a 3B model.
- How do you evaluate a **monolingual** embedding model with no Tigrinya
  similarity benchmark? `tiroberta-bi-encoder` is monolingual, so FLORES+ bitext
  retrieval does not directly apply.
- Are the transliterator's phonemes actually *right*? Needs a native speaker; no
  intrinsic check can answer it.

## Decision log for this area

| Decision | ID | Date | Summary |
| --- | --- | --- | --- |
| Translation baseline | **DEC-011** | 2026-08-10 | MADLAD-400-3B adopted; NC-licensed models are research-only and marked unshippable in code |
| Single model runtime | **DEC-014** | 2026-08-10 | CTranslate2 (MIT), CPU int8 — one runtime, not one per model |
| Adaptation ladder | **DEC-017** | 2026-08-17 | Training gated behind measured triggers; **from-scratch foreclosed** |
| Adopt the existing model layer | **DEC-003** | 2026-07-29 | Build primitives, evaluation and integration — not models |
| chrF primary | **DEC-009** | 2026-08-03 | BLEU for comparability only, never alone |
| Variety-scoped results | **DEC-010** | 2026-08-03 | No cross-variety aggregate; `aggregate()` raises |
| Tier by resource profile | **DEC-013** | 2026-08-10 | Translation is Tier 2 and lazily loaded |
| Decomposition substrate | **DEC-007** | 2026-07-29 | ⚠️ **Amended twice** — tokenization runs on raw Ge'ez; the token-efficiency rationale was refuted |

## What future contributors should add

The actual design, once research supports it. Diagrams where they clarify.
Rationale linked to decision records. Keep it current — an architecture document
that has drifted from reality is worse than none, because people trust it.
