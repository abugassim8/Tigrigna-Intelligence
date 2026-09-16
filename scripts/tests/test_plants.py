#!/usr/bin/env python3
"""Plant known failures and assert the audit tooling reports them.

Eleven checks in this repository have been found that **could not fail** — seven of
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

import os
import pathlib
import shutil
import subprocess
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parents[2]

#: How every plant subprocess decodes its child.
#:
#: ⚠️ `text=True` on its own decodes with the *locale* default — UTF-8 on Linux
#: but **cp1252 on Windows** — and every script planted here prints `⚠️`, `—`
#: and Ge'ez. The decode runs in a reader thread, so a failure there does not
#: raise at the call: the thread dies, `.stdout` becomes None, and the plant
#: reports a misleading exit status instead of a decode error.
#:
#: That is the failure mode this suite exists to prevent, so it must not be the
#: suite's own. ⚠️ A plant expecting exit 1 **still "passes" when the child died
#: of an encoding crash**, because a crash also exits non-zero.
#:
#: This is only half the fix. The other half is in the children: a Python
#: process writing to a *pipe* on Windows encodes with cp1252 regardless of the
#: console, so each entry point forces its own stdout to UTF-8.
CHILD_IO = {"text": True, "encoding": "utf-8", "errors": "replace"}

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
                capture_output=True, **CHILD_IO)
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
    # The other derived count that documents kept getting wrong by hand. Its
    # claim pattern is anchored tightly *and* its markers are switched off, so
    # this is the only thing standing between it and a silent pass.
    ("open-action count contradicting the register",
     "\n\n**3 open actions.**\n", 1),
    # A markdown table is one paragraph, so a ⚠️ in ANY row used to exempt
    # EVERY row — which left the plan of record's `| **Basis** |` line free to
    # claim 99 decisions and 77 experiments. The marked row here must not
    # protect the row above it.
    ("table row exempted by a marker in a sibling row",
     "\n\n| x | y |\n| --- | --- |\n| Basis | 3 reproducible experiments |\n"
     "| Note | ⚠️ superseded |\n", 1),
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
                               cwd=work, capture_output=True, **CHILD_IO)
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
                               cwd=REPO, capture_output=True, **CHILD_IO)
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
                               cwd=REPO, capture_output=True, **CHILD_IO)
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


# --------------------------------------------------------------------------
# translate_tico19.py — the first measurement that loads a model
#
# Three of these cases are silent failures: the pipeline completes, the segment
# count is right, and chrF computes to a plausible number. Nothing else in this
# repository would notice, because the output is perfectly well-formed — it is
# just not a translation of what was asked, or not into Tigrinya.
#
# ⚠️ The model itself is never loaded here. `Translator` is injected exactly as
# `morphology.Analyser` is, which is what makes this testable in an environment
# that cannot reach huggingface.co — and what makes the argparse wiring in
# `main()` testable at all. That wiring had a real bug (a positional argument to
# a keyword-only parameter) that the self-test did not reach.
# --------------------------------------------------------------------------

TRANSLATE_PLANT = r'''
import json, pathlib, sys, tempfile
sys.path.insert(0, "scripts")
import translate_tico19 as t

GEEZ = "ሰላም ዓለም"      # "selam alem"

def steady(batch):
    return [GEEZ for _ in batch]
def drops_one(batch):
    return [GEEZ for _ in batch][:-1] or [GEEZ]
def english(batch):
    return ["Wash your hands often." for _ in batch]
def empties(batch):
    return ["" for _ in batch]

CASE = sys.argv[1]

with tempfile.TemporaryDirectory() as tmp:
    tmp = pathlib.Path(tmp)
    js, sheet = tmp / "r.json", tmp / "s.csv"

    if CASE == "scores_and_writes_with_a_steady_translator":
        out = t.measure(steady, out_json=js, out_sheet=sheet, limit=6, quiet=True)
        ok = (js.exists() and sheet.exists()
              and len(out["scores"]) == 2
              and out["output_shape"]["ethiopic"] == 6)

    elif CASE == "the_cli_wiring_reaches_measure":
        # main() with the model class replaced. Catches argument-passing bugs
        # that --self-test cannot, because --self-test bypasses main()'s body.
        import tigrinya_translate.translate as tt
        tt.MadladTranslator = lambda *a, **k: type(
            "Stub", (), {"_loaded": (None, None), "__call__":
                         staticmethod(lambda b: steady(b))})()
        code = t.main(["--json", str(js), "--sheet", str(sheet), "--limit", "4"])
        ok = code == 0 and js.exists() and sheet.exists()

    elif CASE == "a_dropped_segment_aborts_and_writes_nothing":
        # chrF pairs by position: one dropped segment shifts every later pair
        # and the result reads as poor quality rather than as a bug.
        try:
            t.measure(drops_one, out_json=js, out_sheet=sheet, limit=6, quiet=True)
            ok = False
        except t.SegmentCountError:
            ok = not js.exists() and not sheet.exists()

    elif CASE == "output_in_the_wrong_language_aborts_and_writes_nothing":
        # The failure an unknown language token produces: fluent, right count,
        # scoreable, and about a language nobody asked for.
        try:
            t.measure(english, out_json=js, out_sheet=sheet, limit=6, quiet=True)
            ok = False
        except t.WrongLanguageError:
            ok = not js.exists() and not sheet.exists()

    elif CASE == "empty_output_aborts_rather_than_scoring_nothing":
        try:
            t.measure(empties, out_json=js, out_sheet=sheet, limit=6, quiet=True)
            ok = False
        except t.WrongLanguageError:
            ok = not js.exists() and not sheet.exists()

    elif CASE == "the_sheet_never_leaks_the_reference":
        # Showing the human reference turns "is this usable health information"
        # into "does it match the other translation" -- the question chrF is
        # already answering.
        t.measure(steady, out_json=js, out_sheet=sheet, limit=6, quiet=True)
        text = sheet.read_text(encoding="utf-8")
        refs = t._anchor("tir_et")
        ids = t.sample_indices(len(t._anchor("eng")))[:6]
        ok = all(refs[i] not in text for i in ids)

    elif CASE == "a_rejected_run_preserves_its_output":
        # A 46-minute run was correctly rejected and then discarded the only
        # evidence that could explain why. Refusing to record a MEASUREMENT was
        # right; throwing away the OUTPUT was not.
        try:
            t.measure(english, out_json=js, out_sheet=sheet, limit=6, quiet=True)
            ok = False
        except t.WrongLanguageError:
            rej = js.with_name(js.stem + "-REJECTED.json")
            ok = rej.exists() and not js.exists() and not sheet.exists()
            if ok:
                d = json.loads(rej.read_text(encoding="utf-8"))
                ok = (d["is_a_measurement"] is False
                      and len(d["pairs"]) == 6
                      and "chrf" not in json.dumps(d)
                      and d["pairs"][0]["output"] == "Wash your hands often.")

    elif CASE == "a_resumed_run_matches_an_uninterrupted_one":
        # The whole point of checkpointing: the same hypotheses, and an honest
        # record that the run was stitched from two sessions.
        # ⚠️ 12, not 6. translate_all batches by 8, so a 6-segment run is a
        # SINGLE batch that dies before any batch completes — and a batch that
        # failed must never reach disk. Testing resume needs two batches, and
        # the first version of this plant did not have them.
        clean = t.measure(steady, out_json=js, out_sheet=None, limit=12, quiet=True)

        calls = [0]
        def dies_after_first_batch(batch):
            calls[0] += len(batch)
            if calls[0] > 8:
                raise RuntimeError("simulated interruption")
            return steady(batch)

        js2 = tmp / "r2.json"
        try:
            t.measure(dies_after_first_batch, out_json=js2, out_sheet=None,
                      limit=12, quiet=True)
        except RuntimeError:
            pass
        partial = t._partial_path(js2)
        held = json.loads(partial.read_text(encoding="utf-8"))["hypotheses"]
        resumed = t.measure(steady, out_json=js2, out_sheet=None, limit=12,
                            quiet=True)
        ok = (len(held) == 8                                 # one batch survived
              and partial.exists() is False                  # spent on success
              and resumed["scores"] == clean["scores"]       # same result
              and resumed["resumed_from_partial"] == 8)      # and says so

    elif CASE == "a_resume_refuses_a_different_run":
        # ⚠️ Grafting old hypotheses onto a new sample would be well-formed and
        # completely wrong. The fingerprint is what stops it.
        t.measure(steady, out_json=js, out_sheet=None, limit=6, quiet=True)
        t._save_partial(t._partial_path(js), "not-this-run", ["x", "y"])
        got = t._load_partial(t._partial_path(js), t._fingerprint(["a"], t.MODEL))
        ok = got == []

    elif CASE == "smoke_writes_nothing_at_all":
        # ⚠️ The first version of this plant listed the temp directory before
        # and after. smoke() has no reason to write THERE, so it passed even
        # when smoke() was made to write into the repository root -- a check
        # that could not fail, found by reverting it rather than by reading it.
        #
        # Writing is now forbidden outright, wherever it is aimed.
        import builtins
        real_open, real_write = builtins.open, pathlib.Path.write_text
        def no_open(f, mode="r", *a, **k):
            if any(c in mode for c in "wxa+"):
                raise AssertionError(f"smoke() opened {f} for writing")
            return real_open(f, mode, *a, **k)
        def no_write(self, *a, **k):
            raise AssertionError(f"smoke() wrote {self}")
        builtins.open, pathlib.Path.write_text = no_open, no_write
        try:
            out = t.smoke(steady, 3, quiet=True)
            ok = len(out) == 3
        finally:
            builtins.open, pathlib.Path.write_text = real_open, real_write

    elif CASE == "the_threshold_is_recorded_before_judging":
        out = t.measure(steady, out_json=js, out_sheet=sheet, limit=6, quiet=True)
        saved = json.loads(js.read_text(encoding="utf-8"))
        ok = (saved["pre_committed"]["usable_threshold"] == t.USABLE_THRESHOLD
              and saved["judgement"].startswith("PENDING"))

    else:
        raise SystemExit("unknown case")

sys.exit(0 if ok else 1)
'''

TRANSLATE_PLANTS = [
    ("scores and writes with a steady translator",
     "scores_and_writes_with_a_steady_translator", 0),
    ("the CLI wiring actually reaches measure()",
     "the_cli_wiring_reaches_measure", 0),
    ("a dropped segment aborts and writes NOTHING",
     "a_dropped_segment_aborts_and_writes_nothing", 0),
    ("output in the wrong language aborts and writes NOTHING",
     "output_in_the_wrong_language_aborts_and_writes_nothing", 0),
    ("empty output aborts rather than scoring nothing",
     "empty_output_aborts_rather_than_scoring_nothing", 0),
    ("the judgement sheet never leaks the reference",
     "the_sheet_never_leaks_the_reference", 0),
    ("the threshold is recorded before judging",
     "the_threshold_is_recorded_before_judging", 0),
    ("a rejected run preserves its output for diagnosis",
     "a_rejected_run_preserves_its_output", 0),
    ("a resumed run matches an uninterrupted one, and says it resumed",
     "a_resumed_run_matches_an_uninterrupted_one", 0),
    ("a resume refuses a partial from a different run",
     "a_resume_refuses_a_different_run", 0),
    ("--smoke writes nothing at all",
     "smoke_writes_nothing_at_all", 0),
]


def run_translate_plants() -> list[str]:
    problems = []
    with tempfile.TemporaryDirectory() as tmp:
        script = pathlib.Path(tmp) / "translate_plant.py"
        script.write_text(TRANSLATE_PLANT, encoding="utf-8")
        for label, case, expect in TRANSLATE_PLANTS:
            r = subprocess.run([sys.executable, str(script), case],
                               cwd=REPO, capture_output=True, **CHILD_IO)
            status = "PASS" if r.returncode == expect else "FAIL"
            print(f"  [{status}] translate_tico19: {label} "
                  f"(exit {r.returncode}, expected {expect})")
            if r.returncode != expect:
                detail = (r.stderr or r.stdout).strip().splitlines()[-1:] or [""]
                problems.append(
                    f"translate_tico19 plant misbehaved: {label} — {detail[0]}")
    return problems

# --------------------------------------------------------------------------
# check_commands.py — the instructions a human follows by hand
#
# Every other claim in this repository was enforced: figures, dates, derived
# counts, planted behaviour. The commands it *prints* were not, and two of them
# did not work — one of them the error message shown at the exact moment a user
# needs the right answer (`hm.download('ti')`, A-20), and one a `--verify` flag
# that no script has ever defined.
#
# ⚠️ The negative cases matter more than usual here. A checker that flagged
# every `--flag` it saw would fire on `--write`, `--check` and `--list`, all of
# which are real, and would be switched off the same day.
# --------------------------------------------------------------------------

COMMAND_PLANTS = [
    # The two defects that prompted this, restored verbatim.
    ("a flag no script declares",
     "\n\nRun `python data/anchors/tico19/fetch.py --verify` to check.\n", 1),
    ("a script path that resolves nowhere",
     "\n\nRun `python scripts/check_nothing.py --list` first.\n", 1),
    # Negative cases: every one of these is a real, working command today.
    ("a real flag on a repo-root path", "\n\n`python scripts/check_dates.py --list`\n", 0),
    ("a real flag on a script beside the document",
     "\n\n`python3 scripts/check_figures.py --list`\n", 0),
    ("a flag that is argparse's own", "\n\n`python scripts/check_dates.py --help`\n", 0),
    ("untouched control", "", 0),
]


def run_command_plants() -> list[str]:
    problems = []
    with tempfile.TemporaryDirectory() as tmp:
        work = pathlib.Path(tmp) / "repo"
        shutil.copytree(REPO, work,
                        ignore=shutil.ignore_patterns(".git", "__pycache__",
                                                      ".pytest_cache"))
        target = work / "docs" / "vision" / "goals.md"
        original = target.read_text(encoding="utf-8")
        for label, plant, expect in COMMAND_PLANTS:
            target.write_text(original + plant, encoding="utf-8")
            r = subprocess.run([sys.executable, "scripts/check_commands.py"],
                               cwd=work, capture_output=True, **CHILD_IO)
            status = "PASS" if r.returncode == expect else "FAIL"
            print(f"  [{status}] check_commands: {label} "
                  f"(exit {r.returncode}, expected {expect})")
            if r.returncode != expect:
                detail = (r.stdout or r.stderr).strip().splitlines()[-1:] or [""]
                problems.append(
                    f"check_commands plant misbehaved: {label} — {detail[0]}")
    return problems

# --------------------------------------------------------------------------
# The whole Windows text-encoding class
#
# Two of these scripts were reported crashing on Windows, and both were the
# same defect: text I/O with no explicit encoding, which uses the **locale
# default** — UTF-8 on Linux, cp1252 on Windows. Fixing the eighteen call
# sites is not the fix; this is. It reruns the entry points with an ASCII
# default, which is *stricter* than cp1252, so anything Windows would reject
# is rejected here too and CI catches the regression on Linux.
#
# ⚠️ `LC_ALL=C` alone is not enough. PEP 538 coerces the C locale to C.UTF-8
# and PEP 540 has a UTF-8 mode, so Python quietly hands back UTF-8 anyway and
# the plant would pass on every input — the very failure this file exists to
# catch. `PYTHONCOERCECLOCALE=0`, `PYTHONUTF8=0` and an unset
# `PYTHONIOENCODING` are each required; together they were verified to yield
# `ANSI_X3.4-1968`, and the write plant aborts loudly if they ever stop.
#
# The two halves are tested separately and both are needed:
#   - **printing** — the three checkers emit `⚠️` and `—` into a pipe;
#   - **writing**  — `Harness.save()` writes Ge'ez to a file.
# --------------------------------------------------------------------------

ASCII_ENV = {"PYTHONUTF8": "0", "PYTHONCOERCECLOCALE": "0",
             "LC_ALL": "C", "LANG": "C", "LC_CTYPE": "C"}

#: Set in the child when this suite re-runs *itself* under ASCII, so the
#: re-run does not re-run itself for ever.
ASCII_PASS = "TIGRINYA_PLANTS_ASCII_PASS"

#: Written to a temp file rather than passed with `-c`: under an ASCII locale
#: Python decodes a `-c` argument with the filesystem encoding, so Ge'ez on the
#: command line would fail for a reason that has nothing to do with the code
#: under test. A `.py` file is UTF-8 by default whatever the locale is.
ENCODING_WRITE_PLANT = r'''
"""Round-trip Ge'ez through Harness.save() with no UTF-8 anywhere in the env.

PRINTS ASCII ONLY, on purpose. The *printing* half of this defect is covered
by running the real checkers; this plant isolates the *writing* half, and a
print failure here would mask it.
"""
import json, locale, pathlib, sys, tempfile

if locale.getpreferredencoding(False).lower().replace("-", "") in (
        "utf8", "cp65001"):
    print("ABORT: the locale is still UTF-8, so this plant proves nothing")
    sys.exit(3)

from tigrinya_eval.harness import EvalSet, Harness

GEEZ = ["ሰላም ዓለም"]           # "selam alem"
EM_DASH = "—"

h = Harness()
h.evaluate("plant", GEEZ, EvalSet("plant", "unknown", GEEZ), notes=(EM_DASH,))

with tempfile.TemporaryDirectory() as tmp:
    out = pathlib.Path(tmp) / "r.json"
    h.save(out)                      # UnicodeEncodeError here if unfixed
    back = json.loads(out.read_text(encoding="utf-8"))

assert back["results"][0]["notes"] == [EM_DASH], back
print("OK: non-ASCII round-tripped under", locale.getpreferredencoding(False))
'''

#: (label, argv after the interpreter, expected exit). `None` marks the case
#: that runs ENCODING_WRITE_PLANT from a temp file.
ENCODING_PLANTS = [
    ("check_dates.py prints under an ASCII locale",       ["scripts/check_dates.py"], 0),
    ("check_figures.py prints under an ASCII locale",     ["scripts/check_figures.py"], 0),
    ("check_definitions.py prints under an ASCII locale", ["scripts/check_definitions.py"], 0),
    ("Harness.save() writes Ge'ez under an ASCII locale", None, 0),
    # ⚠️ The one that matters, and the one that was missing. The four above are
    # a HAND-WRITTEN LIST, and a hand-written list is exactly what failed: it
    # did not name `measure_morphology`, which imports nothing of the sort but
    # is reached through `mm.main()` from HARNESS_PLANT — so five plants went on
    # failing on Windows while this group reported the class closed.
    #
    # This entry needs no list. It re-runs *every* plant under ASCII and
    # requires identical behaviour, which reproduces those five failures and
    # nothing else. Whatever is planted next is covered the day it is added.
    ("every plant behaves identically under an ASCII locale", [__file__], 0),
]


def run_encoding_plants() -> list[str]:
    problems = []
    env = dict(os.environ)
    env.pop("PYTHONIOENCODING", None)          # would defeat the whole check
    env.update(ASCII_ENV)
    env[ASCII_PASS] = "1"

    #: True when we ARE the ASCII re-run. Everything still runs; only the entry
    #: that would spawn another copy of this file is held back.
    inner = bool(os.environ.get(ASCII_PASS))

    with tempfile.TemporaryDirectory() as tmp:
        script = pathlib.Path(tmp) / "encoding_plant.py"
        script.write_text(ENCODING_WRITE_PLANT, encoding="utf-8")
        for label, argv, expect in ENCODING_PLANTS:
            if inner and argv == [__file__]:
                skipped.append(label)
                print(f"  [SKIP] ascii-locale: {label} — this IS the ASCII "
                      f"re-run; nesting it would not terminate")
                continue
            argv = [str(script)] if argv is None else argv
            r = subprocess.run([sys.executable, *argv], cwd=REPO, env=env,
                               capture_output=True, **CHILD_IO)
            status = "PASS" if r.returncode == expect else "FAIL"
            print(f"  [{status}] ascii-locale: {label} "
                  f"(exit {r.returncode}, expected {expect})")
            if r.returncode != expect:
                detail = (r.stderr or r.stdout).strip().splitlines()[-1:] or [""]
                problems.append(
                    f"ascii-locale plant misbehaved: {label} — {detail[0]}")
    return problems


def main() -> int:
    problems = (run_screen_plants() + run_figure_plants()
                + run_morphology_plants() + run_harness_plants()
                + run_translate_plants() + run_command_plants()
                + run_encoding_plants())
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
    # ⚠️ Windows writes to a pipe or a redirect with the locale codec
    # (cp1252), not the console's. Without this, printing `⚠️` or `—`
    # raises UnicodeEncodeError — including while printing a traceback.
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
