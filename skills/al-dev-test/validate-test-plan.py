#!/usr/bin/env python3
"""Validate test plan structure and coverage completeness.

Usage:
    python3 validate-test-plan.py <path-to-test-plan.md>

Exit codes:
    0 - All checks pass
    1 - Validation issues found (printed to stdout)
"""

import re
import sys
from pathlib import Path


REQUIRED_SECTIONS = [
    "Test Coverage Summary",
    "Test Codeunits",
    "Test Scenarios",
    "Test Execution",
    "Coverage Analysis",
]

TEST_CATEGORIES = [
    "unit",
    "integration",
    "scenario",
    "edge case",
]

# Matches test count patterns like "12 tests" or "N tests"
TEST_COUNT_PATTERN = re.compile(r"(\d+)\s+tests?")

# Matches codeunit ID references
CODEUNIT_ID_PATTERN = re.compile(
    r"(?:codeunit|Test Codeunit)\s+(\d{5,6})", re.IGNORECASE
)


def check_structure(lines: list[str]) -> list[str]:
    """Check required sections and minimum length."""
    issues: list[str] = []

    if len(lines) < 15:
        issues.append(
            f"Document too short ({len(lines)} lines). "
            "Expected 15+ for a meaningful test plan."
        )

    headings = [
        ln.lstrip("#").strip() for ln in lines if ln.startswith("#")
    ]
    heading_text = " ".join(headings).lower()

    for section in REQUIRED_SECTIONS:
        if section.lower() not in heading_text:
            issues.append(f"Missing required section: '{section}'")

    for i, line in enumerate(lines[:-1]):
        if line.startswith("#") and lines[i + 1].startswith("#"):
            issues.append(
                f"Possibly empty section at line {i + 1}: "
                f"'{line.strip()}'"
            )

    return issues


def check_test_categories(text: str) -> list[str]:
    """Verify all 4 test categories are represented."""
    issues: list[str] = []
    text_lower = text.lower()

    missing = [
        cat for cat in TEST_CATEGORIES if cat not in text_lower
    ]

    if missing:
        missing_list = ", ".join(missing)
        issues.append(
            f"Test categories not mentioned: {missing_list}. "
            "Expected all 4 categories (unit, integration, "
            "scenario, edge case)."
        )

    return issues


def check_test_counts(text: str) -> list[str]:
    """Verify test counts are present and non-zero."""
    issues: list[str] = []

    counts = TEST_COUNT_PATTERN.findall(text)
    if not counts:
        issues.append(
            "No test counts found. Expected patterns like "
            "'12 tests' in the coverage summary."
        )
        return issues

    int_counts = [int(c) for c in counts]

    if all(c == 0 for c in int_counts):
        issues.append(
            "All test counts are zero. At least one category "
            "should have tests."
        )

    total = sum(int_counts)
    if total < 4:
        issues.append(
            f"Very low total test count ({total}). "
            "Expected at least 4 tests across categories."
        )

    return issues


def check_codeunit_ids(text: str) -> list[str]:
    """Check for duplicate test codeunit IDs."""
    issues: list[str] = []

    matches = CODEUNIT_ID_PATTERN.findall(text)
    if not matches:
        issues.append(
            "No test codeunit IDs found. Expected test "
            "codeunit declarations with 5-6 digit IDs."
        )
        return issues

    seen: dict[str, int] = {}
    for cid in matches:
        seen[cid] = seen.get(cid, 0) + 1

    duplicates = {k: v for k, v in seen.items() if v > 1}
    for cid, count in sorted(duplicates.items()):
        issues.append(
            f"Duplicate test codeunit ID {cid} "
            f"(appears {count} times)"
        )

    return issues


def check_execution_result(text: str) -> list[str]:
    """Verify test execution results are documented."""
    issues: list[str] = []
    text_lower = text.lower()

    has_execution = "test execution" in text_lower
    if not has_execution:
        return issues

    passing_indicators = [
        "all passing", "all pass", "passing",
        "pass", "success",
    ]
    failing_indicators = [
        "failing", "failed", "failure",
    ]

    has_result = any(
        ind in text_lower for ind in
        passing_indicators + failing_indicators
    )

    if not has_result:
        issues.append(
            "Test Execution section exists but no pass/fail "
            "result documented. Include test run outcome."
        )

    return issues


def main() -> int:
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <test-plan.md>")
        return 1

    path = sys.argv[1]
    if not Path(path).exists():
        print(f"File not found: {path}")
        return 1

    text = Path(path).read_text(encoding="utf-8")
    lines = text.splitlines()

    all_issues: list[str] = []

    # 1. Structural checks
    struct_issues = check_structure(lines)
    if struct_issues:
        all_issues.append("--- Structure ---")
        all_issues.extend(struct_issues)

    # 2. Category coverage
    cat_issues = check_test_categories(text)
    if cat_issues:
        all_issues.append("--- Test Categories ---")
        all_issues.extend(cat_issues)

    # 3. Test counts
    count_issues = check_test_counts(text)
    if count_issues:
        all_issues.append("--- Test Counts ---")
        all_issues.extend(count_issues)

    # 4. Codeunit IDs
    id_issues = check_codeunit_ids(text)
    if id_issues:
        all_issues.append("--- Codeunit IDs ---")
        all_issues.extend(id_issues)

    # 5. Execution results
    exec_issues = check_execution_result(text)
    if exec_issues:
        all_issues.append("--- Execution ---")
        all_issues.extend(exec_issues)

    real_issues = [
        i for i in all_issues if not i.startswith("---")
    ]

    if not real_issues:
        print(f"PASS: All checks passed for {path}")
        return 0

    print(f"ISSUES FOUND: {len(real_issues)}")
    for item in all_issues:
        if item.startswith("---"):
            print(f"\n{item}")
        else:
            print(f"  {item}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
