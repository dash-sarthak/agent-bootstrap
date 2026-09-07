"""Error types with their exit codes."""
from __future__ import annotations


class BootstrapError(Exception):
    """Base error; exit code 1."""

    exit_code = 1


class UsageError(BootstrapError):
    """Bad arguments, validation failure, or template error. Exit code 1."""

    exit_code = 1


class ConflictError(BootstrapError):
    """Existing files differ from planned content; nothing was modified. Exit code 2."""

    exit_code = 2

    def __init__(self, conflicts: list[str]) -> None:
        self.conflicts = list(conflicts)
        listing = "\n".join(f"  {c}" for c in self.conflicts)
        super().__init__(f"refusing to overwrite existing files:\n{listing}")
