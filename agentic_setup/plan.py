"""Builds the deterministic file plan from CLI inputs and template files."""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from .errors import UsageError
from .render import render

NAME_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")

# How write.apply treats an existing file at the same path.
OWN = "own"      # the plan owns the bytes; anything different is a conflict
MERGE = "merge"  # a list the project also edits; missing entries get appended
SEED = "seed"    # a starting point; an existing file is left alone

LANGS = ("none", "go", "typescript", "python")
PACKS = ("web",)
DEFAULT_TEMPLATES = Path(__file__).resolve().parent.parent / "templates"

# Dependency manifests the CI recipe installs from. Seeded so an existing project keeps its own.
REQUIREMENTS = {
    "python": (
        ("requirements.txt", "requirements/python.txt"),
        ("requirements-dev.txt", "requirements/python-dev.txt"),
    ),
}


@dataclass(frozen=True)
class FileEntry:
    """One planned file: repo-relative posix path, exact bytes, optional exec bit."""

    path: str
    content: bytes
    executable: bool = False
    disposition: str = OWN


def _read(templates: Path, rel: str) -> bytes:
    return (templates / rel).read_bytes()


def _skill_entries(templates: Path, lang: str, packs: tuple[str, ...]) -> list[FileEntry]:
    """Collect every skill file from core, language, and extra packs. First pack wins on collision."""
    entries: list[FileEntry] = []
    seen: set[str] = set()
    for pack in ("core", lang, *packs):
        if pack == "none":
            continue
        base = templates / "skills" / pack
        if not base.is_dir():
            continue
        for file in sorted(p for p in base.rglob("*") if p.is_file()):
            rel = file.relative_to(base).as_posix()
            path = f".agents/skills/{rel}"
            if path in seen:
                continue
            seen.add(path)
            entries.append(FileEntry(path, file.read_bytes()))
    return entries


def build_plan(
    name: str,
    lang: str = "none",
    packs: tuple[str, ...] = (),
    omp: bool = True,
    workspace: bool = False,
    repo_dir: str | None = None,
    templates_dir: Path | None = None,
) -> list[FileEntry]:
    """Pure function: inputs and template files in, sorted file plan out. No I/O on target."""
    templates = Path(templates_dir) if templates_dir else DEFAULT_TEMPLATES
    if not NAME_PATTERN.match(name):
        raise UsageError(
            f"invalid project name {name!r}; must match {NAME_PATTERN.pattern}"
        )
    if lang not in LANGS:
        raise UsageError(f"unknown language {lang!r}; choose from: {', '.join(LANGS)}")
    unknown = [p for p in packs if p not in PACKS]
    if unknown:
        raise UsageError(
            f"unknown pack(s) {', '.join(sorted(unknown))}; choose from: {', '.join(PACKS)}"
        )

    variables = {"PROJECT_NAME": name, "NAME": name, "REPO_DIR": repo_dir or name}

    if workspace:
        text = render(_read(templates, "workspace-AGENTS.md.tmpl").decode(), variables)
        return [FileEntry("AGENTS.md", text.encode())]

    manual = render(_read(templates, "AGENTS.md.tmpl").decode(), variables)
    if lang != "none":
        addendum = render(_read(templates, f"addenda/{lang}.md").decode(), variables)
        manual = manual.rstrip() + "\n\n" + addendum.rstrip() + "\n"
    entries = [FileEntry("AGENTS.md", manual.encode())]

    entries.append(
        FileEntry("PLAN.md", render(_read(templates, "PLAN.md.tmpl").decode(), variables).encode())
    )
    entries.append(
        FileEntry("STATE.md", render(_read(templates, "STATE.md.tmpl").decode(), variables).encode())
    )

    gitignore = _read(templates, "gitignore-base.tmpl")
    if lang != "none":
        gitignore += _read(templates, f"gitignore/{lang}.txt")
    entries.append(FileEntry(".gitignore", gitignore, disposition=MERGE))

    if omp:
        for name_tmpl in ("AGENTS.md.tmpl", "RULES.md.tmpl"):
            out = f".omp/{name_tmpl[: -len('.tmpl')]}"
            entries.append(
                FileEntry(out, render(_read(templates, f"omp/{name_tmpl}").decode(), variables).encode())
            )
        entries.append(FileEntry(".omp/config.yml", _read(templates, "omp/config.yml")))

    entries.extend(_skill_entries(templates, lang, packs))

    if lang != "none":
        entries.append(FileEntry(".github/workflows/ci.yml", _read(templates, f"ci/{lang}.yml")))
        for out, rel in REQUIREMENTS.get(lang, ()):
            entries.append(FileEntry(out, _read(templates, rel), disposition=SEED))

    return sorted(entries, key=lambda e: e.path)
