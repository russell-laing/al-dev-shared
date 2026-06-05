#!/usr/bin/env python3
"""Regenerate the marked sections of docs/maintainer-tooling.md from workflow contracts.

Reads `workflow:` frontmatter blocks from .claude/skills/*/SKILL.md (excluding
archived/) and rewrites only the <!-- BEGIN GENERATED: ... --> regions of
docs/maintainer-tooling.md.

Fail-closed, following scripts/generate-plugin-graph.py: any parse or validation
error (including a missing marker pair) exits non-zero, names the offending skill
or section, and leaves the document untouched. Node-budget overruns are warnings
on stderr; generation still succeeds.
"""
from __future__ import annotations

from pathlib import Path
import sys
import tempfile

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from maintainer_guide_sections import (  # noqa: E402
    build_sections,
    load_contracts,
    validate_contracts,
)
from map_doc_sections import replace_marked_sections  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
SKILLS_DIR = REPO / ".claude" / "skills"
GUIDE_PATH = REPO / "docs" / "maintainer-tooling.md"


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
        current = GUIDE_PATH.read_text(encoding="utf-8")
        updated = replace_marked_sections(current, sections)
        _write_text_atomic(GUIDE_PATH, updated)
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"generate-maintainer-guide: {exc}\n")
        return 1

    for warning in warnings:
        sys.stderr.write(f"generate-maintainer-guide: warning: {warning}\n")
    print(f"Wrote {GUIDE_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
