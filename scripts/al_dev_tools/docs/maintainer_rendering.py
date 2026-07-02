"""Rendering and section-assembly helpers for maintainer tooling docs."""

from __future__ import annotations

from pathlib import Path

from .maintainer_analysis import compute_gaps
from .maintainer_contracts import CORE_STAGES, NODE_BUDGET, WorkflowContract
from .maintainer_journey import render_stage_journey, render_user_journey
from .maintainer_mermaid import (
    DETAIL_CLASSDEFS,
    DERIVE_REQUIRED_INPUTS,
    DERIVE_REQUIRED_NEXT,
    DERIVE_REQUIRED_OUTPUTS,
    DERIVE_REQUIRED_SKILLS,
    DISCOVER_REQUIRED_INPUTS,
    DISCOVER_REQUIRED_NEXT,
    DISCOVER_REQUIRED_OUTPUTS,
    DISCOVER_REQUIRED_SKILLS,
    FOCUSED_DETAIL_CLASSDEFS,
    MAP_SYNC_REQUIRED_INPUTS,
    MAP_SYNC_REQUIRED_NEXT,
    MAP_SYNC_REQUIRED_OUTPUTS,
    MAP_SYNC_REQUIRED_SKILLS,
    OVERVIEW_CLASSDEFS,
    _short_label,
    render_breadcrumb_orchestrator,
    render_decide_stage_detail,
    render_derive_stage_detail,
    render_discover_stage_detail,
    render_implement_stage_detail,
    render_map_sync_stage_detail,
    render_overview,
    render_stage_detail,
)
from .maintainer_tables import SIGNAL_ORDER, STAGE_ARTIFACTS, render_gaps_table, render_skills_tables, render_stage_artifacts
from .render_helpers import wrap_generated_section as _wrap


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


__all__ = [
    "DETAIL_CLASSDEFS",
    "DERIVE_REQUIRED_INPUTS",
    "DERIVE_REQUIRED_NEXT",
    "DERIVE_REQUIRED_OUTPUTS",
    "DERIVE_REQUIRED_SKILLS",
    "DISCOVER_REQUIRED_INPUTS",
    "DISCOVER_REQUIRED_NEXT",
    "DISCOVER_REQUIRED_OUTPUTS",
    "DISCOVER_REQUIRED_SKILLS",
    "FOCUSED_DETAIL_CLASSDEFS",
    "MAP_SYNC_REQUIRED_INPUTS",
    "MAP_SYNC_REQUIRED_NEXT",
    "MAP_SYNC_REQUIRED_OUTPUTS",
    "MAP_SYNC_REQUIRED_SKILLS",
    "OVERVIEW_CLASSDEFS",
    "SIGNAL_ORDER",
    "STAGE_ARTIFACTS",
    "_short_label",
    "build_sections",
    "render_breadcrumb_orchestrator",
    "render_decide_stage_detail",
    "render_derive_stage_detail",
    "render_discover_stage_detail",
    "render_gaps_table",
    "render_implement_stage_detail",
    "render_map_sync_stage_detail",
    "render_overview",
    "render_skills_tables",
    "render_stage_artifacts",
    "render_stage_detail",
    "render_stage_journey",
    "render_user_journey",
]
