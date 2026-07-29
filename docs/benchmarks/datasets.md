# Evaluation Datasets

> **Status: none.** No evaluation datasets have been identified, assembled, or
> built.
>
> **Gated on:** `../research/reports/08_evaluation/` and
> `../research/reports/03_data_strategy/`

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
| — | *None yet* | — | — | — | — | — | — |

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
