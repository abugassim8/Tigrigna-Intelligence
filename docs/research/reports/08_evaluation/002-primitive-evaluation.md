# Evaluating the Primitives Without a Gold Standard — and the Alignment Error It Found

| Field | Value |
| --- | --- |
| **Report ID** | `002-primitive-evaluation` |
| **Domain** | `08_evaluation` |
| **Stage** | Scout → Analyst → Architect |
| **Date** | 2026-08-03 |
| **Status** | Accepted |
| **Summary** | `docs/research/summaries/015-primitive-evaluation.md` |
| **Related decisions** | **DEC-023**; answers DEC-021; **corrects DEC-007 and DEC-022** |
| **Experiment** | `experiments/004-primitive-evaluation/` |

---

## Objective

Answer **DEC-021**: how do you evaluate tokenization, normalisation,
transliteration, and morphology when **no Tigrinya gold standard exists for any
of them**?

**P-4** blocks every MVP capability behind evaluation, and the readiness audit
found **zero MVP capabilities with a validated metric**. The obvious response —
build a Tigrinya benchmark — is what **A-006** anticipated, and would take months.

**This report asks what is measurable for free first.**

---

## Finding 1 — Primitives are unusual: most of their correctness is intrinsic

Translation needs a reference because "good translation" is agreement with a
human. **Primitives are different.** Much of what makes them correct is a
property of the *function itself*:

| Property | Question | Needs gold data? |
| --- | --- | --- |
| **Idempotence** | `f(f(x)) == f(x)`? | ❌ no |
| **Determinism** | same input → same output? | ❌ no |
| **Reversibility** | `decode(encode(x)) == x`? | ❌ no |
| **Alignment integrity** | can offsets be derived? | ❌ no |
| **Coverage** | what fraction is handled? | ❌ no |
| **Accuracy** | is the analysis *right*? | ✅ **yes** |

Only the last one needs annotation. **Experiment 004 tested the other five on
real corpus text.**

## Finding 2 — Three of four properties hold; P-4 is satisfiable for Tier 0 today

| Hypothesis | Prediction | Measured | Verdict |
| --- | --- | --- | --- |
| H1 — normalisation idempotent | 100% | **0 failures** | ✅ |
| H2 — transliteration deterministic | 100% | **0 failures** | ✅ |
| **H3 — character alignment recoverable** ⭐ | ≥ 99% | **23.89%** | ❌ |
| H4 — tokenization losslessly reversible | ≥ 99% | **100.00%**, 0 `[UNK]` | ✅ |

**Coverage: 99.72%** of character tokens transliterated (4,273/4,285). The only
five pass-through characters are **Latin digits** — correct behaviour.

**Normalisation collapses 4 unique forms**, independently matching the 4/496
figure from Experiment 003 on different text.

**DEC-021's premise is supported: the primitives are evaluable now**, without
building a benchmark first.

## Finding 3 — ⚠️ H3's failure is a real error in two accepted decisions

**This is the finding that justifies the experiment.**

**DEC-007** requires "alignment offsets maintained between" surface and analysis
forms. **DEC-022** made those offsets an API contract clause. **Both assumed a
character-level alignment that does not exist.**

Character alignment fails because epitran inserts an epenthetic `ɨ` from context
spanning characters:

| Word | Whole-string | Per-character concat | Delta |
| --- | --- | --- | ---: |
| ሃገርነት | `haɡərɨnət` | `haɡərnət` | +1 |
| ህላውአን | `hɨlawɨʔən` | `hlawʔən` | +2 |

`ር` transliterates to `r` alone but `rɨ` inside ሃገርነት. **Ge'ez 6th-order
characters are ambiguous between "consonant + ɨ" and a bare consonant**, and
epitran resolves that from neighbours.

**This is correct linguistics, not a bug.** Context supplies **1,375 of 8,430
output symbols — 16.3%**. Character-level alignment would not lose a rounding
error; it would lose a sixth of the phonology.

## Finding 4 — The fix is granularity, not engineering — and my first reading was wrong

I initially framed this as a **tradeoff**: exact offsets *or* faithful phonemes.
**A follow-up measurement refuted that before it reached a decision record:**

- **A word's transliteration is preserved inside a sentence: 1,639/1,639
  (100.00%).**
- **Prepending a character changes 0 of 1,635 tokens.**

Epitran resolves epenthesis **within a word**, and nothing crosses word
boundaries. So transliterating **word by word gives full phonological fidelity
*and* exact alignment by construction** — the analysis form simply *is* the
concatenation of per-word outputs.

The residual 9.6% line-level mismatch is a **word-final `ɨ`** that whole-line
transliteration adds at whitespace (`mɨɡutatɨ` vs `mɨɡutat`) — a boundary
artefact, not a within-word difference.

**So the correction is precise and cheap: character offsets are impossible;
word-level spans are exact and lossless.** DEC-007 and DEC-022 asked for the
wrong *granularity*, not for something unachievable. → **DEC-023**

## Finding 5 — What intrinsic evaluation does not do

Stated plainly because it would be easy to oversell:

**Intrinsic checks catch *broken*, not *wrong*.** A transliterator that
deterministically returns the wrong phoneme passes H2 perfectly. Determinism,
idempotence, and reversibility are **necessary and nowhere near sufficient**.

What still needs gold data and a native speaker:

| Capability | Intrinsic gets you | Still needs annotation |
| --- | --- | --- |
| Normalisation | idempotence, collapse rate | **is the collapse right?** |
| Transliteration | determinism, coverage, alignment | **are the phonemes right?** |
| Tokenization | reversibility, fertility, UNK rate | **are the boundaries useful?** |
| **Morphology** | consistency, coverage | **almost everything** |

**Morphology is the honest gap.** Its accuracy is what A-006 anticipated needing
to build, and nothing here removes that. But it is now **one capability needing
gold data, not four** — which is what DEC-021 was trying to establish.

## Limits of this report

- **1,034 unique words** from four files. Property tests generalise better than
  score estimates, but the corpus is small.
- **Morphology is untested** — HornMorpho remains unresolved (**A-07**), so its
  intrinsic properties could not be measured at all.
- **Embeddings are untested.** They are Tier 1 and need a retrieval-style
  evaluation; `tiroberta-bi-encoder` is monolingual, so FLORES+ bitext retrieval
  does not directly apply. Left open.
- **No native-speaker validation**, so nothing here says the primitives are
  *right*.

---

## Decision arising

**DEC-023** — Primitive evaluation is intrinsic-first; surface↔analysis alignment
is **word-level**, correcting DEC-007 and DEC-022.

**Evidence:** `experiments/004-primitive-evaluation/` `[verified]` 2026-08-03,
reproducing byte-identically.
