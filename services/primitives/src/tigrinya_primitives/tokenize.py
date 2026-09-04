"""Subword tokenization on raw Ge'ez.

Operates on **raw Ge'ez characters**, not on decomposed phonemes. That is the
opposite of what DEC-007 originally specified, and the change was forced by
measurement (DEC-007 amendment 2):

  - BPE trained on Epitran-decomposed text produced **worse** fertility than BPE
    on raw Ge'ez in **10 of 10** configurations and **5 of 5** folds
  - mean +0.190 tokens/word, about **8% worse**, at both char and byte level

The mechanism is that Ge'ez is *already* a compression scheme: each character
encodes a consonant+vowel pair, which is exactly the structure BPE would
otherwise have to learn. Decomposing throws that away, doubles sequence length
(1.957× measured), and spends the merge budget rebuilding syllables the script
supplied for free.

Round-trip fidelity is a requirement, not a nicety: DEC-022 obliges the API to
return surface forms verbatim, which is impossible if the tokenizer cannot
reconstruct its input. Verified at **100.00%** with zero `[UNK]` on corpus text.
"""

from __future__ import annotations

import pathlib
from dataclasses import dataclass

from tokenizers import Tokenizer, decoders, models, pre_tokenizers, trainers

DEFAULT_VOCAB_SIZE = 8000
UNK = "[UNK]"


@dataclass(frozen=True)
class Fertility:
    """Tokens per word — the tokenizer's cost metric.

    Reported alongside any tokenizer change, because fertility is what makes a
    tokenizer cheap or expensive downstream, and because it is the number that
    refuted DEC-007's original rationale.
    """

    tokens: int
    words: int

    @property
    def tokens_per_word(self) -> float:
        return self.tokens / self.words if self.words else 0.0


class GeezTokenizer:
    """A byte-level BPE tokenizer over raw Ge'ez text.

    Byte-level is chosen for guaranteed reversibility: no input can produce an
    `[UNK]`, so the surface form is always recoverable.
    """

    def __init__(self, tokenizer: Tokenizer) -> None:
        self._tok = tokenizer

    # ------------------------------------------------------------- lifecycle

    @classmethod
    def train(cls, texts, vocab_size: int = DEFAULT_VOCAB_SIZE,
              min_frequency: int = 2) -> "GeezTokenizer":
        """Train on an iterable of raw Ge'ez strings.

        `min_frequency=2` is the usual default, but note it saturates on small
        corpora — measured, a 792-word corpus capped the vocabulary at 542
        entries regardless of the requested size. Pass `min_frequency=1` when
        training on little data, and check the achieved vocabulary size.
        """
        tok = Tokenizer(models.BPE(unk_token=UNK))
        tok.pre_tokenizer = pre_tokenizers.ByteLevel(add_prefix_space=False)
        tok.decoder = decoders.ByteLevel()
        tok.train_from_iterator(
            texts,
            trainers.BpeTrainer(
                vocab_size=vocab_size,
                special_tokens=[UNK],
                min_frequency=min_frequency,
                show_progress=False,
                # REQUIRED for the round-trip guarantee, and easy to omit.
                # Without it the trainer only learns bytes it actually saw, so
                # unseen bytes become [UNK] and decode() cannot reconstruct the
                # input. Caught by test_tokenizer_round_trips_unseen_text: a
                # tokenizer trained on a small corpus mangled ordinary Tigrinya
                # it had not seen. "Byte-level means reversible" is only true
                # when the alphabet is complete.
                initial_alphabet=pre_tokenizers.ByteLevel.alphabet(),
            ),
        )
        return cls(tok)

    @classmethod
    def load(cls, path: str | pathlib.Path) -> "GeezTokenizer":
        return cls(Tokenizer.from_file(str(path)))

    def save(self, path: str | pathlib.Path) -> None:
        self._tok.save(str(path))

    # ------------------------------------------------------------ operations

    def encode(self, text: str) -> list[int]:
        return self._tok.encode(text).ids

    def tokens(self, text: str) -> list[str]:
        return self._tok.encode(text).tokens

    def decode(self, ids: list[int]) -> str:
        return self._tok.decode(ids)

    def round_trips(self, text: str) -> bool:
        """True if `decode(encode(text)) == text`.

        Exposed rather than merely tested, because a caller relying on the
        DEC-022 verbatim-surface guarantee may want to assert it directly.
        """
        return self.decode(self.encode(text)) == text

    @property
    def vocab_size(self) -> int:
        return self._tok.get_vocab_size()

    def fertility(self, texts) -> Fertility:
        """Measure tokens per whitespace-delimited word."""
        tokens = words = 0
        for t in texts:
            ws = t.split()
            if not ws:
                continue
            words += len(ws)
            tokens += len(self.tokens(t))
        return Fertility(tokens=tokens, words=words)
