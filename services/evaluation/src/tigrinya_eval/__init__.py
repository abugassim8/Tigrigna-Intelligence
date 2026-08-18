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
"""

from .metrics import (
    BLEU_TIGRINYA_PENALTY, SACREBLEU_VERSION,
    MetricScore, TranslationScores, score,
)
from .harness import (
    CrossVarietyAggregationError, EvalSet, Harness, SystemResult,
)

__version__ = "0.1.0"

__all__ = [
    "score", "MetricScore", "TranslationScores",
    "Harness", "EvalSet", "SystemResult", "CrossVarietyAggregationError",
    "BLEU_TIGRINYA_PENALTY", "SACREBLEU_VERSION",
]
