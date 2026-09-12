#!/usr/bin/env python3
"""Plant known failures and assert the audit tooling reports them.

Nine checks in this repository have been found that **could not fail** — five of
them inside the audit tooling itself. Every one was written in good faith,
reviewed, and passing; none was caught by reading the code. They were caught by
planting a failure and watching nothing happen.

So the planting is not a one-off diagnostic. It is the test, and it runs in CI.

Each case below is a (text, expected exit status) pair. A case expecting **1**
proves the checker can fail; a case expecting **0** proves it has not become so
strict it rejects legitimate text. Both directions matter: a check that fires on
everything gets switched off, and a switched-off check is the failure mode
DEC-008 exists to prevent.

Usage:
    python3 scripts/tests/test_plants.py        # exit 1 if any plant misbehaves
"""

from __future__ import annotations

import pathlib
import shutil
import subprocess
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parents[2]

# --------------------------------------------------------------------------
# screen_dataset.py — the Ge'ez mojibake gate
#
# The rule under test is context-sensitive: an accented Latin letter is
# corruption when it adjoins an Ethiopic *syllable* and a borrowed proper noun
# when it does not. Both halves need a plant, because a rule that called
# everything corruption would block TICO-19 and a rule that called nothing
# corruption would pass the known-corrupted sample.
# --------------------------------------------------------------------------

SCREEN = REPO / "scripts" / "data_processing" / "screen_dataset.py"
EVAL_SET = REPO / "experiments/003-metric-validity/data/flores_ti.txt"
CLEAN = REPO / "experiments/002-tokenizer-fertility/corpus/tlt_000_clean.txt"

SCREEN_PLANTS = [
    # (label, text inserted mid-word between two Ge'ez syllables, expected exit)
    ("accented Latin letter between Ge'ez syllables", "ñ", 1),
    ("U+FFFD replacement character", "�", 1),
    ("U+0085 C1 control", "", 1),
    ("U+009D C1 control", "", 1),
    ("borrowed proper noun (Erdoğan)", " Erdoğan ", 0),
    ("multiplication sign in arithmetic (4×109)", " 4×109 ", 0),
    ("untouched control", "", 0),
]


def run_screen_plants() -> list[str]:
    text = CLEAN.read_text(encoding="utf-8")
    cut = text.index("ን")            # a Ge'ez syllable, mid-word
    problems = []
    with tempfile.TemporaryDirectory() as tmp:
        corpus = pathlib.Path(tmp) / "corpus.txt"
        for label, plant, expect in SCREEN_PLANTS:
            corpus.write_text(text[:cut] + plant + text[cut:], encoding="utf-8")
            r = subprocess.run(
                [sys.executable, str(SCREEN), str(corpus), "--licence", "mit",
                 "--script", "geez", "--eval-set", str(EVAL_SET)],
                capture_output=True, text=True)
            status = "PASS" if r.returncode == expect else "FAIL"
            print(f"  [{status}] screen_dataset: {label} "
                  f"(exit {r.returncode}, expected {expect})")
            if r.returncode != expect:
                problems.append(f"screen_dataset plant misbehaved: {label}")
    return problems


# --------------------------------------------------------------------------
# check_figures.py — retired figures, derived counts, identifier integrity
#
# The marker-scope case is the one that already cost something. A `⚠️` in the
# *following* paragraph used to suppress a live claim, and "Seven decisions now
# carry amendments" sat unchecked and wrong behind one.
# --------------------------------------------------------------------------

FIGURES = REPO / "scripts" / "check_figures.py"

FIGURE_PLANTS = [
    ("bare retired figure", "\n\nTier 0 resident footprint is 72 MB.\n", 1),
    ("bare retired figure, wrapped across lines",
     "\n\nThe standing-cost saving from tiering\ndelivers a 22x saving overall.\n", 1),
    ("derived count contradicting the tree",
     "\n\nThis project has 3 reproducible experiments.\n", 1),
    # The count of plants is itself a derived count now. This plant is the
    # reason that is worth anything — and note it changes the very number it
    # guards, which is the cleanest evidence the derivation is live.
    ("planted-case count contradicting the suite",
     "\n\nThe planted-failure suite is (3 cases, CI).\n", 1),
    ("derived count, spelled out",
     "\n\nThis project has three reproducible experiments.\n", 1),
    ("undefined goal id", "\n\nSee G-99 for details.\n", 1),
    ("undefined gap id", "\n\nSee GAP-77 for details.\n", 1),
    ("retired figure with its own retraction marker",
     "\n\n⚠️ Superseded: Tier 0 footprint was 72 MB.\n", 0),
    ("marker in the NEXT paragraph must not suppress",
     "\n\nTier 0 resident footprint is 72 MB.\n\n⚠️ An unrelated warning.\n", 1),
    ("untouched control", "", 0),
]


def run_figure_plants() -> list[str]:
    problems = []
    with tempfile.TemporaryDirectory() as tmp:
        work = pathlib.Path(tmp) / "repo"
        shutil.copytree(REPO, work,
                        ignore=shutil.ignore_patterns(".git", "__pycache__",
                                                      ".pytest_cache"))
        target = work / "docs" / "vision" / "goals.md"
        original = target.read_text(encoding="utf-8")
        for label, plant, expect in FIGURE_PLANTS:
            target.write_text(original + plant, encoding="utf-8")
            r = subprocess.run([sys.executable, "scripts/check_figures.py"],
                               cwd=work, capture_output=True, text=True)
            status = "PASS" if r.returncode == expect else "FAIL"
            print(f"  [{status}] check_figures: {label} "
                  f"(exit {r.returncode}, expected {expect})")
            if r.returncode != expect:
                problems.append(f"check_figures plant misbehaved: {label}")
    return problems


# --------------------------------------------------------------------------
# tigrinya_eval.morphology — the intrinsic checks
#
# These are the checks most exposed to the failure this file exists to catch.
# Their analyser is GPL-3.0 and absent here (DEC-028), so all five SKIP, and a
# skip that quietly reads as a pass would flip the metrics.md morphology row to
# ✅ on a machine where morphology has never once run.
#
# Injected analysers make that testable today: a broken one must fail, and the
# skip must stay distinct from a pass.
# --------------------------------------------------------------------------

MORPH_PLANT = '''
import sys
sys.path.insert(0, "services/evaluation/src")
sys.path.insert(0, "services/primitives/src")
from tigrinya_eval.morphology import (
    check_surface, check_alignment, check_determinism, evaluate_morphology)
from tigrinya_primitives import morphology as _m

# Exit 77 means "this plant could not be run here", the autotools convention.
# Two of these cases assert the *skip* path, which only exists when the
# analyser is absent — on a machine that has HornMorpho they are not failures,
# they are inapplicable. Reporting them as failures would make the one tool
# whose job is to be trusted about real alarms cry wolf.
SKIP = 77

TEXTS = ["ሰላም ዓለም", "ፀሓይ ትወጽእ ኣላ"]
n = [0]

def good(w):
    return [{"seg": "<" + w + ">"}]

def moving(w):
    n[0] += 1
    return [{"seg": "<" + w + ":" + str(n[0]) + ">"}]

CASE = sys.argv[1]
if CASE == "determinism_broken":
    words = sorted({w for t in TEXTS for w in t.split()})
    ok = check_determinism(words, analyser=moving).holds
elif CASE == "determinism_good":
    words = sorted({w for t in TEXTS for w in t.split()})
    ok = check_determinism(words, analyser=good).holds
elif CASE == "surface_broken":
    import tigrinya_eval.morphology as m
    real = m._analyse
    m._analyse = lambda t, a: real(t, a).__class__(
        surface=real(t, a).surface + "!", analysis=real(t, a).analysis)
    ok = check_surface(TEXTS, analyser=good).holds
elif CASE == "alignment_good":
    ok = check_alignment(TEXTS, analyser=good).holds
elif CASE == "skip_is_not_complete":
    if _m.is_available():
        sys.exit(SKIP)
    r = evaluate_morphology(TEXTS)
    ok = not r.complete and bool(r.skipped())
elif CASE == "require_fails_when_absent":
    if _m.is_available():
        sys.exit(SKIP)
    ok = not evaluate_morphology(TEXTS, require=True).holds
else:
    raise SystemExit("unknown case")

sys.exit(0 if ok else 1)
'''

MORPH_PLANTS = [
    ("determinism catches a moving analyser", "determinism_broken", 1),
    ("determinism passes a stable analyser", "determinism_good", 0),
    ("surface catches a mangled surface form", "surface_broken", 1),
    ("alignment passes well-formed spans", "alignment_good", 0),
    ("a skipped check is not 'complete'", "skip_is_not_complete", 0),
    ("--require fails when the analyser is absent", "require_fails_when_absent", 0),
]


#: Mirrors `SKIP` inside MORPH_PLANT. See the note there.
PLANT_SKIP = 77

#: Filled by `run_morphology_plants`, read by `main` so the summary line can
#: never say "all N behaved as specified" when some of them did not run.
skipped: list[str] = []


# --------------------------------------------------------------------------
# scripts/measure_morphology.py — the large-corpus harness
#
# This harness serves surface/alignment/coverage from a table built during
# check_determinism's first pass, which is only legitimate because determinism
# is measured at 100%. That makes `_Recorder.__call__`'s unconditional
# call-through the single line the whole measurement rests on: serve a cached
# value there and determinism compares a value to itself, reports a perfect
# score, and licenses a table nobody checked.
#
# So two plants, and the second is the interesting one. It does not test the
# harness — it tests that the safeguard is load-bearing, by breaking it and
# showing a real failure becomes invisible.
#
# HornMorpho is absent here (DEC-028), so both patch `is_available` and
# `_analyser` to inject a fake. Nothing GPL-3.0 is needed to run them.
# --------------------------------------------------------------------------

HARNESS_PLANT = '''
import pathlib, sys, tempfile
sys.path.insert(0, "scripts")
sys.path.insert(0, "services/evaluation/src")
sys.path.insert(0, "services/primitives/src")
from tigrinya_primitives import morphology as _m

n = [0]
def steady(w):
    return [{"seg": "<" + w + ">"}]
def crashes_on_one(w):
    if w == "ዓለም":
        raise ValueError("too many values to unpack (expected 2)")
    return [{"seg": "<" + w + ">"}]
def always_crashes(w):
    raise ValueError("too many values to unpack (expected 2)")
def moving(w):                      # a different answer every call
    n[0] += 1
    return [{"seg": "<" + w + ":" + str(n[0]) + ">"}]

def run(analyser, corpus, out, recorder_call=None):
    """Run the harness with `analyser` injected. Returns (exit code, wrote?)."""
    n[0] = 0
    _m.is_available = lambda: True
    _m._analyser = lambda: analyser
    import measure_morphology as mm
    original = mm._Recorder.__call__
    if recorder_call:
        mm._Recorder.__call__ = recorder_call
    try:
        code = mm.main([str(corpus), "--json", str(out)])
    finally:
        mm._Recorder.__call__ = original
    return code, pathlib.Path(out).exists()

def cached_call(self, word):
    """The mutation: serve a stored value instead of calling through."""
    self.calls += 1
    if word in self.table:
        return [self.table[word]]
    raw = self._live(word)
    self._store(word, raw)
    return raw

CASE = sys.argv[1]
with tempfile.TemporaryDirectory() as tmp:
    tmp = pathlib.Path(tmp)
    (tmp / "c.txt").write_text("ሰላም ዓለም\\nፀሓይ ትወጽእ ኣላ\\n", encoding="utf-8")
    # 300 distinct Ethiopic words, so a single crashing word is 0.3% — under
    # CRASH_ABORT_FRACTION, which is the case worth testing.
    big = tmp / "big"
    big.mkdir()
    filler = " ".join("ቃል" + chr(0x1200 + i) for i in range(300))
    (big / "c.txt").write_text("ሰላም ዓለም\\n" + filler + "\\n", encoding="utf-8")

    if CASE == "harness_measures_with_a_steady_analyser":
        code, wrote = run(steady, tmp, tmp / "a.json")
        ok = code == 0 and wrote

    elif CASE == "harness_aborts_and_writes_nothing_on_nondeterminism":
        code, wrote = run(moving, tmp, tmp / "b.json")
        # Not merely non-zero: it must not leave a partial artefact behind.
        ok = code != 0 and not wrote

    elif CASE == "call_through_is_load_bearing":
        honest, honest_wrote = run(moving, tmp, tmp / "c.json")
        broken, broken_wrote = run(moving, tmp, tmp / "d.json",
                                   recorder_call=cached_call)
        # Same broken analyser, one line changed: the honest recorder catches
        # it and writes nothing; the caching one reports a clean run.
        ok = (honest != 0 and not honest_wrote) and (broken == 0 and broken_wrote)
        if not ok:
            print("honest:", honest, honest_wrote, "broken:", broken, broken_wrote)

    elif CASE == "a_crashing_word_is_recorded_not_fatal":
        code, wrote = run(crashes_on_one, big, tmp / "e.json")
        # One pathological token must not cost the whole measurement — but it
        # must be named, never folded into "no analysis found".
        ok = code == 0 and wrote

    elif CASE == "an_analyser_that_always_raises_aborts":
        code, wrote = run(always_crashes, big, tmp / "f.json")
        # Past the threshold this is a broken analyser, not an edge case, and
        # measuring around it would be dishonest.
        ok = code != 0 and not wrote

    else:
        raise SystemExit("unknown case")

sys.exit(0 if ok else 1)
'''

HARNESS_PLANTS = [
    ("measures with a steady analyser", "harness_measures_with_a_steady_analyser", 0),
    ("aborts and writes NOTHING on non-determinism",
     "harness_aborts_and_writes_nothing_on_nondeterminism", 0),
    ("a caching recorder hides non-determinism (the safeguard is real)",
     "call_through_is_load_bearing", 0),
    ("one crashing word is recorded, not fatal",
     "a_crashing_word_is_recorded_not_fatal", 0),
    ("an analyser that always raises aborts and writes nothing",
     "an_analyser_that_always_raises_aborts", 0),
]


def run_harness_plants() -> list[str]:
    problems = []
    with tempfile.TemporaryDirectory() as tmp:
        script = pathlib.Path(tmp) / "harness_plant.py"
        script.write_text(HARNESS_PLANT, encoding="utf-8")
        for label, case, expect in HARNESS_PLANTS:
            r = subprocess.run([sys.executable, str(script), case],
                               cwd=REPO, capture_output=True, text=True)
            status = "PASS" if r.returncode == expect else "FAIL"
            print(f"  [{status}] measure_morphology: {label} "
                  f"(exit {r.returncode}, expected {expect})")
            if r.returncode != expect:
                detail = (r.stderr or r.stdout).strip().splitlines()[-1:] or [""]
                problems.append(
                    f"measure_morphology plant misbehaved: {label} — {detail[0]}")
    return problems


def run_morphology_plants() -> list[str]:
    problems = []
    with tempfile.TemporaryDirectory() as tmp:
        script = pathlib.Path(tmp) / "plant.py"
        script.write_text(MORPH_PLANT, encoding="utf-8")
        for label, case, expect in MORPH_PLANTS:
            r = subprocess.run([sys.executable, str(script), case],
                               cwd=REPO, capture_output=True, text=True)
            if r.returncode == PLANT_SKIP:
                skipped.append(label)
                print(f"  [SKIP] morphology: {label} — needs HornMorpho ABSENT; "
                      f"it is installed here, so this plant verified nothing")
                continue
            status = "PASS" if r.returncode == expect else "FAIL"
            print(f"  [{status}] morphology: {label} "
                  f"(exit {r.returncode}, expected {expect})")
            if r.returncode != expect:
                detail = (r.stderr or r.stdout).strip().splitlines()[-1:] or [""]
                problems.append(f"morphology plant misbehaved: {label} — {detail[0]}")
    return problems


def main() -> int:
    problems = (run_screen_plants() + run_figure_plants()
                + run_morphology_plants() + run_harness_plants())
    print()
    for p in problems:
        print(f"::error::{p}")
    if problems:
        print(f"{len(problems)} planted failure(s) did not behave as specified — "
              f"a check has stopped being able to fail")
        return 1
    # Summed by convention rather than by name, so a fifth *_PLANTS list is
    # counted here the day it is added. `docs/figures.json` derives the same
    # number the same way; listing the four names in both places is how the
    # printed total and the documented one would quietly come to disagree.
    total = sum(len(v) for k, v in sorted(globals().items())
                if k.endswith("_PLANTS") and isinstance(v, list))
    if skipped:
        print(f"{total - len(skipped)} of {total} planted cases behaved as "
              f"specified; {len(skipped)} NOT RUN — {', '.join(skipped)}")
        return 0
    print(f"all {total} planted cases behaved as specified")
    return 0


if __name__ == "__main__":
    sys.exit(main())
