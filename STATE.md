# STATE.md — live session state

Updated at session close per AGENTS.md. Facts only; history lives in git log, backlog lives in GitHub issues. omp sessions get this auto-injected; every other agent reads the file.

## Repo and location

agent-bootstrap, git repo on branch `main`, in sync with `origin`
(github.com/dash-sarthak/agent-bootstrap, public). Branch protection is not enabled and
this repo ships no CI workflow of its own, so commits still land directly on `main`
under `gh-0`. Stack: Python 3.9+ stdlib only, stdlib unittest, golden-manifest
determinism tests. 57 tests, green.

`pyweb-gen/` sits inside this working tree as a separate repo with its own remote. It is
gitignored here, so it stays out of this repo's history.

## Last merged

No PRs; this repo has never used one. `main` and `origin/main` are both at `f73e38c`,
which carries the five generator fixes and the push rule from the pyweb-gen field test.
Commit subjects before that point predate the `[gh-N: ...]` convention this repo now
states, so do not read the older log as a style example.

## In flight

Nothing unmerged. Working tree clean.

## Field test: pyweb-gen

github.com/dash-sarthak/pyweb-gen, a 2022 Python repo, is the first real install of this
generator and the source of every change in `f73e38c`. Bootstrapped with `--lang
python`, then modernized end to end by one omp session (224 tool calls,
`zai/glm-5.3-flash`), now at v2.0.0 with 34 tests and ruff, ruff format, and mypy strict
green. Two PRs merged, issue #2 open to tag v2.0.0 for PyPI.

What the generated files got right, unprompted: the manual loaded through the
`.omp/AGENTS.md` pointer without an explicit read, and the session followed
planning-first, tests-first, `[gh-N: ...]` subjects, `gh-0` before the tracker existed,
merge commits over squash, injected clocks with UTC everywhere, and a `chore/<n>` PR at
session close.

What it got wrong is the newest `PLAN.md` entry: missing requirements files, a branch
protection context that matched no job, CI gates the manual asks for but the recipe
skipped, a first commit that failed on unset author identity, and `.gitignore` owned so
strictly the tool refused every real repository. All five are fixed.

Harness performance is a `PLAN.md` entry of its own, dated the same day. Headline: a
cheap fast model carried the manual unassisted for two hours, 224 tool calls, 3 user
turns, 4 of 72 bash commands exiting nonzero. Roughly 7% of calls were repair work, all
of it clustered on omp's line-addressed edit format rather than on reasoning. The one
defect it could not catch locally was install-mode packaging behavior, which CI caught.

Machine note, not a generator bug: this is NixOS, so pip-installed console scripts in a
venv fail with "cannot run dynamically linked executables". Use `.venv/bin/python -m
<tool>` or the system binary. The addendum's `.venv/bin/ruff` form does not run here,
though it is correct for CI.

## Open questions for the user

1. Should this repo get a CI workflow of its own, running the suite it ships? Branch
   protection needs one before `ci` can be a required context.

## Next action

1. Add CI for this repo, then enable branch protection with `ci` as the required
   context and stop committing directly to `main`.
2. Second field test in another language. Go and TypeScript got the same aggregate `ci`
   job as Python but have never been run against a real project, so the equivalent of
   the requirements-file gap may still be hiding in either.
3. Reconcile the go and typescript addenda against their CI recipes the way the python
   pair now is. The python gap was a promise in the addendum that the generator never
   kept; nothing has checked whether the other two make the same kind of promise.
