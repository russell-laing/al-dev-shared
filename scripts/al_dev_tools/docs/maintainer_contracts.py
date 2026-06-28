"""Workflow-contract parsing and discovery helpers for maintainer tooling docs."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

from scripts.al_dev_tools.markdown_frontmatter import parse_required_frontmatter


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
    try:
        data, _body = parse_required_frontmatter(path.read_text(encoding="utf-8"))
    except ValueError as exc:
        raise ValueError(f"{path}: {exc}") from exc
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


__all__ = [
    "ALLOWED_WORKFLOW_KEYS",
    "CORE_STAGES",
    "NODE_BUDGET",
    "SKILL_INVOKER_RE",
    "STAGES",
    "STAGE_DOCS",
    "STAGE_TITLES",
    "SUMMARY_DOC",
    "WorkflowContract",
    "discover_skill_dirs",
    "load_contracts",
    "parse_contract",
    "validate_contracts",
]
