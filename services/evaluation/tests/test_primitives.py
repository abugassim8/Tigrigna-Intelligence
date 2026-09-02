"""Tests for intrinsic primitive evaluation (DEC-023a).

Half of these are **negative controls**: they feed a deliberately broken
primitive to a check and assert the check reports failure.

That is not padding. The finding that produced this module was a verification
that *could not fail* — DEC-023 recorded "1,639/1,639 (100%)" from a containment
test blind to the only failure mode that occurs. A check nobody has watched fail
is not evidence of anything, so each one here is watched failing.
"""

from __future__ import annotations

import functools
import json
import pathlib

import pytest

from tigrinya_eval.primitives import (
    CONTEXT_DIVERGENCE_CEILING,
    IntrinsicReport,
    check_alignment_integrity,
    check_context_divergence,
    check_coverage,
    check_determinism,
    check_idempotence,
    check_reversibility,
    evaluate_primitives,
    is_ethiopic,
    load_corpus,
)

# Real Tigrinya (FLORES+, CC-BY-SA-4.0), already committed to experiments/003.
TEXTS = [
    "እሱ ናይ ዋይፋይ ማዕጾ ደወል ሰሪሑ ኢሉ ተዛሪቡ።",
    "ሪንግ ምስ እቲ መፎኻኽርቱ ዝኾነ፣ ኤዲቲ ኮርፖሬሽን፣ ዝነበሮ ክሲ ፈቲሑዎ እዩ።",
    "እዚ ዝተረኽበ ቅሪት ናይ ኣዕዋፍ መንፈሪ ዝረአ ለውጢ የመልክት።",
    "ልኡላውነት ኤርትራን ናጽነታን ብረታዊ ቃልሲ ዝመጽአ እዩ።",
]


#: services/evaluation/tests/ -> services/evaluation -> services -> repo root
_REPO = pathlib.Path(__file__).resolve().parents[3]
_CORPORA = (
    _REPO / "experiments" / "002-tokenizer-fertility" / "corpus",
    _REPO / "experiments" / "003-metric-validity" / "data",
)


@functools.lru_cache(maxsize=1)
def _corpus_lines() -> tuple[str, ...]:
    """Committed corpus text, or empty if the experiments are not present."""
    present = [d for d in _CORPORA if d.is_dir()]
    if not present:
        return ()
    return tuple(
        ln for t in load_corpus(present) for ln in t.splitlines() if ln.strip()
    )


# ------------------------------------------------------------- the checks pass

def test_all_intrinsic_properties_hold_on_real_text():
    r = evaluate_primitives(TEXTS)
    assert r.holds, r.report()
    assert len(r.results) == 6


def test_idempotence_holds():
    assert check_idempotence(TEXTS).holds


def test_determinism_holds():
    words = sorted({w for t in TEXTS for w in t.split()})
    assert check_determinism(words).holds


def test_alignment_integrity_holds():
    assert check_alignment_integrity(TEXTS).holds


def test_reversibility_holds_with_no_unk():
    r = check_reversibility(TEXTS)
    assert r.holds
    assert "0 [UNK]" in r.note


def test_coverage_counts_letters_not_punctuation():
    """The bug this check had twice: counting characters meant to pass through.

    Every text here ends in `።` (ETHIOPIC FULL STOP), which is never
    transliterated. If punctuation were counted, coverage could not reach 100%.
    """
    r = check_coverage(TEXTS)
    assert r.holds
    assert r.rate == 1.0, f"{r.failures}"
    assert r.regression_guard is True


# ------------------------------------------------------- the checks can fail

class _BrokenTokenizer:
    """Round-trips everything except the one string that matters."""

    def __init__(self, victim: str) -> None:
        self._victim = victim

    def tokens(self, text): return ["[UNK]"] if text == self._victim else [text]
    def encode(self, text): return [0]
    def decode(self, ids): return "mangled"
    def round_trips(self, text): return text != self._victim


def test_reversibility_detects_a_broken_tokenizer():
    """The negative control for the byte-level BPE `[UNK]` bug."""
    r = check_reversibility(TEXTS, tokenizer=_BrokenTokenizer(TEXTS[0]))
    assert not r.holds
    assert r.passed == len(TEXTS) - 1
    assert "[UNK]" in r.note


def test_idempotence_detects_a_non_idempotent_normaliser(monkeypatch):
    import tigrinya_eval.primitives as P
    monkeypatch.setattr(P, "normalise", lambda s: s + "ሀ")
    r = P.check_idempotence(TEXTS)
    assert not r.holds
    assert r.passed == 0


def test_determinism_detects_a_nondeterministic_transliterator(monkeypatch):
    """Also proves the check is not fooled by the `lru_cache`.

    A stub whose answer changes on every call must be caught. If the check
    forgot `cache_clear()`, the second pass would read the memo table and this
    test would pass a broken transliterator.
    """
    import tigrinya_eval.primitives as P

    calls = {"n": 0}

    class _Flaky:
        def cache_clear(self): pass
        def __call__(self, w):
            calls["n"] += 1
            return f"{w}{calls['n']}"

    monkeypatch.setattr(P, "transliterate_word", _Flaky())
    r = P.check_determinism(["ሰላም", "ዓለም"])
    assert not r.holds
    assert r.passed == 0


def test_alignment_integrity_detects_a_wrong_span(monkeypatch):
    import tigrinya_eval.primitives as P
    from tigrinya_primitives import transliterate as real_transliterate
    from tigrinya_primitives.types import Analysis, Span

    def _broken(text, *a, **k):
        good = real_transliterate(text)
        # Offsets still valid, but the span's analysis no longer composes into
        # the analysis form — the silent misalignment this check exists for.
        bad = tuple(
            Span(start=s.start, end=s.end, surface=s.surface,
                 analysis=s.analysis + "X")
            for s in good.spans
        )
        return Analysis(surface=good.surface, analysis=good.analysis, spans=bad)

    monkeypatch.setattr(P, "transliterate", _broken)
    r = P.check_alignment_integrity(TEXTS)
    assert not r.holds


def test_coverage_detects_an_unmapped_letter(monkeypatch):
    import tigrinya_eval.primitives as P
    monkeypatch.setattr(P, "transliterate_word", lambda ch: ch)  # maps nothing
    r = P.check_coverage(TEXTS)
    assert not r.holds
    assert r.rate == 0.0


# ------------------------------------------------ the corrected DEC-023 claim

def test_context_divergence_is_measured_by_equality_not_containment():
    """The specific error DEC-023 made, pinned so it cannot recur.

    A containment test reported 99.62% where exact equality reports 95.47%,
    because an appended word-final `ɨ` leaves the shorter string a substring of
    the longer one. This asserts the check uses equality.
    """
    from tigrinya_primitives.transliterate import _epi, transliterate_word

    epi = _epi()
    # The divergence is position-sensitive: a distant edit flips it, so it
    # cannot be reproduced from a shortened excerpt. The committed corpus is
    # the fixture — which DEC-016 requires to exist regardless.
    lines = _corpus_lines()
    if not lines:
        pytest.skip("committed experiment corpora not present in this checkout")

    divergent = []
    for line in lines:
        words = line.split()
        ctx = epi.transliterate(line).split()
        if len(ctx) != len(words):
            continue
        divergent += [(w, transliterate_word(w), c)
                      for w, c in zip(words, ctx) if transliterate_word(w) != c]
    assert divergent, "expected at least one word to diverge in context"

    # The point: on these words containment SUCCEEDS while equality FAILS.
    # That gap is the whole reason DEC-023 recorded a wrong number.
    fooled_containment = [(w, a, c) for w, a, c in divergent if a in c]
    assert fooled_containment, (
        "expected divergent words that a containment test would pass"
    )
    w, alone, in_ctx = fooled_containment[0]
    assert alone in in_ctx      # containment: passes
    assert alone != in_ctx      # equality: fails

    r = check_context_divergence(TEXTS)
    assert r.regression_guard is True
    assert "DEC-023" in r.note


def test_context_divergence_stays_under_its_ceiling():
    r = check_context_divergence(TEXTS)
    assert r.holds
    assert CONTEXT_DIVERGENCE_CEILING == 0.06


# ------------------------------------------------------------------- report

def test_report_carries_the_broken_not_wrong_caveat():
    """A report that travels without its caveats will be quoted without them."""
    text = evaluate_primitives(TEXTS).report()
    assert "BROKEN" in text and "NOT *WRONG*" in text
    assert "gold standard" in text


def test_report_names_morphology_as_unevaluated():
    """Silence about an unevaluated capability reads as a pass.

    Morphology is now *implemented* (DEC-028) and still unevaluated, which is a
    strictly easier state to misread — "the module exists" invites the
    assumption that it was measured. The report has to keep saying otherwise,
    and has to say why: the analyser is GPL-3.0 and never bundled, so there is
    nothing present to measure.
    """
    report = evaluate_primitives(TEXTS).report()
    assert "Morphology is not evaluated" in report
    assert "DEC-028" in report
    assert "GPL-3.0" in report


def test_thresholds_are_labelled_as_guards_or_predictions():
    """A regression floor presented as a passed hypothesis is overclaiming."""
    r = evaluate_primitives(TEXTS)
    by = {x.name: x for x in r.results}
    assert by["normalisation.idempotent"].regression_guard is False
    assert by["transliteration.coverage"].regression_guard is True


def test_results_serialise_to_json(tmp_path):
    out = tmp_path / "intrinsic.json"
    evaluate_primitives(TEXTS).save(out)
    d = json.loads(out.read_text(encoding="utf-8"))
    assert d["holds"] is True
    assert len(d["results"]) == 6
    assert "caveat" in d


def test_empty_corpus_is_rejected():
    with pytest.raises(ValueError, match="nothing to evaluate"):
        evaluate_primitives(["", "   "])


def test_is_ethiopic_covers_extended_b_above_the_bmp():
    """Ethiopic Extended-B is above the BMP — the block that breaks UTF-16
    clients and is unlikely to reach a test fixture by accident."""
    assert is_ethiopic("\U0001E7E0")
    assert is_ethiopic("ሰ")
    assert not is_ethiopic("a") and not is_ethiopic("1")


def test_load_corpus_skips_the_corrupted_sample(tmp_path):
    (tmp_path / "clean.txt").write_text("ሰላም", encoding="utf-8")
    (tmp_path / "x_CORRUPTED.txt").write_text("ሰላም", encoding="utf-8")
    assert len(load_corpus([tmp_path])) == 1


def test_report_is_a_failure_when_any_property_fails():
    r = IntrinsicReport(
        results=(check_reversibility(TEXTS, _BrokenTokenizer(TEXTS[0])),),
        texts=len(TEXTS), words=10, unique_words=8,
    )
    assert not r.holds
    assert "FAIL" in r.report()
    assert "failing: tokenization.reversible" in r.report()
