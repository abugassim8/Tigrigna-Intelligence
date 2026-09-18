# Next session — start here

| Field | Value |
| --- | --- |
| **Status** | **Live handoff.** Rewritten **2026-09-18**, the day the translation pipeline first produced correct output |
| **Read first** | `CLAUDE.md` (loads automatically), then this file, then `ACTIONS.md` |
| **Rule for this file** | ⚠️ **It points; it does not copy.** A previous `CLAUDE.md` restated `ACTIONS.md` and was wrong within a day. Counts and statuses live in the register and in `docs/figures.json`, where `check_figures.py` fails the build when they drift |

This file exists so a session that starts cold can pick up without re-deriving
anything. It is deliberately short.

**If you do exactly one thing, do A-13** — forward the judgement sheets. Every
correctness claim in this project waits behind it, and it has the longest lead
time of anything here.

---

## Part 1 — Where the project actually is

**The translation pipeline works.** On 2026-09-18, against the converted
checkpoint:

```
<2es>  Lávese las manos con frecuencia.     ← correct
<2de>  Wasche deine Hände regelmäßig.       ← correct
<2am>  እጆችህን በየጊዜው መታጠብ                    ← correct Amharic
<2ti>  እጃምካ ብጣዕሚ ጻሕፍ።                      ← Ge'ez, well-formed
```

⚠️ **Amharic is the control that settles it.** Same Ge'ez script, far more
training data, and it is correct — so the model can generate Ge'ez and can
translate into a Ge'ez-script language. Anything remaining is specific to
**Tigrinya**, which is the question this project exists to answer.

⚠️ **No Tigrinya measurement exists yet, and one sentence is not one.** The
pre-committed threshold is **fewer than 40 of 100 usable retires the approach**,
judged by a Tigrinya speaker on the sheet — never by chrF, which Experiment 011
showed two professional translators scoring ≈ 24 against each other on this
data.

For everything else — packages, anchors, decisions, experiments — run the
checks listed in `CLAUDE.md`. ⚠️ **Deliberately no counts here.** This file used
to claim "175 tests"; it had been 187 for days and nothing noticed, because
`tests` is not one of the nine figures `docs/figures.json` derives. Numbers that
nothing checks do not belong in a handoff.

---

## Part 2 — The next command

```bash
python scripts/check_environment.py
python scripts/translate_tico19.py --model models/madlad400-3b-mt-bf16 --smoke
python scripts/translate_tico19.py --model models/madlad400-3b-mt-bf16 --diagnose
python scripts/translate_tico19.py --model models/madlad400-3b-mt-bf16 --json out.json --sheet sheet.csv
```

In that order — `--smoke` is a minute, `--diagnose` about four, the full run
50–90 minutes. Each rules out a class of failure the next would waste time on.

⚠️ **`--model` on every one.** Without it the measurement loads the 11.76 GB
float32 original, which exceeds the Windows commit limit on a 16 GB machine.

⚠️ **Old `*-REJECTED.json` files will not block the run.** The fingerprint now
includes `head_state`, so a run on a repaired model is a different run from the
wrong-language rejections of 2026-09-15 and -16.

⚠️ **Read the controls before the Tigrinya.** Fluent Spanish and German mean
the pipeline works; poor Tigrinya after that is a **finding about coverage**,
not a bug. That distinction is the whole design of `--diagnose`.

Then the output of the full run goes to the reviewer, not into a claim — see
Part 4.

---

## Part 3 — What the last week actually was

Eight defects, in order, **none of them about Tigrinya**. Every one sat upstream
of the question:

| # | Defect | Recorded as |
| --- | --- | --- |
| 1 | `hm.download('ti')` rejected an abbreviation `analyze()` accepts — six weeks inside an error message | **A-20** |
| 2 | Windows `cp1252` encoding, 39 sites; `main()` is called by import, so a `__main__` guard does not run | CHANGELOG 09-15 |
| 3 | `dtype=` vs `torch_dtype=` — an unknown keyword is forwarded to the config and ignored | `DtypeIgnoredError` |
| 4 | `config.tie_word_embeddings` — transformers 5.x overwrites it to `True` | **twelfth** check that could not fail |
| 5 | the loader puts `lm_head.weight` into `shared.weight`, so the **encoder** embeds with the output projection | **A-22**, DEC-011 Amendment 5 |
| 6 | a repair that inferred tensor roles from the already-corrupted model, and reported success | **thirteenth** |
| 7 | 11.76 GB float32 against a 16 GB commit limit | `shrink_checkpoint.py` |
| 8 | the repair itself holding two matrices and a memory map | `read_tensor`, `tensor_digest` |

⚠️ **The lesson that generalises, and it cost four runs:** *a declared flag is
not an outcome, and neither is a loaded model.* Verify against the **file**.
`CLAUDE.md` carries the short form; `docs/roadmap/READINESS_PLAN.md` §13 carries
every check that could not fail and how each was found.

⚠️ **Two plants written this week could not fail and were deleted rather than
kept.** Both measured peak RSS to catch a Windows commit-limit crash — one
in-process (`ru_maxrss` never decreases, so the fixture masked the repair), one
differential in a child (RSS on Linux does not reflect a Windows commit limit).
They were replaced by structural invariants that hold on any platform. **A green
plant on the wrong platform is worse than no plant.**

---

## Part 4 — What only a person can do

📧 **Including sending every one of these.** No agent transmits email (owner
instruction, 2026-09-04). Drafts in `ACTIONS.md` are written *for the owner to
send*; an assistant may compose and refine, never send.

⚠️ **And including every command that loads a model.** `huggingface.co` is
blocked by org egress policy in the assistant's environment —
`CONNECT tunnel failed, response 403`. An assistant asked to run one should say
it cannot and hand over the command, not improvise a substitute: a measurement
whose provenance is unclear is worthless. ⚠️ Running Claude Code **locally** —
see `docs/guides/LOCAL_SETUP.md` — removes this gap entirely, and is now the
supported way to work.

**In leverage order. Detail, status and ready-to-send drafts are in
[`../../ACTIONS.md`](../../ACTIONS.md), which is the register — this is an
ordering, not a copy of it.**

| # | Action | Why it is first |
| --- | --- | --- |
| 1 | 🔴 **A-13** — forward the judgement sheets, already in the owner's Gmail | The only route to claiming our Tigrinya is correct. ⚠️ The reviewer writes the **Eritrean** standard, and DEC-025 must say so rather than generalise. ⚠️ Never attach `key.json` or `manifest.json` |
| 2 | **A-22** — the `T5Config` report upstream | Now backed by a working before/after. It silently breaks **every** T5-architecture checkpoint with an untied head, not just this one |
| 3 | **A-21** — add `check_commands.py` to `.github/workflows/verify.yml` | One line. The only checker not enforced on a push, and an agent cannot touch `workflows/` |
| 4 | **A-01**, **A-03**, **A-04**, **A-06** | Licence and data obligations; A-03 is an ecosystem duty we are sitting on |
| 5 | **A-05**, **A-19**, **A-20**, **A-18**, **A-16**, **A-10**, **A-11** | Drafts ready. Courtesy reports and lower-leverage asks |

⚠️ **Not an action, a setup step: `HF_TOKEN` is not set on the owner's machine.**
The last run printed *"unauthenticated requests to the HF Hub"*, and
unauthenticated downloads were measured at **57 kB/s**. **A-08 is closed** — the
token was obtained 2026-09-03 — so this is `setx`, covered by
`docs/guides/LOCAL_SETUP.md`, not a register entry. ⚠️ The value goes in the
environment, never in a file.

**Still agent-doable, not email:** **A-14**, Tier 2 cold start (DEC-019).

---

## Part 5 — Cleanup, real but not urgent

Verified still open on 2026-09-18:

- `docs/research/README.md` says **"No research has been conducted…
  contain only scaffolding"**, which the tree contradicts.
- `ACTIONS.md` contradicts itself on **A-12**: the tables say `DONE`, the body
  still says `⏸️ Deliberately deferred`.
- **A-07 is described as an open blocker in ~16 places** after DEC-028 closed
  it. Research reports may be intentionally immutable; living documents are not.
- `docs/vision/success_metrics.md:54` says Tier 1 is blocked on **A-01**. It is
  **A-09** — the exact dependency error the plan records as already corrected.

⚠️ **Worth considering: register `tests` as a derived count.** It drifted 175 →
187 in this very file and nothing caught it, because only nine figures are
derived. The alternative — and the one taken here — is to stop stating it.
Before registering a tenth, read `READINESS_PLAN.md` §13 on how the marker
vocabulary disabled two counts already.
