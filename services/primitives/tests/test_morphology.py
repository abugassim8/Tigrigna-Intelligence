"""Morphology adapter tests — run with HornMorpho absent, which is the point.

HornMorpho is GPL-3.0 and this package is Apache-2.0, so it cannot be a test
dependency (**DEC-028**). Every test here injects a fake analyser instead. That
is not a compromise: the part of this module that has to be *correct* is span
construction, offset alignment and failure reporting, and none of that is
HornMorpho's behaviour. The one thing a live install would settle — the shape
of an individual analysis — is called out as unverified in the module docstring
and tested here only for **how it degrades**, not for what it produces.
"""

from __future__ import annotations

import pytest

from tigrinya_primitives import morphology
from tigrinya_primitives.types import Analysis, Variety

# A word -> analyses fake in the documented "list of dicts" shape.
FAKE = {
    "ሰላም": [{"seg": "ሰላም", "pos": "N"}],
    "ዓለም": [{"seg": "ዓለም", "pos": "N"}],
    "ንዓኻትኩም": [{"seg": "ን-ዓኻትኩም", "pos": "PRON"}],
}


def fake_analyser(word: str):
    return FAKE.get(word, [{"seg": word, "pos": "UNK"}])


# ------------------------------------------------------------- availability

#: These assert the **absent** path, so they cannot run on a machine that has
#: HornMorpho — which is exactly the machine we want this suite to keep working
#: on. Until 2026-09-07 they asserted absence unconditionally, which made them
#: assertions about *the environment* rather than about the code, and they
#: failed the moment someone followed the install instructions. Gated now, with
#: `needs_present` mirroring each one on the other side.
needs_absent = pytest.mark.skipif(
    morphology.is_available(),
    reason="HornMorpho is installed; the absent-path tests do not apply")

needs_present = pytest.mark.skipif(
    not morphology.is_available(),
    reason="HornMorpho is not installed; the present-path tests do not apply")


@needs_absent
def test_unavailable_without_hornmorpho():
    """The honest default in most environments: HornMorpho is not installed."""
    assert morphology.is_available() is False


@needs_absent
def test_analyse_without_hornmorpho_explains_how_to_install():
    with pytest.raises(NotImplementedError) as excinfo:
        morphology.analyse("ሰላም")
    message = str(excinfo.value)
    assert "GPL-3.0" in message
    assert "hltdi/HornMorpho" in message
    # The separate language download is the failure people actually hit.
    assert "download" in message


@needs_present
def test_analyse_without_an_injected_analyser_uses_hornmorpho():
    """The other side of the gate: installed means it actually analyses.

    Nothing asserted this before 2026-09-07, because nothing could — no
    environment in the project's history had HornMorpho importable.
    """
    result = morphology.analyse("ሰላም")
    assert result.spans and result.spans[0].surface == "ሰላም"
    assert result.spans[0].analysis
    result.verify_offsets()


@needs_present
def test_warmup_is_not_a_noop_when_present():
    morphology.warmup()
    assert morphology.is_available() is True


def test_warmup_is_a_noop_when_absent():
    """Warming an optional dependency nobody installed is not an error."""
    morphology.warmup()


def test_is_available_requires_language_data_not_just_the_import(monkeypatch):
    """`import hm` succeeding must not be read as "Tigrinya works".

    This is the upstream trap: a fresh install has no language packs, and
    `hm.analyze` then returns None for every word rather than raising.
    """
    class FakeLanguages:
        CODES = {"ti": "t"}

        @staticmethod
        def is_downloaded(abbrev):
            return False

    fake_hm = type("hm", (), {})()
    monkeypatch.setattr(morphology, "_import_hm", lambda: fake_hm)
    monkeypatch.setitem(
        __import__("sys").modules, "hm.morpho",
        type("m", (), {"languages": FakeLanguages})(),
    )
    monkeypatch.setitem(
        __import__("sys").modules, "hm",
        type("m", (), {"morpho": __import__("sys").modules["hm.morpho"]})(),
    )
    assert morphology.is_available() is False


# ------------------------------------------------------------------- spans

def test_spans_index_back_into_the_surface():
    """DEC-022's contract: offsets must actually address the surface form."""
    text = "ሰላም ዓለም"
    result = morphology.analyse(text, analyser=fake_analyser)
    assert isinstance(result, Analysis)
    result.verify_offsets()          # raises on misalignment
    assert [s.surface for s in result.spans] == ["ሰላም", "ዓለም"]
    assert result.surface == text    # verbatim, never reconstructed


def test_analysis_is_the_concatenation_of_its_spans():
    """What makes word-level alignment exact by construction (DEC-023)."""
    text = "ሰላም ዓለም"
    result = morphology.analyse(text, analyser=fake_analyser)
    rebuilt = ""
    cursor = 0
    for span in result.spans:
        rebuilt += text[cursor:span.start] + span.analysis
        cursor = span.end
    rebuilt += text[cursor:]
    assert rebuilt == result.analysis


def test_whitespace_is_preserved_exactly():
    """Irregular whitespace is where offset bugs hide."""
    text = "  ሰላም\t\tዓለም  \n"
    result = morphology.analyse(text, analyser=fake_analyser)
    result.verify_offsets()
    for span in result.spans:
        assert text[span.start:span.end] == span.surface


def test_segmentation_reaches_the_analysis():
    result = morphology.analyse("ንዓኻትኩም", analyser=fake_analyser)
    assert result.spans[0].analysis == "ን-ዓኻትኩም"


def test_empty_text():
    result = morphology.analyse("", analyser=fake_analyser)
    assert result.surface == "" and result.spans == ()


def test_contract_fields():
    """Morphology must declare the same contract clauses as transliteration."""
    result = morphology.analyse("ሰላም", variety=Variety.ERITREAN,
                                analyser=fake_analyser)
    assert result.variety is Variety.ERITREAN
    assert result.tier == 0
    # Segmentation is not a phonemic transcription, and DEC-022 requires this
    # to be declared rather than left to the caller to assume.
    assert result.analysis_is_phonemic is False
    assert result.to_dict() == __import__("json").loads(
        __import__("json").dumps(result.to_dict())
    )


# --------------------------------------------------------- failure handling

def test_none_from_the_analyser_is_a_broken_install_not_an_empty_result():
    """The upstream trap, asserted.

    `hm.analyze()` returns None when the language cannot be loaded. Mapping
    that to "no analysis" would report a missing language pack as an
    unanalysable corpus — quietly, for every word.
    """
    with pytest.raises(NotImplementedError) as excinfo:
        morphology.analyse("ሰላም", analyser=lambda word: None)
    assert "download" in str(excinfo.value)


def test_unrecognised_shape_degrades_to_surface_and_warns():
    """We do not invent an analysis from an object we do not understand."""
    class Mystery:
        def __init__(self):
            self.unexpected = "value"

    result = morphology.analyse("ሰላም", analyser=lambda word: [Mystery()])
    assert result.spans[0].analysis == "ሰላም"      # surface, unchanged
    assert result.warnings, "an unrecognised shape must be reported"
    assert "unverified" in result.warnings[0]
    result.verify_offsets()


def test_warning_is_not_repeated_per_word():
    result = morphology.analyse("ሰላም ዓለም ሰላም",
                                analyser=lambda word: [object()])
    assert len(result.warnings) == 1


def test_word_object_shape_is_accepted():
    """The other half of upstream's contradictory docstrings."""
    class Word:
        seg = "ን-ዓኻትኩም"

    result = morphology.analyse("ንዓኻትኩም", analyser=lambda word: Word())
    assert result.spans[0].analysis == "ን-ዓኻትኩም"
    assert not result.warnings


def test_empty_analyses_fall_back_to_surface_without_warning():
    """An analyser that genuinely found nothing is not a shape problem."""
    result = morphology.analyse("ሰላም", analyser=lambda word: [])
    assert result.spans[0].analysis == "ሰላም"
    assert not result.warnings


def test_multiple_analyses_are_all_reported():
    """Ambiguity is normal in Ge'ez morphology; it must not be silently cut."""
    result = morphology.analyse(
        "ሰላም", analyser=lambda word: [{"seg": "ሰላም", "pos": "N"},
                                      {"seg": "ሰ-ላም", "pos": "V"}])
    assert result.spans[0].analysis == "ሰላም|ሰ-ላም"


# ------------------------------------- the shape a live install actually returns

def test_an_analysis_without_segmentation_is_braced_not_bare():
    """The defect a live HornMorpho run exposed on 2026-09-07.

    HornMorpho returns a function-word reading with ``seg=None`` *alongside* a
    segmented one. ``ኣብ`` really yields these two. Rendering both bare gave
    ``ADP|-<ኣብ>--``, where slot 0 is a part-of-speech tag and slot 1 a
    segmentation and nothing says so. Every fixture in this file supplies
    ``seg``, so the fallback branch never ran until real data reached it.
    """
    result = morphology.analyse("ኣብ", analyser=lambda word: [
        {"seg": None, "pos": "ADP", "root": None, "lemma": None},
        {"seg": "-<ኣብ>--", "pos": "N", "root": "ኣብ", "lemma": "ኣብ"},
    ])
    assert result.spans[0].analysis == "{ADP}|-<ኣብ>--"
    assert not result.warnings


def test_a_lexeme_is_not_a_segmentation_either():
    """`lemma` and `root` name a lexeme; they are braced for the same reason."""
    result = morphology.analyse(
        "ሰላም", analyser=lambda word: [{"seg": None, "lemma": "ሰላም"}])
    assert result.spans[0].analysis == "{ሰላም}"


def test_segmentation_still_wins_over_a_tag():
    """Braces are the fallback, never a wrapper around a segmented analysis."""
    result = morphology.analyse(
        "ሰላም", analyser=lambda word: [{"seg": "ሰ-ላም", "pos": "V"}])
    assert result.spans[0].analysis == "ሰ-ላም"


def test_braces_cannot_collide_with_upstreams_segmentation_grammar():
    """HornMorpho's `seg` uses `-`, `<` and `>` only — verified 5.3.6."""
    for observed in ("-<ኣብ>--", "---<-ተ-ማሂር-ኦም->-", "--ኣይ-<ይ--ከድ-ኡ->ን-"):
        assert "{" not in observed and "}" not in observed


def test_word_object_attributes_also_fall_back_to_a_braced_tag():
    """The `Word`-shaped path must brace exactly as the dict path does."""
    class Reading:
        seg = None
        pos = "ADP"

    result = morphology.analyse("ኣብ", analyser=lambda word: Reading())
    assert result.spans[0].analysis == "{ADP}"
