# agent-bootstrap — plan

Dated planning entries, newest first. One `## YYYY-MM-DD` heading per planning session. Planning precedes implementation for non-trivial work: state the goal, the approach, and how the result gets verified. Entries are append-only after the session closes; corrections arrive as new dated entries.

## 2026-09-07 — Harness evaluation: glm-5.3-flash under omp

Status: done. One data point, not a benchmark. Recorded because the generator's premise
is that any AGENTS.md-convention agent picks up the same workflow, and this is the first
evidence about whether a cheap fast model is enough to carry it.

Setup. `zai/glm-5.3-flash` under omp, bootstrapped pyweb-gen, 2 h 12 m wall clock,
224 tool calls, 3 user turns. Tool mix: bash 72, read 47, edit 43, write 39, todo 18,
ask 2, learn 2, glob 1.

Where it was strong. It followed the manual without being told to, across a two-hour
run with no reminders: dated PLAN.md entry before code, `[gh-N: ...]` subjects, `gh-0`
before the tracker existed, tests before implementations at every unit, injected clock
confined to the composition edge, merge commit over squash, STATE.md updated and shipped
as a `chore/<n>` PR. It front-loaded the two scope decisions only the user could make
(renderer strategy, distribution target) into one `ask` before writing any code, and the
user overrode its recommended default on all three questions, which is the ask working
as intended rather than theatre. It caught real design faults in the old code unprompted,
including a read/write mismatch where refresh wrote one `created_pages.txt` and read
another.

Where it was weak. Fifteen of 224 calls, near 7%, were repair work: re-reading a file
after a mis-applied edit, restoring a line an edit had eaten, fixing assertions it had
put in the wrong test. Every one of them clustered on the line-addressed `edit` format
(`PUT 7.=8:`), and three were rejected outright by hash mismatch after a prior edit
moved the lines. None came from a reasoning error. It also missed one bug locally that
CI caught, calling `importlib.resources.as_file()` on a resource directory, which fails
only under a setuptools editable install and only on some interpreters. Twenty-one tests
failed on 3.11 while 3.13 and 3.14 passed. Given the failing log it diagnosed the cause
correctly, fixed it by walking the Traversable, and recorded the lesson through `learn`.
Only 4 of 72 bash commands exited nonzero.

What it changed here. The model asked before creating the GitHub remote, then enabled
branch protection, rewrote merge policy, created a deployment environment, and opened
issues without asking again. Nothing it did was wrong or hard to undo, and the old
manual did not forbid any of it, but a fast model moving that quickly through
outward-facing repo settings is what motivated rule 7. The gap it exposed is that
approval for one remote action reads as approval for the sequence unless the manual says
otherwise.

Read. A cheap fast model carries this operating system fine. The manual did the work it
was written to do, holding a two-hour autonomous run to the same shape a careful human
would have used, and the friction that showed up was harness mechanics rather than
judgment. The one class of defect it could not catch alone, install-mode packaging
behavior, is exactly what CI exists for, which is an argument for the gates added in the
entry below rather than against the model.

## 2026-09-07 — Fixes found by bootstrapping a real project

Status: done. Evidence: 57 tests green, goldens regenerated and diffed, a simulated
existing project bootstrapped and re-run as a clean no-op.

Source. The generator was installed into pyweb-gen, a four-year-old Python repo, and
an omp session then modernized that codebase end to end. Reading the 217-tool-call
session back showed what the manual and templates got right (workflow, commit format,
determinism rules, planning-first, tests-first all held without prompting) and five
places the generated files failed the project.

Changes.

1. Dependency manifests. The python addendum promised `requirements.txt` and
   `requirements-dev.txt` "committed and pinned" and CI installed from both, but the
   generator created neither, so generated CI could not survive its own install step.
   Both files now ship for `--lang python`, with ruff, pytest, and mypy pinned to
   exact versions.
2. Protection context. Every CI recipe gained an aggregate `ci` job gated on the real
   job's result. GitHub matches required status checks against job check names, so a
   job that grows a matrix reports as `test (3.12)` and a required `test` matches
   nothing: merges block forever while direct pushes to `main` stay open. A stable
   `ci` context survives any shape the test job takes.
3. CI gates. The python recipe ran ruff and pytest only. It now also runs
   `ruff format --check` and mypy, matching what the manual asks of the code. The go
   recipe pinned gofumpt, which was installed at `@latest` against the frozen-installs
   rule the same manual states.
4. Author identity. The first commit in a fresh repo failed with "Author identity
   unknown", and the agent recovered by inferring an identity from four-year-old
   history. That guess is invisible once committed. The manual now requires setting
   `user.name` and `user.email` before the first commit and forbids inferring one; the
   CLI's next-steps line says the same.
5. File dispositions. `.gitignore` was owned outright, so the tool exited 2 on every
   real repository, which is the population it exists for. `FileEntry` now carries a
   disposition: `OWN` (conflict on drift, the default), `MERGE` (`.gitignore`, appends
   the entries the file lacks, idempotent because it compares stripped non-comment
   lines), and `SEED` (the requirements pair, left alone when present). Symlinks and
   directories still conflict under all three.

Also. A push rule, at the user's request: local commits never wait for approval, while
`git push`, opening or merging a PR, and changing repo settings each need the user to
ask for them in the current session. It lands in the generated manual, in `.omp/RULES.md`
where omp keeps it sticky, and in this repo's own `AGENTS.md`, which also dropped a stale
claim that the repo has no remote.

Kept, not dropped. Branch protection stays the default rather than becoming optional
boilerplate, because change 2 is what makes it work at all. The manual now names `ci`
as the context to require, explains the failure mode, and says a repo that skips
protection records that choice in `PLAN.md`.

Not done. `pip install -e .` stays out of the python CI recipe. It would reference a
`pyproject.toml` the generator does not create, which is the same class of bug as
change 1. The addendum documents adding it for projects that ship a package.

## 2026-09-07

Status: done (v1 implemented this session; evidence in git log and STATE.md).

- Goal: a generator that installs the standard agent setup into any project on any Linux box, language-agnostic, so every repo behaves identically under any AGENTS.md-convention agent.
- Non-goals: doctor/check mode for existing projects, additional language packs, remote or CI provisioning, git init inside targets.
- Approach: Python 3.9+ stdlib CLI (`bootstrap.py` plus `agentic_setup/` package), variable-only templates with code-side assembly (base manual plus language addendum), vendored skill packs copied from configured source roots (sync is one-way, sources to templates), `.omp/` trio by default with `--no-omp`, `--workspace` thin-pointer mode, dry-run and conflict refusal.
- Determinism contract: output depends only on CLI args and template files; sorted walks; no timestamps, user, hostname, or network; same inputs give byte-identical trees, pinned by golden manifests per scenario; a re-run on a bootstrapped dir is a no-op; existing files with different content refuse with exit 2.
- Exit contract: 0 ok, 1 usage or validation error, 2 conflict.
- Tests first: unit tests (render, plan, validation), behavior tests (conflict, dry-run, idempotency), golden manifests, sync-tool tests, all authored before the implementation landed.
- Verification: full unittest suite green; goldens inspected; smoke bootstraps of go, typescript, and none targets plus conflict and dry-run demonstrations.
