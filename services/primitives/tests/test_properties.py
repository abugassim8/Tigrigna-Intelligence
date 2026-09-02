"""Intrinsic property tests for Tier 0 (DEC-023).

These are the evaluation P-4 requires, made executable. No Tigrinya gold
standard exists for any of these primitives, so correctness is asserted as
properties of the functions themselves — idempotence, determinism,
reversibility, alignment integrity — which need no annotated data.

**What these do not do.** They catch *broken*, not *wrong*. A transliterator
that deterministically returns the wrong phoneme passes every test here.
Morphological and phonemic accuracy need gold data and a native speaker
(A-07, A-13). That limit is stated in DEC-023 and repeated here so nobody
mistakes a green suite for linguistic validation.
"""

from __future__ import annotations

import pytest

from tigrinya_primitives import (
    Analysis, GeezTokenizer, Span, Variety,
    is_normalised, morphology, normalise, normalisation_diff, transliterate,
)

# Real Tigrinya from the cleanly-licensed corpora (MIT / CC-BY-SA-4.0).
CORPUS = [
    "ሰላም ዓለም",
    "ሃገርነት ሃገርና ህላውአን",
    "እዘን መርኣያ ንግስነት ዲሞክራሲያዊ ሃዋህው ሃገርና ኮይነን ዘሎዋ ብሕታውያን ጋዜጣታት ኤርትራ",
    "ልኡላውነት ኤርትራን፡ ዝምቡዕ ፖሊሲ ባሕሪ ሰልፊ ብልጽግናን",
    "ኣብ ሃሊፋክስ፣ ኖቫ ስኮቲያ ናይ ዶልሆሲ ዩኒቨርሲቲ ፕሮፌሰር ሕክምና",
]
# Both orthographic variants, to exercise normalisation.
MIXED = ["ፀሓይ ጸሓይ", "አብ ኣብ", "ብልፅግና ብልጽግና"]


# ------------------------------------------------------------- normalisation

@pytest.mark.parametrize("text", CORPUS + MIXED)
def test_normalisation_is_idempotent(text):
    """H1. A non-idempotent normaliser compounds errors silently."""
    once = normalise(text)
    assert normalise(once) == once


@pytest.mark.parametrize("text", CORPUS + MIXED)
def test_normalisation_preserves_length(text):
    """Every substitution is 1:1, so offsets computed on the input stay valid."""
    assert len(normalise(text)) == len(text)


def test_normalisation_collapses_both_variants_together():
    """The point of normalising: variant spellings must match each other."""
    assert normalise("ፀሓይ") == normalise("ጸሓይ")
    assert normalise("አብ") == normalise("ኣብ")


def test_is_normalised_agrees_with_normalise():
    assert is_normalised("ጸሓይ")
    assert not is_normalised("ፀሓይ")


def test_normalisation_diff_explains_the_change():
    """A caller must be able to say WHY two strings matched."""
    diff = normalisation_diff("ፀሓይ")
    assert diff == [(0, "ፀ", "ጸ")]


# ----------------------------------------------------------- transliteration

@pytest.mark.parametrize("text", CORPUS)
def test_transliteration_is_deterministic(text):
    """H2. Same input, same output — across calls."""
    assert transliterate(text).analysis == transliterate(text).analysis


@pytest.mark.parametrize("text", CORPUS)
def test_surface_is_returned_verbatim(text):
    """DEC-022: the surface form is the source of truth and is never rebuilt."""
    assert transliterate(text).surface == text


@pytest.mark.parametrize("text", CORPUS)
def test_offsets_index_back_into_the_surface(text):
    """The alignment guarantee, checked rather than trusted."""
    a = transliterate(text)
    a.verify_offsets()
    for s in a.spans:
        assert text[s.start:s.end] == s.surface


@pytest.mark.parametrize("text", CORPUS)
def test_word_level_alignment_is_exact(text):
    """DEC-023's core claim: the analysis form IS the concatenation.

    Character-level alignment is impossible (23.89% measured). Word-level is
    exact by construction, and this test is what makes that a guarantee rather
    than an assumption.
    """
    a = transliterate(text)
    for s in a.spans:
        assert s.analysis in a.analysis
        # each span's analysis is exactly that word's transliteration
        assert s.analysis == transliterate(s.surface).analysis


@pytest.mark.parametrize("text", CORPUS)
def test_whitespace_is_preserved_in_the_analysis_form(text):
    """Word boundaries must survive, or spans stop meaning anything."""
    a = transliterate(text)
    assert len(a.analysis.split()) == len(text.split())


def test_analysis_is_declared_non_phonemic():
    """DEC-022 clause 3 — 19 real characters pass through untransliterated."""
    assert transliterate("ሰላም").analysis_is_phonemic is False


def test_unmapped_block_produces_a_warning():
    """Ethiopic Extended-B is unmapped; the response must say so, not hide it."""
    a = transliterate("ሰላም \U0001E7E0")
    assert any("Extended-B" in w for w in a.warnings)


def test_extended_b_offsets_stay_correct_above_the_bmp():
    """The trap DEC-022 exists to prevent.

    Extended-B needs a UTF-16 surrogate pair, so a JS client's `.length` and a
    code-point offset disagree. Offsets here are code points, and must still
    index correctly.
    """
    text = "ሰላም \U0001E7E0 ዓለም"
    a = transliterate(text)
    a.verify_offsets()
    assert a.offset_unit.value == "codepoint"


def test_empty_input_is_handled():
    a = transliterate("")
    assert a.surface == "" and a.analysis == "" and a.spans == ()


def test_variety_defaults_to_unknown_not_null():
    """DEC-010: `unknown` is a first-class value; a null would invite callers
    to ignore the distinction the decision exists to preserve."""
    assert transliterate("ሰላም").variety is Variety.UNKNOWN


# -------------------------------------------------------------- tokenization

@pytest.fixture(scope="module")
def tokenizer():
    # min_frequency=1: on a corpus this small, the default of 2 saturates the
    # vocabulary far below the requested size.
    return GeezTokenizer.train(CORPUS, vocab_size=500, min_frequency=1)


@pytest.mark.parametrize("text", CORPUS)
def test_tokenization_round_trips(tokenizer, text):
    """H4. DEC-022 obliges verbatim surface forms, which is impossible if the
    tokenizer cannot reconstruct its input."""
    assert tokenizer.round_trips(text)


def test_tokenizer_produces_no_unk(tokenizer):
    """Byte-level BPE means no input can fall out of vocabulary."""
    for text in CORPUS:
        assert "[UNK]" not in tokenizer.tokens(text)


def test_tokenizer_round_trips_unseen_text(tokenizer):
    """Reversibility must hold for text the tokenizer never saw."""
    assert tokenizer.round_trips("ኣነ ንዓኡ ኣይረኸብክዎን")
    assert tokenizer.round_trips("\U0001E7E0")


def test_fertility_is_reported(tokenizer):
    f = tokenizer.fertility(CORPUS)
    assert f.words > 0
    assert f.tokens_per_word > 0


# ---------------------------------------------------------------- morphology

def test_morphology_is_honestly_unavailable():
    """Absent, not silently degraded.

    A-07 is closed: **DEC-028** adopts HornMorpho as a dependency the *user*
    installs, because it is GPL-3.0 and this package is Apache-2.0. So the
    honest state here is "not installed", and the error has to say how to
    install it rather than pointing at a blocker that no longer exists.

    Full coverage of the adapter — spans, offsets, degradation, the
    None-on-missing-language trap — is in `test_morphology.py`, which injects a
    fake analyser so none of it needs a GPL-3.0 dependency present.
    """
    assert morphology.is_available() is False
    with pytest.raises(NotImplementedError, match="GPL-3.0"):
        morphology.analyse("ሰላም")


# ------------------------------------------------------------------ contract

def test_span_rejects_inconsistent_offsets():
    """A span whose width disagrees with its surface would misalign silently."""
    with pytest.raises(ValueError, match="does not match surface"):
        Span(start=0, end=5, surface="ሰላም", analysis="səlam")


def test_verify_offsets_catches_corruption():
    """The guard must actually fire when offsets are wrong."""
    bad = Analysis(
        surface="ሰላም ዓለም",
        analysis="x",
        spans=(Span(start=4, end=7, surface="ሰላም", analysis="x"),),
    )
    with pytest.raises(ValueError, match="claims"):
        bad.verify_offsets()


def test_to_dict_is_json_shaped():
    import json
    d = transliterate("ሰላም").to_dict()
    assert d["offset_unit"] == "codepoint"
    assert d["variety"] == "unknown"
    assert d["analysis_is_phonemic"] is False
    json.dumps(d)  # must be serialisable


# --------------------------------------------------------------- warmup

def test_warmup_loads_the_transliterator_and_is_idempotent():
    """Lazy loading defers ~3.0 s — 98.7% of Tier 0's cold start (exp 006) —
    onto whoever calls first. An always-warm service should pay it at boot."""
    from tigrinya_primitives import warmup
    from tigrinya_primitives.transliterate import _epi

    warmup()
    assert _epi().transliterate("ሰላም")     # usable immediately
    before = _epi.cache_info().currsize
    warmup()                                # idempotent, no reload
    assert _epi.cache_info().currsize == before == 1


# ------------------------------------------------- contract and API surface

def test_response_discloses_the_serving_tier():
    """DEC-022 names a `tier` clause. It went unimplemented until an audit
    compared the decision text against the actual payload — six of seven
    clauses were enforced and this one silently was not.

    It matters because the tiers differ by ~150x in memory and far more in
    latency; a client cannot set a sensible timeout without knowing which
    answered."""
    from tigrinya_primitives import transliterate
    d = transliterate("ሰላም ዓለም").to_dict()
    assert "tier" in d, "DEC-022 requires the serving tier in the response"
    assert d["tier"] == 0, "primitives are Tier 0 (DEC-013)"


def test_span_rejects_impossible_offsets():
    """The validation branch that makes a misaligned span unrepresentable."""
    from tigrinya_primitives.types import Span
    with pytest.raises(ValueError, match="invalid span"):
        Span(start=-1, end=2, surface="ab", analysis="x")
    with pytest.raises(ValueError, match="invalid span"):
        Span(start=5, end=2, surface="", analysis="")


def test_tokenizer_survives_save_and_load(tmp_path):
    """`save`/`load` are public API and were entirely untested.

    The [UNK] bug this project already shipped was a round-trip failure, and
    serialisation is where a byte-level decoder is most easily lost."""
    from tigrinya_primitives import GeezTokenizer
    corpus = ["ሰላም ዓለም ከመይ ኣለኻ", "ትግርኛ ቋንቋ እዩ", "ሃገርነት ኤርትራ"]
    tok = GeezTokenizer.train(corpus, vocab_size=500, min_frequency=1)
    unseen = "እዚ ዘይተራእየ ጽሑፍ እዩ፣ ምስ ኣሃዛት 1960።"

    path = tmp_path / "tok.json"
    tok.save(path)
    loaded = GeezTokenizer.load(path)

    assert loaded.vocab_size == tok.vocab_size
    assert loaded.encode(unseen) == tok.encode(unseen)
    assert loaded.round_trips(unseen), "reloaded tokenizer lost round-trip fidelity"
    assert "[UNK]" not in loaded.tokens(unseen)


def test_fertility_counts_tokens_per_word():
    from tigrinya_primitives import GeezTokenizer
    corpus = ["ሰላም ዓለም ከመይ ኣለኻ", "ትግርኛ ቋንቋ እዩ"]
    tok = GeezTokenizer.train(corpus, vocab_size=500, min_frequency=1)
    f = tok.fertility(corpus)
    assert f.words == 7           # 4 + 3 whitespace-delimited words
    assert f.tokens >= f.words    # never fewer tokens than words
    assert f.tokens_per_word == f.tokens / f.words
    assert GeezTokenizer.train(["ሰላም"], vocab_size=300,
                               min_frequency=1).fertility([]).tokens_per_word == 0.0
