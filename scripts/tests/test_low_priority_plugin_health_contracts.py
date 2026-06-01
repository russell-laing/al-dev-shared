"""Regression tests for low-priority plugin-health contract fixes."""
from __future__ import annotations

import inspect
import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def read(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def frontmatter(path: str) -> str:
    text = read(path)
    assert text.startswith("---\n"), f"{path} has no frontmatter"
    return text.split("---\n", 2)[1]


def test_developer_agents_do_not_declare_unused_grep_tool() -> None:
    for path in [
        "profile-al-dev-shared/agents/al-dev-developer-tdd.md",
        "profile-al-dev-shared/agents/al-dev-developer-traditional.md",
    ]:
        fm = frontmatter(path)
        assert '"Grep"' not in fm, f"{path} still declares unused Grep"
        assert 'tools: ["Read", "Write", "Bash"]' in fm


def test_developer_agent_inputs_explain_auto_located_dev_artifacts() -> None:
    for path in [
        "profile-al-dev-shared/agents/al-dev-developer-tdd.md",
        "profile-al-dev-shared/agents/al-dev-developer-traditional.md",
    ]:
        text = read(path)
        assert "Callers do not pass these paths explicitly" in text
        assert "auto-locates the latest matching files in `.dev/` by glob" in text


def test_al_dev_plan_phase_2_keeps_architect_invocation_reference() -> None:
    text = read("profile-al-dev-shared/skills/al-dev-plan/SKILL.md")
    phase_2 = text.split("## Phase 2: Spawn Architect Team", 1)[1]
    phase_2 = phase_2.split("## Phase 3:", 1)[0]
    assert "knowledge/architect-invocation-patterns.md" in phase_2


def test_review_develop_code_review_artifact_is_terminal_output_optional_commit_context() -> None:
    skill = read("profile-al-dev-shared/skills/al-dev-review-develop/SKILL.md")
    contracts = read("profile-al-dev-shared/knowledge/artifact-contracts.md")
    handoff_map = read("profile-al-dev-shared/knowledge/handoff-chain-map.md")

    assert "terminal user-facing review output and optional context for `al-dev-commit`" in skill
    assert "terminal user-facing review output; optional context for `al-dev-commit`" in contracts
    assert "`al-dev-review-develop` | `code-review.md` | User, optional commit context | Terminal | Review output" in handoff_map
    assert "review-develop | `code-review.md` | commit | **Mandatory**" not in handoff_map


def test_low_priority_skill_descriptions_match_current_behavior() -> None:
    expected = {
        "profile-al-dev-shared/skills/al-dev-fix/SKILL.md": "Fast bug-fix workflow for trivial direct edits and non-trivial fixes that may route through architect/developer analysis.",
        "profile-al-dev-shared/skills/al-dev-lint/SKILL.md": "Run AL compile, parse diagnostics, auto-fix supported AL issues, and write a lint report.",
        "profile-al-dev-shared/skills/al-dev-handoff/SKILL.md": "Package investigation context, source evidence, and a destination prompt for cross-repo session migration.",
        "profile-al-dev-shared/skills/al-dev-explore/SKILL.md": "Explore codebases with a delegated subagent and persist structured findings to `.dev/` for downstream workflows.",
        "profile-al-dev-shared/skills/al-dev-consolidate/SKILL.md": "Consolidate `.dev/` workflow artifacts into per-session summary notes, a sessions index, and vault-ready archive outputs.",
    }
    for path, description in expected.items():
        fm = frontmatter(path)
        assert f"description: {description}" in fm or description in fm


def test_repo_local_map_suggestions_skill_uses_maintainer_name() -> None:
    old_path = REPO_ROOT / ".claude/skills/al-dev-map-suggestions-verify/SKILL.md"
    new_path = REPO_ROOT / ".claude/skills/verify-map-suggestions/SKILL.md"
    assert not old_path.exists(), "repo-local maintainer skill still uses al-dev-* name"
    assert new_path.is_file(), "renamed repo-local maintainer skill is missing"
    text = new_path.read_text(encoding="utf-8")
    assert "name: verify-map-suggestions" in text
    assert "/verify-map-suggestions" in text
    assert "/al-dev-map-suggestions-verify" not in text


def test_repo_local_workflows_reference_verify_map_suggestions() -> None:
    for path in [
        ".claude/skills/plugin-health-report/SKILL.md",
        ".claude/skills/plugin-health-audit/SKILL.md",
        "docs/al-dev-naming-convention.md",
    ]:
        text = read(path)
        assert "verify-map-suggestions" in text, f"{path} lacks renamed maintainer command"


def _run(func):
    sig = inspect.signature(func)
    if not sig.parameters:
        func()
    else:
        raise TypeError(f"Unsupported signature: {func.__name__}{sig}")


def load_tests(loader, tests, pattern):  # noqa: ARG001
    suite = unittest.TestSuite()
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            suite.addTest(unittest.FunctionTestCase(lambda fn=fn: _run(fn)))
    return suite


if __name__ == "__main__":
    unittest.main()
