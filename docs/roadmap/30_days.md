# Roadmap — 30 Days

## Purpose of this document

The near-term plan: what happens in the first month.

**Why it exists:** The shortest horizon is the only one that can be genuinely
concrete before research has been done. It exists to make the immediate next
steps unambiguous, so that work starts rather than being planned.

**How to use it:** This is the working plan. Check it at the start of a session
to see what is next. Update it as items complete.

**What future contributors should add:** Keep it current. Move completed items
out, pull items in from `90_days.md` as capacity allows. When an item turns out
to be larger than expected, say so rather than letting it silently slip.

> **Horizon: 2026-07-29 → 2026-08-28**

---

## The one thing this month is for

**Establishing what is actually true about Tigrinya language technology today.**

Everything else is downstream of that. No architecture, no model selection, no
implementation — those are decisions that require evidence we do not yet have.

---

## Committed

### Week 0 — Workspace ✅
- [x] Repository structure and research operating system
- [x] Vision, principles, non-goals documented
- [x] Decision log, assumptions register, and templates in place

### Weeks 1–2 — Project definition (`00_project_definition`)

The questions here are gating and cannot be deferred, because several currently
sit open in `assumptions.md` and block work elsewhere.

- [ ] **Scout:** who the users are and what they need — developers, researchers,
      institutions, product teams. Resolves an open item in `assumptions.md`.
- [ ] **Scout:** what each scoped capability means concretely, and what "working"
      would look like for each.
- [ ] **Analyst:** minimum useful platform — the smallest thing genuinely
      valuable to someone.
- [ ] **Analyst:** dialect, register, and orthographic scope. Blocks data
      collection design.
- [ ] **Architect:** record decisions; update `assumptions.md`.

### Weeks 2–4 — Ecosystem scan (`01_ecosystem`)

- [ ] **Scout:** existing Tigrinya language technology — what exists, what works,
      what was abandoned.
- [ ] **Scout:** research groups, communities, and individuals in Tigrinya and
      Ethio-Semitic NLP.
- [ ] **Scout:** what Amharic and adjacent ecosystems have that could transfer.
- [ ] **Analyst:** gap analysis — what is genuinely missing.
- [ ] Populate `docs/research/references/` throughout.

### Ongoing

- [ ] Every research effort produces a ≤2-page summary. No exceptions.
- [ ] Every decision recorded, with rejected alternatives.
- [ ] `references/` grows continuously, not at the end.

---

## Explicitly not this month

- No architecture design.
- No model selection or recommendation.
- No code in `services/`.
- No training of anything.
- No infrastructure provisioning.

These are not neglect; they are gated on research that has not happened. Starting
them now would mean building on assumptions rather than evidence.

---

## Success criteria for the month

By 2026-08-28:

1. The open scope questions in `assumptions.md` are closed, or we know precisely
   what is blocking them.
2. We have a defensible map of what Tigrinya language technology exists today.
3. `references/` is a genuinely useful starting point rather than an empty
   directory.
4. At least three decisions are recorded with evidence.
5. Every piece of research done has a summary that someone could act on without
   reading the source report.

## Risks this month

| Risk | Mitigation |
| --- | --- |
| Research sprawls without producing decisions | Every Analyst report must reach the Architect stage or state explicitly what blocks it |
| Scope drifts toward implementation because building is more fun than researching | Non-goals and the "explicitly not this month" list above |
| Summaries skipped under time pressure | A report without a summary is not accepted in review |
| Ecosystem scan finds very little and stalls | Negative results are results (**P-13**) — record and move on |
