"""Rendering and document-update orchestration for map documents."""

from __future__ import annotations

from pathlib import Path
import re
import shutil
import tempfile
from typing import Callable, Iterable, Optional

from scripts.al_dev_tools.io_utils import write_text_atomic

from .map_inventory import (
    Inventory,
    SectionSpec,
    WORKFLOW_ORDER,
    assert_unique_node_ids,
    collect_inventory,
    validate_inventory_skill_references,
)
from .map_markers import find_marker_spans, replace_marked_sections


TARGET_DOCS = (
    Path("docs/al-dev-skills-map.md"),
    Path("docs/al-dev-agent-map.md"),
    Path("docs/al-dev-plugin-graph.md"),
    Path("docs/al-dev-workflow-diagrams.md"),
)

SKILLS_MAP_DOC = Path("docs/al-dev-skills-map.md")
DRILLDOWN_LAYER_HEADING = "## Layer 2: Per-Skill Drill-Downs"

SECTION_CONFIG: dict[str, dict[str, str | Path]] = {
    "skill-lifecycle-mermaid": {
        "doc": Path("docs/al-dev-skills-map.md"),
        "renderer": "render_skill_lifecycle",
    },
    "agent-catalog-table": {
        "doc": Path("docs/al-dev-agent-map.md"),
        "renderer": "render_agent_catalog",
    },
    "agent-coverage": {
        "doc": Path("docs/al-dev-agent-map.md"),
        "renderer": "render_agent_coverage",
    },
    "skill-coverage": {
        "doc": Path("docs/al-dev-skills-map.md"),
        "renderer": "render_skill_coverage",
    },
    "plugin-dependency-mermaid": {
        "doc": Path("docs/al-dev-plugin-graph.md"),
        "renderer": "render_plugin_dependency",
    },
    "plugin-workflow-overlays": {
        "doc": Path("docs/al-dev-plugin-graph.md"),
        "renderer": "render_plugin_workflow_overlays",
    },
    "plugin-health-callouts": {
        "doc": Path("docs/al-dev-plugin-graph.md"),
        "renderer": "render_plugin_health_callouts",
    },
    "workflow-skills-agents-mermaid": {
        "doc": Path("docs/al-dev-workflow-diagrams.md"),
        "renderer": "render_workflow_skills_agents",
    },
    "workflow-knowledge-mermaid": {
        "doc": Path("docs/al-dev-workflow-diagrams.md"),
        "renderer": "render_workflow_knowledge",
    },
}

LIFECYCLE_BRANCHES: tuple[tuple[str, str, str, str | None], ...] = (
    ("al-dev-explore", "al-dev-plan", "optional", "explore-findings.md"),
    ("al-dev-interview", "al-dev-plan", "optional", "interview-requirements.md"),
    ("al-dev-investigate", "al-dev-plan", "optional", None),
    ("al-dev-perf", "al-dev-plan", "optional", "perf-analysis.md"),
    ("al-dev-plan-preflight", "al-dev-plan", "optional", "preflight-context.md"),
    ("al-dev-develop", "al-dev-lint", "optional", None),
    ("al-dev-commit", "al-dev-release-notes", "optional", None),
    ("al-dev-commit", "al-dev-handoff", "optional", None),
    ("al-dev-commit", "al-dev-document", "optional", None),
    ("al-dev-commit", "al-dev-consolidate", "optional", None),
    ("al-dev-commit", "verify-commits", "default", None),
    ("commit-recover", "al-dev-commit", "default", None),
)

SKILL_DRILLDOWN_PREFIX = "skill-drilldown-"


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _mermaid_block(lines: Iterable[str]) -> str:
    return "```mermaid\n" + "\n".join(lines).rstrip() + "\n```"


def _wrap_generated_section(key: str, body: str) -> str:
    return f"<!-- BEGIN GENERATED: {key} -->\n{body.rstrip()}\n<!-- END GENERATED: {key} -->"


def _format_overlay_title(key: str) -> str:
    return key.replace("-", " ").title()


def _sorted_destinations(edges: Iterable[tuple[str, str]], source: str) -> list[str]:
    return sorted(dst for src, dst in edges if src == source)


def _typed_node_id(kind: str, name: str) -> str:
    from .map_inventory import mermaid_node_id

    return f"{kind}_{mermaid_node_id(name)}"


def _internal_skill_edges(inv: Inventory) -> list[tuple[str, str]]:
    skill_set = set(inv.skills)
    return [(src, dst) for src, dst in inv.skill_to_skill if src in skill_set and dst in skill_set]


def _internal_skill_agent_edges(inv: Inventory) -> list[tuple[str, str]]:
    skill_set = set(inv.skills)
    agent_set = set(inv.agents)
    return [(src, dst) for src, dst in inv.skill_to_agent if src in skill_set and dst in agent_set]


def _internal_skill_knowledge_edges(inv: Inventory) -> list[tuple[str, str]]:
    skill_set = set(inv.skills)
    knowledge_set = set(inv.knowledge)
    return [(src, dst) for src, dst in inv.skill_to_knowledge if src in skill_set and dst in knowledge_set]


def _internal_agent_knowledge_edges(inv: Inventory) -> list[tuple[str, str]]:
    agent_set = set(inv.agents)
    knowledge_set = set(inv.knowledge)
    return [(src, dst) for src, dst in inv.agent_to_knowledge if src in agent_set and dst in knowledge_set]


def _validate_inventory_for_rendering(inv: Inventory) -> None:
    assert_unique_node_ids(inv.skills)
    assert_unique_node_ids(inv.agents)
    assert_unique_node_ids(inv.knowledge)


def render_skill_lifecycle(inv: Inventory) -> str:
    available_skills = set(inv.skills)
    skill_skill_edges = _internal_skill_edges(inv)
    edge_lines: list[str] = []
    lifecycle_nodes: set[str] = set()

    for path in WORKFLOW_ORDER.values():
        visible = [skill for skill in path if skill in available_skills]
        lifecycle_nodes.update(visible)
        for left, right in zip(visible, visible[1:]):
            edge_lines.append(f"    {_typed_node_id('skill', left)} --> {_typed_node_id('skill', right)}")

    for left, right, style, label in LIFECYCLE_BRANCHES:
        if left not in available_skills or right not in available_skills:
            continue
        lifecycle_nodes.update((left, right))
        arrow = "-.->" if style == "optional" else "-->"
        edge = f"    {_typed_node_id('skill', left)} {arrow}"
        if label:
            edge += f" |{label}|"
        edge += f" {_typed_node_id('skill', right)}"
        edge_lines.append(edge)

    if not edge_lines:
        for left, right in skill_skill_edges:
            lifecycle_nodes.update((left, right))
            edge_lines.append(f"    {_typed_node_id('skill', left)} --> {_typed_node_id('skill', right)}")

    if not lifecycle_nodes:
        lifecycle_nodes.update(inv.skills)

    lines = [
        "flowchart TD",
        "    classDef skillNode fill:#dbeafe,stroke:#2563eb,color:#1e3a5f,font-weight:bold",
    ]
    for skill in sorted(lifecycle_nodes):
        lines.append(f"    {_typed_node_id('skill', skill)}[{skill}]")
    lines.append("")
    lines.extend(sorted(set(edge_lines)))
    lines.append("")
    for skill in sorted(lifecycle_nodes):
        lines.append(f"    class {_typed_node_id('skill', skill)} skillNode")
    return _mermaid_block(lines)


def render_agent_catalog(inv: Inventory) -> str:
    skill_agent_edges = _internal_skill_agent_edges(inv)
    rows = [
        "| Agent | Model | Tools | Spawned by |",
        "|-------|-------|-------|------------|",
    ]
    for name in inv.agents:
        meta = inv.agent_meta[name]
        spawned_by = ", ".join(f"`/{skill}`" for skill, agent in skill_agent_edges if agent == name) or "(none found)"
        tools = ", ".join(meta.tools) if meta.tools else "(none)"
        rows.append(f"| {name} | {meta.model} | {tools} | {spawned_by} |")
    return "\n".join(rows)


def render_agent_coverage(inv: Inventory) -> str:
    return (
        f"**Coverage:** {len(inv.agents)} active agents in "
        "`profile-al-dev-shared/agents/` (count derived from disk at generation time)."
    )


def render_skill_coverage(inv: Inventory) -> str:
    return (
        f"**Coverage:** {len(inv.skills)} active skills in "
        "`profile-al-dev-shared/skills/` (count derived from disk at generation time)."
    )


def render_plugin_dependency(inv: Inventory) -> str:
    skill_skill_edges = _internal_skill_edges(inv)
    skill_agent_edges = _internal_skill_agent_edges(inv)
    skill_knowledge_edges = _internal_skill_knowledge_edges(inv)
    agent_knowledge_edges = _internal_agent_knowledge_edges(inv)
    referenced_knowledge = sorted({dst for _, dst in skill_knowledge_edges} | {dst for _, dst in agent_knowledge_edges})
    artifacts = sorted({dst for _, dst in inv.skill_to_artifact})

    lines = [
        "flowchart LR",
        "    classDef skillNode fill:#dbeafe,stroke:#2563eb,color:#1e3a5f,font-weight:bold",
        "    classDef agentNode fill:#d1fae5,stroke:#059669,color:#064e3b,font-weight:bold",
        "    classDef knowledgeNode fill:#fef3c7,stroke:#d97706,color:#78350f,font-weight:bold",
        "    classDef artifactNode fill:#ede9fe,stroke:#7c3aed,color:#4c1d95,font-weight:bold",
        "",
        "    subgraph Skills[Skills]",
    ]
    for skill in inv.skills:
        lines.append(f"        {_typed_node_id('skill', skill)}[{skill}]")
    lines.append("    end")
    lines.append("    subgraph Agents[Agents]")
    for agent in inv.agents:
        lines.append(f"        {_typed_node_id('agent', agent)}[{agent}]")
    lines.append("    end")
    lines.append("    subgraph Knowledge[Knowledge Files]")
    for knowledge in referenced_knowledge:
        lines.append(f"        {_typed_node_id('knowledge', knowledge)}[{knowledge[:-3]}]")
    lines.append("    end")
    if artifacts:
        lines.append("    subgraph Artifacts[Artifacts]")
        for artifact in artifacts:
            lines.append(f"        {_typed_node_id('artifact', artifact)}[.dev/{artifact}]")
        lines.append("    end")
    lines.append("")

    for src, dst in skill_skill_edges:
        lines.append(f"    {_typed_node_id('skill', src)} --> {_typed_node_id('skill', dst)}")
    for src, dst in skill_agent_edges:
        lines.append(f"    {_typed_node_id('skill', src)} --> {_typed_node_id('agent', dst)}")
    for src, dst in skill_knowledge_edges:
        lines.append(f"    {_typed_node_id('skill', src)} --> {_typed_node_id('knowledge', dst)}")
    for src, dst in agent_knowledge_edges:
        lines.append(f"    {_typed_node_id('agent', src)} --> {_typed_node_id('knowledge', dst)}")
    for src, dst in inv.skill_to_artifact:
        lines.append(f"    {_typed_node_id('skill', src)} --> {_typed_node_id('artifact', dst)}")

    lines.append("")
    for skill in inv.skills:
        lines.append(f"    class {_typed_node_id('skill', skill)} skillNode")
    for agent in inv.agents:
        lines.append(f"    class {_typed_node_id('agent', agent)} agentNode")
    for knowledge in referenced_knowledge:
        lines.append(f"    class {_typed_node_id('knowledge', knowledge)} knowledgeNode")
    for artifact in artifacts:
        lines.append(f"    class {_typed_node_id('artifact', artifact)} artifactNode")
    return _mermaid_block(lines)


def render_plugin_workflow_overlays(
    inv: Inventory,
    workflow_paths: Optional[dict[str, list[str]]] = None,
) -> str:
    workflow_paths = workflow_paths or WORKFLOW_ORDER
    available_skills = set(inv.skills)
    blocks: list[str] = []
    preserve_titles = workflow_paths is not WORKFLOW_ORDER
    for workflow_name, path in workflow_paths.items():
        visible = [skill for skill in path if skill in available_skills]
        block_lines = ["flowchart LR", "    classDef skillNode fill:#dbeafe,stroke:#2563eb,color:#1e3a5f,font-weight:bold"]
        if visible:
            for skill in visible:
                block_lines.append(f"    {_typed_node_id('skill', skill)}[{skill}]")
            block_lines.append("")
            for left, right in zip(visible, visible[1:]):
                block_lines.append(f"    {_typed_node_id('skill', left)} --> {_typed_node_id('skill', right)}")
            block_lines.append("")
            for skill in visible:
                block_lines.append(f"    class {_typed_node_id('skill', skill)} skillNode")
        else:
            block_lines.append("    missing[No configured workflow skills present]")
        title = workflow_name if preserve_titles else _format_overlay_title(workflow_name)
        blocks.append(f"### {title}\n\n{_mermaid_block(block_lines)}")
    return "\n\n".join(blocks)


def render_plugin_health_callouts(
    inv: Inventory,
    workflow_paths: Optional[dict[str, list[str]]] = None,
) -> str:
    from .map_inventory import summarize_plugin_health

    health = summarize_plugin_health(inv, workflow_paths=workflow_paths)

    def section(title: str, items: list[str]) -> str:
        if not items:
            return f"**{title}:** none"
        return f"**{title}:**\n\n" + "\n".join(f"- `{item}`" for item in items)

    missing = [f"{kind}: {name}" for kind, name in health["missing_refs"]]
    return "\n\n".join(
        (
            section("Orphan agents (spawned by no skill)", health["orphan_agents"]),
            section("Dead knowledge (referenced by nothing)", health["dead_knowledge"]),
            section("Off-path skills (not on any configured workflow path)", health["offpath_skills"]),
            section("Missing refs (referenced but not on disk)", missing),
        )
    )


def render_workflow_skills_agents(inv: Inventory) -> str:
    skill_skill_edges = _internal_skill_edges(inv)
    skill_agent_edges = _internal_skill_agent_edges(inv)
    skill_nodes = sorted(
        {src for src, _ in skill_skill_edges}
        | {dst for _, dst in skill_skill_edges}
        | {src for src, _ in skill_agent_edges}
    )
    agent_nodes = sorted({dst for _, dst in skill_agent_edges})
    if not skill_nodes:
        skill_nodes = inv.skills

    lines = [
        "flowchart LR",
        "    classDef skillNode fill:#dbeafe,stroke:#2563eb,color:#1e3a5f,font-weight:bold",
        "    classDef agentNode fill:#d1fae5,stroke:#059669,color:#064e3b,font-weight:bold",
        "",
        "    subgraph Skills[Skills]",
    ]
    for skill in skill_nodes:
        lines.append(f"        {_typed_node_id('skill', skill)}[{skill}]")
    lines.append("    end")
    if agent_nodes:
        lines.append("    subgraph Agents[Agents]")
        for agent in agent_nodes:
            lines.append(f"        {_typed_node_id('agent', agent)}[{agent}]")
        lines.append("    end")
    lines.append("")
    for src, dst in skill_skill_edges:
        lines.append(f"    {_typed_node_id('skill', src)} --> {_typed_node_id('skill', dst)}")
    for src, dst in skill_agent_edges:
        lines.append(f"    {_typed_node_id('skill', src)} --> {_typed_node_id('agent', dst)}")
    lines.append("")
    for skill in skill_nodes:
        lines.append(f"    class {_typed_node_id('skill', skill)} skillNode")
    for agent in agent_nodes:
        lines.append(f"    class {_typed_node_id('agent', agent)} agentNode")
    return _mermaid_block(lines)


def render_workflow_knowledge(inv: Inventory) -> str:
    skill_knowledge_edges = _internal_skill_knowledge_edges(inv)
    agent_knowledge_edges = _internal_agent_knowledge_edges(inv)
    skill_nodes = sorted({src for src, _ in skill_knowledge_edges})
    agent_nodes = sorted({src for src, _ in agent_knowledge_edges})
    knowledge_nodes = sorted({dst for _, dst in skill_knowledge_edges} | {dst for _, dst in agent_knowledge_edges})

    lines = [
        "flowchart LR",
        "    classDef skillNode fill:#dbeafe,stroke:#2563eb,color:#1e3a5f,font-weight:bold",
        "    classDef agentNode fill:#d1fae5,stroke:#059669,color:#064e3b,font-weight:bold",
        "    classDef knowledgeNode fill:#fef3c7,stroke:#d97706,color:#78350f,font-weight:bold",
        "",
    ]
    if skill_nodes:
        lines.append("    subgraph Skills[Skills]")
        for skill in skill_nodes:
            lines.append(f"        {_typed_node_id('skill', skill)}[{skill}]")
        lines.append("    end")
    if agent_nodes:
        lines.append("    subgraph Agents[Agents]")
        for agent in agent_nodes:
            lines.append(f"        {_typed_node_id('agent', agent)}[{agent}]")
        lines.append("    end")
    lines.append("    subgraph Knowledge[Knowledge Files]")
    for knowledge in knowledge_nodes:
        lines.append(f"        {_typed_node_id('knowledge', knowledge)}[{knowledge[:-3]}]")
    lines.append("    end")
    lines.append("")
    for src, dst in skill_knowledge_edges:
        lines.append(f"    {_typed_node_id('skill', src)} --> {_typed_node_id('knowledge', dst)}")
    for src, dst in agent_knowledge_edges:
        lines.append(f"    {_typed_node_id('agent', src)} --> {_typed_node_id('knowledge', dst)}")
    lines.append("")
    for skill in skill_nodes:
        lines.append(f"    class {_typed_node_id('skill', skill)} skillNode")
    for agent in agent_nodes:
        lines.append(f"    class {_typed_node_id('agent', agent)} agentNode")
    for knowledge in knowledge_nodes:
        lines.append(f"    class {_typed_node_id('knowledge', knowledge)} knowledgeNode")
    return _mermaid_block(lines)


def _extract_phases(skill_body: str) -> list[str]:
    """Extract phase numbers from skill body headings."""
    phase_pattern = re.compile(r"^## Phase\s+([\d.]+)", re.MULTILINE)
    phases = [match.group(1) for match in phase_pattern.finditer(skill_body)]
    return sorted(set(phases), key=lambda x: (float(x.split(".")[0]), float(x.split(".")[1] if "." in x else "0")))


def render_skill_drilldown(inv: Inventory, skill_name: str) -> str:
    skill_refs = _sorted_destinations(_internal_skill_edges(inv), skill_name)
    agent_refs = _sorted_destinations(_internal_skill_agent_edges(inv), skill_name)
    knowledge_refs = _sorted_destinations(_internal_skill_knowledge_edges(inv), skill_name)
    artifact_refs = _sorted_destinations(inv.skill_to_artifact, skill_name)
    phases = _extract_phases(inv.skill_bodies.get(skill_name, ""))

    lines = [
        "flowchart LR",
        "    classDef skillNode fill:#dbeafe,stroke:#2563eb,color:#1e3a5f,font-weight:bold",
        "    classDef agentNode fill:#d1fae5,stroke:#059669,color:#064e3b,font-weight:bold",
        "    classDef knowledgeNode fill:#fef3c7,stroke:#d97706,color:#78350f,font-weight:bold",
        "    classDef artifactNode fill:#ede9fe,stroke:#7c3aed,color:#4c1d95,font-weight:bold",
        "    classDef phaseNode fill:#e0e7ff,stroke:#6366f1,color:#312e81,font-weight:bold",
        "",
        f"    {_typed_node_id('skill', skill_name)}[{skill_name}]",
    ]

    for phase in phases:
        phase_id = f"Phase{phase.replace('.', '_')}"
        lines.append(f"    {phase_id}[\"Phase {phase}\"]")
    for other_skill in skill_refs:
        lines.append(f"    {_typed_node_id('skill', other_skill)}[{other_skill}]")
    for agent in agent_refs:
        lines.append(f"    {_typed_node_id('agent', agent)}[{agent}]")
    for knowledge in knowledge_refs:
        lines.append(f"    {_typed_node_id('knowledge', knowledge)}[{knowledge[:-3]}]")
    for artifact in artifact_refs:
        lines.append(f"    {_typed_node_id('artifact', artifact)}[.dev/{artifact}]")

    lines.append("")
    for phase in phases:
        phase_id = f"Phase{phase.replace('.', '_')}"
        lines.append(f"    {_typed_node_id('skill', skill_name)} --> {phase_id}")
    for other_skill in skill_refs:
        lines.append(f"    {_typed_node_id('skill', skill_name)} -.-> {_typed_node_id('skill', other_skill)}")
    for agent in agent_refs:
        lines.append(f"    {_typed_node_id('skill', skill_name)} --> {_typed_node_id('agent', agent)}")
    for knowledge in knowledge_refs:
        lines.append(f"    {_typed_node_id('skill', skill_name)} --> {_typed_node_id('knowledge', knowledge)}")
    for artifact in artifact_refs:
        lines.append(f"    {_typed_node_id('skill', skill_name)} --> {_typed_node_id('artifact', artifact)}")

    lines.append("")
    lines.append(f"    class {_typed_node_id('skill', skill_name)} skillNode")
    for phase in phases:
        phase_id = f"Phase{phase.replace('.', '_')}"
        lines.append(f"    class {phase_id} phaseNode")
    for other_skill in skill_refs:
        lines.append(f"    class {_typed_node_id('skill', other_skill)} skillNode")
    for agent in agent_refs:
        lines.append(f"    class {_typed_node_id('agent', agent)} agentNode")
    for knowledge in knowledge_refs:
        lines.append(f"    class {_typed_node_id('knowledge', knowledge)} knowledgeNode")
    for artifact in artifact_refs:
        lines.append(f"    class {_typed_node_id('artifact', artifact)} artifactNode")

    body = _mermaid_block(lines)
    if agent_refs:
        agents_line = ", ".join(f"`al-dev-shared:{agent}`" for agent in agent_refs)
        body += f"\n\nAgents spawned: {agents_line}"
    return body


RENDERERS: dict[str, Callable[..., str]] = {
    "render_skill_lifecycle": render_skill_lifecycle,
    "render_agent_catalog": render_agent_catalog,
    "render_plugin_dependency": render_plugin_dependency,
    "render_plugin_workflow_overlays": render_plugin_workflow_overlays,
    "render_plugin_health_callouts": render_plugin_health_callouts,
    "render_workflow_skills_agents": render_workflow_skills_agents,
    "render_workflow_knowledge": render_workflow_knowledge,
    "render_skill_drilldown": render_skill_drilldown,
    "render_agent_coverage": render_agent_coverage,
    "render_skill_coverage": render_skill_coverage,
}


def build_section_registry(inv: Inventory) -> dict[str, SectionSpec]:
    registry: dict[str, SectionSpec] = {}
    for key, config in SECTION_CONFIG.items():
        registry[key] = SectionSpec(
            key=key,
            doc=Path(config["doc"]),
            renderer_name=str(config["renderer"]),
        )
    for skill_name in inv.skills:
        key = f"{SKILL_DRILLDOWN_PREFIX}{skill_name}"
        registry[key] = SectionSpec(
            key=key,
            doc=Path("docs/al-dev-skills-map.md"),
            renderer_name="render_skill_drilldown",
            context=skill_name,
        )
    return registry


def build_all_sections(inv: Inventory) -> dict[str, str]:
    rendered: dict[str, str] = {}
    for key, spec in build_section_registry(inv).items():
        renderer = RENDERERS[spec.renderer_name]
        body = renderer(inv) if spec.context is None else renderer(inv, spec.context)
        rendered[key] = _wrap_generated_section(key, body)
    return rendered


def build_plugin_graph_document(
    inv: Inventory,
    *,
    today: str,
    generated_by: str = "scripts/generate-plugin-graph.py",
    workflow_paths: Optional[dict[str, list[str]]] = None,
) -> str:
    return (
        "# Plugin Dependency Graph\n\n"
        f"> Generated by `{generated_by}` on {today}.\n"
        "> Re-run the script (or `/plugin-health`) to refresh. Do not hand-edit.\n\n"
        "## Dependency graph\n\n"
        f"{render_plugin_dependency(inv)}\n\n"
        "## Workflow-path overlays\n\n"
        f"{render_plugin_workflow_overlays(inv, workflow_paths=workflow_paths)}\n\n"
        "## Health callouts\n\n"
        f"{render_plugin_health_callouts(inv, workflow_paths=workflow_paths)}\n"
    )


def plan_document_updates(repo: Path, rendered: dict[str, str], inv: Inventory) -> dict[Path, str]:
    updates: dict[Path, str] = {}
    registry = build_section_registry(inv)
    doc_to_keys: dict[Path, list[str]] = {}
    for key, spec in registry.items():
        doc_to_keys.setdefault(spec.doc, []).append(key)

    for rel_path in TARGET_DOCS:
        path = repo / rel_path
        text = _read_text(path)
        spans = find_marker_spans(text)
        expected_keys = sorted(doc_to_keys.get(rel_path, []))
        required_keys = [key for key in expected_keys if key in SECTION_CONFIG]
        drilldown_expected = [key for key in expected_keys if key.startswith(SKILL_DRILLDOWN_PREFIX)]
        drilldown_present = sorted(key for key in spans if key.startswith(SKILL_DRILLDOWN_PREFIX))
        stale_drilldowns = sorted(set(drilldown_present) - set(drilldown_expected))
        if stale_drilldowns:
            raise KeyError(f"{rel_path}: stale drilldown markers: {stale_drilldowns}")

        if rel_path == SKILLS_MAP_DOC and DRILLDOWN_LAYER_HEADING in text:
            required_keys.extend(drilldown_expected)
        missing_keys = sorted(set(required_keys) - set(spans))
        if missing_keys:
            raise KeyError(f"{rel_path}: missing markers for sections: {missing_keys}")
        replacements = {key: rendered[key] for key in sorted(set(required_keys))}
        updates[path] = replace_marked_sections(text, replacements)
    return updates


def generate_document_updates(repo: Path) -> dict[Path, str]:
    """Prepare map-document updates without mutating any files."""
    inv = collect_inventory(repo / "profile-al-dev-shared")
    validate_inventory_skill_references(inv)
    _validate_inventory_for_rendering(inv)
    rendered = build_all_sections(inv)
    return plan_document_updates(repo, rendered, inv)


def apply_document_updates(updates: dict[Path, str]) -> None:
    """Write all prepared document updates atomically."""
    backup_paths: dict[Path, Path] = {}
    committed: list[Path] = []
    try:
        for path, new_text in updates.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(
                "wb",
                dir=path.parent,
                prefix=f".{path.name}.",
                suffix=".bak",
                delete=False,
            ) as handle:
                backup_path = Path(handle.name)
            shutil.copy2(path, backup_path)
            backup_paths[path] = backup_path
            write_text_atomic(path, new_text)
            committed.append(path)

    except Exception:
        for path in reversed(committed):
            write_text_atomic(path, backup_paths[path].read_text(encoding="utf-8"))
        raise
    finally:
        for backup_path in backup_paths.values():
            if backup_path.exists():
                backup_path.unlink()


__all__ = [
    "DRILLDOWN_LAYER_HEADING",
    "LIFECYCLE_BRANCHES",
    "RENDERERS",
    "SECTION_CONFIG",
    "SKILLS_MAP_DOC",
    "SKILL_DRILLDOWN_PREFIX",
    "TARGET_DOCS",
    "_internal_agent_knowledge_edges",
    "_internal_skill_agent_edges",
    "_internal_skill_edges",
    "_internal_skill_knowledge_edges",
    "apply_document_updates",
    "build_all_sections",
    "build_plugin_graph_document",
    "build_section_registry",
    "generate_document_updates",
    "plan_document_updates",
    "render_agent_catalog",
    "render_agent_coverage",
    "render_plugin_dependency",
    "render_plugin_health_callouts",
    "render_plugin_workflow_overlays",
    "render_skill_coverage",
    "render_skill_drilldown",
    "render_skill_lifecycle",
    "render_workflow_knowledge",
    "render_workflow_skills_agents",
]
