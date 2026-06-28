#!/usr/bin/env python3
"""Print the canonical skill → spawned-agent mapping as JSON.

Single source of truth for "Agents spawned" derivation: uses the same edge
parser as scripts/generate_map_doc_sections.py, so skill-metadata audit
results can never disagree with the generated skill-drilldown sections.
Mirrors scripts/derive_agent_callers.py for the skill side.

Replaces the canonical-slug-only extraction formerly embedded in
sync-map-documentation-skill-metadata, whose narrower matching missed bare
agent references (e.g. `Spawn **al-dev-solution-architect**`) and produced
agent_name_mismatch findings that the write phase — regenerating the
drilldowns from this parser — immediately reverted.

Agents are emitted in canonical `al-dev-shared:<name>` form to match the
skill-metadata `spawned_agents` schema.
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
    spawned = {
        name: sorted(
            {f"al-dev-shared:{agent}" for skill, agent in edges if skill == name}
        )
        for name in inv.skills
    }
    json.dump(spawned, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
