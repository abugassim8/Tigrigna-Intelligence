# Experiment 007 — Does our evaluation harness change the number?

| Field | Value |
| --- | --- |
| **Experiment ID** | `007-harness-fidelity` |
| **Date** | 2026-08-19 |
| **Status** | **Complete — H1, H2, H3 confirmed; H4 REFUTED, and the refutation is the finding** |
| **Related decisions** | Tests **DEC-009**, **DEC-010**; adds a caveat to DEC-009 |
| **Determinism** | Byte-identical across runs and across `PYTHONHASHSEED` |

---

## Question

`services/evaluation` wraps sacrebleu to enforce DEC-009 and DEC-010. It has
tests, and **nothing else in the repository used it.** A wrapper nobody consumes
can drift, and its own tests are not independent evidence — this session found
**five checks that could not fail**, one of them a live shipping bug *in this
package* (an inverted confidence interval, `ci_low > ci_high`).

So: **is the number we report the number sacrebleu computed?**

## Results

| Hypothesis | Prediction | Measured | Verdict |
| --- | --- | --- | --- |
| **H1** — the harness is transparent | bit-identical to raw sacrebleu | **4/4 corruption levels identical** | ✅ |
| **H2** — BLEU is never obtainable alone | both metrics always | both returned, chrF primary, no BLEU-only accessor | ✅ |
| **H3** — `aggregate()` raises, not warns | raises | raises for **both** single-variety and `unknown` | ✅ |
| **H4** — CIs widen as *n* falls | monotonic 30 → 3 | **monotonic 30 → 5, breaks at n=3** | ❌ |

**H1 is the load-bearing one.** If it ever fails, every score this project has
published came from our arithmetic rather than sacrebleu's — and it would be
invisible, because the number would still look like a plausible chrF.

### ⚠️ H4's refutation: the bootstrap understates uncertainty at very small n

Median 95% chrF interval width, over 20 random subsets per size:

| n | Median CI width |
| ---: | ---: |
| 30 | **2.69** |
| 20 | 3.06 |
| 10 | 3.87 |
| **5** | **5.02** |
| **3** | **4.59** ⚠️ *narrower than n=5* |

Widening holds from 30 down to 5 and then **reverses**. The likely mechanism:
bootstrap resampling of 3 items has only **27 distinct multisets**, many of them
producing identical scores, so the interval cannot express the uncertainty it
should.

**A confidence interval at n=3 understates uncertainty exactly where uncertainty
is greatest.** DEC-009 requires spread on small sets precisely because point
estimates mislead there — this says the spread itself stops being trustworthy
below roughly n=5. **Our own evaluation anchor is 30 sentences**, so this is a
live concern rather than a curiosity: any per-variety or per-domain breakdown of
that set lands in the range where the interval starts lying.

### A design error, recorded because it changed the answer

**The first version of H4 was confounded and reported a false refutation.** It
used `refs[:n]`, which varies sentence **content** along with sample **size** —
so 10 particular sentences could be more homogeneous than 30, and the sequence
came out non-monotonic (2.71 → 2.33 → 5.08) for reasons that had nothing to do
with the bootstrap.

Averaging over random subsets isolates *n*, which is what the hypothesis was
actually about. **The corrected design changed the finding**: from "CIs do not
widen" to "CIs widen down to n=5 and then break", which is a different and much
more useful statement.

### H2's first result was also a false positive

The initial check flagged `sacrebleu_version` as a "BLEU-only accessor" because
the field name contains the substring `bleu`. **H2 was reported REFUTED by a
faulty test, not a faulty harness.** Fixed by excluding version metadata.

**Two of four hypotheses initially produced wrong verdicts through defects in
the experiment rather than the subject.** Both are recorded rather than quietly
corrected, because the failure mode — a measurement error presented as a finding
— is the same one that produced DEC-023's retracted 1,639/1,639.

## Report caveats

A report from the harness carries its own context, so it cannot be quoted
without it. All four present:

- chrF is primary
- states the measured **1.08×** BLEU penalty on Tigrinya
- says results are **NOT aggregated across varieties**
- marks a CC-BY-NC-4.0 system **`COMPARISON ONLY`**

## Reproduce

```bash
pip install -e services/primitives -e services/evaluation
python3 run.py
```

Deterministic, including sacrebleu's bootstrap.

## Limits

- **30 reference sentences**, and the hypotheses are about the harness, not
  about Tigrinya. Nothing here says our translations are good — no model has
  been scored (**A-09**).
- The n=3 mechanism is **inferred, not proven.** 27 distinct multisets is an
  arithmetic fact; that it *causes* the narrowing is the obvious explanation and
  was not independently tested.
- Corruption is a synthetic error profile. It resembles inflectional near-misses
  but is not real system output.
