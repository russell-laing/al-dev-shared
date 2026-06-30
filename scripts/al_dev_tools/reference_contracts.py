"""Canonical reference contracts for shared runtime and maintainer surfaces."""

from __future__ import annotations

_CANONICAL_ARTIFACT_PATTERNS: dict[str, str] = {
    "commit_analysis": "*-commit-analysis.md",
    "plan_solution_plan": "*-plan-solution-plan.md",
    "develop_code_review": "*-develop-code-review.md",
    "ticket_context": "*-ticket-ticket-context.md",
    "ticket_reply": "*-ticket-reply.md",
    "lint_report": "*-lint-lint-report.md",
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
}

_CANONICAL_SCRIPT_ENTRYPOINTS: dict[str, str] = {
    "generate_agent_projections": "python3 scripts/generate_agent_projections.py",
    "generate_maintainer_guide": "python3 scripts/generate_maintainer_guide.py",
    "derive_agent_callers": "python3 scripts/derive_agent_callers.py",
    "select_health_artifacts": "python3 scripts/select_health_artifacts.py",
}

_GENERATED_OUTPUT_SURFACES: dict[str, tuple[str, ...]] = {
    "maintainer_tooling": (
        "docs/maintainer_tooling.md",
        "docs/maintainer_tooling/",
    ),
}

_ALLOWED_TEMPLATE_PATTERNS: tuple[str, ...] = (
    "docs/health/YYYY-MM-DD-<surface>-findings.md",
    "docs/health/YYYY-MM-DD-<surface>-friction-findings.md",
)

_LEGACY_REFERENCE_ALIASES: dict[str, tuple[str, ...]] = {
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
}


def canonical_artifact_patterns() -> dict[str, str]:
    """Return the canonical glob patterns for live runtime artifact families."""

    return dict(_CANONICAL_ARTIFACT_PATTERNS)


def canonical_script_entrypoints() -> dict[str, str]:
    """Return the runnable maintainer entrypoints in their canonical form."""

    return dict(_CANONICAL_SCRIPT_ENTRYPOINTS)


def generated_output_surfaces() -> dict[str, tuple[str, ...]]:
    """Return the canonical generated-output surfaces keyed by semantic family."""

    return {key: tuple(values) for key, values in _GENERATED_OUTPUT_SURFACES.items()}


def allowed_template_patterns() -> tuple[str, ...]:
    """Return template/example patterns that are intentionally not live refs."""

    return tuple(_ALLOWED_TEMPLATE_PATTERNS)


def legacy_reference_aliases() -> dict[str, tuple[str, ...]]:
    """Return deprecated reference spellings grouped by alias family."""

    return {key: tuple(values) for key, values in _LEGACY_REFERENCE_ALIASES.items()}
