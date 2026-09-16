"""The `Translator` interface, and the MADLAD implementation of it.

Read `UnknownLanguageTokenError` before anything else in this file. It is the
only part that encodes a lesson rather than a mechanism.
"""

from __future__ import annotations

import functools
from typing import Callable, Sequence

#: DEC-011. Apache-2.0, covers `ti`, and its Tigrinya quality is unmeasured —
#: which is the gap `scripts/translate_tico19.py` exists to close.
#:
#: ⚠️ Not NLLB. Every NLLB variant is CC-BY-NC-4.0 and is quarantined to
#: research and comparison use, never shipped. Swapping this constant for an
#: NLLB checkpoint would breach DEC-011 silently, so do not.
MODEL = "google/madlad400-3b-mt"

#: MADLAD selects the target language with a prefix token on the source text.
#:
#: ✅ **Verified 2026-09-15** against `tokenizer.json` on the Hub: language
#: tokens are ordinary Unigram vocab pieces from index 4, sorted alphabetically,
#: and `"<2ti>"` sits between `<2tet>` and `<2tiv>`. `ti` is also in the model
#: card's language list. It was an unchecked guess when written; it is not now.
#:
#: ⚠️ **The check below stays anyway, and deleting it would be the mistake.**
#: The value is verified for *this checkpoint*. It costs nothing and it guards
#: a different checkpoint, a different model, or a careless edit — and the
#: failure it prevents is silent: an unknown prefix does not raise, it becomes
#: ordinary text, and the model emits fluent output in some other language with
#: the right segment count and a perfectly scoreable chrF.
#:
#: ⚠️ It also nearly failed the *other* way. `tokenizer_config.json` has
#: `"additional_special_tokens": []` and `tokenizer.json` has
#: `"added_tokens": []`. Had the `<2xx>` prefixes been split into subwords
#: rather than being real vocab entries, `get_vocab()` would not contain
#: `"<2ti>"` and this gate would have **rejected a valid token and blocked the
#: run** — a check firing on correct input, which is how checks get switched
#: off. They are real pieces, so it does not.
LANGUAGE_TOKEN = "<2ti>"

#: A callable taking English segments and returning the same number of Tigrinya
#: ones. Injecting one is how this package is tested without a 12 GB download,
#: exactly as `morphology.Analyser` is (DEC-028).
Translator = Callable[[list[str]], list[str]]


class UnknownLanguageTokenError(RuntimeError):
    """The target-language token is not in the model's vocabulary.

    ⚠️ **This must raise rather than warn**, and the reason is specific.

    An unrecognised prefix does not stop a translation model. The token is
    split into subwords, treated as part of the sentence, and the model emits
    *some* language — frequently the most common one in its training data. The
    output is fluent, the pipeline completes, chrF computes, and the artefact
    records a number for a language nobody asked for.

    That failure is invisible to every check in this repository: the output has
    the right shape, the right segment count, and a plausible score. Only a
    Tigrinya reader would catch it, and the whole point of the measurement is
    to spend their attention on the answer rather than on whether the
    experiment was run correctly.
    """


class DtypeIgnoredError(RuntimeError):
    """The model did not load in the precision that was asked for.

    ⚠️ Silent, and expensive. `from_pretrained` forwards unrecognised keywords
    to the config instead of raising, so a renamed dtype argument is *accepted
    and ignored* -- and the model loads in float32. On the 16 GB machine this
    targets that is 11.8 GB resident instead of 6, which presents as a very
    slow run rather than as a bug.
    """


class SegmentCountError(RuntimeError):
    """A translator returned a different number of segments than it was given.

    ⚠️ Also fatal, and for a related reason. chrF pairs hypotheses with
    references **by position**. One dropped or merged segment shifts every
    subsequent pair by one, and the result is a low score that looks like poor
    translation quality rather than like a bug.
    """


def translate_all(segments: Sequence[str], translator: Translator,
                  batch_size: int = 8,
                  progress: Callable[[int, int], None] | None = None,
                  checkpoint: Callable[[list[str]], None] | None = None,
                  ) -> list[str]:
    """Translate `segments` in batches, checking alignment as it goes.

    The count is checked **per batch, not once at the end**, so a translator
    that drops a segment is caught at the batch that dropped it rather than
    after an hour of CPU decoding.

    `checkpoint` receives everything translated so far, after each batch is
    validated. ⚠️ It is called **after** the count check, never before: a batch
    that failed alignment must not reach disk, or a resumed run would rebuild
    itself from corrupt state.
    """
    segments = list(segments)
    out: list[str] = []

    for start in range(0, len(segments), batch_size):
        batch = segments[start:start + batch_size]
        got = list(translator(batch))
        if len(got) != len(batch):
            raise SegmentCountError(
                f"translator returned {len(got)} segment(s) for {len(batch)} "
                f"input(s) in the batch starting at index {start}. chrF pairs "
                f"hypotheses with references by position, so continuing would "
                f"misalign every later segment and report the result as poor "
                f"translation quality rather than as a bug."
            )
        out.extend(got)
        if checkpoint is not None:
            checkpoint(out)
        if progress is not None:
            progress(len(out), len(segments))

    return out


class MadladTranslator:
    """`google/madlad400-3b-mt` behind the `Translator` interface.

    ⚠️ **This class has never been executed.** It was written in an environment
    with no access to `huggingface.co`, so every line below the import is
    unverified against the real model. The first run on a machine that can
    download it is the first test it has ever had — which is why the
    language-token check is loud and comes first.

    `LANGUAGE_TOKEN` itself **is** now verified (2026-09-15, against the Hub's
    `tokenizer.json`). The `generate` call below is not, and the two should not
    be confused: knowing the right prefix says nothing about whether the
    decoding arguments are right.

    CPU notes, for the 16 GB machine this was written for:

      - `bfloat16` is about 6 GB resident; float32 is about 12 GB and will
        thrash a 16 GB box into swap.
      - Decoding is **greedy** (`num_beams=1`, `do_sample=False`) so that a
        re-run reproduces. Beam search would score better and would make the
        artefact non-reproducible, which DEC-016 treats as the worse trade.
      - Expect tens of minutes for 100 segments. It is a batch job.
    """

    def __init__(self, model_name: str = MODEL,
                 language_token: str = LANGUAGE_TOKEN,
                 max_new_tokens: int = 256,
                 dtype: str = "bfloat16") -> None:
        self.model_name = model_name
        self.language_token = language_token
        self.max_new_tokens = max_new_tokens
        self.dtype = dtype

    @functools.cached_property
    def _loaded(self):
        import torch
        from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

        tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self._assert_language_token(tokenizer, self.language_token)

        # ⚠️ **Verify the outcome; never guess the keyword.**
        #
        # Two bugs came from guessing. First `try: dtype= except TypeError:` --
        # the TypeError never fires, because `from_pretrained` forwards unknown
        # keywords to the *config* rather than raising. Then a version gate on
        # `major >= 5` -- also wrong, because the rename landed in 4.56, not
        # 5.0. Both would have loaded float32 silently: 11.8 GB resident
        # instead of 6, enough to thrash a 16 GB machine, and looking like a
        # slow run rather than a bug.
        #
        # Asking the loaded model what dtype it actually is cannot be wrong.
        precision = getattr(torch, self.dtype)
        try:
            model = AutoModelForSeq2SeqLM.from_pretrained(
                self.model_name, low_cpu_mem_usage=True, dtype=precision)
        except TypeError:
            model = AutoModelForSeq2SeqLM.from_pretrained(
                self.model_name, low_cpu_mem_usage=True, torch_dtype=precision)

        actual = next(model.parameters()).dtype
        if actual != precision:
            raise DtypeIgnoredError(
                f"asked for {precision} but the model loaded as {actual}. The "
                f"dtype keyword was accepted and ignored, which silently "
                f"multiplies memory by {actual.itemsize // precision.itemsize}x "
                f"-- about {3.0 * actual.itemsize:.0f} GB for this model. "
                f"transformers {__import__('transformers').__version__} may use "
                f"a different keyword than either tried here."
            )

        model.eval()
        return tokenizer, model

    @staticmethod
    def _assert_language_token(tokenizer, token: str) -> None:
        """Refuse to translate into a language the model cannot be told to use.

        Checked against **the tokenizer's own vocabulary**, never against a
        list written here. A check comparing our constant to our constant would
        pass whatever either of them said — the mistake that let
        `hm.download('ti')` survive six weeks in an error message.
        """
        vocab = tokenizer.get_vocab()
        if token in vocab:
            return

        available = sorted(t for t in vocab if t.startswith("<2") and t.endswith(">"))

        # ⚠️ Always name what IS accepted, never only what is not.
        #
        # "HornMorpho doesn't know of any language abbreviated ti" named neither
        # the accepted form nor where to find it, and that is most of why the
        # wrong abbreviation sat in this repository's error messages for six
        # weeks (A-20). A message that reports only a count repeats the defect.
        #
        # MADLAD carries ~400 language tokens, so the full list is noise: show
        # near matches first, then enough of the rest to be orienting, and say
        # exactly how to see all of them.
        stem = token[2:-1] if token.startswith("<2") and token.endswith(">") else token
        near = [t for t in available if stem[:2] and stem[:2] in t]
        shown = near or available
        listing = ", ".join(shown[:12])
        more = len(shown) - len(shown[:12])
        if more > 0:
            listing += f", … and {more} more"

        raise UnknownLanguageTokenError(
            f"{token!r} is not in {getattr(tokenizer, 'name_or_path', 'the model')}'s "
            f"vocabulary, so the model was never told to emit Tigrinya. It would "
            f"treat the token as ordinary text and translate into some other "
            f"language — fluently, with the right segment count and a plausible "
            f"chrF. Refusing.\n"
            f"  {'Closest by prefix' if near else 'Accepted'}: {listing}\n"
            f"  {len(available)} language tokens available; list them with "
            f"`sorted(t for t in tokenizer.get_vocab() if t.startswith('<2'))`, "
            f"then set tigrinya_translate.LANGUAGE_TOKEN to the correct one."
        )

    def use_language(self, token: str) -> None:
        """Switch target language on an already-loaded model, keeping the gate.

        ⚠️ The gate lives in `_loaded`, which is a `cached_property`. Assigning
        `self.language_token = "<2xx>"` directly would therefore **bypass the
        validation entirely** — the one check standing between a typo and a
        fluent, scoreable translation into the wrong language.

        Swapping the token is worth supporting: comparing `<2ti>` against a
        control language is how a pipeline defect is told apart from a finding
        about Tigrinya, and reloading 11.8 GB per language to do it is absurd.
        So the switch is a method that re-validates, not an attribute anyone
        should set.
        """
        tokenizer, _ = self._loaded
        self._assert_language_token(tokenizer, token)
        self.language_token = token

    def __call__(self, segments: list[str]) -> list[str]:
        import torch

        tokenizer, model = self._loaded
        prompts = [f"{self.language_token} {s}" for s in segments]
        batch = tokenizer(prompts, return_tensors="pt", padding=True,
                          truncation=True, max_length=512)

        with torch.inference_mode():
            generated = model.generate(
                **batch,
                max_new_tokens=self.max_new_tokens,
                num_beams=1,
                do_sample=False,
            )

        return tokenizer.batch_decode(generated, skip_special_tokens=True)
