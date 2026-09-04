# Summary: Metric Validity for Tigrinya and the Evaluation Harness

| Field | Value |
| --- | --- |
| **Summary ID** | `006-metric-validity-and-harness` |
| **Full report** | `docs/research/reports/08_evaluation/001-metric-validity-and-harness.md` |
| **Date** | 2026-08-03 |
| **Status** | Current |
| **Confidence** | High — measured, not cited |

**One-line answer:** BLEU is about **8% harsher on Tigrinya** than English — real,
but roughly half the size the standard warning implies; **chrF should be primary**
because its advantage *widens as quality falls*, which is where low-resource
systems live. Separately, **our two evaluation anchors appear to be in different
varieties**, so a single "Tigrinya score" would be meaningless.

---

## Key Findings

- **Answered by measurement, not assertion.** Papers on this are egress-blocked,
  so Experiment 003 measured it on **FLORES+ parallel data** — the same 30
  sentences in both languages, so language is the only variable.

- **All four pre-committed hypotheses were refuted, and all four effects pointed
  in the predicted direction.** The directions were right; my thresholds were
  roughly 2× too aggressive.

  | Claim | Predicted | **Measured** |
  | --- | --- | --- |
  | ti needs fewer words | < 0.80× | **0.93×** |
  | ti type/token ratio higher | > 1.3× | **1.18×** |
  | BLEU falls further on ti | > 1.2× | **1.08×** |
  | chrF retains more than BLEU | > 2.0× | **1.48×** |

- **⭐ chrF is still the right primary metric — for a reason the thresholds
  missed.** Its advantage over BLEU *grows* as quality degrades:

  | Near-miss corruption | BLEU kept | chrF kept | ratio |
  | ---: | ---: | ---: | ---: |
  | 10% | 77.8% | 91.6% | 1.18× |
  | 30% | 41.5% | **74.9%** | **1.80×** |

  Low-resource MT operates in the low-quality regime. Choose the metric for how
  it behaves when systems are weak. → **DEC-009**

- **A methodological check that hardens the result.** Changing a final character
  destroys 27.1% of an average Tigrinya word but only 18.8% of an English one
  (Ge'ez packs consonant+vowel per character). The test was **~1.44× harsher on
  Tigrinya**, biasing *toward* confirmation — and the hypotheses were refuted
  anyway, so the true BLEU penalty is if anything **below 8%**.

- **⚠️ Our two DEC-005 anchors are probably in different varieties.**
  TiQuAD is `[verified]` Eritrean-sourced. FLORES+ Tigrinya carries Ethiopian
  markers: `ፀ`-series tsade ×8, `አ` alef ×8, `እስካብ` ×2, `ብሄራዊ` ×1, `እንትኸውን` ×1 —
  **with zero Eritrean counterparts** for the diagnostic forms.
  - `[verified]`: the set is orthographically mixed (both tsade series, both alef
    forms). ⚠️ **Corrected 2026-08-13:** mixing is **normal** — Eritrean sources
    show it too (1.0–3.8%). What distinguishes FLORES+ is the **rate: 15.1%,
    ~4–15× Eritrean sources**. See summary 009.
  - `[strong signal]`: it leans Ethiopian — now on *better* evidence, since the
    rate has a baseline. **Needs native-speaker confirmation (A-13).**

  Either way: **never report an aggregate Tigrinya score across both anchors.**
  → **DEC-010**

- **Orthographic variation is thinner than feared.** Naive tsade/alef
  normalisation collapses just **4 of 496** unique forms (0.8%) — useful
  calibration against overestimating the normalisation problem (DEC-007).

- **⚠️ Both anchors are gated or awkward.** `openlanguagedata/flores_plus` is
  **🔒 gated**; the convenient parquet mirror (`haoranxu`) **drops every
  low-resource language**; TiQuAD's test split is request-gated (**A-04**).
  A working pipeline for high-resource languages is no evidence our data exists.
  Ungated route found and recorded: `alexei-v-ivanov-amd/flores_plus`, `tir`
  begins at row **188232**, `eng` at **53636**.

- **Cross-experiment check.** Tigrinya words average 3.69 chars × 1.957
  (Experiment 002's measured expansion) = **7.22 phonemes** vs English's 5.31 —
  ~36% more per word. The morphological load is real; **the Ge'ez script hides
  it** at character level. Two experiments, different corpora, agreeing.

## Important Decisions

| Decision | ID | Status |
| --- | --- | --- |
| chrF primary; BLEU reported for comparability only, never alone | DEC-009 | Accepted |
| Evaluation results are variety-scoped; no cross-variety aggregate | DEC-010 | Accepted |

## Rejected Alternatives

| Alternative | Rejected because |
| --- | --- |
| BLEU as primary metric | Measurably harsher on Tigrinya (~8%) and degrades least informatively exactly where low-resource systems sit |
| Drop BLEU entirely | Overreaction — the penalty is modest, and BLEU is what published Tigrinya results report; dropping it forfeits comparability |
| COMET as primary | Untestable here (model downloads egress-blocked); adopting an unvalidated learned metric would repeat the mistake this report exists to avoid |
| Single aggregate "Tigrinya score" | Anchors appear to be in different varieties; the aggregate would average two different languages-in-practice |

## Important Numbers

| Metric | Value | Basis |
| --- | --- | --- |
| **BLEU harshness penalty, ti vs en** | **1.08×** | `[verified]` |
| **chrF/BLEU retention at 30% corruption** | **1.80×** | `[verified]` |
| Type/token ratio, en vs ti (same content) | 0.641 vs **0.753** | `[verified]` |
| Characters per word, en vs ti | 5.31 vs **3.69** | `[verified]` |
| Phonemes per word, en vs ti | 5.31 vs **7.22** | `[verified]` (cross-check) |
| Words per sentence, en vs ti | 23.57 vs 21.97 | `[verified]` |
| Forms collapsed by orthographic normalisation | **4 / 496 (0.8%)** | `[verified]` |
| ET-marker share: Eritrean sources vs FLORES+ | **1.0–3.8%** vs **15.1%** | `[verified]` (added 2026-08-13) |
| FLORES+ `tir` row offset (ungated mirror) | **188232** | `[verified]` |

## Recommended Next Steps

1. **Build the harness** to DEC-009/DEC-010 — chrF + BLEU, variety-scoped,
   variance reported, implementations pinned.
2. **Get a native speaker to confirm the FLORES+ variety attribution** — it
   determines whether DEC-010 is a precaution or a live correction.
3. **Request FLORES+ gated access and the TiQuAD test split** (**A-04**).
4. **Re-run on the full 1,012-sentence devtest** once egress allows (**A-09**).
5. **Resolve whether COMET is usable** — NLLB's published Tigrinya numbers use
   it, so we cannot compare against them without it.

## References

1. `experiments/003-metric-validity/` — this report's evidence
2. `alexei-v-ivanov-amd/flores_plus` — ungated FLORES+ mirror, CC-BY-SA-4.0
3. `sacrebleu` 2.6.0 — pinned metric implementation

---

**Open questions / uncertainty:** Is FLORES+ Tigrinya genuinely Ethiopian-variety
(needs a native speaker)? Is COMET valid here? Do the ~8% and 1.80× figures hold
on 1,012 sentences rather than 30? Does chrF's advantage persist against *real*
MT errors rather than synthetic perturbation?
