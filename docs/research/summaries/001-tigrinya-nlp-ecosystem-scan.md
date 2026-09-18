# Summary: Tigrinya NLP Ecosystem Scan

| Field | Value |
| --- | --- |
| **Summary ID** | `001-tigrinya-nlp-ecosystem-scan` |
| **Full report** | `docs/research/reports/01_ecosystem/001-tigrinya-nlp-ecosystem-scan.md` |
| **Date** | 2026-07-29 · re-compressed same day |
| **Status** | Current |
| **Confidence** | Medium-high |

**One-line answer:** The models we planned to build mostly already exist and are
largely openly licensed — our real gap, and therefore our differentiator, is the
primitives layer (tokenization + morphology), the evaluation harness, and the
API/MCP/SDK surface.

---

## Key Findings

- **One group dominates.** GeezLab / [`fgaim`](https://hf.co/fgaim) has published
  a coherent Tigrinya stack: base LMs, embeddings, POS, NER, QA, OCR,
  classification — 14 models and 4 datasets. `[verified]`
- **`fgaim/tiroberta-bi-encoder` is the most reusable artefact found** — 124.6M
  params, **Apache-2.0**, `sentence-transformers`-compatible. Our embeddings
  capability may need no training at all. `[verified]`
- **⛔ Several key `fgaim` models carry NO licence**, including `tiroberta-base`,
  the family's foundation — confirmed absent from the model card itself, not just
  metadata. **Blocking under P-9/A-009.** → **ACTIONS.md A-01** `[verified]`
- **Nobody has built the infrastructure layer.** No Tigrinya API, MCP server, or
  SDK exists; no production morphology or morphology-aware tokenization service.
  **This absence is the opportunity.** `[verified by absence]`
- **The data ceiling is 40M tokens** — what TiRoBERTa was pretrained on. Small
  enough that linguistically-informed methods beat data-hungry ones. `[verified]`
- **HornMorpho is the only established Tigrinya morphological analyser**
  (rule-based; Amharic/Oromo/Tigrinya). **Not on PyPI**, licence unknown, and
  Tigrinya support may lag Amharic — riskier than it first appeared, and on our
  critical path. → **A-07**
- **Dialect difference is real, modest, measurable.** NLLB-3.3B: COMET 0.82
  Ethiopian vs 0.80 Eritrean. `[reported]`
- **Speech and OCR have active Tigrinya work** — currently non-goals (N-6, N-7),
  noted in case that changes. `[verified]`
- **Negative result:** unsupervised segmentation (Morfessor, last release 2019)
  performs poorly on Tigrinya vs rule-based. Do not start there. `[reported]`

## Evidence caveat

Egress policy blocked arxiv, ACL Anthology, publishers, and Semantic Scholar, so
paper-derived figures are `[reported]`, not read from source. HF and PyPI data,
and anything measured by running code, are `[verified]`.

**A same-day verification pass corrected four things** — most importantly
**TiQuAD's baselines are F1 56–62, not the 81% first recorded**, its test split
is request-gated, it is Eritrean-sourced, and its upstream copyright is
unresolved. Full detail in the report's *Verification addendum*; consequences are
carried in DEC-005 and **A-06**.

## Important Decisions

| Decision | ID | Status |
| --- | --- | --- |
| Adopt the existing model layer; build primitives, evaluation, integration | DEC-003 | Accepted |
| Support both dialects, evaluate and report separately | DEC-004 | Accepted |
| FLORES-200 + TiQuAD as initial evaluation anchors | DEC-005 | Accepted, amended |

## Rejected Alternatives

| Alternative | Rejected because |
| --- | --- |
| Build everything from scratch | Reusable, permissively-licensed artefacts already exist; violates P-1 |
| Wrap commercial APIs as the primary strategy | No cost control, fails A-001, and does nothing for the primitives gap — which is the actual gap. **Retained as a translation baseline** |
| One large multilingual model for everything | No evidence it serves the primitives; conflicts with P-2; GPU cost breaks A-008 |
| Start morphology from unsupervised segmentation | Reported to underperform rule-based on Tigrinya |

## Important Numbers

| Metric | Value | Basis |
| --- | --- | --- |
| **Tigrinya data ceiling** | **40M tokens** (TiRoBERTa pretraining) | `[verified]` |
| `tiroberta-base` | 124.7M params, CPU-servable, **no licence** | `[verified]` |
| `tiroberta-bi-encoder` | 124.6M params, **Apache-2.0** | `[verified]` |
| TiQuAD | 6,508 questions / 10,637 answers, CC-BY-SA-4.0 | `[verified]` |
| TiQuAD baselines | **mBERT F1 58.6 · XLM-R F1 62.4** ⚠️ *corrected from 81%* | `[verified]` |
| TiQuAD test split | **Not public** — request-gated | `[verified]` |
| TIGQA (2nd QA set) | 2.68K pairs, 122 topics, textbook domain | `[verified]` |
| TiALD | 13,717 comments, CC-BY-4.0 | `[verified]` |
| en–ti parallel (largest) | 1.4M pairs, **licence unstated** | `[verified]` |
| TiNC24 NER | 200K+ words, F1 90.18% | `[reported]` — verify |
| MoVoC fertility example | 21 BPE → 6 tokens (one sentence, not a corpus average) | `[reported]` — verify |
| Dialect gap | COMET 0.82 ET vs 0.80 ER | `[reported]` |

## Recommended Next Steps

1. **Resolve `fgaim` licensing** (**A-01**) — blocks the core plan.
2. **Verify HornMorpho** licence and Tigrinya version (**A-07**).
3. **Locate + licence-check** TLMD, NTC, TiNC24, MoVoC morpheme data (**A-09**).
4. Build the evaluation harness on FLORES-200 + TiQuAD; request the test split
   (**A-04**).
5. Benchmark `tiroberta-bi-encoder` on Tigrinya retrieval.
6. Approach GeezLab and L3S as collaborators (**A-10**).

## References

1. arXiv 2507.17974 — NLP for Tigrinya survey (unread; egress-blocked)
2. arXiv 2509.08812 / EMNLP 2025 Findings — MoVoC
3. arXiv 2305.17267 — CoDET dialectal evaluation
4. https://hf.co/fgaim — the GeezLab namespace
5. https://github.com/hltdi/HornMorpho

---

**Open questions / uncertainty:** Are the unlicensed `fgaim` models usable
(blocking)? Is HornMorpho maintained, and does v5.3 cover Tigrinya? Do these
models handle both dialects equally? Paper-derived figures above need
primary-source verification.
