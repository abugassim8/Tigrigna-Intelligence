# References — Open Source Projects

---

### HornMorpho

- **Type:** Project (library) · **Link:** https://github.com/hltdi/HornMorpho
- **Maintainer:** HLTDI (Indiana University)
- **Relevance:** **Direct — critical path**
- **Summary:** Morphological analysis, segmentation, **and generation** for
  Amharic, Oromo, and Tigrinya. Rule-based. Yields grammatical features plus
  stem and affixes.
- **Verdict:** **Very useful — the only established Tigrinya morphological
  analyser found.** But see risk below.
- ⚠️ **Maintenance status UNVERIFIED.** GitHub was not reachable in the
  2026-07-29 session. A single-lab academic project is a classic abandonment
  risk, and this sits on our critical path.
  **Verifying this is a top action item.**
- **Licence:** Not verified.

### TiQuAD

- **Type:** Project + dataset · **Link:** https://github.com/fgaim/TiQuAD
- **Relevance:** Direct · **Licence:** CC-BY-SA-4.0 (per HF dataset card)
- **Verdict:** **Useful** — the QA benchmark, ACL 2023 Outstanding Paper.

### flores-OLDI (FLORES+)

- **Type:** Project · **Link:** https://github.com/avidale/flores-OLDI
- **Relevance:** High — MT evaluation
- **Summary:** Community-maintained continuation of the FLORES MT benchmark
  under the Open Language Data Initiative.
- **Verdict:** **Useful** — likely access route for the Tigrinya FLORES split.
- **Note:** `[reported]` there is published work on *correcting* FLORES for four
  African languages (arXiv 2409.00626) — check whether Tigrinya is among them
  before trusting the split blindly.

### Morfessor

- **Type:** Project · **Relevance:** Low
- **Verdict:** **Not useful as a starting point.** `[reported]` unsupervised
  statistical segmentation performs **poorly** on Tigrinya compared to
  linguistic rule-based approaches. Recorded so the experiment is not repeated
  (**P-13**).

---

## Not found

- No open source **Tigrinya API server**, **MCP server**, or **SDK**.
- No open source **Tigrinya spell checker** library (consumer apps exist — see
  `commercial.md`).
- No open source **Tigrinya grammar checker**.
- No open source **Tigrinya knowledge graph** or entity-linking tooling.

**This absence is the project's opportunity** and is the basis of DEC-003.
