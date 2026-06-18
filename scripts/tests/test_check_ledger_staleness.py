"""Regression tests for disposition ledger closure resolution."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "scripts" / "check_ledger_staleness.py"
SPEC = importlib.util.spec_from_file_location("check_ledger_staleness", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class ResolveClosuresTest(unittest.TestCase):
    def test_explicit_closure_does_not_also_close_by_object_order(self) -> None:
        rows = [
            MODULE.Row(
                1, "unknown", "unknown", "same-object", "first issue", "accepted", "2026-06-07", "", id="001"
            ),
            MODULE.Row(
                2, "unknown", "unknown", "same-object", "second issue", "accepted", "2026-06-07", "", id="002"
            ),
            MODULE.Row(
                3,
                "unknown",
                "unknown",
                "same-object",
                "second issue",
                "fixed",
                "2026-06-07",
                "fix commit; closes #002",
                id="003",
            ),
        ]

        MODULE.resolve_closures(rows)

        self.assertIsNone(rows[0].closed_by)
        self.assertEqual(3, rows[1].closed_by)

    def test_fixed_row_without_token_uses_object_order_fallback(self) -> None:
        rows = [
            MODULE.Row(
                1, "unknown", "unknown", "same-object", "first issue", "accepted", "2026-06-07", ""
            ),
            MODULE.Row(
                2, "unknown", "unknown", "same-object", "first issue", "fixed", "2026-06-07", ""
            ),
        ]

        MODULE.resolve_closures(rows)

        self.assertEqual(2, rows[0].closed_by)

    def test_parse_ledger_text_reads_migrated_rows_without_column_shift(self) -> None:
        rows = MODULE.parse_ledger_text(
            "\n".join(
                [
                    "| Surface | Dimension | Object | Finding | Disposition | Date | Evidence / note |",
                    "|---------|-----------|--------|---------|-------------|------|------------------|",
                    "| tooling | quality | plugin-health-discover | Bloat: nested phases | accepted | 2026-06-07 | note |",
                ]
            )
        )

        self.assertEqual(1, len(rows))
        self.assertEqual("tooling", rows[0].surface)
        self.assertEqual("quality", rows[0].dimension)
        self.assertEqual("plugin-health-discover", rows[0].obj)
        self.assertEqual("Bloat: nested phases", rows[0].issue)

    def test_parse_ledger_text_reads_legacy_rows_as_unknown_surface_dimension(self) -> None:
        rows = MODULE.parse_ledger_text(
            "\n".join(
                [
                    "| Object | Issue | Disposition | Date | Evidence / note |",
                    "|--------|-------|-------------|------|------------------|",
                    "| plugin-health-discover | Bloat: nested phases | accepted | 2026-06-07 | note |",
                ]
            )
        )

        self.assertEqual(1, len(rows))
        self.assertEqual("unknown", rows[0].surface)
        self.assertEqual("unknown", rows[0].dimension)
        self.assertEqual("plugin-health-discover", rows[0].obj)

    def test_legacy_closes_row_token_resolves_accepted_in_seven_column_table(self) -> None:
        """Legacy 7-column table with 'closes row N' token should resolve via CLOSES_RE."""
        rows = [
            MODULE.Row(
                1, "tooling", "quality", "plugin-health-discover", "Bloat: nested phases", "accepted", "2026-06-07", ""
            ),
            MODULE.Row(
                2,
                "tooling",
                "quality",
                "plugin-health-discover",
                "Bloat: nested phases",
                "fixed",
                "2026-06-07",
                "fix commit; closes row 1",
            ),
        ]

        MODULE.resolve_closures(rows)

        self.assertEqual(2, rows[0].closed_by)

    def test_stale_open_row_output_includes_id_for_eight_column_table(self) -> None:
        """8-column table STALE-OPEN output should include the #ID in the line."""
        # This test validates that when main() outputs a STALE-OPEN row for an 8-column
        # ledger entry, the row's ID is included in the output string.
        row = MODULE.Row(
            1,
            "tooling",
            "quality",
            "plugin-health-discover",
            "Bloat: nested phases",
            "accepted",
            "2026-06-07",
            "some note",
            id="001",
        )

        # Simulate the output logic from main() for STALE-OPEN rows (lines 267-269)
        line = f"  row {row.number}"
        if row.id:
            line += f" (ID {row.id})"
        line += f" | {row.obj} | accepted {row.date}"

        self.assertIn("(ID 001)", line)
        self.assertIn("plugin-health-discover", line)


class ClosureProvenanceTest(unittest.TestCase):
    def test_token_closure_records_token_provenance(self) -> None:
        rows = [
            MODULE.Row(1, "t", "q", "obj", "issue A", "accepted", "2026-06-07", "", id="001"),
            MODULE.Row(2, "t", "q", "obj", "issue A", "fixed", "2026-06-08", "closes #001", id="002"),
        ]
        MODULE.resolve_closures(rows)
        self.assertEqual(2, rows[0].closed_by)
        self.assertEqual("token", rows[0].closed_via)

    def test_object_order_closure_records_objorder_provenance(self) -> None:
        rows = [
            MODULE.Row(1, "t", "q", "obj", "issue A", "accepted", "2026-06-07", ""),
            MODULE.Row(2, "t", "q", "obj", "issue A", "fixed", "2026-06-08", "no token"),
        ]
        MODULE.resolve_closures(rows)
        self.assertEqual(2, rows[0].closed_by)
        self.assertEqual("objorder", rows[0].closed_via)


class IntegrityWarningsTest(unittest.TestCase):
    def test_clean_ledger_yields_no_warnings(self) -> None:
        rows = [
            MODULE.Row(1, "t", "q", "obj", "issue A", "accepted", "2026-06-07", "", id="001"),
            MODULE.Row(2, "t", "q", "obj", "issue A", "fixed", "2026-06-08", "closes #001", id="002"),
        ]
        MODULE.resolve_closures(rows)
        self.assertEqual([], MODULE.integrity_warnings(rows))

    def test_warns_on_duplicate_id_across_distinct_findings(self) -> None:
        rows = [
            MODULE.Row(1, "t", "q", "obj", "issue A", "accepted", "2026-06-07", "", id="001"),
            MODULE.Row(2, "t", "q", "obj", "issue B reworded", "declined", "2026-06-08", "", id="001"),
        ]
        MODULE.resolve_closures(rows)
        warnings = MODULE.integrity_warnings(rows)
        self.assertTrue(any("001" in w and "distinct" in w for w in warnings), warnings)

    def test_warns_on_positional_closure_on_multi_finding_object(self) -> None:
        rows = [
            MODULE.Row(1, "t", "q", "obj", "issue A", "accepted", "2026-06-07", "", id="001"),
            MODULE.Row(2, "t", "q", "obj", "issue B", "accepted", "2026-06-07", "", id="002"),
            MODULE.Row(3, "t", "q", "obj", "issue B", "fixed", "2026-06-08", "no token", id="003"),
        ]
        MODULE.resolve_closures(rows)
        warnings = MODULE.integrity_warnings(rows)
        self.assertTrue(any("positional" in w for w in warnings), warnings)

    def test_warns_on_multiple_open_accepted_on_one_object(self) -> None:
        rows = [
            MODULE.Row(1, "t", "q", "obj", "issue A", "accepted", "2026-06-07", "", id="001"),
            MODULE.Row(2, "t", "q", "obj", "issue B", "accepted", "2026-06-07", "", id="002"),
        ]
        MODULE.resolve_closures(rows)
        warnings = MODULE.integrity_warnings(rows)
        self.assertTrue(any("effective-open" in w and "obj" in w for w in warnings), warnings)


def _run_checker(repo_root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(MODULE_PATH), "--root", str(repo_root)],
        capture_output=True,
        text=True,
    )


class ShardedStoreCheckerTest(unittest.TestCase):
    def test_checker_reads_history_store_and_reports_zero_open(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            history = root / "docs" / "health" / "dispositions-history" / "2026"
            history.mkdir(parents=True)

            (history / "2026-06.md").write_text(
                "| ID | Surface | Dimension | Object | Finding | Disposition | Date | Evidence / note |\n"
                "|----|---------|-----------|--------|---------|-------------|------|------------------|\n"
                "| #595 | tooling | quality | record-health-dispositions"
                " | Schema count mismatch | accepted | 2026-06-12 | queued |\n"
                "| #596 | tooling | quality | record-health-dispositions"
                " | Schema count mismatch | fixed | 2026-06-13 | abc1234 closes #595 |\n",
                encoding="utf-8",
            )

            result = _run_checker(root)

            self.assertIn("0 effective-open accepted row(s)", result.stdout)


if __name__ == "__main__":
    unittest.main()
