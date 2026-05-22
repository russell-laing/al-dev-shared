"""Tests for check-alignment.py"""
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "check-alignment.py"
SCRIPT_PATH = str(SCRIPT)
spec = importlib.util.spec_from_file_location("check_alignment", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

strip_frontmatter = mod.strip_frontmatter
is_in_code_fence = mod.is_in_code_fence
parse_forbidden_tokens = mod.parse_forbidden_tokens
_extract_token = mod._extract_token
_iter_vocabulary_table_rows = mod._iter_vocabulary_table_rows
classify_hit = mod.classify_hit
scan_file = mod.scan_file
parse_concepts_from_harness_md = mod.parse_concepts_from_harness_md
parse_mapping_table = mod.parse_mapping_table
compute_coverage_gaps = mod.compute_coverage_gaps


def test_validate_repo_local_claude_boundary_requires_generated_projection_note(tmp_path):
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    (repo_root / "AGENTS.md").write_text(
        "# AGENTS\n\n"
        ".claude/agents/ and .claude/skills/ are repo-local Claude maintainer tooling.\n"
    )
    (repo_root / "CLAUDE.md").write_text(
        "# CLAUDE\n\n"
        ".claude/agents/ and .claude/skills/ are repo-local Claude maintainer tooling.\n"
    )
    generated_root = repo_root / "profile-al-dev-shared" / "generated" / "agents"
    generated_root.mkdir(parents=True)
    (generated_root / "README.md").write_text("# Generated Agent Projections\n")
    issues = mod.validate_repo_local_claude_boundary(repo_root)
    assert any("profile-al-dev-shared/generated/agents/" in issue["error"] for issue in issues)


def test_validate_repo_local_claude_boundary_accepts_three_way_classification(tmp_path):
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    (repo_root / "AGENTS.md").write_text(
        "# AGENTS\n\n"
        "profile-al-dev-shared/ is shared source.\n"
        "profile-al-dev-shared/generated/agents/ is generated projection output.\n"
        ".claude/agents/ and .claude/skills/ are repo-local Claude maintainer tooling.\n"
    )
    (repo_root / "CLAUDE.md").write_text(
        "# CLAUDE\n\n"
        "profile-al-dev-shared/ is shared source.\n"
        "profile-al-dev-shared/generated/agents/ is generated projection output.\n"
        ".claude/agents/ and .claude/skills/ are repo-local Claude maintainer tooling.\n"
    )
    generated_root = repo_root / "profile-al-dev-shared" / "generated" / "agents"
    generated_root.mkdir(parents=True)
    (generated_root / "README.md").write_text(
        "# Generated Agent Projections\n\n"
        "This directory contains generated harness-native agent artifacts.\n\n"
        "- `claude/` contains generated Claude Markdown manifests.\n"
        "- `copilot/` contains generated Copilot Markdown manifests.\n"
        "- `codex/` contains generated Codex TOML manifests.\n\n"
        "These files are derived from `profile-al-dev-shared/agents/*.md` plus\n"
        "projection policy metadata. Do not hand-edit them.\n"
    )
    issues = mod.validate_repo_local_claude_boundary(repo_root)
    assert issues == []


def test_projection_scan_ignores_repo_local_claude_tree(tmp_path):
    repo_root = tmp_path / "repo"
    plugin_root = repo_root / "profile-al-dev-shared"
    (repo_root / ".claude" / "agents").mkdir(parents=True)
    (plugin_root / "generated" / "agents" / "claude").mkdir(parents=True)
    (repo_root / ".claude" / "agents" / "local-only.md").write_text("local")
    paths = mod.classify_projection_paths(repo_root, plugin_root)
    assert ".claude/agents/local-only.md" not in paths["shared_source"]
    assert ".claude/agents/local-only.md" not in paths["generated_projection"]
    assert ".claude/agents/local-only.md" in paths["repo_local_maintainer_tooling"]


def test_projection_validation_fails_when_generated_projection_missing(tmp_path):
    plugin_root = tmp_path / "profile-al-dev-shared"
    (plugin_root / "agents").mkdir(parents=True)
    (plugin_root / "agents" / "al-dev-interview.md").write_text(
        "---\ndescription: test\ntools: [\"Read\"]\n---\n# Agent\n"
    )
    issues = mod.validate_projection_outputs(plugin_root)
    assert any("generated/agents/claude/al-dev-interview.md" in issue["error"] for issue in issues)


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

    def test_tilde_fence_detected_as_code_block(self):
        lines = ["~~~\n", "code\n", "~~~\n"]
        assert is_in_code_fence(1, lines)


class TestExtractToken:
    def test_strips_backticks(self):
        assert _extract_token("`CLAUDE.md`") == "CLAUDE.md"

    def test_strips_bold_markers(self):
        assert _extract_token("**bold**") == "bold"

    def test_strips_tool_suffix(self):
        assert _extract_token("ask_user tool") == "ask_user"

    def test_strips_in_task_tool_suffix(self):
        assert _extract_token("agent_type: explore in task tool") == "agent_type: explore"

    def test_truncates_at_in_middle(self):
        assert _extract_token("something in production") == "something"

    def test_truncates_before_angle_bracket(self):
        assert _extract_token("al-mcp-server-<tool>") == "al-mcp-server-"

    def test_strips_curly_quotes(self):
        assert _extract_token("\u201cquoted\u201d") == "quoted"

    def test_short_result_returns_none(self):
        assert _extract_token("`a`") is None

    def test_empty_returns_none(self):
        assert _extract_token("") is None


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
        assert "agent_type: explore" in tokens

    def test_extracts_mcp_prefix_before_angle_bracket(self):
        tokens = parse_forbidden_tokens(SAMPLE_HARNESS_CONCEPTS)
        assert "mcp__plugin_prefix_al-mcp-server__" in tokens

    def test_extracts_copilot_mcp_prefix_before_angle_bracket(self):
        tokens = parse_forbidden_tokens(SAMPLE_HARNESS_CONCEPTS)
        assert "al-mcp-server-" in tokens

    def test_empty_table_returns_only_hardcoded(self):
        tokens = parse_forbidden_tokens("no table here")
        assert tokens == mod.HARDCODED_TOKENS


class TestClassifyHit:
    def test_prose_line_is_error_and_autofixable(self):
        lines = ["Use CLAUDE.md as your guide.\n"]
        result = classify_hit(0, lines)
        assert result["context_type"] == "prose"
        assert result["severity"] == "error"
        assert result["autofixable"] is True

    def test_line_inside_code_fence_is_warning_not_autofixable(self):
        lines = ["```\n", "use CLAUDE.md here\n", "```\n"]
        result = classify_hit(1, lines)
        assert result["context_type"] == "code_block"
        assert result["severity"] == "warning"
        assert result["autofixable"] is False

    def test_indented_line_is_code_block(self):
        lines = ["    CLAUDE.md is set here\n"]
        result = classify_hit(0, lines)
        assert result["context_type"] == "code_block"
        assert result["autofixable"] is False

    def test_prohibition_rule_line(self):
        lines = ["Never use CLAUDE.md directly.\n"]
        result = classify_hit(0, lines)
        assert result["context_type"] == "prohibition_rule"
        assert result["severity"] == "manual_review"
        assert result["autofixable"] is False

    def test_do_not_line(self):
        lines = ["Do not reference CLAUDE.md.\n"]
        result = classify_hit(0, lines)
        assert result["context_type"] == "prohibition_rule"

    def test_must_not_line(self):
        lines = ["You must not use CLAUDE.md.\n"]
        result = classify_hit(0, lines)
        assert result["context_type"] == "prohibition_rule"

    def test_dont_contraction_line(self):
        lines = ["Don't use CLAUDE.md.\n"]
        result = classify_hit(0, lines)
        assert result["context_type"] == "prohibition_rule"

    def test_dont_unicode_apostrophe_line(self):
        lines = ["Don\u2019t use CLAUDE.md.\n"]
        result = classify_hit(0, lines)
        assert result["context_type"] == "prohibition_rule"

    def test_line_inside_tilde_fence_is_code_block(self):
        lines = ["~~~\n", "use CLAUDE.md here\n", "~~~\n"]
        result = classify_hit(1, lines)
        assert result["context_type"] == "code_block"


class TestScanFile:
    def test_finds_token_in_prose(self):
        lines = ["---\n", "name: test\n", "---\n", "Open CLAUDE.md to configure.\n"]
        hits = scan_file("skills/foo/SKILL.md", lines, {"CLAUDE.md"})
        assert len(hits) == 1
        assert hits[0]["token"] == "CLAUDE.md"
        assert hits[0]["line"] == 4  # 1-indexed; frontmatter preserved as blanks
        assert hits[0]["file"] == "skills/foo/SKILL.md"

    def test_returns_empty_for_clean_file(self):
        lines = ["---\n", "name: test\n", "---\n", "Use the project instructions file.\n"]
        hits = scan_file("skills/foo/SKILL.md", lines, {"CLAUDE.md"})
        assert hits == []

    def test_hit_in_code_fence_has_warning_severity(self):
        lines = ["```\n", "cp CLAUDE.md dest\n", "```\n"]
        hits = scan_file("agents/foo.md", lines, {"CLAUDE.md"})
        assert len(hits) == 1
        assert hits[0]["severity"] == "warning"
        assert hits[0]["autofixable"] is False

    def test_multiple_tokens_on_same_line_produces_multiple_hits(self):
        lines = ["Use CLAUDE.md and AGENTS.md together.\n"]
        hits = scan_file("skills/x/SKILL.md", lines, {"CLAUDE.md", "AGENTS.md"})
        assert len(hits) == 2

    def test_context_field_contains_token(self):
        lines = ["Open CLAUDE.md now.\n"]
        hits = scan_file("skills/x/SKILL.md", lines, {"CLAUDE.md"})
        assert "CLAUDE.md" in hits[0]["context"]

    def test_context_type_field_is_present(self):
        lines = ["Reference CLAUDE.md here.\n"]
        hits = scan_file("skills/x/SKILL.md", lines, {"CLAUDE.md"})
        assert "context_type" in hits[0]

    def test_same_token_twice_on_line_reports_both(self):
        lines = ["Use CLAUDE.md and also CLAUDE.md here\n"]
        hits = scan_file("f.md", lines, {"CLAUDE.md"})
        assert len(hits) == 2
        assert all(h["token"] == "CLAUDE.md" for h in hits)


HARNESS_CONCEPTS_FULL = """\
## Generic Concept Vocabulary

| Concept | Description | Claude Code | Copilot CLI |
|---|---|---|---|
| **project instructions file** | File desc | `CLAUDE.md` | `AGENTS.md` |
| **USER_GATE** | Blocking gate | `AskUserQuestion` tool | `ask_user` tool |
| **explore agent** | Fast agent | `subagent_type: Explore` | `agent_type: "explore"` in task tool |
"""

CLAUDE_MD_WITH_MAPPING = """\
# Project Instructions

Some intro text.

## Harness Mapping

| Concept | Claude Code Value |
|---|---|
| **project instructions file** | `CLAUDE.md` |
| **USER_GATE** | `AskUserQuestion` tool |

## Other Section

More content.
"""

AGENTS_MD_WITH_MAPPING = """\
## Harness Mapping

| Concept | Copilot CLI Value |
|---|---|
| **project instructions file** | `AGENTS.md` |

## Next Section
"""


class TestParseConceptsFromHarnessMd:
    def test_extracts_concept_names(self):
        concepts = parse_concepts_from_harness_md(HARNESS_CONCEPTS_FULL)
        assert "project instructions file" in concepts
        assert "USER_GATE" in concepts
        assert "explore agent" in concepts

    def test_strips_bold_markers(self):
        concepts = parse_concepts_from_harness_md(HARNESS_CONCEPTS_FULL)
        assert "**project instructions file**" not in concepts

    def test_returns_empty_set_for_no_table(self):
        concepts = parse_concepts_from_harness_md("No table here.")
        assert concepts == set()


class TestParseMappingTable:
    def test_extracts_concepts_from_harness_mapping_section(self):
        concepts = parse_mapping_table(CLAUDE_MD_WITH_MAPPING)
        assert "project instructions file" in concepts
        assert "USER_GATE" in concepts

    def test_stops_at_next_heading(self):
        concepts = parse_mapping_table(CLAUDE_MD_WITH_MAPPING)
        assert "Other Section" not in concepts

    def test_skips_separator_rows(self):
        concepts = parse_mapping_table(CLAUDE_MD_WITH_MAPPING)
        assert "---" not in concepts

    def test_skips_header_row(self):
        concepts = parse_mapping_table(CLAUDE_MD_WITH_MAPPING)
        assert "Concept" not in concepts

    def test_strips_bold_and_backticks(self):
        concepts = parse_mapping_table(CLAUDE_MD_WITH_MAPPING)
        assert "**project instructions file**" not in concepts

    def test_returns_empty_set_when_no_section(self):
        concepts = parse_mapping_table("# No mapping here\nContent.\n")
        assert concepts == set()

    def test_extracts_from_agents_md_format(self):
        concepts = parse_mapping_table(AGENTS_MD_WITH_MAPPING)
        assert "project instructions file" in concepts
        assert "USER_GATE" not in concepts  # not present in AGENTS_MD_WITH_MAPPING fixture


class TestComputeCoverageGaps:
    def test_missing_concept_appears_in_missing_list(self):
        concepts = {"project instructions file", "USER_GATE"}
        claude = {"project instructions file"}
        copilot = {"project instructions file"}
        missing, orphaned = compute_coverage_gaps(concepts, claude, copilot)
        assert any(m["concept"] == "USER_GATE" for m in missing)

    def test_missing_in_field_lists_correct_harnesses(self):
        concepts = {"USER_GATE"}
        claude = set()
        copilot = {"USER_GATE"}
        missing, _ = compute_coverage_gaps(concepts, claude, copilot)
        gap = next(m for m in missing if m["concept"] == "USER_GATE")
        assert gap["missing_in"] == ["claude"]
        assert "copilot" not in gap["missing_in"]

    def test_no_gaps_when_all_covered(self):
        concepts = {"project instructions file"}
        claude = {"project instructions file"}
        copilot = {"project instructions file"}
        missing, orphaned = compute_coverage_gaps(concepts, claude, copilot)
        assert missing == []
        assert orphaned == []

    def test_orphaned_row_not_in_concepts(self):
        concepts = {"USER_GATE"}
        claude = {"USER_GATE", "old concept"}
        copilot = {"USER_GATE"}
        _, orphaned = compute_coverage_gaps(concepts, claude, copilot)
        assert any(o["concept"] == "old concept" for o in orphaned)
        orphan = next(o for o in orphaned if o["concept"] == "old concept")
        assert "claude" in orphan["present_in"]

    def test_missing_in_both_harnesses(self):
        concepts = {"USER_GATE"}
        missing, _ = compute_coverage_gaps(concepts, set(), set())
        assert missing[0]["missing_in"] == ["claude", "copilot"]

    def test_end_to_end_with_fixtures(self):
        """Integration: concepts vs both harness mapping fixtures."""
        concepts = parse_concepts_from_harness_md(HARNESS_CONCEPTS_FULL)
        claude_mapping = parse_mapping_table(CLAUDE_MD_WITH_MAPPING)
        copilot_mapping = parse_mapping_table(AGENTS_MD_WITH_MAPPING)
        missing, orphaned = compute_coverage_gaps(concepts, claude_mapping, copilot_mapping)
        # explore agent is in vocabulary but missing from both mapping fixtures
        assert any(m["concept"] == "explore agent" for m in missing)
        assert orphaned == []


class TestCLI:
    def _run(self, args: list[str], *, plugin_root: str = "") -> subprocess.CompletedProcess:
        env = os.environ.copy()
        if plugin_root:
            env["AL_DEV_SHARED_PLUGIN_ROOT"] = plugin_root
        return subprocess.run(
            [sys.executable, SCRIPT_PATH, *args],
            capture_output=True,
            text=True,
            env=env,
        )

    def test_exit_2_when_harness_concepts_missing(self, tmp_path):
        result = self._run(
            ["--claude-profile", str(tmp_path), "--copilot-profile", str(tmp_path)],
            plugin_root=str(tmp_path),
        )
        assert result.returncode == 2

    def test_exit_0_when_all_clean(self, tmp_path):
        # Set up a minimal valid plugin root
        skills_dir = tmp_path / "skills" / "test-skill"
        skills_dir.mkdir(parents=True)
        (skills_dir / "SKILL.md").write_text("---\nname: test\n---\nUse the project instructions file.\n")
        (tmp_path / "knowledge").mkdir()
        harness_concepts = (
            "| Concept | Description | Claude Code | Copilot CLI |\n"
            "|---|---|---|---|\n"
            "| **project instructions file** | desc | `CLAUDE.md` | `AGENTS.md` |\n"
        )
        (tmp_path / "knowledge" / "harness-concepts.md").write_text(harness_concepts)
        mapping_table = (
            "## Harness Mapping\n\n"
            "| Concept | Value |\n"
            "|---|---|\n"
            "| **project instructions file** | `CLAUDE.md` |\n\n"
            "## End\n"
        )
        (tmp_path / "CLAUDE.md").write_text(mapping_table)
        (tmp_path / "AGENTS.md").write_text(mapping_table)
        result = self._run(
            ["--claude-profile", str(tmp_path), "--copilot-profile", str(tmp_path)],
            plugin_root=str(tmp_path),
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["forbidden_tokens"] == []
        assert data["missing_mappings"] == []
        assert data["orphaned_mappings"] == []

    def test_exit_1_enforce_when_issues_found(self, tmp_path):
        skills_dir = tmp_path / "skills" / "bad-skill"
        skills_dir.mkdir(parents=True)
        (skills_dir / "SKILL.md").write_text("---\nname: bad\n---\nOpen CLAUDE.md here.\n")
        (tmp_path / "knowledge").mkdir()
        harness_concepts = (
            "| Concept | Description | Claude Code | Copilot CLI |\n"
            "|---|---|---|---|\n"
            "| **project instructions file** | desc | `CLAUDE.md` | `AGENTS.md` |\n"
        )
        (tmp_path / "knowledge" / "harness-concepts.md").write_text(harness_concepts)
        (tmp_path / "CLAUDE.md").write_text("## Harness Mapping\n\n| Concept | Value |\n|---|---|\n| **project instructions file** | x |\n")
        (tmp_path / "AGENTS.md").write_text("## Harness Mapping\n\n| Concept | Value |\n|---|---|\n| **project instructions file** | x |\n")
        result = self._run(
            ["--mode", "enforce", "--claude-profile", str(tmp_path), "--copilot-profile", str(tmp_path)],
            plugin_root=str(tmp_path),
        )
        assert result.returncode == 1
        data = json.loads(result.stdout)
        assert len(data["forbidden_tokens"]) >= 1

    def test_exit_0_advisory_even_with_issues(self, tmp_path):
        skills_dir = tmp_path / "skills" / "bad-skill"
        skills_dir.mkdir(parents=True)
        (skills_dir / "SKILL.md").write_text("---\nname: bad\n---\nOpen CLAUDE.md here.\n")
        (tmp_path / "knowledge").mkdir()
        harness_concepts = (
            "| Concept | Description | Claude Code | Copilot CLI |\n"
            "|---|---|---|---|\n"
            "| **project instructions file** | desc | `CLAUDE.md` | `AGENTS.md` |\n"
        )
        (tmp_path / "knowledge" / "harness-concepts.md").write_text(harness_concepts)
        (tmp_path / "CLAUDE.md").write_text("## Harness Mapping\n\n| Concept | Value |\n|---|---|\n| **project instructions file** | x |\n")
        (tmp_path / "AGENTS.md").write_text("## Harness Mapping\n\n| Concept | Value |\n|---|---|\n| **project instructions file** | x |\n")
        result = self._run(
            ["--mode", "advisory", "--claude-profile", str(tmp_path), "--copilot-profile", str(tmp_path)],
            plugin_root=str(tmp_path),
        )
        assert result.returncode == 0

    def test_output_is_valid_json(self, tmp_path):
        (tmp_path / "knowledge").mkdir()
        (tmp_path / "knowledge" / "harness-concepts.md").write_text(
            "| Concept | Description | Claude Code | Copilot CLI |\n|---|---|---|---|\n"
        )
        (tmp_path / "CLAUDE.md").write_text("")
        (tmp_path / "AGENTS.md").write_text("")
        result = self._run(
            ["--claude-profile", str(tmp_path), "--copilot-profile", str(tmp_path)],
            plugin_root=str(tmp_path),
        )
        data = json.loads(result.stdout)
        assert "forbidden_tokens" in data
        assert "missing_mappings" in data
        assert "orphaned_mappings" in data


class TestSkillFile:
    # SKILL.md was moved to .claude/skills/ (project-local maintenance tool)
    SKILL_MD = Path(__file__).parent.parent.parent.parent.parent / ".claude" / "skills" / "al-dev-align" / "SKILL.md"

    def test_skill_md_exists(self):
        assert self.SKILL_MD.exists(), "SKILL.md must exist"

    def test_skill_md_has_name_frontmatter(self):
        text = self.SKILL_MD.read_text()
        assert "name: al-dev-align" in text

    def test_skill_md_has_description(self):
        text = self.SKILL_MD.read_text()
        assert "description:" in text

    def test_skill_md_references_plugin_root(self):
        text = self.SKILL_MD.read_text()
        assert "AL_DEV_SHARED_PLUGIN_ROOT" in text, \
            "SKILL.md must reference AL_DEV_SHARED_PLUGIN_ROOT to locate the script"

    def test_skill_md_has_user_gate(self):
        text = self.SKILL_MD.read_text()
        assert "USER_GATE" in text, \
            "SKILL.md must include a USER_GATE before auto-fixing"

    def test_skill_md_has_all_seven_steps(self):
        text = self.SKILL_MD.read_text()
        for i in range(1, 8):
            assert f"## Step {i}" in text, f"SKILL.md missing Step {i}"

    def test_skill_md_captures_json_output(self):
        text = self.SKILL_MD.read_text()
        assert "ALIGN_OUTPUT" in text, \
            "SKILL.md must capture JSON output in a variable (ALIGN_OUTPUT)"
