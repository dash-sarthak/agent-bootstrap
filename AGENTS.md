# agent-bootstrap

Bootstrap generator that installs the standard agent operating system into any project: `AGENTS.md` manual, `.agents/skills`, `.omp/` context, `STATE.md`, `PLAN.md`, a language addendum, and CI. Read `README.md` first for design rationale; this file is operational notes only.

## Commands

- Run tests: `python3 -m unittest discover -s tests -v` (stdlib only; Python 3.9+ floor, zero dependencies)
- Regenerate golden manifests after an intentional output change: `python3 tools/make_goldens.py`, then review the diff
- Sync vendored skills from sources: `python3 tools/sync_skills.py`, then review the diff
- Smoke run: `python3 bootstrap.py /tmp/demo --name demo --lang go`

## Testing notes

- Goldens live in `tests/golden/<scenario>/manifest.txt` as `<sha256>  <path>` lines. They pin byte-identical output; never hand-edit them, regenerate and review the diff.
- Determinism and idempotency tests run the CLI twice and compare trees. When they fail, a template or module reads ambient state (time, env, locale, hostname). Fix the cause, not the test.
- Tests call `agentic_setup.cli.main(argv)` directly. Only the entrypoint smoke test spawns a subprocess.

## Skill provenance

- `templates/skills/core` — vendored from `~/Projects/Passive Income/toolbase/.agents/skills` (9 skills) and `~/.agents/skills` (4: diagnosing-bugs, resolving-merge-conflicts, research, technical-writing)
- `templates/skills/typescript` — typescript-clean-code from toolbase
- `templates/skills/web` — web-design and seo-optimization from toolbase
- `templates/skills/go` and `templates/skills/python` — written here; this repo is their canonical home
- Sync is one-way, sources to templates, via `tools/sync_skills.py`. Never edit vendored copies directly; edit the source repo and sync. Excluded on purpose: find-tool-ideas (passive-income specific), chrome-cdp (workstation-specific), political-* and entity-linking (domain-specific).
- This repo's own `.agents/skills/*` are relative symlinks into `templates/skills/core`, so agents working here see the same skills they will install.

## Conventions

- Branches: `feature/<n>`, `bug/<n>`, `chore/<n>`, `docs/<n>`. Commits: `[gh-<n>: <what changed>]`, subject only. `gh-0` is reserved for pre-tracker bootstrap work; this repo has no remote yet, so it stays on gh-0 until pushed.
- `main` moves through PRs once a remote and branch protection exist. Until then, logical commits land directly on `main`.
- Non-trivial work starts as a dated entry in `PLAN.md` (`## YYYY-MM-DD`, newest first) stating goal, approach, and verification. Entries are append-only after the session closes; corrections arrive as new dated entries.
- Writing follows `unslop` (this repo ships it; see `.agents/skills/unslop`).
