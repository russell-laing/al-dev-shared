#!/usr/bin/env python3
"""
Parse AL compilation errors from .dev/compile-errors.log and group by category.
Outputs a markdown summary suitable for message reporting.
"""

import sys

def categorize_errors(log_file):
    """Read compile log and return errors grouped by category."""

    categories = {
        'naming_violations': [],    # AS0011, AS0012
        'schema_errors': [],         # E2007, E2008 (field/table not found)
        'compilation_errors': [],    # General compilation failures
        'warnings': []               # Minor issues
    }

    try:
        with open(log_file, 'r') as f:
            content = f.read()
    except FileNotFoundError:
        return categories, "No compile errors found"

    lines = content.split('\n')

    for line in lines:
        # Skip empty lines
        if not line.strip():
            continue

        # Naming violations
        if 'AS0011' in line or 'AS0012' in line:
            categories['naming_violations'].append(line.strip())
        # Schema errors (field/table not found)
        elif 'E2007' in line or 'E2008' in line or 'not found' in line.lower():
            categories['schema_errors'].append(line.strip())
        # Warnings
        elif 'warning' in line.lower():
            categories['warnings'].append(line.strip())
        # Compilation errors
        elif 'error' in line.lower():
            categories['compilation_errors'].append(line.strip())

    return categories, None

def format_summary(categories):
    """Format categorized errors into markdown summary."""

    summary = []

    for category_name, errors in categories.items():
        if not errors:
            continue

        # Format category name as title
        title = category_name.replace('_', ' ').title()
        summary.append(f"\n**{title}:** {len(errors)} issue(s)")

        # Show first 3 errors per category, abbreviated
        for error in errors[:3]:
            # Truncate long lines
            if len(error) > 120:
                error = error[:120] + "…"
            summary.append(f"  - {error}")

        if len(errors) > 3:
            summary.append(f"  - ... and {len(errors) - 3} more (see .dev/compile-errors.log)")

    return "\n".join(summary) if summary else "No errors found"

if __name__ == '__main__':
    log_path = sys.argv[1] if len(sys.argv) > 1 else '.dev/compile-errors.log'
    categories, error = categorize_errors(log_path)

    if error:
        print(error)
    else:
        print(format_summary(categories))
