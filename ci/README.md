# CI

## Purpose of this directory

Holds `verify.yml`, the workflow that enforces the machine-checkable rules in
`docs/decisions/DECISIONS.md` (**DEC-018**).

## ⚠️ Not active yet — one step required, and no agent can take it

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

### One defect has already been fixed for you

The `intrinsic` job installed both packages **without** the `[dev]` extra, so
`pytest` was absent — and a step added 2026-09-02 calls `pytest --collect-only`
to verify the readiness plan's test count. **It would have failed on the first
real run.** Now fixed.

It was found by extracting all 28 non-install `run:` blocks from this file and
executing them against the tree — 28 run, 0 failed, every experiment
reproducing byte-identically. That is the closest thing to a runner available
without the push, and it is still **not** the same as a run: nothing here
exercises `actions/checkout`, `actions/setup-python`, a clean `pip install` on
a fresh runner, or network egress from GitHub's network.

## What it checks

| Check | Rule |
| --- | --- |
| `services/primitives` — 61 property tests | **DEC-023** (Tier 0 evaluation) |
| `services/evaluation` — 14 harness tests | **DEC-009**, **DEC-010** |
| Every experiment re-runs and diffs byte-identically | **DEC-016** |
| Screening fails closed with no licence / no eval set | **DEC-015** |
| The known-corrupted corpus still fails the quality gate | **DEC-015** |
| Every research report has a corresponding summary | **DEC-001** |
| Summaries stay within the two-page limit | **DEC-001** |
| Every decision names its rejected alternatives | `CONTRIBUTING.md` |

## Verified locally

All six checks were run by hand before commit, 2026-08-17:

- 61 primitives tests and 14 evaluation tests passed
- 4 experiments reproduced byte-identically
- screening correctly failed closed
- the known-corrupted sample was still detected
- 10 summaries under the word limit
- 17 decisions carried rejected alternatives

**CI that does not work is worse than no CI**, so the logic was exercised rather
than assumed. What has *not* happened is a run on a real GitHub Actions runner.

## Note on the reproducibility job

It doubles as a **dependency regression test**. If `epitran`, `tokenizers`, or
`sacrebleu` changes behaviour, an experiment stops reproducing and CI says so.
That is currently the only guard between DEC-007's amended numbers and silent
drift — another reason activation matters.
