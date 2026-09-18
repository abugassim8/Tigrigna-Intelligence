# Experiment 010 — Do the variety markers measure variety?

| Field | Value |
| --- | --- |
| **Experiment ID** | `010-variety-marker-calibration` |
| **Date** | 2026-09-02 |
| **Status** | **Complete — H1 REFUTED, H2 CONFIRMED, H3 REFUTED** |
| **Related decisions** | Amends **DEC-010**; corrects the variety reading in the HornMT anchor; re-briefs **A-13** |
| **Determinism** | Byte-identical across runs and across `PYTHONHASHSEED` |

---

## Question

The screening gate has reported `eritrean_markers` and `ethiopian_markers` on
every Tigrinya corpus since DEC-010, and **nothing has ever checked whether
those numbers track variety.** They could not be checked: no corpus this project
could reach declared its variety, which is why DEC-010 holds every label at
`unknown` pending a speaker (**A-13**).

TICO-19 ends that. It ships the same 3,071 English segments translated twice —
once declared `ti-ER`, once `ti-ET` — by different translators. Same source
text, same domain, same segment lengths. **The only variable is the variety.**
That is a controlled comparison, and it is the first one available.

## Method

`run.py` reads committed files only and reproduces offline. Two measures over
the same marker set:

- **Pooled ratio** — what the gate reports today: all Eritrean-side markers over
  all markers (ጸ-series + ኣ + `ክሳብ`/`ሃገራዊ` against ፀ-series + አ + `እስካብ`/`ብሄራዊ`).
- **ET-only presence** — per segment, does it contain a ፀ-series character,
  `እስካብ`, or `ብሄራዊ`? These forms belong to the Ethiopian standard and have no
  Eritrean-standard use.

## Hypotheses and thresholds, fixed before looking

| | Hypothesis | Pre-committed threshold | Verdict |
| --- | --- | --- | --- |
| **H1** | The pooled ratio separates the two declared varieties | ≥ **10 points** of ER-share separation, on both splits | **REFUTED** |
| **H2** | ET-only markers do not fire on Eritrean text | precision ≥ **0.99** | **CONFIRMED** |
| **H3** | ET-only markers fire often enough to label a segment | recall ≥ **0.50** | **REFUTED** |

## Results

| corpus | segments | ET-marked | rate | **pooled ER%** |
| --- | ---: | ---: | ---: | ---: |
| `dev` **ER** *(declared Eritrean)* | 971 | 0 | 0.0% | 98.9% |
| `dev` **ET** *(declared Ethiopian)* | 971 | 119 | 12.3% | **91.4%** |
| `test` **ER** *(declared Eritrean)* | 2,100 | 0 | 0.0% | 98.3% |
| `test` **ET** *(declared Ethiopian)* | 2,100 | 184 | 8.8% | **95.0%** |

### H1 — REFUTED, and this is the finding

The pooled ratio separates the declared varieties by **7.5 points on dev and
3.3 on test**, against a pre-committed 10. The corpus that TICO-19 **declares
Ethiopian** scores **91–95% "Eritrean"** on the gate's own number.

The cause is visible in the per-marker counts, and it is a measurement error
rather than a linguistic subtlety:

| marker | ER file | ET file | discriminative? |
| --- | ---: | ---: | --- |
| ኣ (Ge'ez alef, "Eritrean") | 4,877 | 4,546 | ❌ **swamps everything** |
| ጸ-series (Eritrean tsade) | 2,698 | 2,306 | ❌ present in both |
| ፀ-series (Ethiopian tsade) | **0** | 261 | ✅ **clean** |
| `እስካብ` (Ethiopian) | **0** | 30 | ✅ clean |
| `ብሄራዊ` (Ethiopian) | **0** | 13 | ✅ clean |
| አ (Amharic alef, "Ethiopian") | 131 | 66 | ❌ **backwards** |

**ኣ is one of the commonest letters in Tigrinya and both standards use it.**
Pooling ~4,500 counts of a non-discriminative letter with 261 counts of a clean
one buries the signal under a constant. One marker — አ — points the wrong way
outright, appearing twice as often in the Eritrean file.

So the gate's ratio is not a weak variety signal. It is **mostly a measurement
of how much Tigrinya is in the file**, and it should never have been read as a
proportion.

### H2 — CONFIRMED

Across **3,071 segments of declared-Eritrean text, the ET-only markers fired
zero times.** Precision 1.000. Whatever else is true, these forms do not appear
in Eritrean-standard writing in this corpus.

### H3 — REFUTED

Recall is **0.099**: the markers fire on only 9–12% of declared-Ethiopian
segments. As a *segment* classifier the rule is silent on nine segments in ten,
so it cannot label a sentence. Pre-committed threshold was 0.50 and it is not
close; recorded as a negative result (**P-13**) rather than quietly dropped.

**High precision, low recall** is still useful — at *corpus* scale. 0 firings in
3,071 segments versus 303 is decisive even at 10% recall.

## What this says about the corpora that carry no label

| corpus | segments | ET-marked | rate | reading |
| --- | ---: | ---: | ---: | --- |
| **HornMT** | 2,030 | **1,127** | **55.5%** | Ethiopian-consistent |
| FLORES sample | 30 | 7 | 23.3% | Ethiopian-consistent |
| TLT clean | 8 | 0 | 0.0% | too small to read |
| Haddas | 5 | 0 | 0.0% | too small to read |

⚠️ **The HornMT reading in its own README was backwards.** That file records
"6,237 Eritrean-standard markers against 2,181 Ethiopian — 74/26" and reads it
as an Eritrean lean, hedged as "evidence, not a verdict". Calibrated, the
evidence points the other way: **55.5% of HornMT's segments carry an
Ethiopian-only marker — six times the rate of the corpus TICO-19 declares
Ethiopian.** The 74/26 was the swamping artefact above, not a lean.

This matters beyond bookkeeping. HornMT is the project's primary evaluation
anchor, and a model tuned against it is being tuned toward whatever variety it
is actually written in.

## Limits — what this does not establish

- **Precision was measured on one Eritrean source**: two translators, COVID and
  medical domain. Zero false positives in 3,071 segments is strong, but it is
  not proof the markers never fire on Eritrean news prose.
- **The declared labels are TICO-19's, not a speaker's.** This calibrates our
  instrument against *someone else's* label. It does not replace **A-13**.
- **It does not label HornMT.** "Ethiopian-consistent at 55.5%" is a corpus-level
  reading from a rule with 10% recall. Under DEC-010 the label stays `unknown`.
- **Nothing here is a variety classifier.** H3 is refuted; per-segment labelling
  remains unsolved.

## Consequences

1. **DEC-010 amended** — the variety gate's pooled ratio is withdrawn as
   evidence of variety proportion. The gate now reports the ET-only segment rate
   alongside it, and the ratio is labelled for what it is.
2. **HornMT's README corrected** — the 74/26 paragraph is replaced.
3. **A-13 re-briefed** — the speaker is no longer being asked "is HornMT
   Eritrean?" on the strength of a backwards number. The question is now whether
   an anchor that is Ethiopian-consistent at 55.5% is the right anchor at all.

## Reproducing

```bash
python3 run.py            # print the report, rewrite results.json
python3 run.py --check    # verify results.json still matches (CI)
```
