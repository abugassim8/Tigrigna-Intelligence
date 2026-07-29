# Tigrinya Morphology, Ge'ez Script, and the Tokenization Constraint

| Field | Value |
| --- | --- |
| **Report ID** | `001-morphology-script-and-tokenization` |
| **Domain** | `02_linguistics` |
| **Stage** | Scout → Analyst |
| **Date** | 2026-07-29 |
| **Status** | Accepted |
| **Summary** | `docs/research/summaries/003-morphology-script-and-tokenization.md` |
| **Related decisions** | DEC-007; confirms A-007; informs DEC-006 |

---

## Evidence status

`[verified]` — read from a primary artefact (Hugging Face model/dataset cards,
paper metadata via `hf://papers`).
`[reported]` — from search-engine summaries; `arxiv.org`, `aclanthology.org`,
and publisher domains remain blocked by egress policy.

The core linguistic facts below are `[reported]` but **mutually corroborated
across four independent sources**, which raises confidence above the usual bar
for a single second-hand claim.

---

## Objective

Establish the linguistic facts about Tigrinya that drive technical design, and
resolve whether **A-007** — morphological complexity is a first-order design
constraint — holds. DEC-006 places morphology and tokenization in the minimum
viable platform, making this the project's critical path.

## Research Questions

1. How does Tigrinya morphology work, and what does it imply for tokenization
   and lemmatization?
2. How does the Ge'ez script behave computationally?
3. What normalisation is required before anything else works?
4. What tooling exists, and does it transfer?
5. What does this mean for our tokenizer and morphology services?

---

## Finding 1 — Tigrinya morphology is *both* templatic and agglutinative

`[reported]`, corroborated across sources.

Tigrinya exhibits **both** morphological processes at once:

- **Templatic (root-and-pattern)** — the Semitic hallmark. A consonantal root,
  typically **triconsonantal**, is interleaved with vowel patterns. The standard
  example: root **K-T-B** ('write') → ካተበ *kätabä* 'he wrote' (perfective).
- **Agglutinative** — affixes attach concatenatively on top of the templatic
  stem.

Roots are realised through templatic patterns known as **stems** or **measures**,
which alter semantics or valency via **vowel infixation, consonant gemination,
and affixation**. Measure I is the basic unmarked action; derived measures add
causation, intensity, and similar.

### Why this combination is the hard case

Either process alone is tractable. Together they are not:

| Process | Standard NLP handling | Why it breaks here |
| --- | --- | --- |
| Agglutinative | Subword segmentation works reasonably — morphemes are contiguous | — |
| Templatic | Requires non-concatenative analysis — the root is **discontinuous**, interleaved with vowels | Subword tokenizers assume contiguous substrings. A root split across vowel infixes **cannot** be recovered as a contiguous subword |

**A BPE tokenizer cannot represent a discontinuous consonantal root.** This is
not a tuning problem; it is a representational mismatch. It is the mechanism
behind the reported high OOV rates and "extreme data sparsity", and it is why
morphology is a first-order constraint rather than a refinement.

**A-007 is confirmed.**

## Finding 2 — The Ge'ez script encodes consonant+vowel in a single character

`[reported]`.

Ge'ez script (**ፊደል** *Fidel*) is an **abugida** (syllabary-like), not an
alphabet. **26 consonants × 7 vowel orders ≈ 182 characters.** Each character
encodes a **consonant–vowel pair**, not a single phoneme.

Unicode blocks (`[reported]`, verify against the standard):

| Block | Range |
| --- | --- |
| Ethiopic | U+1200–U+137F |
| Ethiopic Supplement | U+1380–U+139F |
| Ethiopic Extended | U+2D80–U+2DDF |
| Ethiopic Extended-A | U+AB00–U+AB2F |

## Finding 3 — ⚠️ The central technical problem: morpheme boundaries fall *inside* characters

**This is the most important finding in this report.**

Combine Findings 1 and 2. Templatic morphology operates on **consonants and
vowels separately** — the root is consonantal, the pattern is vocalic. But the
Ge'ez script **fuses consonant and vowel into one indivisible character**.

Therefore **a morpheme boundary can fall in the middle of a single Ge'ez
character.** The character is atomic in the encoding but not in the morphology.

Direct corroboration `[reported]`: researchers working on Tigrinya segmentation
have chosen to **transliterate to Latin before segmenting**, precisely because
"the syllabic properties of Tigrinya's letters… can result in alterations of
characters at the segmentation boundaries."

### Consequences — these are architectural, not cosmetic

1. **Character-level segmentation on raw Ge'ez cannot express correct morpheme
   boundaries.** Not "performs worse" — *cannot express*.
2. **Byte-level BPE does not rescue this.** UTF-8 bytes of a Ge'ez character are
   an encoding artefact, not a consonant/vowel decomposition. Splitting mid-byte
   yields no linguistic unit.
3. **A consonant–vowel decomposition layer is required** below tokenization —
   either transliteration or explicit CV decomposition — for morphology-aware
   processing.
4. **Transliteration is therefore not a peripheral capability.** Our scope lists
   it as a user-facing feature; this finding makes it **core infrastructure**
   that other services depend on.

This reframes the tokenizer/morphology relationship: they are not two adjacent
services but one pipeline with a shared representational substrate.

## Finding 4 — Existing evidence on tokenization approaches

| Source | Approach | Reported outcome |
| --- | --- | --- |
| **MoVoC** (EMNLP 2025 Findings) `[reported]` | Morpheme-aware subword vocabulary; morpheme+BPE hybrid | One sentence 21 BPE tokens → 6. Gains in MorphoScore and Boundary Precision. **No significant gain in translation quality.** Released annotated morpheme data for 4 Ge'ez-script languages |
| **arXiv 2509.20209** (Teklehaymanot et al.) `[verified` abstract`]` | Language-specific tokenizer + informed embedding initialisation + domain-adaptive fine-tuning | Custom tokenizer **"substantially outperforms" zero-shot baselines**; BLEU, chrF, and human evaluation; **Bonferroni-corrected** |
| **HornMorpho** `[reported]` | Rule-based analysis, segmentation, generation (Amharic/Oromo/Tigrinya) | The established analyser |
| **Morfessor** `[reported]` | Unsupervised statistical segmentation | **Poor** vs rule-based on Tigrinya |
| **Stemming Tigrinya Words for IR** (COLING 2012) `[reported]` | Stemming for retrieval | Not yet assessed — **directly relevant to our retrieval service** |
| **Nagaoka Tigrinya Corpus / NTC** `[reported]` | POS tagging with morphological patterns | Identifies the `NTC` referenced in `fgaim/tiroberta-pos` metadata |

### Reconciling the apparent contradiction

MoVoC reports **no** significant downstream MT gain; 2509.20209 reports a
**substantial** one. These are not in conflict — they test different
interventions:

- MoVoC changes **vocabulary construction** (which subwords exist).
- 2509.20209 changes **the tokenizer plus embedding initialisation**, and
  fine-tunes domain-adaptively.

**The honest reading:** morphology-aware tokenization reliably improves *token
efficiency and linguistic fidelity*; whether it improves *downstream task
accuracy* depends on what else changes with it. **Do not claim accuracy gains
from tokenization alone** — measure them.

That distinction matters for us because token efficiency is a **cost** lever
(**P-6**) even when accuracy is flat. Fewer tokens per word means cheaper
inference and longer effective context, which is worth having regardless.

## Finding 5 — The data ceiling

`[verified]`: **TiRoBERTa, the strongest available Tigrinya encoder, was
pretrained on 40 million tokens** (40 epochs, TPU v3.8).

For scale, high-resource language models are trained on corpora three to five
orders of magnitude larger. 40M tokens is small enough that:

- Data-hungry methods are off the table — confirming **A-002**.
- Rule-based and linguistically-informed methods are comparatively *more*
  attractive here than in high-resource settings, because they encode knowledge
  the data cannot supply. This is the likely explanation for Morfessor's poor
  showing against rule-based approaches.
- **The 40M figure is a planning constraint**, and it belongs in
  `03_data_strategy` as the number to beat.

---

## Alternatives Considered — tokenization/morphology architecture

### Option A — Standard subword tokenizer on raw Ge'ez (BPE/SentencePiece)
Simplest, and what most existing Tigrinya tokenizers do. **Rejected as the
primary path:** structurally cannot represent discontinuous roots or
sub-character morpheme boundaries. Retained as a **baseline to measure against**.

### Option B — Transliterate to Latin, segment, map back
What existing Tigrinya segmentation researchers actually do `[reported]`.
Exposes consonants and vowels as separate units, making templatic analysis
expressible. Cost: a round-trip that must be lossless, and transliteration
scheme choice becomes load-bearing.

### Option C — Explicit consonant–vowel decomposition of Ge'ez characters
Same effect as B without leaving the script: decompose each character into its
consonant and vowel-order components, operate there, recompose. Ge'ez's regular
26×7 structure makes this tractable and, unlike transliteration, it is
**deterministic and trivially reversible**.

### Option D — Adopt HornMorpho and treat morphology as a solved dependency
Attractive under **P-1**. Blocked on the unverified maintenance question, and it
does not by itself solve the tokenizer problem.

### Option E — Morpheme-aware vocabulary (MoVoC-style)
Directly targets the problem and has released data for Tigrinya. Best combined
with B or C rather than used alone.

---

## Tradeoffs

| | A: raw subword | B: transliterate | **C: CV decompose** | D: HornMorpho | E: MoVoC vocab |
| --- | --- | --- | --- | --- | --- |
| Expresses templatic roots | **No** | Yes | Yes | Yes | Partially |
| Reversible / lossless | Yes | Risk of loss | **Deterministic** | n/a | Yes |
| Implementation cost | Lowest | Medium | Medium | Low if maintained | Medium |
| External dependency | None | Scheme choice | None | **Maintenance risk** | Released data |
| Evidence base | Baseline | Used in practice | Inferred from script structure | Established | Published |

---

## Cost Analysis

No compute cost — this is engineering and linguistics work, not training.

| Item | Effort | Note |
| --- | --- | --- |
| CV decomposition layer | Days–2 weeks | Ge'ez's regular 26×7 grid makes this mechanical |
| Normalisation (variant characters) | 1–2 weeks | Needs a real corpus survey first |
| Tokenizer fertility benchmark | Days | Existing tokenizers are on the Hub |
| Adopt HornMorpho | Days | **If** maintained |
| Build morphological analyser | **Months** | Fallback only |

**Token efficiency has a direct, ongoing cost effect.** If morphology-aware
tokenization reduces fertility meaningfully, every downstream inference call
gets cheaper — a **P-6** win independent of any accuracy gain.

---

## Build vs Buy Decision

| Component | Verdict |
| --- | --- |
| CV decomposition / normalisation | **Build** — small, deterministic, no adequate existing option found |
| Transliteration | **Build** — and treat as core infrastructure, not a peripheral feature |
| Morphological analysis | **Adopt HornMorpho if maintained**, else build. Verify first |
| Morpheme-annotated data | **Reuse** — MoVoC's released data for Ge'ez-script languages |
| Subword tokenizer | **Build on top of** the decomposition layer; benchmark against existing Hub tokenizers |
| Stemming for IR | **Evaluate the COLING 2012 work** before building anything for retrieval |

---

## Recommended Approach

**Adopt Option C (explicit consonant–vowel decomposition) as the substrate, with
Option E (morpheme-aware vocabulary) layered on top, and Option A retained as
the measured baseline.** Confidence: **medium-high**.

Rationale: C is deterministic and losslessly reversible, needs no external
dependency, and exploits the script's regular structure. It gets the benefit
that drives researchers to transliteration (Option B) without inheriting
transliteration's ambiguity. It also produces the transliteration capability as
a by-product, which our scope needs anyway.

**What would change this:** if a corpus survey shows Ge'ez decomposition is
messier in practice than the 26×7 grid suggests — variant characters, archaic
forms, non-standard usage — Option B may prove more robust.

---

## Implementation Plan

1. **Ge'ez character inventory + CV decomposition table.** Deterministic
   mapping, exhaustively tested for round-trip losslessness.
2. **Corpus survey of orthographic variation** — which variant spellings occur
   in real text, at what frequency. *Requires corpus access → `03_data_strategy`.*
3. **Normalisation specification**, driven by (2).
4. **Tokenizer fertility benchmark** across existing Hub tokenizers plus our
   decomposition layer. Replicates the MoVoC comparison on our data.
5. **Verify HornMorpho**; if usable, wrap it. If not, scope a builder.
6. **Retrieve MoVoC's released morpheme data** for Tigrinya.
7. **Assess the COLING 2012 Tigrinya stemming work** for the retrieval service.

**Blocked by:** corpus access (step 2), HornMorpho verification (step 5).
**Unblocks:** the tokenizer and morphology services — i.e. all of DEC-006.

---

## Risks

| Risk | Likelihood | Impact | Mitigation |
| --- | --- | --- | --- |
| Ge'ez decomposition messier than the 26×7 grid implies | Medium | Medium | Corpus survey before committing; Option B fallback |
| HornMorpho unmaintained | Medium | **High — critical path** | Verify immediately; MoVoC data as partial fallback |
| Morphology-aware tokenization yields no accuracy gain | **Medium-high** | Low | Token-efficiency gain alone justifies it on cost (P-6). **Do not promise accuracy gains** |
| Orthographic variation worse than expected | Medium | High — silent retrieval failures | Normalisation spec driven by real data, not assumption |
| 40M-token ceiling limits everything downstream | **High** | High | Accept it; favour linguistically-informed over data-hungry methods |
| Transliteration scheme disputes | Medium | Low | Option C avoids the question for internal use |

---

## Open Questions

- What orthographic variation actually occurs, and how often? *(Needs corpus.)*
- Is HornMorpho maintained, and how good is its Tigrinya coverage?
- Does a fifth Ethiopic Unicode block (Extended-B) exist in current Unicode?
- **Register distance** — still unresolved from `00_project_definition`.
- Do the Eritrean and Ethiopian varieties differ **orthographically**, or only
  lexically and phonologically? Material to DEC-004.

---

## References

1. MoVoC — arXiv 2509.08812 / ACL Findings EMNLP 2025 `[reported]`
2. Low-Resource English–Tigrinya MT — arXiv 2509.20209 `[verified` abstract`]`
3. Tigrinya POS Tagging with Morphological Patterns and the New Nagaoka Tigrinya Corpus `[reported]`
4. Stemming Tigrinya Words for Information Retrieval — COLING 2012, aclanthology C12-3043 `[reported]`
5. HornMorpho — https://github.com/hltdi/HornMorpho
6. Morphological Segmentation with LSTM Neural Networks for Tigrinya `[reported]`
7. `fgaim/tiroberta-base` model card — 40M tokens `[verified]`
8. NLP for Tigrinya survey — arXiv 2507.17974 `[reported]`

---

## Checklist

- [x] **What exists?** HornMorpho (rule-based), MoVoC (morpheme vocab + data), several Hub tokenizers, NTC, LSTM segmentation work, COLING 2012 stemming.
- [x] **What can be reused?** MoVoC's morpheme data; HornMorpho if maintained; existing tokenizers as baselines.
- [x] **What should be built?** CV decomposition layer, normalisation, transliteration, and a tokenizer on top of them.
- [x] **What should not be built?** A morphological analyser before verifying HornMorpho; a raw-Ge'ez subword tokenizer as the primary path; anything unsupervised-statistical as a starting point.
- [x] **Cost estimate?** Days-to-weeks engineering, no compute. Months only if HornMorpho fails and we must build an analyser.
- [x] **Maintenance burden?** Low for a deterministic decomposition layer. HornMorpho is the real exposure.
- [x] **Licensing?** MoVoC data licence unverified. HornMorpho licence unverified. Both must be checked (**P-9**).
- [x] **Technical risks?** Script decomposition complexity, HornMorpho maintenance, no guaranteed accuracy gain, orthographic variation.
- [x] **Final recommendation?** CV decomposition substrate + morpheme-aware vocabulary, with a raw-subword baseline. Medium-high confidence.

## Completion

- [x] Summary at `docs/research/summaries/003-morphology-script-and-tokenization.md`
- [x] References updated
- [x] DEC-007 recorded; A-007 confirmed
- [x] Rejected options logged (R-013 … R-015)
