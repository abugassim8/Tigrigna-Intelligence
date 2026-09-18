# Summary: Tigrinya Corpus Inventory and Confirmed Evaluation Contamination

| Field | Value |
| --- | --- |
| **Summary ID** | `005-corpus-inventory-and-contamination` |
| **Full report** | `docs/research/reports/03_data_strategy/001-corpus-inventory-and-contamination.md` |
| **Date** | 2026-07-29 |
| **Status** | Current |
| **Confidence** | High — inventory measured, contamination **CONFIRMED** |

**One-line answer:** The openly-available Tigrinya corpus is small and measured —
~67K monolingual rows plus 1.4M parallel pairs — but **~99% of it carries no
usable licence**, and one dataset advertised for *pretraining* **verifiably
contains our evaluation anchor's validation data**.

---

## Key Findings

- **The corpus is now measured, not estimated.** `[verified]` via the HF dataset
  API:

  | Dataset | Rows | Parquet | Licence |
  | --- | ---: | ---: | --- |
  | `mewaeltsegay/TigrinyaLargeText` | 12,400 | 36.1 MB | **MIT** |
  | `SIMBA9657/haddas-tigrinya-corpus` | 2,653 | 4.3 MB | **CC-BY-SA-4.0** |
  | `farefaine/tigrinya-pretraining` | 52,100 | 15.7 MB | ⚠️ none |
  | `michsethowusu/english-tigrinya_sentence-pairs` | **1,400,000** | 110.4 MB | ⚠️ none |

- **No hidden reservoir exists.** TiRoBERTa was pretrained on 40M tokens; the
  open monolingual text here is 56 MB of parquet across ~67K documents — the same
  order of magnitude, not larger. **A-002 confirmed: we are data-scarce.**
  *(I deliberately did not convert MB→tokens; Ge'ez parquet compression ratios
  are unknown to me and a fabricated figure would propagate.)*
- **The 1.4M en–ti pairs corroborate the `[reported]` NLLB figure.** The schema
  carries a `similarity` column, characteristic of LASER/NLLB-mined bitext.
- **⚠️ Licensing, not volume, is the binding constraint.** Cleanly licensed:
  **15,053 documents.** Everything else — including the single largest resource —
  has no stated licence. Combined with TiQuAD's unresolved upstream copyright,
  this is the sharpest form of **A-009** yet.
- **⚠️ HF `size_categories` tags are unreliable.** Two of four datasets carry
  *internally contradictory* size metadata; `farefaine` overstates by up to ~20×.
  **Query the API for real row counts.**
- **⛔ CONFIRMED evaluation contamination** `[verified]`.
  `farefaine/tigrinya-pretraining`, titled *"Tigrinya Raw Pretraining Sources"*
  and tagged for pretraining, **contains TiQuAD validation data.**

  Evidence chain, all verified: identical schema field-for-field; validation
  split exactly 934 rows in both; **row-level preview returned `article_title`
  ሃብቶም ክብረኣብ (ሞጀ) with a context passage identical to the sample entry TiQuAD
  publishes on its own dataset card**; three answer annotations per question,
  which is TiQuAD's documented validation-set convention.

  **TiQuAD is our DEC-005 evaluation anchor.** Anyone who pretrains on this
  corpus and evaluates on TiQuAD is reporting a contaminated score. Most likely
  an honest aggregation error — the downstream effect is identical.

  **Consequences:** any published Tigrinya model trained on this corpus has an
  untrustworthy QA score; report upstream to the maintainer (**G-11**).

## Important Decisions

| Decision | ID | Status |
| --- | --- | --- |
| Mandatory contamination screening before any dataset enters training use | DEC-008 | Accepted |
| DEC-005 amended — treat external Tigrinya QA scores as suspect until screened | DEC-005 | Amended |

## Rejected Alternatives

| Alternative | Rejected because |
| --- | --- |
| Use everything available, resolve licensing later | We are infrastructure others build on; passing on rights we lack is a serious failure (P-9), and retrofitting compliance means discarding trained artefacts |
| Use unlicensed data freely for shipped artefacts | Same. **Quarantine for research-only use is adopted instead** — structurally, not by convention |
| Build a corpus from scratch now | Months of work before attempting the cheap option: asking maintainers to add a licence file |
| Trust HF `size_categories` for planning | Measured wrong on 2 of 4 datasets sampled, by up to ~20× |

## Important Numbers

| Metric | Value | Basis |
| --- | --- | --- |
| Monolingual/QA rows measured | **67,153** (56.1 MB parquet) | `[verified]` |
| **Cleanly licensed documents** | **15,053** | `[verified]` |
| Unlicensed rows | **1,452,100 (~99%)** | `[verified]` |
| en–ti parallel pairs | **1,400,000** | `[verified]` |
| TiRoBERTa training corpus | 40M tokens | `[verified]` |
| `farefaine` vs TiQuAD validation split | **934 == 934** | `[verified]` |
| **Contamination** | **CONFIRMED — identical context + title + 3-annotation pattern** | `[verified]` |
| Total storage | 166 MB parquet | `[verified]` |
| Size-tag error rate | 2 of 4 datasets sampled | `[verified]` |

## Recommended Next Steps

1. ~~Verify the `farefaine`/TiQuAD row overlap~~ ✅ **done — confirmed.**
   Now: **report it upstream to the `farefaine` maintainer** (G-11), and treat
   any Tigrinya model trained on this corpus as having an untrustworthy QA score.
2. **Pursue licence clarification** with `michsethowusu` and `farefaine`. Cheapest
   high-value action available: a few emails could unlock 1.4M parallel sentences.
3. **Quarantine unlicensed data structurally** — research-only, never shipped.
4. **Adopt `haddas`'s provenance schema** as our internal standard; it is the
   best-documented dataset found (`source_pdf`, `page_start/end`, `issue_date`).
5. **Report the contamination finding upstream** to the `farefaine` maintainer —
   a cheap, genuine ecosystem contribution (**G-11**).

## References

1. HF dataset API, accessed 2026-07-29 `[verified]`
2. `fgaim/tiquad` card — published split sizes `[verified]`
3. `docs/research/RESEARCH_ACCESS.md` — egress limits

---

**Open questions / uncertainty:** ~~Does `farefaine` contain TiQuAD rows?~~
**Confirmed yes.** Still open: what is in the other ~42K train rows? Will the unlicensed datasets be
clarified? **Have published Tigrinya models already trained on contaminated
data** — which would make their reported QA scores unreliable? All blocked on
egress or on maintainer response.
