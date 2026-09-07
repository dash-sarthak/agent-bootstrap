# agent-bootstrap — plan

Dated planning entries, newest first. One `## YYYY-MM-DD` heading per planning session. Planning precedes implementation for non-trivial work: state the goal, the approach, and how the result gets verified. Entries are append-only after the session closes; corrections arrive as new dated entries.

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
