## Language addendum: TypeScript

### Commands

- Install: `pnpm install --frozen-lockfile` (CI enforces; the lockfile is committed)
- Build: `pnpm build` — Test: `pnpm test` — Coverage: `pnpm test:coverage`
- Single package: `npx vitest run packages/<name>`; one build: `turbo run build --filter=<pkg>`

### Conventions

- pnpm workspaces plus turborepo when the project has multiple packages. Pure logic lives in framework-free packages; apps compose. Only composition roots (`apps/*/src`, `main.ts`) read `process.env` / `import.meta.env`.
- Determinism instantiation: no `Date.now()`, `new Date()`, `Math.random()`, or `crypto.randomUUID()` in production logic. Inject a clock and a seeded PRNG as parameters. Tests use `vi.useFakeTimers()` and seeded sources.
- Coverage gate: 100% statements, branches, functions, lines for every package, enforced by thresholds in `vitest.config.ts`. New packages land with tests in the same PR; the coverage `include` list grows with them.
- Logging goes through the project logger package (JSON, one event per line). `console.log` and friends are forbidden outside it; ESLint `no-console` is `error`.
- Floating-point display and comparison go through explicit fixed formatters; never `===` on computed floats.
