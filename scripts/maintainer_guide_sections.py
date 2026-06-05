"""Workflow-contract parsing and generated sections for docs/maintainer-tooling.md.

Library for scripts/generate-maintainer-guide.py. Parses `workflow:` frontmatter
blocks from .claude/skills/*/SKILL.md (excluding archived/), validates them,
computes gap signals, and renders the generated sections of
docs/maintainer-tooling.md. Fail-closed: validation errors raise ValueError
naming the offending skill and field.
"""
from __future__ import annotations

from bisect import insort
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import re

import yaml

STAGES = ("map-sync", "discover", "decide", "derive", "support")
CORE_STAGES = ("map-sync", "discover", "decide", "derive")
STAGE_TITLES = {
    "map-sync": "Map sync",
    "discover": "Discover",
    "decide": "Decide",
    "derive": "Derive",
    "support": "Adjacent tooling",
}
NODE_BUDGET = 15
PLACEHOLDER_RE = re.compile(r"<[^<>]+>|RUN_ID")
EXTERNAL_INPUT_PREFIXES = ("profile-al-dev-shared/", ".claude/")
SKILL_INVOKER_RE = re.compile(r"^skill:([a-z0-9-]+)$")
ALLOWED_WORKFLOW_KEYS = {
    "stage",
    "invoked-by",
    "repeatable",
    "inputs",
    "outputs",
    "next",
    "manual-followup",
}


@dataclass(frozen=True)
class WorkflowContract:
    skill: str
    stage: str
    invoked_by: str
    repeatable: bool
    inputs: tuple[str, ...]
    outputs: tuple[str, ...]
    next_skills: tuple[str, ...]
    manual_followup: str | None
    description: str


def _read_frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n?", text, re.DOTALL)
    if not match:
        raise ValueError(f"{path}: missing or malformed frontmatter")
    try:
        data = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError as exc:
        raise ValueError(f"{path}: invalid YAML frontmatter: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"{path}: frontmatter must be a mapping")
    return data


def discover_skill_dirs(skills_root: Path) -> list[Path]:
    dirs: list[Path] = []
    for child in sorted(skills_root.iterdir()):
        if not child.is_dir() or child.name == "archived":
            continue
        if (child / "SKILL.md").is_file():
            dirs.append(child)
    return dirs


def _require_string_list(skill: str, field_name: str, value) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, list) or any(
        not isinstance(item, str) or not item.strip() for item in value
    ):
        raise ValueError(f"{skill}: workflow.{field_name} must be a list of non-empty strings")
    return tuple(value)


def parse_contract(skill: str, frontmatter: dict) -> WorkflowContract | None:
    block = frontmatter.get("workflow")
    if block is None:
        return None
    if not isinstance(block, dict):
        raise ValueError(f"{skill}: workflow block must be a mapping")
    unknown = set(block) - ALLOWED_WORKFLOW_KEYS
    if unknown:
        raise ValueError(f"{skill}: workflow block has unknown keys: {', '.join(sorted(unknown))}")
    stage = block.get("stage")
    if stage not in STAGES:
        raise ValueError(
            f"{skill}: workflow.stage must be one of {', '.join(STAGES)} (got {stage!r})"
        )
    invoked_by = block.get("invoked-by")
    if not isinstance(invoked_by, str) or not (
        invoked_by in ("user", "both") or SKILL_INVOKER_RE.match(invoked_by)
    ):
        raise ValueError(
            f"{skill}: workflow.invoked-by must be user, both, or skill:<name> (got {invoked_by!r})"
        )
    repeatable = block.get("repeatable", False)
    if not isinstance(repeatable, bool):
        raise ValueError(f"{skill}: workflow.repeatable must be a boolean")
    manual = block.get("manual-followup")
    if manual is not None and (not isinstance(manual, str) or not manual.strip()):
        raise ValueError(f"{skill}: workflow.manual-followup must be a non-empty string")
    description = frontmatter.get("description", "")
    return WorkflowContract(
        skill=skill,
        stage=stage,
        invoked_by=invoked_by,
        repeatable=repeatable,
        inputs=_require_string_list(skill, "inputs", block.get("inputs")),
        outputs=_require_string_list(skill, "outputs", block.get("outputs")),
        next_skills=_require_string_list(skill, "next", block.get("next")),
        manual_followup=manual,
        description=description if isinstance(description, str) else "",
    )


def load_contracts(skills_root: Path) -> tuple[list[WorkflowContract], list[str]]:
    """Return (contracts, names of active skills without a workflow block), both name-sorted."""
    contracts: list[WorkflowContract] = []
    missing: list[str] = []
    for skill_dir in discover_skill_dirs(skills_root):
        frontmatter = _read_frontmatter(skill_dir / "SKILL.md")
        contract = parse_contract(skill_dir.name, frontmatter)
        if contract is None:
            missing.append(skill_dir.name)
        else:
            contracts.append(contract)
    return contracts, missing


def validate_contracts(contracts: list[WorkflowContract], active_skills: set[str]) -> None:
    errors: list[str] = []
    for contract in contracts:
        invoker = SKILL_INVOKER_RE.match(contract.invoked_by)
        if invoker and invoker.group(1) not in active_skills:
            errors.append(f"{contract.skill}: invoked-by names unknown skill {invoker.group(1)!r}")
        for target in contract.next_skills:
            if target not in active_skills:
                errors.append(f"{contract.skill}: next names unknown skill {target!r}")
    if errors:
        raise ValueError("contract validation failed: " + "; ".join(sorted(errors)))


def normalize_template(template: str) -> str:
    """Replace <placeholder> tokens and the literal RUN_ID with * for matching/globbing."""
    return PLACEHOLDER_RE.sub("*", template)


def producers(contracts: list[WorkflowContract]) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for contract in contracts:
        for output in contract.outputs:
            result.setdefault(normalize_template(output), []).append(contract.skill)
    return {key: sorted(set(value)) for key, value in result.items()}


def consumers(contracts: list[WorkflowContract]) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for contract in contracts:
        for input_path in contract.inputs:
            result.setdefault(normalize_template(input_path), []).append(contract.skill)
    return {key: sorted(set(value)) for key, value in result.items()}


def is_user_invocable(contract: WorkflowContract) -> bool:
    return contract.invoked_by in ("user", "both")


def is_internal_only(contract: WorkflowContract) -> bool:
    return contract.invoked_by.startswith("skill:")


def artifact_status(repo: Path, template: str) -> str:
    """Freshness status: 'latest YYYY-MM-DD', 'never produced', or directory presence."""
    norm = normalize_template(template)
    if norm.endswith("/"):
        return "present" if (repo / norm).is_dir() else "missing"
    if "*" in norm:
        matches = [path for path in repo.glob(norm) if path.is_file()]
        if not matches:
            return "never produced"
        latest = max(path.stat().st_mtime for path in matches)
        return f"latest {datetime.fromtimestamp(latest).date().isoformat()}"
    target = repo / norm
    if not target.is_file():
        return "never produced"
    return f"latest {datetime.fromtimestamp(target.stat().st_mtime).date().isoformat()}"


def compute_gaps(
    contracts: list[WorkflowContract],
    missing_contracts: list[str],
    repo: Path,
) -> dict[str, list[tuple[str, str]]]:
    """The six gap signals, each as (item, detail) rows in deterministic order."""
    prod = producers(contracts)
    cons = consumers(contracts)
    gaps: dict[str, list[tuple[str, str]]] = {
        "orphaned-artifact": [],
        "sourceless-input": [],
        "manual-step": [],
        "missing-contract": [],
        "stale-artifact": [],
        "internal-only": [],
    }
    for norm in sorted(prod):
        if norm not in cons:
            gaps["orphaned-artifact"].append(
                (norm, "produced by " + ", ".join(f"/{s}" for s in prod[norm]) + "; consumed by no skill")
            )
    for norm in sorted(cons):
        if norm in prod:
            continue
        if any(norm.startswith(prefix) for prefix in EXTERNAL_INPUT_PREFIXES):
            continue
        gaps["sourceless-input"].append(
            (norm, "consumed by " + ", ".join(f"/{s}" for s in cons[norm]) + "; produced by no skill")
        )
    for contract in sorted(contracts, key=lambda c: c.skill):
        if contract.manual_followup:
            gaps["manual-step"].append((contract.manual_followup, f"follows /{contract.skill}"))
        if is_internal_only(contract):
            dispatcher = contract.invoked_by.split(":", 1)[1]
            gaps["internal-only"].append((contract.skill, f"dispatched by /{dispatcher}"))
    for name in sorted(missing_contracts):
        gaps["missing-contract"].append((name, "active skill with no workflow contract"))
    for norm in sorted(prod):
        gaps["stale-artifact"].append((norm, artifact_status(repo, norm)))
    return gaps


def _node_id(prefix: str, name: str) -> str:
    return f"{prefix}_" + re.sub(r"[^A-Za-z0-9_]", "_", name)


def _short_label(template: str) -> str:
    """Keep Mermaid node labels under the 30-char style-guide limit."""
    if len(template) <= 30:
        return template
    return ".../" + template.rsplit("/", 1)[-1]


def _mermaid_block(lines: list[str]) -> str:
    return "```mermaid\n" + "\n".join(lines).rstrip() + "\n```"


def _assert_unique_artifact_ids(templates: list[str]) -> None:
    seen: dict[str, str] = {}
    for template in templates:
        key = _node_id("art", template)
        if key in seen and seen[key] != template:
            raise ValueError(f"duplicate Mermaid node id for artifacts: {seen[key]} vs {template}")
        seen[key] = template


def _entry_skills(contracts: list[WorkflowContract]) -> list[WorkflowContract]:
    """User-invocable core-stage skills not named in any same-stage skill's next list."""
    by_name = {c.skill: c for c in contracts}
    same_stage_targets: set[str] = set()
    for contract in contracts:
        for target in contract.next_skills:
            target_contract = by_name.get(target)
            if target_contract is not None and target_contract.stage == contract.stage:
                same_stage_targets.add(target)
    return [
        c
        for c in contracts
        if c.stage in CORE_STAGES and is_user_invocable(c) and c.skill not in same_stage_targets
    ]


def _closure_successors(
    contracts: list[WorkflowContract], rendered: set[str]
) -> dict[str, tuple[set[str], set[str]]]:
    """Per rendered skill: (rendered successors reachable via next chains, normalized
    outputs pooled from the source and every traversed non-rendered skill)."""
    by_name = {c.skill: c for c in contracts}
    result: dict[str, tuple[set[str], set[str]]] = {}
    for src in sorted(rendered):
        successors: set[str] = set()
        pooled = {normalize_template(t) for t in by_name[src].outputs}
        seen: set[str] = set()
        stack = list(by_name[src].next_skills)
        while stack:
            current = stack.pop()
            if current in seen or current == src:
                continue
            seen.add(current)
            if current in rendered:
                successors.add(current)
                continue
            contract = by_name.get(current)
            if contract is None:
                continue
            pooled.update(normalize_template(t) for t in contract.outputs)
            stack.extend(contract.next_skills)
        result[src] = (successors, pooled)
    return result


OVERVIEW_CLASSDEFS = (
    "    classDef userSkill fill:#dbeafe,stroke:#2563eb,color:#1e3a5f,font-weight:bold",
    "    classDef manualStep fill:#fef3c7,stroke:#d97706,color:#78350f,font-weight:bold",
)

DETAIL_CLASSDEFS = (
    "    classDef userSkill fill:#dbeafe,stroke:#2563eb,color:#1e3a5f,font-weight:bold",
    "    classDef internalSkill fill:#f3f4f6,stroke:#6b7280,color:#374151,stroke-dasharray:5 5,font-weight:bold",
    "    classDef artifact fill:#ede9fe,stroke:#7c3aed,color:#4c1d95,font-weight:bold",
    "    classDef orphanArtifact fill:#ede9fe,stroke:#dc2626,color:#4c1d95,stroke-dasharray:4 4,font-weight:bold",
    "    classDef manualStep fill:#fef3c7,stroke:#d97706,color:#78350f,font-weight:bold",
)


def render_overview(contracts: list[WorkflowContract]) -> tuple[str, int]:
    """Small journey overview: per-stage user-invoked entry skills plus manual-followup
    declarers; cross-stage artifacts as edge labels; repeat self-loops; amber manual nodes."""
    by_name = {c.skill: c for c in contracts}
    rendered_names = sorted(
        {c.skill for c in _entry_skills(contracts)}
        | {
            c.skill
            for c in contracts
            if c.stage in CORE_STAGES and c.manual_followup and is_user_invocable(c)
        }
    )
    rendered = set(rendered_names)
    closure = _closure_successors(contracts, rendered)

    lines = ["flowchart LR", *OVERVIEW_CLASSDEFS, ""]
    node_count = 0
    manual_ids: dict[str, str] = {}
    for stage in CORE_STAGES:
        stage_skills = [name for name in rendered_names if by_name[name].stage == stage]
        if not stage_skills:
            continue
        stage_id = "stage_" + stage.replace("-", "_")
        lines.append(f'    subgraph {stage_id}["{STAGE_TITLES[stage]}"]')
        for name in stage_skills:
            lines.append(f'        {_node_id("skill", name)}["/{name}"]')
            node_count += 1
            contract = by_name[name]
            if contract.manual_followup:
                manual_id = _node_id("manual", name)
                manual_ids[name] = manual_id
                lines.append(f'        {manual_id}["{contract.manual_followup}"]')
                node_count += 1
        lines.append("    end")
    lines.append("")
    for src in rendered_names:
        successors, pooled = closure[src]
        if src in manual_ids:
            lines.append(f'    {_node_id("skill", src)} --> {manual_ids[src]}')
        src_id = manual_ids.get(src, _node_id("skill", src))
        for dst in sorted(successors):
            labels = sorted(pooled & {normalize_template(t) for t in by_name[dst].inputs})
            if labels:
                lines.append(f'    {src_id} -- "{" + ".join(labels)}" --> {_node_id("skill", dst)}')
            else:
                lines.append(f'    {src_id} --> {_node_id("skill", dst)}')
        if by_name[src].repeatable:
            lines.append(f'    {_node_id("skill", src)} -. "repeat" .-> {_node_id("skill", src)}')
    lines.append("")
    for name in rendered_names:
        lines.append(f'    class {_node_id("skill", name)} userSkill')
    for manual_id in sorted(manual_ids.values()):
        lines.append(f"    class {manual_id} manualStep")
    return _mermaid_block(lines), node_count


def render_stage_detail(
    contracts: list[WorkflowContract], stage: str, orphans: set[str]
) -> tuple[str, int]:
    """Full machinery of one stage: every contracted skill, artifact nodes, next edges,
    repeat self-loops, manual nodes; internal skills muted, orphaned artifacts dashed red."""
    stage_contracts = sorted((c for c in contracts if c.stage == stage), key=lambda c: c.skill)
    if not stage_contracts:
        return (
            "No skills in this stage declare a `workflow:` contract yet. Uncontracted "
            "skills appear under Missing contract in the gaps table.",
            0,
        )
    stage_names = {c.skill for c in stage_contracts}
    by_name = {c.skill: c for c in stage_contracts}
    artifacts = sorted(
        {
            normalize_template(template)
            for contract in stage_contracts
            for template in (*contract.inputs, *contract.outputs)
        }
    )
    _assert_unique_artifact_ids(artifacts)

    lines = ["flowchart LR", *DETAIL_CLASSDEFS, ""]
    node_count = 0
    for contract in stage_contracts:
        lines.append(f'    {_node_id("skill", contract.skill)}["/{contract.skill}"]')
        node_count += 1
    manual_ids: dict[str, str] = {}
    for contract in stage_contracts:
        if contract.manual_followup:
            manual_id = _node_id("manual", contract.skill)
            manual_ids[contract.skill] = manual_id
            lines.append(f'    {manual_id}["{contract.manual_followup}"]')
            node_count += 1
    for template in artifacts:
        lines.append(f'    {_node_id("art", template)}["{_short_label(template)}"]')
        node_count += 1
    lines.append("")
    for contract in stage_contracts:
        skill_id = _node_id("skill", contract.skill)
        for template in sorted({normalize_template(t) for t in contract.inputs}):
            lines.append(f'    {_node_id("art", template)} --> {skill_id}')
        for template in sorted({normalize_template(t) for t in contract.outputs}):
            lines.append(f'    {skill_id} --> {_node_id("art", template)}')
        for target in sorted(set(contract.next_skills)):
            if target in stage_names:
                lines.append(f'    {skill_id} --> {_node_id("skill", target)}')
        invoker = SKILL_INVOKER_RE.match(contract.invoked_by)
        if invoker and invoker.group(1) in stage_names:
            dispatcher = by_name[invoker.group(1)]
            if contract.skill not in dispatcher.next_skills:
                # invoked-by edge, drawn only when no next edge already covers it
                lines.append(f'    {_node_id("skill", dispatcher.skill)} -.-> {skill_id}')
        if contract.skill in manual_ids:
            lines.append(f'    {skill_id} --> {manual_ids[contract.skill]}')
        if contract.repeatable:
            lines.append(f'    {skill_id} -. "repeat" .-> {skill_id}')
    lines.append("")
    for contract in stage_contracts:
        cls = "internalSkill" if is_internal_only(contract) else "userSkill"
        lines.append(f'    class {_node_id("skill", contract.skill)} {cls}')
    for manual_id in sorted(manual_ids.values()):
        lines.append(f"    class {manual_id} manualStep")
    for template in artifacts:
        cls = "orphanArtifact" if template in orphans else "artifact"
        lines.append(f'    class {_node_id("art", template)} {cls}')
    return _mermaid_block(lines), node_count
