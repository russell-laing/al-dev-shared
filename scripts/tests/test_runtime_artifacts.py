from __future__ import annotations

import inspect
import os
import tempfile
import unittest
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.al_dev_tools.runtime_artifacts import contains_any_marker, latest_runtime_artifact


def test_latest_runtime_artifact_prefers_newest_matching_filename_by_mtime(tmp_path: Path) -> None:
    dev = tmp_path / ".dev"
    dev.mkdir()
    older = dev / "2026-06-28-ticket-ticket-context.md"
    newer = dev / "2026-06-29-ticket-ticket-context.md"
    older.write_text("older", encoding="utf-8")
    newer.write_text("newer", encoding="utf-8")
    os.utime(older, (1_000_000_000, 1_000_000_000))
    os.utime(newer, (1_000_000_001, 1_000_000_001))

    selected = latest_runtime_artifact(tmp_path, "*-ticket-ticket-context.md")

    assert selected == newer


def test_latest_runtime_artifact_returns_none_when_no_match(tmp_path: Path) -> None:
    (tmp_path / ".dev").mkdir()

    selected = latest_runtime_artifact(tmp_path, "*-interview-requirements.md")

    assert selected is None


def test_contains_any_marker_reports_missing_markers() -> None:
    ok, problem = contains_any_marker(
        "plain body without markers",
        ("TICKET_ID", "**Ticket ID**"),
    )

    assert ok is False
    assert "TICKET_ID" in problem


def test_contains_any_marker_accepts_present_marker() -> None:
    ok, problem = contains_any_marker(
        "body with TICKET_ID present",
        ("TICKET_ID", "**Ticket ID**"),
    )

    assert ok is True
    assert problem == ""


def _run(func):
    sig = inspect.signature(func)
    if not sig.parameters:
        func()
    elif list(sig.parameters) == ["tmp_path"]:
        with tempfile.TemporaryDirectory() as td:
            func(Path(td))
    else:
        raise TypeError(f"Unsupported signature: {func.__name__}{sig}")


def load_tests(loader, tests, pattern):  # noqa: ARG001
    suite = unittest.TestSuite()
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            suite.addTest(unittest.FunctionTestCase(lambda fn=fn: _run(fn)))
    return suite


if __name__ == "__main__":
    unittest.main()
