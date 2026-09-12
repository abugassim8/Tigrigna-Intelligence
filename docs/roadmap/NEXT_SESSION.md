# Next session — start here

| Field | Value |
| --- | --- |
| **Status** | **Live handoff.** Written 2026-09-03, approved by the owner · **updated 2026-09-12** — the last hand-maintained counts are derived, and building the first of them wrote the tenth check that could not fail |
| **Supersedes** | `READINESS_PLAN.md` §12's *"Nothing. This list is empty"* — that conclusion is **false**, see below |
| **Read first** | This file, then `READINESS_PLAN.md`, then `ACTIONS.md` |

This file exists so a session that starts cold can pick up without re-deriving
anything. It is deliberately short.

**Part 2 is done**, including the full-anchor measurement. The next
agent-doable task is **Part 3** (experiment 011). The highest-leverage thing in
the whole project is still **A-13**, and it needs a person — see Part 5.

⚠️ **A-13's question got sharper on 2026-09-11.** The full anchor found two
words where normalisation *destroys* the analysis (ኣአንጋዲ, ኣአንገድቲ). That is a
specific thing to put to the reviewer, and the 900-segment sample said it never
happened.

---

## Part 1 — Where the project actually is

Two Python packages are built and tested (`services/primitives`,
`services/evaluation`) — **175 tests**. Everything else under `services/` is a
one-file scaffold. Two evaluation anchors are committed and screened
(`data/anchors/hornmt`, `data/anchors/tico19`). 28 decisions, 10 experiments,
16 summaries.

**Four of five GAPs are open** — GAP-2 closed 2026-09-04 when CI was installed,
and **GAP-5's measurement half closed 2026-09-08**, widened to the whole anchor
2026-09-11 (its accuracy half needs A-13). **Three of six v0.1 exit criteria are
met.**

✅ **CI enforces 28 checks** as of 2026-09-04. Its first run failed three of six
jobs; all three were real and are fixed.

✅ **`check_figures.py` derives nine counts** as of 2026-09-12, up from seven —
`plants` and `open_actions` were the last two a human maintained by hand, and
both had already drifted. ⚠️ **Building the first of them wrote the tenth check
that could not fail** (§13): `planted` is itself a suppression marker, so a
count of *planted cases* exempted its own claim and passed on any number. Caught
by testing it against a wrong number — the first of the ten caught before it was
committed.

✅ **HornMorpho runs here** as of 2026-09-07, which had been assumed impossible
since the project began, and **morphology is measured over all 9,212 Tigrinya
segments** as of 2026-09-11. See Part 2 — what the install returned was mostly
*not* the measurement, and what the full anchor returned was mostly not a
bigger *n*.

Never done: **no speaker has validated a single output; no model has ever been
scored; nothing is deployed.**

⚠️ **Run the suite in both states.** `/tmp/venv` (Python 3.11) has no importable
HornMorpho and is the environment the tests were designed around; `/tmp/venv312`
has it. Counts differ **by design** — 173 pass / 2 skip absent, 171 pass / 4
skip present, 175 collected either way. If neither number matches, something
broke; if you only ever run one, you are testing half the code.

⚠️ **`/tmp/venv312` is not in the repository and will not survive a new
container.** Rebuilding it — interpreter with `tkinter`, HornMorpho, the 159 MB
language pack — is the recipe in
[`../benchmarks/measurements/README.md`](../benchmarks/measurements/README.md).

---

## Part 2 — ✅ DONE: HornMorpho installed (09-07), full anchor measured (09-11)

**It worked, and the install was the least interesting part.**

`pip install git+https://github.com/hltdi/HornMorpho` succeeded — **5.3.6**.
This file called that line *"the one untested link and the most likely failure
point"*. It was neither. The Tigrinya data came from the
`media.githubusercontent.com` LFS host exactly as probed, **158,902,071 bytes**,
and `morphology.is_available()` returned `True` for the first time in the
project's life.

### ⚠️ One thing genuinely blocked, and it is upstream's

**`import hm` requires `tkinter`.** `hm/__init__` → `hm.morpho` → `corpus.py:32
from .gui import *` → `gui.py:26 from tkinter import *`, unconditionally. The
whole package-wide dependency is **one call site** — `corpus.py:483`, inside
`Corpus.disambiguate()`, which nothing in the analysis path touches.

So HornMorpho 5.3.6 **cannot be imported headlessly at all** — not here, not in
a slim container, not on a CI runner. That is a fact about the dependency, and
it is now **A-18** (report upstream; a deferred import fixes it).

Getting `tkinter` was its own lesson. The interpreter was Python 3.11 from the
**deadsnakes PPA**, and `ppa.launchpadcontent.net` is **403 at the proxy** — an
org egress denial, not retried and not routed around. The way through was a
*different permitted source*: Ubuntu noble's own `python3-tk` is for **3.12**
and comes from `archive.ubuntu.com`, which is open. Hence `/tmp/venv312`.

### What the first real run found — three defects, and none was a threshold

Every one lived exactly where the injected fake stopped and the real analyser
began, which is why the 171-test suite could not have caught any of them:

1. **`_render` mixed two axes.** HornMorpho returns *several* readings per word,
   some with a segmentation and some with only a POS tag. Both rendered bare
   into the same `|`-separated slot, so ኣብ came out `ADP|-<ኣብ>--` — slot 0 a
   tag, slot 1 a segmentation, nothing distinguishing them. **Every test
   fixture supplied `seg`**, so the fallback branch had never once run. Tags
   are now braced: `{ADP}|-<ኣብ>--`.
   *(Upstream's contradictory docstrings turned out to be the same thing said
   twice: `Word` subclasses `list`, so it **is** a list of dicts.)*

2. **The morphology CLI measured English.** `load_corpus` on a parallel anchor
   directory sweeps in the source language — `data/anchors/tico19` is 6,142
   lines of English beside 9,213 of Tigrinya. Worse, `experiments/003-metric-
   validity/data`, which **CI** has been running morphology over, is **50%
   English**. `_main` now filters by script and prints what it dropped.

3. **Five tests and two planted cases asserted the environment, not the code.**
   They hard-coded *"HornMorpho is absent"* and failed on the first machine that
   had it. The plant harness announced *"a check has stopped being able to
   fail"* when nothing had — **a false alarm inside the one tool whose entire
   job is to be trusted about real alarms.** All are gated on
   `is_available()` now, with present-path mirrors, and the harness reports
   NOT RUN loudly rather than passing quietly.

**The transferable lesson**, and it belongs beside §13's: *an unrun instrument
is not a working instrument.* "Verified against a fake" is a weaker claim than
it reads as, and it is the same failure as the stale access register — a
conclusion standing in where a measurement should be.

### The measurement itself

✅ **Re-measured over the FULL anchor 2026-09-11** — all 9,212 Tigrinya
segments, 194,588 word tokens, via `scripts/measure_morphology.py` (~3.3 h; the
naive path is ~31 h).

| Check | Full anchor | Sample |
| --- | --- | --- |
| `surface` · `alignment` · `determinism` | **100%** | 100% |
| `coverage` | **116,583/194,588 = 59.91%** | 62.27% |
| `normalisation` | **144/197 = 73.10%** | 31/41 |

⚠️ **The sample was optimistic, and in one place misleading.** It reported that
normalisation never destroys an analysis. Over the full anchor it does — **2
lost**, against 22 rescued and 29 changed. Both are ኣአ → ኣኣ rewriting a word out
of the lexicon (ኣአንጋዲ, ኣአንገድቲ). **A-13 now has a specific question to answer.**

**What normalisation actually does**, on the **197** informative pairs (477
words change; 280 are unanalysable either way and are excluded because they
would disagree by construction):

| Outcome | Count | Meaning |
| --- | ---: | --- |
| unchanged | **144** | normalisation left the analysis alone |
| **rescued** | **22** | analysable only *after* normalising — it is working |
| **lost** | **2** | ⚠️ a distinction destroyed |
| differs | **29** | both analyse, differently |

Direction still favours normalising, but **"never harmful" is no longer
available as a claim**, and that sentence is the whole return on running the
full corpus.

⚠️ **Two earlier normalisation figures were wrong or incomplete, in different
ways.** The very first run reported **43.06%**, because pairs unanalysable in
*both* forms were counted as disagreeing — they differ by construction, since
differing is what normalisation just did to them. That was a defect and was
fixed. The sample's **0 lost** was not a defect; it was a true statement about
900 segments that did not generalise. Those are different mistakes and the
second is the harder one to notice.

### Running it — `scripts/measure_morphology.py`

The naive path is ~650,800 analyses, **~31 hours**. The harness does ~65,980,
**~3.3 hours**, from one observation: `check_determinism` already analyses every
unique word twice, so `surface`, `alignment` and `coverage` can be served from
the table its first pass builds.

⚠️ **Determinism at 100% is what licenses that substitution**, and the harness
writes nothing at all below it. So `check_determinism` is **not one result among
five here — it is the precondition for the other four.** Say so wherever these
numbers are quoted.

⚠️ **`_Recorder.__call__` must always call through.** Serving a cached value
there makes determinism compare a value to itself. A plant breaks exactly that
line and proves a real failure then becomes invisible; if you change it, that
plant must fail.

⚠️ **One assumed cost was false and nobody had checked.** `check_determinism`'s
docstring says *"HornMorpho memoises internally"*. It does not — a repeat costs
**77%** of a cold analysis. That is what made the anchor look like a 31-hour job.
Sixth instance of the pattern, and the first found inside our own code rather
than in an access register.

`docs/benchmarks/measurements/` — a category for numbers CI **cannot** re-derive.
Morphology is the first: GPL-3.0 and never installed in CI (DEC-028), **~4.1 GB**
resident, hours of compute.

⚠️ **These numbers carry a weaker guarantee than any `experiments/` entry**, and
that cost is recorded rather than hidden. See that directory's README, which
carries the full reproduction recipe.

⚠️ **Intrinsic checks catch *broken*, not *wrong*.** Nothing here says
HornMorpho's Tigrinya is **correct** — that needs a speaker (**A-13**), exactly
as experiment 004 found. Do not let a coverage number drift into sounding like
an accuracy number.

## Part 3 — The next agent task: Experiment 011, inter-translator agreement

⚠️ **The headline numbers were already observed during planning**, so under
DEC-016 they cannot be presented as pre-committed hypotheses. Record them as
`MEAS`, or pre-commit only on quantities not yet seen — **the dev split and the
per-segment distribution.**

⚠️ **Not HornMT.** An earlier version of this line listed it, and that was
wrong: `data/anchors/hornmt/` holds **one** Tigrinya reference (`tir.txt`), so
there is no second translator to compare against and inter-translator agreement
cannot be measured there at all. **TICO-19 is the only anchor with an
independent pair**, and only `tir_er` vs `tir_et` — `tir_ti` and `tir_et` are
one lineage.

Measured on TICO-19 `test`, chrF:

| | Raw | After `normalise()` |
| --- | ---: | ---: |
| ER vs ET (independent translators) | **24.58** | 24.64 |
| ti vs ET | **83.65** | 83.67 |
| ti vs ER | 23.95 | 24.02 |

**Two professional humans translating the same English agree at chrF ~25.** Any
future model score on these anchors must be read against that. It is **not** a
"ceiling" — chrF between two translations is not the same quantity as chrF
between a system and a reference — and a write-up must not call it one.

Normalisation moves the score by **0.06**, so the ER/ET divergence is lexical
and structural, not orthographic. `ti` vs `ti_ET` at 83.65 confirms
quantitatively that they are one translation lineage, not independent references.

---

## Part 4 — Cleanup, real but not urgent

- `docs/research/README.md` still says **"No research has been conducted…
  contain only scaffolding"** — against 13 domains, 16 summaries, 10 experiments.
- `ACTIONS.md` contradicts itself on **A-12**: two tables say `DONE`, the body
  still says `⏸️ Deliberately deferred`.
- **A-07 is described as an open blocker in ~16 places** after DEC-028 closed it.
  Research reports may be intentionally immutable; the living documents are not.
- `docs/vision/success_metrics.md:54` says Tier 1 is blocked on **A-01**. It is
  **A-09** — the exact dependency error the plan records as already corrected.
- ~~`services/README.md` quotes `61` and `14` tests~~ ✅ **fixed 2026-09-07** —
  dropped rather than updated, per DEC-024.
- ~~**Two hand-maintained counts drift, and `docs/figures.json` derives
  neither.**~~ ✅ **Both derived, 2026-09-12.** Kept here because *how* they
  failed is worth more than that they are fixed:
  - ~~**Open actions.**~~ ✅ Derived with a new `between` option on
    `grep_count`, scoping the pattern to the register's at-a-glance section.
    Unscoped it counts **16** against an answer of 13, because the *Done* table
    repeats the row shape — wrong in the direction of looking finished.
    The second number in that sentence, *"twelve need a human"*, was **deleted
    rather than derived**: it is 13 minus A-14, a judgement recorded nowhere
    machine-readable. Naming the exception beats counting it.
  - ~~**Planted cases.**~~ ✅ **Derived 2026-09-12.** `docs/figures.json` gains
    a `plants` count from a new `python_list_lengths` derive kind, which `ast`-
    parses `test_plants.py` and sums every module-level `*_PLANTS` list. The
    suite now computes its own total the same way, so a fifth list cannot make
    the printed and documented numbers disagree.
    ⚠️ **It did not work on the first attempt, and the way it failed is the
    point.** `planted` is itself a COUNT_MARKER, so the sentence stating how
    many plants there are exempted itself: the check passed on 29 and on 31.
    **Third time this marker vocabulary has disabled a check.** Fixed with a
    per-count `ignore_markers`, which *removes* a suppression rather than
    adding one.

  ⚠️ **The marker vocabulary disabled both**, and a green run proves nothing —
  only testing against a *wrong* number shows it. The two differ in one way
  worth keeping straight:
  - `plants` **shipped broken.** It passed on 29 and on 31 before anyone
    checked, because `planted` is itself a COUNT_MARKER. **Third instance.**
  - `open_actions` **was caught before registering**, by reading `_has_marker`
    rather than by running anything — and then demonstrated: against the
    original claim line, which carried a ⚠️, the check exits **0** on a wrong
    number. **Fourth instance, prevented rather than shipped.**

  Rewording the claim line is what fixes it — measured: with the ⚠️ gone the
  check fails correctly even with markers on. `ignore_markers` is *insurance*
  against a future ⚠️ landing within eight lines, not load-bearing today. It
  *removes* a suppression rather than adding one, which is why a false positive
  is the worst it can cost. Before giving a third count that flag, ask whether
  its claim can simply be reworded.

---

## Part 5 — What only a person can do

📧 **Including sending every one of these.** No agent transmits email (owner
instruction, 2026-09-04). Drafts in `ACTIONS.md` are written *for the owner to
send*; an assistant may compose and refine, never send.

**Thirteen open actions.** All but **A-14** need a person, and A-14 is blocked
on A-09 anyway. Full detail and ready-to-send drafts are in
[`../../ACTIONS.md`](../../ACTIONS.md). In leverage order:

| # | Action | Effort | Unlocks |
| --- | --- | --- | --- |
| 1 | **A-13** — ✅ **sheets sent 2026-09-04**, awaiting the reviewer | **~25 min of a speaker** | The only route to claiming our Tigrinya is correct. GAP-1, DEC-025, v0.1. ⚠️ Reviewer writes the **Eritrean** standard — DEC-025 must say so and must not generalise |
| ~~2~~ | ~~Apply the CI workflow fix~~ | ✅ **DONE 2026-09-04** | All six jobs green. ⚠️ Standing constraint: **an agent cannot push `.github/workflows/`**, so every future CI change needs you — see `ci/README.md` |
| ~~3~~ | ~~**A-02** — confirm DEC-002~~ | ✅ **DONE 2026-09-03** | DEC-002 Accepted. Unblocks the API/MCP/SDK surface |
| 4 | **A-09** — model weights / egress | config | Every score. GAP-4, Tier 1, Tier 2, A-14 |
| 5 | **A-08** — set `HF_TOKEN` | ⚠️ **token created, not yet reaching the agent** | Full FLORES+. Needs the value in the environment's settings AND the gate accepted on the dataset page |
| 6 | **A-01** — licence on the `fgaim` models | one email | Licensing-clean criterion |
| 7 | **A-03** — report the TiQuAD contamination | one post | An ecosystem obligation we are sitting on |
| 8 | A-04, A-05, A-06, A-10, A-11, A-16, **A-18**, **A-19** | varies | Lower leverage; drafts ready. **Two upstream reports are new:** A-18 — HornMorpho cannot be imported without `tkinter`; A-19 — it **crashes on a bare `#`**, because its lexicon loader parses comment lines as entries. Both are courtesy, neither blocks us |

**If you do exactly one thing, do A-13.** It has the longest lead time of
anything in the project and every correctness claim waits behind it.
