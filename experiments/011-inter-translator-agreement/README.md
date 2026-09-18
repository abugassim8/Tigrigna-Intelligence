# Experiment 011 — inter-translator agreement

| Field | Value |
| --- | --- |
| **Date** | 2026-09-12 |
| **Question** | What does a *good* chrF look like on these anchors? |
| **Artefact** | `results.json` — reproduces byte-identically (**DEC-016**) |
| **Depends on** | `sacrebleu` via `tigrinya_eval.metrics`; committed anchors only |

## Why

When **A-09** lands and the first model is finally scored, someone will read
"chrF 30" and have to decide whether it is good. Nothing in this repository said
what good looks like. This measures what **two professional human translators**
score against each other on the same English, in the same domain.

## ⚠️ It is not a ceiling

chrF between two translations and chrF between a system and a reference are
**different quantities** — the first has no privileged "correct" side. A model
can legitimately exceed it. This is a reference point for reading scores, and
any write-up calling it a ceiling is wrong.

## Result

| Pair | Split | chrF | 95% CI | normalised | Δ |
| --- | --- | ---: | --- | ---: | ---: |
| **ER vs ET** — independent translators | dev | **23.84** | [23.16, 24.52] | 23.92 | +0.08 |
| | test | **24.58** | [24.17, 24.99] | 24.64 | +0.06 |
| ti vs ET — one lineage | dev | 85.59 | [83.90, 87.28] | 85.62 | +0.03 |
| | test | 83.65 | [82.66, 84.64] | 83.67 | +0.02 |
| ti vs ER | dev | 23.07 | [22.42, 23.72] | 23.17 | +0.09 |
| | test | 23.95 | [23.56, 24.34] | 24.02 | +0.07 |

**Two professional humans translating the same English agree at chrF ≈ 24.**

⚠️ The three `test` figures were **observed during planning**, so they are
recorded as `already_seen_on_test` and are **not** presented as hypotheses met
(**DEC-016**). That they reproduced to the decimal here is an implementation
check, not a result.

## Pre-registered findings

All three were committed before the dev split or any per-segment number was
looked at.

| | Prediction | Measured | |
| --- | --- | --- | --- |
| **H1** | dev ER-vs-ET within **±3** of test's 24.58 — agreement is a property of the *pair*, not the split | 23.84, difference **0.74** | ✅ **CONFIRMED** |
| **H2** | dev ti-vs-ET above **75**, so the single-lineage relationship holds on dev | **85.59** | ✅ **CONFIRMED** |
| **H3** | the per-segment distribution is right-skewed, **median below mean** | dev 21.78 < 23.76; test 22.91 < 24.42 | ✅ **CONFIRMED** |

### H3 is the one that changes how the number should be read

A corpus chrF of ~24 could have been every segment scoring 24, or half scoring 5
and half scoring 45. **It is neither, and it is much closer to the first.**

| Split | p10 | median | mean | p90 | below 10 | above 50 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| dev | 13.48 | 21.78 | 23.76 | 36.09 | **31** of 971 | **22** of 971 |
| test | 13.76 | 22.91 | 24.42 | 36.69 | **48** of 2,100 | **38** of 2,100 |

The skew is real but mild, and the distribution is **tight**: 80% of segments
fall between roughly 13 and 37, only ~3% score below 10 and ~2% above 50. So
~24 is the *typical* segment, not an average of agreement and disagreement.

**That strengthens it as a reference point.** A model scoring in the low 20s on
this anchor is performing like a second human translator on most sentences,
rather than matching well on some and failing on others.

## ⚠️ What this cannot tell you

**The pair varies in two ways at once.** `tir_er` vs `tir_et` differ by
*translator* **and** by *standard* (Eritrean vs Ethiopian). This experiment
cannot separate them and does not try — **A-13** is what would.

**Normalisation is not the explanation.** Collapsing ጸ/ፀ and ኣ/አ moves every
figure by **less than 0.1 chrF**, so the ER/ET divergence is lexical and
structural, not orthographic. That is consistent with the morphology
measurement, where only 477 of 32,990 unique words change under normalisation at
all.

**n = 1 translator pair, one domain, one direction.** COVID/medical prose from
TICO-19. A reference point, not a general fact about Tigrinya translation.

## Why only TICO-19

Inter-translator agreement needs two independent translations of one source.

- **HornMT cannot contribute.** `data/anchors/hornmt/` holds **one** Tigrinya
  reference (`tir.txt`). An earlier draft of the handoff listed it as a
  pre-commitment target; that was wrong and is corrected.
- **TICO-19 has three references but only one independent pair.** `tir_ti` and
  `tir_et` are one translation lineage — 83.65 and 85.59 between them — so only
  `tir_er` vs `tir_et` is two translators working independently.

## Reproducing

```bash
python3 experiments/011-inter-translator-agreement/run.py          # rewrite results.json
python3 experiments/011-inter-translator-agreement/run.py --check  # CI: must match
```

chrF is **not symmetric** — it is F-score based and beta-weighted — so the
hypothesis/reference direction is fixed in `PAIRS` and recorded in the artefact.

sacrebleu's bootstrap is **seeded**: verified identical across separate
processes on 2026-09-12, which is why confidence intervals can appear in a
DEC-016 artefact at all. Had it not been, the CI bounds would have drifted every
run and the reproducibility job would have failed for a reason that had nothing
to do with the data.
