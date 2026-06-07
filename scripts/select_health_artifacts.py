#!/usr/bin/env python3
"""Select dated health artifacts by surface and filename date."""

from __future__ import annotations

import argparse
import re
from datetime import date
from pathlib import Path


ARTIFACT_PATTERN = re.compile(
    r"^(?P<date>\d{4}-\d{2}-\d{2})-"
    r"(?P<surface>plugin|tooling)-"
    r"(?P<kind>findings|health)\.md$"
)


def non_negative_int(value: str) -> int:
    parsed = int(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("must be zero or greater")
    return parsed


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("must be one or greater")
    return parsed


def select_artifacts(
    directory: Path,
    *,
    kind: str,
    surface: str,
    limit: int,
    offset: int,
) -> list[Path]:
    matches: list[tuple[date, str, Path]] = []

    if not directory.is_dir():
        return []

    for path in directory.iterdir():
        match = ARTIFACT_PATTERN.fullmatch(path.name)
        if match is None:
            continue
        if match["kind"] != kind or match["surface"] != surface:
            continue
        try:
            artifact_date = date.fromisoformat(match["date"])
        except ValueError:
            continue
        matches.append((artifact_date, path.name, path))

    matches.sort(reverse=True)
    return [path for _, _, path in matches[offset : offset + limit]]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Select docs/health artifacts by filename date.",
    )
    parser.add_argument("--directory", type=Path, default=Path("docs/health"))
    parser.add_argument("--kind", choices=("findings", "health"), required=True)
    parser.add_argument("--surface", choices=("plugin", "tooling"), required=True)
    parser.add_argument("--limit", type=positive_int, default=1)
    parser.add_argument("--offset", type=non_negative_int, default=0)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    for path in select_artifacts(
        args.directory,
        kind=args.kind,
        surface=args.surface,
        limit=args.limit,
        offset=args.offset,
    ):
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
