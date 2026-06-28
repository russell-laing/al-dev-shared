"""Canonical `docs/health` path helpers for health scripts."""

from __future__ import annotations

from pathlib import Path


DOCS_HEALTH = Path("docs") / "health"
DISPOSITIONS_EVENTS = DOCS_HEALTH / "dispositions-events"
DISPOSITIONS_HISTORY = DOCS_HEALTH / "dispositions-history"
DISPOSITIONS_LEDGER = DOCS_HEALTH / "dispositions.md"
DISPOSITIONS_OPEN = DOCS_HEALTH / "dispositions-open.md"
DISPOSITIONS_CURRENT = DOCS_HEALTH / "dispositions-current.md"
DISPOSITIONS_INDEX = DOCS_HEALTH / "dispositions-index.json"
DISPOSITIONS_ARCHIVED = DOCS_HEALTH / "archived"
DISPOSITIONS_JSONL_MIGRATION_AUDIT = DOCS_HEALTH / "dispositions-jsonl-migration-audit.md"


def docs_health_root(root: Path = Path(".")) -> Path:
    return root / DOCS_HEALTH


def dispositions_archived_root(root: Path = Path(".")) -> Path:
    return root / DISPOSITIONS_ARCHIVED


def dispositions_events_root(root: Path = Path(".")) -> Path:
    return root / DISPOSITIONS_EVENTS


def dispositions_history_root(root: Path = Path(".")) -> Path:
    return root / DISPOSITIONS_HISTORY


def compatibility_ledger_path(root: Path = Path(".")) -> Path:
    return root / DISPOSITIONS_LEDGER


def dispositions_open_view_path(root: Path = Path(".")) -> Path:
    return root / DISPOSITIONS_OPEN


def dispositions_current_view_path(root: Path = Path(".")) -> Path:
    return root / DISPOSITIONS_CURRENT


def dispositions_index_path(root: Path = Path(".")) -> Path:
    return root / DISPOSITIONS_INDEX


def dispositions_jsonl_migration_audit_path(root: Path = Path(".")) -> Path:
    return root / DISPOSITIONS_JSONL_MIGRATION_AUDIT
