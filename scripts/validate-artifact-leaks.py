#!/usr/bin/env python3
"""
Detect temporary artifacts staged for commit.

Temporary artifacts are one-off outputs that should never be version-tracked:
- Dated research files: .dev/YYYY-MM-DD-*.md
- Spec files: docs/superpowers/specs/*.md (except .gitkeep)
- Working checkpoints: .dev/*-checkpoint.json, .dev/*-work*.json
- Draft reviews: .dev/*-draft*.md

This script is run as a pre-commit hook to catch leaks early.
"""

import subprocess
import sys
from pathlib import Path

TEMP_PATTERNS = [
    ".dev/????-??-??-*.md",      # Dated research files
    ".dev/*-checkpoint.json",     # Checkpoint files
    ".dev/*-work*.json",          # Work-in-progress JSON
    ".dev/*-draft*.md",           # Draft markdown
    "docs/superpowers/specs/*",   # Spec directory (except .gitkeep)
]

EXCLUDE = [
    ".dev/progress.md",                # Active progress file
    "docs/superpowers/specs/.gitkeep", # Directory marker
]


def get_staged_files():
    """Return list of staged files in the current commit."""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip().split("\n") if result.stdout.strip() else []
    except subprocess.CalledProcessError as e:
        print(f"Error getting staged files: {e}", file=sys.stderr)
        return []


def matches_pattern(path, patterns):
    """Check if path matches any glob pattern.

    Uses pathlib.Path.match() which supports glob syntax:
    - ? matches any single character
    - * matches zero or more characters
    - [seq] matches any character in seq

    Example: '.dev/????-??-??-*.md' matches '.dev/2026-06-29-test.md'
    """
    p = Path(path)
    for pattern in patterns:
        if p.match(pattern):
            return True
    return False


def validate():
    """Check staged files for temporary artifacts."""
    staged = get_staged_files()
    leaks = []

    for f in staged:
        if f and matches_pattern(f, TEMP_PATTERNS):
            if not matches_pattern(f, EXCLUDE):
                leaks.append(f)

    if leaks:
        print("\n❌ Pre-commit check FAILED: Temporary artifacts detected\n",
              file=sys.stderr)
        print("Remove these files from staging before committing:",
              file=sys.stderr)
        for f in leaks:
            print(f"  - {f}", file=sys.stderr)
        print("\nThese are one-off outputs that shouldn't be version-tracked.",
              file=sys.stderr)
        print("See CLAUDE.md 'Artifact Lifecycle' section for details.",
              file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(validate())
