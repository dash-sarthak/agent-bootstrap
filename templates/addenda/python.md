## Language addendum: Python

### Commands

- Test: `python3 -m pytest` — one module: `python3 -m pytest tests/test_<name>.py`
- Lint and format: `ruff check .` and `ruff format .` (dev dependency, pinned in `requirements-dev.txt`)
- Environments: `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt -r requirements-dev.txt`. Both requirements files are committed and pinned.

### Conventions

- PEP 8 naming. Type hints on all public functions. Docstrings state what; comments state why.
- Determinism instantiation: no `datetime.now()`, `time.time()`, `random.*`, or `os.environ` reads outside the composition root (`__main__.py`, `cli.py`). Inject a clock callable and a `random.Random` instance. Tests inject fakes or freeze time.
- Tests live in `tests/`, one file per module under test, pytest style, no network, no real clock, no real randomness.
- Stdlib first. A third-party dependency needs a reason written in the PR that adds it.
- Prefer `pathlib.Path` over `os.path`; dataclasses over dicts for structured data; no mutable default arguments.
