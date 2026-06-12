"""Tests for health_disposition_store helpers."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import types
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


class ParseLedgerTest(unittest.TestCase):
    def test_parse_markdown_table_reads_id_and_eight_columns(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            ledger = Path(d) / "2026-06.md"
            ledger.write_text(
                "| ID | Surface | Dimension | Object | Finding | Disposition | Date | Evidence / note |\n"
                "|----|---------|-----------|--------|---------|-------------|------|------------------|\n"
                "| #595 | tooling | quality | record-health-dispositions"
                " | Schema count mismatch | accepted | 2026-06-12 | queued |\n",
                encoding="utf-8",
            )

            rows = STORE.parse_ledger_file(ledger)

            self.assertEqual(rows[0]["id"], "#595")
            self.assertEqual(rows[0]["surface"], "tooling")
            self.assertEqual(rows[0]["disposition"], "accepted")


class AppendRowTest(unittest.TestCase):
    def test_append_row_creates_month_shard_with_header(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            history_root = Path(d) / "docs" / "health" / "dispositions-history"
            row = {
                "id": "#596",
                "surface": "tooling",
                "dimension": "quality",
                "object": "record-health-dispositions",
                "finding": "Terminology drift",
                "disposition": "accepted",
                "date": "2026-06-12",
                "note": "queued",
            }

            shard = STORE.append_row(history_root, row)

            text = shard.read_text(encoding="utf-8")
            self.assertEqual(shard.name, "2026-06.md")
            self.assertIn(
                "| #596 | tooling | quality | record-health-dispositions |", text
            )


class RenderCurrentViewTest(unittest.TestCase):
    def test_render_current_view_writes_small_projection(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            output = Path(d) / "docs" / "health" / "dispositions.md"
            rows = [
                {
                    "id": "#595",
                    "surface": "tooling",
                    "dimension": "quality",
                    "object": "record-health-dispositions",
                    "finding": "Schema count mismatch",
                    "disposition": "accepted",
                    "date": "2026-06-12",
                    "note": "queued",
                }
            ]

            STORE.render_current_view(output, rows)
            text = output.read_text(encoding="utf-8")

            self.assertTrue(text.startswith("# Health Finding Dispositions"))
            self.assertIn("generated current-state view", text)
            self.assertIn(
                "| #595 | tooling | quality | record-health-dispositions |", text
            )


MIGRATE_PATH = REPO_ROOT / "scripts" / "migrate_health_disposition_store.py"


def _load_migrate() -> types.ModuleType:
    spec = importlib.util.spec_from_file_location("migrate_health_disposition_store", MIGRATE_PATH)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


class MigrateStoreTest(unittest.TestCase):
    def test_migration_preserves_row_count_and_produces_smaller_current_view(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            source = Path(d) / "docs" / "health" / "dispositions.md"
            source.parent.mkdir(parents=True)
            source.write_text(
                "# Health Finding Dispositions\n\n"
                "| ID | Surface | Dimension | Object | Finding | Disposition | Date | Evidence / note |\n"
                "|----|---------|-----------|--------|---------|-------------|------|------------------|\n"
                "| #595 | tooling | quality | record-health-dispositions"
                " | Schema count mismatch | accepted | 2026-06-12 | queued |\n"
                "| #596 | tooling | quality | record-health-dispositions"
                " | Schema count mismatch | fixed | 2026-06-13 | abc1234 closes row 1 |\n",
                encoding="utf-8",
            )
            history_root = Path(d) / "docs" / "health" / "dispositions-history"

            mod = _load_migrate()
            report = mod.migrate_store(source, history_root)

            self.assertEqual(report["source_rows"], 2)
            self.assertEqual(report["written_rows"], 2)
            self.assertEqual(report["current_rows"], 1)


if __name__ == "__main__":
    unittest.main()
