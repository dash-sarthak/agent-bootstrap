---
name: py-clean-code
description: Python-specific clean code rules for agent-maintained projects. Companion to the clean-* catalog and the manual's determinism section.
---

# Python clean code

The base `clean-*` skills own naming, functions, comments, and tests in general. This skill adds the Python instantiations. The operating manual's determinism section remains the source of truth; this file never relaxes it.

## Style

- PEP 8 naming, `ruff check` and `ruff format` as the enforced standard. Type hints on every public function and module-level constant.
- `pathlib.Path` over `os.path` string surgery. f-strings over `.format` and `%`. Dataclasses (frozen where possible) over dicts for structured data.
- No mutable default arguments. No bare `except:`. Catch the narrowest exception and let unexpected ones crash loudly.
- Stdlib first. Every third-party dependency states its reason in the PR that adds it, and `requirements.txt` pins exact versions.

## Determinism

- No `datetime.now()`, `time.time()`, `time.monotonic()` in production logic. Inject a clock callable (`Callable[[], datetime]` or `Callable[[], float]`); the composition root wires the real one.
- No `random.*` in production logic. Inject a `random.Random` instance seeded by the composition root.
- No `os.environ` reads outside the composition root. Modules take configuration as parameters or dataclasses.
- UTC everywhere internally. Convert to a named locale or timezone only at the render edge, with the locale fixed explicitly in code.
- Floats: format through an explicit fixed function before comparison or display; never compare computed floats with `==`.

## Tests

- Tests live in `tests/`, one file per module under test, named `test_<module>.py`. pytest style, plain asserts.
- Each test names the behavior it defends. Boundaries are mandatory: empty, zero, off-by-one, invalid input, error paths.
- No network, no real clock, no real randomness, no wall-clock sleeps. Inject fakes through the production API, never through test-only backdoors.
- Keep each test under ~100ms; mark nothing flaky, fix the cause instead.
