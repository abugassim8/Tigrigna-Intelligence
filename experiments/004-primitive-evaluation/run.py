#!/usr/bin/env python3
"""
Experiment 004 — Can the MVP primitives be evaluated without a gold standard?

P-4 blocks every MVP capability behind evaluation, and no Tigrinya gold standard
exists. This tests how much of Tier 0 is measurable by intrinsic properties —
idempotence, determinism, alignment integrity, reversibility — which need no
reference data.

See README.md for pre-committed hypotheses.

Reproduce:
    pip install epitran==1.35.2 tokenizers==0.23.1
    python3 run.py

Deterministic. Emits results.json per DEC-016.
"""

import json
import pathlib
import sys
from collections import Counter

import epitran
from tokenizers import Tokenizer, models, pre_tokenizers, trainers

HERE = pathlib.Path(__file__).parent
RESULTS = HERE / "results.json"
CORPORA = [
    HERE.parent / "002-tokenizer-fertility" / "corpus",
    HERE.parent / "003-metric-validity" / "data",
]

PUNCT = set("።፡፣፤፥፦፧፨፠-–—''\"\"()[]{}/\\.,;:!?'\"«»%“”‘’")
# Eritrean-standard targets; the Ethiopian-common series maps onto them.
NORM_MAP = str.maketrans("ፀፁፂፃፄፅፆአ", "ጸጹጺጻጼጽጾኣ")


def is_ethiopic(ch):
    cp = ord(ch)
    return (0x1200 <= cp <= 0x137F or 0x1380 <= cp <= 0x139F
            or 0x2D80 <= cp <= 0x2DDF or 0xAB00 <= cp <= 0xAB2F
            or 0x1E7E0 <= cp <= 0x1E7FF)


def normalise(text):
    """Orthographic normalisation: collapse the tsade and alef variants."""
    return text.translate(NORM_MAP)


def load_words():
    texts, words = [], []
    for d in CORPORA:
        for f in sorted(d.glob("*.txt")):
            if "CORRUPTED" in f.name:
                continue  # excluded by DEC-015's quality gate
            t = f.read_text(encoding="utf-8")
            texts.append((f.name, t))
            for raw in t.split():
                w = "".join(c for c in raw if c not in PUNCT)
                if w and any(is_ethiopic(c) for c in w):
                    words.append(w)
    return texts, words


def main():
    ti = epitran.Epitran("tir-Ethi")
    texts, words = load_words()
    uniq = sorted(set(words))
    results = {"corpus_files": len(texts), "words": len(words), "unique_words": len(uniq)}

    print("=" * 76)
    print(f"CORPUS — {len(texts)} files, {len(words):,} words, {len(uniq):,} unique")
    print("=" * 76)

    # ------------------------------------------------------- H1 idempotence
    print("\n" + "=" * 76)
    print("1.  H1 — is orthographic normalisation IDEMPOTENT?")
    print("=" * 76)
    bad = [t for _, t in texts if normalise(normalise(t)) != normalise(t)]
    changed = sum(1 for w in uniq if normalise(w) != w)
    collapsed = len(uniq) - len(set(normalise(w) for w in uniq))
    h1 = not bad
    print(f"  texts where normalise(normalise(x)) != normalise(x) : {len(bad)}")
    print(f"  unique forms altered by normalisation               : {changed}")
    print(f"  unique forms COLLAPSED (merged into another)        : {collapsed}")
    print(f"\n  H1 {'CONFIRMED' if h1 else 'REFUTED'}")
    results["H1"] = {"non_idempotent_texts": len(bad), "forms_altered": changed,
                     "forms_collapsed": collapsed, "confirmed": h1}

    # -------------------------------------------------------- H2 determinism
    print("\n" + "=" * 76)
    print("2.  H2 — is transliteration DETERMINISTIC?")
    print("=" * 76)
    mismatch = 0
    for w in uniq:
        a, b = ti.transliterate(w), ti.transliterate(w)
        if a != b:
            mismatch += 1
    h2 = mismatch == 0
    print(f"  words giving different output on repeat calls : {mismatch}")
    print(f"\n  H2 {'CONFIRMED' if h2 else 'REFUTED'}")
    results["H2"] = {"nondeterministic_words": mismatch, "confirmed": h2}

    # ------------------------------------------------ H3 alignment integrity
    print("\n" + "=" * 76)
    print("3.  H3 — is CHARACTER ALIGNMENT RECOVERABLE?  [load-bearing]")
    print("     DEC-007 requires surface<->analysis offsets; DEC-022 makes them")
    print("     an API contract. Both assume alignment is computable.")
    print("=" * 76)
    ok = 0
    fails = []
    for w in uniq:
        whole = ti.transliterate(w)
        piecewise = "".join(ti.transliterate(c) for c in w)
        if whole == piecewise:
            ok += 1
        elif len(fails) < 8:
            fails.append((w, whole, piecewise))
    rate = 100 * ok / len(uniq)
    h3 = rate >= 99.0
    print(f"  words where whole-string == concat(per-character) : {ok}/{len(uniq)}"
          f"  ({rate:.2f}%)")
    if fails:
        print("\n  Examples where they DIFFER:")
        for w, a, b in fails:
            print(f"    {w!r}")
            print(f"      whole     : {a!r}")
            print(f"      piecewise : {b!r}")
    print(f"\n  H3 {'CONFIRMED' if h3 else 'REFUTED'} "
          f"({rate:.2f}% {'>=' if h3 else '<'} 99%)")
    results["H3"] = {"alignable": ok, "total": len(uniq),
                     "rate_pct": round(rate, 3),
                     "examples": [{"word": w, "whole": a, "piecewise": b}
                                  for w, a, b in fails],
                     "confirmed": h3}

    # --------------------------------------------------- H4 round-trip token
    print("\n" + "=" * 76)
    print("4.  H4 — is TOKENIZATION losslessly REVERSIBLE?")
    print("=" * 76)
    tok = Tokenizer(models.BPE(unk_token="[UNK]"))
    tok.pre_tokenizer = pre_tokenizers.ByteLevel(add_prefix_space=False)
    tok.decoder = __import__("tokenizers").decoders.ByteLevel()
    tok.train_from_iterator(
        [" ".join(words)],
        trainers.BpeTrainer(vocab_size=2000, special_tokens=["[UNK]"],
                            show_progress=False, min_frequency=1))
    bad_rt, unk = 0, 0
    for w in uniq:
        enc = tok.encode(w)
        unk += sum(1 for t in enc.tokens if t == "[UNK]")
        if tok.decode(enc.ids) != w:
            bad_rt += 1
    rt = 100 * (len(uniq) - bad_rt) / len(uniq)
    h4 = rt >= 99.0
    print(f"  words where decode(encode(w)) == w : {len(uniq)-bad_rt}/{len(uniq)}"
          f"  ({rt:.2f}%)")
    print(f"  [UNK] tokens produced              : {unk}")
    print(f"\n  H4 {'CONFIRMED' if h4 else 'REFUTED'}")
    results["H4"] = {"roundtrip_ok": len(uniq) - bad_rt, "total": len(uniq),
                     "rate_pct": round(rt, 3), "unk_tokens": unk, "confirmed": h4}

    # ----------------------------------------------------- coverage context
    print("\n" + "=" * 76)
    print("5.  Coverage — what fraction of corpus characters can be analysed?")
    print("=" * 76)
    chars = Counter(c for w in uniq for c in w)
    mapped = sum(n for c, n in chars.items() if ti.transliterate(c) != c)
    total = sum(chars.values())
    print(f"  distinct characters in corpus       : {len(chars)}")
    print(f"  character tokens transliterated     : {mapped:,}/{total:,}"
          f"  ({100*mapped/total:.2f}%)")
    passthru = [c for c in chars if ti.transliterate(c) == c]
    print(f"  distinct characters passing through : {len(passthru)}"
          f"{'  -> ' + ' '.join(passthru[:12]) if passthru else ''}")
    results["coverage"] = {"distinct_chars": len(chars),
                           "char_tokens_transliterated": mapped,
                           "char_tokens_total": total,
                           "pct": round(100 * mapped / total, 3),
                           "passthrough_chars": passthru}

    # ------------------------------------------------------------- summary
    print("\n" + "=" * 76)
    print("SUMMARY")
    print("=" * 76)
    for h in ("H1", "H2", "H3", "H4"):
        print(f"  {h}: {'CONFIRMED' if results[h]['confirmed'] else 'REFUTED'}")
    intrinsic_ok = all(results[h]["confirmed"] for h in ("H1", "H2", "H4"))
    print(f"\n  Intrinsic evaluation viable for Tier 0: "
          f"{'YES' if intrinsic_ok else 'NO'}")
    print(f"  Alignment (DEC-007/DEC-022) sound     : "
          f"{'YES' if results['H3']['confirmed'] else 'NO — needs a real design'}")

    RESULTS.write_text(json.dumps(results, ensure_ascii=False, indent=2))
    print(f"\n  Wrote {RESULTS.name}")


if __name__ == "__main__":
    main()
