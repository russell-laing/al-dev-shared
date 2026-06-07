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
            MODULE.Row(1, "same-object", "first issue", "accepted", "2026-06-07", ""),
            MODULE.Row(2, "same-object", "second issue", "accepted", "2026-06-07", ""),
            MODULE.Row(
                3,
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
            MODULE.Row(1, "same-object", "first issue", "accepted", "2026-06-07", ""),
            MODULE.Row(2, "same-object", "first issue", "fixed", "2026-06-07", ""),
        ]

        MODULE.resolve_closures(rows)

        self.assertEqual(2, rows[0].closed_by)


if __name__ == "__main__":
    unittest.main()
