"""Conformance tests for the DEC-022 response contract.

Why this file exists separately from the property tests
-------------------------------------------------------
**DEC-022 clause 5 — "the serving tier is disclosed" — was decided on
2026-08-03 and was still not implemented on 2026-08-19.** Six of the seven
clauses were enforced. Nothing compared the decision text against the payload,
so the gap survived a build, a test suite, two audits, and a documentation pass
that confidently asserted the clause as part of the contract.

Testing the clauses I happen to remember would reproduce exactly that failure.
So this file does two things instead:

1. **Counts the clauses in the decision record itself** and fails if the
   contract map here does not cover them. Adding a sixth clause to DEC-022
   breaks this suite until someone implements it.
2. **Pins the payload's exact field set**, so drift fails in *both* directions —
   a field added without declaring it, or a declared field quietly dropped.

Neither check knows anything about which clauses seemed important. That is the
point.
"""

from __future__ import annotations

import json
import pathlib
import re

import pytest

from tigrinya_primitives import Variety, transliterate
from tigrinya_primitives.types import Analysis, OffsetUnit, Span

#: services/primitives/tests -> services/primitives -> services -> repo root
_REPO = pathlib.Path(__file__).resolve().parents[3]
_DECISIONS = _REPO / "docs" / "decisions" / "DECISIONS.md"

#: The exact key set every analysis response carries. Not a subset check:
#: an undeclared field is as much a contract change as a missing one, and the
#: whole point is that changes to the payload cannot pass unnoticed.
CONTRACT_FIELDS = {
    "surface", "analysis", "spans", "variety",
    "offset_unit", "analysis_is_phonemic", "tier", "warnings",
}

SPAN_FIELDS = {"start", "end", "surface", "analysis"}

#: One entry per numbered clause in DEC-022. The count is asserted against the
#: decision record below — this map is not allowed to fall behind it.
DEC_022_CLAUSES = {
    1: "offsets are code points and the unit is stated explicitly",
    2: "the surface form is returned verbatim, never reconstructed",
    3: "the analysis form is declared non-phonemic",
    4: "a variety label is mandatory; `unknown` is first-class, never null",
    5: "the serving tier is disclosed",
}

SAMPLE = "ሰላም ዓለም"


@pytest.fixture
def payload():
    return transliterate(SAMPLE, variety=Variety.ERITREAN).to_dict()


# ------------------------------------------------- the contract cannot drift

def _dec022_clause_count() -> int | None:
    """Count the numbered clauses in DEC-022's Decision section."""
    if not _DECISIONS.exists():
        return None
    text = _DECISIONS.read_text(encoding="utf-8")
    start = text.index("## DEC-022")
    body = text[start:text.index("**Context:**", start)]
    return len(re.findall(r"^\d+\. \*\*", body, flags=re.MULTILINE))


def test_every_clause_in_the_decision_record_is_covered_here():
    """The check that would have caught the missing `tier` clause.

    It reads DEC-022 rather than trusting this file's own list, so a clause
    added to the decision fails the suite until it is implemented and tested.
    """
    n = _dec022_clause_count()
    if n is None:
        pytest.skip("DECISIONS.md not present in this checkout")
    assert n == len(DEC_022_CLAUSES), (
        f"DEC-022 states {n} clauses but this suite covers "
        f"{len(DEC_022_CLAUSES)}. A clause was added to the decision and not "
        f"implemented — which is exactly how clause 5 went missing for 16 days."
    )


def test_payload_field_set_is_exactly_the_contract(payload):
    """Both directions. An extra field is a contract change too."""
    assert set(payload) == CONTRACT_FIELDS, (
        f"payload drifted from the contract: "
        f"unexpected {set(payload) - CONTRACT_FIELDS}, "
        f"missing {CONTRACT_FIELDS - set(payload)}"
    )


def test_span_field_set_is_exactly_the_contract(payload):
    assert payload["spans"], "sample must produce spans"
    for s in payload["spans"]:
        assert set(s) == SPAN_FIELDS


def test_payload_is_json_serialisable(payload):
    """A contract that cannot cross the wire is not a contract.

    sacrebleu's numpy float32 broke this for the evaluation harness once; the
    same class of failure would be worse here, on every response.
    """
    round_tripped = json.loads(json.dumps(payload, ensure_ascii=False))
    assert round_tripped == payload


# --------------------------------------------------------- clause by clause

def test_clause_1_offsets_are_codepoints_and_the_unit_is_stated(payload):
    assert payload["offset_unit"] == "codepoint"
    assert isinstance(payload["offset_unit"], str), "must serialise as a string"
    # The unit is only meaningful if the offsets actually index code points.
    for s in payload["spans"]:
        assert SAMPLE[s["start"]:s["end"]] == s["surface"]


def test_clause_1_holds_above_the_bmp():
    """Ethiopic Extended-B is the case the clause exists for.

    A UTF-16 client counting `.length` disagrees with a code-point client on
    exactly these characters, and they appear in none of our corpora — so the
    contract must be right about them before one ever arrives.
    """
    text = "ሰላም \U0001E7E0\U0001E7E1"
    a = transliterate(text)
    a.verify_offsets()
    for s in a.spans:
        assert text[s.start:s.end] == s.surface
    assert a.warnings, "unmapped-block text must carry a warning"


def test_clause_2_surface_is_verbatim():
    """Including whitespace a reconstruction would normalise away."""
    odd = "ሰላም   ዓለም\tኩሉ"
    a = transliterate(odd)
    assert a.surface == odd
    assert a.to_dict()["surface"] == odd


def test_clause_2_surface_is_never_reconstructed_from_analysis():
    """Guards the direction of dependence, not just the value.

    A reconstruction would be lossy: the analysis form of a word is not
    invertible back to Ge'ez, so a response built the other way round would be
    silently wrong for any character the transliterator passes through.
    """
    a = transliterate(SAMPLE)
    assert a.surface == SAMPLE
    assert a.analysis != a.surface
    # Spans carry the surface substring itself, not a re-rendering of it.
    assert "".join(s.surface for s in a.spans) == SAMPLE.replace(" ", "")


def test_clause_3_analysis_is_declared_non_phonemic(payload):
    assert payload["analysis_is_phonemic"] is False, (
        "declaring the analysis form phonemic is measurably false — 19 real "
        "Ethiopic characters pass through and three blocks are unmapped"
    )


def test_clause_4_variety_is_mandatory_and_unknown_is_not_null():
    assert transliterate(SAMPLE).to_dict()["variety"] == "unknown"
    for v in Variety:
        assert transliterate(SAMPLE, variety=v).to_dict()["variety"] == v.value
    # A null would invite callers to ignore the distinction DEC-010 protects.
    assert None not in {v.value for v in Variety}


def test_clause_5_serving_tier_is_disclosed(payload):
    """The clause that was decided and silently unimplemented for 16 days."""
    assert "tier" in payload
    assert payload["tier"] == 0, "primitives are Tier 0 (DEC-013)"
    assert isinstance(payload["tier"], int)


# ------------------------------------------------------- enforcement, not hope

def test_misaligned_spans_are_unrepresentable():
    """The contract is enforced by construction, not by convention."""
    with pytest.raises(ValueError, match="offsets would be wrong"):
        Span(start=0, end=3, surface="ab", analysis="x")


def test_verify_offsets_catches_a_span_that_does_not_index_back():
    bad = Analysis(surface="ሰላም ዓለም", analysis="x",
                   spans=(Span(start=0, end=3, surface="ዓለም", analysis="x"),))
    with pytest.raises(ValueError, match="but surface holds"):
        bad.verify_offsets()


def test_empty_input_still_satisfies_the_contract():
    """Edge cases are where contracts quietly stop applying."""
    d = transliterate("").to_dict()
    assert set(d) == CONTRACT_FIELDS
    assert d["surface"] == "" and d["spans"] == []
    assert d["offset_unit"] == "codepoint" and d["tier"] == 0
    assert d["variety"] == "unknown"


def test_offset_unit_enum_has_one_member():
    """If a second unit is ever added, clause 1 needs re-deciding, not
    extending — the whole point is that one unit is stated and used."""
    assert [u.value for u in OffsetUnit] == ["codepoint"]
