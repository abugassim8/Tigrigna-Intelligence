"""Is the output projection actually loaded, and can it be recovered?

⚠️ **This lives in the package, not in `scripts/`, on purpose.** The measurement
runs through `MadladTranslator`, so a fix that only existed in a repair script
would leave the real run scoring noise while a separate command reported success.

The defect it guards against [verified 2026-09-16]
--------------------------------------------------
`T5ForConditionalGeneration` declares `lm_head.weight` tied to `shared.weight`
in **every** transformers from 4.35 to 5.17, as a **class attribute** — fixed
before any config is read, so it holds even when the config says the weights are
untied. MADLAD's `config.json` sets ``"tie_word_embeddings": false``, and the
same module gates initialisation on exactly that flag::

    if hasattr(module, "lm_head") and not self.config.tie_word_embeddings:
        init.normal_(module.lm_head.weight, mean=0.0, std=factor * 1.0)

A key in the tied mapping is suppressed from the missing-weights report, so a
**missing** `lm_head.weight` is randomly initialised and loads silently. Over a
working encoder that produces one arbitrary token repeated to `max_new_tokens`,
shifting with the input — which is exactly what this project measured before
finding the cause.

⚠️ Differing tensors are NOT the defect
---------------------------------------
With ``tie_word_embeddings: false`` the second stored matrix **is** the untied
output projection, so the two differing is the *correct* state. An earlier form
of this check had that backwards and would have fired on a healthy checkpoint.
"""

from __future__ import annotations

import glob
import math
import os
from typing import Mapping, Sequence

#: How far past the *expected* noise spread a matrix must sit before it counts
#: as trained. Multiplies `noise_spread_bound()` below.
#:
#: ⚠️ **This replaced a hard-coded 2.0, which was wrong.** The row-norm spread
#: of Gaussian noise depends on the dimension: about 1.2 in R^1024, but about
#: 5 in R^8. A fixed number was silently calibrated to one model's `d_model`
#: and misfired on anything else — caught when it called an obviously random
#: 50x8 plant matrix "trained". A threshold that only works for one shape is a
#: threshold that will be switched off the first time it is reused.
SPREAD_SAFETY = 2.0

#: The four 256000x1024 matrices HF's T5 expects. The checkpoint holds two.
EMBEDDING_KEYS = ("shared.weight", "encoder.embed_tokens.weight",
                  "decoder.embed_tokens.weight", "lm_head.weight")

INPUT_EMBEDDING_KEY = "shared.weight"


class RandomHeadError(RuntimeError):
    """`lm_head` is random and the checkpoint offers nothing to repair it with.

    ⚠️ Raised rather than warned. A random output projection still produces
    output with the right segment count, and `translate_all` will happily hand
    it to chrF, which will happily return a number. Scoring noise and recording
    it as a Tigrinya result is the failure this whole pipeline exists to avoid.
    """


class RepairFailedError(RuntimeError):
    """The repair ran and the weights did not change.

    ⚠️ The check that matters most. A repair that silently no-ops leaves a
    broken model behind a reassuring log line, which is worse than not trying.
    """


class AmbiguousProjectionError(RuntimeError):
    """More than one checkpoint tensor could be the output projection.

    Refusing is correct here. Picking one would be a guess, and a wrong guess
    produces fluent-looking output from the wrong matrix — invisible to every
    other check in this repository.
    """


# --------------------------------------------------------------------------
# The decisions. Pure: floats, bools and names, no torch, no model.
#
# ⚠️ Everything that *judges* lives here so it can be planted without an 11.8 GB
# download, exactly as `Translator` exists so the pipeline can be tested without
# one. The torch code below is a shell that measures and applies.
# --------------------------------------------------------------------------

def noise_spread_bound(rows: int, dim: int,
                       safety: float = SPREAD_SAFETY) -> float:
    """The largest row-norm spread a *randomly initialised* matrix should show.

    A row of `normal_(0, s)` in R^d has norm `s * chi_d`, which concentrates:
    mean about `s*sqrt(d - 0.5)`, standard deviation about `s/sqrt(2)`
    regardless of `d`. So the spread narrows as `d` grows — the `s` cancels,
    which is what makes this scale-free. Over `rows` draws the extremes reach
    roughly `z = sqrt(2 ln rows)` standard deviations either side.

    For the real matrix (256000 rows, d_model 1024) this gives about 2.5; for
    the 50x8 matrices the plants use, about 11. Both are far below what a
    trained embedding shows, because trained embeddings have rare and unused
    vocabulary rows near zero and noise never does.
    """
    if rows < 2 or dim < 1:
        raise ValueError(f"cannot bound a {rows}x{dim} matrix")
    mean = math.sqrt(max(dim - 0.5, 0.5))
    sigma = 1.0 / math.sqrt(2.0)
    z = math.sqrt(2.0 * math.log(rows))
    low = mean - z * sigma
    if low <= 0.0:
        # Too few dimensions for the norms to concentrate at all; no useful
        # bound exists, so refuse rather than return a meaningless one.
        raise ValueError(
            f"row norms do not concentrate in {dim} dimensions; the random/"
            f"trained distinction is not measurable here")
    return safety * (mean + z * sigma) / low


def spread(norms: Sequence[float]) -> float:
    """max/min over row norms. The shape statistic that separates the cases.

    Chosen over standard deviation because it is scale-free: it does not care
    what the matrix was multiplied by, only whether some rows are much smaller
    than others — which trained embeddings have and Gaussian noise does not.
    """
    if not len(norms):
        raise ValueError("no rows to measure")
    low = min(norms)
    if low <= 0.0:
        # A genuinely dead row. Trained matrices have these; noise never does.
        return float("inf")
    return float(max(norms)) / float(low)


def classify_head(head_spread: float, head_equals_input: bool,
                  checkpoint_has_separate_head: bool, bound: float,
                  ) -> tuple[str, str]:
    """Say what state `lm_head` is in, and why. Returns (verdict, reason).

    Verdicts: ``RANDOM``, ``TIED_WRONGLY``, ``TRAINED``. The first two are
    broken and repairable; the third is left alone.

    ⚠️ **`config.tie_word_embeddings` is deliberately not a parameter here, and
    this is the second time that lesson has been paid for.** An earlier version
    asked the config, and on the real model it answered `True` and returned
    "TRAINED -- nothing is wrong here" while the decoder was emitting
    `Sally Hansen Sally Hansen ...`. transformers 5.x overwrites the field:

        # configuration_t5.py, T5Config.__post_init__
        self.scale_decoder_outputs = kwargs.pop("tie_word_embeddings", None) is not False
        self.tie_word_embeddings = True

    It repurposes the flag as a decoder-scaling hint and forces tying on,
    assuming every T5-architecture checkpoint ties its embeddings. MADLAD does
    not. **A declared flag is not an outcome** -- the same error as trusting the
    dtype keyword and the `major >= 5` version gate.

    The evidence used instead is `checkpoint_has_separate_head`: whether the
    file stores its own `lm_head.weight`. A genuinely tied model does not store
    one, so a separate stored head means untied **by construction**, whatever
    any config says.

    ⚠️ The equality case is checked first and separately, because a head wrongly
    tied to the input embedding inherits a perfectly trained-looking row spread.
    Testing only for randomness would wave it straight through.
    """
    if head_equals_input and checkpoint_has_separate_head:
        return ("TIED_WRONGLY",
                "lm_head holds the same values as the input embedding, but the "
                "checkpoint stores more than one embedding-shaped matrix -- "
                "which a tied model has no reason to. The loader tied what this "
                "checkpoint keeps separate, so the trained output projection "
                "was loaded and then discarded, and the decoder is projecting "
                "through the INPUT embedding.")
    if head_equals_input:
        return ("TRAINED",
                "lm_head is tied to the input embedding, and the checkpoint "
                "stores a single embedding matrix, so tying is what this model "
                "wants.")
    if head_spread <= bound:
        return ("RANDOM",
                f"lm_head row norms are all within {head_spread:.3f}x of each "
                f"other (bound {bound:.3f} for this shape). Trained embeddings "
                f"have rare and unused rows and spread far wider than this; "
                f"Gaussian noise does not. This matrix was never loaded.")
    return ("TRAINED",
            f"lm_head row norms spread {head_spread:.1f}x, well past the "
            f"{bound:.3f} bound, and differ from the input embedding.")


def choose_output_projection(differs_from_input: Mapping[str, bool]) -> str:
    """Pick the checkpoint tensor that is the untied output projection.

    `differs_from_input` maps each embedding-shaped checkpoint key to whether
    its values differ from the model's loaded input embedding.

    ⚠️ Name-independent on purpose. The whole defect is that this tensor is
    reached under the wrong name, so trusting the name would reproduce the bug.
    MADLAD is untied, therefore exactly one stored matrix is the input
    embedding and exactly one is the output projection.
    """
    # ⚠️ The explicit name wins only when that tensor actually differs from the
    # loaded input embedding. Taking it unconditionally would, on a loader that
    # mapped the two the other way round, select a tensor identical to the
    # current head -- a repair that no-ops and then fails with a message about
    # aliasing that would send the reader somewhere else entirely.
    if differs_from_input.get("lm_head.weight"):
        return "lm_head.weight"

    candidates = sorted(k for k, differs in differs_from_input.items() if differs)
    if not candidates:
        raise RandomHeadError(
            "every embedding-shaped tensor in the checkpoint holds the same "
            "values as the input embedding, so the output projection is not in "
            "this file and cannot be recovered from it. Refusing to translate "
            "with a random head: the output would have the right segment count "
            "and a scoreable chrF, and would be noise.\n"
            f"  keys examined: {sorted(differs_from_input)}")
    if len(candidates) > 1:
        raise AmbiguousProjectionError(
            f"{len(candidates)} tensors differ from the input embedding and any "
            f"of them could be the output projection: {candidates}. Refusing to "
            f"guess — a wrong pick produces fluent output from the wrong matrix, "
            f"which no other check here would catch.")
    return candidates[0]


def locate_checkpoint(model_name: str) -> str:
    """Find the cached `model.safetensors` without downloading anything.

    ⚠️ `model_name` is required, with no default. Defaulting it to the
    package's `MODEL` would make this module import `translate`, which
    imports this one — and a caller that forgot the argument would silently
    inspect a different checkpoint than the one it loaded.
    """
    try:
        from huggingface_hub import try_to_load_from_cache
        path = try_to_load_from_cache(model_name, "model.safetensors")
        if isinstance(path, str) and os.path.exists(path):
            return path
    except Exception:                                     # noqa: BLE001
        pass

    stem = model_name.split("/")[-1].split("-")[0].lower()
    hits = [h for h in glob.glob(os.path.expanduser(
        "~/.cache/huggingface/hub/**/model.safetensors"), recursive=True)
        if stem in h.lower()]
    if not hits:
        raise FileNotFoundError(
            f"no cached model.safetensors for {model_name}. Nothing here ever "
            f"downloads; the cache is populated by the first real run.")
    return hits[0]


def row_norms(weight) -> list[float]:
    """Per-row L2 norms, in float32 so bfloat16 does not distort the ratio."""
    return weight.detach().float().norm(dim=1).tolist()


def checkpoint_stores_separate_projection(checkpoint: str,
                                          shape: tuple[int, int]) -> bool:
    """Does the file store more than one embedding-shaped matrix?

    ⚠️ **This, not the config, is what says whether the model is tied.** A tied
    model has one embedding matrix and nothing to store twice; `save_pretrained`
    drops the tied duplicates. Two or more distinct entries of the embedding
    shape therefore means the model is untied **by construction**, whatever any
    config says.

    `config.tie_word_embeddings` cannot be used: on transformers 5.x
    `T5Config.__post_init__` overwrites it to `True` unconditionally, which is
    exactly how a broken model came to be reported healthy.

    ⚠️ Counting, rather than looking for the name `lm_head.weight`, because the
    projection is not always stored under that name — this checkpoint stores
    `decoder.embed_tokens.weight` and `lm_head.weight` with no `shared.weight`
    at all, and a converter that wrote `shared.weight` plus a differently-valued
    `decoder.embed_tokens.weight` is equally untied. The name is the thing that
    cannot be trusted here.

    A naive converter could in principle store identical copies and be counted
    untied. That costs nothing: `choose_output_projection` then finds no tensor
    differing from the input embedding and refuses loudly rather than repairing.

    Reads only the safetensors header — no tensor data, no download.
    """
    from safetensors import safe_open

    with safe_open(checkpoint, framework="pt") as f:
        matching = [k for k in f.keys()
                    if tuple(f.get_slice(k).get_shape()) == tuple(shape)]
    return len(matching) >= 2


def inspect_head(model, checkpoint: str, *, quiet: bool = False) -> dict:
    """Measure the loaded model's head against the checkpoint. Changes nothing.

    `checkpoint` is required. Deciding without it means deciding from the
    config, which is the mistake this function exists to avoid.
    """
    import torch

    head = model.lm_head.weight
    shared = model.get_input_embeddings().weight
    # Recorded and printed, never consulted. See `classify_head`.
    tie = bool(getattr(model.config, "tie_word_embeddings", False))
    separate = checkpoint_stores_separate_projection(
        checkpoint, tuple(model.lm_head.weight.shape))

    head_spread = spread(row_norms(head))
    shared_spread = spread(row_norms(shared))
    same_object = head is shared
    same_values = same_object or bool(torch.equal(head.detach(), shared.detach()))

    rows, dim = tuple(head.shape)
    bound = noise_spread_bound(rows, dim)
    verdict, reason = classify_head(head_spread, same_values, separate, bound)

    if not quiet:
        print(f"  checkpoint stores 2+ embed : {separate}   "
              f"<- this decides it; a tied model stores one")
        print(f"  config tie_word_embeddings : {tie}   "
              f"<- recorded, NOT used: transformers 5.x forces it True")
        print(f"  lm_head is the same object : {same_object}")
        print(f"  lm_head == input embedding : {same_values}")
        print(f"  input embedding row spread : {shared_spread:.3f}x")
        print(f"  lm_head row spread         : {head_spread:.3f}x   "
              f"(<= {bound:.3f} means never loaded)")
        print(f"  VERDICT                    : {verdict}")
        print(f"    {reason}")

    return {"verdict": verdict, "reason": reason, "tie_word_embeddings": tie,
            "checkpoint_has_separate_head": separate,
            "head_spread": head_spread, "shared_spread": shared_spread,
            "head_equals_input": same_values, "bound": bound}


def repair_head(model, checkpoint: str, *, quiet: bool = False,
                found: dict | None = None) -> dict:
    """Bind the checkpoint's output projection to `lm_head`, if it is broken.

    Returns a record of what was found and what was done. ⚠️ Repairs nothing
    when the inspection says the head is trained — see the module docstring.

    `found` may be a previous `inspect_head` result, so a caller that already
    printed the inspection does not print the whole block a second time.
    """
    import torch
    from safetensors import safe_open

    if found is None:
        found = inspect_head(model, checkpoint, quiet=quiet)
    if found["verdict"] == "TRAINED":
        if not quiet:
            print("  REPAIR                     : SKIPPED — nothing is wrong here")
        return {**found, "repaired": False, "source_key": None}

    shape = tuple(model.lm_head.weight.shape)
    shared = model.get_input_embeddings().weight.detach()

    with safe_open(checkpoint, framework="pt") as f:
        keys = set(f.keys())
        present = [k for k in EMBEDDING_KEYS if k in keys]
        if not quiet:
            print(f"  checkpoint holds           : {present}")

        differs = {}
        for key in present:
            tensor = f.get_tensor(key)
            if tuple(tensor.shape) != shape:
                continue
            # ⚠️ **Compare in the model's dtype, not in float32.** The
            # checkpoint is float32 and the model loads as bfloat16, so
            # widening the stored tensor back to float32 compares it against a
            # value that has been through a lossy round-trip — and *every*
            # candidate then "differs", which raises AmbiguousProjectionError
            # on a perfectly healthy checkpoint. Rounding the stored tensor the
            # same way the loader did makes the comparison exact.
            differs[key] = not bool(
                torch.equal(tensor.to(shared.dtype).cpu(), shared.cpu()))

        source_key = choose_output_projection(differs)
        if not quiet:
            print(f"  output projection is       : {source_key!r}")
        projection = f.get_tensor(source_key)

    before = model.lm_head.weight.detach().clone()
    input_before = shared.clone()
    aliased = model.lm_head.weight is model.get_input_embeddings().weight

    if aliased:
        # ⚠️ **Rebind, never copy, when the head is aliased to the input
        # embedding.** In the TIED_WRONGLY case they are the *same Parameter*,
        # so `copy_` writes through and destroys the input embedding as well --
        # turning a broken decoder into a broken encoder *and* decoder, and
        # reporting success while doing it. Replacing the Parameter separates
        # them, which is what `tie_word_embeddings: false` asked for.
        model.lm_head.weight = torch.nn.Parameter(
            projection.to(before.dtype), requires_grad=False)
    else:
        with torch.no_grad():
            model.lm_head.weight.data.copy_(
                projection.to(model.lm_head.weight.dtype))

    # ⚠️ Prove the write landed. A repair that silently no-ops leaves a broken
    # model behind a reassuring log line, which is worse than not trying.
    if torch.equal(model.lm_head.weight.detach(), before):
        raise RepairFailedError(
            f"copied {source_key!r} into lm_head and the weights are unchanged. "
            f"The head is probably still aliased to the input embedding, so the "
            f"repair did not take. Refusing to report success.")
    del before

    # ⚠️ And prove it landed *only* there. Costs one clone of the embedding
    # (~0.5 GB at bfloat16) and is worth it: a repair that quietly rewrote the
    # input embedding would present as a model that got worse for no reason.
    if not torch.equal(model.get_input_embeddings().weight.detach(), input_before):
        raise RepairFailedError(
            "the repair altered the INPUT embedding as well as lm_head. They "
            "share storage, so the write went through both. Refusing to report "
            "success on a model that is now wrong in a second place.")
    del input_before

    if not quiet:
        after = spread(row_norms(model.lm_head.weight))
        print(f"  REPAIR                     : APPLIED — "
              f"row spread {found['head_spread']:.3f}x -> {after:.1f}x")

    return {**found, "repaired": True, "source_key": source_key}
