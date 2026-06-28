"""Regression tests for the packaged health script surface."""

from __future__ import annotations

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


class HealthPackageBootstrapTest(unittest.TestCase):
    def test_health_package_exports_shared_modules(self) -> None:
        from scripts.al_dev_tools import health

        self.assertTrue(hasattr(health, "health_disposition_store"))
        self.assertTrue(hasattr(health, "check_ledger_staleness"))
        self.assertTrue(hasattr(health, "health_benchmark_adapter"))
        self.assertTrue(hasattr(health, "select_health_artifacts"))

    def test_new_health_submodules_import(self) -> None:
        from scripts.al_dev_tools.health import (
            disposition_events,
            disposition_matching,
            disposition_models,
            disposition_views,
            ledger_cli,
            ledger_models,
            ledger_queries,
        )

        self.assertTrue(hasattr(disposition_models, "normalize_finding"))
        self.assertTrue(hasattr(disposition_events, "append_event"))
        self.assertTrue(hasattr(disposition_views, "render_open_view"))
        self.assertTrue(hasattr(disposition_matching, "match_against_ledger"))
        self.assertTrue(hasattr(ledger_models, "Row"))
        self.assertTrue(hasattr(ledger_queries, "commits_since"))
        self.assertTrue(hasattr(ledger_cli, "main"))

    def test_target_tests_no_longer_bootstrap_modules_by_path(self) -> None:
        for rel_path in (
            "scripts/tests/test_health_disposition_store.py",
            "scripts/tests/test_check_ledger_staleness.py",
            "scripts/tests/test_health_benchmark_adapter.py",
        ):
            text = (REPO_ROOT / rel_path).read_text(encoding="utf-8")
            self.assertNotIn("spec_from_file_location", text, rel_path)
            self.assertNotIn("sys.path.insert", text, rel_path)

    def test_cli_wrappers_stay_thin(self) -> None:
        for rel_path in (
            "scripts/health_disposition_store.py",
            "scripts/check_ledger_staleness.py",
            "scripts/health_benchmark_adapter.py",
            "scripts/select_health_artifacts.py",
        ):
            text = (REPO_ROOT / rel_path).read_text(encoding="utf-8")
            self.assertNotIn("importlib.util", text, rel_path)
            self.assertNotIn("sys.path.insert", text, rel_path)


if __name__ == "__main__":
    unittest.main()
