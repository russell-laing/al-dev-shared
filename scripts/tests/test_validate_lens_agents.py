# scripts/tests/test_validate_lens_agents.py
"""Tests for canonical self-correction output shape in validate-lens-agents."""
from __future__ import annotations

import importlib.util
import inspect
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location(
    "validate_lens_agents",
    REPO_ROOT / "scripts" / "validate-lens-agents.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

_format_failure = _mod._format_failure


def test_format_failure_has_canonical_shape() -> None:
    output = _format_failure(
        path=".claude/agents/quality-agent-lens-clarity.md",
        rule="agent-model",
        issue="model is not set to haiku",
        fix='add "model: haiku" to the YAML frontmatter',
    )
    lines = output.splitlines()
    assert lines[0] == ".claude/agents/quality-agent-lens-clarity.md", (
        f"First line must be path, got: {lines[0]!r}"
    )
    assert any(ln.strip().startswith("rule:") for ln in lines), "Missing 'rule:' field"
    assert any(ln.strip().startswith("issue:") for ln in lines), "Missing 'issue:' field"
    assert any(ln.strip().startswith("fix:") for ln in lines), "Missing 'fix:' field"
    assert "haiku" in output


def test_format_failure_embeds_path_in_fix_when_provided() -> None:
    output = _format_failure(
        path=".claude/agents/foo.md",
        rule="agent-forbidden-tool",
        issue='tool "Bash" is not permitted for lens agents',
        fix='remove "Bash" from the tools list in .claude/agents/foo.md',
    )
    assert ".claude/agents/foo.md" in output
    assert "Bash" in output
    assert "fix:" in output


def test_main_returns_zero_for_current_repo() -> None:
    assert _mod.main() == 0


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
