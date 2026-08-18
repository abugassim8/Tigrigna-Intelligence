# Summary: State of Play — What We Are Cleared to Build vs What We Decided to Build

| Field | Value |
| --- | --- |
| **Summary ID** | `013-state-of-play` |
| **Full report** | `docs/research/reports/12_master_blueprint/001-state-of-play-and-critical-path.md` |
| **Date** | 2026-08-03 |
| **Status** | Current |
| **Confidence** | High — an audit of our own record, not new external research |

**One-line answer:** **P-4 clears exactly one capability — translation — and
DEC-006 explicitly excludes it from the minimum viable platform**, because
DEC-005's evaluation anchors cover capabilities the MVP does not contain. The
next research is evaluation for the primitives, and it is blocked by nothing.

---

## Key Findings

- **⭐ We are cleared to build exactly one capability, and it is the one the MVP
  excludes.**

  | Capability | Metric validated? | In DEC-006 MVP? |
  | --- | --- | --- |
  | **Translation** | ✅ **Yes** (DEC-009) | ❌ **excluded** |
  | Embeddings · Tokenization · Morphology · Transliteration | ❌ TBD | ✅ **yes** |

  **Validated metrics: 1. Inside the MVP: 0.** Translation has a metric, a model,
  a runtime and a tier; **every capability DEC-006 named has no way to tell
  whether it works.**

- **The root cause is DEC-005, not bad sequencing.** It named FLORES-200 (translation)
  and TiQuAD (QA) as anchors. **Neither evaluates tokenization, morphology,
  transliteration, or embeddings.** DEC-005 and DEC-006 were taken the same day;
  each was sound alone, and **together they left the MVP unmeasurable.** Not a
  contradiction — two decisions that do not compose. → **DEC-021**

- **What is true, versus designed, versus assumed:**

  | Layer | Examples |
  | --- | --- |
  | **Measured** | 1.957× expansion · BLEU 1.08× harsher · raw Ge'ez wins 10/10 · TiQuAD contamination confirmed · 3/3 experiments reproduce |
  | **Verified fact** | Every licence in the stack · **0** cleanly-licensed parallel sentences |
  | **Arithmetic** | Tiers 72/191/1,593 MB · 22× saving · LoRA 23× cheaper |
  | **Designed, unbuilt** | Harness · tiers · services — **all of it** |
  | **Assumed** | MADLAD's quality · cold start · COMET · DEC-002's user model |

  **80% of summary claims carry `[verified]`**, 20% `[reported]` — the latter
  almost all paper-derived figures behind the egress block.

- ~~**Nothing has been built.**~~ ⚠️ **Superseded 2026-08-03.** Tier 0 and the
  evaluation harness are now built: **two packages, 75 tests passing**.

  | Package | Status |
  | --- | --- |
  | `services/primitives` | ✅ normalisation, tokenization, transliteration. **Morphology blocked on A-07** |
  | `services/evaluation` | ✅ chrF+BLEU, variety-scoped, CIs by default. **No model run through it (A-09)** |

  **The tests caught two shipping bugs**: byte-level BPE emitted `[UNK]` on
  unseen text (breaking DEC-022's verbatim-surface guarantee), and sacrebleu's
  numpy `float32` broke JSON persistence. Both would have surfaced in
  production.

- **The critical path does not start where you would guess:**

  | # | Step | Blocked by |
  | --- | --- | --- |
  | ~~1~~ | ~~Evaluation for the MVP primitives~~ ✅ **done** (DEC-023) | — |
  | 2 | Confirm DEC-002 (**A-02**) | a human |
  | 3 | `fgaim` licences (**A-01**) | a human |
  | 4 | HornMorpho (**A-07**) | a human |
  | 5 | Build Tier 0 | steps 1, 4 |

  **Step 1 needs no permission, licence, egress, or decision** — and gates
  everything.

- **The blockers are not technical.** Three blocking actions — **A-01**, **A-02**,
  **A-05** — all need a person; **none is resolvable by research.** Plus **A-15**,
  a one-command CI install leaving six rules unenforced. Money is not the
  constraint (52.6 GB-h/month); **attention is.**

- **What the method produced**, worth transferring:
  1. **Measurement beat citation.** Egress blocked the literature, so claims got
     measured — and came out sharper. "BLEU is unsuitable for morphologically
     rich languages" became "**BLEU is 1.08× harsher**."
  2. **Pre-committed thresholds caught overclaiming twice** — Experiments 002 and
     003. Without them, both would have been written up as successes.
  3. **Policy without mechanism fails silently** — DEC-008, ignored three months,
     found by measurement. Structural, not careless.
  4. **Metadata is evidence, not truth** — HF tags wrong on 2 of 4 datasets;
     PyPI's legacy field wrongly reads "NOT STATED" for five packages.
  5. **Corrections improved the evidence** rather than weakening conclusions.

## Important Decisions

| Decision | ID | Status |
| --- | --- | --- |
| Extend evaluation anchors to the MVP primitives; next research is Tier 0 evaluation | DEC-021 | Accepted |

## Rejected Alternatives

| Alternative | Rejected because |
| --- | --- |
| Build translation next, since it is the cleared capability | Follows P-4 but abandons DEC-006's reasoning; the primitives gap is our differentiator and translation has a strong incumbent |
| Revisit DEC-006 to make translation the MVP | The gap-filling argument still holds, and `05_architecture` independently confirmed the MVP is also the cheap tier (191 MB vs 1,593 MB) |
| Build MVP primitives without evaluation | Violates **P-4** directly — the rule exists because unmeasurable capabilities cannot be improved or defended |
| Treat the mismatch as a sequencing accident | It is structural: DEC-005's anchors do not cover DEC-006's platform, and would not have started to at any point |

## Important Numbers

| Metric | Value | Basis |
| --- | --- | --- |
| Research domains complete | **11 of 12** | `[verified]` |
| Decisions recorded | **21** — 1 proposed, 1 refuted, 1 not in force | `[verified]` |
| **Capabilities with a validated metric** | **1** | `[verified]` |
| **…inside DEC-006's MVP** | **0** | `[verified]` |
| Verified share of summary claims | **80%** | `[verified]` |
| Experiments reproducing byte-identically | **3 of 3** | `[verified]` |
| Blocking actions, all needing a human | **3** | `[verified]` |
| **Packages built** | **2** (75 tests passing) | `[verified]` |
| Shipping bugs caught by those tests | **2** | `[verified]` |

## Recommended Next Steps

1. **Research evaluation for the MVP primitives** (DEC-021) — blocked by nothing,
   gates everything.
2. **Send A-01 and A-05, and answer A-02.** Three messages and one decision
   unblock the rest.
3. **Install CI (A-15)** — one command.
4. **`07_api_mcp`** once A-02 lands; it is the last unresearched domain.
5. **Then build Tier 0** — 72 MB, and everything above depends on it.

## References

1. `docs/benchmarks/metrics.md` — the readiness audit's source
2. `docs/decisions/DECISIONS.md` — DEC-001…DEC-021
3. `ACTIONS.md` — the real risk register

---

**Open questions / uncertainty:** Will the primitives even *have* usable metrics —
morphology and tokenization are much harder to evaluate than translation, and no
Tigrinya benchmark exists for either. Is DEC-002 right? Is MADLAD any good?
