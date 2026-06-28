"""Tests for migrating Markdown health dispositions to JSONL events."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.al_dev_tools.health import migrate_health_disposition_jsonl as migrate
from scripts.al_dev_tools.health.paths import (
    dispositions_events_root,
    dispositions_history_root,
    dispositions_jsonl_migration_audit_path,
)

REPO_ROOT = Path(__file__).resolve().parents[2]


class MigrationTest(unittest.TestCase):
    def test_migration_assigns_event_ids_and_preserves_legacy_ids(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            history = dispositions_history_root(root) / "2026"
            history.mkdir(parents=True)
            (history / "2026-06.md").write_text(
                "| ID | Surface | Dimension | Object | Finding | Disposition | Date | Evidence / note |\n"
                "|----|---------|-----------|--------|---------|-------------|------|------------------|\n"
                "| #976 | tooling | quality | validate_health_loop_state.py | Enum omits revise-plugin-plan | accepted | 2026-06-19 | queued |\n"
                "| #977 | tooling | quality | validate_health_loop_state.py | Enum omits revise-plugin-plan | fixed | 2026-06-19 | 8f3c205 closes #976 |\n",
                encoding="utf-8",
            )

            report = migrate.migrate_to_jsonl(root)

            shard = dispositions_events_root(root) / "2026" / "2026-06.jsonl"
            events = [json.loads(line) for line in shard.read_text(encoding="utf-8").splitlines()]
            self.assertEqual(2, len(events))
            self.assertEqual("disp_20260619_000001", events[0]["event_id"])
            self.assertEqual("#976", events[0]["legacy_id"])
            self.assertEqual(["disp_20260619_000001"], events[1]["closes_event_ids"])
            self.assertEqual(2, report["total_events"])

    def test_migration_audit_reports_duplicate_legacy_ids(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            history = dispositions_history_root(root) / "2026"
            history.mkdir(parents=True)
            (history / "2026-06.md").write_text(
                "| ID | Surface | Dimension | Object | Finding | Disposition | Date | Evidence / note |\n"
                "|----|---------|-----------|--------|---------|-------------|------|------------------|\n"
                "| #600 | tooling | quality | one | Finding A | accepted | 2026-06-19 | queued |\n"
                "| #600 | tooling | quality | two | Finding B | declined | 2026-06-19 | not valid |\n",
                encoding="utf-8",
            )

            report = migrate.migrate_to_jsonl(root)

            audit = dispositions_jsonl_migration_audit_path(root)
            self.assertIn("#600", audit.read_text(encoding="utf-8"))
            self.assertEqual(["#600"], report["duplicate_legacy_ids"])


if __name__ == "__main__":
    unittest.main()
