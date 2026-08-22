"""Translation metrics, pinned and constrained by DEC-009.

chrF is primary; BLEU is reported for comparability with published work and is
**never reported alone**. Both choices were measured rather than assumed
(Experiment 003, on FLORES+ parallel data where the same 30 sentences exist in
English and Tigrinya, so language is the only variable):

  - BLEU is **~1.08× harsher** on Tigrinya than English at an identical error
    rate. Real, consistent, and about **half** the size the standard warning
    about morphologically rich languages implies.
  - chrF's advantage over BLEU **widens as quality falls** — retention ratio
    1.18× → 1.46× → 1.80× at 10/20/30% corruption. Low-resource MT lives in the
    low-quality regime, so the metric is chosen for how it behaves when systems
    are weak, not when they are strong.

The BLEU penalty is an **upper** estimate: the perturbation used to measure it
was itself ~1.44× harsher on Tigrinya by construction, because a Ge'ez character
is a consonant+vowel pair while a Latin letter is one phoneme.
"""

from __future__ import annotations

from dataclasses import dataclass

import sacrebleu
from sacrebleu.metrics import BLEU, CHRF

#: Pinned. Metric implementations differ, sometimes substantially, and DEC-009
#: requires the version to travel with any reported number.
SACREBLEU_VERSION = sacrebleu.__version__

#: The measured harshness of BLEU on Tigrinya relative to English. Any
#: cross-language BLEU comparison must state this (DEC-009).
BLEU_TIGRINYA_PENALTY = 1.08

_CROSS_LANGUAGE_WARNING = (
    "BLEU is ~1.08x harsher on Tigrinya than English at an identical error "
    "rate (measured, Experiment 003). Comparing this BLEU score to another "
    "language's without stating that penalty is a documented error, not a "
    "judgement call."
)


@dataclass(frozen=True)
class MetricScore:
    """One metric's score, with the spread that makes it interpretable."""

    name: str
    score: float
    #: 95% bootstrap confidence interval, when computed. Evaluation sets here
    #: are ~1,000 sentences or fewer, and DEC-009 requires spread on small sets
    #: because a bare mean hides everything interesting.
    ci_low: float | None = None
    ci_high: float | None = None
    signature: str = ""

    def __str__(self) -> str:
        s = f"{self.name} {self.score:.2f}"
        if self.ci_low is not None:
            s += f" [{self.ci_low:.2f}, {self.ci_high:.2f}]"
        return s


@dataclass(frozen=True)
class TranslationScores:
    """chrF and BLEU together. There is no way to obtain one without the other.

    This is deliberate. DEC-009 forbids reporting BLEU alone, and the cheapest
    way to enforce that is to make the alternative unrepresentable.
    """

    chrf: MetricScore
    bleu: MetricScore
    sentences: int
    sacrebleu_version: str = SACREBLEU_VERSION

    @property
    def primary(self) -> MetricScore:
        """The score to lead with (DEC-009)."""
        return self.chrf

    def summary(self) -> str:
        return (
            f"chrF {self.chrf.score:.2f}"
            + (f" [{self.chrf.ci_low:.2f}, {self.chrf.ci_high:.2f}]"
               if self.chrf.ci_low is not None else "")
            + f"  |  BLEU {self.bleu.score:.2f}"
            + (f" [{self.bleu.ci_low:.2f}, {self.bleu.ci_high:.2f}]"
               if self.bleu.ci_low is not None else "")
            + f"  (n={self.sentences}, sacrebleu {self.sacrebleu_version})"
        )

    @staticmethod
    def cross_language_warning() -> str:
        """The caveat that must accompany any cross-language BLEU comparison."""
        return _CROSS_LANGUAGE_WARNING


def score(hypotheses: list[str], references: list[str],
          confidence_interval: bool = True) -> TranslationScores:
    """Score `hypotheses` against `references` with chrF and BLEU together.

    `confidence_interval` uses sacrebleu's bootstrap resampling. It is on by
    default because our evaluation sets are small enough that a point estimate
    alone is misleading — FLORES+ devtest is 1,012 sentences, and we have often
    had far fewer.
    """
    if len(hypotheses) != len(references):
        raise ValueError(
            f"{len(hypotheses)} hypotheses vs {len(references)} references — "
            "these must be aligned"
        )
    if not hypotheses:
        raise ValueError("nothing to score")

    chrf_m = CHRF()
    bleu_m = BLEU()

    if confidence_interval and len(hypotheses) > 1:
        # paired_bs computes the interval sacrebleu itself recommends for
        # small sets; falls back cleanly if the backend declines.
        try:
            chrf_r = chrf_m.corpus_score(hypotheses, [references],
                                         n_bootstrap=1000)
            bleu_r = bleu_m.corpus_score(hypotheses, [references],
                                         n_bootstrap=1000)
            return TranslationScores(
                chrf=_to_score("chrF", chrf_r, chrf_m),
                bleu=_to_score("BLEU", bleu_r, bleu_m),
                sentences=len(hypotheses),
            )
        except (TypeError, ValueError):
            pass

    chrf_r = chrf_m.corpus_score(hypotheses, [references])
    bleu_r = bleu_m.corpus_score(hypotheses, [references])
    return TranslationScores(
        chrf=_to_score("chrF", chrf_r, chrf_m),
        bleu=_to_score("BLEU", bleu_r, bleu_m),
        sentences=len(hypotheses),
    )


def _to_score(name, result, metric) -> MetricScore:
    lo = hi = None
    # sacrebleu exposes the interval as _ci when bootstrapping was requested,
    # and sets it to **-1 as a sentinel** when it was not.
    #
    # `if ci:` is true for -1, so the sentinel used to be treated as a real
    # half-width: score - (-1) became the LOWER bound and score + (-1) the
    # upper, producing an inverted interval like [60.33, 58.33] around a score
    # of 59.33. Every caller that declined bootstrapping — and the fallback
    # path below, which declines it on any backend error — got that instead of
    # `None`. Found by an audit test asserting ci_low <= score <= ci_high.
    ci = getattr(result, "_ci", None)
    if ci is not None and ci > 0:
        lo, hi = result.score - ci, result.score + ci
    # sacrebleu returns numpy float32. Coerce to builtin float: the harness
    # persists results as JSON, and float32 is not serialisable — caught by
    # test_results_serialise_to_json, which would otherwise have surfaced the
    # first time anyone tried to save a real evaluation run.
    return MetricScore(
        name=name,
        score=float(result.score),
        ci_low=float(lo) if lo is not None else None,
        ci_high=float(hi) if hi is not None else None,
        signature=str(metric.get_signature()),
    )
