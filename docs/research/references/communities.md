# References — People, Groups, and Communities

Relevant to **G-11** (contribute back to the ecosystem). These are
**collaborators, not competitors** — nothing found suggests anyone else is
building an integrated Tigrinya infrastructure layer.

---

### Fitsum Gaim (`fgaim`) / GeezLab

- **Link:** https://hf.co/fgaim
- **Output:** 14 models, 4 datasets on Hugging Face. TiQuAD (ACL 2023
  **Outstanding Paper**), GLOCR OCR dataset, TiALD abusive-language benchmark,
  the TiRoBERTa/TiELECTRA model families, GeezSwitch script identification.
- **Why they matter:** **By far the most significant external party to this
  project.** Our reuse-first plan (DEC-003) depends substantially on their work.
- **Action:** Contact regarding (a) licence clarification on the unlicensed
  models — *blocking* — and (b) possible collaboration.

### Hailay Teklehaymanot

- **Affiliation:** L3S Research Center, Leibniz Universität Hannover (PhD, CS)
- **Output:** `entimt-en-tigrinya-mt` (NLLB fine-tune), `xlmr-tigrinya-mlm`,
  `fasttext-tigrinya`. Associated with low-resource en–ti MT work
  (arXiv 2509.20209).
- **Why they matter:** Most recent active en–ti translation work found.

### HLTDI — Indiana University

- **Link:** https://github.com/hltdi
- **Output:** HornMorpho — morphological processing for Amharic, Oromo, Tigrinya.
- **Why they matter:** Own the only established Tigrinya morphological analyser,
  which is on our critical path.

### MoVoC authors

- **Venue:** ACL Findings EMNLP 2025 · arXiv 2509.08812
- **Output:** Morpheme-aware subword construction; **released manually annotated
  morpheme data for four Ge'ez-script languages.**
- **Why they matter:** Closest published work to our tokenizer/morphology
  problem, with released data.

### Independent Hugging Face contributors

`mewaeltsegay` (tokenizers, TigrinyaLargeText) · `luel` (Gemma and GPT-2
fine-tunes) · `michsethowusu` (large-scale African parallel corpora) ·
`SIMBA9657` (Eritrean *Haddas* newspaper corpus) · `farefaine` (pretraining
sources, "Qal" LM) · `badrex` (ASR, speech data) · `Aregay01` (Whisper
fine-tunes) · `Samuael` (ASR, seq2seq) · `Yonatanhaile2026` (TrOCR) ·
`Abelex` (AfroXLM-R classification) · `Bonnief` (NLLB tokenizer) ·
`abrhaleitela` (first Tigrinya sentiment dataset)

**Observation:** the community is real, active, and **fragmented** — many
individuals publishing single artefacts with no shared infrastructure,
inconsistent licensing, and no common evaluation. That fragmentation is exactly
the problem this project proposes to solve.

---

## Not yet investigated

- Tigrinya-speaking **user communities** (forums, diaspora orgs, language
  bodies). Not reachable this session; relevant to **G-11** and to validating
  DEC-002.
- **Eritrean and Ethiopian academic institutions** working on Tigrinya.
- **Funding bodies** for African-language technology (→ `11_business`).
