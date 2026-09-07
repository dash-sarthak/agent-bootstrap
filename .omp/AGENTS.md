# agent-bootstrap — session context

Repo: agent-bootstrap (local, no remote yet). Live state: @../STATE.md

## Order of truth

1. User instruction in the current session.
2. STATE.md, injected below (live state, updated every session close).
3. The operating manual @../AGENTS.md: commands, testing notes, skill provenance, conventions.
4. PLAN.md for the current dated plan.

Start omp sessions in this directory; the context above only loads from here.

## Session open

STATE.md is already injected. Read AGENTS.md fully before touching code.

## Session close

Update STATE.md per AGENTS.md. Leave no uncommitted work behind.
