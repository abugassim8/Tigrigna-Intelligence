# Experiment 005 — Does a word's transliteration survive being put in a sentence?

| Field | Value |
| --- | --- |
| **Experiment ID** | `005-word-boundary-epenthesis` |
| **Date** | 2026-08-18 |
| **Author** | Research session |
| **Status** | **Complete — C1 and C3 REFUTED; C2 CONFIRMED** |
| **Related decision** | **DEC-023** (amended by this result); **DEC-016** (which this experiment exists because we violated) |

---

## Question

**DEC-023 rests on a claim that was never committed as a script.** The decision
record, `services/primitives/src/tigrinya_primitives/transliterate.py`, and
`types.py` all quote these two figures:

> a word's transliteration is preserved inside a sentence: **1,639/1,639 (100%)**
> prepending a character changes **0 of 1,635** tokens

They came from an ad-hoc probe during the session that recorded DEC-023. **That
is a DEC-016 violation** — a load-bearing measurement with no reproducible
artefact — and it is the reason this experiment exists.

So: **does a word's transliteration actually survive being placed in a sentence?**

## Why this matters

The claim is load-bearing three times over:

1. **DEC-023 chose word-level alignment** on the grounds that word-by-word
   transliteration is *lossless* — full fidelity *and* exact alignment.
2. **`transliterate()` transliterates word by word**, so if the claim is false
   the shipped analysis form differs from what the transliterator produces on
   running text.
3. **`transliterate_word` is `@lru_cache`d**, and that cache is only sound if a
   word's transliteration does not depend on its surroundings.

## Claims under test

These are **not newly invented predictions**. They are DEC-023's own claims,
restated from a record written *before* this measurement — which is where the
pre-commitment comes from. Inventing fresh "hypotheses" after seeing the answer
would be theatre.

- **C1** — a word's transliteration is preserved inside a sentence. *Recorded:
  1,639/1,639, 100%.*
- **C2** — prepending a character does not change a word's transliteration.
  *Recorded: 0 of 1,635 changed.*
- **C3** — epenthesis resolves within a word; nothing crosses word boundaries.

## Method

Corpus: the same four clean files experiment 004 used (`002-tokenizer-fertility/corpus`,
`003-metric-validity/data`), the `CORRUPTED` sample excluded per DEC-015 — **73
non-empty lines, 2,362 word tokens, 1,565 unique words**.

For each line, transliterate the **whole line**, split on whitespace, and pair
each output token with its input word. Compare each word's standalone
transliteration to its in-context token **two ways**:

- **exact equality** — `alone == in_context`
- **containment** — `alone in in_context`

Reporting both is the point of the experiment.

## Results

### C1 — REFUTED

| Test | Result |
| --- | ---: |
| **Containment** (`alone` is a substring of in-context) | **99.62%** (2,353/2,362) |
| **Exact equality** | **95.47%** (2,255/2,362) |

Lines where the token counts disagreed: **0**, so every comparison is a genuine
pairing rather than a skipped case.

**The recorded 100% came from a test that could not fail.** 92% of the
mismatches (98 of 107) are the in-context form having *exactly one more
character* — a word-final `ɨ` — than the standalone form:

| Word | Standalone | In context |
| --- | --- | --- |
| እዞም | `ʔɨzom` | `ʔɨzomɨ` |
| ኣዕኑድ | `ʔaʕɨnud` | `ʔaʕɨnudɨ` |
| ማለት | `malət` | `malətɨ` |
| ናጽነት | `nat͡sʼɨnət` | `nat͡sʼɨnətɨ` |

**Appending a character leaves the shorter string a substring of the longer
one.** A containment test is structurally blind to the single most common way
this measurement can fail.

### C2 — CONFIRMED

**0 of 1,565** unique words changed when a character was prepended. DEC-023 was
right about this one: **left context is genuinely inert.**

### C3 — REFUTED, and the mechanism is worse than a boundary effect

The obvious reading of C1 is "the final character is sensitive to what follows."
**That is not what is happening.** Local context does not predict it:

- word alone → `ʔɨzom`
- word + following word → `ʔɨzom`
- word + the next 8 words → `ʔɨzom`
- previous 6 words + word + next → `ʔɨzom`
- **the whole 128-word line → `ʔɨzomɨ`**

Section 5 of `run.py` isolates it. For the word at **index 72** of a 128-word
line, replacing the line's **first** word — 72 words away — flips the result:

| First word | Token 72 |
| --- | --- |
| `ልኡላውነት` (7 chars) | `ʔɨzomɨ` |
| `ኩሉ` (3 chars) | `ʔɨzom` |

**A one-word edit 72 positions away changes the output.** The behaviour is
fully deterministic — byte-identical across five calls and across a fresh
`Epitran` instance — but it is **not a function of local linguistic context**,
so it cannot be stated as a phonological rule. It is a property of the whole
input string.

## What this changes

**DEC-023's decision survives; its stated evidence does not.** Word-level
alignment was the right call, and this result makes the case *stronger* than the
original argument did:

- The original argument was "word-by-word is lossless, so we lose nothing."
  **That is false** — word-by-word differs from whole-text output on **4.53%** of
  word tokens.
- The better argument is that **whole-text output is not reproducible from the
  word**. A word's in-context transliteration depends on text arbitrarily far
  away, so an API built on it could not return a stable answer for a word, and
  its output would change when unrelated parts of a request changed.
  Word-by-word makes the result **a function of the word alone**, which is what
  an API contract requires.

**The `lru_cache` on `transliterate_word` is sound**, because it caches the
standalone form and the standalone form is deterministic (C2, and experiment
004's H2).

**What we cannot say** is which output is phonologically *correct*. Word-final
6th-order characters in Tigrinya are usually bare consonants, which would favour
the standalone form — but that is a claim about Tigrinya, not about epitran, and
**we have no native-speaker validation** (the standing gap DEC-007 flagged).
This experiment establishes that the two disagree and that one of them is
unpredictable; it does **not** establish which is right.

## Reproduce

```bash
pip install epitran==1.35.2
python3 run.py
```

Deterministic; `results.json` is byte-identical across runs (verified).

## Limits

- **73 lines, 2,362 word tokens.** The direction is unambiguous (107 mismatches,
  a single dominant shape) but the 4.53% rate is corpus-specific.
- **The mechanism is not explained.** It is offset- or length-sensitive inside
  epitran; reverse-engineering that is a dependency detail, not a design input.
  What matters here is that it is *not predictable from local context*.
- **No correctness claim.** Neither form is validated against a speaker.
