# The ML Pipeline for a Project That Decided Not to Train

| Field | Value |
| --- | --- |
| **Report ID** | `001-pipeline-without-training` |
| **Domain** | `06_ml_pipeline` |
| **Stage** | Scout → Analyst → Architect |
| **Date** | 2026-08-13 |
| **Status** | Accepted |
| **Summary** | `docs/research/summaries/009-pipeline-without-training.md` |
| **Related decisions** | **DEC-015**, **DEC-016**; gives DEC-008 a mechanism; engages A-004, A-005, DEC-010, DEC-014, P-5 |

---

## Objective

Define the ML pipeline. **P-5** requires reproducibility, **DEC-008** requires
screening, **DEC-014** requires model conversion — none of which currently has an
implementation.

**Method note.** Two claims this repository makes about itself were **tested**
rather than assumed: that experiments reproduce, and that DEC-008's gates are
enforced. One held. One did not.

---

## Finding 1 — This is not a training pipeline, and saying so changes the design

Most ML pipeline designs put training at the centre. Ours cannot:

- **A-004** — avoid unnecessary model training.
- **A-005** — prefer fine-tuning and adaptation over training from scratch.
- **DEC-003** — adopt the existing model layer; build primitives, evaluation, integration.
- **DEC-011** — translation is an adopted Apache-2.0 checkpoint, not a trained one.
- **A-002** — a 40M-token data ceiling makes from-scratch training implausible anyway.

**The real pipeline is: acquire → screen → convert → evaluate → release.**
Training is a **contingency branch**, not the main line.

This is not a semantic point. A training-centred design would invest in data
labelling, experiment tracking, and checkpoint management — none of which we
need yet — while under-investing in the two stages that have actually consumed
effort: **screening** and **evaluation**. Naming the pipeline correctly puts the
engineering where the work is.

## Finding 2 — Reproducibility holds where it was designed in, and Experiment 001 predates it

`[verified]` by re-running all three experiments and byte-comparing outputs:

| Experiment | Runs clean | Machine-checkable artefact | Byte-identical on re-run |
| --- | --- | --- | --- |
| 001 — epitran decomposition | ✅ | ❌ **none** | **cannot be checked** |
| 002 — tokenizer fertility | ✅ | ✅ `results.json` | ✅ **identical** |
| 003 — metric validity | ✅ | ✅ `results.json` | ✅ **identical** |

**P-5 is satisfied for 002 and 003 and cannot be evaluated for 001**, whose
results exist only as prose in its README. If `epitran` changed behaviour
tomorrow, nothing would detect it — and DEC-007's amended form rests on
Experiment 001's numbers.

The pattern is instructive: 001 was written before the experiment template's
discipline had been exercised. **Reproducibility was achieved by making the
artefact mandatory, not by intending to be careful.** → **DEC-016**

## Finding 3 — DEC-008 was policy without mechanism

`[verified]`: DEC-008 mentions screening seven times; `scripts/data_processing/`
contained **zero files**; and Ethiopic/quality-screening logic had been
**reimplemented in all three experiment scripts**, differently each time.

A gate that exists only in prose is not a gate. Every dataset this project has
touched was screened by hand, by me, inconsistently.

`scripts/data_processing/screen_dataset.py` now implements the four gates —
**licence** (A-009), **quality** (Experiment 002), **variety** (DEC-010), and
**contamination** (DEC-008) — and emits a machine-readable screening record with
an exit status suitable for gating a pipeline step.

**Validated against known results, including a positive control:**

| Test | Input | Expected | Result |
| --- | --- | --- | --- |
| A | Known-corrupted TigrinyaLargeText sample | fail quality | ✅ **FAIL**, 0.289% foreign chars |
| B | Clean corpus vs FLORES+ eval set | clear | ✅ **CLEARED** |
| C | FLORES+ `tir` | reproduce Exp-003's mixed orthography | ✅ **MIXED**, found independently |
| D | **Eval set screened against itself** | **detect contamination** | ✅ **652 shared 8-grams** |

**Test D is the one that matters.** Without a positive control, "no contamination
found" is indistinguishable from "the detector does not work." It fires.

Two deliberate design choices:

- **Licence is asserted, never detected.** A licence is a legal fact about a
  dataset, not a property of its bytes.
- **Contamination fails closed.** Supplying no evaluation set is a **FAIL**, not
  a pass — DEC-008 requires the check, and silence must not read as clearance.

→ **DEC-015**

## Finding 4 — ⚠️ Building the tool corrected one of my own earlier claims

Running the variety gate across all corpora produced a result I did not have when
writing Experiment 003:

| Source | ER markers | ET markers | ET share |
| --- | ---: | ---: | ---: |
| `tlt_000` — asmarino.com, Eritrean news | 75 | 3 | **3.8%** |
| `haddas` — *Hadas Ertra*, Eritrean state paper | 95 | 1 | **1.0%** |
| **FLORES+ `tir`** — our MT evaluation anchor | 90 | 16 | **15.1%** |

**Orthographic mixing is present in every source, including unambiguously
Eritrean ones.** So mixing *per se* is normal Tigrinya practice, not a defect —
and Experiment 003's framing of FLORES+ as "orthographically inconsistent with
itself" was accurate as a fact but **misleading in implying that was itself
anomalous.**

**This strengthens rather than weakens DEC-010.** Previously the observation had
no baseline. Now it does, and FLORES+'s ET-marker rate is **~4–15× that of
Eritrean sources.** Combined with the lexeme evidence (`እስካብ`, `ብሄራዊ`,
`እንትኸውን`, with zero Eritrean counterparts), the Ethiopian-leaning signal holds —
on better evidence than before.

The correction is recorded in Experiment 003 and Summary 006. **A-13's
native-speaker audit remains the thing that settles it.**

## Finding 5 — The pipeline, stage by stage

| Stage | Status | Mechanism |
| --- | --- | --- |
| **1. Acquire** | Constrained | HF MCP, row-by-row; egress blocks bulk download (**A-09**). Offsets recorded in Summary 006 |
| **2. Screen** | ✅ **Now executable** | `screen_dataset.py`, four gates, machine-readable record (**DEC-015**) |
| **3. Convert** | ⚠️ Designed, unverified | HF → CTranslate2 (**DEC-014**). Support verified; conversion needs weights |
| **4. Evaluate** | Designed, unbuilt | chrF + BLEU, variety-scoped, both models (**DEC-009**, **DEC-010**, **DEC-011**) |
| **5. Release** | Not designed | Gated on `10_infrastructure` |
| **(contingency) Train** | Not needed | A-004, A-005. Revisit only if adopted models prove inadequate |

**Stage 3 is the current bottleneck.** Everything downstream of it — evaluating
MADLAD, comparing against NLLB, publishing the first Tigrinya MADLAD number —
waits on a conversion step that cannot run without model weights.

## Limits of this report

- **The screening tool's quality gate detects mojibake, not meaning.** The
  column-scramble signal is reported as a **review flag, not a verdict**, because
  distinguishing scrambled columns from unusual prose is not reliably automatable
  and a false verdict would be worse than none.
- **The variety gate never returns a verdict** — it labels `unknown` and reports
  evidence. Attribution needs **A-13**.
- **Contamination detection is exact-match n-gram overlap.** It catches copied
  text. It will not catch paraphrase, translation, or reformatting.
- **Nothing about stages 3–5 is verified**, for the same egress reason as
  everywhere else (**A-09**).

---

## Decisions arising

- **DEC-015** — Screening is executable and mandatory; datasets carry a screening
  record.
- **DEC-016** — Every experiment emits a machine-checkable artefact.

**Evidence:** re-run and byte-comparison 2026-08-13 `[verified]`;
`scripts/data_processing/screen_dataset.py` validation runs `[verified]`.
