---
name: go-clean-code
description: Go-specific clean code rules for agent-maintained projects. Companion to the clean-* catalog and the manual's determinism section.
---

# Go clean code

The base `clean-*` skills own naming, functions, comments, and tests in general. This skill adds the Go instantiations. The operating manual's determinism section remains the source of truth; this file never relaxes it.

## Structure

- `cmd/<name>/` for binaries, `internal/` for private packages, `api/` for public contracts. Generated code lives under `gen/` and is never hand-edited.
- Accept interfaces, return concrete types, and define interfaces where they are consumed, not where they are implemented. No interface "just in case".
- Minimal abstractions. A direct, slightly repetitive call site beats an abstraction that does not earn its weight. Functions over methods when no state is involved.

## Errors and context

- Errors are values: return them, wrap with `%w`, never discard with `_` unless the reason is written in a comment at that line.
- Sentinel errors for expected conditions (`ErrNotFound`), wrapped errors for everything else.
- `context.Context` is the first parameter of every blocking or I/O function. Store contexts in structs only at the composition edge.
- Deferred cleanup that must survive cancellation gets its own context (`context.WithoutCancel` plus an explicit timeout), so a timed-out parent cannot leak goroutines, files, or containers.

## Validation

- Parse and validate configuration at load time. Reject contradictory combinations with an error naming the offending fields. Never silently normalize or default contradictory input.
- Stdout and stderr are separate channels with separate meanings. Results structures keep them apart; a non-empty stderr is not automatically a failure.

## Tests

- Table-driven: a slice of struct cases, `t.Run` per case, one assertion focus per case.
- External test packages (`package foo_test`) so tests exercise the public surface only.
- `t.Helper()` on every fixture helper. `t.Parallel()` where cases are independent.
- No `time.Now`, no `rand`, no network in tests. Inject fixed clocks and seeded `*rand.Rand` through the production API itself, never through test-only backdoors.

## Formatting

- `gofumpt -l -w .`, never plain `gofmt`. gofumpt findings are lint failures.
