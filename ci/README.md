# CI

## Purpose of this directory

Holds `verify.yml`, the workflow that enforces the machine-checkable rules in
`docs/decisions/DECISIONS.md` (**DEC-018**).

## ⚠️ Not active yet — one step required

**This workflow is written and locally verified, but it is NOT RUNNING.**

The session that authored it could not push to `.github/workflows/`: GitHub
refuses workflow files from an app token without `workflows` permission —

```
refusing to allow a GitHub App to create or update workflow
`.github/workflows/verify.yml` without `workflows` permission
```

**To activate it**, someone with normal repository write access runs:

```bash
mkdir -p .github/workflows
git mv ci/verify.yml .github/workflows/verify.yml
git commit -m "Activate CI verification workflow (DEC-018)"
git push
```

Tracked as **A-15** in [`../ACTIONS.md`](../ACTIONS.md).

**Until that happens, DEC-018 is policy without mechanism** — which is precisely
the failure DEC-018 exists to prevent, so the gap is recorded loudly rather than
left to be discovered later.

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

All six checks were run by hand before commit, 2026-08-03:

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
