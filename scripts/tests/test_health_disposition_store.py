"""Tests for health_disposition_store helpers."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
STORE_PATH = REPO_ROOT / "scripts" / "health_disposition_store.py"
SPEC = importlib.util.spec_from_file_location("health_disposition_store", STORE_PATH)
assert SPEC is not None and SPEC.loader is not None
STORE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = STORE
SPEC.loader.exec_module(STORE)


class ShardPathTest(unittest.TestCase):
    def test_shard_path_uses_year_and_month(self) -> None:
        result = STORE.shard_path_for_date("2026-06-12")
        self.assertEqual(result, Path("2026") / "2026-06.md")


class MaterializeViewTest(unittest.TestCase):
    def test_current_view_keeps_latest_row_per_finding_key(self) -> None:
        rows = [
            {
                "id": "#001",
                "surface": "tooling",
                "dimension": "quality",
                "object": "record-health-dispositions",
                "finding": "Schema count mismatch",
                "disposition": "accepted",
                "date": "2026-06-11",
                "note": "queued",
            },
            {
                "id": "#002",
                "surface": "tooling",
                "dimension": "quality",
                "object": "record-health-dispositions",
                "finding": "Schema count mismatch",
                "disposition": "fixed",
                "date": "2026-06-12",
                "note": "abc1234 closes row 1",
            },
        ]

        current = STORE.materialize_current_view(rows)

        self.assertEqual(len(current), 1)
        self.assertEqual(current[0]["id"], "#002")
        self.assertEqual(current[0]["disposition"], "fixed")

    def test_disposition_key_normalizes_surrounding_and_internal_whitespace(self) -> None:
        row = {
            "surface": "tooling",
            "dimension": "quality",
            "object": "record-health-dispositions",
            "finding": "Schema count mismatch",
        }

        self.assertEqual(
            STORE.disposition_key(row),
            STORE.disposition_key({**row, "finding": "  Schema   count mismatch  "}),
        )


if __name__ == "__main__":
    unittest.main()
