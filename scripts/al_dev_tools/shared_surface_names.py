"""Canonical naming contract for the shared distributed plugin surface."""

from __future__ import annotations

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


def strip_legacy_shared_prefix(name: str) -> str:
    """Return the canonical prefix-free shared name for a prefixed entry."""

    if name.startswith(LEGACY_SHARED_PREFIX):
        return name[len(LEGACY_SHARED_PREFIX):]
    return name


def runtime_artifact_patterns() -> dict[str, dict[str, str]]:
    """Runtime artifact globs keyed by canonical prefix-free shared skill name."""

    return {
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
            "solution_plan": "*-plan-solution-plan.md",
        },
        "handoff": {
            "prompt": "*-handoff-handoff-prompt.md",
        },
    }
