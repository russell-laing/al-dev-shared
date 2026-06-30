"""Canonical naming contract for the shared distributed plugin surface."""

from __future__ import annotations

from .reference_contracts import (
    allowed_template_patterns as _allowed_template_patterns,
    canonical_artifact_patterns as _canonical_artifact_patterns,
    canonical_script_entrypoints as _canonical_script_entrypoints,
    generated_output_surfaces as _generated_output_surfaces,
    legacy_reference_aliases as _legacy_reference_aliases,
)

LEGACY_SHARED_PREFIX = "al-dev-"

SHARED_SKILL_RENAMES = {
    "al-dev-commit": "commit",
    "al-dev-commit-execute": "commit-execute",
    "al-dev-commit-preflight": "commit-preflight",
    "al-dev-develop-orchestrate": "develop-orchestrate",
    "al-dev-document": "document",
    "al-dev-explore": "explore",
    "al-dev-fix": "fix",
    "al-dev-handoff": "handoff",
    "al-dev-help": "help",
    "al-dev-interview": "interview",
    "al-dev-investigate": "investigate",
    "al-dev-lint": "lint",
    "al-dev-perf": "perf",
    "al-dev-plan": "plan",
    "al-dev-plan-final-review": "plan-final-review",
    "al-dev-plan-preflight": "plan-preflight",
    "al-dev-plan-with-critics": "plan-with-critics",
    "al-dev-release-notes": "release-notes",
    "al-dev-review-develop": "review-develop",
    "al-dev-review-develop-preflight": "review-develop-preflight",
    "al-dev-support-reply": "support-reply",
    "al-dev-ticket": "ticket",
}

SHARED_AGENT_RENAMES = {
    "al-dev-al-pattern-reviewer": "al-pattern-reviewer",
    "al-dev-commit-analyzer": "commit-analyzer",
    "al-dev-commit-executor": "commit-executor",
    "al-dev-commit-group-drafter": "commit-group-drafter",
    "al-dev-commit-hook-classifier": "commit-hook-classifier",
    "al-dev-commit-hook-fixer": "commit-hook-fixer",
    "al-dev-commit-lint-fixer": "commit-lint-fixer",
    "al-dev-corruption-recover": "corruption-recover",
    "al-dev-developer-tdd": "developer-tdd",
    "al-dev-developer-traditional": "developer-traditional",
    "al-dev-diagnostics-resolver": "diagnostics-resolver",
    "al-dev-docs-writer": "docs-writer",
    "al-dev-explore": "explore",
    "al-dev-general-code-reviewer": "general-code-reviewer",
    "al-dev-interview": "interview",
    "al-dev-performance-reviewer": "performance-reviewer",
    "al-dev-release-notes-writer": "release-notes-writer",
    "al-dev-script-engineer": "script-engineer",
    "al-dev-security-reviewer": "security-reviewer",
    "al-dev-solution-architect": "solution-architect",
    "al-dev-support-reply-drafter": "support-reply-drafter",
    "al-dev-support-researcher": "support-researcher",
    "al-dev-ticket-context-writer": "ticket-context-writer",
}

CANONICAL_SHARED_SKILLS = tuple(SHARED_SKILL_RENAMES.values())
CANONICAL_SHARED_AGENTS = tuple(SHARED_AGENT_RENAMES.values())

SHARED_WORKFLOW_ORDER = {
    "development-spine": (
        "plan",
        "develop-orchestrate",
        "review-develop",
        "commit",
    ),
    "ticket-support": (
        "ticket",
        "support-reply",
    ),
    "direct-fix": (
        "fix",
        "commit",
    ),
}


def strip_legacy_shared_prefix(name: str) -> str:
    """Return the canonical prefix-free shared name for a prefixed entry."""

    if name.startswith(LEGACY_SHARED_PREFIX):
        return name[len(LEGACY_SHARED_PREFIX):]
    return name


def runtime_artifact_patterns() -> dict[str, dict[str, str]]:
    """Runtime artifact globs keyed by canonical prefix-free shared skill name."""

    patterns = canonical_artifact_patterns()
    return {
        "commit-execute": {
            "analysis": patterns["commit_analysis"],
        },
        "develop-orchestrate": {
            "progress": patterns["develop_progress"],
            "checklist": patterns["develop_checklist"],
            "scope": patterns["develop_scope"],
            "phase4_handoff": patterns["develop_phase4_handoff"],
        },
        "developer-tdd": {
            "test_plan": patterns["developer_tdd_test_plan"],
            "log": patterns["developer_tdd_log"],
        },
        "ticket": {
            "context": patterns["ticket_context"],
            "reply": patterns["ticket_reply"],
        },
        "interview": {
            "notes": patterns["interview_notes"],
            "requirements": patterns["interview_requirements"],
        },
        "explore": {
            "findings": patterns["explore_findings"],
        },
        "investigate": {
            "findings": patterns["investigate_findings"],
        },
        "plan": {
            "debate_summary": patterns["plan_debate_summary"],
            "solution_plan": patterns["plan_solution_plan"],
        },
        "review-develop": {
            "code_review": patterns["develop_code_review"],
            "preflight": patterns["review_preflight"],
        },
        "lint": {
            "report": patterns["lint_report"],
        },
        "perf": {
            "analysis": patterns["perf_analysis"],
        },
        "release-notes": {
            "report": patterns["release_notes"],
        },
        "handoff": {
            "prompt": patterns["handoff_prompt"],
        },
    }


def canonical_artifact_patterns() -> dict[str, str]:
    """Compatibility adapter for the canonical reference-contract registry."""

    return _canonical_artifact_patterns()


def canonical_script_entrypoints() -> dict[str, str]:
    """Compatibility adapter for the canonical reference-contract registry."""

    return _canonical_script_entrypoints()


def generated_output_surfaces() -> dict[str, tuple[str, ...]]:
    """Compatibility adapter for the canonical reference-contract registry."""

    return _generated_output_surfaces()


def allowed_template_patterns() -> tuple[str, ...]:
    """Compatibility adapter for the canonical reference-contract registry."""

    return _allowed_template_patterns()


def legacy_reference_aliases() -> dict[str, tuple[str, ...]]:
    """Compatibility adapter for the canonical reference-contract registry."""

    return _legacy_reference_aliases()
