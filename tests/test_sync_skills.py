"""Tests for the one-way skill sync tool."""
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tools import sync_skills
from tools.sync_skills import ENV_SOURCES, resolve_sources, sync


def make_source(root, skill, body):
    """root is a skills directory that directly contains skill dirs, like ~/.agents/skills."""
    skill_dir = root / skill
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(body, encoding="utf-8")
    return skill_dir


class SyncTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.base = Path(tmp.name)
        self.packs = {"core": ("alpha",), "go": ()}
        self.sources = [self.base / "src-a"]
        self.dest = self.base / "templates" / "skills"

    def test_copies_new_skill(self):
        make_source(self.base / "src-a", "alpha", "v1")
        report = sync(self.dest, self.sources, self.packs)
        self.assertEqual(report["copied"], ["core/alpha"])
        self.assertEqual(
            (self.dest / "core" / "alpha" / "SKILL.md").read_text(encoding="utf-8"), "v1"
        )

    def test_reports_unchanged_when_identical(self):
        make_source(self.base / "src-a", "alpha", "v1")
        sync(self.dest, self.sources, self.packs)
        report = sync(self.dest, self.sources, self.packs)
        self.assertEqual(report["unchanged"], ["core/alpha"])
        self.assertEqual(report["copied"], [])

    def test_updates_when_source_changed(self):
        make_source(self.base / "src-a", "alpha", "v1")
        sync(self.dest, self.sources, self.packs)
        make_source(self.base / "src-a", "alpha", "v2")
        report = sync(self.dest, self.sources, self.packs)
        self.assertEqual(report["copied"], ["core/alpha"])
        self.assertEqual(
            (self.dest / "core" / "alpha" / "SKILL.md").read_text(encoding="utf-8"), "v2"
        )

    def test_reports_missing_source_and_leaves_dest_alone(self):
        report = sync(self.dest, self.sources, self.packs)
        self.assertEqual(report["missing"], ["core/alpha"])
        self.assertFalse((self.dest / "core" / "alpha").exists())

    def test_empty_pack_is_skipped_silently(self):
        report = sync(self.dest, self.sources, self.packs)
        self.assertEqual(report, {"copied": [], "unchanged": [], "missing": ["core/alpha"]})

    def test_first_source_root_holding_the_skill_wins(self):
        make_source(self.base / "src-a", "alpha", "from-a")
        make_source(self.base / "src-b", "alpha", "from-b")
        sync(self.dest, [self.base / "src-b", self.base / "src-a"], self.packs)
        self.assertEqual(
            (self.dest / "core" / "alpha" / "SKILL.md").read_text(encoding="utf-8"), "from-b"
        )

    def test_later_source_root_supplies_what_the_first_lacks(self):
        make_source(self.base / "src-b", "alpha", "from-b")
        report = sync(self.dest, [self.base / "src-a", self.base / "src-b"], self.packs)
        self.assertEqual(report["copied"], ["core/alpha"])


class ResolveSourcesTests(unittest.TestCase):
    def test_cli_sources_win_over_environment(self):
        with mock.patch.dict(os.environ, {ENV_SOURCES: "/from/env"}):
            self.assertEqual(resolve_sources(["/from/cli"]), [Path("/from/cli")])

    def test_environment_is_split_on_the_path_separator(self):
        raw = os.pathsep.join(["/one", "/two"])
        with mock.patch.dict(os.environ, {ENV_SOURCES: raw}):
            self.assertEqual(resolve_sources([]), [Path("/one"), Path("/two")])

    def test_blank_environment_falls_back_to_the_default(self):
        with mock.patch.dict(os.environ, {ENV_SOURCES: "  "}):
            self.assertEqual(resolve_sources([]), list(sync_skills.DEFAULT_SOURCES))

    def test_default_is_the_conventional_home_skills_directory(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            self.assertEqual(resolve_sources([]), [Path.home() / ".agents" / "skills"])

    def test_tilde_is_expanded(self):
        self.assertEqual(resolve_sources(["~/skills"]), [Path.home() / "skills"])

    def test_no_source_root_is_hardcoded_to_a_specific_project(self):
        text = Path(sync_skills.__file__).read_text(encoding="utf-8")
        self.assertNotIn("Projects", text)


if __name__ == "__main__":
    unittest.main()
