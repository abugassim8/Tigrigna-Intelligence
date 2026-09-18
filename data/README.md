# Data

## Purpose of this directory

Evaluation data the project scores against, held as a first-class asset rather
than as a by-product of whichever experiment happened to need it first.

## Why this directory exists

Until 2026-09-01 every corpus in this repository lived under `experiments/`,
because that is where the first one was needed. That was fine while the only
Tigrinya text we had was a **30-sentence FLORES sample** pulled in to make
experiment 003 run. It stopped being fine the moment we had a real anchor: an
evaluation set that experiments depend on should not itself be filed inside one.

The move also closed a gap. The DEC-015 rule "every committed corpus carries a
screening record" was enforced by a glob over `experiments/`, so a corpus
anywhere else would have been the one exempt from screening — see `ci/verify.yml`.

## Structure

| Directory | Contents |
| --- | --- |
| `anchors/` | Evaluation sets. One directory per corpus, each with its own provenance, licence, screening records, and a fetcher that proves the committed copy is upstream's |

## Rules

1. **Every corpus carries a screening record** (**DEC-015**) at
   `<corpus dir>/screening/<name>.json`, produced by
   `scripts/data_processing/screen_dataset.py`. CI enforces this.
2. **Screen each side of a parallel corpus separately**, declaring `--script`.
   A Latin side screened as Ge'ez fails on legitimate accented letters; a Ge'ez
   side screened as Latin skips the gates written for it. The declaration is
   verified against the contents, so it cannot be used to wave a corpus through.
3. **Attribution is not optional.** Every anchor here is used under a licence
   that requires it. The attribution lives in the corpus's own README.
4. **Committed *and* fetchable.** The bytes are committed so evaluation works
   with no network — egress here is partial — and a `fetch.py` re-derives them
   from upstream and compares SHA-256, so "the committed copy is the real one"
   is a claim that can be checked rather than assumed.
5. **An anchor is never training data.** Anything scored against a set in here
   must be screened against it for contamination first (**DEC-008**).

## Status

**One anchor: HornMT** — 2,030 human-translated English–Tigrinya news pairs,
CC-BY-4.0. It is the project's **first cleanly-licensed parallel corpus**, and
it retires the claim, `[verified]` in summary 013 and wrong, that we had **0**
cleanly-licensed parallel sentences.

## What future contributors should add

More anchors, each with the same apparatus. The gaps worth filling first are the
full FLORES+ dev/devtest (**gated on Hugging Face — needs A-08**), and a
labelled set such as TiALD for tasks the primitives cannot be scored on.
