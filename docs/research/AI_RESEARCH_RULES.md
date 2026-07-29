# AI Research Rules

## Purpose of this document

These are the **mandatory operating rules for AI assistants** working on the
Tigrinya Language Intelligence Platform. They are not style suggestions. They
exist because AI research sessions have a specific and predictable set of
failure modes — burning context re-deriving known facts, producing confident
recommendations without evidence, and quietly contradicting earlier decisions —
and each rule below targets one of them.

**How to use it:** Read this file at the start of every session, before doing
any work. Then follow it.

**What future contributors should add:** When a session goes wrong in a new way,
add a rule that would have prevented it. Rules earned from real failures are
worth more than rules invented in advance.

---

## Before you do anything

Future AI assistants working on this project **must**:

1. **Read [`PROJECT_CONTEXT.md`](../../PROJECT_CONTEXT.md) first.** Not skim —
   read. It defines the mission, the philosophy, and the standing constraints.
   Everything you produce is judged against it.

2. **Read [`../decisions/DECISIONS.md`](../decisions/DECISIONS.md) before making
   recommendations.** Recommending something that was already decided against —
   with reasons — wastes the user's time and undermines confidence in everything
   else you say. Also check
   [`../decisions/rejected_options.md`](../decisions/rejected_options.md).

3. **Never repeat completed research.** Search
   [`summaries/`](summaries/) and [`references/`](references/) before starting.
   If the topic has been covered, build on it or challenge it — do not redo it.
   If you genuinely must revisit prior research, say explicitly why the prior
   work is insufficient.

4. **Read [`RESEARCH_ACCESS.md`](RESEARCH_ACCESS.md) before searching for
   anything.** It maps which sources are reachable from this environment, which
   are blocked, and the working routes around each block. Roughly a third of one
   session's research effort went into rediscovering this. **An access route is a
   research finding** — if you learn something new about access, record it there.

5. **Check package registries before assuming you must build something.** PyPI
   is directly reachable, and you can install and *measure* a library rather than
   reading about it. This project has already had one **P-1 violation** caused by
   assuming "build" without checking: the Ge'ez decomposition layer DEC-007
   originally specified building already existed as `epitran`.

6. **Prefer summaries over full reports.** Read `summaries/` first, always. Open
   a full report only when the summary cannot answer the specific question you
   have. Loading a 40-page report to answer a question the 2-page summary
   already answered is exactly the waste this repository is structured to
   prevent.

---

## While you work

7. **Challenge assumptions.** Read
   [`../decisions/assumptions.md`](../decisions/assumptions.md) and treat it as a
   list of things that might be wrong, not a list of things that are true. If
   evidence contradicts a standing assumption, say so directly and prominently.
   An AI that only ever confirms the existing plan is not adding value.

8. **Compare alternatives.** Never present a single option as though it were the
   only one. Every recommendation must name what else was considered and why it
   lost. If you evaluated only one option, that is a finding about the state of
   your research, and you should report it as such.

9. **Include costs.** Money, compute, storage, and human time. Estimates are
   acceptable; silence is not. State your assumptions and show the arithmetic so
   someone can check it. "Roughly $200–400/month at 10k requests/day, assuming
   X" beats "cost-effective" every time.

10. **Include maintenance.** Who keeps this alive? What breaks when the upstream
   project stops being maintained, when the model is deprecated, when the API
   changes? Ongoing burden is a first-class cost and is routinely omitted — do
   not omit it.

11. **Include implementation details.** A recommendation that cannot be acted on
   is not a recommendation. Say what to install, what to run, what to configure,
   what the integration points are, and roughly how long it takes.

12. **Cite sources.** Every non-obvious factual claim needs a source: paper,
    repository, documentation page, benchmark. Add them to
    [`references/`](references/). If a claim comes from your own training rather
    than a verifiable source, label it as such — and remember that your training
    data has a cutoff and this field moves fast.

13. **Identify uncertainty.** State clearly what you do not know, what you could
    not verify, and what would change your conclusion. Distinguish these three:
    - "I verified this" — you checked a source this session.
    - "I believe this" — from training, plausible, unverified.
    - "I do not know this" — genuinely open.

    Blurring these is the most damaging thing you can do in a research document,
    because it destroys the reader's ability to calibrate on anything else you
    wrote.

---

## Output discipline

14. **Every full report ships with a ≤2-page summary.** The summary is not a
    courtesy; it is the artefact the next session will read instead of your
    report. Write it as though the report will never be opened again.

15. **Write for a stranger in eighteen months.** No unexplained references to
    "the earlier discussion." No assumed context. Documents must stand alone.

16. **Numbers over adjectives.** "Fast", "cheap", "high-quality", and "scalable"
    are not findings. Latencies, dollar figures, benchmark scores, and parameter
    counts are.

17. **Record negative results.** "No usable Tigrinya dataset exists for this
    task", "this library does not support Ge'ez script", "this model's Tigrinya
    output is unusable" — write these down. Unrecorded, they will cost someone
    the same search again.

18. **Separate what you found from what you recommend.** Findings are evidence;
    recommendations are judgement. Mark clearly which is which.

---

## What not to do

- **Do not design architecture before the research supports it.** Every document
  in `docs/architecture/` is currently a scaffold, deliberately.
- **Do not recommend training a model** unless you can articulate the
  proprietary advantage it creates and have costed the alternative of not
  training. The default answer is no; see `PROJECT_CONTEXT.md`.
- **Do not treat scope as roadmap.** The capability list in `PROJECT_CONTEXT.md`
  is what the platform may eventually do, not what is committed or sequenced.
- **Do not let this become a news or content application.** It is language
  infrastructure. Flag scope drift when you see it.
- **Do not invent benchmark numbers, dataset sizes, or model capabilities.** If
  you cannot verify a number, say the number is unverified. A plausible-looking
  fabricated figure is worse than an admitted gap, because it will be quoted.
- **Do not silently contradict a recorded decision.** If you think a decision is
  wrong, say so explicitly and argue it. That is welcome. Quiet contradiction is
  not.

---

## Session start sequence

```
1. Read PROJECT_CONTEXT.md
2. Read this file
3. Read docs/research/RESEARCH_ACCESS.md   <- how to reach sources
4. Read docs/decisions/DECISIONS.md and assumptions.md
5. Scan docs/research/summaries/ for prior work on your topic
6. Identify which stage you are in: Scout, Analyst, or Architect
7. Use the matching template from docs/research/templates/
8. Produce your output AND its summary
9. Record any new decision, rejection, or assumption
```

## Session end checklist

- [ ] Output written to the correct location using the correct template.
- [ ] A ≤2-page summary exists in `summaries/`.
- [ ] Sources cited and added to `references/`.
- [ ] New decisions recorded in `DECISIONS.md`.
- [ ] Rejected options recorded with reasons.
- [ ] New or invalidated assumptions recorded in `assumptions.md`.
- [ ] Uncertainty stated explicitly.
- [ ] `CHANGELOG.md` updated if project direction or structure changed.
