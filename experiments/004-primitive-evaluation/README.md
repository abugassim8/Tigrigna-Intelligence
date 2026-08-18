# Experiment 004 — Can the MVP primitives be evaluated without a gold standard?

| Field | Value |
| --- | --- |
| **Experiment ID** | `004-primitive-evaluation` |
| **Date** | 2026-08-03 |
| **Author** | Research session (Claude Opus 5) |
| **Status** | **Complete — H3 REFUTED; the other three hold** |
| **Related report** | `docs/research/reports/08_evaluation/002-primitive-evaluation.md` |
| **Related decision** | **DEC-021**; tests **DEC-007**'s alignment requirement and **DEC-022**'s offset contract |

---

## Question

**P-4** blocks every MVP capability behind evaluation, and **no Tigrinya gold
standard exists** for tokenization, morphology, or transliteration. So: **how much
of the primitives layer can be evaluated with no annotated data at all?**

## Why this matters

**DEC-021** exists because the readiness audit found **zero MVP capabilities with
a validated metric**, while translation — which DEC-006 excludes — has one. The
obvious fix is "build a Tigrinya benchmark," which **A-006** anticipated and which
would take months.

**Before accepting that cost, it is worth asking what is measurable for free.**
Primitives are unusual: unlike translation, much of their correctness is
**intrinsic** — properties of the function itself rather than agreement with a
human. Idempotence, determinism, reversibility, and alignment integrity need no
reference data.

If most of Tier 0 can be evaluated intrinsically, **P-4 is satisfiable now** and
the gold-standard work shrinks to the part that genuinely needs it.

## Hypotheses — pre-committed

**H1 — Orthographic normalisation is idempotent.**
`normalise(normalise(x)) == normalise(x)` for all corpus text. A normaliser that
is not idempotent is broken in a way that compounds silently.
*Prediction:* holds for 100% of inputs.

**H2 — Transliteration is deterministic.**
The same input always produces the same output within a process and across
repeated calls. *Prediction:* holds for 100%.

**H3 — Character-level alignment is recoverable. ⭐**
**DEC-007 requires offsets between surface and analysis forms; DEC-022 makes them
an API contract clause.** Both assume alignment is *computable*. Test:
transliterating a string whole equals concatenating per-character
transliterations — if so, offsets can be derived by summing per-character output
lengths.
*Prediction:* holds for ≥ 99% of corpus words.

**Why H3 might fail:** epitran maps one Ge'ez character to a *variable* number of
IPA symbols, and may apply context-sensitive rules across character boundaries.
If it does, **naive alignment is impossible** and DEC-007's alignment layer is
harder than recorded.

**H4 — Tokenization is losslessly reversible.**
`decode(encode(x)) == x` for corpus text. A tokenizer that cannot round-trip
cannot serve an API that must return surface forms verbatim (**DEC-022**).
*Prediction:* holds for ≥ 99% of inputs.

## Success Criteria

| Outcome | Consequence |
| --- | --- |
| **H1, H2, H4 hold and H3 holds** | **P-4 is satisfiable for Tier 0 today** via intrinsic checks; gold-standard work narrows to morphological *accuracy* only |
| **H3 fails** | **DEC-007's alignment layer and DEC-022's offset clause are both under-specified** — a significant correction, and alignment needs a real design rather than an assumption |
| H1, H2, or H4 fails | The relevant primitive is broken in a way that must be fixed before anything is built on it |

**Pre-committed:** whatever the result, `docs/benchmarks/metrics.md` gets primitive
rows filled in, and DEC-021's premise — that primitives are evaluable — is either
supported or refuted.

## Method

1. Corpus: the cleanly-licensed text already committed to `experiments/002` and
   `experiments/003` (MIT and CC-BY-SA-4.0).
2. Each hypothesis is a **property test over real text**, not a benchmark score.
3. Where a property fails, report **how often and on what**, not just a pass/fail.

## Known limitations — stated before running

- **Intrinsic properties are necessary, not sufficient.** A transliterator that
  deterministically returns the wrong phoneme passes H2. These checks catch
  *broken*, not *wrong* — and that distinction must survive into the write-up.
- **Morphological accuracy is deliberately out of scope.** It genuinely needs
  gold data; this experiment tests what does not.
- **No native-speaker judgement**, so nothing here validates linguistic
  correctness.

## Reproduce

```
pip install epitran==1.35.2 tokenizers==0.23.1
python3 run.py
```

Deterministic. Emits `results.json` per **DEC-016**.

---

## Results

| Hypothesis | Prediction | Measured | Verdict |
| --- | --- | --- | --- |
| **H1** — normalisation idempotent | 100% | **0 non-idempotent texts** | ✅ **CONFIRMED** |
| **H2** — transliteration deterministic | 100% | **0 non-deterministic words** | ✅ **CONFIRMED** |
| **H3** — character alignment recoverable ⭐ | ≥ 99% | **23.89%** | ❌ **REFUTED** |
| **H4** — tokenization losslessly reversible | ≥ 99% | **100.00%**, 0 `[UNK]` | ✅ **CONFIRMED** |

Corpus: 4 cleanly-licensed files, 1,635 words, 1,034 unique.

**Coverage:** 99.72% of character tokens transliterated (4,273/4,285). The only
5 distinct pass-through characters are **Latin digits** (`1 9 6 0 7`) — correct
behaviour.

**Normalisation:** 14 unique forms altered, **4 collapsed** — matching the
independent 4/496 figure from Experiment 003.

---

## Analysis

### H3's failure is the finding, and it is real phonology

Character-level alignment fails because **epitran inserts an epenthetic `ɨ` using
context that spans characters**:

| Word | Whole-string | Per-character concat | Delta |
| --- | --- | --- | ---: |
| ሃገርነት | `haɡərɨnət` | `haɡərnət` | +1 |
| ሃገርና | `haɡərɨna` | `haɡərna` | +1 |
| ህላውአን | `hɨlawɨʔən` | `hlawʔən` | +2 |

Per character: `ር` → `r` alone, but `rɨ` inside ሃገርነት.

**Ge'ez 6th-order characters are ambiguous between "consonant + ɨ" and a bare
consonant**, and epitran resolves that from neighbours. This is correct
linguistics, not a bug — and it means **offsets cannot be derived by summing
per-character output lengths**, which is what DEC-007 and DEC-022 both assumed.

Across unique words, context supplies **1,375 extra symbols out of 8,430 —
16.3% of all output**. Character-level alignment does not lose a rounding error;
it loses a sixth of the phonology.

### But word-level alignment is sound — and this is not a tradeoff

An initial reading framed this as "exact offsets *or* faithful phonemes."
**That was wrong.** Measured:

- **A word's transliteration is preserved inside a sentence: 1,639/1,639
  (100.00%).**
- **Prepending a character changes 0 of 1,635 tokens.**

So epitran sees a whole word and resolves epenthesis within it. Transliterating
**word by word gives full phonological fidelity AND exact alignment by
construction** — the analysis form simply *is* the concatenation.

The residual 9.6% line-level mismatch is a **word-final `ɨ`** that whole-line
transliteration adds at whitespace boundaries (`mɨɡutatɨ` vs `mɨɡutat`) — a
boundary artefact, not a within-word difference.

**So the correction is precise:** character offsets are impossible; **word-level
spans are exact and lossless.** DEC-007 and DEC-022 asked for the wrong
granularity, not for something unachievable.

### Intrinsic evaluation works, with one honest caveat

Three of four properties hold, on real text, with **no gold standard**. That
answers DEC-021's question: **P-4 is satisfiable for Tier 0 today.**

**But intrinsic checks catch *broken*, not *wrong*.** A transliterator that
deterministically returns the wrong phoneme passes H2 perfectly. These properties
are necessary and nowhere near sufficient, and morphological *accuracy* still
needs gold data and a native speaker.

## Conclusion

**Primitives can be substantially evaluated without any annotated data.**
Idempotence, determinism, reversibility, and coverage are all measurable now, and
all pass.

**H3's refutation is the valuable part.** It found a concrete, load-bearing error
in two accepted decisions: DEC-007 requires surface↔analysis offsets and DEC-022
made them an API contract clause, and **both assumed a character-level alignment
that does not exist.** The fix is not more engineering — it is choosing
**word-level spans**, which are exact.

**Meta-note (P-13):** the first framing of this result — a tradeoff between
alignment and phonology — was wrong, and the follow-up measurement (`0/1635`
context changes) refuted it before it reached a decision record.
