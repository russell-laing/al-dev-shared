from __future__ import annotations

import importlib.util
import inspect
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location(
    "validate_shared_surface",
    REPO_ROOT / "scripts" / "validate_shared_surface.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)


def test_main_reports_existing_repo_issues_without_crashing() -> None:
    assert _mod.main() != 0


def test_main_returns_zero_for_clean_agent_file() -> None:
    target = REPO_ROOT / "profile-al-dev-shared" / "agents" / "developer-tdd.md"
    assert _mod.main([str(target)]) == 0


def test_check_agent_rejects_malformed_frontmatter(tmp_path: Path) -> None:
    target = tmp_path / "broken.md"
    target.write_text("---\n- bad\n---\nbody\n", encoding="utf-8")

    issues = _mod._check_agent(target)

    assert issues
    assert any("frontmatter" in issue for issue in issues)


def test_check_agent_accepts_valid_structured_frontmatter(tmp_path: Path) -> None:
    target = tmp_path / "agent.md"
    target.write_text(
        "---\n"
        "name: agent\n"
        "description: >-\n"
        "  Example agent.\n"
        "model: haiku\n"
        "tools:\n"
        "  - Read\n"
        "---\n"
        "body\n",
        encoding="utf-8",
    )

    assert _mod._check_agent(target) == []


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
