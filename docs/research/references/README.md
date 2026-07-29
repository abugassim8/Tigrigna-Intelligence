# References

## Purpose of this document

A shared bibliography for the project: papers, open source projects, datasets,
documentation, and other sources encountered during research.

## Why this directory exists

Two reasons.

**Finding sources is expensive.** Locating the handful of papers that address
Tigrinya or Ethio-Semitic NLP, or the one maintained library that handles Ge'ez
script correctly, takes real effort. Doing that search twice is pure waste. A
shared reference collection means each source is found once.

**Claims need provenance.** Every non-obvious factual claim in this repository
should trace back to a source recorded here. This is what separates a research
document from an opinion — and it lets a reader check anything they doubt
instead of taking it on trust.

## How to use this directory

**Before searching for sources:** check here. Someone may already have found what
you need — including sources that turned out to be useless, which saves you
evaluating them again.

**While researching:** add sources as you find them, not at the end. Sources
recorded at the end are the ones that get lost.

**When citing:** link to the entry here as well as inline in your report.

## Organisation

Suggested files, created as they accumulate content:

| File | Contents |
| --- | --- |
| `papers.md` | Academic papers — prioritise low-resource, Semitic, Ethio-Semitic, and Ge'ez-script work |
| `projects.md` | Open source projects, libraries, tools |
| `datasets.md` | Datasets, corpora, dictionaries, terminology resources |
| `models.md` | Models evaluated or considered, with licence and Tigrinya coverage |
| `standards.md` | Unicode, script, encoding, and linguistic annotation standards |
| `communities.md` | Research groups, communities, institutions, and individuals |
| `commercial.md` | Commercial products and APIs claiming Tigrinya support |

Split further as any file grows unwieldy.

## Entry format

```markdown
### [Short title]

- **Type:** Paper / Project / Dataset / Model / Standard
- **Link:**
- **Date:** publication or last-updated
- **Licence:** (for anything we might use — mandatory, see P-9)
- **Tigrinya relevance:** Direct / Ethio-Semitic / Low-resource general / Background
- **Summary:** 1–3 sentences on what it is and what it gives us
- **Verdict:** Useful / Partially useful / Not useful — **and why**
- **Cited in:** `reports/NN_domain/NNN-slug.md`
```

**The `Verdict` field is the one that saves the most time.** "Not useful — covers
Amharic only, no Tigrinya data or evaluation" stops the next person spending an
hour reaching the same conclusion.

## What future researchers should add

Every source encountered, including the disappointing ones. Record dead ends:
a paper that sounded relevant and was not, a library that claims Tigrinya support
and does not deliver it, a dataset that turned out to be unlicensed. Negative
findings about sources are findings (**P-13**).

Where a source is a link that may not survive — a forum post, a personal site, a
university page — note the access date and consider archiving it.

## Status

**Populated by Phase 1** (2026-07-29): `papers.md`, `models.md`, `datasets.md`,
`projects.md`, `communities.md`, `commercial.md`.

⚠️ **Access caveat:** arxiv, ACL Anthology, publisher domains, and Semantic
Scholar were blocked by egress policy during the Phase 1 session. Paper entries
carry titles, venues, and IDs (reliable) but their quoted findings are
`[reported]` from search summaries, not read from source. Hugging Face entries
are `[verified]` against the Hub API. **Verify before relying on precision.**
