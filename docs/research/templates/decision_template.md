# Decision Template

> **About this template**
>
> **Purpose:** The standard format for a decision record (ADR). Every entry in
> `docs/decisions/DECISIONS.md` uses this shape.
>
> **Why it exists:** Decisions made without a written record get re-litigated —
> usually by someone who does not know the original reasoning and therefore
> cannot engage with it. A decision record is a message to whoever next wonders
> "why on earth did they do it this way?" The `Context` and `Reason` fields are
> the ones that answer that question, so they get the most care.
>
> **How to use it:** Copy the block below, assign the next sequential ID, append
> it to `DECISIONS.md`. **Decisions are append-only** — to change one, write a
> new record that supersedes it and mark the old one superseded. Never edit the
> history.
>
> **What to add over time:** Keep the format stable. Consistency is what makes
> the file scannable at fifty entries.

---
---

## DEC-NNN — [Short decision title]

**Decision ID:** DEC-NNN

**Date:** YYYY-MM-DD

**Status:** Proposed / Accepted / Superseded by DEC-NNN / Deprecated

**Decision:**
One or two sentences stating what was decided, in the active voice. A reader
should get the answer here without reading further.

**Context:**
What situation forced this decision. What constraints applied. What was known
and unknown at the time. This is the field that ages best — write it for someone
who has none of your current context.

**Options:**
Every option seriously considered, including doing nothing.

| Option | Summary | Pros | Cons |
| --- | --- | --- | --- |
| A | | | |
| B | | | |
| C — do nothing | | | |

**Chosen:**
Which option, stated unambiguously.

**Reason:**
Why this option beat the others. Tie back to the project's priority order —
data quality → evaluation → reproducibility → low operating cost →
maintainability — where relevant. If the decision was a close call, say so; if
it was forced by a constraint, name the constraint.

**Consequences:**
What follows from this. Be honest about the costs, not just the benefits.

- *Positive:*
- *Negative:*
- *Neutral / accepted tradeoff:*
- *Newly constrained:* what this decision now makes harder or forecloses.
- *Revisit when:* the condition or date that should trigger reconsideration.

**Evidence:**
Links to the research that supports this — reports, summaries, experiments,
benchmarks. A decision with no evidence link is a preference, and should be
labelled as one.

**Related:** DEC-NNN, `docs/research/summaries/NNN-slug.md`

---
---

## Compact form for `DECISIONS.md`

For decisions where the full form is overkill, the minimum viable record is:

```markdown
## DEC-NNN — [Title]

**Date:** YYYY-MM-DD · **Status:** Accepted

**Decision:**

**Context:**

**Options:**

**Chosen:**

**Reason:**

**Consequences:**
```

Never drop below this. The seven fields are the record; anything less is a note.
