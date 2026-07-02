"""Regression tests for the self-healing filter contract."""

from __future__ import annotations

import argparse
import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MIGRATION_SPEC = importlib.util.spec_from_file_location(
    "migrate_health_disposition_columns",
    REPO_ROOT / "scripts" / "migrate_health_disposition_columns.py",
)
assert MIGRATION_SPEC is not None and MIGRATION_SPEC.loader is not None
MIGRATION = importlib.util.module_from_spec(MIGRATION_SPEC)
sys.modules[MIGRATION_SPEC.name] = MIGRATION
MIGRATION_SPEC.loader.exec_module(MIGRATION)

SCRIPT = REPO_ROOT / "scripts" / "migrate_health_disposition_columns.py"


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
        maintainer = self.read("docs/maintainer_tooling.md")
        commands = self.read("docs/development_commands.md")
        self.assertIn("health-filter-contract.md", maintainer)
        self.assertIn("--resume` is audit-only", maintainer)
        self.assertIn("/audit-plugin-health --surface tooling --dimension quality", commands)
        self.assertIn("/audit-plugin-health --surface both --dimension naming", commands)

    def test_health_filter_contract_mentions_companion_surfaces(self) -> None:
        text = self.read(".claude/knowledge/health-filter-contract.md")
        for needle in [
            "companion-codex-al-dev",
            "companion-claude-al-dev",
            "companion-copilot-al-dev",
            "`companions` = all canonical companion package surfaces",
            "`both` = legacy alias for `plugin` + `tooling` only",
        ]:
            self.assertIn(needle, text)

    def test_legacy_surface_token_is_preserved_verbatim(self) -> None:
        # Guards the additive-not-destructive requirement: the legacy token must survive.
        text = self.read(".claude/knowledge/health-filter-contract.md")
        self.assertIn("`--surface plugin|tooling|both`", text)

    def test_docs_include_companion_surface_examples(self) -> None:
        commands = self.read("docs/development_commands.md")
        self.assertIn("/audit-plugin-health --surface companions --dimension all", commands)
        self.assertIn("/audit-plugin-health --surface companion-codex-al-dev --dimension quality", commands)
        # And the pre-existing legacy examples must remain (guards append-not-replace):
        self.assertIn("/audit-plugin-health --surface both --dimension naming", commands)
        self.assertIn("/audit-plugin-health --surface tooling --dimension quality", commands)


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

    def test_main_writes_outputs_via_atomic_helper(self) -> None:
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
            calls: list[Path] = []
            original = getattr(MIGRATION, "write_text_atomic", None)

            def fake_write_text_atomic(path: Path, text: str) -> None:
                calls.append(path)
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding="utf-8")

            MIGRATION.write_text_atomic = fake_write_text_atomic
            original_parse_args = MIGRATION.parse_args
            try:
                MIGRATION.parse_args = lambda: argparse.Namespace(
                    ledger=ledger,
                    write=output,
                    report=report,
                    inference_map=None,
                    stamp_ids=False,
                )
                result = MIGRATION.main()
            finally:
                MIGRATION.parse_args = original_parse_args
                if original is None:
                    delattr(MIGRATION, "write_text_atomic")
                else:
                    MIGRATION.write_text_atomic = original

            self.assertEqual(0, result)
            self.assertEqual([output, report], calls)


if __name__ == "__main__":
    unittest.main()
