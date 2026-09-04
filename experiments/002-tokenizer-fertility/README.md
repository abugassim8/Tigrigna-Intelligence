# Experiment 002 — Tokenizer fertility on Tigrinya: does decomposition help?

| Field | Value |
| --- | --- |
| **Experiment ID** | `002-tokenizer-fertility` |
| **Date** | 2026-08-03 |
| **Author** | Research session (Claude Opus 5) |
| **Status** | **Complete — H3 REFUTED** |
| **Related report** | `docs/research/reports/02_linguistics/002-morphology-script-tokenization.md` |
| **Related decision** | **DEC-007** |

---

## Question

Does Epitran consonant–vowel decomposition **reduce** BPE token fertility on
Tigrinya text at matched vocabulary size — or does it increase it?

## Why this matters

**DEC-007 rests on an untested claim.** It adopts Epitran decomposition as the
tokenization substrate, and names token efficiency as the main defensible
benefit, while accepting a **1.97× symbol expansion** as the cost. That 1.97×
came from Experiment 001 — measured on **seven isolated words**. Neither the
expansion ratio on running text nor the token-efficiency benefit has ever been
measured.

If decomposition *increases* fertility, DEC-007's central justification fails and
the decision needs revising before any code depends on it.

## Hypotheses — pre-committed

**H1 — Expansion ratio holds on running text.**
Epitran decomposition expands character count by roughly the 1.97× measured on
isolated words.
*Prediction:* between **1.8× and 2.1×** on running text.

**H2 — Decomposition shrinks the symbol inventory.**
Ge'ez encodes consonant+vowel in a single codepoint, so running text uses
hundreds of distinct syllable characters; decomposed text should use a small
phoneme inventory.
*Prediction:* decomposed unique symbols **< 25%** of raw unique symbols.

**H3 — Decomposition lowers BPE fertility. ⭐ The load-bearing hypothesis.**
At matched vocabulary size, BPE trained on decomposed text yields **fewer tokens
per word** than BPE trained on raw Ge'ez text.
*Prediction:* `fertility(decomposed) < fertility(raw)`.

**Why H3 might fail, stated up front:** decomposition makes every sequence ~2×
longer in symbols, and BPE must then spend merge operations rebuilding the
syllables that Ge'ez already encodes for free. At matched vocab size that could
easily produce *worse* fertility. This is a genuine coin-flip, which is why it is
worth running.

## Success Criteria

| Outcome | Meaning for DEC-007 |
| --- | --- |
| **H3 confirmed** — decomposed fertility lower by any margin | Token-efficiency rationale **supported**; DEC-007 stands as written |
| **H3 refuted** — decomposed fertility equal or higher | Token-efficiency rationale **fails**; DEC-007 must be revised — decomposition would have to be justified on morphological-alignment grounds alone, or dropped |
| H1 refuted | The 1.97× cost figure in DEC-007 is wrong and must be corrected |
| H2 refuted | The compression argument for decomposition is wrong |

**Pre-committed:** a refuted H3 will be recorded and DEC-007 amended. Per **P-13**,
a negative result here is a successful experiment, not a failed one.

## Method

1. Assemble a Tigrinya corpus from **cleanly-licensed** sources only —
   `mewaeltsegay/TigrinyaLargeText` (MIT) and `SIMBA9657/haddas-tigrinya-corpus`
   (CC-BY-SA-4.0). No unlicensed data (**DEC-008**, **A-009**).
2. **Screen the corpus for encoding corruption before measuring.** Measuring
   fertility on corrupted text would produce a meaningless number.
3. Measure raw vs Epitran-decomposed character counts and symbol inventories
   (H1, H2).
4. Train byte-level BPE tokenizers on **identical text**, at **matched vocabulary
   sizes**, differing only in whether the input was decomposed (H3).
5. Measure fertility as **tokens per whitespace-delimited word**, the standard
   definition, on held-out text.

**Controls:** identical training text, identical vocab size, identical BPE
implementation and settings. The only variable is decomposition.

## Known limitations — stated before running

- **Corpus size is constrained by egress policy.** `huggingface.co` is blocked
  (403 CONNECT, org policy), so bulk parquet download is impossible; text can
  only be obtained row-by-row through the HF MCP tool. The corpus is therefore
  **small**, and absolute fertility figures will not be corpus-representative.
- **The controlled comparison is still valid.** H3 compares two tokenizers
  trained on *the same* text, so the direction of the difference is meaningful
  even when the absolute numbers are not. Magnitudes should be treated as
  indicative; **direction** is the finding.
- No comparison against off-the-shelf tokenizers (XLM-R, mBERT) is possible —
  their vocabularies live on the blocked domain.

## Reproduce

```
pip install epitran==1.35.2 tokenizers==0.23.1
python3 run.py
```

Deterministic; no seed required. Corpus committed alongside for exact
reproduction.

---

## Results

| Hypothesis | Result |
| --- | --- |
| **H1** — expansion ratio 1.8–2.1× on running text | ✅ **CONFIRMED** — 1.957× |
| **H2** — decomposed inventory < 25% of raw | ✅ **CONFIRMED** — 22.6% |
| **H3** — decomposition lowers fertility ⭐ | ❌ **REFUTED** — it *raises* fertility in **10/10** configurations |

### Corpus and screening

991 words / 4,826 characters from two cleanly-licensed sources. **Small** — see
Limitations. Type/token ratio **0.622**: 616 unique forms in 991 tokens, which is
itself a striking illustration of Tigrinya's morphological productivity (**A-003**).

Screening excluded one sample carrying mojibake (`'t'×3`, `'ñ'×1` embedded in
Ge'ez text). See "Data quality" below — this turned out to matter beyond this
experiment.

### H1 — expansion ratio: 1.957×

| Measure | Value |
| --- | --- |
| Raw characters | 3,699 |
| Decomposed characters | 7,240 |
| **Aggregate ratio** | **1.957×** |
| Per-word median | **2.000×** |
| Per-word mean | 1.979× |
| Per-word range | 1.50× – 3.50× |
| Words epitran failed on | **0** |

The 1.97× recorded in DEC-007 — extrapolated from **seven isolated words** —
holds on running text to within 0.7%. That was a lucky extrapolation, but it is
now measured rather than assumed, and **DEC-007's stated cost figure is correct**.

### H2 — symbol inventory: 155 → 35

Running Tigrinya used **155 distinct Ge'ez syllable characters**; decomposed, the
same text used **35 phonemes** — 22.6%. Decomposition genuinely compresses the
symbol inventory, exactly as the script's structure predicts.

### H3 — fertility: decomposition is consistently *worse* ⭐

Tokens per word on held-out text. Lower is better.

| vocab | char-level raw | char-level decomp | Δ | byte-level raw | byte-level decomp | Δ |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 500 | **2.492** | 2.819 | +0.327 | **3.251** | 3.543 | +0.291 |
| 1000 | **2.296** | 2.508 | +0.211 | **3.121** | 3.442 | +0.322 |
| 2000 | **2.261** | 2.432 | +0.171 | **3.106** | 3.417 | +0.312 |
| 4000 | **2.261** | 2.432 | +0.171 | **3.106** | 3.417 | +0.312 |
| 8000 | **2.261** | 2.432 | +0.171 | **3.106** | 3.417 | +0.312 |

**Raw Ge'ez wins every single configuration.**

Robustness — 5 rotating train/test folds, char-level, V=2000:

| fold | raw | decomposed | Δ |
| --- | ---: | ---: | ---: |
| 0 | 2.308 | 2.530 | +0.222 |
| 1 | 2.333 | 2.470 | +0.136 |
| 2 | 2.197 | 2.434 | +0.237 |
| 3 | 2.293 | 2.470 | +0.177 |
| 4 | 2.253 | 2.429 | +0.177 |

**Mean Δ +0.190 — decomposition worse in 5/5 folds.** About **8% worse** at
realistic vocabulary size.

---

## Analysis

### Why decomposition loses

**Ge'ez is already a compression scheme.** Each character encodes a
consonant+vowel pair in one codepoint. That is precisely the structure BPE would
otherwise have to *learn* — and Ge'ez supplies it for free, in the encoding.

Decomposition throws that away. It doubles the sequence length (H1: 1.957×) and
then makes BPE spend its merge budget rebuilding the very syllables the script
had already given it. The smaller symbol inventory (H2) is real but does not
compensate: a 35-symbol alphabet with 2× longer sequences loses to a 155-symbol
alphabet with short ones.

**The two confirmed hypotheses explain the refuted one.** H1 and H2 are not
consolation prizes — they are the mechanism. Decomposition buys inventory
compression at the price of length, and for BPE that trade is bad.

### An honest reading of the trend

The char-level gap *narrows* as vocabulary grows (+0.327 → +0.171) before
plateauing. A fair question is whether it would close, or reverse, on a large
corpus with a production-scale vocabulary. **This experiment cannot answer that.**
What it does show: the gap plateaus rather than trending to zero, and at
byte level it does not narrow at all (~+0.31 throughout). There is no evidence of
a crossover, but its existence at scale is not excluded.

### What this does and does not overturn

It refutes **one specific rationale**: that decomposition buys token efficiency.
It does **not** refute the morphological-alignment argument for decomposition —
that a phoneme-level representation aligns better with Tigrinya's root-and-pattern
morphology. That claim is untested and remains open.

But DEC-007 named token efficiency as *the main defensible benefit*. With that
gone, the decision's cost/benefit is **inverted**: decomposition now costs
1.957× expansion **and** ~8% worse fertility, in exchange for a benefit that has
not been demonstrated.

### Data quality — an unplanned finding

Both cleanly-licensed corpora have quality problems serious enough to report:

1. **`TigrinyaLargeText` contains encoding corruption.** One sampled article had
   systematic character insertion (`ብከኸምዚ` for `ብከምዚ`, `ይከኹን` for `ይኹን`),
   Latin mojibake (`ë ð ê ñ t`) inside Ge'ez words, and unrecoverable garbage
   runs (`ሽዘዘቕቐቦብቅቦtዘ`). Corrupted text inflates the apparent vocabulary with
   words that do not exist.
2. **`haddas-tigrinya-corpus` has PDF multi-column extraction scrambling.** Text
   from parallel newspaper columns is interleaved, so masthead fragments
   (`ፋክስ. 12749`, `ቍ.ሳ.ጶ. 247`) appear mid-sentence and clause order is
   destroyed. **Words survive; sentences do not.** Usable for fertility, which is
   word-level. **Not usable for anything sentence-level** — language modelling,
   MT, or syntactic work.

Neither dataset documents these issues. This sharpens **DEC-008**: screening must
cover *quality*, not just contamination and licensing. Our two clean-licence
corpora are the ones we can legally use, and both need repair work first.

## Conclusion

**H3 is refuted. DEC-007's token-efficiency rationale does not survive contact
with data.** Decomposition raises fertility by ~8% at realistic vocabulary size,
consistently across 10 configurations and 5 folds, at both char and byte level.

**Recommended action:** amend DEC-007. Decomposition should not be adopted *for
tokenization*. The Epitran-based alignment layer may still be worth building for
morphological analysis — where the phoneme representation is the point — but that
is now an untested claim that must be labelled as such, not a settled rationale.

**Cost of not having run this:** a tokenizer built on a stated efficiency benefit
that does not exist, discovered after the services depending on it were written.

**Meta-note (P-13):** this is the negative result the experiment was for. The
pre-committed criteria made it unambiguous — no post-hoc reinterpretation was
available, because the threshold was written down before the run.
