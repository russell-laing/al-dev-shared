#!/usr/bin/env python3
"""Find exact duplicate text blocks and write a reviewable Markdown report."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


DEFAULT_INPUTS = (Path(".claude"), Path("profile-al-dev-shared"))


@dataclass(frozen=True, order=True)
class Occurrence:
    path: str
    start_line: int
    end_line: int


@dataclass(frozen=True)
class DuplicateMatch:
    lines: tuple[str, ...]
    occurrences: tuple[Occurrence, ...]

    @property
    def line_count(self) -> int:
        return len(self.lines)

    @property
    def scope(self) -> str:
        paths = {occurrence.path for occurrence in self.occurrences}
        return "within one file" if len(paths) == 1 else "across files"


@dataclass(frozen=True)
class ScanResult:
    root: Path
    inputs: tuple[str, ...]
    min_lines: int
    min_nonblank: int
    min_chars: int
    include_archived: bool
    include_generated: bool
    scanned_files: int
    excluded_files: tuple[tuple[str, str], ...]
    matches: tuple[DuplicateMatch, ...]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Find exact duplicate text blocks and write a Markdown report. "
            "Archives and generated projections are excluded by default."
        )
    )
    parser.add_argument(
        "inputs",
        nargs="*",
        type=Path,
        default=list(DEFAULT_INPUTS),
        help="Files or directories to scan",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Repository root used for relative paths",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help=(
            "Markdown output path. Defaults to "
            "docs/reviews/YYYY-MM-DD-duplicate-text-report.md"
        ),
    )
    parser.add_argument(
        "--min-lines",
        type=int,
        default=8,
        help="Minimum consecutive duplicate lines",
    )
    parser.add_argument(
        "--min-nonblank",
        type=int,
        default=4,
        help="Minimum nonblank lines in a candidate block",
    )
    parser.add_argument(
        "--min-chars",
        type=int,
        default=80,
        help="Minimum characters in a candidate block",
    )
    parser.add_argument(
        "--include-archived",
        action="store_true",
        help="Include files below directories named archived",
    )
    parser.add_argument(
        "--include-generated",
        action="store_true",
        help="Include files below directories named generated",
    )
    parser.add_argument(
        "--date",
        default=dt.date.today().isoformat(),
        help="Report date in YYYY-MM-DD format",
    )
    return parser.parse_args(argv)


def display_path(path: Path, root: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(root.resolve()).as_posix()
    except ValueError:
        return resolved.as_posix()


def exclusion_reason(
    path: Path,
    *,
    include_archived: bool,
    include_generated: bool,
) -> str | None:
    parts = set(path.parts)
    if path.name == ".DS_Store":
        return ".DS_Store"
    if "__pycache__" in parts:
        return "cache"
    if not include_archived and "archived" in parts:
        return "archived"
    if not include_generated and "generated" in parts:
        return "generated"
    return None


def candidate_files(inputs: Iterable[Path]) -> list[Path]:
    files: set[Path] = set()
    for input_path in inputs:
        path = input_path.expanduser().resolve()
        if not path.exists():
            raise FileNotFoundError(f"Input does not exist: {input_path}")
        if path.is_dir():
            files.update(candidate for candidate in path.rglob("*") if candidate.is_file())
        else:
            files.add(path)
    return sorted(files)


def read_normalized_lines(path: Path) -> tuple[list[str] | None, str | None]:
    raw = path.read_bytes()
    if b"\x00" in raw:
        return None, "binary"
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return None, "non-UTF-8"
    return [line.rstrip() for line in text.splitlines()], None


def qualifies(
    lines: tuple[str, ...] | list[str],
    *,
    min_nonblank: int,
    min_chars: int,
) -> bool:
    return (
        sum(bool(line.strip()) for line in lines) >= min_nonblank
        and len("\n".join(lines)) >= min_chars
    )


def seed_hash(lines: list[str], start: int, size: int) -> bytes:
    text = "\n".join(lines[start : start + size]).encode("utf-8")
    return hashlib.sha256(text).digest()


def intervals_overlap(first_start: int, second_start: int, length: int) -> bool:
    return max(first_start, second_start) < min(
        first_start + length,
        second_start + length,
    )


def extend_pair(
    first_path: str,
    first_start: int,
    second_path: str,
    second_start: int,
    all_lines: dict[str, list[str]],
    min_lines: int,
) -> tuple[tuple[str, ...], Occurrence, Occurrence] | None:
    first_lines = all_lines[first_path]
    second_lines = all_lines[second_path]
    left = 0
    while (
        first_start - left > 0
        and second_start - left > 0
        and first_lines[first_start - left - 1]
        == second_lines[second_start - left - 1]
    ):
        left += 1

    first_index = first_start - left
    second_index = second_start - left
    length = min_lines + left
    while (
        first_index + length < len(first_lines)
        and second_index + length < len(second_lines)
        and first_lines[first_index + length]
        == second_lines[second_index + length]
    ):
        length += 1

    if (
        first_path == second_path
        and intervals_overlap(first_index, second_index, length)
    ):
        return None

    block = tuple(first_lines[first_index : first_index + length])
    first = Occurrence(first_path, first_index + 1, first_index + length)
    second = Occurrence(second_path, second_index + 1, second_index + length)
    return block, first, second


def find_matches(
    all_lines: dict[str, list[str]],
    *,
    min_lines: int,
    min_nonblank: int,
    min_chars: int,
) -> tuple[DuplicateMatch, ...]:
    seeds: dict[bytes, list[tuple[str, int]]] = {}
    for path, lines in sorted(all_lines.items()):
        for start in range(0, len(lines) - min_lines + 1):
            window = lines[start : start + min_lines]
            if not qualifies(
                window,
                min_nonblank=min_nonblank,
                min_chars=min_chars,
            ):
                continue
            seeds.setdefault(seed_hash(lines, start, min_lines), []).append(
                (path, start)
            )

    grouped: dict[tuple[str, ...], set[Occurrence]] = {}
    for occurrences in seeds.values():
        if len(occurrences) < 2:
            continue
        for first_index in range(len(occurrences) - 1):
            first_path, first_start = occurrences[first_index]
            for second_path, second_start in occurrences[first_index + 1 :]:
                if (
                    first_path == second_path
                    and abs(first_start - second_start) < min_lines
                ):
                    continue
                extended = extend_pair(
                    first_path,
                    first_start,
                    second_path,
                    second_start,
                    all_lines,
                    min_lines,
                )
                if extended is None:
                    continue
                block, first, second = extended
                if not qualifies(
                    block,
                    min_nonblank=min_nonblank,
                    min_chars=min_chars,
                ):
                    continue
                grouped.setdefault(block, set()).update((first, second))

    matches = [
        DuplicateMatch(lines=block, occurrences=tuple(sorted(occurrences)))
        for block, occurrences in grouped.items()
        if len(occurrences) >= 2
    ]
    matches.sort(
        key=lambda match: (
            -match.line_count,
            match.occurrences[0].path,
            match.occurrences[0].start_line,
            match.lines,
        )
    )
    return tuple(matches)


def scan_paths(
    *,
    root: Path,
    inputs: Iterable[Path],
    min_lines: int = 8,
    min_nonblank: int = 4,
    min_chars: int = 80,
    include_archived: bool = False,
    include_generated: bool = False,
) -> ScanResult:
    if min_lines < 2:
        raise ValueError("min_lines must be at least 2")
    if min_nonblank < 1:
        raise ValueError("min_nonblank must be at least 1")
    if min_chars < 1:
        raise ValueError("min_chars must be at least 1")

    root = root.expanduser().resolve()
    resolved_inputs = tuple(Path(path).expanduser().resolve() for path in inputs)
    all_lines: dict[str, list[str]] = {}
    excluded: list[tuple[str, str]] = []

    for path in candidate_files(resolved_inputs):
        relative = display_path(path, root)
        reason = exclusion_reason(
            path,
            include_archived=include_archived,
            include_generated=include_generated,
        )
        if reason:
            excluded.append((relative, reason))
            continue
        lines, reason = read_normalized_lines(path)
        if reason:
            excluded.append((relative, reason))
            continue
        all_lines[relative] = lines or []

    return ScanResult(
        root=root,
        inputs=tuple(display_path(path, root) for path in resolved_inputs),
        min_lines=min_lines,
        min_nonblank=min_nonblank,
        min_chars=min_chars,
        include_archived=include_archived,
        include_generated=include_generated,
        scanned_files=len(all_lines),
        excluded_files=tuple(sorted(excluded)),
        matches=find_matches(
            all_lines,
            min_lines=min_lines,
            min_nonblank=min_nonblank,
            min_chars=min_chars,
        ),
    )


def code_fence(lines: tuple[str, ...]) -> str:
    longest = max(
        (len(run) for line in lines for run in line.split() if set(run) == {"`"}),
        default=0,
    )
    return "`" * max(3, longest + 1)


def render_markdown(result: ScanResult, *, report_date: str) -> str:
    lines = [
        "# Duplicate Text Report",
        "",
        f"**Date:** {report_date}",
        "",
        "## Scan Configuration",
        "",
        f"- Inputs: {', '.join(f'`{path}`' for path in result.inputs)}",
        f"- Minimum duplicate length: {result.min_lines} lines",
        f"- Minimum nonblank lines: {result.min_nonblank}",
        f"- Minimum characters: {result.min_chars}",
        f"- Include archived content: {'yes' if result.include_archived else 'no'}",
        f"- Include generated content: {'yes' if result.include_generated else 'no'}",
        f"- Text files scanned: {result.scanned_files}",
        f"- Files excluded: {len(result.excluded_files)}",
        "",
        "Trailing whitespace and line endings are normalized. Other text remains exact.",
        "",
        "## Summary",
        "",
        f"Found {len(result.matches)} grouped duplicate blocks.",
        "",
        "Generated and archived matches are excluded by default because they are often",
        "intentional. Each finding still requires human review before refactoring.",
        "",
        "## Findings",
        "",
    ]

    if not result.matches:
        lines.append("No duplicate blocks met the configured thresholds.")
    else:
        for index, match in enumerate(result.matches, start=1):
            lines.extend(
                [
                    f"### {index}. {match.line_count} lines, "
                    f"{len(match.occurrences)} occurrences",
                    "",
                    f"- Scope: {match.scope}",
                    "- Locations:",
                ]
            )
            lines.extend(
                f"  - `{occurrence.path}:{occurrence.start_line}`"
                for occurrence in match.occurrences
            )
            excerpt = match.lines[:12]
            fence = code_fence(excerpt)
            lines.extend(
                [
                    "",
                    "Excerpt:",
                    "",
                    f"{fence}text",
                    *excerpt,
                    fence,
                    "",
                ]
            )

    lines.extend(["## Exclusions", ""])
    if result.excluded_files:
        reason_counts: dict[str, int] = {}
        for _, reason in result.excluded_files:
            reason_counts[reason] = reason_counts.get(reason, 0) + 1
        lines.extend(
            f"- {reason}: {count}"
            for reason, count in sorted(reason_counts.items())
        )
    else:
        lines.append("No files were excluded.")
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    root = args.root.expanduser().resolve()
    inputs = [
        path if path.is_absolute() else root / path
        for path in args.inputs
    ]
    output = args.output or (
        root / "docs" / "reviews" / f"{args.date}-duplicate-text-report.md"
    )
    if not output.is_absolute():
        output = root / output

    try:
        dt.date.fromisoformat(args.date)
        result = scan_paths(
            root=root,
            inputs=inputs,
            min_lines=args.min_lines,
            min_nonblank=args.min_nonblank,
            min_chars=args.min_chars,
            include_archived=args.include_archived,
            include_generated=args.include_generated,
        )
    except (FileNotFoundError, OSError, UnicodeError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        render_markdown(result, report_date=args.date),
        encoding="utf-8",
    )
    print(
        f"Wrote {output} with {len(result.matches)} grouped duplicate blocks "
        f"from {result.scanned_files} text files."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
