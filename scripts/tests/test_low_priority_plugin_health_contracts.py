"""Regression tests for low-priority plugin-health contract fixes."""
from __future__ import annotations

import inspect
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def read(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def frontmatter(path: str) -> str:
    text = read(path)
    assert text.startswith("---\n"), f"{path} has no frontmatter"
    return text.split("---\n", 2)[1]


def _called_from_unittest_loader() -> bool:
    return any("unittest/loader.py" in frame.filename for frame in inspect.stack())


def test_developer_agents_do_not_declare_unused_grep_tool() -> unittest.FunctionTestCase | None:
    def body() -> None:
        for path in [
            "profile-al-dev-shared/agents/developer-tdd.md",
            "profile-al-dev-shared/agents/developer-traditional.md",
        ]:
            fm = frontmatter(path)
            assert '"Grep"' not in fm, f"{path} still declares unused Grep"
            assert 'tools: ["Read", "Write", "Bash"]' in fm

    if _called_from_unittest_loader():
        return unittest.FunctionTestCase(body)
    body()


def test_developer_agent_inputs_explain_auto_located_dev_artifacts() -> unittest.FunctionTestCase | None:
    def body() -> None:
        for path in [
            "profile-al-dev-shared/agents/developer-tdd.md",
            "profile-al-dev-shared/agents/developer-traditional.md",
        ]:
            text = read(path)
            assert "Callers do not pass these paths explicitly" in text
            assert "auto-locates the latest matching files in `.dev/` by glob" in text

    if _called_from_unittest_loader():
        return unittest.FunctionTestCase(body)
    body()


def test_al_dev_plan_phase_2_keeps_architect_invocation_reference() -> unittest.FunctionTestCase | None:
    def body() -> None:
        text = read("profile-al-dev-shared/skills/plan/SKILL.md")
        phase_2 = text.split("## Phase 2: Spawn Architect Team", 1)[1]
        phase_2 = phase_2.split("## Phase 3:", 1)[0]
        assert "knowledge/architect-invocation-patterns.md" in phase_2

    if _called_from_unittest_loader():
        return unittest.FunctionTestCase(body)
    body()


def test_review_develop_code_review_artifact_is_terminal_output_optional_commit_context() -> unittest.FunctionTestCase | None:
    def body() -> None:
        handoff_map = read("profile-al-dev-shared/knowledge/handoff-chain-map.md")

        assert "`review-develop` | `code-review.md` | commit | Optional | Ctx" in handoff_map
        assert "`review-develop` | `code-review.md` | commit | **Mandatory**" not in handoff_map

    if _called_from_unittest_loader():
        return unittest.FunctionTestCase(body)
    body()


def test_low_priority_skill_descriptions_match_current_behavior() -> unittest.FunctionTestCase | None:
    def body() -> None:
        expected = {
            "profile-al-dev-shared/skills/fix/SKILL.md": "Lightweight bug fix workflow without approval gates (fast iteration)",
            "profile-al-dev-shared/skills/lint/SKILL.md": "Run AL compile, then dispatch diagnostics-resolver to auto-fix",
            "profile-al-dev-shared/skills/handoff/SKILL.md": "Package investigation context and generate a session-continuation prompt",
            "profile-al-dev-shared/skills/explore/SKILL.md": "Explore codebases fast — loads project context, classifies the question, then delegates to an Explore subagent for structured, persistent findings.",
            ".claude/archived/skills/al-dev-consolidate/SKILL.md": "Consolidate .dev/ workflow artifacts into per-session summary notes and a",
        }
        for path, description in expected.items():
            fm = frontmatter(path)
            assert f"description: {description}" in fm or description in fm

    if _called_from_unittest_loader():
        return unittest.FunctionTestCase(body)
    body()


def test_repo_local_map_suggestions_skill_uses_maintainer_name() -> unittest.FunctionTestCase | None:
    def body() -> None:
        old_path = REPO_ROOT / ".claude/skills/al-dev-map-suggestions-verify/SKILL.md"
        stale_path = REPO_ROOT / ".claude/skills/verify-map-suggestions/SKILL.md"
        new_path = REPO_ROOT / ".claude/skills/plan-plugin-findings/SKILL.md"
        assert not old_path.exists(), "repo-local maintainer skill still uses al-dev-* name"
        assert not stale_path.exists(), "stale verify-map-suggestions skill still present; should be plan-plugin-findings"
        assert new_path.is_file(), "renamed repo-local maintainer skill is missing"
        text = new_path.read_text(encoding="utf-8")
        assert "name: plan-plugin-findings" in text
        assert "/verify-map-suggestions" not in text

    if _called_from_unittest_loader():
        return unittest.FunctionTestCase(body)
    body()


def test_repo_local_workflows_reference_plan_health_findings() -> unittest.FunctionTestCase | None:
    def body() -> None:
        for path in [
            ".claude/skills/report-plugin-health/SKILL.md",
            ".claude/skills/audit-plugin-health/SKILL.md",
            "docs/al-dev-naming-convention.md",
        ]:
            text = read(path)
            assert "plan-plugin-findings" in text, f"{path} lacks renamed maintainer command"

    if _called_from_unittest_loader():
        return unittest.FunctionTestCase(body)
    body()


def load_tests(loader, tests, pattern):  # noqa: ARG001
    suite = unittest.TestSuite()
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            suite.addTest(fn())
    return suite


if __name__ == "__main__":
    unittest.main()
