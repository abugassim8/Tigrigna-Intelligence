# Summary: Evaluating Tigrinya Embeddings Without a Similarity Benchmark

| Field | Value |
| --- | --- |
| **Summary ID** | `016-embedding-evaluation` |
| **Full report** | `docs/research/reports/08_evaluation/003-embedding-evaluation-without-gold-data.md` |
| **Date** | 2026-08-19 |
| **Status** | Current |
| **Confidence** | High on the method; **nothing run against a neural model** (A-09) |

**One-line answer:** **Six properties are measurable with no annotation**, and a
free lexical baseline **passes the mechanical ones and fails orthographic
invariance at 0.2232** — so the neural model has a specific, measurable job
rather than a vague expectation of being better.

---

## Key Findings

- **⚠️ Tier 1 is blocked on egress, not licensing — the plan said otherwise.**
  `READINESS_PLAN.md` and `ACTIONS.md` both routed A-01 → Tier 1.
  **`tiroberta-bi-encoder` and `tielectra-bi-encoder` are Apache-2.0**, and
  A-01's own text says so. **Only A-09 blocks embeddings.** A dependency graph
  that overstates a blocker makes the wrong thing look urgent.

- **The standard method is impossible here, and one goal is unreachable.**
  Bitext retrieval needs one shared vector space; `tiroberta-bi-encoder` is
  monolingual, so embedding English would measure tokenizer collisions. Beyond
  evaluation: **G-4, cross-language retrieval, is not reachable with this model
  at all** — it needs a different model class, which is an undecided Tier 1
  scope question.

- **⭐ Six properties need no annotation** — the DEC-023 method transferred:

  | | Property | Catches |
  | --- | --- | --- |
  | **E1** | **Orthographic invariance** | An encoder treating ጸ/ፀ as different words |
  | E2 | Self-retrieval | Broken pooling, mis-wired index |
  | E3 | Discrimination | Near-constant vectors |
  | E4 | Corruption monotonicity | Insensitivity to content |
  | E5 | Order sensitivity *(advisory)* | Bag-of-words behaviour |
  | E6 | Length independence *(advisory)* | Similarity tracking length |

- **⭐ E1 is Tigrinya-specific and the reason this is not a generic suite.**
  Mixing the two tsade series is **normal practice, not error** — 1.0–3.8% in
  Eritrean newspapers. An encoder that separates them fails retrieval
  **silently, for whichever spelling the user did not type.** No error surfaces.

- **The lexical floor is not a formality.** Character n-gram TF-IDF — no
  weights, no GPU — was measured:

  | Property | Baseline | Floor |
  | --- | ---: | ---: |
  | **E1 invariance** | **0.2232** | **0.80** ❌ |
  | E2 self-retrieval | 1.0000 | 1.00 ✅ |
  | E3 discrimination | 1.0000 | 0.95 ✅ |
  | E4 monotonicity | 1.0000 | 1.00 ✅ |

  **It is a working encoder that cannot handle Tigrinya spelling variation.**
  That is exactly the job the 124.6M-parameter model has to do to earn roughly
  doubling Tier 1's footprint (**P-6**, **P-7**).

- **⚠️ The first version of E1 could not fail.** Measured at *sentence* level,
  one substituted character sits among hundreds of features, and a deliberately
  spelling-blind control scored **identically** to a correct one — 0.9282 both.
  Moved to word level, where a correct encoder scores **1.0000** and the
  baseline **0.2232**. Found by planting the failure, which is now the sixth
  such case in this project.

## Important Decisions

| Decision | ID | Status |
| --- | --- | --- |
| Embeddings evaluated intrinsically, against a mandatory lexical floor | DEC-026 | Accepted |

## Rejected Alternatives

| Alternative | Rejected because |
| --- | --- |
| FLORES+ bitext retrieval | **Impossible** — the model is monolingual; would measure tokenizer collisions |
| Build a Tigrinya STS set first | Months (A-006) when six properties are measurable today with none |
| Adopt a multilingual encoder instead | Would enable G-4, but is an undecided scope change abandoning a cleared model. **Open, not rejected** |
| Ship embeddings unevaluated | Violates P-4 where failure is least visible |

## Important Numbers

| Metric | Value | Basis |
| --- | --- | --- |
| **Baseline E1 invariance** | **0.2232** (floor 0.80) | `[verified]` |
| Correct encoder E1 | **1.0000** | `[verified]` |
| Baseline E2/E3/E4 | **1.0000** each | `[verified]` |
| Order sensitivity of char n-grams | **0.2246** — not 0 | `[verified]` |
| Affected words in corpus | **10** | `[verified]` |
| Neural model measurements | **0** — blocked by A-09 | `[verified]` |

## Recommended Next Steps

1. **A-09** — the only blocker. The bar is already recorded; running it is one
   script.
2. **Add a sentence-pair sheet to `validation/`** once A-13 returns, turning one
   reviewer session into a minimal Tigrinya STS set.
3. **Decide G-4's model class.** Cross-language retrieval needs a multilingual
   encoder; nobody has taken that decision.
4. **Re-derive the floors** once a real model has been measured — they are
   provisional, from one 30-sentence corpus.

## References

1. `experiments/008-embedding-baseline/` — the floor
2. `services/evaluation/src/tigrinya_eval/embeddings.py` — the six checks
3. DEC-023 — the method this extends

---

**Open questions / uncertainty:** Does `tiroberta-bi-encoder` beat a free
lexical baseline at all? Is its subword vocabulary invariant to ጸ/ፀ? Does G-4
justify a second model class, and if so is Tier 1 still one tier?
