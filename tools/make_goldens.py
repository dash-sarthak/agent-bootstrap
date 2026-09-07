"""Regenerate golden manifests after an intentional output change. Run: python3 tools/make_goldens.py"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from agentic_setup import cli  # noqa: E402
from tests.test_golden import SCENARIOS  # noqa: E402
from tests.util import tree_manifest  # noqa: E402

GOLDEN_DIR = REPO / "tests" / "golden"


def main() -> int:
    for scenario, extra in sorted(SCENARIOS.items()):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "proj"
            code = cli.main([*extra, str(target)])
            if code != 0:
                print(f"error: scenario {scenario} exited {code}", file=sys.stderr)
                return 1
            lines = tree_manifest(target)
        out = GOLDEN_DIR / scenario / "manifest.txt"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"wrote {out.relative_to(REPO)} ({len(lines)} files)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
