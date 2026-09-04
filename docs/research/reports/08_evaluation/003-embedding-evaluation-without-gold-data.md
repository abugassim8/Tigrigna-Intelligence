# Evaluating Tigrinya Embeddings When No Similarity Benchmark Exists

| Field | Value |
| --- | --- |
| **Report ID** | `003-embedding-evaluation-without-gold-data` |
| **Domain** | `08_evaluation` |
| **Stage** | Scout → Analyst → Architect |
| **Date** | 2026-08-23 |
| **Status** | Accepted |
| **Summary** | `docs/research/summaries/016-embedding-evaluation.md` |
| **Related decisions** | **DEC-026**; extends DEC-023's method to Tier 1; corrects the READINESS_PLAN dependency graph |
| **Experiment** | `experiments/008-embedding-baseline/` |

---

## Objective

**Embeddings are the second capability in DEC-006's MVP with no evaluation
path.** DEC-023 solved this for three of four primitives by evaluating them
intrinsically, and explicitly excluded embeddings: *"Untested: embeddings.
Tier 1, and `tiroberta-bi-encoder` is monolingual, so FLORES+ bitext retrieval
does not directly apply."*

Under **P-4** — evaluation before capability — Tier 1 cannot be built until this
is answered. **No Tigrinya semantic-similarity benchmark exists**, and building
one is what **A-006** anticipated costing months.

**This report asks the DEC-023 question again for embeddings: what is measurable
without annotation?**

---

## Finding 1 — ⚠️ The blocker is egress, not licensing. The plan says otherwise

`READINESS_PLAN.md`'s dependency graph reads `A-01 → Tier 1 embeddings`, and
`ACTIONS.md` lists A-01 as blocking "the embeddings service".

**`fgaim/tiroberta-bi-encoder` is Apache-2.0.** So is `tielectra-bi-encoder`.
A-01's own text says so in parentheses: *"Already clean: `tiroberta-bi-encoder`
and `tielectra-bi-encoder` are Apache-2.0."*

| Model | Licence | Blocked by |
| --- | --- | --- |
| **`tiroberta-bi-encoder`** (124.6M) | **Apache-2.0** ✅ | **A-09 only** — we cannot fetch the weights |
| `tielectra-bi-encoder` | **Apache-2.0** ✅ | A-09 only |
| `tiroberta-base`, `tielectra-small`, `tiroberta-pos`, … | NOT STATED ⚠️ | **A-01** |

**A-01 blocks the wider reuse plan; it does not block Tier 1.** The correction
matters because it changes which single action unlocks embeddings — and because
a dependency graph that overstates a blocker makes the wrong thing look urgent.

## Finding 2 — The obvious method is unavailable, and one goal is unreachable

**Bitext retrieval is how multilingual sentence encoders are normally
evaluated**: embed 1,012 English FLORES+ sentences and 1,012 Tigrinya ones,
retrieve across, report accuracy@1. It needs no similarity annotations, which is
exactly why it is attractive here.

**It requires one shared vector space.** `tiroberta-bi-encoder` is a
Tigrinya-only RoBERTa; embedding English with it produces vectors from a model
that never learned English, and the resulting "accuracy" would measure
tokenizer collisions rather than meaning.

Two consequences, and the second is larger than an evaluation problem:

1. **FLORES+ parallel data cannot evaluate this model**, despite being the best
   aligned data we have.
2. **G-4 — cross-language retrieval — is not reachable with this model at all.**
   Not "unevaluated": unreachable. Serving it would require a *different model
   class* (a multilingual encoder such as LaBSE or a multilingual E5), which is
   a Tier 1 scope decision nobody has taken. Recorded here so it is not
   discovered during implementation.

## Finding 3 — Six properties are measurable with no annotation

The DEC-023 insight transfers: **most of what makes an embedding model usable is
a property of the function, not agreement with a human.**

| # | Property | Question | Catches |
| --- | --- | --- | --- |
| **E1** | **Orthographic invariance** | Does normalising ጸ/ፀ move the vector? | An encoder that treats normal Tigrinya spelling variation as different words |
| **E2** | Self-retrieval | Does a sentence retrieve itself at rank 1? | Broken pooling, a mis-wired index |
| **E3** | Discrimination | Is a sentence closer to its own corruption than to a different sentence? | An encoder producing near-constant vectors |
| **E4** | Corruption monotonicity | Does similarity fall as corruption rises? | Insensitivity to content |
| **E5** | Word-order sensitivity | Is a shuffled sentence less similar than the original? | Bag-of-words behaviour |
| **E6** | Length independence | Does similarity track length rather than content? | A model where long sentences are all mutually similar |

**E1 is the Tigrinya-specific one and it is not decorative.** Mixing the two
tsade series and both alef forms is **normal practice, not error** — measured
across Eritrean newspapers at 1.0–3.8%. An encoder whose tokenizer treats ጸ and
ፀ as unrelated types will place the same sentence in two different places, and
**retrieval will silently fail for whichever spelling the user did not choose**.
That is a production failure with no visible symptom.

**E1 also has measurable headroom.** On a character n-gram baseline over
FLORES+ Tigrinya, cos(original, normalised) is **0.9282–0.9655**, not 1.0. The
test discriminates rather than saturating, which is what makes it useful.

## Finding 4 — A lexical baseline is the honest floor

`tiroberta-bi-encoder` is **124.6M parameters** and would roughly **double Tier
1's footprint** over Tier 0. **P-6** optimises for low volume and **P-7** prefers
boring technology, so the question is not "does it work?" but **"does it beat
something free?"**

A character n-gram TF-IDF encoder is that floor: **no model weights, no GPU,
pure arithmetic**, and it handles Ge'ez morphology better than word-level
lexical matching because subword n-grams survive affixation.

`experiments/008-embedding-baseline/` implements it and measures the six
properties, so **when A-09 lands there is already a number to beat**. If the
neural model does not beat a 40-line lexical baseline on these properties, the
119 MB is not earning its place — and that is a decision worth having the
evidence for *before* building the tier, not after.

## Finding 5 — What still needs a human, and the bridge to it

**Intrinsic properties cannot tell us whether two *different* sentences are
similar.** That is what an embedding model is actually for, and it needs either a
Tigrinya STS set (does not exist) or a speaker.

**The bridge already exists.** `validation/` holds an instrument built for A-13
with five sheets. A sixth — sentence pairs rated 0–4 for relatedness — turns the
same reviewer session into a **minimal Tigrinya STS set**. Twenty pairs would
not be a benchmark, but Spearman correlation against twenty human ratings is a
real signal where currently there is none, and it costs a reviewer five extra
minutes.

**This is deliberately not built yet.** A-13 has not been sent, and adding items
before the first sheet returns risks the whole instrument going unanswered. The
design is recorded so it is ready when A-13 comes back.

## Limits of this report

- **Nothing here has been run against `tiroberta-bi-encoder`.** The weights are
  behind the egress policy (**A-09**). Every property is designed and
  implemented; only the lexical baseline has been measured.
- **The six properties are necessary, not sufficient** — the same caveat DEC-023
  carries. A model that is invariant, discriminating and order-sensitive can
  still embed *wrongly*. E1 through E6 catch **broken**, not **wrong**.
- **The baseline floor is one corpus of 30 sentences.** It establishes the
  method and a provisional number, not a robust threshold.
- **E6's length independence is the weakest of the six.** Length and content
  correlate in real text, so a model can fail it for defensible reasons; it is
  reported rather than gated.

---

## Decisions arising

- **DEC-026** — embedding evaluation is intrinsic-first with a mandatory lexical
  baseline; cross-lingual retrieval requires a different model class.

**Evidence:** `experiments/008-embedding-baseline/` `[verified]` 2026-08-23;
licence status from `docs/research/references/models.md` `[verified]`.
