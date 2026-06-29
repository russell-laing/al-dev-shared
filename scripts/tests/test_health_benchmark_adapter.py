"""Regression tests for the self-healing benchmark evidence adapter.

Guards the extraction contract of ``scripts/health_benchmark_adapter.py``:
the canonical ``<!-- benchmark-metrics -->`` block is the only source of metric
counts, a missing block or missing field becomes the literal ``not available``,
and the adapter never infers a denominator from the human-facing prose summary.
"""

from __future__ import annotations

import unittest
from pathlib import Path

from scripts.al_dev_tools.health import health_benchmark_adapter as adapter

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURES = REPO_ROOT / "scripts" / "tests" / "fixtures" / "benchmark"


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


class TokenUsageParserTest(unittest.TestCase):
    def test_token_usage_block_parses_coverage_without_claiming_counts(self) -> None:
        record = adapter.parse_dossier(FIXTURES / "2099-01-04-plugin-token-usage.md")

        self.assertTrue(record["token_usage_block_present"])
        self.assertFalse(record["token_data_available"])
        self.assertEqual(adapter.NOT_AVAILABLE, record["prompt_tokens"])
        self.assertEqual(adapter.NOT_AVAILABLE, record["completion_tokens"])
        self.assertEqual(adapter.NOT_AVAILABLE, record["context_compaction_events"])


class ProcedureLogParserTest(unittest.TestCase):
    def test_expected_phases_parse_for_implement_skill(self) -> None:
        phases = adapter.parse_expected_phases(
            """\
# Expected Health Phases

## implement-plugin-health

| Phase | Required proof |
| --- | --- |
| 0 | plan_located |
| 1 | tasks_executing |
| 2 | per_task_verified |
| 3 | ledger_closed |
| 4 | artifacts_finalized |
| 5 | loop_closed |
"""
        )

        self.assertEqual(
            ["0", "1", "2", "3", "4", "5"],
            phases["implement-plugin-health"],
        )

    def test_procedure_log_reports_missing_phase(self) -> None:
        expected = {"implement-plugin-health": ["0", "1", "2", "3"]}
        records = adapter.parse_procedure_log(
            FIXTURES / "implement-plugin-health-procedure-log.jsonl"
        )
        summary = adapter.summarize_procedure_log(records, expected)

        self.assertFalse(summary["implement-plugin-health"]["complete"])
        self.assertEqual(["3"], summary["implement-plugin-health"]["missing_phases"])


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
        self.assertIn("self_healing_signals", report)
        self.assertIn("dossiers", report)
        self.assertIsInstance(report["dossiers"], list)
        for record in report["dossiers"]:
            self.assertIn("jsonl_open_accepted_count", record)
            self.assertIn("loop_stage_completed", record)
            self.assertIn("next_command", record)


class FalsePositiveClassParserTest(unittest.TestCase):
    def test_false_positive_classes_parse_status_rows(self) -> None:
        rows = adapter.parse_false_positive_classes(
            FIXTURES / "false-positive-classes.md"
        )

        self.assertEqual(
            [
                {
                    "id": "friction-surface-mismatch",
                    "description": "Friction-ingest findings mapped to structurally different target files",
                    "first_seen": "2026-06-18",
                    "last_seen": "2026-06-18",
                    "status": "Candidate",
                },
                {
                    "id": "subjective-clarity-name-fit",
                    "description": "Clarity and name-fit lens findings with no objective criterion",
                    "first_seen": "2026-06-19",
                    "last_seen": "2026-06-19",
                    "status": "Monitor",
                },
                {
                    "id": "stale-generated-path",
                    "description": "Findings against generated projection artifacts instead of canonical source",
                    "first_seen": "2026-06-28",
                    "last_seen": "2026-06-29",
                    "status": "Suppress",
                },
            ],
            rows,
        )

    def test_build_report_includes_false_positive_summary(self) -> None:
        report = adapter.build_report(REPO_ROOT, surface="both", limit=1)

        self.assertIn("false_positive_classes", report)
        self.assertIn("false_positive_status_counts", report)
        self.assertIsInstance(report["false_positive_classes"], list)
        self.assertIn("Candidate", report["false_positive_status_counts"])


class SelfHealingSignalTest(unittest.TestCase):
    def test_cascade_prevention_rate_uses_available_counts_only(self) -> None:
        records = [
            {"raw_count": 10, "dropped_unverified_count": 4},
            {"raw_count": adapter.NOT_AVAILABLE, "dropped_unverified_count": 2},
        ]
        signals = adapter.compute_self_healing_signals([], records)

        self.assertEqual(0.4, signals["cascade_prevention_rate"])
        self.assertEqual(10, signals["cascade_prevention_denominator"])

    def test_disposition_event_counts_capture_close_back_rows(self) -> None:
        events = [
            {"event_id": "disp_20990101_000001", "disposition": "declined"},
            {"event_id": "disp_20990101_000002", "disposition": "fixed"},
            {
                "event_id": "disp_20990101_000003",
                "disposition": "fixed",
                "closes_event_ids": ["disp_20990101_000002"],
            },
        ]
        signals = adapter.compute_self_healing_signals(events, [])

        self.assertEqual(
            {"declined": 1, "fixed": 2},
            signals["disposition_event_counts"],
        )
        self.assertEqual(1, signals["close_back_event_count"])


if __name__ == "__main__":
    unittest.main()
