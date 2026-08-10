# Model Strategy: the Tigrinya MT Baseline Cannot Be Shipped

| Field | Value |
| --- | --- |
| **Report ID** | `001-translation-model-selection` |
| **Domain** | `04_model_strategy` |
| **Stage** | Scout → Analyst → Architect |
| **Date** | 2026-08-03 |
| **Status** | Accepted |
| **Summary** | `docs/research/summaries/007-translation-model-selection.md` |
| **Related decisions** | **DEC-011**; extends DEC-008; engages DEC-003, DEC-009, A-008, A-009 |

---

## Objective

Choose the model that serves our **first buildable capability**. Translation is
first because **P-4** gates capabilities on evaluation, and `08_evaluation`
delivered a validated metric for translation (DEC-009) and nothing else yet.

**Why this domain looked blocked and was not.** `04_model_strategy` was deferred
pending **A-01** (the unlicensed `fgaim` models). That block is real for
embeddings, POS, and NER — but **irrelevant to translation**, because `fgaim`
publishes no MT model. The translation question was answerable all along.

---

## Finding 1 — No Tigrinya-specific translation model exists

`[verified]` — a Hub search filtered to `language:ti` + `translation` returns
**nothing**. The `fgaim`/GeezLab stack, which covers language modelling,
embeddings, POS, NER, QA and OCR, contains **no MT model**.

Translation must therefore come from a **massively multilingual** model that
happens to include Tigrinya. That is a materially different decision from the
rest of DEC-003's reuse plan: we are not adopting a Tigrinya model, we are
adopting a 200-language model and hoping its Tigrinya slice is adequate.

## Finding 2 — ⛔ Every NLLB variant is non-commercial. The field's baseline is unshippable.

**This is the finding that changes the plan.**

`[verified]` from Hub metadata:

| Model | Params | Licence | Downloads | Shippable |
| --- | ---: | --- | ---: | --- |
| `facebook/nllb-200-distilled-600M` | 615M | **CC-BY-NC-4.0** | 28.0M | ⛔ **No** |
| `facebook/nllb-200-distilled-1.3B` | 1,370M | **CC-BY-NC-4.0** | 4.4M | ⛔ **No** |
| `facebook/nllb-200-3.3B` | 3,300M | **CC-BY-NC-4.0** | 2.9M | ⛔ **No** |

**NLLB is the model behind essentially every published Tigrinya MT number**,
including the COMET 0.82 / 0.80 dialect figures underpinning **DEC-004**. It has
28 million downloads. And its licence forbids commercial use.

Under **P-9** and **A-009** this is disqualifying for anything we ship. We are
building infrastructure others build on; shipping an NC-licensed model would
pass on a restriction our users would inherit without knowing it — the same
failure mode as unlicensed data, in a different layer.

**The trap this creates is specific and worth naming.** NLLB is the obvious
choice, it is what every tutorial uses, and its licence is a metadata field
nobody reads. A project could get to production on it and discover the problem
only when someone asks whether the product can be sold.

## Finding 3 — MADLAD-400 is the licensed alternative, and it covers Tigrinya

`[verified]`:

| Model | Params | Licence | `ti` support | GGUF |
| --- | ---: | --- | --- | --- |
| `google/madlad400-3b-mt` | **2,940M** | **Apache-2.0** | ✅ | ✅ |
| `google/madlad400-7b-mt` | 8,297M | **Apache-2.0** | ✅ | ✅ |
| `google/madlad400-10b-mt` | 10,713M | **Apache-2.0** | ✅ | ✅ |

Apache-2.0 is clean for our purposes, and `ti` appears in the language list of
all three. **Note the naming understates size** — "3b" is 2.94B, "7b" is 8.3B,
"10b" is 10.7B.

**MADLAD did not appear in our earlier ecosystem scan.** That scan searched for
*Tigrinya* resources; MADLAD is a general multilingual model that happens to
include Tigrinya. A search shaped by the language finds the language-specific
work and misses the multilingual work — recorded as a method lesson.

## Finding 4 — Licence compliance costs 4.8× the parameters

Weights-only footprint. **Deterministic arithmetic** (params × bytes/weight),
excluding KV cache, activations, and runtime overhead.

| Model | fp16 | int8 | Q4 | Shippable |
| --- | ---: | ---: | ---: | --- |
| NLLB-600M | 1.1 GB | 0.6 GB | 0.3 GB | ⛔ |
| **MADLAD-3B** | 5.5 GB | 2.7 GB | **1.4 GB** | ✅ |
| MADLAD-7B | 15.5 GB | 7.7 GB | 3.9 GB | ✅ |
| `tiroberta-bi-encoder` | 0.2 GB | 0.1 GB | 0.1 GB | ✅ |

**The smallest shippable translation model is 4.8× the parameters of the
smallest NLLB.** That is the price of the licence, stated plainly.

**It is affordable anyway.** MADLAD-3B at Q4 is **1.4 GB** — within reach of
commodity CPU serving, and GGUF quantisations are already published, so we do not
have to produce them. **A-008 survives**, but with less headroom than DEC-003
assumed when it cited 124M-parameter models.

**What I am not claiming:** latency or throughput. Model downloads are
egress-blocked, so I could not run either model. Memory is arithmetic; speed is
an experiment, and it has not been done. Anyone who needs a latency number must
measure it (**A-09**).

## Finding 5 — The `fgaim` licence split, confirmed model by model

`[verified]` — re-checked directly rather than trusted from the earlier scan:

| Model | Params | Licence |
| --- | ---: | --- |
| `fgaim/tiroberta-bi-encoder` | 124.6M | ✅ **Apache-2.0** |
| `fgaim/tiroberta-base` | 124.7M | ⛔ **none stated** |
| `fgaim/tielectra-small` | — | ⛔ **none stated** |

The embeddings capability is **unblocked today**. The foundation model is not.
**A-01 remains blocking for everything except embeddings and translation.**

## Finding 6 — Our production model and our comparison baseline must differ

This follows from Findings 2 and 3 and is the awkward part.

- **NLLB** is what published Tigrinya scores use → needed for **comparability**.
- **MADLAD** is what we can ship → needed for **production**.

NLLB's NC licence permits research use, so evaluating it for comparison is
legitimate. But it means **our headline number and the field's headline number
come from different models**, and any claim like "we match published Tigrinya
MT quality" is unfounded unless both are measured on the same harness.

DEC-009's harness already reports chrF and BLEU together and pins
implementations; extending it to run **both models** is a small addition that
prevents a large error.

**And a genuine contribution falls out of it.** MADLAD-400's Tigrinya quality
appears to be **unpublished** — the ecosystem cites NLLB. Measuring MADLAD on
FLORES+ Tigrinya with a documented harness would be a real result for the
ecosystem (**G-11**), not just an internal number.

---

## Decision arising

**DEC-011** — MADLAD-400-3B is the translation baseline. **NC-licensed models are
research-only and structurally quarantined**, extending DEC-008's data rule to
models.

## Limits of this report

- **No quality measurement.** Neither model was run; Tigrinya MT quality for
  MADLAD is unknown and NLLB's is `[reported]`, not verified by us.
- **No latency measurement.** See Finding 4.
- **Licence read from Hub metadata**, not from legal review. `cc-by-nc-4.0` is
  unambiguous on its face, but the interaction between an NC model licence and a
  commercially-licensed downstream product is a legal question, not a technical
  one — folded into **A-06**.
- **Only translation is decided.** Embeddings are unblocked but unevaluated;
  every other capability remains blocked on A-01, on evaluation, or on both.

**Evidence:** Hub metadata `[verified]` 2026-08-03;
`docs/research/summaries/006-metric-validity-and-harness.md`
