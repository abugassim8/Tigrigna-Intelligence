# Experiment Template

> **About this template**
>
> **Purpose:** The standard structure for an experiment — an empirical test run
> to settle a question that argument alone cannot.
>
> **Why it exists:** Experiments are worthless if they cannot be reproduced or if
> their result is not written down. This template enforces both. It also enforces
> stating the hypothesis and the success criterion *before* running, which is the
> only defence against deciding after the fact that whatever happened was what we
> wanted.
>
> **How to use it:** Copy this into `experiments/NNN-slug/README.md` before
> running anything. Fill in everything above "Results" first. Run. Then fill in
> the rest — including when the result is negative or inconclusive.
>
> **What to add over time:** Add fields that turn out to be necessary for
> reproduction. If you ever fail to reproduce your own experiment, whatever was
> missing belongs in this template.

---
---

# Experiment NNN — [Title]

| Field | Value |
| --- | --- |
| **Experiment ID** | `NNN-slug` |
| **Date** | YYYY-MM-DD |
| **Author** | |
| **Status** | Planned / Running / Complete / Abandoned |
| **Related report** | `docs/research/reports/NN_domain/NNN-slug.md` |
| **Related decision** | DEC-NNN |

---

## Question

What are we trying to find out? One sentence. If you cannot state it in one
sentence, the experiment is not scoped yet.

## Hypothesis

What you expect to happen, and why. **Write this before running.** A hypothesis
recorded after the fact is not a hypothesis.

## Success Criteria

What result would count as confirming the hypothesis, and what would count as
refuting it. **Define these before running.** Include the threshold — "BLEU above
X", "latency under Y ms", "error rate below Z%". Without a pre-committed
threshold, every result looks like a partial success.

## Setup

### Data
| Item | Source | Version / hash | Size | Notes |
| --- | --- | --- | --- | --- |
| | | | | |

Where the data came from, how it was split, and — critically — what was done to
prevent train/eval contamination.

### Models / tools
| Item | Version | Source | Licence |
| --- | --- | --- | --- |
| | | | |

### Environment
- Hardware:
- OS / container image:
- Key dependency versions:
- Random seed(s):
- Config file:

### Command to reproduce
```bash
# The exact command. Not an approximation of it.
```

## Method

What was actually done, step by step. Enough that someone else could re-run it
without asking you questions.

1.
2.
3.

## Results

| Metric | Value | Baseline | Delta |
| --- | --- | --- | --- |
| | | | |

Raw outputs: `experiments/results/NNN-slug/`
Logs: `experiments/logs/NNN-slug/`

Report what happened, not what you hoped would happen.

## Analysis

What the numbers mean. Where the approach succeeded and where it failed. Look at
the failure cases specifically — for a low-resource language, the aggregate
metric routinely hides the thing that actually matters, and error analysis is
usually where the real finding is.

## Conclusion

Was the hypothesis confirmed, refuted, or is the result inconclusive?
**All three are valid outcomes and all three get written down.** A refuted
hypothesis that is recorded saves the next person from running the same
experiment.

## Threats to Validity

What could make this result wrong or misleading?

- Sample size / test set size:
- Data contamination:
- Metric validity for Tigrinya specifically:
- Confounds:
- Generalisation limits:

## Next Steps

What this experiment implies. What to run next. Whether it supports a decision.

## Reproducibility

- [ ] Seeds fixed and recorded
- [ ] Dependency versions pinned
- [ ] Data version / hash recorded
- [ ] Exact command recorded
- [ ] Hardware recorded
- [ ] Config committed
- [ ] Result files committed (small ones) or their retrieval documented
