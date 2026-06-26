#!/usr/bin/env python3
"""Regenerate the maintainer-tooling summary and stage pages from workflow contracts.

Reads `workflow:` frontmatter blocks from .claude/skills/*/SKILL.md (excluding
archived/) and rewrites only the <!-- BEGIN GENERATED: ... --> regions of
docs/maintainer-tooling.md and docs/maintainer-tooling/*.md.

Fail-closed, following scripts/generate-plugin-graph.py: any parse or validation
error (including a missing marker pair) exits non-zero, names the offending skill
or section, and leaves the document untouched. Node-budget overruns are warnings
on stderr; generation still succeeds.
"""
from __future__ import annotations

from pathlib import Path
import sys
import tempfile

from scripts import REPO_ROOT
from scripts.al_dev_tools.docs.maintainer_guide_sections import (
    STAGE_DOCS,
    SUMMARY_DOC,
    build_sections,
    load_contracts,
    validate_contracts,
)
from scripts.al_dev_tools.docs.map_doc_sections import replace_marked_sections

REPO = REPO_ROOT
SKILLS_DIR = REPO_ROOT / ".claude" / "skills"
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


def _write_text_atomic(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
        delete=False,
    ) as handle:
        handle.write(text)
        temp_path = Path(handle.name)
    try:
        temp_path.replace(path)
    finally:
        if temp_path.exists():
            temp_path.unlink()


def main() -> int:
    try:
        contracts, missing = load_contracts(SKILLS_DIR)
        active = {contract.skill for contract in contracts} | set(missing)
        validate_contracts(contracts, active)
        sections, warnings = build_sections(contracts, missing, REPO)
        for rel_path, keys in PAGE_KEYS.items():
            page_path = REPO / rel_path
            current = page_path.read_text(encoding="utf-8")
            replacements = {key: sections[key] for key in keys}
            updated = replace_marked_sections(current, replacements)
            _write_text_atomic(page_path, updated)
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"generate-maintainer-guide: {exc}\n")
        return 1

    for warning in warnings:
        sys.stderr.write(f"generate-maintainer-guide: warning: {warning}\n")
    for rel_path in PAGE_KEYS:
        print(f"Wrote {REPO / rel_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
