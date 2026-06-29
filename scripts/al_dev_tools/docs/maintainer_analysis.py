"""Artifact-flow analysis helpers for maintainer tooling docs."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import re

from .maintainer_contracts import WorkflowContract


PLACEHOLDER_RE = re.compile(r"<[^<>]+>|RUN_ID")
EXTERNAL_INPUT_PREFIXES = ("profile-al-dev-shared/", ".claude/")
SELF_GENERATED_DOC = "docs/maintainer_tooling.md"


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


__all__ = [
    "EXTERNAL_INPUT_PREFIXES",
    "PLACEHOLDER_RE",
    "SELF_GENERATED_DOC",
    "artifact_status",
    "compute_gaps",
    "consumers",
    "is_internal_only",
    "is_user_invocable",
    "normalize_template",
    "producers",
]
