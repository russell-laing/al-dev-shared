#!/usr/bin/env python3
"""
Regression tests for validate-knowledge-quality.py false positive fixes.

Tests ensure that known false positive patterns continue to be skipped.
"""

import re
from pathlib import Path

# Import validator functions (assuming same directory)
import sys
import importlib.util

script_dir = Path(__file__).parent
spec = importlib.util.spec_from_file_location(
    "validate_knowledge_quality",
    script_dir / "validate-knowledge-quality.py"
)
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)

find_knowledge_references = validator.find_knowledge_references
has_emoji_or_checkmark = validator.has_emoji_or_checkmark
check_thin_sections = validator.check_thin_sections
check_code_implication = validator.check_code_implication


def test_dead_ref_path_resolution():
    """Verify DEAD-REF false positives from path duplication are fixed."""
    content = """
# Some Section

See knowledge/proportional-planning.md for more info.
"""
    refs = find_knowledge_references(content)
    # Should return just "proportional-planning.md", not "knowledge/proportional-planning.md"
    assert refs[0][0] == "proportional-planning.md", f"Got {refs[0][0]}"
    print("✓ DEAD-REF path resolution test passed")


def test_emoji_detection():
    """Verify emoji/checkmark detection works."""
    assert has_emoji_or_checkmark("❌ BAD: Example") == True
    assert has_emoji_or_checkmark("✅ GOOD: Example") == True
    assert has_emoji_or_checkmark("🔴 COMPLEX") == True
    assert has_emoji_or_checkmark("Plain text heading") == False
    print("✓ Emoji detection test passed")


def test_no_code_emoji_skip():
    """Verify [NO-CODE] is skipped for emoji headers."""
    # Section with emoji header should not be flagged [NO-CODE]
    sections = [
        ("❌ BAD: SIMPLE Feature with 946-line Plan", 3, 0, "Long explanation here.\nWith multiple lines.\nBut no code block."),
    ]
    issues = check_code_implication("test.md", sections)
    # Should be empty because emoji header is skipped
    assert len(issues) == 0, f"Got issues: {issues}"
    print("✓ NO-CODE emoji skip test passed")


def test_thin_goal_section_skip():
    """Verify [THIN] is skipped for 'Goal' sections."""
    # Goal section with 1 line should not be flagged [THIN]
    sections = [
        ("Goal", 3, 0, "Write minimal code to make test pass."),
    ]
    issues = check_thin_sections("test.md", sections)
    # Should be empty because "Goal" section is skipped
    assert len(issues) == 0, f"Got issues: {issues}"
    print("✓ THIN goal section skip test passed")


def test_align_skill_mentions_generated_projection_surface():
    text = Path(".claude/skills/validate-plugin-neutrality/SKILL.md").read_text(encoding="utf-8")
    assert "profile-al-dev-shared/generated/agents/" in text
    assert "repo-local `.claude` boundary issues" in text
    review_text = Path(".claude/skills/review-skill-map/SKILL.md").read_text(encoding="utf-8")
    assert "generated/agents" in review_text
    print("✓ Local projection-awareness skill text test passed")


if __name__ == "__main__":
    test_dead_ref_path_resolution()
    test_emoji_detection()
    test_no_code_emoji_skip()
    test_thin_goal_section_skip()
    test_align_skill_mentions_generated_projection_surface()
    print("\n✅ All regression tests passed!")
