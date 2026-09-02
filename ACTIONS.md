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

**How to use it:** **A-01 and A-02 are blocking**; A-15 is one command
and switches on 28 checks that currently enforce nothing. Each item states what
to do, why, and what it unblocks; where a message is needed, a
**ready-to-send draft** is included — copy, adjust the bracketed fields, send.

**For the order to do them in and what each unlocks**, see
[`docs/roadmap/READINESS_PLAN.md`](docs/roadmap/READINESS_PLAN.md) — the plan of
record. Six of its seven Phase 0 items are here, and they gate almost everything
else.

✅ **A-13 is widened and ready to send.** `validation/PROTOCOL.md` plus
`validation/sheets/` — 134 items, about 25 minutes. ⚠️ Never send `key.json`.

**What to add over time:** New actions as research surfaces them. Move completed
items to the Done section with the outcome and date — the outcome is often
itself a research finding.

**Status values:** `TODO` · `SENT` (awaiting reply) · `BLOCKED` · `DONE`

---

## At a glance

| ID | Action | Priority | Unblocks | Status |
| --- | --- | --- | --- | --- |
| **A-01** | Get licence clarification on the `fgaim` models | 🔴 **Blocking** | DEC-003's wider reuse plan — ⚠️ **not Tier 1**; the bi-encoders are already Apache-2.0 | TODO |
| **A-02** | Confirm DEC-002 (who our primary users are) | 🔴 **Blocking** | API, MCP, SDK design | TODO |
| **A-03** | Report the TiQuAD contamination to `farefaine` | 🟠 High | Ecosystem (G-11); protects others | TODO |
| **A-04** | Request the TiQuAD test set | 🟠 High | DEC-005 — canonical evaluation | TODO |
| **A-05** | Establish terms for the ~603K usable en–ti pairs — **OPUS NLLB mined bitext** | 🟡 Medium *(was Blocking, then High)* | ⚠️ **Weakened twice.** Experiment 009: **56.9% of the "1.4M" rows have no English side at all**, and a published fine-tune on this pool scored chrF **4.99** | TODO |
| **A-06** | Legal review of TiQuAD's copyright position | 🟠 High | Whether we can ship anything using it | TODO |
| ~~**A-07**~~ | ~~Decide how morphology handles GPL-3.0~~ | ✅ **DONE** | Resolved by **DEC-028** — user-installed, never distributed; a hosted service may use it | **DONE** |
| **A-08** | Set an `HF_TOKEN` for this environment | 🟠 **High** *(was Medium)* | **FLORES+ is a gated repo** — the token is what unlocks the full 997/1,012 devtest, the fix for **GAP-3** | TODO |
| **A-09** | **Fetch model weights** — the runtime installs, the weights do not | 🟠 **High** | Scoring any model at all (**GAP-4**), Tier 1 embeddings. *Re-scoped: reading about models is no longer blocked* | TODO |
| **A-10** | Introduce the project to GeezLab / L3S | 🟢 Low | Collaboration (G-11) | TODO |
| **A-11** | Licence clarification on `fidel` | 🟢 Low | Transliteration option | TODO |
| ~~**A-12**~~ | ~~Choose the project licence~~ | ✅ **DONE** | Resolved by **DEC-020** | **DONE** |
| **A-13** | **Find a Tigrinya speaker to review our output** — sheets are built and ready to send | 🔴 **Blocking v0.1** | **Whether any of our Tigrinya is correct** (**GAP-1**); DEC-025; whether DEC-010 is precaution or live correction | **READY TO SEND** |
| **A-14** | Measure Tier 2 cold start | 🟡 Medium | DEC-019 — the deployment mode, and the hosting choice | TODO — *Tier 0 measured (exp 006); Tier 2 still blocked on A-09* |
| **A-15** | **Activate the CI workflow** (one command) | 🟠 High | DEC-018 — every checkable rule is unenforced until this is done | TODO |
| **A-16** | Report epitran's position-sensitive transliteration upstream | 🟢 Low | Nothing — we work around it; but the next user will not know | TODO |
| ~~**A-17**~~ | ~~Decide how the record is dated~~ | ✅ **DONE** | Resolved: **the commit date wins**; 71 stamps corrected | **DONE** |

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

**Unblocks:** DEC-003, the POS service, and every downstream decision that
assumes model reuse.

⚠️ **Corrected 2026-08-23: this does NOT unblock the embeddings service.**
`tiroberta-bi-encoder` and `tielectra-bi-encoder` are already Apache-2.0 — see
the parenthesis above. This entry claimed otherwise for 25 days, and so did the
readiness plan's dependency graph.

> ### ⚠️ Amended 2026-09-01 — the chain, not the tag
>
> That correction was right about the **declared licence** and incomplete about
> what the models are **derived from**. `tiroberta-bi-encoder`'s own card says it
> is "based on [TiRoBERTa-base](https://huggingface.co/fgaim/tiroberta-base)" —
> and `fgaim/tiroberta-base` carries **no licence tag at all** `[verified]`
> against the live Hub. A fine-tune's Apache-2.0 header does not license the
> weights it started from.
>
> **So A-01 does touch Tier 1** — as an unresolved provenance question rather
> than a blocker on the bi-encoder's own tag. Ask about the base models and the
> fine-tunes in the same message; the draft above already covers both.
>
> The cautionary case is in the wild: `Hailay/entimt-en-tigrinya-mt` declares
> **cc-by-4.0** over a **cc-by-nc-4.0** NLLB base. A derivative cannot drop the
> NC. Full audit in `docs/research/references/models.md`.
>
> ⚠️ **And a contamination note**, recorded before it can be discovered after the
> fact: the bi-encoder card says it was trained on "Tigrinya question-answering
> and information retrieval datasets". The plausible source is **TiQuAD**, which
> is also one of DEC-005's evaluation anchors — so scoring this model on
> TiQuAD-derived data would be contaminated. Worth asking the author outright.

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

> **Alternative found 2026-09-01: TIGQA.** *TIGQA: An Expert-Annotated
> Question-Answering Dataset in Tigrinya* (arXiv **2404.17194**) is a second,
> independent expert-annotated QA set that the original research never located.
> Worth assessing before pressing on TiQuAD — **if its source text does not carry
> A-06's unresolved-copyright problem, it may be the better anchor.** The paper
> itself is unread: `arxiv.org` is still egress-blocked (**A-09**).
>
> Hub metadata `[verified]` this session: `fgaim/tiquad` is tagged
> **cc-by-sa-4.0**, 10.6K QA pairs over 572 paragraphs from 290 news articles;
> `fgaim/tigrinya-squad` (machine-translated silver training data, explicitly
> *not* for evaluation) is also cc-by-sa-4.0.

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

> ### ⚠️ Downgraded again 2026-09-02 — and it is not 1.4M
>
> Nobody had looked at the content; the row count was taken on trust.
> **Experiment 009** sampled it through the Dataset Viewer:
>
> | | |
> | --- | --- |
> | Rows with **no English side** (`nan`) | **56.9%** — ~794,900 of 1,398,177 |
> | Ordering | **sorted by descending similarity** (1.2471 → 1.0500) |
> | Target reuse | one Tigrinya sentence across unrelated English sources |
>
> So the prize is **~603,000 pairs, not 1.4M**, sorted so the readable top is
> the best of it. A fifth of the original claim, before licensing is even
> discussed. **Dropped to Medium.**
>
> A suspected **column desync at a constant lag of 26 rows** is recorded as
> **unproven** — it failed its own pre-committed threshold on two data points,
> and the threshold was not moved to rescue it. → `experiments/009-mined-corpus-probe/`

> ### ⚠️ Re-scoped 2026-09-01 — this is not an unlicensed original
>
> `michsethowusu/english-tigrinya_sentence-pairs` holds exactly **1,398,177**
> rows with no licence tag and no provenance on its card. EnTiMT's independently
> compiled source table lists **"OPUS NLLB (mined) — 1,398,173"**. It is
> **web-mined OPUS/NLLB bitext re-uploaded without attribution**, so the
> question is what OPUS and NLLB's terms allow — not what an uploader will grant.
> Emailing the uploader was never the right move.
>
> **And the payoff is much smaller than assumed.** EnTiMT fine-tuned
> NLLB-600M on 1.14M cleaned pairs from this pool for 13 hours and reports
> **en→ti BLEU 0.133, chrF 4.99**, with output degenerating into repeated
> n-grams. Whether that is the data or their tokenizer transplant is not
> isolated — but "the only remedy if MADLAD underperforms" now has a published
> failure attached, and it should stop being described as insurance.
>
> **Dropped from Blocking to High** for that reason. What would actually settle
> it is a contamination screen against FLORES+, which is written and runnable
> and has nothing to read: the corpus exists only as a 110 MB parquet on
> Hugging Face, and direct downloads are still blocked (**A-09**).

**⚠️ Escalated to Blocking, 2026-08-17 (DEC-017).** The training-strategy audit
found we have ~~**zero cleanly-licensed parallel training data**~~ **2,030 pairs**
*(corrected 2026-09-01 — HornMT, CC-BY-4.0; still far below a training rung)* —
FLORES+ and
TiQuAD are evaluation anchors, so training on them is contamination, and this
1.4M-pair corpus is the only other parallel data that exists.

**DEC-011 adopted MADLAD-400-3B without measuring its Tigrinya quality.** If it
underperforms, fine-tuning is the remedy — and it needs parallel data. **Without
A-05 there is no fix available.** This is no longer an optimisation; it is the
insurance policy on our translation decision.

**Note:** even licensed, it needs screening under **DEC-008**/**DEC-015**.

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

**Second question, added 2026-08-10 (DEC-011):** **does a CC-BY-NC-4.0 *model*
licence reach a commercial downstream product, or only the model's own
redistribution?** Every NLLB variant is NC-licensed. We have assumed the strict
reading and chosen an Apache-2.0 alternative at 4.8× the parameters — a real
cost we accepted on a conservative interpretation. **If the permissive reading is
correct, NLLB becomes available and the cost disappears.** Worth asking in the
same conversation.

**Unblocks:** whether TiQuAD-derived work can ship. Referred to `11_business`.

---

## ✅ A-07 — Morphology under GPL-3.0 · **RESOLVED by DEC-028, 2026-09-02**

**HornMorpho is GPL-3.0.** Verified 2026-09-01 from
[`hltdi/HornMorpho/LICENSE.txt`](https://raw.githubusercontent.com/hltdi/HornMorpho/master/LICENSE.txt)
— the full GPLv3 text. Nobody needs to be emailed.

The three unknowns this action was opened for:

| Question | Answer |
| --- | --- |
| **Licence** | **GPL-3.0** `[verified]` — full text in `LICENSE.txt` |
| **Tigrinya version** | **v5.3 supports Tigrinya and Tigre** alongside Amharic and Oromo; latest is **5.3.6, April 2026** |
| **Maintenance** | Confirmed **not on PyPI** (404). `setup.py` declares **no licence metadata at all** — the licence exists only as `LICENSE.txt` |

⚠️ **This was answerable the whole time.** The action said *"GitHub is
unreachable from my session"*. `raw.githubusercontent.com` responds 200 and
does today — see `RESEARCH_ACCESS.md`. A blocker sat on the register for weeks
because an access assumption was never re-tested.

### What it becomes: a decision, and it collides with DEC-020

**DEC-020 chose Apache-2.0 for code, explicitly because "no code dependency
imposes copyleft".** HornMorpho does. The direction matters: Apache-2.0 code can
be taken into a GPLv3 work, but **GPLv3 code cannot be redistributed under
Apache-2.0**. Importing HornMorpho into `services/primitives` and shipping the
result is not available to us as DEC-020 stands.

| Option | Consequence |
| --- | --- |
| **Optional dependency — recommended** | We never distribute HornMorpho. `morphology.is_available()` returns `False` until the *user* installs it themselves, and the combination is theirs, not ours. **The stub API already works this way** — this is the least new machinery of any option |
| Out-of-process only | Invoke it as a separate program over IPC. The usual copyleft mitigation, but the boundary is a legal judgement rather than a technical fact, and we would still be shipping it |
| Relicense the platform GPL-3.0 | Contradicts DEC-020, and imposes copyleft on the application developers DEC-002 names as the primary users |
| Don't adopt | Morphology stays a documented gap. **GAP-5 becomes permanent**, and DEC-006's MVP is permanently incomplete by its own definition |
| `fgaim` POS models instead | ⚠️ **Worse** — those carry **no licence at all** (**A-01**). Trading a known copyleft for an unknown |

**Resolved 2026-09-02 → DEC-028: Option A.** HornMorpho is adopted as a
**user-installed dependency we never distribute**. Three consequences worth
carrying:

1. **No distributed artefact may contain it — container images included.**
   Shipping an image with HornMorpho inside *is* distribution of a combined
   work. CI now checks for this.
2. **A hosted service may use it.** HornMorpho is **GPL-3.0, not AGPL-3.0** —
   its §13 is *"Use with the GNU Affero General Public License"*, not AGPL's
   *"Remote Network Interaction"*. Network use is not distribution, so the HTTP
   API may call it server-side. **We may run it for users; we may not hand it
   to them.**
3. **It is not on PyPI**, so it could not have been a dependency or an extra in
   any case. The packaging and licence constraints point the same way.

DEC-020 survives intact, with Amendment 1 recording that its "no dependency
imposes copyleft" basis is now conditional.

**Note on scope:** GPL-3.0 does not stop us *evaluating* HornMorpho or measuring
morphological accuracy against it locally. Only distribution is constrained.

---

## 🟠 A-08 — Set an `HF_TOKEN` for this environment

The Hugging Face tools run **anonymously**, with rate limits — which is partly
why the connector dropped repeatedly mid-session and slowed the corpus work.

**What to do:** create a token at `https://hf.co/settings/tokens` (read scope is
enough) and add it per `https://hf.co/settings/mcp/`.

**Unblocks:** faster, more reliable dataset inspection — which is now a required
step under DEC-008 and the size-tag finding.

> ### ⚠️ Upgraded 2026-09-01 — this is not just about rate limits
>
> **`openlanguagedata/flores_plus` is a GATED repository.** Anonymous access
> returns metadata but `401 Unauthorized` on the rows. That single fact
> reassigns a blocker: the full FLORES+ Tigrinya split — **997 dev / 1,012
> devtest** — is not held back by general egress at all, only by the absence of
> a token.
>
> This is the fix for **GAP-3**, "the evaluation anchors are hollow". The
> translation anchor in use is a **30-sentence sample**; experiment 007 found
> confidence intervals stop being trustworthy below n≈5, which that sample's
> per-variety breakdowns land in. A read-scope token replaces it with the real
> benchmark.
>
> HornMT (2,030 pairs, CC-BY-4.0, now at `data/anchors/hornmt/`) already made
> the anchor 68× larger without a token. FLORES+ is what makes our numbers
> **comparable to published work**, which HornMT alone cannot do.

---

## 🟠 A-09 — Model **weights** cannot be fetched · *re-scoped 2026-09-01*

⚠️ **This was one action covering two different blockers, and only one of them
is real.** Re-measuring the egress policy (see `RESEARCH_ACCESS.md`) split it:

| | Status |
| --- | --- |
| **Reading about models** — licences, cards, provenance, parameter counts, dataset structure | ✅ **Open**, through the Hugging Face connector. Open all along |
| **Installing the runtime** — `torch`, `transformers`, `sentence-transformers` | ✅ **Open** — PyPI is reachable and they install |
| **Fetching model weights** | ❌ **Blocked** — `huggingface.co` direct downloads are refused |
| Papers — `arxiv.org`, `aclanthology.org`, publishers, Semantic Scholar | ❌ Blocked |
| `opus.nlpl.eu`, `tico-19.github.io` | ❌ Blocked |

**So A-09 is now precisely one thing: we have the runtime and cannot get the
weights.** "Score a model through the harness" (**GAP-4**) still cannot happen.
Everything else once filed under A-09 — comparing candidates, auditing licence
chains, reading dataset provenance — is done or doable.

### ⚠️ What that cost us

This action's own backlog listed **"HornMT — an unassessed corpus lead"**, under
the wrong owner (`gebre/HornMT`; it is `asmelashteka/HornMT`). It was never
assessed because the register said GitHub was unreachable. It is **CC-BY-4.0,
2,030 human-translated pairs**, it took one `curl`, and it falsifies the
`[verified]` claim that we had **0 cleanly-licensed parallel sentences**. An
unre-tested access assumption hid the answer to a blocking question for weeks.

**The lesson is mechanical, not moral:** an access map is a measurement, and
measurements go stale. `RESEARCH_ACCESS.md` now carries the date it was taken.

### Still genuinely unread

- **arXiv 2507.17974** — the Tigrinya NLP survey. Highest-value source; never read.
- **arXiv 2509.08812** — MoVoC, incl. the 21→6 fertility claim and its released
  morpheme data. *(Its authors' MT model is now assessed — see `models.md`.)*
- **ACL 2023 TiQuAD paper** — the baseline discrepancy (card says F1 56–62; a
  search summary claimed 81%).
- **CoDET (2305.17267)** — the COMET 0.82/0.80 dialect figures behind DEC-004.
- **TiNC24** — 200K-word NER corpus, never located.
- ~~**HornMT**~~ ✅ **assessed and ingested** — `data/anchors/hornmt/`.
- ~~`tigrinyanlp.github.io`~~ — reachable via WebSearch summaries; low value now.

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

**Re-checked against the live PyPI JSON API, 2026-09-01** — this is now
`[verified]` rather than `[reported]`. Version **0.1.0**, uploaded
**2024-09-17**; `license` is `null`, `license_expression` is `null`, and there
are **no licence classifiers at all**. Not a metadata-reporting artefact: the
package genuinely declares nothing. Unusable under **P-9** until the author
says otherwise.

**Contact:** `https://github.com/nypava/Fidel`

---

## ⏸️ A-12 — Choose the project licence

**Deliberately deferred**, not forgotten. Our licence interacts with the licence
of every model and dataset we adopt, so it cannot sensibly be chosen before
A-01, A-05, and A-06 resolve. Owned by `11_business`.

---

## 🔴 A-13 — Find a Tigrinya speaker to review our output

> **The instrument is built and waiting.** Send them `validation/PROTOCOL.md`
> and the `validation/sheets/` directory — **134 items, about 25 minutes.**
> ⚠️ **Never send `validation/key.json`**; it records which answer is ours, and
> the design depends on the reviewer not knowing.
>
> **Widened 2026-08-23.** This action used to cover only a variety audit of the
> evaluation anchors. That was too narrow. What actually needs a speaker:
>
> | Sheet | Question |
> | --- | --- |
> | **1** | **Is the word-final `ɨ` real?** Experiment 005 found two forms differing on 4.53% of tokens and **could not tell which is correct** |
> | 2, 4 | Are the phonemes right at all? DEC-007 records that we cannot detect systematic errors in `tir-Ethi` |
> | 3 | Does collapsing ጸ/ፀ read as a **correction** of how someone chose to write? |
> | 5 | Is our evaluation material Eritrean, Ethiopian, or mixed? *(the original scope)* |
>
> **If they only have ten minutes, sheet 1 is the one.** It settles a question
> nothing else can, and the answer changes shipped code.
>
> ⚠️ **Re-briefed 2026-09-02 — sheet 5's question changed direction.** It used
> to ask whether our anchors are Eritrean, on the strength of HornMT scoring
> "74/26 Eritrean" on the variety gate. **That number was an artefact.**
> Experiment 010 calibrated the gate against TICO-19, the one reachable corpus
> that declares its variety at source, and found the gate scored a
> *declared-Ethiopian* corpus at 91–95% "Eritrean" — the ratio was dominated by
> ኣ, which both standards use ~4,500 times either way.
>
> Measured properly — segments carrying an **Ethiopian-only** form, which fired
> on **0 of 3,071** declared-Eritrean segments — **HornMT is Ethiopian-consistent
> at 55.5%**, six times the rate of the corpus TICO-19 labels Ethiopian.
>
> So sheet 5 is no longer "confirm our anchors are Eritrean". It is: **our
> primary anchor appears to be Ethiopian-standard, and we would like a speaker
> to say whether that reading is right** — because if it is, every score this
> project reports describes one standard, and DEC-004 commits us to both.
>
> **Please offer to pay.** Expert judgement in a low-resource language is scarce
> and routinely extracted for free. `PROTOCOL.md` invites them to raise it —
> that invitation should be genuine.
>
> See `validation/README.md` for the design and what the results will and will
> not establish.

### Original scope — variety audit

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

## 🟡 A-14 — Measure Tier 2 cold start

**A single number that decides the deployment architecture.**

**DEC-019** sets Tier 2's deployment mode by this rule:

> Keep Tier 2 warm when sustained request rate exceeds
> `3600 / (cold_start_seconds + service_seconds)` per hour. Below it, scale to zero.

Every term is known **except cold start**, and the answer swings hard on it:

| Cold start | Break-even | req/min |
| ---: | ---: | ---: |
| 5 s | 514/hour | 8.6 |
| 10 s | 300/hour | 5.0 |
| **60 s** | **58/hour** | **1.0** |

**What to measure:** time from cold container to first translation returned, for
MADLAD-400-3B under CTranslate2 int8 — load, quantised-weight mmap, and first
forward pass. Also the steady-state per-request service time, since the 2 s used
in the model is assumed, not measured.

**Why I could not do it:** model weights are behind egress policy (**A-09**), so
neither the conversion nor the timing can run here.

**Partial progress 2026-08-19 — Tier 0 only, and it does not close this.**
`experiments/006-tier0-latency/` measured the tier that *is* built: cold start
**3.03 s**, service time **0.045 ms**, break-even **1,187 req/hour**. **98.7% of
that cold start is `epitran` loading**; our own import is 40 ms. Two things
follow, neither of which settles A-14:

- The method and the arithmetic are now exercised end to end, so the Tier 2
  measurement is a matter of running the same script against a loaded model.
- The model swings **~20×** on this parameter, which is the argument for
  measuring rather than assuming it — **for Tier 2, where it decides the mode.**
  Tier 0 is kept warm regardless, so its number changes nothing operationally.

**Still needed:** MADLAD-400-3B under CTranslate2 int8, cold container to first
translation.

**Unblocks:** DEC-019's deployment mode, and the hosting-target choice.

---

## 🟠 A-15 — Activate the CI workflow

**One command. Until it runs, six decision-log rules are enforced by nobody.**

`ci/verify.yml` is written and every check was verified by hand. It is **not
running**, because GitHub refused the push:

```
refusing to allow a GitHub App to create or update workflow
`.github/workflows/verify.yml` without `workflows` permission
```

**What to do** — from a normal clone with write access:

```bash
mkdir -p .github/workflows
git mv ci/verify.yml .github/workflows/verify.yml
git commit -m "Activate CI verification workflow (DEC-018)"
git push
```

**Why it matters:** DEC-018 exists because **DEC-008 spent 15 days as policy
with no mechanism and was silently ignored**. Until A-15 is done, **DEC-018 is in
exactly that state** — and so are DEC-015, DEC-016, and DEC-001's summary rules.

The reproducibility job also doubles as a **dependency regression test**: it is
currently the only thing that would catch `epitran`, `tokenizers`, or
`sacrebleu` changing behaviour under DEC-007's amended numbers.

---

## 🟢 A-16 — Report epitran's position-sensitive transliteration upstream

**Who:** the `epitran` maintainers (David R. Mortensen et al.), via a GitHub
issue on `dmort27/epitran`.

**Blocks:** nothing. We work around it by transliterating word by word, and
`tigrinya_eval.primitives.check_context_divergence` pins the behaviour so a
change is visible. This is courtesy, not a dependency.

**What to report:** with `tir-Ethi`, a word's transliteration depends on text
arbitrarily far away in the input string. For a word at index 72 of a 128-word
line, replacing the line's **first** word changes the output for that word:

| First word | Token 72 |
| --- | --- |
| `ልኡላውነት` | `ʔɨzomɨ` |
| `ኩሉ` | `ʔɨzom` |

The behaviour is deterministic — byte-identical across calls and across a fresh
`Epitran` instance — and local context does not predict it: the word alone, the
word plus the next eight words, and six preceding words plus the word all give
`ʔɨzom`. Across our corpus it affects **4.53%** of word tokens (107 of 2,362),
and **92%** of those are a word-final epenthetic `ɨ` appearing only in the
longer string.

**Reproduce:** `experiments/005-word-boundary-epenthesis/run.py`, section 5.
Version tested: `epitran==1.35.2`.

**Worth mentioning:** we have **not** determined which output is
phonologically correct — that needs a Tigrinya speaker, so the report should
describe the inconsistency, not assert a bug in the phonology.

---

## ✅ A-17 — How the record is dated · **RESOLVED 2026-08-24**

**Answer: the commit date wins.** When a document says it was written on one day
and the commit carrying that line landed on another, the commit is right — it is
the only one of the two that cannot be typed wrong.

**The backlog is corrected.** 257 date corrections across 56 files; every
`DEC-NNN` date mention now agrees with that decision's own record.
`scripts/check_dates.py` holds the count at **0** and fails on any new drift.

**What the finding was:** every document date written between 2026-08-21 and
2026-08-23 said `2026-08-19` — six commits of work stamped with the previous
session's date. Measuring it found the habit was older and wider:

| | |
| --- | --- |
| Stamps earlier than the commit carrying them | **71**, across 34 files |
| Worst gap | **15 days** |
| Ten of the 16 summaries, and eleven reports | dated 2026-08-03, committed on the 17th and 18th |

**One claim was wrong by a factor of six, independently of the drift.**
*"DEC-008 spent three months as policy with no mechanism"* appeared in **eleven
places**. DEC-008 is dated 2026-07-29 and the measurement that found it ignored
ran 2026-08-13 — **15 days**. Three months was never possible: this repository's
first commit is 2026-07-29. Every interval computed from a corrected date was
recomputed:

| Claim | Was | Is |
| --- | --- | --- |
| DEC-008 without a mechanism | three months | **15 days** |
| DEC-022 clause 5 unimplemented | 16 days | **5 days** |
| Assumptions register frozen | three weeks | **25 days** |
| README claimed no licence chosen | sixteen days | **six days** |
| `A-01 → Tier 1` dependency error | three weeks | **25 days** |
| "384/384, zero gaps" left standing | three weeks | **25 days** |
| `is_ethiopic` missing Extended-B | three weeks | **19 days** |

**Why the fix does not trip its own check:** blame attributes a line to whatever
commit last touched it, so the commit that corrected 257 dates would look like
the commit that wrote them all. It is listed in `.git-blame-ignore-revs`, which
blame skips. Nothing is exempted by content — a mechanical commit is made
invisible to blame, and that is all.

---

## Done

*(Move completed items here with outcome and date. The outcome is often itself a
research finding — record it in `docs/research/` too.)*

| ID | Action | Outcome | Date |
| --- | --- | --- | --- |
| **A-07** | Resolve HornMorpho's licence position | **GPL-3.0**, verified from `LICENSE.txt` — never an unknown, just unread. → **DEC-028**: user-installed, never distributed; container images may not contain it; a hosted service may, because it is GPL not AGPL | 2026-09-02 |
| **A-17** | Decide how the record is dated | **The commit date wins.** 71 drifted stamps corrected across 56 files, and the seven intervals computed from them recomputed — one of which, *"DEC-008 spent three months as policy"*, was wrong by a factor of six in eleven places | 2026-08-24 |
| **A-12** | Choose the project licence | **DEC-020** — Apache-2.0 code, CC-BY-4.0 docs, inherit for data. Resolved once the upstream licence map was complete: **no code dependency imposes copyleft**; share-alike enters only through data | 2026-08-17 |
