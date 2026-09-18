# Tigrinya Corpus Inventory and a Contamination Risk

| Field | Value |
| --- | --- |
| **Report ID** | `001-corpus-inventory-and-contamination` |
| **Domain** | `03_data_strategy` |
| **Stage** | Scout → Analyst |
| **Date** | 2026-07-29 |
| **Status** | Accepted — contamination **CONFIRMED** same day |
| **Summary** | `docs/research/summaries/005-corpus-inventory-and-contamination.md` |
| **Related decisions** | DEC-008; amends DEC-005; updates A-006 |

---

## Objective

Measure — not estimate — how much openly-available Tigrinya text actually
exists, and assess whether it is usable. This gates the orthographic-variation
survey DEC-007 depends on, and it is the number `04_model_strategy` must plan
against.

**Method note:** rather than reading dataset descriptions, this report queried
the Hugging Face dataset API for **actual row counts, parquet sizes, and
schemas**. That turned out to matter — see Finding 2 and Finding 3.

---

## Finding 1 — The measured inventory

All `[verified]` from the HF dataset API, 2026-07-29.

### Monolingual / document text

| Dataset | Rows | Parquet | Licence | Notes |
| --- | --- | --- | --- | --- |
| `mewaeltsegay/TigrinyaLargeText` | **12,400** | 36.1 MB | **MIT** | Articles; schema `title, content, source, category, url` — has provenance fields |
| `SIMBA9657/haddas-tigrinya-corpus` | **2,653** | 4.3 MB | **CC-BY-SA-4.0** | 63 PDF issues of *Haddas Eritrea*; schema carries `char_count, topic, issue_date, source_pdf, page_start/end` — **the best-documented provenance found** |
| `farefaine/tigrinya-pretraining` | **52,100** | 15.7 MB | **NOT STATED** ⚠️ | ⚠️ **Mislabelled — see Finding 3** |
| **Total** | **67,153 rows** | **56.1 MB** | | |

### Parallel

| Dataset | Rows | Parquet | Licence |
| --- | --- | --- | --- |
| `michsethowusu/english-tigrinya_sentence-pairs` | **1,400,000** | 110.4 MB | **NOT STATED** ⚠️ |

The schema is `similarity, English, Tigrinya` — a `similarity` score is
characteristic of **LASER/NLLB-mined bitext**. This **corroborates** the
previously `[reported]` figure of ~1.4M NLLB en–ti sentence pairs: the number
now has an independent, measured match.

### What this means in context

The strongest available Tigrinya encoder, TiRoBERTa, was pretrained on
**40M tokens** `[verified]`. The openly-licensed monolingual text measured here
is **56 MB of compressed parquet across ~67K documents**.

**A deliberate non-estimate:** I am not converting MB to a token count. Parquet
compression ratios for Ge'ez UTF-8 text are not known to me, and a fabricated
token figure here would propagate into model-strategy decisions. What is
defensible: **the openly-available monolingual corpus is in the same order of
magnitude as TiRoBERTa's 40M-token corpus, not an order of magnitude larger.**
There is no hidden reservoir of Tigrinya text on the Hub.

**A-002 is confirmed** — we are firmly in the data-scarce regime, and
data-hungry methods remain off the table.

## Finding 2 — Hugging Face size tags are unreliable. Do not trust them.

Two of four datasets carry **internally contradictory** size metadata:

| Dataset | Tag says | Metadata says | **Actual** |
| --- | --- | --- | --- |
| `TigrinyaLargeText` | `10K<n<100K` | `100K<n<1M` | **12.4K** |
| `farefaine/tigrinya-pretraining` | `10K<n<100K` | `1M<n<10M` | **52.1K** |

`farefaine`'s metadata overstates by up to **~20×**.

**Operational consequence:** any corpus-size planning based on HF
`size_categories` is unreliable. **Query the dataset API for actual row counts.**
This is cheap and it is now a required step — recorded in `RESEARCH_ACCESS.md`.

## Finding 3 — ⚠️ A dataset advertised for pretraining contains QA evaluation data

**This is the most consequential finding in the report.**

`farefaine/tigrinya-pretraining` is titled *"Tigrinya Raw Pretraining Sources"*
and tagged `task_categories:text-generation`, `pretraining`. Its card describes
it as raw text for the "Qal" language-model project.

**But its actual schema is:**

```
id | question | context | answers | article_title | context_id
```

That is **SQuAD/TiQuAD extractive question-answering format** — not raw
pretraining text. `answers` is a structured list of `{answer_start, text}`.

### The split sizes

| | train | validation | test |
| --- | ---: | ---: | ---: |
| `farefaine/tigrinya-pretraining` | 46,700 | **934** | 4,500 |
| **TiQuAD (published)** | 4,452 | **934** | 1,122 |

**The validation split is exactly 934 rows in both.** TiQuAD's validation split
is 934. The schema is TiQuAD's schema, field for field, including the unusual
`context_id` and `article_title` columns.

### Why this matters

**TiQuAD is our primary QA evaluation anchor under DEC-005.** Its authors
deliberately withheld the test split to prevent contamination from web-crawled
training data — exemplary practice, documented in Phase 1.

If a dataset labelled "pretraining sources" contains TiQuAD's evaluation data,
then **anyone who pretrains on it silently destroys their own TiQuAD evaluation
validity.** The dataset is aggregated from "publicly available Tigrinya
datasets", so this is most likely an honest aggregation error rather than
anything deliberate — but the effect on a downstream user is identical.

### Confidence and limits — stated precisely

This is a **strong signal, not proof.**

**What is verified:** the schema is TiQuAD's; the validation split is exactly
934 rows; the dataset is advertised for pretraining; it carries no licence.

**What is not verified:** row-level content overlap. I could not download and
diff the parquet files — `huggingface.co` direct download is egress-blocked in
this session (see `RESEARCH_ACCESS.md`). The train split (46,700) is ~10× TiQuAD's
(4,452), so it plainly contains more than TiQuAD alone; the aggregation may
include `tigrinya-squad` (the silver MT'd set) and others.

**Falsifiable prediction:** downloading both and comparing `id` or `context`
fields will show overlap. That check is the top action item.

**⚠️ SUPERSEDED — see the CONFIRMED section immediately below.** The row-level
check was subsequently run and the overlap is verified. The hedging above is
retained to show what was known before the check, not because it still stands.

---

## ✅ CONFIRMED — 2026-07-29, same day

**The contamination is verified. This is no longer a signal.**

`dataset_preview` on `farefaine/tigrinya-pretraining`, config `default`, split
`validation`, rows 0–2 returned:

- `article_title`: **ሃብቶም ክብረኣብ (ሞጀ)**
- `context`: a passage beginning *"ሃብቶም ክብረኣብ (ሞጀ) ሞጀ ኣብ 80'ታትን ኣብ ፈለማ 90'ታትን
  ካብቶም ናይ ክለብ ኣልታሕሪር ንፉዓት ተኸላኸልቲ ነይሩ…"*
- `context_id`: `17.1`
- `answers`: **three annotations per question**

**The TiQuAD dataset card publishes its own sample entry as that identical
passage** — same `title` (ሃብቶም ክብረኣብ (ሞጀ)), same context text, three answer
annotations. TiQuAD documents that "validation and test samples include up to 3
answer annotations per question" specifically to enable human-performance
estimation.

### The evidence chain

| Evidence | Status |
| --- | --- |
| Identical schema, field for field | `[verified]` |
| Validation split exactly 934 rows in both | `[verified]` |
| **Identical `article_title` and `context` text** | **`[verified]`** |
| **Three answer annotations per question — TiQuAD's validation convention** | **`[verified]`** |

**Conclusion: `farefaine/tigrinya-pretraining` contains TiQuAD validation data
and is advertised as "Tigrinya Raw Pretraining Sources".** Anyone who pretrains
on it and then evaluates on TiQuAD is reporting a contaminated score.

The earlier hedge ("strong signal, not proof") is **withdrawn** — the row-level
check that was blocked has now been run and it confirms the finding.

**Nothing about the recommendation changes.** DEC-008 was justified by the
possibility; it is now justified by fact. What changes is urgency: this should
be reported upstream to the `farefaine` maintainer promptly, and any published
Tigrinya model that used this corpus has a QA score that cannot be trusted.

---

## Finding 4 — Licensing is the binding constraint, again

| Status | Datasets | Rows |
| --- | --- | ---: |
| **Clean licence** | `TigrinyaLargeText` (MIT), `haddas` (CC-BY-SA-4.0) | 15,053 |
| **No stated licence** ⚠️ | `farefaine`, `michsethowusu/english-tigrinya` | 1,452,100 |

**~99% of the measured rows carry no usable licence.** The single largest
resource — 1.4M parallel sentences — is unlicensed, and the cleanly-licensed
monolingual corpus is **15,053 documents**.

Combined with Phase 1's finding that TiQuAD's upstream copyright is unresolved
(fair-use academic only), **licensing — not volume — is the binding constraint
on this project's data strategy.** That is a sharper statement of **A-009** than
Phase 1 could make.

---

## Alternatives Considered

**A — Use everything available, resolve licensing later.** Rejected. We are
building infrastructure others depend on; passing on rights we do not have is a
serious failure (**P-9**), and retrofitting licence compliance means discarding
trained artefacts.

**B — Use only cleanly-licensed data.** Currently ~15K documents. Safe but very
small. **Adopted as the default** for anything shipped.

**C — Use unlicensed data for research only, quarantined.** **Adopted alongside
B.** Permits measurement and experimentation without creating shipping liability
— provided quarantine is structural, not a convention.

**D — Pursue licence clarification with publishers.** **Recommended in
parallel.** Several are individual HF users who may simply not have added a
licence file. Cheap to ask; potentially unlocks 1.4M parallel sentences.

---

## Cost Analysis

| Item | Cost | Note |
| --- | --- | --- |
| Corpus inventory (this report) | ~0 | API queries only |
| Contamination verification | Hours | Download + diff; **blocked on egress** |
| Licence clarification outreach | Days, mostly waiting | Highest expected value per hour spent |
| Building a clean corpus from scratch | Months | Only if outreach fails |
| Storage | Negligible | 166 MB total parquet |

**The cheapest high-value action is asking people to add licence files.** It
could unlock ~1.4M parallel sentences for nothing but a few emails.

---

## Build vs Buy Decision

| Component | Verdict |
| --- | --- |
| Monolingual corpus | **Reuse** — MIT/CC-BY-SA sets; quarantine the rest |
| Parallel corpus | **Blocked on licence** — pursue clarification |
| Contamination screening | **Build** — see DEC-008; nothing existing does this |
| Provenance tracking | **Build**, modelled on `haddas`'s schema, which is the best example found |
| Evaluation sets for primitives | **Build** — confirmed absent (Phase 1) |

---

## Recommended Approach

1. **Adopt mandatory contamination screening (DEC-008)** before any dataset
   enters training use.
2. **Quarantine unlicensed data structurally** — research-only, never in a
   shipped artefact.
3. **Pursue licence clarification** with `michsethowusu` and `farefaine`.
4. **Verify the `farefaine`/TiQuAD overlap** as soon as egress permits.
5. **Adopt `haddas`'s provenance schema** as our internal standard.
6. **Report the contamination finding upstream** to the `farefaine` maintainer —
   it is a genuine contribution to the ecosystem (**G-11**), and cheap.

Confidence: **high** on the inventory (measured); **medium-high** on the
contamination signal (schema and split size verified, row overlap not).

---

## Risks

| Risk | Likelihood | Impact | Mitigation |
| --- | --- | --- | --- |
| Contamination is real and already propagated into published Tigrinya models | **Medium-high** | **High** — invalidates comparisons against them | Screen everything; treat external Tigrinya QA scores with suspicion |
| Licence clarification fails | Medium | High — leaves ~15K documents | Start outreach now; scope a fallback |
| More mislabelled datasets exist | **High** — 1 of 4 sampled | Medium | DEC-008 screening catches them |
| Available corpus is too small for the capability scope | Medium | High | Confirms narrowing scope at DP-4 (90-day roadmap) |
| I am wrong about `farefaine` | Medium | Low | Stated as a signal, not a fact; falsifiable check specified |

---

## Open Questions

- Does `farefaine` actually contain TiQuAD rows? *(Blocked on egress.)*
- What is in the other 46.7K − 4.4K rows of its train split?
- Will `michsethowusu` clarify the 1.4M-pair licence?
- What is in HornMT? *(GitHub blocked.)*
- Have published Tigrinya models already trained on contaminated data?
- Actual token count of the clean corpus — needs download.

---

## References

1. HF dataset API, accessed 2026-07-29 `[verified]` — row counts, schemas, sizes
2. `docs/research/summaries/001-tigrinya-nlp-ecosystem-scan.md` — TiQuAD splits
3. `fgaim/tiquad` dataset card — published split sizes `[verified]`
4. `docs/research/RESEARCH_ACCESS.md` — egress limits

---

## Checklist

- [x] **What exists?** ~67K monolingual/QA rows (56 MB) and 1.4M parallel pairs (110 MB), measured.
- [x] **What can be reused?** `TigrinyaLargeText` (MIT) and `haddas` (CC-BY-SA-4.0) — 15,053 documents cleanly licensed.
- [x] **What should be built?** Contamination screening, provenance tracking, primitives evaluation sets.
- [x] **What should not be built?** A corpus from scratch before attempting licence clarification.
- [x] **Cost estimate?** Inventory ~0; outreach days; from-scratch corpus months. Storage negligible.
- [x] **Maintenance burden?** Low for adopted data; screening is ongoing but automatable.
- [x] **Licensing?** **The binding constraint — ~99% of measured rows lack a usable licence.**
- [x] **Technical risks?** Contamination, licence failure, mislabelled datasets, corpus too small.
- [x] **Final recommendation?** Screen everything (DEC-008), quarantine unlicensed data, pursue licences, verify the overlap.

## Completion

- [x] Summary at `docs/research/summaries/005-corpus-inventory-and-contamination.md`
- [x] DEC-008 recorded; DEC-005 amended; A-006/A-002/A-009 updated
- [x] Rejected options logged (R-019, R-020)
- [x] References updated
