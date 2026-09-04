#!/usr/bin/env python3
"""
Experiment 005 — Does a word's transliteration survive being put in a sentence?

DEC-023 rests on the claim that it does. Two figures are quoted in the decision
record, in the shipped `transliterate.py` docstring, and in `types.py`:

    a word's transliteration is preserved inside a sentence: 1,639/1,639 (100%)
    prepending a character changes 0 of 1,635 tokens

**Neither was produced by a committed script.** They came from an ad-hoc probe
during the session that recorded DEC-023 — which is itself a DEC-016 violation,
and the reason this experiment exists.

This re-measures both claims with the test that can actually fail, and reports
the containment test alongside so the discrepancy between them is visible rather
than inferred.

On pre-commitment: the hypotheses below are **not** newly invented predictions —
they are DEC-023's own claims, restated verbatim from a record written before
this measurement. That is where the pre-commitment comes from. Writing fresh
"predictions" after having seen the answer would be theatre.

Reproduce:
    pip install epitran==1.35.2
    python3 run.py

Deterministic. Emits results.json per DEC-016.
"""

import json
import pathlib
from collections import Counter

import epitran

HERE = pathlib.Path(__file__).parent
RESULTS = HERE / "results.json"
CORPORA = [
    HERE.parent / "002-tokenizer-fertility" / "corpus",
    HERE.parent / "003-metric-validity" / "data",
]

#: Excluded by DEC-015's quality gate, exactly as experiment 004 excluded it.
CORRUPT_MARKER = "CORRUPTED"


def load_lines():
    lines = []
    for d in CORPORA:
        for f in sorted(d.glob("*.txt")):
            if CORRUPT_MARKER in f.name:
                continue
            for ln in f.read_text(encoding="utf-8").splitlines():
                if ln.strip():
                    lines.append((f.name, ln))
    return lines


def main():
    ti = epitran.Epitran("tir-Ethi")
    lines = load_lines()

    print("=" * 76)
    print(f"CORPUS — {len(set(n for n, _ in lines))} files, {len(lines):,} non-empty lines")
    print("=" * 76)

    # ------------------------------------------------------------------ C1
    # "A word's transliteration is preserved inside a sentence."
    #
    # Measured two ways. The difference between them is the whole point.
    print("\n" + "=" * 76)
    print("1.  C1 — is a word's transliteration PRESERVED inside a sentence?")
    print("     DEC-023 recorded 1,639/1,639 (100%).")
    print("=" * 76)

    contain_ok = exact_ok = total = 0
    misaligned_lines = 0
    mismatches = []
    for _, ln in lines:
        words = ln.split()
        in_context = ti.transliterate(ln).split()
        if len(in_context) != len(words):
            # The whole-text pass did not preserve the number of whitespace
            # tokens, so words cannot be paired off. Counted, not silently
            # skipped — a skipped case is a hidden failure.
            misaligned_lines += 1
            continue
        for w, ctx in zip(words, in_context):
            alone = ti.transliterate(w)
            total += 1
            if alone in ctx:
                contain_ok += 1
            if alone == ctx:
                exact_ok += 1
            elif len(mismatches) < 400:
                mismatches.append((w, alone, ctx))

    contain_pct = 100 * contain_ok / total
    exact_pct = 100 * exact_ok / total
    print(f"  word tokens compared                  : {total:,}")
    print(f"  lines where token counts disagreed    : {misaligned_lines}")
    print(f"  CONTAINMENT  (alone is substring of in-context) : "
          f"{contain_ok:,}/{total:,}  ({contain_pct:.2f}%)")
    print(f"  EXACT        (alone == in-context)              : "
          f"{exact_ok:,}/{total:,}  ({exact_pct:.2f}%)")
    print(f"\n  C1 {'CONFIRMED' if exact_pct >= 99.0 else 'REFUTED'} "
          f"at exact equality ({exact_pct:.2f}% {'>=' if exact_pct >= 99.0 else '<'} 99%)")

    # ------------------------------------------------------------- mechanism
    # If the mismatches share one shape, this is a rule, not noise.
    print("\n" + "=" * 76)
    print("2.  MECHANISM — do the mismatches share a shape?")
    print("=" * 76)
    shapes = Counter()
    for w, alone, ctx in mismatches:
        if ctx == alone + "ɨ":
            shapes["in-context adds word-final 'ɨ'"] += 1
        elif alone == ctx + "ɨ":
            shapes["word-alone adds word-final 'ɨ'"] += 1
        elif len(ctx) > len(alone):
            shapes["in-context longer, other"] += 1
        elif len(ctx) < len(alone):
            shapes["in-context shorter, other"] += 1
        else:
            shapes["same length, differing"] += 1
    n_mis = len(mismatches)
    for shape, n in shapes.most_common():
        print(f"  {shape:36s} : {n:4d}/{n_mis}  ({100*n/n_mis:.1f}%)")

    print("\n  Examples:")
    for w, alone, ctx in mismatches[:8]:
        print(f"    {w!r:16s} alone {alone!r:24s} in-context {ctx!r}")

    # ------------------------------------------------------------------ C2
    # "Prepending a character changes 0 of 1,635 tokens."
    print("\n" + "=" * 76)
    print("3.  C2 — does PREPENDING a character change a word's transliteration?")
    print("     DEC-023 recorded 0 of 1,635 changed.")
    print("=" * 76)
    words = sorted({w for _, ln in lines for w in ln.split()})
    changed_prepend = 0
    prepend_ex = []
    for w in words:
        alone = ti.transliterate(w)
        with_prefix = ti.transliterate("ሀ" + w)
        # Strip the prefix's own transliteration to compare the tail.
        pre = ti.transliterate("ሀ")
        tail = with_prefix[len(pre):] if with_prefix.startswith(pre) else with_prefix
        if tail != alone:
            changed_prepend += 1
            if len(prepend_ex) < 5:
                prepend_ex.append((w, alone, tail))
    print(f"  unique words tested                : {len(words):,}")
    print(f"  words whose transliteration changed: {changed_prepend}")
    for w, a, b in prepend_ex:
        print(f"    {w!r}: alone {a!r} -> after prefix {b!r}")
    c2 = changed_prepend == 0
    print(f"\n  C2 {'CONFIRMED' if c2 else 'REFUTED'}")

    # ------------------------------------------------------------------ C3
    print("\n" + "=" * 76)
    print("4.  C3 — does epenthesis stay WITHIN a word?")
    print("=" * 76)
    print(f"  C3 is C1 restated. Exact equality says {exact_pct:.2f}%, so context")
    print("  beyond the word DOES affect the result, at the word's final")
    print("  character. Section 5 shows the trigger is not local context either:")
    print("  a distant edit flips it, so it is not a phonological rule we can")
    print("  state — it is a property of the whole input string.")
    c3 = exact_pct >= 99.0
    print(f"\n  C3 {'CONFIRMED' if c3 else 'REFUTED'}")

    # ----------------------------------------------- position sensitivity
    # The decisive test. If the in-context form were a function of local
    # linguistic context, editing a distant word could not change it.
    print("\n" + "=" * 76)
    print("5.  POSITION SENSITIVITY — can DISTANT text change a word's output?")
    print("=" * 76)
    flips = []
    for _, ln in lines:
        ws = ln.split()
        if len(ws) < 20:
            continue
        ctx = ti.transliterate(ln).split()
        if len(ctx) != len(ws):
            continue
        for i, (w, c) in enumerate(zip(ws, ctx)):
            if i < 10 or ti.transliterate(w) == c:
                continue
            # Replace the FIRST word — far from index i — and see if token i moves.
            for repl in ("ሰላም", "ኩሉ", "ሀ"):
                alt = list(ws)
                alt[0] = repl
                out = ti.transliterate(" ".join(alt)).split()
                if len(out) == len(alt) and out[i] != c:
                    flips.append((i, w, c, out[i], ws[0], repl))
                    break
            if flips:
                break
        if flips:
            break

    if flips:
        i, w, c, other, orig0, repl = flips[0]
        print(f"  word at index {i}: {w!r}")
        print(f"    with first word {orig0!r:14s} -> {c!r}")
        print(f"    with first word {repl!r:14s} -> {other!r}")
        print(f"    the edit is {i} words away and changes the result.")
        print("\n  So the in-context form is NOT a function of local context.")
        print("  It is deterministic, but depends on the whole string.")
    else:
        print("  No distant-edit flip found.")

    results = {
        "lines": len(lines),
        "position_sensitive": bool(flips),
        "position_sensitivity_example": (
            {"index": flips[0][0], "word": flips[0][1],
             "with_original_first_word": flips[0][2],
             "with_substituted_first_word": flips[0][3],
             "original_first_word": flips[0][4],
             "substituted_first_word": flips[0][5]}
            if flips else None
        ),
        "C1": {
            "word_tokens": total,
            "lines_token_count_disagreed": misaligned_lines,
            "containment_ok": contain_ok,
            "containment_pct": round(contain_pct, 3),
            "exact_ok": exact_ok,
            "exact_pct": round(exact_pct, 3),
            "confirmed_at_exact_equality": exact_pct >= 99.0,
            "examples": [{"word": w, "alone": a, "in_context": c}
                         for w, a, c in mismatches[:8]],
        },
        "mechanism": dict(shapes),
        "C2": {"unique_words": len(words), "changed": changed_prepend,
               "confirmed": c2},
        "C3": {"confirmed": c3},
    }

    print("\n" + "=" * 76)
    print("SUMMARY")
    print("=" * 76)
    print(f"  C1 (preserved in sentence) : "
          f"{'CONFIRMED' if results['C1']['confirmed_at_exact_equality'] else 'REFUTED'}")
    print(f"  C2 (prepending is inert)   : {'CONFIRMED' if c2 else 'REFUTED'}")
    print(f"  C3 (epenthesis is in-word) : {'CONFIRMED' if c3 else 'REFUTED'}")
    print(f"  Position-sensitive           : {'YES' if flips else 'NO'}")
    print(f"\n  The containment test reports {contain_pct:.2f}% where exact equality")
    print(f"  reports {exact_pct:.2f}%. Containment cannot detect an appended")
    print("  character, which is what most of the mismatches are.")

    RESULTS.write_text(json.dumps(results, ensure_ascii=False, indent=2))
    print(f"\n  Wrote {RESULTS.name}")


if __name__ == "__main__":
    main()
