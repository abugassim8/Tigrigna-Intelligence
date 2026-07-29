# Rejected Options

## Purpose of this document

A running log of options that were considered and **not** chosen, with the
reason each was rejected.

**Why it exists:** Rejected options come back. Someone — a new contributor, a
new AI session, or you in six months — proposes an approach that was already
evaluated and dismissed for good reasons, and the whole evaluation happens
again. This file is the cheapest possible defence against that.

It also serves a second purpose: rejection reasons expire. An option rejected
because "no Tigrinya support exists" may become viable when support appears. By
recording *why* something was rejected, we make it possible to notice when the
reason no longer holds — rather than treating the rejection as permanent.

**How to use it:**
- **Check here before proposing anything.** If your idea is listed, either
  engage with the recorded reason or explain what has changed.
- Add a row whenever a decision is recorded, covering every alternative that
  lost.
- If a rejection reason stops being true, do not delete the row — add a note and
  raise it for reconsideration.

**What future contributors should add:** Every rejected alternative from every
decision, plus options that were considered informally and dropped before
reaching a formal decision. The informal ones are the most likely to return.

---

## How to write a good rejection reason

Bad: *"Not a good fit."*
Good: *"Requires a GPU always-on to serve, which costs ~$250/month at our
volume — roughly 10× the CPU-served alternative for a quality gain we could not
measure on Tigrinya."*

The test: could someone who has never seen this option decide, from your reason
alone, whether the rejection still applies today? If not, the reason is too
thin.

---

## Rejected options log

| ID | Option | Context | Rejected because | Decision | Date | Revisit if |
| --- | --- | --- | --- | --- | --- | --- |
| R-001 | Ad-hoc research notes, no formal structure | Choosing how to run project research | Findings do not survive across sessions; research gets repeated; decisions become unrecoverable archaeology. The point at which "we'll document it once it settles" pays off never arrives. | DEC-001 | 2026-07-29 | Never — the failure mode is structural |
| R-002 | Full formal RFC process with review gates and sign-off | Choosing how to run project research | Coordination overhead exceeds what a project at this stage can absorb; a process this heavy would be abandoned within weeks, landing us at R-001 with extra steps. | DEC-001 | 2026-07-29 | Team grows to the point where informal review stops catching contradictions |
| R-003 | Nesting the project under a `tigrinya-language-intelligence/` subdirectory | Laying out the repository | The repository *is* the project; a same-named folder inside it adds a redundant path segment to every reference for no benefit. | — | 2026-07-29 | The repository ever hosts a second, genuinely separate project |
| R-004 | Build all Tigrinya models from scratch | Ecosystem scan → strategic posture | Reusable, permissively-licensed Tigrinya models already exist (`fgaim/tiroberta-bi-encoder`, Apache-2.0, 124.6M params, sentence-transformers-compatible). Building would duplicate months of work and violate P-1 outright. | DEC-003 | 2026-07-29 | The existing models prove unusable on evaluation, or their licences cannot be resolved |
| R-005 | Wrap commercial APIs (Google Translate, Microsoft) as the *primary* strategy | Ecosystem scan → strategic posture | No cost control at any volume; fails A-001; and critically it does nothing for the primitives layer (tokenization, morphology), which is where the actual gap is. **Retained as a translation quality baseline to measure against** — that is a legitimate role and not a rejection of the tools themselves. | DEC-003 | 2026-07-29 | Never as the primary strategy; already in use as a baseline |
| R-006 | Fine-tune one large multilingual model to serve every capability | Ecosystem scan → strategic posture | No evidence a single generative model serves the Layer 0 primitives well; conflicts with P-2 absent a measured gap; 4B-class models need GPU, breaking the low-volume cost constraint (A-008, P-6). | DEC-003 | 2026-07-29 | A measured evaluation shows one model beating the specialised stack on primitives *and* cost |
| R-007 | Start morphology from unsupervised statistical segmentation (Morfessor) | Ecosystem scan → morphology approach | `[reported]` unsupervised segmentation performs **poorly** on Tigrinya compared to linguistic rule-based approaches. Recorded so the experiment is not repeated. | — | 2026-07-29 | Substantially more Tigrinya data becomes available, changing what unsupervised methods can learn |
| R-008 | Lead with translation as the first capability | Project definition → minimum viable platform | Google Translate is an established incumbent that `[reported]` outperforms open alternatives; we have no identified advantage; and it leaves the primitives gap — which everything else depends on — unfilled. Translation remains in scope, just not first. | DEC-006 | 2026-07-29 | We measure against Google Translate and find a gap we can credibly close |
| R-009 | Support only one Tigrinya variety | Project definition → dialect scope | The measured quality gap is small (COMET 0.82 ET vs 0.80 ER, `[reported]`), so one model can serve both. Choosing one would exclude millions of speakers for no technical gain. | DEC-004 | 2026-07-29 | Evidence emerges that the varieties diverge enough to require separate models |
| R-010 | Report a single aggregate "Tigrinya" evaluation score | Project definition → evaluation reporting | The dialect gap is real, measurable, and **asymmetric**. An aggregate would let quality degrade for Eritrean users while the dashboard looked healthy — an equity problem, not just a metrics one. | DEC-004 | 2026-07-29 | The measured gap disappears and stays gone across several evaluations |
| R-011 | Use machine-translated benchmarks (`fgaim/tigrinya-squad`) as evaluation data | Evaluation anchors | Silver-standard by the publisher's own description. Machine-translated data cannot serve as ground truth — using it would make every downstream quality claim unfounded. Usable for *training* only. | DEC-005 | 2026-07-29 | Never for evaluation |
| R-012 | Build our own evaluation sets before measuring anything | Evaluation anchors | Would block all measurement for months. FLORES-200 and TiQuAD are human-produced, available now, and carry published baselines that make our numbers comparable to existing work. Building our own remains necessary for retrieval/morphology/spell/grammar, where nothing exists — just not as a precondition for all measurement. | DEC-005 | 2026-07-29 | Partially adopted already — the gap sets are still to be built |
| R-013 | Standard subword tokenizer (BPE/SentencePiece) on raw Ge'ez as the primary path | Tokenization architecture | Structurally **cannot** represent Tigrinya's discontinuous triconsonantal roots, and cannot express morpheme boundaries that fall inside a single Ge'ez character. A representational failure, not a tuning one. **Retained as a measured baseline.** | DEC-007 | 2026-07-29 | Never as the primary path |
| R-014 | Byte-level BPE as the fix for Ge'ez segmentation | Tokenization architecture | UTF-8 bytes of a Ge'ez character are an encoding artefact, not a consonant/vowel decomposition. Splitting mid-byte yields no linguistic unit, so it does not address the actual problem. | DEC-007 | 2026-07-29 | Never — the reasoning is structural |
| R-015 | Transliterate-to-Latin as the tokenization substrate | Tokenization architecture | Works, and is the empirical precedent — but makes transliteration-scheme choice load-bearing and risks round-trip loss. Consonant–vowel decomposition gets the same benefit deterministically. **Kept as the fallback** if the Ge'ez grid proves irregular in practice. | DEC-007 | 2026-07-29 | A corpus survey shows CV decomposition is unreliable on real text |

---

<!--
Add rejected options above this line. Every decision in DECISIONS.md should
contribute at least one row — a decision with no rejected alternatives usually
means the alternatives were not actually explored.
-->
