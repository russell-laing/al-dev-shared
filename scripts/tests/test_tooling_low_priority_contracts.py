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
    REPO_ROOT / ".claude" / "agents" / "sync-documentation-maps-agent-metadata.md",
    REPO_ROOT / ".claude" / "agents" / "sync-documentation-maps-agent-compare.md",
    REPO_ROOT / ".claude" / "agents" / "sync-documentation-maps-skill-metadata.md",
    REPO_ROOT / ".claude" / "agents" / "sync-documentation-maps-skill-compare.md",
    REPO_ROOT / ".claude" / "agents" / "sync-documentation-maps-agent-update.md",
    REPO_ROOT / ".claude" / "agents" / "sync-documentation-maps-skill-update.md",
]

ARCHIVED_AUDIT_AGENTS = [
    REPO_ROOT / ".claude" / "agents" / "archived" / "sync-documentation-maps-agent-audit.md",
    REPO_ROOT / ".claude" / "agents" / "archived" / "sync-documentation-maps-skill-audit.md",
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

    def test_old_audit_agents_are_archived_not_active(self) -> None:
        """Old audit agents must be in archived/, not in the active .claude/agents/ root."""
        active_agents_dir = REPO_ROOT / ".claude" / "agents"
        for archived_path in ARCHIVED_AUDIT_AGENTS:
            # Must exist in archived/
            self.assertTrue(
                archived_path.exists(),
                f"Expected archived agent at {archived_path}",
            )
            # Must NOT exist in the active agents directory root
            active_path = active_agents_dir / archived_path.name
            self.assertFalse(
                active_path.exists(),
                f"Old audit agent {archived_path.name} still present as active agent",
            )

    def test_sync_maps_skill_metadata_schema_has_phase_count_and_spawned_agents(
        self,
    ) -> None:
        """skill-metadata agent must document phase_count and spawned_agents fields
        so discrepancy agent can detect phase_count_mismatch and agent_name_mismatch."""
        text = read(
            ".claude/agents/sync-documentation-maps-skill-metadata.md"
        )
        self.assertIn("phase_count", text)
        self.assertIn("spawned_agents", text)

    def test_sync_maps_agent_discrepancy_documents_all_five_types(self) -> None:
        """agent-discrepancy agent must document all five canonical discrepancy types."""
        text = read(".claude/agents/sync-documentation-maps-agent-compare.md")
        for dtype in (
            "missing_from_map",
            "stale_in_map",
            "model_mismatch",
            "tools_mismatch",
            "caller_mismatch",
        ):
            with self.subTest(dtype=dtype):
                self.assertIn(dtype, text)

    def test_sync_maps_skill_discrepancy_documents_all_four_types(self) -> None:
        """skill-discrepancy agent must document all four canonical discrepancy types
        including phase_count_mismatch and agent_name_mismatch."""
        text = read(".claude/agents/sync-documentation-maps-skill-compare.md")
        for dtype in (
            "missing_from_map",
            "stale_in_map",
            "phase_count_mismatch",
            "agent_name_mismatch",
        ):
            with self.subTest(dtype=dtype):
                self.assertIn(dtype, text)

    def test_plugin_health_report_merges_rank_and_write_phase(self) -> None:
        # Ranking and writing the dossier must stay in one merged phase. The
        # phase number moved from 2 to 3 in 7ec3e89 (#839,#847), which inserted
        # a "Filter and verify" phase ahead of it; the merge invariant is
        # unchanged. The negative guards catch a re-split where writing would
        # become its own phase after rank.
        text = read(".claude/skills/plugin-health-report/SKILL.md")
        self.assertIn("## Phase 3 — Rank and Write Dossier", text)
        self.assertNotIn("## Phase 4 — Write dossier", text)
        self.assertNotIn("## Phase 4 — Write Dossier", text)

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
                "the HIGH-severity fix guidance interactively "
                "when the user opts in"
            ],
            ".claude/skills/regenerate-projections/SKILL.md": [
                "unidirectionally regenerates harness-native agent projections"
            ],
        }
        for path, fragments in expected_fragments.items():
            text = read(path)
            for fragment in fragments:
                with self.subTest(path=path, fragment=fragment):
                    self.assertIn(fragment, text)


if __name__ == "__main__":
    unittest.main()
