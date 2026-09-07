"""Applies a plan to disk: check everything first, then write. Conflicts refuse atomically."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .errors import ConflictError
from .plan import MERGE, SEED, FileEntry

MERGE_HEADER = "# Added by agent-bootstrap"


@dataclass
class Report:
    written: list[str] = field(default_factory=list)
    merged: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    conflicts: list[str] = field(default_factory=list)


def _find_conflicts(entries: list[FileEntry], target: Path) -> list[str]:
    """Refuse on anything unwritable. Differing bytes only conflict for files the plan owns."""
    conflicts: list[str] = []
    for entry in entries:
        path = target / entry.path
        if path.is_symlink():
            conflicts.append(f"{entry.path} (exists as a symlink)")
        elif path.exists() and not path.is_file():
            conflicts.append(f"{entry.path} (exists and is not a regular file)")
        elif entry.disposition not in (MERGE, SEED) and path.is_file():
            if path.read_bytes() != entry.content:
                conflicts.append(entry.path)
    return conflicts


def _entries_of(raw: bytes) -> list[str]:
    """Meaningful lines of a list file. Blanks and comments are decoration, not entries."""
    lines = (line.strip() for line in raw.decode("utf-8").splitlines())
    return [line for line in lines if line and not line.startswith("#")]


def merge_lines(existing: bytes, planned: bytes) -> bytes:
    """Append the planned entries the existing file lacks, in planned order. Idempotent."""
    if not existing.strip():
        return planned
    have = set(_entries_of(existing))
    missing: list[str] = []
    for line in _entries_of(planned):
        if line not in have:
            have.add(line)
            missing.append(line)
    if not missing:
        return existing
    head = existing.decode("utf-8").rstrip("\n")
    body = "\n".join(missing)
    return f"{head}\n\n{MERGE_HEADER}\n{body}\n".encode("utf-8")


def _resolve(entry: FileEntry, path: Path) -> tuple[bytes | None, str]:
    """Decide the bytes to write and the bucket to report. None means nothing to do."""
    if not path.is_file():
        return entry.content, "written"
    if entry.disposition == SEED:
        return None, "skipped"
    if entry.disposition == MERGE:
        merged = merge_lines(path.read_bytes(), entry.content)
        if merged == path.read_bytes():
            return None, "skipped"
        return merged, "merged"
    return None, "skipped"


def apply(entries: list[FileEntry], target: Path, dry_run: bool = False) -> Report:
    """Write the plan under target. Owned files refuse on drift; merged and seeded ones never do."""
    target = Path(target)
    conflicts = _find_conflicts(entries, target)
    if conflicts:
        raise ConflictError(conflicts)

    report = Report()
    for entry in entries:
        path = target / entry.path
        content, bucket = _resolve(entry, path)
        if content is None:
            report.skipped.append(entry.path)
            continue
        if not dry_run:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
            if entry.executable:
                path.chmod(path.stat().st_mode | 0o111)
        getattr(report, bucket).append(entry.path)
    return report
