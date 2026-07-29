# Summary: Scope, Users, and Dialect Definition

| Field | Value |
| --- | --- |
| **Summary ID** | `002-scope-users-and-dialect` |
| **Full report** | `docs/research/reports/00_project_definition/001-scope-users-and-dialect.md` |
| **Stage** | Scout → Analyst |
| **Date** | 2026-07-29 |
| **Status** | Current |
| **Confidence** | Medium-high (medium on the user question) |

**One-line answer:** Build for application developers first; support both
Tigrinya varieties with separately-reported evaluation; and make the minimum
viable platform the *primitives* layer — normalisation, tokenization,
morphology, embeddings — plus an evaluation harness, not translation.

---

## Key Findings

- **Speakers number in the millions across two countries** — roughly 60/40
  Ethiopia/Eritrea, plus diaspora. Sources conflict (5M–9.9M range; regional
  figures don't reconcile with the headline). Only the order of magnitude and
  the two-country split are load-bearing, and both are clear. `[reported]`
- **Application developers are the strongest-evidenced primary user.** Several
  Ge'ez keyboard products (GeezIME, GeezKTB, Mesmer) each independently
  re-solve word suggestion and dictionary lookup. That duplication *is* the
  demand signal for a shared layer beneath them. `[verified]` that the products
  exist; `[inferential]` that they'd adopt us.
- **The dialect question is settled by evidence.** CoDET reports NLLB-3.3B at
  COMET 0.82 (Ethiopian) vs 0.80 (Eritrean). The gap is real but modest — one
  model can serve both. Crucially it is **measurable and asymmetric**, so an
  aggregate "Tigrinya" score would silently under-serve Eritrean users.
  `[reported]`
- **The capability stack has gaps at the bottom and the top, not the middle.**
  Layer 0 (normalisation, tokenization, morphology) and Layer 5 (API, MCP, SDKs)
  are unbuilt. Layers 1–2 (embeddings, POS, NER, translation) largely exist.
  **This inverts the naive build plan.**
- **Translation should not be the opening move.** Google Translate is a strong
  incumbent, reportedly beating open alternatives. Measure against it before
  assuming we can improve on it.
- **Register scope remains open.** Data exists at both extremes — TiALD is
  YouTube comments, TiQuAD is news — but nothing characterises the distance
  between them for Tigrinya.

## Important Decisions

| Decision | ID | Status |
| --- | --- | --- |
| Primary users = application developers; secondary = researchers | DEC-002 | **Proposed — needs owner confirmation** |
| Support both dialects; evaluate and report separately, always | DEC-004 | Accepted |
| Minimum viable platform = primitives + embeddings + evaluation harness, behind an API | DEC-006 | Accepted |

> **DEC-002 is a product-owner call, not a research finding.** The evidence
> supports it but does not compel it. Everything else here holds regardless of
> how it resolves.

## Rejected Alternatives

| Alternative | Rejected because |
| --- | --- |
| Lead with translation | Strong incumbent (Google); no clear advantage available; does nothing for the primitives gap everything else depends on |
| Lead with an end-user product | Violates N-1 and N-2 — this is infrastructure |
| Lead with knowledge graph / RAG | Most dependency-heavy layer; no Tigrinya groundwork found |
| Pick one dialect to support | The measured gap is small enough that both are servable; picking one would under-serve millions for no technical gain |
| Aggregate dialects into a single evaluation score | Hides a measurable, asymmetric quality gap — an equity problem, not just a metrics problem |

## Important Numbers

| Metric | Value | Basis |
| --- | --- | --- |
| Tigrinya speakers | ~9.9M claimed; 5M–9.9M across sources | `[reported]`, conflicting |
| Ethiopia (Tigray) | ~4.32M | `[reported]` |
| Eritrea | ~2.54M | `[reported]` |
| Dialect quality gap | COMET 0.82 ET vs 0.80 ER (NLLB-3.3B) | `[reported]` |
| Candidate model size | ~124M params — CPU-servable | `[verified]` |
| Effort: adopt + evaluate existing models | 1–2 weeks | Estimate |
| Effort: evaluation harness | 2–4 weeks | Estimate |
| Effort: morphology if HornMorpho unusable | Months, not weeks | Estimate |

## Recommended Next Steps

1. **Confirm DEC-002 with the project owner** — the only blocking item.
2. Proceed to `02_linguistics`: Ge'ez normalisation and morphology are the
   critical path.
3. Run `03_data_strategy` over the located corpora, licence-checking throughout.
4. Stand up the evaluation harness on FLORES-200 + TiQuAD.

## References

1. `docs/research/reports/01_ecosystem/001-tigrinya-nlp-ecosystem-scan.md`
2. arXiv 2305.17267 — CoDET dialectal MT evaluation
3. Speaker demographics — worlddata.info, worldmapper.org (conflicting)
4. https://hf.co/datasets/fgaim/tiquad · https://hf.co/datasets/fgaim/tigrinya-abusive-language-detection
5. GeezIME, GeezKTB, Mesmer Tigrinya — consumer Ge'ez keyboards

---

**Open questions / uncertainty:** The user determination is inferential — no
direct user research was possible (community forums unreachable). Language-pair
priority, register distance, diaspora-specific needs, and deployment model all
remain open. Demographic figures conflict and were not resolved.
