#!/usr/bin/env python3
"""Generate docs/al-dev-plugin-graph.md.

Deterministic structured-grep extraction over profile-al-dev-shared/. Renders a
dependency graph, the three workflow-path overlays, and health callouts (orphans,
dead links, off-path skills, missing refs). Suggestions-only: never edits source.
On a parse error it writes a partial graph with an 'incomplete' banner and exits 0.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PLUGIN = REPO / "profile-al-dev-shared"
OUTPUT = REPO / "docs" / "al-dev-plugin-graph.md"

# The three canonical workflow paths (from CLAUDE.md "Plugin Architecture").
WORKFLOW_PATHS = {
    "Ticket / Support": ["al-dev-ticket", "al-dev-support-reply-drafter"],
    "Development spine": [
        "al-dev-investigate",
        "al-dev-plan",
        "al-dev-develop",
        "al-dev-commit",
    ],
    "Direct fix": ["al-dev-fix"],
}

AGENT_REF = re.compile(r"al-dev-shared:(al-dev-[a-z0-9-]+)")
SKILL_REF = re.compile(r"/([a-z][a-z0-9-]+)")
KNOWLEDGE_REF = re.compile(r"knowledge/([a-z0-9-]+\.md)")
ARTIFACT_REF = re.compile(r"\.dev/([A-Za-z0-9._-]+\.md)")


def node_id(name: str) -> str:
    """Mermaid-safe node id: letters, numbers, underscores only."""
    return re.sub(r"[^A-Za-z0-9_]", "_", name)


def discover(plugin_dir: Path) -> tuple[list[str], list[str], list[str]]:
    skills = sorted(p.parent.name for p in (plugin_dir / "skills").glob("*/SKILL.md"))
    agents = sorted(p.stem for p in (plugin_dir / "agents").glob("*.md"))
    knowledge = sorted(p.name for p in (plugin_dir / "knowledge").glob("*.md"))
    return skills, agents, knowledge


def extract_edges(plugin_dir: Path, skills: list[str]) -> dict[str, set[tuple[str, str]]]:
    edges: dict[str, set[tuple[str, str]]] = {
        "skill_agent": set(),
        "skill_skill": set(),
        "skill_knowledge": set(),
        "agent_knowledge": set(),
        "skill_artifact": set(),
    }
    skill_set = set(skills)
    for skill_md in (plugin_dir / "skills").glob("*/SKILL.md"):
        src = skill_md.parent.name
        text = skill_md.read_text(encoding="utf-8")
        for dst in AGENT_REF.findall(text):
            edges["skill_agent"].add((src, dst))
        for dst in SKILL_REF.findall(text):
            if dst != src and dst in skill_set:
                edges["skill_skill"].add((src, dst))
        for dst in KNOWLEDGE_REF.findall(text):
            edges["skill_knowledge"].add((src, dst))
        for dst in ARTIFACT_REF.findall(text):
            edges["skill_artifact"].add((src, dst))
    for agent_md in (plugin_dir / "agents").glob("*.md"):
        src = agent_md.stem
        text = agent_md.read_text(encoding="utf-8")
        for dst in KNOWLEDGE_REF.findall(text):
            edges["agent_knowledge"].add((src, dst))
    return edges


def find_health(
    skills: list[str],
    agents: list[str],
    knowledge_on_disk: list[str],
    edges: dict[str, set[tuple[str, str]]],
) -> dict[str, list]:
    spawned = {dst for _, dst in edges["skill_agent"]}
    orphan_agents = sorted(a for a in agents if a not in spawned)

    referenced_knowledge = {dst for _, dst in edges["skill_knowledge"]} | {
        dst for _, dst in edges["agent_knowledge"]
    }
    dead_knowledge = sorted(k for k in knowledge_on_disk if k not in referenced_knowledge)

    on_path = {s for path in WORKFLOW_PATHS.values() for s in path}
    offpath_skills = sorted(s for s in skills if s not in on_path)

    agent_set, skill_set, knowledge_set = set(agents), set(skills), set(knowledge_on_disk)
    missing: set[tuple[str, str]] = set()
    for _, dst in edges["skill_agent"]:
        if dst not in agent_set:
            missing.add(("agent", dst))
    for _, dst in edges["skill_skill"]:
        if dst not in skill_set:
            missing.add(("skill", dst))
    for _, dst in edges["skill_knowledge"] | edges["agent_knowledge"]:
        if dst not in knowledge_set:
            missing.add(("knowledge", dst))

    return {
        "orphan_agents": orphan_agents,
        "dead_knowledge": dead_knowledge,
        "offpath_skills": offpath_skills,
        "missing_refs": sorted(missing),
    }


def render_dependency_graph(
    skills: list[str],
    agents: list[str],
    edges: dict[str, set[tuple[str, str]]],
) -> str:
    referenced_knowledge = sorted(
        {dst for _, dst in edges["skill_knowledge"]}
        | {dst for _, dst in edges["agent_knowledge"]}
    )
    lines = [
        "```mermaid",
        "flowchart LR",
        "    classDef skillNode fill:#dbeafe,stroke:#2563eb,color:#1e3a5f,font-weight:bold",
        "    classDef agentNode fill:#d1fae5,stroke:#059669,color:#064e3b,font-weight:bold",
        "    classDef knowledgeNode fill:#fef3c7,stroke:#d97706,color:#78350f,font-weight:bold",
        "",
        "    subgraph Skills[Skills]",
    ]
    for s in skills:
        lines.append(f"        {node_id(s)}[{s}]")
    lines.append("    end")
    lines.append("    subgraph Agents[Agents]")
    for a in agents:
        lines.append(f"        {node_id(a)}[{a}]")
    lines.append("    end")
    lines.append("    subgraph Knowledge[Knowledge Files]")
    for k in referenced_knowledge:
        lines.append(f"        {node_id(k)}[{k[:-3]}]")
    lines.append("    end")
    lines.append("")
    for src, dst in sorted(edges["skill_skill"]):
        lines.append(f"    {node_id(src)} --> {node_id(dst)}")
    for src, dst in sorted(edges["skill_agent"]):
        lines.append(f"    {node_id(src)} --> {node_id(dst)}")
    for src, dst in sorted(edges["skill_knowledge"] | edges["agent_knowledge"]):
        if dst in referenced_knowledge:
            lines.append(f"    {node_id(src)} --> {node_id(dst)}")
    lines.append("")
    for s in skills:
        lines.append(f"    class {node_id(s)} skillNode")
    for a in agents:
        lines.append(f"    class {node_id(a)} agentNode")
    for k in referenced_knowledge:
        lines.append(f"    class {node_id(k)} knowledgeNode")
    lines.append("```")
    return "\n".join(lines)


def render_workflow_overlays() -> str:
    blocks = []
    for title, path in WORKFLOW_PATHS.items():
        lines = ["```mermaid", "flowchart LR"]
        for i in range(len(path) - 1):
            lines.append(f"    {node_id(path[i])}[{path[i]}] --> {node_id(path[i + 1])}[{path[i + 1]}]")
        if len(path) == 1:
            lines.append(f"    {node_id(path[0])}[{path[0]}]")
        lines.append("```")
        blocks.append(f"### {title}\n\n" + "\n".join(lines))
    return "\n\n".join(blocks)


def render_health(health: dict[str, list]) -> str:
    def section(title: str, items: list[str]) -> str:
        if not items:
            return f"**{title}:** none\n"
        body = "\n".join(f"- `{i}`" for i in items)
        return f"**{title}:**\n\n{body}\n"

    missing = [f"{kind}: {name}" for kind, name in health["missing_refs"]]
    parts = [
        section("Orphan agents (spawned by no skill)", health["orphan_agents"]),
        section("Dead knowledge (referenced by nothing)", health["dead_knowledge"]),
        section("Off-path skills (not on any workflow path)", health["offpath_skills"]),
        section("Missing refs (referenced but not on disk)", missing),
    ]
    return "\n".join(parts)


def build_document(skills, agents, knowledge, edges, health, incomplete: bool, today: str) -> str:
    banner = ""
    if incomplete:
        banner = (
            "> Warning: **Incomplete** — the generator hit a parse error and emitted a "
            "partial graph. Re-run after fixing the offending file.\n\n"
        )
    return (
        f"# Plugin Dependency Graph\n\n"
        f"> Generated by `scripts/generate-plugin-graph.py` on {today}.\n"
        f"> Re-run the script (or `/plugin-health`) to refresh. Do not hand-edit.\n\n"
        f"{banner}"
        f"## Dependency graph\n\n"
        f"{render_dependency_graph(skills, agents, edges)}\n\n"
        f"## Workflow-path overlays\n\n"
        f"{render_workflow_overlays()}\n\n"
        f"## Health callouts\n\n"
        f"{render_health(health)}\n"
    )


def main() -> int:
    from datetime import date

    today = date.today().isoformat()
    incomplete = False
    try:
        skills, agents, knowledge = discover(PLUGIN)
        edges = extract_edges(PLUGIN, skills)
        health = find_health(skills, agents, knowledge, edges)
    except Exception as exc:  # noqa: BLE001 — partial graph is the documented fallback
        sys.stderr.write(f"generate-plugin-graph: parse error: {exc}\n")
        skills, agents, knowledge = [], [], []
        edges = {k: set() for k in (
            "skill_agent", "skill_skill", "skill_knowledge", "agent_knowledge", "skill_artifact",
        )}
        health = {"orphan_agents": [], "dead_knowledge": [], "offpath_skills": [], "missing_refs": []}
        incomplete = True

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        build_document(skills, agents, knowledge, edges, health, incomplete, today),
        encoding="utf-8",
    )
    print(f"Wrote {OUTPUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
