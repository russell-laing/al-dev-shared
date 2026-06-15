from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[2] / ".claude" / "hooks" / "stop_projection_check.py"
MODULE_SPEC = importlib.util.spec_from_file_location(
    "stop_projection_check", MODULE_PATH
)
assert MODULE_SPEC is not None and MODULE_SPEC.loader is not None
stop_projection_check = importlib.util.module_from_spec(MODULE_SPEC)
MODULE_SPEC.loader.exec_module(stop_projection_check)


class GeneratedProjectionChangeTest(unittest.TestCase):
    def test_ignores_ds_store_inside_generated_projection_tree(self) -> None:
        self.assertFalse(
            stop_projection_check._is_generated_projection_change(
                "profile-al-dev-shared/generated/agents/.DS_Store"
            )
        )

    def test_accepts_real_generated_projection_files(self) -> None:
        self.assertTrue(
            stop_projection_check._is_generated_projection_change(
                "profile-al-dev-shared/generated/agents/claude/example.md"
            )
        )


if __name__ == "__main__":
    unittest.main()
