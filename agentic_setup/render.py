"""Deterministic template rendering: {{UPPER_CASE}} substitution, nothing else."""
from __future__ import annotations

import re

from .errors import UsageError

VAR_PATTERN = re.compile(r"\{\{([A-Z][A-Z0-9_]*)\}\}")


def render(text: str, variables: dict[str, str]) -> str:
    """Substitute {{VAR}} occurrences. Unknown variables are a hard error, never silent."""
    missing: list[str] = []

    def substitute(match: re.Match[str]) -> str:
        name = match.group(1)
        if name not in variables:
            missing.append(name)
            return match.group(0)
        value = variables[name]
        if not isinstance(value, str):
            raise UsageError(
                f"variable {name} must be a string, got {type(value).__name__}"
            )
        return value

    out = VAR_PATTERN.sub(substitute, text)
    if missing:
        unique = ", ".join(sorted(set(missing)))
        raise UsageError(f"template variables not provided: {unique}")
    return out


def variable_names(text: str) -> list[str]:
    """All {{VAR}} names in a template, sorted, unique."""
    return sorted(set(VAR_PATTERN.findall(text)))
