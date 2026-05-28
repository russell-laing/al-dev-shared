# scripts/tests/test_validate_knowledge_quality.py
"""Tests for canonical self-correction output shape in validate-knowledge-quality."""
from __future__ import annotations

import importlib.util
import inspect
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location(
    "validate_knowledge_quality",
    REPO_ROOT / "scripts" / "validate-knowledge-quality.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

_format_issue = _mod._format_issue
check_thin_sections = _mod.check_thin_sections
check_code_implication = _mod.check_code_implication
check_references = _mod.check_references


def test_format_issue_has_canonical_shape() -> None:
    output = _format_issue(
        "knowledge/foo.md",
        "knowledge-stub",
        'section "Usage" has 1 content line — too thin',
        "expand the section body or remove the header",
    )
    lines = output.splitlines()
    assert lines[0] == "knowledge/foo.md", f"First line must be path, got: {lines[0]!r}"
    assert any(ln.strip().startswith("rule:") for ln in lines), "Missing 'rule:' field"
    assert any(ln.strip().startswith("issue:") for ln in lines), "Missing 'issue:' field"
    assert any(ln.strip().startswith("fix:") for ln in lines), "Missing 'fix:' field"
    assert "knowledge-stub" in output


def test_check_thin_sections_emits_canonical_shape() -> None:
    sections = [("Usage Details", 3, 0, "short")]
    issues = check_thin_sections("knowledge/foo.md", sections)
    assert issues, "Expected at least one issue for a 1-line section"
    output = issues[0]
    assert "rule:" in output
    assert "knowledge-stub" in output
    assert "issue:" in output
    assert "fix:" in output


def test_check_code_implication_emits_canonical_shape() -> None:
    body = "Line one.\nLine two.\nLine three.\nNo code block here."
    sections = [("Usage: Example Pattern", 3, 0, body)]
    issues = check_code_implication("knowledge/foo.md", sections)
    assert issues, "Expected at least one issue for a code-implying section without code block"
    output = issues[0]
    assert "rule:" in output
    assert "knowledge-no-code" in output
    assert "fix:" in output


def test_check_references_emits_canonical_shape(tmp_path: Path) -> None:
    knowledge_dir = tmp_path / "knowledge"
    knowledge_dir.mkdir()
    content = "See knowledge/missing-file.md for details.\n"
    issues = check_references("knowledge/foo.md", content, knowledge_dir)
    assert issues, "Expected a dead-ref issue for a reference to a non-existent file"
    output = issues[0]
    assert "rule:" in output
    assert "knowledge-dead-ref" in output
    assert "fix:" in output
    assert "missing-file.md" in output


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
