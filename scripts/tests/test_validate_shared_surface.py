from __future__ import annotations

import importlib.util
import inspect
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location(
    "validate_shared_surface",
    REPO_ROOT / "scripts" / "validate-shared-surface.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)


def test_main_returns_zero_for_current_repo() -> None:
    assert _mod.main() == 0


def test_main_returns_zero_for_clean_agent_file() -> None:
    target = REPO_ROOT / "profile-al-dev-shared" / "agents" / "al-dev-developer-tdd.md"
    assert _mod.main([str(target)]) == 0


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
