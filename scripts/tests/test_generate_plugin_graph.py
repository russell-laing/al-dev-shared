"""Fixture-based tests for scripts/generate-plugin-graph.py."""
from __future__ import annotations

import importlib.util
import inspect
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location(
    "generate_plugin_graph",
    REPO_ROOT / "scripts" / "generate-plugin-graph.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)


def _build_fixture(root: Path) -> Path:
    """Create a tiny fake plugin dir with a known orphan, dead link, and missing ref."""
    plugin = root / "profile-al-dev-shared"
    (plugin / "skills" / "s-main").mkdir(parents=True)
    (plugin / "skills" / "s-other").mkdir(parents=True)
    (plugin / "agents").mkdir(parents=True)
    (plugin / "knowledge").mkdir(parents=True)

    (plugin / "skills" / "s-main" / "SKILL.md").write_text(
        "Spawn al-dev-shared:al-dev-worker.\n"
        "See ../../knowledge/good.md and ../../knowledge/missing.md.\n"
        "Writes .dev/output.md.\n"
        "Then run /s-other to continue.\n",
        encoding="utf-8",
    )
    (plugin / "skills" / "s-other" / "SKILL.md").write_text(
        "A second skill with no agent or knowledge refs.\n",
        encoding="utf-8",
    )
    (plugin / "agents" / "al-dev-worker.md").write_text(
        "Worker agent. Reads ../../knowledge/good.md.\n", encoding="utf-8"
    )
    (plugin / "agents" / "al-dev-orphan.md").write_text(
        "Orphan agent spawned by no skill.\n", encoding="utf-8"
    )
    (plugin / "knowledge" / "good.md").write_text("good\n", encoding="utf-8")
    (plugin / "knowledge" / "dead.md").write_text("referenced by nobody\n", encoding="utf-8")
    return plugin


def test_discover_finds_skills_agents_knowledge() -> None:
    with tempfile.TemporaryDirectory() as td:
        plugin = _build_fixture(Path(td))
        skills, agents, knowledge = _mod.discover(plugin)
        assert skills == ["s-main", "s-other"], skills
        assert agents == ["al-dev-orphan", "al-dev-worker"], agents
        assert knowledge == ["dead.md", "good.md"], knowledge


def test_extract_edges_finds_all_edge_types() -> None:
    with tempfile.TemporaryDirectory() as td:
        plugin = _build_fixture(Path(td))
        skills, _, _ = _mod.discover(plugin)
        edges = _mod.extract_edges(plugin, skills)
        assert ("s-main", "al-dev-worker") in edges["skill_agent"]
        assert ("s-main", "s-other") in edges["skill_skill"]
        assert ("s-main", "good.md") in edges["skill_knowledge"]
        assert ("s-main", "missing.md") in edges["skill_knowledge"]
        assert ("al-dev-worker", "good.md") in edges["agent_knowledge"]
        assert ("s-main", "output.md") in edges["skill_artifact"]


def test_find_health_detects_orphan_dead_and_missing() -> None:
    with tempfile.TemporaryDirectory() as td:
        plugin = _build_fixture(Path(td))
        skills, agents, knowledge = _mod.discover(plugin)
        edges = _mod.extract_edges(plugin, skills)
        health = _mod.find_health(skills, agents, knowledge, edges)
        assert health["orphan_agents"] == ["al-dev-orphan"], health["orphan_agents"]
        assert "dead.md" in health["dead_knowledge"]
        assert ("knowledge", "missing.md") in health["missing_refs"]


def test_node_id_sanitizes_hyphens() -> None:
    assert _mod.node_id("al-dev-worker") == "al_dev_worker"


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
