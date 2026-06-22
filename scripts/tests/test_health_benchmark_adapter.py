"""Regression tests for the self-healing benchmark evidence adapter.

Guards the extraction contract of ``scripts/health_benchmark_adapter.py``:
the canonical ``<!-- benchmark-metrics -->`` block is the only source of metric
counts, a missing block or missing field becomes the literal ``not available``,
and the adapter never infers a denominator from the human-facing prose summary.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURES = REPO_ROOT / "scripts" / "tests" / "fixtures" / "benchmark"

sys.path.insert(0, str(REPO_ROOT / "scripts"))
import health_benchmark_adapter as adapter  # noqa: E402


class ParseDossierTest(unittest.TestCase):
    def test_full_metrics_block_parses_all_fields(self) -> None:
        record = adapter.parse_dossier(FIXTURES / "2099-01-01-plugin-full-metrics.md")

        self.assertTrue(record["metrics_block_present"])
        self.assertEqual("plugin", record["surface"])
        self.assertEqual(["quality"], record["dimensions"])
        self.assertEqual(45, record["raw_count"])
        self.assertEqual(24, record["verified_count"])
        self.assertEqual(20, record["dropped_unverified_count"])
        self.assertEqual(1, record["stale_dropped_count"])
        self.assertEqual(0, record["suppressed_count"])
        self.assertEqual(0, record["failed_lens_count"])
        self.assertEqual(24, record["new_count"])
        self.assertEqual(0, record["recurring_count"])

    def test_partial_block_uses_not_available_for_missing_and_literal_fields(self) -> None:
        record = adapter.parse_dossier(
            FIXTURES / "2099-01-02-tooling-partial-metrics.md"
        )

        self.assertTrue(record["metrics_block_present"])
        self.assertEqual("tooling", record["surface"])
        self.assertEqual(["quality", "naming"], record["dimensions"])
        # raw_count is the literal "not available" and the omitted suppressed_count
        # falls back to the same sentinel — never inferred from other fields.
        self.assertEqual(adapter.NOT_AVAILABLE, record["raw_count"])
        self.assertEqual(adapter.NOT_AVAILABLE, record["suppressed_count"])
        self.assertEqual(11, record["verified_count"])
        self.assertEqual(25, record["dropped_unverified_count"])

    def test_no_metrics_block_marks_every_field_not_available(self) -> None:
        record = adapter.parse_dossier(FIXTURES / "2099-01-03-plugin-no-metrics.md")

        self.assertFalse(record["metrics_block_present"])
        for field in adapter.METRIC_FIELDS:
            self.assertEqual(
                adapter.NOT_AVAILABLE,
                record[field],
                f"{field} should be not available when no block is present",
            )


class CoerceCountTest(unittest.TestCase):
    def test_numeric_string_becomes_int(self) -> None:
        self.assertEqual(12, adapter._coerce_count("12"))

    def test_not_available_literal_is_preserved(self) -> None:
        self.assertEqual(adapter.NOT_AVAILABLE, adapter._coerce_count(" not available "))

    def test_non_numeric_never_infers_a_count(self) -> None:
        self.assertEqual(adapter.NOT_AVAILABLE, adapter._coerce_count("abc"))


class BuildReportSmokeTest(unittest.TestCase):
    """End-to-end guard that the adapter still runs clean against the live repo.

    This is the enforcement half of the documented benchmark-refresh procedure:
    if the adapter rots, this test fails before a manual scoring run trusts it.
    """

    def test_build_report_against_live_repo(self) -> None:
        report = adapter.build_report(REPO_ROOT, surface="both", limit=1)

        self.assertIn("procedure_integrity", report)
        self.assertEqual(
            {
                "evidence_gate_run",
                "jsonl_views_generated",
                "loop_state_closed",
                "jsonl_open_accepted_zero",
                "legacy_staleness_clean",
                "integrity_clean",
                "close_back_ids_present",
            },
            set(report["procedure_integrity"]),
        )
        self.assertIn("list_open_accepted_count", report)
        self.assertIn("close_back_event_count", report)
        self.assertTrue(report["dossiers"], "expected at least one live dossier")
        for record in report["dossiers"]:
            self.assertIn("jsonl_open_accepted_count", record)
            self.assertIn("loop_stage_completed", record)
            self.assertIn("next_command", record)


if __name__ == "__main__":
    unittest.main()
