"""Regression test for the generic-preflight tributary arrow in the Layer 1 diagram."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.al_dev_tools.docs.map_inventory import Inventory
from scripts.al_dev_tools.docs.map_rendering import render_skill_lifecycle


def _fixture_inventory(skills: list[str]) -> Inventory:
    return Inventory(
        skills=skills,
        agents=[],
        knowledge=[],
        agent_meta={},
        skill_to_skill=[],
        skill_to_agent=[],
        skill_to_knowledge=[],
        agent_to_knowledge=[],
        skill_to_artifact=[],
    )


class GenericPreflightTributaryTest(unittest.TestCase):
    def test_generic_preflight_tributary_arrow_is_rendered(self) -> None:
        inv = _fixture_inventory(["plan", "generic-preflight"])

        body = render_skill_lifecycle(inv)

        self.assertIn(
            "skill_generic_preflight -.-> |preflight-context.md| skill_plan",
            body,
        )


if __name__ == "__main__":
    unittest.main()
