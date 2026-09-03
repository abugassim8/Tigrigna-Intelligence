# CI

## Purpose of this directory

Holds `verify.yml`, the workflow that enforces the machine-checkable rules in
`docs/decisions/DECISIONS.md` (**DEC-018**).

## ⚠️ Not active yet — and no agent can take the step

**This workflow is written and locally verified, but it is NOT RUNNING.**

An agent cannot install it. **Re-tested 2026-09-02 by a session that tried and
failed both available routes**, so nobody has to try a third time:

| Route | Result |
| --- | --- |
| `git push` with the workflow file in the commit | `remote rejected` — *refusing to allow a GitHub App to create or update workflow `.github/workflows/verify.yml` without `workflows` permission* |
| REST contents API (`PUT /repos/.../contents/...`) | **403** `Resource not accessible by integration` |

This is a **token scope**, not a repository setting and not something a retry or
a different phrasing gets around. It needs a human with normal write access.

**To activate it**, run:

```bash
mkdir -p .github/workflows
git mv ci/verify.yml .github/workflows/verify.yml
git commit -m "Activate CI verification workflow (DEC-018)"
git push
```

Then repoint the derived count, or `scripts/check_figures.py` will crash on a
path that no longer exists:

```bash
sed -i 's|"file": "ci/verify.yml"|"file": ".github/workflows/verify.yml"|' docs/figures.json
```

Tracked as **A-15** in [`../ACTIONS.md`](../ACTIONS.md).

**Until that happens, DEC-018 is policy without mechanism** — which is precisely
the failure DEC-018 exists to prevent, so the gap is recorded loudly rather than
left to be discovered later.

### Two defects have already been fixed for you

1. The `intrinsic` job installed both packages **without** the `[dev]` extra, so
   `pytest` was absent — and a step added 2026-09-02 calls `pytest
   --collect-only` to verify the readiness plan's test count. **It would have
   failed on the first real run.**
2. The validation-instrument step was **not re-runnable on one machine**: `cp -r
   src /tmp/v-sheets` nests `src` inside an existing destination, so a second
   local run failed with `Only in /tmp/v-sheets: sheets` — which reads as the
   instrument being non-deterministic when it is not. Harmless on a clean
   runner, actively misleading to anyone debugging locally.

Both were found by extracting all 28 non-install `run:` blocks from this file
and executing them against the tree — 28 run, 0 failed, every experiment
reproducing byte-identically. That is the closest thing to a runner available
without the push, and it is still **not** the same as a run: nothing here
exercises `actions/checkout`, `actions/setup-python`, a clean `pip install` on
a fresh runner, or network egress from GitHub's network.

## What it checks

**28 non-install steps across five jobs.** The count is derived from this
workflow by `docs/figures.json` → `ci_checks`, so adding a step and forgetting
to update the documents fails `scripts/check_figures.py`.

| Job | Enforces |
| --- | --- |
| `packages` | `services/primitives` (**97 tests**) and `services/evaluation` (**64 tests**) — DEC-023, DEC-009, DEC-010 |
| `intrinsic` | Tier 0 intrinsic properties over the committed corpus (DEC-023a); morphology's five checks, and that a SKIP is **not** a pass (DEC-028); the readiness plan's test count |
| `reproducibility` | All **10** experiments re-run and diff byte-identically (DEC-016) |
| `screening` | Screening fails closed; contamination positively detected; every committed corpus carries a record; both anchors match upstream and stay aligned; planted failures still detected (DEC-015, DEC-029) |
| `documentation` | Reports have summaries and stay in budget (DEC-001); no retired figure quoted as current (DEC-024); date stamps match their commits (A-17); no packaged artefact declares HornMorpho (DEC-028); every decision names its rejected alternatives |

## Verified locally — and what that is worth

**2026-09-02:** all **28** non-install `run:` blocks extracted from this file and
executed against the tree — **28 run, 0 failed**, twice in a row, all 10
experiments reproducing byte-identically, 161 tests passing.

⚠️ **That is still not a run.** Nothing local exercises `actions/checkout`,
`actions/setup-python`, a clean `pip install` on a fresh runner, or egress from
GitHub's network. **CI that does not work is worse than no CI**, so the logic is
exercised rather than assumed — but "verified locally" and "verified" are the
distinction this whole file exists to make.

*(The original note here recorded 6 checks, 61 + 14 tests and 4 experiments,
verified by hand on 2026-08-17. Every one of those figures had since drifted —
they are replaced above rather than left standing.)*

## Note on the reproducibility job

It doubles as a **dependency regression test**. If `epitran`, `tokenizers`, or
`sacrebleu` changes behaviour, an experiment stops reproducing and CI says so.
That is currently the only guard between DEC-007's amended numbers and silent
drift — another reason activation matters.
