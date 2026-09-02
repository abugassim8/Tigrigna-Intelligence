# Data Architecture

> **Status: the screening policy is decided and executable; there is almost no
> data to apply it to.** DEC-008 and DEC-015 settle how data enters the system.
> The corpus itself is the constraint: **~99% of discovered Tigrinya data is
> unlicensed**, and there are ~~**0 cleanly-licensed parallel sentences**~~
> **2,030** of them.
>
> ⚠️ **RETRACTED 2026-09-01 — this was false.** [HornMT](https://github.com/asmelashteka/HornMT) is **2,030 human-translated en–ti pairs under CC-BY-4.0**, now committed at `data/anchors/hornmt/`. The zero was measured behind an egress block that made GitHub unreadable; the corpus was public the whole time.
>
> **Evidence:** `../research/summaries/005-data-and-contamination.md`,
> `../research/summaries/009-pipeline-and-screening.md`

## Purpose of this document

How data moves and lives in the platform: ingestion, storage, processing pipelines, versioning, and lineage — from raw source to served artefact.

## Why this document exists

Data quality is the first priority in the project's philosophy, and data architecture is where that priority becomes concrete or gets quietly abandoned. Lineage matters especially here: for a low-resource language, knowing exactly which data produced which artefact is what makes results reproducible and licensing defensible.

## How to use it

- **Reading:** this is the current design of record for this area. Where it
  conflicts with a decision in
  [`../decisions/DECISIONS.md`](../decisions/DECISIONS.md), the decision wins and
  this document needs updating.
- **Writing:** update it when an Architect-stage decision changes the design. Do
  not use it as a scratchpad for ideas — exploratory thinking belongs in
  `../research/`. This document holds what we have *decided*, not what we are
  *considering*.
- **Every design element here must trace to a decision record.** Design without a
  recorded decision behind it is how projects end up unable to explain
  themselves.

## Relevant principles

**P-3** data quality beats model sophistication · **P-5** reproducibility · **P-9** licensing is a hard constraint

## The constraint, stated first

| Fact | Value |
| --- | ---: |
| Monolingual rows discovered | ~67K |
| Parallel pairs discovered | 1.4M |
| **Cleanly-licensed parallel sentences** | **0** |
| Share of discovered data that is unlicensed | **~99%** |
| Working corpus actually committed | **4 files, 2,362 word tokens** |

**This is a licensing problem, not a scarcity problem.** The 1.4M parallel pairs
exist; what is missing is permission (**A-05**). Everything below is built to
that shape: a small, cleanly-licensed corpus, screened hard, with quarantine as
the default rather than the exception.

## Ingestion and screening (DEC-008, DEC-015)

**Screening is executable and mandatory**, not a convention:
`scripts/data_processing/screen_dataset.py` implements DEC-008's four gates.

| Gate | Rule |
| --- | --- |
| **Licence** | Must be **asserted by the caller** — never inferred from metadata |
| **Contamination** | Overlap against declared evaluation sets |
| **Quality** | Detects corruption; the known-bad sample still fails |
| **Provenance** | Source recorded with the artefact |

Two properties matter more than the gate list:

- **It fails closed.** With no licence and no evaluation set, screening
  *refuses* — verified, and re-verified in CI. A gate that passes on missing
  input is not a gate.
- **Licence is never auto-detected.** Metadata is evidence, not truth: **HF tags
  were wrong on 2 of 4 datasets**, and PyPI's legacy field reads "NOT STATED" for
  five packages whose licences are declared under PEP 639. Trusting either would
  have produced confidently wrong answers in both directions.

**Why it is executable at all:** DEC-008 spent 15 days as policy with no
mechanism and was **silently ignored the entire time** — screening reimplemented
three times, differently, with zero files in `scripts/data_processing/`. That was
found by measurement, not by anyone noticing. → DEC-015, then DEC-018.

## Train/eval separation

**Contamination is the one form of sloppiness that invalidates everything
downstream**, and it has already been found in the wild here:
`farefaine/tigrinya-pretraining`, advertised as raw pretraining sources,
**verifiably contains TiQuAD validation data** — identical `article_title` and
`context`, with TiQuAD's three-annotation validation convention. Anyone
pretraining on it and evaluating on TiQuAD gets a contaminated score without
knowing. Reporting it upstream is **A-03**.

Structurally, separation is enforced by the screening gate rather than by
discipline: a corpus is screened *against a declared evaluation set*, and with no
evaluation set declared the run fails rather than passing.

## Licence and provenance (DEC-020, P-9)

**Licence obligations travel by artefact class:**

| Artefact | Licence |
| --- | --- |
| Code | **Apache-2.0** |
| Documentation | **CC-BY-4.0** |
| Data | **Inherits** — whatever the source imposes |

**No code dependency imposes copyleft** — the full upstream licence map was
checked. **Share-alike enters only through data** (FLORES+ is CC-BY-SA-4.0), so
the obligation is contained to derived corpora rather than the platform.

**Unstated licensing is disqualifying** (P-9, A-009). That is why the `fgaim`
models sit quarantined pending **A-01**, and why the working corpus is four files
rather than 67K rows.

## Storage, versioning, lineage

Deliberately minimal, and sized to the corpus that exists:

- **Data lives in the repository**, beside the experiments that consume it.
  2,362 word tokens does not need object storage, and a corpus a contributor
  cannot read is one nobody checks.
- **Lineage is the experiment.** Each experiment emits `results.json` and
  **reproduces byte-identically** (DEC-016), so an artefact traces to the code
  and corpus that produced it. Timing experiments declare
  `"deterministic": false` and are exempt from the byte-comparison — and get no
  drift detection in exchange (DEC-016 Amendment 1).
- **No data warehouse, no feature store, no vector database.** Retrieval is not
  in DEC-006's minimum platform (**P-7**).
- **Retention and backup:** git, plus whatever the remote provides. At this size
  a separate durability story would be ceremony.

## Normalisation

Ge'ez orthographic normalisation is implemented in
`tigrinya_primitives.normalise` — tsade (ጸ/ፀ) and alef (ኣ/አ) collapsed toward the
Eritrean standard. Three measured properties shape it:

- **Orthographic variation is thin**: naive normalisation collapses **4 of 496**
  unique forms (0.8%). Real, but small — a useful guard against over-engineering.
- **Mixing the two series is normal practice, not a defect** — Eritrean
  newspapers mix at 1.0–3.8%. So normalisation is a *matching aid*, never a
  correction, and the surface form is always preserved.
- **It is length-preserving and idempotent**, both checked over corpus text, so
  offsets computed before normalisation stay valid after it.

## Open questions

- **Will A-05 land?** It is the only route to parallel data, and the entire
  training ladder is blocked below it.
- Is TiQuAD's copyright position usable at all (**A-06**)? It is one of our two
  evaluation anchors.
- **Do our evaluation anchors mix varieties?** DEC-010 assumes they might;
  **A-13** would settle whether that is a precaution or a live correction.
- At what corpus size does storing data in git stop being reasonable? Not yet,
  but the answer should be decided before it is passed accidentally.

## Decision log for this area

| Decision | ID | Date | Summary |
| --- | --- | --- | --- |
| Mandatory contamination screening | **DEC-008** | 2026-07-29 | Unlicensed data quarantined — ⚠️ spent 15 days as policy with no mechanism |
| Screening is executable | **DEC-015** | 2026-08-13 | A script, not a convention; datasets carry a screening record; fails closed |
| Licence by artefact class | **DEC-020** | 2026-08-17 | Apache-2.0 code, CC-BY-4.0 docs, inherit for data; closes A-12 |
| Evaluation anchors | **DEC-005** | 2026-07-29 | FLORES-200 and TiQuAD — TiQuAD contamination since confirmed in a third-party corpus |
| Machine-checkable experiment artefacts | **DEC-016** | 2026-08-13 | `results.json`, byte-identical on re-run — ⚠️ **Amendment 1** exempts timing experiments |
| Support both varieties | **DEC-004** | 2026-07-29 | Data carries a variety label; results never aggregate across them |

## What future contributors should add

The actual design, once research supports it. Diagrams where they clarify.
Rationale linked to decision records. Keep it current — an architecture document
that has drifted from reality is worse than none, because people trust it.
