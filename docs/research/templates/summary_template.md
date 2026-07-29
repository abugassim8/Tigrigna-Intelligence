# Summary Template

> **About this template — read this part carefully.**
>
> **Purpose:** To compress research into something a future session can absorb in
> two minutes instead of forty.
>
> **Why it exists:** This is the most important template in the repository. Full
> reports are the evidence record, but almost nobody will read them — not the
> next contributor, and certainly not the next AI session with a finite context
> budget. **The summary is the artefact that actually gets read.** If the summary
> is bad, the research effectively did not happen.
>
> **How to use it:** Write it *after* the report, but write it as though the
> report will never be opened again. Lead with conclusions. Keep every number
> that matters and discard every sentence that does not change what someone
> would do.
>
> **Hard limit: 2 pages.** Roughly 800–1000 words. This constraint is the point,
> not an inconvenience — if it does not fit, you have not finished compressing.
> A summary that runs long is a second report, and it will go unread exactly like
> the first one.
>
> **What to add over time:** Nothing structural. Resist adding sections; every
> one added costs the compression that makes this work.

---
---

# Summary: [Title]

| Field | Value |
| --- | --- |
| **Summary ID** | `NNN-slug` |
| **Full report** | `docs/research/reports/NN_domain/NNN-slug.md` |
| **Stage** | Scout / Analyst |
| **Date** | YYYY-MM-DD |
| **Status** | Current / Superseded by `NNN-slug` |
| **Confidence** | High / Medium / Low |

**One-line answer:** _[The single sentence someone should walk away with.]_

---

## Key Findings

The 3–7 things that matter. Each one a bullet, each one concrete. If a finding
does not change what someone would do, it does not belong here.

-
-
-

Mark each finding's evidential status where it is not obvious:
`[verified]` — checked against a source this session ·
`[reported]` — claimed by a source, not independently checked ·
`[unverified]` — plausible, from background knowledge, not confirmed.

## Important Decisions

Decisions this research produced or directly enables. Link the decision record.

| Decision | ID | Status |
| --- | --- | --- |
| | DEC-NNN | Recorded / Proposed / Deferred |

If this research produced no decision, say so and say what is blocking one.

## Rejected Alternatives

**Do not skip this section.** It is what stops the same option being proposed
again in three months. One line each: what it was, why it lost.

| Alternative | Rejected because |
| --- | --- |
| | |

## Important Numbers

Every figure worth remembering, in one place, with units and sources. Cost,
latency, accuracy, dataset size, parameter count, throughput. This section is
what makes the summary reusable without reopening the report.

| Metric | Value | Source / basis |
| --- | --- | --- |
| | | |

## Recommended Next Steps

Concrete and actionable. Who or what stage picks this up next.

1.
2.
3.

## References

The 3–10 sources that actually mattered. Not the full bibliography — that lives
in the report and in `docs/research/references/`.

1.
2.

---

**Open questions / uncertainty:** _What this research could not settle. Be
explicit — an honest gap here is worth more than a smoothed-over conclusion._
