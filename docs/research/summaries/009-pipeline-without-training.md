# Summary: The ML Pipeline for a Project That Decided Not to Train

| Field | Value |
| --- | --- |
| **Summary ID** | `009-pipeline-without-training` |
| **Full report** | `docs/research/reports/06_ml_pipeline/001-pipeline-without-training.md` |
| **Date** | 2026-08-13 |
| **Status** | Current |
| **Confidence** | High — two self-claims tested; one held, one did not |

**One-line answer:** Our pipeline is **acquire → screen → convert → evaluate →
release**, with training as a contingency branch — and testing two claims this
repo makes about itself found that reproducibility holds where it was designed
in, while **DEC-008's screening gates had no implementation at all.**

---

## Key Findings

- **This is not a training pipeline, and naming it correctly changes the design.**
  A-004 avoids training, A-005 prefers adaptation, DEC-003 adopts models, DEC-011
  adopts a checkpoint, and A-002's 40M-token ceiling makes from-scratch
  implausible. A training-centred design would invest in labelling, experiment
  tracking, and checkpoint management — **none of which we need** — while
  under-investing in the two stages that have actually consumed effort:
  **screening and evaluation.**

- **Reproducibility tested by re-running everything and byte-comparing:**

  | Experiment | Machine-checkable artefact | Byte-identical on re-run |
  | --- | --- | --- |
  | 001 — epitran | ❌ **none** | **cannot be checked** |
  | 002 — fertility | ✅ `results.json` | ✅ **identical** |
  | 003 — metrics | ✅ `results.json` | ✅ **identical** |

  **P-5 holds for 002/003 and cannot be evaluated for 001**, whose results exist
  only as prose. If `epitran` changed behaviour, nothing would detect it — and
  **DEC-007's amended form rests on Experiment 001's numbers.** Reproducibility
  was achieved by making the artefact mandatory, not by intending to be careful.
  → **DEC-016**

- **⭐ DEC-008 was policy without mechanism** `[verified]`. It mentions screening
  seven times; `scripts/data_processing/` contained **zero files**; and screening
  logic had been **reimplemented in all three experiment scripts, differently
  each time.** A gate that exists only in prose is not a gate.

  `scripts/data_processing/screen_dataset.py` now implements all four gates —
  licence, quality, variety, contamination — with a machine-readable record and
  a pipeline-usable exit status. → **DEC-015**

- **Validated against known results, with a positive control:**

  | Test | Input | Result |
  | --- | --- | --- |
  | A | known-corrupted sample | ✅ **FAIL** quality, 0.289% foreign |
  | B | clean corpus vs FLORES+ | ✅ **CLEARED** |
  | C | FLORES+ `tir` | ✅ independently found Exp-003's mixed orthography |
  | D | **eval set against itself** | ✅ **652 shared 8-grams detected** |

  **Test D is the one that matters:** without a positive control, "no
  contamination found" is indistinguishable from "the detector is broken."

- **Two deliberate design choices.** **Licence is asserted, never detected** — a
  licence is a legal fact, not a property of bytes. **Contamination fails
  closed** — supplying no eval set is a FAIL, because silence must not read as
  clearance.

- **⚠️ Building the tool corrected one of my own earlier claims.**

  | Source | ER | ET | ET share |
  | --- | ---: | ---: | ---: |
  | `tlt_000` — Eritrean news | 75 | 3 | **3.8%** |
  | `haddas` — *Hadas Ertra* | 95 | 1 | **1.0%** |
  | **FLORES+ `tir`** | 90 | 16 | **15.1%** |

  **Orthographic mixing appears in every source, including unambiguously Eritrean
  ones** — so mixing *per se* is normal practice, not a defect. Experiment 003
  called FLORES+ "orthographically inconsistent with itself," which was true as a
  fact but **implied an anomaly that the baseline does not support.**

  **This strengthens DEC-010 rather than weakening it:** the observation now has
  a control, and FLORES+'s ET rate is **~4–15× Eritrean sources**. With the
  lexeme evidence, the Ethiopian-leaning signal holds on *better* evidence.

- **Stage 3 (convert) is the bottleneck.** Evaluating MADLAD, comparing against
  NLLB, and publishing the first Tigrinya MADLAD number all wait on a CTranslate2
  conversion that cannot run without model weights (**A-09**).

## Important Decisions

| Decision | ID | Status |
| --- | --- | --- |
| Screening is executable and mandatory; datasets carry a screening record | DEC-015 | Accepted |
| Every experiment emits a machine-checkable artefact | DEC-016 | Accepted |

## Rejected Alternatives

| Alternative | Rejected because |
| --- | --- |
| A training-centred pipeline | We decided not to train (A-004, A-005, DEC-003); it would invest where there is no work and under-invest where the work is |
| Leaving DEC-008 as prose policy | Measured outcome: screening was reimplemented three times, differently, and enforced by nobody |
| Auto-detecting licences | A licence is a legal fact about a dataset, not a property of its bytes |
| Passing contamination when no eval set is given | Silence would read as clearance — the exact failure DEC-008 exists to prevent |
| An automated column-scramble verdict | Not reliably separable from unusual prose; a false verdict is worse than a review flag |

## Important Numbers

| Metric | Value | Basis |
| --- | --- | --- |
| Experiments reproducing byte-identically | **2 of 3** | `[verified]` |
| Experiments with no machine-checkable artefact | **1** (001) | `[verified]` |
| Ad-hoc screening implementations before DEC-015 | **3** | `[verified]` |
| Files in `scripts/data_processing/` before this work | **0** | `[verified]` |
| Contamination positive control | **652 shared 8-grams** | `[verified]` |
| ET-marker share: Eritrean sources vs FLORES+ | **1.0–3.8%** vs **15.1%** | `[verified]` |

## Recommended Next Steps

1. **Give Experiment 001 a `results.json`** and bring it under DEC-016 — DEC-007
   depends on numbers nothing currently re-checks.
2. **Run `screen_dataset.py` over every dataset already in the inventory** and
   commit the records.
3. **Unblock Stage 3** — CTranslate2 conversion needs weights (**A-09**).
4. **Wire screening into CI** so a dataset cannot be added without a record.
5. **Extend contamination detection** beyond exact n-grams if paraphrase or
   translation contamination becomes a concern.

## References

1. Re-run and byte-comparison, 2026-08-13 `[verified]`
2. `scripts/data_processing/screen_dataset.py` — the mechanism
3. `docs/research/summaries/006-metric-validity-and-harness.md` — corrected here

---

**Open questions / uncertainty:** Does CTranslate2 conversion actually succeed?
Will exact-match n-grams catch the contamination that matters, or is paraphrase
overlap the real risk? Is the 0.1% foreign-character threshold right, or tuned to
one corpus?
