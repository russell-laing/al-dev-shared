"""Regression tests for health disposition workflow contract wording."""

from __future__ import annotations

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


FILES = [
    ".claude/skills/record-health-dispositions/SKILL.md",
    ".claude/skills/plan-health-findings/SKILL.md",
    ".claude/skills/revise-health-plan/SKILL.md",
    ".claude/skills/implement-health-plan/SKILL.md",
    ".claude/knowledge/health-disposition-storage-contract.md",
    ".claude/knowledge/ledger-closure-protocol.md",
    ".claude/knowledge/health-plan-context-template.md",
]


class DispositionWorkflowContractTest(unittest.TestCase):
    def test_new_contract_names_event_ids(self) -> None:
        combined = "\n".join((REPO_ROOT / path).read_text(encoding="utf-8") for path in FILES)

        self.assertIn("event_id", combined)
        self.assertIn("closes_event_ids", combined)
        self.assertIn("dispositions-open.md", combined)
        self.assertIn("dispositions-index.json", combined)

    def test_stale_closes_rows_term_is_removed(self) -> None:
        for path in FILES:
            text = (REPO_ROOT / path).read_text(encoding="utf-8")
            self.assertNotIn("closes_rows", text, path)

    def test_no_manual_append_to_generated_markdown_instruction(self) -> None:
        forbidden = "append rows to docs/health/dispositions.md"
        for path in FILES:
            text = (REPO_ROOT / path).read_text(encoding="utf-8").lower()
            self.assertNotIn(forbidden, text, path)


if __name__ == "__main__":
    unittest.main()
