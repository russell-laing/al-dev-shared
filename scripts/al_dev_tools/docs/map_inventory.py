"""Inventory and shared model helpers for map documents."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re
from typing import Iterable, Optional

from scripts.al_dev_tools.markdown_frontmatter import (
    parse_optional_frontmatter,
    parse_required_frontmatter,
)


AGENT_REF = re.compile(r"al-dev-shared:(al-dev-[a-z0-9-]+)")
BARE_AGENT_REF = re.compile(r"\b(al-dev-[a-z0-9-]+)\b")
SKILL_REF = re.compile(r"(?<![A-Za-z0-9_.-])/([a-z][a-z0-9-]+)\b")
KNOWLEDGE_REF = re.compile(r"knowledge/([a-z0-9-]+\.md)")
ARTIFACT_REF = re.compile(r"\.dev/([A-Za-z0-9._-]+\.[A-Za-z0-9_-]+)")

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


def dedupe_sorted(edges: Iterable[tuple[str, str]]) -> list[tuple[str, str]]:
    """Return deterministic edge order."""
    return sorted(set(edges), key=lambda item: (item[0], item[1]))


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _parse_frontmatter(path: Path) -> tuple[dict, str]:
    text = _read_text(path)
    try:
        data, body = parse_required_frontmatter(text)
    except ValueError as exc:
        raise ValueError(f"{path}: {exc}") from exc
    return data, body


def _split_optional_frontmatter(path: Path) -> tuple[dict, str]:
    text = _read_text(path)
    try:
        data, body = parse_optional_frontmatter(text)
    except ValueError as exc:
        raise ValueError(f"{path}: {exc}") from exc
    return data, body


def _parse_agent_meta(path: Path) -> AgentMeta:
    data, _body = _parse_frontmatter(path)
    required = ("name", "description", "model")
    missing = [key for key in required if key not in data]
    if missing:
        raise ValueError(f"{path}: frontmatter missing required keys: {', '.join(missing)}")

    tools = data.get("tools", [])
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


def summarize_plugin_health(
    inv: Inventory,
    workflow_paths: Optional[dict[str, list[str]]] = None,
) -> dict[str, list]:
    workflow_paths = workflow_paths or WORKFLOW_ORDER
    spawned = {dst for _, dst in inv.skill_to_agent if dst in set(inv.agents)}
    orphan_agents = sorted(agent for agent in inv.agents if agent not in spawned)

    skill_knowledge_edges = [
        (src, dst) for src, dst in inv.skill_to_knowledge if src in set(inv.skills) and dst in set(inv.knowledge)
    ]
    agent_knowledge_edges = [
        (src, dst) for src, dst in inv.agent_to_knowledge if src in set(inv.agents) and dst in set(inv.knowledge)
    ]
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


__all__ = [
    "AGENT_RELATION_HINTS",
    "AGENT_REF",
    "ARTIFACT_REF",
    "AgentMeta",
    "BARE_AGENT_REF",
    "IGNORED_EXTERNAL_SKILL_REFS",
    "Inventory",
    "KNOWLEDGE_REF",
    "MarkerSpan",
    "SHELLISH_HINTS",
    "SKILL_REF",
    "SKILL_RELATION_HINTS",
    "SectionSpec",
    "WORKFLOW_ORDER",
    "assert_unique_node_ids",
    "collect_inventory",
    "dedupe_sorted",
    "find_missing_references",
    "mermaid_node_id",
    "summarize_plugin_health",
    "validate_inventory_references",
    "validate_inventory_skill_references",
]
