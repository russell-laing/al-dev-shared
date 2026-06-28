#!/usr/bin/env python3
"""Shared helpers for document validator scripts."""

from pathlib import Path


def read_text_lines(path: str) -> tuple[str, list[str]]:
    """Read a UTF-8 document and return both the text and split lines."""
    text = Path(path).read_text(encoding="utf-8")
    return text, text.splitlines()


def check_structure(
    lines: list[str],
    required_sections: list[str],
    minimum_lines: int,
    document_name: str,
) -> list[str]:
    """Check shared heading and empty-section rules."""
    issues: list[str] = []

    if len(lines) < minimum_lines:
        issues.append(
            f"Document too short ({len(lines)} lines). "
            f"Expected {minimum_lines}+ for a meaningful {document_name}."
        )

    headings = [
        ln.lstrip("#").strip() for ln in lines if ln.startswith("#")
    ]
    heading_text = " ".join(headings).lower()

    for section in required_sections:
        if section.lower() not in heading_text:
            issues.append(f"Missing required section: '{section}'")

    for i, line in enumerate(lines[:-1]):
        if line.startswith("#") and lines[i + 1].startswith("#"):
            issues.append(
                f"Possibly empty section at line {i + 1}: "
                f"'{line.strip()}'"
            )

    return issues
