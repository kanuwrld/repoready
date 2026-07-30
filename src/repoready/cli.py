"""Command-line interface for RepoReady."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from . import __version__
from .checks import audit_repository
from .renderers import render_json, render_markdown, render_text


def _score(value: str) -> int:
    try:
        score = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("score must be an integer") from error
    if not 0 <= score <= 100:
        raise argparse.ArgumentTypeError("score must be between 0 and 100")
    return score


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="repoready",
        description="Score repository readiness from 0 to 100.",
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="repository directory to audit (default: current directory)",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json", "markdown"),
        default="text",
        help="report format (default: text)",
    )
    parser.add_argument(
        "--min-score",
        type=_score,
        default=80,
        help="minimum score required for exit code 0 (default: 80)",
    )
    parser.add_argument(
        "--output",
        default="-",
        metavar="PATH",
        help="write report to PATH instead of stdout; use - for stdout (default: -)",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        report = audit_repository(args.path, min_score=args.min_score)
    except (FileNotFoundError, NotADirectoryError, OSError, ValueError) as error:
        parser.error(str(error))

    renderers = {
        "json": render_json,
        "markdown": render_markdown,
        "text": render_text,
    }
    renderer = renderers[args.format]
    output = renderer(report)
    if args.output == "-":
        print(output)
    else:
        destination = Path(args.output).expanduser()
        try:
            destination.write_text(f"{output}\n", encoding="utf-8")
        except OSError as error:
            parser.error(f"Could not write report to {destination}: {error}")

    return 0 if report.passes_threshold else 1


def entrypoint() -> None:
    sys.exit(main())
