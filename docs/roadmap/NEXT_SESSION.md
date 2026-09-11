# Next session — start here

| Field | Value |
| --- | --- |
| **Status** | **Live handoff.** Written 2026-09-03, approved by the owner · **updated 2026-09-07** (Part 2 done — HornMorpho installed, three instrument defects fixed) |
| **Supersedes** | `READINESS_PLAN.md` §12's *"Nothing. This list is empty"* — that conclusion is **false**, see below |
| **Read first** | This file, then `READINESS_PLAN.md`, then `ACTIONS.md` |

This file exists so a session that starts cold can pick up without re-deriving
anything. It is deliberately short.

**Part 2 is done.** The next agent-doable task is **Part 3** (experiment 011).
The highest-leverage thing in the whole project is still **A-13**, and it needs
a person — see Part 5.

---

## Part 1 — Where the project actually is

Two Python packages are built and tested (`services/primitives`,
`services/evaluation`) — **175 tests**. Everything else under `services/` is a
one-file scaffold. Two evaluation anchors are committed and screened
(`data/anchors/hornmt`, `data/anchors/tico19`). 28 decisions, 10 experiments,
16 summaries.

**Four of five GAPs are open** — GAP-2 closed 2026-09-04 when CI was installed,
and **GAP-5's measurement half closed 2026-09-08** (its accuracy half needs
A-13). **Three of six v0.1 exit criteria are met.**

✅ **CI enforces 28 checks** as of 2026-09-04. Its first run failed three of six
jobs; all three were real and are fixed.

✅ **HornMorpho runs here** as of 2026-09-07, which had been assumed impossible
since the project began. See Part 2 — it is done, and what it returned was
mostly not the measurement.

Never done: **no speaker has validated a single output; no model has ever been
scored; nothing is deployed.**

⚠️ **Run the suite in both states.** `/tmp/venv` (Python 3.11) has no importable
HornMorpho and is the environment the tests were designed around; `/tmp/venv312`
has it. Counts differ **by design** — 173 pass / 2 skip absent, 171 pass / 4
skip present, 175 collected either way. If neither number matches, something
broke; if you only ever run one, you are testing half the code.

---

## Part 2 — ✅ DONE 2026-09-07: HornMorpho installed, instrument fixed

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

**What normalisation actually does**, on the 41 informative pairs: **31
unchanged, 7 rescued** (analysable only *after* normalising — it is working),
**0 lost**, **3 differ** (all word-final `አ`→`ኣ`). It helps seven, changes
three, harms none. The three need a speaker (**A-13**).

⚠️ **The first run's normalisation figure was 43.06% and was wrong** — 31 of 41
"disagreements" were pairs unanalysable in *both* forms, which differ by
construction because differing is what normalisation just did to them. Fixed,
re-run whole. **`coverage` reproduced to the token across both three-hour
runs**, which is the only cross-run reproduction evidence this category has.

`docs/benchmarks/measurements/` — a new category, for numbers CI **cannot**
re-derive. Morphology is the project's first: the analyser is GPL-3.0 and never
installed in CI (DEC-028), it needs **~4.1 GB** resident, and it runs at
**~0.85 s per word token**, so the full anchor is ~40 hours. The sample is the
first 300 segments of each of the three TICO-19 dev references — **17,135 word
tokens**, SHA-256 of each recorded, ~4 hours to run.

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
`MEAS`, or pre-commit only on quantities not yet seen (the dev split, HornMT,
the per-segment distribution).

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
- **Nothing derives the open-action count.** It drifted to "fourteen … thirteen"
  against a register holding twelve, and `check_figures.py` could not catch it
  because `docs/figures.json` has no entry for it. A `grep_count` on
  `^\| \*\*A-\d+\*\* \|` gives **15**, not 12 — three rows in the *Done*
  table match the same shape — so this needs a **section-scoped** derive kind,
  which `check_figures.py` does not have.
  ⚠️ **Do this deliberately, not quickly.** Five of the nine checks-that-could-
  not-fail lived in exactly this tooling; a new derive kind needs a planted
  failure in `scripts/tests/test_plants.py` before it is worth anything.

---

## Part 5 — What only a person can do

📧 **Including sending every one of these.** No agent transmits email (owner
instruction, 2026-09-04). Drafts in `ACTIONS.md` are written *for the owner to
send*; an assistant may compose and refine, never send.

**Thirteen open actions; twelve need a human.** ⚠️ *This line said "fourteen …
thirteen" until 2026-09-07 and had drifted — counting the register's at-a-glance
table gives thirteen open (A-01, A-03, A-04, A-05, A-06, A-09, A-10, A-11,
A-13, A-14, A-16, A-18, A-19), of which **A-14** is the only one an agent could
do, and only once A-09 lands. `check_figures.py` does not track this count, which is why it
drifted quietly — the same class as the test count that went 145 → 161
unnoticed.* Full detail and ready-to-send drafts are in
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
