"""CLI: argument parsing, exit contract, human output."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .errors import BootstrapError, UsageError
from .plan import LANGS, PACKS, build_plan
from .write import apply


class _Parser(argparse.ArgumentParser):
    """argparse errors become UsageError so the exit contract stays ours (usage = 1)."""

    def error(self, message: str):  # noqa: D401 - argparse override signature
        raise UsageError(message)


def build_parser() -> _Parser:
    parser = _Parser(
        prog="bootstrap",
        description="Bootstrap the standard agent setup into a project directory.",
    )
    parser.add_argument("target", help="project directory (created if missing)")
    parser.add_argument("--name", required=True, help="project name")
    parser.add_argument("--lang", default="none", choices=list(LANGS), help="language addendum")
    parser.add_argument(
        "--pack", action="append", default=[], choices=list(PACKS), help="extra skill pack (repeatable)"
    )
    parser.add_argument("--no-omp", action="store_true", help="skip the .omp/ directory")
    parser.add_argument(
        "--workspace", action="store_true", help="write only a thin pointer AGENTS.md (workspace root)"
    )
    parser.add_argument(
        "--repo-dir", default=None, help="with --workspace: repo directory name the pointer targets"
    )
    parser.add_argument("--dry-run", action="store_true", help="print the plan, write nothing")
    return parser


def main(argv: list[str] | None = None) -> int:
    try:
        args = build_parser().parse_args(argv)
        entries = build_plan(
            args.name,
            lang=args.lang,
            packs=tuple(args.pack),
            omp=not args.no_omp,
            workspace=args.workspace,
            repo_dir=args.repo_dir,
        )
        report = apply(entries, Path(args.target), dry_run=args.dry_run)
    except BootstrapError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return exc.exit_code

    verb = "would write" if args.dry_run else "wrote"
    print(
        f"{verb} {len(report.written)} file(s), merged {len(report.merged)}, "
        f"skipped {len(report.skipped)} existing"
    )
    for path in report.written:
        print(f"  + {path}")
    for path in report.merged:
        print(f"  ~ {path}")
    for path in report.skipped:
        print(f"  = {path}")
    if args.dry_run:
        print("dry run: nothing written")
    else:
        print(
            "next steps: review AGENTS.md, git init if needed, set user.name and "
            "user.email, then plan the first unit of work in PLAN.md"
        )
    return 0
