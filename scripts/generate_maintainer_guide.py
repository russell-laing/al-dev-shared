#!/usr/bin/env python3
"""Regenerate the maintainer-tooling summary and stage pages from workflow contracts.

Reads `workflow:` frontmatter blocks from .claude/skills/*/SKILL.md (excluding
archived/) and rewrites only the <!-- BEGIN GENERATED: ... --> regions of
docs/maintainer_tooling.md and docs/maintainer_tooling/*.md.

Fail-closed, following scripts/generate_plugin_graph.py: any parse or validation
error (including a missing marker pair) exits non-zero, names the offending skill
or section, and leaves the document untouched. Node-budget overruns are warnings
on stderr; generation still succeeds.
"""
from __future__ import annotations

from pathlib import Path
import sys

from _entrypoint_bootstrap import bootstrap_repo

REPO_ROOT = bootstrap_repo(__file__)
from scripts.al_dev_tools.io_utils import write_text_atomic
from scripts.al_dev_tools.docs.maintainer_guide_sections import (
    build_sections,
    load_contracts,
    validate_contracts,
)
from scripts.al_dev_tools.docs.maintainer_pages import PAGE_KEYS
from scripts.al_dev_tools.docs.map_doc_sections import replace_marked_sections

REPO = REPO_ROOT
SKILLS_DIR = REPO_ROOT / ".claude" / "skills"


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
            write_text_atomic(page_path, updated)
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"generate_maintainer_guide: {exc}\n")
        return 1

    for warning in warnings:
        sys.stderr.write(f"generate_maintainer_guide: warning: {warning}\n")
    for rel_path in PAGE_KEYS:
        print(f"Wrote {REPO / rel_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
