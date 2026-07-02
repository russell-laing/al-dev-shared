"""Shared git utilities for path normalization across scripts."""

from __future__ import annotations

import subprocess
from pathlib import Path


def get_changed_paths(repo_root: Path, since_ref: str) -> set[Path]:
    """Resolve changed paths from git diff output.

    Returns a set of resolved absolute paths that changed since the given ref.
    This implementation is canonical and shared across all git path resolution.

    Args:
        repo_root: The repository root directory.
        since_ref: The git reference to diff against (e.g., 'HEAD').

    Returns:
        Set of absolute Path objects for files changed since since_ref.
    """
    actual_root = Path(
        subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=repo_root, capture_output=True, text=True, check=True,
        ).stdout.strip()
    )
    out = subprocess.run(
        ["git", "diff", "--name-only", since_ref],
        cwd=repo_root, capture_output=True, text=True, check=True,
    ).stdout.splitlines()
    return {(actual_root / line.strip()).resolve() for line in out if line.strip()}
