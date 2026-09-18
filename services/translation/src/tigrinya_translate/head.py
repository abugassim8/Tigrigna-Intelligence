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
import pathlib
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


#: Names a checkpoint may store the input embedding under. Exactly one of them
#: should be present alongside `lm_head.weight`.
INPUT_EMBEDDING_KEYS = ("shared.weight", "decoder.embed_tokens.weight",
                        "encoder.embed_tokens.weight")

OUTPUT_PROJECTION_KEY = "lm_head.weight"


def identify_matrices(names: Sequence[str]) -> tuple[str, str]:
    """`(input embedding key, output projection key)`, read from the names.

    ⚠️ **The names in the file are authoritative. The loaded model is not.**
    An earlier version inferred the roles by asking which stored tensor
    *differed from the model's input embedding* — valid only if the input
    embedding loaded correctly, and on this checkpoint it does not.

    Measured 2026-09-18 on `google/madlad400-3b-mt`: the file stores
    `decoder.embed_tokens.weight` and `lm_head.weight` and **no
    `shared.weight`**, and transformers loads **`lm_head.weight` into
    `shared.weight`** — so the encoder embeds its input with the output
    projection. The old inference therefore concluded that the *input
    embedding* was the output projection, bound it to `lm_head`, and reported
    `REPAIR: APPLIED` on a model it had just made wrong in a second place.

    So the file says which is which, and this trusts it: `lm_head.weight` is
    the output projection because that is what it is called.
    """
    present = set(names)
    if OUTPUT_PROJECTION_KEY not in present:
        raise RandomHeadError(
            f"the checkpoint stores no {OUTPUT_PROJECTION_KEY!r}, so the output "
            f"projection is not in this file and cannot be recovered from it. "
            f"Refusing to translate with a head that was never loaded: the "
            f"output would have the right segment count and a scoreable chrF, "
            f"and would be noise.\n"
            f"  embedding-shaped keys present: {sorted(present)}")

    inputs = [k for k in INPUT_EMBEDDING_KEYS if k in present]
    if not inputs:
        raise AmbiguousProjectionError(
            f"the checkpoint stores {OUTPUT_PROJECTION_KEY!r} but nothing "
            f"recognisable as an input embedding "
            f"({', '.join(INPUT_EMBEDDING_KEYS)}). Refusing to guess which of "
            f"{sorted(present)} the encoder should use.")
    if len(inputs) > 1:
        raise AmbiguousProjectionError(
            f"{len(inputs)} tensors could be the input embedding: {inputs}. "
            f"Refusing to guess — picking wrong produces fluent output from the "
            f"wrong matrix, which no other check here would catch.")
    return inputs[0], OUTPUT_PROJECTION_KEY


def degenerate_ratio(text: str) -> float:
    """Distinct characters over total, ignoring whitespace. Lower is worse.

    ⚠️ **The check that would have caught every failure this project has had.**
    A broken projection does not produce bad translation, it produces one token
    repeated: `Sally Hansen` nine times, `ᛉ` thirty-two times, Syriac `ܠܹܗ` to
    the token limit. Every one of those scores 0.03–0.08 here; real Spanish and
    real Tigrinya score 0.5–0.8. Nothing else in this repository noticed,
    because degenerate output has the right segment count and a real chrF.
    """
    packed = "".join(text.split())
    if not packed:
        return 0.0
    return len(set(packed)) / len(packed)


#: Below this, output is a repeated token rather than a translation. Measured
#: against every real failure seen here (0.031–0.085) and real text
#: (0.536–0.786), so it sits in an empty gap two octaves wide.
DEGENERATE_BELOW = 0.15

#: Shorter than this, the ratio is meaningless — "ሰላም" is 4 distinct of 4.
DEGENERATE_MIN_CHARS = 20


def looks_degenerate(text: str) -> bool:
    """Is this a repeated token rather than a translation?"""
    packed = "".join(text.split())
    if len(packed) < DEGENERATE_MIN_CHARS:
        return False
    return degenerate_ratio(text) < DEGENERATE_BELOW



def locate_checkpoint(model_name: str) -> str:
    """Resolve a local directory, a local file, or a Hub id to a weights file.

    ⚠️ `model_name` is required, with no default. Defaulting it to the
    package's `MODEL` would make this module import `translate`, which
    imports this one — and a caller that forgot the argument would silently
    inspect a different checkpoint than the one it loaded.

    ⚠️ **Local paths are checked first, and used to be not checked at all.**
    `scripts/shrink_checkpoint.py` writes a converted model into a directory and
    then prints the command to run against it — and that command failed, because
    this function only ever searched the Hugging Face cache. `from_pretrained`
    accepts local paths, so the lookup was the only thing that did not.

    That is the defect `scripts/check_commands.py` exists to prevent: a command
    printed at the moment it is needed that does not work. The checker reads
    flags statically, so `--model` being declared was enough for it to pass; it
    cannot know an argument *value* is unsupported. `shrink_checkpoint.py` now
    resolves the path itself before printing the instruction.
    """
    candidate = pathlib.Path(os.path.expanduser(model_name))

    if candidate.is_dir():
        weights = candidate / "model.safetensors"
        if weights.is_file():
            return str(weights)
        raise FileNotFoundError(
            f"{candidate} is a directory but holds no model.safetensors. "
            f"Sharded checkpoints are not supported here; point at a directory "
            f"written by scripts/shrink_checkpoint.py, or at a Hub model id.")

    if candidate.suffix == ".safetensors":
        if candidate.is_file():
            return str(candidate)
        raise FileNotFoundError(f"{candidate} does not exist.")

    # ⚠️ A path-looking argument must not fall through to the cache search.
    # `--model models/typo-here` would otherwise resolve to whatever MADLAD
    # copy the glob found first, and report success against a different model.
    #
    # ⚠️ **But a Hub id contains a slash too.** The first version of this tested
    # for `os.sep` or `os.altsep` anywhere in the string, which rejected
    # `google/madlad400-3b-mt` -- the default model -- on every platform, since
    # `/` is `os.sep` on POSIX and `os.altsep` on Windows. `check_environment.py`
    # caught it on its first real run.
    #
    # A Hub id is `namespace/name`: one slash, no OS separators, no leading dot.
    # Everything else that looks like a path is treated as one.
    looks_local = (
        candidate.is_absolute()
        or "\\" in model_name
        or model_name.startswith((".", "~"))
        or model_name.count("/") > 1
        # `models/converted` when `models` exists here, but not `google/...`
        or (str(candidate.parent) not in (".", "") and candidate.parent.is_dir())
    )
    if looks_local and not candidate.exists():
        raise FileNotFoundError(
            f"{model_name} looks like a path and does not exist. Nothing here "
            f"downloads; check the spelling, or pass a Hub model id instead.")

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


def read_safetensors_header(path: str) -> dict:
    """Tensor names, dtypes and shapes — without mapping the file.

    ⚠️ **Why this is not `safe_open`.** A safetensors file starts with an 8-byte
    little-endian length followed by that many bytes of UTF-8 JSON describing
    every tensor. For MADLAD that header is about **92 KB** in front of an
    **11.76 GB** file. `safe_open` maps the whole thing; two callers here wanted
    only names and shapes and paid 11.76 GB of address space for them.

    On a 16 GB Windows machine that is not free: the commit limit is RAM plus
    pagefile, and `transformers` needs nearly all of it to load this checkpoint.
    A run died with ``OSError: The paging file is too small for this operation
    to complete. (os error 1455)``. The dominant cost was the loader's own map,
    not this one — but reading 92 KB to learn what is in a file should never
    have cost 11.8 GB of headroom.

    Returns ``{name: {"dtype": str, "shape": list[int], "data_offsets": [a, b]}}``
    with the ``__metadata__`` entry removed, so every key is a real tensor.
    """
    import json

    with open(path, "rb") as fh:
        raw = fh.read(8)
        if len(raw) != 8:
            raise ValueError(f"{path} is too short to be a safetensors file")
        length = int.from_bytes(raw, "little")
        # A sane header is kilobytes. Refuse an absurd length rather than
        # attempt a multi-gigabyte read on a file that is not what we think.
        if not 0 < length <= 100_000_000:
            raise ValueError(
                f"{path} declares a {length}-byte header, which is not a "
                f"safetensors file this can read")
        blob = fh.read(length)
        if len(blob) != length:
            raise ValueError(
                f"{path} declares a {length}-byte header but holds "
                f"{len(blob)}; the file is truncated")

    header = json.loads(blob.decode("utf-8"))
    header.pop("__metadata__", None)
    return header


def read_safetensors_metadata(path: str) -> dict:
    """The file's `__metadata__` block, or `{}`. No mapping, no tensor data.

    safetensors reserves a `__metadata__` key in the header for free-form
    string pairs. `scripts/shrink_checkpoint.py` writes provenance there —
    which model a converted file came from — so a converted checkpoint carries
    its own origin rather than relying on a directory name.
    """
    import json

    with open(path, "rb") as fh:
        length = int.from_bytes(fh.read(8), "little")
        if not 0 < length <= 100_000_000:
            return {}
        blob = fh.read(length)
    try:
        meta = json.loads(blob.decode("utf-8")).get("__metadata__") or {}
    except Exception:                                     # noqa: BLE001
        return {}
    return meta if isinstance(meta, dict) else {}


def source_model_id(checkpoint: str, fallback: str) -> str:
    """What model a checkpoint *is*, regardless of where it sits on disk.

    ⚠️ **This is what a run fingerprint must be built on, not the path.**
    `shrink_checkpoint.py` produces a bfloat16 copy whose weights are
    bit-identical to what the loader would have produced from the float32
    original — the conversion only moves the rounding from every load to one
    disk write. So a result from the cache and a result from the converted
    directory are the *same measurement*, and a run rejected under one must
    stay blocked under the other.

    Keying on the path would silently unblock a known-failing configuration and
    spend another ninety minutes reproducing it.
    """
    try:
        return read_safetensors_metadata(checkpoint).get("converted_from") or fallback
    except Exception:                                     # noqa: BLE001
        return fallback


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

    Reads only the safetensors header — no tensor data, no memory mapping,
    no download. See `read_safetensors_header`.
    """
    header = read_safetensors_header(checkpoint)
    matching = [k for k, spec in header.items()
                if tuple(spec["shape"]) == tuple(shape)]
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
    """Restore the input embedding **and** the output projection, by name.

    ⚠️ **Both, not just the head.** transformers loads this checkpoint's
    `lm_head.weight` into `shared.weight`, so the encoder embeds its input with
    the output projection and the decoder projects through it as well. Repairing
    only `lm_head` leaves the encoder reading rubbish; an earlier version did
    exactly that and reported success.

    Returns a record of what was found and what was done. Repairs nothing when
    the inspection says the head is trained.
    """
    import torch
    from safetensors import safe_open

    if found is None:
        found = inspect_head(model, checkpoint, quiet=quiet)
    if found["verdict"] == "TRAINED":
        if not quiet:
            print("  REPAIR                     : SKIPPED — nothing is wrong here")
        return {**found, "repaired": False, "source_key": None,
                "input_key": None}

    shape = tuple(model.lm_head.weight.shape)
    header = read_safetensors_header(checkpoint)
    embedding_keys = [k for k, spec in header.items()
                      if tuple(spec["shape"]) == shape]
    if not quiet:
        print(f"  checkpoint holds           : {sorted(embedding_keys)}")

    input_key, output_key = identify_matrices(embedding_keys)
    if not quiet:
        print(f"  input embedding is         : {input_key!r}")
        print(f"  output projection is       : {output_key!r}")

    embeddings = model.get_input_embeddings()
    aliased = model.lm_head.weight is embeddings.weight
    target_dtype = model.lm_head.weight.dtype

    with safe_open(checkpoint, framework="pt") as f:
        want_input = f.get_tensor(input_key).to(target_dtype)
        want_output = f.get_tensor(output_key).to(target_dtype)

    if torch.equal(want_input, want_output):
        raise RepairFailedError(
            f"{input_key!r} and {output_key!r} hold identical values, so this "
            f"checkpoint is tied after all and there is nothing to separate. "
            f"Refusing rather than reporting a repair that changed nothing.")

    # ⚠️ **Untie first.** While `lm_head.weight` *is* the embedding Parameter,
    # writing either one writes both, and the second write silently undoes the
    # first. Replacing the Parameter is what `tie_word_embeddings: false` asked
    # for and transformers overrode.
    if aliased:
        model.lm_head.weight = torch.nn.Parameter(want_output.clone(),
                                                  requires_grad=False)
    else:
        with torch.no_grad():
            model.lm_head.weight.data.copy_(want_output)

    with torch.no_grad():
        embeddings.weight.data.copy_(want_input)

    # ⚠️ Verify the outcome, the rule this whole file exists to enforce. Three
    # things must now hold, and a previous version checked only that something
    # changed -- which was true while it was making the model worse.
    head_now = model.lm_head.weight.detach()
    input_now = model.get_input_embeddings().weight.detach()
    if not torch.equal(head_now, want_output):
        raise RepairFailedError(
            f"lm_head does not hold {output_key!r} after the repair; the write "
            f"did not land. Refusing to report success.")
    if not torch.equal(input_now, want_input):
        raise RepairFailedError(
            f"the input embedding does not hold {input_key!r} after the repair. "
            f"They are probably still the same Parameter, so the second write "
            f"undid the first.")
    if torch.equal(head_now, input_now):
        raise RepairFailedError(
            "the input embedding and lm_head are identical after the repair, so "
            "they are still tied. This checkpoint keeps them separate.")

    # The encoder and decoder token embeddings must follow the input embedding,
    # or the encoder is still reading the wrong matrix.
    for stack in ("encoder", "decoder"):
        block = getattr(model, stack, None)
        embed = getattr(block, "embed_tokens", None) if block is not None else None
        if embed is not None and not torch.equal(embed.weight.detach(), want_input):
            raise RepairFailedError(
                f"model.{stack}.embed_tokens does not follow the input "
                f"embedding after the repair, so that stack is still using the "
                f"wrong matrix.")

    if not quiet:
        print(f"  REPAIR                     : APPLIED — input embedding and "
              f"lm_head restored separately")

    return {**found, "repaired": True, "source_key": output_key,
            "input_key": input_key}
