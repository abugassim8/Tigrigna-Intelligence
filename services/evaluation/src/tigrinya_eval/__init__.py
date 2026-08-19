"""Tigrinya evaluation harness — DEC-009, DEC-010, DEC-011.

Scores translation systems with **chrF primary and BLEU alongside**, keeps
**varieties strictly separate**, and refuses to produce a single aggregate
"Tigrinya score".

    >>> from tigrinya_eval import EvalSet, Harness
    >>> flores = EvalSet(name="flores+_devtest", variety="unknown",
    ...                  references=refs, licence="CC-BY-SA-4.0")
    >>> h = Harness()
    >>> h.evaluate("madlad400-3b", madlad_out, flores)
    >>> h.evaluate("nllb-200-3.3B", nllb_out, flores, shippable=False)
    >>> print(h.report())

Two things this enforces that are easy to get wrong:

  - **BLEU is unobtainable alone.** `score()` always returns both, because
    DEC-009 forbids reporting BLEU by itself and the cheapest enforcement is to
    make the alternative unrepresentable.
  - **`aggregate()` raises.** Our two DEC-005 anchors appear to be in different
    varieties, so a combined score would describe a language nobody speaks.

`shippable=False` marks a system that may be measured but never deployed —
every NLLB variant is CC-BY-NC-4.0 (DEC-011), and it is the comparison baseline
the published Tigrinya literature uses.

Primitives are evaluated separately and differently
---------------------------------------------------
chrF and BLEU measure **translation** — the one capability DEC-006 excludes from
the MVP. Scoring only that would reproduce the exact gap DEC-021 was raised to
close, so `tigrinya_eval.primitives` evaluates Tier 0 **intrinsically** per
DEC-023(a), with no annotated data:

    >>> from tigrinya_eval.primitives import evaluate_primitives, load_corpus
    >>> print(evaluate_primitives(load_corpus(["corpus/"])).report())

Importing it requires `tigrinya-primitives` (the `primitives` extra).
"""

from .metrics import (
    BLEU_TIGRINYA_PENALTY, SACREBLEU_VERSION,
    MetricScore, TranslationScores, score,
)
from .harness import (
    CrossVarietyAggregationError, EvalSet, Harness, SystemResult,
)

__version__ = "0.1.0"

#: `primitives` is deliberately NOT imported here. It depends on
#: `tigrinya-primitives`, and translation scoring must stay usable without
#: pulling in epitran's 107 MB of `panphon` data (DEC-013).
__all__ = [
    "score", "MetricScore", "TranslationScores",
    "Harness", "EvalSet", "SystemResult", "CrossVarietyAggregationError",
    "BLEU_TIGRINYA_PENALTY", "SACREBLEU_VERSION",
]
