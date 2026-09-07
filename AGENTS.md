# agent-bootstrap

Bootstrap generator that installs the standard agent operating system into any project: `AGENTS.md` manual, `.agents/skills`, `.omp/` context, `STATE.md`, `PLAN.md`, a language addendum, and CI. Read `README.md` first for design rationale; this file is operational notes only.

## Commands

- Run tests: `python3 -m unittest discover -s tests -v` (stdlib only; Python 3.9+ floor, zero dependencies)
- Regenerate golden manifests after an intentional output change: `python3 tools/make_goldens.py`, then review the diff
- Sync vendored skills: `python3 tools/sync_skills.py --source <skills-dir>` (repeatable, or set `AGENT_SKILL_SOURCES`; defaults to `~/.agents/skills`), then review the diff
- Smoke run: `python3 bootstrap.py /tmp/demo --name demo --lang go`

## Testing notes

- Goldens live in `tests/golden/<scenario>/manifest.txt` as `<sha256>  <path>` lines. They pin byte-identical output; never hand-edit them, regenerate and review the diff.
- Determinism and idempotency tests run the CLI twice and compare trees. When they fail, a template or module reads ambient state (time, env, locale, hostname). Fix the cause, not the test.
- Tests call `agentic_setup.cli.main(argv)` directly. Only the entrypoint smoke test spawns a subprocess.

## Skill provenance

- The core, typescript, and web packs are vendored copies of skills maintained outside this repo. Where they come from is machine configuration, not a committed path: pass `--source DIR` to `tools/sync_skills.py`, or set `AGENT_SKILL_SOURCES`. Each pack declares skill names in `PACKS`; the first source root holding a name wins.
- `templates/skills/go` and `templates/skills/python` originate here. This repo is their canonical home and sync never writes over them.
- Sync runs one way, sources to templates. Never edit a vendored copy directly; edit it at its source and sync, or the next sync silently reverts you.
- A skill tied to one product, one workstation, or one subject domain does not belong in a pack. Anything shipped here has to make sense in an arbitrary project the generator bootstraps.
- This repo's own `.agents/skills/*` are relative symlinks into `templates/skills/core`, so agents working here see the same skills they will install.

## Conventions

- Branches: `feature/<n>`, `bug/<n>`, `chore/<n>`, `docs/<n>`. Commits: `[gh-<n>: <what changed>]`, subject only. `gh-0` is reserved for pre-tracker bootstrap work; this repo has no remote yet, so it stays on gh-0 until pushed.
- `main` moves through PRs once a remote and branch protection exist. Until then, logical commits land directly on `main`.
- Non-trivial work starts as a dated entry in `PLAN.md` (`## YYYY-MM-DD`, newest first) stating goal, approach, and verification. Entries are append-only after the session closes; corrections arrive as new dated entries.
- Writing follows `unslop` (this repo ships it; see `.agents/skills/unslop`).
