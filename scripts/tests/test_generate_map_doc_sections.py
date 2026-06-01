"""Fixture-based tests for scripts/map_doc_sections.py."""
from __future__ import annotations

import importlib.util
import inspect
import shutil
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MAP_DOC_SECTIONS_PATH = REPO_ROOT / "scripts" / "map_doc_sections.py"
TARGET_DOCS = (
    "docs/al-dev-skills-map.md",
    "docs/al-dev-agent-map.md",
    "docs/al-dev-plugin-graph.md",
    "docs/al-dev-workflow-diagrams.md",
)


def _load_map_doc_sections():
    spec = importlib.util.spec_from_file_location("map_doc_sections", MAP_DOC_SECTIONS_PATH)
    if spec is None or spec.loader is None:
        raise FileNotFoundError(MAP_DOC_SECTIONS_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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
        "Spawn al-dev-worker to parallelize checks.\n"
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
    (plugin / "agents" / "al-dev-worker.md").write_text(
        "---\n"
        "name: al-dev-worker\n"
        "description: Worker agent\n"
        "model: haiku\n"
        'tools: ["Read", "Write"]\n'
        "---\n\n"
        "# Agent: al-dev-worker\n"
        "Reads knowledge/guide.md and knowledge/guide.md.\n",
        encoding="utf-8",
    )
    (plugin / "agents" / "al-dev-orphan.md").write_text(
        "---\n"
        "name: al-dev-orphan\n"
        "description: Orphan agent\n"
        "model: sonnet\n"
        'tools: ["Read"]\n'
        "---\n\n"
        "# Agent: al-dev-orphan\n"
        "No skill spawns this agent.\n",
        encoding="utf-8",
    )
    (plugin / "knowledge" / "guide.md").write_text("guide\n", encoding="utf-8")
    (plugin / "knowledge" / "workflow.md").write_text("workflow\n", encoding="utf-8")
    (repo / "docs" / "al-dev-skills-map.md").write_text(
        "# Skills Map\n\n"
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
    (repo / "docs" / "al-dev-agent-map.md").write_text(
        "# Agent Map\n\n"
        "<!-- BEGIN GENERATED: agent-catalog-table -->\n"
        "old content\n"
        "<!-- END GENERATED: agent-catalog-table -->\n",
        encoding="utf-8",
    )
    (repo / "docs" / "al-dev-plugin-graph.md").write_text(
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
    (repo / "docs" / "al-dev-workflow-diagrams.md").write_text(
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
    (repo / "docs" / "al-dev-agent-map.md").write_text(
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
        mod = _load_map_doc_sections()
        inventory = mod.collect_inventory(repo / "profile-al-dev-shared")

        assert inventory.skills == ["skill-a", "skill-b"], inventory.skills
        assert inventory.agents == ["al-dev-orphan", "al-dev-worker"], inventory.agents
        assert inventory.knowledge == ["guide.md", "workflow.md"], inventory.knowledge
        assert inventory.skill_to_agent == [("skill-a", "al-dev-worker")], inventory.skill_to_agent
        assert inventory.skill_to_skill == [("skill-a", "plan"), ("skill-a", "skill-b")], inventory.skill_to_skill
        assert inventory.skill_to_knowledge == [("skill-a", "guide.md")], inventory.skill_to_knowledge
        assert inventory.agent_to_knowledge == [("al-dev-worker", "guide.md")], inventory.agent_to_knowledge
        assert inventory.skill_to_artifact == [("skill-a", "report.md")], inventory.skill_to_artifact


def test_collect_inventory_raises_on_broken_agent_frontmatter() -> None:
    with tempfile.TemporaryDirectory() as td:
        repo = _build_fixture_repo(Path(td))
        broken = repo / "profile-al-dev-shared" / "agents" / "broken.md"
        broken.write_text("no frontmatter\n", encoding="utf-8")
        mod = _load_map_doc_sections()

        with unittest.TestCase().assertRaisesRegex(ValueError, "frontmatter"):
            mod.collect_inventory(repo / "profile-al-dev-shared")


def test_mermaid_node_ids_must_be_unique_after_sanitization() -> None:
    mod = _load_map_doc_sections()

    with unittest.TestCase().assertRaisesRegex(ValueError, "duplicate Mermaid node id"):
        mod.assert_unique_node_ids(["al-dev-worker", "al_dev_worker"])


def test_replace_marked_sections_rejects_unknown_keys() -> None:
    mod = _load_map_doc_sections()
    doc = (
        "# Map\n\n"
        "<!-- BEGIN GENERATED: agent-catalog-table -->\n"
        "old content\n"
        "<!-- END GENERATED: agent-catalog-table -->\n"
    )

    with unittest.TestCase().assertRaisesRegex(KeyError, "unknown section keys"):
        mod.replace_marked_sections(doc, {"unknown-section": "new content"})


def test_marker_scan_requires_matching_begin_and_end() -> None:
    mod = _load_map_doc_sections()

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
    mod = _load_map_doc_sections()
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
        mod = _load_map_doc_sections()
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
        mod = _load_map_doc_sections()

        updates = mod.generate_document_updates(repo)

        plugin_graph = updates[repo / "docs" / "al-dev-plugin-graph.md"]
        workflow = updates[repo / "docs" / "al-dev-workflow-diagrams.md"]
        skills_map = updates[repo / "docs" / "al-dev-skills-map.md"]

        assert "old dependency" not in plugin_graph
        assert "old overlays" not in plugin_graph
        assert "old health" not in plugin_graph
        assert "skill_skill_b[skill-b]" in plugin_graph
        assert "skill_plan[plan]" not in plugin_graph
        assert "skill_plan[plan]" not in workflow
        assert "Missing refs" in plugin_graph
        assert "skill: plan" not in plugin_graph
        assert "knowledge: guide.md" not in plugin_graph
        assert "Agents spawned: `al-dev-shared:al-dev-worker`" in skills_map
        assert "skill_plan[plan]" not in skills_map
        assert "<!-- BEGIN GENERATED: skill-drilldown-skill-a -->" in skills_map


def test_generate_document_updates_fails_on_missing_internal_skill_refs() -> None:
    with tempfile.TemporaryDirectory() as td:
        repo = _build_missing_internal_skill_repo(Path(td))
        mod = _load_map_doc_sections()

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
        mod = _load_map_doc_sections()
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
