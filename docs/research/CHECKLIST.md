# Research Phase Checklist

## Purpose of this document

This is the completion bar for research on this project. Every research report
must answer all nine questions below. A report that cannot answer them is not
finished — it is a draft.

**Why it exists:** Research tends to answer the question that is interesting
rather than the questions that are decision-relevant. These nine questions are
the ones that actually determine whether we can act. Making them mandatory keeps
reports useful to the Architect stage rather than merely informative.

**How to use it:** Copy the block below into the bottom of your report and fill
it in. Reviewers check this before accepting a report.

**What future researchers should add:** Add a question when you find that a
decision keeps stalling for want of information the checklist did not require.
Remove one only if it has repeatedly proven to be noise — and record that as a
decision.

---

## The nine questions

Every report must answer:

□ **What exists?**
The current state of the world for this problem. Models, libraries, datasets,
products, papers, standards, prior attempts. Include the ones that are bad or
abandoned — knowing an approach was tried and failed is valuable.

□ **What can be reused?**
Given the core philosophy of reuse-first, what can we take off the shelf as-is
or with light adaptation? Be specific: name the artefact, version, licence, and
what exactly it gives us.

□ **What should be built?**
What genuinely does not exist, or exists but not for Tigrinya, or exists but is
unusable for our purposes. Justify each item — "we should build it" needs a
reason beyond "it would be nice to own."

□ **What should not be built?**
Just as important. What are we explicitly declining to build, and why? This
prevents scope creep and stops the same proposal returning every quarter. Feed
these into `docs/vision/non_goals.md` where they are durable.

□ **Cost estimate?**
Money, compute, storage, and human time — for both initial build and ongoing
operation. Show your arithmetic and state your assumptions so the estimate can
be checked and updated. Ranges are fine; silence is not.

□ **Maintenance burden?**
What does this cost us *forever*? Who maintains it? What happens when the
upstream project is abandoned, the model deprecated, the API changed, the
licence altered? Ongoing burden is routinely underweighted and is often the
deciding factor between two otherwise similar options.

□ **Licensing?**
Licence of every model, dataset, and dependency involved. Can we use it for our
intended purpose? Are there commercial restrictions, share-alike obligations, or
attribution requirements? Is the provenance of the training data itself known?
Unverified licensing is a blocker, not a footnote — we cannot build a platform
others depend on top of rights we do not have.

□ **Technical risks?**
What could go wrong, how likely, how bad, and what would we do about it. Include
risks specific to low-resource languages: data scarcity, evaluation validity,
script and encoding issues, dialectal variation, and benchmark contamination.

□ **Final recommendation?**
A clear, actionable position. Not "it depends" — if it depends, say what it
depends on and give a recommendation for each branch. State your confidence
level and what evidence would change your mind.

---

## Copy this into your report

```markdown
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
```

---

## Additional bars for specific report types

**Data reports** must also answer: provenance, collection method, consent and
ethics where human-sourced, dialect and register coverage, script and encoding
normalisation, and train/eval contamination risk.

**Model reports** must also answer: Tigrinya-specific evaluation evidence (not
just multilingual averages that Tigrinya may not even be in), inference cost per
request, hardware requirements, and quantisation or distillation options.

**Infrastructure reports** must also answer: cost at realistic low volume — not
just at scale — cold-start behaviour, and what the minimum viable deployment
looks like.

**Any report recommending training a model** must additionally justify the
proprietary advantage gained and cost the alternative of *not* training. The
default answer is no; see `PROJECT_CONTEXT.md`.
