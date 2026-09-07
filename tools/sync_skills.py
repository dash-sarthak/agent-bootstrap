"""One-way skill sync: source roots -> templates/skills.

Run: python3 tools/sync_skills.py [--source DIR ...]

Source roots are machine configuration, never committed. Give them with repeated
--source flags, or in the AGENT_SKILL_SOURCES environment variable as a
path-separator-delimited list. With neither, the default is ~/.agents/skills.

Each pack names the skills it wants. A skill is resolved against the source roots
in order and the first root holding it wins, so a local override can shadow a
shared checkout by coming first. The go and python packs originate in this repo
and have no upstream, so they are never synced over.
"""
from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
ENV_SOURCES = "AGENT_SKILL_SOURCES"
DEFAULT_SOURCES = (Path.home() / ".agents" / "skills",)

PACKS: dict[str, tuple[str, ...]] = {
    "core": (
        "blast-radius",
        "boy-scout",
        "clean-comments",
        "clean-functions",
        "clean-general",
        "clean-names",
        "clean-tests",
        "diagnosing-bugs",
        "research",
        "resolving-merge-conflicts",
        "tdd",
        "technical-writing",
        "unslop",
    ),
    "typescript": ("typescript-clean-code",),
    "web": ("seo-optimization", "web-design"),
    "go": (),
    "python": (),
}


def resolve_sources(cli_sources: list[str] | None = None) -> list[Path]:
    """Source roots from --source, else the environment, else the default. Order is preserved."""
    if cli_sources:
        return [Path(s).expanduser() for s in cli_sources]
    raw = os.environ.get(ENV_SOURCES, "")
    if raw.strip():
        return [Path(s).expanduser() for s in raw.split(os.pathsep) if s.strip()]
    return list(DEFAULT_SOURCES)


def _tree_digest(root: Path) -> list[tuple[str, bytes]]:
    return sorted(
        (p.relative_to(root).as_posix(), p.read_bytes())
        for p in root.rglob("*")
        if p.is_file()
    )


def _locate(skill: str, sources: list[Path]) -> Path | None:
    for root in sources:
        candidate = root / skill
        if candidate.is_dir():
            return candidate
    return None


def sync(
    dest: Path,
    sources: list[Path],
    packs: dict[str, tuple[str, ...]] | None = None,
) -> dict[str, list[str]]:
    """Copy each named skill into dest/<pack>/<skill>. Identical trees are left alone."""
    packs = PACKS if packs is None else packs
    report: dict[str, list[str]] = {"copied": [], "unchanged": [], "missing": []}
    for pack, skills in packs.items():
        for skill in skills:
            src = _locate(skill, sources)
            out = dest / pack / skill
            if src is None:
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="sync_skills",
        description="Sync vendored skills from source roots into templates/skills.",
        epilog=f"Sources may also come from {ENV_SOURCES} (path-separator-delimited).",
    )
    parser.add_argument(
        "--source",
        action="append",
        default=[],
        metavar="DIR",
        help="skills directory to read from (repeatable, searched in order)",
    )
    args = parser.parse_args(argv)

    sources = resolve_sources(args.source)
    print("sources: " + ", ".join(str(s) for s in sources))
    report = sync(REPO / "templates" / "skills", sources)
    for key in ("copied", "unchanged", "missing"):
        for item in report[key]:
            print(f"{key}: {item}")
    if report["missing"]:
        print(
            "error: some skills were not found in any source root; "
            "pass --source or set " + ENV_SOURCES,
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
