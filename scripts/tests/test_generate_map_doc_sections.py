"""Fixture-based tests for scripts/al_dev_tools/docs/map_doc_sections.py."""
from __future__ import annotations

import inspect
import re
import shutil
import tempfile
import unittest
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = REPO_ROOT / "scripts"
for path in (REPO_ROOT, SCRIPTS_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from scripts.al_dev_tools.docs import map_doc_sections as mod
TARGET_DOCS = (
    "docs/skills_map.md",
    "docs/agent_map.md",
    "docs/plugin_graph.md",
    "docs/workflow_diagrams.md",
)


def test_map_doc_sections_keeps_public_entrypoints() -> None:
    from scripts.al_dev_tools.docs import map_doc_sections as map_mod

    assert hasattr(map_mod, "collect_inventory")
    assert hasattr(map_mod, "AgentMeta")
    assert hasattr(map_mod, "MarkerSpan")
    assert hasattr(map_mod, "build_all_sections")
    assert hasattr(map_mod, "render_skill_lifecycle")
    assert hasattr(map_mod, "generate_document_updates")


def test_split_modules_expose_expected_helpers() -> None:
    from scripts.al_dev_tools.docs import map_inventory, map_markers, map_rendering

    assert hasattr(map_inventory, "AgentMeta")
    assert hasattr(map_inventory, "Inventory")
    assert hasattr(map_inventory, "SectionSpec")
    assert hasattr(map_inventory, "collect_inventory")
    assert hasattr(map_markers, "MarkerSpan")
    assert hasattr(map_markers, "find_marker_spans")
    assert hasattr(map_markers, "replace_marked_sections")
    assert hasattr(map_rendering, "build_all_sections")
    assert hasattr(map_rendering, "render_skill_lifecycle")
    assert hasattr(map_rendering, "generate_document_updates")


def _build_fixture_repo(root: Path) -> Path:
    """Build a tiny fake profile-al-dev-shared tree plus placeholder docs."""
    repo = root / "fixture-repo"
    plugin = repo / "profile-al-dev-shared"

    for rel in (
        "skills/skill-b",
        "skills/skill-a",
        "agents",
        "knowledge",
    ):
        (plugin / rel).mkdir(parents=True, exist_ok=True)
    (repo / "docs").mkdir(parents=True, exist_ok=True)

    (plugin / "skills" / "skill-a" / "SKILL.md").write_text(
        "---\n"
        "name: skill-a\n"
        "description: Skill A\n"
        "---\n\n"
        "# Skill A\n"
        "Spawn worker to parallelize checks.\n"
        "Then run /skill-b and /skill-b again.\n"
        "If needed, run /plan to switch to an external wrapper.\n"
        "Uses knowledge/guide.md and knowledge/guide.md.\n"
        "Writes .dev/report.md.\n",
        encoding="utf-8",
    )
    (plugin / "skills" / "skill-b" / "SKILL.md").write_text(
        "---\n"
        "name: skill-b\n"
        "description: Skill B\n"
        "---\n\n"
        "# Skill B\n"
        "Refers to nothing else.\n",
        encoding="utf-8",
    )
    (plugin / "agents" / "worker.md").write_text(
        "---\n"
        "name: worker\n"
        "description: Worker agent\n"
        "model: haiku\n"
        'tools: ["Read", "Write"]\n'
        "---\n\n"
        "# Agent: worker\n"
        "Reads knowledge/guide.md and knowledge/guide.md.\n",
        encoding="utf-8",
    )
    (plugin / "agents" / "orphan.md").write_text(
        "---\n"
        "name: orphan\n"
        "description: Orphan agent\n"
        "model: sonnet\n"
        'tools: ["Read"]\n'
        "---\n\n"
        "# Agent: orphan\n"
        "No skill spawns this agent.\n",
        encoding="utf-8",
    )
    (plugin / "knowledge" / "guide.md").write_text("guide\n", encoding="utf-8")
    (plugin / "knowledge" / "workflow.md").write_text("workflow\n", encoding="utf-8")
    (repo / "docs" / "skills_map.md").write_text(
        "# Skills Map\n\n"
        "<!-- BEGIN GENERATED: skill-coverage -->\n"
        "old coverage\n"
        "<!-- END GENERATED: skill-coverage -->\n\n"
        "<!-- BEGIN GENERATED: skill-lifecycle-mermaid -->\n"
        "old lifecycle\n"
        "<!-- END GENERATED: skill-lifecycle-mermaid -->\n\n"
        "## Layer 2: Per-Skill Drill-Downs\n\n"
        "Manual prose stays outside generated sections.\n\n"
        "### /skill-a\n\n"
        "<!-- BEGIN GENERATED: skill-drilldown-skill-a -->\n"
        "old drilldown a\n"
        "<!-- END GENERATED: skill-drilldown-skill-a -->\n\n"
        "### /skill-b\n\n"
        "<!-- BEGIN GENERATED: skill-drilldown-skill-b -->\n"
        "old drilldown b\n"
        "<!-- END GENERATED: skill-drilldown-skill-b -->\n",
        encoding="utf-8",
    )
    (repo / "docs" / "agent_map.md").write_text(
        "# Agent Map\n\n"
        "<!-- BEGIN GENERATED: agent-coverage -->\n"
        "old agent coverage\n"
        "<!-- END GENERATED: agent-coverage -->\n\n"
        "<!-- BEGIN GENERATED: agent-catalog-table -->\n"
        "old content\n"
        "<!-- END GENERATED: agent-catalog-table -->\n",
        encoding="utf-8",
    )
    (repo / "docs" / "plugin_graph.md").write_text(
        "# Plugin Graph\n\n"
        "<!-- BEGIN GENERATED: plugin-dependency-mermaid -->\n"
        "old dependency\n"
        "<!-- END GENERATED: plugin-dependency-mermaid -->\n\n"
        "<!-- BEGIN GENERATED: plugin-workflow-overlays -->\n"
        "old overlays\n"
        "<!-- END GENERATED: plugin-workflow-overlays -->\n\n"
        "<!-- BEGIN GENERATED: plugin-health-callouts -->\n"
        "old health\n"
        "<!-- END GENERATED: plugin-health-callouts -->\n",
        encoding="utf-8",
    )
    (repo / "docs" / "workflow_diagrams.md").write_text(
        "# Workflow Diagrams\n\n"
        "<!-- BEGIN GENERATED: workflow-skills-agents-mermaid -->\n"
        "old skills agents\n"
        "<!-- END GENERATED: workflow-skills-agents-mermaid -->\n\n"
        "<!-- BEGIN GENERATED: workflow-knowledge-mermaid -->\n"
        "old knowledge\n"
        "<!-- END GENERATED: workflow-knowledge-mermaid -->\n",
        encoding="utf-8",
    )
    return repo


def _build_missing_internal_skill_repo(root: Path) -> Path:
    repo = _build_fixture_repo(root)
    skill_a = repo / "profile-al-dev-shared" / "skills" / "skill-a" / "SKILL.md"
    skill_a.write_text(
        skill_a.read_text(encoding="utf-8") + "Then run /skill-missing for the hidden phase.\n",
        encoding="utf-8",
    )
    return repo


def _build_bad_marker_repo(root: Path) -> Path:
    repo = _build_fixture_repo(root)
    (repo / "docs" / "agent_map.md").write_text(
        "# Agent Map\n\n"
        "<!-- BEGIN GENERATED: agent-catalog-table -->\n"
        "old content\n"
        "<!-- END GENERATED: agent-catalog-table -->\n\n"
        "<!-- BEGIN GENERATED: agent-catalog-table -->\n"
        "duplicate section\n"
        "<!-- END GENERATED: agent-catalog-table -->\n",
        encoding="utf-8",
    )
    return repo


def test_collect_inventory_discovers_deterministically_and_dedupes_refs() -> None:
    with tempfile.TemporaryDirectory() as td:
        repo = _build_fixture_repo(Path(td))
        inventory = mod.collect_inventory(repo / "profile-al-dev-shared")

        assert inventory.skills == ["skill-a", "skill-b"], inventory.skills
        assert inventory.agents == ["orphan", "worker"], inventory.agents
        assert inventory.knowledge == ["guide.md", "workflow.md"], inventory.knowledge
        assert inventory.skill_to_agent == [("skill-a", "worker")], inventory.skill_to_agent
        assert inventory.skill_to_skill == [("skill-a", "plan"), ("skill-a", "skill-b")], inventory.skill_to_skill
        assert inventory.skill_to_knowledge == [("skill-a", "guide.md")], inventory.skill_to_knowledge
        assert inventory.agent_to_knowledge == [("worker", "guide.md")], inventory.agent_to_knowledge
        assert inventory.skill_to_artifact == [("skill-a", "report.md")], inventory.skill_to_artifact


def test_collect_inventory_raises_on_broken_agent_frontmatter() -> None:
    with tempfile.TemporaryDirectory() as td:
        repo = _build_fixture_repo(Path(td))
        broken = repo / "profile-al-dev-shared" / "agents" / "broken.md"
        broken.write_text("no frontmatter\n", encoding="utf-8")

        with unittest.TestCase().assertRaisesRegex(ValueError, "frontmatter"):
            mod.collect_inventory(repo / "profile-al-dev-shared")


def test_mermaid_node_ids_must_be_unique_after_sanitization() -> None:
    with unittest.TestCase().assertRaisesRegex(ValueError, "duplicate Mermaid node id"):
        mod.assert_unique_node_ids(["worker-a", "worker_a"])


def test_replace_marked_sections_rejects_unknown_keys() -> None:
    doc = (
        "# Map\n\n"
        "<!-- BEGIN GENERATED: agent-catalog-table -->\n"
        "old content\n"
        "<!-- END GENERATED: agent-catalog-table -->\n"
    )

    with unittest.TestCase().assertRaisesRegex(KeyError, "unknown section keys"):
        mod.replace_marked_sections(doc, {"unknown-section": "new content"})


def test_marker_scan_requires_matching_begin_and_end() -> None:
    with unittest.TestCase().assertRaisesRegex(ValueError, "end marker"):
        mod.find_marker_spans(
            "# Map\n\n"
            "<!-- BEGIN GENERATED: agent-catalog-table -->\n"
            "old content\n"
        )

    with unittest.TestCase().assertRaisesRegex(ValueError, "begin marker"):
        mod.find_marker_spans(
            "# Map\n\n"
            "old content\n"
            "<!-- END GENERATED: agent-catalog-table -->\n"
        )


def test_marker_scan_rejects_duplicate_marker_keys() -> None:
    doc = (
        "# Map\n\n"
        "<!-- BEGIN GENERATED: agent-catalog-table -->\n"
        "old content\n"
        "<!-- END GENERATED: agent-catalog-table -->\n\n"
        "<!-- BEGIN GENERATED: agent-catalog-table -->\n"
        "other content\n"
        "<!-- END GENERATED: agent-catalog-table -->\n"
    )

    with unittest.TestCase().assertRaisesRegex(ValueError, "duplicate"):
        mod.find_marker_spans(doc)


def test_generate_document_updates_is_atomic_when_rendering_fails() -> None:
    with tempfile.TemporaryDirectory() as td:
        repo = _build_bad_marker_repo(Path(td))
        docs_root = repo / "docs"
        target_docs = [docs_root / Path(rel).name for rel in TARGET_DOCS]
        before = {path: path.read_text(encoding="utf-8") for path in target_docs}

        with unittest.TestCase().assertRaisesRegex(ValueError, "duplicate marker"):
            mod.generate_document_updates(repo)

        after = {path: path.read_text(encoding="utf-8") for path in target_docs}
        assert after == before, (before, after)


def test_generate_document_updates_renders_full_marker_set_without_external_skill_nodes() -> None:
    with tempfile.TemporaryDirectory() as td:
        repo = _build_fixture_repo(Path(td))

        updates = mod.generate_document_updates(repo)

        plugin_graph = updates[repo / "docs" / "plugin_graph.md"]
        workflow = updates[repo / "docs" / "workflow_diagrams.md"]
        skills_map = updates[repo / "docs" / "skills_map.md"]

        assert "old dependency" not in plugin_graph
        assert "old overlays" not in plugin_graph
        assert "old health" not in plugin_graph
        assert "skill_skill_b[skill-b]" in plugin_graph
        assert "skill_plan[plan]" not in plugin_graph
        assert "skill_plan[plan]" not in workflow
        assert "Missing refs" in plugin_graph
        assert "skill: plan" not in plugin_graph
        assert "knowledge: guide.md" not in plugin_graph
        assert "Agents spawned: `al-dev-shared:worker`" in skills_map
        assert "skill_plan[plan]" not in skills_map
        assert "<!-- BEGIN GENERATED: skill-drilldown-skill-a -->" in skills_map


def test_generate_document_updates_fails_on_missing_internal_skill_refs() -> None:
    with tempfile.TemporaryDirectory() as td:
        repo = _build_missing_internal_skill_repo(Path(td))

        with unittest.TestCase().assertRaisesRegex(ValueError, "skill reference skill-a -> skill-missing"):
            mod.generate_document_updates(repo)


def test_real_repo_render_is_deterministic_without_mutating_tracked_docs() -> None:
    with tempfile.TemporaryDirectory() as td:
        temp_repo = Path(td) / "fixture-repo"
        shutil.copytree(
            REPO_ROOT,
            temp_repo,
            ignore=shutil.ignore_patterns(".git", "__pycache__", ".pytest_cache", ".mypy_cache"),
        )
        skills_map = temp_repo / "docs" / "skills_map.md"
        text = skills_map.read_text(encoding="utf-8")
        text = re.sub(
            r"\n<!-- BEGIN GENERATED: skill-drilldown-verify-commits -->.*?"
            r"<!-- END GENERATED: skill-drilldown-verify-commits -->\n",
            "\n",
            text,
            flags=re.DOTALL,
        )
        text = text.replace("skill-drilldown-al-dev-", "skill-drilldown-")
        skills_map.write_text(text, encoding="utf-8")
        tracked_before = {path: path.read_text(encoding="utf-8") for path in (REPO_ROOT / rel for rel in TARGET_DOCS)}

        first = mod.generate_document_updates(temp_repo)
        second = mod.generate_document_updates(temp_repo)

        assert first == second
        assert first, "Expected generate_document_updates(temp_repo) to return updates"
        expected_docs = {temp_repo / rel for rel in TARGET_DOCS}
        assert expected_docs.issubset(set(first)), first
        tracked_after = {path: path.read_text(encoding="utf-8") for path in (REPO_ROOT / rel for rel in TARGET_DOCS)}
        assert tracked_after == tracked_before, (tracked_before, tracked_after)


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
