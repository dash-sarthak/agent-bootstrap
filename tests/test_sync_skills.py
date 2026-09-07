"""Tests for the one-way skill sync tool."""
import tempfile
import unittest
from pathlib import Path

from tools.sync_skills import sync


def make_source(root, skill, body):
    """root is the skills directory that directly contains skill dirs, matching sync's tuples."""
    skill_dir = root / skill
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(body, encoding="utf-8")
    return skill_dir


class SyncTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.base = Path(tmp.name)
        self.sources = {"core": [(self.base / "src-a", "alpha")], "go": []}
        self.dest = self.base / "templates" / "skills"

    def test_copies_new_skill(self):
        make_source(self.base / "src-a", "alpha", "v1")
        report = sync(self.dest, self.sources)
        self.assertEqual(report["copied"], ["core/alpha"])
        self.assertEqual(
            (self.dest / "core" / "alpha" / "SKILL.md").read_text(encoding="utf-8"), "v1"
        )

    def test_reports_unchanged_when_identical(self):
        make_source(self.base / "src-a", "alpha", "v1")
        sync(self.dest, self.sources)
        report = sync(self.dest, self.sources)
        self.assertEqual(report["unchanged"], ["core/alpha"])
        self.assertEqual(report["copied"], [])

    def test_updates_when_source_changed(self):
        make_source(self.base / "src-a", "alpha", "v1")
        sync(self.dest, self.sources)
        make_source(self.base / "src-a", "alpha", "v2")
        report = sync(self.dest, self.sources)
        self.assertEqual(report["copied"], ["core/alpha"])
        self.assertEqual(
            (self.dest / "core" / "alpha" / "SKILL.md").read_text(encoding="utf-8"), "v2"
        )

    def test_reports_missing_source_and_leaves_dest_alone(self):
        report = sync(self.dest, self.sources)
        self.assertEqual(report["missing"], ["core/alpha"])
        self.assertFalse((self.dest / "core" / "alpha").exists())

    def test_empty_pack_is_skipped_silently(self):
        report = sync(self.dest, self.sources)
        self.assertEqual(report, {"copied": [], "unchanged": [], "missing": ["core/alpha"]})


if __name__ == "__main__":
    unittest.main()
