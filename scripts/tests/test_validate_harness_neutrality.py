from pathlib import Path

from scripts.validate_harness_neutrality import scan_paths


def test_flags_shared_surface_leakage_and_ignores_allowlisted_mapping_docs(tmp_path: Path) -> None:
    plugin_root = tmp_path / "profile-al-dev-shared"
    knowledge = plugin_root / "knowledge"
    skills = plugin_root / "skills" / "demo"

    knowledge.mkdir(parents=True)
    skills.mkdir(parents=True)

    (skills / "SKILL.md").write_text("open claude code in: /tmp\n", encoding="utf-8")
    (knowledge / "harness-concepts.md").write_text(
        'agent_type: "al-dev-shared:reviewer"\nAskUserQuestion | ask_user\n',
        encoding="utf-8",
    )
    (knowledge / "review-panel-pattern.md").write_text(
        'Agent(\n  subagent_type: "al-dev-shared:al-dev-security-reviewer"\n)\n',
        encoding="utf-8",
    )

    findings = scan_paths(plugin_root)
    findings_by_path = {item.path: item for item in findings}

    assert "skills/demo/SKILL.md" in findings_by_path
    assert "knowledge/harness-concepts.md" not in findings_by_path
    assert "knowledge/review-panel-pattern.md" in findings_by_path


def test_flags_harness_native_copilot_dispatch_syntax_for_any_agent_type(tmp_path: Path) -> None:
    plugin_root = tmp_path / "profile-al-dev-shared"
    skills = plugin_root / "skills" / "demo"

    skills.mkdir(parents=True)
    (skills / "SKILL.md").write_text(
        "Dispatch with task(agent_type: al-dev-shared:custom-reviewer)\n",
        encoding="utf-8",
    )

    findings = scan_paths(plugin_root)

    assert any(
        item.path == "skills/demo/SKILL.md" and item.rule == "Copilot dispatch token"
        for item in findings
    )


def test_flags_capitalized_copilot_session_wording(tmp_path: Path) -> None:
    plugin_root = tmp_path / "profile-al-dev-shared"
    markdown = plugin_root / "markdown"

    markdown.mkdir(parents=True)
    (markdown / "guide.md").write_text("Start a new Copilot CLI session before continuing.\n", encoding="utf-8")

    findings = scan_paths(plugin_root)

    assert any(
        item.path == "markdown/guide.md" and item.rule == "Copilot session wording"
        for item in findings
    )


def test_scans_authored_roots_but_not_unscanned_top_level_projection_or_archive_roots(
    tmp_path: Path,
) -> None:
    plugin_root = tmp_path / "profile-al-dev-shared"
    skills = plugin_root / "skills" / "demo"
    generated = plugin_root / "generated" / "agents" / "copilot"
    archived = plugin_root / "archived" / "knowledge"
    markdown = plugin_root / "markdown"

    skills.mkdir(parents=True)
    generated.mkdir(parents=True)
    archived.mkdir(parents=True)
    markdown.mkdir(parents=True)

    (skills / "SKILL.md").write_text("Restart Claude Code to continue.\n", encoding="utf-8")
    (generated / "example.md").write_text("Open Claude Code in: /tmp\n", encoding="utf-8")
    (archived / "example.yaml").write_text('agent_type: "al-dev-shared:archived"\n', encoding="utf-8")
    (markdown / "guide.md").write_text("Use ask_user to continue.\n", encoding="utf-8")

    findings = scan_paths(plugin_root)
    found_paths = {item.path for item in findings}

    assert "skills/demo/SKILL.md" in found_paths
    assert "markdown/guide.md" in found_paths
    assert "generated/agents/copilot/example.md" not in found_paths
    assert "archived/knowledge/example.yaml" not in found_paths


def test_scans_authored_files_with_uppercase_extensions(tmp_path: Path) -> None:
    plugin_root = tmp_path / "profile-al-dev-shared"
    skills = plugin_root / "skills" / "demo"
    markdown = plugin_root / "markdown"

    skills.mkdir(parents=True)
    markdown.mkdir(parents=True)

    (skills / "SKILL.MD").write_text("Restart Claude Code to continue.\n", encoding="utf-8")
    (markdown / "guide.YAML").write_text("ask_user: true\n", encoding="utf-8")

    findings = scan_paths(plugin_root)
    found_paths = {item.path for item in findings}

    assert "skills/demo/SKILL.MD" in found_paths
    assert "markdown/guide.YAML" in found_paths


def test_reports_unreadable_scanned_files_without_crashing(tmp_path: Path) -> None:
    plugin_root = tmp_path / "profile-al-dev-shared"
    markdown = plugin_root / "markdown"

    markdown.mkdir(parents=True)
    (markdown / "broken.md").write_bytes(b"\xff\xfe\x00binary")

    findings = scan_paths(plugin_root)

    assert any(
        item.path == "markdown/broken.md"
        and item.rule == "Unreadable file"
        and item.excerpt == "UnicodeDecodeError"
        for item in findings
    )
