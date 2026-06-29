"""Behavioral tests for scripts/validate-artifact-leaks.py."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPT = REPO_ROOT / "scripts" / "validate-artifact-leaks.py"


def _load():
    spec = importlib.util.spec_from_file_location("validate_artifact_leaks", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_allows_persistent_progress_file():
    module = _load()

    assert module.find_temporary_artifacts([".dev/progress.md"]) == []


def test_blocks_dated_dev_markdown():
    module = _load()

    leaks = module.find_temporary_artifacts([".dev/2026-06-30-research-notes.md"])

    assert leaks == [".dev/2026-06-30-research-notes.md"]


def test_blocks_named_progress_markdown():
    module = _load()

    leaks = module.find_temporary_artifacts([".dev/implement-plugin-health-progress.md"])

    assert leaks == [".dev/implement-plugin-health-progress.md"]


def test_blocks_raw_superpowers_plan():
    module = _load()

    leaks = module.find_temporary_artifacts(
        ["docs/superpowers/plans/2026-06-30-scratch-plan.md"]
    )

    assert leaks == ["docs/superpowers/plans/2026-06-30-scratch-plan.md"]


def test_blocks_legacy_archived_plan_edits():
    module = _load()

    leaks = module.find_temporary_artifacts(
        ["docs/superpowers/plans/archived/2026-06-30-legacy-plan.md"]
    )

    assert leaks == ["docs/superpowers/plans/archived/2026-06-30-legacy-plan.md"]


def test_allows_gitkeep_markers():
    module = _load()

    leaks = module.find_temporary_artifacts(
        [
            "docs/superpowers/plans/.gitkeep",
            "docs/superpowers/specs/.gitkeep",
        ]
    )

    assert leaks == []


def load_tests(loader, tests, pattern):  # noqa: ARG001
    suite = unittest.TestSuite()
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            suite.addTest(unittest.FunctionTestCase(fn))
    return suite


if __name__ == "__main__":
    test_allows_persistent_progress_file()
    test_blocks_dated_dev_markdown()
    test_blocks_named_progress_markdown()
    test_blocks_raw_superpowers_plan()
    test_blocks_legacy_archived_plan_edits()
    test_allows_gitkeep_markers()
    print("\nAll tests passed")
