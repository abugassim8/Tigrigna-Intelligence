# Evaluation Datasets

> **Status: one evaluation set committed and in use; the second anchor is not
> obtainable.** ⚠️ **This document read "Status: none — no evaluation datasets
> have been identified, assembled, or built" until 2026-08-19**, while a
> screened FLORES+ sample was committed and had already produced DEC-009.
>
> **Evidence:** DEC-005 (anchors), `../../experiments/003-metric-validity/`,
> and the screening records under `../../experiments/*/*/screening/`.

## Purpose of this document

The register of evaluation datasets used by this project: what each one is,
where it came from, what it measures, and how trustworthy it is.

## Why this document exists

Evaluation data is the ground truth for every quality claim the project makes.
If it is wrong, contaminated, or unrepresentative, every downstream number is
wrong in a way that no amount of careful modelling will reveal.

For a low-resource language, this problem is sharper than usual. Evaluation sets
are scarce, and the ones that exist are often small, of unknown provenance, or
derived from sources that may also appear in training data. Assumption **A-006**
holds that we will need to build much of this ourselves — a significant
workstream that this document tracks.

There is also a durability argument: a well-built Tigrinya evaluation set will
outlive every model this project ships. It is plausibly the most valuable thing
we produce.

## How to use it

- Before evaluating anything, check which dataset is appropriate and what its
  known limitations are.
- Before reporting a result, confirm the evaluation set was not contaminated by
  the training data.
- When adding a dataset, fill in every field below. An evaluation set with
  unknown provenance is not usable as evidence.

## Dataset register

| ID | Name | Capability | Size | Source | Licence | Contamination checked | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **E-01** | FLORES+ Tigrinya sample (`flores_ti.txt`) | Translation (target side) | **30 sentences**, 661 words | `alexei-v-ivanov-amd/flores_plus`, `tir_Ethi` ids 0–29 | **CC-BY-SA-4.0** | ✅ **yes** — `CLEARED`, record committed | **In use** — produced DEC-009 |
| **E-02** | FLORES+ English sample (`flores_en.txt`) | Translation (source side) | **30 sentences**, 708 words | same, `eng_Latn` ids 0–29 | **CC-BY-SA-4.0** | ✅ yes — `BLOCKED — quality`, **expected**: it is English, and the gate measures non-Ethiopic characters | **In use** as the source side |
| **E-03** | FLORES+ devtest (full) | Translation | 1,012 sentences `[reported]` | FLORES+ | CC-BY-SA-4.0 | ❌ not obtained | ⚠️ **Blocked — egress (A-09)** |
| **E-04** | TiQuAD | Extractive QA | 6,508 Q / 10,637 A `[verified]` | `farefaine` / upstream | CC-BY-SA-4.0, **upstream copyright unresolved** | ⚠️ **contamination CONFIRMED in a third-party corpus** | ⚠️ **Not obtained** — test set not public (**A-04**), copyright unresolved (**A-06**) |

**One of DEC-005's two anchors is unusable and the other is a 30-sentence
sample.** That is the real evaluation position, and it is easy to lose behind
the phrase "FLORES-200 and TiQuAD as evaluation anchors."

### Why E-01 is small, and what it is not

30 sentences is enough to establish a *metric property* — experiment 003
measured chrF's behaviour against BLEU on identical content in two languages —
and **nowhere near enough to score a system**. Confidence intervals on 30
sentences are very wide (chrF `[30.62, 88.05]` on a sample run), which is
exactly why DEC-009 requires intervals rather than point estimates.

### Datasets used for property testing, not evaluation

These are **not** evaluation sets. They are corpus text used to exercise
intrinsic properties, and they carry screening records for the same reason:

| File | Source | Licence | Screening |
| --- | --- | --- | --- |
| `tlt_000_clean.txt` | `mewaeltsegay/TigrinyaLargeText` | MIT | `CLEARED` |
| `haddas_001_colscrambled.txt` | `SIMBA9657/haddas-tigrinya-corpus` | CC-BY-SA-4.0 | `CLEARED` |
| `tlt_001_CORRUPTED_sample.txt` | same as `tlt_000` | MIT | `BLOCKED — quality`, **intentionally** — it is the negative control for the quality gate |

### What is not here, and why it matters

**No Tigrinya evaluation set exists for any MVP primitive.** DEC-023 answers
that for three of four capabilities by evaluating them **intrinsically** — no
annotation needed. **Morphology is the exception**: it needs gold data, and it
is also unimplemented (**A-07**).

**A-006 anticipated building evaluation data.** DEC-023 shrank that from four
capabilities to one, which is the single largest reduction in scope this
project has achieved. It did not eliminate it.

## Required fields for each dataset

```markdown
### [Dataset name]

- **ID:**
- **Capability evaluated:**
- **Size:** items, tokens, or pairs
- **Source and provenance:** where it came from, who produced it, how
- **Licence:** and what it permits
- **Collection method:** and consent basis if human-sourced
- **Dialect / register coverage:**
- **Annotation process:** who annotated, guidelines, inter-annotator agreement
- **Known limitations:** be specific and honest
- **Contamination check:** method used, date, result
- **Baseline scores:** what known systems achieve on it
- **Location:** `datasets/evaluation/...`
- **Maintainer:**
```

## Standards for evaluation data

1. **Provenance is mandatory.** A dataset of unknown origin cannot support a
   claim.
2. **Contamination checks are mandatory**, documented with method and date.
3. **Limitations are stated.** Every evaluation set is unrepresentative in some
   way; say how.
4. **Held out means held out.** Evaluation data is never used for training,
   tuning, or prompt development. Once it leaks, it is burned and cannot be
   un-burned.
5. **Versioned.** Changing an evaluation set invalidates comparison with earlier
   results unless the change is versioned and recorded.
6. **Licence permits our use** — see **P-9**.

## What future contributors should add

Every evaluation dataset, with all fields completed. Also record datasets that
were evaluated and **rejected**, with the reason — "found, but derived from the
same corpus as our training data" is exactly the kind of finding that saves
someone else a week.

## Related

- `evaluation_strategy.md` · `metrics.md`
- `../../datasets/evaluation/` — where the data lives
- `../research/reports/03_data_strategy/` · `../research/reports/08_evaluation/`
