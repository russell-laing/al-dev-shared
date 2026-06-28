"""Focused tests for scripts/al_dev_tools/io_utils.py."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts.al_dev_tools.io_utils import write_text_atomic


def test_write_text_atomic_writes_content_and_leaves_no_temp_files() -> None:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        target = root / "output.txt"

        write_text_atomic(target, "hello world\n")

        assert target.read_text(encoding="utf-8") == "hello world\n"
        assert list(root.glob(f".{target.name}.*.tmp")) == []


def test_write_text_atomic_cleans_up_temp_file_when_replace_fails() -> None:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        target = root / "output.txt"

        with mock.patch.object(Path, "replace", side_effect=RuntimeError("boom")):
            with unittest.TestCase().assertRaisesRegex(RuntimeError, "boom"):
                write_text_atomic(target, "hello world\n")

        assert not target.exists()
        assert list(root.glob(f".{target.name}.*.tmp")) == []


def _run(func):
    func()


def load_tests(loader, tests, pattern):  # noqa: ARG001
    suite = unittest.TestSuite()
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            suite.addTest(unittest.FunctionTestCase(lambda fn=fn: _run(fn)))
    return suite


if __name__ == "__main__":
    unittest.main()
