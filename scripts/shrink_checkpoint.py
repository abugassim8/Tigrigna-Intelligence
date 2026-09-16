#!/usr/bin/env python3
"""Rewrite MADLAD's float32 checkpoint as bfloat16, one tensor at a time.

Why this exists
---------------
**A 16 GB Windows machine cannot reliably load an 11.76 GB float32 checkpoint.**
The load died with::

    OSError: The paging file is too small for this operation to complete.
             (os error 1455)

That is the Windows *commit limit* — physical RAM plus pagefile — exhausted
while `transformers` memory-maps the whole checkpoint and converts it to
bfloat16 on the way in. The same machine had loaded it successfully an hour
earlier, which is the point: it fits, with nothing to spare, and anything else
running pushes it over.

This removes the margin problem instead of managing it. **11.76 GB → 5.9 GB on
disk**, and the loader no longer converts dtype while mapping.

⚠️ Peak memory is one tensor, not one model
-------------------------------------------
`safetensors.torch.save_file` takes every tensor at once — 5.9 GB resident,
which is the problem again in a new place. So the container is assembled by
hand: an 8-byte length, the JSON header, then each tensor's bytes appended in
order. The source is read with **ordinary file reads at the offsets its own
header gives**, never mapped. Peak is the largest single tensor: 1 GB as float32,
0.5 GB converted.

⚠️ This does not fix the forced tie
-----------------------------------
`T5Config.__post_init__` ties `lm_head` to the input embedding regardless of
what any checkpoint contains, so the converted file loads with the same defect.
The in-memory repair in `tigrinya_translate.head` still applies, unchanged. This
script only makes the file small enough to load.

Usage:
    python3 scripts/shrink_checkpoint.py                    # convert the cache
    python3 scripts/shrink_checkpoint.py --out DIR
    python3 scripts/shrink_checkpoint.py --self-test        # stub, no model
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import shutil
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "services" / "evaluation" / "src"))
sys.path.insert(0, str(REPO / "services" / "translation" / "src"))

from tigrinya_translate.head import (                       # noqa: E402
    locate_checkpoint,
    read_safetensors_header,
)

MODEL = "google/madlad400-3b-mt"

#: Where the converted model is written, relative to the repository.
DEFAULT_OUT = REPO / "models" / "madlad400-3b-mt-bf16"

#: The small files `from_pretrained` needs beside the weights. Copied verbatim
#: from the cache so the converted directory loads with no network at all.
SIDECAR_FILES = ("config.json", "generation_config.json", "tokenizer.json",
                 "tokenizer_config.json", "special_tokens_map.json",
                 "spiece.model", "added_tokens.json")

#: safetensors dtype names to torch dtypes, for the formats this can read.
#: ⚠️ Deliberately short. An unrecognised dtype raises rather than being
#: guessed at: a silently mis-read tensor is indistinguishable from a working
#: model until the output is wrong, which is the failure this whole line of
#: work has been chasing.
READABLE = {"F32": "float32", "F16": "float16", "BF16": "bfloat16"}

#: Bytes per element of the output dtype.
OUT_DTYPE = "BF16"
OUT_ITEMSIZE = 2

#: Read granularity for a single tensor's bytes. Tensors here reach 1 GB; the
#: read still happens in one call, but this bounds the copy buffer.
CHUNK = 64 * 1024 * 1024


class UnreadableDtypeError(RuntimeError):
    """A tensor uses a dtype this converter will not guess at."""


def _numel(shape) -> int:
    n = 1
    for d in shape:
        n *= d
    return n


def plan_output(header: dict) -> tuple[list[str], dict, int]:
    """Decide the output layout. Pure: no files, no torch.

    Returns `(names in write order, new header, total data bytes)`. Tensors are
    ordered by their **source** offset so the input is read front to back rather
    than seeking all over an 11.76 GB file.
    """
    names = sorted(header, key=lambda k: header[k]["data_offsets"][0])
    new: dict = {}
    offset = 0
    for name in names:
        spec = header[name]
        if spec["dtype"] not in READABLE:
            raise UnreadableDtypeError(
                f"{name} has dtype {spec['dtype']}, which this converter does "
                f"not read. Refusing: a mis-read tensor produces a model that "
                f"loads cleanly and is wrong.")
        size = _numel(spec["shape"]) * OUT_ITEMSIZE
        new[name] = {"dtype": OUT_DTYPE, "shape": list(spec["shape"]),
                     "data_offsets": [offset, offset + size]}
        offset += size
    return names, new, offset


def encode_header(new_header: dict) -> bytes:
    """The 8-byte length plus padded JSON that opens a safetensors file.

    Padded to an 8-byte boundary with spaces. JSON tolerates trailing
    whitespace, and aligning the data start is what every reader expects.
    """
    blob = json.dumps(new_header, separators=(",", ":")).encode("utf-8")
    blob += b" " * (-len(blob) % 8)
    return len(blob).to_bytes(8, "little") + blob


def source_data_start(path: str) -> int:
    """Where tensor data begins: 8 bytes of length plus the header itself."""
    with open(path, "rb") as fh:
        return 8 + int.from_bytes(fh.read(8), "little")


def convert(src: str, dst: str, *, progress=None) -> dict:
    """Stream `src` into `dst` as bfloat16. Peak memory is one tensor."""
    import ctypes

    import torch

    header = read_safetensors_header(src)
    names, new_header, total = plan_output(header)
    data_start = source_data_start(src)
    prologue = encode_header(new_header)

    written = 0
    with open(src, "rb") as fin, open(dst, "wb") as fout:
        fout.write(prologue)
        for index, name in enumerate(names):
            spec = header[name]
            begin, end = spec["data_offsets"]
            fin.seek(data_start + begin)
            raw = bytearray(end - begin)
            if fin.readinto(raw) != len(raw):
                raise OSError(f"short read for {name} in {src}")

            source = torch.frombuffer(
                raw, dtype=getattr(torch, READABLE[spec["dtype"]]))
            out = source.to(torch.bfloat16).contiguous()
            nbytes = out.numel() * out.element_size()
            # Raw bytes straight out of the tensor's storage. No numpy, and no
            # second copy of a tensor that may be a gigabyte.
            buffer = (ctypes.c_char * nbytes).from_address(out.data_ptr())
            fout.write(buffer)
            written += nbytes
            del raw, source, out, buffer

            if progress is not None:
                progress(index + 1, len(names), name)

    if written != total:
        raise OSError(
            f"wrote {written} bytes of tensor data, planned {total}. The "
            f"output is not a valid safetensors file; delete it.")
    return {"tensors": len(names), "data_bytes": written,
            "file_bytes": os.path.getsize(dst)}


def verify(src: str, dst: str, *, samples: int = 3) -> list[str]:
    """Check the conversion, and say what was checked rather than that it passed.

    ⚠️ Compares against the **source**, not against expectations. Names and
    shapes must match exactly; every output dtype must be BF16; and a few
    tensors are re-read from both files and compared within bfloat16 rounding.
    """
    import torch

    notes = []
    a, b = read_safetensors_header(src), read_safetensors_header(dst)
    if set(a) != set(b):
        missing = sorted(set(a) - set(b))[:5]
        extra = sorted(set(b) - set(a))[:5]
        raise OSError(f"tensor names differ — missing {missing}, extra {extra}")
    notes.append(f"{len(b)} tensor names identical to the source")

    bad_shape = [n for n in a if list(a[n]["shape"]) != list(b[n]["shape"])]
    if bad_shape:
        raise OSError(f"shape changed for {bad_shape[:5]}")
    notes.append("every shape unchanged")

    wrong = sorted(n for n in b if b[n]["dtype"] != OUT_DTYPE)
    if wrong:
        raise OSError(f"{len(wrong)} tensor(s) are not {OUT_DTYPE}: {wrong[:5]}")
    notes.append(f"every tensor is {OUT_DTYPE}")

    start_a, start_b = source_data_start(src), source_data_start(dst)
    chosen = sorted(a, key=lambda n: -_numel(a[n]["shape"]))[:samples]
    for name in chosen:
        with open(src, "rb") as fh:
            begin, end = a[name]["data_offsets"]
            fh.seek(start_a + begin)
            raw = bytearray(end - begin)
            fh.readinto(raw)
        original = torch.frombuffer(
            raw, dtype=getattr(torch, READABLE[a[name]["dtype"]]))
        with open(dst, "rb") as fh:
            begin, end = b[name]["data_offsets"]
            fh.seek(start_b + begin)
            raw2 = bytearray(end - begin)
            fh.readinto(raw2)
        converted = torch.frombuffer(raw2, dtype=torch.bfloat16)
        if not torch.equal(original.to(torch.bfloat16), converted):
            raise OSError(
                f"{name} does not match the source after conversion. The "
                f"output is wrong; delete it and do not load it.")
        del raw, raw2, original, converted
    notes.append(f"{len(chosen)} largest tensors byte-identical after rounding")
    return notes


def copy_sidecars(src_checkpoint: str, out_dir: pathlib.Path) -> list[str]:
    """Copy config and tokenizer files so the output loads with no network."""
    source_dir = pathlib.Path(src_checkpoint).parent
    copied = []
    for name in SIDECAR_FILES:
        candidate = source_dir / name
        if candidate.exists():
            shutil.copy2(candidate, out_dir / name)
            copied.append(name)
    return copied


def main(argv: list[str] | None = None) -> int:
    from tigrinya_eval.primitives import force_utf8_stdio
    force_utf8_stdio()

    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--model", default=MODEL, help="checkpoint to convert")
    ap.add_argument("--out", default=str(DEFAULT_OUT),
                    help="directory to write the converted model into")
    ap.add_argument("--self-test", action="store_true",
                    help="convert a stub checkpoint; no model, no network")
    args = ap.parse_args(argv)

    if args.self_test:
        return _self_test()

    print("=" * 74)
    print("Converting the checkpoint to bfloat16, one tensor at a time")
    print("=" * 74)

    try:
        src = locate_checkpoint(args.model)
    except FileNotFoundError as exc:
        print(f"  {exc}")
        return 1

    out_dir = pathlib.Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    dst = out_dir / "model.safetensors"

    src_bytes = os.path.getsize(src)
    print(f"  from        {src}")
    print(f"              {src_bytes:,} bytes")
    print(f"  to          {dst}")

    free = shutil.disk_usage(out_dir).free
    need = src_bytes // 2
    if free < need * 11 // 10:
        print(f"  ⚠️ {free:,} bytes free, and this needs about {need:,}. "
              f"Free some space first; nothing was written.")
        return 1

    def show(done, total, name):
        if done % 50 == 0 or done == total:
            print(f"    {done:4}/{total}  {name}", flush=True)

    stats = convert(src, str(dst), progress=show)
    print(f"  wrote       {stats['file_bytes']:,} bytes "
          f"({stats['tensors']} tensors)")
    print(f"  saved       {src_bytes - stats['file_bytes']:,} bytes")

    print("  verifying against the source ...")
    for note in verify(src, str(dst)):
        print(f"    ✓ {note}")

    copied = copy_sidecars(src, out_dir)
    print(f"  copied      {len(copied)} config/tokenizer file(s): "
          f"{', '.join(copied)}")

    # ⚠️ **Prove the next command before printing it.** The first version of
    # this script printed `--model <out_dir>` and that command failed:
    # `locate_checkpoint` searched only the Hugging Face cache and had no
    # branch for a local directory. `check_commands.py` passed it, because it
    # reads flags statically and cannot know an argument *value* is
    # unsupported. Resolving the path here is the runtime half of that checker.
    try:
        resolved = locate_checkpoint(str(out_dir))
    except FileNotFoundError as exc:
        print(f"  ⚠️ the converted model was written, but {out_dir} does not "
              f"resolve as a checkpoint: {exc}")
        print("  Not printing a command that would fail. This is a bug here, "
              "not something you did.")
        return 1
    if os.path.realpath(resolved) != os.path.realpath(dst):
        print(f"  ⚠️ {out_dir} resolves to {resolved}, not the file just "
              f"written ({dst}). Refusing to print a command that would "
              f"inspect a different model than it loads.")
        return 1

    print()
    print("-" * 74)
    print("  Now run the repair against the converted model:")
    print(f"    python3 scripts/repair_lm_head.py --model {out_dir}")
    print()
    print("  ⚠️ The forced tie is a loader behaviour, not a file property, so")
    print("  the converted model still needs the in-memory repair. This only")
    print("  makes it small enough to load.")
    return 0


def _self_test() -> int:
    """Convert a stub checkpoint and verify it, with no model and no network."""
    import tempfile

    import torch
    from safetensors.torch import save_file

    # The layout planning is pure and gets checked without touching a file.
    header = {
        "b.weight": {"dtype": "F32", "shape": [4, 8], "data_offsets": [128, 256]},
        "a.weight": {"dtype": "F32", "shape": [2, 8], "data_offsets": [0, 128]},
    }
    names, new, total = plan_output(header)
    assert names == ["a.weight", "b.weight"], f"not in source order: {names}"
    assert total == (16 + 32) * 2, total
    assert new["a.weight"]["data_offsets"] == [0, 32], new
    assert new["b.weight"]["data_offsets"] == [32, 96], new
    assert all(v["dtype"] == "BF16" for v in new.values())

    try:
        plan_output({"x": {"dtype": "I64", "shape": [2], "data_offsets": [0, 16]}})
    except UnreadableDtypeError:
        pass
    else:                                                 # pragma: no cover
        raise AssertionError("an unknown dtype must be refused, never guessed")

    prologue = encode_header(new)
    assert len(prologue) % 8 == 0, "the data start must be 8-byte aligned"

    with tempfile.TemporaryDirectory() as tmp:
        tmp = pathlib.Path(tmp)
        src, dst = tmp / "src.safetensors", tmp / "dst.safetensors"
        torch.manual_seed(20260916)
        tensors = {"shared.weight": torch.randn(50, 8),
                   "lm_head.weight": torch.randn(50, 8) * 7.5,
                   "block.0.q.weight": torch.randn(8, 8)}
        save_file(tensors, str(src))

        stats = convert(str(src), str(dst))
        assert stats["tensors"] == 3, stats
        assert os.path.getsize(dst) < os.path.getsize(src), "it must be smaller"
        verify(str(src), str(dst), samples=3)

        # ⚠️ The output must be readable by the real library, not only by the
        # code that wrote it. A container this file assembles by hand is worth
        # nothing if `safetensors` cannot open it.
        from safetensors import safe_open
        with safe_open(str(dst), framework="pt") as f:
            assert sorted(f.keys()) == sorted(tensors), sorted(f.keys())
            for name, original in tensors.items():
                got = f.get_tensor(name)
                assert got.dtype is torch.bfloat16, (name, got.dtype)
                assert torch.equal(got, original.to(torch.bfloat16)), name

        # And a corrupted output must be caught rather than reported as fine.
        raw = bytearray(dst.read_bytes())
        raw[-2:] = b"\xff\xff"
        (tmp / "bad.safetensors").write_bytes(raw)
        try:
            verify(str(src), str(tmp / "bad.safetensors"), samples=3)
        except OSError:
            pass
        else:                                             # pragma: no cover
            raise AssertionError("a corrupted conversion must not verify")

    print("self-test passed: a stub checkpoint converts, verifies, reopens with "
          "safetensors,")
    print("  and a corrupted copy is rejected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())       # main() calls force_utf8_stdio() itself
