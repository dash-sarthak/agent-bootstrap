"""Applies a plan to disk: check everything first, then write. Conflicts refuse atomically."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .errors import ConflictError
from .plan import FileEntry


@dataclass
class Report:
    written: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    conflicts: list[str] = field(default_factory=list)


def _find_conflicts(entries: list[FileEntry], target: Path) -> list[str]:
    conflicts: list[str] = []
    for entry in entries:
        path = target / entry.path
        if path.is_symlink():
            conflicts.append(f"{entry.path} (exists as a symlink)")
        elif path.exists() and not path.is_file():
            conflicts.append(f"{entry.path} (exists and is not a regular file)")
        elif path.is_file() and path.read_bytes() != entry.content:
            conflicts.append(entry.path)
    return conflicts


def apply(entries: list[FileEntry], target: Path, dry_run: bool = False) -> Report:
    """Write the plan under target. Identical existing files are skipped, differing ones refuse."""
    target = Path(target)
    conflicts = _find_conflicts(entries, target)
    if conflicts:
        raise ConflictError(conflicts)

    report = Report()
    for entry in entries:
        path = target / entry.path
        if path.is_file():
            report.skipped.append(entry.path)
            continue
        if not dry_run:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(entry.content)
            if entry.executable:
                path.chmod(path.stat().st_mode | 0o111)
        report.written.append(entry.path)
    return report
