# Summary: The Tigrinya MT Baseline Cannot Be Shipped

| Field | Value |
| --- | --- |
| **Summary ID** | `007-translation-model-selection` |
| **Full report** | `docs/research/reports/04_model_strategy/001-translation-model-selection.md` |
| **Date** | 2026-08-03 |
| **Status** | Current |
| **Confidence** | High on licensing and sizes (verified); **no quality measured** |

**One-line answer:** Every NLLB variant — the model behind essentially every
published Tigrinya MT number — is **CC-BY-NC-4.0 and cannot be shipped**.
**MADLAD-400-3B is Apache-2.0, covers Tigrinya, and is the shippable choice**, at
4.8× the parameters.

---

## Key Findings

- **No Tigrinya-specific MT model exists** `[verified]`. A Hub search on
  `language:ti` + `translation` returns nothing; the `fgaim`/GeezLab stack has no
  MT model. Translation must come from a massively multilingual model — a
  different kind of bet from the rest of DEC-003's reuse plan.

- **⛔ Every NLLB variant is non-commercial** `[verified]`:

  | Model | Params | Licence | Downloads |
  | --- | ---: | --- | ---: |
  | `nllb-200-distilled-600M` | 615M | **CC-BY-NC-4.0** | 28.0M |
  | `nllb-200-distilled-1.3B` | 1,370M | **CC-BY-NC-4.0** | 4.4M |
  | `nllb-200-3.3B` | 3,300M | **CC-BY-NC-4.0** | 2.9M |

  NLLB produced the COMET 0.82/0.80 dialect figures underpinning **DEC-004**. It
  has 28M downloads. Under **P-9**/**A-009** we cannot ship it — shipping it
  would pass a restriction to our users that they would inherit unknowingly.

  **The trap is specific:** NLLB is the obvious choice, every tutorial uses it,
  and its licence is a metadata field nobody reads. A project can reach
  production on it and find out only when asked whether the product can be sold.

- **✅ MADLAD-400 is the licensed alternative and covers `ti`** `[verified]` —
  `madlad400-3b-mt` (2,940M), `7b-mt` (8,297M), `10b-mt` (10,713M), all
  **Apache-2.0**, all with published GGUF quantisations. *(The names understate:
  "3b" is 2.94B.)*

- **Licence compliance costs 4.8× the parameters** — 615M → 2,940M — but is
  **still affordable**. MADLAD-3B at Q4 is **1.4 GB** weights, within commodity
  CPU serving, and the quantisations already exist. **A-008 survives**, with less
  headroom than DEC-003 assumed when citing 124M-parameter models.

- **⚠️ Our production model and our comparison baseline must be different
  models.** NLLB is what published scores use (research use is permitted);
  MADLAD is what we can ship. So **"we match published Tigrinya MT quality" is
  unfounded unless both are measured on the same harness.** DEC-009's harness
  must run both.

- **A contribution falls out of this.** MADLAD-400's Tigrinya quality appears
  **unpublished** — the ecosystem cites NLLB. Measuring it on FLORES+ with a
  documented harness would be a real ecosystem result (**G-11**).

- **`fgaim` licence split re-confirmed model by model** `[verified]`:
  `tiroberta-bi-encoder` **Apache-2.0** (124.6M) ✅ · `tiroberta-base` **none**
  ⛔ · `tielectra-small` **none** ⛔. **Embeddings are unblocked today**;
  everything else still waits on **A-01**.

- **Method lesson.** MADLAD never appeared in our ecosystem scan because that
  scan searched for *Tigrinya* resources. **A search shaped by the language finds
  language-specific work and misses multilingual work that includes it.**

## Important Decisions

| Decision | ID | Status |
| --- | --- | --- |
| MADLAD-400-3B is the translation baseline; NC-licensed models are research-only and structurally quarantined | DEC-011 | Accepted |

## Rejected Alternatives

| Alternative | Rejected because |
| --- | --- |
| NLLB-200 as the production model | **CC-BY-NC-4.0** — cannot ship; would pass an inherited restriction to users (P-9, A-009) |
| NLLB now, replace it later | The replacement never happens on schedule, and by then the API, evaluations, and docs all assume it |
| MADLAD-400-7B or 10B | 3.9–5.0 GB at Q4 versus 1.4 GB, with no measured quality justification for the cost (A-008) |
| Wait for A-01 before deciding | A-01 concerns `fgaim` models; `fgaim` publishes no MT model. Translation was answerable all along |
| Commercial translation APIs | Already rejected under DEC-003 — fails A-001 and gives no cost control |

## Important Numbers

| Metric | Value | Basis |
| --- | --- | --- |
| Tigrinya-specific MT models on the Hub | **0** | `[verified]` |
| Smallest **shippable** MT model | **2,940M** params | `[verified]` |
| Smallest NLLB (unshippable) | 615M params | `[verified]` |
| **Parameter cost of licence compliance** | **4.8×** | `[verified]` |
| MADLAD-3B weights at Q4 | **1.4 GB** | arithmetic |
| MADLAD-3B weights at fp16 | 5.5 GB | arithmetic |
| `tiroberta-bi-encoder` | 124.6M, Apache-2.0 | `[verified]` |
| NLLB Tigrinya COMET (ET / ER) | 0.82 / 0.80 | `[reported]` — not ours |

## Recommended Next Steps

1. **Build the evaluation harness to run both MADLAD and NLLB** on FLORES+
   Tigrinya (DEC-009, DEC-010). Nothing else can be claimed until this exists.
2. **Measure MADLAD-400-3B on Tigrinya** — likely the first published number.
3. **Measure latency, don't assume it** — memory is arithmetic, speed is an
   experiment, and it has not been run (**A-09**).
4. **Fold the NC-licence question into the legal review** (**A-06**) — the
   interaction between an NC model and a commercial downstream product is a legal
   question, not a technical one.
5. **Benchmark `tiroberta-bi-encoder`** — the one capability unblocked today.

## References

1. Hub metadata for `facebook/nllb-200-*`, `google/madlad400-*`, `fgaim/*`,
   accessed 2026-08-03 `[verified]`
2. `docs/research/summaries/006-metric-validity-and-harness.md` — the harness

---

**Open questions / uncertainty:** How good is MADLAD-400 on Tigrinya — **nobody
appears to have measured it**. Does it handle both varieties (DEC-004)? Is
2.94B at Q4 fast enough on CPU for interactive use? Does an NC model licence
contaminate a commercial downstream product, or only its own redistribution?
