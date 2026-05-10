#!/usr/bin/env python3
"""Validate solution plan structure and requirements coverage.

Usage:
    python3 validate-plan.py <path-to-solution-plan.md> [path-to-requirements.md]

Exit codes:
    0 - All checks pass
    1 - Validation issues found (printed to stdout)
"""

import re
import sys
from pathlib import Path


REQUIRED_SECTIONS = [
    "Overview",
    "Architecture",
    "Integration",
    "Testability",
    "Implementation",
    "Rationale",
]

ARCHITECTURE_SUBSECTIONS = [
    "Component",
    "Data",
    "API",
]

# Matches REQ-NNN definitions as markdown headings in requirements doc
REQ_TOKEN_PATTERN = re.compile(r"^###\s+REQ-(\d+)", re.MULTILINE)

# Matches REQ-NNN references in plan text
REQ_REF_PATTERN = re.compile(r"REQ-(\d+)")


def check_structure(text: str, lines: list[str]) -> list[str]:
    """Check required sections and minimum length."""
    issues: list[str] = []

    if len(lines) < 30:
        issues.append(
            f"Document too short ({len(lines)} lines). "
            "Expected 30+ for a meaningful solution plan."
        )

    headings = [
        ln.lstrip("#").strip() for ln in lines if ln.startswith("#")
    ]
    heading_text = " ".join(headings).lower()

    for section in REQUIRED_SECTIONS:
        if section.lower() not in heading_text:
            issues.append(f"Missing required section: '{section}'")

    for subsection in ARCHITECTURE_SUBSECTIONS:
        if subsection.lower() not in heading_text and subsection.lower() not in text.lower():
            issues.append(
                f"Architecture missing subsection or mention: "
                f"'{subsection}'"
            )

    for i, line in enumerate(lines[:-1]):
        if line.startswith("#") and lines[i + 1].startswith("#"):
            issues.append(
                f"Possibly empty section at line {i + 1}: "
                f"'{line.strip()}'"
            )

    return issues


def check_requirements_coverage(
    plan_text: str, req_path: str
) -> list[str]:
    """Cross-reference plan against requirements document."""
    issues: list[str] = []

    req_text = Path(req_path).read_text(encoding="utf-8")
    req_tokens = REQ_TOKEN_PATTERN.findall(req_text)

    if not req_tokens:
        issues.append(
            f"No REQ tokens found in {req_path}. "
            "Cannot check traceability."
        )
        return issues

    req_ids = sorted(set(req_tokens), key=int)
    plan_refs = set(REQ_REF_PATTERN.findall(plan_text))

    covered = [rid for rid in req_ids if rid in plan_refs]
    missing = [rid for rid in req_ids if rid not in plan_refs]

    total = len(req_ids)
    covered_count = len(covered)

    if missing:
        missing_list = ", ".join(f"REQ-{m}" for m in missing)
        issues.append(
            f"Requirements not referenced in plan: {missing_list}"
        )

    coverage_pct = (
        round(covered_count / total * 100) if total else 0
    )
    label = "PASS" if not missing else "WARN"
    issues.insert(
        0,
        f"[{label}] Requirements coverage: "
        f"{covered_count}/{total} ({coverage_pct}%)",
    )

    return issues


def main() -> int:
    if len(sys.argv) < 2:
        print(
            f"Usage: {sys.argv[0]} <solution-plan.md> "
            "[requirements.md]"
        )
        return 1

    plan_path = sys.argv[1]
    req_path = sys.argv[2] if len(sys.argv) > 2 else None

    if not Path(plan_path).exists():
        print(f"File not found: {plan_path}")
        return 1

    text = Path(plan_path).read_text(encoding="utf-8")
    lines = text.splitlines()

    all_issues: list[str] = []

    # 1. Structural checks
    struct_issues = check_structure(text, lines)
    if struct_issues:
        all_issues.append("--- Structure ---")
        all_issues.extend(struct_issues)

    # 2. Requirements traceability (optional)
    if req_path:
        if not Path(req_path).exists():
            all_issues.append("--- Traceability ---")
            all_issues.append(
                f"Requirements file not found: {req_path}"
            )
        else:
            rtm_issues = check_requirements_coverage(
                text, req_path
            )
            if rtm_issues:
                all_issues.append("--- Traceability ---")
                all_issues.extend(rtm_issues)
    else:
        # Auto-detect requirements file
        auto_path = Path(plan_path).parent / "01-requirements.md"
        if auto_path.exists():
            rtm_issues = check_requirements_coverage(
                text, str(auto_path)
            )
            if rtm_issues:
                all_issues.append("--- Traceability ---")
                all_issues.extend(rtm_issues)

    # Filter to real issues (exclude PASS lines)
    real_issues = [
        i for i in all_issues
        if not i.startswith("[PASS]") and not i.startswith("---")
    ]

    if not real_issues:
        for line in all_issues:
            if line.startswith("[PASS]"):
                print(line)
        print(f"PASS: All checks passed for {plan_path}")
        return 0

    print(f"ISSUES FOUND: {len(real_issues)}")
    for item in all_issues:
        if item.startswith("---"):
            print(f"\n{item}")
        else:
            prefix = "  " if not item.startswith("[") else ""
            print(f"{prefix}{item}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
