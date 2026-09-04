# Pending workflow changes — an agent cannot apply these

## Why this directory exists

Activating CI (**A-15**) moved `verify.yml` into `.github/workflows/`. That was
the right move and it closed GAP-2. It also had a consequence neither party
anticipated:

> ⚠️ **The workflow is now in the one directory an agent cannot write to.**
> Any commit touching `.github/workflows/` is rejected with
> *"refusing to allow a GitHub App to create or update workflow … without
> `workflows` permission"* — the same wall that made A-15 human-only in the
> first place.

**Before activation an agent could edit the workflow freely and could not run
it. After activation it can run it and cannot edit it.** Every future CI fix
therefore needs a human to apply it.

This directory holds patches an agent has prepared and verified but cannot push.

## How to apply one

From a normal clone with write access, on the branch:

```
git pull
git apply ci/pending/fix-first-run-failures.patch
git commit -am "Apply pending CI workflow fix"
git push
```

Then delete the patch file in a follow-up commit once CI is green — a stale
patch that has already been applied is worse than none, because the next person
will try to apply it again.

`git apply` works identically in Windows CMD, PowerShell, macOS and Linux.

## What is pending now

| Patch | Fixes |
| --- | --- |
| `fix-first-run-failures.patch` | The three failures from CI's first-ever run (2026-09-04), plus the duplicate-run trigger |

**All four changes are verified locally** — the definition-based rule finds all
28 decisions and flags none, and both plant directions behave. What cannot be
verified without applying it is the run itself, which is the whole lesson of
that first run.
