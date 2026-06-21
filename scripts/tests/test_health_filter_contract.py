"""Regression tests for the self-healing filter contract."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MIGRATION_SPEC = importlib.util.spec_from_file_location(
    "migrate_health_dispositions",
    REPO_ROOT / "scripts" / "migrate_health_dispositions.py",
)
assert MIGRATION_SPEC is not None and MIGRATION_SPEC.loader is not None
MIGRATION = importlib.util.module_from_spec(MIGRATION_SPEC)
sys.modules[MIGRATION_SPEC.name] = MIGRATION
MIGRATION_SPEC.loader.exec_module(MIGRATION)

SCRIPT = REPO_ROOT / "scripts" / "migrate_health_dispositions.py"


class HealthFilterContractFileTest(unittest.TestCase):
    def read(self, relative_path: str) -> str:
        return (REPO_ROOT / relative_path).read_text(encoding="utf-8")

    def test_health_filter_contract_file_defines_required_sections(self) -> None:
        text = self.read(".claude/knowledge/health-filter-contract.md")
        for needle in [
            "# Health Filter Contract",
            "## Public Command Contract",
            "`--surface plugin|tooling|both`",
            "`--dimension design|quality|naming|all`",
            "## Legacy Compatibility",
            "## Resume Contract",
            "## Migration Provenance",
        ]:
            self.assertIn(needle, text)

    def test_health_skills_reference_contract_and_naming_dimension(self) -> None:
        expected_hint = "[--surface plugin|tooling|both] [--dimension design|quality|naming|all]"
        for path in [
            ".claude/skills/audit-plugin-health/SKILL.md",
            ".claude/skills/discover-plugin-health/SKILL.md",
            ".claude/skills/report-plugin-health/SKILL.md",
            ".claude/skills/record-plugin-dispositions/SKILL.md",
            ".claude/skills/plan-plugin-findings/SKILL.md",
        ]:
            with self.subTest(path=path):
                text = self.read(path)
                self.assertIn("health-filter-contract.md", text)
                self.assertIn("naming", text)
        self.assertIn(
            expected_hint + " [--resume]",
            self.read(".claude/skills/audit-plugin-health/SKILL.md"),
        )

    def test_plan_writes_health_filters_metadata_block(self) -> None:
        plan = self.read(".claude/skills/plan-plugin-findings/SKILL.md")
        self.assertIn("health_filters:", plan)
        self.assertIn("dimensions:", plan)
        self.assertIn("Apply filters in this order:", plan)

    def test_report_preserves_metadata_without_public_dimension_flag(self) -> None:
        report = self.read(".claude/skills/report-plugin-health/SKILL.md")
        self.assertIn('argument-hint: "[--findings <path>] [--surface plugin|tooling]"', report)
        self.assertIn("_Not requested in this run._", report)
        self.assertIn("dimensions:", report)
        self.assertNotIn("[--dimension", report)

    def test_docs_link_to_canonical_contract_and_resume_rule(self) -> None:
        maintainer = self.read("docs/maintainer-tooling.md")
        commands = self.read("docs/development-commands.md")
        self.assertIn("health-filter-contract.md", maintainer)
        self.assertIn("--resume` is audit-only", maintainer)
        self.assertIn("/audit-plugin-health --surface tooling --dimension quality", commands)
        self.assertIn("/audit-plugin-health --surface both --dimension naming", commands)


class HealthDispositionMigrationTest(unittest.TestCase):
    def test_migration_uses_exact_object_finding_date_key_and_preserves_order(self) -> None:
        legacy = "\n".join(
            [
                "| Object | Issue | Disposition | Date | Evidence / note |",
                "|--------|-------|-------------|------|------------------|",
                "| discover-plugin-health | Bloat: nested phases | accepted | 2026-06-05 | note |",
                "| discover-plugin-health | Clarity: missing else branch | declined | 2026-06-07 | note 2 |",
            ]
        )
        migrated, unresolved, rewrites = MIGRATION.migrate_ledger_text(
            legacy,
            override_index={
                (
                    MIGRATION.normalize_text("discover-plugin-health"),
                    MIGRATION.normalize_text("Bloat: nested phases"),
                    "2026-06-05",
                ): ("tooling", "quality"),
                (
                    MIGRATION.normalize_text("discover-plugin-health"),
                    MIGRATION.normalize_text("Clarity: missing else branch"),
                    "2026-06-07",
                ): ("tooling", "quality"),
            },
        )

        self.assertIn(
            "| Surface | Dimension | Object | Finding | Disposition | Date | Evidence / note |",
            migrated,
        )
        self.assertIn(
            "| tooling | quality | discover-plugin-health | Bloat: nested phases | accepted | 2026-06-05 | note |",
            migrated,
        )
        self.assertIn(
            "| tooling | quality | discover-plugin-health | Clarity: missing else branch | declined | 2026-06-07 | note 2 |",
            migrated,
        )
        self.assertEqual([], unresolved)
        self.assertEqual([], rewrites)

    def test_migration_falls_back_to_unknown_when_provenance_is_not_provable(self) -> None:
        legacy = "\n".join(
            [
                "| Object | Issue | Disposition | Date | Evidence / note |",
                "|--------|-------|-------------|------|------------------|",
                "| mystery-skill | Unmatched issue | accepted | 2026-06-07 | note |",
            ]
        )

        migrated, unresolved, rewrites = MIGRATION.migrate_ledger_text(legacy)

        self.assertIn(
            "| unknown | unknown | mystery-skill | Unmatched issue | accepted | 2026-06-07 | note |",
            migrated,
        )
        self.assertEqual(1, len(unresolved))
        self.assertEqual("mystery-skill", unresolved[0].object_name)
        self.assertEqual([], rewrites)

    def test_migration_can_infer_dimension_from_dossier_context(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            health_dir = Path(td)
            (health_dir / "2026-06-07-tooling-health.md").write_text(
                "\n".join(
                    [
                        "# Tooling Health — 2026-06-07",
                        "",
                        "## Quality findings",
                        "",
                        "- **discover-plugin-health** | High | Phase 1 has no else branch | Add explicit proceed branch.",
                    ]
                ),
                encoding="utf-8",
            )
            findings_index = MIGRATION.build_findings_index(health_dir)
            dossier_index = MIGRATION.build_dossier_index(health_dir)
            migrated, unresolved, rewrites = MIGRATION.migrate_ledger_text(
                "\n".join(
                    [
                        "| Object | Issue | Disposition | Date | Evidence / note |",
                        "|--------|-------|-------------|------|------------------|",
                        "| discover-plugin-health | Phase 1 has no else branch | accepted | 2026-06-07 | note |",
                    ]
                ),
                findings_index=findings_index,
                dossier_index=dossier_index,
            )

            self.assertIn(
                "| tooling | quality | discover-plugin-health | Phase 1 has no else branch | accepted | 2026-06-07 | note |",
                migrated,
            )
            self.assertEqual([], unresolved)
            self.assertEqual([], rewrites)

    def test_cli_write_emits_migration_audit_report(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            ledger = root / "dispositions.md"
            output = root / "dispositions-migrated.md"
            report = root / "dispositions-migration-audit.md"
            ledger.write_text(
                "\n".join(
                    [
                        "| Object | Issue | Disposition | Date | Evidence / note |",
                        "|--------|-------|-------------|------|------------------|",
                        "| mystery-skill | Unmatched issue | accepted | 2026-06-07 | note |",
                    ]
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--ledger",
                    str(ledger),
                    "--write",
                    str(output),
                    "--report",
                    str(report),
                ],
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(0, result.returncode, result.stderr)
            self.assertTrue(output.is_file())
            self.assertTrue(report.is_file())
            self.assertIn("Rows requiring manual provenance cleanup: 1", report.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
