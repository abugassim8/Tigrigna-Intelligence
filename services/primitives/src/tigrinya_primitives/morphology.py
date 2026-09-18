"""Morphological analysis via HornMorpho — present if the user installed it.

This module is an **adapter, not a dependency**. `tigrinya-primitives` does not
require, vendor or ship HornMorpho, and must never do so: HornMorpho is
**GPL-3.0** and this platform is Apache-2.0 (**DEC-028**, **DEC-020
Amendment 1**). The user installs it themselves, which makes the combination
theirs rather than ours to distribute.

    You may:  install HornMorpho and get morphology; run it behind a service.
    We may not:  depend on it, vendor it, or ship it inside a container image.

That asymmetry is real and not a technicality. HornMorpho is **GPL-3.0, not
AGPL-3.0** — its §13 is *"Use with the GNU Affero General Public License"*, not
AGPL's *"Remote Network Interaction"* — so **network use is not distribution**.
A hosted API may call this; a wheel or an image may not contain it. CI enforces
the packaging half (`ci/verify.yml`).

Installing it
-------------
HornMorpho is **not on PyPI**, so there is no name pip can resolve — which is
also why it could never have been an extra::

    pip install git+https://github.com/hltdi/HornMorpho
    python -c "import hm; hm.download('t')"

The second line is not optional and is the failure this module works hardest to
report clearly: **language data is a separate download**, so `import hm`
succeeding tells you nothing about whether Tigrinya works.

Two upstream behaviours this adapter defends against
----------------------------------------------------
Both were found by reading HornMorpho 5.3.6's source, not by hitting them:

1. **`hm.analyze()` returns `None` when the language cannot be loaded.** Its
   body is ``language = morpho.get_language(...)`` then ``if language:``, with
   no ``else``. A missing Tigrinya pack therefore yields `None` rather than an
   exception — which, mapped naively, becomes "this word has no analysis" for
   every word in the corpus. We treat `None` as **unavailable** and raise.
2. **The documented return type looked ambiguous.** `hm.analyze`'s docstring
   says *"returning a list of dicts"*; the `Language.analyze` it delegates to
   says *"returning a Word object"*. ✅ **Settled 2026-09-07 by a live run:
   both are right.** `Word` subclasses `list`, so the object *is* a list of
   dicts. `_render` still accepts either and warns rather than assuming.

✅ What is verified here
------------------------
Verified 2026-09-02 by reading the upstream source at the pinned version:

  - licence **GPL-3.0** (`LICENSE.txt`), version **5.3.6**, not on PyPI;
  - the entry point is ``hm.analyze(language, word, **kwargs)`` (alias ``anal``);
  - Tigrinya's code is ``'ti'``, normalised to ``'t'`` by ``CODES``;
  - the `None`-on-load-failure path above.

**The shape of an individual analysis was the one open question**, and a live
install settled it on **2026-09-07**. An analysis is a dict with the keys::

    feats freq head lemma misc nsegs pos pre root seg stem suf token udfeats um

`_render` was checked against that output and **was wrong in a way no test
could have caught**: `pos` sat in the same fallback chain as `seg`, so a word
whose readings mixed segmented and unsegmented analyses rendered as
``ADP|-<ኣብ>--`` — slot 0 a part-of-speech tag, slot 1 a segmentation, nothing
distinguishing them. Every test fixture supplied `seg`, so the fallback branch
never ran until real data reached it. The two axes now use different
separators; see `_render`.

Still deliberately tolerant: an unrecognised shape degrades to the surface form
and attaches a warning naming the keys it actually saw, rather than emitting a
confident string built from a guess. Everything else — span construction,
offsets, degradation, error paths — is exercised by the test suite through an
injected analyser and does not depend on HornMorpho at all.

⚠️ **`import hm` requires `tkinter`** (`hm.morpho.corpus` does an unconditional
`from .gui import *`), so HornMorpho cannot be imported in a headless
environment without the platform Tk package installed. That is a property of
the dependency, not of any one machine — see
`docs/research/RESEARCH_ACCESS.md`.

Evaluation
----------
Experiment 004 found morphology is the one Tier 0 primitive whose **accuracy**
genuinely needs gold data (A-006). Its *intrinsic* properties — consistency
under normalisation, coverage — become measurable as soon as an analyser is
present, and `metrics.md`'s morphology row stays ❌ until something measures
them.
"""

from __future__ import annotations

import functools
import re
from typing import Any, Callable, Sequence

from .types import Analysis, OffsetUnit, Span, Variety

_WS = re.compile(r"(\s+)")

#: HornMorpho's code for Tigrinya — the **canonical** one, not the ISO-ish
#: alias, and the difference is not cosmetic.
#:
#: ⚠️ `hm/morpho/languages.py` keeps two mappings. `CODES` maps aliases onto
#: canonical codes ('ti' -> 't'); `ABBREV2LANG` holds only the canonical keys.
#: **`hm.analyze()` normalises through `CODES`; `hm.download()` does not** — it
#: tests raw membership (`hm/__init__.py:276`), so `hm.download('ti')` prints
#: "HornMorpho doesn't know of any language abbreviated ti" and downloads
#: nothing. Verified against 5.3.6: `'ti' in ABBREV2LANG` is False.
#:
#: 't' is the only form that works for **both** calls, which is why it is used
#: here and in every instruction this package prints. Reported as **A-20**.
LANGUAGE = "t"

#: Kept for callers that branched on it while this module was a stub.
BLOCKER = "A-07"

#: An analyser is any callable taking a word and returning HornMorpho's
#: analyses for it. Injecting one is how this module is tested without a
#: GPL-3.0 dependency present.
Analyser = Callable[[str], Any]

#: Fields that hold a **segmentation** — the morpheme analysis of the word.
#: Rendered bare.
_SEGMENTATION_KEYS = ("seg", "segmentation")

#: Fields that describe an analysis **without** segmenting it: a
#: part-of-speech tag, or a lexeme. Rendered braced, so a reader and a
#: determinism check can both tell them from a segmentation.
_TAG_KEYS = ("pos", "lemma", "root")

_NOT_INSTALLED = (
    "HornMorpho is not installed. It is GPL-3.0 and this package is "
    "Apache-2.0, so it is never bundled (DEC-028) — install it yourself:\n"
    "    pip install git+https://github.com/hltdi/HornMorpho\n"
    '    python -c "import hm; hm.download(\'t\')"\n'
    "Both lines are needed: the language data is a separate download."
)

_NO_LANGUAGE = (
    "HornMorpho is installed but could not load Tigrinya ('t'). The language "
    "data is downloaded separately:\n"
    "    python -c \"import hm; hm.download('t')\"\n"
    "Reported explicitly because hm.analyze() returns None in this case rather "
    "than raising, which would otherwise look like 'no analysis found'."
)


def _import_hm():
    """Import HornMorpho, or return None. Never raises."""
    try:
        import hm  # type: ignore[import-not-found]
    except Exception:                                    # noqa: BLE001
        return None
    return hm


def is_available() -> bool:
    """True only if HornMorpho is importable **and** Tigrinya data is present.

    Both halves matter. Checking only the import is the mistake this function
    exists to avoid: `import hm` succeeds on a fresh install with no language
    packs, and every analysis then silently comes back `None`.

    Deliberately cheap — it does not load the FST. `warmup()` does that.
    """
    hm = _import_hm()
    if hm is None:
        return False
    try:
        from hm.morpho import languages  # type: ignore[import-not-found]

        # LANGUAGE is already canonical, but map it anyway and try both, so
        # this keeps working if upstream renames the canonical code.
        canonical = getattr(languages, "CODES", {}).get(LANGUAGE, LANGUAGE)
        return bool(languages.is_downloaded(canonical)
                    or languages.is_downloaded(LANGUAGE))
    except Exception:                                    # noqa: BLE001
        # Internals moved. Fall back to "installed", and let analyse() report
        # the language failure precisely if it comes to that.
        return True


def warmup() -> None:
    """Load the analyser now so the first real request does not.

    Same contract as `transliterate.warmup()`, and the same reason: DEC-013
    keeps Tier 0 warm, and experiment 006 measured that lazy loading hands the
    entire cold start to whoever calls first. Idempotent.

    Does nothing if HornMorpho is absent — warming an optional dependency that
    was never installed is not an error.
    """
    if is_available():
        _analyser()


@functools.lru_cache(maxsize=1)
def _analyser() -> Analyser:
    """Bind HornMorpho's entry point, lazily.

    Lazy for the same reason epitran is: importing this module should not pay a
    model load.
    """
    hm = _import_hm()
    if hm is None:
        raise NotImplementedError(_NOT_INSTALLED)

    def analyse_word(word: str) -> Any:
        return hm.analyze(LANGUAGE, word)

    return analyse_word


def _render(entry: Any) -> tuple[str, str | None]:
    """Render one word's analyses to a string. Returns (text, warning).

    ✅ **Verified against HornMorpho 5.3.6 on 2026-09-07** — see the module
    docstring. `hm.analyze()` returns a `Word`, and `Word` subclasses `list`,
    so it *is* a list of dicts: upstream's two docstrings were each describing
    half of one object rather than contradicting each other.

    Two axes, two separators, because conflating them is the defect the first
    live run exposed:

    ``|`` separates **competing analyses** of the same word. Ambiguity is
    normal in Ge'ez morphology and must not be silently cut.

    ``{}`` marks an analysis that carries **no segmentation**. HornMorpho
    routinely returns a function-word reading with ``seg=None`` alongside a
    segmented one — ``ኣብ`` yields an ADP reading with no ``seg`` and a noun
    reading segmented ``-<ኣብ>--``. Rendering both bare produced ``ADP|-<ኣብ>--``,
    in which slot 0 is a part-of-speech tag and slot 1 a segmentation, with
    nothing to tell them apart. A lexeme (`lemma`, `root`) is not a
    segmentation either, and is braced for the same reason. Braces cannot
    collide with a segmentation: upstream's `seg` grammar uses ``-``, ``<``
    and ``>`` only.

    When nothing is recognisable this **says so and returns nothing** rather
    than inventing a string from `str(obj)` that would look like an analysis
    and not be one.
    """
    if entry is None:
        return "", None
    items: Sequence[Any] = entry if isinstance(entry, (list, tuple)) else [entry]
    if not items:
        return "", None

    rendered: list[str] = []
    unknown: set[str] = set()
    for item in items:
        if isinstance(item, str):
            rendered.append(item)
            continue
        if isinstance(item, dict):
            get = item.get
        else:
            # A `Word` element, or something else entirely.
            get = lambda key, _item=item: getattr(_item, key, None)

        for key in _SEGMENTATION_KEYS:
            value = get(key)
            if value:
                rendered.append(str(value))
                break
        else:
            for key in _TAG_KEYS:
                value = get(key)
                if value:
                    rendered.append("{" + str(value) + "}")
                    break
            else:
                if isinstance(item, dict):
                    unknown.update(str(k) for k in item)
                else:
                    unknown.add(type(item).__name__)

    if rendered:
        return "|".join(rendered), None
    return "", (
        "HornMorpho returned analyses in an unrecognised shape "
        f"({sorted(unknown)}); the surface form is returned unchanged. "
        "The expected shape was verified against HornMorpho 5.3.6 on "
        "2026-09-07, so this is a different analyser or a changed upstream — "
        "see tigrinya_primitives.morphology."
    )


def analyse(
    text: str,
    variety: Variety = Variety.UNKNOWN,
    *,
    analyser: Analyser | None = None,
) -> Analysis:
    """Analyse `text` morphologically, returning the DEC-022 contract shape.

    Word-level spans, exactly as `transliterate` produces them (DEC-023):
    character-level alignment is measurably impossible for Ge'ez, and the
    analysis form simply *is* the concatenation of its spans' analyses.

    `analyser` injects an alternative word analyser. It exists because
    HornMorpho is GPL-3.0 and cannot be a test dependency of an Apache-2.0
    package — every path below is exercised with a fake one.

    Raises `NotImplementedError` if HornMorpho is absent, with instructions.
    """
    if analyser is None:
        if not is_available():
            raise NotImplementedError(
                _NOT_INSTALLED if _import_hm() is None else _NO_LANGUAGE
            )
        analyser = _analyser()

    if not text:
        return Analysis(surface="", analysis="", variety=variety, tier=0)

    spans: list[Span] = []
    parts: list[str] = []
    warnings: list[str] = []
    cursor = 0

    for chunk in _WS.split(text):
        if not chunk:
            continue
        if chunk.isspace():
            parts.append(chunk)
            cursor += len(chunk)
            continue

        raw = analyser(chunk)
        if raw is None:
            # Not "no analysis" — hm.analyze() returns None when the language
            # failed to load, and mapping that to an empty result would report
            # a broken install as an unanalysable corpus.
            raise NotImplementedError(_NO_LANGUAGE)

        text_out, warning = _render(raw)
        if warning and warning not in warnings:
            warnings.append(warning)
        # An unrenderable analysis falls back to the surface form, so the
        # analysis string stays aligned with the text it describes.
        analysis = text_out or chunk

        parts.append(analysis)
        spans.append(Span(start=cursor, end=cursor + len(chunk),
                          surface=chunk, analysis=analysis))
        cursor += len(chunk)

    result = Analysis(
        surface=text,
        analysis="".join(parts),
        spans=tuple(spans),
        variety=variety,
        offset_unit=OffsetUnit.CODEPOINT,
        # Morphological segmentation is not a phonemic transcription, and
        # DEC-022 requires this to be declared rather than implied.
        analysis_is_phonemic=False,
        tier=0,
        warnings=tuple(warnings),
    )
    result.verify_offsets()
    return result
