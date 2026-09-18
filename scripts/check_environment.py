#!/usr/bin/env python3
"""Is this workstation ready to work on this repository? One command, one answer.

Why this exists
---------------
`diagnose_environment.py` diagnoses the **model**. This diagnoses the
**machine**: interpreter, packages, credentials, checkpoints, checkers. It is
the first thing to run in a fresh clone or a fresh editor, so that setup
problems are named once rather than discovered one failing command at a time.

⚠️ **It reports; it never installs.** A setup script that pip-installs on a
developer's machine is how an environment silently diverges from CI — and this
project lost a day to a `transformers` downgrade that broke the
`tokenizers==0.23.1` pin and moved `huggingface_hub` from 1.31 to 0.36.

⚠️ **It never loads the model.** That costs ~6 GB and belongs to
`repair_lm_head.py`. A readiness check that needs 6 GB stops being run, which is
the failure DEC-008 exists to prevent. Checkpoints are inspected by path and
size only.

⚠️ **It never prints an `HF_TOKEN` value.** Only whether one is set. The value
belongs in the environment and nowhere else — not in a file, not in output that
gets pasted into a chat window.

Usage:
    python3 scripts/check_environment.py
    python3 scripts/check_environment.py --skip-checkers
    python3 scripts/check_environment.py --self-test
"""

from __future__ import annotations

import argparse
import importlib
import os
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "services" / "evaluation" / "src"))
sys.path.insert(0, str(REPO / "services" / "translation" / "src"))

#: Importable or the repository does not work. `(module, why)`.
REQUIRED = (
    ("tigrinya_primitives", "pip install -e services/primitives"),
    ("tigrinya_eval", 'pip install -e "services/evaluation[dev]"'),
    ("tigrinya_translate", 'pip install -e "services/translation[dev]"'),
    ("sacrebleu", "a dependency of tigrinya-eval; reinstall that package"),
    ("pytest", "pip install pytest"),
)

#: Needed only for the model path. Absent is fine until you run the model.
MODEL_ONLY = (
    ("torch", 'pip install -e "services/translation[madlad]"'),
    ("transformers", 'pip install -e "services/translation[madlad]"'),
    ("safetensors", "installed with transformers"),
)

#: ⚠️ Absent is **SKIP, not FAIL** — DEC-028. HornMorpho is GPL-3.0, installed
#: by the user and never distributed, so a machine without it is a normal
#: machine and the morphology checks are written to skip rather than pass.
OPTIONAL = (("hm", "HornMorpho — GPL-3.0, user-installed (DEC-028)"),)

#: The fast checkers. ⚠️ `scripts/tests/test_plants.py` is deliberately absent:
#: it spawns ~89 subprocesses and takes minutes, and a readiness check that
#: takes minutes stops being run. It is named in the output instead.
CHECKERS = ("check_figures.py", "check_dates.py", "check_commands.py",
            "check_definitions.py")

MODEL = "google/madlad400-3b-mt"
CONVERTED = REPO / "models" / "madlad400-3b-mt-bf16"


def probe_import(name: str) -> tuple[bool, str]:
    """Import a module and report its version, or why it could not be had."""
    try:
        module = importlib.import_module(name)
    except Exception as exc:                              # noqa: BLE001
        return False, f"{type(exc).__name__}: {exc}"
    return True, str(getattr(module, "__version__", "no __version__"))


def probe_token(environ) -> tuple[bool, str]:
    """Whether a Hub token is set. ⚠️ Never returns or logs the value.

    Unauthenticated Hub downloads were measured at **57 kB/s**, about 47 hours
    for this model, so this is worth reporting — but the token itself must not
    reach a log, a file or a pasted terminal transcript.
    """
    for key in ("HF_TOKEN", "HUGGING_FACE_HUB_TOKEN", "HUGGINGFACEHUB_API_TOKEN"):
        value = environ.get(key)
        if value and value.strip():
            return True, f"{key} is set ({len(value.strip())} characters)"
    return False, ("no HF_TOKEN — Hub downloads are throttled "
                   "(measured 57 kB/s). Set it with setx, not in a file.")


def probe_checkpoint(target: str) -> tuple[bool, str]:
    """Resolve a checkpoint by path or Hub id, reporting size. Loads nothing."""
    try:
        from tigrinya_translate.head import locate_checkpoint
    except Exception as exc:                              # noqa: BLE001
        return False, f"tigrinya_translate not importable: {exc}"
    try:
        path = locate_checkpoint(target)
    except Exception as exc:                              # noqa: BLE001
        return False, str(exc)
    return True, f"{path} ({os.path.getsize(path):,} bytes)"


def run_checker(name: str, timeout: int = 900) -> tuple[int, str]:
    """Run one checker and return its exit code and last meaningful line."""
    script = REPO / "scripts" / name
    if not script.is_file():
        return 127, f"{script} does not exist"
    try:
        r = subprocess.run([sys.executable, str(script)], cwd=REPO,
                           capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=timeout)
    except subprocess.TimeoutExpired:
        # ⚠️ A timeout used to read as an ordinary failure. It is not: the
        # checkers were scanning the whole filesystem including `.venv/`, and
        # `check_figures.py` timed out at 180s on a healthy repository. Say
        # what it means, and give the limit room now that they ask git instead.
        return -9, (f"TIMED OUT after {timeout}s — that is a finding about the "
                    f"checker, not about this repository")
    except Exception as exc:                              # noqa: BLE001
        return -1, f"could not start: {type(exc).__name__}: {exc}"
    lines = [ln for ln in (r.stdout or "").splitlines() if ln.strip()]
    return r.returncode, (lines[-1] if lines else (r.stderr or "").strip()[:120])


def verdict(required_ok: bool, checkers_ok: bool, model_ok: bool) -> tuple[int, str]:
    """Turn the findings into an exit code and a sentence. Pure.

    ⚠️ **A missing model does not fail the run**, and that is deliberate. Most
    work here — 187 tests, 89 planted cases, every checker — needs no model at
    all, and failing a readiness check on a 5.9 GB file nobody needs yet is how
    a check becomes something people learn to ignore (DEC-008).
    """
    if not required_ok:
        return 1, ("NOT READY — a required package is missing. The commands to "
                   "fix each one are printed above.")
    if not checkers_ok:
        return 1, ("NOT READY — the packages are installed but a checker is "
                   "failing. Fix that before committing anything.")
    if not model_ok:
        return 0, ("READY for everything except the model. Tests, plants and "
                   "checkers will all run. See docs/guides/LOCAL_SETUP.md for "
                   "the model steps when you need them.")
    return 0, "READY — packages, checkers and the model checkpoint are all in place."


def collect(environ=None, *, skip_checkers: bool = False) -> tuple[int, list[str]]:
    """Run every probe and return `(exit code, report lines)`.

    ⚠️ Every probe runs regardless of earlier failures. A readiness check that
    stops at the first problem makes the owner run it once per problem.
    """
    environ = os.environ if environ is None else environ
    out: list[str] = []
    out.append("=" * 74)
    out.append("Workstation readiness")
    out.append("=" * 74)

    out.append(f"  python      {sys.version.split()[0]}")
    out.append(f"  executable  {sys.executable}")
    in_venv = sys.prefix != getattr(sys, "base_prefix", sys.prefix)
    out.append(f"  virtualenv  {'yes' if in_venv else 'NO — expected .venv'}")
    out.append(f"  repository  {REPO}")

    out.append("")
    out.append("  required packages")
    required_ok = True
    for name, remedy in REQUIRED:
        ok, detail = probe_import(name)
        required_ok = required_ok and ok
        out.append(f"    {'OK  ' if ok else 'MISSING'} {name:22} "
                   f"{detail if ok else remedy}")

    out.append("")
    out.append("  model packages (only needed to run the model)")
    model_packages_ok = True
    for name, remedy in MODEL_ONLY:
        ok, detail = probe_import(name)
        model_packages_ok = model_packages_ok and ok
        out.append(f"    {'OK  ' if ok else 'absent '} {name:22} "
                   f"{detail if ok else remedy}")

    out.append("")
    out.append("  optional")
    for name, why in OPTIONAL:
        ok, _detail = probe_import(name)
        # ⚠️ SKIP, never FAIL. DEC-028.
        out.append(f"    {'OK  ' if ok else 'SKIP'}  {name:22} {why}")

    out.append("")
    out.append("  credentials")
    token_ok, token_detail = probe_token(environ)
    out.append(f"    {'OK  ' if token_ok else 'absent '} {'HF_TOKEN':22} "
               f"{token_detail}")

    out.append("")
    out.append("  checkpoints (inspected by path and size; nothing is loaded)")
    cache_ok, cache_detail = probe_checkpoint(MODEL)
    out.append(f"    {'OK  ' if cache_ok else 'absent '} {'cache':22} {cache_detail}")
    conv_ok, conv_detail = probe_checkpoint(str(CONVERTED))
    out.append(f"    {'OK  ' if conv_ok else 'absent '} {'converted bf16':22} "
               f"{conv_detail}")

    checkers_ok = True
    if skip_checkers:
        out.append("")
        out.append("  checkers    skipped (--skip-checkers)")
    else:
        out.append("")
        out.append("  checkers")
        for name in CHECKERS:
            code, line = run_checker(name)
            checkers_ok = checkers_ok and code == 0
            out.append(f"    {'OK  ' if code == 0 else f'EXIT {code}'} "
                       f"{name:22} {line[:90]}")
        out.append("    note  scripts/tests/test_plants.py is not run here — "
                   "~89 subprocesses, minutes. Run it before committing.")

    code, sentence = verdict(required_ok, checkers_ok, cache_ok or conv_ok)
    out.append("")
    out.append("-" * 74)
    out.append(f"  {sentence}")
    return code, out


def main(argv: list[str] | None = None) -> int:
    from tigrinya_eval.primitives import force_utf8_stdio
    force_utf8_stdio()

    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--skip-checkers", action="store_true",
                    help="skip the four checkers; report packages and paths only")
    ap.add_argument("--self-test", action="store_true",
                    help="exercise the probes with stubs; no network")
    args = ap.parse_args(argv)

    if args.self_test:
        return _self_test()

    code, lines = collect(skip_checkers=args.skip_checkers)
    print("\n".join(lines))
    return code


def _self_test() -> int:
    """Check the parts that decide, and the one that must never leak."""
    # ⚠️ The token probe must report presence and never the value.
    ok, detail = probe_token({"HF_TOKEN": "hf_SECRETVALUE123"})
    assert ok, detail
    assert "hf_SECRETVALUE123" not in detail, "the token value leaked into output"
    assert "17 characters" in detail, detail
    ok, detail = probe_token({})
    assert not ok and "57 kB/s" in detail, detail
    ok, _ = probe_token({"HF_TOKEN": "   "})
    assert not ok, "whitespace is not a token"

    # A missing package is reported, not raised.
    ok, detail = probe_import("a_module_that_does_not_exist")
    assert not ok and "ModuleNotFoundError" in detail, detail

    # The verdict, including the deliberate "no model is still ready".
    assert verdict(False, True, True)[0] == 1
    assert verdict(True, False, True)[0] == 1
    code, sentence = verdict(True, True, False)
    assert code == 0 and "except the model" in sentence, sentence
    assert verdict(True, True, True)[0] == 0

    # A checker that does not exist is reported, not crashed on.
    code, line = run_checker("check_nothing_of_the_sort.py")
    assert code == 127 and "does not exist" in line, line

    # ⚠️ The whole report is produced even with everything unavailable.
    code, lines = collect(environ={}, skip_checkers=True)
    text = "\n".join(lines)
    for expected in ("required packages", "credentials", "checkpoints", "SKIP"):
        assert expected in text, f"{expected!r} missing from the report"

    print("self-test passed: the token value never reaches the report, a missing")
    print("  package is reported rather than raised, and the verdict is correct")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())       # main() calls force_utf8_stdio() itself
