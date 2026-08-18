"""Ge'ez → phoneme transliteration with word-level alignment.

Wraps epitran's `tir-Ethi` map (DEC-007, amended) and produces the word-level
spans the DEC-022 contract requires.

Why word-level, and why that is exact rather than a compromise
--------------------------------------------------------------
DEC-007 originally asked for offsets between surface and analysis forms without
specifying a granularity, and DEC-022 made those offsets an API contract clause.
Both assumed character-level alignment. Measurement refuted it:

  - transliterating a word whole equals concatenating its per-character
    transliterations for only **23.89%** of words
  - because Ge'ez 6th-order characters are ambiguous between "consonant + ɨ" and
    a bare consonant, and epitran resolves that from surrounding characters
  - context supplies **16.3%** of all output symbols (1,375 of 8,430)

So character offsets cannot be derived by summing per-character output lengths.
But epenthesis resolves *within* a word and nothing crosses word boundaries:

  - a word's transliteration is preserved inside a sentence: **1,639/1,639**
  - prepending a character changes **0 of 1,635** tokens

Transliterating word by word therefore gives full phonological fidelity *and*
exact alignment, because the analysis form simply *is* the concatenation.

What this does not give you
---------------------------
The analysis form is **not guaranteed phonemic**. 19 real Ethiopic characters
(16 syllables, 3 combining marks) pass through untransliterated, and the
Supplement, Extended-A and Extended-B blocks are entirely unmapped. Consumers
must not assume IPA — `Analysis.analysis_is_phonemic` says so explicitly.
"""

from __future__ import annotations

import functools
import re

from .types import Analysis, OffsetUnit, Span, Variety

_WS = re.compile(r"(\s+)")

#: Ethiopic blocks epitran's tir-Ethi map does not cover at all.
_UNMAPPED_BLOCKS = (
    (0x1380, 0x139F, "Ethiopic Supplement"),
    (0x2D80, 0x2DDF, "Ethiopic Extended"),
    (0xAB00, 0xAB2F, "Ethiopic Extended-A"),
    (0x1E7E0, 0x1E7FF, "Ethiopic Extended-B"),
)


@functools.lru_cache(maxsize=1)
def _epi():
    """Load epitran lazily.

    Tier 0 is meant to stay small and warm (DEC-013), and importing this module
    should not pay a model-load cost until transliteration is actually used.
    """
    import epitran

    return epitran.Epitran("tir-Ethi")


@functools.lru_cache(maxsize=100_000)
def transliterate_word(word: str) -> str:
    """Transliterate a single word. Deterministic; safe to cache.

    Caching is sound precisely because of the measurement above: a word's
    transliteration does not depend on its neighbours.
    """
    if not word:
        return ""
    return _epi().transliterate(word)


def _unmapped_warnings(text: str) -> list[str]:
    seen = set()
    for ch in text:
        cp = ord(ch)
        for lo, hi, name in _UNMAPPED_BLOCKS:
            if lo <= cp <= hi and name not in seen:
                seen.add(name)
                break
    return [
        f"text contains {name} characters, which the transliterator does not "
        f"map; they appear unchanged in the analysis form"
        for name in sorted(seen)
    ]


def transliterate(text: str, variety: Variety = Variety.UNKNOWN) -> Analysis:
    """Transliterate `text`, returning surface form, analysis form and spans.

    The surface form is preserved verbatim and is never reconstructed from the
    analysis form (DEC-007). Spans are word-level and exact: each span's
    analysis is the transliteration of exactly that word.
    """
    if not text:
        return Analysis(surface="", analysis="", variety=variety)

    spans: list[Span] = []
    analysis_parts: list[str] = []
    cursor = 0

    # Split keeping whitespace, so offsets track the original string exactly.
    for chunk in _WS.split(text):
        if not chunk:
            continue
        if chunk.isspace():
            analysis_parts.append(chunk)
        else:
            out = transliterate_word(chunk)
            analysis_parts.append(out)
            spans.append(
                Span(start=cursor, end=cursor + len(chunk),
                     surface=chunk, analysis=out)
            )
        cursor += len(chunk)

    result = Analysis(
        surface=text,
        analysis="".join(analysis_parts),
        spans=tuple(spans),
        variety=variety,
        offset_unit=OffsetUnit.CODEPOINT,
        analysis_is_phonemic=False,
        warnings=tuple(_unmapped_warnings(text)),
    )
    # Cheap, and turns a misalignment into an immediate failure.
    result.verify_offsets()
    return result
