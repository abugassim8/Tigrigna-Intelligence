# Action Register — things only a human can do

## Purpose of this document

Every open item that requires **a person**, not a research session: emails to
send, licences to obtain, decisions to confirm, legal questions to resolve, and
access to arrange.

## Why this document exists

Research produces findings; findings produce blockers; blockers sit unmoved
because nobody wrote down *who does what next*. Several items below are cheap —
a single email — and unblock disproportionately large amounts of work. One of
them potentially unlocks **1.4 million parallel sentences** for the cost of a
message.

**How to use it:** Work top-down. A-01 through A-04 are blocking. Each item
states what to do, why, and what it unblocks; where a message is needed, a
**ready-to-send draft** is included — copy, adjust the bracketed fields, send.

**What to add over time:** New actions as research surfaces them. Move completed
items to the Done section with the outcome and date — the outcome is often
itself a research finding.

**Status values:** `TODO` · `SENT` (awaiting reply) · `BLOCKED` · `DONE`

---

## At a glance

| ID | Action | Priority | Unblocks | Status |
| --- | --- | --- | --- | --- |
| **A-01** | Get licence clarification on the `fgaim` models | 🔴 **Blocking** | DEC-003 — the entire reuse plan | TODO |
| **A-02** | Confirm DEC-002 (who our primary users are) | 🔴 **Blocking** | API, MCP, SDK design | TODO |
| **A-03** | Report the TiQuAD contamination to `farefaine` | 🟠 High | Ecosystem (G-11); protects others | TODO |
| **A-04** | Request the TiQuAD test set | 🟠 High | DEC-005 — canonical evaluation | TODO |
| **A-05** | Get licence on 1.4M en–ti parallel sentences | 🟠 High | Translation work; largest single resource | TODO |
| **A-06** | Legal review of TiQuAD's copyright position | 🟠 High | Whether we can ship anything using it | TODO |
| **A-07** | Resolve HornMorpho licence + Tigrinya version | 🟡 Medium | Morphology service (DEC-006 critical path) | TODO |
| **A-08** | Set an `HF_TOKEN` for this environment | 🟡 Medium | Removes anonymous rate limits | TODO |
| **A-09** | Arrange a session with unrestricted egress | 🟡 Medium | The whole verification backlog | TODO |
| **A-10** | Introduce the project to GeezLab / L3S | 🟢 Low | Collaboration (G-11) | TODO |
| **A-11** | Licence clarification on `fidel` | 🟢 Low | Transliteration option | TODO |
| **A-12** | Choose the project licence | ⏸️ Deferred | Deliberately deferred to `11_business` | TODO |
| **A-13** | **Native-speaker variety audit of our two evaluation anchors** | 🟠 High | Whether DEC-010 is a precaution or a live correction | TODO |

---

## 🔴 A-01 — Licence clarification on the `fgaim` models

**Blocking DEC-003, which is the core of our entire strategy.**

Several GeezLab models carry **no stated licence** — not in metadata, and not in
the model card. Under **P-9**/**A-009** unstated licensing is disqualifying, so
until this is resolved we cannot build on them.

**Affected:** `fgaim/tiroberta-base` (the family's foundation), `tielectra-small`,
`tiroberta-pos`, `tielectra-small-pos`, `tibert-base`, `tiroberta-sentiment`,
`tielectra-small-sentiment`

*(Already clean: `tiroberta-bi-encoder` and `tielectra-bi-encoder` are
Apache-2.0; `tiroberta-geezswitch`, `tiroberta-abusiveness-detection`, and
`tiroberta-tiald-multi-task` are CC-BY-4.0.)*

**Contact:** Fitsum Gaim — `fitsum.gaim@kaist.ac.kr`, or open a discussion on
each model repo at `https://hf.co/fgaim/<model>/discussions`

> **Subject:** Licence clarification for the TiRoBERTa / TiELECTRA models
>
> Dear Dr Gaim,
>
> I'm working on an open infrastructure project for Tigrinya language
> technology, and your GeezLab models are the strongest foundation we've found —
> particularly `tiroberta-bi-encoder`, which we hope to use for embeddings.
>
> Several of the models don't carry a stated licence, including
> `tiroberta-base`, `tielectra-small`, and `tiroberta-pos`. Because we're
> building infrastructure that others will build on, we can't adopt a model
> whose terms are unclear — we'd be passing on rights we don't have.
>
> Would you be willing to add a licence to these repositories, or confirm the
> intended terms? Apache-2.0 or CC-BY-4.0 would match what you've already
> applied to the bi-encoders and the TiALD models.
>
> Thank you for making this work available — it has saved our project months.
>
> [Your name] · [Affiliation, if any] · [Project link]

**Unblocks:** DEC-003, the embeddings service, the POS service, and every
downstream decision that assumes model reuse.
**If refused or unanswered:** the reuse plan narrows sharply — see
`docs/research/summaries/001-tigrinya-nlp-ecosystem-scan.md` for what remains.

---

## 🔴 A-02 — Confirm DEC-002: who our primary users are

**This is yours to decide, not mine to research.**

I recorded **DEC-002 as *Proposed*** — primary users are **application
developers**, secondary are **researchers** — on inferential evidence: several
Ge'ez keyboard products (GeezIME, GeezKTB, Mesmer, GeezWord) each independently
re-solve word suggestion and dictionary lookup, which is a real signal that a
shared layer is wanted. But no direct user research was possible.

**What to do:** Read
`docs/research/summaries/002-scope-users-and-dialect.md` (≈3 minutes) and either
confirm, or tell me to change it.

**Why it matters:** it drives API surface, SDK priorities, and capability
sequencing. Cheap to change now; expensive after the API exists.

**Unblocks:** `07_api_mcp` design.

---

## 🟠 A-03 — Report the TiQuAD contamination to `farefaine`

**A confirmed problem in someone else's dataset that will harm others if left
unreported.**

`farefaine/tigrinya-pretraining` is advertised as *"Tigrinya Raw Pretraining
Sources"* but **verifiably contains TiQuAD validation data** — identical
`article_title` and `context` to TiQuAD's own published sample, with TiQuAD's
three-annotation validation convention. Anyone pretraining on it and evaluating
on TiQuAD gets a contaminated score.

Almost certainly an honest aggregation error. Reporting it is a genuine
ecosystem contribution (**G-11**) and costs one message.

**Contact:** HF discussion at
`https://hf.co/datasets/farefaine/tigrinya-pretraining/discussions`

> **Title:** Dataset appears to contain TiQuAD evaluation data
>
> Hello — thank you for assembling this collection.
>
> I think there may be an issue worth flagging. The dataset is described as raw
> pretraining sources, but its schema is TiQuAD's extractive-QA format
> (`id, question, context, answers, article_title, context_id`), and the
> validation split contains exactly 934 rows — matching TiQuAD's validation
> split.
>
> Checking the rows, the first entries carry `article_title` "ሃብቶም ክብረኣብ (ሞጀ)"
> with a context passage identical to the sample entry published on the TiQuAD
> dataset card, including three answer annotations per question — which is
> TiQuAD's documented convention for validation data.
>
> If TiQuAD validation data is present, anyone pretraining on this corpus and
> then evaluating on TiQuAD would get a contaminated score without realising it.
> Given TiQuAD's authors deliberately withheld the test split to prevent exactly
> this, it seemed worth raising.
>
> Might be worth either separating the QA-format rows or noting it on the card.
> Happy to share details of what I checked.
>
> [Your name]

**Consider also:** notifying Fitsum Gaim, since it concerns his dataset (can be
folded into A-01 or A-04).

---

## 🟠 A-04 — Request the TiQuAD test set

TiQuAD's test split (1,122 questions) is **deliberately withheld** to prevent
contamination and released only on request. Without it we evaluate on validation
only and must say so — which weakens comparability with published results.

**The authors specify the format.** Send to `fitsum.gaim@kaist.ac.kr`:

> **Subject:** TiQuAD Test Set Request
>
> Dear Dr Gaim,
>
> I'd like to request access to the TiQuAD test set.
>
> **Full name:** [your name]
> **Affiliation:** [university / company / independent]
> **Purpose and usage plan:** Evaluating Tigrinya question-answering and
> retrieval components for an open language-infrastructure project. TiQuAD is
> our primary QA evaluation anchor. We would report exact-match and token-level
> F1 using your official evaluation script, on both validation and test.
> **Acknowledgment:** I confirm the dataset will be used for **evaluation only,
> never for model training**, and will not be redistributed.
>
> Separately, you may want to know that `farefaine/tigrinya-pretraining` on the
> Hub — described as pretraining text — appears to contain TiQuAD validation
> rows. [See A-03.]
>
> [Your name]

**Unblocks:** DEC-005 evaluation on the canonical split.

---

## 🟠 A-05 — Licence on the 1.4M en–ti parallel sentences

**The cheapest high-value action available on this project.**

`michsethowusu/english-tigrinya_sentence-pairs` holds **1,400,000 English–
Tigrinya sentence pairs** — by far the largest Tigrinya resource found — with
**no stated licence**. One message could unlock all of it.

**Contact:**
`https://hf.co/datasets/michsethowusu/english-tigrinya_sentence-pairs/discussions`

> **Title:** Licence for this dataset?
>
> Hello — thank you for publishing these African-language sentence pairs; the
> English–Tigrinya set is the largest we've found.
>
> The repository doesn't state a licence, which unfortunately means we can't use
> it: we're building open language infrastructure that others will build on, so
> we can only adopt data whose terms are clear.
>
> Would you be willing to add a licence file? Something permissive like CC-BY-4.0
> or CC0 would make it usable for the wider community. It would also help to know
> the provenance — the `similarity` column suggests LASER/NLLB-style mining, and
> knowing the upstream source would let downstream users check their obligations.
>
> Same question for `amharic-tigrinya_sentence-pairs` if you're willing.
>
> [Your name]

**Unblocks:** translation work; a large share of the usable data.
**Note:** even licensed, it needs contamination screening under **DEC-008**.

---

## 🟠 A-06 — Legal review of TiQuAD's copyright position

**Not a research question — a legal one.**

TiQuAD is CC-BY-SA-4.0, but its card states plainly that the authors *"do not own
the copyright to the original news articles… used under fair use principles for
academic research purposes only."* Sources are the Eritrean Ministry of
Information and *Hadas Ertra*.

**The question:** academic evaluation use is defensible, but is use inside
infrastructure that others build on — possibly commercially — covered? A
CC-BY-SA licence cannot grant rights the licensor does not hold.

**What to do:** get a view from someone competent in copyright/fair use before
TiQuAD is used beyond internal evaluation. Same question applies to
`haddas-tigrinya-corpus` (newspaper-derived) and any news-sourced corpus.

**Unblocks:** whether TiQuAD-derived work can ship. Referred to `11_business`.

---

## 🟡 A-07 — HornMorpho licence and Tigrinya version status

HornMorpho is the **only established Tigrinya morphological analyser**, and
DEC-006 puts morphology on the critical path. Three unknowns:

1. **Licence** — unknown. Blocks adoption under **P-9**.
2. **Tigrinya version** — docs say *"Version 5 replaces Version 4.5 for Amharic.
   For other languages, see Version 4.3."* **Does v5.3.5 fully support Tigrinya,
   or should Tigrinya users be on 4.3?**
3. **Maintenance** — not on PyPI; GitHub-only, hand-built wheel.

**Also check `fgaim/HornMorpho`** — a GeezLab fork exists, and may be the
Tigrinya-relevant line of development. Ask in A-01 if convenient.

**Contact:** GitHub issues on `hltdi/HornMorpho`.

**Why I couldn't do this:** GitHub is unreachable from my session and `add_repo`
refuses cross-owner repositories. See `docs/research/RESEARCH_ACCESS.md`.

---

## 🟡 A-08 — Set an `HF_TOKEN` for this environment

The Hugging Face tools run **anonymously**, with rate limits — which is partly
why the connector dropped repeatedly mid-session and slowed the corpus work.

**What to do:** create a token at `https://hf.co/settings/tokens` (read scope is
enough) and add it per `https://hf.co/settings/mcp/`.

**Unblocks:** faster, more reliable dataset inspection — which is now a required
step under DEC-008 and the size-tag finding.

---

## 🟡 A-09 — Arrange a session with unrestricted egress

`arxiv.org`, `aclanthology.org`, publisher domains, Semantic Scholar, Wikipedia,
and `*.github.io` are **blocked by egress policy** in this environment. That is
why several findings are marked `[reported]` rather than `[verified]`.

**The verification backlog** (full list in `docs/research/RESEARCH_ACCESS.md`):

- **arXiv 2507.17974** — the Tigrinya NLP survey. Highest-value source; never read.
- **arXiv 2509.08812** — MoVoC, incl. the 21→6 fertility claim, and its **released
  morpheme data** which may be directly reusable.
- **ACL 2023 TiQuAD paper** — resolve the baseline discrepancy (card says F1
  56–62; a search summary claimed 81%).
- **CoDET (2305.17267)** — the COMET 0.82/0.80 dialect figures behind DEC-004.
- **TiNC24** — 200K-word NER corpus, never located.
- **`tigrinyanlp.github.io`** — a Tigrinya NLP resource hub.
- **HornMT** (`github.com/gebre/HornMT`) — an unassessed corpus lead.

---

## 🟢 A-10 — Introduce the project to GeezLab and L3S

Not blocking, but **G-11** (contribute back) and genuinely mutual. The ecosystem
is small, active, and fragmented — nobody else is building the integration layer.

- **Fitsum Gaim / GeezLab** — most of our reuse plan rests on their work. Fold
  into A-01.
- **Hailay Kidu Teklehaymanot** (L3S, Leibniz Universität Hannover) — current
  en–ti MT work, TIGQA, custom tokenizers. Directly adjacent to DEC-007.
- **MoVoC authors** — closest published work to our tokenizer problem, with
  released morpheme data for four Ge'ez-script languages.

---

## 🟢 A-11 — Licence clarification on `fidel`

`fidel` (PyPI) does Ge'ez ↔ Latin transliteration but states **no licence**.
Minor: Epitran already covers our decomposition need (DEC-007), so this is a
nice-to-have alternative.

**Contact:** `https://github.com/nypava/Fidel`

---

## ⏸️ A-12 — Choose the project licence

**Deliberately deferred**, not forgotten. Our licence interacts with the licence
of every model and dataset we adopt, so it cannot sensibly be chosen before
A-01, A-05, and A-06 resolve. Owned by `11_business`.

---

## 🟠 A-13 — Native-speaker variety audit of the evaluation anchors

**A measurement I cannot make, and it changes what our scores mean.**

**DEC-005** names TiQuAD and FLORES+ as evaluation anchors. They appear to be in
**different varieties of Tigrinya**:

- **TiQuAD** — `[verified]` Eritrean-sourced (Eritrean Ministry of Information,
  *Hadas Ertra*).
- **FLORES+ Tigrinya** — `[verified]` orthographically inconsistent with itself
  (both `ጸ`- and `ፀ`-series tsade; both `ኣ` and `አ` alef, in one file), and
  `[strong signal]` Ethiopian-leaning: `እስካብ` ×2, `ብሄራዊ` ×1, `እንትኸውን` ×1, with
  **zero** Eritrean counterparts among the diagnostic forms.

**What I need from a native speaker** — ideally one Eritrean and one Ethiopian
Tigrinya speaker, separately:

1. Read ~30 sentences of FLORES+ Tigrinya. **Which variety does this read as?**
   Natural, or translated-from-Amharic?
2. Same for a TiQuAD sample.
3. Are the mixed `ጸ`/`ፀ` and `ኣ`/`አ` spellings **normal variation** or **errors**?
4. Would an Eritrean reader find the FLORES+ text odd — and vice versa?

**Why it matters:** **DEC-010** already forbids aggregating scores across
varieties, so the harness is safe either way. But if confirmed, it means the
field's published Tigrinya translation scores describe **Ethiopian Tigrinya**
while being reported as "Tigrinya" — worth writing up for the ecosystem
(**G-11**).

**Why I could not do this:** it requires native fluency and dialect intuition.
Stating it as fact from character-frequency counts would be exactly the
overconfidence this project's rules exist to prevent.

---

## Done

*(Move completed items here with outcome and date. The outcome is often itself a
research finding — record it in `docs/research/` too.)*

| ID | Action | Outcome | Date |
| --- | --- | --- | --- |
| — | *Nothing completed yet* | — | — |
