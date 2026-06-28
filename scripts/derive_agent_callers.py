#!/usr/bin/env python3
"""Print the canonical agent → caller-skill mapping as JSON.

Single source of truth for "Spawned by" derivation: uses the same edge
parser as scripts/generate_map_doc_sections.py, so audit results can never
disagree with the generated agent-catalog table. Replaces the grep-based
caller discovery formerly embedded in sync-documentation-maps-agent-audit,
whose looser matching produced caller_mismatch findings that the write
phase (regenerating the catalog from this parser) immediately reverted.
"""

from __future__ import annotations

import json
import sys

from _entrypoint_bootstrap import bootstrap_repo

REPO_ROOT = bootstrap_repo(__file__)
from scripts.al_dev_tools.docs.map_doc_sections import (
    _internal_skill_agent_edges,
    collect_inventory,
)


def main() -> int:
    inv = collect_inventory(REPO_ROOT / "profile-al-dev-shared")
    edges = _internal_skill_agent_edges(inv)
    callers = {
        name: sorted({skill for skill, agent in edges if agent == name})
        for name in inv.agents
    }
    json.dump(callers, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
