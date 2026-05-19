#!/usr/bin/env python3
"""
Validator for knowledge file quality. Detects structural stubs and issues.

Usage:
  python3 validate-knowledge-quality.py [--path <dir>] [--strict] [--verbose]

Exit codes:
  0: No issues (or advisory-only with --strict off)
  1: Issues found (when --strict is set)
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple

# Files/patterns to exclude from validation (these are intentionally brief)
EXCLUDED_PATTERNS = [
    "doc-templates/",
    "quality-checklist.md",
    "code-review-template.md",
    "solution-plan-template.md",
    "skill-test-format.md",
    "interview-question-bank.md",  # Question bank is inherently concise
]

# Keywords that imply code blocks should follow
CODE_KEYWORDS = {
    "example:",
    "pattern:",
    "skeleton:",
    "good:",
    "bad:",
    "usage:",
    "**good**",
    "**bad**",
}

# Knowledge directory relative to repo root
KNOWLEDGE_DIR = "profile-al-dev-shared/knowledge"


def should_exclude(filepath: str) -> bool:
    """Check if file should be excluded from validation."""
    for pattern in EXCLUDED_PATTERNS:
        if pattern in filepath:
            return True
    return False


def parse_sections(content: str) -> List[Tuple[str, int, int, str]]:
    """Parse markdown sections. Returns list of (heading, level, line_num, body)."""
    sections = []
    lines = content.split("\n")
    current_heading = None
    current_level = 0
    body_start = 0

    for i, line in enumerate(lines):
        # Match heading
        match = re.match(r"^(#{1,6})\s+(.+)$", line)
        if match:
            level = len(match.group(1))
            heading = match.group(2).strip()

            # Save previous section if exists
            if current_heading:
                body = "\n".join(lines[body_start : i]).strip()
                sections.append((current_heading, current_level, body_start, body))

            current_heading = heading
            current_level = level
            body_start = i + 1

    # Save last section
    if current_heading:
        body = "\n".join(lines[body_start:]).strip()
        sections.append((current_heading, current_level, body_start, body))

    return sections


def has_code_block(text: str) -> bool:
    """Check if text contains a fenced code block."""
    return "```" in text


def count_body_lines(body: str) -> int:
    """Count non-blank lines in section body."""
    return len([line for line in body.split("\n") if line.strip()])


def find_knowledge_references(content: str) -> List[str]:
    """Extract all knowledge file references from content."""
    pattern = r"knowledge/[\w\-]+\.md"
    return re.findall(pattern, content)


def check_thin_sections(filepath: str, sections: List) -> List[str]:
    """Check for sections with minimal body content."""
    issues = []
    for heading, level, body_start, body in sections:
        # Skip level-2 (##) headings and special sections
        if level <= 2 or heading.lower() in ("overview", "usage", "example"):
            continue

        line_count = count_body_lines(body)
        if line_count < 3:
            issues.append(
                f"[THIN]     {filepath}: {heading} ({line_count} lines)"
            )

    return issues


def check_code_implication(filepath: str, sections: List) -> List[str]:
    """Check sections that imply code but have no code blocks."""
    issues = []
    for heading, level, body_start, body in sections:
        # Skip sections that are short by design
        if heading.lower() in ("overview", "usage", "references"):
            continue

        heading_lower = heading.lower()
        body_lower = body.lower()

        # Check if heading or first line implies code
        implies_code = any(
            keyword in heading_lower or keyword in body_lower for keyword in CODE_KEYWORDS
        )

        if implies_code and not has_code_block(body) and count_body_lines(body) > 2:
            issues.append(
                f"[NO-CODE]  {filepath}: {heading} — body implies code but has none"
            )

    return issues


def check_references(filepath: str, content: str, knowledge_dir: Path) -> List[str]:
    """Check for broken cross-references."""
    issues = []
    refs = find_knowledge_references(content)

    for ref in refs:
        # Skip self-references (file referencing itself is fine)
        if ref.endswith(Path(filepath).name):
            continue

        ref_path = knowledge_dir / ref
        if not ref_path.exists():
            issues.append(f"[DEAD-REF] {filepath}: {ref} (not found)")

    return issues


def validate_knowledge_dir(
    knowledge_dir: Path, verbose: bool = False
) -> Tuple[List[str], List[str]]:
    """Validate all knowledge files. Returns (warnings, clean_files)."""
    warnings = []
    clean_files = []

    if not knowledge_dir.exists():
        print(f"Error: Knowledge directory not found: {knowledge_dir}")
        sys.exit(1)

    md_files = sorted(knowledge_dir.rglob("*.md"))

    for filepath in md_files:
        rel_path = filepath.relative_to(knowledge_dir.parent)
        str_path = str(rel_path)

        # Check exclusions
        if should_exclude(str_path):
            if verbose:
                clean_files.append(f"[EXCLUDED] {str_path}")
            continue

        # Read and parse
        try:
            with open(filepath, "r") as f:
                content = f.read()
        except Exception as e:
            warnings.append(f"[ERROR]    {str_path}: {e}")
            continue

        sections = parse_sections(content)

        # Run checks
        file_warnings = []
        file_warnings.extend(check_thin_sections(str_path, sections))
        file_warnings.extend(check_code_implication(str_path, sections))
        file_warnings.extend(check_references(str_path, content, knowledge_dir))

        if file_warnings:
            warnings.extend(file_warnings)
        else:
            clean_files.append(str_path)

    return warnings, clean_files


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Validate knowledge file quality")
    parser.add_argument(
        "--path",
        default=KNOWLEDGE_DIR,
        help=f"Path to knowledge directory (default: {KNOWLEDGE_DIR})",
    )
    parser.add_argument(
        "--strict", action="store_true", help="Exit with code 1 if any warnings found"
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Show all file results"
    )

    args = parser.parse_args()

    # Resolve path
    knowledge_dir = Path(args.path)
    if not knowledge_dir.is_absolute():
        # Make relative to current directory
        knowledge_dir = Path.cwd() / knowledge_dir

    print(f"Validating {knowledge_dir}...")
    warnings, clean_files = validate_knowledge_dir(knowledge_dir, args.verbose)

    # Print results
    if warnings:
        print(f"\nWARNINGS ({len(warnings)}):")
        for warning in warnings:
            print(f"  {warning}")

    if args.verbose and clean_files:
        print(f"\nCLEAN ({len(clean_files)}):")
        for clean_file in clean_files:
            print(f"  {clean_file}")
    elif clean_files:
        print(f"\nPASS ({len(clean_files)} files clean)")

    print()

    # Exit code
    if warnings and args.strict:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
