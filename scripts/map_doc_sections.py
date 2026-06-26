"""Shared inventory and generated-section helpers for map documents."""

from dataclasses import dataclass, field
from pathlib import Path
import re
import shutil
import tempfile
from typing import Callable, Iterable, Match, Optional

import yaml


AGENT_REF = re.compile(r"al-dev-shared:(al-dev-[a-z0-9-]+)")
BARE_AGENT_REF = re.compile(r"\b(al-dev-[a-z0-9-]+)\b")
SKILL_REF = re.compile(r"(?<![A-Za-z0-9_.-])/([a-z][a-z0-9-]+)\b")
KNOWLEDGE_REF = re.compile(r"knowledge/([a-z0-9-]+\.md)")
ARTIFACT_REF = re.compile(r"\.dev/([A-Za-z0-9._-]+\.[A-Za-z0-9_-]+)")
BEGIN_RE = re.compile(r"<!-- BEGIN GENERATED: ([a-z0-9-]+) -->")
END_RE = re.compile(r"<!-- END GENERATED: ([a-z0-9-]+) -->")

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

WORKFLOW_ORDER: dict[str, list[str]] = {
    "development-spine": [
        "al-dev-plan",
        "al-dev-develop",
        "al-dev-review-develop",
        "al-dev-commit",
    ],
    "ticket-support": [
        "al-dev-ticket",
        "al-dev-support-reply",
    ],
    "direct-fix": [
        "al-dev-fix",
        "al-dev-commit",
    ],
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
SKILL_RELATION_HINTS = (
    "spawn",
    "run ",
    "re-run ",
    "use ",
    "uses ",
    "dispatch",
    "chain",
    "continue",
    "suggest",
    "skip",
    "proceed",
    "next step",
    "recommend",
    "route",
    "handled by",
    "orchestrates",
    "return here later with",
    "before ",
    "after ",
    " then ",
    "follow-up",
    "resume",
    "first",
)
AGENT_RELATION_HINTS = (
    "spawn",
    "agent:",
    "dispatch",
    "teammate",
    "teammates",
    "developer",
    "architect",
    "reviewer",
    "specialist",
    "analysis agent",
    "support-reply-drafter",
    "diagnostics-fixer",
)
SHELLISH_HINTS = (
    "$(",
    "2>/dev/null",
    ">/dev/null",
    "tail -1",
    "sort |",
    " ls ",
    " cp ",
    " cat ",
    " mkdir ",
    " grep ",
    "al-compile",
    "al compile",
    "/project:",
    "/packagecachepath:",
    "/errorlog:",
)
IGNORED_EXTERNAL_SKILL_REFS = frozenset(
    {
        "al-dev-init-context",
        "validate-plugin-neutrality",
        "analyze-agent-design",
        "analyze-skill-design",
        "audit-knowledge-quality",
        "interview",
        "plan",
        "superpowers",
    }
)


@dataclass(frozen=True)
class AgentMeta:
    name: str
    model: str
    tools: tuple[str, ...]
    description: str
    path: Path


@dataclass(frozen=True)
class Inventory:
    skills: list[str]
    agents: list[str]
    knowledge: list[str]
    agent_meta: dict[str, AgentMeta]
    skill_to_skill: list[tuple[str, str]]
    skill_to_agent: list[tuple[str, str]]
    skill_to_knowledge: list[tuple[str, str]]
    agent_to_knowledge: list[tuple[str, str]]
    skill_to_artifact: list[tuple[str, str]]
    skill_bodies: dict[str, str] = field(default_factory=dict)
    skill_descriptions: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class MarkerSpan:
    key: str
    start: int
    end: int
    begin_start: int
    begin_end: int
    end_start: int
    end_end: int


@dataclass(frozen=True)
class SectionSpec:
    key: str
    doc: Path
    renderer_name: str
    context: Optional[str] = None


@dataclass(frozen=True)
class _OpenMarker:
    key: str
    begin_start: int
    begin_end: int


def dedupe_sorted(edges: Iterable[tuple[str, str]]) -> list[tuple[str, str]]:
    """Return deterministic edge order."""
    return sorted(set(edges), key=lambda item: (item[0], item[1]))


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _parse_frontmatter(path: Path) -> tuple[dict, str]:
    text = _read_text(path)
    match = re.match(r"^---\n(.*?)\n---\n?", text, re.DOTALL)
    if not match:
        raise ValueError(f"{path}: missing or malformed frontmatter")
    try:
        data = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError as exc:
        raise ValueError(f"{path}: invalid YAML frontmatter: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"{path}: frontmatter must be a mapping")
    return data, text[match.end():]


def _split_optional_frontmatter(path: Path) -> tuple[dict, str]:
    text = _read_text(path)
    match = re.match(r"^---\n(.*?)\n---\n?", text, re.DOTALL)
    if not match:
        return {}, text
    try:
        data = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError as exc:
        raise ValueError(f"{path}: invalid YAML frontmatter: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"{path}: frontmatter must be a mapping")
    return data, text[match.end():]


def _parse_agent_meta(path: Path) -> AgentMeta:
    data, _body = _parse_frontmatter(path)
    required = ("name", "description", "model", "tools")
    missing = [key for key in required if key not in data]
    if missing:
        raise ValueError(f"{path}: frontmatter missing required keys: {', '.join(missing)}")

    tools = data["tools"]
    if not isinstance(tools, list) or any(not isinstance(tool, str) for tool in tools):
        raise ValueError(f"{path}: frontmatter tools must be a list of strings")

    name = data["name"]
    description = data["description"]
    model = data["model"]
    if not all(isinstance(value, str) and value for value in (name, description, model)):
        raise ValueError(f"{path}: frontmatter name, description, and model must be non-empty strings")

    if path.stem != name:
        raise ValueError(f"{path}: frontmatter name does not match filename")

    return AgentMeta(
        name=name,
        model=model,
        tools=tuple(tools),
        description=description,
        path=path,
    )


def _discover_skills(plugin_dir: Path) -> list[str]:
    return sorted(path.parent.name for path in (plugin_dir / "skills").glob("*/SKILL.md"))


def _discover_agents(plugin_dir: Path) -> list[str]:
    return sorted(path.stem for path in (plugin_dir / "agents").glob("*.md"))


def _discover_knowledge(plugin_dir: Path) -> list[str]:
    return sorted(path.name for path in (plugin_dir / "knowledge").glob("*.md"))


def _looks_like_shell_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    if stripped.startswith("```"):
        return True
    if stripped.startswith(("ls ", "cp ", "cat ", "mkdir ", "grep ", "echo ", "al-compile", "al compile")):
        return True
    upper = stripped.upper()
    if "=" in stripped and upper == stripped and any(ch.isalpha() for ch in upper.split("=", 1)[0]):
        return True
    lower = f" {stripped.lower()} "
    return any(hint in lower or hint in stripped for hint in SHELLISH_HINTS)


def _line_allows_skill_refs(line: str) -> bool:
    stripped = line.strip()
    if not stripped or stripped.startswith("|") or stripped.startswith("/"):
        return False
    if _looks_like_shell_line(stripped):
        return False
    lower = stripped.lower()
    if " /" not in f" {stripped}":
        return False
    return any(hint in lower for hint in SKILL_RELATION_HINTS) or "→ /" in stripped or "-> /" in stripped


def _line_allows_bare_agent_refs(line: str) -> bool:
    stripped = line.strip()
    if not stripped or stripped.startswith("|"):
        return False
    if _looks_like_shell_line(stripped):
        return False
    lower = stripped.lower()
    return any(hint in lower for hint in AGENT_RELATION_HINTS)


def _extract_bare_agent_refs(text: str, agent_set: set[str]) -> set[str]:
    found: set[str] = set()
    for line in text.splitlines():
        if not _line_allows_bare_agent_refs(line):
            continue
        for candidate in BARE_AGENT_REF.findall(line):
            if candidate in agent_set:
                found.add(candidate)
    return found


def _extract_skill_refs(
    skill_name: str,
    text: str,
    *,
    agent_set: set[str],
) -> tuple[set[tuple[str, str]], set[tuple[str, str]], set[tuple[str, str]], set[tuple[str, str]]]:
    skill_to_agent = {(skill_name, dst) for dst in AGENT_REF.findall(text)}
    skill_to_agent.update((skill_name, dst) for dst in _extract_bare_agent_refs(text, agent_set))

    skill_to_skill: set[tuple[str, str]] = set()
    for line in text.splitlines():
        if not _line_allows_skill_refs(line):
            continue
        for dst in SKILL_REF.findall(line):
            if dst != skill_name:
                skill_to_skill.add((skill_name, dst))

    skill_to_knowledge = {(skill_name, dst) for dst in KNOWLEDGE_REF.findall(text)}
    skill_to_artifact = {(skill_name, dst) for dst in ARTIFACT_REF.findall(text)}
    return skill_to_agent, skill_to_skill, skill_to_knowledge, skill_to_artifact


def _extract_agent_knowledge(agent_name: str, text: str) -> set[tuple[str, str]]:
    return {(agent_name, dst) for dst in KNOWLEDGE_REF.findall(text)}


def find_missing_references(
    skills: list[str],
    agents: list[str],
    knowledge: list[str],
    skill_to_skill: Iterable[tuple[str, str]],
    skill_to_agent: Iterable[tuple[str, str]],
    skill_to_knowledge: Iterable[tuple[str, str]],
    agent_to_knowledge: Iterable[tuple[str, str]],
) -> list[str]:
    skill_set = set(skills)
    agent_set = set(agents)
    knowledge_set = set(knowledge)

    missing: list[str] = []
    for src, dst in skill_to_skill:
        if src not in skill_set or (dst not in skill_set and dst not in IGNORED_EXTERNAL_SKILL_REFS):
            missing.append(f"skill reference {src} -> {dst}")
    for src, dst in skill_to_agent:
        if src not in skill_set or dst not in agent_set:
            missing.append(f"agent reference {src} -> {dst}")
    for src, dst in skill_to_knowledge:
        if src not in skill_set or dst not in knowledge_set:
            missing.append(f"knowledge reference {src} -> {dst}")
    for src, dst in agent_to_knowledge:
        if src not in agent_set or dst not in knowledge_set:
            missing.append(f"knowledge reference {src} -> {dst}")
    return sorted(missing)


def validate_inventory_references(inv: Inventory) -> None:
    """Fail closed when source-derived refs point at missing inventory items."""
    missing = find_missing_references(
        skills=inv.skills,
        agents=inv.agents,
        knowledge=inv.knowledge,
        skill_to_skill=inv.skill_to_skill,
        skill_to_agent=inv.skill_to_agent,
        skill_to_knowledge=inv.skill_to_knowledge,
        agent_to_knowledge=inv.agent_to_knowledge,
    )
    if missing:
        raise ValueError(f"inventory contains missing references: {'; '.join(missing)}")


def validate_inventory_skill_references(inv: Inventory) -> None:
    """Fail closed on missing internal skill refs exposed by extraction."""
    skill_set = set(inv.skills)
    missing = sorted(
        f"skill reference {src} -> {dst}"
        for src, dst in inv.skill_to_skill
        if src not in skill_set or (dst not in skill_set and dst not in IGNORED_EXTERNAL_SKILL_REFS)
    )
    if missing:
        raise ValueError(f"inventory contains missing references: {'; '.join(missing)}")


def collect_inventory(plugin_dir: Path) -> Inventory:
    """Discover plugin inventory and source-derived references deterministically."""
    skills = _discover_skills(plugin_dir)
    agents = _discover_agents(plugin_dir)
    knowledge = _discover_knowledge(plugin_dir)
    skill_set = set(skills)
    agent_set = set(agents)

    agent_meta: dict[str, AgentMeta] = {}
    skill_bodies: dict[str, str] = {}
    skill_descriptions: dict[str, str] = {}
    skill_to_skill: set[tuple[str, str]] = set()
    skill_to_agent: set[tuple[str, str]] = set()
    skill_to_knowledge: set[tuple[str, str]] = set()
    agent_to_knowledge: set[tuple[str, str]] = set()
    skill_to_artifact: set[tuple[str, str]] = set()

    for agent_name in agents:
        path = plugin_dir / "agents" / f"{agent_name}.md"
        agent_meta[agent_name] = _parse_agent_meta(path)
        agent_to_knowledge.update(_extract_agent_knowledge(agent_name, _read_text(path)))

    for skill_name in skills:
        path = plugin_dir / "skills" / skill_name / "SKILL.md"
        data, body = _split_optional_frontmatter(path)
        skill_bodies[skill_name] = body
        description = data.get("description", "")
        skill_descriptions[skill_name] = description if isinstance(description, str) else ""
        refs = _extract_skill_refs(
            skill_name,
            _read_text(path),
            agent_set=agent_set,
        )
        skill_to_agent.update(refs[0])
        skill_to_skill.update(refs[1])
        skill_to_knowledge.update(refs[2])
        skill_to_artifact.update(refs[3])

    return Inventory(
        skills=skills,
        agents=agents,
        knowledge=knowledge,
        agent_meta=agent_meta,
        skill_to_skill=dedupe_sorted(skill_to_skill),
        skill_to_agent=dedupe_sorted(skill_to_agent),
        skill_to_knowledge=dedupe_sorted(skill_to_knowledge),
        agent_to_knowledge=dedupe_sorted(agent_to_knowledge),
        skill_to_artifact=dedupe_sorted(skill_to_artifact),
        skill_bodies=skill_bodies,
        skill_descriptions=skill_descriptions,
    )


def find_marker_spans(text: str) -> dict[str, MarkerSpan]:
    """Find validated generated-section spans in document text."""
    events: list[tuple[int, str, str, Match[str]]] = []
    for match in BEGIN_RE.finditer(text):
        events.append((match.start(), "begin", match.group(1), match))
    for match in END_RE.finditer(text):
        events.append((match.start(), "end", match.group(1), match))
    events.sort(key=lambda item: (item[0], 0 if item[1] == "begin" else 1))

    spans: dict[str, MarkerSpan] = {}
    open_marker: Optional[_OpenMarker] = None

    for _pos, kind, key, match in events:
        if kind == "begin":
            if key in spans or (open_marker is not None and open_marker.key == key):
                raise ValueError(f"duplicate marker key: {key}")
            if open_marker is not None:
                raise ValueError(f"overlapping marker spans: {open_marker.key} and {key}")
            open_marker = _OpenMarker(key=key, begin_start=match.start(), begin_end=match.end())
            continue

        if open_marker is None:
            raise ValueError(f"end marker without matching begin marker: {key}")
        if open_marker.key != key:
            raise ValueError(f"mismatched marker keys: begin {open_marker.key}, end {key}")

        spans[key] = MarkerSpan(
            key=key,
            start=open_marker.begin_start,
            end=match.end(),
            begin_start=open_marker.begin_start,
            begin_end=open_marker.begin_end,
            end_start=match.start(),
            end_end=match.end(),
        )
        open_marker = None

    if open_marker is not None:
        raise ValueError(f"begin marker without matching end marker: {open_marker.key}")

    return spans


def replace_marked_sections(text: str, replacements: dict[str, str]) -> str:
    spans = find_marker_spans(text)
    unknown = set(replacements) - set(spans)
    if unknown:
        raise KeyError(f"unknown section keys: {sorted(unknown)}")

    output = text
    for key, span in reversed(sorted(spans.items(), key=lambda item: item[1].start)):
        if key not in replacements:
            continue
        output = output[:span.start] + replacements[key] + output[span.end:]
    return output


def mermaid_node_id(name: str) -> str:
    node_id = re.sub(r"[^A-Za-z0-9_]", "_", name)
    if not node_id:
        raise ValueError("empty Mermaid node id")
    return node_id


def assert_unique_node_ids(names: list[str]) -> None:
    ids: dict[str, str] = {}
    for name in names:
        key = mermaid_node_id(name)
        if key in ids and ids[key] != name:
            raise ValueError(f"duplicate Mermaid node id: {ids[key]} vs {name}")
        ids[key] = name


def _typed_node_id(kind: str, name: str) -> str:
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


def summarize_plugin_health(
    inv: Inventory,
    workflow_paths: Optional[dict[str, list[str]]] = None,
) -> dict[str, list]:
    workflow_paths = workflow_paths or WORKFLOW_ORDER
    skill_agent_edges = _internal_skill_agent_edges(inv)
    skill_knowledge_edges = _internal_skill_knowledge_edges(inv)
    agent_knowledge_edges = _internal_agent_knowledge_edges(inv)

    spawned = {dst for _, dst in skill_agent_edges}
    orphan_agents = sorted(agent for agent in inv.agents if agent not in spawned)

    referenced_knowledge = {dst for _, dst in skill_knowledge_edges} | {
        dst for _, dst in agent_knowledge_edges
    }
    dead_knowledge = sorted(knowledge for knowledge in inv.knowledge if knowledge not in referenced_knowledge)

    on_path = {skill for path in workflow_paths.values() for skill in path}
    offpath_skills = sorted(skill for skill in inv.skills if skill not in on_path)

    skill_set = set(inv.skills)
    agent_set = set(inv.agents)
    knowledge_set = set(inv.knowledge)
    missing_refs: set[tuple[str, str]] = set()
    for _, dst in inv.skill_to_skill:
        if dst not in skill_set and dst not in IGNORED_EXTERNAL_SKILL_REFS:
            missing_refs.add(("skill", dst))
    for _, dst in inv.skill_to_agent:
        if dst not in agent_set:
            missing_refs.add(("agent", dst))
    for _, dst in inv.skill_to_knowledge:
        if dst not in knowledge_set:
            missing_refs.add(("knowledge", dst))
    for _, dst in inv.agent_to_knowledge:
        if dst not in knowledge_set:
            missing_refs.add(("knowledge", dst))

    return {
        "orphan_agents": orphan_agents,
        "dead_knowledge": dead_knowledge,
        "offpath_skills": offpath_skills,
        "missing_refs": sorted(missing_refs),
    }


def _mermaid_block(lines: Iterable[str]) -> str:
    return "```mermaid\n" + "\n".join(lines).rstrip() + "\n```"


def _wrap_generated_section(key: str, body: str) -> str:
    return f"<!-- BEGIN GENERATED: {key} -->\n{body.rstrip()}\n<!-- END GENERATED: {key} -->"


def _format_overlay_title(key: str) -> str:
    return key.replace("-", " ").title()


def _sorted_destinations(edges: Iterable[tuple[str, str]], source: str) -> list[str]:
    return sorted(dst for src, dst in edges if src == source)


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
    """Extract phase numbers from skill body (e.g., '## Phase 0', '## Phase 1.5').

    Parses skill SKILL.md bodies for Phase heading markers and returns a sorted
    list of phase numbers (as strings). Used by render_skill_drilldown() to
    generate Phase<N> nodes in Layer 2 Mermaid diagrams.

    Phases are sorted numerically by integer and decimal parts separately to
    ensure natural ordering (0, 0.5, 1, 1.5, etc.) regardless of string form.
    """
    phase_pattern = re.compile(r"^## Phase\s+([\d.]+)", re.MULTILINE)
    phases = []
    for match in phase_pattern.finditer(skill_body):
        phase_num = match.group(1)
        phases.append(phase_num)
    return sorted(set(phases), key=lambda x: (float(x.split('.')[0]), float(x.split('.')[1] if '.' in x else '0')))


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
    temp_paths: dict[Path, Path] = {}
    backup_paths: dict[Path, Path] = {}
    committed: list[Path] = []
    try:
        for path, new_text in updates.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(
                "w",
                encoding="utf-8",
                dir=path.parent,
                prefix=f".{path.name}.",
                suffix=".tmp",
                delete=False,
            ) as handle:
                handle.write(new_text)
                temp_paths[path] = Path(handle.name)
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

        try:
            for path in updates:
                temp_paths[path].replace(path)
                committed.append(path)
        except Exception:
            for path in reversed(committed):
                backup_paths[path].replace(path)
            raise
    finally:
        for temp_path in temp_paths.values():
            if temp_path.exists():
                temp_path.unlink()
        for backup_path in backup_paths.values():
            if backup_path.exists():
                backup_path.unlink()
