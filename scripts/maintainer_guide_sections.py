"""Workflow-contract parsing and generated maintainer-tooling documentation.

Library for scripts/generate-maintainer-guide.py. Parses `workflow:` frontmatter
blocks from .claude/skills/*/SKILL.md (excluding archived/), validates them,
computes gap signals, and renders the generated summary and stage sections.
Fail-closed: validation errors raise ValueError naming the offending skill and
field.
"""
from __future__ import annotations

from bisect import insort
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import re

import yaml

STAGES = ("map-sync", "discover", "decide", "implement", "derive", "support")
CORE_STAGES = ("map-sync", "discover", "decide", "implement", "derive")
STAGE_TITLES = {
    "map-sync": "Map sync",
    "discover": "Discover",
    "decide": "Decide",
    "implement": "Implement",
    "derive": "Derive",
    "support": "Adjacent tooling",
}
SUMMARY_DOC = Path("docs/maintainer-tooling.md")
STAGE_DOCS = {
    "map-sync": Path("docs/maintainer-tooling/map-sync.md"),
    "discover": Path("docs/maintainer-tooling/discover.md"),
    "decide": Path("docs/maintainer-tooling/decide.md"),
    "implement": Path("docs/maintainer-tooling/implement.md"),
    "derive": Path("docs/maintainer-tooling/derive.md"),
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
    """User-invocable core-stage skills not named in any same-stage skill's next list.

    Only non-user-invocable same-stage targets (i.e. skill-dispatched steps) are
    suppressed from the overview.  User-invocable same-stage targets remain visible
    so that chains like record-health-dispositions → plan-health-findings both appear
    in the decide subgraph.
    """
    by_name = {c.skill: c for c in contracts}
    same_stage_targets: set[str] = set()
    for contract in contracts:
        for target in contract.next_skills:
            target_contract = by_name.get(target)
            if (
                target_contract is not None
                and target_contract.stage == contract.stage
                and not is_user_invocable(target_contract)
            ):
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

FOCUSED_DETAIL_CLASSDEFS = (
    "    classDef userSkill fill:#dbeafe,stroke:#2563eb,color:#1e3a5f,font-weight:bold",
    "    classDef artifact fill:#ede9fe,stroke:#7c3aed,color:#4c1d95,font-weight:bold",
)


MAP_SYNC_REQUIRED_SKILLS = {
    "sync-documentation-maps",
    "sync-documentation-maps-collect",
    "sync-documentation-maps-apply",
    "sync-documentation-maps-write",
}

MAP_SYNC_REQUIRED_INPUTS = {
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
    "sync-documentation-maps": ("sync-documentation-maps-collect",),
    "sync-documentation-maps-collect": ("sync-documentation-maps-apply",),
    "sync-documentation-maps-apply": ("sync-documentation-maps-write",),
}

DISCOVER_REQUIRED_SKILLS = {
    "ingest-friction-log",
    "plugin-health-audit",
    "plugin-health-discover",
    "plugin-health-report",
}

DISCOVER_REQUIRED_INPUTS = {
    "ingest-friction-log": (
        "~/friction-log/<session>-findings.md",
        "~/friction-log/<session>-signals.json",
    ),
    "plugin-health-audit": ("docs/al-dev-skills-map.md", "docs/al-dev-agent-map.md"),
    "plugin-health-discover": (
        "docs/al-dev-skills-map.md",
        "docs/al-dev-agent-map.md",
        "profile-al-dev-shared/knowledge/lens-invocation-patterns.md",
    ),
    "plugin-health-report": (
        "docs/health/<date>-<surface>-findings.md",
        "docs/health/dispositions-open.md",
    ),
}

DISCOVER_REQUIRED_OUTPUTS = {
    "ingest-friction-log": (
        "docs/health/<date>-<surface>-friction-findings.md",
    ),
    "plugin-health-discover": ("docs/health/<date>-<surface>-findings.md",),
    "plugin-health-report": ("docs/health/<date>-<surface>-health.md",),
}

DISCOVER_REQUIRED_NEXT = {
    "ingest-friction-log": ("plugin-health-report",),
    "plugin-health-audit": ("plugin-health-discover",),
    "plugin-health-discover": ("plugin-health-report",),
}

DERIVE_REQUIRED_SKILLS = {
    "regenerate-agent-projections",
    "audit-knowledge-quality",
    "fix-knowledge-quality",
    "validate-plugin-neutrality",
}

DERIVE_REQUIRED_INPUTS = {
    "regenerate-agent-projections": ("profile-al-dev-shared/agents/",),
    "audit-knowledge-quality": ("profile-al-dev-shared/knowledge/",),
    "fix-knowledge-quality": ("docs/al-dev-knowledge-quality.md",),
    "validate-plugin-neutrality": (
        "profile-al-dev-shared/skills/",
        "profile-al-dev-shared/agents/",
        "profile-al-dev-shared/knowledge/",
    ),
}

DERIVE_REQUIRED_OUTPUTS = {
    "regenerate-agent-projections": ("profile-al-dev-shared/generated/agents/",),
    "audit-knowledge-quality": ("docs/al-dev-knowledge-quality.md",),
    "fix-knowledge-quality": ("profile-al-dev-shared/knowledge/",),
}

DERIVE_REQUIRED_NEXT = {
    "regenerate-agent-projections": ("validate-plugin-neutrality",),
    "audit-knowledge-quality": ("fix-knowledge-quality",),
    "fix-knowledge-quality": ("validate-plugin-neutrality",),
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
    """Compact landing-page overview of the five-stage maintenance journey."""
    names = {contract.skill for contract in contracts}
    required = {
        "sync-documentation-maps",
        "sync-documentation-maps-write",
        "plugin-health-audit",
        "plugin-health-discover",
        "ingest-friction-log",
        "plugin-health-report",
        "record-health-dispositions",
        "plan-health-findings",
        "implement-health-plan",
    }
    if not required <= names:
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

    lines = [
        "flowchart TD",
        '    classDef stage fill:#dbeafe,stroke:#2563eb,color:#1e3a5f,font-weight:bold',
        '    classDef alternate fill:#fef3c7,stroke:#d97706,color:#78350f,font-weight:bold',
        "",
        '    stage_map_sync["1. Map sync<br/>refresh maps when stale"]',
        '    stage_discover["2. Discover<br/>findings become a ranked dossier"]',
        '    stage_decide["3. Decide<br/>record decisions and write a verified plan"]',
        '    stage_implement["4. Implement<br/>apply the plan and close disposition events"]',
        '    stage_derive["5. Derive<br/>regenerate and validate changed shared source"]',
        '    entry_friction["Alternate source<br/>/ingest-friction-log"]',
        "",
        "    stage_map_sync --> stage_discover",
        '    entry_friction -- "friction-findings" --> stage_discover',
        "    stage_discover --> stage_decide",
        "    stage_decide --> stage_implement",
        '    stage_implement -. "when shared source changed" .-> stage_derive',
        "",
        "    class stage_map_sync,stage_discover,stage_decide,stage_implement,stage_derive stage",
        "    class entry_friction alternate",
    ]
    return _mermaid_block(lines), 6


def render_map_sync_stage_detail(
    stage_contracts: list[WorkflowContract],
    orphans: set[str],
) -> tuple[str, int]:
    """Focused map-sync view: the maintained four-step async chain."""
    lines = [
        "flowchart TD",
        *FOCUSED_DETAIL_CLASSDEFS,
        "",
        '    skill_sync_documentation_maps["/sync-documentation-maps"]',
        '    skill_sync_documentation_maps_collect["/sync-documentation-maps-collect"]',
        '    skill_sync_documentation_maps_apply["/sync-documentation-maps-apply"]',
        '    skill_sync_documentation_maps_write["/sync-documentation-maps-write"]',
        '    art_generated["derived docs + projections"]',
        "",
        '    skill_sync_documentation_maps -- "checkpoint + audit results" --> skill_sync_documentation_maps_collect',
        '    skill_sync_documentation_maps_collect -- "validated update artifacts" --> skill_sync_documentation_maps_apply',
        '    skill_sync_documentation_maps_apply -- "updated map docs" --> skill_sync_documentation_maps_write',
        "    skill_sync_documentation_maps_write --> art_generated",
        "",
        "    class skill_sync_documentation_maps userSkill",
        "    class skill_sync_documentation_maps_collect userSkill",
        "    class skill_sync_documentation_maps_apply userSkill",
        "    class skill_sync_documentation_maps_write userSkill",
        "    class art_generated artifact",
    ]
    node_count = 5
    return _mermaid_block(lines), node_count


def render_discover_stage_detail(
    stage_contracts: list[WorkflowContract],
    orphans: set[str],
) -> tuple[str, int]:
    """Focused discover view: audit-driven and friction-driven entries converge on report."""
    lines = [
        "flowchart TD",
        *FOCUSED_DETAIL_CLASSDEFS,
        "",
        '    subgraph lane_a["Audit-driven entry"]',
        '        skill_plugin_health_audit["/plugin-health-audit"]',
        '        skill_plugin_health_discover["/plugin-health-discover"]',
        "    end",
        '    subgraph lane_b["Friction-driven entry"]',
        '        skill_ingest_friction_log["/ingest-friction-log"]',
        "    end",
        '    art_breadcrumb[".dev/health-loop-state.md"]',
        '    art_dispositions["docs/health/dispositions-open.md"]',
        '    skill_plugin_health_report["/plugin-health-report"]',
        '    art_dossier["docs/health/*-*-health.md"]',
        "",
        "    skill_plugin_health_audit --> skill_plugin_health_discover",
        '    skill_plugin_health_discover -- "standard findings + handoff" --> art_breadcrumb',
        '    skill_ingest_friction_log -- "friction findings + handoff" --> art_breadcrumb',
        '    art_breadcrumb -- "adopt exact findings path" --> skill_plugin_health_report',
        "    art_dispositions --> skill_plugin_health_report",
        "    skill_plugin_health_report --> art_dossier",
        "",
        "    class skill_plugin_health_audit userSkill",
        "    class skill_plugin_health_discover userSkill",
        "    class skill_ingest_friction_log userSkill",
        "    class skill_plugin_health_report userSkill",
        "    class art_breadcrumb artifact",
        "    class art_dispositions artifact",
        "    class art_dossier artifact",
    ]
    return _mermaid_block(lines), 7


def render_decide_stage_detail() -> tuple[str, int]:
    """Focused decide view: primary ledger-to-plan path plus optional revision."""
    lines = [
        "flowchart TD",
        *FOCUSED_DETAIL_CLASSDEFS,
        "",
        '    art_dossier["ranked health dossier"]',
        '    skill_record_health_dispositions["/record-health-dispositions"]',
        '    art_ledger["accepted rows in disposition ledger"]',
        '    skill_plan_health_findings["/plan-health-findings"]',
        '    art_plan["verified plan with closes_event_ids"]',
        '    art_commentary["optional review commentary"]',
        '    skill_revise_health_plan["/revise-health-plan"]',
        "",
        "    art_dossier --> skill_record_health_dispositions",
        "    skill_record_health_dispositions --> art_ledger",
        "    art_ledger --> skill_plan_health_findings",
        "    skill_plan_health_findings --> art_plan",
        "    art_commentary -.-> skill_revise_health_plan",
        "    art_plan -.-> skill_revise_health_plan",
        '    skill_revise_health_plan -. "reconciled plan + ledger" .-> art_plan',
        "",
        "    class skill_record_health_dispositions userSkill",
        "    class skill_plan_health_findings userSkill",
        "    class skill_revise_health_plan userSkill",
        "    class art_dossier,art_ledger,art_plan,art_commentary artifact",
    ]
    return _mermaid_block(lines), 7


def render_implement_stage_detail() -> tuple[str, int]:
    """Focused implement view: execute, checkpoint, and close the loop."""
    lines = [
        "flowchart TD",
        *FOCUSED_DETAIL_CLASSDEFS,
        "",
        '    art_plan["approved plan with closes_event_ids"]',
        '    art_ledger["accepted disposition events"]',
        '    skill_implement_health_plan["/implement-health-plan"]',
        '    art_progress["resumable progress checkpoint"]',
        '    art_changed["verified source and documentation changes"]',
        '    art_closed["fixed events written + breadcrumb closed"]',
        "",
        "    art_plan --> skill_implement_health_plan",
        "    art_ledger --> skill_implement_health_plan",
        "    skill_implement_health_plan --> art_progress",
        "    skill_implement_health_plan --> art_changed",
        "    skill_implement_health_plan --> art_closed",
        "",
        "    class skill_implement_health_plan userSkill",
        "    class art_plan,art_ledger,art_progress,art_changed,art_closed artifact",
    ]
    return _mermaid_block(lines), 6


def render_derive_stage_detail(
    stage_contracts: list[WorkflowContract],
    orphans: set[str],
) -> tuple[str, int]:
    """Focused derive view: independent agent and knowledge flows converge on neutrality."""
    lines = [
        "flowchart TD",
        *FOCUSED_DETAIL_CLASSDEFS,
        "",
        '    subgraph agent_lane["Agent source changed"]',
        '        art_agent_source["agents/"]',
        '        skill_regenerate_agent_projections["/regenerate-agent-projections"]',
        '        art_generated_agents["generated/agents/"]',
        "    end",
        '    subgraph knowledge_lane["Knowledge source changed"]',
        '        art_knowledge_source["knowledge/"]',
        '        skill_audit_knowledge_quality["/audit-knowledge-quality"]',
        '        art_knowledge_quality_report[".../knowledge-quality.md"]',
        '        skill_fix_knowledge_quality["/fix-knowledge-quality"]',
        "    end",
        '    art_shared_surface["shared authored surface"]',
        '    skill_align_harness_repos["/validate-plugin-neutrality"]',
        "",
        "    art_agent_source --> skill_regenerate_agent_projections",
        "    skill_regenerate_agent_projections --> art_generated_agents",
        "    skill_regenerate_agent_projections --> skill_align_harness_repos",
        "    art_knowledge_source --> skill_audit_knowledge_quality",
        "    skill_audit_knowledge_quality --> art_knowledge_quality_report",
        '    art_knowledge_quality_report -- "if HIGH" --> skill_fix_knowledge_quality',
        '    skill_audit_knowledge_quality -. "if clean" .-> skill_align_harness_repos',
        "    skill_fix_knowledge_quality --> art_knowledge_source",
        "    skill_fix_knowledge_quality --> skill_align_harness_repos",
        "    art_shared_surface --> skill_align_harness_repos",
        "",
        "    class skill_regenerate_agent_projections userSkill",
        "    class skill_audit_knowledge_quality userSkill",
        "    class skill_fix_knowledge_quality userSkill",
        "    class skill_align_harness_repos userSkill",
        "    class art_agent_source artifact",
        "    class art_generated_agents artifact",
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
    if stage == "discover" and _stage_has_contract_shape(
        stage_contracts,
        DISCOVER_REQUIRED_SKILLS,
        DISCOVER_REQUIRED_INPUTS,
        DISCOVER_REQUIRED_OUTPUTS,
        DISCOVER_REQUIRED_NEXT,
    ):
        return render_discover_stage_detail(stage_contracts, orphans)
    if stage == "derive" and _stage_has_contract_shape(
        stage_contracts,
        DERIVE_REQUIRED_SKILLS,
        DERIVE_REQUIRED_INPUTS,
        DERIVE_REQUIRED_OUTPUTS,
        DERIVE_REQUIRED_NEXT,
    ):
        return render_derive_stage_detail(stage_contracts, orphans)
    if stage == "decide" and {contract.skill for contract in stage_contracts} == {
        "record-health-dispositions",
        "plan-health-findings",
        "revise-health-plan",
    }:
        return render_decide_stage_detail()
    if stage == "implement" and {contract.skill for contract in stage_contracts} == {
        "implement-health-plan",
    }:
        return render_implement_stage_detail()
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

    orientation = "TD" if stage in {"decide", "implement"} else "LR"
    lines = [f"flowchart {orientation}", *DETAIL_CLASSDEFS, ""]
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


def render_stage_journey(contracts: list[WorkflowContract], stage: str) -> str:
    stage_user = [c for c in contracts if c.stage == stage and is_user_invocable(c)]
    if not stage_user:
        return "No user-invoked skills in this stage declare a `workflow:` contract yet."
    by_name = {contract.skill: contract for contract in stage_user}

    def command(name: str, suffix: str = "") -> str:
        contract = by_name[name]
        return f"`/{name}{suffix}` — {_first_sentence(contract.description)}"

    if stage == "map-sync" and MAP_SYNC_REQUIRED_SKILLS <= set(by_name):
        return "\n".join(
            [
                "### Primary path",
                "",
                "1. " + command("sync-documentation-maps"),
                "2. " + command("sync-documentation-maps-collect"),
                "3. " + command("sync-documentation-maps-apply"),
                "4. " + command("sync-documentation-maps-write"),
            ]
        )
    if stage == "discover" and DISCOVER_REQUIRED_SKILLS <= set(by_name):
        return "\n".join(
            [
                "### Audit-driven path",
                "",
                "1. " + command("plugin-health-audit"),
                "2. `/plugin-health-discover` dispatches the lenses and writes standard findings.",
                "3. `/plugin-health-report --findings <path>` verifies and ranks those findings into a dossier.",
                "",
                "### Friction-driven path",
                "",
                "1. " + command("ingest-friction-log"),
                "2. `/plugin-health-report --findings <path>` consumes the explicit friction findings path; automatic findings selection intentionally does not match this artifact family.",
            ]
        )
    if stage == "decide" and {
        "record-health-dispositions",
        "plan-health-findings",
        "revise-health-plan",
    } <= set(by_name):
        return "\n".join(
            [
                "### Primary path",
                "",
                "1. " + command("record-health-dispositions"),
                "2. " + command("plan-health-findings"),
                "",
                "### Optional revision path",
                "",
                "Run `/revise-health-plan` only when a separate review or commentary artifact requires the plan and ledger decisions to be reconciled before implementation.",
            ]
        )
    if stage == "implement" and "implement-health-plan" in by_name:
        return "\n".join(
            [
                "### Primary path",
                "",
                "1. Run `/implement-health-plan --plan <path>` in the fresh session named by the breadcrumb.",
                "2. Execute and verify each plan task, preserving the progress checkpoint for recovery.",
                "3. Append `fixed` disposition events to the JSONL event store, archive consumed health artifacts, and commit `next_command: none` with the close-back.",
            ]
        )
    if stage == "derive" and DERIVE_REQUIRED_SKILLS <= set(by_name):
        return "\n".join(
            [
                "### Agent source changed",
                "",
                "1. Run `/regenerate-agent-projections` to validate authored agents and regenerate harness-native projections.",
                "2. Run `/validate-plugin-neutrality` to verify the shared source remains harness-neutral.",
                "",
                "### Knowledge source changed",
                "",
                "1. Run `/audit-knowledge-quality`.",
                "2. If HIGH findings exist and are approved, run `/fix-knowledge-quality`.",
                "3. Re-run the applicable quality and neutrality checks after fixes.",
                "",
                "### Any shared source changed",
                "",
                "Run `/validate-plugin-neutrality` after edits to shared skills, agents, or knowledge. In a health-plan run, the applicable Derive actions occur during Implement finalization before loop closure; they are not another breadcrumb-controlled step.",
            ]
        )

    lines = ["### Primary path", ""]
    for step, contract in enumerate(_topo_order(stage_user), start=1):
        lines.append(f"{step}. `/{contract.skill}` — {_first_sentence(contract.description)}")
        if contract.manual_followup:
            lines.append(f"{step + 1}. Manual step: {contract.manual_followup}.")
    return "\n".join(lines)


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


STAGE_ARTIFACTS: dict[str, tuple[tuple[str, str], ...]] = {
    "map-sync": (
        (
            "docs/al-dev-skills-map.md` and `docs/al-dev-agent-map.md",
            "Canonical inventory maps audited and updated by the stage.",
        ),
        (
            ".dev/sync-documentation-maps-checkpoint.json",
            "Records the active run, team identifiers, and current async phase.",
        ),
        (
            ".dev/sync-documentation-maps-runs/RUN_ID/",
            "Keeps raw audit results and validated update artifacts separate from the canonical maps.",
        ),
        (
            "docs/al-dev-workflow-diagrams.md`, `docs/al-dev-plugin-graph.md`, `docs/maintainer-tooling.md`, and `docs/maintainer-tooling/",
            "Derived documentation regenerated only after the canonical maps are applied.",
        ),
        (
            "profile-al-dev-shared/generated/agents/",
            "Harness-native projections regenerated from canonical shared agent source.",
        ),
    ),
    "discover": (
        (
            "docs/al-dev-skills-map.md` and `docs/al-dev-agent-map.md",
            "Provide current inventory and relationship context to the audit-driven path.",
        ),
        (
            "docs/health/<date>-<surface>-findings.md",
            "Stores raw lens findings before report-time evidence checks and ranking.",
        ),
        (
            "docs/health/<date>-<surface>-friction-findings.md",
            "Carries friction-derived findings into report through an explicit `--findings` path.",
        ),
        (
            ".dev/health-loop-state.md",
            "Persists the exact report handoff across sessions.",
        ),
        (
            "docs/health/dispositions-open.md",
            "Lets report suppress or re-verify findings that already have durable decisions.",
        ),
        (
            "docs/health/<date>-<surface>-health.md",
            "The ranked dossier handed to the Decide stage.",
        ),
    ),
    "decide": (
        (
            "docs/health/<date>-<surface>-health.md",
            "Presents the verified findings that require a maintainer decision.",
        ),
        (
            "docs/health/dispositions-events/YYYY/YYYY-MM.jsonl` (canonical) + `docs/health/dispositions-open.md",
            "Canonical event store for decisions; dispositions-open.md is the generated open-items read view.",
        ),
        (
            "profile-al-dev-shared/knowledge/map-change-rubber-duck-checks.md",
            "Defines the live verification checks used before accepted findings become plan tasks.",
        ),
        (
            "docs/superpowers/plans/<date>-<topic>.md",
            "Carries the verified implementation tasks and required `closes_event_ids:` identifiers.",
        ),
        (
            "docs/superpowers/plans/<date>-<topic>-commentary.md",
            "Optional review evidence used only when the plan must be revised.",
        ),
    ),
    "implement": (
        (
            "docs/superpowers/plans/<date>-<topic>.md",
            "The approved execution contract; each task must name the event IDs it closes via `closes_event_ids:`.",
        ),
        (
            ".dev/implement-health-plan-progress.md",
            "Supports recovery by recording completed tasks and their commits.",
        ),
        (
            "docs/health/dispositions-events/YYYY/YYYY-MM.jsonl",
            "Receives the fixed close-back events that prove accepted work was completed; generated views regenerate from the event store.",
        ),
        (
            ".dev/health-loop-state.md",
            "Closes the core loop with `next_command: none` in the ledger-close commit.",
        ),
        (
            "docs/health/archived/` and `docs/superpowers/plans/archived/",
            "Retain consumed findings, dossiers, plans, and review evidence outside live selectors.",
        ),
    ),
    "derive": (
        (
            "profile-al-dev-shared/agents/",
            "Canonical authored agent source.",
        ),
        (
            "profile-al-dev-shared/generated/agents/",
            "Generated harness-native projections; never edit these files directly.",
        ),
        (
            "profile-al-dev-shared/knowledge/",
            "Canonical shared guidance audited for structural and semantic quality.",
        ),
        (
            "docs/al-dev-knowledge-quality.md",
            "Records knowledge findings and the structured HIGH-severity fix task block.",
        ),
        (
            "scripts/validate_harness_neutrality.py",
            "Checks shared skills, agents, and knowledge for harness-specific leakage.",
        ),
    ),
}


def render_stage_artifacts(contracts: list[WorkflowContract], stage: str) -> str:
    if not any(contract.stage == stage for contract in contracts):
        return "No key artifacts are declared for this stage."
    lines = ["| Artifact | Role |", "| --- | --- |"]
    for artifact, role in STAGE_ARTIFACTS[stage]:
        lines.append(f"| `{artifact}` | {role} |")
    return "\n".join(lines)


def render_breadcrumb_orchestrator() -> str:
    return "\n".join(
        [
            "The breadcrumb-controlled core runs from Discover through Implement.",
            "It uses `.dev/health-loop-state.md` as a durable cross-session pointer: each lifecycle skill reads the current pointer before work and writes the next supported command on successful completion.",
            "Map sync prepares the inputs and Derive performs conditional finalization before the closing commit, but neither is a breadcrumb lifecycle stage.",
            "",
            "The canonical schema and lifecycle are in `.claude/knowledge/health-loop-state-contract.md`; validation details are in Appendix A.",
            "",
            "| Completing skill | Persisted next command | Why it matters |",
            "| --- | --- | --- |",
            "| `/ingest-friction-log` | `/plugin-health-report --findings ...` | friction is an alternate discover source, not a lens rerun |",
            "| `/plugin-health-discover` | `/plugin-health-report --findings ...` | discover is intentionally split across sessions to avoid compaction |",
            "| `/plugin-health-report` | `/record-health-dispositions` | the dossier becomes durable input for ledger triage |",
            "| `/record-health-dispositions` | `/plan-health-findings` | only accepted rows move into planning |",
            "| `/plan-health-findings` | `/implement-health-plan --plan ...` | the handoff preserves `closes_event_ids:` and bypasses the generic writing-plans ending |",
            "| `/implement-health-plan` | `none` | loop closure is explicit and machine-checked |",
        ]
    )


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
    """Wrapped marker sections for the landing page and five stage detail pages."""
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
    record("maintainer-breadcrumb-orchestrator", render_breadcrumb_orchestrator())
    for stage in CORE_STAGES:
        body, count = render_stage_detail(contracts, stage, orphans)
        record(f"maintainer-stage-{stage}-diagram", body, count)
        record(f"maintainer-stage-{stage}-journey", render_stage_journey(contracts, stage))
        record(f"maintainer-stage-{stage}-artifacts", render_stage_artifacts(contracts, stage))
    record("maintainer-user-journey", render_user_journey(contracts))
    record("maintainer-skills-tables", render_skills_tables(contracts))
    record("maintainer-gaps", render_gaps_table(gaps))
    return sections, warnings
