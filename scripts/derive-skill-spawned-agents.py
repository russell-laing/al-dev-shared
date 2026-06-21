#!/usr/bin/env python3
"""Print the canonical skill → spawned-agent mapping as JSON.

Single source of truth for "Agents spawned" derivation: uses the same edge
parser as scripts/generate-map-doc-sections.py, so skill-metadata audit
results can never disagree with the generated skill-drilldown sections.
Mirrors scripts/derive-agent-callers.py for the skill side.

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
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from map_doc_sections import collect_inventory, _internal_skill_agent_edges


def main() -> int:
    repo = SCRIPT_DIR.parent
    inv = collect_inventory(repo / "profile-al-dev-shared")
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
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"derive-skill-spawned-agents: {exc}\n")
        raise SystemExit(1) from exc
