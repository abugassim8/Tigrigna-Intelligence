"""Variety-scoped evaluation harness (DEC-010).

Every result carries a Tigrinya variety label, and **scores from different
varieties are never aggregated**. That is not a stylistic preference: our two
DEC-005 anchors appear to be in different varieties.

  - **TiQuAD** is `[verified]` Eritrean-sourced.
  - **FLORES+ Tigrinya** carries Ethiopian markers — `እስካብ`, `ብሄራዊ`, `እንትኸውን`,
    with zero Eritrean counterparts — at an ET-marker rate of **15.1%** against
    **1.0–3.8%** for unambiguously Eritrean sources.

So an aggregate "Tigrinya score" across both would describe a language nobody
speaks. `UNKNOWN` is a first-class label, not an absence: most Tigrinya
resources do not state their variety, and guessing defeats the purpose.

The attribution above is a strong signal, not a ruling — it needs native-speaker
confirmation (**A-13**). The harness is correct either way, which is why it does
not wait on that.
"""

from __future__ import annotations

import json
import pathlib
from dataclasses import dataclass, field

from .metrics import TranslationScores, score


class CrossVarietyAggregationError(RuntimeError):
    """Raised when someone tries to combine scores across varieties.

    An exception rather than a warning. DEC-010 exists because the aggregate is
    *meaningless*, and a warning would be ignored exactly when it mattered.
    """


@dataclass(frozen=True)
class EvalSet:
    """An evaluation set, with the provenance a score needs to be readable."""

    name: str
    variety: str            # "eritrean" | "ethiopian" | "unknown"
    references: list[str]
    source: str = ""
    licence: str = ""

    def __post_init__(self) -> None:
        if self.variety not in ("eritrean", "ethiopian", "unknown"):
            raise ValueError(
                f"variety must be eritrean/ethiopian/unknown, got {self.variety!r} "
                "— DEC-010 requires an explicit label, and `unknown` is a "
                "first-class value rather than a null"
            )


@dataclass(frozen=True)
class SystemResult:
    """One system's score on one evaluation set."""

    system: str
    eval_set: str
    variety: str
    scores: TranslationScores
    #: Whether this system may be shipped, or is comparison-only. NLLB is
    #: CC-BY-NC-4.0, so it can be measured but never deployed (DEC-011).
    shippable: bool = True
    notes: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict:
        return {
            "system": self.system,
            "eval_set": self.eval_set,
            "variety": self.variety,
            "shippable": self.shippable,
            "chrf": self.scores.chrf.score,
            "chrf_ci": [self.scores.chrf.ci_low, self.scores.chrf.ci_high],
            "bleu": self.scores.bleu.score,
            "bleu_ci": [self.scores.bleu.ci_low, self.scores.bleu.ci_high],
            "sentences": self.scores.sentences,
            "sacrebleu_version": self.scores.sacrebleu_version,
            "chrf_signature": self.scores.chrf.signature,
            "bleu_signature": self.scores.bleu.signature,
            "notes": list(self.notes),
        }


class Harness:
    """Runs systems against evaluation sets, keeping varieties apart."""

    def __init__(self) -> None:
        self._results: list[SystemResult] = []

    def evaluate(self, system: str, hypotheses: list[str], eval_set: EvalSet,
                 shippable: bool = True,
                 notes: tuple[str, ...] = ()) -> SystemResult:
        """Score one system on one evaluation set."""
        r = SystemResult(
            system=system,
            eval_set=eval_set.name,
            variety=eval_set.variety,
            scores=score(hypotheses, eval_set.references),
            shippable=shippable,
            notes=notes,
        )
        self._results.append(r)
        return r

    # --------------------------------------------------------------- reading

    @property
    def results(self) -> list[SystemResult]:
        return list(self._results)

    def by_variety(self) -> dict[str, list[SystemResult]]:
        """Results grouped by variety — the only legitimate grouping."""
        out: dict[str, list[SystemResult]] = {}
        for r in self._results:
            out.setdefault(r.variety, []).append(r)
        return out

    def aggregate(self) -> None:
        """Refuses. There is no such thing as a single Tigrinya score.

        Present so the attempt fails loudly with the reason attached, rather
        than someone quietly averaging the results themselves.
        """
        varieties = {r.variety for r in self._results}
        raise CrossVarietyAggregationError(
            f"Refusing to aggregate across {sorted(varieties)} (DEC-010). "
            "Our evaluation anchors appear to be in different Tigrinya "
            "varieties, so a combined score would describe a language nobody "
            "speaks. Use by_variety() and report each separately."
        )

    def report(self) -> str:
        """A human-readable report that carries its own caveats."""
        if not self._results:
            return "No results."
        lines = ["Tigrinya translation evaluation", "=" * 62]
        for variety, rs in sorted(self.by_variety().items()):
            lines.append(f"\nVariety: {variety}")
            lines.append("-" * 62)
            for r in sorted(rs, key=lambda x: -x.scores.chrf.score):
                flag = "" if r.shippable else "   [COMPARISON ONLY — not shippable]"
                lines.append(f"  {r.system:<28} {r.scores.summary()}{flag}")
                for n in r.notes:
                    lines.append(f"      note: {n}")
        lines += [
            "\n" + "=" * 62,
            "chrF is primary (DEC-009). BLEU is shown for comparability with",
            "published work and must not be read alone.",
            "",
            TranslationScores.cross_language_warning(),
            "",
            "Scores are NOT aggregated across varieties (DEC-010).",
        ]
        return "\n".join(lines)

    def save(self, path: str | pathlib.Path) -> None:
        pathlib.Path(path).write_text(
            json.dumps({"results": [r.to_dict() for r in self._results]},
                       ensure_ascii=False, indent=2)
        )
