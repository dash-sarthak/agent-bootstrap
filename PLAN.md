# agent-bootstrap — plan

Dated planning entries, newest first. One `## YYYY-MM-DD` heading per planning session. Planning precedes implementation for non-trivial work: state the goal, the approach, and how the result gets verified. Entries are append-only after the session closes; corrections arrive as new dated entries.

## 2026-09-07

Status: done (v1 implemented this session; evidence in git log and STATE.md).

- Goal: a generator that installs the standard agent setup into any project on any Linux box, language-agnostic, so every repo behaves identically under any AGENTS.md-convention agent.
- Non-goals: doctor/check mode for existing projects, additional language packs, remote or CI provisioning, git init inside targets.
- Approach: Python 3.9+ stdlib CLI (`bootstrap.py` plus `agentic_setup/` package), variable-only templates with code-side assembly (base manual plus language addendum), vendored skill packs copied from toolbase and home sources (sync is one-way, sources to templates), `.omp/` trio by default with `--no-omp`, `--workspace` thin-pointer mode, dry-run and conflict refusal.
- Determinism contract: output depends only on CLI args and template files; sorted walks; no timestamps, user, hostname, or network; same inputs give byte-identical trees, pinned by golden manifests per scenario; a re-run on a bootstrapped dir is a no-op; existing files with different content refuse with exit 2.
- Exit contract: 0 ok, 1 usage or validation error, 2 conflict.
- Tests first: unit tests (render, plan, validation), behavior tests (conflict, dry-run, idempotency), golden manifests, sync-tool tests, all authored before the implementation landed.
- Verification: full unittest suite green; goldens inspected; smoke bootstraps of go, typescript, and none targets plus conflict and dry-run demonstrations.
