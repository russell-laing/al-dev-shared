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
from fnmatch import fnmatchcase

TEMP_PATTERNS = [
    ".dev/????-??-??-*.md",          # Dated research files
    ".dev/*-progress.md",            # Named progress scratch files
    ".dev/*-checkpoint.json",        # Checkpoint files
    ".dev/*-work*.json",             # Work-in-progress JSON
    ".dev/*-draft*.md",              # Draft markdown
    "docs/superpowers/plans/*.md",   # Raw plans, including archived legacy paths
    "docs/superpowers/specs/*.md",   # Raw specs
]

EXCLUDE = [
    ".dev/progress.md",                 # Active progress file
    "docs/superpowers/plans/.gitkeep",  # Directory marker
    "docs/superpowers/specs/.gitkeep",  # Directory marker
]


def get_staged_files():
    """Return list of staged files in the current commit."""
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip().split("\n") if result.stdout.strip() else []


def matches_pattern(path, patterns):
    """Check if path matches any glob pattern.

    Uses fnmatch-style matching so rules apply consistently to nested paths.
    """
    for pattern in patterns:
        if fnmatchcase(path, pattern):
            return True
    return False


def find_temporary_artifacts(paths):
    """Return staged paths that should not be committed."""
    leaks = []
    for path in paths:
        if path and matches_pattern(path, TEMP_PATTERNS):
            if not matches_pattern(path, EXCLUDE):
                leaks.append(path)
    return leaks


def validate():
    """Check staged files for temporary artifacts."""
    leaks = find_temporary_artifacts(get_staged_files())

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
