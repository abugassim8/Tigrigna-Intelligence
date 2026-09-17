# Working on this project locally, in Cursor

**Why this document exists.** Every command that touches the model has had to
run on the owner's machine and come back as pasted terminal output, because
the Hugging Face host is unreachable from the assistant's environment. That
round trip is the single biggest cost this project has paid; running Claude Code
locally removes it.

⚠️ **The blocker was never the repository.** 187 tests, 89 planted cases, four
checkers and every `--self-test` already run with no network at all.
`huggingface.co` is blocked from the assistant's environment by **org egress
policy** (`CONNECT tunnel failed, response 403`) — a standing policy, not an
outage, and not something to route around. `download.pytorch.org` is blocked the
same way. On a local machine neither applies.

## Setup, in order

**1 · Cursor** — install it, then **open the folder** `C:\dev\Tigrigna-Intelligence`
(open the folder, not a single file, or the tooling will not see the repository).

**2 · Interpreter** — `Ctrl+Shift+P` → *Python: Select Interpreter* →
`.venv\Scripts\python.exe`.

**3 · Claude Code** — in Cursor's terminal:

```
npm install -g @anthropic-ai/claude-code
claude
```

Node 18 or newer. Authenticate when prompted. It reads `CLAUDE.md` from the
repository root automatically — that file holds the rules this project runs on.

**4 · `HF_TOKEN`** — set it persistently, then **open a new terminal**:

```
setx HF_TOKEN "your-token-here"
```

⚠️ **The value goes in the environment and nowhere else.** Never in a file,
never in a commit, never pasted into a chat window. `check_environment.py`
reports only whether one is set, never what it is.

⚠️ Worth doing even though the model is already downloaded: an unauthenticated
Hub request was measured at **57 kB/s**, about 47 hours for this checkpoint.

**5 · Packages**

```
pip install -e services/primitives -e "services/evaluation[dev]" -e "services/translation[dev]"
```

Add `-e "services/translation[madlad]"` for `torch` and `transformers` when you
need the model.

**6 · Confirm**

```
python scripts/check_environment.py
```

One command, one verdict, and it names exactly what is missing. It **reports and
never installs** — a setup script that installs is how a machine silently
diverges from CI, and this project lost a day to a `transformers` downgrade that
broke the `tokenizers==0.23.1` pin.

⚠️ It does **not** load the model, by design. That costs ~6 GB and belongs to
`repair_lm_head.py`; a readiness check that needs 6 GB stops being run (DEC-008).

## The model, on a 16 GB machine

The checkpoint is **float32, 11.76 GB**, and loading it exhausted the Windows
commit limit — `OSError: The paging file is too small for this operation to
complete. (os error 1455)`. Convert it once:

```
python scripts/shrink_checkpoint.py
python scripts/repair_lm_head.py --model models/madlad400-3b-mt-bf16
```

**11.76 GB → 5.88 GB.** No download, no restart. ⚠️ Read the **control
languages** before the Tigrinya: fluent Spanish and German mean the pipeline
works, and poor Tigrinya after that is a finding about coverage rather than a
bug.

The alternative is raising the pagefile (`sysdm.cpl` → Advanced → Performance
Settings → Advanced → Virtual memory), which needs a restart and leaves every
future load at 11.76 GB.

## Before committing

The six commands in `CLAUDE.md`, all green. `scripts/tests/test_plants.py` is
the slow one — minutes, ~89 subprocesses — and is deliberately not run by
`check_environment.py`.

## What still needs a person

⚠️ **Not listed here.** `ACTIONS.md` is the register, and
`docs/roadmap/READINESS_PLAN.md` is the order. A copy of that list in a second
document goes stale — `CLAUDE.md` managed it within a day of being written.
