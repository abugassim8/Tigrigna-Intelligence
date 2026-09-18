"""Tests for intrinsic embedding evaluation (DEC-026).

Each gated property is watched **both passing and failing**. That discipline is
not ceremony here: the first version of E1 compared whole sentences, and a
deliberately spelling-blind encoder scored **identically** to a correct one
(0.9282 both) because one substituted character sits among hundreds of
features. **The check could not fail.** It is word-level now, where a correct
encoder scores 1.0000 and the lexical baseline 0.2232.
"""

from __future__ import annotations

import pathlib

import pytest

from tigrinya_primitives import normalise
from tigrinya_eval.embeddings import (
    CharNgramEmbedder, EmbeddingReport, INVARIANCE_FLOOR,
    check_corruption_monotonicity, check_discrimination,
    check_orthographic_invariance, check_self_retrieval, evaluate_embeddings,
)

_REPO = pathlib.Path(__file__).resolve().parents[3]
_CORPUS = _REPO / "experiments" / "003-metric-validity" / "data" / "flores_ti.txt"


@pytest.fixture(scope="module")
def sentences():
    if not _CORPUS.exists():
        pytest.skip("committed corpus not present")
    return [l.strip() for l in _CORPUS.read_text(encoding="utf-8").splitlines()
            if l.strip()]


@pytest.fixture(scope="module")
def baseline(sentences):
    return CharNgramEmbedder().fit(sentences)


class _Normalising:
    """Correct by construction: normalises before embedding."""

    def __init__(self, inner):
        self.inner = inner

    def embed(self, text):
        return self.inner.embed(normalise(text))

    def similarity(self, a, b):
        return self.inner.similarity(a, b)


class _Constant:
    """Every sentence gets the same vector — broken pooling."""

    def embed(self, text):
        return {"c": 1.0}

    def similarity(self, a, b):
        return 1.0


# ------------------------------------------------------------ the baseline

def test_baseline_is_a_working_encoder(baseline, sentences):
    assert check_self_retrieval(baseline, sentences).holds
    assert check_discrimination(baseline, sentences).holds
    assert check_corruption_monotonicity(baseline, sentences).holds


def test_baseline_fails_orthographic_invariance(baseline, sentences):
    """The finding, asserted so it cannot quietly change.

    Character n-grams have no notion that ጸ and ፀ are the same letter. This is
    the specific job a neural model has to do to earn its 119 MB."""
    r = check_orthographic_invariance(baseline, sentences)
    assert not r.holds
    assert r.value < 0.5, f"expected poor invariance, measured {r.value}"


def test_embedder_requires_fitting_first():
    with pytest.raises(ValueError, match="fit"):
        CharNgramEmbedder().embed("ሰላም")


# --------------------------------------------- every check can pass AND fail

def test_invariance_passes_for_a_correct_encoder(baseline, sentences):
    """Without this, E1 is only ever seen failing — as uninformative as a
    check only ever seen passing."""
    r = check_orthographic_invariance(_Normalising(baseline), sentences)
    assert r.holds and r.value == pytest.approx(1.0)


def test_constant_encoder_fails_the_mechanical_checks(sentences):
    c = _Constant()
    assert not check_self_retrieval(c, sentences).holds
    assert not check_discrimination(c, sentences).holds
    assert not check_corruption_monotonicity(c, sentences).holds


def test_report_verdicts_differ_across_the_three_models(baseline, sentences):
    base = evaluate_embeddings(baseline, sentences, name="baseline")
    good = evaluate_embeddings(_Normalising(baseline), sentences, name="normalising")
    bad = evaluate_embeddings(_Constant(), sentences, name="constant")
    assert not base.holds and good.holds and not bad.holds


# ------------------------------------------------------------------ report

def test_report_carries_the_broken_not_wrong_caveat(baseline, sentences):
    text = evaluate_embeddings(baseline, sentences, name="baseline").report()
    assert "BROKEN" in text and "NOT *WRONG*" in text
    assert "speaker" in text


def test_advisory_properties_never_gate(baseline, sentences):
    """A floor invented before any model was measured is not a threshold."""
    r = evaluate_embeddings(baseline, sentences, name="baseline")
    advisory = [x for x in r.results if x.advisory]
    assert advisory, "E5 and E6 are advisory"
    assert all(x.holds for x in advisory)


def test_results_serialise(baseline, sentences):
    import json
    d = evaluate_embeddings(baseline, sentences, name="baseline").to_dict()
    assert json.loads(json.dumps(d)) == d
    assert d["model"] == "baseline" and "caveat" in d


def test_too_few_sentences_is_rejected(baseline):
    with pytest.raises(ValueError, match="at least 5"):
        evaluate_embeddings(baseline, ["ሰላም", "ዓለም"], name="x")


def test_invariance_floor_is_above_the_baseline():
    """If the floor ever drops to where the baseline passes, E1 stops asking
    the question it exists for."""
    assert INVARIANCE_FLOOR > 0.5
