#!/usr/bin/env python3
"""Validate code review document structure and plan coverage.

Usage:
    python3 validate-code-review.py <code-review.md> [solution-plan.md]

Validation outcome:
    0 means the code review passes structure, coverage, and resolution checks.
    1 means the review validator printed issues to stdout.
"""

import re
import sys
from pathlib import Path

VALIDATION_ROOT = Path(__file__).resolve().parents[1]
if str(VALIDATION_ROOT) not in sys.path:
    sys.path.insert(0, str(VALIDATION_ROOT))

import validator_common as review_validator


REQUIRED_SECTIONS = [
    "Change Summary",
    "Review Process",
    "Critical Issues",
    "Issues for User Decision",
    "Review Consensus",
    "Recommendation",
]

REVIEWER_KEYWORDS = [
    "security",
    "al expert",
    "performance",
]

# Matches AL object references like "50100" or "Object ID 50100"
OBJECT_ID_PATTERN = re.compile(r"\b(\d{5,6})\b")

# Matches severity labels

def check_review_structure(lines: list[str]) -> list[str]:
    """Check required sections and document quality."""
    return review_validator.check_structure(
        lines, REQUIRED_SECTIONS, 20, "code review"
    )


def check_review_completeness(text: str) -> list[str]:
    """Verify all 3 reviewer perspectives are represented."""
    issues: list[str] = []
    text_lower = text.lower()

    missing = [
        kw for kw in REVIEWER_KEYWORDS if kw not in text_lower
    ]

    if missing:
        missing_list = ", ".join(missing)
        issues.append(
            f"Review perspectives not mentioned: {missing_list}. "
            "Expected all 3 specialist reviewers represented."
        )

    return issues


def check_critical_resolution(text: str) -> list[str]:
    """Check that critical issues are marked as resolved."""
    issues: list[str] = []
    text_lower = text.lower()

    has_critical = bool(
        re.search(r"critical", text_lower)
    )

    if has_critical:
        resolved_indicators = [
            "resolved", "fixed", "all resolved",
            "no critical", "none found",
        ]
        has_resolution = any(
            ind in text_lower for ind in resolved_indicators
        )
        if not has_resolution:
            issues.append(
                "Critical issues mentioned but no resolution "
                "status found. Mark critical issues as resolved "
                "or indicate none were found."
            )

    return issues


def check_plan_coverage(
    review_text: str, plan_path: str
) -> list[str]:
    """Cross-reference review against solution plan objects."""
    issues: list[str] = []

    plan_text = Path(plan_path).read_text(encoding="utf-8")

    plan_ids = set(OBJECT_ID_PATTERN.findall(plan_text))
    review_ids = set(OBJECT_ID_PATTERN.findall(review_text))

    # Filter to likely AL object IDs (50000-99999 range)
    plan_obj_ids = {
        oid for oid in plan_ids
        if 50000 <= int(oid) <= 99999
    }
    review_obj_ids = {
        oid for oid in review_ids
        if 50000 <= int(oid) <= 99999
    }

    if not plan_obj_ids:
        return issues

    missing = plan_obj_ids - review_obj_ids
    if missing:
        missing_sorted = sorted(missing, key=int)
        missing_list = ", ".join(missing_sorted)
        coverage = len(plan_obj_ids - missing) / len(plan_obj_ids)
        issues.append(
            f"Plan objects not referenced in review: "
            f"{missing_list} "
            f"(coverage: {round(coverage * 100)}%)"
        )

    return issues


def main() -> int:
    if len(sys.argv) < 2:
        print(
            f"Usage: {sys.argv[0]} <code-review.md> "
            "[solution-plan.md]"
        )
        return 1

    review_path = sys.argv[1]
    plan_path = sys.argv[2] if len(sys.argv) > 2 else None

    if not Path(review_path).exists():
        print(f"File not found: {review_path}")
        return 1

    text, lines = review_validator.read_text_lines(review_path)

    all_issues: list[str] = []

    # 1. Structural checks
    struct_issues = check_review_structure(lines)
    if struct_issues:
        all_issues.append("--- Structure ---")
        all_issues.extend(struct_issues)

    # 2. Review completeness
    review_issues = check_review_completeness(text)
    if review_issues:
        all_issues.append("--- Review Coverage ---")
        all_issues.extend(review_issues)

    # 3. Critical issue resolution
    crit_issues = check_critical_resolution(text)
    if crit_issues:
        all_issues.append("--- Critical Issues ---")
        all_issues.extend(crit_issues)

    # 4. Plan object coverage (optional)
    if plan_path:
        if not Path(plan_path).exists():
            all_issues.append("--- Plan Coverage ---")
            all_issues.append(
                f"Plan file not found: {plan_path}"
            )
        else:
            plan_issues = check_plan_coverage(text, plan_path)
            if plan_issues:
                all_issues.append("--- Plan Coverage ---")
                all_issues.extend(plan_issues)
    else:
        auto_path = (
            Path(review_path).parent / "02-solution-plan.md"
        )
        if auto_path.exists():
            plan_issues = check_plan_coverage(
                text, str(auto_path)
            )
            if plan_issues:
                all_issues.append("--- Plan Coverage ---")
                all_issues.extend(plan_issues)

    # Filter section headers for count
    real_issues = [
        i for i in all_issues if not i.startswith("---")
    ]

    if not real_issues:
        print(f"PASS: All checks passed for {review_path}")
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
