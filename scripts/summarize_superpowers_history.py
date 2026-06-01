#!/usr/bin/env python3
"""Summarize historical Superpowers plan/spec artifacts."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path


SUPERPOWERS_DIRS = (Path("docs/superpowers/plans"), Path("docs/superpowers/specs"))


@dataclass(frozen=True)
class Artifact:
    path: str
    date: str
    kind: str
    title: str
    status: str
    summary: str


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def extract_date(path: Path, text: str) -> str:
    filename_match = re.search(r"(\d{4}-\d{2}-\d{2})", path.name)
    if filename_match:
        return filename_match.group(1)

    text_match = re.search(r"(?im)^\*\*Date:\*\*\s*(\d{4}-\d{2}-\d{2})\b", text)
    if text_match:
        return text_match.group(1)

    return "unknown"


def extract_title(path: Path, text: str) -> str:
    for line in text.splitlines():
        match = re.match(r"^#\s+(.+?)\s*$", line)
        if match:
            return match.group(1).strip()

    stem = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", path.stem)
    return stem.replace("-", " ").title()


def classify_kind(path: Path) -> str:
    parts = path.as_posix().split("/")
    if "plans" in parts:
        return "plan"
    if "specs" in parts:
        return "spec"
    if path.name.endswith("-design.md"):
        return "spec"
    if "plan" in path.stem:
        return "plan"
    return "unknown"


def extract_explicit_status(text: str) -> str | None:
    status_match = re.search(r"(?im)^\s*(?:\*\*)?Status:(?:\*\*)?\s*(.+?)\s*$", text)
    if status_match:
        return status_match.group(1).strip()
    return None


def normalize_status(status_text: str) -> str:
    lowered = status_text.lower()
    if re.search(r"\bsuperseded\b", lowered):
        return "superseded"
    if re.search(r"\bimplemented\b", lowered):
        return "implemented"
    if re.search(r"\b(completed|complete)\b", lowered) and not re.search(
        r"\b(pending|awaiting|needs?)\b.{0,40}\b(implementation\s+plan|plan)\b",
        lowered,
    ):
        return "implemented"
    if re.search(r"\b(approved|draft|proposed|archived|pending)\b", lowered):
        return "historical"
    return "unknown"


def classify_status(text: str) -> str:
    explicit_status = extract_explicit_status(text)
    if explicit_status is not None:
        return normalize_status(explicit_status)
    return normalize_status(text)


def extract_summary(text: str) -> str:
    lines = text.splitlines()
    for prefix in ("**Goal:**", "**Problem:**", "**Solution:**"):
        for line in lines:
            if line.startswith(prefix):
                return line[len(prefix) :].strip()

    in_summary = False
    summary_lines: list[str] = []
    for line in lines:
        if re.match(r"^##\s+Executive Summary\s*$", line, re.IGNORECASE):
            in_summary = True
            continue
        if in_summary and line.startswith("## "):
            break
        if in_summary and line.strip() and not line.startswith("**"):
            summary_lines.append(line.strip())
        if len(summary_lines) >= 2:
            break

    if summary_lines:
        return " ".join(summary_lines)

    paragraphs: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("---"):
            if paragraphs:
                break
            continue
        if stripped.startswith(">"):
            continue
        paragraphs.append(stripped)

    return " ".join(paragraphs) if paragraphs else "No summary available."


def inspect_artifact(path: Path, root: Path) -> Artifact:
    text = read_text(path)
    relative_path = path.relative_to(root).as_posix() if path.is_absolute() else path.as_posix()
    return Artifact(
        path=relative_path,
        date=extract_date(path, text),
        kind=classify_kind(Path(relative_path)),
        title=extract_title(path, text),
        status=classify_status(text),
        summary=extract_summary(text),
    )


def collect_artifacts(root: Path) -> list[Artifact]:
    artifacts: list[Artifact] = []
    for directory in SUPERPOWERS_DIRS:
        full_directory = root / directory
        if not full_directory.exists():
            continue
        for path in sorted(full_directory.glob("*.md")):
            artifacts.append(inspect_artifact(path, root))
    return sorted(artifacts, key=lambda item: (item.date, item.kind, item.title, item.path), reverse=True)


def _is_under(path: Path, directory: Path) -> bool:
    try:
        path.relative_to(directory)
    except ValueError:
        return False
    return True


def find_external_references(root: Path, paths: list[Path]) -> dict[str, list[str]]:
    references = {path.as_posix(): [] for path in paths}
    excluded_dirs = tuple(root / directory for directory in SUPERPOWERS_DIRS)
    search_files = [
        path
        for path in root.rglob("*.md")
        if not any(_is_under(path, directory) for directory in excluded_dirs)
        and ".git" not in path.parts
    ]

    targets: list[tuple[str, str]] = []
    for path in paths:
        relative = path.relative_to(root).as_posix() if path.is_absolute() else path.as_posix()
        targets.append((path.as_posix(), relative))

    for search_file in sorted(search_files):
        try:
            text = read_text(search_file)
        except UnicodeDecodeError:
            continue
        relative_search_file = search_file.relative_to(root).as_posix()
        for key, relative_target in targets:
            if relative_target in text:
                references[key].append(relative_search_file)

    return references


def render_history(artifacts: list[Artifact], references: dict[str, list[str]]) -> str:
    lines = [
        "# Superpowers Planning History",
        "",
        "Current source of truth: active implementation guidance lives in the current shared plugin source and knowledge documents.",
        "",
    ]

    current_date: str | None = None
    for artifact in sorted(artifacts, key=lambda item: (item.date, item.kind, item.title), reverse=True):
        if artifact.date != current_date:
            current_date = artifact.date
            lines.extend([f"## {current_date}", ""])

        lines.append(f"### {artifact.title}")
        lines.append("")
        lines.append(f"- Path: `{artifact.path}`")
        lines.append(f"- Kind: {artifact.kind}")
        lines.append(f"- Status: {artifact.status}")
        lines.append(f"- Summary: {artifact.summary}")
        external_refs = references.get(artifact.path, [])
        if external_refs:
            lines.append(f"- External references: {', '.join(f'`{ref}`' for ref in external_refs)}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def display_path(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Summarize Superpowers plan/spec artifacts.")
    parser.add_argument("--root", default=".", help="Repository root to scan.")
    parser.add_argument("--output", default="docs/superpowers/history.md", help="Output markdown path.")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    output = Path(args.output)
    output_path = output if output.is_absolute() else root / output
    artifacts = collect_artifacts(root)
    artifact_paths = [root / artifact.path for artifact in artifacts]
    references_by_path = find_external_references(root, artifact_paths)
    references = {
        path.relative_to(root).as_posix(): refs
        for path, refs in ((Path(key), value) for key, value in references_by_path.items())
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_history(artifacts, references), encoding="utf-8")
    print(f"Wrote {display_path(output_path, root)} with {len(artifacts)} artifacts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
