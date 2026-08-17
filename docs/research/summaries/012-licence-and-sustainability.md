# Summary: Licensing and Sustainability — What This Project Can Die Of

| Field | Value |
| --- | --- |
| **Summary ID** | `012-licence-and-sustainability` |
| **Full report** | `docs/research/reports/11_business/001-licence-and-sustainability.md` |
| **Date** | 2026-08-03 |
| **Status** | Current |
| **Confidence** | High on the licence map; **legal readings are readings, not rulings** |

**One-line answer:** Nothing forces copyleft on our code, so **Apache-2.0 for
code, CC-BY-4.0 for docs, inherit upstream for data** (closing **A-12**). And the
running cost is so small that **money is not the binding constraint — maintainer
attention is.**

---

## Key Findings

- **A-12 is now decidable** because every upstream licence is `[verified]`:

  | Layer | Licences | Copyleft? |
  | --- | --- | --- |
  | Code deps (`ctranslate2`, `epitran`, `tokenizers`, `sacrebleu`, `fastapi`, …) | MIT / Apache-2.0 | **No** |
  | Models (`madlad400-3b-mt`, `tiroberta-bi-encoder`) | Apache-2.0 | **No** |
  | Data (`haddas`, FLORES+, TiQuAD) | **CC-BY-SA-4.0** | **Yes — share-alike** |
  | Data (`TigrinyaLargeText`) | MIT | No |

  **Share-alike enters only through data, and binds only derivatives of that
  data** — not source code, which is not a derivative of a corpus.
  → **DEC-020**: licence by artefact class.

- **⚠️ A licence false-negative I nearly recorded.** PyPI's `license` field
  returned **"NOT STATED"** for `sacrebleu`, `sentence-transformers`, `fastapi`,
  `trl`, and `bitsandbytes`. Under P-9 that is disqualifying — recording it would
  have wrongly rejected four dependencies, including the metric implementation
  **DEC-009** depends on.

  **They are licensed.** The values live in PEP 639's newer `license_expression`
  field, empty in the legacy one:

  | Package | legacy | `license_expression` |
  | --- | --- | --- |
  | `sacrebleu` | `''` | **Apache-2.0** |
  | `fastapi` | `''` | **MIT** |
  | `ctranslate2` | `MIT` | *(none — older packaging)* |

  Same shape as HF `size_categories` being wrong on 2 of 4 datasets:
  **metadata fields are evidence, not truth, and one field is not a check.**

- **⭐ Running cost is near zero, which changes the question.** No training
  (DEC-017), no GPU (DEC-014/019), no orchestration or registry (DEC-019), and
  **Tier 0 always-warm is 52.6 GB-h/month** with the whole MVP at 191 MB.
  Whatever a vendor charges per GB-hour, 52.6 of them does not kill a project.

  **So reaching for a funding model would be solving the wrong problem.**

- **What this project can actually die of**, ranked:

  1. **Maintainer attention — the real one.** 15 items in `ACTIONS.md` need a
     human and **three are blocking** (A-01 `fgaim` licences, A-02 DEC-002,
     A-05 parallel data). **No amount of research resolves any of them.** The
     action register is the real risk register.
  2. **Upstream dependency.** Our embeddings model, several primitives, and the
     ecosystem's entire published Tigrinya baseline come from few parties.
     Disappearance is survivable; a **licence change** less so.
  3. **Legal exposure through data, not code** (**A-06**). DEC-011 already paid
     **4.8× the parameters** to avoid the NC-model question on a conservative
     reading — **if the permissive reading is right, that cost was unnecessary.**

  **Running out of money is conspicuously absent** — which is what a
  business-model document is normally about.

- **N-9 stands.** Not a hosted commercial service *yet*. Four conditions would
  make it a live question — A-06 resolved, a measured quality bar (nothing is
  measured yet), demand evidence (A-02 is step one), and a maintenance commitment
  surviving the first paying user. **None hold today.**

## Important Decisions

| Decision | ID | Status |
| --- | --- | --- |
| Licence by artefact class: Apache-2.0 code, CC-BY-4.0 docs, inherit for data | DEC-020 | Accepted — closes **A-12** |

## Rejected Alternatives

| Alternative | Rejected because |
| --- | --- |
| A single project-wide licence | Data derivatives carry share-alike obligations code does not; one licence either over-restricts code or under-honours upstream data terms |
| GPL / AGPL for code | Nothing upstream requires it, and it would restrict the application developers DEC-002 names as primary users |
| MIT for code | Apache-2.0's explicit patent grant matters more for infrastructure others build on; the ecosystem already uses it |
| Deferring A-12 further | It was deferred pending A-01/A-05/A-06; the *code* licence turns out not to depend on any of them |
| Proposing a revenue model | **N-9** forecloses a commercial service for now; inventing one would contradict a recorded non-goal |
| Treating funding as the sustainability risk | Measured cost is 52.6 GB-h/month for the always-warm tier — the scarce resource is attention, not money |

## Important Numbers

| Metric | Value | Basis |
| --- | --- | --- |
| Code dependencies forcing copyleft | **0** | `[verified]` |
| Datasets carrying share-alike | **3 of 6** | `[verified]` |
| Dependencies falsely reading "unlicensed" | **4** | `[verified]` |
| Tier 0 always-warm | **52.6 GB-h/month** | arithmetic |
| Minimum viable platform footprint | **191 MB** | arithmetic |
| ACTIONS items needing a human | **15**, 3 blocking | `[verified]` |
| Parameter cost already paid for legal caution | **4.8×** (DEC-011) | `[verified]` |

## Recommended Next Steps

1. **Add `LICENSE` (Apache-2.0) and `LICENSE-docs` (CC-BY-4.0)** — DEC-020 is not
   in force until the files exist.
2. **Resolve A-06.** It gates N-9 *and* could refund DEC-011's 4.8× parameter
   cost.
3. **Treat `ACTIONS.md` as the risk register** in any status review.
4. **Record data provenance and obligations per artefact**, so share-alike is
   honoured mechanically rather than remembered.
5. **Revisit N-9 only when all four conditions hold**, not before.

## References

1. PyPI `license_expression` and Hub licence metadata `[verified]` 2026-08-03
2. `docs/research/summaries/011-cost-model-and-enforcement.md` — cost model
3. `docs/vision/non_goals.md` — N-9

---

**Open questions / uncertainty:** Does a CC-BY-SA corpus taint a downstream
artefact (**A-06**)? Does an NC model licence reach a commercial product? Would
anyone pay for this — unknown, and **A-02** is the first evidence either way.
