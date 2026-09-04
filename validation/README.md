# Native-speaker validation

| Field | Value |
| --- | --- |
| **Purpose** | Answer the one question no automated check can: **is our Tigrinya correct?** |
| **Status** | **Instrument built, not yet reviewed.** Awaiting **A-13** |
| **Plan** | `docs/roadmap/READINESS_PLAN.md` steps 1.1–1.5 |
| **Decisions** | Required by **DEC-007**; will settle **DEC-025**; tests **DEC-010** |

---

## Why this exists

**Every intrinsic check in this project catches *broken*, not *wrong*.** A
transliterator returning deterministically incorrect phonemes passes
idempotence, determinism, reversibility, coverage and alignment integrity —
all six — without a murmur. `tigrinya_eval.primitives` says so in its own
docstring, and DEC-023 says so in its consequences.

Nothing here has ever been read by someone who speaks Tigrinya. That is the
single largest correctness risk in the project (**GAP-1**), and it is the one gap
no amount of engineering closes.

## What the reviewer receives

Send them **`PROTOCOL.md`** and the **`sheets/`** directory. Nothing else.

⚠️ **Never send `key.json`.** It records which option on sheet 1 is the form we
ship. The whole design depends on the reviewer not knowing.

## The sheets

| Sheet | Items | Question it settles |
| --- | ---: | --- |
| **1 · which is right** | 25 | **The word-final `ɨ`.** Experiment 005 found word-by-word and running-text transliteration disagree on **4.53%** of tokens and could not determine which is correct. → **DEC-025** |
| 2 · common words | 35 | Accuracy on the highest-frequency words — widest blast radius |
| 3 · spelling variants | 14 | Is collapsing ጸ/ፀ and ኣ/አ a **matching aid** or a **correction** of how someone chose to write? |
| 4 · random sample | 40 | **The only unbiased accuracy estimate.** Sheets 1–3 select hard cases on purpose |
| 5 · which variety | 20 | Is our evaluation material Eritrean, Ethiopian, or mixed? → tests **DEC-010** |

**134 items, roughly 25 minutes.** Sheets are ordered most-informative-first so
**partial completion is still useful** — a reviewer who does only sheet 1 has
settled the most valuable open question in the project.

### Stratum D is empty, and that is a measurement

There is no pass-through sheet. Coverage over Ethiopic **letters** is
**100.00%** on this corpus, so there are no unmapped-letter words to review.
Recorded in `manifest.json` as an empty stratum rather than quietly omitted.

## Design decisions

**Stratified, not random.** A random sample spends a volunteer's scarce time on
easy cases. Each stratum answers one open question and is independently
analysable.

**Forced choice with the answer hidden.** Sheet 1 shows both candidate forms in
**randomised order** with no indication of which we produce. Asking "is our
output right?" invites agreement; asking "which of these is right?" does not.
Verified: our form sits in position 1 for 11 items and position 2 for 14, so
position carries no signal.

**IPA is a barrier, so it gets a key.** Our output uses `ʔ ɨ ə ħ ʕ t͡sʼ`, and a
fluent speaker who is not a linguist has no reason to read those. The
pronunciation key in `PROTOCOL.md` is **generated from the corpus** — every
symbol anchored to a real Ge'ez character that produces it. The most important
entry, `ɨ`, has no single-character anchor because it is epenthetic, so it falls
back to the shortest word containing it (ሕቶ → `ħɨto`). An earlier version
omitted that entry entirely — the symbol appearing **1,419 times** and the one
sheet 1 is about.

**`unsure` is a first-class answer.** A reviewer who declines to guess is giving
information. `analyse.py` reports it separately and never folds it into
agreement.

## Running it

```bash
pip install -e services/primitives

python3 validation/generate.py                 # rebuild the instrument
python3 validation/analyse.py returned/rev-01/ # score a completed set
```

`generate.py` is deterministic — sheets, manifest and key reproduce
byte-identically across `PYTHONHASHSEED` values, so two reviewers can be given
provably identical material.

## What the analysis will and will not conclude

- **Accuracy comes from sheet 4 only.** A rate computed over sheets 1–3 would
  describe our sampling, not the transliterator. `analyse.py` refuses to present
  one rather than leaving it to discipline.
- **One reviewer is not a consensus.** Every figure is one person's judgement —
  real evidence, and not a measurement of the language. Two reviewers would let
  us report agreement; one cannot.
- **A `no` on sheet 3 is a finding**, not noise: DEC-007 records normalisation as
  a matching aid, *never* a correction. If a speaker disagrees, the decision is
  wrong, not the speaker.

## Obligations to the reviewer

- **Credit by name**, unless they decline.
- Their answers enter an openly licensed project (docs are CC-BY-4.0). Say so
  before they start, not after.
- **If this should be paid, it should be paid.** Expert judgement in a
  low-resource language is scarce and routinely extracted for free. `PROTOCOL.md`
  invites them to say so; that invitation should be genuine.

## When results come back

1. `python3 validation/analyse.py returned/<reviewer>/`
2. Record measured accuracy in `docs/benchmarks/metrics.md`, replacing
   "intrinsic only" for transliteration and normalisation.
3. **Settle the `ɨ` question as DEC-025.** If the in-context form wins,
   `transliterate.py` changes and DEC-023 needs a second amendment.
4. If sheet 5 shows mixed varieties, **DEC-010 stops being a precaution** and
   becomes a live correction to the evaluation set.
5. Retire the caveat "no native-speaker validation" everywhere it appears —
   currently **29 places**.
