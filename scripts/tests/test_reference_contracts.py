from __future__ import annotations

import unittest

from scripts.al_dev_tools.reference_contracts import (
    allowed_template_patterns,
    canonical_artifact_patterns,
    canonical_script_entrypoints,
    generated_output_surfaces,
    legacy_reference_aliases,
    runtime_artifact_pattern_groups,
)
from scripts.al_dev_tools.shared_surface_names import runtime_artifact_patterns


class ReferenceContractsTest(unittest.TestCase):
    def test_canonical_artifact_patterns_cover_active_runtime_surface(self) -> None:
        grouped = runtime_artifact_patterns()
        expected = {
            f"{skill}.{artifact}": pattern
            for skill, artifacts in grouped.items()
            for artifact, pattern in artifacts.items()
        }
        flattened = canonical_artifact_patterns()
        self.assertEqual(flattened, expected)
        self.assertEqual(flattened["ticket.context"], "*-ticket-ticket-context.md")
        self.assertEqual(flattened["plan.solution_plan"], "*-plan-solution-plan.md")
        self.assertEqual(
            flattened["review-develop.code_review"],
            "*-develop-code-review.md",
        )
        self.assertEqual(flattened["lint.report"], "*-lint-lint-report.md")

    def test_runtime_artifact_patterns_adapter_reuses_grouped_registry(self) -> None:
        self.assertEqual(runtime_artifact_patterns(), runtime_artifact_pattern_groups())
        self.assertEqual(
            runtime_artifact_patterns()["develop-orchestrate"]["phase4_handoff"],
            "*-develop-phase4-handoff.md",
        )

    def test_script_entrypoints_use_runnable_forms(self) -> None:
        entrypoints = canonical_script_entrypoints()
        self.assertEqual(
            entrypoints["generate_agent_projections"],
            "python3 scripts/generate_agent_projections.py",
        )
        self.assertEqual(
            entrypoints["generate_maintainer_guide"],
            "python3 scripts/generate_maintainer_guide.py",
        )
        self.assertEqual(
            entrypoints["derive_agent_callers"],
            "python3 scripts/derive_agent_callers.py",
        )
        self.assertEqual(
            entrypoints["select_health_artifacts"],
            "python3 scripts/select_health_artifacts.py",
        )

    def test_generated_output_surfaces_include_maintainer_guide_targets(self) -> None:
        outputs = generated_output_surfaces()
        self.assertEqual(
            outputs["maintainer_guide"],
            (
                "docs/maintainer_tooling.md",
                "docs/maintainer_tooling/",
                "docs/maintainer_tooling/*.md",
            ),
        )

    def test_allowed_template_patterns_classify_dated_health_templates(self) -> None:
        templates = allowed_template_patterns()
        self.assertIn("docs/health/YYYY-MM-DD-<surface>-findings.md", templates)
        self.assertIn("docs/health/YYYY-MM-DD-<surface>-health.md", templates)

    def test_legacy_aliases_are_explicitly_classified(self) -> None:
        aliases = legacy_reference_aliases()
        self.assertEqual(
            aliases["legacy_script.generate_maintainer_guide"],
            ("generate-maintainer-guide.py",),
        )
        self.assertEqual(
            aliases["legacy_artifact.solution_plan"],
            (".dev/02-solution-plan.md",),
        )
        self.assertIn(
            ".dev/*-al-dev-plan-solution-plan.md",
            aliases["legacy_artifact.prefixed_plan"],
        )


if __name__ == "__main__":
    unittest.main()
