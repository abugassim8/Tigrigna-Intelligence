# Licensing and Sustainability: What This Project Can Die Of

| Field | Value |
| --- | --- |
| **Report ID** | `001-licence-and-sustainability` |
| **Domain** | `11_business` |
| **Stage** | Scout → Analyst → Architect |
| **Date** | 2026-08-17 |
| **Status** | Accepted |
| **Summary** | `docs/research/summaries/012-licence-and-sustainability.md` |
| **Related decisions** | **DEC-020**; closes **A-12**; engages N-9, P-9, A-009, G-11 |

---

## Objective

Settle the project licence (**A-12**, deferred here deliberately) and answer the
sustainability question: what does keeping this alive actually require?

**Scope note.** **N-9** states we are not building a hosted commercial service
*yet*. This report therefore contains **no revenue model** — inventing one would
contradict a recorded non-goal. What it does instead is establish the licence and
identify what the project can realistically die of.

---

## Finding 1 — A-12 is now decidable, and nothing forces copyleft on our code

A-12 was deferred because our licence interacts with every upstream licence, and
those were unknown. They are now all `[verified]`:

**Code dependencies — uniformly permissive:**

| Package | Licence |
| --- | --- |
| `ctranslate2` (DEC-014) | **MIT** |
| `epitran` | **MIT-Modern-Variant** |
| `tokenizers` | **Apache-2.0** |
| `sacrebleu` (DEC-009) | **Apache-2.0** |
| `sentence-transformers` | **Apache-2.0** |
| `fastapi` | **MIT** |
| `peft` / `accelerate` / `datasets` | **Apache-2.0** |

**Models — both permissive:**

| Model | Licence |
| --- | --- |
| `google/madlad400-3b-mt` (DEC-011) | **Apache-2.0** |
| `fgaim/tiroberta-bi-encoder` (DEC-003) | **Apache-2.0** |

**Data — where the constraint actually lives:**

| Dataset | Licence | Obligation |
| --- | --- | --- |
| `TigrinyaLargeText` | MIT | attribution |
| **`haddas`** | **CC-BY-SA-4.0** | **share-alike** |
| **FLORES+** | **CC-BY-SA-4.0** | **share-alike** |
| **TiQuAD** | **CC-BY-SA-4.0** | share-alike + **upstream copyright unresolved (A-06)** |

**No code dependency imposes copyleft.** Share-alike enters only through *data*,
and only binds *derivatives of that data* — not our source code, which is not a
derivative of a corpus.

→ **DEC-020**: licence **by artefact class**.

## Finding 2 — ⚠️ A licence false-negative I nearly recorded

Checking PyPI's `license` field returned **"NOT STATED"** for `sacrebleu`,
`sentence-transformers`, `fastapi`, `trl`, and `bitsandbytes`.

Under **P-9**/**A-009**, an unstated licence is disqualifying. Recording that
reading would have wrongly disqualified four dependencies — including the metric
implementation **DEC-009** depends on and the runtime **DEC-012** assumes.

**The licences are stated.** They live in PEP 639's newer `license_expression`
field, which the legacy `license` field leaves empty:

| Package | legacy `license` | `license_expression` |
| --- | --- | --- |
| `sacrebleu` | `''` | **Apache-2.0** |
| `sentence-transformers` | `''` | **Apache-2.0** |
| `fastapi` | `''` | **MIT** |
| `ctranslate2` | `MIT` | *(none — older packaging)* |

**Licence metadata lives in two places depending on packaging vintage, and
checking one gives false negatives in both directions.** This is the same shape
as the earlier finding that Hugging Face `size_categories` tags were wrong on 2
of 4 datasets: **metadata fields are evidence, not truth, and a single field is
not a check.**

Recorded in `RESEARCH_ACCESS.md` as a required step.

## Finding 3 — The project's running cost is near zero, which changes the question

Consolidating what the technical domains established:

| Cost driver | Status | Source |
| --- | --- | --- |
| Model training | **None** — adopted checkpoints | DEC-011, DEC-017 |
| GPU | **None** — CPU int8 | DEC-014, DEC-019 |
| Orchestration | **None** — deliberately | DEC-019 |
| Model registry / vector DB | **None yet** | DEC-019 |
| **Tier 0 always-warm** | **52.6 GB-h/month** | DEC-013, DEC-019 |
| Tier 2 | Lazily loaded; mode pending **A-14** | DEC-019 |

**A container serving the entire minimum viable platform is 191 MB
(DEC-013).** Whatever a vendor charges per GB-hour, 52.6 of them is not what
kills a project.

**So money is not the binding constraint, and treating it as one would be
solving the wrong problem.** The reflex for an open infrastructure project is to
reach for a funding model. The measured cost profile says that is not where the
risk is.

## Finding 4 — What this project can actually die of

Three failure modes, ranked by how likely they look from here:

**1. Maintainer attention — the real one.** Fifteen items in `ACTIONS.md` require
a human, and **three are blocking**: `fgaim` licence clarification (**A-01**),
DEC-002 confirmation (**A-02**), and the parallel-data licence (**A-05**). None
can be resolved by any amount of further research. **The action register is the
project's real risk register**, and it is entirely composed of things only a
person can do.

**2. Upstream dependency.** **DEC-003** noted concentration risk on one group's
output; the picture has since sharpened. Our embeddings model, several primitives,
and the ecosystem's entire published Tigrinya evaluation baseline come from a
small number of parties. Mitigation is real but partial: artefacts are downloadable
and mostly permissively licensed, so a disappearance is survivable — a *licence
change* less so.

**3. Legal exposure through data, not code.** **A-06** remains open on two
questions: whether TiQuAD's fair-use-derived corpus can support anything shipped,
and whether an NC *model* licence reaches a commercial downstream product.
DEC-011 already paid **4.8× the parameters** to avoid the second on a conservative
reading. **If the permissive reading is correct, that cost was unnecessary** — a
concrete reason A-06 is worth resolving rather than deferring.

**What is conspicuously absent from this list is running out of money**, which is
what a business-model document would normally be about.

## Finding 5 — What N-9's "yet" would take

**N-9** forecloses a hosted commercial service *for now*. Recording the conditions
under which that becomes a live question, so it is not reopened casually:

1. **A-06 resolved**, since commercialisation is exactly where TiQuAD's upstream
   copyright and the NC-model question stop being theoretical.
2. **A measured quality bar** — DEC-009's harness showing our capabilities are
   good enough that someone would pay. **Nothing has been measured yet.**
3. **Demand evidence**, which **A-02** is the first step toward.
4. **A maintenance commitment** that survives the first paying user, since
   Finding 4 says attention is the scarce resource.

**None of these hold today**, so N-9 stands. It should be revisited when they do,
not before.

## Limits of this report

- **No revenue model**, deliberately — N-9 forecloses it and inventing one would
  contradict a recorded non-goal.
- **No legal advice.** Findings 1 and 4 read licence texts and metadata; whether
  a CC-BY-SA corpus taints a downstream artefact is a lawyer's question
  (**A-06**).
- **"Share-alike binds data derivatives, not our code"** is the standard reading
  and the one I would act on, but it is a reading, not a ruling.
- **Cost figures are resource-hours**, not currency — see `10_infrastructure` for
  why no dollar figure appears.

---

## Decision arising

**DEC-020** — Licence by artefact class: **Apache-2.0** for code, **CC-BY-4.0**
for documentation, **inherit upstream** for data derivatives. Closes **A-12**.

**Evidence:** PyPI and Hub licence metadata `[verified]` 2026-08-17; cost model
from `docs/research/summaries/011-cost-model-and-enforcement.md`.
