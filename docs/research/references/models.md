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

### ⚠️ Licence-chain audit — 2026-09-01, `[verified]` against the live Hub

A declared licence on a fine-tune is not a licence for what it was built from.
Re-checked against Hub metadata and each model's own card:

| Model | Declares | Its stated base | Base declares | Chain |
| --- | --- | --- | --- | --- |
| `fgaim/tiroberta-bi-encoder` | **apache-2.0** | `fgaim/tiroberta-base` (named in its README) | **NOT STATED** | ⚠️ **unresolved** |
| `fgaim/tielectra-bi-encoder` | **apache-2.0** | TiELECTRA line | **NOT STATED** | ⚠️ **unresolved** |
| `Hailay/entimt-en-tigrinya-mt` | cc-by-4.0 | `facebook/nllb-200-distilled-600M` | **cc-by-nc-4.0** | ❌ **conflict — a derivative cannot drop the NC** |

**What this changes.** The readiness plan was corrected on 2026-08-23 to say
"Tier 1 is blocked on A-09 alone", on the grounds that the bi-encoders are
Apache-2.0. That is right about the *declared* licence and incomplete about the
*chain*: the weights the bi-encoder was fine-tuned from carry no licence at all.
**A-01 therefore does touch Tier 1** — not as a blocker on the bi-encoder's own
tag, but as an unresolved question about what it is derived from. Ask the author
about the base models and the fine-tunes in the same message.

**`Hailay/entimt-en-tigrinya-mt` is the cautionary case**, and it is exactly the
trap DEC-011 exists to avoid: a model that looks shippable by its own tag while
its base is non-commercial. Do not adopt it. Its own card also reports
**en→ti BLEU 0.133 / chrF 4.99** with severe repetition — see below.

**Provenance worth recording:** `tiroberta-base` was pretrained on **40 million
tokens for 40 epochs** (its card). That is a very small pretraining budget, and
it is the foundation under our chosen embedding model.

⚠️ **Contamination note for DEC-026.** The bi-encoder card says it is "trained
on Tigrinya question-answering and information retrieval datasets" — the
plausible source is TiQuAD, which is also one of DEC-005's evaluation anchors.
**Scoring this model on anything TiQuAD-derived would be contaminated.** Not yet
confirmed with the author; recorded so it is not discovered after the fact.

## Other Tigrinya models

| Model | Task | Base | Licence | Verdict |
| --- | --- | --- | --- | --- |
| `Hailay/entimt-en-tigrinya-mt` | translation | NLLB-200-distilled-600M | cc-by-4.0 ⚠️ *(conflicts with its CC-BY-**NC**-4.0 base)* | ❌ **Do not adopt** — licence conflict, and its own card reports en→ti chrF **4.99** with severe repetition |
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

| Model | Licence | Note |
| --- | --- | --- |
| **MADLAD-400-3B** (`google/madlad400-3b-mt`) | **Apache-2.0** | ⭐ **ADOPTED as the translation baseline — DEC-011.** Absent from this list until 2026-08-23, which is how the reference omitted the one model we actually chose. ⚠️ **Never scored** — its quality is assumed (**A-09**) |
| **NLLB-200** (facebook) | ⛔ **CC-BY-NC-4.0** | **Measurable, never deployable (DEC-011).** Every variant is non-commercial, so it is a research comparison baseline only. The evaluation harness marks it `shippable=False` and prints `COMPARISON ONLY`, because a licence rule nobody enforces is a licence rule that gets broken. `[reported]`: into Tigrinya supported only from French and Spanish in some deployments — **verify** |
| **AfroXLM-R** | see repo | Used as a base by `Abelex`; African-language multilingual encoder |
| **Google Translate** | proprietary | Supports Tigrinya; `[reported]` outperforms NLLB on accuracy/fluency. **Baseline to measure against, never a dependency** (A-001, R-005) |

⚠️ **The NC constraint is the trap in this table.** Several attractive Tigrinya
fine-tunes descend from NLLB-200 and inherit **CC-BY-NC-4.0**. Under **P-9** and
**A-009** that makes them unusable in anything we ship, however good they are.

---

## Not found

- No Tigrinya **grammar-correction** model.
- No Tigrinya **spell-correction** model.
- No Tigrinya **entity-linking** or **knowledge-graph** model.
- No Tigrinya-specific **reranker** or **cross-encoder** (bi-encoders only).
- No **morphological analyser as a served model** — HornMorpho is a library.
