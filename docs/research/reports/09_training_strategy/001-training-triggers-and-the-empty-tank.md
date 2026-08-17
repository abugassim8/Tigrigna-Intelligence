# Training Strategy: The Contingency Plan Has No Fuel

| Field | Value |
| --- | --- |
| **Report ID** | `001-training-triggers-and-the-empty-tank` |
| **Domain** | `09_training_strategy` |
| **Stage** | Scout → Analyst → Architect |
| **Date** | 2026-08-03 |
| **Status** | Accepted |
| **Summary** | `docs/research/summaries/010-training-triggers.md` |
| **Related decisions** | **DEC-017**; engages A-004, A-005, A-002, A-008, DEC-011, DEC-008 |

---

## Objective

Define the training strategy for a project that has decided not to train
(**A-004**, **A-005**, **DEC-003**, **DEC-011**). The useful content of this
domain is therefore not a training plan but **the conditions under which the
decision not to train would be overturned, and what we could actually do if it
were.**

---

## Finding 1 — ⛔ We have **zero** cleanly-licensed parallel training data

`[verified]` by auditing every dataset in the inventory against its licence and
its role:

| Dataset | Size | Licence | Trainable? | Why not |
| --- | --- | --- | --- | --- |
| `michsethowusu/english-tigrinya` | **1,400,000 pairs** | **NONE** | ⛔ | Unlicensed (**A-05**) |
| FLORES+ `tir` | 1,012 sents | CC-BY-SA-4.0 | ⛔ | **Is our evaluation anchor** — training on it is contamination (DEC-008) |
| TiQuAD | 6,508 q | CC-BY-SA-4.0 | ⛔ | Upstream copyright unresolved (**A-06**); also an anchor |
| `farefaine/tigrinya-pretraining` | 52,100 rows | **NONE** | ⛔ | Unlicensed **and** confirmed contaminated |
| `mewaeltsegay/TigrinyaLargeText` | 12,400 docs | **MIT** | ✅ mono | Encoding corruption found (Exp 002) |
| `SIMBA9657/haddas` | 2,653 docs | **CC-BY-SA-4.0** | ✅ mono | PDF column-scrambled — words survive, sentences do not |

**Parallel data legally usable for translation fine-tuning: 0 sentences.**
**Monolingual data legally usable: 15,053 documents**, both corpora carrying
documented defects.

**This is the finding that matters, and it is not a compute problem.** Translation
fine-tuning is blocked on **licensing**, not on method, hardware, or expertise.

## Finding 2 — ⚠️ Therefore the fallback from DEC-011 is currently unavailable

**DEC-011 adopted MADLAD-400-3B with zero quality measurement.** That was the
right call on the evidence — it is the only Apache-2.0 model covering Tigrinya at
a servable size — but it was explicitly made on licensing and size, not quality.

So the most likely trigger for training is: **MADLAD turns out to be inadequate
at Tigrinya.**

**And if that happens, we cannot currently fix it.** Fine-tuning a translation
model requires parallel data, and Finding 1 says we have none we may lawfully
use. The contingency plan exists, and its tank is empty.

**This substantially raises the importance of A-05.** Getting a licence on the
1.4M en–ti pairs was previously filed as "the cheapest high-value action" — a
nice-to-have that would unlock a large corpus. It is now also **the only route to
a remedy if our adopted translation model fails.** A-05 is not an optimisation;
it is the insurance policy on DEC-011.

The `haddas` defect matters here too: **column-scrambling preserves words but
destroys sentences.** Continued pretraining tolerates that poorly, and MT
fine-tuning not at all. Of our 15,053 usable documents, the 2,653 from `haddas`
are unusable for anything sentence-level until repaired.

## Finding 3 — If triggered, LoRA is ~23× cheaper and that decides the method

Deterministic arithmetic on MADLAD-400-3B (2,940.4M parameters):

| Approach | Trainable params | ~Peak memory | Hardware class |
| --- | ---: | ---: | --- |
| Full fine-tune (fp16 + Adam) | **2,940M** | **32.9 GB** | Rented A100/H100 |
| **LoRA r=16 on a 4-bit base** | **7.4M** | **1.4 GB** | Consumer GPU |

**~23× less memory and ~400× fewer trainable parameters.** Under **A-008** that
is the difference between renting datacentre hardware and using a desktop
machine, which for a project optimising for low volume is decisive.

Tooling is available and permissively licensed `[verified]` from PyPI:
`peft` 0.20.0 (Apache), `accelerate` 1.14.0 (Apache), `datasets` 5.0.1
(Apache-2.0), `trl` 1.10.0, `bitsandbytes` 0.50.1.

**What is not estimated here: training time and resulting quality.** Neither can
be known without running it, and inventing figures would be exactly the error
this project keeps catching elsewhere.

## Finding 4 — From-scratch training is foreclosed, and it is worth saying so once

**A-002** puts the Tigrinya data ceiling at ~40M tokens — the corpus TiRoBERTa
was pretrained on, and the same order of magnitude as everything openly available
(Summary 005). Our *cleanly-licensed* share is a fraction of that.

Training a competitive translation model from scratch on that is not a resource
question; it is not possible. **This is recorded so nobody proposes it again**,
which is the function `rejected_options.md` exists to serve.

## Finding 5 — The adaptation ladder

Given the above, the strategy is a **ladder climbed only under measurement**,
cheapest rung first:

| Rung | Intervention | Training? | Blocked by |
| --- | --- | --- | --- |
| **0** | Decoding config, prompting, beam/length tuning | No | Nothing — always try first |
| **1** | Vocabulary / tokenizer adaptation | No gradients | Nothing |
| **2** | **LoRA adapter** on the adopted model | Yes, 7.4M params | **Parallel data (A-05)** |
| **3** | Full fine-tune | Yes, 2,940M params | A-05 **and** A-008 hardware |
| **4** | Train from scratch | — | **Foreclosed by A-002** |

**Rung 0 is not a formality.** Decoding parameters routinely move translation
quality more than people expect, they cost nothing, and they are reversible. No
proposal to climb higher should be entertained until rung 0 has been measured on
the DEC-009 harness.

→ **DEC-017.**

## Finding 6 — What would justify climbing

**A-004** places the burden of proof on whoever proposes training. Made concrete:

1. **A measured deficit.** The DEC-009 harness must show the adopted model failing
   a **pre-committed** threshold — not a subjective impression of poor output.
2. **Rung 0 exhausted**, with the measurement recorded.
3. **Lawful data**, screened through DEC-015's gates.
4. **A stated evaluation plan** for the trained artefact, including how it will be
   compared and how regression will be detected (DEC-016).
5. **Named maintenance owner.** A trained model must be kept alive, re-evaluated,
   and eventually retrained — A-004 calls this a permanent burden, correctly.

**No training without a number.** The failure mode this guards against is
training because it feels like progress.

## Limits of this report

- **No training was run.** Memory figures are arithmetic; time and quality are
  not estimated, because they cannot be known without the weights (**A-09**).
- **LoRA's 0.25%-trainable figure is a conventional r=16 attention-only
  configuration**, not tuned for this model. The order of magnitude is what the
  argument rests on.
- **Whether MADLAD is actually inadequate is unknown** — that is exactly the
  measurement DEC-011 flagged as missing and the harness has not yet run.
- **A-06 may change Finding 1.** If legal review reads TiQuAD's position
  permissively, or the NC-model question resolves, the trainable set changes.

---

## Decision arising

**DEC-017** — Training is gated behind an adaptation ladder and measured trigger
conditions; from-scratch training is foreclosed.

**Evidence:** licence audit `[verified]` against
`docs/research/summaries/005-corpus-inventory-and-contamination.md` and
`007-translation-model-selection.md`; PyPI metadata `[verified]` 2026-08-03.
