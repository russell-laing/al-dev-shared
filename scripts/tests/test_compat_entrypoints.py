"""Regression tests for compatibility wrappers."""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


class CompatEntrypointTest(unittest.TestCase):
    def _run_help(self, script_name: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, f"scripts/{script_name}", "--help"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_argparse_wrappers_support_direct_help(self) -> None:
        for script_name in (
            "assemble_health_findings.py",
            "health_benchmark_adapter.py",
            "health_disposition_store.py",
            "migrate_health_disposition_jsonl.py",
            "migrate_health_disposition_store.py",
            "select_health_artifacts.py",
            "split_multilens_findings.py",
            "validate_health_loop_state.py",
        ):
            result = self._run_help(script_name)
            self.assertEqual(result.returncode, 0, (script_name, result.stderr))
            self.assertIn("usage:", result.stdout.lower(), (script_name, result.stdout))

    def test_check_ledger_staleness_runs_as_direct_wrapper(self) -> None:
        result = subprocess.run(
            [sys.executable, "scripts/check_ledger_staleness.py"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("ledger-check:", result.stdout)


if __name__ == "__main__":
    unittest.main()
