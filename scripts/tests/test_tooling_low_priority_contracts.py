"""Regression tests for low-priority tooling health fixes."""
from __future__ import annotations

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


ACTIVE_TOOLING_SKILLS = sorted(
    path
    for path in (REPO_ROOT / ".claude" / "skills").glob("*/SKILL.md")
    if "archived" not in path.parts
)

SYNC_MAP_AGENTS = [
    REPO_ROOT / ".claude" / "agents" / "sync-documentation-maps-agent-audit.md",
    REPO_ROOT / ".claude" / "agents" / "sync-documentation-maps-skill-audit.md",
    REPO_ROOT / ".claude" / "agents" / "sync-documentation-maps-agent-update.md",
    REPO_ROOT / ".claude" / "agents" / "sync-documentation-maps-skill-update.md",
]


def read(path: str | Path) -> str:
    path = Path(path)
    if not path.is_absolute():
        path = REPO_ROOT / path
    return path.read_text(encoding="utf-8")


def untagged_fence_lines(path: Path) -> list[int]:
    lines = read(path).splitlines()
    in_block = False
    untagged: list[int] = []
    for line_no, line in enumerate(lines, start=1):
        if not line.startswith("```"):
            continue
        marker = line.strip()
        if not in_block:
            if marker == "```":
                untagged.append(line_no)
            in_block = True
        else:
            in_block = False
    return untagged


class ToolingLowPriorityContractsTest(unittest.TestCase):
    def test_active_tooling_skill_fences_are_language_tagged(self) -> None:
        failures = {
            str(path.relative_to(REPO_ROOT)): untagged_fence_lines(path)
            for path in ACTIVE_TOOLING_SKILLS
            if untagged_fence_lines(path)
        }
        self.assertEqual({}, failures)

    def test_sync_documentation_map_agent_fences_are_language_tagged(self) -> None:
        failures = {
            str(path.relative_to(REPO_ROOT)): untagged_fence_lines(path)
            for path in SYNC_MAP_AGENTS
            if untagged_fence_lines(path)
        }
        self.assertEqual({}, failures)

    def test_plugin_health_report_merges_rank_and_write_phase(self) -> None:
        text = read(".claude/skills/plugin-health-report/SKILL.md")
        self.assertIn("## Phase 2 - Rank and Write Dossier", text)
        self.assertNotIn("## Phase 3 - Write dossier", text)
        self.assertNotIn("## Phase 3 - Write Dossier", text)

    def test_analyze_design_skills_delegate_highest_leverage_selection(self) -> None:
        for path in [
            ".claude/skills/analyze-agent-design/SKILL.md",
            ".claude/skills/analyze-skill-design/SKILL.md",
        ]:
            with self.subTest(path=path):
                text = read(path)
                self.assertIn(
                    "`/draft-map-suggestions` owns highest-leverage selection", text
                )
                self.assertNotIn("After Phase 5 invocation completes", text)

    def test_low_priority_name_fit_descriptions_are_explicit(self) -> None:
        expected_fragments = {
            ".claude/skills/review-agent-map/SKILL.md": [
                "Pass --no-update to run audit-only"
            ],
            ".claude/skills/review-skill-map/SKILL.md": [
                "Pass --no-update to run audit-only"
            ],
            ".claude/skills/align-harness-repos/SKILL.md": [
                "single shared plugin surface"
            ],
            ".claude/skills/audit-quality/SKILL.md": [
                "can offer or apply fixes after reporting"
            ],
            ".claude/skills/audit-knowledge-quality/SKILL.md": [
                "can offer targeted fixes after reporting"
            ],
            ".claude/skills/projection-sync/SKILL.md": [
                "unidirectionally regenerates harness-native projections"
            ],
            ".claude/skills/discover-agent-design/SKILL.md": [
                "Internal discovery phase"
            ],
            ".claude/skills/discover-skill-design/SKILL.md": [
                "Internal discovery phase"
            ],
        }
        for path, fragments in expected_fragments.items():
            text = read(path)
            for fragment in fragments:
                with self.subTest(path=path, fragment=fragment):
                    self.assertIn(fragment, text)


if __name__ == "__main__":
    unittest.main()
