from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
_SPEC = importlib.util.spec_from_file_location(
    "validate_reference_integrity",
    REPO_ROOT / "scripts" / "validate_reference_integrity.py",
)
_MOD = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = _MOD
_SPEC.loader.exec_module(_MOD)

validate_reference_path = _MOD.validate_reference_path


def _write(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def test_flags_dead_inline_doc_path(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    doc = _write(
        root / "profile-al-dev-shared" / "knowledge" / "guide.md",
        "See knowledge/missing.md for details.\n",
    )

    _MOD.REPO_ROOT = root
    issues = validate_reference_path(doc)

    assert any("reference-dead-path" in issue for issue in issues)
    assert any("knowledge/missing.md" in issue for issue in issues)


def test_allows_cross_surface_claude_to_shared_knowledge_reference(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    shared = _write(
        root / "profile-al-dev-shared" / "knowledge" / "workflow-resilience.md",
        "# shared\n",
    )
    doc = _write(
        root / ".claude" / "knowledge" / "tooling.md",
        "See `knowledge/workflow-resilience.md`.\n",
    )

    _MOD.REPO_ROOT = root
    issues = validate_reference_path(doc)

    assert issues == []
    assert shared.exists()


def test_flags_stale_script_entrypoint_in_prose(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    doc = _write(
        root / ".claude" / "knowledge" / "tooling.md",
        "Run scripts/generate_maintainer_guide.py after edits.\n",
    )

    _MOD.REPO_ROOT = root
    issues = validate_reference_path(doc)

    assert any("reference-stale-command" in issue for issue in issues)
    assert any("python3 scripts/generate_maintainer_guide.py" in issue for issue in issues)


def test_allows_template_example_path(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    doc = _write(
        root / ".claude" / "knowledge" / "tooling.md",
        "Template: `docs/health/YYYY-MM-DD-<surface>-findings.md`.\n",
    )

    _MOD.REPO_ROOT = root
    issues = validate_reference_path(doc)

    assert issues == []


def test_flags_legacy_alias_on_active_surface_but_allows_archived_surface(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    active = _write(
        root / ".claude" / "knowledge" / "active.md",
        "Legacy path `.dev/02-solution-plan.md`.\n",
    )
    archived = _write(
        root / "profile-al-dev-shared" / "archived" / "skills" / "old" / "SKILL.md",
        "Legacy path `.dev/02-solution-plan.md`.\n",
    )

    _MOD.REPO_ROOT = root
    active_issues = validate_reference_path(active)
    archived_issues = validate_reference_path(archived)

    assert any("reference-legacy-alias" in issue for issue in active_issues)
    assert archived_issues == []


def test_direct_script_runs_with_repo_relative_path() -> None:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        clean = _write(
            root / "profile-al-dev-shared" / "knowledge" / "clean.md",
            "See knowledge/file.md for an example placeholder.\n",
        )
        dirty = _write(
            root / "profile-al-dev-shared" / "knowledge" / "dirty.md",
            "See knowledge/missing.md for details.\n",
        )

        clean_result = subprocess.run(
            [
                sys.executable,
                str(REPO_ROOT / "scripts" / "validate_reference_integrity.py"),
                "--path",
                str(clean),
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        dirty_result = subprocess.run(
            [
                sys.executable,
                str(REPO_ROOT / "scripts" / "validate_reference_integrity.py"),
                "--path",
                str(dirty),
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

    assert clean_result.returncode == 0, clean_result.stdout + clean_result.stderr
    assert "PASS (" in clean_result.stdout
    assert dirty_result.returncode == 1, dirty_result.stdout + dirty_result.stderr
    assert "FAIL (" in dirty_result.stdout
    assert "reference-dead-path" in dirty_result.stdout


def _run(func):
    import inspect

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
