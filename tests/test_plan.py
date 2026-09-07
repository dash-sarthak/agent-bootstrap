"""Unit tests for plan building: file selection, packs, sorting, workspace mode."""
import unittest
from pathlib import Path

from agentic_setup.errors import UsageError
from agentic_setup.plan import build_plan

REPO = Path(__file__).resolve().parent.parent
TEMPLATES = REPO / "templates"


def entries_by_path(**kwargs):
    entries = build_plan(templates_dir=TEMPLATES, **kwargs)
    return {e.path: e for e in entries}


class BuildPlanTests(unittest.TestCase):
    def test_default_plan_contains_core_files(self):
        plan = entries_by_path(name="demo")
        for expected in ("AGENTS.md", "PLAN.md", "STATE.md", ".gitignore"):
            self.assertIn(expected, plan)

    def test_default_plan_has_no_ci_and_no_language_skill(self):
        plan = entries_by_path(name="demo")
        self.assertNotIn(".github/workflows/ci.yml", plan)
        self.assertNotIn(".agents/skills/typescript-clean-code/SKILL.md", plan)

    def test_omp_trio_present_by_default(self):
        plan = entries_by_path(name="demo")
        for expected in (".omp/AGENTS.md", ".omp/RULES.md", ".omp/config.yml"):
            self.assertIn(expected, plan)

    def test_no_omp_flag_removes_trio(self):
        plan = entries_by_path(name="demo", omp=False)
        self.assertFalse(any(p.startswith(".omp/") for p in plan))

    def test_go_adds_addendum_ci_and_skill(self):
        plan = entries_by_path(name="demo", lang="go")
        self.assertIn("Language addendum: Go", plan["AGENTS.md"].content.decode())
        self.assertIn(".github/workflows/ci.yml", plan)
        self.assertIn(".agents/skills/go-clean-code/SKILL.md", plan)

    def test_none_has_no_language_pack(self):
        plan = entries_by_path(name="demo")
        self.assertFalse(any("clean-code" in p for p in plan))

    def test_web_pack_adds_web_skills(self):
        plan = entries_by_path(name="demo", lang="typescript", packs=("web",))
        self.assertIn(".agents/skills/web-design/SKILL.md", plan)
        self.assertIn(".agents/skills/seo-optimization/SKILL.md", plan)
        self.assertIn(".agents/skills/typescript-clean-code/SKILL.md", plan)

    def test_skill_copies_match_template_bytes(self):
        plan = entries_by_path(name="demo", lang="python")
        source = (TEMPLATES / "skills" / "python" / "py-clean-code" / "SKILL.md").read_bytes()
        self.assertEqual(plan[".agents/skills/py-clean-code/SKILL.md"].content, source)

    def test_project_name_rendered_into_manual(self):
        plan = entries_by_path(name="my-tool")
        self.assertIn("# my-tool — operating manual", plan["AGENTS.md"].content.decode())

    def test_plan_is_sorted_by_path(self):
        entries = build_plan(templates_dir=TEMPLATES, name="demo", lang="go", packs=("web",))
        paths = [e.path for e in entries]
        self.assertEqual(paths, sorted(paths))

    def test_workspace_mode_is_single_pointer(self):
        plan = entries_by_path(name="hub", workspace=True, repo_dir="app")
        self.assertEqual(list(plan), ["AGENTS.md"])
        self.assertIn("app/AGENTS.md", plan["AGENTS.md"].content.decode())

    def test_unknown_lang_is_rejected(self):
        with self.assertRaises(UsageError):
            build_plan(templates_dir=TEMPLATES, name="demo", lang="rust")

    def test_unknown_pack_is_rejected(self):
        with self.assertRaises(UsageError):
            build_plan(templates_dir=TEMPLATES, name="demo", packs=("mobile",))

    def test_invalid_name_is_rejected(self):
        for bad in ("../evil", "-flag", "", "a/b", "x y"):
            with self.subTest(name=bad):
                with self.assertRaises(UsageError):
                    build_plan(templates_dir=TEMPLATES, name=bad)


if __name__ == "__main__":
    unittest.main()
