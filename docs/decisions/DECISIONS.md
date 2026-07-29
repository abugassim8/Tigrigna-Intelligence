# Decisions

## Purpose of this document

This is the authoritative log of every significant technical and strategic
decision made on this project. It is the answer to "why is it built this way?"

**Why it exists:** Undocumented decisions get re-litigated by people who cannot
engage with the original reasoning because they never saw it. Worse, they get
*silently reversed* — someone makes a locally sensible choice that contradicts a
deliberate earlier one, and nobody notices until it is expensive. This file
prevents both.

**How to use it:**
- **Read it before making any recommendation.** This is mandatory for AI
  assistants (see `../research/AI_RESEARCH_RULES.md`) and strongly expected of
  humans.
- Append a record when a choice is made that would be expensive to reverse or
  that someone would otherwise re-argue.
- Use the format below, from `../research/templates/decision_template.md`.

**What future contributors should add:** One record per decision, in sequence.
Do not batch several decisions into one record — they will need to be superseded
independently.

---

## Rules

1. **Append-only.** To change a decision, write a new record that supersedes it
   and mark the old one `Superseded by DEC-NNN`. Never edit or delete history —
   the record of a decision that turned out badly is more valuable than the
   record of one that went well.
2. **Sequential IDs.** `DEC-001`, `DEC-002`, … Never reuse, never renumber.
3. **Every decision names its rejected alternatives.** Log them in
   [`rejected_options.md`](rejected_options.md) too.
4. **Every decision links its evidence.** A decision with no link to research is
   a preference; label it as one rather than dressing it up.
5. **Every decision states its consequences honestly**, including the negative
   ones and what it forecloses.

---

## Record format

```
Decision ID:
Date:
Decision:
Context:
Options:
Chosen:
Reason:
Consequences:
```

Expanded records may add **Status**, **Evidence**, **Revisit when**, and
**Related**. See `../research/templates/decision_template.md`.

---

## Index

| ID | Date | Decision | Status |
| --- | --- | --- | --- |
| DEC-001 | 2026-07-29 | Adopt a research-first repository and decision-log workflow | Accepted |

---

## DEC-001 — Adopt a research-first repository and decision-log workflow

**Decision ID:** DEC-001

**Date:** 2026-07-29

**Status:** Accepted

**Decision:**
The project will run on a documented research operating system
(Scout → Analyst → Architect) with a mandatory decision log, compressed
summaries, and a strict separation between research, decisions, experimentation,
and production design. The workspace is built before research begins.

**Context:**
This project has a very wide capability scope — translation, retrieval,
embeddings, morphology, NER, knowledge graph, RAG, APIs, MCP, SDKs — for a
low-resource language where authoritative information is scarce and scattered.
Much of the research will be conducted across many separate sessions, including
AI-assisted sessions that begin with no memory of prior work. Without a
structure that makes prior findings cheap to reload, each session would
re-derive the same conclusions at significant cost, and contradictory decisions
would accumulate unnoticed.

**Options:**

| Option | Summary | Pros | Cons |
| --- | --- | --- | --- |
| A | Structured research OS with decision log, templates, and mandatory summaries | Findings are durable and cheap to reload; decisions are traceable; contradictions surface early | Upfront setup cost; ongoing documentation discipline required |
| B | Ad-hoc notes; document once the design settles | No upfront cost; feels faster early | Findings get lost; research is repeated; decisions become archaeology; the "settle" point never arrives |
| C | Full formal process (RFCs, review gates, sign-off) | Maximum rigour | Far too heavy for current team size; process would be abandoned within weeks |

**Chosen:** Option A.

**Reason:**
The dominant cost in a project of this shape is not computation or even
engineering — it is repeatedly rediscovering things that were already known.
Option A targets that cost directly at modest ongoing expense. Option B fails
precisely when the project gets interesting, because that is when the volume of
findings exceeds what anyone can hold in their head. Option C imposes
coordination overhead that a project at this stage cannot absorb and would
therefore be quietly abandoned, leaving us at Option B with extra steps.

The two-page summary limit and the summaries-before-reports read order are the
load-bearing parts of this decision, not incidental details: they are what make
the accumulated research affordable to consult.

**Consequences:**

- *Positive:* Research findings survive across sessions and contributors.
  Decisions are traceable to evidence. Rejected options stay rejected.
  Contradictions surface at review rather than in production.
- *Negative:* Every research effort carries a documentation tax — the report is
  not done until the summary is written. Some contributors will find this
  slower.
- *Accepted tradeoff:* We spend time on documentation infrastructure before
  producing any technical output. This is deliberate.
- *Newly constrained:* Code cannot land in `services/` without a corresponding
  decision record; capabilities cannot be built before their evaluation method
  exists.
- *Revisit when:* Documentation overhead is demonstrably slowing delivery
  without a corresponding reduction in repeated work, or the team grows past the
  point where an append-only flat file is workable.

**Evidence:**
None — this is a process decision made on judgement, not a research finding. It
is recorded here so that the reasoning is visible and so the process itself can
be challenged on evidence later.

**Related:** `../research/README.md`, `../research/AI_RESEARCH_RULES.md`,
`assumptions.md`

---

<!--
Append new decisions below this line. Copy the format from
../research/templates/decision_template.md and update the Index table above.
-->
