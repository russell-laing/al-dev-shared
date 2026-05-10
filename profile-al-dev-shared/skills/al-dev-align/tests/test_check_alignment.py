"""Tests for check-alignment.py"""
import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "check-alignment.py"
spec = importlib.util.spec_from_file_location("check_alignment", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

strip_frontmatter = mod.strip_frontmatter
is_in_code_fence = mod.is_in_code_fence
parse_forbidden_tokens = mod.parse_forbidden_tokens


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

    def test_empty_list_returns_empty(self):
        result = strip_frontmatter([])
        assert result == []

    def test_unclosed_frontmatter_returns_unchanged(self):
        lines = ["---\n", "key: val\n", "# Never closed\n"]
        result = strip_frontmatter(lines)
        assert result == lines

    def test_file_with_only_opening_dash_returns_unchanged(self):
        lines = ["---\n"]
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


SAMPLE_HARNESS_CONCEPTS = """\
| Concept | Description | Claude Code | Copilot CLI |
|---|---|---|---|
| **project instructions file** | The file | `CLAUDE.md` | `AGENTS.md` |
| **harness settings file** | Settings | `~/.claude/settings.json` | `~/.copilot/settings.json` |
| **USER_GATE** | Blocking gate | `AskUserQuestion` tool | `ask_user` tool |
| **explore agent** | Fast agent | `subagent_type: Explore` | `agent_type: "explore" in task tool` |
| **restart the agent** | New session | "Restart Claude Code" | "start a new Copilot CLI session" |
| **MCP: al-mcp-server** | AL symbols | `mcp__plugin_prefix_al-mcp-server__<tool>` | `al-mcp-server-<tool>` |
"""


class TestParseForbiddenTokens:
    def test_includes_hardcoded_tokens(self):
        tokens = parse_forbidden_tokens(SAMPLE_HARNESS_CONCEPTS)
        assert "~/.claude" in tokens
        assert "~/claude-configs" in tokens
        assert "~/.copilot" in tokens
        assert "~/copilot-configs" in tokens
        assert "CLAUDE_CODE" in tokens

    def test_extracts_claude_md(self):
        tokens = parse_forbidden_tokens(SAMPLE_HARNESS_CONCEPTS)
        assert "CLAUDE.md" in tokens

    def test_extracts_agents_md(self):
        tokens = parse_forbidden_tokens(SAMPLE_HARNESS_CONCEPTS)
        assert "AGENTS.md" in tokens

    def test_extracts_tool_name_without_tool_suffix(self):
        tokens = parse_forbidden_tokens(SAMPLE_HARNESS_CONCEPTS)
        assert "AskUserQuestion" in tokens
        assert "ask_user" in tokens

    def test_strips_in_task_tool_suffix(self):
        tokens = parse_forbidden_tokens(SAMPLE_HARNESS_CONCEPTS)
        # "agent_type: "explore" in task tool" -> "agent_type: explore"
        assert any("agent_type" in t for t in tokens)

    def test_extracts_mcp_prefix_before_angle_bracket(self):
        tokens = parse_forbidden_tokens(SAMPLE_HARNESS_CONCEPTS)
        assert "mcp__plugin_prefix_al-mcp-server__" in tokens

    def test_extracts_copilot_mcp_prefix_before_angle_bracket(self):
        tokens = parse_forbidden_tokens(SAMPLE_HARNESS_CONCEPTS)
        assert "al-mcp-server-" in tokens

    def test_empty_table_returns_only_hardcoded(self):
        tokens = parse_forbidden_tokens("no table here")
        assert tokens == mod.HARDCODED_TOKENS
