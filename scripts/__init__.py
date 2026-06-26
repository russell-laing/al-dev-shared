"""Explicit package for repo-local maintainer automation."""

from __future__ import annotations

from pathlib import Path

SCRIPTS_ROOT = Path(__file__).resolve().parent
REPO_ROOT = SCRIPTS_ROOT.parent

__all__ = ["REPO_ROOT", "SCRIPTS_ROOT"]
