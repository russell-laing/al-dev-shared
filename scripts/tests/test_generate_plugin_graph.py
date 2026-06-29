"""Fixture-based tests for scripts/generate_plugin_graph.py."""
from __future__ import annotations

import importlib.util
import inspect
import tempfile
import unittest
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = REPO_ROOT / "scripts"
for path in (REPO_ROOT, SCRIPTS_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from scripts.al_dev_tools.docs import map_doc_sections as shared

_spec = importlib.util.spec_from_file_location(
    "generate_plugin_graph",
    REPO_ROOT / "scripts" / "generate_plugin_graph.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)


def _build_fixture(root: Path) -> Path:
    """Create a tiny fake plugin dir with an orphan, dead knowledge, and missing ref."""
    plugin = root / "profile-al-dev-shared"
    (plugin / "skills" / "s-main").mkdir(parents=True)
    (plugin / "skills" / "s-other").mkdir(parents=True)
    (plugin / "agents").mkdir(parents=True)
    (plugin / "knowledge").mkdir(parents=True)

    (plugin / "skills" / "s-main" / "SKILL.md").write_text(
        "Spawn al-dev-shared:worker.\n"
        "See ../../knowledge/good.md and ../../knowledge/missing.md.\n"
        "Writes .dev/output.md.\n"
        "Then run /s-other to continue.\n"
        "If needed, run /plan to switch to an external wrapper.\n",
        encoding="utf-8",
    )
    (plugin / "skills" / "s-other" / "SKILL.md").write_text(
        "A second skill with no agent or knowledge refs.\n",
        encoding="utf-8",
    )
    (plugin / "agents" / "worker.md").write_text(
        "---\n"
        "name: worker\n"
        "description: Worker agent\n"
        "model: haiku\n"
        'tools: ["Read"]\n'
        "---\n\n"
        "Worker agent. Reads ../../knowledge/good.md.\n",
        encoding="utf-8",
    )
    (plugin / "agents" / "orphan.md").write_text(
        "---\n"
        "name: orphan\n"
        "description: Orphan agent\n"
        "model: sonnet\n"
        'tools: ["Read"]\n'
        "---\n\n"
        "Orphan agent spawned by no skill.\n",
        encoding="utf-8",
    )
    (plugin / "knowledge" / "good.md").write_text("good\n", encoding="utf-8")
    (plugin / "knowledge" / "dead.md").write_text("referenced by nobody\n", encoding="utf-8")
    return plugin


def _graph_doc_template() -> str:
    return (
        "# Plugin Dependency Graph\n\n"
        "<!-- BEGIN GENERATED: plugin-dependency-mermaid -->\n"
        "old dependency\n"
        "<!-- END GENERATED: plugin-dependency-mermaid -->\n\n"
        "<!-- BEGIN GENERATED: plugin-workflow-overlays -->\n"
        "old overlays\n"
        "<!-- END GENERATED: plugin-workflow-overlays -->\n\n"
        "<!-- BEGIN GENERATED: plugin-health-callouts -->\n"
        "old health\n"
        "<!-- END GENERATED: plugin-health-callouts -->\n"
    )


def test_build_document_preserves_fixture_edges_and_health() -> None:
    with tempfile.TemporaryDirectory() as td:
        plugin = _build_fixture(Path(td))
        inventory = shared.collect_inventory(plugin)
        health = shared.summarize_plugin_health(inventory, workflow_paths=_mod.WORKFLOW_PATHS)
        rendered = _mod.build_document(inventory, health, today="2026-06-02")

        assert inventory.skills == ["s-main", "s-other"], inventory.skills
        assert inventory.skill_to_skill == [("s-main", "plan"), ("s-main", "s-other")]
        assert "flowchart LR" in rendered
        assert "skill_s_main[s-main]" in rendered
        assert "skill_s_main --> skill_s_other" in rendered
        assert "agent_worker[worker]" in rendered
        assert "agent_worker --> knowledge_good_md" in rendered
        assert "knowledge: missing.md" in rendered
        assert "Orphan agents" in rendered
        assert "orphan" in rendered


def test_build_document_does_not_render_external_wrapper_nodes() -> None:
    with tempfile.TemporaryDirectory() as td:
        plugin = _build_fixture(Path(td))
        inventory = shared.collect_inventory(plugin)
        health = shared.summarize_plugin_health(inventory, workflow_paths=_mod.WORKFLOW_PATHS)
        rendered = _mod.build_document(inventory, health, today="2026-06-02")

        assert "skill_plan[plan]" not in rendered
        assert " --> skill_plan" not in rendered
        assert "skill: plan" not in rendered


def test_main_writes_document_on_success() -> None:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        plugin = _build_fixture(root)
        output = root / "docs" / "plugin_graph.md"
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(_graph_doc_template(), encoding="utf-8")
        old_plugin = _mod.PLUGIN
        old_output = _mod.OUTPUT
        try:
            _mod.PLUGIN = plugin
            _mod.OUTPUT = output
            assert _mod.main() == 0
        finally:
            _mod.PLUGIN = old_plugin
            _mod.OUTPUT = old_output

        rendered = output.read_text(encoding="utf-8")
        assert "<!-- BEGIN GENERATED: plugin-dependency-mermaid -->" in rendered
        assert "skill_s_main --> skill_s_other" in rendered
        assert "knowledge: missing.md" in rendered
        assert "old dependency" not in rendered


def test_main_fails_closed_without_partial_write_on_inventory_error() -> None:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        plugin = _build_fixture(root)
        (plugin / "agents" / "broken.md").write_text("no frontmatter\n", encoding="utf-8")
        output = root / "docs" / "plugin_graph.md"
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(_graph_doc_template(), encoding="utf-8")
        before = output.read_text(encoding="utf-8")
        old_plugin = _mod.PLUGIN
        old_output = _mod.OUTPUT
        try:
            _mod.PLUGIN = plugin
            _mod.OUTPUT = output
            assert _mod.main() == 1
        finally:
            _mod.PLUGIN = old_plugin
            _mod.OUTPUT = old_output

        assert output.read_text(encoding="utf-8") == before


def test_node_id_uses_shared_mermaid_sanitization() -> None:
    assert _mod.node_id("worker") == "worker"
    assert _mod.node_id("worker") == shared.mermaid_node_id("worker")


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
