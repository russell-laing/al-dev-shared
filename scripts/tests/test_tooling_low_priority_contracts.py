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
        self.assertIn("## Phase 2 — Rank and Write Dossier", text)
        self.assertNotIn("## Phase 3 - Write dossier", text)
        self.assertNotIn("## Phase 3 - Write Dossier", text)

    def test_plugin_health_excludes_archived_tooling_skills(self) -> None:
        discover = read(".claude/skills/plugin-health-discover/SKILL.md")
        handoff_lens = read(".claude/agents/design-skill-lens-handoff-gaps.md")

        self.assertIn('! -path "*/archived/*"', discover)
        self.assertIn("only the other paths in `file_list`", handoff_lens)

    def test_plugin_health_cadence_guard_has_explicit_happy_path(self) -> None:
        discover = read(".claude/skills/plugin-health-discover/SKILL.md")

        self.assertIn(
            "Disposition coverage exists and is dated on or after the dossier",
            discover,
        )
        self.assertIn("proceed to the stale-open check", discover)

    def test_sync_maps_cadence_guard_keeps_only_operational_rule(self) -> None:
        sync_maps = read(".claude/skills/sync-documentation-maps/SKILL.md")

        self.assertNotIn(
            "Abandoned runs spawn audit agents whose results are never read",
            sync_maps,
        )
        self.assertIn("Check the checkpoint before dispatching", sync_maps)

    def test_low_priority_name_fit_descriptions_are_explicit(self) -> None:
        expected_fragments = {
            ".claude/skills/align-harness-repos/SKILL.md": [
                "single shared plugin surface"
            ],
            ".claude/skills/audit-knowledge-quality/SKILL.md": [
                "offers user-gated fix guidance for HIGH-severity findings"
            ],
            ".claude/skills/projection-sync/SKILL.md": [
                "unidirectionally regenerates harness-native projections"
            ],
        }
        for path, fragments in expected_fragments.items():
            text = read(path)
            for fragment in fragments:
                with self.subTest(path=path, fragment=fragment):
                    self.assertIn(fragment, text)


if __name__ == "__main__":
    unittest.main()
