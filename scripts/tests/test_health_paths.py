from __future__ import annotations

from pathlib import Path

from scripts.al_dev_tools.health.paths import (
    compatibility_ledger_path,
    dispositions_events_root,
    dispositions_history_root,
    dispositions_index_path,
    dispositions_open_view_path,
)


def test_health_paths_are_root_relative() -> None:
    root = Path("/tmp/example-root")
    assert dispositions_events_root(root) == root / "docs" / "health" / "dispositions-events"
    assert dispositions_history_root(root) == root / "docs" / "health" / "dispositions-history"
    assert compatibility_ledger_path(root) == root / "docs" / "health" / "dispositions.md"
    assert dispositions_open_view_path(root) == root / "docs" / "health" / "dispositions-open.md"
    assert dispositions_index_path(root) == root / "docs" / "health" / "dispositions-index.json"
