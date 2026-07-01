"""Canonical reference spellings shared by validators, docs, and helpers."""

from __future__ import annotations

from typing import Dict, Tuple

_ARTIFACT_PATTERN_GROUPS: dict[str, dict[str, str]] = {
    "commit-execute": {
        "analysis": "*-commit-analysis.md",
    },
    "develop-orchestrate": {
        "progress": "*-develop-progress.md",
        "checklist": "*-develop-checklist.md",
        "scope": "*-develop-scope.md",
        "phase4_handoff": "*-develop-phase4-handoff.md",
    },
    "developer-tdd": {
        "test_plan": "*-test-test-plan.md",
        "log": "*-developer-tdd-log.md",
    },
    "ticket": {
        "context": "*-ticket-ticket-context.md",
        "reply": "*-ticket-reply.md",
    },
    "interview": {
        "notes": "*-interview-notes.md",
        "requirements": "*-interview-requirements.md",
    },
    "explore": {
        "findings": "*-explore-findings.md",
    },
    "investigate": {
        "findings": "*-investigate-findings.md",
    },
    "plan": {
        "debate_summary": "*-plan-debate-summary.md",
        "solution_plan": "*-plan-solution-plan.md",
    },
    "review-develop": {
        "code_review": "*-develop-code-review.md",
        "preflight": "*-plugin-review-preflight.md",
    },
    "lint": {
        "report": "*-lint-lint-report.md",
    },
    "perf": {
        "analysis": "*-perf-perf-analysis.md",
    },
    "release-notes": {
        "report": "*-plugin-release-notes.md",
    },
    "handoff": {
        "prompt": "*-handoff-handoff-prompt.md",
    },
}

_SCRIPT_ENTRYPOINTS = {
    "generate_agent_projections": "python3 scripts/generate_agent_projections.py",
    "generate_maintainer_guide": "python3 scripts/generate_maintainer_guide.py",
    "derive_agent_callers": "python3 scripts/derive_agent_callers.py",
    "select_health_artifacts": "python3 scripts/select_health_artifacts.py",
}

_GENERATED_OUTPUT_SURFACES = {
    "maintainer_guide": (
        "docs/maintainer_tooling.md",
        "docs/maintainer_tooling/",
        "docs/maintainer_tooling/*.md",
    ),
    "documentation_maps": (
        "docs/agent_map.md",
        "docs/skills_map.md",
        "docs/plugin_graph.md",
    ),
    "agent_projections": (
        "profile-al-dev-shared/generated/agents/claude/*.md",
        "profile-al-dev-shared/generated/agents/copilot/*.md",
        "profile-al-dev-shared/generated/agents/codex/*.toml",
    ),
}

_ALLOWED_TEMPLATE_PATTERNS = (
    "docs/health/YYYY-MM-DD-<surface>-findings.md",
    "docs/health/YYYY-MM-DD-<surface>-health.md",
    "docs/health/YYYY-MM-DD-<surface>-friction-findings.md",
    "pyproject.toml",
    "Features/*.md",
    "profile-al-dev-shared/skills/skill-*/SKILL.md",
    "profile-al-dev-shared/agents/agent-*.md",
    "profile-al-dev-shared/agents/review-*.md",
    "../../../*-knowledge.md",
    ".claude/skills/validate-*/SKILL.md",
    ".codex/agents/custom-*.md",
    "../../knowledge/*.md",
    "knowledge/file.md",
    "scripts/generate-*.py",
    "docs/migration-v*.md",
    "path/to/file.md",
)

_LEGACY_REFERENCE_ALIASES = {
    "legacy_script.generate_agent_projections": ("generate-agent-projections.py",),
    "legacy_script.generate_maintainer_guide": ("generate-maintainer-guide.py",),
    "legacy_script.derive_agent_callers": ("derive-agent-callers.py",),
    "legacy_artifact.requirements": (".dev/01-requirements.md",),
    "legacy_artifact.solution_plan": (".dev/02-solution-plan.md",),
    "legacy_artifact.test_plan": (".dev/test-plan.md",),
    "legacy_artifact.prefixed_plan": (".dev/*-al-dev-plan-solution-plan.md",),
    "legacy_artifact.prefixed_review": (".dev/*-al-dev-develop-code-review.md",),
    "legacy_artifact.prefixed_lint": (".dev/*-al-dev-lint-lint-report.md",),
    # Pre-2026-07-02 hyphen spellings of the generated disposition-ledger views.
    # The store now writes underscore names (see paths.py); these hyphen forms
    # are deleted on disk, so any surviving reference is a drift bug. Listing
    # them here upgrades the diagnostic from generic dead-path to a clear
    # legacy-alias fix hint.
    "legacy_artifact.dispositions_open": ("docs/health/dispositions-open.md",),
    "legacy_artifact.dispositions_current": ("docs/health/dispositions-current.md",),
    "legacy_artifact.dispositions_index": ("docs/health/dispositions-index.json",),
}


def runtime_artifact_pattern_groups() -> Dict[str, Dict[str, str]]:
    """Return runtime artifact patterns grouped by skill and artifact role."""

    return {skill: dict(patterns) for skill, patterns in _ARTIFACT_PATTERN_GROUPS.items()}


def canonical_artifact_patterns() -> Dict[str, str]:
    """Return flattened runtime artifact patterns keyed by semantic family."""

    return {
        f"{skill}.{artifact}": pattern
        for skill, artifacts in _ARTIFACT_PATTERN_GROUPS.items()
        for artifact, pattern in artifacts.items()
    }


def canonical_script_entrypoints() -> Dict[str, str]:
    """Return runnable script entrypoints keyed by stable semantic name."""

    return dict(_SCRIPT_ENTRYPOINTS)


def generated_output_surfaces() -> Dict[str, Tuple[str, ...]]:
    """Return generated output declarations keyed by output family."""

    return {name: tuple(paths) for name, paths in _GENERATED_OUTPUT_SURFACES.items()}


def allowed_template_patterns() -> Tuple[str, ...]:
    """Return template/example patterns that should not be treated as live refs."""

    return tuple(_ALLOWED_TEMPLATE_PATTERNS)


def legacy_reference_aliases() -> Dict[str, Tuple[str, ...]]:
    """Return explicit legacy aliases that validators may classify separately."""

    return {name: tuple(values) for name, values in _LEGACY_REFERENCE_ALIASES.items()}
