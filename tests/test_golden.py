"""Golden manifest tests: byte-identical output per scenario."""
import tempfile
import unittest
from pathlib import Path

from agentic_setup import cli
from tests.util import tree_manifest

SCENARIOS = {
    "go_default": ["--name", "proj", "--lang", "go"],
    "typescript_default": ["--name", "proj", "--lang", "typescript"],
    "python_default": ["--name", "proj", "--lang", "python"],
    "none_default": ["--name", "proj"],
    "typescript_web": ["--name", "proj", "--lang", "typescript", "--pack", "web"],
    "go_no_omp": ["--name", "proj", "--lang", "go", "--no-omp"],
    "workspace": ["--name", "hub", "--workspace", "--repo-dir", "toolbase"],
}

GOLDEN_DIR = Path(__file__).resolve().parent / "golden"


class GoldenTests(unittest.TestCase):
    def test_output_matches_golden_manifest(self):
        for scenario, extra in sorted(SCENARIOS.items()):
            with self.subTest(scenario=scenario):
                with tempfile.TemporaryDirectory() as tmp:
                    target = Path(tmp) / "proj"
                    code = cli.main([*extra, str(target)])
                    self.assertEqual(code, 0)
                    actual = tree_manifest(target)
                golden = GOLDEN_DIR / scenario / "manifest.txt"
                expected = golden.read_text(encoding="utf-8").splitlines()
                self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
