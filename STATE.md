# STATE.md — live session state

Updated at session close per AGENTS.md. Facts only; history lives in git log, backlog lives in GitHub issues. omp sessions get this auto-injected; every other agent reads the file.

## Repo and location

agent-bootstrap, local git repo at `~/Projects/agent-bootstrap`, branch `main`. No remote yet; commits use `gh-0` until a tracker exists. Stack: Python 3.9+ stdlib only, stdlib unittest, golden-manifest determinism tests.

## Last merged

Nothing yet (no remote, no PRs).

## In flight

Nothing unmerged.

## Open questions for the user

(none)

## Next action

1. Create the GitHub remote (private) and push `main`; enable branch protection (required status check `ci`, PRs required, merge commits, no squash), then stop using gh-0 commits.
2. Real-world use: bootstrap a scratch Go project and a scratch TypeScript project, work inside each once, and record friction as new dated PLAN.md entries.
