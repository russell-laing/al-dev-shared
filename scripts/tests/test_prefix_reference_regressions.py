from __future__ import annotations

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

SHARED_SURFACE_CASES = {
    "profile-al-dev-shared/knowledge/developer-invocation-patterns.md": [
        "Reference document for the three contexts in which `al-dev-developer` is spawned.",
        "agent: al-dev-shared:al-dev-developer-<variant>",
    ],
    "profile-al-dev-shared/knowledge/anti-patterns.md": [
        "Always use `al-dev-developer` agent for code",
    ],
    "profile-al-dev-shared/knowledge/workflow-routing.md": [
        "Spawns `al-dev-developer` with confirmed approach",
    ],
    "profile-al-dev-shared/knowledge/map-change-rubber-duck-checks.md": [
        "profile-al-dev-shared/agents/al-dev-developer.md",
        "profile-al-dev-shared/generated/agents/claude/al-dev-developer.md",
    ],
    "profile-al-dev-shared/agents/corruption-recover.md": [
        "# Agent: al-dev-commit-recover",
    ],
    "profile-al-dev-shared/skills/develop-orchestrate/tests/scenarios.yaml": [
        "al-dev-shared:al-dev-developer",
    ],
    "profile-al-dev-shared/skills/fix/tests/scenarios.yaml": [
        "al-dev-shared:al-dev-developer",
    ],
    "profile-al-dev-shared/skills/develop-orchestrate/SKILL.md": [
        "/review-develop-preflight",
    ],
    "profile-al-dev-shared/skills/fix/SKILL.md": [
        "/review-develop-preflight",
    ],
    "profile-al-dev-shared/skills/generic-preflight/SKILL.md": [
        "/plan-preflight",
        "/review-develop-preflight",
    ],
}

TOOLING_CASES = {
    ".claude/agents/sync-map-documentation-skill-metadata.md": [
        '"spawned_agents": ["al-dev-shared:al-dev-developer"]',
        "Spawn **al-dev-solution-architect**",
    ],
    ".claude/skills/fix-knowledge-quality/SKILL.md": [
        "al-dev-docs-writer",
        "al-dev-shared:al-dev-docs-writer",
    ],
    ".claude/knowledge/fix-knowledge-quality-dispatch.md": [
        "## Agent: al-dev-shared:al-dev-docs-writer",
        "Agent: al-dev-shared:al-dev-docs-writer",
    ],
    ".codex/skills/review-improvement-reports/SKILL.md": [
        "profile-al-dev-shared/skills/al-dev-plan/SKILL.md",
        "profile-al-dev-shared/skills/al-dev-develop/SKILL.md",
        "profile-al-dev-shared/skills/al-dev-fix/SKILL.md",
        "profile-al-dev-shared/skills/al-dev-commit/SKILL.md",
    ],
}

DOC_CASES = {
    "docs/projection_layer_readme.md": [
        "generated/agents/claude/al-dev-interview.md",
        "profile-al-dev-shared/skills/al-dev-plan/SKILL.md",
        "al-dev-shared:al-dev-solution-architect",
        "al-dev-shared:al-dev-interview",
        "al-dev-shared:al-dev-developer",
        "generated/agents/claude/al-dev-developer.md",
    ],
    "CLAUDE.md": [
        "al-dev-investigate",
        "al-dev-ticket",
        "al-dev-support-reply",
        "al-dev-plan",
        "al-dev-develop",
        "al-dev-commit",
        "al-dev-fix",
        "al-dev-explore",
        "al-dev-interview",
        "al-dev-perf",
        "al-dev-release-notes",
        "al-dev-handoff",
        "al-dev-document",
        "al-dev-plan-preflight",
        "al-dev-plan-with-critics",
        "al-dev-plan-final-review",
        "al-dev-commit-preflight",
        "al-dev-commit-execute",
        "al-dev-review-develop-preflight",
        "al-dev-help",
    ],
    "docs/skills_map.md": [
        "al-dev-shared:al-dev-developer-tdd",
        "complex fixes route through al-dev-solution-architect",
        "### /al-dev-explore",
        "### /al-dev-interview",
    ],
    "docs/harness_coverage_model.md": [
        "profile-al-dev-shared/skills/al-dev-develop-orchestrate/tests/scenarios.yaml",
    ],
    "docs/knowledge_quality.md": [
        "skills/al-dev-investigate/SKILL.md",
    ],
    ".claude/agents/design-skill-lens-preplanning.md": [
        "/al-dev-interview",
        "/al-dev-explore",
        "al-dev-explore-deep",
    ],
}

AGENT_MAP_CASES = {
    "docs/agent_map.md": [
        "### al-dev-general-code-reviewer",
        "### al-dev-commit-analyzer",
        "### al-dev-developer-tdd",
        "### al-dev-interview",
        "### al-dev-solution-architect",
        ".dev/$(date +%Y-%m-%d)-al-dev-developer-tdd-log.md",
        ".dev/$(date +%Y-%m-%d)-al-dev-explore-findings.md",
        ".dev/*-al-dev-interview-requirements.md",
        ".dev/$(date +%Y-%m-%d)-al-dev-interview-requirements.md",
    ],
}


class PrefixReferenceRegressionTests(unittest.TestCase):
    def test_shared_surface_has_no_retired_prefix_references(self) -> None:
        for rel_path, needles in SHARED_SURFACE_CASES.items():
            text = (REPO_ROOT / rel_path).read_text(encoding="utf-8")
            for needle in needles:
                self.assertNotIn(needle, text, f"{rel_path} still contains {needle!r}")

    def test_tooling_surface_has_no_retired_prefix_references(self) -> None:
        for rel_path, needles in TOOLING_CASES.items():
            text = (REPO_ROOT / rel_path).read_text(encoding="utf-8")
            for needle in needles:
                self.assertNotIn(needle, text, f"{rel_path} still contains {needle!r}")

    def test_authored_docs_have_no_retired_prefix_edge_cases(self) -> None:
        for rel_path, needles in DOC_CASES.items():
            text = (REPO_ROOT / rel_path).read_text(encoding="utf-8")
            if rel_path == "CLAUDE.md":
                start = text.index("**Active skills:**")
                end = text.index("## Diagram Guidance")
                text = text[start:end]
            for needle in needles:
                self.assertNotIn(needle, text, f"{rel_path} still contains {needle!r}")

    def test_agent_map_has_no_retired_headings_or_runtime_artifact_names(self) -> None:
        for rel_path, needles in AGENT_MAP_CASES.items():
            text = (REPO_ROOT / rel_path).read_text(encoding="utf-8")
            for needle in needles:
                self.assertNotIn(needle, text, f"{rel_path} still contains {needle!r}")


if __name__ == "__main__":
    unittest.main()
