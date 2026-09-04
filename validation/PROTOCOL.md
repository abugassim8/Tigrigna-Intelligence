# How to review — Tigrinya reading check

**Thank you.** This takes about **25 minutes**, and you can stop at any point —
the sheets are ordered so the most useful questions come first, and a partly
finished sheet is still genuinely useful to us.

## What this is

We are building open tools for Tigrinya — spelling normalisation, word
splitting, and a system that writes out how a word is *pronounced*. The
pronunciation part is built on an automatic tool, and **nobody who speaks
Tigrinya has ever checked whether it is right.**

Automatic checks can tell us the tool is consistent. They cannot tell us it is
**correct**. That is the only thing we are asking you for.

**There are no trick questions and no right answers we are hoping for.** If
something looks wrong, saying so is the most valuable thing you can do.

## How to fill it in

1. Open the files in `sheets/` with Excel, Numbers, or Google Sheets. They will
   display Tigrinya correctly.
2. Type your answer in the empty column. Use the words listed at the top of each
   sheet — `yes`, `no`, `unsure`, and so on.
3. **`unsure` is a real answer.** Please use it rather than guessing; a guess
   looks identical to knowledge in our results, which makes it worse than a gap.
4. The `comment` column is optional. Anything you write there is useful,
   including "this is a rare word" or "depends on where you're from".
5. Send the files back however is easiest.

## Reading the pronunciation spellings

We write pronunciations with the International Phonetic Alphabet, so some
symbols will look unfamiliar. **You do not need to know the alphabet** — here is
every unusual symbol we use, with a Tigrinya example that contains it.

| Symbol | Example |
| --- | --- |
| `ɨ` | ሕቶ → `ħɨto` |
| `ə` | ለ → `lə` |
| `ʔ` | አ → `ʔə` |
| `ɡ` | ገ → `ɡə` |
| `ħ` | ሐ → `ħə` |
| `ʕ` | ዐ → `ʕə` |
| `t͡sʼ` | ጸ → `t͡sʼə` |
| `tʼ` | ጠ → `tʼə` |
| `qʰ` | ቐ → `qʰə` |
| `ʃ` | ሸ → `ʃə` |
| `d͡ʒ` | ጀ → `d͡ʒə` |
| `kʷ` | ኲ → `kʷi` |
| `t͡ʃʼ` | ጨ → `t͡ʃʼə` |
| `ɲ` | ኛ → `ɲa` |
| `t͡ʃ` | ቸ → `t͡ʃə` |
| `ɡʷ` | ጓ → `ɡʷa` |
| `xʷ` | ዃ → `xʷa` |
| `pʼ` | ጳ → `pʼa` |
| `qʷ` | ቋ → `qʷa` |
| `ʒ` | ዥ → `ʒ` |

The symbol **`ɨ`** is the one that matters most. It is the short "uh" sound that
appears between consonants — the sound in ሕቶ (`ħɨto`). **Sheet 1 is entirely
about when that sound is really there and when it is not.**

## The sheets

### 1 · Which is right? (25 items) — **the most important**

Two possible pronunciations of the same word. Our software produces different
answers depending on whether it reads the word on its own or inside a sentence,
and **we do not know which is correct.**

Answer `1`, `2`, `both`, `neither`, or `unsure`.

Usually the only difference is a short `ɨ` at the end. If both sound acceptable
to you, `both` is the right answer — that itself tells us something.

### 2 · Common words (35 items)

The words that appear most often. If our reading is wrong here, it is wrong in a
lot of places.

Answer `yes`, `no`, `close`, or `unsure`. If `no` or `close`, please write what
it should be in the `correction` column — in Tigrinya letters is completely
fine, you do not need to use the phonetic symbols.

### 3 · Spelling variants (14 items)

Tigrinya can write some sounds two ways — ጸ and ፀ, or ኣ and አ. For searching, we
treat both spellings as the same word.

- `same_word` — are these the same word? `yes` / `no` / `unsure`
- `acceptable` — is it acceptable for us to treat them as the same, or does it
  feel like we are **correcting** how someone chose to write? `yes` / `no` / `unsure`

**We would rather know now if this is offensive or wrong.**

### 4 · Random sample (40 items)

The same question as sheet 2, on randomly chosen words. Sheets 2 and 3 pick
difficult cases on purpose, so this is the only sheet that tells us how often we
are right **in general**.

### 5 · Which variety? (20 items)

Whole sentences. Does each read as **Eritrean** Tigrinya, **Ethiopian**
Tigrinya, or could it be `either`? And does it read like real, natural Tigrinya
at all (`natural`: `yes` / `no`)?

This matters because we never mix results from the two varieties, and we need to
know which one our test material actually is.

## Credit, licence, and your time

- **You will be credited by name** in the project, unless you prefer not to be.
- Your answers become part of an openly licensed project (documentation is
  CC-BY-4.0). Please tell us if that is a problem.
- The text is from openly licensed public sources: news and general prose.
- **If this should be paid work rather than a favour, say so.** Expert judgement
  in a low-resource language is scarce and undervalued, and we would rather be
  asked than assume.

## Questions we already know we cannot answer without you

- Is the short `ɨ` at the end of words real? (Sheet 1)
- Is collapsing ጸ/ፀ acceptable, or a correction? (Sheet 3)
- Is our test material Eritrean, Ethiopian, or mixed? (Sheet 5)

**If you only have ten minutes, sheet 1 is the one to do.**
