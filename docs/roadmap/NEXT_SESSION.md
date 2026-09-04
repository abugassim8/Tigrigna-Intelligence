# Next session — start here

| Field | Value |
| --- | --- |
| **Status** | **Live handoff.** Written 2026-09-03, approved by the owner · **updated 2026-09-04** (A-02, A-08, A-15 closed; speaker found for A-13) |
| **Supersedes** | `READINESS_PLAN.md` §12's *"Nothing. This list is empty"* — that conclusion is **false**, see below |
| **Read first** | This file, then `READINESS_PLAN.md`, then `ACTIONS.md` |

This file exists so a session that starts cold can pick up without re-deriving
anything. It is deliberately short. **If you do one thing, do Part 2.**

---

## Part 1 — Where the project actually is

Two Python packages are built and tested (`services/primitives`,
`services/evaluation`) — **161 tests**. Everything else under `services/` is a
one-file scaffold. Two evaluation anchors are committed and screened
(`data/anchors/hornmt`, `data/anchors/tico19`). 28 decisions, 10 experiments,
16 summaries.

**Four of five GAPs are open** — GAP-2 closed 2026-09-04 when CI was installed.
**Three of six v0.1 exit criteria are met.** Three of fourteen capability rows
in `metrics.md` are measured.

✅ **CI enforces 28 checks** as of 2026-09-04. Its first run failed three of six
jobs; all three were real and are fixed.

Never done: **no speaker has validated a single output; no model has ever been
scored; nothing is deployed.**

---

## Part 2 — The next task: install HornMorpho and measure morphology

**`READINESS_PLAN.md` §12 says there is nothing left an agent can do. That is
wrong, and the reason is the mistake this project keeps catching itself on: a
stale assumption about access.**

Morphology measurement (**GAP-5**, `metrics.md`'s ❌ row, plan step 2.3) is
recorded everywhere as blocked on *"an actual install"*. Nobody tested whether
the install was possible. It was tested 2026-09-03, read-only:

| Probe | Result |
| --- | --- |
| `raw.githubusercontent.com/hltdi/HornMorpho/master/setup.py` | ✅ 200 |
| `github.com/hltdi/HornMorpho` (HTML), `codeload…/tar.gz` | ❌ 403 |
| `raw…/src/hm/languages/t.tgz` | ✅ 200 — **134 bytes, a Git LFS pointer** |
| **`media.githubusercontent.com/media/hltdi/HornMorpho/master/src/hm/languages/t.tgz`** | ✅ **200 — 158,902,071 bytes** |

**The Tigrinya data is reachable.** `t` is the correct abbreviation — `ti` and
`ት` both 404. HornMorpho's own `get_language_url()` builds a
`github.com/.../raw/...` URL which **is** 403 here; that is almost certainly why
this was assumed impossible. See `docs/research/RESEARCH_ACCESS.md`.

**It is explicitly permitted.** DEC-028(e): *"Evaluating it is unaffected.
Measuring morphological accuracy locally is use, not distribution."* GPL-3.0
constrains **distribution**. Nothing here distributes it, and CI already checks
that no packaged artefact declares HornMorpho.

**It makes existing work real.** `tigrinya_eval.morphology`'s five intrinsic
checks all currently report `SKIP`. They have never measured anything.

### Steps

1. **Get the package.** Try `pip install git+https://github.com/hltdi/HornMorpho`.
   ⚠️ **This is the one untested link and the most likely failure point** —
   git-over-https works for this repo's own remote, but third-party repos are
   unproven. If it 403s, assemble `src/hm/` from `raw.githubusercontent.com`.
2. **Get the language data** from the `media.githubusercontent.com` URL above
   and place it where `hm.morpho.languages.is_downloaded('t')` looks
   (`Language.get_lang_dir`). **Fetch out-of-band and drop the file in place —
   do not patch HornMorpho's own download URL.**
3. **Verify `morphology.is_available()` is True** — it checks import *and*
   language data, which is the exact failure it was written for.
4. ⚠️ **Check `_render` against live output before trusting any number.**
   `services/primitives/src/tigrinya_primitives/morphology.py` flags this as
   *"the one unverified part of the module"*: upstream's own docstrings disagree
   on whether an analysis is a dict or a `Word` object. **This is the likely
   real code change.**
5. **Run** `python -m tigrinya_eval.morphology --require data/anchors/tico19`
   over a real anchor, not the FLORES sample.
6. **Record the two `MEAS` numbers** (coverage, normalisation) that have never
   had a value. The first measurement **sets** a floor; it is not judged by one.

### Files likely touched

`services/primitives/.../morphology.py` (`_render`) · `docs/benchmarks/metrics.md`
(the morphology row) · `READINESS_PLAN.md` §2 GAP-5 and §12 · `ACTIONS.md` ·
`CHANGELOG.md` · `docs/research/RESEARCH_ACCESS.md` (already updated).

### If it fails

**Stop and record it.** A negative result is worth as much here (**P-13**). Do
not patch upstream, do not vendor it, **do not commit any HornMorpho bytes**.

### Verification

```bash
python -c "from tigrinya_primitives import morphology; print(morphology.is_available())"
python -c "
from tigrinya_primitives.morphology import analyse
a = analyse('ኣብ ቤት ትምህርቲ')
print(a.analysis); print([(s.surface, s.analysis) for s in a.spans]); print(a.warnings)"
python -m tigrinya_eval.morphology --require data/anchors/tico19   # must exit 0
/tmp/venv/bin/python3 -m pytest services -q                        # 161 tests
python scripts/tests/test_plants.py                                # 22 planted cases
python scripts/check_figures.py && python scripts/check_dates.py
```

⚠️ Two tests are gated `@needs_absent` and **will now skip** — expect the count
to drop by exactly two, and confirm it is those two. Before committing, check
`git status` shows **no HornMorpho bytes**.

---

## Part 3 — Fallback: Experiment 011, inter-translator agreement

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
- `services/README.md` quotes `61` and `14` tests; both stale, and DEC-024
  excludes volatile counts from living documents.

---

## Part 5 — What only a person can do

**Fourteen open actions; thirteen need a human.** Full detail and ready-to-send
drafts are in [`../../ACTIONS.md`](../../ACTIONS.md). In leverage order:

| # | Action | Effort | Unlocks |
| --- | --- | --- | --- |
| 1 | **A-13** — get a Tigrinya speaker through `validation/` | **~25 min of a speaker** | The only route to claiming our Tigrinya is correct. GAP-1, DEC-025, v0.1. ⚠️ **Never send `validation/key.json`** |
| ~~2~~ | ~~Apply the CI workflow fix~~ | ✅ **DONE 2026-09-04** | All six jobs green. ⚠️ Standing constraint: **an agent cannot push `.github/workflows/`**, so every future CI change needs you — see `ci/README.md` |
| ~~3~~ | ~~**A-02** — confirm DEC-002~~ | ✅ **DONE 2026-09-03** | DEC-002 Accepted. Unblocks the API/MCP/SDK surface |
| 4 | **A-09** — model weights / egress | config | Every score. GAP-4, Tier 1, Tier 2, A-14 |
| 5 | **A-08** — set `HF_TOKEN` | ⚠️ **token created, not yet reaching the agent** | Full FLORES+. Needs the value in the environment's settings AND the gate accepted on the dataset page |
| 6 | **A-01** — licence on the `fgaim` models | one email | Licensing-clean criterion |
| 7 | **A-03** — report the TiQuAD contamination | one post | An ecosystem obligation we are sitting on |
| 8 | A-04, A-05, A-06, A-10, A-11, A-16 | varies | Lower leverage; drafts ready |

**If you do exactly one thing, do A-13.** It has the longest lead time of
anything in the project and every correctness claim waits behind it.
