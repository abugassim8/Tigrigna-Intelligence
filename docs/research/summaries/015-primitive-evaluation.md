# Summary: Evaluating the Primitives Without a Gold Standard

| Field | Value |
| --- | --- |
| **Summary ID** | `015-primitive-evaluation` |
| **Full report** | `docs/research/reports/08_evaluation/002-primitive-evaluation.md` |
| **Date** | 2026-08-18 |
| **Status** | Current |
| **Confidence** | High — measured on real text, reproduces byte-identically |

**One-line answer:** **Most of the primitives layer is evaluable with no
annotated data at all** — three of four intrinsic properties hold, so **P-4 is
satisfiable for Tier 0 today**. The fourth failed, and in failing found a **real
error in DEC-007 and DEC-022**: the surface↔analysis alignment they both require
must be **word-level, not character-level**.

---

## Key Findings

- **Primitives are unusual: most of their correctness is intrinsic.** Unlike
  translation, idempotence, determinism, reversibility, alignment integrity, and
  coverage are properties of the *function*, not agreement with a human. **Only
  accuracy needs gold data.**

- **Three of four hypotheses hold on real corpus text:**

  | Hypothesis | Prediction | Measured | Verdict |
  | --- | --- | --- | --- |
  | H1 — normalisation idempotent | 100% | **0 failures** | ✅ |
  | H2 — transliteration deterministic | 100% | **0 failures** | ✅ |
  | **H3 — character alignment recoverable** ⭐ | ≥ 99% | **23.89%** | ❌ |
  | H4 — tokenization losslessly reversible | ≥ 99% | **100.00%**, 0 `[UNK]` | ✅ |

  Coverage **100.00%** of Ethiopic letters. *(The 99.72% first reported was
  diluted by 5 Latin digits, which correctly pass through.)*
  Normalisation collapses **4** unique forms — independently matching
  Experiment 003's 4/496 on different text.

  **DEC-021's premise is supported: no benchmark needs building first.**

- **⚠️ H3's failure is a real error in two accepted decisions.** DEC-007 requires
  surface↔analysis offsets; DEC-022 made them an API contract clause. **Both
  assumed character-level alignment, which does not exist.**

  | Word | Whole-string | Per-char concat | Delta |
  | --- | --- | --- | ---: |
  | ሃገርነት | `haɡərɨnət` | `haɡərnət` | +1 |
  | ህላውአን | `hɨlawɨʔən` | `hlawʔən` | +2 |

  `ር` → `r` alone, but `rɨ` inside ሃገርነት. **Ge'ez 6th-order characters are
  ambiguous between "consonant + ɨ" and a bare consonant**, resolved from
  neighbours. Correct linguistics — and it means context supplies **1,375 of
  8,430 symbols, 16.3% of all output**.

- **⭐ The fix is granularity — but the measurement behind it was wrong.**
  ⚠️ **Corrected 2026-08-19, experiment 005.** This summary recorded that
  word-by-word transliteration loses nothing, citing "**1,639/1,639 (100%)**".
  **That figure came from a containment test** (`alone in in_context`), which
  cannot detect an *appended* character — and an appended word-final `ɨ` is
  **92%** of the real failures.

  | Test | Result |
  | --- | ---: |
  | Containment — what was actually measured | **99.62%** |
  | **Exact equality — what was claimed** | **95.47%** |

  **The decision survives on a better argument.** The running-text form is
  deterministic but **not a function of local context** — for a word at index 72
  of a 128-word line, replacing the line's *first* word flips the result. So it
  cannot serve an API contract, and word-by-word is right because it makes the
  answer depend on the word alone, **not** because the two agree. Prepending is
  genuinely inert (**0 of 1,565**), which is what makes the cache sound.
  → **DEC-023 Amendment 1**

- **What intrinsic evaluation does NOT do.** It catches **broken, not wrong** — a
  transliterator returning deterministically wrong phonemes passes H2 perfectly.

  | Capability | Intrinsic gives | Still needs gold data |
  | --- | --- | --- |
  | Normalisation | idempotence, collapse rate | is the collapse right? |
  | Transliteration | determinism, coverage, alignment | are the phonemes right? |
  | Tokenization | reversibility, fertility, UNK | are the boundaries useful? |
  | **Morphology** | *(would be)* consistency, coverage — **none of it measured** | **almost everything** |

  **Morphology is the honest gap** — but it is now **one capability needing
  annotation, not four.**

## Important Decisions

| Decision | ID | Status |
| --- | --- | --- |
| Primitive evaluation is intrinsic-first; alignment is word-level (corrects DEC-007, DEC-022) | DEC-023 | Accepted |

## Rejected Alternatives

| Alternative | Rejected because |
| --- | --- |
| Build a Tigrinya primitives benchmark before evaluating anything | Months of work, when three of four properties are measurable today with no annotation |
| Character-level surface↔analysis offsets | **Measurably impossible** — 23.89% alignable; context supplies 16.3% of output symbols |
| Accepting a tradeoff between alignment and phonology | **Refuted by measurement** — word-level gives exact alignment; the tradeoff framing was my error |
| Keeping the containment measurement | It cannot fail on an appended character, which is 92% of the failures — a check that cannot fail is not evidence (experiment 005) |
| Treating intrinsic properties as sufficient | They catch *broken*, not *wrong*; morphological accuracy still needs gold data and a native speaker |
| Skipping evaluation and building the primitives | Violates P-4 — and H3 shows exactly the kind of error that surfaces only when you check |

## Important Numbers

| Metric | Value | Basis |
| --- | --- | --- |
| Intrinsic properties holding | **3 of 4** | `[verified]` |
| **Character-level alignment rate** | **23.89%** | `[verified]` |
| Output symbols supplied by context | **1,375 / 8,430 (16.3%)** | `[verified]` |
| **Word transliteration preserved in context** | **95.47%** (was wrongly recorded as 100%) | `[verified]` |
| Prepending a character changes | **0 of 1,565** words | `[verified]` |
| Tokenization round-trip | **100.00%**, 0 `[UNK]` | `[verified]` |
| Transliteration coverage | **100.00%** of Ethiopic letters (99.72% figure counted digits) | `[verified]` |
| Forms collapsed by normalisation | **4** | `[verified]` |
| Capabilities still needing gold data | **1** (morphology) | `[verified]` |

## Recommended Next Steps

1. **Amend DEC-007 and DEC-022 to word-level spans.** *(Done in this pass.)*
2. **Fill `metrics.md`'s primitive rows** with the intrinsic checks. *(Done.)*
3. **Resolve HornMorpho (A-07)** — morphology's intrinsic properties could not be
   measured because the tool is unavailable.
4. **Design embeddings evaluation** — Tier 1, untested; `tiroberta-bi-encoder` is
   monolingual so FLORES+ bitext retrieval does not directly apply.
5. **Then build Tier 0.** P-4 is satisfied for it.

## References

1. `experiments/004-primitive-evaluation/` — the evidence
2. DEC-007 · DEC-021 · DEC-022 — the decisions this corrects and answers

---

**Open questions / uncertainty:** Are the phonemes actually *right* (needs a
native speaker)? Is HornMorpho usable at all? How do you evaluate a monolingual
embedding model with no Tigrinya similarity benchmark?
