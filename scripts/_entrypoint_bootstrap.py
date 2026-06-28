"""Helpers for running repo-local scripts directly by file path."""

from __future__ import annotations

import sys
from pathlib import Path


def bootstrap_repo(script_file: str) -> Path:
    repo_root = Path(script_file).resolve().parents[1]
    repo_root_str = str(repo_root)
    if repo_root_str not in sys.path:
        sys.path.insert(0, repo_root_str)
    return repo_root


__all__ = ["bootstrap_repo"]
