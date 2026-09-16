"""Tests for the translation interface.

⚠️ **None of these load a model, and that is the design working.** The
`Translator` injection point exists so the pipeline around the model is real
code under real test in an environment where the model cannot be downloaded.
`MadladTranslator.__call__` is the one thing not covered here; its first run on
a machine with the weights is its first test.
"""

from __future__ import annotations

import pytest

from tigrinya_translate import (LANGUAGE_TOKEN, MODEL, SegmentCountError,
                                UnknownLanguageTokenError, translate_all)
from tigrinya_translate.translate import MadladTranslator


class FakeTokenizer:
    """Just enough tokenizer to exercise the language-token gate."""

    name_or_path = "fake/madlad"

    def __init__(self, tokens):
        self._vocab = {t: i for i, t in enumerate(tokens)}

    def get_vocab(self):
        return dict(self._vocab)


# ------------------------------------------------------- the language token

def test_a_known_language_token_is_accepted():
    tok = FakeTokenizer(["<2en>", "<2ti>", "<2am>", "hello"])
    MadladTranslator._assert_language_token(tok, "<2ti>")


def test_an_unknown_language_token_refuses_rather_than_translating():
    """The check that stops a plausible, scoreable, meaningless result.

    An unrecognised prefix does not stop a translation model — it becomes part
    of the sentence and the model emits *some* language. Segment count, shape
    and chrF all look fine. Nothing else in this repository would notice.
    """
    tok = FakeTokenizer(["<2en>", "<2am>", "<2so>", "hello"])
    with pytest.raises(UnknownLanguageTokenError) as exc:
        MadladTranslator._assert_language_token(tok, "<2ti>")

    message = str(exc.value)
    assert "<2ti>" in message
    assert "3 language tokens available" in message
    # It must say what IS accepted. `hm.download('ti')` failed to, and that is
    # most of why the wrong abbreviation survived six weeks.
    assert "<2am>" in message


def test_the_refusal_suggests_near_matches():
    tok = FakeTokenizer(["<2ti_Ethi>", "<2en>"])
    with pytest.raises(UnknownLanguageTokenError) as exc:
        MadladTranslator._assert_language_token(tok, "<2ti>")
    assert "<2ti_Ethi>" in str(exc.value)


def test_the_default_token_is_checked_against_a_vocabulary_not_asserted_here():
    """⚠️ A deliberately weak test, and the docstring is the point.

    `LANGUAGE_TOKEN` is an unverified guess — `huggingface.co` was unreachable
    when it was written. Asserting it equals `'<2ti>'` would only confirm that
    the constant equals itself, which is the shape of a check that cannot fail.
    The real verification is `_assert_language_token` running against the actual
    tokenizer, on a machine that can download one.
    """
    assert LANGUAGE_TOKEN.startswith("<2") and LANGUAGE_TOKEN.endswith(">")


# ------------------------------------------------------------- DEC-011

def test_the_model_is_not_nllb():
    """DEC-011: every NLLB variant is CC-BY-NC-4.0 and is never shipped.

    NLLB is behind essentially every published Tigrinya MT number, so it is the
    tempting default and the one this project may not use in a shipped artefact.
    """
    assert "nllb" not in MODEL.lower()
    assert MODEL == "google/madlad400-3b-mt"


# ------------------------------------------------------- segment alignment

def test_translate_all_passes_segments_through_in_order():
    seen = []

    def stub(batch):
        seen.append(list(batch))
        return [f"<{s}>" for s in batch]

    out = translate_all(["a", "b", "c", "d", "e"], stub, batch_size=2)
    assert out == ["<a>", "<b>", "<c>", "<d>", "<e>"]
    assert seen == [["a", "b"], ["c", "d"], ["e"]]


def test_a_dropped_segment_aborts_instead_of_misaligning():
    """The failure that would read as poor translation quality, not as a bug.

    chrF pairs by position, so one dropped segment shifts every later pair.
    """
    def drops(batch):
        return [f"<{s}>" for s in batch][:-1] or ["x"]

    with pytest.raises(SegmentCountError) as exc:
        translate_all(["a", "b", "c"], drops, batch_size=3)
    assert "misalign" in str(exc.value)


def test_an_extra_segment_also_aborts():
    with pytest.raises(SegmentCountError):
        translate_all(["a", "b"], lambda b: list(b) + ["extra"], batch_size=2)


def test_the_count_is_checked_per_batch_not_at_the_end():
    """Caught at the batch that dropped it, not after an hour of decoding."""
    calls = []

    def drops_on_second(batch):
        calls.append(list(batch))
        return list(batch) if len(calls) == 1 else list(batch)[:-1]

    with pytest.raises(SegmentCountError) as exc:
        translate_all(["a", "b", "c", "d", "e", "f"], drops_on_second,
                      batch_size=2)
    assert "index 2" in str(exc.value)
    assert len(calls) == 2, "should have stopped at the failing batch"


def test_progress_reports_against_the_true_total():
    seen = []
    translate_all(["a", "b", "c"], lambda b: list(b), batch_size=2,
                  progress=lambda done, total: seen.append((done, total)))
    assert seen == [(2, 3), (3, 3)]


# ------------------------------------------------ switching target language

class LoadedStub(MadladTranslator):
    """A translator whose model is already 'loaded', for the switch tests."""

    def __init__(self, tokens):
        super().__init__()
        self._fake = FakeTokenizer(tokens)

    @property
    def _loaded(self):
        return self._fake, None


def test_use_language_switches_without_reloading():
    t = LoadedStub(["<2ti>", "<2am>", "<2es>"])
    t.use_language("<2am>")
    assert t.language_token == "<2am>"


def test_use_language_still_validates():
    """⚠️ The gate lives in a cached_property, so a plain assignment skips it.

    That is the whole reason `use_language` exists rather than letting callers
    set the attribute: a typo'd control language would otherwise translate
    fluently into something else and be scored.
    """
    t = LoadedStub(["<2ti>", "<2am>"])
    with pytest.raises(UnknownLanguageTokenError):
        t.use_language("<2zz>")
    assert t.language_token == "<2ti>", "must not change on a rejected token"


def test_the_prompt_uses_the_current_token_not_the_one_loaded_with():
    """If the token were captured at load time, every control language would
    produce identical output and a diagnostic would report a false pipeline
    failure."""
    seen = []

    class Probe(LoadedStub):
        def __call__(self, segments):
            seen.append([f"{self.language_token} {s}" for s in segments])
            return list(segments)

    t = Probe(["<2ti>", "<2am>"])
    t(["hello"])
    t.use_language("<2am>")
    t(["hello"])
    assert seen == [["<2ti> hello"], ["<2am> hello"]]
