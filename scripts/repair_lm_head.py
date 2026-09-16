#!/usr/bin/env python3
"""Detect and repair a randomly-initialised `lm_head` on MADLAD-400.

What this is for
----------------
`google/madlad400-3b-mt` loads and runs, and the decoder emits **a single junk
token repeated to `max_new_tokens`** — and the junk *differs per input*. So the
encoder reads the text and the decoder emits noise. That is not a
mistranslation and not poor Tigrinya. It is a broken output projection.

The mechanism [verified 2026-09-16]
-----------------------------------
`T5ForConditionalGeneration` declares, in **every** transformers from 4.35 to
5.17 and unconditionally::

    # 4.35 - 4.57, a list
    _tied_weights_keys = ["encoder.embed_tokens.weight",
                          "decoder.embed_tokens.weight", "lm_head.weight"]
    # 5.x, a dict -- the "tied weights mapping" the load warning names
    _tied_weights_keys = {"lm_head.weight": "shared.weight", ...}

⚠️ That mapping is a **class attribute**. It is fixed before any config is read,
so it claims `lm_head.weight` is tied even when the config says it is not.
MADLAD's `config.json` sets ``"tie_word_embeddings": false``, and the same file
gates initialisation on exactly that flag::

    if hasattr(module, "lm_head") and not self.config.tie_word_embeddings:
        init.normal_(module.lm_head.weight, mean=0.0, std=factor * 1.0)

So `lm_head` is freshly randomised — and because its key is in the tied
mapping, a **missing** `lm_head.weight` is suppressed from the missing-weights
warning. It loads silently, and a random projection over a working encoder
gives logits dominated by one arbitrary vocabulary row: one token, repeated,
shifting with the input because the encoder state still varies.

⚠️ Two of the four matrices, not four
-------------------------------------
The Hub reports **2940.4M** parameters for this checkpoint. For this config the
non-embedding parameters are 2,416,086,016 and one 256000x1024 matrix is
262,144,000, so 2940.4M fits **two** such matrices exactly and fits no other
count (three would be 3202.5M, four 3464.7M). HF wants four. At least one is
being invented at load time.

⚠️ Why "the tensors differ" is NOT evidence of a bad checkpoint
--------------------------------------------------------------
With ``tie_word_embeddings: false`` the second matrix **is** the untied output
projection, so the two differing is the *correct* state. An earlier version of
this investigation had that backwards and would have fired on a healthy file,
sending the owner after a second 11.8 GB download. ``jbochi/madlad400-3b-mt``
is byte-identical to ``google/`` — all 13 files, same sizes, same config — so
that download never had anything to offer.

What this script does, and what it refuses to do
------------------------------------------------
⚠️ **It repairs only when the loaded weights say repair is needed**, decided
from the weights themselves and never from a version number. An unconditional
overwrite would silently corrupt a correctly-loaded model on some future
transformers, which is the exact class of invisible breakage this repository
keeps finding.

Usage:
    python3 scripts/repair_lm_head.py                 # diagnose, repair, prove
    python3 scripts/repair_lm_head.py --dry-run       # diagnose only
    python3 scripts/repair_lm_head.py --self-test     # no model, no network
"""

from __future__ import annotations

import argparse
import os
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "services" / "evaluation" / "src"))
sys.path.insert(0, str(REPO / "services" / "translation" / "src"))

# ⚠️ The logic lives in the package, not here. The measurement runs through
# `MadladTranslator`, so a fix that existed only in this script would leave
# the real run scoring noise while this command reported success.
from tigrinya_translate.head import (          # noqa: E402
    EMBEDDING_KEYS,
    SPREAD_SAFETY,
    AmbiguousProjectionError,
    RandomHeadError,
    RepairFailedError,
    choose_output_projection,
    classify_head,
    noise_spread_bound,
    locate_checkpoint,
    row_norms,
    spread,
    checkpoint_stores_separate_projection,
    read_safetensors_header,
    inspect_head as inspect,
    repair_head as repair,
)

MODEL = "google/madlad400-3b-mt"
PROMPT = "Wash your hands often."

#: ⚠️ Controls first, Tigrinya last, and the order matters for reading the
#: result. Without a control, "the output is not Tigrinya" cannot be told apart
#: from "this model's Tigrinya is poor", and those need opposite responses.
#: `<2am>` is the sharp one: same Ge'ez script, far more training data.
LANGUAGES = ("<2es>", "<2de>", "<2am>", "<2ti>")

# --------------------------------------------------------------------------
# The shell. Measures, applies, and proves. Needs torch and the checkpoint.
# --------------------------------------------------------------------------

def translate_samples(model, tokenizer, languages=LANGUAGES,
                      prompt: str = PROMPT, *, quiet: bool = False) -> dict:
    """Translate one sentence into each language. `ascii()` for paste safety."""
    import torch

    out = {}
    for lang in languages:
        ids = tokenizer(f"{lang} {prompt}", return_tensors="pt")
        with torch.inference_mode():
            generated = model.generate(**ids, max_new_tokens=32, num_beams=1,
                                       do_sample=False)
        text = tokenizer.batch_decode(generated, skip_special_tokens=True)[0]
        out[lang] = text
        if not quiet:
            print(f"  {lang:8} -> {ascii(text)}")
    return out


def load(model_name: str, dtype: str):
    """Load tokenizer and model, verifying the dtype actually applied."""
    import torch
    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

    precision = getattr(torch, dtype)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    try:
        model = AutoModelForSeq2SeqLM.from_pretrained(
            model_name, low_cpu_mem_usage=True, dtype=precision)
    except TypeError:
        model = AutoModelForSeq2SeqLM.from_pretrained(
            model_name, low_cpu_mem_usage=True, torch_dtype=precision)

    actual = next(model.parameters()).dtype
    if actual != precision:
        raise RuntimeError(
            f"asked for {precision} and the model loaded as {actual}; the dtype "
            f"keyword was accepted and ignored, which multiplies memory by "
            f"{actual.itemsize // precision.itemsize}x.")
    model.eval()
    return tokenizer, model


def main(argv: list[str] | None = None) -> int:
    # ⚠️ At the top of the entry *function*, not under `if __name__`. `main()`
    # is called by import from the plants, and a `__main__` guard does not run
    # then -- the bug that failed five plants on Windows and passed on Linux.
    from tigrinya_eval.primitives import force_utf8_stdio, is_ethiopic
    force_utf8_stdio()

    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--model", default=MODEL, help="checkpoint to inspect")
    ap.add_argument("--dtype", default="bfloat16",
                    help="bfloat16 (~6 GB) or float32 (~12 GB, will thrash 16 GB)")
    ap.add_argument("--dry-run", action="store_true",
                    help="report the verdict and change nothing")
    ap.add_argument("--self-test", action="store_true",
                    help="exercise the decisions with no model and no network")
    args = ap.parse_args(argv)

    if args.self_test:
        return _self_test()

    print("=" * 74)
    print("lm_head repair — is the output projection actually loaded?")
    print("=" * 74)

    try:
        checkpoint = locate_checkpoint(args.model)
    except FileNotFoundError as exc:
        # ⚠️ A traceback here would be the wrong answer to an ordinary
        # situation: the cache is simply empty. Say what to do instead.
        print(f"  {exc}")
        print(f"  Nothing was changed. Run the measurement once first:")
        print(f"    python3 scripts/translate_tico19.py --smoke")
        return 1
    print(f"  checkpoint  {checkpoint}")
    print(f"  size        {os.path.getsize(checkpoint):,} bytes")

    # ⚠️ Printed unconditionally, including when nothing turns out to be wrong.
    # This is the one fact that says how many of the four matrices HF's T5
    # expects are actually in the file, and a run that repairs nothing is
    # exactly when it is most needed to explain why.
    # ⚠️ The header, not the file. `safe_open` here mapped all 11.76 GB to
    # print 92 KB of names — headroom a 16 GB Windows box does not have, and a
    # run died on the commit limit with `os error 1455`.
    header = read_safetensors_header(checkpoint)
    interesting = sorted(k for k in header if "embed_tokens" in k
                         or k.startswith(("shared", "lm_head")))
    print(f"  tensors     {len(header)} total, of which "
          f"{len(interesting)} embedding-shaped:")
    for k in interesting:
        print(f"                {k:34} {tuple(header[k]['shape'])} "
              f"{header[k]['dtype']}")

    print(f"  loading {args.model} as {args.dtype} ...", flush=True)
    tokenizer, model = load(args.model, args.dtype)
    print()

    found = inspect(model, checkpoint)
    if args.dry_run:
        return 0

    if found["verdict"] != "TRAINED":
        print()
        print("  BEFORE the repair:")
        translate_samples(model, tokenizer)
        print()

    record = repair(model, checkpoint, found=found)
    print()
    print("  AFTER:" if record["repaired"] else "  Output:")
    produced = translate_samples(model, tokenizer)

    # ⚠️ The pass condition was written into the plan before any of this output
    # existed. Controls first: if Spanish and German are fluent and Tigrinya is
    # not, the repair worked and the finding is about Tigrinya coverage -- which
    # is the measurement this project exists to make, not a bug.
    geez = any(is_ethiopic(ch) for ch in produced.get("<2ti>", ""))
    print()
    print("-" * 74)
    print(f"  <2ti> returned Ge'ez script : {geez}")
    if record["repaired"]:
        print(f"  repaired from               : {record['source_key']!r}")
        print("  Read the controls first. Fluent Spanish and German mean the")
        print("  repair took; Tigrinya quality is then a finding, not a bug.")
    else:
        print("  Nothing was repaired: the checkpoint stores no separate")
        print("  lm_head.weight, so tying is what this model wants. Junk output")
        print("  therefore has some other cause -- the tokenizer is the next thread.")
    return 0


def _self_test() -> int:
    """Exercise every decision with no torch, no model and no network.

    ⚠️ The decisions are all here *because* of this. A check that needs an
    11.8 GB download to run is a check that stops being run, and the one thing
    this script must never do is silently overwrite a good matrix.
    """
    import math
    import random

    # `spread` itself.
    assert spread([32.0, 32.0, 32.0]) == 1.0
    assert spread([1.0, 4.0]) == 4.0
    assert spread([0.0, 5.0]) == float("inf"), "a dead row must read as trained"
    try:
        spread([])
    except ValueError:
        pass
    else:                                                 # pragma: no cover
        raise AssertionError("an empty matrix must not be judged")

    # The bound, against the distribution it models — at BOTH the real shape
    # and the plants' shape, because a fixed threshold that only worked at one
    # `d_model` is exactly the bug this replaced.
    real_bound = noise_spread_bound(256_000, 1024)
    tiny_bound = noise_spread_bound(50, 8)
    assert tiny_bound > real_bound * 2, (
        f"the bound must widen as dimension falls ({tiny_bound:.2f} at 8 dims "
        f"vs {real_bound:.2f} at 1024); if it does not, it is a magic number")
    try:
        noise_spread_bound(50, 1)
    except ValueError:
        pass
    else:                                                 # pragma: no cover
        raise AssertionError("a shape with no concentration must be refused")

    rng = random.Random(20260916)

    # ⚠️ Real vectors, not sampled norms, at the plants' shape. Sampling norms
    # from the same model the bound is derived from would test the formula
    # against itself and pass no matter what either of them said.
    tiny = [math.sqrt(sum(rng.gauss(0.0, 1.0) ** 2 for _ in range(8)))
            for _ in range(50)]
    tiny_spread = spread(tiny)
    assert tiny_spread < tiny_bound, (
        f"50 real Gaussian rows in 8 dimensions spread {tiny_spread:.2f}x, at "
        f"or above the {tiny_bound:.2f} bound — random heads would be missed")

    # At the real shape, 256,000 rows x 1024 dims is too slow to build honestly
    # in pure Python, so the norms are drawn from their limiting distribution.
    noise = [rng.gauss(32.0, 0.707) for _ in range(20_000)]
    noise_spread = spread(noise)
    assert noise_spread < real_bound, (
        f"Gaussian rows spread {noise_spread:.3f}x, at or above the "
        f"{real_bound:.3f} bound — the bound would miss a random head")

    # A trained matrix: most rows ordinary, some rare tokens near zero.
    #
    # ⚠️ Drawn lognormal, not Gaussian. A row *norm* cannot be negative, and a
    # Gaussian fixture wide enough to be interesting produces negative draws --
    # which `spread` correctly reports as `inf`, so the assertion below passed
    # on a number that meant nothing. A check that cannot fail is worse than no
    # check, so the fixture is now shaped like the thing it stands in for.
    trained = [rng.lognormvariate(0.0, 0.45) for _ in range(19_900)] + \
              [rng.uniform(0.001, 0.01) for _ in range(100)]
    assert min(trained) > 0.0, "row norms are non-negative; fix the fixture"
    trained_spread = spread(trained)
    assert trained_spread != float("inf"), (
        "the trained fixture must give a finite spread, or this assertion "
        "passes without testing the bound")
    assert trained_spread > real_bound, (
        f"a trained matrix spread only {trained_spread:.3f}x — the bound "
        f"would repair a matrix that was fine")

    # The verdicts. Third argument is "the checkpoint stores its own
    # lm_head.weight" -- NOT config.tie_word_embeddings, which transformers 5.x
    # overwrites to True and which reported a broken model healthy.
    assert classify_head(noise_spread, False, False, real_bound)[0] == "RANDOM"
    assert classify_head(trained_spread, False, False, real_bound)[0] == "TRAINED"
    # ⚠️ A head wrongly tied to the input inherits a trained-looking spread, so
    # testing only for randomness would wave it through.
    assert classify_head(trained_spread, True, True, real_bound)[0] == "TIED_WRONGLY"
    assert classify_head(trained_spread, True, False, real_bound)[0] == "TRAINED", \
        "a genuinely tied checkpoint must not be 'repaired'"

    # ⚠️ The explicit key must not win when it matches the input embedding:
    # choosing it would no-op and then fail with a message about aliasing.
    assert choose_output_projection(
        {"lm_head.weight": False,
         "decoder.embed_tokens.weight": True}) == "decoder.embed_tokens.weight"

    # Choosing the projection.
    assert choose_output_projection(
        {"shared.weight": False, "lm_head.weight": True}) == "lm_head.weight"
    assert choose_output_projection(
        {"shared.weight": False,
         "decoder.embed_tokens.weight": True}) == "decoder.embed_tokens.weight"
    try:
        choose_output_projection({"shared.weight": False,
                                  "encoder.embed_tokens.weight": False})
    except RandomHeadError:
        pass
    else:                                                 # pragma: no cover
        raise AssertionError("a checkpoint with no projection must be refused")
    try:
        choose_output_projection({"shared.weight": False,
                                  "encoder.embed_tokens.weight": True,
                                  "decoder.embed_tokens.weight": True})
    except AmbiguousProjectionError:
        pass
    else:                                                 # pragma: no cover
        raise AssertionError("two candidates must be refused, never guessed")

    print(f"self-test passed: noise spreads {noise_spread:.3f}x at 1024 dims "
          f"(bound {real_bound:.3f}) and {tiny_spread:.2f}x at 8 "
          f"(bound {tiny_bound:.2f}); trained {trained_spread:.0f}x")
    print("  a wrongly-tied head is caught, and an ambiguous checkpoint refused")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())       # main() calls force_utf8_stdio() itself
