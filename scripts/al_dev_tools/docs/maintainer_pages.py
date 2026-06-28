"""Page registry for maintainer-tooling generation."""

from __future__ import annotations

from .maintainer_contracts import STAGE_DOCS, SUMMARY_DOC

PAGE_KEYS = {
    SUMMARY_DOC: (
        "maintainer-workflow-overview",
        "maintainer-breadcrumb-orchestrator",
        "maintainer-skills-tables",
        "maintainer-gaps",
    ),
    STAGE_DOCS["map-sync"]: (
        "maintainer-stage-map-sync-diagram",
        "maintainer-stage-map-sync-journey",
        "maintainer-stage-map-sync-artifacts",
    ),
    STAGE_DOCS["discover"]: (
        "maintainer-stage-discover-diagram",
        "maintainer-stage-discover-journey",
        "maintainer-stage-discover-artifacts",
    ),
    STAGE_DOCS["decide"]: (
        "maintainer-stage-decide-diagram",
        "maintainer-stage-decide-journey",
        "maintainer-stage-decide-artifacts",
    ),
    STAGE_DOCS["implement"]: (
        "maintainer-stage-implement-diagram",
        "maintainer-stage-implement-journey",
        "maintainer-stage-implement-artifacts",
    ),
    STAGE_DOCS["derive"]: (
        "maintainer-stage-derive-diagram",
        "maintainer-stage-derive-journey",
        "maintainer-stage-derive-artifacts",
    ),
}

__all__ = ["PAGE_KEYS"]
