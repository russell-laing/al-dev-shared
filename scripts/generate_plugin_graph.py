#!/usr/bin/env python3
"""Generate docs/plugin-graph.md from shared inventory helpers.

This script is fail-closed: parse or inventory errors exit non-zero and leave
the existing document untouched. It does not emit partial output.
"""
from __future__ import annotations

from datetime import date
from pathlib import Path
import sys

from _entrypoint_bootstrap import bootstrap_repo

REPO_ROOT = bootstrap_repo(__file__)
from scripts.al_dev_tools.io_utils import write_text_atomic
from scripts.al_dev_tools.docs.map_doc_sections import (
    build_all_sections,
    build_plugin_graph_document,
    collect_inventory,
    mermaid_node_id,
    replace_marked_sections,
    summarize_plugin_health,
)


REPO = REPO_ROOT
PLUGIN = REPO / "profile-al-dev-shared"
OUTPUT = REPO / "docs" / "plugin-graph.md"

# The three canonical workflow paths (from CLAUDE.md "Plugin Architecture").
WORKFLOW_PATHS = {
    "Ticket / Support": ["ticket", "support-reply"],
    "Development spine": [
        "investigate",
        "plan",
        "develop-orchestrate",
        "commit",
    ],
    "Direct fix": ["fix"],
}


def node_id(name: str) -> str:
    return mermaid_node_id(name)


def build_document(inventory, health, *, today: str) -> str:  # noqa: ANN001
    del health
    return build_plugin_graph_document(
        inventory,
        today=today,
        generated_by="scripts/generate_plugin_graph.py",
        workflow_paths=WORKFLOW_PATHS,
    )


def main() -> int:
    try:
        inventory = collect_inventory(PLUGIN)
        health = summarize_plugin_health(inventory, workflow_paths=WORKFLOW_PATHS)
        del health
        rendered = build_all_sections(inventory)
        replacements = {
            key: rendered[key]
            for key in (
                "plugin-dependency-mermaid",
                "plugin-workflow-overlays",
                "plugin-health-callouts",
            )
        }
        current = OUTPUT.read_text(encoding="utf-8")
        updated = replace_marked_sections(current, replacements)
        write_text_atomic(OUTPUT, updated)
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"generate_plugin_graph: {exc}\n")
        return 1

    print(f"Wrote {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
