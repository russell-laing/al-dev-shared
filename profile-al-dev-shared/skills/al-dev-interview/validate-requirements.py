#!/usr/bin/env python3
"""Validate requirements document structure and completeness.

Usage:
    python validate-requirements.py <path-to-requirements.md>

Exit codes:
    0 - All checks pass
    1 - Validation issues found (printed to stdout)
"""

import re
import sys
from pathlib import Path


REQUIRED_SECTIONS = [
    "Business",
    "Functional",
    "Data",
    "UI",
    "Constraint",
    "Success Criteria",
]


def validate(path: str) -> list[str]:
    """Return list of validation issues found."""
    issues: list[str] = []
    text = Path(path).read_text(encoding="utf-8")
    lines = text.splitlines()

    if len(lines) < 20:
        issues.append(
            f"Document too short ({len(lines)} lines). "
            "Expected 20+ for meaningful requirements."
        )

    headings = [
        ln.lstrip("#").strip() for ln in lines if ln.startswith("#")
    ]
    heading_text = " ".join(headings).lower()

    for section in REQUIRED_SECTIONS:
        if section.lower() not in heading_text:
            issues.append(f"Missing required section: '{section}'")

    req_count = len(re.findall(r"^###\s+REQ-\d+", text, re.MULTILINE))
    if req_count == 0:
        issues.append(
            "No REQ governance tokens found. "
            "Expected at least one ### REQ-NNN heading."
        )

    acc_count = len(re.findall(r"\*\*ACC-\d+", text))
    if acc_count == 0:
        issues.append(
            "No ACC governance tokens found. "
            "Expected at least one **ACC-NNN** criterion."
        )

    for i, line in enumerate(lines[:-1]):
        if line.startswith("#") and lines[i + 1].startswith("#"):
            issues.append(
                f"Possibly empty section at line {i + 1}: "
                f"'{line.strip()}'"
            )

    return issues


def main() -> int:
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <requirements.md>")
        return 1

    path = sys.argv[1]
    if not Path(path).exists():
        print(f"File not found: {path}")
        return 1

    issues = validate(path)

    if not issues:
        print(f"PASS: All checks passed for {path}")
        return 0

    print(f"ISSUES FOUND: {len(issues)}")
    for i, issue in enumerate(issues, 1):
        print(f"  {i}. {issue}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
