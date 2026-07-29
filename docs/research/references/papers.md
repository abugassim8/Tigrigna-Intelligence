# References — Papers

> **Access caveat:** none of these papers could be opened during the 2026-07-29
> session — `arxiv.org`, `aclanthology.org`, `api.semanticscholar.org`, and
> publisher domains are blocked by this environment's egress policy. Titles,
> venues, IDs, and author names below are reliable (from search results).
> **Quoted findings are second-hand and marked `[reported]`.** A session with
> unrestricted egress should verify these and upgrade the markers.

---

### Natural Language Processing for Tigrinya: Current State and Future Directions

- **Type:** Paper (survey) · **ID:** arXiv 2507.17974 · **Date:** Jul 2025
- **Tigrinya relevance:** **Direct — highest value single source found**
- **Summary:** Survey of Tigrinya NLP covering 50+ studies from 2011–2025 across
  fifteen downstream tasks (morphology, POS, NER, MT, QA, ASR, TTS, …).
- **Reported findings:** Scarce annotated data is the principal impediment;
  Tigrinya's complex morphology causes high OOV rates and extreme data sparsity,
  challenging standard tokenization and modelling. `[reported]`
- **Verdict:** **Useful — read first.** Likely answers many `02_linguistics` and
  `03_data_strategy` questions outright.
- **Cited in:** `reports/01_ecosystem/001`

### MoVoC: Morphology-Aware Subword Construction for Ge'ez Script Languages

- **Type:** Paper + released data · **ID:** arXiv 2509.08812; ACL Findings EMNLP 2025
- **Tigrinya relevance:** **Direct — informs the tokenizer decision**
- **Summary:** Morpheme-aware subword vocabulary construction; hybrid of
  morpheme-based and BPE tokens. Covers Amharic, Tigrinya, Ge'ez, Tigre.
  **Released manually annotated morpheme data for four Ge'ez-script languages**
  and morpheme-aware vocabularies for two.
- **Reported findings:** One Tigrinya sentence: 21 BPE tokens → 6 morphology-aware
  tokens. Improvements in MorphoScore and Boundary Precision, but **no
  significant gain in automatic translation quality.** `[reported]`
- **Verdict:** **Very useful.** The released morpheme data may be directly
  reusable. Note the honest negative result on downstream MT gains.
- **Cited in:** `reports/01_ecosystem/001`, summary 001

### TiQuAD — Tigrinya Question Answering Dataset

- **Type:** Paper + dataset · **Venue:** ACL 2023 (**Outstanding Paper Award**)
- **Links:** https://github.com/fgaim/TiQuAD · https://hf.co/datasets/fgaim/tiquad
- **Licence:** CC-BY-SA-4.0 · **Relevance:** Direct
- **Reported findings:** 10.6K QA pairs, 6.5K unique questions, 572 paragraphs
  from 290 news articles. Baseline F1 81%; estimated human performance 92%.
- **Verdict:** **Useful — human-annotated and openly licensed.** An evaluation anchor.

### Towards Neural Named Entity Recognition System in Tigrinya with Large-scale Dataset

- **Type:** Paper · **Venue:** Language Resources and Evaluation (Springer), 2025
- **Relevance:** Direct
- **Reported findings:** TiNC24 corpus — 200K+ words NER-annotated, 118K tokens
  also POS-annotated, 8 entity classes across 10 domains. F1 90.18% fine-tuned.
- **Verdict:** **Useful** — but the dataset itself was not located. Finding it
  and checking its licence is a `03_data_strategy` action.

### CoDET: A Benchmark for Contrastive Dialectal Evaluation of Machine Translation

- **Type:** Paper + benchmark · **ID:** arXiv 2305.17267
- **Relevance:** **Direct — the evidence base for DEC-004**
- **Reported findings:** NLLB-3.3B scores COMET 0.82 on the Ethiopian variety of
  Tigrinya vs 0.80 on the Eritrean variety.
- **Verdict:** **Useful.** Only source found quantifying the dialect gap.

### Error Analysis of Tigrinya–English Machine Translation Systems

- **Type:** Paper · **Venue:** AfricaNLP @ ICLR 2023 · **Link:** openreview.net/forum?id=BQVqNyzCxx
- **Reported findings:** Evaluated Google Translate, Microsoft Translator, and
  Lesan. Under MQM-DQF, **mistranslation and omission** are the most frequent
  error types.
- **Verdict:** **Useful** — tells us what MT failure looks like for Tigrinya.

### Transferring Monolingual Model to Low-Resource Language: The Case of Tigrinya

- **Type:** Paper · **ID:** arXiv 2006.07698; also AIMS ACI 2024
- **Reported findings:** Cost-effective transfer learning from strong
  monolingual source models competitive with multilingual models on Tigrinya
  sentiment analysis.
- **Verdict:** **Useful** — supports A-005 (adapt rather than train from scratch).

### Text Classification Based on CNN and Word Embedding for Low-Resource Languages: Tigrinya

- **Type:** Paper · **Venue:** Information (MDPI) 12(2):52
- **Reported findings:** CBOW reported as the most successful word-embedding
  method tested.
- **Verdict:** **Partially useful** — predates current embedding models; treat as
  historical context.

### Morphological Segmentation with LSTM Neural Networks for Tigrinya

- **Type:** Paper · **Relevance:** Direct (morphology)
- **Verdict:** **Potentially useful** — not yet assessed. Neural alternative to
  HornMorpho's rule-based approach.

### Low-Resource English–Tigrinya MT

- **Type:** Paper · **ID:** arXiv 2509.20209
- **Note:** Referenced by `Hailay/entimt-en-tigrinya-mt` on Hugging Face.
- **Verdict:** **Potentially useful** — the method behind a current MT model.

### HornMorpho: a system for morphological processing of Amharic, Oromo, and Tigrinya

- **Type:** Paper + software · **Link:** https://github.com/hltdi/HornMorpho
- **Verdict:** **Very useful** — the established Tigrinya morphological analyser.
  See `projects.md`.

---

## Searched for and NOT found

Recording negative results (**P-13**) so nobody repeats these searches:

- No Tigrinya-specific **grammar-checking** research paper found.
- No Tigrinya **knowledge graph** or **entity linking** work found.
- No Tigrinya **semantic search / IR benchmark** found.
- No Tigrinya **spell correction** research paper found (consumer products
  exist — see `commercial.md`).
- No published **API, MCP server, or SDK** for Tigrinya NLP.
