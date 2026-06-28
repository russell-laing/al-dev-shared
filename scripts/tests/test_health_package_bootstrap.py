"""Regression tests for the packaged health script surface."""

from __future__ import annotations

import unittest
from importlib import import_module
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


class HealthPackageBootstrapTest(unittest.TestCase):
    def test_health_package_exports_shared_modules(self) -> None:
        from scripts.al_dev_tools import health

        for name in (
            "assemble_health_findings",
            "check_disposition_store_consistency",
            "check_ledger_staleness",
            "health_benchmark_adapter",
            "health_disposition_store",
            "migrate_health_disposition_jsonl",
            "migrate_health_disposition_store",
            "select_health_artifacts",
            "split_multilens_findings",
            "validate_health_loop_state",
        ):
            self.assertIsNotNone(import_module(f"scripts.al_dev_tools.health.{name}"))
            self.assertTrue(hasattr(health, name))

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
