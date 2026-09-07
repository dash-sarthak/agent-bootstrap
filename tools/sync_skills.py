"""One-way skill sync: canonical sources -> templates/skills. Run: python3 tools/sync_skills.py

Canonical sources live in the toolbase checkout and the home skills directory.
The go and python packs originate in this repo and are never synced over.
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TOOLBASE = Path.home() / "Projects" / "Passive Income" / "toolbase" / ".agents" / "skills"
HOME = Path.home() / ".agents" / "skills"

PACKS: dict[str, list[tuple[Path, str]]] = {
    "core": [(TOOLBASE, s) for s in (
        "unslop",
        "tdd",
        "blast-radius",
        "boy-scout",
        "clean-comments",
        "clean-functions",
        "clean-general",
        "clean-names",
        "clean-tests",
    )] + [(HOME, s) for s in (
        "diagnosing-bugs",
        "resolving-merge-conflicts",
        "research",
        "technical-writing",
    )],
    "typescript": [(TOOLBASE, "typescript-clean-code")],
    "web": [(TOOLBASE, "web-design"), (TOOLBASE, "seo-optimization")],
    "go": [],
    "python": [],
}


def _tree_digest(root: Path) -> list[tuple[str, bytes]]:
    return sorted(
        (p.relative_to(root).as_posix(), p.read_bytes())
        for p in root.rglob("*")
        if p.is_file()
    )


def sync(dest: Path, packs: dict[str, list[tuple[Path, str]]] | None = None) -> dict[str, list[str]]:
    """Copy source skills into dest/<pack>/<skill>. Identical trees are left alone."""
    packs = PACKS if packs is None else packs
    report: dict[str, list[str]] = {"copied": [], "unchanged": [], "missing": []}
    for pack, items in packs.items():
        for source_root, skill in items:
            src = source_root / skill
            out = dest / pack / skill
            if not src.is_dir():
                report["missing"].append(f"{pack}/{skill}")
                continue
            if out.is_dir() and _tree_digest(out) == _tree_digest(src):
                report["unchanged"].append(f"{pack}/{skill}")
                continue
            if out.is_dir():
                shutil.rmtree(out)
            out.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(src, out)
            report["copied"].append(f"{pack}/{skill}")
    return report


def main() -> int:
    report = sync(REPO / "templates" / "skills")
    for key in ("copied", "unchanged", "missing"):
        for item in report[key]:
            print(f"{key}: {item}")
    if report["missing"]:
        print("error: missing canonical sources", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
