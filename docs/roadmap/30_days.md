# Roadmap — 30 Days

> ⚠️ **Superseded as a plan, kept as a record.** This was written **before any
> research** — in the project's first days. All 13 research domains are now complete, two packages are
> built, and **[`READINESS_PLAN.md`](READINESS_PLAN.md) is the plan of record.**
>
> **Its blocking items are still blocking**, which is the finding: `fgaim` licences (**A-01**), HornMorpho (**A-07**), confirming DEC-002 (**A-02**) and egress (**A-09**) were open on day one and are open now. They were never engineering problems.

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

### Weeks 1–2 — Project definition (`00_project_definition`) ✅

Completed 2026-07-29 — `reports/00_project_definition/001-scope-users-and-dialect.md`,
summary `002-scope-users-and-dialect.md`.

- [x] **Scout:** who the users are → **DEC-002 (Proposed)**: application
      developers primary, researchers secondary. *Needs owner confirmation.*
- [x] **Analyst:** minimum useful platform → **DEC-006**: primitives +
      embeddings + evaluation harness. Translation explicitly excluded.
- [x] **Analyst:** dialect scope → **DEC-004**: both varieties, evaluated and
      reported separately, on measured evidence (COMET 0.82 vs 0.80).
- [x] **Architect:** decisions recorded; `assumptions.md` updated.
- [ ] **Deferred:** register scope — data exists at both extremes but nothing
      characterises the distance between them. → `02_linguistics`.
- [ ] **Deferred:** per-capability definition of "working" — folded into
      `08_evaluation`, since it is an evaluation-design question.

### Weeks 2–4 — Ecosystem scan (`01_ecosystem`) ✅

Completed 2026-07-29 — `reports/01_ecosystem/001-tigrinya-nlp-ecosystem-scan.md`,
summary `001-tigrinya-nlp-ecosystem-scan.md`.

- [x] **Scout:** existing Tigrinya language technology mapped — GeezLab stack,
      community models, HornMorpho, consumer keyboards.
- [x] **Scout:** research groups and individuals identified — GeezLab/`fgaim`,
      Hailay Teklehaymanot (L3S Hannover), HLTDI, ~12 HF contributors.
- [x] **Scout:** adjacent-ecosystem transfer — Amharic parallel data, AfroXLM-R,
      MoVoC covering four Ge'ez-script languages.
- [x] **Analyst:** gap analysis → **DEC-003**. The gaps are Layer 0 (primitives)
      and Layer 5 (API/MCP/SDK), not the model layer.
- [x] `docs/research/references/` populated: papers, models, datasets, projects,
      communities, commercial.

### Ongoing

- [x] Every research effort produces a ≤2-page summary. No exceptions.
- [x] Every decision recorded, with rejected alternatives (DEC-002…006;
      R-004…R-012).
- [x] `references/` grows continuously, not at the end.

---

## Remaining this month — the blocking items

Phase 1 surfaced three concrete blockers. These now take priority over starting
Phase 2:

- [ ] **Resolve licensing on the `fgaim` models.** `tiroberta-base` and family
      carry no stated licence. Under **P-9**/**A-009** this blocks DEC-003, the
      core reuse plan. *Contact the author.* **Highest priority.**
- [ ] **Verify HornMorpho is maintained.** It is the only established Tigrinya
      morphological analyser and DEC-006 puts morphology on the critical path.
      GitHub was unreachable this session.
- [ ] **Confirm DEC-002 with the project owner** — the user determination is
      inferential and is the one decision awaiting sign-off.
- [ ] **Locate and licence-check** TLMD, NTC, TiNC24, FLORES-200 Tigrinya split,
      and the MoVoC morpheme data.
- [ ] **Re-verify `[reported]` figures** against primary sources if egress allows.

---

## Explicitly not this month

- No architecture design.
- No **final** model selection. *(Amended 2026-07-29: DEC-003 records a
  reuse-first posture and a shortlist of candidates. It does not select a served
  model — that is gated on `04_model_strategy` and on the evaluation harness
  existing, per **P-4**.)*
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
