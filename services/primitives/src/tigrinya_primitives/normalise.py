"""Ge'ez orthographic normalisation.

Collapses the orthographic variants that Tigrinya writers use interchangeably,
so that matching and retrieval are not defeated by spelling choice.

Two measured facts shape this module:

  - Ge'ez is normalisation-stable under Unicode NFC/NFD: 0 of 384 core Ethiopic
    characters change. Offsets therefore do not shift, and this module does not
    need to pin a Unicode normalisation form to stay aligned.
  - Orthographic variation is THIN. Naive tsade/alef normalisation collapses
    only 4 of 496 unique forms (0.8%) on real text. That is a useful guard
    against over-engineering: the problem is real but small.

Mixing the two tsade series and both alef forms is NORMAL Tigrinya practice, not
a defect — measured across sources, Eritrean newspapers mix at 1.0–3.8%. So this
is a matching aid, never a correction, and the surface form is always preserved.
"""

from __future__ import annotations

# Eritrean-standard targets. The Ethiopian-common series maps onto them; the
# direction is a convention for internal matching, not a judgement about which
# spelling is correct.
_TSADE = str.maketrans("ፀፁፂፃፄፅፆ", "ጸጹጺጻጼጽጾ")
_ALEF = str.maketrans("አ", "ኣ")

#: Characters this module will alter, for callers that want to explain a match.
NORMALISED_CHARS = frozenset("ፀፁፂፃፄፅፆአ")


def normalise(text: str) -> str:
    """Return `text` with Ge'ez orthographic variants collapsed.

    Idempotent: `normalise(normalise(x)) == normalise(x)`, verified as a
    property test over corpus text. Length-preserving, so offsets computed on
    the input remain valid on the output — every substitution is 1:1.
    """
    return text.translate(_TSADE).translate(_ALEF)


def is_normalised(text: str) -> bool:
    """True if `text` contains no character this module would change."""
    return not (NORMALISED_CHARS & set(text))


def normalisation_diff(text: str) -> list[tuple[int, str, str]]:
    """Return `(index, original, normalised)` for each altered character.

    Exists so a caller can explain *why* two strings matched, rather than
    presenting a normalised form as though it were what the user wrote.
    """
    out = []
    for i, ch in enumerate(text):
        n = normalise(ch)
        if n != ch:
            out.append((i, ch, n))
    return out
