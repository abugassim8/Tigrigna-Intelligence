"""Intrinsic evaluation for sentence embeddings (DEC-026).

Why this module exists
----------------------
**Embeddings were the second capability in DEC-006's MVP with no evaluation
path.** DEC-023 solved this for three of four primitives by measuring intrinsic
properties, and explicitly excluded embeddings: `tiroberta-bi-encoder` is
monolingual, so the standard method — FLORES+ bitext retrieval — measures
tokenizer collisions rather than meaning when you feed it English.

So the DEC-023 question gets asked again: **what is measurable without
annotation?** Six properties, and none needs a similarity judgement.

The Tigrinya-specific one
-------------------------
**E1, orthographic invariance, is the property that matters here and would not
appear in a generic embedding test suite.** Mixing the two tsade series (ጸ/ፀ)
and both alef forms (ኣ/አ) is **normal Tigrinya practice, not error** — measured
across Eritrean newspapers at 1.0–3.8%. An encoder whose tokenizer treats ጸ and
ፀ as unrelated types places the same sentence in two different regions, and
**retrieval silently fails for whichever spelling the user did not type.** No
error surfaces; results are merely worse for half the population.

Works with anything
-------------------
`Embedder` is a two-method protocol, so this evaluates a neural model, the
lexical baseline below, or anything else, on identical terms. That matters
because **the baseline is the point**: `tiroberta-bi-encoder` is 124.6M
parameters and would roughly double Tier 1's footprint, so under **P-6** and
**P-7** the question is not "does it work?" but "does it beat something free?"

⚠️ **These checks catch *broken*, not *wrong*** — the same limit DEC-023 carries.
A model that is invariant, discriminating and order-sensitive can still embed
incorrectly. Real similarity needs a speaker (see `validation/`).
"""

from __future__ import annotations

import math
import random
from collections import Counter
from dataclasses import dataclass
from typing import Iterable, Protocol, Sequence

from tigrinya_primitives import normalise

#: Pre-committed thresholds. Provisional: only the lexical baseline has been
#: measured, so these are floors chosen to catch a broken encoder, not targets
#: derived from a model that earned them.
#: E1 is word-level. A correct (normalising) encoder scores 1.0000 and the
#: character n-gram baseline 0.2232, so this floor is set where a model has
#: to actually treat the variants as one word. **The baseline fails it** —
#: that is the finding, not a miscalibration.
INVARIANCE_FLOOR = 0.80
SELF_RETRIEVAL_FLOOR = 1.00   # E2 — anything below this is a wiring bug
DISCRIMINATION_FLOOR = 0.95   # E3
MONOTONICITY_FLOOR = 1.00     # E4 — a rank property, so it holds or it does not
ORDER_SENSITIVITY_FLOOR = 0.0  # E5 — advisory; baseline measures 0.2246

_CAVEAT = (
    "INTRINSIC EMBEDDING CHECKS CATCH *BROKEN*, NOT *WRONG*. A model can pass "
    "all six and still place unrelated sentences together. Whether two "
    "different sentences are actually similar needs a Tigrinya speaker or an "
    "STS set, and neither exists yet (A-006, A-13)."
)


class Embedder(Protocol):
    """Anything that turns text into a vector and compares two of them.

    Deliberately minimal so a neural model and a 40-line lexical baseline are
    evaluated on identical terms.
    """

    def embed(self, text: str): ...
    def similarity(self, a, b) -> float: ...


# --------------------------------------------------------------- the baseline

class CharNgramEmbedder:
    """Character n-gram TF-IDF. The floor a neural model has to beat.

    Character n-grams rather than words because **Ge'ez morphology defeats
    word-level lexical matching**: ሃገር, ሃገራዊ and ሃገርነት are one root and three
    types, and subword n-grams survive affixation where whole words do not.

    No weights, no GPU, no download. If `tiroberta-bi-encoder` cannot beat this
    on the six properties, its 119 MB is not earning its place — and that is
    worth knowing before Tier 1 is built rather than after.
    """

    def __init__(self, sizes: tuple[int, ...] = (3, 4, 5)) -> None:
        self.sizes = sizes
        self._idf: dict[str, float] = {}

    def _grams(self, text: str) -> list[str]:
        # Pad so word boundaries are themselves features.
        s = f" {text} "
        return [s[i:i + n] for n in self.sizes for i in range(len(s) - n + 1)]

    def fit(self, corpus: Sequence[str]) -> "CharNgramEmbedder":
        df = Counter()
        for s in corpus:
            df.update(set(self._grams(s)))
        n = len(corpus)
        self._idf = {g: math.log((n + 1) / (c + 1)) + 1 for g, c in df.items()}
        return self

    def embed(self, text: str) -> dict[str, float]:
        if not self._idf:
            raise ValueError("call fit() on a corpus before embedding")
        tf = Counter(self._grams(text))
        v = {g: (1 + math.log(c)) * self._idf[g]
             for g, c in tf.items() if g in self._idf}
        norm = math.sqrt(sum(x * x for x in v.values())) or 1.0
        return {g: x / norm for g, x in v.items()}

    @staticmethod
    def similarity(a: dict[str, float], b: dict[str, float]) -> float:
        # Iterate the smaller side; both vectors are already unit-normalised.
        small, big = (a, b) if len(a) < len(b) else (b, a)
        return sum(x * big.get(g, 0.0) for g, x in small.items())


# ------------------------------------------------------------------- results

@dataclass(frozen=True)
class PropertyResult:
    name: str
    value: float
    floor: float
    detail: str = ""
    #: True when the number is reported for information rather than gated —
    #: a floor invented before any model was measured is not a threshold.
    advisory: bool = False

    @property
    def holds(self) -> bool:
        return self.advisory or self.value >= self.floor

    def __str__(self) -> str:
        mark = "INFO" if self.advisory else ("PASS" if self.holds else "FAIL")
        return (f"{mark}  {self.name:32s} {self.value:7.4f}"
                f"  (floor {self.floor:.2f})" + (f"  {self.detail}" if self.detail else ""))


@dataclass(frozen=True)
class EmbeddingReport:
    results: tuple[PropertyResult, ...]
    sentences: int
    model: str

    @property
    def holds(self) -> bool:
        return all(r.holds for r in self.results)

    def report(self) -> str:
        lines = [f"Embedding intrinsic evaluation — {self.model}",
                 f"  {self.sentences} sentences", ""]
        lines += [f"  {r}" for r in self.results]
        lines += ["", f"  VERDICT: {'PASS' if self.holds else 'FAIL'}", "", "  " + _CAVEAT]
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "model": self.model, "sentences": self.sentences, "holds": self.holds,
            "caveat": _CAVEAT,
            "results": [{"name": r.name, "value": round(r.value, 6),
                         "floor": r.floor, "holds": r.holds,
                         "advisory": r.advisory, "detail": r.detail}
                        for r in self.results],
        }

    @staticmethod
    def caveat() -> str:
        return _CAVEAT


# -------------------------------------------------------------------- checks

def _corrupt(s: str, rate: float, rng: random.Random) -> str:
    """The inflectional near-miss used throughout this project's experiments."""
    ws = s.split()
    k = int(len(ws) * rate)
    for i in (rng.sample(range(len(ws)), k) if k and ws else []):
        if len(ws[i]) >= 2:
            ws[i] = ws[i][:-1] + "ን"
    return " ".join(ws)


def check_orthographic_invariance(model: Embedder,
                                  sentences: Sequence[str]) -> PropertyResult:
    """E1 — does normalising ጸ/ፀ and ኣ/አ move the vector?

    Measured **per word, not per sentence**, and the reason is a defect the
    first version of this check actually had. At sentence level one substituted
    character sits among hundreds of features, so similarity stays high whatever
    the model does: a deliberately spelling-blind control scored **identically**
    to the correct one (0.9282 both). **The check could not fail.**

    At word level it separates cleanly — an embedder that normalises before
    encoding scores **1.0000**, the character n-gram baseline **0.2232** — so
    that is what is measured.

    The failure this catches is invisible in production: retrieval degrades only
    for users who chose the other spelling, and nothing errors.
    """
    words = sorted({w for s in sentences for w in s.split() if normalise(w) != w})
    if not words:
        return PropertyResult("E1 orthographic invariance", 1.0, INVARIANCE_FLOOR,
                              "no affected words in this corpus", advisory=True)
    sims = [model.similarity(model.embed(w), model.embed(normalise(w))) for w in words]
    mean = sum(sims) / len(sims)
    return PropertyResult("E1 orthographic invariance", mean, INVARIANCE_FLOOR,
                          f"mean over {len(words)} affected words "
                          f"(min {min(sims):.3f})")


def check_self_retrieval(model: Embedder, sentences: Sequence[str]) -> PropertyResult:
    """E2 — does a sentence retrieve itself at rank 1? A wiring sanity floor."""
    vecs = [model.embed(s) for s in sentences]
    hits = sum(1 for i, v in enumerate(vecs)
               if max(range(len(vecs)), key=lambda j: model.similarity(v, vecs[j])) == i)
    return PropertyResult("E2 self-retrieval @1", hits / len(vecs),
                          SELF_RETRIEVAL_FLOOR, f"{hits}/{len(vecs)}")


def check_discrimination(model: Embedder, sentences: Sequence[str],
                         seed: int = 20260819) -> PropertyResult:
    """E3 — is a sentence closer to its own corruption than to a different one?

    The floor a near-constant encoder fails. Everything scoring alike is the
    classic symptom of broken pooling or an untrained head.
    """
    rng = random.Random(seed)
    ok = 0
    for i, s in enumerate(sentences):
        own = model.similarity(model.embed(s), model.embed(_corrupt(s, 0.2, rng)))
        other = sentences[(i + 1) % len(sentences)]
        cross = model.similarity(model.embed(s), model.embed(other))
        ok += own > cross
    return PropertyResult("E3 discrimination", ok / len(sentences),
                          DISCRIMINATION_FLOOR, f"{ok}/{len(sentences)}")


def check_corruption_monotonicity(model: Embedder, sentences: Sequence[str],
                                  seed: int = 20260819) -> PropertyResult:
    """E4 — does similarity fall as corruption rises?

    A rank property, so it holds or it does not; the mean similarity at each
    level is reported so a near-miss is diagnosable.
    """
    levels = (0.0, 0.1, 0.2, 0.4)
    means = []
    for rate in levels:
        rng = random.Random(seed)
        sims = [model.similarity(model.embed(s), model.embed(_corrupt(s, rate, rng)))
                for s in sentences]
        means.append(sum(sims) / len(sims))
    monotonic = all(a > b for a, b in zip(means, means[1:]))
    return PropertyResult("E4 corruption monotonicity", 1.0 if monotonic else 0.0,
                          MONOTONICITY_FLOOR,
                          " > ".join(f"{m:.3f}" for m in means))


def check_order_sensitivity(model: Embedder, sentences: Sequence[str],
                            seed: int = 20260819) -> PropertyResult:
    """E5 — is a word-shuffled sentence less similar than the original?

    ⚠️ **Advisory, not gated**, and the reason is worth stating because the
    obvious expectation is wrong. Character n-grams look order-blind, so this
    "should" score 0 — **measured, the baseline scores 0.2246.** Padded n-grams
    span word boundaries, so shuffling destroys some of them; the model is
    *partially* order-sensitive without representing order at all.

    That makes this a comparison rather than a pass/fail: **a neural model
    scoring below ~0.22 has learned less about word order than accidental
    character overlap provides**, which would be a genuinely bad sign.
    """
    rng = random.Random(seed)
    drops = []
    for s in sentences:
        ws = s.split()
        if len(ws) < 4:
            continue
        shuffled = ws[:]
        rng.shuffle(shuffled)
        v = model.embed(s)
        drops.append(1.0 - model.similarity(v, model.embed(" ".join(shuffled))))
    value = sum(drops) / len(drops) if drops else 0.0
    return PropertyResult("E5 order sensitivity", value, ORDER_SENSITIVITY_FLOOR,
                          f"mean similarity drop over {len(drops)} sentences",
                          advisory=True)


def check_length_independence(model: Embedder,
                              sentences: Sequence[str]) -> PropertyResult:
    """E6 — does similarity track length rather than content?

    ⚠️ **Advisory.** Length and content correlate in real text, so a model can
    fail this for defensible reasons. Reported, never gated.
    """
    pairs = [(i, j) for i in range(len(sentences)) for j in range(i + 1, len(sentences))]
    if len(pairs) < 3:
        return PropertyResult("E6 length independence", 0.0, 0.0,
                              "too few pairs", advisory=True)
    vecs = [model.embed(s) for s in sentences]
    sims = [model.similarity(vecs[i], vecs[j]) for i, j in pairs]
    ldiff = [abs(len(sentences[i]) - len(sentences[j])) for i, j in pairs]
    r = _spearman(sims, ldiff)
    return PropertyResult("E6 length independence", 1.0 - abs(r), 0.0,
                          f"Spearman(similarity, length gap) = {r:+.3f}",
                          advisory=True)


def _spearman(a: Sequence[float], b: Sequence[float]) -> float:
    """Rank correlation, without pulling in scipy for one function."""
    def ranks(xs):
        order = sorted(range(len(xs)), key=lambda i: xs[i])
        r = [0.0] * len(xs)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
                j += 1
            avg = (i + j) / 2 + 1
            for k in range(i, j + 1):
                r[order[k]] = avg
            i = j + 1
        return r
    ra, rb = ranks(a), ranks(b)
    n = len(a)
    ma, mb = sum(ra) / n, sum(rb) / n
    num = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    den = math.sqrt(sum((x - ma) ** 2 for x in ra) * sum((y - mb) ** 2 for y in rb))
    return num / den if den else 0.0


def evaluate_embeddings(model: Embedder, sentences: Sequence[str],
                        name: str = "unnamed") -> EmbeddingReport:
    """Run all six intrinsic properties (DEC-026)."""
    sentences = [s for s in sentences if s and s.strip()]
    if len(sentences) < 5:
        raise ValueError("need at least 5 sentences to evaluate embeddings")
    return EmbeddingReport(
        results=(
            check_orthographic_invariance(model, sentences),
            check_self_retrieval(model, sentences),
            check_discrimination(model, sentences),
            check_corruption_monotonicity(model, sentences),
            check_order_sensitivity(model, sentences),
            check_length_independence(model, sentences),
        ),
        sentences=len(sentences),
        model=name,
    )
