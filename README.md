# agent-bootstrap

One command installs the standard agent operating system into any project: the `AGENTS.md` operating manual, portable skills, omp context, `STATE.md`, `PLAN.md`, a language addendum, and CI. After it runs, any agent that follows the `AGENTS.md` convention (Codex, Cursor, Jules, Gemini CLI, Amp, omp) picks up the same files, the same workflow, and the same rules, whichever directory of the repo it starts in.

## Philosophy

- Interoperability. Generated files follow open conventions only: `AGENTS.md` (plural) at the repo root, skills under `.agents/skills/<name>/SKILL.md`. Nothing requires a specific vendor. The `.omp/` directory is additive; other agents ignore it safely.
- Predictability. The generator is a pure function of its arguments and its template files. Same inputs give byte-identical output, proven by golden manifests in CI. It never reads the clock, the user, the hostname, or the network, and it never writes a file it did not announce.
- Determinism by default. Generated projects carry hard rules against non-deterministic agent and code behavior: injected clocks and randomness, no ambient environment or locale reads in logic, frozen lockfiles, fake timers in tests, UTC everywhere, JSON-only logging. The language addendum instantiates each rule per ecosystem.
- Planning before implementation. Generated repos keep `PLAN.md` as an append-only decision log, newest dated entry first, and their manual makes planning the default first step for non-trivial requests.

## Usage

```bash
python3 bootstrap.py <target-dir> --name <project> [options]
```

| Option | Meaning |
|---|---|
| `--name` | Project name, validated against `^[A-Za-z0-9][A-Za-z0-9._-]*$`. Required. |
| `--lang` | `none` (default), `go`, `typescript`, or `python`. Selects the addendum, CI template, and language skill pack. |
| `--pack` | Repeatable. Currently `web` (web-design, seo-optimization). |
| `--no-omp` | Skip the `.omp/` directory. |
| `--workspace` | Write only a thin pointer `AGENTS.md` for a workspace root that holds the repo (see below). |
| `--repo-dir` | With `--workspace`: the repo directory name the pointer targets. Defaults to `--name`. |
| `--dry-run` | Print the exact file plan, write nothing. |

Exit codes: `0` ok, `1` usage or validation error, `2` conflict (an existing file differs from the planned content; nothing is modified).

The target directory is created if missing. Existing files with identical planned content are skipped, which makes re-runs no-ops. The tool never runs `git init`, never touches git state, and prints the next steps instead of performing them.

`--workspace` mode writes a single `AGENTS.md` into a parent directory that holds the repo (a "workspace"), pointing agents at `toolbase`-style layout: the repo dir, mission docs, and worktrees.

## What gets generated

```
<target>/
├── AGENTS.md                  # base manual + language addendum
├── PLAN.md                    # append-only dated planning log
├── STATE.md                   # live session state scaffold
├── .gitignore                 # base + language section
├── .omp/                      # AGENTS.md pointer, RULES.md, config.yml (unless --no-omp)
├── .agents/skills/            # core pack + language pack + extra packs (copies, not symlinks)
└── .github/workflows/ci.yml   # per language (skipped for --lang none)
```

Skill packs:

| Pack | Skills |
|---|---|
| core (always) | unslop, tdd, blast-radius, boy-scout, clean-general, clean-names, clean-functions, clean-comments, clean-tests, diagnosing-bugs, resolving-merge-conflicts, research, technical-writing |
| typescript | typescript-clean-code |
| go | go-clean-code |
| python | py-clean-code |
| web | web-design, seo-optimization |

Deliberately excluded: find-tool-ideas (passive-income specific), chrome-cdp (workstation-specific), political-* and entity-linking (domain-specific).

## Sources and sync

Skills are vendored as committed copies so a clone is self-contained on any machine. Canonical sources: `~/Projects/Passive Income/toolbase/.agents/skills` and `~/.agents/skills` (plus this repo for go-clean-code and py-clean-code). Sync runs one way, sources to `templates/skills/`, via `python3 tools/sync_skills.py`; review the diff and ship it as a PR. Never edit vendored copies directly.

## Development

Python 3.9+, zero runtime dependencies, stdlib `unittest`:

```bash
python3 -m unittest discover -s tests -v
```

Layout: `bootstrap.py` (entrypoint), `agentic_setup/` (cli, plan, render, write), `templates/` (manual, addenda, skills, ci, gitignore sections), `tests/` (unit, behavior, golden manifests), `tools/` (sync_skills, make_goldens). See `AGENTS.md` for operational notes and `PLAN.md` for the decision log.
