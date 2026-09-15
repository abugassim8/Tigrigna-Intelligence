"""English → Tigrinya translation, behind an interface testable without a model.

Why this package exists at all
------------------------------
**No model had ever been loaded in this project.** Six weeks of decisions,
eleven experiments and a measurement harness were built around scoring a
translation system, and none had ever scored one. This is the package that
closes that.

Licensing is not a detail here
------------------------------
⚠️ **DEC-011 quarantines every NLLB variant.** They are CC-BY-NC-4.0, and the
decision is explicit that NC-licensed models are *"never present in a shipped
artefact"*. NLLB is the model behind essentially every published Tigrinya MT
number, so it is tempting and it is disqualified — on licensing, not on merit.

The baseline is **`google/madlad400-3b-mt`, Apache-2.0**, which DEC-011 chose
while recording that its *"Tigrinya quality is unmeasured"*. Measuring it is the
point of the pipeline in `scripts/translate_tico19.py`.

The injection idiom, and why
----------------------------
`Translator` is a callable taking a list of English segments and returning the
same number of Tigrinya ones. `MadladTranslator` is one implementation; tests
and plants inject stubs.

This mirrors `tigrinya_primitives.morphology.Analyser` exactly, and for the same
reason: the heavy dependency must not be required to test the code around it. A
test suite that cannot run without a 12 GB download is a test suite that stops
being run.
"""

from __future__ import annotations

from .translate import (
    LANGUAGE_TOKEN,
    MODEL,
    SegmentCountError,
    Translator,
    UnknownLanguageTokenError,
    translate_all,
)

__all__ = [
    "LANGUAGE_TOKEN",
    "MODEL",
    "SegmentCountError",
    "Translator",
    "UnknownLanguageTokenError",
    "translate_all",
]
