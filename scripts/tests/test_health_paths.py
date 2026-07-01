from __future__ import annotations

from pathlib import Path

from scripts.al_dev_tools.health.paths import (
    compatibility_ledger_path,
    dispositions_archived_root,
    dispositions_current_view_path,
    dispositions_events_root,
    dispositions_history_root,
    dispositions_index_path,
    dispositions_jsonl_migration_audit_path,
    dispositions_open_view_path,
    docs_health_root,
)


def test_health_paths_are_root_relative() -> None:
    root = Path("/tmp/example-root")
    assert docs_health_root(root) == root / "docs" / "health"
    assert dispositions_archived_root(root) == root / "docs" / "health" / "archived"
    assert dispositions_events_root(root) == root / "docs" / "health" / "dispositions_events"
    assert dispositions_history_root(root) == root / "docs" / "health" / "dispositions_history"
    assert compatibility_ledger_path(root) == root / "docs" / "health" / "dispositions.md"
    assert dispositions_current_view_path(root) == root / "docs" / "health" / "dispositions_current.md"
    assert dispositions_open_view_path(root) == root / "docs" / "health" / "dispositions_open.md"
    assert dispositions_index_path(root) == root / "docs" / "health" / "dispositions_index.json"
    assert (
        dispositions_jsonl_migration_audit_path(root)
        == root / "docs" / "health" / "dispositions_jsonl_migration_audit.md"
    )
