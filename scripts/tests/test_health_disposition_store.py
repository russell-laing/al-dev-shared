"""Tests for health_disposition_store helpers."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.al_dev_tools.health import health_disposition_store as STORE
from scripts.al_dev_tools.health import migrate_health_disposition_store as MIGRATE


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
                "object": "record-plugin-dispositions",
                "finding": "Schema count mismatch",
                "disposition": "accepted",
                "date": "2026-06-11",
                "note": "queued",
            },
            {
                "id": "#002",
                "surface": "tooling",
                "dimension": "quality",
                "object": "record-plugin-dispositions",
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
            "object": "record-plugin-dispositions",
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
                "| #595 | tooling | quality | record-plugin-dispositions"
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
                "object": "record-plugin-dispositions",
                "finding": "Terminology drift",
                "disposition": "accepted",
                "date": "2026-06-12",
                "note": "queued",
            }

            shard = STORE.append_row(history_root, row)

            text = shard.read_text(encoding="utf-8")
            self.assertEqual(shard.name, "2026-06.md")
            self.assertIn(
                "| #596 | tooling | quality | record-plugin-dispositions |", text
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
                    "object": "record-plugin-dispositions",
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
                "| #595 | tooling | quality | record-plugin-dispositions |", text
            )


class ListOpenTest(unittest.TestCase):
    LEDGER = (
        "# Health Finding Dispositions\n\n"
        "| ID | Surface | Dimension | Object | Finding | Disposition | Date | Evidence / note |\n"
        "|----|---------|-----------|--------|---------|-------------|------|------------------|\n"
        "| #001 | tooling | design | lens-a | Model fit | accepted | 2026-06-05 | queued |\n"
        "| #002 | plugin | quality | skill-b | Bloat | accepted | 2026-06-06 | queued |\n"
        "| #003 | tooling | quality | skill-c | Clarity gap | accepted | 2026-06-07 | queued |\n"
        "| #004 | tooling | quality | skill-c | Clarity gap | fixed | 2026-06-08 | abc closes 3 |\n"
        "| #005 | plugin | design | skill-d | Merge candidate | declined | 2026-06-09 | out of scope |\n"
    )

    def _write_ledger(self, d: str) -> Path:
        ledger = Path(d) / "dispositions.md"
        ledger.write_text(self.LEDGER, encoding="utf-8")
        return ledger

    def test_lists_only_accepted_rows(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            ledger = self._write_ledger(d)
            rows = STORE.list_open(ledger)
            ids = sorted(r["id"] for r in rows)
            # #001 and #002 are open; #003 superseded by fixed #004; #005 declined.
            self.assertEqual(ids, ["#001", "#002"])

    def test_last_writer_wins_excludes_fixed_supersede(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            ledger = self._write_ledger(d)
            rows = STORE.list_open(ledger)
            self.assertNotIn("skill-c", {r["object"] for r in rows})

    def test_surface_and_dimension_filters(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            ledger = self._write_ledger(d)
            self.assertEqual(
                [r["id"] for r in STORE.list_open(ledger, surface="tooling")],
                ["#001"],
            )
            self.assertEqual(
                [r["id"] for r in STORE.list_open(ledger, surface="tooling", dimension="design")],
                ["#001"],
            )
            self.assertEqual(
                STORE.list_open(ledger, surface="tooling", dimension="naming"),
                [],
            )

    def test_status_argument_selects_other_dispositions(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            ledger = self._write_ledger(d)
            self.assertEqual(
                [r["id"] for r in STORE.list_open(ledger, status="declined")],
                ["#005"],
            )


class MigrateStoreTest(unittest.TestCase):
    def test_migration_preserves_row_count_and_produces_smaller_current_view(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            source = Path(d) / "docs" / "health" / "dispositions.md"
            source.parent.mkdir(parents=True)
            source.write_text(
                "# Health Finding Dispositions\n\n"
                "| ID | Surface | Dimension | Object | Finding | Disposition | Date | Evidence / note |\n"
                "|----|---------|-----------|--------|---------|-------------|------|------------------|\n"
                "| #595 | tooling | quality | record-plugin-dispositions"
                " | Schema count mismatch | accepted | 2026-06-12 | queued |\n"
                "| #596 | tooling | quality | record-plugin-dispositions"
                " | Schema count mismatch | fixed | 2026-06-13 | abc1234 closes row 1 |\n",
                encoding="utf-8",
            )
            history_root = Path(d) / "docs" / "health" / "dispositions-history"

            report = MIGRATE.migrate_store(source, history_root)

            self.assertEqual(report["source_rows"], 2)
            self.assertEqual(report["written_rows"], 2)
            self.assertEqual(report["current_rows"], 1)


class HealthFacadeExportTests(unittest.TestCase):
    def test_store_facade_keeps_public_helpers(self) -> None:
        self.assertTrue(hasattr(STORE, "append_event"))
        self.assertTrue(hasattr(STORE, "materialize_current_events"))
        self.assertTrue(hasattr(STORE, "match_against_ledger"))


if __name__ == "__main__":
    unittest.main()
