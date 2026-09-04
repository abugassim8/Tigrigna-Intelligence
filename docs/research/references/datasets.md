# References — Datasets

`[verified]` = confirmed on the Hugging Face Hub API 2026-07-29,
**re-checked 2026-09-01** for the rows marked below.
`[reported]` = named in literature, **not located**.

---

## Located and verified

| Dataset | Size | Licence | Type | Verdict |
| --- | --- | --- | --- | --- |
| `fgaim/tiquad` | 290 articles · 572 paragraphs · **6,508 questions · 10,637 answers** | **cc-by-sa-4.0** ⚠️ see caveat | QA, **human-annotated** | **Very useful** — evaluation anchor. See the four notes below |
| `fgaim/GLOCR-Tigrinya` | 1M–10M rows | **cc-by-4.0** | OCR / text recognition | Useful if N-7 revisited; large Ge'ez text source |
| `fgaim/tigrinya-abusive-language-detection` (TiALD) | 13,717 comments | **cc-by-4.0** | classification | Useful — **rare informal-register source** (YouTube) |
| `fgaim/tigrinya-squad` | 10K–100K | **cc-by-sa-4.0** | QA, **silver** | Partially useful — machine-translated, explicitly silver-standard. **Never use as evaluation data.** |
| **HornMT** (`asmelashteka/HornMT`, GitHub) | **2,030 pairs** · 43,511 ti words | **cc-by-4.0** | parallel, **human-translated news** | ✅ **Ingested 2026-09-01** — `data/anchors/hornmt/`. The project's **first cleanly-licensed parallel corpus**; multi-way across 6 Horn languages |
| `michsethowusu/english-tigrinya_sentence-pairs` | **1,398,177 rows** `[verified]` 2026-09-01 | NOT STATED ⚠️ | parallel, **web-mined** | Largest en–ti found — **but see the provenance note below**; it is a re-upload, not an original |
| `michsethowusu/amharic-tigrinya_sentence-pairs` | 100K–1M | NOT STATED ⚠️ | parallel | Relevant for Ethio-Semitic transfer |
| `mewaeltsegay/TigrinyaLargeText` | 10K–100K | **mit** | monolingual | Useful — cleanly licensed |
| `SIMBA9657/haddas-tigrinya-corpus` | 1K–10K | **cc-by-sa-4.0** | monolingual | Useful — **explicitly Eritrean** (*Haddas Ertra*); important for dialect balance |
| `SIMBA9657/tigrinya-haddas-dataset` | 10K–100K | — | monolingual | Related to above |
| `saillab/alpaca_tigrinya_taco` | 10K–100K | NOT STATED | instruction | TaCo paper; translated instructions |
| `saillab/alpaca-tigrinya-cleaned` | 10K–100K | NOT STATED | instruction | Cleaned variant |
| `farefaine/tigrinya-pretraining` | 52.1K rows | NOT STATED ⚠️ | ⛔ **CONTAMINATED** | **DO NOT USE FOR TRAINING.** Advertised as "pretraining sources" but **verifiably contains TiQuAD validation data** (identical context + title + 3-annotation pattern). See DEC-008 |
| `michsethowusu/Code-170k-tigrinya` | 176,999 items | **apache-2.0** | code instructions | Marginal — translated code conversations |
| `badrex/tigrinya-speech` | 10K–100K | — | speech | Out of scope (**N-6**) |
| `Aregay01/Tigrinya_feature_extracted` | 10K–100K | apache-2.0 | speech features | Out of scope |

`michsethowusu` has published Tigrinya paired with ~20 African languages
(Zulu, Xhosa, Swahili, Hausa, Wolof, …). Only **English** and **Amharic** pairs
are plausibly relevant.

### ⚠️ TiQuAD — four verified caveats (2026-07-29)

All `[verified]` from the dataset card:

1. **Test split is NOT public.** Train 4,452 / validation 934 are public; test
   1,122 is **request-gated** (`fitsum.gaim@kaist.ac.kr`) to prevent
   contamination from web-crawled training data. Exemplary practice — but our
   harness must complete the request or evaluate on validation and say so.
2. **Baselines are lower than widely quoted.** mBERT EM 42.1 / F1 58.6; XLM-R
   EM 45.8 / F1 62.4 (validation). **Not 81%.** Use 56–62 F1 as the reference
   range.
3. **Eritrean-sourced** — Eritrean Ministry of Information (shabait.com) and
   *Hadas Ertra* newspaper. Under DEC-004, **Ethiopian-variety QA evaluation is
   therefore an open gap.**
4. **Upstream copyright is unresolved.** The authors state they *"do not own the
   copyright to the original news articles… used under fair use principles for
   academic research purposes only,"* with CC-BY-SA-4.0 applied on top.
   **Under P-9 this is a real risk for infrastructure use.** Academic evaluation
   is defensible; redistribution or commercial service use may not be. **Legal
   review required.**

Good practice worth copying: **article-based** train/val/test partitioning to
prevent leakage; up to 3 answer annotations per question on val/test to enable
human-performance estimation; official evaluation script handling article
normalisation.

### TIGQA — a second, distinct Tigrinya QA dataset

`[verified]` via arXiv 2404.17194 metadata. **2.68K QA pairs · 122 topics · 537
paragraphs**, from **Tigrinya and Biology textbooks** (educational domain).
Authors: Teklehaymanot, Fazlija, Ganguly, Patro, Nejdl (L3S Hannover).

**Complements TiQuAD** rather than duplicating it — different domain (textbooks
vs news) and different provenance. **Candidate for the Ethiopian-variety
evaluation gap.** Licence and hosting location not yet verified — locate it.

### ⚠️ The 1.4M "unlicensed" corpus is re-uploaded OPUS NLLB bitext (2026-09-01)

`michsethowusu/english-tigrinya_sentence-pairs` carries **no licence tag and no
provenance** on its card — the card is nothing but a `dataset_info` block. Its
row count is **1,398,177**. EnTiMT's independently compiled source table lists
**"OPUS NLLB (mined) — 1,398,173"**. The four-row difference is consistent with
cleaning, and the schema (`similarity`, `English`, `Tigrinya`) is a mining
pipeline's output.

**It is web-mined bitext re-uploaded without attribution.** Three consequences:

1. **A-05 is not about the uploader.** The terms that matter are OPUS's and
   NLLB's, not a permission an uploader could grant. `opus.nlpl.eu` is
   egress-blocked, so this is still unresolved — but it is a different question
   than the register asked for weeks.
2. **Contamination is unscreened and unscreenable here.** Mined web text is
   exactly where FLORES+ leakage would hide. Our gate is written and runnable;
   the corpus is a 110 MB parquet on Hugging Face and direct downloads are
   refused (**A-09**).
3. ⚠️ **It has already been tried, and it failed.** EnTiMT fine-tuned
   NLLB-600M on 1.14M cleaned pairs from this pool and reports **en→ti BLEU
   0.133, chrF 4.99** with severe repetition. Cause not isolated — their
   tokenizer transplant is a confound — but the assumption that this corpus is
   the remedy if MADLAD underperforms no longer stands unexamined.

### Other parallel sources assessed 2026-09-01, not ingested

| Source | Pairs | Licence | Why not |
| --- | ---: | --- | --- |
| TICO-19 | ~6,142 | **unverified** | `tico-19.github.io` is egress-blocked. Professionally translated, COVID-19 domain — worth revisiting |
| Travis Foundation `Tigrinya-Parallel-Corpus` | ~126,930 | declares **cc-by-sa-4.0** ⚠️ | The majority is scraped from a Jehovah's Witnesses site the authors state they **do not own**; the rest is volunteer-translated Wikipedia text. Same unresolved-upstream shape as **A-06**, at 60× the size |

## Named in the literature but NOT located

**Finding and licence-checking these is a top `03_data_strategy` action.**

| Dataset | Reported detail | Why it matters |
| --- | --- | --- |
| **TLMD** (Tigrinya Language Modeling Dataset) | Referenced in `fgaim` model metadata. **Scale now known:** TiRoBERTa was pretrained on **40M tokens** `[verified]` | The corpus behind the primary reuse candidates — and the project's data ceiling |
| **NTC** (Nagaoka Tigrinya Corpus) | Referenced in `fgaim/tiroberta-pos` metadata. **Source identified:** "Tigrinya POS Tagging with Morphological Patterns and the New Nagaoka Tigrinya Corpus" | POS training data |
| **TiNC24** | 200K+ words NER, 118K POS-annotated, 8 entity classes, 10 domains | Would make NER a reuse rather than build |
| **FLORES-200** (Tigrinya split) | ~3K eval samples; human-reviewed, 204 languages | **Primary MT evaluation anchor** (DEC-005) |
| **NLLB en–ti parallel corpus** | ~1.4M sentence pairs | Would be the largest licensed parallel resource |
| **MoVoC morpheme data** | Manually annotated morphemes, 4 Ge'ez-script languages | Directly reusable for the morphology service |

Related: `Muennighoff/flores200` and `avidale/flores-OLDI` (FLORES+) are
candidate access points for FLORES — verify licence and Tigrinya coverage.

---

## Standing observations

1. **Licensing is the recurring blocker.** Several of the largest and most useful
   datasets state no licence. Under **P-9** they are unusable until resolved.
2. **Register coverage is unusually lucky.** TiALD (YouTube, informal) and
   TiQuAD/news (formal) bracket the register range. Most low-resource languages
   have only formal text.
3. **Dialect provenance is trackable.** `haddas-tigrinya-corpus` is explicitly
   Eritrean; much other work is Ethiopian-sourced. Tracking this per-dataset is
   necessary to honour **DEC-004**.
4. **Contamination risk is concrete.** `fgaim/tigrinya-squad` (silver, MT'd) and
   `fgaim/tiquad` (gold, human) come from the same author and overlapping news
   sources. **Check for overlap before using TiQuAD as held-out evaluation.**
5. **No Tigrinya IR/retrieval evaluation set was found.** If semantic search is
   a target capability, its evaluation set will have to be built (**G-2**).
