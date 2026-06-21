"""Tests for migrating Markdown health dispositions to JSONL events."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MIGRATE_PATH = REPO_ROOT / "scripts" / "migrate_health_disposition_jsonl.py"


def load_migrate():
    spec = importlib.util.spec_from_file_location("migrate_health_disposition_jsonl", MIGRATE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class MigrationTest(unittest.TestCase):
    def test_migration_assigns_event_ids_and_preserves_legacy_ids(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            history = root / "docs" / "health" / "dispositions-history" / "2026"
            history.mkdir(parents=True)
            (history / "2026-06.md").write_text(
                "| ID | Surface | Dimension | Object | Finding | Disposition | Date | Evidence / note |\n"
                "|----|---------|-----------|--------|---------|-------------|------|------------------|\n"
                "| #976 | tooling | quality | validate_health_loop_state.py | Enum omits revise-plugin-plan | accepted | 2026-06-19 | queued |\n"
                "| #977 | tooling | quality | validate_health_loop_state.py | Enum omits revise-plugin-plan | fixed | 2026-06-19 | 8f3c205 closes #976 |\n",
                encoding="utf-8",
            )

            report = load_migrate().migrate_to_jsonl(root)

            shard = root / "docs" / "health" / "dispositions-events" / "2026" / "2026-06.jsonl"
            events = [json.loads(line) for line in shard.read_text(encoding="utf-8").splitlines()]
            self.assertEqual(2, len(events))
            self.assertEqual("disp_20260619_000001", events[0]["event_id"])
            self.assertEqual("#976", events[0]["legacy_id"])
            self.assertEqual(["disp_20260619_000001"], events[1]["closes_event_ids"])
            self.assertEqual(2, report["total_events"])

    def test_migration_audit_reports_duplicate_legacy_ids(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            history = root / "docs" / "health" / "dispositions-history" / "2026"
            history.mkdir(parents=True)
            (history / "2026-06.md").write_text(
                "| ID | Surface | Dimension | Object | Finding | Disposition | Date | Evidence / note |\n"
                "|----|---------|-----------|--------|---------|-------------|------|------------------|\n"
                "| #600 | tooling | quality | one | Finding A | accepted | 2026-06-19 | queued |\n"
                "| #600 | tooling | quality | two | Finding B | declined | 2026-06-19 | not valid |\n",
                encoding="utf-8",
            )

            report = load_migrate().migrate_to_jsonl(root)

            audit = root / "docs" / "health" / "dispositions-jsonl-migration-audit.md"
            self.assertIn("#600", audit.read_text(encoding="utf-8"))
            self.assertEqual(["#600"], report["duplicate_legacy_ids"])


if __name__ == "__main__":
    unittest.main()
