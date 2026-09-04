"""Morphology intrinsic checks, exercised through injected analysers.

HornMorpho is GPL-3.0 and this package is Apache-2.0, so it is never a test
dependency (DEC-028). Every path below runs against a fake analyser — including
every *failure* path, which is the part that matters: a check nobody has watched
fail is a check nobody knows can fail.

Each broken analyser here is a specific defect the corresponding check exists to
catch, not a generic error.
"""

from __future__ import annotations

import pytest

from tigrinya_eval.morphology import (
    check_alignment,
    check_coverage,
    check_determinism,
    check_normalisation,
    check_surface,
    evaluate_morphology,
)
from tigrinya_eval.primitives import PropertyResult
from tigrinya_primitives import morphology

#: These two assert the *absent-analyser* behaviour, so they cannot run on a
#: machine that has HornMorpho — which is precisely the machine we want this
#: suite to keep working on. Gated rather than left to break for the one user
#: who followed the install instructions.
needs_absent = pytest.mark.skipif(
    morphology.is_available(),
    reason="HornMorpho is installed; the skip-path tests do not apply")

TEXTS = [
    "ሰላም ዓለም",
    "ፀሓይ ትወጽእ ኣላ",
    "ንሱ ናብ ቤት ትምህርቲ ከይዱ",
]


# ------------------------------------------------------------------ analysers

def good(word: str):
    """A well-behaved analyser: one deterministic dict per word."""
    return [{"seg": f"<{word}>"}]


def unanalysable(word: str):
    """Returns nothing renderable — `analyse` falls back to the surface form."""
    return []


def nondeterministic(word: str):
    """Different answer each call. Caught only by comparing two passes."""
    nondeterministic.n += 1
    return [{"seg": f"<{word}:{nondeterministic.n}>"}]


nondeterministic.n = 0


def variety_sensitive(word: str):
    """Analyses only the Eritrean tsade — the normalisation interaction."""
    return [] if "ፀ" in word else [{"seg": f"<{word}>"}]


# ------------------------------------------------------------------ the happy path

def test_surface_holds_with_a_working_analyser():
    r = check_surface(TEXTS, analyser=good)
    assert r.holds and r.passed == len(TEXTS)
    assert not r.skipped and not r.measurement_only


def test_alignment_holds_with_a_working_analyser():
    r = check_alignment(TEXTS, analyser=good)
    assert r.holds and r.passed == len(TEXTS)


def test_determinism_holds_with_a_working_analyser():
    words = sorted({w for t in TEXTS for w in t.split()})
    r = check_determinism(words, analyser=good)
    assert r.holds and r.passed == len(words)


# ------------------------------------------------------------------ the failures

def test_determinism_catches_a_moving_analyser():
    """The check that would be worthless if it compared a cached call twice."""
    nondeterministic.n = 0
    words = sorted({w for t in TEXTS for w in t.split()})
    r = check_determinism(words, analyser=nondeterministic)
    assert not r.holds
    assert r.passed == 0
    assert r.failures


def test_alignment_catches_spans_that_do_not_rebuild():
    """An analysis longer than its span still indexes back but cannot rebuild.

    This is the appended-character failure that a containment test misses and
    which cost DEC-023 its "1,639/1,639 (100%)".
    """
    r = check_alignment(TEXTS, analyser=good)
    assert r.holds, "control: the well-formed case must pass first"

    # Now a genuinely broken one: the span text disagrees with the analysis.
    import tigrinya_eval.morphology as m

    real = m._analyse

    def corrupt(text, analyser):
        a = real(text, analyser)
        if not a.spans:
            return a
        bad = a.spans[0].__class__(
            start=a.spans[0].start, end=a.spans[0].end,
            surface=a.spans[0].surface, analysis=a.spans[0].analysis + "X")
        return a.__class__(
            surface=a.surface, analysis=a.analysis,
            spans=(bad,) + a.spans[1:], variety=a.variety,
            offset_unit=a.offset_unit,
            analysis_is_phonemic=a.analysis_is_phonemic, tier=a.tier)

    m._analyse = corrupt
    try:
        r = check_alignment(TEXTS, analyser=good)
    finally:
        m._analyse = real
    assert not r.holds
    assert r.failures


def test_surface_catches_a_mangled_surface():
    import tigrinya_eval.morphology as m

    real = m._analyse

    def corrupt(text, analyser):
        a = real(text, analyser)
        return a.__class__(surface=a.surface + "!", analysis=a.analysis,
                           spans=a.spans, variety=a.variety,
                           offset_unit=a.offset_unit,
                           analysis_is_phonemic=a.analysis_is_phonemic,
                           tier=a.tier)

    m._analyse = corrupt
    try:
        r = check_surface(TEXTS, analyser=good)
    finally:
        m._analyse = real
    assert not r.holds
    assert r.passed == 0


# ------------------------------------------------------------------ measurements

def test_coverage_is_a_measurement_never_a_pass():
    r = check_coverage(TEXTS, analyser=good)
    assert r.measurement_only
    assert r.verdict == "MEAS"
    assert r.holds, "measurement-only results must not fail a build"
    assert r.rate == 1.0


def test_coverage_counts_surface_fallback_as_uncovered():
    r = check_coverage(TEXTS, analyser=unanalysable)
    assert r.passed == 0 and r.total > 0
    assert r.failures, "the uncovered surfaces should be reported"


def test_normalisation_measures_only_words_that_change():
    words = ["ፀሓይ", "ሰላም"]
    r = check_normalisation(words, analyser=good)
    assert r.measurement_only
    # Only ፀሓይ changes under normalisation; ሰላም must not pad the denominator.
    assert r.total == 1


def test_normalisation_detects_a_variety_sensitive_lexicon():
    """Normalisation rescuing a word is a real, reportable interaction."""
    r = check_normalisation(["ፀሓይ"], analyser=variety_sensitive)
    assert r.total == 1
    assert r.passed == 0, "ፀሓይ analyses only after normalisation — a disagreement"
    assert r.failures


def test_normalisation_with_no_changing_word_reports_zero_not_a_pass():
    r = check_normalisation(["ሰላም"], analyser=good)
    assert r.total == 0 and r.measurement_only
    assert "nothing to compare" in r.note


# ------------------------------------------------------------------ skip semantics

def test_a_skip_is_not_a_pass():
    """The whole reason `skipped` exists as a third state."""
    r = PropertyResult(name="x", passed=0, total=0, threshold=1.0,
                       skipped=True, skip_reason="not installed")
    assert r.holds, "a skip must not fail the build"
    assert r.verdict == "SKIP"
    assert "NOT RUN" in str(r)


@needs_absent
def test_report_marks_skipped_checks_loudly():
    report = evaluate_morphology(TEXTS)          # no analyser -> all skipped
    text = report.report()
    assert report.skipped()
    assert not report.complete, "skipped checks must not read as complete"
    assert "NOT RUN" in text and "NOT MEASURED" in text
    assert "metrics.md morphology row stays" in text


@needs_absent
def test_require_turns_a_skip_into_a_failure():
    report = evaluate_morphology(TEXTS, require=True)
    assert not report.holds
    assert all(not r.skipped for r in report.results)


def test_injected_analyser_runs_every_check():
    report = evaluate_morphology(TEXTS, analyser=good)
    assert not report.skipped()
    assert report.holds
    assert not report.complete, "two checks are measurements, so not complete"
    assert "First real run" in "\n".join(report.notes)


def test_empty_corpus_is_an_error_not_a_pass():
    with pytest.raises(ValueError):
        evaluate_morphology(["", "   "])
