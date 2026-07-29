# Summary: Tigrinya NLP Ecosystem Scan

| Field | Value |
| --- | --- |
| **Summary ID** | `001-tigrinya-nlp-ecosystem-scan` |
| **Full report** | `docs/research/reports/01_ecosystem/001-tigrinya-nlp-ecosystem-scan.md` |
| **Stage** | Scout → Analyst |
| **Date** | 2026-07-29 |
| **Status** | Current |
| **Confidence** | Medium-high |

**One-line answer:** The models we planned to build mostly already exist and are
largely openly licensed — our real gap, and therefore our differentiator, is the
primitives layer (tokenization + morphology), the evaluation harness, and the
API/MCP/SDK surface.

---

## Key Findings

- **A single group dominates.** GeezLab / `fgaim` has published a coherent
  Tigrinya stack: base LMs, embeddings, POS, NER, QA, OCR, classification.
  14 models and 4 datasets. `[verified]` via HF API.
- **`fgaim/tiroberta-bi-encoder` is the single most reusable artefact** — a
  124.6M-param, **Apache-2.0**, `sentence-transformers` Tigrinya embedding
  model. Our embeddings capability may need no training at all. `[verified]`
- **Several key `fgaim` models have NO stated licence**, including
  `tiroberta-base`, the family's foundation. **Blocking under P-9/A-009.**
  `[verified]`
- **Nobody has built the infrastructure layer.** No Tigrinya API, MCP server, or
  SDK found. No production morphology or morphology-aware tokenization service.
  This is the gap. `[verified — by absence]`
- **Morphology-aware tokenization is worth a lot.** MoVoC (EMNLP 2025 Findings)
  reports one Tigrinya sentence going from 21 BPE tokens to 6. But it also
  reports **no significant gain in translation quality** — the benefit is token
  efficiency and linguistic fidelity, not automatically downstream accuracy.
  `[reported]`
- **HornMorpho is the only established Tigrinya morphological analyser**
  (rule-based, covers Amharic/Oromo/Tigrinya). Maintenance status **unverified**
  — and it sits on our critical path. `[reported]`
- **Dialect difference is real, modest, and measurable.** NLLB-3.3B: COMET 0.82
  Ethiopian vs 0.80 Eritrean (CoDET). `[reported]`
- **Speech and OCR have active Tigrinya work** — currently non-goals (N-6, N-7),
  noted in case that changes. `[verified]`
- **Negative result:** unsupervised segmentation (Morfessor) reportedly performs
  poorly on Tigrinya versus rule-based. Do not start there. `[reported]`

## ⚠️ Evidence caveat — and four corrections

**Egress policy blocked arxiv, ACL Anthology, publishers, and Semantic Scholar.**
Paper-derived numbers are `[reported]` from search summaries. HF data is
`[verified]`.

**A same-day verification pass via the HF filesystem API corrected two figures
and surfaced two constraints** (full detail in the report's addendum):

- **C-1** TiQuAD baselines are **F1 56–62, not 81%.** The state of the art for
  Tigrinya QA is lower than this summary first stated.
- **C-2** TiQuAD's **test split is not public** — request-gated. Affects DEC-005
  operationally.
- **C-3** TiQuAD is **Eritrean-sourced**. So Ethiopian-variety QA evaluation is a
  **gap**, not a balanced pair — sharpens DEC-004.
- **C-4** TiQuAD's authors **do not own the source-article copyright**; it is
  fair-use "academic research purposes only" under a CC-BY-SA-4.0 wrapper.
  **A real P-9 risk for infrastructure use** — legal review needed before use
  beyond internal evaluation.

Still `[reported]` and unverified: MoVoC's 21→6 fertility example, the survey's
OOV claims, NLLB's 1.4M pair count, TiNC24's F1 90.18%, and the CoDET COMET
figures. Neither the survey nor MoVoC is indexed on `hf://papers`.

## Important Decisions

| Decision | ID | Status |
| --- | --- | --- |
| Adopt reuse-first posture on the GeezLab stack; build primitives + integration | DEC-003 | Accepted |
| Support both dialects, evaluate and report separately | DEC-004 | Accepted |
| FLORES-200 + TiQuAD as initial evaluation anchors | DEC-005 | Accepted |

## Rejected Alternatives

| Alternative | Rejected because |
| --- | --- |
| Build everything from scratch | Reusable, permissively-licensed artefacts already exist; violates P-1 |
| Wrap commercial APIs (Google/Microsoft) as the primary strategy | No cost control, fails A-001, and does nothing for the primitives gap — which is the actual gap. **Retained as a translation baseline** |
| Fine-tune one large multilingual model for everything | No evidence it serves the primitives; conflicts with P-2 absent a measured gap |
| Start from unsupervised morphological segmentation (Morfessor) | Reported to underperform rule-based approaches on Tigrinya |

## Important Numbers

| Metric | Value | Basis |
| --- | --- | --- |
| `tiroberta-base` params | 124.7M — CPU-servable | `[verified]` HF API |
| `tiroberta-bi-encoder` params / licence | 124.6M / Apache-2.0 | `[verified]` |
| `tiroberta-base` all-time downloads | 7.5K | `[verified]` |
| **Tigrinya data ceiling** | **TiRoBERTa pretrained on 40M tokens** | `[verified]` — the hard number for data scale |
| TiQuAD size | 290 articles · 572 paragraphs · 6,508 questions · 10,637 answers; CC-BY-SA-4.0 | `[verified]` |
| TiQuAD published baselines | **mBERT F1 58.6 · XLM-R F1 62.4 (val)** — ⚠️ **corrected**, was cited as 81% | `[verified]` — see C-1 |
| TiQuAD test split | **Not public** — request-gated to prevent contamination | `[verified]` — see C-2 |
| TIGQA (second QA dataset) | 2.68K pairs · 122 topics · 537 paragraphs, from textbooks | `[verified]` — new find |
| TiALD size | 13,717 YouTube comments, CC-BY-4.0 | `[verified]` |
| GLOCR-Tigrinya | 1M–10M rows, CC-BY-4.0 | `[verified]` |
| en–ti parallel (largest found) | 1M–10M pairs, licence unstated | `[verified]` size class |
| NLLB en–ti corpus / FLORES-200 | 1.4M pairs / 3K eval samples | `[reported]` — **verify** |
| TiNC24 NER | 200K+ words, F1 90.18% | `[reported]` — **verify** |
| MoVoC fertility example | 21 BPE → 6 tokens (one sentence, **not** a corpus average) | `[reported]` — **verify** |
| Dialect gap (NLLB-3.3B COMET) | 0.82 ET vs 0.80 ER | `[reported]` |
| Ge'ez Unicode blocks | U+1200–137F, U+1380–139F, U+2D80–2DDF, U+AB00–AB2F | `[reported]` |

## Recommended Next Steps

1. **Resolve `fgaim` licensing.** Contact the author. *Blocks the core plan.*
2. **Verify HornMorpho's maintenance status** — critical path for morphology.
3. **Locate + licence-check** TLMD, NTC, TiNC24, MoVoC morpheme data.
4. Build the minimal evaluation harness on FLORES-200 + TiQuAD.
5. Benchmark `tiroberta-bi-encoder` on Tigrinya retrieval.
6. Measure tokenizer fertility across existing tokenizers.
7. Approach GeezLab and Hailay Teklehaymanot as collaborators (**G-11**).

## References

1. arXiv 2507.17974 — NLP for Tigrinya: Current State and Future Directions
2. arXiv 2509.08812 / ACL Findings EMNLP 2025 — MoVoC
3. arXiv 2305.17267 — CoDET dialectal MT evaluation
4. https://hf.co/fgaim — the GeezLab namespace
5. https://github.com/hltdi/HornMorpho
6. Springer LRE 2025 — Tigrinya NER / TiNC24
7. AfricaNLP @ ICLR 2023 — Tigrinya–English MT error analysis

---

**Open questions / uncertainty:** Are the unlicensed `fgaim` models usable
(blocking)? Is HornMorpho maintained? Do these models handle both dialects
equally? What is the true total volume of usable Tigrinya text? All
paper-derived figures above need primary-source verification.
