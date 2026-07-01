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


def test_flags_legacy_disposition_hyphen_alias(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    doc = _write(
        root / ".claude" / "skills" / "s" / "SKILL.md",
        "Read `docs/health/dispositions-open.md` for open rows.\n",
    )

    _MOD.REPO_ROOT = root
    issues = validate_reference_path(doc)

    assert any("reference-legacy-alias" in issue for issue in issues)
    assert any("dispositions-open.md" in issue for issue in issues)


def test_match_filters_on_issue_text_not_file_path(tmp_path: Path) -> None:
    # File name contains "dispositions"; the broken ref does NOT. The --match
    # filter must key off the issue token, not the incidental path substring.
    root = tmp_path / "repo"
    doc = _write(
        root / ".claude" / "skills" / "record-plugin-dispositions" / "SKILL.md",
        "See knowledge/missing.md for details.\n",
    )

    _MOD.REPO_ROOT = root
    unscoped = validate_reference_path(doc)
    scoped = validate_reference_path(doc, match="dispositions")

    assert any("knowledge/missing.md" in issue for issue in unscoped)
    assert scoped == []


def test_skips_shell_template_placeholder_path(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    doc = _write(
        root / ".claude" / "skills" / "s" / "SKILL.md",
        "Shard: `docs/health/dispositions_events/${YEAR}/${YEAR}-${MONTH}.jsonl`.\n",
    )

    _MOD.REPO_ROOT = root
    assert validate_reference_path(doc) == []


def test_bare_knowledge_ref_resolves_from_non_knowledge_dir(tmp_path: Path) -> None:
    # A skill (outside a knowledge/ dir) citing a bare knowledge/X token should
    # resolve against the canonical knowledge roots, not be flagged dead.
    root = tmp_path / "repo"
    _write(root / ".claude" / "knowledge" / "contract.md", "# contract\n")
    doc = _write(
        root / ".claude" / "skills" / "s" / "SKILL.md",
        "Follows `knowledge/contract.md`.\n",
    )

    _MOD.REPO_ROOT = root
    assert validate_reference_path(doc) == []


def test_strips_file_line_citation_suffix(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    _write(root / "scripts" / "store.py", "x = 1\n")
    doc = _write(
        root / ".claude" / "knowledge" / "k.md",
        "See `scripts/store.py:802` for the loop.\n",
    )
    _MOD.REPO_ROOT = root
    assert validate_reference_path(doc) == []


def test_strips_anchor_suffix(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    _write(root / ".claude" / "knowledge" / "guide.md", "# guide\n")
    doc = _write(
        root / ".claude" / "knowledge" / "k.md",
        "See `knowledge/guide.md#section-two`.\n",
    )
    _MOD.REPO_ROOT = root
    assert validate_reference_path(doc) == []


def test_strips_shell_var_assignment_prefix(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    _write(root / "docs" / "map.md", "# map\n")
    doc = _write(
        root / ".claude" / "knowledge" / "k.md",
        "Run with `MAP_FILE=docs/map.md` set.\n",
    )
    _MOD.REPO_ROOT = root
    assert validate_reference_path(doc) == []


def test_skips_bracket_placeholder_and_ellipsis(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    doc = _write(
        root / ".claude" / "knowledge" / "k.md",
        "Example `docs/API/[name].md` and `.../skills/x/SKILL.md`.\n",
    )
    _MOD.REPO_ROOT = root
    assert validate_reference_path(doc) == []


def test_skips_archived_and_generated_surfaces(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    _write(
        root / "profile-al-dev-shared" / "archived" / "skills" / "old" / "SKILL.md",
        "Dead ref `docs/gone.md`.\n",
    )
    _write(
        root / "profile-al-dev-shared" / "generated" / "agents" / "claude" / "a.md",
        "Dead ref `docs/gone.md`.\n",
    )
    _MOD.REPO_ROOT = root
    # Directory scan must skip both frozen surfaces entirely.
    assert validate_reference_path(root / "profile-al-dev-shared") == []


def test_bare_reference_regex_does_not_double_capture_dotdot(tmp_path: Path) -> None:
    # `../../knowledge/real.md` must yield ONE resolvable token, not also a
    # spurious `./../knowledge/real.md` mid-path capture.
    root = tmp_path / "repo"
    _write(root / ".claude" / "knowledge" / "real.md", "# real\n")
    doc = _write(
        root / ".claude" / "skills" / "s" / "SKILL.md",
        "Follows ../../knowledge/real.md here.\n",
    )
    _MOD.REPO_ROOT = root
    assert validate_reference_path(doc) == []


def test_foo_placeholder_is_allowed(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    doc = _write(
        root / ".claude" / "knowledge" / "k.md",
        "For example `knowledge/foo.md` or `scripts/foo.py`.\n",
    )
    _MOD.REPO_ROOT = root
    assert validate_reference_path(doc) == []


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
