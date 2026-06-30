"""Unit tests for the canonical reference-contract registry."""

from __future__ import annotations

import sys
from pathlib import Path
import unittest

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.al_dev_tools.reference_contracts import (  # noqa: E402
    allowed_template_patterns,
    canonical_artifact_patterns,
    canonical_script_entrypoints,
    generated_output_surfaces,
    legacy_reference_aliases,
)
from scripts.al_dev_tools.shared_surface_names import (  # noqa: E402
    runtime_artifact_patterns,
)


class ReferenceContractsTests(unittest.TestCase):
    def test_canonical_artifact_patterns_cover_active_runtime_families(self) -> None:
        self.assertEqual(
            canonical_artifact_patterns(),
            {
                "plan_solution_plan": "*-plan-solution-plan.md",
                "develop_code_review": "*-develop-code-review.md",
                "ticket_context": "*-ticket-ticket-context.md",
                "ticket_reply": "*-ticket-reply.md",
                "lint_report": "*-lint-lint-report.md",
                "commit_analysis": "*-commit-analysis.md",
                "develop_progress": "*-develop-progress.md",
                "develop_checklist": "*-develop-checklist.md",
                "develop_scope": "*-develop-scope.md",
                "develop_phase4_handoff": "*-develop-phase4-handoff.md",
                "developer_tdd_test_plan": "*-test-test-plan.md",
                "developer_tdd_log": "*-developer-tdd-log.md",
                "interview_notes": "*-interview-notes.md",
                "interview_requirements": "*-interview-requirements.md",
                "explore_findings": "*-explore-findings.md",
                "investigate_findings": "*-investigate-findings.md",
                "plan_debate_summary": "*-plan-debate-summary.md",
                "review_preflight": "*-plugin-review-preflight.md",
                "perf_analysis": "*-perf-perf-analysis.md",
                "release_notes": "*-plugin-release-notes.md",
                "handoff_prompt": "*-handoff-handoff-prompt.md",
            },
        )

    def test_shared_surface_runtime_patterns_adapt_from_canonical_registry(self) -> None:
        patterns = runtime_artifact_patterns()
        self.assertEqual(patterns["plan"]["solution_plan"], "*-plan-solution-plan.md")
        self.assertEqual(patterns["review-develop"]["code_review"], "*-develop-code-review.md")
        self.assertEqual(patterns["ticket"]["context"], "*-ticket-ticket-context.md")
        self.assertEqual(patterns["lint"]["report"], "*-lint-lint-report.md")

    def test_canonical_script_entrypoints_use_runnable_forms(self) -> None:
        self.assertEqual(
            canonical_script_entrypoints(),
            {
                "generate_agent_projections": "python3 scripts/generate_agent_projections.py",
                "generate_maintainer_guide": "python3 scripts/generate_maintainer_guide.py",
                "derive_agent_callers": "python3 scripts/derive_agent_callers.py",
                "select_health_artifacts": "python3 scripts/select_health_artifacts.py",
            },
        )

    def test_generated_output_surfaces_include_summary_and_stage_pages(self) -> None:
        self.assertEqual(
            generated_output_surfaces(),
            {
                "maintainer_tooling": (
                    "docs/maintainer_tooling.md",
                    "docs/maintainer_tooling/",
                ),
            },
        )

    def test_allowed_template_patterns_cover_health_findings_family(self) -> None:
        self.assertEqual(
            allowed_template_patterns(),
            (
                "docs/health/YYYY-MM-DD-<surface>-findings.md",
                "docs/health/YYYY-MM-DD-<surface>-friction-findings.md",
            ),
        )

    def test_legacy_reference_aliases_are_explicitly_classified(self) -> None:
        self.assertEqual(
            legacy_reference_aliases(),
            {
                "hyphenated_script_entrypoints": (
                    "python3 scripts/generate-agent-projections.py",
                    "python3 scripts/generate-maintainer-guide.py",
                    "python3 scripts/derive-agent-callers.py",
                    "python3 scripts/select-health-artifacts.py",
                ),
                "hyphenated_generated_outputs": (
                    "docs/maintainer-tooling.md",
                    "docs/maintainer-tooling/",
                ),
            },
        )


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
