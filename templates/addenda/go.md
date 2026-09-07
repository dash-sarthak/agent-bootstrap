## Language addendum: Go

### Commands

- Build: `go build ./...` — Test: `go test ./...` — Vet: `go vet ./...`
- Format: `gofumpt -l -w .` (never plain gofmt; gofumpt is a stricter superset and its findings are lint findings)
- CI runs vet and the full test suite on every PR.

### Conventions

- Table-driven tests, external test packages (`package foo_test`, not `package foo`), `t.Helper()` in shared fixtures. Match this in every new test.
- Determinism instantiation: no `time.Now`, `time.Since` on wall clocks, `rand.Float64`, or `os.Getenv` outside `main` and other composition roots. Inject `func() time.Time` and a seeded `*rand.Rand`. Tests use fixed clocks and seeded sources.
- Errors are returned, never swallowed. Every blocking call takes a `context.Context` as its first argument.
- Deferred cleanup (container teardown, file removal) runs on an independent context (`context.WithoutCancel` plus its own timeout) so a cancelled parent cannot leak resources.
- Config and schema validation rejects contradictory input at parse time. Never silently normalize.
- stdout and stderr are separate channels. stderr is not reliably "the error"; keep them separate in results and logs.
- Prefer direct, slightly repetitive call sites over an abstraction that does not earn its weight. Minimal abstractions; functions over classes when no state is needed.
