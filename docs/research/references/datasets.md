# References — Datasets

`[verified]` = confirmed on the Hugging Face Hub API 2026-07-29.
`[reported]` = named in literature, **not located**.

---

## Located and verified

| Dataset | Size | Licence | Type | Verdict |
| --- | --- | --- | --- | --- |
| `fgaim/tiquad` | 10.6K QA pairs | **cc-by-sa-4.0** | QA, **human-annotated** | **Very useful** — evaluation anchor |
| `fgaim/GLOCR-Tigrinya` | 1M–10M rows | **cc-by-4.0** | OCR / text recognition | Useful if N-7 revisited; large Ge'ez text source |
| `fgaim/tigrinya-abusive-language-detection` (TiALD) | 13,717 comments | **cc-by-4.0** | classification | Useful — **rare informal-register source** (YouTube) |
| `fgaim/tigrinya-squad` | 10K–100K | **cc-by-sa-4.0** | QA, **silver** | Partially useful — machine-translated, explicitly silver-standard. **Never use as evaluation data.** |
| `michsethowusu/english-tigrinya_sentence-pairs` | 1M–10M | NOT STATED ⚠️ | parallel | Largest en–ti found — **licence blocks use** |
| `michsethowusu/amharic-tigrinya_sentence-pairs` | 100K–1M | NOT STATED ⚠️ | parallel | Relevant for Ethio-Semitic transfer |
| `mewaeltsegay/TigrinyaLargeText` | 10K–100K | **mit** | monolingual | Useful — cleanly licensed |
| `SIMBA9657/haddas-tigrinya-corpus` | 1K–10K | **cc-by-sa-4.0** | monolingual | Useful — **explicitly Eritrean** (*Haddas Ertra*); important for dialect balance |
| `SIMBA9657/tigrinya-haddas-dataset` | 10K–100K | — | monolingual | Related to above |
| `saillab/alpaca_tigrinya_taco` | 10K–100K | NOT STATED | instruction | TaCo paper; translated instructions |
| `saillab/alpaca-tigrinya-cleaned` | 10K–100K | NOT STATED | instruction | Cleaned variant |
| `farefaine/tigrinya-pretraining` | 10K–100K | — | monolingual | Aggregated public sources |
| `michsethowusu/Code-170k-tigrinya` | 176,999 items | **apache-2.0** | code instructions | Marginal — translated code conversations |
| `badrex/tigrinya-speech` | 10K–100K | — | speech | Out of scope (**N-6**) |
| `Aregay01/Tigrinya_feature_extracted` | 10K–100K | apache-2.0 | speech features | Out of scope |

`michsethowusu` has published Tigrinya paired with ~20 African languages
(Zulu, Xhosa, Swahili, Hausa, Wolof, …). Only **English** and **Amharic** pairs
are plausibly relevant.

## Named in the literature but NOT located

**Finding and licence-checking these is a top `03_data_strategy` action.**

| Dataset | Reported detail | Why it matters |
| --- | --- | --- |
| **TLMD** (Tigrinya Language Modeling Dataset) | Referenced in `fgaim` model metadata | The corpus behind the primary reuse candidates |
| **NTC** (Nagaoka Tigrinya Corpus) | Referenced in `fgaim/tiroberta-pos` metadata | POS training data |
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
