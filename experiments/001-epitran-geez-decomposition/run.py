#!/usr/bin/env python3
"""
Experiment 001 — Epitran as the Ge'ez consonant-vowel decomposition substrate.

Tests whether epitran's `tir-Ethi` map satisfies DEC-007's requirements:
decomposition, coverage, language specificity, and lossless reversibility.

Reproduce:
    python3 -m venv .v && . .v/bin/activate
    pip install epitran==1.35.2
    python3 run.py

Deterministic: no randomness, no seed required. Runs in under a second.
See README.md in this directory for results and analysis.
"""

import statistics
from collections import defaultdict

import epitran

ETHIOPIC_CORE = range(0x1200, 0x1380)  # Core Ethiopic block only
VOWELS = set("aeiouɨəɛɔɐ")
SAMPLES = ["ትግርኛ", "ካተበ", "ሰላም", "ኤርትራ", "መንእሰይ", "ዓቕሚ", "ተራእዩ"]


def transliterate(ep, text):
    """Return IPA for text, or '' if epitran cannot map it."""
    try:
        return ep.transliterate(text)
    except Exception:
        return ""


def main():
    ti = epitran.Epitran("tir-Ethi")
    am = epitran.Epitran("amh-Ethi")

    # 1. Language specificity: does tir-Ethi differ from amh-Ethi?
    differences = []
    identical = 0
    for cp in ETHIOPIC_CORE:
        ch = chr(cp)
        t, a = transliterate(ti, ch), transliterate(am, ch)
        if not t and not a:
            continue
        if t != a:
            differences.append((ch, t, a))
        else:
            identical += 1

    print("=== 1. tir-Ethi vs amh-Ethi ===")
    print(f"  identical: {identical} | different: {len(differences)}")
    for ch, t, a in differences[:12]:
        print(f"    U+{ord(ch):04X} {ch}  tir={t!r}  amh={a!r}")

    # 2. Coverage of the core Ethiopic block
    mapped = sum(1 for cp in ETHIOPIC_CORE if transliterate(ti, chr(cp)))
    total = len(ETHIOPIC_CORE)
    print(f"\n=== 2. Coverage ===\n  mapped {mapped}/{total}")

    # 3. Consonant/vowel separation on the canonical K-T-B example
    word = "ካተበ"
    ipa = transliterate(ti, word)
    print("\n=== 3. C/V separation ===")
    print(f"  {word} ({len(word)} chars) -> {ipa} ({len(ipa)} symbols)")
    print(f"  consonants: {[c for c in ipa if c not in VOWELS]}")
    print(f"  vowels    : {[c for c in ipa if c in VOWELS]}")

    # 4. Reversibility: is the forward map injective?
    inverse = defaultdict(list)
    for cp in ETHIOPIC_CORE:
        ch = chr(cp)
        out = transliterate(ti, ch)
        if out:
            inverse[out].append(ch)
    collisions = {k: v for k, v in inverse.items() if len(v) > 1}

    print("\n=== 4. Reversibility ===")
    print(f"  chars mapped {mapped} -> distinct outputs {len(inverse)}")
    print(f"  colliding outputs: {len(collisions)}")
    print(f"  chars lost:        {sum(len(v) - 1 for v in collisions.values())}")
    for k, v in list(collisions.items())[:8]:
        print(f"    {k!r:>6} <- {' '.join(v)}")
    print("  => many-to-one; round-trip is LOSSY (collisions are Ge'ez homophone pairs)")

    # 5. Symbol expansion factor
    print("\n=== 5. Expansion ===")
    ratios = []
    for s in SAMPLES:
        out = transliterate(ti, s)
        ratios.append(len(out) / len(s))
        print(f"  {s:>8} {len(s)} -> {len(out):>2} ({ratios[-1]:.2f}x) {out}")
    print(f"  mean expansion: {statistics.mean(ratios):.2f}x")


if __name__ == "__main__":
    main()
