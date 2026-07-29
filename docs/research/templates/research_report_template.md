# Research Report Template

> **About this template**
>
> **Purpose:** The standard structure for a full Analyst-stage research report.
>
> **Why it exists:** So reports are comparable, complete, and skimmable. A reader
> should be able to jump to "Cost Analysis" in any report and find the same kind
> of content. Ad-hoc structures make reports impossible to compare and easy to
> leave incomplete.
>
> **How to use it:** Copy everything below the line into
> `docs/research/reports/NN_domain/NNN-slug.md` and fill it in. Delete sections
> that genuinely do not apply — but say why you deleted them rather than removing
> them silently. **Then write the ≤2-page summary**; the report is not finished
> without it.
>
> **What to add over time:** Add sections that repeatedly turn out to be
> necessary. Do not add sections that merely feel thorough.

---
---

# [Title]

| Field | Value |
| --- | --- |
| **Report ID** | `NNN-slug` |
| **Domain** | `NN_domain_name` |
| **Stage** | Analyst |
| **Author** | |
| **Date** | YYYY-MM-DD |
| **Status** | Draft / In review / Accepted / Superseded |
| **Summary** | `docs/research/summaries/NNN-slug.md` |
| **Supersedes** | — |
| **Related decisions** | DEC-NNN, … |

---

## Objective

What this report is trying to determine, in two or three sentences. State the
decision this research is meant to enable — research that does not enable a
decision should not be happening.

## Research Questions

The specific questions this report answers. Numbered, concrete, answerable.

1.
2.
3.

## Existing Solutions

What already exists in this space. Include approaches that failed or were
abandoned — knowing something was tried and did not work saves the next person
from trying it.

| Solution | Type | Tigrinya support | Licence | Maintained | Notes |
| --- | --- | --- | --- | --- | --- |
| | | | | | |

## Papers

Academic work relevant to this question. Prioritise work on low-resource
languages, Semitic and Ethio-Semitic languages, and Ge'ez-script languages, which
is far more likely to transfer than general high-resource-language work.

| Paper | Year | Relevance | Key finding | Link |
| --- | --- | --- | --- | --- |
| | | | | |

## Open Source Projects

| Project | Stars / activity | Licence | Last release | Relevance | Risk |
| --- | --- | --- | --- | --- | --- |
| | | | | | |

Note maintenance signal honestly: last commit date, open issue count, whether
there is more than one maintainer. A single-maintainer project is a dependency
risk regardless of how good the code is.

## Datasets

| Dataset | Size | Language(s) | Licence | Quality | Access | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| | | | | | | |

Record what you looked for and did **not** find. Negative results are findings.

## Alternatives Considered

Every option evaluated, including the ones dismissed quickly. For each: what it
is, what it would give us, and why it did or did not make the shortlist.

### Option A —
### Option B —
### Option C —

## Tradeoffs

The real axes of the decision, and where each option sits on them. A table or
matrix usually beats prose here.

| | Option A | Option B | Option C |
| --- | --- | --- | --- |
| Quality | | | |
| Cost | | | |
| Latency | | | |
| Maintenance | | | |
| Licence risk | | | |
| Integration effort | | | |

## Cost Analysis

Money, compute, storage, and human time. Both **initial** and **ongoing**. Show
the arithmetic and state assumptions so someone can check and update it.

| Item | One-time | Monthly | Assumptions |
| --- | --- | --- | --- |
| | | | |

Include the cost of the option we are *not* choosing, so the comparison is real.
Cost at realistic low volume matters more here than cost at scale — see the
operating-cost priority in `PROJECT_CONTEXT.md`.

## Build vs Buy Decision

Given the reuse-first philosophy: what do we take off the shelf, what do we
adapt, what do we build, and what do we decline to do at all? Justify anything
in the "build" column — the burden of proof sits there, not in "reuse".

## Recommended Approach

A clear position. State confidence (high / medium / low) and what evidence would
change it. If the answer genuinely depends on something undecided, say what it
depends on and recommend for each branch.

## Implementation Plan

Concrete enough to act on. Steps, sequence, dependencies, rough effort, and what
"done" looks like.

1.
2.
3.

**Effort estimate:**
**Blocked by:**
**Unblocks:**

## Risks

| Risk | Likelihood | Impact | Mitigation |
| --- | --- | --- | --- |
| | | | |

Consider low-resource-language-specific risks: data scarcity, evaluation
validity, script and encoding handling, dialectal variation, and benchmark
contamination.

## Open Questions

What this report could not resolve, and what it would take to resolve it.

## References

Numbered, linked, dated. Add these to `docs/research/references/` as well.

1.
2.

---

## Checklist

- [ ] **What exists?**
- [ ] **What can be reused?**
- [ ] **What should be built?**
- [ ] **What should not be built?**
- [ ] **Cost estimate?**
- [ ] **Maintenance burden?**
- [ ] **Licensing?**
- [ ] **Technical risks?**
- [ ] **Final recommendation?**

---

## Completion

- [ ] All nine checklist questions answered
- [ ] ≤2-page summary written to `docs/research/summaries/NNN-slug.md`
- [ ] References added to `docs/research/references/`
- [ ] Rejected options logged in `docs/decisions/rejected_options.md`
- [ ] New assumptions logged in `docs/decisions/assumptions.md`
- [ ] Decision recorded in `docs/decisions/DECISIONS.md`, or explicitly deferred
