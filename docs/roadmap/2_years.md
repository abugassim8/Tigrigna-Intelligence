# Roadmap — 2 Years

## Purpose of this document

The long horizon: what this project could become, and what would make it matter.

**Why it exists:** Not for planning — two-year plans made before any research are
fiction, and treating them otherwise leads to commitments nobody can keep. It
exists to state the ambition clearly enough that near-term decisions can be
checked against it. When choosing between two options today, "which of these
leads somewhere worth being in two years?" is a legitimate tiebreaker.

**How to use it:** As a direction check, never as a plan. If work today is
incompatible with everything described here, that is worth noticing.

**What future contributors should add:** Rewrite this once the platform is real.
Until then it is a statement of intent.

> **Horizon: 2026-07-29 → 2028-07-29**
> **Confidence: none, and deliberately so.** This is ambition, not forecast.

---

## The ambition

**That building something in Tigrinya stops being a research project.**

Today, anyone wanting to build a Tigrinya application must first solve
computational linguistics — find data, handle the script, deal with morphology,
build evaluation, train or adapt models. Almost nobody has the time or expertise,
so almost nothing gets built.

The two-year ambition is that this is no longer true. That a developer with an
idea can install an SDK, call an API, and build the thing they actually wanted to
build.

---

## What that requires

**Capability coverage.** Enough of the scoped capabilities working well enough to
build on. Not all of them, and not perfectly — enough.

**Trustworthiness.** Quality that is measured, documented, and honest about its
limits. Infrastructure people can rely on because they know exactly what it does
and does not do.

**Durability.** The platform survives changes in maintainers, funding, and the
model landscape. Nothing built on it breaks because we changed our minds.

**Sustainability.** A funding and governance model that keeps it alive without
depending on anyone's spare time.

**Ecosystem contribution.** Datasets, evaluation sets, and tools released
publicly, raising the floor for everyone working on Tigrinya — not just for us
(**G-11**). A low-resource language ecosystem is not zero-sum.

---

## What would represent real success

Not metrics — outcomes.

- **Applications exist that could not have existed before.** Somebody built
  something useful, and this platform is why it was feasible.
- **The evaluation sets became a standard.** Other researchers use them to
  measure Tigrinya systems. This is plausibly the most durable contribution
  available to us — a good evaluation set outlives every model.
- **The data foundation is a public good.** Documented, licensed, reusable.
- **Other people maintain parts of it.** The project outgrew its founders.
- **The approach transfers.** What we learned about building infrastructure for a
  low-resource language helps someone do it for another one.

That last point may be the most valuable outcome of all. Tigrinya is one of many
languages in this position. A well-documented, honestly-evaluated,
affordably-operated example of how to build this layer is worth more than the
platform itself.

---

## What would represent failure

Worth naming, because these are the plausible failure modes rather than dramatic
ones:

- **A wide platform where nothing works well.** Twelve capabilities, all
  mediocre, none trusted.
- **Impressive claims, unmeasurable quality.** Benchmark numbers with no
  Tigrinya-specific validity behind them.
- **Unmaintainable complexity.** More components than the team can keep alive.
- **Abandoned.** Funding or attention ran out and people who built on it were
  stranded.
- **Nobody used it.** Technically fine, practically irrelevant.

Each of these is reached by a series of individually reasonable decisions, which
is what makes them worth writing down in advance.

---

## Things that could change everything

Honest acknowledgement that two years is long enough for the ground to move:

- General multilingual models improve enough that much of this is unnecessary for
  some capabilities. **This would be good news**, and the reuse-first philosophy
  means we would adopt it rather than defend our own work — a project that
  cannot accept being made partly obsolete will make bad decisions to avoid it.
- A significant Tigrinya data source becomes available, changing what is
  feasible.
- Another project solves part of this well, and the right move is to use theirs
  and narrow ours.
- Institutional funding or partnership changes the achievable scope.
- Community contribution grows past the founding team.

**We should want to be made partly obsolete.** The mission is that Tigrinya
speakers have good language technology — not that we are the ones who built it.

---

## Directional check

When facing a choice today, ask: does this lead toward a platform that is
trustworthy, durable, sustainable, and actually used — or toward one that is
broad, impressive-sounding, and fragile?

That is the only planning value this document has, and it is enough.
