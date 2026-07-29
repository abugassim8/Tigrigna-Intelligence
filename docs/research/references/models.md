# References — Models

All entries `[verified]` against the Hugging Face Hub API on **2026-07-29**
unless noted. Download counts are all-time as reported at access time.

---

## The GeezLab / `fgaim` stack — primary reuse candidate

Namespace: https://hf.co/fgaim

| Model | Params | Task | Licence | Downloads | Verdict |
| --- | --- | --- | --- | --- | --- |
| `fgaim/tiroberta-base` | 124.7M | fill-mask | **NOT STATED** ⚠️ | 7.5K | Useful — **blocked on licence** |
| `fgaim/tiroberta-bi-encoder` | 124.6M | sentence-similarity | **apache-2.0** | 1.8K | **Most useful artefact found** |
| `fgaim/tielectra-bi-encoder` | — | sentence-similarity | **apache-2.0** | — | Useful — smaller alternative |
| `fgaim/tielectra-small` | — | fill-mask | NOT STATED ⚠️ | 3.2K | Useful if licensed — cheap to serve |
| `fgaim/tiroberta-pos` | 124.1M | POS tagging | NOT STATED ⚠️ | 2.1K | Useful — trained on TLMD + NTC |
| `fgaim/tielectra-small-pos` | — | POS tagging | NOT STATED ⚠️ | — | Useful — smaller |
| `fgaim/tibert-base` | — | fill-mask | NOT STATED ⚠️ | — | Alternative base |
| `fgaim/tiroberta-sentiment` | — | classification | NOT STATED ⚠️ | — | Out of current scope |
| `fgaim/tielectra-small-sentiment` | — | classification | NOT STATED ⚠️ | — | Out of current scope |
| `fgaim/tiroberta-abusiveness-detection` | — | classification | **cc-by-4.0** | — | Out of scope |
| `fgaim/tiroberta-tiald-multi-task` | — | multi-task | **cc-by-4.0** | — | Out of scope |
| `fgaim/tiroberta-geezswitch` | — | Ge'ez script language ID | **cc-by-4.0** | — | **Potentially useful** — script/language detection |
| `fgaim/tielectra-geezswitch` | — | Ge'ez script language ID | **cc-by-4.0** | — | Smaller variant |

⚠️ **BLOCKER:** models marked NOT STATED carry no licence on the repo. Under
**P-9** / **A-009** they are unusable until clarified. Contacting the author is
the top action item from `reports/01_ecosystem/001`.

**`fgaim/tiroberta-bi-encoder`** has DOI `10.57967/hf/6068` and is
`sentence-transformers`-compatible — the direct candidate for the embeddings
service.

## Other Tigrinya models

| Model | Task | Base | Licence | Verdict |
| --- | --- | --- | --- | --- |
| `Hailay/entimt-en-tigrinya-mt` | translation | NLLB-200-distilled-600M | cc-by-4.0 | **Useful** — most recent en–ti MT found (Jul 2026) |
| `Hailay/xlmr-tigrinya-mlm` | fill-mask | XLM-R | apache-2.0 | Useful — trained on NLLB data |
| `Hailay/fasttext-tigrinya` | embeddings | fastText | apache-2.0 | Possibly useful — cheap classical baseline |
| `luel/gemma-3-4b-tigrinya` | text-gen | gemma-3-4b-pt | gemma | Partially useful — 4B needs GPU; licence restrictive |
| `luel/gemma-3-4b-tigrinya-qa` | QA | ↑ | gemma | Same caveats; GGUF quantisations exist |
| `luel/gpt2-tigrinya-medium` / `-small` | text-gen | GPT-2 | mit | Marginal — small and dated (2024) |
| `mewaeltsegay/Tigrinya-BPE-Tokenizer` | tokenizer | — | mit | **Useful baseline** for fertility comparison |
| `mewaeltsegay/Tigrinya-SentencePiece-Tokenizer` | tokenizer | — | — | Useful baseline |
| `mewaeltsegay/Tigrinya-WordLevel-Tokenizer` | tokenizer | — | mit | Useful baseline |
| `Bonnief/tigrinya-nllb-tokenizer` | tokenizer | NLLB | NOT STATED | Baseline |
| `Abelex/afro-xlmr-large-tigrinya-news` | classification | AfroXLM-R | — | Note AfroXLM-R as a base option |
| `Samuael/ethiopic-sec2sec-tigrinya` | seq2seq | T5 | — | Unassessed |

## Out of current scope — recorded for completeness

Speech (**N-6**) and OCR (**N-7**) are non-goals, but active work exists and is
noted in case those non-goals are revisited:

| Model | Task | Licence |
| --- | --- | --- |
| `badrex/Ethio-ASR-tigrinya` | ASR (w2v-bert-2.0) | cc-by-4.0 |
| `Aregay01/whisper-*-tigrinya-*` | ASR (Whisper variants, several) | apache-2.0 |
| `Samuael/tigrinya-asr-characters` | ASR | apache-2.0 |
| `Yonatanhaile2026/tigrinya-trocrprinted` / `-handwritten` | OCR | mit |
| `shetizmo/Tigrinya-tacotron-1.1`, `tigrinya-tts-beta` | TTS | mit |
| `husnainbinmunawar/tigrinya-tts-model` | TTS | — |

## External / multilingual models relevant to Tigrinya

| Model | Note |
| --- | --- |
| **NLLB-200** (facebook) | Supports Tigrinya (`tir_Ethi`). Base of several fine-tunes. `[reported]`: NLLB-200 into Tigrinya supported only from French and Spanish in some deployments — **verify**. |
| **AfroXLM-R** | Used as a base by `Abelex`; African-language multilingual encoder |
| **Google Translate** | Supports Tigrinya; `[reported]` outperforms NLLB on accuracy/fluency. Baseline, not a dependency. |

---

## Not found

- No Tigrinya **grammar-correction** model.
- No Tigrinya **spell-correction** model.
- No Tigrinya **entity-linking** or **knowledge-graph** model.
- No Tigrinya-specific **reranker** or **cross-encoder** (bi-encoders only).
- No **morphological analyser as a served model** — HornMorpho is a library.
