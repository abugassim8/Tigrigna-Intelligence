"""Response types implementing the DEC-022 API contract.

Every clause here traces to a decision. The contract exists because these
choices are expensive to change once consumers depend on them, and because
three of them were arrived at by measurement rather than convention:

  - offsets are WORD-LEVEL spans, not character offsets (DEC-023). Character
    alignment is measurably impossible: only 23.89% of words align, because
    Ge'ez 6th-order characters are ambiguous between "consonant + ɨ" and a bare
    consonant, and epitran resolves that from surrounding characters.
  - the analysis form is NOT guaranteed phonemic (DEC-022). 19 real Ethiopic
    characters pass through untransliterated, and three whole blocks are
    unmapped.
  - variety is mandatory and `unknown` is a first-class value, never null
    (DEC-010). Most Tigrinya resources do not state their variety, and a null
    invites callers to ignore the distinction.
  - the serving tier is disclosed (DEC-013, DEC-022), because the tiers differ
    by ~150x in memory and far more in latency, and a client cannot set a
    sensible timeout without knowing which one answered.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field, asdict
from typing import Any


class Variety(str, enum.Enum):
    """Tigrinya variety (DEC-004, DEC-010).

    `UNKNOWN` is the expected common case, not an error. Scores and analyses
    from different varieties are never aggregated.
    """

    ERITREAN = "eritrean"
    ETHIOPIAN = "ethiopian"
    UNKNOWN = "unknown"


class OffsetUnit(str, enum.Enum):
    """The unit `Span` offsets are expressed in.

    Stated explicitly in every response rather than assumed. Ethiopic
    Extended-B (U+1E7E0–U+1E7FF) lies above the BMP, so a UTF-16 client
    (JavaScript `.length`) and a code-point client (Python `len`) disagree about
    the same string — silently, and only on characters unlikely to reach a test
    fixture. Code points are the unit where neither is wrong by default.
    """

    CODEPOINT = "codepoint"


@dataclass(frozen=True)
class Span:
    """A word-level span linking surface text to its analysis.

    Word-level rather than character-level is exact by construction: the
    analysis form simply *is* the concatenation of its spans' analyses.

    ⚠️ **Corrected 2026-08-18 (experiment 005).** This docstring previously
    claimed per-word analysis was also *fully faithful* — that a word's
    transliteration is preserved inside a sentence "1,639/1,639 times". That
    figure came from a containment test that could not detect an appended
    character. By exact equality it is **95.47%**: the rest gain a word-final
    `ɨ` in running text. Word-by-word is chosen because the in-context form is
    **not a function of local context** (a distant edit changes it), so only the
    per-word form is stable enough to put in a contract — not because the two
    agree.
    """

    start: int
    end: int
    surface: str
    analysis: str

    def __post_init__(self) -> None:
        if self.start < 0 or self.end < self.start:
            raise ValueError(f"invalid span [{self.start}, {self.end})")
        if len(self.surface) != self.end - self.start:
            raise ValueError(
                f"span width {self.end - self.start} does not match surface "
                f"length {len(self.surface)} — offsets would be wrong"
            )


@dataclass(frozen=True)
class Analysis:
    """The result of analysing Tigrinya text.

    `surface` is returned verbatim and is the source of truth for anything shown
    to a user. It is never reconstructed from `analysis` (DEC-007).
    """

    surface: str
    analysis: str
    spans: tuple[Span, ...] = ()
    variety: Variety = Variety.UNKNOWN
    offset_unit: OffsetUnit = OffsetUnit.CODEPOINT
    #: False whenever the analysis form may contain non-phonemic characters,
    #: which with the current transliterator is always. Declared rather than
    #: implied, so a consumer expecting IPA cannot be silently wrong.
    analysis_is_phonemic: bool = False
    #: Which resource tier served this (DEC-013, DEC-022). Primitives are
    #: Tier 0; embeddings Tier 1; translation Tier 2.
    #:
    #: In the contract because the tiers differ by ~150x in memory and far more
    #: in time: `transliterate` is 0.04 ms warm, while Tier 2 is seconds plus a
    #: possible cold start. Presenting them uniformly is a lie the client pays
    #: for — one timeout either aborts valid translations or hangs on a
    #: tokenize call. DEC-022 named this clause and it went unimplemented until
    #: an audit compared the decision against the payload.
    tier: int = 0
    warnings: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        """The wire form. Every value here is a JSON primitive, list or dict.

        `warnings` is converted to a list for the same reason `spans` is:
        `asdict` preserves tuples, so the payload was **not equal to its own
        JSON round-trip** — `spans` normalised to a list and `warnings` did
        not. Harmless in transit, but it means a consumer comparing a response
        to re-parsed JSON gets inequality on a field that never changed. Found
        by the DEC-022 conformance suite.
        """
        d = asdict(self)
        d["variety"] = self.variety.value
        d["offset_unit"] = self.offset_unit.value
        d["spans"] = [asdict(s) for s in self.spans]
        d["warnings"] = list(self.warnings)
        return d

    def verify_offsets(self) -> None:
        """Check every span actually indexes back into the surface form.

        Cheap, and it turns the class of bug this contract exists to prevent
        into an immediate failure rather than a silent misalignment downstream.
        """
        for s in self.spans:
            actual = self.surface[s.start:s.end]
            if actual != s.surface:
                raise ValueError(
                    f"span [{s.start},{s.end}) claims {s.surface!r} but surface "
                    f"holds {actual!r}"
                )
