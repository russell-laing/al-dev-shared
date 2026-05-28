#!/usr/bin/env python3
"""
Validator for knowledge file quality. Detects structural stubs and issues.

FALSE POSITIVES ELIMINATED (2026-05-22):
- [DEAD-REF] path resolution: Fixed double "knowledge/" prefix in reference checks
- [NO-CODE] emoji headers: Skip sections with emoji/checkmark titles (have content in body)
- [THIN] summary sections: Skip intentional summary sections (Goal, Overview, etc.)

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

def _format_issue(path: str, rule: str, issue: str, fix: str) -> str:
    return (
        f"{path}\n"
        f"  rule: {rule}\n"
        f"  issue: {issue}\n"
        f"  fix: {fix}"
    )


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

# Section names that are intentionally brief summaries
SUMMARY_SECTIONS = {
    "goal",
    "summary",
    "overview",
    "introduction",
    "rationale",
    "motivation",
    "purpose",
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


def has_emoji_or_checkmark(text: str) -> bool:
    """Check if text contains status emoji used in markdown headings.

    Detects emoji commonly used in knowledge file section headers:
    - Status emoji: 🟢 🟡 🔴 ✅ ❌ 🔵
    - Fallback: broader emoji range for future extensibility
    """
    # Known status emoji in use across knowledge files
    known_emoji = {'🟢', '🟡', '🔴', '✅', '❌', '🔵'}
    if any(e in text for e in known_emoji):
        return True

    # Fallback: detect emoji in standard emoji range U+1F300–U+1F9FF
    # Using non-raw string with proper Unicode escapes
    pattern = '[\U0001F300-\U0001F9FF]'
    return bool(re.search(pattern, text))


# Quick test of emoji detection (validates regex works)
assert has_emoji_or_checkmark("🟢 TRIVIAL") == True
assert has_emoji_or_checkmark("✅ Example") == True
assert has_emoji_or_checkmark("Normal text") == False
assert has_emoji_or_checkmark("## Overview") == False


def find_knowledge_references(content: str) -> List[Tuple[str, int]]:
    """Extract all knowledge file references (filename only, no 'knowledge/' prefix)."""
    pattern = r"knowledge/([\w\-]+\.md)"
    matches = re.finditer(pattern, content)
    return [(match.group(1), match.start()) for match in matches]


def check_thin_sections(filepath: str, sections: List) -> List[str]:
    """Check for sections with minimal body content.

    FALSE POSITIVES FIXED:
    - Skips sections with emoji/checkmark headers (e.g., "🟢 TRIVIAL", "✅ Good Example")
      These typically use subsections for actual content, so brief headers are intentional
    - Skips known summary sections (Goal, Overview, etc.) which are intentionally brief

    REAL ISSUES DETECTED:
    - Level 3+ sections with < 3 lines of content that need actual expansion

    Skip behavior:
    - Level 1-2 headings (document titles and section headers)
    - Known summary sections (Goal, Overview, etc.) which are intentionally brief
    - Sections with emoji/checkmark headers
    """
    issues = []
    for heading, level, body_start, body in sections:
        # Skip level-2 (##) headings and special sections
        if level <= 2:
            continue

        # Skip known summary sections that are intentionally brief
        if heading.lower() in SUMMARY_SECTIONS:
            continue

        # Skip sections with emoji/checkmark headers (typically have content in subsections)
        if has_emoji_or_checkmark(heading):
            continue

        line_count = count_body_lines(body)
        if line_count < 3:
            issues.append(
                _format_issue(
                    filepath,
                    "knowledge-stub",
                    f'section "{heading}" has {line_count} content line(s) — too thin for a level-{level} section',
                    "expand the section body or remove the header if the content belongs elsewhere",
                )
            )

    return issues


def check_code_implication(filepath: str, sections: List) -> List[str]:
    """Check sections that imply code but have no code blocks.

    FALSE POSITIVES FIXED:
    - Skips sections with emoji/checkmark headers (typically contain code in body subsections,
      or intentionally illustrate good/bad patterns without full code examples)

    REAL ISSUES DETECTED:
    - Sections implying code (contain keywords like "example:", "pattern:", "bad:", "usage:", etc.)
      that lack code block examples and are not intentionally brief
    """
    issues = []
    for heading, level, body_start, body in sections:
        # Skip sections that are short by design
        if heading.lower() in ("overview", "usage", "references"):
            continue

        # Skip sections with emoji/checkmark headers (typically section titles with examples below)
        if has_emoji_or_checkmark(heading):
            continue

        heading_lower = heading.lower()
        body_lower = body.lower()

        # Check if heading or first line implies code
        implies_code = any(
            keyword in heading_lower or keyword in body_lower for keyword in CODE_KEYWORDS
        )

        if implies_code and not has_code_block(body) and count_body_lines(body) > 2:
            issues.append(
                _format_issue(
                    filepath,
                    "knowledge-no-code",
                    f'section "{heading}" implies code (keyword in heading or body) but has no fenced code block',
                    "add a fenced code block example, or rename the heading to remove the code implication",
                )
            )

    return issues


def check_references(filepath: str, content: str, knowledge_dir: Path) -> List[str]:
    """Check for broken cross-references.

    FALSE POSITIVES FIXED:
    - Fixed path duplication: references like "knowledge/file.md" no longer produce
      "knowledge/knowledge/file.md" lookups (extract filename only from pattern match)

    REAL ISSUES DETECTED:
    - References to files that don't exist in the knowledge directory
    """
    issues = []
    refs = find_knowledge_references(content)

    for ref_filename, _ in refs:
        # Skip self-references (file referencing itself is fine)
        if ref_filename == Path(filepath).name:
            continue

        ref_path = knowledge_dir / ref_filename
        if not ref_path.exists():
            issues.append(
                _format_issue(
                    filepath,
                    "knowledge-dead-ref",
                    f"reference to knowledge/{ref_filename} does not resolve to an existing file",
                    f"check the filename for typos or create the missing file at knowledge/{ref_filename}",
                )
            )

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
            warnings.append(
                _format_issue(
                    str_path,
                    "file-unreadable",
                    f"could not read file: {e}",
                    "check file encoding (must be UTF-8) or fix file permissions",
                )
            )
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
        print()
        print("\n\n".join(warnings))

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
