# Summary: Tigrinya Morphology, Ge'ez Script, and the Tokenization Constraint

| Field | Value |
| --- | --- |
| **Summary ID** | `003-morphology-script-and-tokenization` |
| **Full report** | `docs/research/reports/02_linguistics/001-morphology-script-and-tokenization.md` |
| **Stage** | Scout → Analyst |
| **Date** | 2026-07-29 |
| **Status** | Current |
| **Confidence** | Medium-high |

**One-line answer:** Tigrinya morpheme boundaries can fall *inside* a single
Ge'ez character, so no subword tokenizer operating on raw Ge'ez can represent
them — we need a consonant–vowel decomposition layer beneath tokenization, which
makes transliteration core infrastructure rather than a peripheral feature.

---

## Key Findings

- **Tigrinya is templatic *and* agglutinative.** Triconsonantal roots (K-T-B →
  ካተበ *kätabä* 'he wrote') interleave with vowel patterns, plus concatenative
  affixes on top. Roots are **discontinuous**. `[reported]`
- **A BPE tokenizer cannot represent a discontinuous root.** Subword methods
  assume contiguous substrings. This is a representational mismatch, not a
  tuning problem — and it is the mechanism behind the reported high OOV rates
  and data sparsity. **A-007 confirmed.**
- **⚠️ The central problem: Ge'ez fuses consonant+vowel into one character**
  (abugida, 26 consonants × 7 vowel orders ≈ 182 characters), but templatic
  morphology operates on consonants and vowels *separately*. **So a morpheme
  boundary can fall mid-character.** Researchers already work around this by
  transliterating to Latin before segmenting. `[reported]`
- **Byte-level BPE does not rescue this.** UTF-8 bytes are an encoding artefact,
  not a consonant/vowel decomposition.
- **Transliteration is core infrastructure, not a feature.** Other services
  depend on the decomposition it provides. This changes its priority.
- **The data ceiling is 40M tokens** — TiRoBERTa, the strongest Tigrinya
  encoder, was pretrained on that. `[verified]` Small enough that
  linguistically-informed methods beat data-hungry ones, which explains
  Morfessor's poor showing against rule-based approaches.
- **Two tokenization studies appear to conflict — they don't.** MoVoC found *no*
  significant downstream MT gain; arXiv 2509.20209 found a *substantial* one.
  They test different interventions (vocabulary construction vs. tokenizer +
  embedding initialisation + fine-tuning). **Honest reading: morphology-aware
  tokenization reliably improves token efficiency and fidelity; downstream
  accuracy gains depend on what else changes. Do not claim accuracy from
  tokenization alone.**
- **Token efficiency is a cost win regardless** (**P-6**) — fewer tokens per word
  means cheaper inference, even if accuracy is flat.

## Important Decisions

| Decision | ID | Status |
| --- | --- | --- |
| Consonant–vowel decomposition as the substrate beneath tokenization | DEC-007 | Accepted |
| A-007 (morphology is first-order) — **confirmed**, mechanism identified | — | Assumption upgraded |

## Rejected Alternatives

| Alternative | Rejected because |
| --- | --- |
| Standard subword tokenizer on raw Ge'ez as the primary path | Structurally cannot express discontinuous roots or sub-character morpheme boundaries. **Retained as a measured baseline** |
| Byte-level BPE as the fix | UTF-8 bytes of a Ge'ez character carry no linguistic decomposition |
| Transliterate-to-Latin as the substrate (Option B) | Works, and is what researchers do — but adds scheme-choice ambiguity and round-trip loss risk that CV decomposition avoids. **Kept as fallback** if the script proves messier than expected |
| Build a morphological analyser now | HornMorpho may already serve; verify before spending months (**P-1**) |
| Unsupervised statistical segmentation | Reported poor vs rule-based on Tigrinya; the 40M-token ceiling explains why |

## Important Numbers

| Metric | Value | Basis |
| --- | --- | --- |
| Ge'ez character inventory | 26 consonants × 7 vowel orders ≈ **182 characters** | `[reported]` |
| Ge'ez Unicode blocks | U+1200–137F, U+1380–139F, U+2D80–2DDF, U+AB00–AB2F | `[reported]` |
| Typical root size | **Triconsonantal** (3 consonants) | `[reported]` |
| **Tigrinya data ceiling** | **40M tokens** (TiRoBERTa pretraining) | `[verified]` |
| MoVoC fertility example | 21 BPE → 6 tokens (one sentence, **not** a corpus average) | `[reported]` |
| Effort: CV decomposition layer | Days–2 weeks, no compute | Estimate |
| Effort: build analyser if HornMorpho fails | **Months** | Estimate |

## Recommended Next Steps

1. **Build the Ge'ez CV decomposition table** — deterministic, round-trip tested.
2. **Verify HornMorpho's maintenance status.** *Still blocking; critical path.*
3. **Corpus survey of orthographic variation** → needs `03_data_strategy`.
4. **Benchmark tokenizer fertility** across Hub tokenizers + our layer.
5. **Retrieve MoVoC's released Tigrinya morpheme data** and check its licence.
6. **Assess "Stemming Tigrinya Words for IR"** (COLING 2012) before designing
   anything for the retrieval service.

## References

1. arXiv 2509.08812 / ACL Findings EMNLP 2025 — MoVoC
2. arXiv 2509.20209 — Low-Resource English–Tigrinya MT (`[verified]` abstract)
3. COLING 2012 — Stemming Tigrinya Words for Information Retrieval
4. Nagaoka Tigrinya Corpus / POS tagging with morphological patterns
5. https://github.com/hltdi/HornMorpho
6. `fgaim/tiroberta-base` model card — 40M tokens `[verified]`

---

**Open questions / uncertainty:** What orthographic variation actually occurs
(needs corpus access)? Is HornMorpho maintained? Does a fifth Ethiopic Unicode
block exist? Do the two varieties differ **orthographically** or only lexically
— material to DEC-004. Core linguistic facts here are `[reported]` but
corroborated across four independent sources.
