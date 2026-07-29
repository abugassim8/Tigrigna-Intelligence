# Assumptions

## Purpose of this document

A register of the things this project takes as given — the beliefs that shape
decisions but have not themselves been proven.

**Why it exists:** Every project runs on assumptions. The dangerous ones are the
invisible ones: beliefs so embedded that nobody notices they are beliefs, which
therefore never get tested even when evidence starts contradicting them. Writing
them down converts an invisible assumption into a testable claim.

**How to use it:**
- Read this before making recommendations. Treat it as **a list of things that
  might be wrong**, not a list of things that are true.
- **Challenge these.** If you find evidence contradicting an assumption, say so
  prominently. An assumption overturned by evidence is a good outcome, not an
  embarrassment.
- Add new assumptions as you notice yourself relying on them.

**What future contributors should add:** New assumptions as they surface — and,
just as importantly, updates to the status of existing ones as evidence arrives.
An assumption that has been validated should say so and link the evidence.

---

## Status values

| Status | Meaning |
| --- | --- |
| **Unvalidated** | Believed, not tested. Default for new entries. |
| **Supported** | Evidence gathered that supports it; linked. |
| **Contested** | Evidence exists on both sides; needs resolution. |
| **Invalidated** | Shown to be false. Kept in the register with what replaced it. |

---

## Standing assumptions

### A-001 — We prefer open source before commercial APIs

**Status:** Unvalidated · **Confidence:** High · **Since:** 2026-07-29

Open models and open source tooling are preferred over commercial APIs where
they are viable. Rationale: cost control at low volume, no vendor deprecation
risk, the ability to inspect and adapt behaviour, and the ability to run without
sending data to third parties.

*This is a preference, not an absolute.* A commercial API that is dramatically
better for a capability we cannot otherwise deliver should be evaluated on its
merits, and rejecting it reflexively would violate the reuse-first philosophy.

**Would be invalidated by:** open options proving unusable for Tigrinya
specifically, or total cost of self-hosting exceeding API cost at our realistic
volume.

---

### A-002 — We optimize for low-resource language capability

**Status:** Unvalidated · **Confidence:** High · **Since:** 2026-07-29

Techniques, models, and architectures are selected for how well they work under
data scarcity — not for how well they perform on high-resource benchmarks. A
method that is state-of-the-art with 10M training examples is irrelevant to us
if we have 50k.

**Implication:** multilingual benchmark averages are near-worthless as evidence
here. What matters is Tigrinya-specific performance, and where that is
unavailable, performance on Ge'ez-script or Ethio-Semitic languages as the
nearest proxy.

**Would be invalidated by:** discovering Tigrinya data resources far larger than
currently expected.

---

### A-003 — We prioritize accuracy over speed

**Status:** Unvalidated · **Confidence:** Medium · **Since:** 2026-07-29

Where the two conflict, correctness wins. A wrong translation returned in 50ms
is worse than a right one in 500ms — for infrastructure that others build on,
errors propagate into every downstream product.

*Bounded:* this holds within reason. An approach that is marginally more
accurate and 100× slower fails the operating-cost priority. Specific latency
budgets are a per-service decision, not a global one.

**Would be invalidated by:** a target use case with a hard real-time
requirement.

---

### A-004 — We avoid unnecessary model training

**Status:** Unvalidated · **Confidence:** High · **Since:** 2026-07-29

Training is a last resort, not a first instinct. It carries data cost, compute
cost, evaluation cost, and permanent maintenance burden — a trained model is
something we must keep alive, re-evaluate, and eventually retrain.

The default answer to "should we train this?" is **no**. The burden of proof
sits with whoever proposes training, and the proposal must articulate the
proprietary advantage created and cost the alternative of not training.

**Would be invalidated by:** finding that no existing model handles Tigrinya
adequately for a core capability — which is a plausible outcome, and exactly the
case where training becomes justified.

---

### A-005 — Fine-tuning and adaptation are preferred over training from scratch

**Status:** Unvalidated · **Confidence:** High · **Since:** 2026-07-29

Where model work is genuinely required, adapting an existing model is preferred
over training from scratch. Corollary of A-004 and the reuse-first philosophy.

**Would be invalidated by:** a fundamental incompatibility between available
base models and Tigrinya's script or morphology that adaptation cannot bridge.

---

### A-006 — Tigrinya-specific evaluation data is scarce and will need to be built

**Status:** Unvalidated · **Confidence:** Medium · **Since:** 2026-07-29

We assume there is little high-quality Tigrinya evaluation data, and that
building trustworthy test sets will be a significant, unavoidable workstream
rather than a preliminary step.

**Flagged as high-impact:** if true, this affects sequencing across the entire
project — it means evaluation work starts early and is a first-class deliverable,
not a phase-two concern. This should be among the first things Phase 1 research
tests.

---

### A-007 — Morphological complexity is a first-order design constraint

**Status:** Unvalidated · **Confidence:** Medium · **Since:** 2026-07-29

We assume Tigrinya's morphology materially affects tokenization, retrieval,
embeddings, and search quality — and that approaches designed around
analytic languages will underperform without adaptation.

**Explicitly flagged for verification.** This assumption is currently based on
general knowledge of Ethio-Semitic languages, not on research conducted for this
project. It sits upstream of several architectural choices, which makes it both
high-impact and, right now, insufficiently evidenced. `02_linguistics` should
resolve it early.

---

### A-008 — The platform must be affordable to run at low volume

**Status:** Unvalidated · **Confidence:** High · **Since:** 2026-07-29

We assume usage grows slowly and that the platform must be economically
sustainable at low request volumes for an extended period. Architectures that
only make economic sense at scale we do not have are rejected.

**Would be invalidated by:** funding or adoption arriving far faster than
expected.

---

### A-009 — Licensing and provenance must be verifiable for everything we adopt

**Status:** Unvalidated · **Confidence:** High · **Since:** 2026-07-29

We assume that unclear licensing is disqualifying. As infrastructure that others
will build on, we cannot pass on rights we do not have — a downstream user
inheriting a licensing problem from us is a serious failure, not an inconvenience.

**Would be invalidated by:** nothing foreseeable. This is close to a hard
constraint.

---

## Assumptions we have deliberately not yet made

Recorded so nobody mistakes silence for a decision:

- **Target users.** Whether this primarily serves developers, researchers,
  institutions, or end-user products is **open**. It is a `00_project_definition`
  question and it affects API design, SDK priorities, and licensing.
- **Deployment model.** Self-hosted, managed service, or both — **open**.
- **Language pairs.** Which translation directions matter most — **open**.
- **Dialect and register scope.** Which varieties of Tigrinya are in scope —
  **open**, and consequential for data collection.
- **Project licence.** **Open**, deliberately deferred until data and model
  strategy research is complete.

---

<!--
Add new assumptions above, numbered sequentially. When evidence arrives, update
Status and link it. Do not delete invalidated assumptions — record what replaced
them.
-->
