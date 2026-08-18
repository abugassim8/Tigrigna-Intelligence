"""Morphological analysis — BLOCKED, interface only.

This module deliberately contains no implementation.

Why
---
Morphology is part of Tier 0 (DEC-013) and on the DEC-006 critical path, and
**HornMorpho is the only established Tigrinya morphological analyser**. Three
things about it are unresolved, tracked as **A-07** in `ACTIONS.md`:

  1. **Licence — unknown.** Under P-9 and A-009 an unstated licence is
     disqualifying. Adopting it anyway would pass a restriction to downstream
     users that they inherit without knowing it — the same failure this project
     rejected NLLB for (DEC-011).
  2. **Tigrinya version status.** The documentation says Version 5 replaces 4.5
     *for Amharic*, and directs other languages to Version 4.3. Whether v5
     covers Tigrinya properly is unclear.
  3. **Maintenance.** Not on PyPI; GitHub-only, hand-built.

Shipping a stub is the honest option. Implementing against an unlicensed
dependency, or quietly substituting a weaker approach, would both misrepresent
what the platform can do.

What is already known about evaluating it
-----------------------------------------
Experiment 004 established that most Tier 0 primitives can be evaluated by
intrinsic properties with no gold data. **Morphology is the exception** — its
accuracy genuinely needs annotation, which A-006 anticipated. Its *intrinsic*
properties (consistency, coverage) could not even be measured, because the tool
is unavailable.

Unblocking
----------
Resolve **A-07**. If HornMorpho proves unusable, the fallback options are a
rule-based analyser built on the existing normalisation and transliteration
primitives, or an unsupervised approach — which Experiment 001's research noted
performs poorly on Tigrinya relative to rule-based methods.
"""

from __future__ import annotations

from .types import Analysis

BLOCKER = "A-07"

_MESSAGE = (
    "Morphological analysis is not implemented. The only established Tigrinya "
    "analyser (HornMorpho) has an unresolved licence, unclear Tigrinya version "
    "support, and no PyPI distribution — tracked as A-07 in ACTIONS.md. "
    "Adopting an unlicensed dependency would violate P-9/A-009, so this is "
    "blocked deliberately rather than incomplete by accident."
)


def analyse(text: str) -> Analysis:  # noqa: ARG001 - interface placeholder
    """Not implemented — see module docstring and A-07."""
    raise NotImplementedError(_MESSAGE)


def is_available() -> bool:
    """False. Lets callers degrade gracefully instead of catching an exception.

    Tier 0 is usable without morphology: normalisation, tokenization and
    transliteration all work. Callers should check this rather than assume the
    whole tier is unavailable.
    """
    return False
