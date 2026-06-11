"""Tests for sync-documentation-maps-apply validation contract.

Asserts that the documented apply-stage artifact-validation rules are present
and correct in checkpoint-patterns.md and SKILL.md, and that Phase 1 / Phase 3
stay within their prescribed line-count budgets.
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

CHECKPOINT_PATTERNS = (
    REPO_ROOT
    / ".claude"
    / "skills"
    / "sync-documentation-maps"
    / "checkpoint-patterns.md"
)
APPLY_SKILL = (
    REPO_ROOT
    / ".claude"
    / "skills"
    / "sync-documentation-maps-apply"
    / "SKILL.md"
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _apply_section(text: str) -> str:
    """Return the text of the Apply-stage artifact validation section."""
    start = text.find("## Apply-stage Artifact Validation")
    if start == -1:
        return ""
    # Grab everything from that heading to the next ## heading (or EOF)
    rest = text[start:]
    m = re.search(r"\n## ", rest[1:])
    return rest[: m.start() + 1] if m else rest


def _phase_line_counts(text: str) -> dict[str, int]:
    phases: dict[str, int] = {}
    cur = None
    for line in text.splitlines(keepends=True):
        m = re.match(r"^## Phase (\w+)", line)
        if m:
            cur = m.group(1)
            phases[cur] = 0
        if cur:
            phases[cur] += 1
    return phases


class ApplyStageValidationContractTest(unittest.TestCase):
    """Each invalid-artifact rule must be documented in checkpoint-patterns.md."""

    def setUp(self) -> None:
        self.cp_text = read(CHECKPOINT_PATTERNS)
        self.apply_section = _apply_section(self.cp_text)

    def test_apply_stage_section_exists(self) -> None:
        self.assertIn(
            "## Apply-stage Artifact Validation",
            self.cp_text,
            "checkpoint-patterns.md must have an 'Apply-stage Artifact Validation' section",
        )

    def test_absent_rule_present(self) -> None:
        self.assertIn(
            "File absent",
            self.apply_section,
            "Apply-stage section must document the 'File absent' rule",
        )

    def test_empty_rule_present(self) -> None:
        self.assertIn(
            "File empty",
            self.apply_section,
            "Apply-stage section must document the 'File empty' rule",
        )

    def test_missing_al_dev_header_rule_present(self) -> None:
        # The rule references the literal header string
        self.assertIn(
            "# AL Dev",
            self.apply_section,
            "Apply-stage section must document the 'Missing # AL Dev header' rule",
        )

    def test_count_mismatch_rule_present(self) -> None:
        # The rule mentions catalog rows vs disk agents
        self.assertTrue(
            "CATALOG_ROWS" in self.apply_section
            or "catalog" in self.apply_section.lower(),
            "Apply-stage section must document the catalog count mismatch rule",
        )

    def test_per_surface_independence_rule_present(self) -> None:
        # The per-surface independence rule must appear
        self.assertTrue(
            "Per-surface Independence" in self.apply_section
            or "per-surface" in self.apply_section.lower()
            or "independent" in self.apply_section.lower(),
            "Apply-stage section must document the per-surface independence rule",
        )

    def test_all_invalid_stop_rule_present(self) -> None:
        # The all-surfaces-invalid stop message must be documented
        self.assertIn(
            "No valid update artifacts found",
            self.apply_section,
            "Apply-stage section must include the all-invalid stop message",
        )


class ApplySkillPhaseLengthTest(unittest.TestCase):
    """Phase 1 and Phase 3 must stay within their prescribed line-count budgets."""

    def setUp(self) -> None:
        self.phase_counts = _phase_line_counts(read(APPLY_SKILL))

    def test_phase_1_within_budget(self) -> None:
        count = self.phase_counts.get("1", 0)
        self.assertLessEqual(
            count,
            22,
            f"Phase 1 must be ≤22 lines, got {count}",
        )

    def test_phase_3_within_budget(self) -> None:
        count = self.phase_counts.get("3", 0)
        self.assertLessEqual(
            count,
            28,
            f"Phase 3 must be ≤28 lines, got {count}",
        )


class ApplySkillCallsiteTest(unittest.TestCase):
    """SKILL.md must reference checkpoint-patterns.md for parsing and validation."""

    def setUp(self) -> None:
        self.skill_text = read(APPLY_SKILL)

    def test_phase_1_references_checkpoint_patterns(self) -> None:
        # Phase 1 must cite checkpoint-patterns.md for the read pattern
        self.assertIn(
            "checkpoint-patterns.md",
            self.skill_text,
            "SKILL.md Phase 1 must reference checkpoint-patterns.md",
        )

    def test_phase_3_references_apply_stage_section(self) -> None:
        # Phase 3 must reference the shared validation section
        self.assertIn(
            "Apply-stage artifact validation",
            self.skill_text,
            "SKILL.md Phase 3 must reference the 'Apply-stage artifact validation' section",
        )

    def test_phase_3_states_per_surface_independence(self) -> None:
        # The per-surface independence rule must appear in SKILL.md Phase 3 too
        self.assertIn(
            "independently",
            self.skill_text,
            "SKILL.md must state that surfaces are validated independently",
        )

    def test_phase_3_no_inline_validation_table(self) -> None:
        # The inline table should no longer exist in the SKILL.md
        self.assertNotIn(
            "| File absent |",
            self.skill_text,
            "SKILL.md Phase 3 must not contain the inline validation table (it should be in checkpoint-patterns.md)",
        )


if __name__ == "__main__":
    unittest.main()
