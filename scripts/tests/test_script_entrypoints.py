"""Regression tests for direct file-path entrypoints."""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

from scripts._entrypoint_bootstrap import bootstrap_repo


REPO_ROOT = Path(__file__).resolve().parents[2]


class ScriptEntrypointTest(unittest.TestCase):
    def test_bootstrap_repo_returns_repo_root_and_is_idempotent(self) -> None:
        script_path = REPO_ROOT / "scripts" / "derive_agent_callers.py"
        first = bootstrap_repo(str(script_path))
        second = bootstrap_repo(str(script_path))
        self.assertEqual(first, REPO_ROOT)
        self.assertEqual(second, REPO_ROOT)
        self.assertEqual(sys.path.count(str(REPO_ROOT)), 1)

    def test_derive_agent_callers_runs_as_direct_script(self) -> None:
        result = subprocess.run(
            [sys.executable, "scripts/derive_agent_callers.py"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(result.stdout.startswith("{\n"), result.stdout)
        self.assertIn('"al-dev-interview"', result.stdout)

    def test_derive_skill_spawned_agents_runs_as_direct_script(self) -> None:
        result = subprocess.run(
            [sys.executable, "scripts/derive_skill_spawned_agents.py"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(result.stdout.startswith("{\n"), result.stdout)
        self.assertIn('"al-dev-shared:', result.stdout)


if __name__ == "__main__":
    unittest.main()
