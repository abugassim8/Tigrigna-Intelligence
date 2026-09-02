# Research Access Playbook

## Purpose of this document

A map of **which information sources are actually reachable** from a working
session on this project, which are blocked, and what the working routes around
each block are.

## Why this document exists

In the 2026-07-29 session roughly a third of the research effort went into
*discovering how to reach sources* rather than reading them. Several primary
sources were blocked; a workaround was eventually found; and without this file
the next session would repeat the entire discovery process from scratch.

That is exactly the waste `AI_RESEARCH_RULES.md` exists to prevent — applied to
tooling rather than findings. **An access route is a research finding.**

**How to use it:** Read this before starting a research task. Use the working
routes. Do not re-probe the blocked list unless you have reason to think the
policy changed.

**What future contributors should add:** New routes as you find them. New blocks
as you hit them. Correct anything here that has changed — and date your
corrections, because access policy is environment-specific and time-varying.

> ⚠️ **Environment-specific.** This describes the Claude Code remote execution
> environment used on 2026-07-29. A session on a different machine, network, or
> egress policy may see something completely different. **Verify before
> trusting; treat this as a strong prior, not a guarantee.**

---

## ✅ Working routes

### Hugging Face MCP + `hf://` filesystem — the highest-value route

The single most useful discovery of the Phase 1–2 sessions. It reaches
model cards, dataset cards, **and paper metadata**, and is **not** subject to the
egress block that stops `arxiv.org` directly.

| Need | Call |
| --- | --- |
| Find models/datasets | `hub_repo_search` — filter by `author`, sort by `downloads` |
| Params, licence, downloads | `hub_repo_details` |
| **Read a full model/dataset card** | `hf_fs cat hf://models/OWNER/NAME README.md` |
| **Read a paper abstract** | `hf_fs cat hf://papers/ARXIV_ID/metadata.json` |
| Find papers by topic | `hf_fs search hf://papers "QUERY"` |

**The card is far richer than the API metadata.** `hub_repo_details` on
`fgaim/tiroberta-base` returns no licence; the card itself confirms the licence
is genuinely absent *and* reveals the 40M-token training corpus. **Always read
the card, not just the metadata.**

⚠️ `hf://papers` only indexes papers linked to Hub artefacts. The Tigrinya NLP
survey (2507.17974) and MoVoC (2509.08812) are **not** there. Coverage is
partial — absence from `hf://papers` is not absence from the literature.

### PyPI — reachable directly, and underrated

`pypi.org` and `files.pythonhosted.org` are in the proxy's **no-proxy list**, so
they are reachable by plain `curl` and by `pip`.

```bash
curl -sS "https://pypi.org/pypi/<package>/json"    # metadata + full description
```

This gives version history, **last release date** (a maintenance signal), licence,
homepage, and the full README. It is often the fastest way to answer "is this
project alive?" when GitHub is unreachable.

**Better still: you can install and run the thing.** Experiment 001 verified
Epitran's Tigrinya support empirically — coverage, collisions, expansion factor —
in a venv, in seconds. **Prefer measuring a library to reading about it.**

### WebSearch

Works. Returns titles, URLs, and substantive summaries. Reliable for *discovering*
what exists and for author/venue/ID metadata.

⚠️ **Its summaries of papers are second-hand and have been wrong.** The TiQuAD
"81% F1" figure came from a search summary and was contradicted by the primary
dataset card (actual: 56–62 F1). **Mark search-derived figures `[reported]` and
verify anything load-bearing.**

### `curl` to non-blocked hosts

`raw.githubusercontent.com` responds (200) — this is how HornMT was obtained.
Note the repo-scope restriction below before using these.

> ⚠️ **Re-measured 2026-09-01, and two entries changed.** This page was written
> on 2026-07-29 and not re-checked for a month, while five actions in the
> register were justified by it.
>
> | Route | 2026-07-29 | 2026-09-01 |
> | --- | --- | --- |
> | `raw.githubusercontent.com` | ✅ | ✅ **200** |
> | `api.github.com` | ✅ 200 | ❌ **403** — use `raw.` or the GitHub MCP |
> | PyPI | ✅ | ✅ **`torch` and `sentence-transformers` install** |
> | `huggingface.co` direct download | *(untested)* | ❌ **connection refused** — the MCP reads metadata and text files, but **weights cannot be fetched** |
> | `opus.nlpl.eu` | *(untested)* | ❌ blocked |
> | `tico-19.github.io` | *(untested)* | ❌ blocked |
>
> **The consequence for A-09.** "Egress is blocked" was one blocker covering two
> different things. *Reading about* models — licences, cards, provenance,
> parameter counts — is open through the MCP and was open the whole time.
> *Running* them is not: PyPI gives us the runtime, and nothing gives us the
> weights. **A-09 is now only the second half.**
>
> Separately, `openlanguagedata/flores_plus` returns **401** rather than a proxy
> denial — it is a **gated repo**, not an egress block, and a token fixes it
> (**A-08**).

---

## ❌ Blocked — do not retry

These returned **403 at the proxy CONNECT level** on 2026-07-29. Per
`/root/.ccr/README.md`, proxy 403/407 are organisation egress-policy denials:
**do not retry and do not route around them — report them.**

| Host | Consequence |
| --- | --- |
| `arxiv.org` | No paper PDFs or abstracts directly |
| `aclanthology.org` | No ACL/EMNLP/COLING papers |
| `api.semanticscholar.org` | No metadata fallback |
| `huggingface.co/papers` (web) | Use `hf://papers` via MCP instead — that works |
| MDPI, Springer, Nature | No publisher-hosted papers |
| `en.wikipedia.org` | No general reference |
| `www.ethnologue.com` | No authoritative language demographics |
| `*.github.io` (tested: `tigrinyanlp.github.io`) | Community documentation sites unreachable |

**Practical effect on this project:** every claim sourced from a paper is
`[reported]`, not `[verified]`, unless it also appears on a Hugging Face card or
in `hf://papers`. This is why the evidence-marking convention exists.

### `add_repo` — cross-owner adds are refused

```
add_repo: cross-tier adds are not supported in v1: requested "hltdi/hornmorpho"
but session already has repos from owner(s) [abugassim8]
```

A session scoped to `abugassim8/*` **cannot** attach a third-party repository.
Combined with the standing instruction not to read repositories outside session
scope, **direct GitHub inspection of external dependencies is unavailable.**

**Workarounds that do work:**
- **PyPI** — if the project ships a package, metadata and releases are readable,
  and you can install and test it.
- **WebSearch** — surfaces README content, forks, and version numbers.
- If GitHub inspection is genuinely required, it needs a session started with
  that repo as an initial source.

**Live example:** HornMorpho could not be inspected on GitHub. PyPI showed it is
**not published there at all** (itself a finding — GitHub-only distribution, no
versioned releases through standard channels), and WebSearch supplied the version
(5.3.5), language coverage, and the existence of a `fgaim` fork.

> ⚠️ **Superseded 2026-09-01.** `raw.githubusercontent.com` responds, and
> `LICENSE.txt` fetched directly settles it: **GPL-3.0**. The workaround above
> was a good workaround for a restriction that had **stopped applying**. Worth
> keeping as the method, and worth noting as the cost: a fallback route that
> works becomes a reason never to re-test the direct one.

---

## Evidence marking convention

Used throughout `docs/research/`. It exists because the access situation forces
two very different confidence levels:

| Marker | Meaning |
| --- | --- |
| `[verified]` | Read from a primary artefact this session — HF card, `hf://papers` metadata, PyPI JSON, or **measured by running code** |
| `[reported]` | From a search-engine summary of a source that could not be opened |
| `[unverified]` | Plausible, from background knowledge, not confirmed |

**Never blur these.** A `[reported]` figure has already been wrong once on this
project in a way that would have propagated into a decision.

---

## Recommended research sequence

Cheapest and most reliable first:

1. **`docs/research/summaries/`** — it may already be answered. Free.
2. **`hf://` + HF MCP** — primary artefacts, `[verified]`.
3. **PyPI** — maintenance signals; and *install and measure* rather than read.
4. **WebSearch** — discovery and metadata; mark `[reported]`.
5. **Direct `curl`** — for hosts not on the blocked list.
6. **Record the outcome here** if you learn something new about access.

## Standing verification backlog

Sources that need re-checking from a session with unrestricted egress:

- **arXiv 2507.17974** — the Tigrinya NLP survey. Highest-value single source;
  never read.
- **arXiv 2509.08812** — MoVoC, including the 21→6 fertility example.
- **ACL 2023 TiQuAD paper** — to resolve the baseline discrepancy (card says
  F1 56–62; a search summary claimed 81%).
- **CoDET** (2305.17267) — the COMET 0.82/0.80 dialect figures behind DEC-004.
- **TiNC24** — the reported 200K-word NER corpus, never located.
- **`tigrinyanlp.github.io`** — a Tigrinya NLP resource hub, blocked.
- ~~**HornMorpho on GitHub**~~ ✅ **resolved 2026-09-01** — **GPL-3.0**, v5.3.6
  (April 2026), Tigrinya and Tigre supported, not on PyPI, and `setup.py`
  declares no licence metadata at all.
