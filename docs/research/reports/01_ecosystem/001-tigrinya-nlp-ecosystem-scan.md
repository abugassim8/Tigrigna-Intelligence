# Tigrinya NLP Ecosystem Scan

| Field | Value |
| --- | --- |
| **Report ID** | `001-tigrinya-nlp-ecosystem-scan` |
| **Domain** | `01_ecosystem` |
| **Stage** | Scout → Analyst |
| **Date** | 2026-07-29 |
| **Status** | Accepted |
| **Summary** | `docs/research/summaries/001-tigrinya-nlp-ecosystem-scan.md` |
| **Related decisions** | DEC-002, DEC-003, DEC-004, DEC-005 |

---

## ⚠️ Evidence limitation — read before using this report

**Primary academic sources could not be retrieved.** This session's egress policy
blocks `arxiv.org`, `aclanthology.org`, publisher domains (MDPI, Springer,
Nature), `huggingface.co/papers`, and `api.semanticscholar.org` at the proxy
CONNECT level. Per `/root/.ccr/README.md`, these are organisation policy denials
and were not routed around.

Consequently this report has **two tiers of evidence**:

| Marker | Meaning | Source |
| --- | --- | --- |
| `[verified]` | Retrieved directly from a primary API this session | Hugging Face Hub API |
| `[reported]` | From search-engine summaries of papers I could not open | WebSearch |

**Every paper-derived number in this report is `[reported]`, not `[verified]`.**
Titles, venues, and author names are reliable; specific figures quoted from
abstracts are second-hand and must be confirmed against the primary source
before being used in any decision that depends on their precision. This is
flagged again in the summary and is the single most important caveat here.

**Action for a future session with unrestricted egress:** re-verify every
`[reported]` figure below, starting with the four flagged in
"Numbers requiring verification".

---

## Objective

Establish what Tigrinya language technology already exists — models, datasets,
tools, research groups, and commercial products — so that the reuse-first
philosophy (**P-1**) can be applied against real options rather than
assumptions. This report is intended to answer: *what can we take, and what is
genuinely missing?*

## Research Questions

1. What Tigrinya language technology exists today, and how good is it?
2. What models are available, under what licences, and are they usable?
3. What datasets exist, at what scale, and are they licensed for our use?
4. Who works on Tigrinya NLP — researchers, labs, communities, companies?
5. What consumer-facing Tigrinya tools already exist?
6. Where are the genuine gaps?

---

## Headline finding

**The ecosystem is substantially richer than a "low-resource language" framing
would suggest — and it is concentrated in one place.**

A single research group (GeezLab, associated with the Hugging Face user
`fgaim`) has published a coherent, permissively-licensed stack covering language
modelling, embeddings, POS tagging, question answering, OCR, and classification.
This is the most consequential finding in the report: it moves several of our
planned capabilities from "build" to "evaluate and adopt".

The second finding is that **the primitives layer is the real gap.** Morphology
and tokenization have active research but no maintained, production-ready,
Tigrinya-specific service — which is precisely the layer our dependency graph
puts first.

---

## Existing Solutions — Models

All rows `[verified]` against the Hugging Face Hub API on 2026-07-29. Download
counts are all-time and were reported by the API at time of access.

### The GeezLab / `fgaim` stack — the primary reuse candidate

| Model | Params | Task | Licence | Downloads | Created |
| --- | --- | --- | --- | --- | --- |
| [`fgaim/tiroberta-base`](https://hf.co/fgaim/tiroberta-base) | 124.7M | fill-mask (Tigrinya RoBERTa) | *not stated on repo* | 7.5K | Mar 2022 |
| [`fgaim/tiroberta-bi-encoder`](https://hf.co/fgaim/tiroberta-bi-encoder) | 124.6M | sentence-similarity | **apache-2.0** | 1.8K | Apr 2024 |
| [`fgaim/tielectra-bi-encoder`](https://hf.co/fgaim/tielectra-bi-encoder) | — | sentence-similarity | **apache-2.0** | — | Apr 2024 |
| [`fgaim/tielectra-small`](https://hf.co/fgaim/tielectra-small) | — | fill-mask | *not stated* | 3.2K | Oct 2021 |
| [`fgaim/tiroberta-pos`](https://hf.co/fgaim/tiroberta-pos) | 124.1M | POS tagging | *not stated* | 2.1K | Mar 2022 |
| [`fgaim/tielectra-small-pos`](https://hf.co/fgaim/tielectra-small-pos) | — | POS tagging | *not stated* | — | Mar 2022 |
| [`fgaim/tiroberta-sentiment`](https://hf.co/fgaim/tiroberta-sentiment) | — | classification | *not stated* | — | Mar 2022 |
| [`fgaim/tiroberta-abusiveness-detection`](https://hf.co/fgaim/tiroberta-abusiveness-detection) | — | classification | **cc-by-4.0** | — | May 2023 |
| [`fgaim/tiroberta-geezswitch`](https://hf.co/fgaim/tiroberta-geezswitch) | — | Ge'ez-script language ID | **cc-by-4.0** | — | Apr 2022 |
| [`fgaim/tiroberta-tiald-multi-task`](https://hf.co/fgaim/tiroberta-tiald-multi-task) | — | multi-task | **cc-by-4.0** | — | May 2025 |

**`tiroberta-bi-encoder` is the single most directly reusable artefact found.**
It is an Apache-2.0, `sentence-transformers`-compatible Tigrinya embedding model
with a DOI (`10.57967/hf/6068`). Our embeddings service (**G-4**) has a
candidate that may require no training at all.

**Licence gap:** several `fgaim` models — including `tiroberta-base`, the base
of the family — carry **no stated licence** on the repo. Under **P-9** and
**A-009**, unstated licensing is disqualifying until resolved. This is a
tractable problem (contact the author) but it is a blocker, not a footnote.

### Other Tigrinya models

| Model | Task | Base | Licence | Notes |
| --- | --- | --- | --- | --- |
| [`Hailay/entimt-en-tigrinya-mt`](https://hf.co/Hailay/entimt-en-tigrinya-mt) | translation | NLLB-200-distilled-600M | cc-by-4.0 | Jul 2026 — most recent MT work found |
| [`Hailay/xlmr-tigrinya-mlm`](https://hf.co/Hailay/xlmr-tigrinya-mlm) | fill-mask | XLM-R | apache-2.0 | Trained on NLLB data |
| [`luel/gemma-3-4b-tigrinya`](https://hf.co/luel/gemma-3-4b-tigrinya) | text-gen | gemma-3-4b-pt | gemma | Plus a `-qa` variant and GGUF quantisations |
| [`luel/gpt2-tigrinya-medium`](https://hf.co/luel/gpt2-tigrinya-medium) | text-gen | GPT-2 | mit | Small, 2024 |
| [`mewaeltsegay/Tigrinya-BPE-Tokenizer`](https://hf.co/mewaeltsegay/Tigrinya-BPE-Tokenizer) | tokenizer | — | mit | Also WordLevel and SentencePiece variants |
| [`Bonnief/tigrinya-nllb-tokenizer`](https://hf.co/Bonnief/tigrinya-nllb-tokenizer) | tokenizer | NLLB | *not stated* | — |
| [`Yonatanhaile2026/tigrinya-trocr*`](https://hf.co/Yonatanhaile2026/tigrinya-trocrprinted) | OCR | TrOCR | mit | Printed + handwritten, Apr 2026 |
| [`badrex/Ethio-ASR-tigrinya`](https://hf.co/badrex/Ethio-ASR-tigrinya) | ASR | w2v-bert-2.0 | cc-by-4.0 | Out of scope (**N-6**) but noted |

Speech (ASR/TTS) and OCR both have active work. Both are current non-goals
(**N-6**, **N-7**) — recorded so we know the option exists if those non-goals
are ever revisited.

---

## Existing Solutions — Datasets

All `[verified]` via the Hugging Face Hub API unless marked otherwise.

| Dataset | Size | Licence | Type | Notes |
| --- | --- | --- | --- | --- |
| [`fgaim/tiquad`](https://hf.co/datasets/fgaim/tiquad) | 10.6K QA pairs | **cc-by-sa-4.0** | QA, **human-annotated** | 6.5K unique questions, 572 paragraphs, 290 news articles `[reported]` |
| [`fgaim/GLOCR-Tigrinya`](https://hf.co/datasets/fgaim/GLOCR-Tigrinya) | 1M–10M rows | **cc-by-4.0** | OCR / text recognition | Ge'ez script |
| [`fgaim/tigrinya-abusive-language-detection`](https://hf.co/datasets/fgaim/tigrinya-abusive-language-detection) | 13,717 comments | **cc-by-4.0** | classification | TiALD; YouTube-sourced; multi-task |
| [`fgaim/tigrinya-squad`](https://hf.co/datasets/fgaim/tigrinya-squad) | 10K–100K | **cc-by-sa-4.0** | QA, **silver** | Machine-translated SQuAD 1.1 — explicitly silver-standard |
| [`michsethowusu/english-tigrinya_sentence-pairs`](https://hf.co/datasets/michsethowusu/english-tigrinya_sentence-pairs) | 1M–10M | *not stated* | parallel | Largest en–ti parallel set found |
| [`michsethowusu/amharic-tigrinya_sentence-pairs`](https://hf.co/datasets/michsethowusu/amharic-tigrinya_sentence-pairs) | 100K–1M | *not stated* | parallel | Relevant for Ethio-Semitic transfer |
| [`mewaeltsegay/TigrinyaLargeText`](https://hf.co/datasets/mewaeltsegay/TigrinyaLargeText) | 10K–100K | **mit** | monolingual | Articles, for LM training |
| [`SIMBA9657/haddas-tigrinya-corpus`](https://hf.co/datasets/SIMBA9657/haddas-tigrinya-corpus) | 1K–10K | **cc-by-sa-4.0** | monolingual | Eritrean newspaper (*Haddas Ertra*) |
| [`saillab/alpaca_tigrinya_taco`](https://hf.co/datasets/saillab/alpaca_tigrinya_taco) | 10K–100K | *not stated* | instruction | TaCo paper |
| [`farefaine/tigrinya-pretraining`](https://hf.co/datasets/farefaine/tigrinya-pretraining) | 10K–100K | *not stated* | monolingual | Aggregated public sources |
| [`badrex/tigrinya-speech`](https://hf.co/datasets/badrex/tigrinya-speech) | 10K–100K | *not stated* | speech | Out of scope |

`michsethowusu` has published Tigrinya paired with ~20 African languages. Only
the English and Amharic pairs are plausibly relevant to us.

### Datasets referenced in the literature but not directly located

`[reported]` — named in search summaries; **not** found or verified on the Hub:

- **TLMD** (Tigrinya Language Modeling Dataset) — referenced as a training
  dataset in `fgaim` model metadata.
- **NTC** (Nagaoka Tigrinya Corpus) — referenced in `fgaim/tiroberta-pos`
  metadata.
- **TiNC24** — NER corpus, reported as 200K+ words annotated for NER, 118K
  tokens also POS-annotated, 8 entity classes across 10 domains.
- **FLORES-200** — includes Tigrinya; reported 3K evaluation samples.
- **NLLB parallel corpus** — reported 1.4M en–ti sentence pairs.
- **MoVoC morpheme data** — manually annotated morpheme data for four
  Ge'ez-script languages, released with the MoVoC paper.

Locating and licence-checking these is the highest-value follow-up for
`03_data_strategy`.

---

## Papers

`[reported]` throughout — none of these could be opened. Titles and venues are
from search results and are reliable; quoted figures are not independently
confirmed.

| Paper | Venue / ID | Relevance | Reported key finding |
| --- | --- | --- | --- |
| Natural Language Processing for Tigrinya: Current State and Future Directions | arXiv 2507.17974 (Jul 2025) | **Very high** — a survey of exactly our domain | 50+ studies 2011–2025 across 15 downstream tasks; morphology causes high OOV and extreme data sparsity, challenging standard tokenization |
| MoVoC: Morphology-Aware Subword Construction for Ge'ez Script Languages | ACL Findings EMNLP 2025 / arXiv 2509.08812 | **Very high** — directly informs tokenizer | Morpheme+BPE hybrid; example sentence 21 BPE tokens → 6; gains in MorphoScore and Boundary Precision but **no significant gain in translation quality** |
| TiQuAD / Tigrinya QA (Outstanding Paper, ACL 2023) | ACL 2023 | High | Baseline F1 81%, estimated human performance 92% |
| Towards Neural NER in Tigrinya with Large-scale Dataset | Lang. Resources & Evaluation (Springer, 2025) | High | TiNC24; F1 90.18% by fine-tuning |
| Transferring Monolingual Model to Low-Resource Language: Tigrinya | arXiv 2006.07698 / AIMS ACI 2024 | High | Cost-effective transfer beats multilingual models on Tigrinya sentiment |
| Error Analysis of Tigrinya–English MT Systems | AfricaNLP @ ICLR 2023 | High | Google, Microsoft, Lesan compared; mistranslation and omission dominate (MQM-DQF) |
| CoDET: Contrastive Dialectal Evaluation of MT | arXiv 2305.17267 | **High — dialect evidence** | NLLB-3.3B COMET 0.82 (Ethiopian) vs 0.80 (Eritrean) |
| Low-Resource English–Tigrinya MT | arXiv 2509.20209 | Medium | Basis of `Hailay/entimt-en-tigrinya-mt` |
| Text Classification with CNN + Word Embedding: Tigrinya | Information (MDPI) 12(2):52 | Medium | CBOW reported most successful embedding method |
| Morphological Segmentation with LSTM for Tigrinya | — | Medium | Neural segmentation |
| HornMorpho: morphological processing of Amharic, Oromo, Tigrinya | — | **High** | The established rule-based analyser |

---

## Open Source Projects

| Project | What it is | Relevance | Risk |
| --- | --- | --- | --- |
| [HornMorpho](https://github.com/hltdi/HornMorpho) (`hltdi`) | Morphological analysis, segmentation, and **generation** for Amharic, Oromo, Tigrinya. Rule-based. | **Very high** — the only established Tigrinya morphological analyser found | Maintenance status not verified (GitHub not reachable this session). Academic single-lab project — classic abandonment risk. **Verify before depending on it.** |
| [TiQuAD](https://github.com/fgaim/TiQuAD) (`fgaim`) | The QA benchmark repo | High | Tied to GeezLab |
| [flores-OLDI](https://github.com/avidale/flores-OLDI) | FLORES+ MT benchmark, community-maintained | High — evaluation | — |
| Morfessor | Unsupervised morphological segmentation | Low | `[reported]`: performs **poorly** on Tigrinya vs rule-based — a useful negative result |

**Negative result, recorded (P-13):** unsupervised statistical segmentation
(Morfessor) is reported to underperform linguistic rule-based approaches on
Tigrinya. Do not start there.

---

## Commercial and consumer products

| Product | What it does | Notes |
| --- | --- | --- |
| **Google Translate** | Tigrinya MT | `[reported]` outperformed NLLB on accuracy and fluency in a comparative study |
| **Microsoft Translator** | Tigrinya MT | Evaluated in the AfricaNLP error analysis |
| **Lesan.ai** | Ethiopian-language MT | Evaluated alongside Google and Microsoft |
| **GeezIME** | Ge'ez keyboard with word suggestions — Tigrinya, Tigre, Blin, Amharic. iOS, macOS, Android, Windows, Web. User-extensible dictionary. | The most established consumer input tool |
| **GeezKTB** | Free web Ge'ez keyboard; advertises AI chatbot dictionary, voice input, translation, **grammar check** | Claims overlap our scope — worth evaluating |
| **Mesmer Tigrinya Geez Keyboard** | Cross-platform Ge'ez typing | — |
| **GeezWord** | Ge'ez script in MS Office / Adobe | Legacy desktop |
| **Lexilogos** | Online Tigrinya keyboard | Utility |

**Implication for scope:** the *input* problem (keyboards, basic word
suggestion) is well served by existing consumer products. This supports **N-2** —
we should not build consumer input tools. It also means a Tigrinya spell
correction *API* has a plausible consumer already: these keyboard apps.

---

## People and groups

| Who | Affiliation | Output |
| --- | --- | --- |
| **Fitsum Gaim** (`fgaim`) / **GeezLab** | — | By far the most prolific: 14 models, 4 datasets on HF; TiQuAD (ACL 2023 Outstanding Paper); GLOCR; TiALD. **The single most important external party to this project.** |
| **Hailay Teklehaymanot** | L3S Research Center, Leibniz Universität Hannover | En–Ti MT, XLM-R Tigrinya MLM, fastText Tigrinya |
| **HLTDI** (`hltdi`) | Indiana University | HornMorpho |
| `mewaeltsegay`, `luel`, `michsethowusu`, `SIMBA9657`, `farefaine`, `badrex`, `Aregay01`, `Samuael` | Various | Tokenizers, corpora, LMs, ASR, parallel data |

These are **collaborators, not competitors** (**G-11**). Nothing found suggests
anyone is building the integrated infrastructure layer this project proposes.

---

## Ge'ez script — technical facts

`[reported]` Unicode blocks:

| Block | Range |
| --- | --- |
| Ethiopic | U+1200–U+137F |
| Ethiopic Supplement | U+1380–U+139F |
| Ethiopic Extended | U+2D80–U+2DDF |
| Ethiopic Extended-A | U+AB00–U+AB2F |

Verify against the Unicode standard directly in `02_linguistics`. A fifth block
(Ethiopic Extended-B) may exist in recent Unicode versions and was not
confirmed here.

---

## Alternatives Considered — strategic posture

### Option A — Build everything from scratch
Rejected. The ecosystem contains directly reusable, permissively-licensed
artefacts. Violates **P-1** outright.

### Option B — Adopt the GeezLab stack as the foundation, build only the gaps
**Recommended.** Treat `fgaim`'s models as the default starting point for
language modelling, embeddings, and POS; concentrate our own effort on the
primitives (tokenization, morphology), evaluation, and the integration layer
(API, MCP, SDKs) that nobody has built.

### Option C — Wrap commercial APIs (Google Translate et al.)
Rejected as the primary strategy. Fails **A-001** (open-source preference),
gives no cost control, and provides nothing for the primitives layer — which is
where the actual gap is. **Retained as a translation baseline** to measure
against, which is a legitimate and useful role.

### Option D — Fine-tune a large multilingual model for everything
Deferred. Plausible for translation specifically, but no evidence yet that one
model serves the primitives well, and it conflicts with **P-2** absent a measured
gap.

---

## Tradeoffs

| | A: Build all | **B: Adopt + fill gaps** | C: Wrap commercial | D: One big model |
| --- | --- | --- | --- | --- |
| Time to first capability | Very slow | **Fast** | Fast | Medium |
| Operating cost | High | **Low** (124M-param models are CPU-servable) | Per-call, uncontrolled | High (GPU) |
| Licence risk | None | **Medium — several licences unstated** | High (ToS limits) | Medium |
| Maintenance | Very high | **Low–medium** | Low | High |
| Fills the real gap (primitives) | Yes | **Yes** | No | Unclear |
| Consistent with P-1/P-2 | No | **Yes** | Partially | No |

---

## Cost Analysis

Preliminary; refine in `10_infrastructure`.

The reuse-first path is cheap because the candidate models are small. The
`fgaim` family is ~124M parameters — comfortably CPU-servable, no GPU required
for inference at low volume. This is a direct fit with **P-6** and **A-008**.

| Item | One-time | Monthly | Basis |
| --- | --- | --- | --- |
| Evaluating existing models | ~1–2 weeks effort | — | No compute cost beyond a laptop/small VM |
| Serving a 124M encoder (CPU) | — | Low (single small instance) | Model size; **not yet measured** |
| Serving a 4B generative model | — | Substantially higher; likely GPU | `luel/gemma-3-4b-tigrinya` class |
| Commercial MT API | — | Per-call, unbounded | Rejected as primary |
| Training a base model | Large | — | Not justified (**N-5**) — the artefacts already exist |

**Not yet measured**: actual inference latency and cost per request. Deliberately
not estimated — a fabricated figure here would be worse than an admitted gap
(**P-8**).

---

## Build vs Buy Decision

| Capability | Verdict | Basis |
| --- | --- | --- |
| Base language model | **Reuse** | `tiroberta-base` / `tielectra-small` exist — pending licence |
| Embeddings | **Reuse** | `tiroberta-bi-encoder`, Apache-2.0 |
| POS tagging | **Reuse** | `tiroberta-pos` |
| NER | **Reuse / adapt** | TiNC24 + reported F1 90.18% |
| QA | **Reuse / adapt** | TiQuAD is human-annotated, CC-BY-SA-4.0 |
| Translation | **Reuse / adapt** | NLLB + `entimt-en-tigrinya-mt`; benchmark against Google |
| **Tokenization** | **Build (informed by MoVoC)** | Tokenizers exist but none morphology-aware and production-ready |
| **Morphology** | **Adopt HornMorpho if maintained, else build** | Only established analyser; maintenance unverified |
| **Evaluation harness** | **Build** | Components exist (FLORES, TiQuAD); integrated harness does not |
| **API / MCP / SDKs** | **Build** | Nobody has built this — it is our differentiator |
| Spell / grammar | **Build later** | Depends on morphology |
| Knowledge graph | **Defer** | No Tigrinya-specific groundwork found |
| Speech, OCR | **Decline** | **N-6**, **N-7** — but note active work exists |

**This is the report's central conclusion: our differentiator is not models. It
is the primitives layer, the evaluation harness, and the integration surface.**
The models largely already exist.

---

## Recommended Approach

**Adopt Option B.** Confidence: **medium-high**.

1. Treat the GeezLab/`fgaim` stack as the default foundation. **Resolve
   licensing first** — this gates everything.
2. Concentrate our build effort on tokenization + morphology, the evaluation
   harness, and the API/MCP/SDK layer.
3. Use FLORES-200 and TiQuAD as the initial evaluation anchors.
4. Use Google Translate as a translation quality baseline to measure against —
   not as a dependency.
5. Approach `fgaim`/GeezLab and Hailay Teklehaymanot as potential collaborators.

**What would change this:** if the `fgaim` licences cannot be resolved, or if
the models evaluate poorly on data unlike their news-article training
distribution, the reuse path narrows considerably and the build/train calculus
changes.

---

## Implementation Plan

1. **Resolve licensing** on `tiroberta-base` and family. Contact the author.
   *Blocks everything downstream.*
2. **Locate and licence-check** TLMD, NTC, TiNC24, and the MoVoC morpheme data.
3. **Verify HornMorpho's maintenance status** and Tigrinya coverage quality.
4. **Build a minimal evaluation harness** around FLORES-200 + TiQuAD.
5. **Benchmark** `tiroberta-bi-encoder` on a Tigrinya retrieval task.
6. **Measure tokenizer fertility** across existing tokenizers, replicating the
   MoVoC comparison.

**Unblocks:** `02_linguistics`, `03_data_strategy`, `04_model_strategy`,
`08_evaluation`.

---

## Risks

| Risk | Likelihood | Impact | Mitigation |
| --- | --- | --- | --- |
| `fgaim` licences unresolvable | Medium | **High** — invalidates the core reuse plan | Contact author early; identify fallbacks now |
| Single-source concentration on one group | **High** | Medium | Their artefacts are downloadable and mostly openly licensed; mirror what we may |
| HornMorpho unmaintained | Medium | High — morphology is our critical path | Verify early; MoVoC morpheme data is a partial fallback |
| Models trained on news text generalise poorly | Medium | Medium | Evaluate on out-of-domain text explicitly |
| Reported figures inaccurate (egress-blocked) | **High** | Medium | Re-verify against primary sources |
| Ge'ez normalisation inconsistency across sources | Medium | High — silent retrieval failures | `02_linguistics` priority |

---

## Numbers requiring verification

The four figures most load-bearing for later decisions, all `[reported]`:

1. **NLLB en–ti parallel corpus = 1.4M sentence pairs** — sizes the data
   situation.
2. **MoVoC token fertility 21 → 6** — a single illustrative sentence, not a
   corpus average. **Do not quote as a corpus-level statistic.**
3. **TiNC24 = 200K+ words, F1 90.18%** — sets the NER baseline.
4. **CoDET COMET 0.82 vs 0.80 dialect gap** — the basis of DEC-004.

---

## Open Questions

- Are the unlicensed `fgaim` models usable? *Blocking.*
- Is HornMorpho maintained?
- What is the real total volume of usable Tigrinya text? (→ `03_data_strategy`)
- Do the `fgaim` models handle Eritrean and Ethiopian varieties equally?
- Is the GeezKTB "grammar check" real, and what does it do?

---

## References

All added to `docs/research/references/`.

1. Natural Language Processing for Tigrinya: Current State and Future Directions — arXiv 2507.17974
2. MoVoC: Morphology-Aware Subword Construction for Ge'ez Script Languages — ACL Findings EMNLP 2025 / arXiv 2509.08812
3. TiQuAD — https://github.com/fgaim/TiQuAD ; https://hf.co/datasets/fgaim/tiquad
4. Towards Neural NER in Tigrinya with Large-scale Dataset — Springer LRE, 2025
5. CoDET: Contrastive Dialectal Evaluation of MT — arXiv 2305.17267
6. Error Analysis of Tigrinya–English MT Systems — AfricaNLP @ ICLR 2023
7. Transferring Monolingual Model to Low-Resource Language: Tigrinya — arXiv 2006.07698
8. HornMorpho — https://github.com/hltdi/HornMorpho
9. Hugging Face Hub API, `fgaim` namespace — accessed 2026-07-29
10. Machine Translate — Tigrinya — https://machinetranslate.org/tigrinya

---

## Checklist

- [x] **What exists?** A concentrated GeezLab stack, scattered community models, an established rule-based morphological analyser, real evaluation benchmarks, and mature consumer keyboards.
- [x] **What can be reused?** Embeddings (Apache-2.0), base LMs, POS, NER data, QA data, NLLB translation, FLORES-200 + TiQuAD for evaluation.
- [x] **What should be built?** Morphology-aware tokenization, the morphology service, the evaluation harness, and the API/MCP/SDK integration layer.
- [x] **What should not be built?** Base language models, consumer keyboards/input tools, speech, OCR, a from-scratch morphological analyser before evaluating HornMorpho.
- [x] **Cost estimate?** Reuse path is cheap — ~124M-param CPU-servable models. Absolute figures not yet measured; deliberately not fabricated.
- [x] **Maintenance burden?** Low for adopted models; concentration risk on one group; HornMorpho abandonment risk is the main exposure.
- [x] **Licensing?** Mixed. Apache-2.0 and CC-BY on the most important artefacts; **several key models carry no stated licence — a blocker under P-9.**
- [x] **Technical risks?** Licence resolution, HornMorpho maintenance, news-domain overfitting, Ge'ez normalisation inconsistency, unverified reported figures.
- [x] **Final recommendation?** Option B — adopt the existing model layer, build the primitives, evaluation, and integration layer. Medium-high confidence.

## Completion

- [x] Summary written to `docs/research/summaries/001-tigrinya-nlp-ecosystem-scan.md`
- [x] References added to `docs/research/references/`
- [x] Rejected options logged (R-004 … R-007)
- [x] Assumptions updated (A-001, A-002, A-004, A-006, A-007, A-009)
- [x] Decisions recorded: DEC-003, DEC-004, DEC-005
