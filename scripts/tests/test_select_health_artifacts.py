"""Regression tests for deterministic docs/health artifact selection."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SELECTOR = REPO_ROOT / "scripts" / "select_health_artifacts.py"
HEALTH_SKILLS = [
    ".claude/skills/report-plugin-health/SKILL.md",
    ".claude/skills/plan-plugin-findings/SKILL.md",
    ".claude/skills/record-plugin-dispositions/SKILL.md",
]


class SelectHealthArtifactsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.health_dir = Path(self.temp_dir.name)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def create_artifact(self, name: str, mtime: int | None = None) -> Path:
        path = self.health_dir / name
        path.write_text(f"# {name}\n", encoding="utf-8")
        if mtime is not None:
            os.utime(path, (mtime, mtime))
        return path

    def select(
        self,
        *,
        kind: str,
        surface: str,
        limit: int = 1,
        offset: int = 0,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(SELECTOR),
                "--directory",
                str(self.health_dir),
                "--kind",
                kind,
                "--surface",
                surface,
                "--limit",
                str(limit),
                "--offset",
                str(offset),
            ],
            check=False,
            capture_output=True,
            text=True,
        )

    def test_selects_latest_artifact_independently_per_surface(self) -> None:
        plugin = self.create_artifact("2026-06-05-plugin-health.md")
        tooling = self.create_artifact("2026-06-07-tooling-health.md")
        self.create_artifact("2026-06-06-tooling-health.md")

        plugin_result = self.select(kind="health", surface="plugin")
        tooling_result = self.select(kind="health", surface="tooling")

        self.assertEqual(0, plugin_result.returncode, plugin_result.stderr)
        self.assertEqual([str(plugin)], plugin_result.stdout.splitlines())
        self.assertEqual(0, tooling_result.returncode, tooling_result.stderr)
        self.assertEqual([str(tooling)], tooling_result.stdout.splitlines())

    def test_filename_date_wins_over_filesystem_modification_time(self) -> None:
        older = self.create_artifact(
            "2026-06-06-tooling-health.md",
            mtime=2_000_000_000,
        )
        newer = self.create_artifact(
            "2026-06-07-tooling-health.md",
            mtime=1_000_000_000,
        )

        result = self.select(kind="health", surface="tooling")

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertNotEqual(str(older), result.stdout.strip())
        self.assertEqual(str(newer), result.stdout.strip())

    def test_offset_selects_previous_same_surface_artifact(self) -> None:
        previous = self.create_artifact("2026-06-06-tooling-findings.md")
        self.create_artifact("2026-06-07-tooling-findings.md")
        self.create_artifact("2026-06-08-plugin-findings.md")

        result = self.select(
            kind="findings",
            surface="tooling",
            offset=1,
        )

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(str(previous), result.stdout.strip())

    def test_excludes_legacy_both_and_unrelated_markdown_files(self) -> None:
        plugin = self.create_artifact("2026-06-05-plugin-health.md")
        self.create_artifact("2026-06-08-both-health.md")
        self.create_artifact("2026-06-09-audit-friction-analysis.md")
        self.create_artifact("not-a-date-plugin-health.md")

        result = self.select(kind="health", surface="plugin", limit=5)

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual([str(plugin)], result.stdout.splitlines())

    def test_missing_surface_returns_success_without_output(self) -> None:
        self.create_artifact("2026-06-07-tooling-health.md")

        result = self.select(kind="health", surface="plugin")

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual("", result.stdout)

    def test_archived_subdirectory_files_are_not_returned(self) -> None:
        """Files under an archived/ subdirectory must not appear in results.

        select_artifacts uses directory.iterdir() (non-recursive).  This test
        locks that contract so a future change to rglob cannot silently
        re-include archived findings.
        """
        self.create_artifact("2026-06-05-plugin-health.md")
        archived_dir = self.health_dir / "archived"
        archived_dir.mkdir()
        (archived_dir / "2026-06-09-plugin-health.md").write_text(
            "# archived\n", encoding="utf-8"
        )

        result = self.select(kind="health", surface="plugin", limit=5)

        returned_paths = result.stdout.splitlines()
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertFalse(
            any("archived" in p for p in returned_paths),
            f"archived/ file leaked into results: {returned_paths}",
        )
        self.assertEqual(1, len(returned_paths), returned_paths)


class HealthArtifactSelectionContractTest(unittest.TestCase):
    def read(self, path: str) -> str:
        return (REPO_ROOT / path).read_text(encoding="utf-8")

    def test_active_health_consumers_use_selector_without_mtime_globs(self) -> None:
        for path in HEALTH_SKILLS:
            with self.subTest(path=path):
                text = self.read(path)
                self.assertIn("scripts/select_health_artifacts.py", text)
                self.assertNotRegex(text, r"ls -t [^\n]*docs/health")

    def test_report_uses_previous_same_surface_findings_for_recurrence(self) -> None:
        report = self.read(".claude/skills/report-plugin-health/SKILL.md")

        self.assertIn("--kind findings", report)
        self.assertIn("--offset 1", report)

    def test_report_documents_friction_specific_recurrence_path(self) -> None:
        report = self.read(".claude/skills/report-plugin-health/SKILL.md")

        self.assertIn("--kind friction-findings", report)
        self.assertIn("path ends in `-friction-findings.md`", report)

    def test_report_input_gates_documents_family_specific_recurrence(self) -> None:
        gates = self.read(".claude/knowledge/report-input-gates.md")

        self.assertIn("--kind friction-findings", gates)
        self.assertIn("--kind findings", gates)
        self.assertIn("path ends in `-friction-findings.md`", gates)
        self.assertIn("current artifact family", gates)
        self.assertIn("stays within family", gates)

    def test_multi_surface_consumers_select_plugin_and_tooling_explicitly(self) -> None:
        for path in [
            ".claude/skills/report-plugin-health/SKILL.md",
            ".claude/skills/plan-plugin-findings/SKILL.md",
        ]:
            with self.subTest(path=path):
                text = self.read(path)
                self.assertIn("--surface plugin", text)
                self.assertIn("--surface tooling", text)

    def test_architectural_synthesis_is_retired_from_active_health_flow(self) -> None:
        active_path = (
            REPO_ROOT
            / ".claude"
            / "skills"
            / "analyze-architectural-design"
            / "SKILL.md"
        )
        archived_path = (
            REPO_ROOT
            / ".claude"
            / "skills"
            / "archived"
            / "analyze-architectural-design"
            / "SKILL.md"
        )
        report = self.read(".claude/skills/report-plugin-health/SKILL.md")

        self.assertFalse(active_path.exists())
        self.assertTrue(archived_path.is_file())
        self.assertNotIn(
            "next: [analyze-architectural-design, record-plugin-dispositions]",
            report,
        )


if __name__ == "__main__":
    unittest.main()
