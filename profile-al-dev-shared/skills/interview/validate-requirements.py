#!/usr/bin/env python3
"""Validate requirements document structure and completeness.

Usage:
    python validate-requirements.py <path-to-requirements.md>

Validation outcome:
    0 means the requirements document passes all checks.
    1 means the requirements validator printed issues to stdout.
"""

import re
import sys
from pathlib import Path

MODULE_ROOT = Path(__file__).resolve().parents[1]
if str(MODULE_ROOT) not in sys.path:
    sys.path.insert(0, str(MODULE_ROOT))

from validator_common import check_structure as check_document_structure
from validator_common import read_text_lines


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
    text, lines = read_text_lines(path)

    issues.extend(
        check_document_structure(
            lines, REQUIRED_SECTIONS, 20, "requirements document"
        )
    )

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
