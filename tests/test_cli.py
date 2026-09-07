"""End-to-end behavior tests: success, idempotency, conflicts, dry-run, validation."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from agentic_setup import cli
from tests.util import tree_state

REPO = Path(__file__).resolve().parent.parent


class CliEndToEndTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.base = Path(tmp.name)

    def target(self, name="target"):
        return self.base / name

    def test_bootstrap_writes_tree_and_exits_zero(self):
        code = cli.main(["--name", "demo", "--lang", "go", str(self.target())])
        self.assertEqual(code, 0)
        self.assertTrue((self.target() / "AGENTS.md").is_file())
        self.assertTrue((self.target() / ".omp" / "config.yml").is_file())
        self.assertTrue((self.target() / ".agents" / "skills" / "go-clean-code" / "SKILL.md").is_file())
        self.assertTrue((self.target() / ".github" / "workflows" / "ci.yml").is_file())

    def test_idempotent_rerun_is_a_noop(self):
        cli.main(["--name", "demo", "--lang", "go", str(self.target())])
        before = tree_state(self.target())
        code = cli.main(["--name", "demo", "--lang", "go", str(self.target())])
        self.assertEqual(code, 0)
        self.assertEqual(tree_state(self.target()), before)

    def test_conflict_refuses_and_leaves_tree_unchanged(self):
        target = self.target()
        target.mkdir()
        (target / "AGENTS.md").write_text("my own manual", encoding="utf-8")
        code = cli.main(["--name", "demo", "--lang", "go", str(target)])
        self.assertEqual(code, 2)
        self.assertEqual((target / "AGENTS.md").read_text(encoding="utf-8"), "my own manual")
        self.assertFalse((target / "STATE.md").exists())

    def test_identical_existing_file_is_skipped(self):
        cli.main(["--name", "demo", str(self.target())])
        (self.target() / "STATE.md").unlink()
        code = cli.main(["--name", "demo", str(self.target())])
        self.assertEqual(code, 0)
        self.assertTrue((self.target() / "STATE.md").is_file())

    def test_dry_run_creates_nothing(self):
        code = cli.main(["--name", "demo", "--dry-run", str(self.target("absent"))])
        self.assertEqual(code, 0)
        self.assertFalse(self.target("absent").exists())

    def test_invalid_names_exit_1(self):
        for bad in ("../evil", "-flag", "", "a/b", "x y"):
            with self.subTest(name=bad):
                code = cli.main(["--name", bad, str(self.target())])
                self.assertEqual(code, 1)

    def test_unknown_lang_exits_1(self):
        self.assertEqual(cli.main(["--name", "demo", "--lang", "rust", str(self.target())]), 1)

    def test_unknown_pack_exits_1(self):
        self.assertEqual(cli.main(["--name", "demo", "--pack", "mobile", str(self.target())]), 1)

    def test_workspace_mode_writes_single_file(self):
        code = cli.main(["--name", "hub", "--workspace", "--repo-dir", "app", str(self.target())])
        self.assertEqual(code, 0)
        self.assertEqual([p.name for p in self.target().iterdir()], ["AGENTS.md"])

    def test_nested_target_is_created(self):
        deep = self.base / "a" / "b" / "proj"
        code = cli.main(["--name", "proj", str(deep)])
        self.assertEqual(code, 0)
        self.assertTrue((deep / "AGENTS.md").is_file())

    def test_existing_gitignore_merges_instead_of_conflicting(self):
        target = self.target()
        target.mkdir()
        (target / ".gitignore").write_text("build/\nvenv/\n", encoding="utf-8")
        code = cli.main(["--name", "demo", "--lang", "python", str(target)])
        self.assertEqual(code, 0)
        merged = (target / ".gitignore").read_text(encoding="utf-8")
        self.assertIn("build/", merged)
        self.assertIn("venv/", merged)
        self.assertIn("__pycache__/", merged)
        self.assertTrue(merged.startswith("build/\nvenv/\n"))

    def test_gitignore_merge_is_idempotent(self):
        target = self.target()
        target.mkdir()
        (target / ".gitignore").write_text("build/\n", encoding="utf-8")
        cli.main(["--name", "demo", "--lang", "python", str(target)])
        after_first = tree_state(target)
        code = cli.main(["--name", "demo", "--lang", "python", str(target)])
        self.assertEqual(code, 0)
        self.assertEqual(tree_state(target), after_first)

    def test_gitignore_merge_adds_nothing_when_already_covered(self):
        target = self.target()
        cli.main(["--name", "demo", "--lang", "python", str(target)])
        generated = (target / ".gitignore").read_bytes()
        cli.main(["--name", "demo", "--lang", "python", str(target)])
        self.assertEqual((target / ".gitignore").read_bytes(), generated)

    def test_requirements_are_seeded_for_python(self):
        code = cli.main(["--name", "demo", "--lang", "python", str(self.target())])
        self.assertEqual(code, 0)
        self.assertTrue((self.target() / "requirements.txt").is_file())
        dev = (self.target() / "requirements-dev.txt").read_text(encoding="utf-8")
        for tool in ("ruff==", "pytest==", "mypy=="):
            self.assertIn(tool, dev)

    def test_existing_requirements_are_left_alone(self):
        target = self.target()
        target.mkdir()
        (target / "requirements.txt").write_text("flask==3.0.0\n", encoding="utf-8")
        code = cli.main(["--name", "demo", "--lang", "python", str(target)])
        self.assertEqual(code, 0)
        self.assertEqual((target / "requirements.txt").read_text(encoding="utf-8"), "flask==3.0.0\n")

    def test_requirements_absent_for_other_languages(self):
        cli.main(["--name", "demo", "--lang", "go", str(self.target())])
        self.assertFalse((self.target() / "requirements-dev.txt").exists())

    def test_gitignore_as_a_directory_still_conflicts(self):
        target = self.target()
        (target / ".gitignore").mkdir(parents=True)
        code = cli.main(["--name", "demo", "--lang", "python", str(target)])
        self.assertEqual(code, 2)
        self.assertFalse((target / "AGENTS.md").exists())

    def test_ci_exposes_a_stable_protection_context(self):
        for lang in ("go", "typescript", "python"):
            with self.subTest(lang=lang):
                target = self.target(f"ctx-{lang}")
                cli.main(["--name", "demo", "--lang", lang, str(target)])
                ci = (target / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
                self.assertIn("\n  ci:\n", ci)

    def test_entrypoint_smoke(self):
        proc = subprocess.run(
            [sys.executable, str(REPO / "bootstrap.py"), "--help"],
            capture_output=True, text=True, cwd=REPO,
        )
        self.assertEqual(proc.returncode, 0)
        self.assertIn("--lang", proc.stdout)


if __name__ == "__main__":
    unittest.main()
