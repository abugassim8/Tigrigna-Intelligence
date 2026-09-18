#!/usr/bin/env python3
"""Collect everything needed to diagnose the translation failure, in one run.

Why this exists
---------------
The wrong-language failure took **six round trips and two ninety-minute runs**
to get one line of usable evidence, because each attempt answered one question
and the assistant then asked for another command. That is not a way to debug
someone else's machine.

This answers every question at once and writes a single file to paste back.

⚠️ **Every stage runs in its own subprocess.** The previous attempt exited
silently — header printed, no traceback, no `Loading weights` bar, nothing — and
took the whole diagnostic with it. A native crash or an out-of-memory kill
produces no Python exception, so in one process it destroys the report. Out of
process it becomes a recorded line, and the later stages still run.

⚠️ **The report is written even when every stage fails.** A diagnostic that
produces nothing when everything is broken is worthless, and that is precisely
the case it exists for.

What each stage is for
----------------------
**Stage 2 is the decisive one, and it is nearly free.** The model prints this at
load time:

    the tied weights mapping ... specifies to tie shared.weight to
    decoder.embed_tokens.weight, but both are present in the checkpoints with
    different values, so we will NOT tie them

The MADLAD paper says the SentencePiece vocabulary is *"shared on both the
encoder and decoder side"*, so those tensors **should be identical**. Stage 2
opens the checkpoint with `safetensors.safe_open` and compares them directly,
reading only the tensors it needs rather than materialising 11.8 GB. If they
differ, the checkpoint is wrong and no `transformers` version will fix it.

Usage:
    python3 scripts/diagnose_environment.py
    python3 scripts/diagnose_environment.py --self-test   # stubs, no model
"""

from __future__ import annotations

import argparse
import pathlib
import subprocess
import sys
import textwrap
import time

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "services" / "evaluation" / "src"))

REPORT = REPO / "diagnostic-report.txt"

#: Generous. A stage that needs longer than this on a CPU has told us something
#: by taking longer than this.
TIMEOUT_SECONDS = 420

MODEL = "google/madlad400-3b-mt"
PROMPT = "Wash your hands often."


# --------------------------------------------------------------------------
# The stages. Each is a complete, standalone program.
#
# ⚠️ Written as source strings and run from a temp file, not with `-c`: under a
# non-UTF-8 locale Python decodes a `-c` argument with the filesystem encoding,
# so non-ASCII in the command line would fail for reasons unrelated to what is
# being measured. A `.py` file is UTF-8 whatever the locale is.
# --------------------------------------------------------------------------

STAGE_VERSIONS = '''
import platform, sys
print("python     ", sys.version.split()[0])
print("executable ", sys.executable)
print("platform   ", platform.platform())
try:
    import ctypes
    if not hasattr(ctypes, "windll"):
        raise OSError("not Windows")
    class MS(ctypes.Structure):
        _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("ullExtendedVirtual", ctypes.c_ulonglong)]
    m = MS(); m.dwLength = ctypes.sizeof(MS)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
    print("RAM total  ", round(m.ullTotalPhys / 2**30, 1), "GB")
    print("RAM free   ", round(m.ullAvailPhys / 2**30, 1), "GB")
except Exception:
    try:
        import os
        total = os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES")
        print("RAM total  ", round(total / 2**30, 1), "GB")
    except Exception as exc:
        print("RAM        unavailable:", type(exc).__name__, exc)

for name in ("torch", "transformers", "tokenizers", "huggingface_hub",
             "sentencepiece", "safetensors", "sacrebleu"):
    try:
        print(f"{name:12}", __import__(name).__version__)
    except Exception as exc:
        print(f"{name:12} MISSING ({type(exc).__name__})")
'''

STAGE_CHECKPOINT = '''
# THE DECISIVE STAGE. Reads individual tensors from the checkpoint without
# materialising 11.8 GB, and answers whether the two embedding tensors the
# loader complains about actually differ.
import glob, os
from huggingface_hub import try_to_load_from_cache
from safetensors import safe_open

path = try_to_load_from_cache("%(model)s", "model.safetensors")
if not isinstance(path, str) or not os.path.exists(path):
    hits = glob.glob(os.path.expanduser(
        "~/.cache/huggingface/hub/**/model.safetensors"), recursive=True)
    hits = [h for h in hits if "madlad" in h.lower()]
    path = hits[0] if hits else None

if not path:
    raise SystemExit("could not locate a cached model.safetensors")

print("checkpoint ", path)
print("size       ", os.path.getsize(path), "bytes")

with safe_open(path, framework="pt") as f:
    keys = sorted(f.keys())
    print("tensors    ", len(keys))
    interesting = [k for k in keys if "embed_tokens" in k or k.startswith("shared")
                   or k.startswith("lm_head")]
    for k in interesting:
        sl = f.get_slice(k)
        print(f"  {k:40} {sl.get_shape()} {sl.get_dtype()}")

    import torch
    def load(name):
        return f.get_tensor(name) if name in keys else None

    shared = load("shared.weight")
    enc = load("encoder.embed_tokens.weight")
    dec = load("decoder.embed_tokens.weight")

    print()
    for label, a, b in (("shared vs encoder", shared, enc),
                        ("shared vs decoder", shared, dec),
                        ("encoder vs decoder", enc, dec)):
        if a is None or b is None:
            print(f"  {label:20} one side absent")
            continue
        same = bool(torch.equal(a, b))
        print(f"  {label:20} identical={same}", end="")
        if not same:
            d = (a.float() - b.float()).abs()
            print(f"  max|diff|={d.max().item():.6g}  mean|diff|={d.mean().item():.6g}")
        else:
            print()

    for label, t in (("shared", shared), ("encoder", enc), ("decoder", dec)):
        if t is not None:
            v = t.float()
            print(f"  {label:8} mean={v.mean().item():+.6f} std={v.std().item():.6f} "
                  f"min={v.min().item():+.4f} max={v.max().item():+.4f} "
                  f"nan={bool(v.isnan().any())}")
''' % {"model": MODEL}

STAGE_TOKENIZER = '''
from transformers import AutoTokenizer
M = "%(model)s"
PROMPT = "<2ti> %(prompt)s"

fast = AutoTokenizer.from_pretrained(M)
print("fast class ", type(fast).__name__)
vocab = fast.get_vocab()
print("vocab size ", len(vocab))
for t in ("<2ti>", "<2am>", "<2es>", "<2en>"):
    print(f"  {t:8} in vocab: {t in vocab}  id={vocab.get(t)}")
print("fast tokens", fast.tokenize(PROMPT))
print("fast ids   ", fast(PROMPT)["input_ids"])

try:
    from transformers import T5Tokenizer
    slow = T5Tokenizer.from_pretrained(M)
    print("slow class ", type(slow).__name__)
    print("slow tokens", slow.tokenize(PROMPT))
    print("slow ids   ", slow(PROMPT)["input_ids"])
except Exception as exc:
    print("slow       unavailable:", type(exc).__name__, exc)
''' % {"model": MODEL, "prompt": PROMPT}

STAGE_LOAD = '''
import torch
from transformers import AutoModelForSeq2SeqLM
M = "%(model)s"

try:
    model = AutoModelForSeq2SeqLM.from_pretrained(
        M, low_cpu_mem_usage=True, dtype=torch.bfloat16)
    print("keyword    dtype=")
except TypeError:
    model = AutoModelForSeq2SeqLM.from_pretrained(
        M, low_cpu_mem_usage=True, torch_dtype=torch.bfloat16)
    print("keyword    torch_dtype=")

model.eval()
actual = next(model.parameters()).dtype
print("asked      torch.bfloat16")
print("loaded as  ", actual)
print("MATCHES    ", actual == torch.bfloat16)
print("params     ", sum(p.numel() for p in model.parameters()))
print("config tie ", model.config.tie_word_embeddings)

# Do the in-memory tensors agree, after whatever the loader did to them?
sd = model.state_dict()
for a, b in (("shared.weight", "encoder.embed_tokens.weight"),
             ("shared.weight", "decoder.embed_tokens.weight")):
    if a in sd and b in sd:
        print(f"  {a} == {b}: {bool(torch.equal(sd[a], sd[b]))}")
    else:
        print(f"  {a} / {b}: not both present in state_dict")
''' % {"model": MODEL}

STAGE_GENERATE = '''
import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
M = "%(model)s"

tok = AutoTokenizer.from_pretrained(M)
try:
    model = AutoModelForSeq2SeqLM.from_pretrained(
        M, low_cpu_mem_usage=True, dtype=torch.bfloat16)
except TypeError:
    model = AutoModelForSeq2SeqLM.from_pretrained(
        M, low_cpu_mem_usage=True, torch_dtype=torch.bfloat16)
model.eval()

# ⚠️ Controls. Without them "the output is not Tigrinya" cannot be told from
# "this model's Tigrinya is poor", and those need opposite responses.
for lang in ("<2es>", "<2de>", "<2am>", "<2ti>"):
    prompt = lang + " " + "%(prompt)s"
    ids = tok(prompt, return_tensors="pt")
    with torch.inference_mode():
        out = model.generate(**ids, max_new_tokens=32, num_beams=1,
                             do_sample=False)
    text = tok.batch_decode(out, skip_special_tokens=True)[0]
    # ascii() so the report is safe to paste from any console encoding.
    print(f"{lang:8} -> {ascii(text)}")
''' % {"model": MODEL, "prompt": PROMPT}

STAGES = (
    ("1. versions and memory", STAGE_VERSIONS),
    ("2. CHECKPOINT — do the embedding tensors actually differ?", STAGE_CHECKPOINT),
    ("3. tokenizer", STAGE_TOKENIZER),
    ("4. model load and dtype", STAGE_LOAD),
    ("5. generation, with control languages", STAGE_GENERATE),
)


def run_stage(source: str, workdir: pathlib.Path) -> tuple[str, int]:
    """Run one stage out of process and return (captured text, exit code).

    ⚠️ Never raises. A stage that segfaults, is OOM-killed or hangs must become
    a line in the report, not the end of the run.
    """
    script = workdir / "stage.py"
    script.write_text(source, encoding="utf-8")
    started = time.time()
    try:
        r = subprocess.run(
            [sys.executable, str(script)], cwd=REPO, capture_output=True,
            text=True, encoding="utf-8", errors="replace",
            timeout=TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        return (f"TIMED OUT after {TIMEOUT_SECONDS}s — that is itself a finding\n",
                -9)
    except Exception as exc:                              # noqa: BLE001
        return (f"could not start: {type(exc).__name__}: {exc}\n", -1)

    body = (r.stdout or "")
    if r.stderr:
        body += "\n--- stderr ---\n" + r.stderr
    if r.returncode != 0 and not body.strip():
        body += (f"\n⚠️ exited {r.returncode} with NO output at all. That is a "
                 f"native crash or an out-of-memory kill, not a Python error.\n")
    body += f"\n[exit {r.returncode}, {time.time() - started:.1f}s]\n"
    return body, r.returncode


def collect(stages=STAGES) -> str:
    import tempfile

    lines = [
        "=" * 74,
        "TRANSLATION DIAGNOSTIC — paste this whole file",
        "=" * 74,
        f"generated {time.strftime('%Y-%m-%d %H:%M:%S')}",
        f"repo      {REPO}",
        "",
        "Every stage ran in its own process, so a crash in one is recorded",
        "rather than ending the report.",
        "",
    ]
    with tempfile.TemporaryDirectory() as tmp:
        tmp = pathlib.Path(tmp)
        for title, source in stages:
            print(f"  running {title} ...", flush=True)
            body, code = run_stage(textwrap.dedent(source), tmp)
            lines += ["", "-" * 74, title, "-" * 74, body.rstrip(), ""]
            print(f"      exit {code}", flush=True)
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    from tigrinya_eval.primitives import force_utf8_stdio
    force_utf8_stdio()

    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--self-test", action="store_true",
                    help="run stub stages proving the harness survives a crash")
    args = ap.parse_args(argv)

    if args.self_test:
        return _self_test()

    print("=" * 74)
    print("Collecting the translation diagnostic. A few minutes.")
    print("=" * 74)

    report = collect()
    # ⚠️ Written unconditionally: the case this exists for is everything failing.
    REPORT.write_text(report, encoding="utf-8")

    print()
    print(f"  wrote {REPORT}")
    print("  Paste that whole file. It is the only thing needed.")
    return 0


def _self_test() -> int:
    """Prove the harness records crashes instead of dying with them."""
    stages = (
        ("ok", "print('fine')"),
        ("hard crash", "import os; os._exit(3)"),
        ("nonzero with output", "print('said something'); raise SystemExit(2)"),
        ("still runs after a crash", "print('reached the end')"),
    )
    text = collect(stages)
    assert "fine" in text, text
    assert "NO output at all" in text, text
    assert "said something" in text, text
    assert "reached the end" in text, "a crash stopped later stages"
    print("self-test passed: a hard crash is recorded and later stages still run")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())       # main() calls force_utf8_stdio() itself
