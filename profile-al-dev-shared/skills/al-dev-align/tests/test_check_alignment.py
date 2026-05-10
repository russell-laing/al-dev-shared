"""Tests for check-alignment.py"""
import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "check-alignment.py"
spec = importlib.util.spec_from_file_location("check_alignment", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

strip_frontmatter = mod.strip_frontmatter
is_in_code_fence = mod.is_in_code_fence


class TestStripFrontmatter:
    def test_file_with_frontmatter_preserves_line_count(self):
        lines = ["---\n", "name: foo\n", "---\n", "Body line\n"]
        result = strip_frontmatter(lines)
        assert len(result) == 4

    def test_file_with_frontmatter_replaces_fm_lines_with_blank(self):
        lines = ["---\n", "name: foo\n", "---\n", "Body line\n"]
        result = strip_frontmatter(lines)
        assert result[0] == ""
        assert result[1] == ""
        assert result[2] == ""
        assert result[3] == "Body line\n"

    def test_file_without_frontmatter_returns_unchanged(self):
        lines = ["# Title\n", "Some content\n"]
        result = strip_frontmatter(lines)
        assert result == lines

    def test_body_after_frontmatter_is_preserved(self):
        lines = ["---\n", "key: val\n", "---\n", "line1\n", "line2\n"]
        result = strip_frontmatter(lines)
        assert result[3] == "line1\n"
        assert result[4] == "line2\n"

    def test_file_starting_with_dashes_not_frontmatter(self):
        lines = ["-- not frontmatter\n", "body\n"]
        result = strip_frontmatter(lines)
        assert result == lines


class TestIsInCodeFence:
    def test_line_before_fence_is_not_in_fence(self):
        lines = ["normal\n", "```\n", "code\n", "```\n"]
        assert not is_in_code_fence(0, lines)

    def test_line_inside_fence_is_in_fence(self):
        lines = ["normal\n", "```\n", "code\n", "```\n"]
        assert is_in_code_fence(2, lines)

    def test_line_after_closed_fence_is_not_in_fence(self):
        lines = ["```\n", "code\n", "```\n", "normal\n"]
        assert not is_in_code_fence(3, lines)

    def test_second_fence_block(self):
        lines = ["```\n", "code\n", "```\n", "normal\n", "```\n", "more\n", "```\n"]
        assert is_in_code_fence(5, lines)
        assert not is_in_code_fence(3, lines)

    def test_opening_fence_line_itself_is_not_inside(self):
        lines = ["```\n", "code\n", "```\n"]
        assert not is_in_code_fence(0, lines)
