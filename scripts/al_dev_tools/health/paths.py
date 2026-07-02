"""Canonical `docs/health` path helpers for health scripts.

Note: All path helpers require an explicit `root` parameter to prevent
cwd-relative path resolution. The default Path(".") is removed to ensure
callers are intentional about their root directory (typically REPO_ROOT).
"""

from __future__ import annotations

from pathlib import Path


DOCS_HEALTH = Path("docs") / "health"
DISPOSITIONS_EVENTS = DOCS_HEALTH / "dispositions_events"
DISPOSITIONS_HISTORY = DOCS_HEALTH / "dispositions_history"
DISPOSITIONS_LEDGER = DOCS_HEALTH / "dispositions.md"
DISPOSITIONS_OPEN = DOCS_HEALTH / "dispositions_open.md"
DISPOSITIONS_CURRENT = DOCS_HEALTH / "dispositions_current.md"
DISPOSITIONS_INDEX = DOCS_HEALTH / "dispositions_index.json"
DISPOSITIONS_ARCHIVED = DOCS_HEALTH / "archived"
DISPOSITIONS_JSONL_MIGRATION_AUDIT = DOCS_HEALTH / "dispositions_jsonl_migration_audit.md"


def docs_health_root(root: Path | None = None) -> Path:
    if root is None:
        raise TypeError("docs_health_root() requires an explicit 'root' parameter to prevent cwd-relative resolution")
    return root / DOCS_HEALTH


def dispositions_archived_root(root: Path | None = None) -> Path:
    if root is None:
        raise TypeError("dispositions_archived_root() requires an explicit 'root' parameter")
    return root / DISPOSITIONS_ARCHIVED


def dispositions_events_root(root: Path | None = None) -> Path:
    if root is None:
        raise TypeError("dispositions_events_root() requires an explicit 'root' parameter")
    return root / DISPOSITIONS_EVENTS


def dispositions_history_root(root: Path | None = None) -> Path:
    if root is None:
        raise TypeError("dispositions_history_root() requires an explicit 'root' parameter")
    return root / DISPOSITIONS_HISTORY


def compatibility_ledger_path(root: Path | None = None) -> Path:
    if root is None:
        raise TypeError("compatibility_ledger_path() requires an explicit 'root' parameter")
    return root / DISPOSITIONS_LEDGER


def dispositions_open_view_path(root: Path | None = None) -> Path:
    if root is None:
        raise TypeError("dispositions_open_view_path() requires an explicit 'root' parameter")
    return root / DISPOSITIONS_OPEN


def dispositions_current_view_path(root: Path | None = None) -> Path:
    if root is None:
        raise TypeError("dispositions_current_view_path() requires an explicit 'root' parameter")
    return root / DISPOSITIONS_CURRENT


def dispositions_index_path(root: Path | None = None) -> Path:
    if root is None:
        raise TypeError("dispositions_index_path() requires an explicit 'root' parameter")
    return root / DISPOSITIONS_INDEX


def dispositions_jsonl_migration_audit_path(root: Path | None = None) -> Path:
    if root is None:
        raise TypeError("dispositions_jsonl_migration_audit_path() requires an explicit 'root' parameter")
    return root / DISPOSITIONS_JSONL_MIGRATION_AUDIT
