#!/usr/bin/env python3
"""
Experiment 008 — What must a Tigrinya embedding model beat?

**Tier 1 cannot be built until embeddings can be evaluated (P-4), and no
Tigrinya similarity benchmark exists.** DEC-023 solved this for three of four
primitives by measuring intrinsic properties and explicitly excluded embeddings.
DEC-026 extends the method; this experiment establishes the floor.

`tiroberta-bi-encoder` is **124.6M parameters** and would roughly double Tier 1's
footprint. Under **P-6** and **P-7** the question is therefore not "does it
work?" but **"does it beat something free?"** — so a character n-gram TF-IDF
encoder is measured first, and its numbers are the bar.

Hypotheses — pre-committed
--------------------------
**H1 — The lexical baseline passes the mechanical properties.** Self-retrieval,
discrimination and corruption monotonicity are about being a functioning
encoder, not about Tigrinya. *Prediction:* E2, E3, E4 all pass.

**H2 — The lexical baseline FAILS orthographic invariance.** Character n-grams
have no notion that ጸ and ፀ are the same letter, and a short word's n-grams
mostly change when one character does. *Prediction:* E1 well below the 0.80
floor — this is the specific job a real model has to do.

**H3 — Character n-grams are partially order-sensitive.** They look order-blind,
but padded n-grams span word boundaries, so shuffling destroys some.
*Prediction:* E5 strictly between 0 and 0.5.

**H4 — The checks discriminate.** Each gated property fails for a model built to
fail it and passes for one built to pass it. *Prediction:* a constant-vector
encoder fails E2/E3/E4; an encoder that normalises before embedding passes E1.

Reproduce:
    pip install -e services/primitives -e services/evaluation
    python3 run.py

Deterministic. Emits results.json per DEC-016.
"""

import json
import pathlib

from tigrinya_primitives import normalise
from tigrinya_eval.embeddings import (
    CharNgramEmbedder, evaluate_embeddings,
)

HERE = pathlib.Path(__file__).parent
RESULTS = HERE / "results.json"
CORPUS = HERE.parent / "003-metric-validity" / "data" / "flores_ti.txt"


class NormalisingEmbedder:
    """Control: normalises before embedding, so E1 is satisfied by construction.

    Exists to prove E1 *can* pass. A check only ever seen failing is as
    uninformative as one only ever seen passing.
    """

    def __init__(self, inner):
        self.inner = inner

    def embed(self, text):
        return self.inner.embed(normalise(text))

    def similarity(self, a, b):
        return self.inner.similarity(a, b)


class ConstantEmbedder:
    """Control: every sentence gets the same vector.

    The classic symptom of broken pooling or an untrained head — and the thing
    an intrinsic suite exists to catch before it reaches production.
    """

    def embed(self, text):
        return {"constant": 1.0}

    def similarity(self, a, b):
        return 1.0


def main():
    refs = [l.strip() for l in CORPUS.read_text(encoding="utf-8").splitlines()
            if l.strip()]
    baseline = CharNgramEmbedder().fit(refs)

    print("=" * 76)
    print(f"EXPERIMENT 008 — embedding baseline ({len(refs)} sentences)")
    print("=" * 76)

    models = [
        ("char-ngram TF-IDF (the floor)", baseline),
        ("normalising control", NormalisingEmbedder(baseline)),
        ("constant-vector control", ConstantEmbedder()),
    ]

    reports = {}
    for name, model in models:
        r = evaluate_embeddings(model, refs, name=name)
        reports[name] = r
        print("\n" + r.report().split("\n\n")[0])
        for res in r.results:
            print(f"  {res}")
        print(f"  VERDICT: {'PASS' if r.holds else 'FAIL'}")

    base = {r.name.split()[0]: r for r in reports["char-ngram TF-IDF (the floor)"].results}
    norm = {r.name.split()[0]: r for r in reports["normalising control"].results}
    const = {r.name.split()[0]: r for r in reports["constant-vector control"].results}

    # ------------------------------------------------------------ hypotheses
    h1 = all(base[k].holds for k in ("E2", "E3", "E4"))
    h2 = not base["E1"].holds
    h3 = 0.0 < base["E5"].value < 0.5
    h4 = (not const["E2"].holds and not const["E3"].holds
          and not const["E4"].holds and norm["E1"].holds)

    print("\n" + "=" * 76)
    print("HYPOTHESES")
    print("=" * 76)
    print(f"  H1 baseline passes E2/E3/E4          : "
          f"{'CONFIRMED' if h1 else 'REFUTED'}")
    print(f"  H2 baseline FAILS E1 (invariance)    : "
          f"{'CONFIRMED' if h2 else 'REFUTED'}  — measured {base['E1'].value:.4f} "
          f"vs floor {base['E1'].floor:.2f}")
    print(f"  H3 partial order sensitivity         : "
          f"{'CONFIRMED' if h3 else 'REFUTED'}  — {base['E5'].value:.4f}")
    print(f"  H4 the checks discriminate           : "
          f"{'CONFIRMED' if h4 else 'REFUTED'}")

    print("\n" + "=" * 76)
    print("THE BAR FOR tiroberta-bi-encoder")
    print("=" * 76)
    print(f"  {'property':<28} {'baseline':>10}  must be")
    for k in ("E1", "E2", "E3", "E4", "E5"):
        r = base[k]
        need = "advisory" if r.advisory else f">= {r.floor:.2f}"
        print(f"  {r.name:<28} {r.value:>10.4f}  {need}")
    print("\n  E1 is where the neural model has to earn its 119 MB. The baseline")
    print(f"  scores {base['E1'].value:.4f} against a floor of {base['E1'].floor:.2f}, so a model")
    print("  that merely matches the baseline on E1 is not worth deploying.")
    print("\n  ⚠️ Nothing here has been run against a neural model — the weights")
    print("  are behind the egress policy (A-09). This is the bar, not a result.")

    results = {
        "corpus_sentences": len(refs),
        "H1_baseline_passes_mechanical": h1,
        "H2_baseline_fails_invariance": h2,
        "H3_partial_order_sensitivity": h3,
        "H4_checks_discriminate": h4,
        "models": {name: r.to_dict() for name, r in reports.items()},
        "bar_for_neural_model": {
            k: {"baseline": round(base[k].value, 6),
                "floor": base[k].floor,
                "gated": not base[k].advisory}
            for k in ("E1", "E2", "E3", "E4", "E5", "E6")
        },
        "not_yet_measured": "tiroberta-bi-encoder — weights blocked by A-09",
    }
    RESULTS.write_text(json.dumps(results, ensure_ascii=False, indent=2))
    print(f"\n  Wrote {RESULTS.name}")


if __name__ == "__main__":
    main()
