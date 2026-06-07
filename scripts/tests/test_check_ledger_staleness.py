"""Regression tests for disposition ledger closure resolution."""

from __future__ import annotations

import importlib.util
import sys
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
                1, "unknown", "unknown", "same-object", "first issue", "accepted", "2026-06-07", ""
            ),
            MODULE.Row(
                2, "unknown", "unknown", "same-object", "second issue", "accepted", "2026-06-07", ""
            ),
            MODULE.Row(
                3,
                "unknown",
                "unknown",
                "same-object",
                "second issue",
                "fixed",
                "2026-06-07",
                "fix commit; closes row 2",
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


if __name__ == "__main__":
    unittest.main()
