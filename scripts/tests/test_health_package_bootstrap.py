"""Regression tests for the packaged health script surface."""

from __future__ import annotations

import json
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

    def test_codex_companion_manifest_exists(self) -> None:
        manifest = REPO_ROOT / "companions/codex/al-dev/.codex-plugin/plugin.json"
        self.assertTrue(manifest.is_file())
        data = json.loads(manifest.read_text(encoding="utf-8"))
        self.assertEqual(data["name"], "codex-al-dev")

    def test_in_scope_companion_readmes_exist(self) -> None:
        for relative in [
            "companions/README.md",
            "companions/codex/al-dev/README.md",
            "companions/claude/al-dev/README.md",
            "companions/copilot/al-dev/README.md",
        ]:
            self.assertTrue((REPO_ROOT / relative).is_file(), relative)

    def test_claude_and_copilot_companion_manifests_exist(self) -> None:
        pairs = [
            ("companions/claude/al-dev/.claude-plugin/plugin.json", "claude-al-dev"),
            ("companions/copilot/al-dev/.plugin/plugin.json", "copilot-al-dev"),
        ]
        for relative, expected_name in pairs:
            manifest = REPO_ROOT / relative
            self.assertTrue(manifest.is_file(), relative)
            data = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertEqual(data["name"], expected_name)


if __name__ == "__main__":
    unittest.main()
