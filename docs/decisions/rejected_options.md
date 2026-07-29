# Rejected Options

## Purpose of this document

A running log of options that were considered and **not** chosen, with the
reason each was rejected.

**Why it exists:** Rejected options come back. Someone — a new contributor, a
new AI session, or you in six months — proposes an approach that was already
evaluated and dismissed for good reasons, and the whole evaluation happens
again. This file is the cheapest possible defence against that.

It also serves a second purpose: rejection reasons expire. An option rejected
because "no Tigrinya support exists" may become viable when support appears. By
recording *why* something was rejected, we make it possible to notice when the
reason no longer holds — rather than treating the rejection as permanent.

**How to use it:**
- **Check here before proposing anything.** If your idea is listed, either
  engage with the recorded reason or explain what has changed.
- Add a row whenever a decision is recorded, covering every alternative that
  lost.
- If a rejection reason stops being true, do not delete the row — add a note and
  raise it for reconsideration.

**What future contributors should add:** Every rejected alternative from every
decision, plus options that were considered informally and dropped before
reaching a formal decision. The informal ones are the most likely to return.

---

## How to write a good rejection reason

Bad: *"Not a good fit."*
Good: *"Requires a GPU always-on to serve, which costs ~$250/month at our
volume — roughly 10× the CPU-served alternative for a quality gain we could not
measure on Tigrinya."*

The test: could someone who has never seen this option decide, from your reason
alone, whether the rejection still applies today? If not, the reason is too
thin.

---

## Rejected options log

| ID | Option | Context | Rejected because | Decision | Date | Revisit if |
| --- | --- | --- | --- | --- | --- | --- |
| R-001 | Ad-hoc research notes, no formal structure | Choosing how to run project research | Findings do not survive across sessions; research gets repeated; decisions become unrecoverable archaeology. The point at which "we'll document it once it settles" pays off never arrives. | DEC-001 | 2026-07-29 | Never — the failure mode is structural |
| R-002 | Full formal RFC process with review gates and sign-off | Choosing how to run project research | Coordination overhead exceeds what a project at this stage can absorb; a process this heavy would be abandoned within weeks, landing us at R-001 with extra steps. | DEC-001 | 2026-07-29 | Team grows to the point where informal review stops catching contradictions |
| R-003 | Nesting the project under a `tigrinya-language-intelligence/` subdirectory | Laying out the repository | The repository *is* the project; a same-named folder inside it adds a redundant path segment to every reference for no benefit. | — | 2026-07-29 | The repository ever hosts a second, genuinely separate project |

---

<!--
Add rejected options above this line. Every decision in DECISIONS.md should
contribute at least one row — a decision with no rejected alternatives usually
means the alternatives were not actually explored.
-->
