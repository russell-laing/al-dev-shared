"""Helpers for locating and validating runtime artifacts in ``.dev``."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


@dataclass(frozen=True)
class RuntimeArtifactRule:
    """Declarative rule for a runtime artifact check."""

    skill: str
    pattern: str
    markers: tuple[str, ...]
    problem: str


def latest_runtime_artifact(repo_root: Path, pattern: str) -> Path | None:
    """Return the newest matching artifact under ``repo_root/.dev``.

    The selection is deterministic for a fixed filesystem state. When multiple
    files have the same modification timestamp, the lexicographically greatest
    path wins as a stable tie-breaker.
    """

    dev_root = repo_root / ".dev"
    if not dev_root.exists():
        return None

    candidates = [path for path in dev_root.glob(pattern) if path.is_file()]
    if not candidates:
        return None

    return max(candidates, key=lambda path: (path.stat().st_mtime_ns, path.as_posix()))


def contains_any_marker(content: str, markers: Sequence[str]) -> tuple[bool, str]:
    """Return whether any marker appears in ``content``.

    The second return value is a compact description of the missing marker set,
    suitable for validator diagnostics.
    """

    if any(marker in content for marker in markers):
        return True, ""
    return False, ", ".join(markers)
