"""Tests for the evaluation harness.

These check that DEC-009 and DEC-010 are *enforced*, not merely documented.
Both decisions exist because the failure they prevent is silent: BLEU reported
alone reads as a normal score, and an aggregate across varieties reads as a
normal average. Neither announces itself as wrong.
"""

from __future__ import annotations

import json

import pytest

from tigrinya_eval import (
    CrossVarietyAggregationError, EvalSet, Harness, SACREBLEU_VERSION, score,
)

# Real Tigrinya from FLORES+ (CC-BY-SA-4.0), already committed to experiments/003.
REFS = [
    "እሱ ናይ ዋይፋይ ማዕጾ ደወል ሰሪሑ ኢሉ ተዛሪቡ።",
    "ሪንግ ምስ እቲ መፎኻኽርቱ ዝኾነ፣ ኤዲቲ ኮርፖሬሽን፣ ዝነበሮ ክሲ ፈቲሑዎ እዩ።",
    "እዚ ዝተረኽበ ቅሪት ናይ ኣዕዋፍ መንፈሪ ዝረአ ለውጢ የመልክት።",
]
# A plausible-but-imperfect system output.
HYPS = [
    "እሱ ናይ ዋይፋይ ማዕጾ ደወል ሰሪሑ ኢሉ ተዛሪቡ።",
    "ሪንግ ምስ እቲ ተወዳዳሪ ኩባንያ ዝነበሮ ክሲ ፈቲሑዎ እዩ።",
    "እዚ ቅሪት ናይ ኣዕዋፍ ለውጢ የመልክት።",
]


@pytest.fixture
def eval_set():
    return EvalSet(
        name="flores+_sample",
        variety="unknown",
        references=REFS,
        source="alexei-v-ivanov-amd/flores_plus",
        licence="CC-BY-SA-4.0",
    )


# ------------------------------------------------------------------ metrics

def test_bleu_cannot_be_obtained_alone():
    """DEC-009 forbids reporting BLEU alone; enforced by making it
    unrepresentable rather than by a convention someone must remember."""
    s = score(HYPS, REFS)
    assert s.chrf is not None and s.bleu is not None
    assert s.primary is s.chrf  # chrF leads


def test_perfect_translation_scores_perfectly():
    s = score(REFS, REFS)
    assert s.chrf.score == pytest.approx(100.0, abs=0.01)
    assert s.bleu.score == pytest.approx(100.0, abs=0.01)


def test_scores_carry_the_pinned_implementation_version():
    """A metric number without its implementation version is not reproducible."""
    s = score(HYPS, REFS)
    assert s.sacrebleu_version == SACREBLEU_VERSION == "2.6.0"
    assert s.chrf.signature and s.bleu.signature


def test_misaligned_input_is_rejected():
    with pytest.raises(ValueError, match="aligned"):
        score(HYPS[:2], REFS)


def test_empty_input_is_rejected():
    with pytest.raises(ValueError, match="nothing to score"):
        score([], [])


def test_cross_language_warning_states_the_measured_penalty():
    """The ~8% figure must appear, or the caveat is not actionable."""
    from tigrinya_eval import TranslationScores
    assert "1.08" in TranslationScores.cross_language_warning()


# -------------------------------------------------------------- variety rule

def test_variety_label_is_mandatory_and_validated():
    with pytest.raises(ValueError, match="eritrean/ethiopian/unknown"):
        EvalSet(name="x", variety="tigrinya", references=REFS)


def test_unknown_is_a_legitimate_variety():
    """DEC-010: `unknown` is a first-class value, not a null or an error.
    Most Tigrinya resources do not state their variety."""
    s = EvalSet(name="x", variety="unknown", references=REFS)
    assert s.variety == "unknown"


def test_aggregate_refuses_and_says_why(eval_set):
    """The central DEC-010 guarantee. An exception, not a warning — a warning
    would be ignored exactly when it mattered."""
    h = Harness()
    h.evaluate("sys-a", HYPS, eval_set)
    with pytest.raises(CrossVarietyAggregationError, match="DEC-010"):
        h.aggregate()


def test_results_group_by_variety():
    h = Harness()
    er = EvalSet(name="tiquad", variety="eritrean", references=REFS)
    et = EvalSet(name="flores", variety="ethiopian", references=REFS)
    h.evaluate("sys", HYPS, er)
    h.evaluate("sys", HYPS, et)
    groups = h.by_variety()
    assert set(groups) == {"eritrean", "ethiopian"}
    assert len(groups["eritrean"]) == 1


# ------------------------------------------------------------- shippability

def test_non_shippable_system_is_marked(eval_set):
    """NLLB is CC-BY-NC-4.0 — measurable, never deployable (DEC-011)."""
    h = Harness()
    r = h.evaluate("nllb-200-3.3B", HYPS, eval_set, shippable=False,
                   notes=("CC-BY-NC-4.0 — comparison baseline only",))
    assert r.shippable is False
    assert "COMPARISON ONLY" in h.report()


def test_report_carries_its_own_caveats(eval_set):
    """A report that travels without its caveats will be quoted without them."""
    h = Harness()
    h.evaluate("madlad400-3b", HYPS, eval_set)
    text = h.report()
    assert "chrF is primary" in text
    assert "1.08" in text                      # the cross-language penalty
    assert "NOT aggregated across varieties" in text


def test_results_serialise_to_json(eval_set, tmp_path):
    h = Harness()
    h.evaluate("madlad400-3b", HYPS, eval_set)
    out = tmp_path / "results.json"
    h.save(out)
    d = json.loads(out.read_text())
    r = d["results"][0]
    assert r["variety"] == "unknown"
    assert r["sacrebleu_version"] == "2.6.0"
    assert "chrf" in r and "bleu" in r


# ------------------------------------------------- the measured chrF property

def test_chrf_degrades_more_gracefully_than_bleu():
    """The reason chrF is primary (DEC-009), asserted rather than assumed.

    Under inflectional near-misses chrF retains substantially more of a perfect
    score than BLEU — the advantage that widens as quality falls, which is the
    regime low-resource MT lives in.
    """
    import random
    rng = random.Random(20260803)
    corrupted = []
    for s in REFS:
        ws = s.split()
        idx = rng.sample(range(len(ws)), max(1, len(ws) // 4))
        for i in idx:
            if len(ws[i]) >= 2:
                ws[i] = ws[i][:-1] + "ን"        # right stem, wrong affix
        corrupted.append(" ".join(ws))
    s = score(corrupted, REFS)
    assert s.chrf.score > s.bleu.score, (
        f"chrF {s.chrf.score:.1f} should exceed BLEU {s.bleu.score:.1f} "
        "under inflectional near-misses"
    )


def test_confidence_intervals_are_actually_produced():
    """DEC-009 requires spread on small evaluation sets.

    `score()` catches TypeError/ValueError and falls back to point estimates
    with no interval. Nothing asserted the interval exists, so a sacrebleu API
    change would have silently removed CIs with every test still green."""
    s = score(HYPS, REFS, confidence_interval=True)
    for m in (s.chrf, s.bleu):
        assert m.ci_low is not None, f"{m.name} lost its confidence interval"
        assert m.ci_high is not None
        assert m.ci_low <= m.score <= m.ci_high, f"{m.name} score outside its own CI"
    assert "[" in s.summary(), "summary must show the interval"


def test_confidence_intervals_can_be_declined():
    s = score(HYPS, REFS, confidence_interval=False)
    assert s.chrf.ci_low is None and s.bleu.ci_low is None
    assert s.chrf.score > 0
