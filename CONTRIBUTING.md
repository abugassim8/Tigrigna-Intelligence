# Contributing

## Purpose of this document

This document defines how work enters this repository — research, decisions,
data, and code. It exists so that contributions are *additive* rather than
*entropic*: so that the tenth contributor, and the fiftieth AI research session,
can build on what came before instead of accidentally rediscovering or silently
contradicting it.

**How to use it:** Read the section matching what you are about to contribute.
Follow the checklist at the end before opening a pull request.

**What to add over time:** Add sections as new contribution types appear (data
licensing review, model release process, security disclosure). Tighten rules
that get violated repeatedly — a rule people keep breaking is usually a rule
that is unclear, not a people problem.

---

## Before you contribute anything

Three files, in this order, every time:

1. [`PROJECT_CONTEXT.md`](PROJECT_CONTEXT.md) — what we are building and why.
2. [`docs/decisions/DECISIONS.md`](docs/decisions/DECISIONS.md) — what has
   already been settled.
3. [`docs/decisions/assumptions.md`](docs/decisions/assumptions.md) — what we are
   taking as given, and how confident we are.

If your contribution contradicts something in these files, that is not
automatically a problem — but you must say so explicitly and argue the case.
Silent contradiction is the failure mode we are guarding against.

---

## Contributing research

Research follows the **Scout → Analyst → Architect** protocol defined in
[`docs/research/README.md`](docs/research/README.md).

### Rules

1. **Search before you research.** Check `docs/research/summaries/` and
   `docs/research/references/` first. Duplicated research is the most expensive
   mistake available in this repository, and for AI sessions it is also the most
   common.
2. **Use the templates.** `docs/research/templates/` — do not invent your own
   structure.
3. **Every full report gets a summary.** A report without a corresponding
   summary in `docs/research/summaries/` is incomplete. The summary is not
   optional documentation; it is the artefact future sessions will actually
   read.
4. **Answer the checklist.** Every report must answer all nine questions in
   [`docs/research/CHECKLIST.md`](docs/research/CHECKLIST.md).
5. **Cite everything.** Claims without sources are opinions. Add sources to
   `docs/research/references/`.
6. **State uncertainty.** "I could not determine X" is a valid and valuable
   research finding. Confident vagueness is not.

### Naming

Reports: `docs/research/reports/NN_domain/NNN-short-slug.md`
e.g. `docs/research/reports/03_data_strategy/001-tigrinya-corpus-survey.md`

Summaries: `docs/research/summaries/NNN-short-slug.md`, matching the report
number where one exists.

---

## Contributing decisions

A decision is recorded when a choice is made that would be expensive to reverse
or that future contributors would otherwise re-litigate.

1. Append to [`docs/decisions/DECISIONS.md`](docs/decisions/DECISIONS.md) using
   the format defined there (`docs/research/templates/decision_template.md`).
2. Record what you *rejected* in
   [`docs/decisions/rejected_options.md`](docs/decisions/rejected_options.md),
   with the reason. Rejected options are as valuable as chosen ones — they stop
   the same idea being proposed every quarter.
3. Assign the next sequential decision ID. Never reuse or renumber IDs.
4. **Decisions are append-only.** To change a decision, write a new one that
   supersedes it and mark the old one `Superseded by DEC-NNN`. Do not edit
   history.

---

## Contributing code

Code contributions are gated on research being complete for the area in
question. If there is no decision record covering the component you want to
build, the decision record is the contribution that is needed first.

### Rules

1. **Decision before code.** Nothing lands in `services/` without a
   corresponding entry in `DECISIONS.md`.
2. **Evaluation before capability.** Before building a capability, there must be
   an agreed way to measure it — see `docs/benchmarks/`. This is the single
   easiest rule to skip and the most expensive one to have skipped.
3. **Services are independent.** Each directory under `services/` must be
   runnable and testable on its own. Cross-service imports are a design smell;
   raise them for discussion.
4. **Experiments stay in `experiments/`.** Exploratory work is welcome and is
   allowed to be messy. It gets promoted into `services/` only after producing a
   result recorded in `models/evaluations/`.
5. **Reproducibility is required.** Pin versions. Seed randomness. Record
   hardware. A result that cannot be reproduced from this repository does not
   exist.
6. **No secrets, ever.** Not in code, not in notebooks, not in config, not in
   commit history. Use `.env` files (git-ignored) and document required variables
   in the relevant `README.md`.

### Data contributions

Data carries obligations that code does not:

- **Licence and provenance are mandatory.** Every dataset added must document
  where it came from, under what licence, and what may be done with it. Undocumented
  data is unusable data — we cannot ship on top of it.
- Raw data is immutable. Transformations produce new artefacts in
  `datasets/processed/`, driven by scripts in `scripts/data_processing/`.
- Large files do not belong in git. Use a pointer file plus a documented
  retrieval script until a storage decision is recorded.
- Evaluation data must be kept strictly separate from training data, with
  contamination checks documented. This is the one form of sloppiness that
  invalidates everything downstream of it.

---

## Commit and branch conventions

- Branch from the current default branch; use descriptive branch names.
- Write commit messages that explain *why*, not just *what*. The diff already
  shows what.
- Keep commits scoped. A commit that adds a dataset, refactors a service, and
  changes a decision record is three commits.
- Update `CHANGELOG.md` for anything that changes project direction, structure,
  or a recorded decision.

---

## Pull request checklist

- [ ] I read `PROJECT_CONTEXT.md`, `DECISIONS.md`, and `assumptions.md`.
- [ ] I searched `docs/research/summaries/` for prior work on this topic.
- [ ] Research contributions use the templates and answer `CHECKLIST.md`.
- [ ] Every full report has a corresponding ≤2-page summary.
- [ ] New decisions are recorded with rejected alternatives.
- [ ] Sources are cited and added to `docs/research/references/`.
- [ ] Uncertainty is stated explicitly rather than smoothed over.
- [ ] No secrets, credentials, or `.env` files are included.
- [ ] Data contributions document licence and provenance.
- [ ] `CHANGELOG.md` updated if project direction or structure changed.

---

## A note on tone in documents

Write for the reader who arrives eighteen months from now with no context and no
patience. Prefer short sentences, concrete numbers, and explicit uncertainty.
Avoid enthusiasm as a substitute for evidence.
