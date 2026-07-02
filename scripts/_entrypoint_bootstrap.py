"""Helpers for running repo-local scripts directly by file path."""

from __future__ import annotations

import sys
from pathlib import Path


def bootstrap_repo(script_file: str) -> Path:
    # Walk up from script_file looking for the repo root (marked by .git),
    # rather than a fixed parents[N] — callers live at varying depths under
    # scripts/ (top-level scripts/foo.py vs nested scripts/al_dev_tools/health/foo.py)
    # and a fixed index silently resolves to the wrong directory for the latter.
    candidate = Path(script_file).resolve().parent
    while True:
        if (candidate / ".git").exists():
            repo_root = candidate
            break
        if candidate == candidate.parent:
            raise RuntimeError(f"could not locate repo root (no .git found) above {script_file}")
        candidate = candidate.parent
    repo_root_str = str(repo_root)
    if repo_root_str not in sys.path:
        sys.path.insert(0, repo_root_str)
    return repo_root


__all__ = ["bootstrap_repo"]
