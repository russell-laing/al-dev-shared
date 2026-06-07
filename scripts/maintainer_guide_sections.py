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
SELF_GENERATED_DOC = "docs/maintainer-tooling.md"
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
        if norm == SELF_GENERATED_DOC:
            continue
        gaps["stale-artifact"].append((norm, artifact_status(repo, norm)))
    return gaps


def _node_id(prefix: str, name: str) -> str:
    return f"{prefix}_" + re.sub(r"[^A-Za-z0-9_]", "_", name)


def _short_label(template: str) -> str:
    """Keep Mermaid node labels compact while preserving meaningful directory names."""
    is_directory = template.endswith("/")
    trimmed = template.rstrip("/")
    if not is_directory and len(template) <= 30:
        return template

    parts = [part for part in trimmed.split("/") if part]
    if is_directory:
        if len(parts) >= 3:
            return "/".join(parts[-2:]) + "/"
        if parts:
            return parts[-1] + "/"
        return template

    if len(template) <= 30:
        return template
    return ".../" + trimmed.rsplit("/", 1)[-1]


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


MAP_SYNC_REQUIRED_SKILLS = {
    "review-maps",
    "sync-documentation-maps",
    "sync-documentation-maps-collect",
    "sync-documentation-maps-apply",
    "sync-documentation-maps-write",
}

MAP_SYNC_REQUIRED_INPUTS = {
    "review-maps": (),
    "sync-documentation-maps": ("docs/al-dev-skills-map.md", "docs/al-dev-agent-map.md"),
    "sync-documentation-maps-collect": (
        ".dev/sync-documentation-maps-checkpoint.json",
        ".dev/sync-documentation-maps-runs/RUN_ID/audit/<surface>-audit.json",
    ),
    "sync-documentation-maps-apply": (
        ".dev/sync-documentation-maps-checkpoint.json",
        ".dev/sync-documentation-maps-runs/RUN_ID/updates/<surface>-map.md",
    ),
    "sync-documentation-maps-write": (
        ".dev/sync-documentation-maps-checkpoint.json",
        "docs/al-dev-skills-map.md",
        "docs/al-dev-agent-map.md",
    ),
}

MAP_SYNC_REQUIRED_OUTPUTS = {
    "review-maps": (),
    "sync-documentation-maps": (
        ".dev/sync-documentation-maps-checkpoint.json",
        ".dev/sync-documentation-maps-runs/RUN_ID/audit/<surface>-audit.json",
    ),
    "sync-documentation-maps-collect": (
        ".dev/sync-documentation-maps-runs/RUN_ID/updates/<surface>-map.md",
    ),
    "sync-documentation-maps-apply": ("docs/al-dev-skills-map.md", "docs/al-dev-agent-map.md"),
    "sync-documentation-maps-write": (
        "docs/al-dev-workflow-diagrams.md",
        "docs/al-dev-plugin-graph.md",
        "docs/maintainer-tooling.md",
        "profile-al-dev-shared/generated/agents/",
    ),
}

MAP_SYNC_REQUIRED_NEXT = {
    "review-maps": ("sync-documentation-maps",),
    "sync-documentation-maps": ("sync-documentation-maps-collect",),
    "sync-documentation-maps-collect": ("sync-documentation-maps-apply",),
    "sync-documentation-maps-apply": ("sync-documentation-maps-write",),
}

DERIVE_REQUIRED_SKILLS = {
    "projection-sync",
    "audit-knowledge-quality",
    "fix-knowledge-quality",
    "align-harness-repos",
}

DERIVE_REQUIRED_INPUTS = {
    "projection-sync": ("profile-al-dev-shared/agents/",),
    "audit-knowledge-quality": ("profile-al-dev-shared/knowledge/",),
    "fix-knowledge-quality": ("docs/al-dev-knowledge-quality.md",),
    "align-harness-repos": (
        "profile-al-dev-shared/skills/",
        "profile-al-dev-shared/agents/",
        "profile-al-dev-shared/knowledge/",
    ),
}

DERIVE_REQUIRED_OUTPUTS = {
    "projection-sync": ("profile-al-dev-shared/generated/agents/",),
    "audit-knowledge-quality": ("docs/al-dev-knowledge-quality.md",),
    "fix-knowledge-quality": ("profile-al-dev-shared/knowledge/",),
}

DERIVE_REQUIRED_NEXT = {
    "projection-sync": ("align-harness-repos",),
    "audit-knowledge-quality": ("fix-knowledge-quality",),
    "fix-knowledge-quality": ("align-harness-repos",),
}


def _has_required_templates(actual: tuple[str, ...], required: tuple[str, ...]) -> bool:
    actual_norm = {normalize_template(value) for value in actual}
    required_norm = {normalize_template(value) for value in required}
    return required_norm <= actual_norm


def _stage_has_contract_shape(
    stage_contracts: list[WorkflowContract],
    names: set[str],
    required_inputs: dict[str, tuple[str, ...]],
    required_outputs: dict[str, tuple[str, ...]],
    required_next: dict[str, tuple[str, ...]],
) -> bool:
    by_name = {contract.skill: contract for contract in stage_contracts}
    if set(by_name) != names:
        return False
    for name in names:
        contract = by_name[name]
        if not _has_required_templates(contract.inputs, required_inputs.get(name, ())):
            return False
        if not _has_required_templates(contract.outputs, required_outputs.get(name, ())):
            return False
        if not set(required_next.get(name, ())) <= set(contract.next_skills):
            return False
    return True


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
    present_stage_ids: list[str] = []
    for stage in CORE_STAGES:
        stage_skills = [name for name in rendered_names if by_name[name].stage == stage]
        if not stage_skills:
            continue
        stage_id = "stage_" + stage.replace("-", "_")
        lines.append(f'    subgraph {stage_id}["{STAGE_TITLES[stage]}"]')
        present_stage_ids.append(stage_id)
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
    for earlier, later in zip(present_stage_ids, present_stage_ids[1:]):
        lines.append(f"    {earlier} ~~~ {later}")
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
    lines.append("")
    for name in rendered_names:
        lines.append(f'    class {_node_id("skill", name)} userSkill')
    for manual_id in sorted(manual_ids.values()):
        lines.append(f"    class {manual_id} manualStep")
    return _mermaid_block(lines), node_count


def render_map_sync_stage_detail(
    stage_contracts: list[WorkflowContract],
    orphans: set[str],
) -> tuple[str, int]:
    """Focused map-sync view: normal entry point plus async lane."""
    lines = [
        "flowchart LR",
        *DETAIL_CLASSDEFS,
        "",
        '    subgraph map_entry["Normal entry point"]',
        '        skill_review_maps["/review-maps"]',
        "    end",
        '    subgraph map_async["Async lane"]',
        '        skill_sync_documentation_maps["/sync-documentation-maps"]',
        '        skill_sync_documentation_maps_collect["/sync-documentation-maps-collect"]',
        '        skill_sync_documentation_maps_apply["/sync-documentation-maps-apply"]',
        '        skill_sync_documentation_maps_write["/sync-documentation-maps-write"]',
        "    end",
        '    art_source_dirs["skills/ + agents/"]',
        '    art_map_docs["map docs"]',
        '    art_async_checkpoint["checkpoint + audit artifacts"]',
        '    art_update_artifacts["update artifacts"]',
        '    art_downstream_generated["downstream generated"]',
        "",
        "    skill_review_maps --> skill_sync_documentation_maps",
        "    art_source_dirs --> skill_sync_documentation_maps",
        "    art_map_docs --> skill_sync_documentation_maps",
        "    skill_sync_documentation_maps --> art_async_checkpoint",
        "    skill_sync_documentation_maps --> skill_sync_documentation_maps_collect",
        "    art_async_checkpoint --> skill_sync_documentation_maps_collect",
        "    skill_sync_documentation_maps_collect --> art_update_artifacts",
        "    skill_sync_documentation_maps_collect --> skill_sync_documentation_maps_apply",
        "    art_update_artifacts --> skill_sync_documentation_maps_apply",
        "    art_async_checkpoint --> skill_sync_documentation_maps_apply",
        "    skill_sync_documentation_maps_apply --> art_map_docs",
        "    skill_sync_documentation_maps_apply --> skill_sync_documentation_maps_write",
        "    art_map_docs --> skill_sync_documentation_maps_write",
        "    art_async_checkpoint --> skill_sync_documentation_maps_write",
        "    skill_sync_documentation_maps_write --> art_downstream_generated",
        "",
        "    class skill_review_maps userSkill",
        "    class skill_sync_documentation_maps userSkill",
        "    class skill_sync_documentation_maps_collect userSkill",
        "    class skill_sync_documentation_maps_apply userSkill",
        "    class skill_sync_documentation_maps_write userSkill",
        "    class art_source_dirs artifact",
        "    class art_map_docs artifact",
        "    class art_async_checkpoint artifact",
        "    class art_update_artifacts artifact",
        "    class art_downstream_generated orphanArtifact",
    ]
    node_count = 10
    return _mermaid_block(lines), node_count


def render_derive_stage_detail(
    stage_contracts: list[WorkflowContract],
    orphans: set[str],
) -> tuple[str, int]:
    """Focused derive view: independent agent and knowledge flows converge on neutrality."""
    generated_cls = (
        "orphanArtifact"
        if "profile-al-dev-shared/generated/agents/" in orphans
        else "artifact"
    )
    lines = [
        "flowchart LR",
        *DETAIL_CLASSDEFS,
        "",
        '    subgraph agent_lane["Agent source changed"]',
        '        art_agent_source["agents/"]',
        '        skill_projection_sync["/projection-sync"]',
        '        art_generated_agents["generated/agents/"]',
        "    end",
        '    subgraph knowledge_lane["Knowledge source changed"]',
        '        art_knowledge_source["knowledge/"]',
        '        skill_audit_knowledge_quality["/audit-knowledge-quality"]',
        '        art_knowledge_quality_report[".../knowledge-quality.md"]',
        '        skill_fix_knowledge_quality["/fix-knowledge-quality"]',
        "    end",
        '    art_shared_surface["shared authored surface"]',
        '    skill_align_harness_repos["/align-harness-repos"]',
        "",
        "    art_agent_source --> skill_projection_sync",
        "    skill_projection_sync --> art_generated_agents",
        "    skill_projection_sync --> skill_align_harness_repos",
        "    art_knowledge_source --> skill_audit_knowledge_quality",
        "    skill_audit_knowledge_quality --> art_knowledge_quality_report",
        '    art_knowledge_quality_report -- "if HIGH" --> skill_fix_knowledge_quality',
        '    skill_audit_knowledge_quality -. "if clean" .-> skill_align_harness_repos',
        "    skill_fix_knowledge_quality --> art_knowledge_source",
        "    skill_fix_knowledge_quality --> skill_align_harness_repos",
        "    art_shared_surface --> skill_align_harness_repos",
        "",
        "    class skill_projection_sync userSkill",
        "    class skill_audit_knowledge_quality userSkill",
        "    class skill_fix_knowledge_quality userSkill",
        "    class skill_align_harness_repos userSkill",
        "    class art_agent_source artifact",
        f"    class art_generated_agents {generated_cls}",
        "    class art_knowledge_source artifact",
        "    class art_knowledge_quality_report artifact",
        "    class art_shared_surface artifact",
    ]
    node_count = 9
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
    if stage == "map-sync" and _stage_has_contract_shape(
        stage_contracts,
        MAP_SYNC_REQUIRED_SKILLS,
        MAP_SYNC_REQUIRED_INPUTS,
        MAP_SYNC_REQUIRED_OUTPUTS,
        MAP_SYNC_REQUIRED_NEXT,
    ):
        return render_map_sync_stage_detail(stage_contracts, orphans)
    if stage == "derive" and _stage_has_contract_shape(
        stage_contracts,
        DERIVE_REQUIRED_SKILLS,
        DERIVE_REQUIRED_INPUTS,
        DERIVE_REQUIRED_OUTPUTS,
        DERIVE_REQUIRED_NEXT,
    ):
        return render_derive_stage_detail(stage_contracts, orphans)
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


def _first_sentence(description: str) -> str:
    text = " ".join(description.split())
    if not text:
        return "(no description)"
    if ". " in text:
        return text.split(". ", 1)[0] + "."
    return text if text.endswith(".") else text + "."


def _topo_order(stage_contracts: list[WorkflowContract]) -> list[WorkflowContract]:
    """Kahn's algorithm over same-stage next edges, alphabetical tie-break, cycle fallback."""
    by_name = {c.skill: c for c in stage_contracts}
    names = set(by_name)
    indegree = {name: 0 for name in names}
    for contract in stage_contracts:
        for target in sorted(set(contract.next_skills)):
            if target in names and target != contract.skill:
                indegree[target] += 1
    ready = sorted(name for name, degree in indegree.items() if degree == 0)
    order: list[WorkflowContract] = []
    placed: set[str] = set()
    while ready:
        current = ready.pop(0)
        order.append(by_name[current])
        placed.add(current)
        for target in sorted(set(by_name[current].next_skills)):
            if target in indegree and target not in placed and target != current:
                indegree[target] -= 1
                if indegree[target] == 0:
                    insort(ready, target)
    for name in sorted(names - placed):
        order.append(by_name[name])
    return order


def render_user_journey(contracts: list[WorkflowContract]) -> str:
    """Numbered per-stage step list of user-invoked skills in next-chain order."""
    sections: list[str] = []
    for stage in CORE_STAGES:
        stage_user = [c for c in contracts if c.stage == stage and is_user_invocable(c)]
        if not stage_user:
            continue
        lines = [f"### {STAGE_TITLES[stage]} steps", ""]
        step = 0
        for contract in _topo_order(stage_user):
            step += 1
            repeat = " Repeat as needed." if contract.repeatable else ""
            lines.append(f"{step}. `/{contract.skill}` — {_first_sentence(contract.description)}{repeat}")
            if contract.inputs:
                lines.append("   - reads: " + ", ".join(f"`{t}`" for t in contract.inputs))
            if contract.outputs:
                lines.append("   - writes: " + ", ".join(f"`{t}`" for t in contract.outputs))
            if contract.manual_followup:
                step += 1
                lines.append(f"{step}. Manual step: {contract.manual_followup}.")
        sections.append("\n".join(lines))
    return "\n\n".join(sections)


def _md_cell(text: str) -> str:
    """Escape a pipe so free text is safe inside a GFM table cell."""
    return text.replace("|", "\\|")


def render_skills_tables(contracts: list[WorkflowContract]) -> str:
    ordered = sorted(contracts, key=lambda c: (STAGES.index(c.stage), c.skill))
    glance = [
        "### Skills at a glance",
        "",
        "| Skill | Stage | Invoked by | Role |",
        "| --- | --- | --- | --- |",
    ]
    for contract in ordered:
        glance.append(
            f"| `/{contract.skill}` | {contract.stage} | {contract.invoked_by} "
            f"| {_md_cell(_first_sentence(contract.description))} |"
        )

    def cell(values: tuple[str, ...]) -> str:
        return ", ".join(f"`{v}`" for v in values) if values else "—"

    io = [
        "### Inputs and outputs",
        "",
        "| Skill | Reads | Writes | Next |",
        "| --- | --- | --- | --- |",
    ]
    for contract in ordered:
        next_cell = (
            ", ".join(f"`/{t}`" for t in contract.next_skills) if contract.next_skills else "—"
        )
        io.append(
            f"| `/{contract.skill}` | {cell(contract.inputs)} | {cell(contract.outputs)} "
            f"| {next_cell} |"
        )
    return "\n".join(glance) + "\n\n" + "\n".join(io)


SIGNAL_ORDER = (
    ("orphaned-artifact", "Orphaned artifact"),
    ("sourceless-input", "Sourceless input"),
    ("manual-step", "Manual step"),
    ("missing-contract", "Missing contract"),
    ("stale-artifact", "Artifact freshness"),
    ("internal-only", "Internal-only skill"),
)


def render_gaps_table(gaps: dict[str, list[tuple[str, str]]]) -> str:
    lines = [
        "| Signal | Item | Detail |",
        "| --- | --- | --- |",
    ]
    for key, title in SIGNAL_ORDER:
        rows = gaps[key]
        if not rows:
            lines.append(f"| {title} | none | — |")
            continue
        for item, detail in rows:
            lines.append(f"| {title} | `{item}` | {detail} |")
    return "\n".join(lines)


def _wrap(key: str, body: str) -> str:
    return f"<!-- BEGIN GENERATED: {key} -->\n{body.rstrip()}\n<!-- END GENERATED: {key} -->"


def build_sections(
    contracts: list[WorkflowContract],
    missing_contracts: list[str],
    repo: Path,
) -> tuple[dict[str, str], list[str]]:
    """All nine wrapped marker sections plus node-budget warnings (warnings never fail)."""
    gaps = compute_gaps(contracts, missing_contracts, repo)
    orphans = {item for item, _ in gaps["orphaned-artifact"]}
    sections: dict[str, str] = {}
    warnings: list[str] = []

    def record(key: str, body: str, node_count: int = 0) -> None:
        if node_count > NODE_BUDGET:
            warnings.append(f"diagram {key} has {node_count} nodes (budget {NODE_BUDGET})")
        sections[key] = _wrap(key, body)

    overview_body, overview_count = render_overview(contracts)
    record("maintainer-workflow-overview", overview_body, overview_count)
    for stage in STAGES:
        body, count = render_stage_detail(contracts, stage, orphans)
        record(f"maintainer-stage-{stage}", body, count)
    record("maintainer-user-journey", render_user_journey(contracts))
    record("maintainer-skills-tables", render_skills_tables(contracts))
    record("maintainer-gaps", render_gaps_table(gaps))
    return sections, warnings
