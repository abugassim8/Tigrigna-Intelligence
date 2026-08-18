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
| R-016 | Build the consonant–vowel decomposition layer ourselves | Ge'ez tooling survey | Epitran's `tir-Ethi` map already does it — 384/384 coverage, correct Tigrinya phonology, MIT-Modern-Variant, actively maintained. **Building it would have been a P-1 violation caused by not checking a package registry before assuming "build."** | DEC-007 amendment | 2026-07-29 | Epitran becomes unmaintained *and* proves unforkable |
| R-017 | Adopt Epitran as the single text representation | Ge'ez tooling survey | Not reversible — 384 chars collapse to 362 outputs. Any user-facing text output (spell-correction suggestions, transliteration display) would be corrupted. Hence dual representation. | DEC-007 amendment | 2026-07-29 | Never — the map is many-to-one by construction |
| R-018 | Build a reverse mapping from the analysis form back to Ge'ez | Ge'ez tooling survey | Ambiguous by construction: 22 IPA outputs each have two valid Ge'ez sources (ሀ/ኀ, ሠ/ሰ …). No reverse function exists. **Preserve the surface form instead** — it is free and exact. | DEC-007 amendment | 2026-07-29 | Never — this is a mathematical property, not a tooling gap |
| R-019 | Trust Hugging Face `size_categories` tags for corpus planning | Corpus inventory | Measured wrong on **2 of 4** datasets sampled; `farefaine/tigrinya-pretraining` overstates by up to ~20× and its tag contradicts its own metadata. Query the dataset API for actual row counts instead — it is cheap. | DEC-008 | 2026-07-29 | HF adds validated size metadata |
| R-020 | Screen only datasets that look like evaluation data | Contamination policy | **The case that motivated DEC-008 was a dataset labelled "pretraining sources"** that carried TiQuAD's QA schema. A looks-like-evaluation heuristic would have missed it entirely. Screen everything. | DEC-008 | 2026-07-29 | Never — the heuristic is disproven by the founding case |

---

| BLEU as the primary translation metric | DEC-009 | 2026-08-03 | Measured ~1.08x harsher on Tigrinya, and degrades least informatively exactly where low-resource systems operate |
| Dropping BLEU entirely | DEC-009 | 2026-08-03 | Overreaction — the penalty is modest, and BLEU is what every published Tigrinya result reports; dropping it forfeits comparability for no measured gain |
| COMET as the primary metric | DEC-009 | 2026-08-03 | Untestable in this environment (model downloads egress-blocked); adopting an unvalidated learned metric is the exact error the decision exists to prevent. **Revisit** — NLLB's published Tigrinya numbers use it |
| A single aggregate "Tigrinya score" | DEC-010 | 2026-08-03 | The two DEC-005 anchors appear to be in different varieties; the aggregate would describe a language nobody speaks |
| Evaluating one variety only | DEC-010 | 2026-08-03 | Contradicts DEC-004 and abandons roughly half the speaker population |
| Waiting for native-speaker confirmation before designing the harness | DEC-010 | 2026-08-03 | Variety-scoped reporting is correct whether or not the attribution holds; waiting blocks the harness on an unscheduled dependency |
| Citing the literature on metric validity instead of measuring it | DEC-009 | 2026-08-03 | Sources egress-blocked; measurement was available and produced a sharper answer — an ~8% penalty, not the qualitative "unsuitable" the literature is usually summarised as |

| NLLB-200 as the production translation model | DEC-011 | 2026-08-03 | **CC-BY-NC-4.0** — unshippable. Would pass an inherited restriction to downstream users (P-9, A-009), despite being the field's de facto Tigrinya baseline |
| "NLLB now, swap it later" | DEC-011 | 2026-08-03 | Deferring a licence problem does not shrink it — it moves it to the point where the API, published evaluations, and docs all assume the model that must be removed |
| MADLAD-400-7B / 10B | DEC-011 | 2026-08-03 | 3.9–5.0 GB at Q4 versus 1.4 GB for the 3B, with **no measured quality justification** for the cost (A-008) |
| Waiting on A-01 before deciding model strategy | DEC-011 | 2026-08-03 | A-01 concerns the unlicensed `fgaim` models; `fgaim` publishes **no MT model**. Translation was answerable the whole time |

| Decomposing services by domain | DEC-013 | 2026-08-03 | Ignores the measured ~150x resource spread — the thing that actually determines deployment cost |
| One container serving all capabilities | DEC-013 | 2026-08-03 | 1.6 GB resident just to normalise a string; multi-second cold start on microsecond operations |
| Keeping all tiers warm | DEC-013 | 2026-08-03 | Pays idle cost for 1.4 GB continuously at low volume (A-008) |
| Scaling all tiers to zero | DEC-013 | 2026-08-03 | Multi-second cold start on tokenization, which should take microseconds |
| Service-first, extract libraries later | DEC-012 | 2026-08-03 | Imposes infrastructure on the developer users DEC-002 names as primary; and the extraction never happens once services exist |
| Services-only (no libraries) | DEC-012 | 2026-08-03 | Makes the primitives unusable without infrastructure — fails the users who most need them |
| `llama-cpp-python` as the model runtime | DEC-014 | 2026-08-03 | Serves MADLAD GGUF but not the Roberta encoder — two runtimes where one suffices (P-7) |
| `transformers` as the serving runtime | DEC-014 | 2026-08-03 | Heaviest option with no native int8 CPU path; poorest fit for A-008 |

| Leaving DEC-008 screening as written policy | DEC-015 | 2026-08-03 | Measured outcome: three ad-hoc reimplementations, zero files in scripts/data_processing, enforced by nobody |
| Auto-detecting dataset licences | DEC-015 | 2026-08-03 | A licence is a legal fact about a dataset, not a property of its bytes |
| Passing contamination when no eval set is supplied | DEC-015 | 2026-08-03 | Silence would read as clearance — the exact failure DEC-008 exists to prevent |
| An automated column-scramble verdict | DEC-015 | 2026-08-03 | Not reliably separable from unusual prose; a false verdict is worse than a review flag |
| A training-centred ML pipeline | DEC-015 | 2026-08-03 | We decided not to train (A-004, A-005, DEC-003); it would invest where there is no work and under-invest in screening and evaluation |
| Prose-only experiment results | DEC-016 | 2026-08-03 | Measured: makes drift undetectable and P-5 unverifiable — the actual state of Experiment 001 |
| A full experiment-tracking system | DEC-016 | 2026-08-03 | Far too heavy for three experiments; would be abandoned, per DEC-001's reasoning |

| Training a Tigrinya MT model from scratch | DEC-017 | 2026-08-03 | A-002's ~40M-token ceiling is the entire open corpus; our lawful share is a fraction. Not a resource question — not possible |
| Fine-tuning on the 1.4M unlicensed en–ti pairs | DEC-017 | 2026-08-03 | Unlicensed (P-9, A-009); shipping the result would pass on rights we do not hold |
| Fine-tuning on FLORES+ or TiQuAD | DEC-017 | 2026-08-03 | They are our evaluation anchors — training on them is contamination (DEC-008) and destroys our only measurement |
| Full fine-tune as the default adaptation method | DEC-017 | 2026-08-03 | 23x LoRA's memory for no measured benefit; fails A-008 |
| Training because output "looks bad" | DEC-017 | 2026-08-03 | A-004 puts the burden of proof on the proposer — no training without a measured deficit against a pre-committed threshold |

| Relying on review discipline to enforce decision-log rules | DEC-018 | 2026-08-03 | Already measured to fail — DEC-008 was policy with no mechanism for three months and silently ignored |
| Automating enforcement of judgement calls | DEC-018 | 2026-08-03 | Not mechanically checkable; would produce false failures until someone disabled the workflow |
| Fixing Tier 2 as scale-to-zero now | DEC-019 | 2026-08-03 | Break-even may be ~1 req/min at slow cold start, where scale-to-zero is both slower and dearer. Unmeasured |
| Fixing Tier 2 as always-warm now | DEC-019 | 2026-08-03 | Wastes 1,162.9 GB-h/month at genuinely low volume (A-008) |
| Costing infrastructure in dollar figures | DEC-019 | 2026-08-03 | Vendor pricing unverifiable from this environment and volatile; GB-hours and break-even rates survive price changes |
| Kubernetes or a comparable orchestration layer | DEC-019 | 2026-08-03 | Three tiers, one runtime, low volume — a continuous expense buying nothing (P-7) |
| GPU infrastructure | DEC-019 | 2026-08-03 | DEC-014's runtime is CPU int8, and DEC-017's training is blocked on data rather than hardware |

| A single project-wide licence | DEC-020 | 2026-08-03 | Data derivatives carry share-alike obligations code does not; one licence either over-restricts code or under-honours upstream data terms |
| GPL / AGPL for source code | DEC-020 | 2026-08-03 | Nothing upstream requires it, and it would restrict the application developers DEC-002 names as primary users |
| MIT for source code | DEC-020 | 2026-08-03 | Apache-2.0's explicit patent grant matters more for infrastructure others build on; the surrounding ecosystem already uses it |
| Deferring the licence choice further | DEC-020 | 2026-08-03 | Deferred pending A-01/A-05/A-06, but the code licence turns out to depend on none of them |
| Proposing a revenue model | DEC-020 | 2026-08-03 | N-9 forecloses a commercial service for now; inventing one would contradict a recorded non-goal |
| Treating funding as the main sustainability risk | DEC-020 | 2026-08-03 | Measured cost is 52.6 GB-h/month for the always-warm tier — the scarce resource is maintainer attention, not money |

| Building translation next because it is the cleared capability | DEC-021 | 2026-08-03 | Follows P-4 literally but abandons DEC-006's reasoning; the primitives gap is our differentiator and translation has a strong incumbent |
| Revisiting DEC-006 to make translation the MVP | DEC-021 | 2026-08-03 | The gap-filling argument still holds, and 05_architecture independently confirmed the MVP is also the cheap tier — 191 MB against 1,593 MB |
| Building MVP primitives without evaluation | DEC-021 | 2026-08-03 | Violates P-4 directly — unmeasurable capabilities cannot be improved or defended, and failures could not be localised |
| Treating the anchor/MVP mismatch as a sequencing accident | DEC-021 | 2026-08-03 | It is structural: DEC-005's anchors do not cover DEC-006's platform and never would have |

| Deferring all of 07_api_mcp to A-02 | DEC-022 | 2026-08-03 | A-02 blocks the surface, not the contract — and the contract is the part that is expensive to change once consumers exist |
| UTF-8 byte offsets | DEC-022 | 2026-08-03 | Natural in Python, wrong for every JS client; 3–4 bytes per Ge'ez character also makes them unreadable when debugging |
| UTF-16 code-unit offsets | DEC-022 | 2026-08-03 | Natural in JS, wrong in Python, and inherits the surrogate-pair split precisely at Ethiopic Extended-B |
| Leaving the offset unit implicit | DEC-022 | 2026-08-03 | The divergence is silent and appears only on rare characters — the worst failure profile available |
| Uniform latency expectations across endpoints | DEC-022 | 2026-08-03 | A 150x spread; one client timeout either aborts valid translations or hangs on a tokenize call |
| `null` for unknown Tigrinya variety | DEC-022 | 2026-08-03 | Invites clients to ignore the distinction DEC-010 exists to preserve; `unknown` is the common case, not an absence |
| Describing the analysis form as phonemes | DEC-022 | 2026-08-03 | Measurably false for 19 real characters and for three entire Ethiopic blocks |

| Building a Tigrinya primitives benchmark before evaluating anything | DEC-023 | 2026-08-03 | Months of work (A-006) when three of four intrinsic properties are measurable today with no annotation |
| Character-level surface<->analysis offsets | DEC-023 | 2026-08-03 | Measurably impossible — 23.89% of words align; epitran resolves epenthetic vowels from cross-character context supplying 16.3% of output |
| Accepting a tradeoff between alignment and phonology | DEC-023 | 2026-08-03 | A false dilemma I proposed and then refuted by measurement — word-level gives exact alignment AND full fidelity (1,639/1,639 preserved in context) |
| Treating intrinsic properties as sufficient evaluation | DEC-023 | 2026-08-03 | They catch broken, not wrong; a deterministically incorrect transliterator passes every one of them |
| Skipping evaluation and building the primitives directly | DEC-023 | 2026-08-03 | Violates P-4 — and H3 is precisely the class of error that surfaces only when you check |

<!--
Add rejected options above this line. Every decision in DECISIONS.md should
contribute at least one row — a decision with no rejected alternatives usually
means the alternatives were not actually explored.
-->
