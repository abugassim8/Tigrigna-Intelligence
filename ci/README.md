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

```
git pull
mkdir .github\workflows
git mv ci/verify.yml .github/workflows/verify.yml
git commit -am "Activate CI verification workflow (DEC-018)"
git push
```

**These five work unchanged in Windows CMD, PowerShell, macOS and Linux.** No
`sed`, no `mkdir -p`, no shell switching — on Windows use a backslash in the
`mkdir` line, forward slashes everywhere else (git always takes forward slashes).

⚠️ **`git pull` first is not optional** if the clone is more than a few minutes
old — the agent pushes to this branch too, and a stale clone is rejected with
*"Updates were rejected because the remote contains work that you do not have."*

*(There used to be a `sed` step here to repoint `docs/figures.json`. It is gone:
`docs/figures.json` now lists **both** paths and `scripts/check_figures.py` takes
the first that exists, so the count derives correctly before and after the move.
The `sed` was the step that broke on Windows.)*

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

## ✅ It ran — and the first run found three defects

**Activated 2026-09-04** (commit `888633d`). The first run in the project's life:
**three of six jobs failed**, none of them a flake.

| Failure | Cause |
| --- | --- |
| `DEC-027 has no entry in rejected_options.md` | The check iterated every DEC-NNN **mentioned**, not defined. DEC-027 is a reserved id for the endpoint surface (blocked on A-02); citing it is not deciding it |
| `ModuleNotFoundError: tigrinya_eval` | The `reproducibility` job never installed `services/evaluation`, and experiment 007 imports it. Five experiments reproduced, then it died |
| 4 planted morphology cases "misbehaved" | The `screening` job had **no install at all**, so `sacrebleu` was missing. ✅ The plant suite was right — it reported failure instead of passing quietly |

### ⚠️ A consequence of activation, discovered immediately

**The workflow is now in the one directory an agent cannot write to.** Any
commit touching `.github/workflows/` is rejected with the same
*"without `workflows` permission"* error that made A-15 human-only.

Before activation an agent could edit the workflow and not run it. After
activation it can run it and not edit it. **Every future CI fix needs a human to
apply it** — see [`pending/`](pending/), which holds patches prepared and
verified but unpushable.

That is not an argument against activation. It is the cost, and it was not
foreseen by either party.

### ⚠️ Why local pre-flight missed two of them

Before activation, all 28 non-install `run:` blocks were extracted from this
file and executed locally: **28 run, 0 failed**, twice. But that harness
**skipped the 7 `pip install` steps by design** — the local venv already had
everything — so it could not possibly detect an install step that installs the
*wrong things*. **Two of the three failures were exactly that.**

The third was a genuine regression introduced *after* the pre-flight ran: a new
DEC-002 amendment cited DEC-027, and the pre-flight had already finished.

**This is the concrete evidence for the distinction this file kept asserting.**
"Verified locally" and "verified" are different claims, and the gap is not
hand-waving — it is the seven steps a local harness cannot honestly run.

## Note on the reproducibility job

It doubles as a **dependency regression test**. If `epitran`, `tokenizers`, or
`sacrebleu` changes behaviour, an experiment stops reproducing and CI says so.
That is currently the only guard between DEC-007's amended numbers and silent
drift — another reason activation matters.
