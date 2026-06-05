"""Fixture-based tests for scripts/maintainer_guide_sections.py and generate-maintainer-guide.py."""
from __future__ import annotations

import contextlib
import importlib.util
import inspect
import io
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def _load_module(filename: str, module_name: str):
    spec = importlib.util.spec_from_file_location(
        module_name,
        REPO_ROOT / "scripts" / filename,
    )
    if spec is None or spec.loader is None:
        raise FileNotFoundError(REPO_ROOT / "scripts" / filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


lib = _load_module("maintainer_guide_sections.py", "maintainer_guide_sections")


def _write_skill(parent: Path, name: str, frontmatter_yaml: str) -> None:
    skill_dir = parent / name
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        "---\n" + frontmatter_yaml + "---\n\n# " + name + "\n",
        encoding="utf-8",
    )


def _build_skills_fixture(root: Path) -> Path:
    """Four active skills + one archived: covers every contract shape and gap signal."""
    skills = root / ".claude" / "skills"
    _write_skill(
        skills,
        "alpha-audit",
        "name: alpha-audit\n"
        "description: Audits the surface. Second sentence is ignored.\n"
        "workflow:\n"
        "  stage: discover\n"
        "  invoked-by: user\n"
        "  repeatable: true\n"
        "  inputs:\n"
        "    - profile-al-dev-shared/skills/\n"
        "  outputs:\n"
        "    - docs/health/<date>-findings.md\n"
        "  next: [beta-report]\n",
    )
    _write_skill(
        skills,
        "beta-report",
        "name: beta-report\n"
        "description: Ranks findings into a dossier.\n"
        "workflow:\n"
        "  stage: discover\n"
        "  invoked-by: skill:alpha-audit\n"
        "  repeatable: false\n"
        "  inputs:\n"
        "    - docs/health/<date>-findings.md\n"
        "  outputs:\n"
        "    - docs/health/<date>-dossier.md\n"
        "  next: [gamma-plan]\n",
    )
    _write_skill(
        skills,
        "gamma-plan",
        "name: gamma-plan\n"
        "description: Plans accepted findings.\n"
        "workflow:\n"
        "  stage: decide\n"
        "  invoked-by: user\n"
        "  repeatable: true\n"
        "  inputs:\n"
        "    - docs/health/<date>-dossier.md\n"
        "    - docs/ledger.md\n"
        "  outputs:\n"
        "    - docs/plans/<date>-plan.md\n"
        "  manual-followup: implement the plan\n",
    )
    _write_skill(
        skills,
        "delta-notes",
        "name: delta-notes\ndescription: No contract yet.\n",
    )
    _write_skill(
        skills / "archived",
        "old-skill",
        "name: old-skill\ndescription: Archived, must be ignored.\n",
    )
    return skills


def test_load_contracts_parses_and_reports_missing() -> None:
    with tempfile.TemporaryDirectory() as td:
        skills = _build_skills_fixture(Path(td))
        contracts, missing = lib.load_contracts(skills)
        assert [c.skill for c in contracts] == ["alpha-audit", "beta-report", "gamma-plan"]
        assert missing == ["delta-notes"]
        alpha = contracts[0]
        assert alpha.stage == "discover"
        assert alpha.invoked_by == "user"
        assert alpha.repeatable is True
        assert alpha.inputs == ("profile-al-dev-shared/skills/",)
        assert alpha.outputs == ("docs/health/<date>-findings.md",)
        assert alpha.next_skills == ("beta-report",)
        assert alpha.manual_followup is None
        assert alpha.description.startswith("Audits the surface.")
        gamma = contracts[2]
        assert gamma.manual_followup == "implement the plan"
        assert gamma.next_skills == ()


def test_parse_contract_returns_none_without_block() -> None:
    assert lib.parse_contract("x", {"name": "x", "description": "d"}) is None


def test_parse_contract_rejects_bad_stage() -> None:
    fm = {"description": "d", "workflow": {"stage": "bogus", "invoked-by": "user"}}
    try:
        lib.parse_contract("bad-skill", fm)
    except ValueError as exc:
        assert "bad-skill" in str(exc) and "stage" in str(exc)
    else:
        raise AssertionError("expected ValueError for bad stage")


def test_parse_contract_rejects_bad_invoked_by() -> None:
    fm = {"description": "d", "workflow": {"stage": "discover", "invoked-by": "cron"}}
    try:
        lib.parse_contract("bad-skill", fm)
    except ValueError as exc:
        assert "bad-skill" in str(exc) and "invoked-by" in str(exc)
    else:
        raise AssertionError("expected ValueError for bad invoked-by")


def test_parse_contract_rejects_empty_input_entry() -> None:
    fm = {
        "description": "d",
        "workflow": {"stage": "discover", "invoked-by": "user", "inputs": ["ok", ""]},
    }
    try:
        lib.parse_contract("bad-skill", fm)
    except ValueError as exc:
        assert "bad-skill" in str(exc) and "inputs" in str(exc)
    else:
        raise AssertionError("expected ValueError for empty input entry")


def test_parse_contract_rejects_unknown_keys() -> None:
    fm = {
        "description": "d",
        "workflow": {"stage": "discover", "invoked-by": "user", "repeatible": True},
    }
    try:
        lib.parse_contract("bad-skill", fm)
    except ValueError as exc:
        assert "bad-skill" in str(exc) and "repeatible" in str(exc)
    else:
        raise AssertionError("expected ValueError for unknown workflow key")


def test_validate_contracts_rejects_unknown_next_and_invoker() -> None:
    with tempfile.TemporaryDirectory() as td:
        skills = _build_skills_fixture(Path(td))
        contracts, missing = lib.load_contracts(skills)
        active = {c.skill for c in contracts} | set(missing)
        lib.validate_contracts(contracts, active)  # must not raise
        try:
            lib.validate_contracts(contracts, active - {"beta-report"})
        except ValueError as exc:
            assert "beta-report" in str(exc)
        else:
            raise AssertionError("expected ValueError for unknown next target")


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
