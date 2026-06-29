"""Assert every .claude/ lens-agent name matches docs/naming_convention.md."""
from __future__ import annotations

import inspect
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_DIR = REPO_ROOT / "scripts"
AGENTS_DIR = REPO_ROOT / ".claude" / "agents"
SKILLS_DIR = REPO_ROOT / ".claude" / "skills"
CONVENTION_DOC = REPO_ROOT / "docs" / "naming_convention.md"

LENS_PATTERN = re.compile(r"^(design|quality)-(agent|skill)-lens-[a-z0-9-]+$")
LENS_EXCEPTIONS = {"naming-convention-lens"}
SNAKE_CASE_SCRIPT = re.compile(r"^[a-z0-9_]+\.py$")
SCRIPT_EXCEPTIONS = {"__init__.py", "_compat_entrypoint.py", "_entrypoint_bootstrap.py"}
SKILL_DIR_EXCEPTIONS = set()


def test_convention_doc_exists() -> None:
    assert CONVENTION_DOC.is_file(), f"missing {CONVENTION_DOC}"


def test_all_lens_agents_match_enforced_pattern() -> None:
    offenders = []
    for path in sorted(AGENTS_DIR.glob("*.md")):
        name = path.stem
        if name in LENS_EXCEPTIONS:
            continue
        if "-lens-" in name and not LENS_PATTERN.match(name):
            offenders.append(name)
    assert not offenders, f"lens agents break the enforced pattern: {offenders}"


def test_no_legacy_lens_names_remain() -> None:
    legacy = re.compile(r"^(design|quality)-lens-")
    offenders = [p.stem for p in AGENTS_DIR.glob("*.md") if legacy.match(p.stem)]
    assert not offenders, f"legacy lens names still present: {offenders}"


def test_skill_dirs_are_kebab_case() -> None:
    kebab = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
    offenders = [
        p.name
        for p in SKILLS_DIR.iterdir()
        if p.is_dir() and p.name not in SKILL_DIR_EXCEPTIONS and not kebab.match(p.name)
    ]
    assert not offenders, f"non-kebab skill dirs: {offenders}"


def test_top_level_python_scripts_are_snake_case() -> None:
    offenders = [
        path.name
        for path in SCRIPT_DIR.glob("*.py")
        if path.name not in SCRIPT_EXCEPTIONS and not SNAKE_CASE_SCRIPT.match(path.name)
    ]
    assert not offenders, f"non-snake-case top-level python scripts: {offenders}"


def _run(func):
    sig = inspect.signature(func)
    if not sig.parameters:
        func()
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
