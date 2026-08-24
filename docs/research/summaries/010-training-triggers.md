# Summary: Training Strategy — The Contingency Plan Has No Fuel

| Field | Value |
| --- | --- |
| **Summary ID** | `010-training-triggers` |
| **Full report** | `docs/research/reports/09_training_strategy/001-training-triggers-and-the-empty-tank.md` |
| **Date** | 2026-08-17 |
| **Status** | Current |
| **Confidence** | High on the licence audit and cost arithmetic; **no training run** |

**One-line answer:** We have **zero cleanly-licensed parallel training data**, so
if the translation model we adopted without measuring turns out to be inadequate,
**we currently cannot fine-tune our way out of it** — which makes **A-05** the
insurance policy on DEC-011 rather than a nice-to-have.

---

## Key Findings

- **⛔ Parallel data legally usable for translation fine-tuning: 0 sentences**
  `[verified]` by auditing every dataset against licence *and* role:

  | Dataset | Size | Licence | Trainable |
  | --- | --- | --- | --- |
  | `michsethowusu/english-tigrinya` | 1.4M pairs | **NONE** | ⛔ unlicensed (**A-05**) |
  | FLORES+ `tir` | 1,012 | CC-BY-SA-4.0 | ⛔ **is our eval anchor** (DEC-008) |
  | TiQuAD | 6,508 q | CC-BY-SA-4.0 | ⛔ copyright unresolved (**A-06**); also an anchor |
  | `farefaine` | 52,100 | **NONE** | ⛔ unlicensed **and** contaminated |
  | `TigrinyaLargeText` | 12,400 docs | **MIT** | ✅ mono, encoding corruption |
  | `haddas` | 2,653 docs | **CC-BY-SA-4.0** | ✅ mono, column-scrambled |

  **Monolingual usable: 15,053 documents**, both corpora defective.
  **This is a licensing problem, not a compute problem.**

- **⭐ Therefore DEC-011's fallback is unavailable.** DEC-011 adopted MADLAD-400-3B
  **with zero quality measurement** — correctly, on licensing and size. So the
  most likely training trigger is *MADLAD turns out to be bad at Tigrinya*, and
  **if that happens we cannot currently fix it**, because fine-tuning needs
  parallel data we may not lawfully use.

  **A-05 is re-framed:** previously "the cheapest high-value action," it is now
  **the only route to a remedy if our adopted translation model fails.**

- **`haddas`'s defect bites here specifically.** Column-scrambling preserves words
  but destroys sentences — tolerable for word-level work, poor for continued
  pretraining, useless for MT. 2,653 of our 15,053 usable documents are
  effectively unavailable for anything sentence-level until repaired.

- **If triggered, LoRA is ~23× cheaper and that settles the method:**

  | Approach | Trainable | ~Peak memory | Hardware |
  | --- | ---: | ---: | --- |
  | Full fine-tune (fp16 + Adam) | 2,940M | **32.9 GB** | rented A100/H100 |
  | **LoRA r=16, 4-bit base** | **7.4M** | **1.4 GB** | consumer GPU |

  ~400× fewer trainable parameters. Under **A-008** that is the difference
  between renting datacentre hardware and using a desktop.

- **From-scratch training is foreclosed.** **A-002**'s ~40M-token ceiling is the
  whole open Tigrinya corpus; our cleanly-licensed share is a fraction. Recorded
  once, explicitly, so it is not proposed again.

- **The adaptation ladder** — climbed only under measurement, cheapest first:

  | Rung | Intervention | Training? | Blocked by |
  | --- | --- | --- | --- |
  | **0** | decoding config, prompting, beam/length | No | nothing — **always first** |
  | 1 | vocabulary / tokenizer adaptation | no gradients | nothing |
  | 2 | **LoRA adapter** | 7.4M params | **A-05** |
  | 3 | full fine-tune | 2,940M params | A-05 + hardware |
  | 4 | from scratch | — | **foreclosed (A-002)** |

  Rung 0 is not a formality: decoding parameters move MT quality more than people
  expect, cost nothing, and are reversible.

- **Tooling is available and Apache-licensed** `[verified]`: `peft` 0.20.0,
  `accelerate` 1.14.0, `datasets` 5.0.1, `trl` 1.10.0, `bitsandbytes` 0.50.1.
  **Nothing is blocked on tooling.**

## Important Decisions

| Decision | ID | Status |
| --- | --- | --- |
| Training gated behind an adaptation ladder and measured triggers; from-scratch foreclosed | DEC-017 | Accepted |

## Rejected Alternatives

| Alternative | Rejected because |
| --- | --- |
| Train a Tigrinya MT model from scratch | A-002's ~40M-token ceiling makes it not a resource question but an impossible one |
| Fine-tune on the 1.4M unlicensed pairs now | Unlicensed — P-9/A-009. Shipping the result would pass on rights we do not hold |
| Fine-tune on FLORES+ or TiQuAD | They are our evaluation anchors; training on them is contamination (DEC-008) and destroys our only measurement |
| Full fine-tune as the default adaptation | 23× the memory of LoRA for no measured benefit; fails A-008 |
| Train because output "looks bad" | A-004 puts the burden of proof on the proposer. **No training without a number** |

## Important Numbers

| Metric | Value | Basis |
| --- | --- | --- |
| **Cleanly-licensed parallel sentences** | **0** | `[verified]` |
| Cleanly-licensed monolingual documents | **15,053** | `[verified]` |
| …unusable for sentence-level work (`haddas`) | 2,653 | `[verified]` |
| Full fine-tune peak memory | **32.9 GB** | arithmetic |
| **LoRA r=16 peak memory** | **1.4 GB** | arithmetic |
| LoRA memory advantage | **~23×** | arithmetic |
| LoRA trainable-parameter reduction | **~400×** | arithmetic |

## Recommended Next Steps

1. **Escalate A-05.** It is now the insurance policy on DEC-011, not an
   optimisation. Without it there is no remedy if MADLAD underperforms.
2. **Measure MADLAD before anything else** — the trigger condition cannot be
   evaluated until the DEC-009 harness runs.
3. **Exhaust rung 0** (decoding configuration) and record the measurement before
   any training proposal is entertained.
4. **Repair or discard `haddas` for sentence-level use** — scrambling is
   detectable; whether it is repairable is not yet known.
5. **Re-audit after A-06.** Legal review could change what is trainable.

## References

1. `docs/research/summaries/005-corpus-inventory-and-contamination.md` — licences
2. `docs/research/summaries/007-translation-model-selection.md` — DEC-011
3. PyPI metadata for `peft`, `accelerate`, `trl` `[verified]` 2026-08-17

---

**Open questions / uncertainty:** Is MADLAD actually inadequate — unmeasured, and
the whole trigger rests on it. Is `haddas` repairable? Would A-06 change the
trainable set? How much parallel data would a useful LoRA actually need — a
question nobody can answer for Tigrinya from published work we can reach.
