"""Tigrinya language primitives — Tier 0 of the platform.

Normalisation, tokenization, and transliteration for Ge'ez-script Tigrinya.
Pure computation over small data: **113.4 MB measured**, no model weights, no
GPU. (DEC-013 estimated 72 MB before this was built; `epitran`'s `panphon`
dependency is 107.4 MB of the total. The measured figure is the one to quote.)

This is a **library first** (DEC-012). Services wrap it; no capability logic
lives only behind a network call, and the primitives are usable with no
infrastructure at all.

    >>> from tigrinya_primitives import normalise, transliterate
    >>> normalise("ፀሓይ")
    'ጸሓይ'
    >>> a = transliterate("ሰላም ዓለም")
    >>> a.surface          # verbatim, always
    'ሰላም ዓለም'
    >>> [s.surface for s in a.spans]
    ['ሰላም', 'ዓለም']

**Morphology is implemented but its dependency is never bundled** (DEC-028).
HornMorpho is GPL-3.0 and this package is Apache-2.0, so the user installs it;
`morphology.is_available()` is False until they do, and callers degrade
gracefully rather than crashing. See `morphology.py`.

Decisions realised here: DEC-006 (Tier 0 is the MVP), DEC-007 amended
(raw-Ge'ez tokenization; word-level alignment), DEC-010 (variety labels),
DEC-012 (library-first), DEC-013 (resource tiering), DEC-022 (response
contract), DEC-023 (intrinsic evaluation, word-level spans).
"""

from .types import Analysis, OffsetUnit, Span, Variety
from .normalise import NORMALISED_CHARS, is_normalised, normalisation_diff, normalise
from .transliterate import transliterate, transliterate_word, warmup
from .tokenize import DEFAULT_VOCAB_SIZE, Fertility, GeezTokenizer
from . import morphology

__version__ = "0.1.0"

__all__ = [
    "Analysis", "OffsetUnit", "Span", "Variety",
    "normalise", "is_normalised", "normalisation_diff", "NORMALISED_CHARS",
    "transliterate", "transliterate_word", "warmup",
    "GeezTokenizer", "Fertility", "DEFAULT_VOCAB_SIZE",
    "morphology",
]
